# Research Writing Skill: Research Communication Engine (RCE)

A model-agnostic skill for CLI-based LLM agents (Claude Code, Codex, Gemini, any
OpenAI-compatible or local model) that turns a folder of raw research evidence into a
**scientifically rigorous, evidence-traceable, audience-aware** paper.

It targets one failure specifically: generated papers whose pieces are individually correct but
never add up to a mental model a reader can follow. The skill makes the model act less like
*"an LLM that knows how papers look"* and more like *"a researcher who understands what the
reader needs to understand before they can understand the research."*

## Repository map

```
docs/                         research and architecture phase
  01_FOUNDATION_ANALYSIS.md   course principles A–X → validity check → operational mechanisms
  02_RESEARCH_CORPUS_STRATEGY.md  source hierarchy L0–L4, discovery, filters, extraction schema
  03_AGENT_ARCHITECTURE.md    CORPUS / REVIEW / SKILL agents, isolation, contracts, protocol
  04_EVALUATION_FRAMEWORK.md  reconstruction test, 20 dimensions, blind + human protocols
  05_SKILL_SPECIFICATION.md   the final skill design, and why it should beat a single agent
  SOURCES.md                  every external source, verified 2026-09-24
skill/                        the executable skill (start at skill/SKILL.md)
tools/                        stdlib-only Python: gates (validator, lint, number tracing, visuals, G4, gate runner),
                              model-agnostic role runner (rce_llm.py, rce_roles.py), versioning
evaluation/                   external validation study, A/B tests, end-to-end run, calibrations (see its logs/)
```

## Use it with any model
Follow `skill/adapters/README.md`. In short:
- your agent reads `skill/SKILL.md` (or `skill/adapters/entrypoints/AGENTS.md`);
- the gates are deterministic Python;
- the blind reviewer, grader and readers run on whatever model you bind in `.rcs/models.json`: OpenAI-compatible
  APIs (OpenAI, OpenRouter, Ollama, vLLM, LM Studio), Anthropic, Gemini, any CLI, or copy-paste into any chat UI.

Calibrate a reviewer model once:

```bash
python tools/rce_roles.py calibrate --rcs .rcs
```


## Foundation
The theory comes from the course *Object Oriented Modelling & Design: Technical Writing*,
Units 1–4 (PES University). Its principles (reader-centered communication, audience tiers,
Plan → Draft → Revise → Edit, evidence evaluation, ethical data representation, visual
integration, IMRaD) are **kept**. Their implementation is modernized against current publisher
policy and research on scientific communication and LLM-generated science (see `docs/01`).

## Quick checks
```bash
python -m unittest discover -s tools/tests -v
python tools/validate_artifacts.py skill/examples/demo_project/.rcs
python tools/lint_draft.py skill/tests/perturbations/E_unsupported_interpretation.md --rcs skill/examples/demo_project/.rcs
python tools/validate_artifacts.py --check-skill
```

## Status
**v0.3.0** (released 2026-09-30) adds:
- a truth guardrail;
- evidence-bound figures;
- reader-comprehension tooling;
- an enforced multi-role workflow with human checkpoints;
- a model-agnostic runtime.

Evidence (`skill/changelog.md`, `evaluation/logs/DECISIONS.md` D-25 to D-32):
- **Checks:** 95 unit tests and 49 replay fixtures of real failure cases.
- **ASMOS end-to-end run:** separate role agents, human answers applied, and two blind review rounds.
- **Reviewer calibration:** passed on three model families (Claude Opus 0.933, NVIDIA Nemotron 0.945, Qwen3.8-27B
  0.911; the bar is 0.90).
- **Reader-level benefit is not shown:** the pre-registered A/B was better on 1 of 3 projects and worse on none.
  v0.3.0 is released as a process upgrade.

Open, and needing people: a blinded human reading study (`skill/templates/human_study_protocol.md`).
