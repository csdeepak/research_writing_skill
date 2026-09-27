# Final External Validation Report — Research Communication Skill v0.1.0

**Status:** Phases 0–6 and 8 complete; Phase 9 (v0.2.0 candidate A/B) — see §6; Phase 10 (personal projects) not yet run.
**Primary success criterion (from the brief):** readers reconstruct the actual research more accurately, with fewer unsupported beliefs and fewer important misunderstandings.
**Primary metric:** Mental-Model Fidelity **MMF = RR − DR − 0.5·IR** against a frozen, independently verified Gold Account (RR = nugget recall, DR = distortion rate — overstated/contradicted, IR = unsupported-belief intrusions).
All numbers are from `results/comparison/scores/per_review.json`, `reviewer_validation/scores/`, `evidence_agent/*` (evaluator v0.2, Gold Set v1.0). Decisions D-01…D-17 in `logs/DECISIONS.md`.

This report separates **[M] measured results**, **[O] observations**, **[I] interpretations**, **[A] assumptions**, **[L] limitations**, **[U] unresolved questions**.

---

## 1. Set-up in one paragraph
Six public projects (SWE-bench, BEIR, MLPerf Tiny, SAM, Whisper, OpenHands) were assessed and accepted; their official paper + README snapshots were pinned. For each, a Sonnet agent drafted a Gold Account (18 sections + 36–40 scoring nuggets) from the snapshot only, and an independent Opus agent verified it (every project needed corrections; 1–3 high-severity errors caught per project), after which the Gold Set was frozen. A plain agent and a skill-guided agent (same model: Claude Sonnet; same snapshot, task, audience, length, tools, no web) each wrote a paper per project. Papers were cleaned of provenance and reviewed blind by two reader families — Claude Opus (F1) and NVIDIA Nemotron-3-Ultra (F2) — who answered 12 reconstruction questions and scored 20 dimensions. A separate grader scored each reconstruction against the Gold nuggets without seeing the paper.

---

## 2. Q1 — Can the blind reviewer reliably detect known communication failures?

**[M]** On the 7-variant synthetic benchmark (evaluator v0.2):

| | F1 Claude Opus (2 seeds) | F2 Nemotron (1 seed) |
|---|---|---|
| Pairwise discrimination (degraded < clean, mean dimension score) | 12/12 | 6/6 |
| Dimension-attribution sensitivity (provisional threshold ≥ 0.90) | 0.956 | 0.933 |
| False-alarm rate on clean text (provisional ≤ 0.10) | 0.05 | 0.00 |
| Reconstruction MMF: clean / overclaiming (E) / citation misuse (G) | 0.97–1.00 / 0.29–0.47 / 0.71–0.90 | 0.95 / 0.37 / 0.55 |
| Reconstruction MMF: ordering (B) / jargon (C) / buried contribution (F) | 0.97–1.00 | 0.95–0.97 |

**[O]** The first evaluator version (v0.1) had a defect: reviewers answered their own question set instead of the defined 12 questions, and grading was inconsistent (same variant 0.95 vs 0.53 across seeds). It was repaired (harness only) and all reviews were re-run (D-13).
**[I]** Yes — at the level of *dimension diagnostics*, both families reliably separate good from degraded communication. The *reconstruction* channel detects content-truth failures (overclaiming, citation misuse, missing interpretation) but not structural/readability failures, because strong LLM readers recover facts from badly ordered or jargon-heavy text.
**[L]** 7 items, ≤2 seeds; thresholds remain provisional; no human readers; no v0.2 inter-grader agreement estimate.

---

## 3. Q2 — Does the skill improve faithful reconstruction compared with a plain agent?

**[M] Per project, MMF (RR / DR), plain → skill v0.1.0:**

| Project | F1 Opus plain | F1 Opus skill | Δ | F2 Nemotron plain | F2 Nemotron skill | Δ |
|---|---|---|---|---|---|---|
| BEIR | 0.662 (0.713/0.00) | 0.787 (0.812/0.00) | **+0.125** | 0.600 | 0.737 | **+0.137** |
| SWE-bench | 0.575 (0.700/0.025) | 0.663 (0.675/0.00) | **+0.088** | 0.387 | 0.588 | **+0.201** |
| SAM | 0.653 (0.819/0.056) | 0.611 (0.722/0.028) | −0.042 | 0.750 | 0.597 | −0.153 |
| OpenHands | 0.675 (0.725/0.00) | 0.325 (0.438/0.05) | **−0.350** | 0.450 | 0.462 | +0.012 |
| MLPerf Tiny | 0.688 (0.725/0.00) | 0.500 (0.575/0.025) | −0.188 | 0.713 | n/a (unusable) | — |
| Whisper | 0.600 (0.688/0.05) | 0.525 (0.625/0.05) | −0.075 | n/a (malformed ×2) | 0.550 | — |

