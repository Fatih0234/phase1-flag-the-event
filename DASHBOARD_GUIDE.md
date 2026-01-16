# Dashboard User Guide

## 🚀 Quick Start

### Launch the Dashboard

```bash
# From project root
./run_dashboard.sh

# Or directly with streamlit
streamlit run bikeclf/phase1/dashboard.py
```

Access at: **http://localhost:8501**

## 📊 Dashboard Overview

The dashboard provides a comprehensive view of your evaluation runs with interactive visualizations and detailed error analysis.

### Main Sections

#### 1. **Sidebar: Run Selection**
- **Dropdown**: Select any evaluation run from `runs/` directory
- **Run Details**: Shows prompt version, model, timestamp, and prediction counts
- Automatically discovers all available runs sorted by date (newest first)

#### 2. **Metrics Overview** (Top of page)
Four key metrics displayed as cards:
- **Accuracy**: Overall classification accuracy
- **Macro F1**: F1 score averaged across all classes (treats classes equally)
- **Correct Predictions**: Count of correct predictions
- **Misclassified**: Count of errors

#### 3. **Per-Class Performance**
Table showing precision, recall, F1, and support for each class:
- `true` - Bike-related issues
- `false` - Non-bike issues
- `uncertain` - Ambiguous cases

#### 4. **Confusion Matrix** (Left column)
Interactive heatmap showing:
- Rows: Gold (true) labels
- Columns: Predicted labels
- Cell values: Count of predictions
- Diagonal: Correct predictions
- Off-diagonal: Misclassifications

**How to read:**
- `true → false` (row 0, col 1): True labels predicted as false
- `false → true` (row 1, col 0): False labels predicted as true

#### 5. **Label Distribution** (Right column)
Bar chart comparing:
- **Gold**: Actual label distribution in dataset
- **Predicted**: Model's predicted distribution

**What to look for:**
- Large differences indicate systematic bias
- Example: If model predicts fewer `uncertain` cases, it might be over-confident

#### 6. **Misclassified Predictions Table**
Detailed table of all errors with:
- **Filters**: Filter by gold label and predicted label
- **Sort**: Sort by confidence, text length, or ID
- **Columns**: ID, gold label, predicted label, confidence, subject, text length

**Workflow:**
1. Filter to specific error types (e.g., `true → false`)
2. Sort by confidence (low confidence = model was unsure)
3. Inspect individual cases

#### 7. **Detailed Case Inspection**
Select any misclassified case to see:
- **Labels**: Gold vs predicted, confidence score
- **Text Length**: Number of characters
- **Latency**: Model response time
- **Attempts**: Number of retry attempts (1 or 2)
- **Subject**: Issue title
- **Evidence**: Quotes extracted by model
- **Reasoning**: Model's explanation
- **Full Description**: Complete text

**Use cases:**
- Understand why model made mistake
- Identify patterns in evidence extraction
- Find prompt improvement opportunities

#### 8. **Failed Predictions** (if any)
Table of predictions that failed validation:
- Usually due to API errors or schema violations
- Shows error message and attempts
- These are logged to `errors.jsonl`

#### 9. **Performance by Text Length**
Analysis of accuracy across length buckets:
- **Buckets**: 0-100, 100-200, 200-300, 300-500, 500-1000, 1000+ chars
- **Table**: Shows correct count, total, accuracy, average confidence per bucket
- **Bar Chart**: Visualizes accuracy by bucket

**What to look for:**
- Does accuracy drop for very short texts? (Not enough context)
- Does accuracy drop for very long texts? (Too much noise)
- Which bucket has lowest accuracy? (Focus prompt improvements there)

#### 10. **Confidence Distribution**
Two histograms:
- **Left**: Overall confidence distribution (all predictions)
- **Right**: Confidence split by correctness (correct vs incorrect)

**Healthy pattern:**
- Correct predictions should have **higher confidence**
- Incorrect predictions should have **lower confidence**
- If overlap is large, model is not well-calibrated

#### 11. **Error Breakdown**
Bar chart of most common misclassification patterns:
- Format: `gold_label → predicted_label`
- Example: `true → false` means bike-related issues misclassified as non-bike
- Sorted by frequency (most common first)

**Use cases:**
- Identify systematic errors
- Prioritize prompt fixes for most frequent errors
- Track improvement across prompt versions

## 🔍 Common Analysis Workflows

### Workflow 1: Find Systematic Errors

1. **Check Confusion Matrix**: Identify which cells have high counts
2. **Filter Misclassifications**: Use filters to show only that error type
3. **Sort by Confidence**: Start with high-confidence errors (model was sure but wrong)
4. **Inspect Cases**: Read descriptions and evidence
5. **Identify Pattern**: What do these cases have in common?
6. **Update Prompt**: Add rules or examples to address pattern

**Example:**
- Confusion matrix shows 7 cases of `true → uncertain`
- Filter to show only these cases
- Notice all have "Schutzstreifen" but model marks as uncertain
- Update prompt to make "Schutzstreifen" a strong TRUE signal

### Workflow 2: Compare Prompt Versions

1. **Select Run A** (e.g., v001): Note metrics and error patterns
2. **Take screenshots** or note specific misclassified IDs
3. **Switch to Run B** (e.g., v002): Compare metrics
4. **Check same IDs**: Did v002 fix the errors you targeted?
5. **Check new errors**: Did v002 introduce new mistakes?

