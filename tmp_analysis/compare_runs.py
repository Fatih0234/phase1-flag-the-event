import json
from pathlib import Path
from collections import Counter, defaultdict

runs_root = Path('/Volumes/T7/flag-the-event/runs')

run_dirs = {
    'v001': {
        '2.0': runs_root / '20260116_135146_v001_2.0-flash-001',
        '2.5': runs_root / '20260116_143925_v001_2.5-lite',
    },
    'v002': {
        '2.0': runs_root / '20260116_153132_v002_2.0-flash-001',
        '2.5': runs_root / '20260116_153311_v002_2.5-lite',
    },
    'v003': {
        '2.0': runs_root / '20260116_153414_v003_2.0-flash-001',
        '2.5': runs_root / '20260116_153542_v003_2.5-lite',
    },
}


def load_jsonl(path):
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def load_metrics(path):
    return json.loads(path.read_text(encoding='utf-8'))


def summarize_predictions(preds):
    gold = [p['gold_label'] for p in preds]
    pred = [p['pred']['label'] for p in preds]
    total = len(preds)
    correct = sum(g == p for g, p in zip(gold, pred))
    return {
        'total': total,
        'accuracy': correct / total,
        'gold_dist': Counter(gold),
        'pred_dist': Counter(pred),
    }


report = {}

for version, models in run_dirs.items():
    report[version] = {}
    for model_key, run_dir in models.items():
        preds = load_jsonl(run_dir / 'predictions.jsonl')
        metrics = load_metrics(run_dir / 'metrics.json')
        errors = [p for p in preds if p['pred']['label'] != p['gold_label']]
        report[version][model_key] = {
            'run_dir': str(run_dir),
            'metrics': metrics,
            'summary': summarize_predictions(preds),
            'errors': errors,
        }

# Print a concise report
print('DATASET SIZE:', report['v001']['2.0']['summary']['total'])
print()

for version in ['v001', 'v002', 'v003']:
    print(f'== {version} ==')
    for model_key in ['2.0', '2.5']:
        m = report[version][model_key]['metrics']
        print(f"  {model_key}: acc={m['accuracy']:.3f} macro_f1={m['macro_f1']:.3f}")
    print()

print('MISCLASSIFICATIONS (by version/model):')
for version in ['v001', 'v002', 'v003']:
    for model_key in ['2.0', '2.5']:
        errors = report[version][model_key]['errors']
        print(f"  {version} {model_key}: {len(errors)}")
print()

# List error IDs for 2.0 to compare prompt shifts
for version in ['v001', 'v002', 'v003']:
    errors = report[version]['2.0']['errors']
    ids = [e['id'] for e in errors]
    print(f"2.0 errors {version}: {', '.join(ids) if ids else 'none'}")
print()

# List error IDs for 2.5 to compare prompt shifts
for version in ['v001', 'v002', 'v003']:
    errors = report[version]['2.5']['errors']
    ids = [e['id'] for e in errors]
    print(f"2.5 errors {version}: {', '.join(ids) if ids else 'none'}")
print()

# Save full report
Path('/Volumes/T7/flag-the-event/tmp_analysis/compare_report.json').write_text(
    json.dumps(report, indent=2, ensure_ascii=False),
    encoding='utf-8'
)
