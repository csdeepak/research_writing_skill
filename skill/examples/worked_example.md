# Worked example: from "information dump" to research story

All content is from the **synthetic** `demo_project/`. The point is to show *mechanisms* acting
on text, not house style. Your paper's voice can differ completely.

---

## 1. Evidence → spine (steps 2–3)

CORPUS_AGENT found 12 evidence items: 6 hard results, 1 negative result (E005: no benefit at
s = 0.8), 1 superseded conflicting value (E010: an early 0.66 that the notes say preceded a
bug fix), and soft notes. Two findings drove the design:

- **Conflict handled, not averaged.** E010 vs E003 was raised as `CONFLICTING_EVIDENCE`. The
  notes explain E010 as a pre-fix run, so the user confirmed E003, and E010 became
  `superseded`.
- **The negative result is part of the story.** E005 turns "RWN fixes level shift" into "RWN
  fixes *moderate* level shift". That is spine line 5 and contribution 2.

The spine (`demo_project/.rcs/story/spine.md`) was written before any prose. Every line
carries claim or limitation IDs.

## 2. Result dumping → Result Interpretation Chain (step 10, section rules)

**Before** (variant D, `tests/perturbations/D_result_dumping.md`):

> The baseline obtained an MAE of 0.412 without shift and RWN obtained 0.409. At s = 0.2 the
> baseline obtained 0.471 and RWN 0.421. At s = 0.4 the baseline obtained 0.553 and RWN 0.433.
> At s = 0.6 …

Every number is correct. The reader still can't answer Q7 (the strongest result), Q8 (what it
establishes), or Q9 (what it doesn't). The lint flags `A6-result-dumping`.

**After** (variant A), the RIC steps are visible:

| RIC step | Text in variant A |
|----------|-------------------|
| 1 What was measured | "### 3.1 RQ1: accuracy with and without level shift" (the section opens with the question) |
| 2 What happened | "the baseline's error grew with shift magnitude while RWN's stayed close to its unshifted level (Figure 1)" |
| 3 How large | "At s = 0.6, RWN reduced MAE from 0.641 to 0.452 … the reduction was 11–29%" |
| 4 Robust? | "Seed spread was at most 0.012, small next to these differences, so the ordering held across seeds" |
| 5 Meaning | "Adapting the normalization therefore cost no measurable accuracy here" |
| 6 Link to RQ | "which answers the second half of RQ1" / "RQ1 is answered yes for moderate shifts only" |
| 7 What we can't conclude | "a gap of about one standard deviation, so we cannot claim a benefit there" |

The numbers are identical in both variants. Only the reader's path through them changed.

## 3. Overclaim → evidence-matched language (step 17)

Variant E says: *"These results demonstrate that stale normalization, not model capacity, causes
forecasting failure under shift {C005}."* C005 is typed `interpretation` (capacity was held
fixed, not varied: L002), so the lint raises **ERROR `B4-verb-vs-type`**. The permitted repair
is to *downgrade the language*: "suggest … account for much of … in this setting". Never find a
way to keep "demonstrate".

## 4. Buried contribution → orientation (steps 8, 13)

Variant F has correct content, but its introduction never states a question or a contribution.
The lint raises `A1-late-question` and `A2-buried-contribution`. The architecture fix is
structural: add paragraph slots I.3 (RQ1/RQ2) and I.4 (contributions, each tied to a result).
This isn't a sentence-level edit.

## 5. Citation misuse → citation pipeline (step 16)

Variant G attaches placeholders [R1]–[R6] to claims. Each has a defined "actual content" in
`tests/perturbations/EXPECTED.json`. The lint can't see this. The citation audit catches it:
R1 fails *support*, R3 fails *strength*, R5 *contradicts* the sentence it's cited for, and R6
fails *status* (opinion). This is why citation correctness is a pipeline step, not a lint
rule.

## 6. What the reviewer is expected to see

For every variant, `EXPECTED.json` lists the dimensions that a calibrated REVIEW_AGENT should
score lower than on A, and the reconstruction questions that should degrade. A reviewer that
fails to notice them is not trusted for gating (`docs/04_EVALUATION_FRAMEWORK.md` §8, step 9).
