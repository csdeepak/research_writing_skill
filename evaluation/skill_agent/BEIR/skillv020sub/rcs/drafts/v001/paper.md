# BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

## Abstract

Retrieval models are typically trained on one dataset and evaluated on a held-out split of that same dataset, so how they behave once the domain or the task changes -- a zero-shot setting (evaluation without in-domain training data), common in practice -- is largely untested. Existing multi-dataset resources each relax only one kind of narrowness, task type or domain, but not both {C002}. We introduce BEIR (Benchmarking-IR), a benchmark of 18 datasets across 9 retrieval tasks selected to jointly maximize diversity of task, domain, difficulty, and annotation method {C001,C021}, and use it to evaluate 10 publicly available systems spanning five architecture families: lexical, sparse-neural, dense, late-interaction, and re-ranking {C022}. In-domain accuracy on the field's dominant training set does not predict zero-shot performance: the untrained lexical baseline BM25 trails the tested neural systems by 7-18 points in-domain, yet on average across the 18 datasets it outperforms six of the nine neural systems tested {C004,C006}. The two architectures that generalize best on average, re-ranking and late-interaction, also cost far more compute per query than the rest, roughly 450ms versus under 20ms {C007,C008}. A manual check on one dataset finds that dense systems' scores rise far more than lexical systems' scores once missing relevance judgments are added {C018}, suggesting the benchmark's own judgments can be biased toward the kind of system used to build them, which bounds how precisely these margins should be read {C019}.

## 1 Introduction

Retrieval is a first step in many natural-language-processing pipelines -- open-domain question answering, fact-checking, and duplicate-question detection all begin by finding a small set of relevant documents from a much larger collection. In practice, though, a retrieval model is usually trained on one dataset and tested on a held-out split of that same dataset.

Because collecting enough in-domain training data for every new domain or task is costly, retrieval systems are frequently applied zero-shot: evaluated on a dataset, domain, or task different from the one they were trained on. Before this work, it was unclear how well trained neural retrieval models perform outside the setting they were trained and tested on, and in particular how differently sparse and dense architectures generalize once that setting changes {C020}.

The closest existing resources for testing retrieval across multiple datasets each relax only one kind of narrowness. One evaluates a single task, answer retrieval, over mostly small, largely Wikipedia-based corpora; another spans several task types but retrieves exclusively from Wikipedia and treats retrieval as secondary to another task {C002}. Neither tests whether an architecture's zero-shot performance holds up when both the domain and the task type can change together.

We ask: which retrieval architectures generalize best, zero-shot, across diverse tasks and domains; at what computational cost; and how much does in-domain accuracy predict the answer {C003}?

We built BEIR by selecting 18 datasets across 9 retrieval tasks to jointly maximize diversity of task type, subject domain, task difficulty, and annotation method, reasoning that a benchmark narrower on any one of these axes would not test genuine generalization, and could let one technique's annotation artifacts dominate the comparison {C021}. We converted every dataset to one shared format and scored every system with one metric, then evaluated ten publicly available systems spanning five retrieval architecture families -- lexical, sparse-neural, dense, late-interaction, and re-ranking -- under this common protocol.

This paper makes three contributions. First, BEIR itself: a standardized, openly released benchmark spanning 18 datasets and 9 tasks, with a common data format and evaluation protocol, so that new datasets and new models can be added and compared directly {C001}. Second, an empirical answer to our research question: in-domain accuracy does not predict zero-shot performance, and the architectures that generalize best on average currently cost up to 20-30x more compute per query than the alternatives {C004,C006,C007}. Third, a case study showing that a benchmark's own relevance judgments are not automatically neutral across architecture families, which bounds how precisely the second contribution's margins should be read {C018,C019}. Section 2 places this work against the two closest prior resources; Section 3 describes BEIR's construction; Section 4 describes the systems we evaluate; Section 5 presents the results behind these three contributions in turn; Section 6 discusses what they mean; and Section 7 states the limitations that bound them.

## 2 Related Work

