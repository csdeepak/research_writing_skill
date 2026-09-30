# Learning Which Agent to Ask: A Small-Scale Study of Token Cost and Adaptation in Ownership-Based Routing for Shared LLM-Agent Memory

Section headings:
- Abstract
- 1. Introduction
- 2. Context and related work
- 3. Method and experimental setup
- 3.1 The system and the four routing arms
- 3.2 The cost experiment
- 3.3 Statistical design and the authors' reasons for it
- 3.4 The adaptation experiments
- 3.5 The static question-answering comparison
- 4. Results
- 4.1 RQ1: routing to a learned owner cut tokens per query by 22.1%
- 4.2 RQ2: routing kept answerability, and accuracy was lower in every recorded seed (untested)
- 4.3 RQ3: with ownership frozen, the router did not route and the saving nearly disappeared
- 4.4 RQ4: ASMOS reached a new topic's owner without retraining
- 4.5 Boundary: in one static question-answering run, ASMOS-memory did not help
- 5. Discussion
- 6. Limitations
- 6.1 Limitations stated by the authors
- 6.2 Additional caveats
- 7. Conclusion
- Availability and disclosure
- References
- Appendix A. Supplementary results

## Figure 1

[figure: Dot plot of the percentage reduction in LLM tokens per query for ten seeds, all near 22 percent, and a pooled row at 22.1 percent with a wider interval from 17.9 to 26.3 percent.]
[values drawn in the figure (Reduction in LLM total tokens per query %): seed 11: 22.1; seed 22: 22; seed 33: 22.1; seed 44: 22.1; seed 55: 22.1; seed 66: 21.9; seed 77: 22.1; seed 88: 22; seed 99: 22.2; seed 110: 22.1; All 10 seeds, 95% CI over queries: 22.1 (interval 17.9 to 26.3)]

*Figure 1.* Per-seed token reductions are nearly identical (21.9% to 22.2%), while the bootstrap 95% confidence interval over the 50 queries spans 17.9% to 26.3%, so the uncertainty comes from the queries, not the seeds. Points are the reduction in LLM total tokens per query of A1 relative to A0 in each of 10 seeds; the last row pools all 10 seeds. The horizontal axis does not start at zero. Source: the project's 10-seed cost result file.

## Figure 2

[figure: Dot plot of answer accuracy for four routing arms in five seeds: A0 and A2 at 0.72 in every seed, A1 between 0.68 and 0.70, and A3 between 0.54 and 0.56.]
[values drawn in the figure (Answer accuracy proportion correct): seed 66 / A0 global search: 0.72; seed 66 / A1 learned-ownership routing: 0.68; seed 66 / A2 ownership frozen at prior: 0.72; seed 66 / A3 similarity routing: 0.56; seed 77 / A0 global search: 0.72; seed 77 / A1 learned-ownership routing: 0.68; seed 77 / A2 ownership frozen at prior: 0.72; seed 77 / A3 similarity routing: 0.56; seed 88 / A0 global search: 0.72; seed 88 / A1 learned-ownership routing: 0.68; seed 88 / A2 ownership frozen at prior: 0.72; seed 88 / A3 similarity routing: 0.56; seed 99 / A0 global search: 0.72; seed 99 / A1 learned-ownership routing: 0.7; seed 99 / A2 ownership frozen at prior: 0.72; seed 99 / A3 similarity routing: 0.56; seed 110 / A0 global search: 0.72; seed 110 / A1 learned-ownership routing: 0.7; seed 110 / A2 ownership frozen at prior: 0.72; seed 110 / A3 similarity routing: 0.54]

*Figure 2.* Learned-ownership routing (A1) answered 0.68 to 0.70 of questions correctly in each of five seeds, below global search (A0) at 0.72 in every seed, while ownership frozen at its prior (A2) matched A0 and similarity routing (A3) reached 0.54 to 0.56. Each point is one arm in one seed over 50 queries (seeds 66 to 110); no paired test is available. The horizontal axis does not start at zero. Source: the project's 10-seed cost result file.

## Figure 3

