#!/usr/bin/env python3
"""Standalone script to generate markdown report for an existing run."""
import sys
from pathlib import Path
from bikeclf.io import read_predictions_jsonl
from bikeclf.markdown_report import generate_misclassification_report
from bikeclf.schema import PredictionRecord


def main():
    """Generate markdown report for existing run."""
    if len(sys.argv) != 2:
        print("Usage: python generate_report_for_run.py <run_directory>")
        print("\nExample:")
        print("  python generate_report_for_run.py runs/20260116_135146_v001")
        sys.exit(1)

    run_dir = Path(sys.argv[1])

    if not run_dir.exists():
        print(f"Error: Run directory not found: {run_dir}")
        sys.exit(1)

    predictions_path = run_dir / "predictions.jsonl"
    if not predictions_path.exists():
        print(f"Error: predictions.jsonl not found in {run_dir}")
        sys.exit(1)

    # Load predictions
    print(f"Loading predictions from {predictions_path}...")
    pred_dicts = read_predictions_jsonl(predictions_path)

    # Convert to PredictionRecord objects
    predictions = []
    for pred_dict in pred_dicts:
        # Reconstruct the PredictionRecord
        from bikeclf.schema import ClassificationOutput, PredictionMeta

        pred = PredictionRecord(
            id=pred_dict["id"],
            subject=pred_dict["subject"],
            description=pred_dict["description"],
            gold_label=pred_dict["gold_label"],
            pred=ClassificationOutput(**pred_dict["pred"]),
            meta=PredictionMeta(**pred_dict["meta"]),
        )
        predictions.append(pred)

    # Generate report
    report_path = run_dir / "misclassifications.md"
    print(f"Generating report to {report_path}...")

    num_misclassified = generate_misclassification_report(predictions, report_path)

    if num_misclassified > 0:
        print(f"✓ Generated report with {num_misclassified} misclassified cases")
    else:
        print("✓ Generated report: Perfect accuracy!")

    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
