"""Configuration management for bikeclf system."""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PROMPTS_DIR = PROJECT_ROOT / "prompts" / "phase1"
RUNS_DIR = PROJECT_ROOT / "runs"


class APIConfig(BaseModel):
    """Google Gen AI API configuration."""

    api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    default_model: str = "gemini-2.0-flash-001"
    default_temperature: float = 0.0
    default_max_tokens: int = 512

    def validate_required(self) -> None:
        """Ensure required credentials are present."""
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found. "
                "Set it in .env file or as environment variable.\n"
                "Get your API key from: https://aistudio.google.com/apikey"
            )


class LangfuseConfig(BaseModel):
    """Langfuse tracing configuration."""

    public_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY")
    )
    secret_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY")
    )
    host: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    )

    def is_enabled(self) -> bool:
        """Check if Langfuse tracing is configured."""
        return bool(self.public_key and self.secret_key)


# Supported model identifiers
SUPPORTED_MODELS = [
    "gemini-2.0-flash-001",  # Stable version
    "gemini-2.0-flash",      # Latest version
    "gemini-2.0-flash-exp",  # Experimental version
]

# Valid classification labels
VALID_LABELS = ["true", "false", "uncertain"]
