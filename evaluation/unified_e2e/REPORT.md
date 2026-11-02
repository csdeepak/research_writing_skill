# Unified workflow: end-to-end run on the demo project (Stage D)

**Date:** 2026-11-02. **Branch:** `rce-unified-workflow` (0.5.0 candidate). **Mode:** `paper`.

**Project:** a copy of `skill/examples/demo_project/` outside the repository, so the example stays
unchanged. It is a synthetic teaching project: its README says the numbers are invented, and it has
no code or run logs.

**Runtime:**
- Tools ran as plain commands.
- The isolated roles ran as Claude Code subagents, one fresh context each: VERIFIER, REVIEW_AGENT,
  the field analyst, five panel seats and the synthesizer.
- Isolation is soft. Each subagent was told which files it may read, and no runtime enforced it.
- Literature lookups were live, with `--online`, against OpenAlex, Crossref, the DOI resolver, Semantic
  Scholar and arXiv.
- Formatting used Pandoc 3.13 and MiKTeX pdfTeX 4.23.

**Outcome in one line:** the workflow ran from intake to a formatted PDF. It correctly refused to call
the paper final: GI stops it on three integrity modes that need a named person, and G5 fails on three
open markers.

## What ran, and what each gate said

| Phase | Steps run | Result |
|---|---|---|
| P0 Intake | `paper_config.json` (paper, audience B, IEEE, 2500 words, MANDATORY oversight) | C0 was not confirmed by a person: checkpoint Q-C0 stays open, as this run was unattended |
| P1 Story | `rq_check.md`, `alternatives.md` | the existing demo story was used |
| P2 Literature | search plan reviewed by hand; 10 facet queries on OpenAlex and Crossref from 2018; 66 candidates (62 distinct works); 5 kept and verified; GAP scoped to the search | **GL passed** |
| P3–P4 Draft | draft v001 from the clean demo draft, with 3 author-year citations | **G1 passed**, **G3 passed** (lint and numbers) |
| P5 Integrity (pre) | 3 VERIFIER rounds (the cap) on drafts v001, v002, v003, each in a fresh context | **GI failed** at the cap; checkpoints Q-002 and Q-004 are open for a named person |
| P6 Review | packet pkt-e979296a; REVIEW_AGENT; field analyst; 5 seats committed before reading, then reviewed; synthesizer | **panel_check passed** (decision Major, derived Major, 0 errors); 24 dispositions; **G4 passed** |
| P7 Finalize | line edit (v005), claim invariance, tags stripped to `paper/paper.md`, final integrity bundle, `format_paper.py --to latex,docx,pdf --online`, `disclosure.py` | invariance passed; **GI final failed** (no VERIFIER run, M6 and M7 unresolved from pre); md, bib, tex, docx and a 4-page PDF written; disclosure drafted; **G5 failed** |

### P5 by round

| Round | Draft | Finding | AUTHOR action |
|---|---|---|---|
| 1 | v001 | M1 INSUFFICIENT_EVIDENCE: only a lab note says a test-split bug was fixed | Q-002 for a named person |
| 1 | v001 | M2 SUSPECTED: "Passalis and Tefas" was written for a five-author paper, and "Berthelier and Nabil" for a six-author one | labels corrected; tool fixed (FC-0030) |
| 1 | v001 | A003 overstated: no quote said "for shifting series", and one source did not back the sentence | sentence and claim sources narrowed |
| 1 | v001 | M4 INSUFFICIENT_EVIDENCE | listed in `open_issues.md` |
| 1 | v001 | M5: a hedge was dropped | wording corrected |
| 1 | v001 | M7: the spine kept the gap from before the search | spine updated; `story_changes` recorded |
| 2 | v002 | M7 SUSPECTED: the conclusion said "stem mostly from" where the claim says "account for much of", with no shift bound | scoped |
| 2 | v002 | "66 works" counted a preprint and its published version twice | count corrected to 62; tool fixed (FC-0032) |
| 3 | v003 | M6 SUSPECTED: no record says the normalizations use the mean and standard deviation | Q-004 |
| 3 | v003 | M7 SUSPECTED: abstracts on record (including the cited DAIN and Dish-TS) evaluate normalization with the forecaster held fixed, which contradicts the paper's gap | Q-004 |

