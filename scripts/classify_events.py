"""
Classify events using Gemini 2.5 Flash Lite.

This script runs classification without requiring gold labels.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime
import csv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bikeclf.config import APIConfig
from bikeclf.gemini_client import GeminiClient
from bikeclf.phase1.prompt_loader import load_prompt, format_prompt
from bikeclf.io import write_predictions_jsonl, write_json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn

console = Console()
MAX_EVIDENCE_CHARS = 180


def load_csv_events(csv_path: Path) -> list[dict]:
    """Load events from CSV file."""
    events = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events


def truncate_evidence(evidence: list[str]) -> list[str]:
    """Cap evidence snippet length to avoid validation failures."""
    truncated = []
    for snippet in evidence or []:
        if len(snippet) > MAX_EVIDENCE_CHARS:
            truncated.append(snippet[:MAX_EVIDENCE_CHARS - 3] + "...")
        else:
            truncated.append(snippet)
    return truncated


def classify_events(
    events: list[dict],
    prompt_version: str,
    model: str,
    temperature: float = 0.0
) -> tuple[list[dict], Path]:
    """
    Classify events using Gemini.

    Returns:
        Tuple of (predictions, run_dir)
    """
    # Load prompt
    console.print(f"[bold blue]Loading prompt {prompt_version}...[/bold blue]")
    system_prompt, prompt_hash = load_prompt(prompt_version)
    console.print(f"✓ Loaded prompt (hash: {prompt_hash})")

    # Initialize Gemini client
    api_config = APIConfig()
    api_config.validate_required()
    client = GeminiClient(config=api_config)
    console.print(f"✓ Initialized Gemini client (model: {model})")

    # Create run directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short = model.replace('gemini-', '').replace('-', '_')
    run_name = f"{timestamp}_{prompt_version}_{model_short}"
    run_dir = Path("runs") / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"✓ Created run directory: {run_dir}")

    # Save run config
    config_data = {
        "prompt_version": prompt_version,
        "prompt_hash": prompt_hash,
        "model": model,
        "temperature": temperature,
        "timestamp": timestamp,
        "total_events": len(events)
    }
    write_json(config_data, run_dir / "config.json")

    # Classify events
    predictions = []
    errors = []

    console.print(f"\n[bold green]Classifying {len(events)} events...[/bold green]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Processing events...", total=len(events))

        for i, event in enumerate(events):
            # Format prompt with event data
            messages = format_prompt(
                system_prompt=system_prompt,
                subject=event['subject'],
                description=event['description']
            )

            # Classify with retry logic
            output, latency_ms, attempts, error = client.classify_with_retry(
                prompt=messages,
                model_id=model,
                temperature=temperature
            )

            if output:
                # Create prediction record
                prediction = {
                    'id': event['id'],
                    'subject': event['subject'],
                    'description': event['description'],
                    'pred': {
                        'label': output.label,
                        'evidence': truncate_evidence(output.evidence),
                        'reasoning': output.reasoning,
                        'confidence': output.confidence
                    },
                    'meta': {
                        'model_id': model,
                        'prompt_version': prompt_version,
                        'prompt_hash': prompt_hash,
                        'temperature': temperature,
                        'latency_ms': latency_ms,
                        'attempts': attempts,
                        'timestamp': datetime.now().isoformat()
                    }
                }
                predictions.append(prediction)
            else:
                # Record error
                errors.append({
                    'id': event['id'],
                    'error': error,
                    'timestamp': datetime.now().isoformat()
                })

            # Update progress
            progress.update(task, advance=1)

            # Rate limiting (10 per second)
            time.sleep(0.1)

    # Save predictions
    console.print(f"\n[bold blue]Saving results...[/bold blue]")
    # Save predictions as JSONL manually since write_predictions_jsonl expects Pydantic objects
    with open(run_dir / "predictions.jsonl", 'w', encoding='utf-8') as f:
        for pred in predictions:
            f.write(json.dumps(pred, ensure_ascii=False) + '\n')
    console.print(f"✓ Saved {len(predictions)} predictions to {run_dir / 'predictions.jsonl'}")

    # Save errors if any
    if errors:
        with open(run_dir / "errors.jsonl", 'w') as f:
            for error in errors:
                f.write(json.dumps(error) + '\n')
        console.print(f"⚠ Saved {len(errors)} errors to {run_dir / 'errors.jsonl'}")

    # Print summary
    label_counts = {'true': 0, 'false': 0, 'uncertain': 0}
    for pred in predictions:
        label_counts[pred['pred']['label']] += 1

    console.print(f"\n[bold green]Classification Complete![/bold green]")
    console.print(f"  Total events: {len(events)}")
    console.print(f"  Successful:   {len(predictions)}")
    console.print(f"  Errors:       {len(errors)}")
    console.print(f"\n[bold]Label Distribution:[/bold]")
    console.print(f"  TRUE:         {label_counts['true']} ({label_counts['true']/len(predictions)*100:.1f}%)")
    console.print(f"  FALSE:        {label_counts['false']} ({label_counts['false']/len(predictions)*100:.1f}%)")
    console.print(f"  UNCERTAIN:    {label_counts['uncertain']} ({label_counts['uncertain']/len(predictions)*100:.1f}%)")

    return predictions, run_dir


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(description="Classify events using Gemini")
    parser.add_argument("--dataset", required=True, help="Path to CSV file with events")
    parser.add_argument("--prompt", default="v003", help="Prompt version (default: v003)")
    parser.add_argument("--model", default="gemini-2.5-flash-lite", help="Model to use")
    parser.add_argument("--temperature", type=float, default=0.0, help="Temperature (default: 0.0)")

    args = parser.parse_args()

    # Load events
    console.print(f"[bold blue]Loading events from {args.dataset}...[/bold blue]")
    events = load_csv_events(Path(args.dataset))
    console.print(f"✓ Loaded {len(events)} events")

    # Classify
    predictions, run_dir = classify_events(
        events=events,
        prompt_version=args.prompt,
        model=args.model,
        temperature=args.temperature
    )

    console.print(f"\n[bold green]Results saved to: {run_dir}[/bold green]")


if __name__ == "__main__":
    main()
