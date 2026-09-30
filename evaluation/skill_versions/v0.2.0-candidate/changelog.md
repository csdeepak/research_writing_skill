# Changelog

Every change to the skill is recorded here. Behavior changes need a proposal in
`versions/proposals/` (schema `schemas/skill_change.schema.json`) with: failure observed ·
evidence · root cause · rule added/changed · expected improvement · possible regressions ·
tests added · gate result. **No silent changes.** `tools/validate_artifacts.py --check-skill`
warns about any file whose hash differs from the latest released manifest.

Versioning: MAJOR = workflow or contract change · MINOR = new mechanism, check, or rule ·
PATCH = clarification with no behavior change.

---

## [0.2.0] — 2026-09-24 (candidate, **REJECTED** 2026-09-28 — see below)

**Proposal:** `versions/proposals/20260924-attribution-and-adherence.json` (gate: **rejected**).
**Driven by:** the Phase 5 baseline failure analysis, clusters S1+S2 (author-stated limitations
and rationale replaced by the writer's own), S3 (skill as executed ≠ skill as designed), and S4
(length overruns). `SKILL.md` keeps `version: 0.1.0` until the release gate passes (release
procedure step 4).

**Changed:**
- *Attribution (S1+S2).* New evidence kind `rationale_stated`. Limitations now require `origin:
  author_stated | writer_derived`. Claims gain `origin` and `rationale: motivation |
  design_choice`. The Limitations contract now reports every author-stated limitation first,
  attributed. Writer-derived caveats go in an "Additional caveats" paragraph, and broad author
  limitations attach to the central claim instead of being dropped as "generic". Motivation and
  design rationale stay in the authors' framing, in the Introduction and Method. New failure
  states `AUTHOR_STATEMENT_DROPPED` and `ATTRIBUTION_ERROR`. `LIMITATION_MISSING` drafts are
  `writer_derived`.
- *Adherence (S3).* Gates G1, G3, and G5 are executable. A gate is `"passed"` only when a
  tool report under `.rcs/audits/gates/` (`--out`) shows 0 errors and matches the current
  inputs. Otherwise the validator raises `SELF_CERTIFIED_GATE`. It also flags a malformed
  `state.json`. The tools are no longer optional: when they can't run, the gate is
  `"unverified"`. `SKILL.md` now inlines the attribution rules, a section-contract summary, the
  claim-type and confidence enums, and the gate commands.
- *Length (S4).* `length_limit_words` in `state.json`, or the venue's `words_main`. The lint
  adds `S4-over-length`, which counts the main text without back matter, and G5 fails over the
  limit. The step-21 procedure relocates content and never deletes claims, negative results,
  author limitations, or rationale. `paper_architecture.md` gains a planned-words column.
- *Tools.* `validate_artifacts.py` adds attribution checks, `check_gates`, and `--out`.
  `lint_draft.py` adds the `S1-*`, `S2-*`, and `S4-*` rules, `--max-words`, and `--out`.
  `rce_common.py` adds `length_limit` and `main_text_words`, and resolves the skill directory
  for both the repo layout and a skill-version layout.
- *Demo.* The four demo limitations gain `origin` (additive; no claim changed).

**Tests added:** T-008 … T-018 (`tools/tests/test_v020_attribution_gates.py`; fixtures in
`tools/tests/fixtures/`). All existing tests (T-001 … T-007) are unchanged and pass.

**Known risks:** a longer Limitations section, a larger `SKILL.md` (~1,880 words), a possibly
unusual "Additional caveats" label, noisy `S1-caveat-attribution` warnings on older text, and
extra tool cost. See the proposal.

**Release gate result (Phase 9, 2026-09-28): REJECTED.** Pre-registered rule: accept only if Q11
recall improves AND MMF/DR do not regress on ≥2 of 3 projects (OPENHANDS, MLPERF_TINY, BEIR; F1
Claude Opus reader vs frozen Gold Set v1.0). MMF regressed on 2/3 projects (MLPERF_TINY −0.037,
OPENHANDS −0.162; only BEIR improved, +0.025); Q11 recall improved on OPENHANDS (+0.4) but
regressed on MLPERF_TINY (−0.1) and was already at ceiling on BEIR. The OpenHands regression turned out to be an
evaluator artifact (D-24: the grader counts source-true detail missing from the curated gold as an
unsupported belief). Under the source-verified sensitivity metric OpenHands improves (+0.025), but BEIR (−0.062) and
MLPerf Tiny (−0.049) still regress slightly, so the verdict holds: not shown better, not shown worse. **v0.1.0 remains
canonical.** Full numbers: `versions/proposals/20260924-attribution-and-adherence.json` → `gate`,
and `evaluation/results/comparison/scores/paired.json` / `per_review.json` in the main repo. This
candidate is kept (not deleted) as a documented, tested, evidence-grounded rejection — a
starting point for a future revision, not a dead end.

---

## [0.1.0] — 2026-09-24 — initial design release

**Status:** design complete, tools tested, **not yet empirically validated** (see
`docs/05_SKILL_SPECIFICATION.md` §9).

**Origin of the rules (not failure-driven yet):**
- The foundation principles come from the OOMD Technical Writing course (F0), operationalized as
  described in `docs/01_FOUNDATION_ANALYSIS.md`.
- The modernizations come from current guidance and research (S01–S31 in `docs/SOURCES.md`).

**Contents:**
- 21-step workflow in 5 gated phases (Plan-evidence, Plan-context, Draft, Revise, Edit)
- Central artifacts: evidence map, claim–evidence graph (8 claim types, permitted verbs), Paper
  Spine, Research Story Graph (17 node types, 15 edge types), experiment narrative chains,
  question and term ledgers
- Section contracts for 14 section types (incl. venue-injected required statements) and the
  Result Interpretation Chain
- Figure/table cards; citation pipeline; literature → gap → question chain
- Anti-pattern catalog (18 comprehension, 17 integrity, 7 LLM-drift patterns)
- Failure states (19) with classes STOP / ASK / MARK / FIX
- Agent prompts: CORPUS_AGENT, REVIEW_AGENT, SKILL_AGENT, RECON_GRADER
- 9 JSON Schemas; stdlib tools: validate_artifacts, lint_draft, build_review_packet,
  score_reconstruction, snapshot_version
- Perturbation benchmark seed set (1 base × 7 variants) with expected detections
- Adapters: Claude Code (+ subagent definitions), Codex, OpenAI-compatible, Gemini, local models

**Tests added:** T-001 … T-007 (`tests/README.md`).

**Known limitations of this version:**
- No real-project validation yet. The expected improvements are hypotheses (`docs/04` §11).
- The lint is heuristic (English-only regexes). Expect false positives on some domain phrasing.
- The perturbation set has only one base text, in one domain (a synthetic forecasting study).
- Reviewer calibration thresholds (≥90% / ≤10%) are initial choices, not empirically derived.

**Next planned work (not yet proposals):**
1. Run the §11 final quality test on ≥5 real projects with researcher-approved gold stories.
2. Add perturbation bases from ≥3 other domains (e.g. wet-lab biology, qualitative HCI, theory).
3. Run reviewer calibration across ≥2 model families.
4. Test the cheaper CORPUS_AGENT (`docs/03` §8).