**Tip:** Open two browser tabs with different runs for side-by-side comparison

### Workflow 3: Text Length Analysis

1. **View "Performance by Text Length"** section
2. **Identify worst bucket**: Which length range has lowest accuracy?
3. **Filter misclassifications** and sort by text length
4. **Inspect cases** from problematic bucket
5. **Hypothesis**: Too short? Need more keywords. Too long? Noise overwhelms signal.
6. **Test**: Update prompt with length-specific guidance

**Example findings:**
- Short texts (0-100 chars): Need explicit keywords like "Radweg"
- Long texts (500+ chars): Model gets distracted by irrelevant details

### Workflow 4: Calibration Check

1. **View Confidence Distribution** (split by correctness)
2. **Check overlap**: Do incorrect predictions have high confidence?
3. **Sort misclassifications by confidence** (descending)
4. **Inspect high-confidence errors**: Model was very sure but wrong
5. **Update prompt**: Add VETO rules or explicit counterexamples

**Red flag:**
- If incorrect predictions have average confidence > 0.8, model is overconfident
- Need stronger VETO rules in prompt

### Workflow 5: Error Pattern Deep Dive

1. **View "Error Breakdown"** bar chart
2. **Click most common error** (e.g., `false → uncertain`)
3. **Filter table** to show only that pattern
4. **Read all cases**: Look for common words, topics, or structures
5. **Document pattern**: Write down what makes these hard
6. **Prompt strategy**: Add explicit examples or decision rules

## 📈 Metrics Interpretation

### Accuracy
- **Good**: > 0.85 (85%)
- **Acceptable**: 0.70 - 0.85
- **Needs work**: < 0.70

### Macro F1
- **Why it matters**: Treats all classes equally (doesn't favor majority class)
- **Good**: > 0.80
- **Target**: Match or exceed accuracy

### Per-Class Metrics

**Precision**: Of all cases predicted as X, how many were actually X?
- Low precision → Many false positives for this class

**Recall**: Of all actual X cases, how many did we predict as X?
- Low recall → Many false negatives (missed cases)

**Example:**
```
Class "true":
  Precision: 0.67 → 33% of "true" predictions were wrong
  Recall: 1.00 → We caught all actual bike cases (but with false alarms)
```

**Strategy:**
- Low precision, high recall → Model is too eager (tighten criteria)
- High precision, low recall → Model is too conservative (loosen criteria)

## 🎯 Tips and Tricks

### Tip 1: Bookmark Runs
After launching dashboard, the URL includes run selection. Bookmark URLs to quickly return to specific runs.

### Tip 2: Export Data
Use browser's copy function on tables to paste into spreadsheet for further analysis.

### Tip 3: Track Changes
Keep a notebook of:
- Run name
- Accuracy / F1
- Top 3 error patterns
- Changes made in next prompt version

### Tip 4: Focus on Impact
Fix the most frequent errors first (highest bars in Error Breakdown). Small improvements to common errors = big accuracy gains.

### Tip 5: Test Hypotheses
Before updating prompt:
1. Form hypothesis: "Short texts need explicit 'Radweg' mention"
2. Check in dashboard: Filter by length 0-100, verify pattern
3. Update prompt with rule
4. Run new evaluation
5. Check if accuracy improved for that bucket

## 🚨 Troubleshooting

### Dashboard shows "No runs found"
**Solution:** Run an evaluation first:
```bash
python -m bikeclf.phase1.eval evaluate --prompt v001
```

### Metrics don't load
**Check:** Ensure run directory has both `predictions.jsonl` and `metrics.json`

### Dashboard is slow
**Cause:** Loading many predictions (>1000)
**Solution:** Dashboard caches data - first load is slow, subsequent refreshes are fast

### Can't see recent run
**Solution:** Refresh browser page (Ctrl+R or Cmd+R)

## 📚 Related Commands

```bash
# Run evaluation
python -m bikeclf.phase1.eval evaluate --prompt v001

# List available prompts
python -m bikeclf.phase1.eval list-prompts

# Compare two runs
python -m bikeclf.phase1.eval diff \
  runs/20260116_120000_v001/predictions.jsonl \
  runs/20260116_130000_v002/predictions.jsonl

# Launch dashboard
./run_dashboard.sh
```

## 🎓 Advanced: Manual Analysis

If you need more control, load predictions directly:

```python
import json
import pandas as pd

# Load predictions
predictions = []
with open("runs/20260116_135146_v001/predictions.jsonl") as f:
    for line in f:
        predictions.append(json.loads(line))

# Convert to DataFrame
df = pd.DataFrame(predictions)

# Custom analysis
df['text_length'] = df['description'].str.len()
df['is_correct'] = df['gold_label'] == df['pred'].apply(lambda x: x['label'])

# Length-based analysis
print(df.groupby('gold_label')['text_length'].describe())

# Misclassifications only
errors = df[~df['is_correct']]
print(errors[['id', 'gold_label', 'pred']].to_string())
```

## 🤝 Feedback

Found a bug or have a feature request?
- Open issue: https://github.com/Fatih0234/phase1-flag-the-event/issues
- Or update `dashboard.py` directly

Happy analyzing! 🚴‍♀️
