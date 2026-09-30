# Synthetic example: a study with planted integrity problems

Everything in this folder is invented: the method (AdaptNorm), the datasets, the numbers and the reference. It is safe
for CI and meant for reading. It shows what RCE's deterministic checks catch, and what they do not.

```text
project/            the "research repository": results CSVs, a stale README, author notes
.rcs/               artifacts the skill's roles produce: evidence map, claim map, source registry, checkpoint, figure registry
figures/            the shipped figure (edited by hand: its axis labels no longer match the bars)
drafts/flawed.md    a draft with the planted problems
drafts/clean.md     the control: the same facts, stated correctly
```

## Run it

From the repository root:

```bash
python tools/rce.py check examples/synthetic_project --draft examples/synthetic_project/drafts/flawed.md
python tools/rce.py check examples/synthetic_project --draft examples/synthetic_project/drafts/clean.md
```

The clean draft still fails at project level until the evidence conflict is resolved and the figure is re-rendered.
That is by design: a project does not pass while its README and results disagree. The test
`tools/tests/test_v040_release.py` (T-064) resolves both in a copy and checks that the clean control then passes.

## Expected results (verified by T-064)

| # | Planted problem | Where | Caught by | Result |
|---|---|---|---|---|
| 1 | Correct numbers (0.80 vs 1.00) | both drafts | `verify_numbers` | traced, no finding |
| 2 | Invented number: Traffic MAE "0.69" (the file says 0.72) | flawed | `verify_numbers --strict` | **ERROR** `UNTRACED_NUMBER` |
| 3 | README says four datasets, results cover three | evidence | `validate_artifacts` | **ERROR** `UNRECONCILED_CONFLICT` until resolved (`resolution.chosen`) |
| 4 | Missing sample size (Energy has no `n`) | results | none | **not detected**: known gap (docs/concepts/EVIDENCE_INTEGRITY.md) |
| 5 | "significantly outperforms" with no test | flawed | `lint_draft` | **ERROR** `UNLICENSED-significance_test`, `UNLICENSED-matched_evaluation` |
| 6 | Figure edited by hand: axis labels no longer match the bars | figure | `validate_visuals` | **ERROR** `V6_NOT_REPRODUCIBLE`, `V3_AXIS_ENCODING` |
| 7 | "state-of-the-art" without a comparison | flawed | `lint_draft` | **ERROR** `UNLICENSED-sota_comparison` |
| 8 | Fabricated citation "(Moreau et al., 2022)" | flawed | `lint_draft` | **ERROR** `C5-citation-unregistered` |
| 9 | Author's untested hunch ("sensor drift explains the gap") stated as fact | flawed | `lint_draft` + checkpoint Q-001 | **ERROR** `BLOCKED-claim-used` |
| 10 | Derived metric: "fell by 25%" (correct: 20% of StaticNorm's error) | flawed | `verify_numbers` | **flagged, not rejected**: `DERIVED_MATCH` (INFO). 25% is a valid ratio with the other base (0.20 / 0.80), so the tool asks for confirmation and cannot decide the direction: known gap |
| 11 | Instruction planted in the text ("Ignore previous instructions…") | flawed | `lint_draft`; `build_review_packet` strips it | **ERROR** `C6-injection` |

Items 4 and 10 are the honest part of this example. RCE flags or blocks much of what a careless or overconfident
writer does, but not everything, and the gaps are listed so contributors can close them.
