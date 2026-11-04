<div align="center">

# Research Communication Engine

**Turn research evidence into a paper where every claim traces back to its source**

An agent skill with standard-library checks: it maps your evidence before any prose, writes from that map, and asks you when the evidence runs out.

</div>

## Install

```bash
curl -L -o rce.zip https://github.com/csdeepak/research_writing_skill/releases/download/skill-v0.4.0/research-communication-engine-v0.4.0.zip && unzip rce.zip -d ~/.claude/skills
```

That installs the skill for Claude Code. For claude.ai, upload the same ZIP under **Customize > Skills** with code execution turned on. Codex, Gemini CLI, Cursor and any model behind an API are covered in [INSTALL.md](docs/guides/INSTALL.md). The checks need Python 3.9 or later and nothing else.

The release is 0.4.0. The unified workflow described below (literature search, an independent integrity check, a review panel, formatted output) is the unreleased 0.5.0 candidate on `main`: build its ZIP from a clone with `python tools/package_skill.py`.

## Quickstart

Point your agent at the demo project that ships with the skill:

> Use the Research Communication Engine skill to write a paper from ~/.claude/skills/research-communication-engine/examples/demo_project for machine-learning researchers outside forecasting.

To watch the checks catch planted problems without an agent, run them on the invented study in this repository:

```bash
git clone https://github.com/csdeepak/research_writing_skill.git && cd research_writing_skill
python tools/rce.py check examples/synthetic_project --draft examples/synthetic_project/drafts/flawed.md
```

```text
== artifacts (G1): FAIL (1 error(s), 1 warning(s))
   [ERROR] evidence/E003+E004: same quantity reported as 3 (project/results/metrics.csv) and 4 (project/README.md) but not recorded as a conflict (UNRECONCILED_CONFLICT)
== draft lint: FAIL (6 error(s), 4 warning(s), 0 info)
   ERROR L5    UNLICENSED-significance_test 'significantly' asserted for C001 without a significance_test license backed by evidence
   ERROR L12   C5-citation-unregistered     no registered source has this first author and year
   ERROR L13   C6-injection                 instruction-like text aimed at models/reviewers (INJECTION_DETECTED)
== number tracing: FAIL (1 error(s), 0 warning(s))
   ERROR L6    UNTRACED_NUMBER  0.69       no evidence value or project-file value matches this number
RESULT: FAIL (see ERROR lines; each names the rule to satisfy)
```

