# BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

**Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, Iryna Gurevych**  
Ubiquitous Knowledge Processing Lab (UKP-TUDA), Technische Universität Darmstadt

---

## Abstract

Neural models for information retrieval (IR)—the task of finding relevant documents for a user query—have historically been evaluated in narrow, single-domain settings, leaving their generalization capability largely unknown. This paper presents BEIR (Benchmarking IR), a heterogeneous zero-shot evaluation benchmark comprising 18 datasets drawn from 9 distinct retrieval tasks and domains. BEIR is designed to measure how well a model trained on one distribution transfers to entirely unseen domains and task types, without any additional fine-tuning. We evaluate 10 state-of-the-art retrieval systems spanning five architectural families—lexical, sparse, dense, late-interaction, and re-ranking—and reveal that the classical BM25 term-matching algorithm remains a surprisingly strong zero-shot baseline. Models that substantially outperform BM25 on the in-domain training dataset often underperform it on the diverse held-out tasks. Re-ranking and late-interaction architectures generalize best but incur high inference costs. We further expose an annotation selection bias present in many existing datasets and quantify its unfair penalization of non-lexical methods. BEIR is publicly available as an open-source Python package, providing a unified framework for fair, broad evaluation of retrieval systems.

---

## 1. Introduction

Retrieving relevant text from a large corpus is a foundational capability in applied machine learning: it underlies open-domain question answering, fact verification, duplicate detection, and many other downstream tasks (Thorne et al., 2018; Chen et al., 2017). For decades, lexical approaches such as TF-IDF and BM25—which match tokens between a query and a document—dominated this space (Robertson and Zaragoza, 2009). These methods are simple and fast but suffer from the *lexical gap*: they cannot match semantically related terms unless they share surface form (Berger et al., 2000).

Pre-trained Transformer models such as BERT (Devlin et al., 2018) introduced a new wave of neural retrieval systems. These models can be applied to retrieval in several fundamentally different ways, and many achieve large gains over BM25 on standard benchmarks. However, those benchmarks tend to evaluate within a single domain (e.g., Wikipedia passages) or task type (e.g., open-domain question answering). Training and evaluation data come from the same distribution, and a model that looks impressive on its home dataset may generalize poorly elsewhere.

This paper asks: *How well do modern neural retrieval models generalize to unseen domains and task types without any task-specific training?* Existing multi-task benchmarks such as MultiReQA (Guo et al., 2020) and KILT (Petroni et al., 2020) do not address this question directly—MultiReQA restricts itself to one task type and small corpora, while KILT treats retrieval as a sub-component rather than the primary objective, and both rely primarily on Wikipedia.

To fill this gap, we introduce BEIR (Benchmarking-IR), a heterogeneous benchmark designed for *zero-shot* retrieval evaluation. Its key properties are:

- **18 datasets from 9 retrieval task types**, including fact checking, biomedical information retrieval, entity retrieval, argument retrieval, duplicate question detection, and more.
- **Diverse domains**: corpora range from broad Wikipedia articles to specialized scientific publications, financial discussion forums, news archives, and Twitter feeds.
- **Diverse annotation strategies**: different datasets were labeled by crowd workers, domain experts, and community feedback, which partially mitigates correlated biases.
- **Zero-shot evaluation protocol**: all models are evaluated on benchmark datasets without any exposure to their training labels. The majority of models are trained on MS MARCO (Nguyen et al., 2016), a large-scale web search passage dataset.
- **Open-source framework**: a Python package (`pip install beir`) provides standardized data loading, model wrappers, and evaluation metrics, enabling researchers to plug in new models or datasets with minimal effort.

Our evaluation of ten diverse retrieval systems reveals that in-domain performance is a poor predictor of zero-shot generalization, that simple BM25 remains a robust baseline that many neural models fail to surpass, and that annotation biases in existing datasets systematically disadvantage non-lexical models. We hope BEIR accelerates progress toward more robust, generalizable retrieval systems.

---

## 2. Background: Architectures for Text Retrieval

