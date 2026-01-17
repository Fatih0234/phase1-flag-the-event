"""Phase 2 specific configuration."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
PHASE2_PROMPTS_DIR = PROJECT_ROOT / "phase2" / "prompts"
PHASE2_RUNS_DIR = PROJECT_ROOT / "phase2" / "runs"

# Valid Phase 2 categories (must match schema exactly)
VALID_CATEGORIES = [
    "Sicherheit & Komfort (Geometrie/Führung)",
    "Müll / Scherben / Splitter (Sharp objects & debris)",
    "Oberflächenqualität / Schäden",
    "Wasser / Eis / Entwässerung",
    "Hindernisse & Blockaden (inkl. Parken & Baustelle)",
    "Vegetation & Sichtbehinderung",
    "Markierungen & Beschilderung",
    "Ampeln & Signale (inkl. bike-specific Licht)",
    "Other / Unklar",
]
