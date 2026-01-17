"""
Run Phase 2 Supabase pipeline: fetch bike_related=true events -> classify into 9 categories -> write-back.

This script:
1. Fetches events where bike_related = true
2. Classifies each into one of 9 bike issue categories
3. Writes results to bike_issue_* columns in Supabase

Supports:
- Batch processing with configurable batch size
- Row limit for testing (--limit flag)
- Resume from last processed ID (checkpoint file)
- Only process unclassified events (bike_issue_category IS NULL)
"""
import json
import os
import sys
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request, parse, error

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bikeclf.config import APIConfig, SUPPORTED_MODELS
from bikeclf.phase2.gemini_client import Phase2GeminiClient
from bikeclf.phase2.prompt_loader import load_prompt, format_prompt
from bikeclf.io import write_json


DEFAULT_BATCH_SIZE = 100
DEFAULT_SLEEP_SECONDS = 0.1
CHECKPOINT_FILE = Path(__file__).parent.parent / "phase2" / "checkpoint_supabase.json"


class SupabaseClient:
    """Minimal Supabase REST API client."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def request_json(
        self,
        method: str,
        path: str,
        params: dict[str, str] | None = None,
        body: Any | None = None,
        headers: dict[str, str] | None = None,
        retries: int = 3,
        retry_delay: float = 2.0,
    ) -> Any:
        """Make HTTP request with retries."""
        url = f"{self.base_url}{path}"
        if params:
            query = parse.urlencode(params, safe=",()")
            url = f"{url}?{query}"

        data = None
        if body is not None:
            data = json.dumps(body).encode("utf-8")

        req = request.Request(url, data=data, method=method)
        req.add_header("apikey", self.api_key)
        req.add_header("Authorization", f"Bearer {self.api_key}")
        req.add_header("Content-Type", "application/json")
        req.add_header("Prefer", "return=minimal")  # Don't return updated rows
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        last_error = None
        for attempt in range(retries):
            try:
                with request.urlopen(req, timeout=60) as resp:
                    payload = resp.read().decode("utf-8")
                    return json.loads(payload) if payload else None
            except error.HTTPError as exc:
                detail = exc.read().decode("utf-8")
                last_error = f"HTTP {exc.code}: {detail}"
                if exc.code >= 500 and attempt < retries - 1:
                    # Retry on server errors
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise RuntimeError(f"Supabase API error: {last_error}") from exc
            except Exception as exc:
                last_error = str(exc)
                if attempt < retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                raise

        raise RuntimeError(f"Failed after {retries} attempts: {last_error}")


def load_env(name: str) -> str:
    """Load required environment variable."""
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def build_subject(event: dict) -> str:
    """Build subject from category + subcategory + subcategory2.

    Args:
        event: Event dict with category, subcategory, subcategory2 fields

    Returns:
        Combined subject string (handles NULL values)
    """
    parts = [event.get("category")]

    sub1 = event.get("subcategory")
    if sub1 and sub1.upper() != "NULL":
        parts.append(sub1)

    sub2 = event.get("subcategory2")
    if sub2 and sub2.upper() != "NULL":
        parts.append(sub2)

    return " - ".join(p for p in parts if p)


def fetch_events(
    client: SupabaseClient,
    batch_size: int,
    last_id: str | None,
    only_unclassified: bool,
) -> list[dict]:
    """Fetch a batch of bike_related=true events.

    Args:
        client: Supabase client
        batch_size: Number of rows to fetch
        last_id: Last processed service_request_id (for pagination)
        only_unclassified: If True, only fetch events where bike_issue_category IS NULL

    Returns:
        List of event dicts
    """
    params = {
        "select": "service_request_id,category,subcategory,subcategory2,description",
        "bike_related": "eq.true",  # Only bike-related events
        "order": "service_request_id",
        "limit": str(batch_size),
    }

    if last_id:
        params["service_request_id"] = f"gt.{last_id}"

    if only_unclassified:
        params["bike_issue_category"] = "is.null"

    return client.request_json("GET", "/rest/v1/events", params=params)


def classify_batch(
    client: Phase2GeminiClient,
    system_prompt: str,
    prompt_hash: str,
    events: list[dict],
    prompt_version: str,
    model: str,
    temperature: float,
    sleep_seconds: float,
) -> tuple[list[dict], list[dict]]:
    """Classify a batch of events into Phase 2 categories.

    Returns:
        Tuple of (predictions, errors)
    """
    predictions = []
    errors = []
    total = len(events)

    for idx, event in enumerate(events, start=1):
        # Build subject from category fields
        subject = build_subject(event)
        description = event.get("description", "")

        if not description:
            print(f"  [{idx}/{total}] Skipping {event['service_request_id']}: No description")
            continue

        # Format prompt
        full_prompt = format_prompt(
            system_prompt=system_prompt,
            subject=subject,
            description=description,
        )

        # Classify with retry
        output, latency_ms, attempts, error_msg = client.classify_with_retry(
            prompt=full_prompt,
            model_id=model,
            temperature=temperature,
            max_tokens=512,
        )

        if output:
            predictions.append(
                {
                    "id": event["service_request_id"],
                    "subject": subject,
                    "description": description,
                    "pred": {
                        "category": output.category,
                        "evidence": output.evidence,
                        "reasoning": output.reasoning,
                        "confidence": output.confidence,
                    },
                    "meta": {
                        "model_id": model,
                        "prompt_version": prompt_version,
                        "prompt_hash": prompt_hash,
                        "temperature": temperature,
                        "latency_ms": latency_ms,
                        "attempts": attempts,
                        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    },
                }
            )
            print(f"  [{idx}/{total}] ✓ {event['service_request_id']}: {output.category} (conf={output.confidence:.2f})")
        else:
            errors.append(
                {
                    "id": event["service_request_id"],
                    "error": error_msg,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                }
            )
            print(f"  [{idx}/{total}] ✗ {event['service_request_id']}: {error_msg}")

        # Rate limiting
        if sleep_seconds > 0 and idx < total:
            time.sleep(sleep_seconds)

    return predictions, errors


def write_predictions_to_supabase(
    client: SupabaseClient,
    predictions: list[dict],
    sleep_seconds: float = 0.05,
) -> int:
    """Write Phase 2 predictions back to Supabase.

    Uses PATCH per row to update bike_issue_* columns.

    Returns:
        Number of successfully written rows
    """
    success_count = 0
    total = len(predictions)

    for idx, pred in enumerate(predictions, start=1):
        row_id = pred["id"]

        # Prepare update payload
        payload = {
            "bike_issue_category": pred["pred"]["category"],
            "bike_issue_confidence": pred["pred"]["confidence"],
            "bike_issue_evidence": pred["pred"]["evidence"],
            "bike_issue_reasoning": pred["pred"]["reasoning"],
        }

        try:
            client.request_json(
                "PATCH",
                "/rest/v1/events",
                params={"service_request_id": f"eq.{row_id}"},
                body=payload,
            )
            success_count += 1
            print(f"  [{idx}/{total}] ✓ Wrote {row_id}")
        except Exception as e:
            print(f"  [{idx}/{total}] ✗ Failed to write {row_id}: {e}")

        # Rate limiting
        if sleep_seconds > 0 and idx < total:
            time.sleep(sleep_seconds)

    return success_count


def load_checkpoint() -> dict | None:
    """Load checkpoint from file."""
    if not CHECKPOINT_FILE.exists():
        return None

    try:
        with CHECKPOINT_FILE.open("r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load checkpoint: {e}")
        return None


def save_checkpoint(last_id: str, total_processed: int, total_classified: int):
    """Save checkpoint to file."""
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    checkpoint = {
        "last_service_request_id": last_id,
        "total_processed": total_processed,
        "total_classified": total_classified,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    write_json(checkpoint, CHECKPOINT_FILE)


def main():
    parser = argparse.ArgumentParser(description="Run Phase 2 Supabase pipeline")
    parser.add_argument("--prompt", "-p", required=True, help="Prompt version (e.g., v001)")
    parser.add_argument("--model", "-m", default="gemini-2.5-flash-lite", help="Model ID")
    parser.add_argument("--temperature", "-t", type=float, default=0.0, help="Temperature")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS, help="Sleep between classifications (seconds)")
    parser.add_argument("--only-unclassified", action="store_true", help="Only process events where bike_issue_category IS NULL")
    parser.add_argument("--limit", type=int, help="Max number of events to process (for testing)")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--dry-run", action="store_true", help="Classify but don't write to Supabase")

    args = parser.parse_args()

    # Load environment
    load_dotenv()

    # Validate model
    if args.model not in SUPPORTED_MODELS:
        print(f"Error: Unsupported model: {args.model}")
        print(f"Supported models: {', '.join(SUPPORTED_MODELS)}")
        return 1

    # Initialize clients
    print("Initializing clients...")
    api_config = APIConfig()
    try:
        api_config.validate_required()
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    gemini_client = Phase2GeminiClient(api_config)

    supabase_url = load_env("SUPABASE_URL")
    supabase_key = load_env("SUPABASE_SERVICE_ROLE_KEY")
    supabase_client = SupabaseClient(supabase_url, supabase_key)

    # Load prompt
    print(f"Loading prompt: {args.prompt}")
    try:
        system_prompt, prompt_hash = load_prompt(args.prompt)
        print(f"✓ Loaded prompt (hash: {prompt_hash})")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    # Load checkpoint if resuming
    last_id = None
    total_processed = 0
    total_classified = 0

    if args.resume:
        checkpoint = load_checkpoint()
        if checkpoint:
            last_id = checkpoint.get("last_service_request_id")
            total_processed = checkpoint.get("total_processed", 0)
            total_classified = checkpoint.get("total_classified", 0)
            print(f"✓ Resuming from checkpoint: last_id={last_id}, processed={total_processed}")
        else:
            print("No checkpoint found, starting from beginning")

    # Create run directory
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_dir = Path(__file__).parent.parent / "phase2" / "runs" / f"supabase_pipeline_{timestamp}_{args.prompt}"
    run_dir.mkdir(parents=True, exist_ok=True)

    predictions_file = run_dir / "predictions.jsonl"
    errors_file = run_dir / "errors.jsonl"

    print(f"Run directory: {run_dir}\n")

    # Save config
    config = {
        "prompt_version": args.prompt,
        "prompt_hash": prompt_hash,
        "model_id": args.model,
        "temperature": args.temperature,
        "batch_size": args.batch_size,
        "only_unclassified": args.only_unclassified,
        "limit": args.limit,
        "dry_run": args.dry_run,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    write_json(config, run_dir / "config.json")

    # Main processing loop
    all_predictions = []
    all_errors = []
    events_processed = 0

    try:
        while True:
            # Check limit
            if args.limit and events_processed >= args.limit:
                print(f"\n✓ Reached limit of {args.limit} events")
                break

            # Fetch batch
            fetch_size = args.batch_size
            if args.limit:
                remaining = args.limit - events_processed
                fetch_size = min(fetch_size, remaining)

            print(f"\nFetching batch (size={fetch_size}, last_id={last_id})...")
            events = fetch_events(supabase_client, fetch_size, last_id, args.only_unclassified)

            if not events:
                print("✓ No more events to process")
                break

            print(f"✓ Fetched {len(events)} events")

            # Classify batch
            print(f"Classifying batch...")
            predictions, errors = classify_batch(
                gemini_client,
                system_prompt,
                prompt_hash,
                events,
                args.prompt,
                args.model,
                args.temperature,
                args.sleep,
            )

            all_predictions.extend(predictions)
            all_errors.extend(errors)

            # Write to Supabase
            if predictions and not args.dry_run:
                print(f"Writing {len(predictions)} predictions to Supabase...")
                written = write_predictions_to_supabase(supabase_client, predictions, sleep_seconds=0.05)
                print(f"✓ Wrote {written}/{len(predictions)} predictions")
            elif predictions and args.dry_run:
                print(f"[DRY RUN] Would write {len(predictions)} predictions")

            # Save predictions to JSONL (for audit trail)
            with predictions_file.open("a", encoding="utf-8") as f:
                for pred in predictions:
                    f.write(json.dumps(pred, ensure_ascii=False) + "\n")

            # Save errors
            if errors:
                with errors_file.open("a", encoding="utf-8") as f:
                    for err in errors:
                        f.write(json.dumps(err, ensure_ascii=False) + "\n")

            # Update counters
            events_processed += len(events)
            total_processed += len(events)
            total_classified += len(predictions)

            # Save checkpoint
            last_id = events[-1]["service_request_id"]
            save_checkpoint(last_id, total_processed, total_classified)

            print(f"\nProgress: {events_processed} events processed, {len(all_predictions)} classified, {len(all_errors)} errors")

    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        print(f"Checkpoint saved: last_id={last_id}")
        print("Use --resume to continue from checkpoint")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Final summary
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Total events processed: {events_processed}")
    print(f"Successfully classified: {len(all_predictions)}")
    print(f"Errors: {len(all_errors)}")
    print(f"Success rate: {len(all_predictions) / max(events_processed, 1) * 100:.1f}%")
    print(f"\nArtifacts saved to: {run_dir}")
    print(f"  - predictions.jsonl: {len(all_predictions)} records")
    print(f"  - errors.jsonl: {len(all_errors)} records")

    # Category distribution
    if all_predictions:
        print("\nCategory Distribution:")
        from collections import Counter
        category_counts = Counter(p["pred"]["category"] for p in all_predictions)
        for cat, count in category_counts.most_common():
            pct = count / len(all_predictions) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
