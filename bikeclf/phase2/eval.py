"""Evaluation runner for Phase 2 categorization."""
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table

from bikeclf.config import (
    APIConfig,
    LangfuseConfig,
    PROJECT_ROOT,
    SUPPORTED_MODELS,
    get_model_short_name,
)
from bikeclf.schema import Phase2PredictionRecord, PredictionMeta
from bikeclf.io import write_json, append_error_jsonl
from bikeclf.phase2.config import PHASE2_RUNS_DIR
from bikeclf.phase2.io import load_phase2_eval_set, write_phase2_predictions_jsonl, read_phase2_predictions_jsonl
from bikeclf.phase2.gemini_client import Phase2GeminiClient
from bikeclf.phase2.metrics import compute_phase2_metrics
from bikeclf.phase2.markdown_report import generate_phase2_misclassification_report
from bikeclf.phase2.prompt_loader import load_prompt, list_available_prompts, format_prompt

app = typer.Typer(help="Phase 2: Bike issue categorization CLI")
console = Console()


def get_git_commit() -> str:
    """Get current git commit hash.

    Returns:
        Short commit hash (12 chars) or 'unknown' if not available
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()[:12]
    except Exception:
        pass
    return "unknown"


def init_langfuse() -> Optional[any]:
    """Initialize Langfuse if configured.

    Returns:
        Langfuse client instance or None if not configured
    """
    config = LangfuseConfig()

    if not config.is_enabled():
        console.print("[yellow]Langfuse not configured, skipping tracing[/yellow]")
        return None

    try:
        from langfuse import Langfuse

        langfuse = Langfuse(
            public_key=config.public_key,
            secret_key=config.secret_key,
            host=config.host,
        )
        console.print("[green]✓ Langfuse tracing enabled[/green]")
        return langfuse
    except Exception as e:
        console.print(f"[yellow]Failed to initialize Langfuse: {e}[/yellow]")
        return None


def create_run_directory(prompt_version: str, model_id: str) -> Path:
    """Create run directory with timestamp, prompt version, and model name.

    Args:
        prompt_version: Prompt version identifier (e.g., 'v001')
        model_id: Model identifier (e.g., 'gemini-2.5-flash-lite')

    Returns:
        Path to created run directory
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    model_short = get_model_short_name(model_id)
    run_dir = PHASE2_RUNS_DIR / f"{timestamp}_{prompt_version}_{model_short}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


