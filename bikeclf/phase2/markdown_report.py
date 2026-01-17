"""Generate markdown reports for Phase 2 misclassifications."""
from pathlib import Path
from typing import List
from bikeclf.schema import Phase2PredictionRecord


def generate_phase2_misclassification_report(
    predictions: List[Phase2PredictionRecord],
    output_path: Path,
) -> int:
    """Generate markdown report of misclassified Phase 2 predictions.

    Args:
        predictions: List of Phase2PredictionRecord objects
        output_path: Path to output markdown file

    Returns:
        Number of misclassified predictions
    """
    # Find misclassifications
    misclassified = [
        p for p in predictions if p.gold_category != p.pred.category
    ]

    # Write report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("# Phase 2 Misclassification Report\n\n")
        f.write(
            f"Total predictions: {len(predictions)}  \n"
            f"Misclassified: {len(misclassified)}  \n"
            f"Accuracy: {(1 - len(misclassified) / len(predictions)) * 100:.1f}%\n\n"
        )

        if not misclassified:
            f.write("✅ Perfect accuracy! No misclassifications.\n")
            return 0

        f.write("---\n\n")

        # Group by gold category for easier analysis
        by_gold = {}
        for p in misclassified:
            if p.gold_category not in by_gold:
                by_gold[p.gold_category] = []
            by_gold[p.gold_category].append(p)

        # Write each misclassification
        for gold_cat in sorted(by_gold.keys()):
            cases = by_gold[gold_cat]
            f.write(f"## Gold Category: {gold_cat}\n\n")
            f.write(f"Misclassified: {len(cases)} cases\n\n")

            for p in cases:
                f.write(f"### ID: {p.id}\n\n")
                f.write(f"**Subject:** {p.subject}\n\n")
                f.write(f"**Description:**  \n{p.description}\n\n")
                f.write(f"- **Gold Category:** {p.gold_category}\n")
                f.write(f"- **Predicted Category:** {p.pred.category}\n")
                f.write(f"- **Confidence:** {p.pred.confidence:.2f}\n")
                f.write(f"- **Reasoning:** {p.pred.reasoning}\n")

                if p.pred.evidence:
                    f.write(f"- **Evidence:**\n")
                    for ev in p.pred.evidence:
                        f.write(f"  - \"{ev}\"\n")

                f.write("\n---\n\n")

    return len(misclassified)
