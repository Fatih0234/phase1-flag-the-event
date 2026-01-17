# UNCERTAIN Classifications Analysis - v003 Prompt

**Date:** 2026-01-17
**Total UNCERTAIN:** 46 out of 118 classified events (39.0%)
**Target UNCERTAIN Rate:** 5-15%
**Issue:** Model is **3x more conservative** than desired

---

## Root Cause Analysis

### Primary Issue: Overly Strict "No Explicit Evidence" Rule

The v003 prompt contains this instruction:

> **CRITICAL: Do NOT infer bike-relevance from context alone**

This causes the model to classify as UNCERTAIN any event that:
1. Could plausibly affect cyclists BUT
2. Doesn't explicitly mention bike-specific keywords

### Pattern Breakdown

| Pattern | Count | % of UNCERTAIN | Should Be |
|---------|-------|----------------|-----------|
| **No explicit evidence** | 20 | 43.5% | FALSE |
| **Defective surface (unclear location)** | 11 | 23.9% | FALSE |
| **Other** | 7 | 15.2% | Mixed |
| **Trash/waste on path** | 4 | 8.7% | FALSE |
| **Sidewalk/pedestrian issue** | 3 | 6.5% | FALSE |
| **Traffic light issue** | 1 | 2.2% | FALSE |

**Key Insight:** ~75% of UNCERTAIN cases should actually be FALSE.

---

## Specific Problems

### Problem 1: Sidewalk Issues Marked as UNCERTAIN ❌

**Example: Event 100-2025**
- Description: "Abstehende Gehwegplatten im Bereich Taunusstr"
- Current: UNCERTAIN (0.6 confidence)
- Reasoning: "beschreibt eine defekte Oberfläche auf dem Gehweg, aber es gibt keine expliziten Hinweise auf Radinfrastruktur"

**Why this is wrong:**
- "Gehweg" (sidewalk) is explicitly for pedestrians
- No bike keywords → should be FALSE, not UNCERTAIN
- The model is confusing "could theoretically affect bikes" with "is bike infrastructure"

**What we need:** Clear guidance that generic sidewalk issues = FALSE unless bike-specific context exists

---

### Problem 2: Generic Trash on "Weg" Marked as UNCERTAIN ❌

**Example: Event 10013-2025**
- Description: "Der Weg hier wird schon seit Wochen nicht gereinigt"
- Current: UNCERTAIN (0.6 confidence)
- Reasoning: "erwähnt einen Weg, der nicht gereinigt wird, aber es gibt keine expliziten Hinweise auf Radinfrastruktur"

**Why this is wrong:**
- Generic "Weg" without bike context = NOT bike infrastructure
- This is just general maintenance, not bike-specific

**What we need:** "Weg" alone is not bike infrastructure. Only "Radweg", "Geh- und Radweg" count.

---

### Problem 3: Car Traffic Issues Marked as UNCERTAIN ❌

**Example: Event 10036-2025**
- Description: "Die Ampel von der Ostmerheimer Straße ist um 90Grad verdreht"
- Category: "Kfz-Ampel defekt" (car traffic light)
- Current: UNCERTAIN (0.9 confidence!)
- Reasoning: "mentions a defective traffic light for cars...but provides no explicit evidence related to bike infrastructure"

**Why this is wrong:**
- Category explicitly says "Kfz-Ampel" (car traffic light)
- No bike mention = FALSE, not UNCERTAIN

**What we need:** If it's explicitly a car-only issue, mark FALSE immediately.

---

### Problem 4: Confusing UNCERTAIN with FALSE ❌

The model is using UNCERTAIN when it should use FALSE in these scenarios:

1. **Generic infrastructure issues** (potholes, trash, broken signs) with NO bike context
   - Current: UNCERTAIN
   - Should be: FALSE

2. **Pedestrian-specific issues** (sidewalk problems, pedestrian lights)
   - Current: UNCERTAIN
   - Should be: FALSE

3. **Car-specific issues** (Kfz-Ampel, parking, car lanes)
   - Current: UNCERTAIN
   - Should be: FALSE

**The confusion:**
- Model thinks: "No bike evidence = UNCERTAIN"
- Should think: "No bike evidence = FALSE"

**Reserve UNCERTAIN for:**
- "Defekte Oberfläche" with unclear location (could be road or bike lane)
- "Straße" with damage but unclear if it affects bike lane
- "Kreuzung" issues without location specificity

---

## Correct vs. Incorrect UNCERTAIN Classifications

### ✅ CORRECT UNCERTAIN (Acceptable - keep as is)

**Event 10024-2025:**
- Description: "Das Loch zwischen Bahnhof Mülheim und der U-Bahn Station ist sogar noch tiefer geworden"
- Why UNCERTAIN is correct: Location unclear, could be on bike lane or car lane
- Needs: Manual review with local knowledge

**Event 1004-2026:**
- Description: "Mehrere Schlaglöcher vom Niehler Ei aus kommend Richtung Autobahn A1. Rechte Spur"
- Why UNCERTAIN is correct: "Rechte Spur" often = bike lane in Germany, but not explicit

### ❌ INCORRECT UNCERTAIN (Should be FALSE)

**Event 1-2026 - Pedestrian traffic light with broken glass**
- Current: UNCERTAIN
- Should be: FALSE
- Reason: "Fußgängerampel" = pedestrian light, no bike context

**Event 100-2025 - Protruding sidewalk slabs**
- Current: UNCERTAIN
- Should be: FALSE
- Reason: "Gehwegplatten" = sidewalk, explicitly pedestrian

