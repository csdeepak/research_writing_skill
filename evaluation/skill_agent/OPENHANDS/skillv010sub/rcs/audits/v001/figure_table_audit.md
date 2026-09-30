# Step 15 -- Figure/table audit

Two visuals, both tables (TASK.md: no images). Cards: `plan/figure_cards/TAB-1.md`,
`plan/figure_cards/TAB-2.md`.

| Check | Table 1 (SWE-Bench Lite) | Table 2 (15-benchmark synthesis) |
|-------|---------------------------|-----------------------------------|
| Card complete before placement | Yes (`TAB-1.md`) | Yes (`TAB-2.md`) |
| Referenced by number *before* it appears | "Table 1 places these next to five reproducible open baselines..." precedes the table | "Table 2 lays out all fifteen benchmarks side by side..." precedes the table | 
| Takeaway stated in prose | Yes, same paragraph (falls within the baseline range) | Yes, following paragraph ("Counting benchmarks...") |
| Linked to the RQ | Grounds C001/C002, the first direct test of the RQ | Grounds C015, the structural synthesis answering the RQ |
| All conditions shown (no cherry-picking) | All agents/configs reported for SWE-Bench Lite in the source are shown (B8 check) | All 15 evaluated benchmarks shown, including the 4 where OpenHands trails |
| Uncertainty disclosed | Table note: no seed/variance reported in source (L001) | Table note: no seed/variance reported in source (L001) |
| Axes/scale honesty (F0 U2) | N/A -- text table, no chart axes | N/A -- text table |
| Missing-value marking | "--" explained in a table note | N/A (no missing cells) |
| Selection rule for comparison baseline | N/A -- all baselines for the benchmark are listed | Disclosed in the card and inferable from the caption: one representative baseline per row, matching the one discussed in the corresponding Results paragraph |
| Accessibility | Plain-text Markdown tables; no color-only encoding; row/column headers with units | same |

**Result: PASS.** No `FIGURE_NOT_EXPLAINED` findings (`lint_draft.py`'s `A7-figure-*` checks: 0
findings for both tables -- both are referenced before appearing and discussed afterward).
