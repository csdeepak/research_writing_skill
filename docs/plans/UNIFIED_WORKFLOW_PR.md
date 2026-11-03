Unify RCE with the capabilities of Academic Research Skills as one ordered workflow, RCE as the spine (0.5.0 candidate, unreleased).

## What changed?

The 0.5.0 candidate is one ordered workflow of 8 phases and 22 steps (`skill/workflow.md`, `skill/modes.md`). Five
capabilities move into RCE as phases with their own gates. It was built in five stages on this branch, each committed
and checked on its own (`docs/plans/UNIFIED_WORKFLOW_HANDOFF.md`, section 9).

- **Stage A, documents and contracts.**
  - `SKILL.md` and `workflow.md` are rewritten.
  - New documents: `modes.md`, `literature.md`, `integrity.md`, `review_panel.md`, `finalize.md`.
  - Five new failure states, and the proposal `skill/versions/proposals/20261102-unified-workflow.json`.
- **Stage B, tools** (standard library only; network only behind `--online`).
  - `rce_index.py` covers the DOI resolver, Crossref, OpenAlex, Semantic Scholar and arXiv.
  - `lit_search.py` handles corpus intake and search.
  - `verify_citations.py` does lookups, verdicts, retraction status and gate GL.
  - `integrity_check.py` covers M1–M7 evidence, the alignment sample and gate GI.
  - `format_paper.py` builds the bibliography and the LaTeX, DOCX and PDF outputs; `disclosure.py` drafts the AI-use
    statement.
  - GL and GI are wired into the validator, the gate runner, the CLI and the role ledger.
- **Stage C, schemas, prompts and adapters.**
  - New schemas: `paper_config`, `candidates`, `integrity_report`, `reviewer_cards`, `panel_review` and
    `editorial_decision`; `source_registry` is extended additively.
  - New prompts: the VERIFIER, the review panel (field analyst, five seats, synthesizer) and the COACH.
  - `rce_roles.py` gains `panel`, `rebut` and `verify`. `panel_check.py` is new, and G4 now covers the panel.
  - Claude Code subagents and the other adapters are updated.
- **Stage D, tests and an end-to-end run.**
  - Integrity benchmark: variants H–L plant a fabricated DOI, a wrong-paper DOI, a retracted source, a
    hallucinated result and a method with no basis.
  - Failure cases FC-0019 to FC-0033, with replay fixtures.
  - A paper-mode run on a copy of the demo project, with live lookups, subagent roles, Pandoc and LaTeX
    (`evaluation/unified_e2e/REPORT.md`).
- **Stage E.** `README.md` and `skill/README.md` describe the candidate, and `main` is merged in (no file changes).

The revision cap falls from 3 review rounds to 2 revision loops. `SKILL.md` keeps `version: 0.4.0` until the release
decision.

## Why? What evidence supports the change?

The proposal records a static review of the v0.4.0 skill against its goal. It found five capability gaps:
- no search or citation-lookup tooling;
- no index check behind GL-style citation rules;
- no independent check between drafting and review;
- a single reviewer, with no external-review path;
- no formatted output.

No reader or user failure is claimed.

The build then produced its own evidence:
- **Live index run (Stage B).** 8 planted sources were all judged correctly, and GL failed on exactly the 4 bad
  ones.
- **End-to-end run (Stage D).** It found eight tool defects, each now a failure case with a regression test
  (FC-0026 to FC-0033). The isolated VERIFIER caught a citation label naming the wrong author list, which every
  deterministic tool had passed. It also caught a gap contradicted by abstracts the search itself retrieved.

Design source: Academic Research Skills by Cheng-I Wu, CC BY-NC 4.0, commit `a41f3b2` (`docs/SOURCES.md` S32). It was
read for design only. Everything here is written fresh for this Apache-2.0 repository. Word 6-gram scans against all
ARS text files found no shared prose, only code idioms, schema keywords, URLs, titles and the credit line.

## Tests
- [x] new tests that fail before this change: T-072 to T-106 (216 tests in `tools/tests/test_v050_*.py`, network
  and models mocked), plus a regression test for each end-to-end defect
- [x] `python -m unittest discover -s tools/tests` passes (320 tests)
- [x] `python tools/replay_fixtures.py` passes (60/60; no existing failure case regressed)
- [x] `python tools/validate_cases.py` (33 cases) and `python tools/check_repo.py` pass. `validate_artifacts.py
  --check-skill` gives 0 errors, and `package_skill.py` builds a valid package of 144 files
- [x] CI passed on every stage commit (runs 19 to 22)

## Integrity impact
- **Could this alter evidence-integrity behaviour?** **Yes.**
  - New gates: GL for citations and GI for integrity.
  - G4 now needs a five-seat panel in `paper` and `restructure` modes.
  - G5 needs a clean final GI on unified projects.
  - An untraced number in a result sentence is an M3 error.
  - Citations resolve by author form and year suffix, and an ambiguous citation is an error.
  - Before and after behaviour, and the rationale, are in `skill/changelog.md` (0.5.0 candidate) and the proposal
    `skill/versions/proposals/20261102-unified-workflow.json`, whose gate status is `pending`.
- **Did an existing failure case or expected output change?** No. `EXPECTED.json` gains `integrity_variants`
  additively; the reviewer `variants`, and so the calibration set, are unchanged (T-106). Existing failure cases
  FC-0001 to FC-0018 and their fixtures all still pass. v0.4 projects, those without `mode` in `state.json`, are not
  asked for GL or GI.

## Documentation
- [x] docs updated: the skill documents, the changelog, `docs/SOURCES.md`, `docs/PRIVACY.md`, both READMEs and the
  handoff. No public claim is strengthened without new evidence: reader comprehension is still "not established",
  and the new evidence rows say what was run and how often.
- [x] no private research data, keys or local paths added. Keys travel in headers from environment variables only,
  and `check_repo.py` passes.

## Not verified
- **Not run live:**
  - a final-stage VERIFIER pass;
  - a second panel round;
  - the devil's-advocate rebuttal;
  - the COACH.

  Unit tests cover these paths, with models mocked.
- **Isolation.** Subagent isolation in the end-to-end run was by instruction only.
- **Sample size.** One end-to-end run, on one synthetic project. Index lookups are tested live by hand, not in CI.
- **Reader effect.** Any effect on reader comprehension or paper quality is not measured.
- **Release.** The release decision has not been made. Merging this PR does not change the version.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