**[M] Aggregates.** F1 (6 pairs): ΔMMF mean −0.074 (bootstrap 95% CI −0.204 … +0.052), skill better in 2/6; ΔRR −0.087 (CI −0.183 … +0.007), skill better in 1/6; ΔDR +0.004 (CI −0.018 … +0.025); reviewer dimension mean **+0.56 in favour of skill**. F2 (4 pairs): ΔMMF mean +0.049, skill better in 3/4.
**[M] Other outcomes.** Skill papers exceeded the 4,500-word limit in 2/6 (plain 0/6). Skill papers cost ≈ 8× more to produce (≈ $3.3–3.9 vs ≈ $0.35–0.5).
**[O]** Direction agrees across reader families for 3 of 4 comparable projects (BEIR +, SWE-bench +, SAM −); OpenHands disagrees strongly (F1 −0.35, F2 +0.01).
**[O]** The reviewer's 20-dimension ratings favour skill papers even where readers reconstructed less (F1: SAM +1.05 dims with −0.04 MMF; Whisper +1.5 with −0.075).
**[I]** **No.** Under this protocol, skill v0.1.0 did not improve faithful reconstruction on average; the effect is project-dependent (positive on BEIR and SWE-bench under both readers, negative on SAM under both) and the pooled estimate is near zero to negative with a CI spanning zero. It did not increase distortion. It *did* make papers rate better on the reviewer's quality dimensions — so "looks better" and "is understood better" came apart, exactly the failure the study was designed to catch.
**[A]** An LLM reader's reconstruction approximates a careful expert reader's; the verified Gold Account is the right target for a paper presenting third-party research.
**[L]** n = 6 projects (underpowered by design, docs/04 §11); one seed per paper in Phase 5; F2 had 2 unusable outputs; the external projects already come with a polished narrative (ceiling effect — the plain agent can largely re-tell the authors' story); in-loop reviewer (Opus) is the same family as reader F1 (D-08); skill runs used one review round (not up to three).

---

## 4. Q3 — Which components appear responsible for improvements/failures?

**[M] Nugget-level attribution (F1, 6 projects, plain→skill):** net losses concentrate in **Q11 author-stated limitations (−7)**, **Q2 motivation (−3)**, **Q5 design rationale (−3)**; interpretation-strength nuggets lost 6 vs gained 2; measured/derived nuggets lost 11 vs gained 8. **(F2, 4 projects):** net **gain on Q7 strongest results (+4)**; measured/derived lost 2 vs gained 9.
**[M] Process audit (Phase 5 CLI runs):** artifact coverage 0.38–0.69; question/term ledgers and lit→gap chain never built; validator/linter never run; `section_rules.md`, `citation_rules.md`, `audience_model.md`, `information_design.md` never opened; all runs self-certified gates G1–G5 as passed. (Subagent-path runs in Phases 6/9 did run the tools — execution path affects adherence.)
**[O] Mechanism (verified in text):** the Limitations contract ("no generic limitations unattached to claims") plus LIMITATION_MISSING ("draft the limitation from the claim graph") led writers to replace the authors' own stated limitations with writer-derived caveats presented in the paper's voice (e.g., OpenHands). Author rationale, typed as interpretation/context, was compressed in favour of the evidence-bound spine.
**[I] Components:**
- *Likely helpful:* the Result Interpretation Chain / evidence-bound results (F2 Q7 gain; the two projects with gains are results-heavy benchmarks).
- *Likely harmful:* the limitations/attribution rules (S1), the spine's displacement of author framing (S2).
- *Largely inert as executed:* most secondary rule files, ledgers and tool gates (never reached the writer in CLI runs) — the skill's effect came mainly from `SKILL.md`, `workflow.md` and one external review.
- *Evaluator component:* reviewer quality ratings are **not a valid proxy** for reader understanding here.
**[L]** Attribution is observational (no component ablation was run).

---

## 5. Q4 — Can the evidence/corpus stage use a cheaper model without materially degrading downstream communication?

**[M] Package quality (3 projects; cheap = Claude Haiku 4.5, strong = Claude Opus):**

| | SWE-bench cheap / strong | Whisper cheap / strong | OpenHands cheap / strong |
|---|---|---|---|
| Gold-nugget coverage | 0.625 / **0.750** | 0.675 / **0.713** | 0.487 / **0.600** |
| Numbers traceable to source | 0.78 / **1.00** | 0.97 / **1.00** | 0.98 / **1.00** |
| Negative results captured | 0 / 3 | 2 / 3 | 1 / 2 |
| Author limitations captured | 2 / 3 | 3 / 5 | 3 / 5 |
| Claims typed stronger than gold | 4 / 3 | 4 / 1 | 1 / 0 |
| Cost (USD) | 0.31 / 2.79 | 0.29 / 2.08 | 0.28 / 2.62 |

Ungrounded "cheap" numbers were unit re-formatting (1.96% → 0.0196; 438K → 438000), not fabrication — but they violate the copy-verbatim rule.
**[M] Downstream (same skill writer, step-17 drafts, F1 reader, MMF / DR):** SWE-bench cheap 0.413 / 0.10 vs strong 0.500 / 0.025; Whisper cheap 0.625 / 0.025 vs strong 0.525 / 0.00; OpenHands cheap 0.225 / 0.05 vs strong 0.075 / 0.075 (IR 0.275). Downstream favours strong in 1/3 projects and cheap in 2/3. All package-based papers except Whisper-cheap score below papers written from the full snapshot.
**[I]** At the package level the strong model is better on every measure (coverage, grounding, negative results, limitations, claim typing) at ≈ 9× the cost. Downstream reader fidelity does **not** track package quality (strong better on SWE-bench with 4× lower distortion; cheap better on Whisper and OpenHands) — with n = 3 and one run each, writer/reader variance dominates the package difference. The cheap model is adequate for inventory and extraction breadth but should not be trusted for claim typing and negative-result capture without a strong-model check. The information loss from *any* package interface (vs the writer reading the source) is larger than the cheap/strong difference.
**[L]** 3 projects, one run each; downstream drafts skip the review round (D-16); single reader family downstream.

---

## 6. Phase 9 — engineering loop

**Candidate v0.2.0** (SKILL_AGENT, from aggregated evidence only): `origin: author_stated | writer_derived` on limitations/claims; new `rationale_stated` evidence kind; validator checks `AUTHOR_STATEMENT_DROPPED` / `ATTRIBUTION_ERROR`; lint errors for missing author limitations/rationale; Limitations contract = authors' limitations first, writer caveats in a labelled paragraph; executable gates (tool reports + hashes, `SELF_CERTIFIED_GATE`); length gate; load-bearing rules inlined in SKILL.md. 44/44 tests (23 new; 21 of them fail on v0.1.0).
**A/B test (v0.1.0 vs v0.2.0, same subagent path, step-17 drafts, OpenHands / MLPerf Tiny / BEIR):** **[pending — to be filled when runs complete]**.

---

## 7. Failure analysis summary (details: `FAILURE_ANALYSIS.md`)
| Cluster | Origin | Evidence |
|---|---|---|
| S1 author limitations replaced by writer caveats | B/C | Q11 net −7 (F1); verified in OpenHands text |
| S2 author rationale/motivation lost | B | Q2 −3, Q5 −3 (F1) |
| S3 low process adherence; self-certified gates | C/D (packaging) | process audit, 6/6 CLI runs |
| S4 length overruns | C/D | 2/6 skill papers |
| E1–E2 evaluator question drift, grading noise | E/F | repaired (v0.2) |
| E6 reviewer ratings diverge from reconstruction | E/F | +0.56 dims vs −0.087 RR |
| E7 LLM readers insensitive to structural defects | F | Phase 4 B/C/F ≈ 1.0 |

---

## 8. Confounders and threats to validity
- **Ceiling / task framing [L]:** writers re-present already-published, well-written papers; the skill was designed for raw project evidence (notes, logs), where the plain agent has no ready narrative. This study therefore tests the skill in its *least favourable* setting.
- **Reader-model dependence [O]:** project-level effects can flip between reader families (OpenHands).
- **Execution path [O]:** CLI vs subagent writers differed in skill adherence; Phase 5 used CLI, Phases 6/9 subagents.
- **Same-family in-loop reviewer [L]:** may bias F1 toward skill papers — yet F1 was the *less* favourable reader, so this bias did not produce a spurious positive.
- **Infrastructure [O]:** OpenAI access lost mid-study; Claude CLI credit exhausted; repeated session limits; OpenRouter free-tier caps. No fabricated or partial outputs were used (partials explicitly excluded, D-15).

## 9. Unresolved questions [U]
1. Does the skill help when the input is raw project evidence rather than a finished paper? (Phase 10 / a raw-evidence benchmark.)
2. Do the dimension-level gains (reviewer ratings) correspond to real reading-ease gains for **human** readers, even though LLM reconstruction does not show them?
3. Does v0.2.0 recover the author-attribution losses without new regressions? (Phase 9, pending.)
4. How stable are project-level effects across seeds (only one seed per paper here)?

## 10. Bottom line
Skill v0.1.0 **does not yet meet its own success criterion**: across six real projects, readers did not reconstruct the research more faithfully than from a plain agent's paper (pooled effect ≈ 0 to slightly negative, project-dependent, CI spanning zero), although it did not increase distortions and it did produce papers that reviewers *rate* higher. The failure analysis points to specific, fixable mechanisms (author attribution of limitations/rationale; rules that never reach the writer; self-certified gates), which v0.2.0 targets and which are being tested.
