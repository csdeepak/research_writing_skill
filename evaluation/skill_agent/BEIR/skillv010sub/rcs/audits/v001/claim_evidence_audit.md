# Step 12 — Evidence/claim audit

## Tagging completeness
`python rce/tools/lint_draft.py .rcs/drafts/v001/paper.md --rcs .rcs` -> **0 errors**, 41 warnings, 49 info
(full findings in `.rcs/audits/v001/lint_v001.json`). All `{C###}`/`{L###}` tags resolve against
`claims/claim_evidence_map.json` (no `tag-unresolved` findings). Two `C1-orphan-claim` WARNs
remain, both reviewed and accepted:
- Section 6 para 1, "...making it look worse than it is...": a conditional/hypothetical sentence
  explaining the *mechanism* of possible bias, not itself an asserted finding; the finding it sets
  up is tagged two sentences later ({C017}).
- Section 6 para 3, the first Hole@10 sentence: part of a 3-sentence group reporting one evidence
  item (E037); the group carries {C017} on the first, second and third sentences after this fix
  (see draft line 127). No untagged claim-bearing sentence remains without a nearby tag covering it.

## Numeric fidelity (every number in the draft re-checked against its evidence item)
Spot-checked 100% of the draft's inline numbers (not just the required 20%), because the source
tables were flagged as extraction-damaged (`evidence/missing_evidence.json`) and needed the extra
care regardless:

| Draft number | Evidence item | Match |
|---|---|---|
| 7-18 points (in-domain gap) | E014 | exact (paper's own stated range) |
| 3 of 9 systems beat BM25 on average | E012 (count of positive signs) | exact |
| +11% / 16 of 18 / fails ArguAna+Touche | E012, E021 | exact |
| +2.5% / 9 of 18 | E012, E022 | exact |
| >350ms / 20-30x / <20ms / 20-25ms | E033 | exact |
| ~900GB / ~18GB | E035 | exact |
| -27.9% / -20.3% | E012 | exact |
| -7.4% / -2.8% | E012 | exact |
| 11 of 18 / +1.6% | E018, E012 | exact |
| 14 of 18 / 17 of 18 | E024 | exact |
| 17.3 points / 7.8 points | E026 | exact |
| ~10 vs ~160 words; 14 vs 89 words | E027 | exact |
| 15.3 points | E028 | exact |
| Table 1 (all cells) | E011 | exact (see research_evidence.json#E011 for the cross-validation method) |
| Table 2 (all cells) | E012, E013 | exact |
| Table 3 (all cells) | E037, E038 | exact |
| 0.89 / 0.13 (domain overlap) | E061 | exact, and marked `soft`/`extracted_from_image` in the evidence item; draft hedges with "about" |
| "about 8 points" (ANCE 0.735-0.654) | derived from E038, declared subtraction | exact, transparent |
| 5.8 points (ColBERT) | E038/E039 (paper's own stated delta) | exact |
| 980 pairs | E040 | exact |
| 512 word pieces | E009 | exact |
| 6.4/2.8/1.6/30.6/31.8% Hole@10 | E037 | exact |

No number in the draft was found that lacks a corresponding evidence item, and no evidence item's
value was rounded beyond what the source itself reports (no `rounding:` declaration was needed).

## Claim type vs. verb
`lint_draft.py`'s `B4-verb-vs-type` check found **one** mismatch pre-fix: the abstract used "show
that" for two `interpretation`-typed claims (C003, C019). **Fixed** by downgrading to "suggest
that" (evidence_model.md §3 permitted verb for `interpretation`). Re-run after the fix: 0 such
errors. `confirms`/`establishes` remain twice, both attached to `derived`-typed C018 (a direct
before/after re-measurement, not an inferential leap); `derived` claims are not restricted by this
check and the verb matches the evidence's directness, so no further downgrade was made.

## Negative-result coverage
All four `negative_result`-kind evidence items have a `reported_main` decision in
`claims/claim_evidence_map.json -> negative_result_decisions`, and all four appear in the draft:
E017 (DeepCT/SPARTA fail to generalize, C006, Section 5 para "at the other end"), E019 (dense
retrievers underperform under domain/task shift, folded into C008), E020 (DPR worst overall, C008,
same paragraph), E026 (TAS-B loses to ANCE on 2 datasets, C011, Section 5 para "two systems buck
their family's trend"). No negative result was excluded or held back. `SELECTIVE_REPORTING` not
raised.

## Claim map coverage
All 22 claims (C001-C022) and all 8 limitations (L001-L008) appear at least once in the draft
(checked by grep for each tag). No claim in `claim_evidence_map.json` is unused; no tag in the
draft is missing from the map (confirmed by `lint_draft.py`'s `tag-unresolved` check returning
none).
