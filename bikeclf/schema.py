"""Pydantic schemas for classification output and predictions."""
from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class ClassificationOutput(BaseModel):
    """Structured output from Gemini model for bike relevance classification (Phase 1)."""

    label: Literal["true", "false", "uncertain"] = Field(
        description="Bike relevance classification: true (bike-related), false (not bike-related), or uncertain (needs review)"
    )
    evidence: List[str] = Field(
        description="Short literal quotes from the report supporting the decision",
        min_length=0,
        max_length=10,
    )
    reasoning: str = Field(
        description="Single sentence explaining the classification logic based on evidence",
        max_length=500,
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0",
        ge=0.0,
        le=1.0,
    )

    @field_validator("evidence")
    @classmethod
    def validate_evidence_length(cls, v: List[str]) -> List[str]:
        """Ensure evidence items are short quotes (not full paragraphs)."""
        max_len = 200
        for i, item in enumerate(v):
            if len(item) > max_len:
                v[i] = item[: max_len - 3] + "..."
        return v


class Phase2ClassificationOutput(BaseModel):
    """Structured output from Gemini model for bike issue categorization (Phase 2)."""

    category: Literal[
        "Sicherheit & Komfort (Geometrie/Führung)",
        "Müll / Scherben / Splitter (Sharp objects & debris)",
        "Oberflächenqualität / Schäden",
        "Wasser / Eis / Entwässerung",
        "Hindernisse & Blockaden (inkl. Parken & Baustelle)",
        "Vegetation & Sichtbehinderung",
        "Markierungen & Beschilderung",
        "Ampeln & Signale (inkl. bike-specific Licht)",
        "Other / Unklar",
    ] = Field(
        description="Single category classification for bike-related issue"
    )
    evidence: List[str] = Field(
        description="Short literal quotes from the report supporting the categorization",
        min_length=0,
        max_length=10,
    )
    reasoning: str = Field(
        description="Single sentence explaining the categorization logic based on evidence",
        max_length=500,
    )
    confidence: float = Field(
        description="Confidence score between 0.0 and 1.0",
        ge=0.0,
        le=1.0,
    )

    @field_validator("evidence")
    @classmethod
    def validate_evidence_length(cls, v: List[str]) -> List[str]:
        """Ensure evidence items are short quotes (not full paragraphs)."""
        max_len = 200
        for i, item in enumerate(v):
            if len(item) > max_len:
                v[i] = item[: max_len - 3] + "..."
        return v


class PredictionMeta(BaseModel):
    """Metadata for a single prediction."""

    model_id: str
    prompt_version: str
    temperature: float
    max_output_tokens: int
    timestamp_utc: str
    latency_ms: int
    attempts: int = 1


class PredictionRecord(BaseModel):
    """Complete prediction record for JSONL output (Phase 1)."""

    id: str
    subject: str
    description: str
    gold_label: str
    pred: ClassificationOutput
    meta: PredictionMeta

    def to_dict(self) -> dict:
        """Convert to dictionary for JSONL serialization."""
        return self.model_dump(mode="json")


class Phase2PredictionRecord(BaseModel):
    """Complete prediction record for Phase 2 JSONL output."""

    id: str
    subject: str
    description: str
    gold_category: str  # Maps to phase2_label from eval set
    pred: Phase2ClassificationOutput
    meta: PredictionMeta

    def to_dict(self) -> dict:
        """Convert to dictionary for JSONL serialization."""
        return self.model_dump(mode="json")
