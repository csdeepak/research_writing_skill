# Phase 4 — Blind Reviewer Validation Report

**Benchmark:** 7-variant synthetic set (`skill/tests/perturbations/`, unchanged). **Gold:** demo gold story (correct by construction).
**Reviewer families:** F1 = Claude Opus (`claude-opus-4-8` via headless CLI, no tools; 2 seeds) · F2 = NVIDIA Nemotron-3-Ultra-550B (OpenRouter free; 1 seed). OpenAI/Codex was planned as F2 but became unavailable (D-10).
**Blinding:** random packet IDs, sealed mapping, variant-identifying comment stripped, one wording substitution in G (D-07). Reviewers saw only paper + audience + objective.
**Grader:** Claude Sonnet (CLI, then in-session subagent after the CLI credit blocker, D-14); grader sees gold nuggets + unlabeled reconstruction only.
Raw outputs: `raw/` · normalized: `normalized/` · gradings: `grading/` · scores: `scores/` · evaluator v0.1 archive: `evaluator_v0.1/`.

## 1. Evaluator defect found and repaired (v0.1 → v0.2)
Under evaluator v0.1 the reviewers did not answer the 12 defined reconstruction questions — they substituted their own question sequence, inconsistently across reviews, and grading of misaligned answers was noisy (e.g., the same variant F scored MMF 0.947 and 0.526 across seeds). Repair (harness-only, D-13): restate the 12 questions verbatim in the output template; grader searches the whole reconstruction per nugget. All results below are **v0.2**. (v0.1 numbers retained in the archive: F1 dimension sensitivity 0.868, false alarms 0.10.)

## 2. Can the reviewer distinguish good communication from known failures? (measured)

| Criterion | F1 Claude Opus (2 seeds) | F2 Nemotron (1 seed) | Provisional threshold |
|-----------|--------------------------|----------------------|-----------------------|
| Pairwise discrimination (variant mean dimension score < clean A, same seed) | **12/12** | **6/6** | — |
| Dimension-attribution sensitivity (expected dims ≥1 lower than A) | **0.956** | **0.933** | ≥ 0.90 (provisional) |
| False-alarm rate on clean A (dims ≤ 2) | **0.05** (only `evidence_traceability`, explained by A's own [CITATION NEEDED] markers) | **0.00** | ≤ 0.10 (provisional) |
| Mean dimension score, A vs degraded | A 3.95–4.20; degraded 1.6–3.15 | A 4.65; degraded 1.65–4.1 | — |
| Malformed JSON outputs | 0/14 | 2/9 attempts (1 recovered on retry) | — |

Both families pass the provisional thresholds under v0.2. **The thresholds remain provisional**: 7 items × ≤2 seeds is far too small to estimate them, and EXPECTED.json itself over-specifies some drops (D-11).

## 3. Reconstruction test on planted problems (measured, MMF = RR − DR − 0.5·IR)

| Variant | F1 seed 1 / seed 2 | F2 | Planted problem detected by reconstruction? |
|---------|--------------------|----|---------------------------------------------|
| A clean | 0.974 / 1.000 | 0.947 | (reference) |
| B poor ordering | 0.974 / 0.974 | 0.974 | **No** — reader recovers all facts |
| C jargon | 1.000 / 1.000 | 0.974 | **No** |
| D result dumping | 0.816 / 0.895 | 0.763 | Yes (recall loss) |
| E unsupported interpretation | 0.289 / 0.474 (DR 0.21 / 0.11) | 0.368 (DR 0.16) | **Yes — strong distortion** (reader adopts overclaims) |
| F buried contribution | 0.974 / 0.974 | 0.947 | **No** |
| G citation misuse | 0.711 / 0.895 (DR 0.05) | 0.553 (DR 0.21) | Yes (reader adopts the mis-cited "most common failure mode" claim) |

## 4. Interpretation
- The reviewer's **dimension diagnostics** reliably separate good from degraded communication for both families (observation from 18/18 pairwise comparisons).
- **Reconstruction fidelity** — the primary metric — is sensitive to *content-truth* defects (overclaiming, citation misuse, missing interpretation) but **insensitive to structural/readability defects** (ordering, jargon, buried contribution) when the reader is a strong LLM. This is an important limitation of LLM readers as proxies for humans: a human adjacent researcher would very likely be slowed or misled by C and F (interpretation; not measured — no human readers were available).
- Consequence for Phase 5: a null or negative reconstruction effect cannot be read as "readability did not improve"; it can be read as "the reader's factual model of the research did not become more accurate".

## 5. Reliability and variation
- Seed variation (F1, v0.2): |Δ MMF| between seeds ≤ 0.03 for A, B, C, F; 0.08 for D; 0.18 for E and G — distortion-heavy variants are the least stable.
- Family variation: F2 rates everything higher on dimensions (A 4.65 vs 4.08), flags fewer inference issues on clean text (0 vs 4), and recovers slightly less from D and G.
- Inter-grader agreement: a second-grader pass was run under v0.1 only (Nemotron, F1 seed-1); it is not comparable to v0.2 grading and is not used. **No v0.2 inter-grader agreement estimate exists** (quota) — stated as a limitation.

## 6. Verdict
The blind reviewer (evaluator v0.2) is **fit for use** as a detector of known communication failures at the dimension level, with the caveat that its reconstruction channel under-detects structural/readability failures. Evaluator v0.2 is frozen for Phase 5/6/9.
