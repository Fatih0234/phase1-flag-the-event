"""Tests for metrics computation."""
import pytest
from bikeclf.metrics import compute_metrics


def test_perfect_accuracy():
    """Test perfect predictions."""
    gold = ["true", "false", "uncertain"]
    pred = ["true", "false", "uncertain"]

    metrics = compute_metrics(gold, pred)

    assert metrics["accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0

    # All per-class metrics should be perfect
    for label in ["true", "false", "uncertain"]:
        assert metrics["per_class"][label]["precision"] == 1.0
        assert metrics["per_class"][label]["recall"] == 1.0
        assert metrics["per_class"][label]["f1"] == 1.0
        assert metrics["per_class"][label]["support"] == 1


def test_confusion_matrix_structure():
    """Test confusion matrix format and structure."""
    gold = ["true", "true", "false", "false", "uncertain"]
    pred = ["true", "false", "false", "true", "uncertain"]

    metrics = compute_metrics(gold, pred)

    cm = metrics["confusion_matrix"]
    assert cm["labels"] == ["true", "false", "uncertain"]
    assert len(cm["matrix"]) == 3  # 3x3 matrix
    assert len(cm["matrix"][0]) == 3
    assert len(cm["matrix"][1]) == 3
    assert len(cm["matrix"][2]) == 3

    # Check matrix is list of lists (JSON-serializable)
    assert isinstance(cm["matrix"], list)
    assert isinstance(cm["matrix"][0], list)


def test_zero_support_class():
    """Test handling of class with no examples in gold labels."""
    gold = ["true", "true", "false"]
    pred = ["true", "false", "false"]

    # No "uncertain" in gold labels
    metrics = compute_metrics(gold, pred)

    # Should not crash, metrics for "uncertain" should be 0
    assert metrics["per_class"]["uncertain"]["support"] == 0
    # With zero_division=0, precision/recall/f1 should be 0
    assert metrics["per_class"]["uncertain"]["precision"] == 0.0
    assert metrics["per_class"]["uncertain"]["recall"] == 0.0
    assert metrics["per_class"]["uncertain"]["f1"] == 0.0


def test_macro_f1_calculation():
    """Test macro F1 is average of per-class F1 scores."""
    gold = ["true"] * 10 + ["false"] * 10 + ["uncertain"] * 10
    pred = ["true"] * 10 + ["false"] * 5 + ["true"] * 5 + ["uncertain"] * 10

    metrics = compute_metrics(gold, pred)

    # Manual calculation of macro F1
    f1_scores = [
        metrics["per_class"]["true"]["f1"],
        metrics["per_class"]["false"]["f1"],
        metrics["per_class"]["uncertain"]["f1"],
    ]
    expected_macro_f1 = sum(f1_scores) / len(f1_scores)

    assert abs(metrics["macro_f1"] - expected_macro_f1) < 0.001


def test_mismatched_lengths_error():
    """Test that mismatched label list lengths raise error."""
    gold = ["true", "false"]
    pred = ["true"]  # Different length

    with pytest.raises(ValueError) as exc_info:
        compute_metrics(gold, pred)

    assert "same length" in str(exc_info.value).lower()


def test_realistic_scenario():
    """Test a realistic scenario with mixed predictions."""
    # Simulate 55 predictions similar to our dataset
    gold = (
        ["true"] * 11 + ["false"] * 9 + ["uncertain"] * 6
    )  # Distribution from dataset
    pred = (
        ["true"] * 9
        + ["uncertain"] * 2  # 11 true: 9 correct, 2 misclassified
        + ["false"] * 8
        + ["true"] * 1  # 9 false: 8 correct, 1 misclassified
        + ["uncertain"] * 5
        + ["false"] * 1  # 6 uncertain: 5 correct, 1 misclassified
    )

    metrics = compute_metrics(gold, pred)

    # Check that metrics are computed
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert 0.0 <= metrics["macro_f1"] <= 1.0

    # Check that all classes have metrics
    for label in ["true", "false", "uncertain"]:
        assert label in metrics["per_class"]
        assert "precision" in metrics["per_class"][label]
        assert "recall" in metrics["per_class"][label]
        assert "f1" in metrics["per_class"][label]
        assert "support" in metrics["per_class"][label]

    # Check support values match gold distribution
    assert metrics["per_class"]["true"]["support"] == 11
    assert metrics["per_class"]["false"]["support"] == 9
    assert metrics["per_class"]["uncertain"]["support"] == 6


def test_all_wrong():
    """Test scenario where all predictions are wrong."""
    gold = ["true", "true", "true"]
    pred = ["false", "false", "false"]

    metrics = compute_metrics(gold, pred)

    assert metrics["accuracy"] == 0.0
    # Macro F1 should be very low (likely 0)
    assert metrics["macro_f1"] <= 0.1
