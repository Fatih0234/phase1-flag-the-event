"""I/O utilities for reading datasets and writing artifacts."""
import json
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from bikeclf.schema import PredictionRecord


def load_dataset(csv_path: Path) -> pd.DataFrame:
    """Load gold standard dataset from CSV.

    Args:
        csv_path: Path to CSV file

    Returns:
        DataFrame with required columns

    Raises:
        ValueError: If required columns are missing
        FileNotFoundError: If CSV file doesn't exist
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path, encoding="utf-8")

    required_cols = ["id", "subject", "description", "gold_label"]
    missing = set(required_cols) - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required columns in dataset: {missing}\n"
            f"Found columns: {list(df.columns)}"
        )

    return df


def write_predictions_jsonl(
    records: List[PredictionRecord], output_path: Path
) -> None:
    """Write prediction records to JSONL file.

    Args:
        records: List of prediction records
        output_path: Path to output JSONL file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for record in records:
            json.dump(record.to_dict(), f, ensure_ascii=False)
            f.write("\n")


def write_json(data: Dict[str, Any], output_path: Path) -> None:
    """Write dictionary to formatted JSON file.

    Args:
        data: Dictionary to serialize
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_error_jsonl(error_record: Dict[str, Any], output_path: Path) -> None:
    """Append error record to errors.jsonl file.

    Args:
        error_record: Dictionary with error details
        output_path: Path to errors.jsonl file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("a", encoding="utf-8") as f:
        json.dump(error_record, f, ensure_ascii=False)
        f.write("\n")


def read_predictions_jsonl(jsonl_path: Path) -> List[Dict[str, Any]]:
    """Read prediction records from JSONL file.

    Args:
        jsonl_path: Path to JSONL file

    Returns:
        List of prediction dictionaries

    Raises:
        FileNotFoundError: If JSONL file doesn't exist
    """
    if not jsonl_path.exists():
        raise FileNotFoundError(f"Predictions file not found: {jsonl_path}")

    records = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise ValueError(
                        f"Invalid JSON at line {line_num} in {jsonl_path}: {e}"
                    )
    return records
