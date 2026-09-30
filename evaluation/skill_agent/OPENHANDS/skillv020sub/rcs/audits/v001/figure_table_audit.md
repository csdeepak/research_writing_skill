# Step 15 -- Figure/table audit

No images are used anywhere in the draft (TASK.md hard rule: "No images"); all three visuals are
Markdown tables, each with a completed card in `plan/figure_cards/` (TAB-1, TAB-2, TAB-3).

| Check | Table 1 (software) | Table 2 (web) | Table 3 (misc.) |
|---|---|---|---|
| Card complete before drafting (`figure_cards/TAB-*.md`) | Yes | Yes | Yes |
| Referenced by number *before* it appears in text | Yes ("(Table 1)" in the SWE-Bench Lite paragraph, 2 paragraphs before the table) | Yes ("(Table 2)" in the WebArena paragraph) | Yes ("(Table 3)" in the six-benchmark paragraph) |
| Takeaway stated in the prose, not only the caption | Yes -- the paragraph text states the same comparison the caption leads with | Yes | Yes |
| Caption's first sentence is a declarative finding, not a bare description | Yes (revised at step-14 cleanup to lead with the finding) | Yes | Yes |
| Connected to its RQ | Yes -- all three ground RQ2 (software/web/misc. halves respectively) | Yes | Yes |
| Bold/highlight rule stated and honest | "OpenHands' own rows are in bold" stated in every caption; checked that bolding is applied consistently to every OpenHands row and no non-OpenHands row, in all three tables | same | same |
| All conditions shown, or a selection rule stated | Table 1: all 5 SWE-Bench Lite rows + all HumanEvalFix rows reported in the source except Aider/Moatless (selection rule stated in the card: no citable year). Table 2: all WebArena/MiniWoB++ comparator rows reported except OpenHands' own weaker-backbone duplicate rows (selection rule: one representative OpenHands configuration per benchmark, stated in `claim_evidence_audit.md`). Table 3: all 6 benchmarks' primary comparator rows shown. | -- | -- |
| Axes/scale honesty (bar-from-zero, consistent scale, no dual axis, no 3-D) | N/A -- these are data tables, not charts; no axis to distort | N/A | N/A |
| Numbers match evidence exactly | Verified in step 12's numeric spot-check | Verified | Verified |
| No table left with an empty takeaway or RQ (the A7/`FIGURE_NOT_EXPLAINED` check) | Lint's `A7-figure-not-discussed` / `A7-figure-late-reference` rules: 0 hits in `audits/gates/G3_lint.json` | -- | -- |

**Result: all three tables pass.** No `FIGURE_NOT_EXPLAINED` failure. Proceeding to step 16.
