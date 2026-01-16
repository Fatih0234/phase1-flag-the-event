"""Metrics computation for classification evaluation."""
from typing import Dict, List, Any
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)
from bikeclf.config import VALID_LABELS


def compute_metrics(
    gold_labels: List[str],
    pred_labels: List[str],
) -> Dict[str, Any]:
    """Compute classification metrics for bike relevance task.

    Args:
        gold_labels: Ground truth labels
        pred_labels: Predicted labels

    Returns:
        Dictionary with metrics:
        - accuracy: Overall accuracy
        - macro_f1: Macro-averaged F1 score (treats classes equally)
        - per_class: Precision, recall, F1, and support for each class
        - confusion_matrix: 3x3 confusion matrix with labels

    Raises:
        ValueError: If label lists have different lengths
    """
    if len(gold_labels) != len(pred_labels):
        raise ValueError(
            f"Label lists must have same length. "
            f"Got gold={len(gold_labels)}, pred={len(pred_labels)}"
        )

    # Compute overall accuracy
    accuracy = accuracy_score(gold_labels, pred_labels)

    # Per-class metrics with explicit label ordering
    precision, recall, f1, support = precision_recall_fscore_support(
        gold_labels,
        pred_labels,
        labels=VALID_LABELS,
        average=None,
        zero_division=0,
    )

    # Macro F1 (average of per-class F1 scores)
    macro_f1 = f1.mean()

    # Confusion matrix (rows=gold, cols=pred)
    cm = confusion_matrix(gold_labels, pred_labels, labels=VALID_LABELS)

    # Build per-class results dictionary
    per_class = {}
    for i, label in enumerate(VALID_LABELS):
        per_class[label] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }

    return {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "per_class": per_class,
        "confusion_matrix": {
            "labels": VALID_LABELS,
            "matrix": cm.tolist(),
        },
    }
