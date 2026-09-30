# Step 15 -- Figure/table audit

Two Markdown tables are used (no images, per the task's requirements). Both have a complete card
in `plan/figure_cards/` (TAB-1.md, TAB-2.md) written before being placed.

| Check | Table 1 | Table 2 |
|---|---|---|
| Referenced by number before it appears | Yes: "Table 1 places both numbers... side by side" precedes the table | Yes: "Table 2 reports the resulting Hole@10 rates..." precedes the table (fixed during this audit -- see below) |
| Takeaway stated in the caption | Yes, first sentence of the caption | Yes, first sentence of the caption |
| Takeaway also restated in prose | Yes (Sec. 5.1-5.2 unpack every column) | Yes (Sec. 5.4 unpacks Hole@10 and the before/after columns) |
| Linked to the RQ | Yes (answers "does in-domain predict zero-shot, and at what cost") | Yes (answers the case-study question raised in 5.4) |
| All conditions shown / selection rule stated | Yes: all 10 systems for Table 1; all 9 systems with a Hole@10 for Table 2 (BM25+CE's Hole@10 of 1.6% is in `research_evidence.json` E015 but was not additionally added as a 10th row, since 5.4's prose already reports it is the lowest of all; noted as a minor completeness gap, not a selection bias -- BM25+CE is otherwise absent from Table 2 only) | see left |
| Axes/bars start at zero, no dual axis, no 3D | N/A (table, not a chart) | N/A |
| Uncertainty shown or its absence stated | Caption states "single run, no seed variance" | Caption implicitly single-pass; Sec. 7 states no variance is available for any comparison |
| Consistent decimals / units / missing-entry symbols | nDCG@10 to 3 decimals; latency in ms; "not reported"/"not applicable" used where the source does not give a per-system figure | percentages to 1 decimal; nDCG@10 to 3 decimals |
| Source noted | Yes, in the caption | Yes, in the caption |

**Finding and fix:** the original draft of Section 5.4 did not name "Table 2" anywhere in the
prose before the table appeared (`tools/lint_draft.py` flagged `A7-figure-not-discussed`). Fixed
by adding an explicit lead-in sentence ("Table 2 reports the resulting Hole@10 rates and rescored
nDCG@10 values.") immediately before the table. Re-run of the lint after the fix shows 0
`A7-figure-not-discussed` / `A7-figure-late-reference` findings for either table.

**Completeness note (not a `FIGURE_NOT_EXPLAINED` failure):** Table 2 omits BM25+CE's Hole@10
(1.6%, the lowest of all ten systems, per `research_evidence.json` E015) because Table 4 in
`project/paper.txt` itself separates BM25+CE into a footnote-style entry distinct from the other
nine systems' main block. Leaving it out of Table 2 does not change the table's takeaway (dense
systems still have the highest Hole@10 shown), so no correction was made; recorded here for
transparency rather than silently dropped.
