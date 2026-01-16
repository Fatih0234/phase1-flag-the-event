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


# Supported Gemini model identifiers
# Add new models here to make them available system-wide
SUPPORTED_MODELS = [
    # Gemini 2.0 Flash family
    "gemini-2.0-flash-001",      # Stable version (2.0)
    "gemini-2.0-flash",          # Latest version (2.0)
    "gemini-2.0-flash-exp",      # Experimental version (2.0)

    # Gemini 2.5 Flash family
    "gemini-2.5-flash-lite",     # Lightweight fast version (2.5)
    "gemini-2.5-flash",          # Latest version (2.5)
]

# Model display names for better readability
MODEL_DISPLAY_NAMES = {
    "gemini-2.0-flash-001": "Gemini 2.0 Flash (Stable)",
    "gemini-2.0-flash": "Gemini 2.0 Flash (Latest)",
    "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental)",
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
    "gemini-2.5-flash": "Gemini 2.5 Flash",
}

def get_model_short_name(model_id: str) -> str:
    """Get a short name for model ID suitable for file naming.

    Args:
        model_id: Full model identifier

    Returns:
        Short model name for file naming (e.g., '2.0-flash', '2.5-lite')
    """
    # Extract version and variant
    if "gemini-" in model_id:
        parts = model_id.replace("gemini-", "").split("-")
        # Reconstruct: version + key parts
        if "2.0" in model_id:
            if "exp" in model_id:
                return "2.0-flash-exp"
            elif "001" in model_id:
                return "2.0-flash-001"
            else:
                return "2.0-flash"
        elif "2.5" in model_id:
            if "lite" in model_id:
                return "2.5-lite"
            else:
                return "2.5-flash"
    return model_id  # Fallback to full ID

# Valid classification labels
VALID_LABELS = ["true", "false", "uncertain"]