To make this paper self-contained for readers outside information retrieval, we briefly describe the five architectural families evaluated in BEIR.

**Lexical retrieval** methods treat both queries and documents as bags of words and rank documents by weighted term overlap. BM25 (Robertson and Zaragoza, 2009) is the standard representative: it assigns weights based on term frequency (TF) and inverse document frequency (IDF), and applies length normalization. BM25 is fast and requires no training, but cannot match documents that express the same concept in different words.

**Sparse retrieval** methods use neural networks to augment or replace the term weights used in lexical retrieval, while retaining a sparse, inverted-index-compatible representation. Examples include DeepCT (Dai and Callan, 2020), which uses BERT to predict per-term relevance weights, and DocT5query (Nogueira et al., 2019), which uses a T5 model to generate synthetic queries and append them to each document before BM25 indexing. SPARTA (Zhao et al., 2021) instead produces a high-dimensional sparse vector from BERT token-level embeddings.

**Dense retrieval** models use a bi-encoder architecture: two separate Transformer encoders map a query and a document each to a single dense vector in a shared embedding space, and retrieval is performed by maximum inner product or cosine search. Because document vectors can be precomputed, dense retrieval scales to millions of documents with approximate nearest-neighbor (ANN) search. Representatives include DPR (Karpukhin et al., 2020), trained on four question-answering datasets; ANCE (Xiong et al., 2020), which mines hard negatives from an ANN index during training; and TAS-B (Hofstätter et al., 2021a), which trains with knowledge distillation from a cross-encoder teacher and balanced topic-aware sampling.

**Late-interaction** models, exemplified by ColBERT (Khattab and Zaharia, 2020), encode queries and documents into *sets* of token-level dense vectors rather than a single vector. At retrieval time, relevance is computed by a MaxSim operation: for each query token, the maximum dot-product similarity over all document tokens is summed. This operation mimics full cross-attention at much lower cost. Document token vectors can be precomputed, though storage requirements are substantially larger than for bi-encoders.

**Re-ranking** approaches use a two-stage pipeline: a fast first-stage retriever (typically BM25) retrieves a candidate set (e.g., top 100 documents), and a more expressive cross-encoder *re-ranks* those candidates by jointly attending to query and document tokens. Cross-encoders, which are full BERT-style models that take the query-document pair as a single input, are much more accurate than bi-encoders but cannot scale to retrieve from millions of documents directly. The re-ranking model evaluated here (BM25+CE) uses a 6-layer MiniLM (Wang et al., 2020) cross-encoder trained on MS MARCO via knowledge distillation from larger BERT models (Hofstätter et al., 2021b).

The key generalization question is whether models trained on MS MARCO—a web-search dataset with short factoid queries and Wikipedia-sourced passages—can transfer their learned representations to the very different query types, document types, and domain vocabularies encountered in BEIR's held-out tasks.

---

## 3. The BEIR Benchmark

### 3.1 Dataset Selection Criteria

BEIR was assembled according to four guiding principles:

1. **Diverse tasks**: retrieval tasks vary in the nature of the query (a short keyword, a full sentence, a long argument) and the expected document (a tweet, a news article, a PubMed abstract). Covering a wide range avoids over-fitting the benchmark to a single input format.

2. **Diverse domains**: both broad (Wikipedia, news) and specialized (COVID-19 publications, financial forums, Twitter) domains are included to stress-test domain transfer.

3. **Sufficient difficulty**: tasks that can be trivially solved by any method are not informative for model comparison. Datasets were selected based on evidence from prior literature that they remain challenging.

4. **Diverse annotation strategies**: evaluation datasets are known to carry annotation biases (discussed in Section 5). By including datasets with different labeling procedures—crowd workers, domain experts, community votes—BEIR partially distributes those biases rather than compounding them.

### 3.2 The 18 Datasets

BEIR includes 18 English datasets spanning 9 task types. Table 1 summarizes key statistics.

