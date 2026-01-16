# Adding New Gemini Models

This guide shows how to add support for new Gemini models to the system.

## Quick Start

Adding a new model is a **one-line change** in `bikeclf/config.py`:

```python
SUPPORTED_MODELS = [
    # Existing models...
    "gemini-2.0-flash-001",

    # Add your new model here:
    "gemini-3.0-pro",  # ← Just add the model ID
]
```

That's it! The system automatically handles everything else.

## Step-by-Step Guide

### 1. Find the Model ID

Check Google AI Studio or Gemini API documentation for the exact model identifier:
- Format is usually: `gemini-{version}-{variant}`
- Examples: `gemini-2.5-flash-lite`, `gemini-3.0-pro`

### 2. Add to SUPPORTED_MODELS

Edit `bikeclf/config.py`:

```python
# Supported Gemini model identifiers
# Add new models here to make them available system-wide
SUPPORTED_MODELS = [
    # Gemini 2.0 Flash family
    "gemini-2.0-flash-001",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",

    # Gemini 2.5 Flash family
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",

    # NEW: Add your model here
    "gemini-3.0-pro",  # Your new model
]
```

### 3. (Optional) Add Display Name

For better readability in logs and dashboard:

```python
MODEL_DISPLAY_NAMES = {
    # Existing models...
    "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",

    # Add display name for your model
    "gemini-3.0-pro": "Gemini 3.0 Pro",
}
```

### 4. (Optional) Customize Short Name

If the automatic short name isn't ideal, customize it in `get_model_short_name()`:

```python
def get_model_short_name(model_id: str) -> str:
    """Get a short name for model ID suitable for file naming."""
    if "gemini-" in model_id:
        # ... existing logic ...

        # Add custom handling for your model
        elif "3.0" in model_id:
            if "pro" in model_id:
                return "3.0-pro"
            else:
                return "3.0"
    return model_id
```

### 5. Test It

```bash
# Run evaluation with new model
python -m bikeclf.phase1.eval evaluate \
  --prompt v001 \
  --model gemini-3.0-pro

# Run directory will be named:
# runs/20260116_151234_v001_3.0-pro
```

## What Works Automatically

Once you add the model ID to `SUPPORTED_MODELS`, the system automatically:

✅ **Validates** the model ID in CLI arguments
✅ **Creates** run directories with model name suffix
✅ **Tracks** model ID in config.json
✅ **Displays** in dashboard dropdown
✅ **Compares** across models in dashboard
✅ **Traces** to Langfuse with model metadata

## Examples

### Example 1: Adding Gemini 2.5 Flash Lite

```python
# In bikeclf/config.py
SUPPORTED_MODELS = [
    # ... existing models ...
    "gemini-2.5-flash-lite",  # ← Added this line
]
```

```bash
# Use it immediately
python -m bikeclf.phase1.eval evaluate \
  --prompt v001 \
  --model gemini-2.5-flash-lite

# Output: runs/20260116_151234_v001_2.5-lite/
```

### Example 2: Adding Multiple Experimental Models

```python
SUPPORTED_MODELS = [
    # Production models
    "gemini-2.0-flash-001",
    "gemini-2.5-flash",

    # Experimental models
    "gemini-2.5-flash-exp",
    "gemini-2.5-pro-exp",
    "gemini-3.0-preview",
]
```

## Model Comparison Workflow

Once you've added multiple models, compare them:

```bash
# Run same prompt with different models
python -m bikeclf.phase1.eval evaluate --prompt v001 --model gemini-2.0-flash-001
python -m bikeclf.phase1.eval evaluate --prompt v001 --model gemini-2.5-flash-lite
python -m bikeclf.phase1.eval evaluate --prompt v001 --model gemini-3.0-pro

# Compare in dashboard
./run_dashboard.sh

# Or compare specific runs
python -m bikeclf.phase1.eval diff \
  runs/20260116_135146_v001_2.0-flash-001/predictions.jsonl \
  runs/20260116_140325_v001_2.5-lite/predictions.jsonl
```

## Dashboard Integration

The dashboard automatically:
- Lists all runs from all models
- Shows model ID in run selection dropdown
- Groups runs by prompt version
- Allows filtering and comparison

Example dropdown:
```
20260116_135146_v001_2.0-flash-001 (Acc: 0.782, F1: 0.778)
20260116_140325_v001_2.5-lite (Acc: 0.845, F1: 0.821)
20260116_141502_v002_2.0-flash-001 (Acc: 0.891, F1: 0.887)
```

## Naming Convention

**Run directory format:**
```
YYYYMMDD_HHMMSS_<prompt>_<model-short>
```

**Examples:**
- `20260116_135146_v001_2.0-flash-001`
- `20260116_140325_v001_2.5-lite`
- `20260116_141502_v002_3.0-pro`

**Model short names:**
- `gemini-2.0-flash-001` → `2.0-flash-001`
- `gemini-2.5-flash-lite` → `2.5-lite`
- `gemini-3.0-pro` → `3.0-pro`

## Troubleshooting

### Model Not Recognized

```
Error: Unsupported model: gemini-3.0-pro
```

**Solution:** Add the model ID to `SUPPORTED_MODELS` in `bikeclf/config.py`

### API Error with New Model

```
API error: Model not found
```

**Possible causes:**
1. Model ID is incorrect (check Google AI Studio)
2. Model not available in your region
3. API key doesn't have access to that model

**Solution:** Verify the exact model ID from Google's documentation

### Short Name Collision

If two models produce the same short name (rare):

```python
def get_model_short_name(model_id: str) -> str:
    # Add explicit mapping
    short_name_map = {
        "gemini-2.5-flash": "2.5-flash-full",
        "gemini-2.5-flash-lite": "2.5-flash-lite",
    }

    if model_id in short_name_map:
        return short_name_map[model_id]

    # ... rest of logic ...
```

## Best Practices

1. **Use descriptive model IDs**: Follow Google's naming convention
2. **Test with small dataset first**: Before running full evaluation
3. **Document model characteristics**: Add comments about what each model is good for
4. **Track model versions**: Keep notes on when models were added/deprecated
5. **Compare systematically**: Run same prompt across multiple models to find best performer

## Model Registry Example

For better organization, consider documenting your models:

```python
# In bikeclf/config.py

# Model registry with metadata
MODEL_REGISTRY = {
    "gemini-2.0-flash-001": {
        "version": "2.0",
        "variant": "flash",
        "stability": "stable",
        "speed": "fast",
        "cost": "low",
        "notes": "Default production model",
    },
    "gemini-2.5-flash-lite": {
        "version": "2.5",
        "variant": "flash-lite",
        "stability": "stable",
        "speed": "very-fast",
        "cost": "very-low",
        "notes": "Lightweight for high-throughput scenarios",
    },
    # Add metadata for new models...
}
```

## Future: Auto-Discovery

For advanced use cases, you could implement auto-discovery:

```python
# Hypothetical future feature
def discover_available_models():
    """Query Gemini API for available models."""
    # This would require API support
    pass
```

Currently, models must be manually added to `SUPPORTED_MODELS`.

## Summary

**To add a new Gemini model:**
1. Add model ID to `SUPPORTED_MODELS` list in `bikeclf/config.py`
2. (Optional) Add display name to `MODEL_DISPLAY_NAMES`
3. Test with `python -m bikeclf.phase1.eval evaluate --model <model-id>`

**That's it!** The system handles everything else automatically.