Five families of retrieval architecture are active in the field, and nearly all of them are built the same way: a BERT-family Transformer encoder (Devlin et al., 2019), fine-tuned on a single large training set. Lexical retrieval (Robertson and Zaragoza, 2009) needs no training at all, but is limited by the lexical gap: a query and a relevant document that share no words will not match (Berger et al., 2000). Sparse-neural methods keep an inverted index but let a network decide what goes into it, either by reweighting existing terms, as in DeepCT, or by predicting and appending new terms a document is likely to answer (Nogueira et al., 2019). Dense bi-encoders (Karpukhin et al., 2020; Xiong et al., 2020; Hofstatter et al., 2021) embed the query and the document independently and compare the two vectors, trading the lexical gap for a need to see enough training examples to learn a good embedding space. Late-interaction retrieval (Khattab and Zaharia, 2020) keeps one embedding per token instead of pooling to a single vector. Re-ranking (Nogueira and Cho, 2020), the most computationally expensive family, lets the query and a candidate document attend to each other jointly, but only for a short list that a cheaper first-stage retriever has already narrowed down.

Almost all of this work is trained and evaluated within one dataset, most often MS MARCO (Nguyen et al., 2016) or an open-domain question-answering set such as Natural Questions. The two prior resources that test retrieval across several datasets each relax only one dimension of that narrowness. MultiReQA (Guo et al., 2020) evaluates answer retrieval across eight question-answering datasets, but covers one task only, and five of the eight datasets are Wikipedia-based with comparatively small candidate pools {C002}. KILT (Petroni et al., 2020) spans five knowledge-intensive task types over eleven datasets, but retrieves exclusively from a single Wikipedia snapshot, and treats retrieval as a supporting step for another task rather than as the object of evaluation itself {C002}.

Among these two prior multi-dataset resources, neither tests domain shift and task-type shift jointly, or what either kind of shift costs computationally {C002}. Closing that gap, at the scale of 18 datasets and 9 tasks, is the contribution this paper makes.

## 3 Method: Building the BEIR Benchmark

We built BEIR to test retrieval architectures under conditions closer to real deployment than a single train/test split can provide. We selected datasets to jointly satisfy four criteria: they had to come from diverse retrieval tasks, from diverse subject domains, be difficult enough that no single existing approach had already solved them, and be built through diverse annotation strategies, since a benchmark whose datasets were all annotated the same way risks favoring whichever retrieval approach was used to build the annotation pool in the first place {C021}.

The result is 18 datasets across 9 tasks -- fact-checking, citation prediction, duplicate-question retrieval, argument retrieval, news retrieval, question answering, tweet retrieval, biomedical retrieval, and entity retrieval -- ranging from 3,600 to 15 million documents per corpus, average query lengths of 3 to 192 words, and average document lengths of 11 to 635 words {C001}. Only 8 of the 19 datasets we report on, including MS MARCO, provide any training data at all {C001}.

We score every system with a single metric, nDCG@10, across every task. We rejected the alternatives for concrete reasons: Precision and Recall ignore rank order entirely, and Mean Reciprocal Rank and Mean Average Precision assume binary relevance, which fails on the BEIR datasets that use graded relevance judgments; nDCG@10 handles both binary and graded judgments on the same scale, rewarding a relevant result more the higher it is ranked among the top 10 {C022}.

Every neural system in our comparison truncates each document to its first 512 word pieces, the input limit of the Transformer encoders involved (Section 7 returns to what this bounds). BM25 -- an untrained, keyword-matching baseline that indexes both title (where present) and passage text -- is scored on every dataset as a shared, zero-shot reference point throughout the rest of this paper.

## 4 Experimental Setup

We group the ten systems we evaluate into five architecture families. Lexical retrieval (BM25) matches query and document text directly through an inverted index and token-frequency statistics, with no training at all. Sparse-neural retrieval keeps an inverted index but lets a neural network change what goes into it: DeepCT and SPARTA reweight existing terms, and docT5query appends terms predicted from the queries a document is likely to answer. Dense retrieval (a "bi-encoder") embeds the query and the document independently as single vectors and compares them by similarity: DPR (Dense Passage Retrieval), ANCE, TAS-B, and GenQ are all bi-encoders that differ mainly in their training data, negative-sampling strategy, and loss. Late-interaction retrieval (ColBERT, "Contextualized Late Interaction over BERT") keeps a separate embedding per token and combines them with a lightweight interaction function instead of pooling to a single vector. Re-ranking (a "cross-encoder", instantiated here as BM25+CE) encodes the query and a candidate document jointly, so attention can cross between them, but only for a short list of candidates that a cheaper first-stage retriever -- BM25 -- has already narrowed down; the specific cross-encoder we use is a 6-layer MiniLM model (Wang et al., 2020) distilled from an ensemble of larger teacher models.

