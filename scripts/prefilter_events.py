"""
Apply pre-filtering rules to events before LLM classification.

This script:
1. Loads events from supabase_test_200.csv
2. Applies DEFINITELY_EXCLUDE rules based on service_name
3. Skips events without description
4. Outputs filtered dataset for LLM classification
"""

import csv
import sys
from pathlib import Path
from collections import Counter

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.supabase_config import should_check_with_llm


def load_events(csv_path: Path) -> list[dict]:
    """Load events from CSV file."""
    events = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            events.append(row)
    return events


def prefilter_events(events: list[dict]) -> dict:
    """
    Apply pre-filtering rules to events.

    Returns:
        Dict with keys:
        - to_check: Events that need LLM classification
        - skipped: Events that were filtered out
        - stats: Filtering statistics
    """
    to_check = []
    skipped = []
    skip_reasons = Counter()

    for event in events:
        should_check, reason = should_check_with_llm(
            event['service_name'],
            event['description']
        )

        if should_check:
            to_check.append(event)
        else:
            skipped.append(event)
            skip_reasons[reason] += 1

    return {
        'to_check': to_check,
        'skipped': skipped,
        'stats': {
            'total': len(events),
            'to_check': len(to_check),
            'skipped': len(skipped),
            'skip_reasons': dict(skip_reasons)
        }
    }


def save_filtered_csv(events: list[dict], output_path: Path):
    """Save filtered events to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Save with only the fields needed for bikeclf
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['id', 'subject', 'description']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for event in events:
            writer.writerow({
                'id': event['id'],
                'subject': event['subject'],
                'description': event['description']
            })

    print(f"✅ Saved {len(events)} filtered events to {output_path}")


def print_statistics(stats: dict):
    """Print filtering statistics."""
    print("\n" + "=" * 60)
    print("PRE-FILTERING STATISTICS")
    print("=" * 60)
    print(f"Total events:           {stats['total']:>6}")
    print(f"Events to check (LLM):  {stats['to_check']:>6} ({stats['to_check']/stats['total']*100:.1f}%)")
    print(f"Events skipped:         {stats['skipped']:>6} ({stats['skipped']/stats['total']*100:.1f}%)")
    print("\nSkip reasons:")
    for reason, count in sorted(stats['skip_reasons'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {reason:30} {count:>6}")
    print("=" * 60)


def main():
    """Main execution function."""
    # Paths
    input_csv = Path('data/supabase_test_200.csv')
    output_csv = Path('data/supabase_test_200_filtered.csv')

    print("=" * 60)
    print("PRE-FILTERING EVENTS")
    print("=" * 60)

    # Load events
    print(f"\nLoading events from {input_csv}...")
    events = load_events(input_csv)
    print(f"✅ Loaded {len(events)} events")

    # Apply pre-filtering
    print("\nApplying pre-filtering rules...")
    result = prefilter_events(events)

    # Print statistics
    print_statistics(result['stats'])

    # Save filtered events
    print(f"\nSaving filtered events...")
    save_filtered_csv(result['to_check'], output_csv)

    # Show sample of skipped events
    print("\n" + "=" * 60)
    print("SAMPLE OF SKIPPED EVENTS (first 5)")
    print("=" * 60)
    for i, event in enumerate(result['skipped'][:5], 1):
        desc = event['description'][:60] + '...' if len(event['description']) > 60 else event['description']
        desc = desc if desc else 'NO DESCRIPTION'
        print(f"\n{i}. ID: {event['id']}")
        print(f"   Service: {event['service_name']}")
        print(f"   Description: {desc}")

    # Show sample of events to check
    print("\n" + "=" * 60)
    print("SAMPLE OF EVENTS TO CHECK WITH LLM (first 5)")
    print("=" * 60)
    for i, event in enumerate(result['to_check'][:5], 1):
        desc = event['description'][:60] + '...' if len(event['description']) > 60 else event['description']
        desc = desc if desc else 'NO DESCRIPTION'
        print(f"\n{i}. ID: {event['id']}")
        print(f"   Service: {event['service_name']}")
        print(f"   Description: {desc}")

    print("\n" + "=" * 60)
    print(f"NEXT STEP: Run classification on {output_csv}")
    print("=" * 60)


if __name__ == "__main__":
    main()
