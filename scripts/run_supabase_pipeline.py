"""
Run end-to-end Supabase pipeline: fetch -> prefilter -> LLM -> write-back.

Supports prefilter-only mode for marking excluded categories as FALSE without LLM calls.
"""
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib import request, parse, error

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from bikeclf.config import APIConfig
from bikeclf.gemini_client import GeminiClient
from bikeclf.phase1.prompt_loader import load_prompt, format_prompt
from config.supabase_config import should_check_with_llm


DEFAULT_BATCH_SIZE = 500
DEFAULT_SLEEP_SECONDS = 0.1


class SupabaseClient:
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
    ) -> Any:
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
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)

        try:
            with request.urlopen(req, timeout=60) as resp:
                payload = resp.read().decode("utf-8")
                return json.loads(payload) if payload else None
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"Supabase API error: {exc.code} {detail}") from exc


def load_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def fetch_events(
    client: SupabaseClient,
    batch_size: int,
    last_id: str | None,
    only_unclassified: bool,
) -> list[dict]:
    params = {
        "select": "service_request_id,title,description,service_name",
        "order": "service_request_id",
        "limit": str(batch_size),
    }
    if last_id:
        params["service_request_id"] = f"gt.{last_id}"
    if only_unclassified:
        params["bike_related"] = "is.null"

    return client.request_json("GET", "/rest/v1/events", params=params)


def classify_batch(
    client: GeminiClient,
    system_prompt: str,
    prompt_hash: str,
    events: list[dict],
    prompt_version: str,
    model: str,
    temperature: float,
    sleep_seconds: float,
) -> tuple[list[dict], list[dict]]:
    predictions = []
    errors = []
    total = len(events)

    for idx, event in enumerate(events, start=1):
        messages = format_prompt(
            system_prompt=system_prompt,
            subject=event["subject"],
            description=event["description"],
        )

        output, latency_ms, attempts, error_msg = client.classify_with_retry(
            prompt=messages,
            model_id=model,
            temperature=temperature,
        )

        if output:
            predictions.append(
                {
                    "id": event["id"],
                    "subject": event["subject"],
                    "description": event["description"],
                    "pred": {
                        "label": output.label,
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
                        "timestamp": datetime.now().isoformat(),
                    },
                }
            )
        else:
            errors.append(
                {
                    "id": event["id"],
                    "error": error_msg,
                    "timestamp": datetime.now().isoformat(),
                }
            )

        if idx == 1 or idx % 10 == 0 or idx == total:
            print(f"  LLM progress: {idx}/{total}")

        time.sleep(sleep_seconds)

    return predictions, errors


def prediction_to_update(pred: dict) -> dict:
    label = pred["pred"]["label"]
    if label == "true":
        bike_related = True
    elif label == "false":
        bike_related = False
    else:
        bike_related = None

    return {
        "service_request_id": pred["id"],
        "bike_related": bike_related,
        "bike_confidence": pred["pred"]["confidence"],
        "bike_evidence": pred["pred"]["evidence"],
        "bike_reasoning": pred["pred"]["reasoning"],
    }


