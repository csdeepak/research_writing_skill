# Learning Which Agent to Ask: A Small-Scale Study of Token Cost and Adaptation in Ownership-Based Routing for Shared LLM-Agent Memory

## Abstract

When several large language model (LLM) agents share a memory, a system must decide whose memory to consult per query; consulting all (global search) costs tokens every time. We measure the Adaptive Semantic Memory Operating System (ASMOS), which learns from verified outcomes which agent owns each topic and routes queries to that owner, on a deliberately constructed two-agent corpus. On 50 queries with gpt-4o-mini and 10 seeds, routing used 22.1% fewer LLM total tokens per query than global search (bootstrap 95% confidence interval (CI) 17.9% to 26.3%). Answerability (a per-query measure whose definition is undocumented) was 0.98 under both, but accuracy was lower under routing in each of five recorded seeds (0.68 to 0.70 against 0.72; no paired test), so the accuracy cost cannot be bounded. With ownership frozen at its initial value the router did not route and the saving nearly disappeared, which is consistent with the saving requiring routing but does not isolate learning. For a new topic, ASMOS had cumulative regret (summed shortfall in route@1, the share of queries sent first to the right owner) of 3.24 (std 1.30) and 0.92 (std 0.41) with two embedders and 0 retrains, against 4.8 for the best retrained classifier and 10.0 for a frozen one over 5 seeds, untested. In one static question-answering run, ASMOS-memory scored below a no-memory baseline and retrieval-augmented generation; the authors state it is not a question-answering method. The saving is not a rate for organic workloads.

## 1. Introduction

When LLM agents share a semantic memory, each query raises a question: whose memory to consult? The default, global search, consults every candidate. On the two-agent test corpus used below, global search considers a mean of 32.0 candidates and passes 123.2 context tokens per query to the answering model, so candidates are not agents. ASMOS adds to a shared memory an ownership layer that decides which agent to ask. Ownership of a topic is learned online from verification-gated reputation: a verified claim raises an agent's ownership of a topic, a refuted claim lowers it, and a query is routed to the learned owner, with a fallback to global search when routing is not confident.

The gap is one of measurement: what learned ownership saves against global search, costs in answer quality, and does when topics change. Without verified literature, we cannot place the work against published routing or memory methods. We ask four research questions. RQ1: how many fewer LLM tokens per query does routing to a learned owner use than global search, and how certain is the size? RQ2: what does routing do to answer accuracy and answerability? RQ3: does the saving depend on ownership having moved from its prior, as tested by freezing it? RQ4: how quickly does ownership-based routing reach the owner of a new topic (cumulative regret in route@1), compared with supervised classifier routers? A boundary check asks whether ASMOS memory helps on static single-agent question answering.

The paper is a bounded measurement, not a new method positioned against prior work, and makes four contributions:

1. A token saving of 22.1% per query against global search, with a bootstrap interval, a signed-rank test and an effect size beside the number of non-zero pairs (Section 4.1).
2. An accuracy accounting: equal answerability, but lower accuracy in every recorded seed by an amount the evidence cannot bound (Section 4.2).
3. An ablation, with its reach stated, that is consistent with the saving requiring routing on learned ownership (Section 4.3).
4. Descriptive new-topic results with two embedders and two negative results: a degraded embedder, and static question answering (Sections 4.4 and 4.5).

Section 2 gives context, Section 3 the setup, Section 4 the results by question, and Sections 5 to 7 the discussion, limitations and conclusion.

## 2. Context and related work

We organize the context by dimension and claim no novelty, since no literature search was run. On how a query is routed, this study compares global search, similarity routing, routing with ownership frozen, and routing on ownership learned from verified outcomes. On how a memory answers, a retrieval-augmented generation (RAG) baseline and a no-memory baseline bracket ASMOS memory in the static comparison. On what adapts under change, the comparison is a supervised classifier router, frozen or retrained on a schedule, which regains a new topic only after a retrain. How work on expert finding or on reputation from verified outcomes relates to learned ownership is left open.

## 3. Method and experimental setup

### 3.1 The system and the four routing arms

