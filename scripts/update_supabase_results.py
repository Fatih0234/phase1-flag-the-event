"""
Update Supabase events table with classification results.

This script:
1. Reads classification results from predictions.jsonl
2. Generates SQL UPDATE statements
3. Outputs SQL file for manual execution or applies via Supabase MCP
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.supabase_config import SUPABASE_PROJECT_ID


def load_predictions(jsonl_path: Path) -> list[dict]:
    """Load predictions from JSONL file."""
    predictions = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                predictions.append(json.loads(line))
    return predictions


def generate_update_sql(predictions: list[dict]) -> str:
    """
    Generate SQL UPDATE statements for all predictions.

    Args:
        predictions: List of prediction dicts

    Returns:
        SQL statements as string
    """
    sql_statements = []

    # Header
    sql_statements.append("-- Bike Classification Results Update")
    sql_statements.append(f"-- Generated: {datetime.now().isoformat()}")
    sql_statements.append(f"-- Total predictions: {len(predictions)}")
    sql_statements.append("")

    for pred in predictions:
        event_id = pred['id']
        label = pred['pred']['label']
        confidence = pred['pred']['confidence']
        evidence = pred['pred']['evidence']
        reasoning = pred['pred']['reasoning']

        # Map label to bike_related value
        # true -> TRUE, false -> FALSE, uncertain -> NULL
        if label == 'true':
            bike_related = 'TRUE'
        elif label == 'false':
            bike_related = 'FALSE'
        else:  # uncertain
            bike_related = 'NULL'

        # Escape single quotes in evidence and reasoning
        evidence_str = [e.replace("'", "''") for e in evidence]
        reasoning_escaped = reasoning.replace("'", "''")

        # Build ARRAY literal for evidence
        evidence_array = "ARRAY[" + ", ".join(f"'{e}'" for e in evidence_str) + "]"

        # Generate UPDATE statement
        sql = f"""UPDATE events SET
    bike_related = {bike_related},
    bike_confidence = {confidence},
    bike_evidence = {evidence_array},
    bike_reasoning = '{reasoning_escaped}'
WHERE service_request_id = '{event_id}';
"""
        sql_statements.append(sql)

    return '\n'.join(sql_statements)


def save_sql_file(sql: str, output_path: Path):
    """Save SQL statements to file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sql)
    print(f"✅ Saved SQL statements to {output_path}")


def generate_summary_stats(predictions: list[dict]) -> dict:
    """Generate summary statistics from predictions."""
    stats = {
        'total': len(predictions),
        'true': 0,
        'false': 0,
        'uncertain': 0
    }

    for pred in predictions:
        label = pred['pred']['label']
        stats[label] += 1

    return stats


def print_summary(stats: dict):
    """Print summary statistics."""
    print("\n" + "=" * 60)
    print("CLASSIFICATION SUMMARY")
    print("=" * 60)
    print(f"Total events classified: {stats['total']}")
    print(f"  TRUE (bike-related):   {stats['true']:3d} ({stats['true']/stats['total']*100:5.1f}%)")
    print(f"  FALSE (not bike):      {stats['false']:3d} ({stats['false']/stats['total']*100:5.1f}%)")
    print(f"  UNCERTAIN (review):    {stats['uncertain']:3d} ({stats['uncertain']/stats['total']*100:5.1f}%)")
    print("=" * 60)


def main():
    """Main execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate SQL to update Supabase with classification results"
    )
    parser.add_argument(
        "--predictions",
        required=True,
        help="Path to predictions.jsonl file"
    )
    parser.add_argument(
        "--output",
        default="migrations/update_bike_classifications.sql",
        help="Output SQL file path"
    )

    args = parser.parse_args()

    # Load predictions
    predictions_path = Path(args.predictions)
    print(f"Loading predictions from {predictions_path}...")
    predictions = load_predictions(predictions_path)
    print(f"✅ Loaded {len(predictions)} predictions")

    # Generate summary stats
    stats = generate_summary_stats(predictions)
    print_summary(stats)

    # Generate SQL
    print("\nGenerating SQL UPDATE statements...")
    sql = generate_update_sql(predictions)

    # Save to file
    output_path = Path(args.output)
    save_sql_file(sql, output_path)

    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print(f"1. Review the SQL file: {output_path}")
    print(f"2. Run the migration on Supabase:")
    print(f"   - Option A: Copy SQL and run in Supabase SQL Editor")
    print(f"   - Option B: Use Supabase CLI: supabase db execute -f {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
