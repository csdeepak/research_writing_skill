# Self-audit of draft v001 (AUTHOR, workflow steps 11 to 17)

Pre-screen only; it does not replace the blind review of step 18.

## Step 11 Reconstruction (from the skeleton and the abstract)
- The abstract alone gives Q1, Q3 (measurement gap), Q4, Q7, Q10 and the main limit; the skeleton gives all twelve (see G2_skeleton.md).
- The research question appears in the second of four Introduction paragraphs (before 50% of the introduction).

## Step 12 Evidence and claim audit
- verify_numbers: 0 errors, 0 warnings (no untraced number, no p-value outside the recorded 6.788e-09, 1.145e-08, 6.418e-09, 8.259e-08).
- lint_draft: 0 errors. No UNLICENSED-* finding. WARN-level findings: five claims still NEEDS_REVIEW (C005, C012, C014, C029, C031), and one undefined acronym (RULER, which is explained in prose).
- No BLOCKED claim is tagged. A text search of the draft for the blocked claims' distinctive values and wording (23.84, 39.14, 0.545, 0.917, 0 of 12, saturation, zero added labels, README E2/E7 values) returns nothing.
- Superseded values: r = 0.688 and z = 4.865 appear only in Section 4.6 as superseded, as the authors' correction record does.
- Negative results: E015 (Section 4.2, Figure 2), E072 (Section 4.4), E078 (Section 4.5) are in the main text; E094 is excluded with a provenance reason recorded in the claim map.

## Step 13 Flow
- Each Results subsection opens with the question it answers (title) and closes with the answer (RQ1 to RQ4). Section 4.5 and 4.6 are labelled boundary and correction.
- Connectives were checked: "therefore" in Section 4.4 follows from the regrets stated in the same sentence.

## Step 14 Terms and load
- audit_reader (persona B): 0 warnings. Terms defined at first use: ASMOS, LLM, CI, route@1 and regret (abstract), A0 to A3 (Section 3.1), RAG (Section 2), answerability (Section 3.2, definition requested from the authors).
- Sentences over 35 words are kept only where they carry a required attribution (the authors' limitations).

## Step 15 Figures and tables
- Registry V001 to V003 (figures) and T001 to T002 (tables). V1 to V4 and V6 pass; V5 needs a recorded human review and is NOT_RUN (not recorded on anyone's behalf).
- Every figure is drawn from a CSV under .rcs/plan/data/ built from the named project result file, and every plotted value occurs in that file.

## Step 16 Citations
- No source registry exists. There are no citations; five [CITATION NEEDED] markers stand in for related work and the effect-size reference.

## Step 17 Overclaim
- Watch-list words (significant, robust, generalizes, novel, outperforms, state of the art, causes, always, never) do not occur as assertions; the only hits are the ordinal 'first' (first retrain, first five seeds), 'No significance test is recorded', and the authors' own negated statement that ASMOS does not beat RAG. The ablation is worded "consistent with" and tagged low confidence. "Accuracy" is reported as measured in every seed.
- Scope: every result sentence names the corpus, model or run it comes from.
