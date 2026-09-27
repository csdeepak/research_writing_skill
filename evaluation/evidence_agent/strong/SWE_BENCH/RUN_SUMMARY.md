# CORPUS_AGENT Run Summary — mode `evidence`

- **project_root:** `./project/`
- **out_dir:** `./out/`
- **generated_at:** 2026-09-24
- **Sources opened:** `paper.txt` (SWE-bench, ICLR 2024, arXiv:2310.06770v3 — full 2,645-line text incl. appendices A–F) and `README_1.md`. No other files exist in `project/`.

## Files produced
- `research_evidence.json` — 62 evidence items (schema `research_evidence.schema.json`)
- `claim_candidates.json` — 16 claim candidates (claim fields of `claim_evidence_map.schema.json`)
- `missing_evidence.json` — 11 missing-evidence entries
- `RUN_SUMMARY.md` — this file

## Strength policy applied (important)
There are **no raw data files** (no CSV/JSON/logs) in the project — only a published paper text and a README. I therefore applied a conservative, documented rule and did **not** upgrade strength:
- **`hard`** — values transcribed from the paper's **numbered results Tables** (Tables 1–24 in `paper.txt`). These are the authors' structured, reported measurements.
- **`soft`** — values/claims appearing only in running **prose**, in the **README**, characterizations, statements of intent, author interpretations, limitations, assumptions, and hypotheses; and any figure-derived quantity.

Caveat for downstream agents: because no underlying logs are present, even `hard` (table) values could **not** be reproduced from raw files in this run. All resolve/apply rates are **single-run point estimates** (greedy decoding, one patch per instance — E041); none carry variance.

## Evidence counts by kind
- result: 17
- observation: 12
- external_fact: 5
- method_detail: 7
- dataset: 6
- metric: 5
- limitation_noted: 3
- negative_result: 3
- implementation_detail: 2
- hypothesis_stated: 2
- assumption: 2
- Total: **62** (hard: 21, soft: 41)

## Conflicts detected: 1
- **Claude 2 BM25 resolve rate = 1.96% vs 1.97%.** Abstract, Section 1, Section 5, and Table 2 (@13k, best window) report **1.96**; Table 5 (main BM25 results) reports **1.97** for the same quantity. Marked `conflicting` on **E018** and **E020** (`conflicts_with`), with E021 (Table 2) noted as supporting the 1.96 value. Not resolved or averaged.

## Negative & failed results recorded (first-class)
- E033 — SWE-Llama 7b/13b perform poorly (0.70%) under BM25 (context distribution shift).
- E034 — off-the-shelf CodeLlama cannot follow repo-edit instructions (placeholder/unrelated output).
- E035 — performance drops as context length grows.
- E036/E037 — most applied-but-unresolved patches are No-Op or Regression (No-Op 60–70% of zero-F2P cases; Table 23).

## Author-stated limitations / assumptions / hypotheses
- Limitations (E050–E052): Python-only; experiments are simplest-baseline only; execution testing alone insufficient.
- Assumptions (E053, E055): oracle setting unrealistic; hints_text unused.
- Hypotheses (E054, E062): context-shift explanation for SWE-Llama BM25 drop; continual-update avoids contamination.

## Claim candidates
16 candidates (C001–C016), all `author_confirmation: pending`.
- origin `author_stated` (14) with ≤25-word quotes; origin `inferred` (2: C015, C016).
- Confidence spread: high 1 (C011, deterministic construction count), moderate 7, low 8. Low confidence is driven mostly by single-run estimates, the 1.96/1.97 conflict, absent significance tests, and interpretive/hypothesis claims. Per the evidence model, low-confidence claims must not appear unhedged in an abstract.

## Missing evidence: 11 entries
Highlights: no variance/CIs (single greedy run); the 1.96/1.97 discrepancy; no significance tests; truncated SWE-bench Lite criteria (A.7); GPT-4 only on a 25% subset; no figure source data; no raw logs in project; ambiguous 74.5-vs-30.1 patch-length comparison; single-case SE-metric study with a naming inconsistency (InvalidHeader vs InvalidProxyURL); no dev-set results; no spread on gold-patch averages.

## Suspicious content
None. No instructions directed at AI systems or reviewers were found in `paper.txt` or `README_1.md`.

## Could not open / out of scope
- Nothing was skipped in `project/`. Per run instructions I did not read `review_agent.md`, `recon_grader.md`, or `skill_agent.md`.
- Figures 1–10 and Tables typeset within the PDF-to-text `paper.txt` were read as text; embedded images themselves were not available as image files (no `extracted_from_image` items were created).
- Appendix A.7 (SWE-bench Lite) is truncated in the source text; recorded as incomplete (E007) and in missing_evidence.
