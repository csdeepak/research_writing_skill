# Step 11 -- Reader reconstruction self-test

Read `.rcs/drafts/v001/paper.md` top to bottom as a fresh reader would (no subagent available in
this run; performed by the sole agent as a distinct pass after drafting, per `evaluation_rubric.md`
Section 1), then compared the answers against `story/spine.md` and `claims/claim_evidence_map.json`.

| # | Question | Answer found in the draft | Location | vs. gold (spine/claims) |
|---|----------|---------------------------|----------|--------------------------|
| Q1 | Problem | Retrieval models are trained/tested on one dataset; behavior elsewhere is untested | Abstract; Intro P1 | present, matches spine line 1 |
| Q2 | Motivation | Zero-shot deployment is common because in-domain data is costly to collect for every new setting | Intro P2 | present, matches C020 |
| Q3 | What's missing | Prior multi-dataset resources (MultiReQA, KILT) each relax only one axis of narrowness | Intro P3; Related Work | present, matches spine line 2 / C002 |
| Q4 | What was done | Built BEIR (18 datasets/9 tasks, 4-way diversity), one format, nDCG@10, evaluated 10 systems/5 families | Intro P5; Sec. 3-4 | present, matches C001/C021/C022 |
| Q5 | Why this method | Dataset-selection rationale (avoid narrowness / annotation-artifact dominance); metric rationale (handles binary+graded) | Intro P5; Sec. 3 P1,P3 | present, matches C021/C022 |
| Q6 | Experiments | Main 18x10 comparison; TREC-COVID annotation-bias case study; similarity-function ablation | Sec. 5.1-5.4 (subheadings) | present |
| Q7 | Strongest results | In-domain/OOD reversal; avg-vs-BM25 ranking; 20-30x cost gap; annotation-bias effect, all with magnitudes | Abstract; Table 1; Table 2; Sec. 5 | present, magnitudes given |
| Q8 | What results establish | Each Discussion paragraph opens by answering one research question directly | Sec. 6, P1-P3 | present, matches C005/C008/C019 |
| Q9 | What results do NOT establish | Explicit non-conclusions: bias effect not confirmed on other 17 datasets; margins are point estimates; upper-bound framing | Sec. 5.4 last P; Sec. 6 P3; Sec. 7 | present |
| Q10 | Primary contribution | Numbered three-contribution list | Intro, last paragraph | present, matches spine lines 4-5 |
| Q11 | Main limitations | Five author-stated boundaries + no-variance caveat + two additional (writer-derived) caveats | Sec. 7 | present, matches L001-L008 |
| Q12 | One-day-later memory | In-domain accuracy is a poor guide to zero-shot performance; lexical baseline competitive; generalization/cost trade-off | Conclusion P1 | present, matches spine lines 5-6 |

**Grading:** all 12 answers are `present` (none `weakened`, `overstated`, `contradicted`, or
`absent`); no intrusions (no reference to anything outside the draft's own text/tables) were
found. Core RR (Q1, Q4, Q7, Q10, Q11) = 5/5 present = 1.0, which meets the >=0.8 exit criterion
in `evaluation_rubric.md` Section 4.

**Note on isolation:** this is a same-context self-test, not an isolated fresh-context read (no
subagent available in this run). Labeled `isolation: none` per `workflow.md` step 11 and the
"No shortcut" table in `workflow.md`'s Shortcuts section. It is a pre-screen and does not replace
step 18 (blind review), which is out of scope for this run per the run-specific constraints.