| Task | Dataset | Corpus Size | # Test Queries | Avg. Docs/Query |
|---|---|---|---|---|
| Bio-Medical IR | TREC-COVID | 171K | 50 | 493.5 |
| Bio-Medical IR | NFCorpus | 3.6K | 323 | 38.2 |
| Bio-Medical IR | BioASQ | 14.9M | 500 | 4.7 |
| Question Answering | NQ | 2.68M | 3,452 | 1.2 |
| Question Answering | HotpotQA | 5.23M | 7,405 | 2.0 |
| Question Answering | FiQA-2018 | 57K | 648 | 2.6 |
| Tweet Retrieval | Signal-1M | 2.87M | 97 | 19.6 |
| News Retrieval | TREC-NEWS | 595K | 57 | 19.6 |
| News Retrieval | Robust04 | 528K | 249 | 69.9 |
| Argument Retrieval | ArguAna | 8.7K | 1,406 | 1.0 |
| Argument Retrieval | Touché-2020 | 383K | 49 | 19.0 |
| Dup. Question | CQADupStack | 457K | 13,145 | 1.4 |
| Dup. Question | Quora | 523K | 10,000 | 1.6 |
| Entity Retrieval | DBPedia | 4.64M | 400 | 38.2 |
| Citation Prediction | SCIDOCS | 25K | 1,000 | 4.9 |
| Fact Checking | FEVER | 5.42M | 6,666 | 1.2 |
| Fact Checking | Climate-FEVER | 5.42M | 1,535 | 3.0 |
| Fact Checking | SciFact | 5.2K | 300 | 1.1 |

*Table 1: Dataset statistics for the BEIR benchmark. Corpus Size = number of indexed documents. Avg. Docs/Query = average number of labeled relevant documents per query.*

The datasets span extremes in every dimension: corpora range from 3,633 documents (NFCorpus) to 14.9 million (BioASQ); average query length ranges from 3.3 words (NFCorpus queries) to 193 words (ArguAna, where the query is itself a full argument); and average relevant documents per query range from 1.0 (ArguAna) to 493.5 (TREC-COVID). Only 8 of the 18 datasets have labeled training data, underscoring the practical importance of zero-shot retrieval.

### 3.3 Domain Diversity Analysis

To verify that datasets are genuinely diverse—i.e., that good performance on one does not trivially predict performance on another—the authors compute pairwise weighted Jaccard similarity (Ioffe, 2010) over unigram word frequencies between all dataset pairs. Two datasets with high vocabulary overlap would suggest similar distributions.

Most dataset pairs show low overlap (scores below 0.3), confirming that the benchmark poses genuine domain transfer challenges. Exceptions are natural: HotpotQA and DBPedia both draw from Wikipedia and share substantial vocabulary (overlap 0.89); FEVER also draws from Wikipedia (overlap ~0.78–0.80 with HotpotQA and DBPedia). Biomedical datasets cluster with each other (TREC-COVID and BioASQ at 0.51), while Twitter-based Signal-1M is distant from all others.

### 3.4 Evaluation Metric

The authors adopt nDCG@10 (Normalized Discounted Cumulative Gain at rank 10) as the primary metric across all datasets. Unlike precision or recall, nDCG is *rank-aware* (it rewards systems that place the most relevant documents higher) and handles *graded relevance* (some datasets use 3- or 5-level relevance scales rather than binary labels). Wang et al. (2013) provide a theoretical justification for nDCG's desirable properties. Computing nDCG@10 for all 18 datasets via the pytrec_eval interface (Van Gysel and de Rijke, 2018) provides a consistent, comparable signal.

---

## 4. Experimental Setup

All models are evaluated using publicly available pre-trained checkpoints with no task-specific fine-tuning on BEIR datasets. The dominant training source is MS MARCO (Nguyen et al., 2016)—a passage ranking dataset with 532,761 training query-passage pairs drawn from Bing web search—except for DPR, which is trained on four open-domain QA datasets. Document inputs are truncated to 512 word pieces for all Transformer-based models.

The ten evaluated models are:

- **Lexical**: BM25 (Anserini with default Lucene parameters k=0.9, b=0.4) (Robertson and Zaragoza, 2009)
- **Sparse**: DeepCT (Dai and Callan, 2020), SPARTA (Zhao et al., 2021), DocT5query (Nogueira et al., 2019)
- **Dense**: DPR (Karpukhin et al., 2020), ANCE (Xiong et al., 2020), TAS-B (Hofstätter et al., 2021a), GenQ (a domain-adaptive variant that fine-tunes TAS-B on synthetically generated queries for each target dataset)
- **Late-interaction**: ColBERT (Khattab and Zaharia, 2020)
- **Re-ranking**: BM25 + MiniLM cross-encoder (BM25+CE) (Wang et al., 2020)

GenQ deserves special mention: it generates 5 synthetic queries per document using a T5 model (Raffel et al., 2020) and continues fine-tuning TAS-B on the (synthetic query, document) pairs. Because it creates a task-specific model from unlabeled document text, it represents an unsupervised domain adaptation approach. Corpora are capped at 100K documents for GenQ due to computational constraints.

---

## 5. Results and Analysis

Table 2 reports nDCG@10 for all models on all datasets. The bottom row "Avg. Performance vs. BM25" summarizes how each model compares to the BM25 baseline on average across the 18 zero-shot datasets.

| Dataset | BM25 | DeepCT | SPARTA | DocT5q | DPR | ANCE | TAS-B | GenQ | ColBERT | BM25+CE |
|---|---|---|---|---|---|---|---|---|---|---|
| MS MARCO† | 0.228 | 0.296 | 0.351 | 0.338 | 0.177 | 0.388 | 0.408 | 0.408 | 0.401 | 0.413 |
| TREC-COVID | 0.656 | 0.406 | 0.538 | 0.713 | 0.332 | 0.654 | 0.481 | 0.619 | 0.677 | 0.757 |
| NFCorpus | 0.325 | 0.283 | 0.301 | 0.328 | 0.189 | 0.237 | 0.319 | 0.319 | 0.305 | 0.350 |
| BioASQ | 0.465 | 0.407 | 0.351 | 0.431 | 0.127 | 0.306 | 0.383 | 0.398 | 0.474 | 0.523 |
| NQ | 0.329 | 0.188 | 0.398 | 0.399 | 0.474 | 0.446 | 0.463 | 0.358 | 0.524 | 0.533 |
| HotpotQA | 0.603 | 0.503 | 0.492 | 0.580 | 0.391 | 0.456 | 0.584 | 0.534 | 0.593 | 0.707 |
| FiQA-2018 | 0.236 | 0.191 | 0.198 | 0.291 | 0.112 | 0.295 | 0.300 | 0.308 | 0.317 | 0.347 |
| Signal-1M | 0.330 | 0.269 | 0.252 | 0.307 | 0.155 | 0.249 | 0.289 | 0.281 | 0.274 | 0.338 |
| TREC-NEWS | 0.398 | 0.220 | 0.258 | 0.420 | 0.161 | 0.382 | 0.377 | 0.396 | 0.393 | 0.431 |
| Robust04 | 0.408 | 0.287 | 0.276 | 0.437 | 0.252 | 0.392 | 0.427 | 0.362 | 0.391 | 0.475 |
| ArguAna | 0.315 | 0.309 | 0.279 | 0.349 | 0.175 | 0.415 | 0.429 | 0.493 | 0.233 | 0.311 |
| Touché-2020 | 0.367 | 0.156 | 0.175 | 0.347 | 0.131 | 0.240 | 0.162 | 0.182 | 0.202 | 0.271 |
| CQADupStack | 0.299 | 0.268 | 0.257 | 0.325 | 0.153 | 0.296 | 0.314 | 0.347 | 0.350 | 0.370 |
| Quora | 0.789 | 0.691 | 0.630 | 0.802 | 0.248 | 0.852 | 0.835 | 0.830 | 0.854 | 0.825 |
| DBPedia | 0.313 | 0.177 | 0.314 | 0.331 | 0.263 | 0.281 | 0.384 | 0.328 | 0.392 | 0.409 |
| SCIDOCS | 0.158 | 0.124 | 0.126 | 0.162 | 0.077 | 0.122 | 0.149 | 0.143 | 0.145 | 0.166 |
| FEVER | 0.753 | 0.353 | 0.596 | 0.714 | 0.562 | 0.669 | 0.700 | 0.669 | 0.771 | 0.819 |
| Climate-FEVER | 0.213 | 0.066 | 0.082 | 0.201 | 0.148 | 0.198 | 0.228 | 0.175 | 0.184 | 0.253 |
| SciFact | 0.665 | 0.630 | 0.582 | 0.675 | 0.318 | 0.507 | 0.643 | 0.644 | 0.671 | 0.688 |
| **Avg. vs. BM25** | — | −27.9% | −20.3% | +1.6% | −47.7% | −7.4% | −2.8% | −3.6% | +2.5% | **+11%** |

