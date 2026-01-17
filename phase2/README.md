# Phase 2: Bike Issue Categorization

This folder contains the Phase 2 prompt workflow and evaluation assets.

## Files

- `PHASE2_PLAN.md`: Full planning document and workflow design.
- `phase2-eval-set.jsonl`: Gold evaluation set for prompt iteration.
- `prompts/`: Prompt versions (v001, v002, ...).
- `runs/`: Run artifacts (config, predictions, errors).

## Intended Workflow

1) Draft `prompts/v001.md` with the Phase 2 categories.
2) Run evaluation on `phase2-eval-set.jsonl`.
3) Inspect misclassifications and update the prompt version.
4) Keep all run artifacts under `runs/` for traceability.

