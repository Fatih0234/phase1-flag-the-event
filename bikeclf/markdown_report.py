"""Generate markdown reports for misclassified predictions."""
from pathlib import Path
from typing import List
from bikeclf.schema import PredictionRecord


def generate_misclassification_report(
    predictions: List[PredictionRecord],
    output_path: Path,
) -> int:
    """Generate a markdown report of all misclassified predictions.

    Args:
        predictions: List of prediction records
        output_path: Path to output markdown file

    Returns:
        Number of misclassified cases written
    """
    # Filter misclassified predictions
    misclassified = [
        p for p in predictions if p.gold_label != p.pred.label
    ]

    if not misclassified:
        # Create report noting perfect accuracy
        content = "# Misclassification Report\n\n"
        content += "## Summary\n\n"
        content += "✅ **Perfect accuracy!** No misclassifications found.\n\n"
        content += f"- Total predictions: {len(predictions)}\n"
        content += "- Correct predictions: 100%\n"

        output_path.write_text(content, encoding="utf-8")
        return 0

    # Build markdown report
    content = "# Misclassification Report\n\n"

    # Summary section
    content += "## Summary\n\n"
    content += f"- **Total predictions**: {len(predictions)}\n"
    content += f"- **Correct predictions**: {len(predictions) - len(misclassified)}\n"
    content += f"- **Misclassified**: {len(misclassified)}\n"
    content += f"- **Accuracy**: {(len(predictions) - len(misclassified)) / len(predictions):.1%}\n\n"

    # Error breakdown
    error_types = {}
    for pred in misclassified:
        error_type = f"{pred.gold_label} → {pred.pred.label}"
        error_types[error_type] = error_types.get(error_type, 0) + 1

    content += "### Error Breakdown\n\n"
    for error_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
        content += f"- **{error_type}**: {count} cases\n"
    content += "\n---\n\n"

    # Individual cases
    content += "## Misclassified Cases\n\n"

    for i, pred in enumerate(misclassified, 1):
        content += f"### {i}. Case {pred.id}\n\n"

        # Labels with emoji indicators
        gold_emoji = _get_label_emoji(pred.gold_label)
        pred_emoji = _get_label_emoji(pred.pred.label)

        content += f"**Gold Label**: {gold_emoji} `{pred.gold_label}`  \n"
        content += f"**Predicted Label**: {pred_emoji} `{pred.pred.label}`  \n"
        content += f"**Confidence**: {pred.pred.confidence:.2f}  \n"
        content += f"**Attempts**: {pred.meta.attempts}  \n\n"

        # Subject
        content += f"**Subject:**\n"
        content += f"> {pred.subject}\n\n"

        # Description
        content += f"**Description:**\n"
        content += f"> {pred.description}\n\n"

        # Model's reasoning
        content += f"**Model's Reasoning:**\n"
        content += f"> {pred.pred.reasoning}\n\n"

        # Evidence (if any)
        if pred.pred.evidence:
            content += f"**Evidence Extracted:**\n"
            for evidence in pred.pred.evidence:
                content += f"> - {evidence}\n"
            content += "\n"
        else:
            content += f"**Evidence Extracted:** _(None)_\n\n"

        # Metadata
        content += f"**Metadata:**\n"
        content += f"- Text length: {len(pred.description)} chars\n"
        content += f"- Latency: {pred.meta.latency_ms} ms\n"
        content += f"- Model: {pred.meta.model_id}\n"
        content += f"- Prompt version: {pred.meta.prompt_version}\n\n"

        content += "---\n\n"

    # Write to file
    output_path.write_text(content, encoding="utf-8")

    return len(misclassified)


def _get_label_emoji(label: str) -> str:
    """Get emoji for label type.

    Args:
        label: Label string

    Returns:
        Emoji string
    """
    emoji_map = {
        "true": "✅",
        "false": "❌",
        "uncertain": "❓",
    }
    return emoji_map.get(label, "•")