The output is abridged. The clean control passes, and two planted problems are not caught (a missing sample size, and the direction of a percentage's denominator). The example says so.

## What it checks

A gate passes only on a fresh tool report, never because an agent says it passed.

- **Numbers:** every number in a draft traces to an evidence item or a project file, and p-values are never inferred.
- **Strong wording:** "significant", "state of the art", "causes" and "outperforms" each need an evidence license, configurable per research field.
- **Citations:** each resolves to a verified source registry. With `--online`, every source is looked up in the DOI resolver, Crossref, OpenAlex, Semantic Scholar and arXiv and checked for retraction, so a fabricated or wrong-paper DOI fails the gate.
- **Conflicts:** two files that disagree are recorded and put to you, never resolved silently.
- **The authors' voice:** limitations and rationale the authors stated stay in the paper, attributed to them.
- **Figures:** re-rendered from the data, with marks that must match the axes.
- **Integrity before review (0.5.0 candidate):** an isolated VERIFIER checks seven AI-specific research failures, from an unfixed implementation bug to a story locked in before the results. Tool findings override its "clear".
- **Review:** a blind reader, plus a five-seat panel (0.5.0 candidate) that commits to its criteria before it reads the paper. Every finding ends fixed, declined with a reason, deferred, put to the authors, or marked a false positive; none disappears.

## How it works

<p align="center"><img src="docs/assets/evidence-to-paper.svg" alt="Sources feed an evidence map, claim map, story and paper, with a traceability path from each paper claim back to its source file" width="760"></p>

Each sentence of a draft carries claim tags such as `{C007}`. Each claim cites evidence ids such as `E012`, and each evidence item points to a file and a line, row or value. The 0.5.0 candidate runs this in eight phases, each closed by a gate:

| Phase | What happens | Gate |
|---|---|---|
| P0 Intake | Route by the materials, record the paper config, set the oversight level | C0: you confirm the config |
| P1 Evidence | Inspect the repository, build the evidence map, the spine and the claim graph | G1 |
| P2 Literature | Stress-test the question, search, verify every source | GL |
| P3 Plan | Reader model, venue profile, architecture | G2: you approve the outline |
| P4 Draft | Write the sections, results first and the abstract last | G3 |
| P5 Integrity | Seven failure modes and claim-to-reference alignment | GI |
| P6 Review | Blind reader and panel, revise, re-review, at most two loops | G4 |
| P7 Finalize | Line edit, a fresh integrity pass, references, formats, disclosure | G5 |

## Current evidence

| Area | Status |
|---|---|
| Deterministic checks | 322 tests passing, in CI on Linux and Windows with Python 3.9 and 3.12 |
| Known failures | 38 documented cases, each tied to a regression test; 60 replay fixtures (31 adversarial, 17 negative controls, 12 from real failures) |
| Reviewer calibration | Claude Opus 0.933, NVIDIA Nemotron 0.945, Qwen3.8-27B 0.911 sensitivity against a bar of 0.90; 7-paper benchmark, 1 seed |
| Live citation lookup (0.5.0 candidate) | 8 planted sources judged correctly in one manual run, including a fake DOI, a wrong-paper DOI and a retracted paper. Not in CI |
| Unified workflow (0.5.0 candidate) | One end-to-end run on the synthetic demo project: every phase ran, a formatted PDF was built, and the integrity gate stopped the paper on questions only a person can answer ([report](evaluation/unified_e2e/REPORT.md)) |
| Reader comprehension | **Not established.** v0.1.0 against a plain agent: better on 2 of 6 projects. v0.3.0 against v0.1.0: better on 1 of 3, worse on none. Single runs |
| Human reader study | Not run; the protocol and kit are ready |

Every row has a source in [EVALUATION.md](docs/research/EVALUATION.md).

## Notes

- **Not promised:** that a model never hallucinates, that RCE replaces domain experts, statistical review or peer review, or that it decides whether a hypothesis is true. Whether papers become easier to understand is still open.
- **Known gaps:** the checks cannot tell whether a model understood a source, and they miss missing sample sizes, the direction of a percentage change's denominator, and units in prose. Index lookups are only as good as the indexes. The VERIFIER and the panel are models, and their isolation is only as strong as the runtime makes it. The evaluation is small (6 public projects, 1 private, single runs, model readers) and covers ML, IR, speech, vision and agents papers only.
- **Any model:** the reviewer, VERIFIER, panel and readers run on any model bound in `.rcs/models.json`: OpenAI-compatible APIs, Anthropic, Gemini, a local server, any CLI, or copy-paste. Hosted endpoints must be allowed explicitly, and keys come only from environment variables ([PRIVACY.md](docs/PRIVACY.md)).
- **Governed changes:** real failures become permanent regression cases, and rule changes are proposals a maintainer decides ([SELF_IMPROVEMENT.md](docs/concepts/SELF_IMPROVEMENT.md), [GOVERNANCE.md](GOVERNANCE.md)).
- **Prior art:** the unified workflow's design draws on Academic Research Skills by Cheng-I Wu (CC BY-NC 4.0). It was read for design only, and no text, prompts, tables or code were copied ([SOURCES.md](docs/SOURCES.md), S32). The theoretical foundation is in `docs/01_FOUNDATION_ANALYSIS.md`.
- **More:** [architecture](docs/architecture.md), [evidence integrity](docs/concepts/EVIDENCE_INTEGRITY.md), [security](SECURITY.md), [roadmap](ROADMAP.md). A failure report is the most useful contribution ([CONTRIBUTING.md](CONTRIBUTING.md)). To cite RCE, use [CITATION.cff](CITATION.cff).

## License

Apache-2.0. Third-party texts used in the evaluation are not redistributed; see [NOTICE](NOTICE).
