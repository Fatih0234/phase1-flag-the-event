"""Metrics computation for Phase 2 (9-way classification)."""
from typing import Dict, List, Any
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
)
from bikeclf.phase2.config import VALID_CATEGORIES


def compute_phase2_metrics(
    gold_categories: List[str],
    pred_categories: List[str],
) -> Dict[str, Any]:
    """Compute classification metrics for Phase 2 (9 categories).

    Args:
        gold_categories: List of gold standard category labels
        pred_categories: List of predicted category labels

    Returns:
        Dictionary containing:
        - accuracy: Overall accuracy score
        - macro_f1: Macro-averaged F1 score
        - per_category: Dict mapping each category to precision/recall/F1/support
        - confusion_matrix: Dict with category labels and matrix

    Raises:
        ValueError: If input lists have different lengths
    """
    if len(gold_categories) != len(pred_categories):
        raise ValueError(
            f"Category lists must have same length. "
            f"Got gold={len(gold_categories)}, pred={len(pred_categories)}"
        )

    # Overall accuracy
    accuracy = accuracy_score(gold_categories, pred_categories)

    # Per-category metrics (precision, recall, F1, support)
    precision, recall, f1, support = precision_recall_fscore_support(
        gold_categories,
        pred_categories,
        labels=VALID_CATEGORIES,
        average=None,
        zero_division=0,
    )

    # Macro F1 (average across categories)
    macro_f1 = f1.mean()

    # Confusion matrix
    cm = confusion_matrix(gold_categories, pred_categories, labels=VALID_CATEGORIES)

    # Build per-category dict
    per_category = {}
    for i, category in enumerate(VALID_CATEGORIES):
        per_category[category] = {
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
            "support": int(support[i]),
        }

    return {
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "per_category": per_category,
        "confusion_matrix": {
            "categories": VALID_CATEGORIES,
            "matrix": cm.tolist(),
        },
    }