@app.command()
def evaluate(
    dataset: Path = typer.Option(
        PROJECT_ROOT / "phase2" / "phase2-eval-set.jsonl",
        "--dataset",
        "-d",
        help="Path to Phase 2 evaluation JSONL",
    ),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt version (e.g., v001)"),
    model: str = typer.Option(
        "gemini-2.5-flash-lite",
        "--model",
        "-m",
        help="Model identifier",
    ),
    temperature: float = typer.Option(
        0.0,
        "--temperature",
        "-t",
        help="Sampling temperature (0.0 for determinism)",
    ),
    max_tokens: int = typer.Option(
        512,
        "--max-tokens",
        help="Maximum output tokens",
    ),
):
    """Run Phase 2 evaluation on dataset with specified prompt version."""

    # Validate model
    if model not in SUPPORTED_MODELS:
        console.print(f"[red]✗ Unsupported model: {model}[/red]")
        console.print(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
        raise typer.Exit(1)

    # Load and validate API configuration
    api_config = APIConfig()
    try:
        api_config.validate_required()
    except ValueError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    # Initialize services
    console.print("[blue]Initializing services...[/blue]")
    client = Phase2GeminiClient(api_config)
    langfuse = init_langfuse()

    # Load prompt
    try:
        system_prompt, prompt_hash = load_prompt(prompt)
        console.print(f"[green]✓ Loaded prompt: {prompt} (hash: {prompt_hash})[/green]")
    except FileNotFoundError as e:
        console.print(f"[red]✗ {e}[/red]")
        raise typer.Exit(1)

    # Load dataset
    try:
        records = load_phase2_eval_set(dataset)
        console.print(f"[green]✓ Loaded dataset: {len(records)} examples[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to load dataset: {e}[/red]")
        raise typer.Exit(1)

    # Create run directory
    run_dir = create_run_directory(prompt, model)
    console.print(f"[blue]Run directory: {run_dir}[/blue]\n")

    # Process each record
    predictions: List[Phase2PredictionRecord] = []
    errors_path = run_dir / "errors.jsonl"

    # Use Langfuse span for the entire evaluation if configured
    span_context = (
        langfuse.start_as_current_span(
            name=f"eval_phase2_{prompt}",
            metadata={
                "prompt_version": prompt,
                "model_id": model,
                "dataset_rows": len(records),
                "temperature": temperature,
            },
        )
        if langfuse
        else None
    )

    try:
        if span_context:
            span_context.__enter__()

        with console.status("[bold green]Processing reports...") as status:
            for idx, record in enumerate(records):
                status.update(f"Processing {record['id']} ({idx + 1}/{len(records)})")

                # Format prompt with report details
                full_prompt = format_prompt(
                    system_prompt,
                    record["subject"],
                    record["description"],
                )

                # Create a nested generation span for this classification
                generation_context = (
                    langfuse.start_as_current_generation(
                        name=f"classify_{record['id']}",
                        model=model,
                        input=full_prompt,
                        metadata={
                            "row_id": record["id"],
                            "gold_category": record["phase2_label"],
                        },
                    )
                    if langfuse
                    else None
                )

                try:
                    if generation_context:
                        generation_context.__enter__()

                    # Classify with retry logic
                    output, latency_ms, attempts, error = client.classify_with_retry(
                        prompt=full_prompt,
                        model_id=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )

                    timestamp_utc = datetime.now(timezone.utc).isoformat()

                    # Handle failure
                    if output is None:
                        error_record = {
                            "id": record["id"],
                            "subject": record["subject"],
                            "description": record["description"],
                            "gold_category": record["phase2_label"],
                            "error": error,
                            "attempts": attempts,
                            "timestamp_utc": timestamp_utc,
                        }
                        append_error_jsonl(error_record, errors_path)
                        console.print(f"[red]✗ Failed: {record['id']} - {error}[/red]")

                        # Update generation with error
                        if generation_context:
                            langfuse.update_current_generation(
                                output={"error": error},
                                metadata={
                                    "latency_ms": latency_ms,
                                    "attempts": attempts,
                                    "status": "error",
                                },
                            )
                        continue

                    # Create prediction record
                    meta = PredictionMeta(
                        model_id=model,
                        prompt_version=prompt,
                        temperature=temperature,
                        max_output_tokens=max_tokens,
                        timestamp_utc=timestamp_utc,
                        latency_ms=latency_ms,
                        attempts=attempts,
                    )

                    pred_record = Phase2PredictionRecord(
                        id=record["id"],
                        subject=record["subject"],
                        description=record["description"],
                        gold_category=record["phase2_label"],
                        pred=output,
                        meta=meta,
                    )

                    predictions.append(pred_record)

                    # Update Langfuse generation with output
                    if generation_context:
                        langfuse.update_current_generation(
                            output=output.model_dump(),
                            metadata={
                                "pred_category": output.category,
                                "latency_ms": latency_ms,
                                "attempts": attempts,
                                "confidence": output.confidence,
                            },
                        )

                finally:
                    if generation_context:
                        generation_context.__exit__(None, None, None)

    finally:
        if span_context:
            span_context.__exit__(None, None, None)

    # Save predictions
    predictions_path = run_dir / "predictions.jsonl"
    write_phase2_predictions_jsonl(predictions, predictions_path)
    console.print(f"\n[green]✓ Saved {len(predictions)} predictions to {predictions_path.name}[/green]")

    # Compute and display metrics
    if predictions:
        gold_categories = [p.gold_category for p in predictions]
        pred_categories = [p.pred.category for p in predictions]

        metrics = compute_phase2_metrics(gold_categories, pred_categories)

        # Save metrics
        metrics_path = run_dir / "metrics.json"
        write_json(metrics, metrics_path)

        # Display metrics
        console.print("\n[bold]Classification Metrics:[/bold]")
        console.print(f"Accuracy:  {metrics['accuracy']:.3f}")
        console.print(f"Macro F1:  {metrics['macro_f1']:.3f}\n")

        # Per-category metrics table
        table = Table(title="Per-Category Metrics")
        table.add_column("Category", style="cyan", max_width=40)
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1", justify="right")
        table.add_column("Support", justify="right")

        for category, scores in metrics["per_category"].items():
            # Shorten category names for display
            display_cat = category.split("(")[0].strip() if "(" in category else category
            table.add_row(
                display_cat,
                f"{scores['precision']:.3f}",
                f"{scores['recall']:.3f}",
                f"{scores['f1']:.3f}",
                str(scores["support"]),
            )

        console.print(table)

        # Generate misclassification report
        report_path = run_dir / "misclassifications.md"
        num_misclassified = generate_phase2_misclassification_report(predictions, report_path)

        if num_misclassified > 0:
            console.print(
                f"\n[cyan]📝 Generated misclassification report: {report_path.name} "
                f"({num_misclassified} cases)[/cyan]"
            )
        else:
            console.print("\n[green]📝 Generated report: Perfect accuracy![/green]")
    else:
        console.print("[yellow]⚠ No successful predictions to compute metrics[/yellow]")

    # Save configuration
    config_data = {
        "model_id": model,
        "prompt_version": prompt,
        "prompt_hash": prompt_hash,
        "temperature": temperature,
        "max_output_tokens": max_tokens,
        "dataset_path": str(dataset),
        "dataset_rows": len(records),
        "successful_predictions": len(predictions),
        "failed_predictions": len(records) - len(predictions),
        "git_commit": get_git_commit(),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    config_path = run_dir / "config.json"
    write_json(config_data, config_path)

    # Flush Langfuse traces
    if langfuse:
        langfuse.flush()
        console.print("\n[green]✓ Langfuse traces flushed[/green]")

    console.print(f"\n[bold green]✓ Run complete: {run_dir}[/bold green]")


@app.command("list-prompts")
def list_prompts():
    """List all available Phase 2 prompt versions."""
    prompts = list_available_prompts()

    if not prompts:
        console.print("[yellow]No prompts found in phase2/prompts/[/yellow]")
        console.print(f"Create a prompt file at: {PROJECT_ROOT}/phase2/prompts/v001.md")
        return

    table = Table(title="Available Phase 2 Prompts")
    table.add_column("Version", style="cyan")
    table.add_column("Path")

    for version in prompts:
        path = f"phase2/prompts/{version}.md"
        table.add_row(version, path)

    console.print(table)


@app.command()
def diff(
    run_a: Path = typer.Argument(..., help="Path to first predictions.jsonl"),
    run_b: Path = typer.Argument(..., help="Path to second predictions.jsonl"),
):
    """Compare predictions between two runs."""

    # Load predictions
    try:
        preds_a = read_phase2_predictions_jsonl(run_a)
        preds_b = read_phase2_predictions_jsonl(run_b)
    except Exception as e:
        console.print(f"[red]✗ Failed to load predictions: {e}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Run A: {len(preds_a)} predictions[/blue]")
    console.print(f"[blue]Run B: {len(preds_b)} predictions[/blue]\n")

    # Build lookup by ID
    lookup_a = {p["id"]: p for p in preds_a}
    lookup_b = {p["id"]: p for p in preds_b}

    # Find differences
    all_ids = sorted(set(lookup_a.keys()) | set(lookup_b.keys()))

    differences = []
    for row_id in all_ids:
        pred_a = lookup_a.get(row_id)
        pred_b = lookup_b.get(row_id)

        if pred_a and pred_b:
            cat_a = pred_a["pred"]["category"]
            cat_b = pred_b["pred"]["category"]

            if cat_a != cat_b:
                differences.append(
                    {
                        "id": row_id,
                        "gold": pred_a["gold_category"],
                        "run_a": cat_a,
                        "run_b": cat_b,
                        "subject": pred_a["subject"],
                    }
                )
        elif pred_a:
            differences.append(
                {
                    "id": row_id,
                    "gold": pred_a["gold_category"],
                    "run_a": pred_a["pred"]["category"],
                    "run_b": "MISSING",
                    "subject": pred_a["subject"],
                }
            )
        elif pred_b:
            differences.append(
                {
                    "id": row_id,
                    "gold": pred_b["gold_category"],
                    "run_a": "MISSING",
                    "run_b": pred_b["pred"]["category"],
                    "subject": pred_b["subject"],
                }
            )

    # Display differences
    if not differences:
        console.print("[green]✓ No differences found! Predictions are identical.[/green]")
        return

    table = Table(title=f"Prediction Differences ({len(differences)} total)")
    table.add_column("ID", style="cyan")
    table.add_column("Gold", max_width=30)
    table.add_column("Run A", max_width=30)
    table.add_column("Run B", max_width=30)
    table.add_column("Subject", max_width=50)

    for diff_item in differences:
        # Color code the predictions
        run_a_cat = diff_item["run_a"]
        run_b_cat = diff_item["run_b"]
        gold_cat = diff_item["gold"]

        # Highlight correct predictions in green
        if run_a_cat == gold_cat:
            run_a_cat = f"[green]{run_a_cat[:27]}...[/green]" if len(run_a_cat) > 30 else f"[green]{run_a_cat}[/green]"
        else:
            run_a_cat = run_a_cat[:27] + "..." if len(run_a_cat) > 30 else run_a_cat

        if run_b_cat == gold_cat:
            run_b_cat = f"[green]{run_b_cat[:27]}...[/green]" if len(run_b_cat) > 30 else f"[green]{run_b_cat}[/green]"
        else:
            run_b_cat = run_b_cat[:27] + "..." if len(run_b_cat) > 30 else run_b_cat

        gold_display = gold_cat[:27] + "..." if len(gold_cat) > 30 else gold_cat

        subject = diff_item["subject"]
        if len(subject) > 50:
            subject = subject[:47] + "..."

        table.add_row(
            diff_item["id"],
            gold_display,
            run_a_cat,
            run_b_cat,
            subject,
        )

    console.print(table)
    console.print(f"\n[yellow]{len(differences)} differences found[/yellow]")


if __name__ == "__main__":
    app()
