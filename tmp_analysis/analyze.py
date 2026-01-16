import json
from pathlib import Path
from collections import Counter, defaultdict
import re

run_a = Path('/Volumes/T7/flag-the-event/runs/20260116_135146_v001_2.0-flash-001')
run_b = Path('/Volumes/T7/flag-the-event/runs/20260116_143925_v001_2.5-lite')


def load_jsonl(path):
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows

pred_a = {r['id']: r for r in load_jsonl(run_a / 'predictions.jsonl')}
pred_b = {r['id']: r for r in load_jsonl(run_b / 'predictions.jsonl')}

ids = sorted(set(pred_a) & set(pred_b))

# Basic stats

def basic_stats(preds):
    gold = [preds[i]['gold_label'] for i in ids]
    pred = [preds[i]['pred']['label'] for i in ids]
    total = len(ids)
    correct = sum(g == p for g, p in zip(gold, pred))
    return {
        'total': total,
        'correct': correct,
        'accuracy': correct / total,
        'gold_dist': Counter(gold),
        'pred_dist': Counter(pred)
    }

stats_a = basic_stats(pred_a)
stats_b = basic_stats(pred_b)

# Compare per-id
compare = []
for i in ids:
    ga = pred_a[i]['gold_label']
    pa = pred_a[i]['pred']['label']
    pb = pred_b[i]['pred']['label']
    compare.append({
        'id': i,
        'gold': ga,
        'a': pa,
        'b': pb,
        'a_correct': pa == ga,
        'b_correct': pb == ga,
        'subject': pred_a[i]['subject'],
        'description': pred_a[i]['description'],
        'a_reasoning': pred_a[i]['pred']['reasoning'],
        'b_reasoning': pred_b[i]['pred']['reasoning'],
    })

# Differing predictions
model_diff = [c for c in compare if c['a'] != c['b']]

# Error types heuristic
bike_markers = re.compile(r"\b(radweg|radfahr|radfahrer|fahrrad|fahrradständer|fahrradstaender|fahrradbügel|fahrradbu(e)?gel|radfurt|fahrradstraße|fahrradstrasse|fahrradzone|schutzstreifen|geh- und radweg|radweg|rad-?streifen)\b", re.IGNORECASE)
private_markers = re.compile(r"\b(verloren|gefunden|fundbüro|fundbuero|diebstahl|gestohlen|schlüssel|schloss|zu verschenken|verkauf|kaufen|privat|büro|buero|keller|wohnung)\b", re.IGNORECASE)


def error_type(case):
    text = f"{case['subject']} {case['description']}"
    has_bike = bool(bike_markers.search(text))
    has_private = bool(private_markers.search(text))
    if has_private and has_bike:
        return 'private_bike'
    if has_bike:
        return 'bike_keyword_no_private'
    return 'no_bike_evidence'


def error_summary(preds):
    errors = [c for c in compare if preds[c['id']]['pred']['label'] != c['gold']]
    types = Counter(error_type(c) for c in errors)
    return errors, types

errors_a, types_a = error_summary(pred_a)
errors_b, types_b = error_summary(pred_b)

# Reasoning lengths and evidence sizes

def reasoning_stats(preds):
    lens = [len(preds[i]['pred']['reasoning']) for i in ids]
    ev_counts = [len(preds[i]['pred'].get('evidence') or []) for i in ids]
    return {
        'avg_reasoning_len': sum(lens) / len(lens),
        'avg_evidence_count': sum(ev_counts) / len(ev_counts),
        'avg_confidence': sum(preds[i]['pred'].get('confidence', 0) for i in ids) / len(ids)
    }

reason_a = reasoning_stats(pred_a)
reason_b = reasoning_stats(pred_b)

# Prepare a compact report dict
report = {
    'stats': {'2.0-flash-001': stats_a, '2.5-flash-lite': stats_b},
    'diff_count': len(model_diff),
    'diff_cases': model_diff,
    'errors': {
        '2.0-flash-001': {'count': len(errors_a), 'types': types_a, 'cases': errors_a},
        '2.5-flash-lite': {'count': len(errors_b), 'types': types_b, 'cases': errors_b}
    },
    'reasoning': {'2.0-flash-001': reason_a, '2.5-flash-lite': reason_b}
}

# Print a human-readable summary
print('DATASET SIZE:', len(ids))
print('LABEL DISTRIBUTION (gold):', stats_a['gold_dist'])
print('\nACCURACY:')
print('  2.0-flash-001:', f"{stats_a['accuracy']:.3f}")
print('  2.5-flash-lite:', f"{stats_b['accuracy']:.3f}")
print('\nERROR TYPE COUNTS:')
print('  2.0-flash-001:', dict(types_a))
print('  2.5-flash-lite:', dict(types_b))
print('\nREASONING/EVIDENCE AVG:')
print('  2.0-flash-001:', reason_a)
print('  2.5-flash-lite:', reason_b)
print('\nDIFFERING PREDICTIONS:', len(model_diff))
print('IDS:', ', '.join(c['id'] for c in model_diff))

# Print misclassified summaries for 2.0 flash
print('\nMISCLASSIFIED (2.0-flash-001):')
for c in errors_a:
    print(f"- {c['id']} gold={c['gold']} pred={pred_a[c['id']]['pred']['label']} subject={c['subject']}")

print('\nMISCLASSIFIED (2.5-flash-lite):')
for c in errors_b:
    print(f"- {c['id']} gold={c['gold']} pred={pred_b[c['id']]['pred']['label']} subject={c['subject']}")

# Save json report
(Path('/Volumes/T7/flag-the-event/tmp_analysis') / 'report.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