*Table 2: nDCG@10 on the BEIR benchmark. † MS MARCO is the in-domain training dataset and is excluded from the zero-shot average. Best score per dataset in bold; second best underlined.*

Seven findings emerge from this evaluation:

**1. In-domain performance does not predict zero-shot generalization.** On MS MARCO, neural models outperform BM25 by 7–18 points in nDCG@10. Yet on the zero-shot BEIR datasets, BM25 outperforms most of them on average. DPR, despite being trained on four QA datasets, underperforms BM25 by nearly 48% on average—illustrating that even multi-task training does not guarantee broad generalization when the task types and domains are sufficiently diverse.

**2. Sparse neural models diverge in behavior.** DeepCT and SPARTA, which use Transformers to reweight or replace term frequencies, underperform BM25 on almost every BEIR dataset despite strong in-domain results. Their learned term weights are tied to MS MARCO's vocabulary distribution and fail to transfer. By contrast, DocT5query appends synthetically generated queries to documents, effectively enriching the lexical coverage of the index. This bridges the lexical gap: DocT5query outperforms BM25 on 11 of 18 datasets and is competitive on the rest, achieving +1.6% on average—the only sparse model with positive net performance.

**3. Dense retrievers show task- and domain-dependent generalization failures.** Dense models map queries and documents to fixed-dimensional vectors. In domains or task types far removed from MS MARCO's web-search format, such as BioASQ (biomedical) or Touché-2020 (argument retrieval), they underperform BM25 substantially. TAS-B achieves the best average among dense models (−2.8% vs. BM25) thanks to its strong training objective combining pairwise margin-MSE distillation from an ensemble of teachers with in-batch negatives. ANCE (−7.4%) and DPR (−47.7%) lag behind, with DPR suffering most due to its narrower training distribution.

**4. Re-ranking and late-interaction models generalize best.** BM25+CE outperforms BM25 on 16 of 18 datasets and achieves +11% on average. The two failures are ArguAna and Touché-2020—both involve retrieving argumentative texts, which are maximally different from the web-search passage format of MS MARCO. ColBERT, using token-level late-interaction, also generalizes well (+2.5%), outperforming BM25 on 9 of 18 datasets. Both methods employ cross-attention-like operations that appear to provide robustness to distribution shift.

**5. Domain adaptation with synthetic data partially helps.** GenQ—which fine-tunes TAS-B on unlabeled target-domain documents by generating synthetic queries—improves over TAS-B on specialized domains (scientific publications, finance, StackExchange) but regresses on broad domains like Wikipedia. The net effect is a small improvement (−3.6% vs. −2.8% for TAS-B), suggesting that synthetic domain adaptation is task-sensitive.

**6. Dense models exhibit retrieval length bias.** TAS-B and ANCE retrieve documents of systematically different lengths for the same query. On TREC-COVID, TAS-B retrieves documents with a median length of approximately 10 words, while ANCE retrieves documents with a median of approximately 160 words. This difference is traced to the similarity function: cosine similarity normalizes by vector magnitude and becomes agnostic to text length, while dot-product accumulates contributions proportionally to document length. For TREC-COVID, many short documents are publication titles with empty abstracts—these receive inflated cosine similarity scores. The consequence is a 17.3-point nDCG@10 gap between ANCE and TAS-B on this dataset, despite TAS-B being generally stronger. Researchers should be aware that their choice of similarity function implicitly induces a length bias that interacts with the distribution of relevant documents in the target corpus.