def prefilter_update(event: dict, reason: str) -> dict:
    return {
        "service_request_id": event["id"],
        "bike_related": False,
        "bike_confidence": 1.0,
        "bike_evidence": [],
        "bike_reasoning": f"prefilter: {reason}",
    }


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    with open(path, "a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def save_checkpoint(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def load_checkpoint(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def patch_updates(client: SupabaseClient, rows: list[dict], sleep_seconds: float) -> int:
    if not rows:
        return 0
    failures = 0
    for row in rows:
        event_id = row["service_request_id"]
        payload = {k: v for k, v in row.items() if k != "service_request_id"}
        for attempt in range(1, 4):
            try:
                client.request_json(
                    "PATCH",
                    "/rest/v1/events",
                    params={"service_request_id": f"eq.{event_id}"},
                    body=payload,
                    headers={"Prefer": "return=minimal"},
                )
                break
            except RuntimeError as exc:
                if attempt == 3:
                    failures += 1
                    print(f"  PATCH failed for {event_id}: {exc}")
                else:
                    time.sleep(0.5 * attempt)
        time.sleep(max(0.02, sleep_seconds / 5))
    return failures


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Run Supabase bike classification pipeline")
    parser.add_argument("--prompt", default="v006", help="Prompt version (default: v006)")
    parser.add_argument("--model", default="gemini-2.5-flash-lite", help="Model ID")
    parser.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Rows per fetch")
    parser.add_argument("--sleep", type=float, default=DEFAULT_SLEEP_SECONDS, help="Sleep between LLM calls")
    parser.add_argument("--only-unclassified", action="store_true", help="Only process rows with bike_related IS NULL")
    parser.add_argument("--write-prefiltered", action="store_true", help="Write excluded categories as FALSE")
    parser.add_argument("--prefilter-only", action="store_true", help="Only write excluded categories as FALSE (no LLM)")
    parser.add_argument("--dry-run", action="store_true", help="Skip Supabase updates")
    parser.add_argument("--run-dir", default="", help="Optional run directory name")
    parser.add_argument("--max-batches", type=int, default=0, help="Stop after N batches (0 = no limit)")

    args = parser.parse_args()

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    supabase_url = load_env("SUPABASE_URL")
    supabase_key = load_env("SUPABASE_SERVICE_ROLE_KEY")

    client = SupabaseClient(supabase_url, supabase_key)

    gemini_client = None
    system_prompt = ""
    prompt_hash = ""
    if not args.prefilter_only:
        api_config = APIConfig()
        api_config.validate_required()
        gemini_client = GeminiClient(config=api_config)
        system_prompt, prompt_hash = load_prompt(args.prompt)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = args.run_dir or f"supabase_pipeline_{timestamp}_{args.prompt}"
    run_dir = Path("runs") / run_name
    run_dir.mkdir(parents=True, exist_ok=True)

    predictions_path = run_dir / "predictions.jsonl"
    errors_path = run_dir / "errors.jsonl"
    checkpoint_path = run_dir / "checkpoint.json"

    checkpoint = load_checkpoint(checkpoint_path)
    last_id = checkpoint.get("last_id")
    stats = checkpoint.get(
        "stats",
        {
            "batches": 0,
            "fetched": 0,
            "prefiltered": 0,
            "classified": 0,
            "updated": 0,
            "errors": 0,
        },
    )

    while True:
        if args.max_batches and stats.get("batches", 0) >= args.max_batches:
            print(f"Reached max batches limit: {args.max_batches}")
            break

        batch = fetch_events(
            client=client,
            batch_size=args.batch_size,
            last_id=last_id,
            only_unclassified=args.only_unclassified,
        )
        if not batch:
            break

        print(f"\nFetched batch: {len(batch)} rows (last_id={batch[-1]['service_request_id']})")

        last_id = batch[-1]["service_request_id"]
        stats["fetched"] += len(batch)

        to_check = []
        prefilter_rows = []
        for row in batch:
            should_check, reason = should_check_with_llm(
                row.get("service_name", ""),
                row.get("description", ""),
            )
            if should_check:
                if not args.prefilter_only:
                    to_check.append(
                        {
                            "id": row["service_request_id"],
                            "subject": row.get("title", ""),
                            "description": row.get("description", ""),
                            "service_name": row.get("service_name", ""),
                        }
                    )
            else:
                if args.write_prefiltered and reason.startswith("excluded_category"):
                    prefilter_rows.append(prefilter_update(
                        {
                            "id": row["service_request_id"],
                        },
                        reason,
                    ))
                    stats["prefiltered"] += 1

        if args.prefilter_only:
            predictions = []
            errors = []
        else:
            predictions, errors = classify_batch(
                client=gemini_client,
                system_prompt=system_prompt,
                prompt_hash=prompt_hash,
                events=to_check,
                prompt_version=args.prompt,
                model=args.model,
                temperature=args.temperature,
                sleep_seconds=args.sleep,
            )
        print(
            f"Batch done: to_check={len(to_check)} predictions={len(predictions)} "
            f"errors={len(errors)} prefiltered={len(prefilter_rows)}"
        )

        if predictions:
            write_jsonl(predictions_path, predictions)
        if errors:
            write_jsonl(errors_path, errors)
            stats["errors"] += len(errors)

        updates = [prediction_to_update(pred) for pred in predictions]
        updates.extend(prefilter_rows)

        if not args.dry_run:
            update_failures = patch_updates(client, updates, args.sleep)
            stats["errors"] += update_failures

        stats["classified"] += len(predictions)
        stats["updated"] += len(updates)
        stats["batches"] = stats.get("batches", 0) + 1

        save_checkpoint(
            checkpoint_path,
            {
                "last_id": last_id,
                "stats": stats,
            },
        )

    save_checkpoint(
        checkpoint_path,
        {
            "last_id": last_id,
            "stats": stats,
            "completed_at": datetime.now().isoformat(),
        },
    )

    print("\nPipeline complete")
    print(f"Run directory: {run_dir}")
    print(f"Batches: {stats.get('batches', 0)}")
    print(f"Fetched: {stats['fetched']}")
    print(f"Prefiltered updates: {stats['prefiltered']}")
    print(f"Classified: {stats['classified']}")
    print(f"Updated: {stats['updated']}")
    print(f"Errors: {stats['errors']}")


if __name__ == "__main__":
    main()
