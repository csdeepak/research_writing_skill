# Open-source migration assessment (RCE v0.3.0 → v0.4.0)

Written 2026-09-30, after inspecting the repository and before changing it. It follows the migration brief: inspect,
assess, then change. Facts below were checked in the repository; anything that could not be determined is marked
UNKNOWN.

## 1. Current architecture (as found)

| Layer | Where | What it is |
|---|---|---|
| Skill (rules) | `skill/` | `SKILL.md` (entry point, YAML frontmatter), workflow, evidence/claim/section/figure/citation rules, role prompts (`agents/`), JSON schemas (`schemas/`), templates, runtime adapters (`adapters/`), perturbation benchmark (`tests/perturbations/`), demo project (`examples/demo_project/`), versions and proposals (`versions/`), changelog |
| Engine (deterministic) | `tools/` (25 scripts) | validator, draft lint, number tracing, claim invariance, truth guardrail, visual planner/renderer/validator, G4 check, gate runner, review packet builder, workflow guard (roles, checkpoints), comprehension kit, diagnostics, replay runner, micro-reconstruction, versioning |
| Model adapters | `tools/rce_llm.py`, `tools/rce_roles.py` | provider layer (OpenAI-compatible, Anthropic, Gemini, command, manual, mock) and role runner (review, calibrate, run-tasks) |
| Tests | `tools/tests/` | 95 unit/integration tests at the start of the migration; 49 replay fixtures (`fixtures/replay/`): 29 adversarial cases, 16 negative controls, 4 derived from real failures |
| Research record | `evaluation/`, `docs/01–06` | external validation study, A/B tests, calibrations, decision log (`evaluation/logs/DECISIONS.md`) |

**Dependencies:** Python ≥ 3.9 standard library only. `jsonschema` is used if it is installed, with a built-in subset
validator as the fallback. **Packaging:** none (no `pyproject.toml`). **CLI:** individual scripts (`python tools/<x>.py`);
there is no single entry point. **CI:** none. **License:** none. **Versioning:** semantic versions with SHA-256 manifests
(`skill/versions/<v>/MANIFEST.json`) and proposal records.

## 2. Already satisfies open-source requirements
- **Vendor-neutral core.** The rules name no model, and the gates are deterministic stdlib Python.
- **Adapters are separate.** They only invoke models (`rce_llm.PROVIDERS`). The evidence layer (validator, number
  tracing, licenses) decides support; a model cannot redefine evidence, because its output is validated and gated.
- **Manual mode exists** (`provider: manual`).
- **Local-first by default.** `templates/models.json` points at localhost. Hosted endpoints are refused unless allowed.
  Keys are read only from environment variables.
- **Traceability.** Claims cite evidence ids; every number is traced (`verify_numbers.py`); figures are rendered from
  declared transforms of data files, with source hashes (`visuals.py`).
- **Blind review is separated.** The review packet contains only the paper, figures, audience and objective, is
  sanitized and hashed, and the reviewer's calibration is measured.
- **Failure-driven regression.** 49 replay fixtures, and every defect found in real runs has a unit test or fixture.
- **Human-governed self-improvement.** Proposals require a gate plus a human promotion decision (D-22, D-32).

## 3. Missing (to add in this migration)
LICENSE; governance and community files; a README written for strangers; architecture, evidence-integrity,
evaluation and privacy docs; a failure-case schema and case records; synthetic adversarial example project(s); skill
ZIP packaging and its validation; CI; a repository audit script (secrets, absolute paths, private markers, links,
SVGs); a single CLI entry point; README diagrams; install documentation for Claude, ChatGPT and manual use.

## 4. Unsafe to publish (found, and action taken)