**7. No single architecture dominates across all tasks.** Figure 3 of the original paper makes this concrete: BM25+CE wins on the most datasets, but every model (except DPR) has at least one dataset where it ranks near the top. This heterogeneity confirms that a multi-dataset benchmark is essential for understanding model strengths and weaknesses.

---

## 6. Efficiency Analysis

Beyond accuracy, practical deployment requires considering inference latency and memory footprint. Using 1 million randomly sampled DBPedia documents as the test corpus, the authors measure retrieval latency per query and index size.

| Architecture | Model | GPU Latency | CPU Latency | Index Size |
|---|---|---|---|---|
| Re-ranking | BM25+CE | 450 ms | 6,100 ms | 0.4 GB |
| Late-interaction | ColBERT | 350 ms | — | 20 GB |
| Sparse | DocT5query | 14 ms | 20 ms | 0.4 GB |
| Lexical | BM25 | 14 ms | 20 ms | 0.4 GB |
| Dense | TAS-B | 14 ms | 125 ms | 3 GB |
| Dense | ANCE / GenQ | ~19 ms | ~230 ms | 3 GB |
| Sparse | SPARTA | 20 ms | 25 ms | 12 GB |
| Sparse | DeepCT | — | 25 ms | 0.4 GB |
| Dense | DPR | 19 ms | 230 ms | 3 GB |

*Table 3: Approximate retrieval latency and index sizes for 1 million documents (DBPedia). Rankings ordered by zero-shot BEIR performance.*

The results reveal a sharp accuracy-efficiency tradeoff. BM25+CE and ColBERT achieve the best zero-shot generalization but are 20–30× slower than dense models on GPU and require substantially more memory: ColBERT's index of 20 GB for 1 million documents would reach approximately 900 GB for BioASQ's 15 million documents, versus only 18 GB for BM25. Dense retrievers occupy a middle ground—3 GB for 1 million documents at 14–20 ms GPU latency—while offering moderate generalization. Sparse models (BM25, DocT5query, DeepCT) offer the smallest footprints and fastest CPU speeds at the cost of limited semantic generalization.

This profile suggests that practical deployment choices must balance accuracy requirements against latency budgets and hardware constraints, and that no single architecture currently satisfies all criteria simultaneously.

---

## 7. Annotation Selection Bias

Beyond the architectural comparison, a deeper issue affects the validity of any retrieval benchmark: *annotation selection bias*. Creating relevance labels for millions of (query, document) pairs is infeasible; instead, candidate documents are first retrieved by one or more systems and then labeled by annotators. Crucially, documents *not* retrieved for annotation are assumed irrelevant—an assumption that is wrong whenever a new retrieval system surfaces different documents.

If the candidate pool was built primarily with lexical methods (as is common in older datasets), then dense retrieval systems may surface highly relevant documents that were never seen by annotators, causing their scores to be artificially depressed. The authors measure this via the *Hole@10* metric: the fraction of each system's top-10 results that were never annotated.

Even on TREC-COVID—which used a pooling strategy aggregating results from many participating systems—the authors find large discrepancies:

| Model | Hole@10 | nDCG@10 (original) | nDCG@10 (re-annotated) |
|---|---|---|---|
| BM25 | 6.4% | 0.656 | 0.668 |
| DocT5query | 2.8% | 0.713 | 0.714 |
| DeepCT | 19.4% | 0.406 | 0.472 |
| SPARTA | 12.4% | 0.538 | 0.624 |
| DPR | 30.6% | 0.332 | 0.445 |
| ANCE | 14.4% | 0.654 | 0.735 |
| TAS-B | 31.8% | 0.481 | 0.555 |
| ColBERT | 12.4% | 0.677 | 0.735 |
| BM25+CE | 1.6% | 0.757 | 0.760 |

