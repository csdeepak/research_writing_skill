# Step 15 — Figure/table audit

No images are used, per the task's "No images" requirement; all three visuals are Markdown tables,
audited against `figure_table_rules.md` and their cards in `plan/figure_cards/`.

| Table | Card | Referenced before it appears | Takeaway stated in prose | Honesty checks |
|---|---|---|---|---|
| Table 1 (dataset stats) | TBL-1-dataset-stats.md | Yes -- "(Table 1)" in Section 3 para 2, before the table | Yes -- the scale/length ranges are stated in prose immediately after the table | All 18 rows shown (no cherry-picking); units labeled in the header; no axes/3D/dual-axis issues (it is a table) |
| Table 2 (zero-shot summary) | TBL-2-zeroshot-summary.md | Yes -- "Table 2 summarizes..." opens Section 5, before the table | Yes -- Section 5's following paragraphs state the direction and magnitude for every named system | All 10 systems shown; BM25 marked as the reference row; caption discloses no variance is available (L006), rather than implying precision the source doesn't have |
| Table 3 (Hole@10/bias) | TBL-3-hole10-bias.md | Yes -- "(Table 3)" added in Section 6 para 2, before the table (fixed during this audit -- see below) | Yes -- Section 6 para 3 states the Hole@10 contrast and the before/after deltas | All 9 systems shown; caption states the scope (TREC-COVID only, one re-annotation pass) |

**Finding and fix:** `lint_draft.py` flagged `A7-figure-not-discussed` for Table 3 (no in-text
"Table 3" mention). Fixed by adding an explicit "(Table 3)" reference at the point Hole@10 is
introduced, before the table appears. Re-run confirms the finding is cleared.

No figure/table lacks a takeaway or an RQ link (all three cards have non-empty `takeaway` and `rq`
fields), so `FIGURE_NOT_EXPLAINED` is not raised for any of them after the fix. No table uses a
non-zero-start bar axis, dual axis, 3D effect, or undisclosed cherry-picking (n/a for tables; the
honesty checks in each card record this explicitly). Every highlight/emphasis in the tables (e.g.
which systems beat BM25) is stated in the surrounding prose rather than only implied by bolding, so
no honesty issue with unexplained emphasis arises.
