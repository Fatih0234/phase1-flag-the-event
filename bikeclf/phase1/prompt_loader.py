"""Prompt versioning and loading for Phase 1."""
import hashlib
from pathlib import Path
from typing import List, Tuple
from bikeclf.config import PROMPTS_DIR


def list_available_prompts() -> List[str]:
    """List all available prompt versions.

    Returns:
        Sorted list of version identifiers (e.g., ['v001', 'v002', 'v003'])
    """
    if not PROMPTS_DIR.exists():
        return []

    prompt_files = sorted(PROMPTS_DIR.glob("v*.md"))
    return [f.stem for f in prompt_files]


def load_prompt(version: str) -> Tuple[str, str]:
    """Load a specific prompt version.

    Args:
        version: Version identifier (e.g., 'v001')

    Returns:
        Tuple of (prompt_content, content_hash):
        - prompt_content: Full text of the prompt
        - content_hash: Short SHA-256 hash (12 chars) for tracking

    Raises:
        FileNotFoundError: If prompt version doesn't exist
    """
    prompt_path = PROMPTS_DIR / f"{version}.md"

    if not prompt_path.exists():
        available = list_available_prompts()
        raise FileNotFoundError(
            f"Prompt version '{version}' not found at {prompt_path}\n"
            f"Available versions: {available if available else 'none'}\n"
            f"Create a prompt file at: {PROMPTS_DIR}/{version}.md"
        )

    content = prompt_path.read_text(encoding="utf-8")

    # Compute SHA-256 hash for tracking (use short version)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]

    return content, content_hash


def format_prompt(
    system_prompt: str,
    subject: str,
    description: str,
) -> str:
    """Format prompt with report details.

    Args:
        system_prompt: Base system prompt from version file
        subject: Report subject line
        description: Report description text

    Returns:
        Complete formatted prompt with system instructions and user message
    """
    user_message = (
        f"**Betreff:** {subject}\n\n" f"**Beschreibung:** {description}"
    )

    return f"{system_prompt}\n\n{user_message}"