Nearly every system is a BERT-family encoder fine-tuned on MS MARCO. The one exception is DPR, whose released checkpoint was instead trained on four question-answering datasets rather than MS MARCO. GenQ is the other departure from a single shared recipe: it further fine-tunes TAS-B, separately for each target dataset, on up to 100,000 synthetic (query, document) pairs generated for that dataset's own documents.

Every comparison in this paper reflects a single evaluation run per system. Most of the ten systems are public, pre-trained checkpoints released without accessible training code, so retraining them repeatedly to estimate run-to-run variance was not feasible for most of the comparison {L006}; Section 7 returns to what this means for reading the results.

## 5 Results

### 5.1 In-domain accuracy does not predict zero-shot performance

Our first finding answers our third question directly. On the in-domain MS MARCO test set, BM25 trails the nine neural systems we evaluate by 7-18 points nDCG@10. Averaged across the 18 BEIR datasets, however, BM25 outperforms six of those same nine neural systems {C004}. This reversal is the paper's central result: a system's rank on the field's dominant single-dataset benchmark does not predict its rank once evaluation moves outside that dataset {C005}. Table 1 places both numbers, together with each system's inference cost, side by side {C007}.

Table 1. In-domain accuracy does not predict zero-shot generalization, and the best zero-shot generalizers cost the most compute. nDCG@10 on MS MARCO (in-domain, single run, no seed variance); average zero-shot nDCG@10 relative to BM25 across the 18 BEIR datasets (single run per system); GPU query latency on 1M sampled documents.

| Architecture family | System | In-domain MS MARCO (nDCG@10) | Avg. zero-shot vs. BM25 (18 datasets) | GPU latency/query |
|---|---|---|---|---|
| Lexical | BM25 | 0.228 | 0% (reference) | not applicable (untrained) |
| Sparse | DeepCT | 0.296 | -27.9% | not reported |
| Sparse | SPARTA | 0.351 | -20.3% | not reported |
| Sparse | docT5query | 0.338 | +1.6% | not reported |
| Dense | DPR | 0.177 | -47.7% | under 20 ms |
| Dense | ANCE | 0.388 | -7.4% | under 20 ms |
| Dense | TAS-B | 0.408 | -2.8% | under 20 ms |
| Dense | GenQ | 0.408 | -3.6% | under 20 ms |
| Late-interaction | ColBERT | 0.401 | +2.5% | not separately reported |
| Re-ranking | BM25+CE | 0.413 | +11% | ~450 ms |

Looking at the average column alone, only three systems beat BM25 zero-shot: the cross-encoder re-ranker BM25+CE (+11%), the late-interaction model ColBERT (+2.5%), and the sparse document-expansion method docT5query (+1.6%) {C006}. The other six -- two more sparse methods and four dense bi-encoders -- all average below BM25, by margins as large as 47.7% for DPR {C006}.

These systems are not equally expensive to run. Re-ranking and late-interaction, the two best zero-shot generalizers on average, both score candidate documents with a cross-attention-like computation, and pay for it at query time: BM25+CE takes roughly 450 ms per query on a GPU (350 ms on CPU), compared with under 20 ms for the dense retrievers we tested here -- a 20-30x difference {C007}. Sparse methods are fastest of all on CPU, at 20-25 ms.

### 5.2 The architecture families diverge for different reasons

The two sparse methods that split most sharply illustrate why an in-domain number can mislead. DeepCT and SPARTA both learn to reweight terms with a neural network and both do well in-domain, but both underperform BM25 on nearly all 18 datasets zero-shot {C009}. docT5query, also a sparse method, instead expands each document with predicted queries before indexing it; it outperforms BM25 on 11 of the 18 datasets {C009}. Dense bi-encoders, which replace lexical matching with a single learned vector per query and per document, show a related but even sharper split.