For each query, the ASMOS router scores an agent by the product of the query's similarity to the agent's memory and the agent's ownership of the topic, routes to the top-scoring agent, and falls back to global search when the score is below a threshold (tau).

The package does not specify, and we do not reconstruct, what a claim is, how verification outcomes arise, how topics are assigned, the update rule and prior, when ownership is learned relative to evaluation, or what a candidate is.

The four arms run on the same queries. Global search (A0) consults every candidate. Learned-ownership routing (A1, called transactive routing in the project) is ASMOS as described. Ownership frozen at its prior (A2) is the authors' ablation of A1. In this run A2 does not route to a single owner in any recorded seed (route@1 0.0) and falls back to global search, so it contrasts routing with no routing rather than testing the learning process. Why the prior ownership does not lift the score above tau is not documented, and A2's small differences from A0 (179.3 against 180.2 tokens per query, 31.7 against 32.0 candidates) are unexplained. Similarity routing (A3) routes on embedding similarity alone.

### 3.2 The cost experiment

The evaluation set has 50 queries in five query classes on a corpus whose ownership is asymmetric by construction. The classes, Q1 to Q5 in the result file, are not described. The answering model is gpt-4o-mini at temperature 0, run with 10 seeds (11, 22, ..., 110) and a routing threshold fixed at 0.351493.

Seeds 11 to 55 come from an earlier result file that is not in the package, so accuracy, answerability, route@1, context tokens and candidate-set size exist for seeds 66 to 110 only. The seeds agree closely on every recorded measure, and what they randomize at temperature 0 is not documented. The cost result file does not record which embedder was used.

The primary measure is LLM total tokens per query as recorded in the result file. The authors state that these are exact usage counts and that counting them does not depend on the embedder. The counted quantity does depend on it, because the chosen agent and the number of candidates passed depend on similarity, so the unrecorded embedder matters for the pooled seeds.

The file reports no separate cost for computing embeddings, updating ownership or producing verification outcomes, so the saving is in recorded LLM usage per query, not a whole-system net saving. We also report answer accuracy, whose grading on this corpus is not documented; answerability, recorded per query without a documented definition; and route@1, the share of queries whose top-ranked agent is the ground-truth owner. Global search has route@1 0.0 by construction because it routes to no single agent, and route@1 is recorded without its denominator.

### 3.3 Statistical design and the authors' reasons for it

The uncertainty is a bootstrap 95% CI over the 50 queries with 2000 resamples. The paired per-query difference is tested with a one-sided Wilcoxon signed-rank test (normal approximation) that drops zero differences. The authors keep zero differences dropped because switching to the Pratt method would change an already pre-registered p-value. No multiplicity correction is applied because the analysis is a single comparison of A0 with A1. The package holds no registry entry or dated protocol for the cited pre-registration, and the other runs' tests (Appendix A) are uncorrected. The effect size is the matched-pairs rank-biserial correlation. (Appendix A gives its definition.) The authors chose it because it is the direct companion of the signed-rank test and has a single definition, whereas Rosenthal's z divided by the square root of N has an ambiguous N here. They report the number of non-zero pairs (n_eff) beside every effect size, because a bare r = 1.0 invites the false reading that every query improved.

### 3.4 The adaptation experiments

In the new-topic regime a topic appears whose true owner is a single agent, and the router has to find that owner; the runs do not record how many agents take part. Each run has 10 steps, 5 evaluation queries per step and 5 seeds, with the all-mpnet-base-v2 or the bge-m3 embedder. Regret is the sum over steps 1 to 10 of one minus route@1 on the new topic, so a router that does not find the topic at any step has a regret of 10.0.

ASMOS is compared with a supervised classifier router that is frozen, retrained every 5 steps, or retrained every 10 steps. The comparison is not matched on tuning or update access. ASMOS uses the cost experiment's threshold (0.351493), which was not tuned on a held-out split, while the classifiers use 0.5; the artifacts count 10 labels consumed by ASMOS, as by each retrained classifier, under an undocumented counter; and no classifier updated online from the same labels is included. The classifier results are identical under both embedders, and their input features and tuning are not recorded.

