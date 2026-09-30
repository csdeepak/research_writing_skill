# Step 15: Figure/table audit (draft v001)

TASK.md requires "No images," so this audit covers the draft's two Markdown tables only; there
are no FIG cards or raster/vector figures to check.

## Card completeness
Both `plan/figure_cards/TAB-1.md` and `TAB-2.md` have a non-empty `takeaway` and `rq` (checked
against `figure_table_rules.md` SS1's rule that an empty takeaway/rq means the visual has no job).
Both cards' `claims`/`evidence` fields resolve to real ids in `claims/claim_evidence_map.json` and
`evidence/research_evidence.json`.

## Reference-before-appearance and prose takeaway
- **Table 1**: referenced in prose ("Table 1 lays out the four benchmarks side by side...")
  immediately before the table, and its takeaway ("every reference model is under 330 KB... the
  memory constraint... is what unifies the suite") appears in the caption; the caption's own
  substance (parameter-budget commonality across dissimilar tasks) is echoed in Method P1's
  framing of the suite as memory-constrained across all four tasks, so the takeaway is not
  caption-only.
- **Table 2**: referenced in prose ("Table 2 summarizes what each submission targeted")
  immediately before the table, and its takeaway (one submission per major hardware class, each
  demonstrating a different stack layer) is restated in the prose paragraph immediately following
  the table (Results P3), not left for the caption alone to carry.
- `lint_draft.py`'s `A7-figure-not-discussed` / `A7-figure-late-reference` checks report 0
  findings for both tables.

## Honesty checks (`figure_table_rules.md` SS5, adapted for tables -- no axes/bars apply)
- **All conditions shown:** Table 1 shows all four v0.5 benchmarks (none omitted); Table 2 shows
  all five v0.5 submissions (none omitted). Both cards record `selection_rule: "all ... are shown;
  nothing was selected out."`
- **No cherry-picking:** neither table excludes an unfavorable benchmark or submission.
- **Honest columns:** Table 2 deliberately does NOT include an accuracy/latency/energy score
  column, because those per-submission numbers are not recoverable from `project/paper.txt`
  (`missing_evidence.json` MISS-4). Inventing plausible-looking numbers to fill that column would
  have been a clear violation of the hard rules; leaving the column out and saying so in the
  caption and in Limitations is the honest alternative. Table 2 also does not assert the source
  paper's own fine-grained Dataset/Training/Model modification marks, because those did not
  survive text extraction with confidence (MISS-3) -- see `accepted_risks` AR-007 in `state.json`.
- **No dual axes, no 3-D, no manipulated scale:** not applicable to Markdown tables; both cards
  record this explicitly (`honesty_checks`).

## Accessibility
Both tables use plain column headers with units in the header or cell (KB, %, AUC), consistent
decimal precision (one decimal place for the two non-integer figures, 86.5% and 0.85 AUC, matching
the precision the source itself reports -- no invented extra precision), and row order that puts
comparable items together (the four benchmarks in Table 1 follow Table 1's own order in
`project/paper.txt`; Table 2's closed-division rows precede its one open-division row, matching
the source's own Table 2 order). Both cards include `alt_text` describing the table's structure
and content in prose, for the venue types that support it.

## Numbering and cross-reference
Both tables are numbered (1, 2) and referenced by number in prose, never as "the table above/below"
(`A-figure-position` reports 0 findings for either table).

**Result: 0 blocking table defects.** `FIGURE_NOT_EXPLAINED` not raised for either table.
