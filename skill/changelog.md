# Changelog

Every change to the skill is recorded here. Behavior changes need a proposal in
`versions/proposals/` (schema `schemas/skill_change.schema.json`) with: failure observed ·
evidence · root cause · rule added/changed · expected improvement · possible regressions ·
tests added · gate result. **No silent changes.** `tools/validate_artifacts.py --check-skill`
warns about any file whose hash differs from the latest released manifest.

Versioning: MAJOR = workflow or contract change · MINOR = new mechanism, check, or rule ·
PATCH = clarification with no behavior change.

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