A separate single stationary run compares ASMOS with the classifier under the MiniLM-L6-v2 embedder and under a lexical-hash fallback. The authors regard the hash fallback as a degraded offline mode and not their evaluation baseline, and use MiniLM for the routing numbers reported in their own documentation. In short, the embedder is not recorded for the cost experiment, is all-mpnet-base-v2 or bge-m3 in the new-topic runs, and is MiniLM-L6-v2 or the hash fallback in the stationary run.

### 3.5 The static question-answering comparison

No-Memory, RAG, ASMOS-memory alone and ASMOS combined with RAG each ran once, with gpt-4o-mini and one uniform answering call, on 24 static single-agent question-answering items that the project draws from a benchmark it names RULER. There are no seeds, and the exact-match and token-F1 definitions used are not documented.

The authors note that retrieval precision and recall and route@1 cannot be computed here, because the data has no relevant-document or owner labels, and that the combined system exercises routing with a single expert.

## 4. Results

### 4.1 RQ1: routing to a learned owner cut tokens per query by 22.1%

Table 1 compares the four arms. Over 50 queries and all 10 seeds, the mean LLM tokens per query were 180.2 for global search (A0) and 140.4 for learned-ownership routing (A1), so A1 used 22.1% fewer tokens, a mean of 39.8 tokens per query. In seeds 66 to 110, the mean context tokens per query fell from 123.2 to 83.6 and the mean candidate-set size from 32.0 to 20.8.

**Table 1.** A0 and A2 cost about the same; A1 costs fewer tokens per query with equal answerability but lower accuracy; A3 is cheapest but answers far fewer queries. Tokens per query are means over 50 queries and all 10 seeds; the other columns cover seeds 66 to 110 only (accuracy is a range over those seeds).

| Arm | LLM tokens per query (10 seeds) | Context tokens | Candidate-set size | Answer accuracy | Answerability | route@1 |
|---|---|---|---|---|---|---|
| A0 global search | 180.2 | 123.2 | 32.0 | 0.72 | 0.98 | 0.0 |
| A1 learned-ownership routing | 140.4 | 83.6 | 20.8 | 0.68 to 0.70 | 0.98 | 0.909 |
| A2 ownership frozen at prior | 179.3 | 122.3 | 31.7 | 0.72 | 0.98 | 0.0 |
| A3 similarity routing | 123.4 | 65.9 | 17.9 | 0.54 to 0.56 | 0.58 | 0.614 |

Figure 1 shows how certain the size is. The bootstrap 95% CI over queries is 17.9% to 26.3%, and the per-seed reductions lie between 21.9% and 22.2%. The one-sided Wilcoxon signed-rank test on the 50 per-query differences gave W = 1141.5 and p = 6.788e-09, over 48 non-zero pairs of 50; the rank-biserial correlation is r = 0.941 (T+ = 1141.5, T- = 34.5), so nearly all of the rank weight lies with pairs favouring routing. The interval is wide relative to the per-seed spread because it reflects differences between queries: the per-seed standard deviation of the reduction is 0.07 percentage points against an interval width of 8.3, so more seeds would not narrow it. The stored effect size for this test was corrected before this paper (Appendix A).

![Figure 1](figures/V001.svg)

**Figure 1.** Per-seed token reductions are nearly identical (21.9% to 22.2%), while the bootstrap 95% confidence interval over the 50 queries spans 17.9% to 26.3%, so the uncertainty comes from the queries, not the seeds. Points: reduction in LLM total tokens per query, A1 relative to A0, per seed; the last row pools all 10 seeds. The horizontal axis does not start at zero. Source: the project's 10-seed cost result file.

This answers RQ1: on this constructed corpus and answering model, learned-ownership routing used about a fifth fewer LLM tokens per query than global search. It does not show the saving on an organic workload or for accuracy, which the next subsection examines. For two other answering models only signed-rank statistics are recorded (Appendix A), so the size of the saving for another model is not established.

### 4.2 RQ2: routing kept answerability, and accuracy was lower in every recorded seed (untested)

