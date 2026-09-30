# Step 11 — Reader reconstruction self-test (AUTHOR, reading paper.md alone, tags mentally stripped)

Q1 What problem is this paper solving? -> Whether/how well retrieval systems generalize zero-shot to tasks/domains they were not trained on (Intro para 1). **Present.**
Q2 Why does this problem matter? -> Building labeled data per new domain is costly, so deployments already rely on untested zero-shot transfer (Intro para 1). **Present.**
Q3 What is missing from existing approaches? -> No broad evaluation compares architectures zero-shot across many tasks/domains at once; MultiReQA/KILT are each narrower (Intro para 2, Background para 1). **Present.**
Q4 What exactly did the authors do? -> Built BEIR (18 datasets/9 tasks/1 format/1 metric), evaluated 10 systems/5 families zero-shot, profiled latency/index size, ran a TREC-COVID annotation-bias case study (Intro para 4, Sections 3-6). **Present.**
Q5 Why did they choose this method? -> Four dataset-selection criteria stated and justified (Section 3 para 1); nDCG@10 chosen because it scores both binary and graded judgements (Section 3 para 4); shared truncation/hardware for a fair comparison (Section 4 last para). **Present.**
Q6 What experiments were performed? -> The 18-dataset zero-shot comparison (Section 5) and the TREC-COVID Hole@10/re-annotation case study (Section 6). **Present.**
Q7 What are the strongest results? -> BM25+CE +11%/16 of 18; ColBERT +2.5%/9 of 18; several dense/sparse systems well below BM25; TAS-B/ANCE case; Hole@10 and re-annotation deltas (Section 5-6). **Present, with magnitudes.**
Q8 What do those results actually establish? -> In-domain accuracy does not predict zero-shot generalization; cross-attention-like interaction associates with better generalization at a cost; part of the non-lexical "gap" is a pooling artifact (Section 7 paras 1-2). **Present.**
Q9 What do they NOT establish? -> Not proof of a causal mechanism (Section 5 last para); not evidence against a task-specific model beating generalists (Limitations para 2); bias finding not measured beyond TREC-COVID (Limitations para 3, Discussion para 2). **Present.**
Q10 What is the primary contribution? -> BEIR itself, plus the comparative finding and the bias case study (Intro para 5, Conclusion para 1). **Present.**
Q11 What are the main limitations? -> English-only, short/medium documents, text-only signals, 1-2 fields, generalist-only, no error bars, incomplete compute reporting, bias measured on one dataset (Section 8, all four paragraphs). **Present.**
Q12 What should the reader remember one day later? -> BM25 is a strong, cheap zero-shot baseline; the best generalizers (re-ranking/late-interaction) are also the slowest; in-domain leaderboard position does not forecast zero-shot performance; some of the "non-lexical gap" is a measurement artifact of how test collections are built. **Present** (Abstract, Conclusion).

## Comparison against spine.md and claims/claim_evidence_map.json
No mismatches found: every spine line's claim IDs are represented in the draft at the location predicted by plan/paper_architecture.md, and no claim in the draft states something absent from, or stronger than, its claim_evidence_map.json entry (cross-checked against the specific overclaim fix in step 17). Grading: **all Q1-Q12 = present**, none weakened/overstated/contradicted/absent, no intrusions (no content not traceable to a claim/evidence ID or explicit background note) found.

This is a same-context self-test per the run's no-subagent/no-fresh-context constraint (accepted_risks RISK-003 in state.json), not a substitute for step 18's blind review, which is out of scope for this run.
