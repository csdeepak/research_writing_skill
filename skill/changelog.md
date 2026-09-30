# Changelog

Every change to the skill is recorded here. Behavior changes need a proposal in
`versions/proposals/` (schema `schemas/skill_change.schema.json`) with: failure observed ·
evidence · root cause · rule added/changed · expected improvement · possible regressions ·
tests added · gate result. **No silent changes.** `tools/validate_artifacts.py --check-skill`
warns about any file whose hash differs from the latest released manifest.

Versioning: MAJOR = workflow or contract change · MINOR = new mechanism, check, or rule ·
PATCH = clarification with no behavior change.

---

## [0.4.0] — 2026-09-30 (open-source release)

**Why minor:** new checks and mechanisms (the policy above: MINOR = new mechanism, check or rule). No artifact becomes
invalid; one new ERROR applies only to projects that keep a source registry.

**Changed (behaviour):**
- `lint_draft.py` **C5-citation-unregistered**: every author-year citation must resolve to the source registry (ERROR;
  WARN when there is no registry). T-065.
- `lint_draft.py` **language policy**: `.rcs/language_policy.json` extends or disables existing license types; the
  applied policy is written into the report. T-070.
- `g4_check.py` **finding lifecycle**: `author_question` (needs an existing checkpoint), `false_positive` and
  `not_reproducible` (need a reason) join `fixed` / `declined` / `deferred`. T-063.
- `SKILL.md`: the description is shortened to 181 characters (the claude.ai upload limit is 200); new bullets on
  citations and the language policy.

**Added:**
- `tools/rce.py` (single CLI entry point; `check` runs every deterministic check on a project and draft). T-069.
- `tools/package_skill.py` (skill ZIP + validation). T-067.
- `tools/check_repo.py` (repository audit). T-068.
- `tools/validate_cases.py` + `schemas/failure_case.schema.json` + `cases/failures/` (18 real failure cases). T-066.
- `examples/synthetic_project/` (planted integrity problems + clean control). T-064.
- T-071 tests every strong-language license rule and `UNSUPPORTED_FACT`.

**Fixed:**
- `snapshot_sources.py` `restore` / `verify`: third-party texts are no longer redistributed.
- Test fixtures derived from a private project were replaced with synthetic equivalents.
- Line endings normalised to LF (`.gitattributes`).

**Not claimed:** any change in reader comprehension (see `docs/research/EVALUATION.md`).

## [0.3.0] — released 2026-09-30 (promoted by the user's decision as a PROCESS upgrade)

**Release decision (D-32):** the user promoted v0.3.0 into `skill/` on 2026-09-30.
- **Shown:**
  - checks and workflow: 95 tests, 49 replay fixtures, and the ASMOS end-to-end run including human answers and two
    review rounds;
  - a calibrated reviewer on three model families;
  - no reader harm.
- **Not shown:** better reader comprehension. The tier-3 A/B (D-30) was better on 1 of 3 projects, worse on none.
- **Not claimed:** "writes better papers".

### Stage 1: truth guardrail (vNext Stage 1; offline gate passed)

**Proposal:** `versions/proposals/20260929-truth-guardrail.json` (gate: pending, offline gate passed).
**Driven by:** `docs/06_VNEXT_SPEC.md` §4 and its ten adversarial cases (§10), plus real defects from
this study's Phase 9 drafts (D-23 to D-25). Built on the v0.2.0 candidate's code (its attribution and
executable-gate tooling is kept; v0.2.0 was rejected on reader outcomes, not on tool correctness).

**Added (all backward compatible; strict behavior only for projects that opt in):**
- *Evidence conflicts:* `quantity`/`run_id`, automatic detection (`UNRECONCILED_CONFLICT`), documented
  `resolution`, `BLOCKED_BY_CONFLICT`, `CITES_REJECTED_EVIDENCE`.
- *Evidence-conditional language:* claim `licenses` with evidence predicates; lint `UNLICENSED-*`
  (ERROR once the claim map uses `licenses`, WARN for legacy maps); claim `basis`/`status`;
  `BLOCKED-claim-used`.
- *Numbers:* `tools/verify_numbers.py`. Every number traced; derivations only from evidence cited on
  the same line; p-values never inferred.
