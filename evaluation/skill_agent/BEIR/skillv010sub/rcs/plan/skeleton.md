# Research skeleton (one topic sentence per paragraph slot; step 9)

## Abstract
- AB.1 Existing broad retrieval evaluations do not test how retrieval systems generalize zero-shot across many tasks and domains at once {C020}.
- AB.2 We built BEIR, unifying 18 datasets across 9 tasks into one format and metric, and evaluated 10 systems from 5 architecture families zero-shot {C021}.
- AB.3 BM25 remains a strong zero-shot baseline; no architecture dominates; re-ranking and late-interaction generalize best but are slowest, while several dense and sparse systems underperform BM25 on average {C001}{C004}{C008}{C015}.
- AB.4 Some BEIR test collections' lexically-pooled annotations understate non-lexical systems' true performance {C018}.
- AB.5 In-domain accuracy is a poor generalization proxy, and these findings are bounded to English, mostly short-to-medium text {C003}.

## 1. Introduction
- I.1 Retrieval models are usually trained and tested on one dataset, so how they perform zero-shot on other tasks and domains is largely unknown.
- I.2 Because building labeled data for every new domain is costly, deployments often rely on exactly this untested zero-shot transfer.
- I.3 Prior work shows large neural gains over BM25, but only when trained and tested on the same large in-domain dataset {C001-partial}.
- I.4 The two existing broad retrieval evaluations, MultiReQA and KILT, each cover one task type or lean on Wikipedia-scale corpora, leaving architecture-level zero-shot comparison untested {C020}.
- I.5 RQ1: how well, and via what mechanism, do systems from five architecture families generalize zero-shot relative to BM25?
- I.6 We built BEIR and evaluated 10 systems zero-shot on 18 datasets under one data format and metric {C021}.
- I.7 This paper contributes the benchmark and software, the comparative generalization/cost finding, and an annotation-bias case study {C021}{C019}{C018}.
- I.8 The paper proceeds by question: what's missing, what we built, what we compared, what we found for RQ1, a bias check (RQ2), and what it means.

## 2. Related Work
- RW.1 MultiReQA evaluates only sentence-level QA retrieval, mostly over small, Wikipedia-based corpora {C020}.
- RW.2 KILT spans more tasks but retrieves only from Wikipedia and does not treat retrieval as the primary evaluated skill {C020}.
- RW.3 Five retrieval architecture families are compared throughout this paper: lexical, sparse, dense, late-interaction, and re-ranking.

## 3. The BEIR Benchmark
- BM.1 Datasets were selected by four criteria: diverse tasks, diverse domains, sufficient difficulty, and diverse annotation strategies {C021}.
- BM.2 The result is 18 datasets across 9 tasks, standardized into one corpus/query/qrel format (Table 1) {C021}.
- BM.3 Scale and length vary enormously: corpora range 3.6k-15M documents, queries 3-192 words, documents 11-635 words, and only 8 of 19 datasets provide training data {C021}.
- BM.4 Measured word overlap between datasets is generally low, and concentrated mainly among datasets sharing a source domain {C022}.
- BM.5 A single metric, nDCG@10, was chosen so binary- and graded-relevance datasets can be compared on the same scale.

## 4. Retrieval Systems Compared
- SY.1 Ten systems, mostly trained on MS MARCO, represent the five families; bi-encoders, cross-encoders, and their negative-sampling strategies differ across them {C021}.
- SY.2 Lexical/sparse: BM25 needs no training; DeepCT and SPARTA learn term weights/representations on top of lexical matching; docT5query expands documents with generated queries.
- SY.3 Dense: DPR, ANCE and TAS-B are bi-encoders differing mainly in negative sampling and loss; GenQ further adapts TAS-B with synthetic in-domain queries.
- SY.4 Late-interaction/re-ranking: ColBERT keeps token-level vectors compared at query time; BM25+CE re-ranks BM25's top-100 with a cross-attention model.
- SY.5 All systems truncate documents to 512 word pieces, and efficiency is measured on one shared 1M-document sample and shared hardware, so comparisons are on equal footing on these dimensions.

