"""Tests for Pydantic schema validation."""
import pytest
from pydantic import ValidationError
from bikeclf.schema import ClassificationOutput, PredictionRecord, PredictionMeta


def test_classification_output_valid():
    """Test valid classification output."""
    output = ClassificationOutput(
        label="true",
        evidence=["Radweg wird blockiert"],
        reasoning="Explizite Erwähnung von Radweg-Blockade.",
        confidence=0.95,
    )
    assert output.label == "true"
    assert len(output.evidence) == 1
    assert output.confidence == 0.95


def test_classification_output_invalid_label():
    """Test invalid label raises validation error."""
    with pytest.raises(ValidationError):
        ClassificationOutput(
            label="maybe",  # Invalid - must be 'true', 'false', or 'uncertain'
            evidence=[],
            reasoning="Test",
            confidence=0.5,
        )


def test_classification_output_confidence_bounds():
    """Test confidence must be in [0, 1]."""
    # Test too high
    with pytest.raises(ValidationError):
        ClassificationOutput(
            label="true",
            evidence=[],
            reasoning="Test",
            confidence=1.5,  # Too high
        )

    # Test too low
    with pytest.raises(ValidationError):
        ClassificationOutput(
            label="true",
            evidence=[],
            reasoning="Test",
            confidence=-0.1,  # Too low
        )

    # Test valid boundaries
    output_min = ClassificationOutput(
        label="true", evidence=[], reasoning="Test", confidence=0.0
    )
    assert output_min.confidence == 0.0

    output_max = ClassificationOutput(
        label="true", evidence=[], reasoning="Test", confidence=1.0
    )
    assert output_max.confidence == 1.0


def test_evidence_too_long():
    """Test evidence items must be reasonably short."""
    with pytest.raises(ValidationError) as exc_info:
        ClassificationOutput(
            label="true",
            evidence=["x" * 300],  # Too long (>200 chars)
            reasoning="Test",
            confidence=0.8,
        )
    assert "Evidence quote too long" in str(exc_info.value)


def test_evidence_empty_allowed():
    """Test that empty evidence list is allowed."""
    output = ClassificationOutput(
        label="uncertain",
        evidence=[],  # Empty is valid
        reasoning="Keine klare Evidenz gefunden.",
        confidence=0.3,
    )
    assert len(output.evidence) == 0


def test_reasoning_max_length():
    """Test reasoning must be under 500 characters."""
    with pytest.raises(ValidationError):
        ClassificationOutput(
            label="true",
            evidence=[],
            reasoning="x" * 501,  # Too long
            confidence=0.8,
        )


def test_prediction_record_serialization():
    """Test prediction record can be serialized to dict."""
    output = ClassificationOutput(
        label="false",
        evidence=[],
        reasoning="Kein Radbezug erkennbar.",
        confidence=0.9,
    )

    meta = PredictionMeta(
        model_id="gemini-2.0-flash-001",
        prompt_version="v001",
        temperature=0.0,
        max_output_tokens=512,
        timestamp_utc="2026-01-16T12:00:00Z",
        latency_ms=1234,
    )

    record = PredictionRecord(
        id="A-01",
        subject="Test Subject",
        description="Test description",
        gold_label="false",
        pred=output,
        meta=meta,
    )

    data = record.to_dict()
    assert data["id"] == "A-01"
    assert data["pred"]["label"] == "false"
    assert data["meta"]["latency_ms"] == 1234
    assert data["meta"]["attempts"] == 1  # Default value


def test_all_three_labels():
    """Test all three valid labels."""
    for label in ["true", "false", "uncertain"]:
        output = ClassificationOutput(
            label=label,
            evidence=[],
            reasoning="Test reasoning.",
            confidence=0.8,
        )
        assert output.label == label