*Table 4: Hole@10 annotation bias analysis on TREC-COVID. nDCG@10 before and after manual annotation of 980 missing (query, document) pairs.*

BM25 and DocT5query—both lexical approaches—have Hole@10 rates of 6.4% and 2.8%, meaning their top-10 lists are almost entirely covered by prior annotations. Their scores barely change after re-annotation (+1.2 and +0.1 points).

Dense models tell a very different story. ANCE has a 14.4% Hole@10 rate, and its score jumps from 0.654 to 0.735 after annotation—a gain of 8.1 points, placing it 6.7 points *above* BM25 rather than slightly below. TAS-B (Hole@10 = 31.8%) improves from 0.481 to 0.555. DPR (Hole@10 = 30.6%) improves from 0.332 to 0.445. The cross-encoder re-ranker BM25+CE has only 1.6% holes (because it re-ranks BM25 candidates, which are already covered), so its score changes minimally.

The takeaway is significant: even a benchmark designed to be unbiased, built from a competitive pool of heterogeneous systems, still retains substantial lexical bias that can misrepresent model quality by nearly 10 nDCG points. Benchmark designers should use pooling strategies that deliberately include non-lexical systems, and users of BEIR scores should be aware that reported numbers likely underestimate the true capability of semantic (dense and sparse neural) retrievers.

---

## 8. Limitations

The authors explicitly acknowledge several limitations of BEIR:

1. **Language**: all 18 datasets are English. Cross-lingual and multilingual retrieval remain important open problems not covered by the benchmark.
2. **Document length**: most corpora contain documents of a few hundred words. Long-document retrieval (entire books, full-length articles) is not covered and would require different architectural choices given Transformer length limits.
3. **Single-modality text**: BEIR focuses on pure text retrieval. Real-world search systems often incorporate click-through rates, document recency, authority scores, and other signals not captured here.
4. **Multi-field retrieval**: documents with multiple fields (title, abstract, body, author list) are reduced to one or two fields; richer multi-field modeling is not evaluated.
5. **Task-specific models**: specialized models optimized for a single domain (e.g., a biomedical-specific retriever) can outperform the general models in BEIR, but they are not the target of this zero-shot benchmark.

---

## 9. Conclusions

BEIR establishes a principled, large-scale benchmark for measuring the zero-shot generalization of text retrieval systems. Its key contributions are:

- **A curated suite of 18 diverse datasets** spanning 9 task types and multiple domains, with a unified data format and evaluation protocol.
- **Empirical evidence** that in-domain neural retrieval performance does not predict out-of-distribution performance, and that BM25 remains a strong zero-shot baseline that many neural models fail to beat.
- **A systematic analysis of annotation selection bias**, demonstrating that lexical biases in existing datasets can suppress dense retrieval scores by up to 8 nDCG points on a single dataset.
- **An open-source evaluation framework** that lowers the barrier to running broad multi-dataset evaluations.

The findings point to important directions for the broader ML community: training objectives and architectures for retrieval need to prioritize robustness to domain shift, not just peak in-domain performance; late-interaction and cross-attention-based mechanisms appear to transfer better than fixed-vector representations; and the community needs improved annotation methodologies that pool candidates from diverse retrieval paradigms to avoid penalizing models that retrieve relevant but previously unseen documents.

---

## References

Berger et al., 2000 — Adam Berger, Rich Caruana, David Cohn, Dayne Freitag, and Vibhu Mittal. Bridging the lexical chasm: statistical approaches to answer-finding. In *Proceedings of the 23rd Annual International ACM SIGIR Conference*, pages 192–199.

Chen et al., 2017 — Danqi Chen, Adam Fisch, Jason Weston, and Antoine Bordes. Reading Wikipedia to answer open-domain questions. In *Proceedings of ACL*, pages 1870–1879.

Dai and Callan, 2020 — Zhuyun Dai and Jamie Callan. Context-aware term weighting for first stage passage retrieval. In *Proceedings of SIGIR 2020*, pages 1533–1536.