Dense bi-encoders perform well on some BEIR datasets but drop sharply on others with a large shift in domain (for example BioASQ) or task type (for example Touche-2020) relative to their training data {C010}. DPR, the only one of the ten systems trained solely on question-answering data rather than MS MARCO, generalizes worst of all ten systems: it averages 47.7% below BM25 across the 18 datasets {C010}.

The two families with the best average, re-ranking and late-interaction, are not universal winners either. BM25+CE outperforms BM25 on 16 of the 18 datasets, failing only on ArguAna and Touche-2020, two argument-retrieval tasks whose queries differ sharply from MS MARCO's question-style queries {C011}. ColBERT, despite a positive average, outperforms BM25 on just 9 of 18 datasets {C011}. Cross-attention, or a cross-attention-like interaction between query and document, appears to matter for this kind of generalization among the systems we tested; comparing query and document through a single fixed vector, as a bi-encoder does, is where the pattern breaks down most often {C011}.

### 5.3 Why the best dense model still loses on two datasets

Among the dense bi-encoders, TAS-B generalizes best, outperforming ANCE on 14 of the 18 datasets and DPR on 17 of 18 {C012}. The authors attribute this to TAS-B's training setup -- in-batch negatives combined with a Margin-MSE loss distilled from a cross-encoder/ColBERT ensemble -- though this explanation is speculative and not isolated by a dedicated experiment {C013}.

TAS-B's two losses to ANCE are better understood. On TREC-COVID it trails ANCE by 17.3 points nDCG@10, and on Touche-2020 by 7.8 points {C014}; these are the two datasets where the two models retrieve documents of the most different length (a median of 10 words for TAS-B versus 160 words for ANCE on TREC-COVID) {C014}. A separate, controlled comparison isolates one source of this length preference: two otherwise identical models trained on MS MARCO, differing only in whether they compare query and document vectors by cosine similarity or by dot product, reproduce the same pattern -- the cosine variant favors shorter documents and the dot-product variant favors longer ones, with a 15.3-point nDCG@10 gap between the two variants on TREC-COVID {C015}. This is consistent with a simple explanation the authors offer: dot-product similarity grows with a vector's length, so a longer document can score higher by that measure alone, while cosine similarity does not carry this effect {C015}. The similarity function used during training is therefore one identifiable source of a dense retriever's document-length preference, though a length preference is not itself an error: which document length is actually relevant to a query varies by dataset {C016}.

Domain adaptation is not uniformly beneficial either. GenQ, which further fine-tunes TAS-B on synthetic queries generated for each target dataset, outperforms TAS-B on specialized domains such as scientific publications, finance, and community question-answering, but underperforms it on broader, more generic domains such as Wikipedia-sourced datasets {C017}.

### 5.4 A case study: are the benchmark's own judgments neutral?

The comparisons above assume the benchmark's relevance judgments are themselves neutral across architecture families. We checked this assumption on one dataset. TREC-COVID's original judgments (Voorhees et al., 2021) were built by pooling the top results from many participating systems, most of them lexical; a document that no pooled system had retrieved was treated as irrelevant by default. We manually judged the 980 (query, document) pairs that our ten systems retrieved in their top 10 results but that the original pool had never scored -- each system's "holes" -- following the original task's guidelines and blinded to which system had retrieved each pair {C018}. Table 2 reports the resulting Hole@10 rates and rescored nDCG@10 values.

Table 2. TREC-COVID's original judgment pool undercounted non-lexical systems' top hits. Hole@10 is the share of a system's top-10 hits absent from the original judgments; nDCG@10 is shown before and after 980 missing judgments were added.

| System | Family | Hole@10 | nDCG@10 before | nDCG@10 after |
|---|---|---|---|---|
| docT5query | Sparse | 2.8% | 0.713 | 0.714 |
| BM25 | Lexical | 6.4% | 0.656 | 0.668 |
| SPARTA | Sparse | 12.4% | 0.538 | 0.624 |
| ColBERT | Late-interaction | 12.4% | 0.677 | 0.735 |
| ANCE | Dense | 14.4% | 0.654 | 0.735 |
| DeepCT | Sparse | 19.4% | 0.406 | 0.472 |
| DPR | Dense | 30.6% | 0.332 | 0.445 |
| TAS-B | Dense | 31.8% | 0.481 | 0.555 |

