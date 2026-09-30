# Open issues: BEIR (adjacent-audience version), draft v001

Steps 1-17 of the Research Communication Engine workflow are complete for this draft. Step 18
(blind audience review) and steps 19-21 (revise/repeat/final line-edit + tag-stripping) are out of
scope for this run per the task's run-specific constraints, so `{C###}`/`{L###}` claim tags remain
in both `.rcs/drafts/v001/paper.md` and `./paper.md` by design, not by omission.

## Must resolve before this could be treated as a submission-ready manuscript
- Claim tags are still present in both copies of the draft (by instruction for this run; would be
  stripped at step 21, `tools/lint_draft.py --final`, in a full run).
- No `[MISSING RESULT]`, `[CITATION NEEDED]`, or `[ASK AUTHOR]` markers remain anywhere in the
  draft — confirmed by `lint_draft.py`'s marker scan returning none. Nothing is blocked on missing
  evidence.

## Accepted risks (chosen without a human reviewer; see `.rcs/state.json -> accepted_risks` for the full record)
- **RISK-001/002**: every ASK/STOP point in the workflow (claim confirmation at Gate G1, venue
  choice, audience-mode default, literature-search scope, review isolation) was resolved by
  choosing the most defensible option directly from the evidence, rather than pausing, since no
  human is available this run.
- **RISK-003**: CORPUS_AGENT's evidence- and literature-extraction role was performed by AUTHOR in
  the same context (no subagents available). This is not the blind-review isolation the skill
  reserves for REVIEW_AGENT, so `ISOLATION_BREACH` does not apply, but it does mean the evidence
  extraction was not independently cross-checked by a separate role.
- **RISK-004**: literature coverage is limited to works cited in `project/paper.txt` itself
  (no web access); `corpus/source_registry.json` entries are verified only against that one
  document (`verification.method: user_supplied_file`, `read_depth: abstract`).
- **RISK-005**: two of the source paper's tables (the per-dataset breakdown for 3 of 10 systems in
  its Table 2, and its Table 3 on latency/index size) were damaged by PDF-to-text extraction badly
  enough that individual cells could not be confidently reconstructed; this paper reports only the
  values that could be cross-validated (see `evidence/missing_evidence.json`).

## Assumed venue rules (no official venue was given; see `plan/venue_profile.yaml`)
- Section structure, heading wording, and reference style beyond the task's explicit citation-form
  instruction are AUTHOR's judgment calls, not requirements of a named venue.
- Citation form: `(FirstAuthor et al., Year)` applied uniformly, except where the source's own
  in-text usage names only two authors ("X and Y"), which was kept as "(X and Y, Year)" to match
  "as they appear there" (task requirement) — e.g. (Dai and Callan, 2020), (Nogueira and Lin, 2019).
  Two same-first-author pairs (Hofstätter 2021 SIGIR paper vs. a second 2021 Hofstätter paper on
  cross-architecture distillation; Voorhees 2005 vs. Voorhees et al. 2021) were resolved by citing
  only one Hofstätter work in the final draft (no collision) and by year, respectively.
- `publication_status` for several registered sources (MultiReQA, KILT, ANCE, Climate-FEVER, the
  second Hofstätter paper, the Lin et al. survey) is `PREPRINT` because `project/paper.txt`'s own
  reference-list entry gives no venue string at all; this is a best-effort inference (see
  `corpus/corpus_log.md`), not a confirmed publication record, and `peer_review_known: false` is
  set accordingly in `corpus/source_registry.json`.

## Claims awaiting independent (human) confirmation
None outstanding: every claim in `claims/claim_evidence_map.json` is marked `author_confirmation:
"confirmed"` because each restates, closely paraphrases, or transparently derives from a statement
explicitly present in `project/paper.txt` (see `.rcs/state.json -> accepted_risks -> RISK-002` for
the reasoning). A human author revisiting this project should still read every `{C###}` tag against
its source location before treating "confirmed" as final, since this run's confirmation was
self-review, not independent review.

## Word count
`./paper.md` main text (everything before "## References"): 4,448 words (task requirement:
3,000-4,500). Total file including references: 5,343 words.