In seeds 66, 77, 88, 99 and 110, answerability was 0.98 for A0, A1 and A2 and 0.58 for the similarity arm A3 in every seed. Answer accuracy was 0.72 for A0 and A2 in every seed, between 0.68 and 0.70 for A1 and between 0.54 and 0.56 for A3. On 50 questions the difference is 1 or 2 questions per seed, and because the seeds agree closely on every measure they are not five independent replications. With no paired test and an undocumented grading procedure, neither the size nor the reliability of the accuracy difference is established.

![Figure 2](figures/V002.svg)

**Figure 2.** Learned-ownership routing (A1) answered 0.68 to 0.70 of questions correctly in each of five seeds, below global search (A0) at 0.72 in every seed, while A2 matched A0 and A3 reached 0.54 to 0.56. Each point is one arm in one seed over 50 queries (seeds 66 to 110). The horizontal axis does not start at zero. Source: the project's 10-seed cost result file.

This answers RQ2 descriptively: routing preserved answerability relative to global search (0.98 for both) but not accuracy in the recorded seeds, so the token saving is not a saving at equal accuracy. The similarity-only arm shows the trade-off in the other direction: it is the cheapest arm at 123.4 tokens per query, but its answerability is 0.58. The recorded route@1 was 0.909 for A1 and 0.614 for A3. These values are descriptive: no test and no denominator are recorded, and with two agents a router that picked an agent at random would be right about half the time.

### 4.3 RQ3: with ownership frozen, the router did not route and the saving nearly disappeared

With ownership frozen at its prior (A2), the mean LLM tokens per query were 179.3, within 0.9 tokens of global search (180.2) and 38.9 tokens above A1 (140.4). A2's route@1 was 0.0: it did not route to a single owner and fell back to global search. This is consistent with the saving requiring routing on ownership that has moved above the threshold. Because A2 collapses to global search, the ablation contrasts routing with no routing; it cannot separate the learning process from, for example, a correctly set static ownership, and no arm with static but informative ownership was run. This answers RQ3 at low confidence: there is no test, per-seed gap or interval for A1 against A2, and the result concerns one constructed corpus.

### 4.4 RQ4: ASMOS reached a new topic's owner without retraining

With the all-mpnet-base-v2 embedder, ASMOS reached a cumulative regret of 3.24 (std 1.30) with 0 retrains and routed the new topic in 5 of 5 seeds; the criterion for having routed it is not recorded. A frozen classifier did not route it in any of the 5 seeds (regret 10.0), a classifier retrained every 5 steps had regret 4.8 (std 0.4, 2 retrains) and one retrained every 10 steps had regret 9.0 (1 retrain), so ASMOS had the lowest mean regret of the routers in this run, in an untested and unmatched comparison. With the bge-m3 embedder, ASMOS reached 0.92 (std 0.41) with 0 retrains and again routed the topic in 5 of 5 seeds, and the classifier results were identical (10.0, 4.8 and 9.0). In both runs ASMOS thus adapted with zero retraining, though not without labels: the artifacts record 10 labels consumed by ASMOS, as by each retrained classifier. Figure 3 shows the route@1 path: ASMOS climbs gradually, and after its first retrain at step 5 the classifier retrained every 5 steps is briefly ahead of ASMOS with the all-mpnet-base-v2 embedder, before ASMOS passes it. No significance test is recorded for these regret comparisons.

![Figure 3](figures/V003.svg)

**Figure 3.** Without retraining, the share of new-topic queries ASMOS sends first to the right owner rises gradually, whereas a frozen classifier stays at zero and retrained classifiers stay at zero until their first retrain. Axes: route@1 on the new topic (0 to 1) against step (0 to 10); lines are means over 5 seeds; ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3); classifier lines, from the all-mpnet-base-v2 run, are the same with bge-m3. No error bars are drawn; the source records the standard deviation across seeds. Source: the project's new-topic result files.