Hole@10 is far higher for dense systems (14.4% for ANCE, 31.8% for TAS-B) than for lexical or document-expansion systems (6.4% for BM25, 2.8% for docT5query) {C018}. After scoring the missing pairs, the lexical and document-expansion systems' scores barely moved (docT5query: 0.713 to 0.714), while the dense systems' scores rose sharply: ANCE's score rose from 0.654 to 0.735, which is 6.7 points above BM25's own re-scored value of 0.668, and ColBERT's own score rose by a comparable 5.8 points {C018}. The original judgment pool, in other words, was itself biased toward the kind of system used to build it {C019}.

This case study does not overturn our main comparison -- lexical retrieval's zero-shot robustness is also visible across the other 17 datasets, which were not re-annotated -- but it means the exact size of the gap between lexical and non-lexical systems on TREC-COVID, and possibly on other similarly built collections, should be read as an upper bound on the true difference in retrieval quality, not as an exact one {C019}.

## 6 Discussion

Returning to our first question: does in-domain accuracy predict zero-shot performance? Our results say no. A system's rank on MS MARCO, the field's dominant single-dataset benchmark, does not carry over to its rank once evaluation moves to new tasks and domains, and an untrained lexical baseline remains a meaningful reference point that most of the trained neural systems we tested do not clear on average {C005}.

Our second question was about cost as well as accuracy. Right now, the two families with the best average zero-shot accuracy -- re-ranking and late-interaction -- also require the most computation per query, while the cheaper dense and sparse families generalize less reliably and behave unevenly depending on training data, negative-sampling, and domain-adaptation choices we can point to individually but not yet predict in general {C008}. Reporting accuracy alone therefore hides a real engineering trade-off: a system chosen purely from a zero-shot leaderboard could be 20-30 times slower than an alternative that trails it by only a few points {C008}.

Our third question, raised by the TREC-COVID case study, is how much to trust the exact size of these margins. Because that collection's judgments were pooled mostly from lexical systems, at least part of the measured gap between lexical and non-lexical retrieval on it is an annotation artifact, not a pure difference in retrieval quality {C019}. We did not re-run this check on the other 17 datasets, so we cannot say how much of BM25's overall zero-shot robustness reflects the same effect elsewhere; we can only say the possibility is now demonstrated on one collection, not merely hypothesized {C019}.

A later resource paper built on this benchmark makes a related point about how we summarized our own results: collapsing scores from 18 heterogeneous datasets into one average, as in Table 1, is difficult to interpret on its own, and per-dataset effect-size analyses are offered as a complement (Kamalloo et al., 2024).

Taken together, these three answers point to the same practical recommendation: compare retrieval architectures on broad, heterogeneous suites rather than one dataset, report accuracy alongside computational cost, and treat any single collection's absolute numbers as bounded by how that collection's judgments were built.

## 7 Limitations

We state five boundaries on this benchmark directly. BEIR currently covers English only {L001}. Its documents are mostly a few hundred words long, and every neural system we test truncates input to 512 word pieces, so long-document retrieval is not represented {L002}. We evaluate pure text matching only, without auxiliary ranking signals such as recency, authority, or click-through data that real deployed systems often use {L003}. We retrieve over at most two fields, typically title and body, even though real documents such as scientific papers have several {L004}. And because we compare generalist systems, a specialized model built for one task -- which we did not evaluate here -- can still outperform every system in this comparison on that one task, since it is not required to generalize across the others {L005}.

A further limitation concerns how sure we can be about the exact numbers we report. No comparison in this paper carries a variance estimate or significance test, because retraining most of the ten public checkpoints repeatedly to obtain multiple seeds was not feasible {L006}. A margin as large as the 47.7% gap between DPR and BM25 is unlikely to be an artifact of a single run, but smaller margins, such as the 1.6-2.8-point gaps that separate several systems near BM25's own average, should be read as suggestive rather than exact {L006}.