**Event 10010-2025 - Trash on "Geweg"**
- Current: UNCERTAIN
- Should be: FALSE
- Reason: Generic path with trash, no bike context

---

## Proposed Changes for v004 Prompt

### Change 1: Clarify the UNCERTAIN Category

**Current (v003):**
```
'uncertain': Insufficient information to determine bike-relevance
- Generic road damage without location specificity
- Ambiguous "Straße" references that could be bike lane or car lane
```

**Proposed (v004):**
```
'uncertain': Insufficient information to determine bike-relevance
ONLY use this when:
- "Defekte Oberfläche" or "Schlagloch" WITHOUT explicit location (could be bike lane OR car lane)
- "Rechte Spur" or similar ambiguous lane references
- "Straße" damage where the specific lane is unclear

Do NOT use 'uncertain' for:
- Generic "Gehweg" (sidewalk) issues → FALSE
- Generic "Weg" without bike context → FALSE
- "Kfz-Ampel" or car-specific infrastructure → FALSE
- Trash/waste without bike context → FALSE
```

### Change 2: Add Explicit FALSE Rules

**Add new section after UNCERTAIN definition:**

```markdown
## When to Classify as FALSE

Mark as 'false' immediately if:

1. **Pedestrian-specific:** "Gehweg", "Fußgängerampel", "Bürgersteig" with NO bike mention
2. **Car-specific:** "Kfz-Ampel", "Parkplatz", "Fahrspur" (unless explicitly "rechte Spur" near "Radweg")
3. **Generic infrastructure:** "Weg", "Straße", "Kreuzung" with NO bike-specific context
4. **Waste/trash:** "Wilder Müll", "Sperrmüll" on generic paths with NO bike mention
5. **Buildings/indoor:** Anything related to buildings, houses, private property

**Key principle:** If there's no bike-specific evidence AND the context is clearly non-bike (pedestrian/car/general), classify as FALSE, not UNCERTAIN.
```

### Change 3: Refine the "No Inference" Rule

**Current (v003):**
```
CRITICAL: Do NOT infer bike-relevance from context alone
```

**Proposed (v004):**
```
CRITICAL: Do NOT infer bike-relevance from context alone

However, you MUST distinguish between:
- **UNCERTAIN**: Could be bike lane or car lane, genuinely ambiguous
- **FALSE**: No bike context, clearly pedestrian/car/general infrastructure

If the text describes a generic infrastructure issue (sidewalk, pedestrian light, trash on a path) with NO mention of bikes, radfahrer, or radweg, classify as FALSE, not UNCERTAIN.

Reserve UNCERTAIN only for cases where the location is genuinely ambiguous (e.g., "defekte Oberfläche auf der Straße" without specifying which lane).
```

### Change 4: Add Examples of FALSE vs UNCERTAIN

**Add new examples section:**

```markdown
### Example Comparisons: FALSE vs UNCERTAIN

**FALSE Example 1:**
"Abstehende Gehwegplatten" (protruding sidewalk slabs)
→ FALSE: "Gehweg" is pedestrian-specific, no bike context

**FALSE Example 2:**
"Kfz-Ampel ist um 90 Grad verdreht" (car traffic light rotated)
→ FALSE: "Kfz-Ampel" explicitly for cars, no bike context

**FALSE Example 3:**
"Wilder Müll auf dem Weg" (trash on the path)
→ FALSE: Generic "Weg" with no bike context

**UNCERTAIN Example 1:**
"Schlagloch auf der rechten Spur" (pothole on right lane)
→ UNCERTAIN: "rechte Spur" could be bike lane in mixed traffic

**UNCERTAIN Example 2:**
"Defekte Oberfläche zwischen Bahnhof und U-Bahn" (surface damage between train stations)
→ UNCERTAIN: Location unclear, could affect bike lane or car lane

**TRUE Example:**
"Radweg sehr verengt Unfallgefahr" (bike lane very narrow dangerous)
→ TRUE: Explicit "Radweg" mention
```

---

## Expected Impact of Changes

### Current Results (v003)
- TRUE: 7 (5.9%)
- FALSE: 65 (55.1%)
- UNCERTAIN: 46 (39.0%)

### Expected Results (v004)
- TRUE: 7-10 (6-8%) - slight increase as some UNCERTAIN→TRUE
- FALSE: 95-105 (80-85%) - major increase as most UNCERTAIN→FALSE
- UNCERTAIN: 6-12 (5-10%) - aligned with target

### Specific Expected Movements

**UNCERTAIN → FALSE (~35 events):**
- 20 "no explicit evidence" → FALSE
- 8 "Gehweg/sidewalk" → FALSE
- 4 "trash on generic path" → FALSE
- 3 "car-specific" → FALSE

**UNCERTAIN → TRUE (~2-3 events):**
- Events with "rechte Spur" near bike context
- Events with implicit but strong bike safety concerns

**Remain UNCERTAIN (~8-10 events):**
- Genuine ambiguous location cases
- "Defekte Oberfläche" without lane specificity

---

## Summary

**Problem:** v003 prompt is TOO conservative, treating "no explicit evidence" as UNCERTAIN instead of FALSE.

**Root Cause:** Unclear boundary between FALSE and UNCERTAIN. Model thinks absence of bike evidence = uncertain classification.

**Solution:** Clarify that FALSE = "no bike context", UNCERTAIN = "ambiguous location", and add explicit FALSE rules for pedestrian/car/generic infrastructure.

**Expected Outcome:** Reduce UNCERTAIN from 39% to 5-10%, increase FALSE to 80-85%, maintain or slightly increase TRUE classifications.