Three qualifications apply. First, regret depends strongly on the embedder, 3.24 against 0.92. Second, per-step answerability is identical for all four arms in both runs (0.0 at step 0 rising to 1.0 at step 10), so the comparison rests on routing alone. Third, in the single stationary run, ASMOS with the lexical-hash fallback had route@1 0.667 against 1.0 for the classifier, so it was not routing-competitive there; the MiniLM-L6-v2 values of that run are in Appendix A.

This answers RQ4 descriptively for the tested runs: ASMOS reached the new owner with no retraining and had lower mean regret than the scheduled classifiers, in a comparison that is untested and not matched on tuning or update access (Section 3.4), and the result does not extend to the degraded embedder.

### 4.5 Boundary: in one static question-answering run, ASMOS-memory did not help

Table 2 gives the four-system comparison on 24 items. Exact-match scores were 0.3333 for No-Memory, 0.7083 for RAG, 0.1667 for ASMOS-memory and 0.625 for ASMOS combined with RAG, equal to the containment scores in every row, and token-F1 was 0.5642, 0.7513, 0.4155 and 0.4329. For the combined system exact match exceeds token-F1, which standard definitions do not allow, so at least one column is not computed as its name suggests. ASMOS-memory alone scored below No-Memory and below RAG on both metrics, and ASMOS did not exceed RAG. The paired token-F1 difference of RAG over ASMOS-memory was 0.3358 (bootstrap 95% CI 0.1494 to 0.5228), and the combined system was below RAG by 0.3184 (CI -0.4990 to -0.1406). On exact match the combined system trails RAG by less (0.625 against 0.7083), and no interval is recorded for that metric.

**Table 2.** In a single run of static question answering, ASMOS-memory scores below both No-Memory and RAG on both metrics; ASMOS combined with RAG is close to RAG on exact match but far below it on token-F1, and its exact match exceeds its token-F1, which standard definitions do not allow. All rows are one run of 24 items; mean total tokens are per question.

| System | Exact match | Token-F1 | Mean total tokens |
|---|---|---|---|
| No-Memory | 0.3333 | 0.5642 | 152.0 |
| RAG | 0.7083 | 0.7513 | 711.4 |
| ASMOS-memory | 0.1667 | 0.4155 | 353.7 |
| ASMOS + RAG | 0.625 | 0.4329 | 1181.9 |

ASMOS-memory used 353.7 total tokens per question against 152.0 for No-Memory, and the combined system spent the most, 1181.9. Why ASMOS-memory scored below No-Memory is not diagnosed (Appendix A). The authors state that ASMOS does not beat RAG on span-retrieval question answering and is not a question-answering-accuracy method.

## 5. Discussion

Routing to a learned owner used 22.1% fewer LLM tokens per query (RQ1) with equal answerability and lower accuracy of unknown size (RQ2). The saving is consistent with requiring routing on learned ownership (RQ3), and ASMOS reached a new topic's owner without retraining in untested comparisons (RQ4).

Learned ownership sits between global search and similarity routing: it cost 39.8 tokens per query less than global search while keeping answerability at 0.98, whereas similarity routing cost fewer tokens still (123.4 against 140.4) but its answerability was 0.58. One untested explanation is that the ownership signal, and not similarity alone, lets routing narrow the candidate set without losing answerability on this corpus; the accuracy shortfall of A1 suggests that narrowing is not free.

In absolute terms the saving is 39.8 of 180.2 recorded tokens per query. Scaling with memory and team size, and the cost of verification, ownership updates and embeddings, are not measured, so the full cost ledger is unknown. We cannot relate these results to published methods. Within these limits, where a workload has topic-specific owners and an accuracy cost of unknown size is acceptable, learned ownership is a candidate way to lower per-query LLM usage. It is not evidence for using ASMOS to improve answer quality on static questions.

## 6. Limitations

### 6.1 Limitations stated by the authors

The authors state that more seeds cannot narrow a confidence interval that is set by heterogeneity between queries. They state that ownership asymmetry does not emerge organically because the corpus is deliberately constructed, so the saving is not a rate for organic multi-agent workloads. They state that ASMOS does not beat RAG on span-retrieval question answering and is not a question-answering-accuracy method. They note that retrieval precision and recall and route@1 cannot be computed on the single-agent question-answering data.