The last finding is the most important result of the run. The paper's gap does not hold against the
works the search retrieved. Prose cannot repair it: the story has to go back to P1 and P2. The
workflow stopped there instead of letting the wording carry it.

### P6

- **The panel.** 33 findings: 17 major, 16 minor, no fatal. They merged into 13 blocking and 11
  optional roadmap items that cover all 33. The decision was Major, with no downgrades.
- **REVIEW_AGENT.** 4 blocking findings (figure_table 2, evidence_traceability 3 twice,
  unsupported_inference 3) and 3 inference issues.
- **Revision (v004).** Table 1 replaces the caption-only figure. The account is bounded to s ≤ 0.6,
  and the capacity contrast is dropped. The ablation's confound is stated as new limitation L005. One
  claim per citation, and the search is described.
- **Dispositions.** 15 fixed, 8 author questions (Q-003 for setup facts, Q-004 for the gap and the
  normalization), and 1 deferred (a new baseline run, DO-4).
- **Commitment hashes.** Recorded before any seat saw the paper. They still matched when the AUTHOR
  stamped them into the reviews.

## Tool defects the run found, all fixed with regression tests

| Case | Defect | Found by |
|---|---|---|
| FC-0026 | The drafted search plan queried the indexes with RQ labels and the project's coined names | orchestrator |
| FC-0027 | A title with a typographic hyphen crashed the tools on a cp1252 console | orchestrator |
| FC-0028 | An arXiv preprint typed JournalArticle by Semantic Scholar lost its preprint flag | orchestrator |
| FC-0029 | A citation matching two works was checked against the wrong one | orchestrator |
| FC-0030 | A citation label naming the wrong author list passed every tool | VERIFIER |
| FC-0031 | `run_workflow.py` passed a draft path that did not exist, and GL passed without reading the draft | orchestrator |
| FC-0032 | A preprint and its published paper counted as two works in a scoped gap | VERIFIER |
| FC-0033 | Reviewers saw author-year citations with no reference list | domain seat |

Replay fixtures CIT-05 to CIT-08 cover FC-0029 and FC-0030.

## Not run, or not verified

- **The final VERIFIER pass (step 20).** It was not run, because GI cannot pass while Q-002 and
  Q-004 are open. The gate was run without it and failed closed (`GI_NO_VERIFIER`,
  `GI_PRE_UNRESOLVED`).
- **Round 2 of the panel (verification re-review), the devil's-advocate rebuttal and the COACH.**
  These were not run. A re-review means little before the gap is re-scoped. Unit tests T-101 and
  T-102 cover these paths, but no live run has.
- **Checkpoints.** No checkpoint was answered. C0, Q-002, Q-003 and Q-004 are open, because only a
  named person can answer them.
- **Role records.** They were written by the orchestrator after the subagents ran, since the
  subagents were told to run no commands. `plan/paper_config.json` and
  `evidence/research_evidence.json` have no record (an `UNATTRIBUTED_CHANGE` warning).
- **Isolation.** It was by instruction only. Nothing checked which files a subagent opened, beyond
  the reviewer log REVIEW_AGENT wrote.
- **The disclosure** says `VENUE_UNKNOWN`: the demo has no venue profile with an AI policy. Each role
  shows "tool not on record", because the subagents are not bound in `models.json`.
- **Known, not fixed:**
  - Citeproc rendered "Étienne Le Naour" as "É. L. Naour". OpenAlex gives display names without a
    family/given split, so the particle is lost.
  - `verify_numbers.py` does not trace a literature count to `corpus/`, so "62" stays an
    `UNTRACED_NUMBER` warning. The VERIFIER traced it by hand.
- **Not claimed:** anything about paper quality or reader comprehension. This run tests whether the
  workflow and its tools behave as specified on one synthetic project.
