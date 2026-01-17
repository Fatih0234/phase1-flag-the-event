"""I/O utilities for Phase 2 evaluation."""
import json
from pathlib import Path
from typing import List, Dict, Any
from bikeclf.schema import Phase2PredictionRecord


def load_phase2_eval_set(jsonl_path: Path) -> List[Dict[str, Any]]:
    """Load Phase 2 evaluation set from JSONL.

    Args:
        jsonl_path: Path to phase2-eval-set.jsonl

    Returns:
        List of evaluation examples

    Raises:
        FileNotFoundError: If eval set file doesn't exist
        ValueError: If JSON parsing fails or required fields are missing
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Eval set not found: {jsonl_path}")

    records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    record = json.loads(line)
                    # Validate required fields
                    required = ["id", "subject", "description", "phase2_label"]
                    missing = [f for f in required if f not in record]
                    if missing:
                        raise ValueError(f"Missing fields: {missing}")
                    records.append(record)
                except json.JSONDecodeError as e:
                    # Log error but continue (some lines may be corrupted)
                    print(f"Warning: Invalid JSON at line {line_num}, skipping: {e}")
                    continue

    return records


def write_phase2_predictions_jsonl(
    records: List[Phase2PredictionRecord],
    output_path: Path
) -> None:
    """Write Phase 2 prediction records to JSONL file.

    Args:
        records: List of Phase2PredictionRecord objects
        output_path: Path to output JSONL file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write("\n")


def read_phase2_predictions_jsonl(jsonl_path: Path) -> List[Dict[str, Any]]:
    """Read Phase 2 predictions from JSONL file.

    Args:
        jsonl_path: Path to predictions JSONL file

    Returns:
        List of prediction dictionaries
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Predictions file not found: {jsonl_path}")

    predictions = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                predictions.append(json.loads(line))

    return predictions
