# Bike Infrastructure Issue Classification System

Two-phase LLM-powered classification system for German civic issue reports (Cologne "Sags-Uns"):

**Phase 1:** Classify events as bike-related (TRUE/FALSE/UNCERTAIN)
**Phase 2:** Categorize bike-related events into 9 maintenance/safety categories

Powered by Google Gemini with structured output, prompt versioning, and full reproducibility.

## Features

- **Structured Output**: Gemini generates validated JSON via Pydantic schemas
- **Prompt Versioning**: Zero-code-change prompt iteration (just add new `.md` files)
- **Comprehensive Metrics**: Accuracy, F1, confusion matrix, per-class metrics
- **Langfuse Tracing**: Optional observability for model calls
- **Retry Logic**: Automatic retry with repair prompts on validation failures
- **Rich CLI**: Beautiful command-line interface with tables and progress indicators
- **Reproducible**: Tracks model version, prompt hash, git commit for full reproducibility
- **Interactive Dashboard**: Streamlit app for error analysis, length-based slicing, and pattern discovery

## Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/Fatih0234/phase1-flag-the-event.git
cd phase1-flag-the-event
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys
```

**Required:**
- `GOOGLE_API_KEY`: Get from [Google AI Studio](https://aistudio.google.com/apikey)

**Optional (for tracing):**
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST`: Get from [Langfuse](https://langfuse.com)

### 3. Verify Setup

```bash
# List available prompts (should show v001)
python -m bikeclf.phase1.eval list-prompts
```

### 4. Run First Evaluation

```bash
python -m bikeclf.phase1.eval evaluate \
  --dataset bike_related_gold_dataset_A_to_F.csv \
  --prompt v001 \
  --model gemini-2.0-flash-001 \
  --temperature 0.0
```

## Usage

### Evaluate with a Prompt

```bash
# Basic usage (uses defaults)
python -m bikeclf.phase1.eval evaluate --prompt v001

# Full options
python -m bikeclf.phase1.eval evaluate \
  --dataset bike_related_gold_dataset_A_to_F.csv \
  --prompt v001 \
  --model gemini-2.0-flash-001 \
  --temperature 0.0 \
  --max-tokens 512
```

**Options:**
- `--dataset`, `-d`: Path to CSV dataset (default: `bike_related_gold_dataset_A_to_F.csv`)
- `--prompt`, `-p`: Prompt version (e.g., `v001`, `v002`)
- `--model`, `-m`: Model ID (default: `gemini-2.0-flash-001`)
- `--temperature`, `-t`: Sampling temperature (default: `0.0`)
- `--max-tokens`: Maximum output tokens (default: `512`)

### List Available Prompts

```bash
python -m bikeclf.phase1.eval list-prompts
```

### Compare Two Runs

```bash
python -m bikeclf.phase1.eval diff \
  runs/20260116_120000_v001/predictions.jsonl \
  runs/20260116_130000_v002/predictions.jsonl
```

### Launch Interactive Dashboard

Analyze evaluation runs with a comprehensive Streamlit dashboard:

```bash
# Option 1: Using the launch script
./run_dashboard.sh

# Option 2: Direct streamlit command
streamlit run bikeclf/phase1/dashboard.py
```

The dashboard automatically discovers all runs and provides:
- **Run Selection**: Dropdown with all available runs and their metrics
- **Overview Metrics**: Accuracy, F1, per-class performance
- **Confusion Matrix**: Interactive heatmap visualization
- **Misclassification Analysis**: Filter, sort, and inspect errors in detail
- **Length-Based Slicing**: Performance breakdown by text length buckets
- **Confidence Distribution**: Compare confidence for correct vs incorrect predictions
- **Error Patterns**: Most common misclassification types
- **Detailed Case Inspection**: Dive deep into individual misclassifications with evidence and reasoning

Access at: http://localhost:8501

## Phase Reports

### Phase 1: Bike Relevance Classification
See **`PHASE1_REPORT.md`** for complete details:
- 2,045 events classified as bike-related (TRUE)
- 29,439 events classified as not bike-related (FALSE)
- 3,876 events uncertain or without description
- Total cost: €2.33
- Model: gemini-2.5-flash-lite

### Phase 2: Issue Categorization
See **`PHASE2_REPORT.md`** for complete details:
- 2,025 bike-related events categorized into 9 categories
- 95.4% accuracy on evaluation set (108 examples)
- 100% success rate on production run
- Total cost: €0.22
- Model: gemini-2.5-flash-lite

**Top Categories:**
1. Oberflächenqualität / Schäden (43.5%) - Surface damage
2. Hindernisse & Blockaden (17.2%) - Parking/barriers
3. Müll / Scherben / Splitter (12.6%) - Glass/debris

## Project Structure

```
.
├── README.md
├── PHASE1_REPORT.md            # Phase 1 complete results
├── PHASE2_REPORT.md            # Phase 2 complete results
├── pyproject.toml              # Dependencies and project metadata
├── .env.example                # Environment variable template
├── .gitignore
├── bike_related_gold_dataset_A_to_F.csv
├── prompts/                    # Prompt versions
│   └── phase1/
│       ├── README.md           # Prompt versioning guide
│       └── v001-v006.md        # Phase 1 prompts
├── phase2/                     # Phase 2 specific files
│   ├── PHASE2_PLAN.md          # Planning document
│   ├── README.md               # Quick reference
│   ├── phase2-eval-set.jsonl   # Gold standard (108 examples)
│   ├── prompts/
│   │   └── v001.md             # Phase 2 prompt
│   └── runs/                   # Phase 2 evaluation/production runs
│       ├── {timestamp}_v001_2.5-lite/       # Eval run
│       └── supabase_pipeline_{timestamp}/   # Production run
├── runs/                       # Phase 1 runs (gitignored)
│   └── <timestamp>_<version>/
│       ├── predictions.jsonl   # Full predictions with metadata
│       ├── metrics.json        # Accuracy, F1, confusion matrix
│       ├── config.json         # Run configuration
│       └── errors.jsonl        # Failed predictions (if any)
├── scripts/
│   ├── run_supabase_pipeline.py           # Phase 1 production
│   └── run_supabase_phase2_pipeline.py    # Phase 2 production
├── bikeclf/                    # Main package
│   ├── __init__.py
│   ├── config.py               # Environment and configuration
│   ├── schema.py               # Pydantic models (Phase 1 + Phase 2)
│   ├── io.py                   # File I/O utilities
│   ├── gemini_client.py        # Gemini API wrapper (Phase 1)
│   ├── metrics.py              # Metrics computation
│   ├── phase1/
│   │   ├── __init__.py
│   │   ├── prompt_loader.py    # Prompt versioning
│   │   ├── eval.py             # CLI entry point
│   │   └── dashboard.py        # Streamlit dashboard
│   └── phase2/                 # Phase 2 module
│       ├── __init__.py
│       ├── config.py            # Phase 2 paths and categories
│       ├── eval.py              # Phase 2 CLI
│       ├── gemini_client.py     # Phase 2 client (9-way)
│       ├── io.py                # JSONL I/O
│       ├── metrics.py           # 9-way metrics
│       ├── markdown_report.py   # Category reports
│       └── prompt_loader.py     # Phase 2 prompt loader
└── tests/
    ├── test_schema.py          # Pydantic schema tests
    └── test_metrics.py         # Metrics computation tests
```

## Workflow: Iterating on Prompts

### 1. Run Baseline

```bash
python -m bikeclf.phase1.eval evaluate --prompt v001
```

Check the output in `runs/<timestamp>_v001/`:
- `metrics.json`: Overall performance
- `predictions.jsonl`: Detailed predictions
- `misclassifications.md`: **Human-readable report of all errors** ✨
- `config.json`: Run configuration
- `errors.jsonl`: Failures (if any)

### 2. Analyze Results

**Option A: Read the Markdown Report** (Recommended)

Open `runs/<timestamp>_v001/misclassifications.md` to see a formatted report with:
- Summary of accuracy and error breakdown
- All misclassified cases with:
  - Subject and description
  - Gold label vs predicted label
  - Model's reasoning and evidence
  - Confidence score and metadata

**Option B: Use the Dashboard**

```bash
./run_dashboard.sh
```

Select your run from the dropdown and explore interactively.

**Option C: Programmatic Analysis**

```python
# Quick analysis script
import json

with open("runs/<timestamp>_v001/predictions.jsonl") as f:
    for line in f:
        pred = json.loads(line)
        if pred["gold_label"] != pred["pred"]["label"]:
            print(f"\nMismatch: {pred['id']}")
            print(f"  Gold: {pred['gold_label']}")
            print(f"  Pred: {pred['pred']['label']}")
            print(f"  Subject: {pred['subject']}")
            print(f"  Evidence: {pred['pred']['evidence']}")
            print(f"  Reasoning: {pred['pred']['reasoning']}")
```

### 3. Create New Prompt Version

```bash
# Copy and edit
cp prompts/phase1/v001.md prompts/phase1/v002.md
# Edit v002.md with improvements based on error analysis
```

### 4. Test New Prompt

```bash
python -m bikeclf.phase1.eval evaluate --prompt v002
```

### 5. Compare Results

```bash
python -m bikeclf.phase1.eval diff \
  runs/<timestamp_v001>/predictions.jsonl \
  runs/<timestamp_v002>/predictions.jsonl
```

### 6. Commit Changes

```bash
git add prompts/phase1/v002.md
git commit -m "Add v002: Improved decision criteria for 'uncertain' cases"
```

## Output Format

### Misclassification Report (misclassifications.md)

Human-readable markdown report automatically generated for each run:

```markdown
# Misclassification Report

## Summary
- Total predictions: 55
- Correct predictions: 43
- Misclassified: 12
- Accuracy: 78.2%

### Error Breakdown
- false → true: 8 cases
- false → uncertain: 2 cases
- uncertain → true: 2 cases

## Misclassified Cases

### 1. Case E-01
**Gold Label**: ❌ `false`
**Predicted Label**: ✅ `true`
**Confidence**: 1.00

**Subject:**
> Fahrrad am Rhein gefunden

**Description:**
> Heute am Rheinufer stand ein herrenloses Fahrrad...

**Model's Reasoning:**
> Die Meldung bezieht sich auf ein gefundenes Fahrrad...

**Evidence Extracted:**
> - Fahrrad am Rhein gefunden
```

**Generate for existing runs:**
```bash
python generate_report_for_run.py runs/20260116_135146_v001
```

### Prediction Record (predictions.jsonl)

Each line is a complete prediction record:

```json
{
  "id": "A-01",
  "subject": "Glasscherben auf Radweg",
  "description": "Auf dem Radweg zwischen...",
  "gold_label": "true",
  "pred": {
    "label": "true",
    "evidence": ["Radweg wird erwähnt"],
    "reasoning": "Explizite Erwähnung von Radweg-Infrastruktur.",
    "confidence": 0.95
  },
  "meta": {
    "model_id": "gemini-2.0-flash-001",
    "prompt_version": "v001",
    "temperature": 0.0,
    "max_output_tokens": 512,
    "timestamp_utc": "2026-01-16T12:00:00Z",
    "latency_ms": 1234,
    "attempts": 1
  }
}
```

### Metrics (metrics.json)

```json
{
  "accuracy": 0.873,
  "macro_f1": 0.845,
  "per_class": {
    "true": {
      "precision": 0.917,
      "recall": 0.917,
      "f1": 0.917,
      "support": 11
    },
    "false": {
      "precision": 0.889,
      "recall": 0.889,
      "f1": 0.889,
      "support": 9
    },
    "uncertain": {
      "precision": 0.714,
      "recall": 0.833,
      "f1": 0.769,
      "support": 6
    }
  },
  "confusion_matrix": {
    "labels": ["true", "false", "uncertain"],
    "matrix": [
      [10, 0, 1],
      [0, 8, 1],
      [0, 1, 5]
    ]
  }
}
```

## Supported Models

All Gemini models from Google are supported. Simply add new model IDs to `bikeclf/config.py` in the `SUPPORTED_MODELS` list.

**Currently supported:**

### Gemini 2.0 Flash Family
- `gemini-2.0-flash-001` - **Default**, stable version
- `gemini-2.0-flash` - Latest version
- `gemini-2.0-flash-exp` - Experimental version

### Gemini 2.5 Flash Family
- `gemini-2.5-flash-lite` - Lightweight, fast version ⚡
- `gemini-2.5-flash` - Full featured version

**Run naming convention:**
Run directories include the model name for easy comparison:
- `20260116_135146_v001_2.0-flash-001` - Gemini 2.0 Flash stable
- `20260116_140325_v001_2.5-lite` - Gemini 2.5 Flash Lite

**Compare models:**
```bash
# Test same prompt with different models
python -m bikeclf.phase1.eval evaluate --prompt v001 --model gemini-2.0-flash-001
python -m bikeclf.phase1.eval evaluate --prompt v001 --model gemini-2.5-flash-lite

# Compare results in dashboard
./run_dashboard.sh  # Select each run from dropdown
```

## Langfuse Tracing

If Langfuse credentials are configured, each run automatically traces:
- Full prompt text
- Model output
- Gold label vs predicted label
- Latency and attempt count
- Dataset row ID for easy lookup

Access traces at your Langfuse dashboard to:
- Filter by prompt version
- Analyze error patterns
- Compare latencies
- Debug specific predictions

## Testing

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=bikeclf --cov-report=html

# Run specific test file
pytest tests/test_schema.py -v
```

## Troubleshooting

### API Key Not Found

```
Error: GOOGLE_API_KEY not found
```

**Solution:** Create `.env` file with your API key:
```bash
cp .env.example .env
# Edit .env and add: GOOGLE_API_KEY=your-key-here
```

### Prompt Not Found

```
Error: Prompt version 'v002' not found
```

**Solution:** Create the prompt file:
```bash
cp prompts/phase1/v001.md prompts/phase1/v002.md
```

Check available prompts:
```bash
python -m bikeclf.phase1.eval list-prompts
```

### Validation Errors

Check `runs/<timestamp>/errors.jsonl` for details. Common causes:
- Model output doesn't match schema
- Network timeouts
- Rate limiting

The system automatically retries once with a repair prompt.

### Langfuse Not Working

System works without Langfuse. If you see warnings:
1. Check credentials in `.env`
2. Verify network access to Langfuse host
3. System continues normally even if tracing fails

## Development

### Adding New Prompts

1. Copy latest version: `cp prompts/phase1/vXXX.md prompts/phase1/vYYY.md`
2. Edit the new file
3. Test: `python -m bikeclf.phase1.eval evaluate --prompt vYYY`
4. Commit: `git add prompts/phase1/vYYY.md && git commit -m "..."`

### Code Style

- Type hints for all functions
- Docstrings in Google style
- Black for formatting
- pylint/mypy for linting (optional)

## Dataset Format

CSV with required columns:
- `id`: Unique identifier (e.g., "A-01")
- `subject`: Issue title
- `description`: Full description
- `gold_label`: Ground truth ("true", "false", "uncertain")

Optional columns (for analysis):
- `gold_notes`: Reasoning for gold label
- `challenge_type`: Difficulty classification
- `category`: Issue category

## License

MIT

## Acknowledgments

- Built for Cologne "Sags-Uns" bike infrastructure classification
- Powered by Gemini 2.0 Flash
- Tracing by Langfuse
