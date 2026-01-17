# Phase 2 Plan: Bike-Issue Categorization

Status: Planning only (no implementation in this phase)

## Objective

Take the Phase 1 bike-related events (`bike_related = true`) and classify each into a single Phase 2 category using an LLM. The result should be reproducible, trackable, and easy to audit — matching the Phase 1 workflow style (prompt versioning, run artifacts, per-run configs, and error logs).

## Phase 2 Categories (Final List)

Use exactly these labels (case and punctuation must match):

1. **Sicherheit & Komfort (Geometrie/Führung)**
2. **Müll / Scherben / Splitter (Sharp objects & debris)**
3. **Oberflächenqualität / Schäden**
4. **Wasser / Eis / Entwässerung**
5. **Hindernisse & Blockaden (inkl. Parken & Baustelle)**
6. **Vegetation & Sichtbehinderung**
7. **Markierungen & Beschilderung**
8. **Ampeln & Signale (inkl. bike-specific Licht)**
9. **Other / Unklar**

Exactly one label per event (no multi-label output).

## Dataset & Scope

Source: Supabase `public.events` table where:

```
bike_related = true
```

Current counts (after Phase 1 + prefilter write-back):

| bike_related | count |
|-------------|------:|
| true        | 2,045 |
| false       | 29,439 |
| null        | 3,876 |

Phase 2 only processes the 2,045 TRUE rows.

## Evaluation Set

File: `phase2/phase2-eval-set.jsonl`

Structure (per line):
```json
{"id":"P2-SK-001","category":"Sicherheit & Komfort (Geometrie/Führung)","subject":"...","description":"...","phase1_label":"true","phase2_label":"Sicherheit & Komfort (Geometrie/Führung)","gold_notes":"...","challenge_type":"easy"}
```

Notes:
- 108 examples (12 per category).
- All are Phase 1 TRUE by construction.
- Challenge types: `easy`, `ambiguous`, `mixed`, `edge_case`.

## Prompting Design (Phase 2)

### Goals
- Enforce *single* category selection.
- Require explicit evidence in the input text.
- Avoid category confusion (e.g., debris vs. surface damage).
- Preserve data provenance (evidence snippets + reasoning).

### Output Schema (strict JSON)
```json
{
  "category": "<one of the 9 category strings above>",
  "evidence": ["<short quote>", "..."],
  "reasoning": "<single sentence>",
  "confidence": 0.0
}
```

### Category Guidance (high-level)
- **Sicherheit & Komfort (Geometrie/Führung)**: design/geometry issues, narrow lanes, forced unsafe positioning, unclear priority that causes fear/conflicts.
- **Müll / Scherben / Splitter**: loose debris on bike infrastructure; not structural surface damage.
- **Oberflächenqualität / Schäden**: cracks, potholes, uneven slabs, roots, sunken manholes.
- **Wasser / Eis / Entwässerung**: standing water, flooding, ice, blocked drains.
- **Hindernisse & Blockaden**: parked vehicles, fences, containers, construction barriers, blocked access to bike parking.
- **Vegetation & Sichtbehinderung**: overgrowth narrowing space or blocking visibility/signs.
- **Markierungen & Beschilderung**: missing/faded markings, wrong or missing signs, confusing guidance.
- **Ampeln & Signale**: bike signals, timing, sensors, detection failure.
- **Other / Unklar**: insufficient info or truly unmatched cases.

### Category Disambiguation Rules
- Debris vs Surface: if *loose* objects → debris; if *structural surface* → surface damage.
- Blockade vs Geometry: temporary physical blockers → blockade; permanent design issue → geometry.
- Vegetation vs Marking/Sign: if the issue is blocked by vegetation, still vegetation.
- Signals vs Markings: traffic light logic is signals; paint/lines are markings.

## Folder Structure (Phase 2)

Create a separate folder to keep Phase 2 isolated and clean:

```
phase2/
  prompts/
    v001.md
    v002.md
    ...
  runs/
    2026xxxx_xxxxxx_v001_2.5_flash_lite/
      config.json
      predictions.jsonl
      errors.jsonl
  phase2-eval-set.jsonl
  PHASE2_PLAN.md
  PROMPT_ITERATION_LOG.md
```

## Execution Flow (Phase 2)

1) **Prompt development**
   - Start with v001 based on Phase 2 categories.
   - Run on `phase2-eval-set.jsonl`.
   - Review misclassifications and update prompt version.

2) **Evaluation runs**
   - Use consistent run naming (timestamp + prompt version + model).
   - Save `config.json`, `predictions.jsonl`, `errors.jsonl` per run.
   - Summarize label distribution and confusion.

3) **Production run**
   - Query Supabase for `bike_related = true`.
   - Classify via Phase 2 prompt.
   - Store outputs (category, evidence, reasoning, confidence) in a Phase 2 output store
     (either new columns in `events` or a dedicated `events_bike_phase2` table).

## Models

Target model family: Gemini 2.5 Flash Lite (default).

Run config example:
```
model: gemini-2.5-flash-lite
temperature: 0.0
max_tokens: 512
```

## Metrics & Tracking

- Per-category counts
- Confusion matrix on `phase2-eval-set.jsonl`
- % Other/Unklar
- Sample review of mislabels (per category)

## Open Questions (to resolve before implementation)

- Should Phase 2 write back into `events` or a new table?
- What is the target acceptable % of `Other / Unklar`?
- Do we want a separate prefilter for Phase 2 (e.g., skip rows with too-short descriptions)?