**Additional caveats.** The annotation-bias case study in Section 5.4 covers one of the eighteen datasets, and the missing judgments were added by us, not by independent annotators, albeit while blinded to which system had retrieved each one; how far the same bias extends to the other 17 datasets is not established {L007}. Separately, our architecture comparison is a snapshot of the 10 publicly available systems we could evaluate at the time; the software we released alongside this paper has since been extended to additional model integrations that are not part of the comparison reported here {L008}.

## 8 Conclusion

We built BEIR to find out which retrieval architectures actually generalize once evaluation leaves the single dataset most of the field trains and tests on, and at what cost. The answer is that in-domain accuracy is a poor guide to that question: a simple, untrained lexical baseline remains competitive with, and on average ahead of, most of the trained neural systems we tested, and the two architecture families that do generalize best currently require up to 20-30x more computation per query {C005,C008}.

The main boundary on this finding is that it rests on 18 English datasets evaluated once each, and on a bias check performed on only one of them, so we do not yet know how far either the architecture ranking or the annotation-bias effect extends beyond what we tested here {C019,L007}. Building retrieval test collections with fairer, multi-strategy annotation pooling, and extending this kind of benchmark to more languages and to longer documents, are the most direct next steps.

## References

Berger, A., Caruana, R., Cohn, D., Freitag, D., and Mittal, V. (2000). Bridging the lexical chasm: statistical approaches to answer-finding. In *Proceedings of the 23rd Annual International ACM SIGIR Conference on Research and Development in Information Retrieval*, pages 192-199.

Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. In *Proceedings of NAACL-HLT 2019*, Volume 1, pages 4171-4186.

Guo, M., Yang, Y., Cer, D., Shen, Q., and Constant, N. (2020). MultiReQA: A Cross-Domain Evaluation for Retrieval Question Answering Models.

Hofstatter, S., Lin, S.-C., Yang, J.-H., Lin, J., and Hanbury, A. (2021). Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling. In *Proceedings of SIGIR 2021*.

Kamalloo, E., Thakur, N., Lassance, C., Ma, X., Yang, J.-H., and Lin, J. (2024). Resources for Brewing BEIR: Reproducible Reference Models and Statistical Analyses. In *Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval*, pages 1431-1440. https://doi.org/10.1145/3626772.3657862

Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., and Yih, W. (2020). Dense Passage Retrieval for Open-Domain Question Answering. In *Proceedings of EMNLP 2020*, pages 6769-6781.

Khattab, O. and Zaharia, M. (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. In *Proceedings of the 43rd International ACM SIGIR Conference*, pages 39-48.

Nguyen, T., Rosenberg, M., Song, X., Gao, J., Tiwary, S., Majumder, R., and Deng, L. (2016). MS MARCO: A Human Generated MAchine Reading COmprehension Dataset.

Nogueira, R. and Cho, K. (2020). Passage Re-ranking with BERT. arXiv preprint arXiv:1901.04085.

Nogueira, R., Yang, W., Lin, J., and Cho, K. (2019). Document Expansion by Query Prediction.

Petroni, F., Piktus, A., Fan, A., Lewis, P., Yazdani, M., De Cao, N., Thorne, J., Jernite, Y., Plachouras, V., Rocktaschel, T., and Riedel, S. (2020). KILT: a Benchmark for Knowledge Intensive Language Tasks.

Robertson, S. and Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval*, 3(4):333-389.

Voorhees, E., Alam, T., Bedrick, S., Demner-Fushman, D., Hersh, W. R., Lo, K., Roberts, K., Soboroff, I., and Wang, L. L. (2021). TREC-COVID: Constructing a Pandemic Information Retrieval Test Collection. *SIGIR Forum*, 54(1).

Wang, W., Wei, F., Dong, L., Bao, H., Yang, N., and Zhou, M. (2020). MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers. In *Advances in Neural Information Processing Systems*, volume 33, pages 5776-5788.

Xiong, L., Xiong, C., Li, Y., Tang, K.-F., Liu, J., Bennett, P., Ahmed, J., and Overwijk, A. (2020). Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval.
