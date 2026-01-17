# Phase 1 Report: Bike Relevance Classification (Supabase)

Date: 2026-01-17  
Prompt: `prompts/phase1/v006.md`  
Model: `gemini-2.5-flash-lite`

## Objective

Classify bike-infrastructure relevance for the full Supabase `events` table using:

- Rule-based prefiltering to skip irrelevant categories
- LLM classification for the remaining events
- Database write-back for analysis and downstream use

## Data Sources

- Supabase table: `public.events`
- Primary key: `service_request_id`
- Local samples (kept for reproducibility):
  - `data/supabase_test_200.csv`
  - `data/supabase_test_200_filtered.csv`

## Prompt Version (v006)

Location: `prompts/phase1/v006.md`

Key behaviors:
- TRUE requires explicit bike terms or infrastructure markers.
- FALSE for pedestrian-only or generic issues without bike evidence.
- UNCERTAIN only for ambiguous lane or location cases.
- Evidence quotes limited to short snippets.

## Pipeline Overview

Script: `scripts/run_supabase_pipeline.py`

Flow:
1) Fetch events in pages from Supabase.
2) Apply prefilter rules (`config/supabase_config.py`).
3) Classify remaining events with Gemini.
4) PATCH results back to Supabase.
5) Checkpoint progress for resume on interruption.

## Run Summary

Full LLM classification run (no prefilter write-back):
- Events fetched: 35,360
- LLM classified: 21,462
- LLM label counts (from `runs/supabase_pipeline_20260117_023221_v006/predictions.jsonl`):
  - TRUE: 2,045
  - FALSE: 17,822
  - UNCERTAIN: 1,595
- LLM errors: 2 (kept in `runs/supabase_pipeline_20260117_023221_v006/errors.jsonl`)

Prefilter-only run (write excluded categories as FALSE, no LLM):
- Events fetched: 15,093
- Prefiltered updates: 11,217

Final database counts:
| bike_related | count |
|------------|------:|
| true       | 2,045 |
| false      | 29,439 |
| null       | 3,876 |

Interpretation of `NULL`:
- 1,595 rows: LLM `uncertain`
- ~2,251 rows: no description (never sent to LLM)
- Remainder: small residue from errors/retries (2) or rows not processed in the LLM run

## Cost Summary

Total LLM cost: €2.33

Approximate unit costs:
- €0.000108 per LLM-classified row (2.33 / 21,462)
- €0.0659 per 1,000 total rows (2.33 / 35,360)

## Supabase Setup Notes

Required columns (SQL migration in `migrations/add_bike_classification_columns.sql`):
- `bike_related` BOOLEAN
- `bike_confidence` DECIMAL(3,2)
- `bike_evidence` TEXT[]
- `bike_reasoning` TEXT

Service role permissions used:
```sql
grant usage on schema public to service_role;
grant select, update, insert on table public.events to service_role;
```

## Operational Issues & Fixes

- 403 permission errors: resolved by using a service_role key and granting SELECT/UPDATE/INSERT.
- REST upsert (POST) failed due to NOT NULL fields: switched to PATCH per row.
- Evidence quote length errors: added truncation in `bikeclf/schema.py`.
- Cloudflare 500s on bulk PATCH: added retry/backoff and per-row pacing.
- CLI flags on new lines were ignored by shell; run commands on a single line.

## Reproducible Commands

Full pipeline (writes to Supabase):
```bash
uv run python scripts/run_supabase_pipeline.py \
  --prompt v006 \
  --model gemini-2.5-flash-lite \
  --only-unclassified \
  --write-prefiltered \
  --batch-size 500 \
  --sleep 0.1
```

Prefilter-only (no LLM calls):
```bash
uv run python scripts/run_supabase_pipeline.py \
  --only-unclassified \
  --write-prefiltered \
  --prefilter-only \
  --batch-size 500
```

## Project Structure (Key Items)

- `prompts/phase1/v006.md`: production prompt
- `scripts/run_supabase_pipeline.py`: full pipeline
- `config/supabase_config.py`: prefilter rules
- `migrations/add_bike_classification_columns.sql`: DB schema changes
- `runs/supabase_pipeline_20260117_023221_v006/`: full LLM run artifacts
- `runs/supabase_pipeline_20260117_115034_v006/`: prefilter-only run artifacts

