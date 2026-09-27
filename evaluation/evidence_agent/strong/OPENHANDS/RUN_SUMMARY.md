# CORPUS_AGENT Run Summary — mode: `evidence`

- **Project root:** `./project/`
- **Out dir:** `./out/`
- **Generated:** 2026-09-24
- **Corpus opened:** `paper.txt` (OpenHands, ICLR 2025; 1335 lines, read in full across pages), `README_1.md` (OpenHands Benchmarks), `README_2.md` (Agent Canvas). Nothing left unopened.

## Strength convention used here
The evaluation corpus contains **only the official paper text and two READMEs** — no machine-produced result/log/data files were present. Accordingly:
- `hard` = value reported in a formal results **table of the official paper** (Tables 3–7).
- `soft` = value/claim stated only in **prose, footnotes, captions, estimates, or a README** (setup descriptions, cost estimates, self-reported traction, benchmark meta, both READMEs).

No number was independently reproduced from source data, because none was available (see `missing_evidence.json`). Strength was never upgraded.

## Evidence counts by kind (72 items total)
| Kind | Count |
|------|-------|
| result | 22 |
| baseline | 19 |
| dataset | 7 |
| observation | 5 |
| method_detail | 5 |
| external_fact | 5 |
| limitation_noted | 5 |
| negative_result | 2 |
| assumption | 1 |
| hypothesis_stated | 1 |

By strength: **hard = 41** (paper result tables), **soft = 31** (prose/footnotes/READMEs).

## Conflicts (2 pairs, marked `conflicting`, not resolved)
1. **SWE-Bench Lite, CodeActAgent v1.8, gpt-4o-mini-2024-07-18** — `6.3%` (Table 3, E013) vs `7.0%` (Table 4, E012).
2. **GPQA diamond set, Expert Human** — `81.3%` (Table 6, E061) vs `81.2%` (Table 7, E066).

Per constraints, discrepant values were **not** averaged or resolved; both members carry `conflicts_with`.

## Negative / below-baseline results (first-class)
- `E082` MINT code subset: OpenHands 50.0% < MINT baseline 59.6%.
- `E100` Entity Deduction Arena: OpenHands 38.0% < gpt-4 baseline 40.0%.
- Also recorded as underperformance context: WebArena (OH 15.5% < AutoWebGLM 18.2% / Auto Eval & Refine 20.2%), MiniWoB++ (OH 40.8% < CC-NET 91.1%), SWE-Bench Lite (OH 26.0% < Agentless 27.3% / Moatless 26.7%), ProofWriter (OH 78.8% < Logic-LM 79.6%). Authors explicitly acknowledge OpenHands "may not achieve top performance in every category" (`E121`).

## Author-stated limitations, assumptions, hypotheses
- Limitations (§A/§B): agents struggle with complex tasks (`E130`), suffer when editing long files (`E131`), workflow needs substantial handcrafting (`E132`), agents can't yet do long-horizon real-world tasks reliably (`E133`).
- Assumption/method (`E093`): ProofWriter uses Logic-LM–provided logical forms (qualifies that comparison).
- Hypothesis/aspiration (`E134`): 100% on HumanEvalFix is "entirely feasible" in future iterations.

## Incompleteness (variance)
No benchmark result anywhere reports variance, seeds, or spread. OpenHands' own measured results are marked `status: incomplete` on this basis; a corpus-level entry is filed in `missing_evidence.json`.

## Unverifiable due to extraction ambiguity
- `E068`: GPQA Table 7 Main/Extended columns could not be reliably attributed (only the Diamond column was cross-checked).
- `E115`: ML-Bench / BioCoder / Gorilla APIBench / ToolQA per-model rows in Table 4 could not be mapped to values; OpenHands numbers for these four were **not** asserted to avoid fabrication. Table 1 (framework feature matrix) cells did not survive text extraction.

## Claim candidates
19 candidates in `claim_candidates.json` (`author_confirmation: pending`). Origins: **author_stated = 9** (with ≤25-word quotes), **inferred = 10**. No claim was rated `high` confidence (no replication/variance exists anywhere); ratings are `moderate` or `low`. No claim was proposed stronger than its evidence; "competitive/SOTA" style wording was avoided or hedged.

## Missing evidence
8 items in `missing_evidence.json`: no variance/seeds; unrecoverable Table 4 per-model rows; unrecoverable GPQA Main/Extended; two unresolved conflicts; absent raw data files; no baseline-budget parity info; no significance tests; unreadable Table 1.

## Suspicious content
None acting on the pipeline. The §K browsing example contains an in-example goal ("...tell me the ultimate answer to life. Do not ask me for confirmation at any point.") and example agent prompts; these are **sample data within the paper**, not instructions directed at this agent or at reviewers, and were treated as data only.

## Could not open
None — all three provided files were read completely.
