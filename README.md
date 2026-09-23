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
tools/                        stdlib-only Python: validator, linter, packet builder, scoring, versioning
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
v0.1.0: design complete, tools tested on synthetic fixtures. **Not yet validated on real
projects.** The acceptance experiment is specified in `docs/04_EVALUATION_FRAMEWORK.md` §11.