## 5. Results: Zero-Shot Generalization Across Architectures
- R1.1 RQ1 asks whether the systems' zero-shot ranking against BM25 matches their in-domain ranking (Table 2).
- R1.2 BM25 trails neural systems in-domain by 7-18 points but is a strong zero-shot baseline, and no architecture wins on every dataset {C001}{C002}{C003}.
- R1.3 Re-ranking (+11% average, 16/18 datasets) and late-interaction (+2.5%, 9/18) generalize best, each failing mainly on the two tasks least like MS MARCO {C004}{C005}.
- R1.4 That generalization is not free: the best-generalizing systems are also the slowest (>350ms) and, for ColBERT, need the most memory to index {C015}{C016}.
- R1.5 Term-reweighting sparse methods and most dense bi-encoders underperform BM25 on average despite strong in-domain scores, with DPR generalizing worst overall {C006}{C008}.
- R1.6 Two exceptions buck their families' trend: docT5query (sparse) and TAS-B (dense) generalize comparatively well {C007}{C009}.
- R1.7 TAS-B still loses specifically to the weaker-on-average ANCE on two datasets, a gap tied to a document-length preference partly traced to the similarity function used in training {C011}{C012}{C013}.
- R1.8 Adapting TAS-B to the target domain with synthetic queries (GenQ) helps specialized domains but hurts broad/generic ones {C014}.
- R1.9 Across systems, robust generalization tracks the presence of cross-attention(-like) interaction more than embedding architecture alone, at a compute/latency cost, which answers RQ1 {C019}.

## 6. Annotation Selection Bias: A Case Study on TREC-COVID
- R2.1 If some BEIR test collections were pooled mainly from lexical systems, the RQ1 ranking on those datasets could be partly a measurement artifact rather than a true capability gap.
- R2.2 On TREC-COVID, each system's Hole@10 was measured, then the 980 previously-unjudged pairs were manually annotated, blind to which system had retrieved them.
- R2.3 Lexical systems' top hits were mostly already judged (2.8-6.4% missing); non-lexical systems' were not (up to 31.8% missing) {C017}.
- R2.4 After annotation, lexical scores barely moved while non-lexical scores rose substantially, e.g. ANCE by about 8 points and ColBERT by 5.8 {C018}.
- R2.5 This confirms lexical pooling bias measurably affected this comparison on this dataset without reversing the overall zero-shot ranking, which answers RQ2 {C018}.

## 7. Discussion
- D.1 RQ1's answer: in-domain accuracy does not predict zero-shot generalization, and the interaction mechanism between query and document representations matters more than the embedding family, at a real computational cost {C003}{C019}.
- D.2 RQ2's answer: annotation-pooling bias is real and measurable, but qualifies specific comparisons rather than overturning the overall ranking {C018}.
- D.3 Together, these findings argue for reporting zero-shot/cross-domain results as standard practice and for building future test collections with more diverse pooling {C019}{C018}.

## 8. Limitations
- Lim.1 The comparison covers English-only, mostly short-to-medium (<=512-wordpiece), text-only, single/dual-field retrieval {L001}{L002}{L003}{L004}.
- Lim.2 It compares generalist systems, without error bars, and without full compute reporting {L005}{L006}{L007}.
- Lim.3 The bias finding is measured on one dataset and argued, not measured, elsewhere in BEIR {L008}.

## 9. Conclusion
- C.1 BEIR gives one standardized way to measure zero-shot retrieval generalization across many tasks and domains {C021}.
- C.2 In-domain accuracy misleads about generalization, and part of the apparent weakness of non-lexical systems is itself a measurement artifact {C003}{C018}.
- C.3 Future work should extend coverage (multilingual, long-document, multi-field) and diversify test-collection pooling.

---

## Gate G2 self-reconstruction (read the skeleton alone, top to bottom, then answer):
Q1 problem: I.1. Q2 motivation: I.2. Q3 gap: I.4/RW.1-2. Q4 what was done: I.6/BM.1-5/SY.1-5.
Q5 why this method: BM.1,BM.5,SY.1 (selection criteria; one metric; matched training/truncation).
Q6 experiments: R1.1 (18-dataset zero-shot comparison) and R2.2 (TREC-COVID re-annotation case study).
Q7 strongest results: R1.3 (+11%/+2.5% generalizers) and R2.4 (bias-driven score changes).
Q8 what results establish: R1.9/D.1 and R2.5/D.2.
Q9 what they do NOT establish: Lim.1-3 (scope) plus R1.9's "associated with, not proven causal" framing.
Q10 primary contribution: I.7/C.1.
Q11 main limitations: Lim.1-3.
Q12 one-day-later memory: AB.3+AB.4 / D.1+D.2 (BM25 is robust; best generalizers are slow; in-domain success is not a generalization guarantee; part of the non-lexical gap is a measurement artifact).
All 12 answerable from the skeleton alone -> Gate G2 passes without returning to step 8.