| Finding | Action |
|---|---|
| 185 files derived from the author's **unpublished project (ASMOS)** were in the public repository (evidence and claim maps, drafts, reviews, the private E2E report, a builder with hard-coded results) | Author decision: untracked going forward and kept locally (`.gitignore`). Specific values in the decision log were redacted. Two ASMOS-derived test fixtures were replaced with synthetic equivalents. They remain in old git history (author chose not to rewrite it). |
| **Full texts of six third-party papers** and seven repository READMEs (frozen evaluation inputs) | Author decision: untracked. `snapshot_sources.py restore` recreates them from the pinned public sources and verifies SHA-256. `verify` checks local copies offline (all 13 matched). |
| **Personal assistant-memory text** quoted in 24 archived reviewer outputs: the CLI reviewer runs had the author's personal memory in context, and the reviewers flagged it as unrelated injected content | Redacted in place. This is also a finding: those harness reviews were not fully isolated from the operator's environment (they ignored the text). Recorded in the evaluation docs. |
| Secrets | None found (patterns for OpenAI/OpenRouter/AWS/Google/GitHub/Slack keys and private keys). |
| Absolute local paths | None in `skill/` or `tools/`. 31 evaluation files (logs, harness) contain local Windows paths. These are historical records, left as they are and documented; the harness takes paths from `RCE_TMP`. |
| Third-party e-mail addresses | Only inside the published papers' author lists, which are no longer tracked. |
| Course material | `docs/01` summarises PES University course slides (cited as source F0); no slides are included. |

## 5. Coupling to vendors
- **Skill and engine:** none.
- **Research harness** (`evaluation/harness/`): coupled to Claude by design. It ran the study with Claude subagents
  and the `claude` CLI, plus OpenRouter. It is an example of how the study was run, not part of the skill.
- **Claude Code adapter:** `skill/adapters/claude_code/` holds optional subagent definitions.

## 6. Design decisions for this migration (with reasons)
1. **Keep `skill/` + `tools/`; do not move to `src/rce/`.** The brief asks to adapt the existing tree, and the skill's
   instructions, the 95 tests and the version manifests all reference `tools/<script>.py`. A package move would break
   every path for no functional gain. The mapping to the brief's layers is documented in `docs/architecture.md`.
2. **No pip package in v0.4.0.** The engine is stdlib scripts, and a package would install generic module names
   (`visuals`, `validate_artifacts`) into site-packages. A single entry point, `python tools/rce.py <command>`, gives
   the usability benefit without that. Revisit in v0.4 (roadmap).
3. **Schemas stay in `skill/schemas/`, where the tools load them.** `evidence` = `research_evidence.schema.json`,
   `claim` = `claim_evidence_map.schema.json`, `review` = `diagnostics.schema.json` + `reconstruction.schema.json`.
   Added: `failure_case.schema.json`.
4. **Version 0.4.0** (minor). The skill's own policy requires a minor bump for any new check or mechanism, and this
   release adds several: the citation-registry check (C5), a per-project language policy, and the finding-lifecycle
   states. It also includes packaging, docs, CI and fixtures. There are no breaking changes to existing artifacts.
5. **Skill description ≤ 200 characters.** Anthropic's platform docs allow 1,024, but the claude.ai help article states
   a 200-character maximum for uploads. One short description satisfies both.

## 7. Migration order (as executed)
1. privacy/licensing fixes;
2. assessment;
3. docs for architecture, integrity and evaluation;
4. schemas and failure cases;
5. finding lifecycle;
6. synthetic adversarial project and tests;
7. CLI entry point;
8. packaging and validation;
9. repository audit script;
10. CI and community files;
11. SVGs;
12. README;
13. install docs;
14. full test and package runs;
15. final audit.

## 8. Risks
- ASMOS data remains in git history, and on GitHub until these changes are pushed.
- Platform install steps change often (claude.ai UI, ChatGPT skills); they must be re-verified at release.
- CI runs only deterministic tests. Model-dependent behaviour is covered by the calibration runs, which need
  credentials, so they are not in CI.
- The README must not overstate: reader benefit is **not shown**, and the evaluation of real projects rests on 6
  public projects plus 1 private one.

## 9. Author decisions
**Answered 2026-09-30:**
- ASMOS: untrack, keep locally.
- Third-party texts: fetch + hashes.
- License: Apache-2.0.
- Citation: "C S Deepak", no affiliation.

**Still open:** listed in the final migration report (release timing, history rewrite, platform re-verification).