They list among their caveats a tested convergence and sample-efficiency hypothesis whose result file is not in the package and whose reporting is undecided, so we claim nothing about faster or more sample-efficient learning. They list as descoped agent-specific memory projection, contradiction detection (refutation is claimed only when supplied as a verification outcome) and continuous forgetting (off by default). They state that the routing threshold is tuned in the same corpus rather than on a held-out split, which can favour ASMOS. They also state that question-answering grading is done by an LLM, that ownership verification is deterministic, that a memory-reuse threshold is an untuned placeholder feeding no reported number, and that their multi-agent validation is one seedless run with an imposed partition, not reported here because its result file is missing. They state that the embedder of their earliest centerpiece run, not reported here, is unconfirmed, and that token counts are exact and embedder-independent. They exclude one embedder cell from the new-topic replication because its run fell back to a hash embedder. They note that a recorded continuous-integration pass or coverage artifact is outstanding, so we report no software test result.

### 6.2 Additional caveats

Additional caveats are ours, not the authors'. Seeds 11 to 55 come from an absent result file (Section 3.2). The accuracy difference is untested and rests on 1 or 2 questions per seed (Section 4.2). The ablation has no test (Section 4.3). The token measure excludes embedding, ownership updates and verification. The cost corpus has two agents, and the new-topic runs do not record their agent count, so nothing is measured for larger teams. Route@1 denominators are not recorded.

The corpus, query set, agent partition and code are not in the package, and classifier tuning is not documented. The new-topic comparison is not matched on tuning or update access (Section 3.4). The new-topic regime has 5 seeds and 5 evaluation queries per step, and regret differs about threefold between embedders. The four-system comparison is one run of 24 items with no p-values and inconsistent metric values. The stationary embedder run is a single run with no stated query count. For other answering models only signed-rank statistics are recorded. Several results in the project's documentation are not reported because their source files are missing. The headline saving uses one answering model, gpt-4o-mini.

## 7. Conclusion

On a deliberately constructed two-agent corpus, routing on ASMOS's learned ownership (mechanism undocumented) used 22.1% fewer LLM tokens per query than global search, while accuracy was lower in every recorded seed by an amount the evidence cannot bound. With ownership frozen the router did not route and the saving nearly disappeared (untested), which is consistent with the saving requiring routing on learned ownership, while leaving open whether the learning process produces it; in the tested new-topic runs, ASMOS reached the new owner without retraining. The key boundary is that the corpus is constructed, and ASMOS-memory did not improve static question answering in a single small run. Next questions: does the saving survive an organic workload, larger teams and other answering models; what does a paired accuracy test show; and how does ASMOS compare with an online-updated classifier given the same labels?

## Availability and disclosure

The corpus, query set and code were not part of the material used for this paper. This draft was prepared with an automated writing assistant.

## References

No verified references are available for this draft; see the citation markers in the text.

## Appendix A. Supplementary results

**Effect-size correction.** The effect size first stored for the headline test (r = 0.688, labelled a rank-biserial correlation) and its z-statistic (4.865) were computed incorrectly, and are superseded by r = 0.941 and z = 5.679. The authors' correction record reports that the stored value used null moments built on all 50 pairs while the statistic ranks 48, so the defect could only understate a positive effect; W, the one-sided p-value, the percentage reduction, the interval and the per-seed spread did not change.

**Other cost runs.** Corrected signed-rank statistics are recorded for three further cost runs: gpt-4o-mini with 5 seeds (W = 1142.5, 48 of 50 non-zero, r = 0.943), qwen3-30b-a3b with 5 seeds (W = 1052.0, 46 of 50, r = 0.946) and a one-seed qwen-2.5-72b pilot (W = 666.0, 36 of 50, r = 1.0 with 14 zero differences, so not every query improved). Their percentage reductions are not recorded.

