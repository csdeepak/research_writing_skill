# Step 15 -- Figure/table audit (draft v001)

TASK.md forbids images, so the only visuals are the two Markdown tables planned in
`plan/figure_cards/TAB-1.md` and `TAB-2.md`. Both audited against `figure_table_rules.md`.

## Table 1 (Methods)
- **Card complete?** Yes (`plan/figure_cards/TAB-1.md`): purpose, RQ (N05), takeaway, claims
  (C001), evidence (E001), honesty/accessibility checks all filled.
- **Referenced by number before it appears?** Yes: "Table 1 lists the four benchmarks the v0.5
  suite specifies" precedes the table itself in Methods.
- **Takeaway stated in prose, not just the caption?** Yes: the paragraph before the table
  restates each benchmark's dataset/model pairing in prose; the paragraph after states the
  cross-cutting pattern (the quality-target margin) that the table alone doesn't spell out.
- **Caption first sentence = a takeaway, not a bare description?** Revised to lead with what the
  table shows and why ("each pairing one dataset with one microcontroller-sized reference model
  and one numeric quality target") rather than "Table showing benchmark specifications."
- **Honesty checks:** all 4 rows shown (no selection), consistent units (KB) across rows, no
  dual-axis/3D (not applicable to a text table), source cited.

## Table 2 (Results)
- **Card complete?** Yes (`TAB-2.md`): purpose, RQ (N05), takeaway, claims (C005, C006),
  evidence (E009, E010).
- **Referenced by number before it appears?** Yes: "Table 2 summarizes what the round produced."
- **Takeaway stated in prose?** Yes, both immediately after the table (per-submission
  elaboration paragraph) and again in the interpretation paragraph (R5) that ties the table's
  pattern to the research question.
- **Non-conclusions disclosed?** Yes, via the table note (the accuracy/latency/energy scores each
  submission achieved are not shown, because they are not recoverable from the extracted source
  text -- see `missing_evidence.json` MISS-001) and via the reconstruction caveat for row 5.
- **Honesty on the reconstructed cell:** the table note explicitly flags that row 5's
  dataset/training/model marks were reconstructed, names the two sources used for the
  reconstruction (the closed-division rule; the "no dataset was modified" sentence), and does not
  present the reconstruction as a direct read of an intact cell. This is the figure_table_rules.md
  section 5 "state the selection/derivation rule" requirement applied to a reconstructed cell
  rather than a selected subset.
- **All conditions shown, or selection rule stated?** All 5 v0.5 submissions are shown (complete
  enumeration, matches E010).

**No `FIGURE_NOT_EXPLAINED` instance found.** `lint_draft.py`'s A7 checks (figure-not-discussed /
figure-late-reference) fired 0 times for TAB-1/TAB-2 in `lint_v001.json`.
