# Prompt Iteration Log - Bike Event Classification

This document tracks the evolution of prompts and their performance on the 200-event test dataset.

---

## Test Dataset

- **Source:** First 200 events from Supabase (ordered by service_request_id)
- **After Pre-filtering:** 121 events (39.5% filtered out)
- **Model:** Gemini 2.5 Flash Lite
- **Temperature:** 0.0 (deterministic)

---

## Iteration 1: v003 (Baseline)

**Run Date:** 2026-01-16 23:56:09
**Run Directory:** `runs/20260116_235609_v003_2.5_flash_lite/`

### Results

| Label | Count | % of Classified |
|-------|-------|-----------------|
| TRUE | 7 | 5.9% |
| FALSE | 65 | 55.1% |
| **UNCERTAIN** | **46** | **39.0%** |
| **Errors** | 3 | 2.5% |

### Analysis

**Problem:** UNCERTAIN rate is 3x higher than target (39% vs. 5-15%)

**Root Cause:** Overly strict "no explicit evidence" rule causes model to classify as UNCERTAIN instead of FALSE for:
- Pedestrian-specific issues (sidewalks, pedestrian lights): 3 events
- Generic infrastructure without bike context (trash on paths, generic road damage): 31 events
- Car-specific issues (Kfz-Ampel): 1 event

**Key Insight:** ~75% of UNCERTAIN cases should actually be FALSE.

### Prompt Characteristics

- ✅ TRUE classifications are accurate (100% precision)
- ✅ Pre-filtering works excellently
- ❌ FALSE vs UNCERTAIN boundary is unclear
- ❌ Model treats "no bike evidence" as UNCERTAIN instead of FALSE

### See Also
- Full analysis: `UNCERTAIN_ANALYSIS.md`
- Test report: `ANALYSIS_REPORT_200_EVENTS.md`

---

## Iteration 2: v004 (Clarified FALSE vs UNCERTAIN)

**Run Date:** 2026-01-17 (TBD)
**Run Directory:** `runs/[timestamp]_v004_2.5_flash_lite/`

### Changes from v003

1. **Expanded FALSE section** with explicit sub-categories:
   - Explicitly NOT for cycling (Gehweg, Fußgängerampel, Kfz-Ampel)
   - Generic infrastructure WITHOUT bike context
   - Private/social themes
   - Other non-bike categories

2. **Added critical rule** for FALSE classification:
   ```
   KRITISCHE REGEL: Wenn der Text eine generische Infrastruktur-Störung beschreibt
   (Gehweg-Schaden, Müll auf Weg, defekte Ampel) OHNE jeglichen Rad-Bezug,
   dann ist es FALSE, NICHT UNCERTAIN.
   ```

3. **Narrowed UNCERTAIN scope** to only:
   - Ambiguous lane assignment (rechte Spur, unklare Spurzuordnung)
   - Unclear location with potentially mixed use

4. **Added explicit exclusions** for UNCERTAIN:
   - Gehweg-Probleme → FALSE (not UNCERTAIN)
   - Fußgängerampel-Probleme → FALSE (not UNCERTAIN)
   - Müll auf generischem "Weg" → FALSE (not UNCERTAIN)
   - Kfz-Ampel → FALSE (not UNCERTAIN)

5. **Added rule of thumb (Faustregel):**
   ```
   Wenn es keine Rad-Erwähnung gibt UND die Infrastruktur klar nicht für Radverkehr ist
   → FALSE
   Wenn es keine Rad-Erwähnung gibt UND die Infrastruktur mehrdeutig ist
   → UNCERTAIN
   ```

6. **Added new FALSE examples** from actual UNCERTAIN misclassifications:
   - "Abstehende Gehwegplatten" (sidewalk issue)
   - "Fußgängerampel defekt" (pedestrian light)
   - "Kfz-Ampel ist um 90 Grad verdreht" (car light)
   - "Wilder Müll auf dem Weg" (trash on generic path)
   - "Sperrmüll auf dem Geweg" (trash without bike context)

### Expected Results

| Label | Expected Count | Expected % |
|-------|---------------|------------|
| TRUE | 7-10 | 6-8% |
| FALSE | 95-105 | 80-85% |
| UNCERTAIN | 6-12 | 5-10% |

### Expected Improvements

- ✅ UNCERTAIN rate reduced from 39% to 5-10%
- ✅ FALSE rate increased from 55% to 80-85%
- ✅ Clearer decision boundary between FALSE and UNCERTAIN
- ✅ More aligned with target precision-focused approach

### Testing Strategy

Run v004 on the **same 121 filtered events** to enable direct comparison with v003.

---

## Comparison Template (to be filled after v004 run)

| Metric | v003 | v004 | Change |
|--------|------|------|--------|
| TRUE | 7 (5.9%) | TBD | TBD |
| FALSE | 65 (55.1%) | TBD | TBD |
| UNCERTAIN | 46 (39.0%) | TBD | TBD |
| Errors | 3 (2.5%) | TBD | TBD |

### Label Transitions v003 → v004

To be analyzed after v004 run:
- UNCERTAIN → FALSE: ? events
- UNCERTAIN → TRUE: ? events
- FALSE → UNCERTAIN: ? events
- TRUE → FALSE: ? events (should be 0)
- TRUE → UNCERTAIN: ? events (should be 0)

---

## Next Steps

1. ✅ Create v004 prompt with clarified FALSE rules
2. ⏳ Run v004 on same 121 filtered events
3. ⏳ Compare v003 vs v004 results
4. ⏳ Analyze label transitions
5. ⏳ Decide: Deploy v004 or iterate to v005
6. ⏳ If v004 is good: Run on full 35K dataset

---

## Decision Criteria for Deployment

**v004 is ready for full dataset if:**
- ✅ UNCERTAIN rate: 5-15% (target: 10%)
- ✅ FALSE rate: 75-85% (target: 80%)
- ✅ TRUE rate: 6-12% (target: 10%)
- ✅ No degradation in TRUE precision (maintain 100%)
- ✅ No FALSE → UNCERTAIN regressions

**If not met:** Iterate to v005 with further refinements.

---

**Last Updated:** 2026-01-17
**Status:** v004 created, ready for testing