- *Sources:* `as_cited`, `TITLE_REPAIRED_FROM_MEMORY`.
- *Visuals, fail-closed cards:* `NO_VALID_VISUAL`, `UNTRACED_COMPONENT`, `BLOCKED_PERMISSION`,
  `UNLABELLED_ILLUSTRATION`.
- *Editing:* `tools/claim_invariance.py`. Effective gate status (NOT_RUN for self-certified). With
  `"guardrail": "v0.3"`, G3 and G5 also require number and invariance reports.
- *Consistency:* lint `INCONSISTENT-COUNT`.
- *Self-improvement (tiers 0–1):* `tools/rce_diagnostics.py` (opt-in, local, content-free) and
  `tools/replay_fixtures.py` with a 25-fixture library.
- *Self-improvement (tier 2, added during Stage 4):* `tools/micro_recon.py` runs paragraph-level
  reconstruction screens with deterministic required/forbidden grading (T-046). Pilot on 2 real
  fixtures, 1 Haiku reader each: MLPERF-bound recall 0.0 -> 1.0 ("under 350 KB" -> "325 KB");
  ASMOS-interval 0.8 -> 0.4 when intervals are removed. n=1 per cell, so this is a smoke test only.

**Tests added:** T-019…T-028 (16 tests) and 25 replay fixtures. 60/60 pass. v0.2.0's tools catch 1/16
of the failure fixtures; this candidate catches 16/16. The 9 negative controls pass.

**Not claimed:** any effect on reader reconstruction (no live A/B was run for Stage 1).

### Stage 2: visual intelligence (proposal `20260929-visual-intelligence.json`, gate: pending, offline passed)
- *Plan* (`tools/plan_visuals.py`, M04/M06/M10): whether a visual helps, and which form.
- *Produce* (`tools/visuals.py`, M05/M07): registry + deterministic stdlib SVG from declarative transforms of real files.
- *Check* (`tools/validate_visuals.py`, V1–V6 + M09 caption contract): V gates are wired into
  `validate_artifacts.py`; V5 passes only with a recorded human review.