Devlin et al., 2018 — Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. BERT: Pre-training of deep bidirectional transformers for language understanding. *arXiv preprint arXiv:1810.04805*.

Guo et al., 2020 — Mandy Guo, Yinfei Yang, Daniel Cer, Qinlan Shen, and Noah Constant. MultiReQA: A cross-domain evaluation for retrieval question answering models.

Hofstätter et al., 2021a — Sebastian Hofstätter, Sheng-Chieh Lin, Jheng-Hong Yang, Jimmy Lin, and Allan Hanbury. Efficiently teaching an effective dense retriever with balanced topic aware sampling. In *Proceedings of SIGIR 2021*.

Hofstätter et al., 2021b — Sebastian Hofstätter, Sophia Althammer, Michael Schröder, Mete Sertkan, and Allan Hanbury. Improving efficient neural ranking models with cross-architecture knowledge distillation.

Ioffe, 2010 — Sergey Ioffe. Improved consistent sampling, weighted minhash and L1 sketching. In *Proceedings of ICDM 2010*, pages 246–255.

Karpukhin et al., 2020 — Vladimir Karpukhin, Barlas Oguz, Sewon Min, Patrick Lewis, Ledell Wu, Sergey Edunov, Danqi Chen, and Wen-tau Yih. Dense passage retrieval for open-domain question answering. In *Proceedings of EMNLP 2020*, pages 6769–6781.

Khattab and Zaharia, 2020 — Omar Khattab and Matei Zaharia. ColBERT: Efficient and effective passage search via contextualized late interaction over BERT. In *Proceedings of SIGIR 2020*, pages 39–48.

Nguyen et al., 2016 — Tri Nguyen, Mir Rosenberg, Xia Song, Jianfeng Gao, Saurabh Tiwary, Rangan Majumder, and Li Deng. MS MARCO: A human generated machine reading comprehension dataset. In *Proceedings of NIPS Workshop*.

Nogueira et al., 2019 — Rodrigo Nogueira, Jimmy Lin, and AI Epistemic. From doc2query to docTTTTTquery. Online preprint.

Petroni et al., 2020 — Fabio Petroni et al. KILT: A benchmark for knowledge intensive language tasks.

Raffel et al., 2020 — Colin Raffel et al. Exploring the limits of transfer learning with a unified text-to-text transformer. *Journal of Machine Learning Research*, 21(140):1–67.

Robertson and Zaragoza, 2009 — Stephen Robertson and Hugo Zaragoza. The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4):333–389.

Thorne et al., 2018 — James Thorne, Andreas Vlachos, Christos Christodoulopoulos, and Arpit Mittal. FEVER: A large-scale dataset for fact extraction and verification. In *Proceedings of NAACL 2018*, pages 809–819.

Van Gysel and de Rijke, 2018 — Christophe Van Gysel and Maarten de Rijke. Pytrec_eval: An extremely fast Python interface to trec_eval. In *Proceedings of SIGIR 2018*.

Wang et al., 2013 — Yining Wang, Liwei Wang, Yuanzhi Li, Di He, Wei Chen, and Tie-Yan Liu. A theoretical analysis of NDCG ranking measures. In *Proceedings of COLT 2013*.

Wang et al., 2020 — Wenhui Wang, Furu Wei, Li Dong, Hangbo Bao, Nan Yang, and Ming Zhou. MiniLM: Deep self-attention distillation for task-agnostic compression of pre-trained transformers. In *Advances in NeurIPS 33*, pages 5776–5788.

Xiong et al., 2020 — Lee Xiong, Chenyan Xiong, Ye Li, Kwok-Fung Tang, Jialin Liu, Paul Bennett, Junaid Ahmed, and Arnold Overwijk. Approximate nearest neighbor negative contrastive learning for dense text retrieval.

Zhao et al., 2021 — Tiancheng Zhao, Xiaopeng Lu, and Kyusong Lee. SPARTA: Efficient open-domain question answering via sparse transformer matching retrieval. In *Proceedings of NAACL 2021*, pages 565–575.