**Stationary embedder run.** In the single stationary run, which has no seeds and no stated query count, ASMOS with the MiniLM-L6-v2 embedder and the classifier both had route@1 1.0. The recorded answerability was 0.909 for ASMOS and 0.727 for the classifier; these values are multiples of 1/11, so if the run had 11 queries the gap is two queries, and no test exists.

**Static question answering.** The paired token-F1 difference between ASMOS combined with RAG and ASMOS-memory was +0.0174 (CI -0.1546 to +0.1862), which spans zero. No p-values are recorded for these comparisons. The package does not diagnose why ASMOS-memory scored below No-Memory. One untested possibility is that the memory context it adds displaces or distracts from what the answering model would otherwise answer; whether a similar effect contributes to A1's lower accuracy is also untested.

Effect-size definition. Over the non-zero pairs, r = (T+ - T-)/(T+ + T-), where T+ and T- are the rank sums of the pairs favouring routing and favouring global search, so r runs from -1 to 1 and r = 1 means that every non-zero pair favoured routing. Of the 50 pairs, 43 favoured routing, 5 favoured global search and 2 were identical.


**Figure 1.** Per-seed token reductions are nearly identical (21.9% to 22.2%), while the bootstrap 95% confidence interval over the 50 queries spans 17.9% to 26.3%, so the uncertainty comes from the queries, not the seeds. Points are the reduction in LLM total tokens per query of A1 relative to A0 in each of 10 seeds; the last row pools all 10 seeds. The horizontal axis does not start at zero. Source: the project's 10-seed cost result file. [figure: Dot plot of the percentage reduction in LLM tokens per query for ten seeds, all near 22 percent, and a pooled row at 22.1 percent with a wider interval from 17.9 to 26.3 percent.] [values drawn in the figure (Reduction in LLM total tokens per query %): seed 11: 22.1; seed 22: 22; seed 33: 22.1; seed 44: 22.1; seed 55: 22.1; seed 66: 21.9; seed 77: 22.1; seed 88: 22; seed 99: 22.2; seed 110: 22.1; All 10 seeds, 95% CI over queries: 22.1 (interval 17.9 to 26.3)]

**Figure 2.** Learned-ownership routing (A1) answered 0.68 to 0.70 of questions correctly in each of five seeds, below global search (A0) at 0.72 in every seed, while ownership frozen at its prior (A2) matched A0 and similarity routing (A3) reached 0.54 to 0.56. Each point is one arm in one seed over 50 queries (seeds 66 to 110); no paired test is available. The horizontal axis does not start at zero. Source: the project's 10-seed cost result file. [figure: Dot plot of answer accuracy for four routing arms in five seeds: A0 and A2 at 0.72 in every seed, A1 between 0.68 and 0.70, and A3 between 0.54 and 0.56.] [values drawn in the figure (Answer accuracy proportion correct): seed 66 / A0 global search: 0.72; seed 66 / A1 learned-ownership routing: 0.68; seed 66 / A2 ownership frozen at prior: 0.72; seed 66 / A3 similarity routing: 0.56; seed 77 / A0 global search: 0.72; seed 77 / A1 learned-ownership routing: 0.68; seed 77 / A2 ownership frozen at prior: 0.72; seed 77 / A3 similarity routing: 0.56; seed 88 / A0 global search: 0.72; seed 88 / A1 learned-ownership routing: 0.68; seed 88 / A2 ownership frozen at prior: 0.72; seed 88 / A3 similarity routing: 0.56; seed 99 / A0 global search: 0.72; seed 99 / A1 learned-ownership routing: 0.7; seed 99 / A2 ownership frozen at prior: 0.72; seed 99 / A3 similarity routing: 0.56; seed 110 / A0 global search: 0.72; seed 110 / A1 learned-ownership routing: 0.7; seed 110 / A2 ownership frozen at prior: 0.72; seed 110 / A3 similarity routing: 0.54]