[figure: Line plot with step 0 to 10 on the horizontal axis and route@1 on the new topic (0 to 1) on the vertical axis: ASMOS with two embedders rises gradually from 0.0 or 0.2 to 1.0, a frozen classifier stays at 0.0, and retrained classifiers stay at 0.0 until a retrain.]
[values drawn in the figure (Route@1 on the new topic): 0 / ASMOS (all-mpnet-base-v2): 0; 1 / ASMOS (all-mpnet-base-v2): 0.12; 2 / ASMOS (all-mpnet-base-v2): 0.24; 3 / ASMOS (all-mpnet-base-v2): 0.44; 4 / ASMOS (all-mpnet-base-v2): 0.64; 5 / ASMOS (all-mpnet-base-v2): 0.76; 6 / ASMOS (all-mpnet-base-v2): 0.8; 7 / ASMOS (all-mpnet-base-v2): 0.88; 8 / ASMOS (all-mpnet-base-v2): 0.92; 9 / ASMOS (all-mpnet-base-v2): 0.96; 10 / ASMOS (all-mpnet-base-v2): 1; 0 / ASMOS (bge-m3): 0.2; 1 / ASMOS (bge-m3): 0.52; 2 / ASMOS (bge-m3): 0.8; 3 / ASMOS (bge-m3): 0.84; 4 / ASMOS (bge-m3): 0.96; 5 / ASMOS (bge-m3): 0.96; 6 / ASMOS (bge-m3): 1; 7 / ASMOS (bge-m3): 1; 8 / ASMOS (bge-m3): 1; 9 / ASMOS (bge-m3): 1; 10 / ASMOS (bge-m3): 1; 0 / Frozen classifier: 0; 1 / Frozen classifier: 0; 2 / Frozen classifier: 0; 3 / Frozen classifier: 0; 4 / Frozen classifier: 0; 5 / Frozen classifier: 0; 6 / Frozen classifier: 0; 7 / Frozen classifier: 0; 8 / Frozen classifier: 0; 9 / Frozen classifier: 0; 10 / Frozen classifier: 0; 0 / Classifier retrained every 5 steps: 0; 1 / Classifier retrained every 5 steps: 0; 2 / Classifier retrained every 5 steps: 0; 3 / Classifier retrained every 5 steps: 0; 4 / Classifier retrained every 5 steps: 0; 5 / Classifier retrained every 5 steps: 0.84; 6 / Classifier retrained every 5 steps: 0.84; 7 / Classifier retrained every 5 steps: 0.84; 8 / Classifier retrained every 5 steps: 0.84; 9 / Classifier retrained every 5 steps: 0.84; 10 / Classifier retrained every 5 steps: 1; 0 / Classifier retrained every 10 steps: 0; 1 / Classifier retrained every 10 steps: 0; 2 / Classifier retrained every 10 steps: 0; 3 / Classifier retrained every 10 steps: 0; 4 / Classifier retrained every 10 steps: 0; 5 / Classifier retrained every 10 steps: 0; 6 / Classifier retrained every 10 steps: 0; 7 / Classifier retrained every 10 steps: 0; 8 / Classifier retrained every 10 steps: 0; 9 / Classifier retrained every 10 steps: 0; 10 / Classifier retrained every 10 steps: 1]

*Figure 3.* Without any retraining, the share of new-topic queries that ASMOS sends first to the right owner rises gradually over the steps, whereas a frozen classifier stays at zero and the retrained classifiers stay at zero until their first retrain. The vertical axis is route@1 on the new topic (0 to 1) and the horizontal axis is the step (0 to 10); lines are means over 5 seeds, and ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3) at step 0; classifier lines are from the all-mpnet-base-v2 run and are the same in the bge-m3 run. No error bars are drawn; the source records the standard deviation across seeds. Source: the project's new-topic result files.

## Table 1

[figure: ]


*Table 1.* Global search (A0) and ownership frozen at its prior (A2) cost about the same, learned-ownership routing (A1) costs fewer tokens per query with equal answerability but lower accuracy, and similarity routing (A3) is cheapest but answers far fewer queries.

## Table 2

[figure: ]


*Table 2.* In a single run of static question answering, ASMOS-memory scores below both No-Memory and RAG on both metrics; ASMOS combined with RAG is close to RAG on exact match but far below it on token-F1, and its exact match exceeds its token-F1, which standard definitions of the two metrics do not allow.
