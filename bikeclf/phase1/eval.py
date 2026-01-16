"""Evaluation runner for Phase 1 classification."""
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
    RUNS_DIR,
    PROJECT_ROOT,
    SUPPORTED_MODELS,
)
from bikeclf.schema import PredictionRecord, PredictionMeta
from bikeclf.io import (
    load_dataset,
    write_predictions_jsonl,
    write_json,
    append_error_jsonl,
    read_predictions_jsonl,
)
from bikeclf.gemini_client import GeminiClient
from bikeclf.metrics import compute_metrics
from bikeclf.phase1.prompt_loader import (
    load_prompt,
    list_available_prompts,
    format_prompt,
)

app = typer.Typer(help="Phase 1: Bike relevance classification CLI")
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


def create_run_directory(prompt_version: str) -> Path:
    """Create run directory with timestamp.

    Args:
        prompt_version: Prompt version identifier (e.g., 'v001')

    Returns:
        Path to created run directory
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = RUNS_DIR / f"{timestamp}_{prompt_version}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


@app.command()
def evaluate(
    dataset: Path = typer.Option(
        PROJECT_ROOT / "bike_related_gold_dataset_A_to_F.csv",
        "--dataset",
        "-d",
        help="Path to gold standard CSV",
    ),
    prompt: str = typer.Option(..., "--prompt", "-p", help="Prompt version (e.g., v001)"),
    model: str = typer.Option(
        "gemini-2.0-flash-001",
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
    """Run evaluation on dataset with specified prompt version."""

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
    client = GeminiClient(api_config)
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
        df = load_dataset(dataset)
        console.print(f"[green]✓ Loaded dataset: {len(df)} rows[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to load dataset: {e}[/red]")
        raise typer.Exit(1)

    # Create run directory
    run_dir = create_run_directory(prompt)
    console.print(f"[blue]Run directory: {run_dir}[/blue]\n")

    # Initialize Langfuse trace
    trace = None
    if langfuse:
        trace = langfuse.trace(
            name=f"eval_{prompt}",
            metadata={
                "prompt_version": prompt,
                "model_id": model,
                "dataset_rows": len(df),
                "temperature": temperature,
            },
        )

    # Process each row
    predictions: List[PredictionRecord] = []
    errors_path = run_dir / "errors.jsonl"

    with console.status("[bold green]Processing reports...") as status:
        for idx, row in df.iterrows():
            status.update(f"Processing {row['id']} ({idx + 1}/{len(df)})")

            # Format prompt with report details
            full_prompt = format_prompt(
                system_prompt,
                row["subject"],
                row["description"],
            )

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
                    "id": row["id"],
                    "subject": row["subject"],
                    "description": row["description"],
                    "gold_label": row["gold_label"],
                    "error": error,
                    "attempts": attempts,
                    "timestamp_utc": timestamp_utc,
                }
                append_error_jsonl(error_record, errors_path)
                console.print(f"[red]✗ Failed: {row['id']} - {error}[/red]")
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

            record = PredictionRecord(
                id=row["id"],
                subject=row["subject"],
                description=row["description"],
                gold_label=row["gold_label"],
                pred=output,
                meta=meta,
            )

            predictions.append(record)

            # Langfuse trace for this classification
            if trace:
                trace.generation(
                    name=f"classify_{row['id']}",
                    model=model,
                    input=full_prompt,
                    output=output.model_dump(),
                    metadata={
                        "gold_label": row["gold_label"],
                        "pred_label": output.label,
                        "latency_ms": latency_ms,
                        "attempts": attempts,
                        "row_id": row["id"],
                    },
                )

    # Save predictions
    predictions_path = run_dir / "predictions.jsonl"
    write_predictions_jsonl(predictions, predictions_path)
    console.print(f"\n[green]✓ Saved {len(predictions)} predictions to {predictions_path.name}[/green]")

    # Compute and display metrics
    if predictions:
        gold_labels = [p.gold_label for p in predictions]
        pred_labels = [p.pred.label for p in predictions]

        metrics = compute_metrics(gold_labels, pred_labels)

        # Save metrics
        metrics_path = run_dir / "metrics.json"
        write_json(metrics, metrics_path)

        # Display metrics
        console.print("\n[bold]Classification Metrics:[/bold]")
        console.print(f"Accuracy:  {metrics['accuracy']:.3f}")
        console.print(f"Macro F1:  {metrics['macro_f1']:.3f}\n")

        # Per-class metrics table
        table = Table(title="Per-Class Metrics")
        table.add_column("Class", style="cyan")
        table.add_column("Precision", justify="right")
        table.add_column("Recall", justify="right")
        table.add_column("F1", justify="right")
        table.add_column("Support", justify="right")

        for label, scores in metrics["per_class"].items():
            table.add_row(
                label,
                f"{scores['precision']:.3f}",
                f"{scores['recall']:.3f}",
                f"{scores['f1']:.3f}",
                str(scores["support"]),
            )

        console.print(table)
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
        "dataset_rows": len(df),
        "successful_predictions": len(predictions),
        "failed_predictions": len(df) - len(predictions),
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
    """List all available prompt versions."""
    prompts = list_available_prompts()

    if not prompts:
        console.print("[yellow]No prompts found in prompts/phase1/[/yellow]")
        console.print(f"Create a prompt file at: {PROJECT_ROOT}/prompts/phase1/v001.md")
        return

    table = Table(title="Available Prompts")
    table.add_column("Version", style="cyan")
    table.add_column("Path")

    for version in prompts:
        path = f"prompts/phase1/{version}.md"
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
        preds_a = read_predictions_jsonl(run_a)
        preds_b = read_predictions_jsonl(run_b)
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
            label_a = pred_a["pred"]["label"]
            label_b = pred_b["pred"]["label"]

            if label_a != label_b:
                differences.append(
                    {
                        "id": row_id,
                        "gold": pred_a["gold_label"],
                        "run_a": label_a,
                        "run_b": label_b,
                        "subject": pred_a["subject"],
                    }
                )
        elif pred_a:
            differences.append(
                {
                    "id": row_id,
                    "gold": pred_a["gold_label"],
                    "run_a": pred_a["pred"]["label"],
                    "run_b": "MISSING",
                    "subject": pred_a["subject"],
                }
            )
        elif pred_b:
            differences.append(
                {
                    "id": row_id,
                    "gold": pred_b["gold_label"],
                    "run_a": "MISSING",
                    "run_b": pred_b["pred"]["label"],
                    "subject": pred_b["subject"],
                }
            )

    # Display differences
    if not differences:
        console.print("[green]✓ No differences found! Predictions are identical.[/green]")
        return

    table = Table(title=f"Prediction Differences ({len(differences)} total)")
    table.add_column("ID", style="cyan")
    table.add_column("Gold")
    table.add_column("Run A")
    table.add_column("Run B")
    table.add_column("Subject", max_width=50)

    for diff_item in differences:
        # Color code the predictions
        run_a_label = diff_item["run_a"]
        run_b_label = diff_item["run_b"]
        gold_label = diff_item["gold"]

        # Highlight correct predictions in green
        if run_a_label == gold_label:
            run_a_label = f"[green]{run_a_label}[/green]"
        if run_b_label == gold_label:
            run_b_label = f"[green]{run_b_label}[/green]"

        subject = diff_item["subject"]
        if len(subject) > 50:
            subject = subject[:47] + "..."

        table.add_row(
            diff_item["id"],
            gold_label,
            run_a_label,
            run_b_label,
            subject,
        )

    console.print(table)
    console.print(f"\n[yellow]{len(differences)} differences found[/yellow]")


if __name__ == "__main__":
    app()