- *Samples* (`tools/select_samples.py`, M08): a declared rule; never unconsented or identifying samples.
- **Acceptance (spec §12):** PASS on 2 real projects, ASMOS (the user's own results) and MLPerf Tiny.
  4 figures published, 1 correctly refused. Reproduce with `evaluation/stage2_acceptance/run_acceptance.py`.
  67/67 tests, 41/41 fixtures.

### Stage 3: reader comprehension (proposal `20260929-reader-comprehension.json`, gate: pending; human evidence pending)
- *Readers* (M02): `reader_model.json` (schema + template) and `tools/audit_reader.py`: unknown terms, overload,
  prerequisite order, misconceptions, reader questions.
- *Density and wording* (M11): excess precision against the value's own interval; synonym drift against the term ledger.
- *Compression* (M12): `tools/skim_layer.py` builds a verbatim skim sheet and checks that abstracts and slides keep
  numbers, scope, hedges, intervals and denominators.
- *Measured comprehension* (M13): `tools/comprehension_kit.py`. A frozen key, blinded visual-only vs full packets,
  blind grading, Krippendorff's alpha, CIs over readers. LLM proxy mode is available; the human protocol is in
  `templates/human_study_protocol.md`.
- *V5:* `tools/record_review.py`, a human-only record that goes stale when the figure is re-rendered.
- 74/74 tests. Proxy run on ASMOS: `evaluation/stage3_proxy/`. Its first run exposed and fixed 3 pipeline defects.
- **Acceptance not met:** the spec requires blinded human results, and none have been collected.

### Stage 4: full workflow (proposal `20260929-full-workflow.json`, gate: pending)
- *Roles* (M15): `tools/workflow_guard.py`, with per-role write permissions, an append-only `provenance.jsonl` and
  `ROLE_VIOLATION` / `UNATTRIBUTED_CHANGE`.
- *Human checkpoints:* ask/answer/status (answers only by a named person), `CHECKPOINT_BYPASSED`, and accepted risks
  typed workflow|factual (`ACCEPTED_RISK_FACTUAL` is an error).
- *G4 executable:* `tools/g4_check.py` (dispositions for every blocking finding; the review must cover the exact draft).
- *Gate runner:* `tools/run_workflow.py gates` with `RUN_LOG.jsonl`; it records only validator-confirmed statuses.
- `agents/review_agent.md` restates the 12 reconstruction questions verbatim.
- *Tier 2 self-improvement:* `tools/micro_recon.py` (see Stage 1 self-improvement).
- **Defects found by the end-to-end run on ASMOS and fixed** (`evaluation/stage4_e2e/MIDRUN_TOOL_CHANGES.jsonl`):
  - `workflow_guard.record` crashed on the final manuscript `paper/paper.md`, which lies outside `.rcs`. AUTHOR may
    now write `../paper/`. Any other outside path is a `ROLE_VIOLATION`, not a crash (T-047).
  - Review packets did not include the figures the paper links. The author copied them in after the manifest was
    written, so they were unhashed. `build_review_packet.py` now copies, sanitizes and hashes linked figures (T-048).
  - S1/S2 required a BLOCKED author rationale or limitation to appear in the draft, while `BLOCKED-claim-used`
    forbade it. The author had to invent a placeholder claim. It is now `S1/S2-author-statement-withheld`
    (WARN, T-049).
  - The blind reviewer found that line charts drew the value ticks and value label on the **horizontal** axis, which
    encodes x, so "route@1 by step" read as route@1 against route@1. No V gate caught it. The renderer now draws a
    vertical value axis with x ticks and an `x_label`. The new renderer-independent `V3_AXIS_ENCODING` fits the tick
    positions and requires every mark to lie where its value says. The real faulty ASMOS figure is the regression
    fixture (T-050).
  - The gate runner ran G1 before the G3/V reports were refreshed, so the first run after any edit failed G1. G1 now
    runs after them (T-045).
- Found by the tier-3 A/B (D-30): the length gate counted prose only (3,751 words for a 4,403-word paper). v0.3
  projects now count headings and table text; `length_count` in state.json overrides this (T-051).
- 84/84 tests, 49/49 replay fixtures. End-to-end result: `evaluation/stage4_e2e/E2E_REPORT.md`.

### Stage 5: model-agnostic runtime (proposal `20260930-model-agnostic.json`, gate: pending)
- *Any model for the single-shot roles:* `tools/rce_llm.py` supports several providers.
  - OpenAI-compatible endpoints: OpenAI, OpenRouter, Ollama, vLLM, LM Studio, llama.cpp, Groq, Together.
  - The Anthropic and Gemini APIs.
  - `command` (any CLI), `manual` (any chat UI) and `mock` (tests).
- *Role runner:* `tools/rce_roles.py`. `review` runs step 18 and sends only the packet; `calibrate` runs the reviewer
  benchmark for any model and resumes where it stopped; `run-tasks` executes task folders.
- *Bindings and setup:* bindings live in `.rcs/models.json` (`templates/models.json`, defaulting to a local server).
  Setup is in `adapters/README.md`, `adapters/entrypoints/AGENTS.md` (Codex, Cursor, Amp and Gemini CLI as `GEMINI.md`)
  and the updated adapter notes. `SKILL.md` names no model.
- *Guarantees independent of the model:*
  - hosted endpoints are refused unless their host is listed in `data_policy.allowed_hosts`;
  - keys come only from environment variables, never from files, URLs, command lines or logs;
  - the call log is content-free.
- *Weak-model robustness:*
  - JSON is extracted from fenced or chatty replies, and missing closing brackets are completed. A non-Claude reviewer
    truncated its last `}` on every reply.
  - Validation errors are sent back for a retry.
  - Rate limits and overloads are retried with backoff. A free-tier 429 had crashed the first live run.
- *Found by applying the user's checkpoint answers on ASMOS* (the first real answer -> claim path):
  - G4 did not notice a claim added after the blind review. It is now STALE with a request for another review round
    (T-059); old G4 reports without the claim list count as stale on v0.3 projects.
  - The lint called rejected author statements "withheld". Rejected now means decided (T-060).
- Tests T-052..T-060. Real non-Claude calibration runs: `evaluation/model_agnostic/`.

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