**Figure 3.** Without any retraining, the share of new-topic queries that ASMOS sends first to the right owner rises gradually over the steps, whereas a frozen classifier stays at zero and the retrained classifiers stay at zero until their first retrain. The vertical axis is route@1 on the new topic (0 to 1) and the horizontal axis is the step (0 to 10); lines are means over 5 seeds, and ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3) at step 0; classifier lines are from the all-mpnet-base-v2 run and are the same in the bge-m3 run. No error bars are drawn; the source records the standard deviation across seeds. Source: the project's new-topic result files. [figure: Line plot with step 0 to 10 on the horizontal axis and route@1 on the new topic (0 to 1) on the vertical axis: ASMOS with two embedders rises gradually from 0.0 or 0.2 to 1.0, a frozen classifier stays at 0.0, and retrained classifiers stay at 0.0 until a retrain.] [values drawn in the figure (Route@1 on the new topic): 0 / ASMOS (all-mpnet-base-v2): 0; 1 / ASMOS (all-mpnet-base-v2): 0.12; 2 / ASMOS (all-mpnet-base-v2): 0.24; 3 / ASMOS (all-mpnet-base-v2): 0.44; 4 / ASMOS (all-mpnet-base-v2): 0.64; 5 / ASMOS (all-mpnet-base-v2): 0.76; 6 / ASMOS (all-mpnet-base-v2): 0.8; 7 / ASMOS (all-mpnet-base-v2): 0.88; 8 / ASMOS (all-mpnet-base-v2): 0.92; 9 / ASMOS (all-mpnet-base-v2): 0.96; 10 / ASMOS (all-mpnet-base-v2): 1; 0 / ASMOS (bge-m3): 0.2; 1 / ASMOS (bge-m3): 0.52; 2 / ASMOS (bge-m3): 0.8; 3 / ASMOS (bge-m3): 0.84; 4 / ASMOS (bge-m3): 0.96; 5 / ASMOS (bge-m3): 0.96; 6 / ASMOS (bge-m3): 1; 7 / ASMOS (bge-m3): 1; 8 / ASMOS (bge-m3): 1; 9 / ASMOS (bge-m3): 1; 10 / ASMOS (bge-m3): 1; 0 / Frozen classifier: 0; 1 / Frozen classifier: 0; 2 / Frozen classifier: 0; 3 / Frozen classifier: 0; 4 / Frozen classifier: 0; 5 / Frozen classifier: 0; 6 / Frozen classifier: 0; 7 / Frozen classifier: 0; 8 / Frozen classifier: 0; 9 / Frozen classifier: 0; 10 / Frozen classifier: 0; 0 / Classifier retrained every 5 steps: 0; 1 / Classifier retrained every 5 steps: 0; 2 / Classifier retrained every 5 steps: 0; 3 / Classifier retrained every 5 steps: 0; 4 / Classifier retrained every 5 steps: 0; 5 / Classifier retrained every 5 steps: 0.84; 6 / Classifier retrained every 5 steps: 0.84; 7 / Classifier retrained every 5 steps: 0.84; 8 / Classifier retrained every 5 steps: 0.84; 9 / Classifier retrained every 5 steps: 0.84; 10 / Classifier retrained every 5 steps: 1; 0 / Classifier retrained every 10 steps: 0; 1 / Classifier retrained every 10 steps: 0; 2 / Classifier retrained every 10 steps: 0; 3 / Classifier retrained every 10 steps: 0; 4 / Classifier retrained every 10 steps: 0; 5 / Classifier retrained every 10 steps: 0; 6 / Classifier retrained every 10 steps: 0; 7 / Classifier retrained every 10 steps: 0; 8 / Classifier retrained every 10 steps: 0; 9 / Classifier retrained every 10 steps: 0; 10 / Classifier retrained every 10 steps: 1]

**Table 1.** Global search (A0) and ownership frozen at its prior (A2) cost about the same, learned-ownership routing (A1) costs fewer tokens per query with equal answerability but lower accuracy, and similarity routing (A3) is cheapest but answers far fewer queries. [figure: ] 

**Table 2.** In a single run of static question answering, ASMOS-memory scores below both No-Memory and RAG on both metrics; ASMOS combined with RAG is close to RAG on exact match but far below it on token-F1, and its exact match exceeds its token-F1, which standard definitions of the two metrics do not allow. [figure: ] 