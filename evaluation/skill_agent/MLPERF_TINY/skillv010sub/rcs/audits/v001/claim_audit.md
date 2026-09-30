# Step 12 -- Evidence / claim audit (draft v001)

## Numeric spot-check (>20%, min 10, re-read from project/paper.txt directly)
22 distinct numeric/textual values used in the draft were re-read directly from
`project/paper.txt` (not from the evidence map) and compared character-for-character:
91.6, 91.7, 92.2, 38.6K params, 86.5%, 200 images, AUC 0.88, AUC 0.86, AUC 0.85, 248 samples,
52.5 KB, 325 KB, 96 KB, 270 KB, 90%, 80%, 85%, "June 2021", "NUCLEO-L4R5ZI", 105,829 utterances,
2,618 speakers, 60,000/6,000/10,000 CIFAR-10 counts, plus the 10-250 MHz / <50 mW envelope from
`project/README_1.md`. **All 22 matched the source exactly; 0 mismatches.** (script and result
recorded in the session transcript; this is >20% of the ~28 quantitative evidence items, above
the >=10 floor.)

## Every claim-like sentence tagged?
`lint_draft.py --rcs .rcs` (see `lint_v001.json`) found 0 orphan-claim errors after the fix
round; 3 remaining WARN-level orphan-claim flags were reviewed by hand and are background/
definitional sentences (what TinyML is; the wireless-vs-compute energy-cost aside; the
quantization definition), not contestable findings of this paper -- accepted, not tagged, per
information_design.md's own carve-out that transitional/definitional content needs no claim ID.

## Claim type vs. verb
`lint_draft.py --rcs .rcs` found 0 `B4-verb-vs-type` errors in the current draft (2 were found
and fixed in the previous pass -- see state.json log -- both were "shows that .../ demonstrate"
attached to C006, an `interpretation` claim; rewritten to "is consistent with .../ show").
Spot-checked the remaining claim types by hand:
- C009-C011 (`literature`): verbs used are "does not profile/represent", "need... has no
  support", "plans to..., precludes" -- report what the source says, no upgrade.
- C002, C012 (`derived`): verbs "is set... below", "there is a need for / closes this gap" --
  matches evidence_model.md's permitted derived-claim frames.
- C006 (`interpretation`): "is consistent with" throughout -- correct frame for interpretation.
- C014-C016 (`future`): "describe three directions", "extending / widening" -- framed as the
  authors' stated plans, not promises of a result ("will solve"), consistent with the `future`
  type's permitted frame.

## Negative-result / non-positive-finding coverage
This project has no failed run or non-beneficial ablation in the classic sense (see
`missing_evidence.json`'s note). The three findings that function as this paper's negative/
qualifying evidence are all present in the draft: no submission changed the training dataset
(C008, Results P4); the streaming/feature-extraction measurement tension the authors flag
themselves (L004, Discussion); and the narrow closed-division architecture coverage (L005,
Discussion). None was moved to a supplement or omitted (TASK.md allows no supplement in any
case) -- **no `SELECTIVE_REPORTING` finding.**

## Confidence vs. abstract placement
Only claims with confidence >= moderate appear in the Abstract (C001 high, C003/C004 high, C005
moderate, C006 moderate, C009-C012 moderate) -- no `low`-confidence claim (C014-C016, the future
claims) appears in the Abstract, consistent with evidence_model.md section 4.

**No blocking defect found under evaluation_rubric.md section 3** (no dimension inspectable here
scored <=2; no distortion found in the step-11 reconstruction; no unresolved overclaim flag;
citation status covered in citation_audit.json; the one open failure, F001 VENUE_UNKNOWN, is
accepted per the run's own constraints).
