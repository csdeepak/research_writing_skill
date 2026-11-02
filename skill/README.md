# Research Communication Engine: skill package

A model-agnostic skill that turns raw research evidence into a paper a reader can understand,
evaluate, remember, and build on, without changing the truth of the research.

**Start here:** [`SKILL.md`](SKILL.md) (the entry point any agent loads first).

| File | What it holds |
|------|---------------|
| `SKILL.md` | Router, hard rules, input/output contract, workflow at a glance, gates, conventions |
| `modes.md` | The 12 modes: which phases each runs, routing by materials, what no mode may skip |
| `principles.md` | 12 principles, each with its origin and the check that enforces it |
| `workflow.md` | 8 phases and 22 steps: role, input, action, output, done-when, failure states, gates |
| `literature.md` | Search, corpus intake, source verification, grading, gate GL, systematic reviews |
| `integrity.md` | The seven failure modes, claim↔reference alignment, blocking rules, gate GI |
| `review_panel.md` | Five-seat panel, editorial synthesis, revision caps, external reviews, gate G4 |
| `finalize.md` | Formats, citation styles, disclosure, packaging, gate G5 |
| `evidence_model.md` | Evidence items, claim types, permitted verbs, confidence, negative results |
| `research_story.md` | Spine, story graph, experiment chains, question and term ledgers |
| `audience_model.md` | Audience tiers, reader modes A–E, content invariance, first read, term budget |
| `information_design.md` | Paragraph model, density classes, cognitive load, old→new coherence |
| `section_rules.md` | Contracts for each section, including the Result Interpretation Chain |
| `figure_table_rules.md` | Figure/table cards, chart choice, captions, honesty, accessibility |
| `citation_rules.md` | Citation pipeline, dimension matrix, literature → gap → question |
| `anti_patterns.md` | Comprehension, integrity (anti-hype), and LLM-drift patterns |
| `evaluation_rubric.md` | Reconstruction questions, 20 dimensions with anchors, exit criteria |
| `failure_states.md` | Failure states, their classes and required actions; contribution elicitation |
| `agents/` | Prompts for CORPUS_AGENT, REVIEW_AGENT, VERIFIER, COACH, SKILL_AGENT, RECON_GRADER, and the review panel in `agents/panel/` (field analyst, five seats, synthesizer). Each is for its own role only |
| `schemas/` | JSON Schemas for every artifact that crosses a boundary |
| `templates/` | Architecture table, figure card, venue profiles, packet inputs, open issues, disclosure |
| `adapters/` | Model-agnostic setup (`adapters/README.md`): Claude Code, Codex, Gemini, OpenAI-compatible, local models, `entrypoints/AGENTS.md`; executable bindings in `templates/models.json` |
| `examples/` | Project layout; synthetic demo project with full artifacts; worked example |
| `tests/` | Perturbation benchmark (7 variants) + expected detections; regression registry |
| `changelog.md`, `versions/` | Versioned evolution |

Design rationale is in `../docs/01`–`05`. Verified sources are in `../docs/SOURCES.md`.

## Quick start (any runtime)
1. Put the project's evidence in a folder (see `examples/project_layout.md`).
2. Tell your agent: *"Use the Research Communication Engine skill (`skill/SKILL.md`) to write a
   paper from `<folder>` for `<audience>` at `<venue>`."*
3. Expect questions at C0 (the paper config), Gate G1 (spine and claims) and G2 (outline). Those are
   the cheapest points to correct a misunderstanding.
4. Read `open_issues.md` before the paper.
