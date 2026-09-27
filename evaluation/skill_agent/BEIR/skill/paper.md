# BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of Information Retrieval Models

**Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, Iryna Gurevych**  
Ubiquitous Knowledge Processing Lab (UKP-TUDA), Technische Universität Darmstadt

---

## Abstract

Neural information retrieval (IR) models have delivered impressive gains on standard benchmarks, but those benchmarks typically evaluate within the same distribution used for training. Whether these gains reflect genuine generalization—the ability to retrieve well across new tasks and domains without additional fine-tuning—has remained largely untested. We present BEIR (Benchmarking-IR), a heterogeneous evaluation suite of 18 publicly available retrieval datasets spanning 9 distinct task types and domains ranging from biomedical literature to Twitter to legal arguments. Using BEIR, we evaluate 10 retrieval systems from five architectural families (lexical, sparse, dense, late-interaction, and cross-encoder re-ranking) in a fully zero-shot setting, where all models are applied directly to target datasets without any domain-specific training. Our principal finding is that in-domain performance is a poor predictor of zero-shot generalization: BM25, a classical keyword-matching baseline that underperforms neural models by 7–18 nDCG@10 points on in-domain evaluation, proves to be a competitive zero-shot baseline that most neural models fail to consistently surpass. Cross-encoder re-ranking achieves the best overall zero-shot performance (+11% average over BM25), but at high computational cost; dense retrieval models—despite their efficiency advantages—vary widely in zero-shot performance, with results ranging from near-parity (TAS-B: −2.8% vs. BM25) to large deficits (DPR: −47.7%). We additionally demonstrate that annotation selection bias systematically penalises non-lexical models, and show, in a case study on TREC-COVID, that correcting for this bias substantially narrows the gap between dense and lexical methods on that dataset. BEIR is released as an open-source Python package to support standardised evaluation of future retrieval systems.

---

## 1. Introduction

Retrieval is the first stage of many high-stakes NLP pipelines. Open-domain question answering, fact verification, scientific literature discovery, and duplicate detection all depend on a retrieval component that can surface relevant documents from a large collection in milliseconds (Kwiatkowski et al., 2019; Thorne et al., 2018; Zhang et al., 2015). The standard approach is to train a retrieval model on a large supervised dataset—most commonly MS MARCO (Nguyen et al., 2016), which provides 532,761 query-passage pairs drawn from Bing search logs—and then evaluate on held-out queries from the same distribution. On MS MARCO, neural retrieval models dramatically outperform classical methods: the best neural systems beat BM25 (Robertson and Zaragoza, 2009) by 7–18 nDCG@10 points.

This evaluation protocol has a structural problem: a model trained on web search queries over web passages is being evaluated on web search queries over web passages. When the same models are applied to biomedical literature, financial forum posts, or argumentative texts—all legitimate retrieval settings—there is no guarantee the gains hold. Practitioners who deploy retrieval in a new domain routinely discover this the hard way.

Two prior efforts at multi-dataset IR evaluation—MultiReQA (Guo et al., 2020) and KILT (Petroni et al., 2020)—provide partial coverage but leave the core question unanswered. MultiReQA covers only question-answering over small corpora (8 datasets, 5 of them Wikipedia-based, all a single task type), and it does not measure zero-shot generalisation explicitly. KILT spans five knowledge-intensive task families but restricts retrieval exclusively to Wikipedia and treats retrieval as a subtask rather than the primary measurement target. Together, neither benchmark crosses more than one retrieval domain or tests whether in-domain rankings translate to new domains.

The central empirical question is whether in-domain ranking performance predicts zero-shot performance across new domains and tasks. The distributional argument above suggests it should not—but no systematic, multi-task, multi-domain test of this hypothesis existed.

This paper introduces BEIR, a benchmark designed specifically to measure zero-shot generalisation in text retrieval. BEIR curates 18 datasets across 9 retrieval task types—question answering, fact checking, argument retrieval, duplicate question detection, biomedical IR, news retrieval, tweet retrieval, citation prediction, and entity retrieval—spanning corpora from 3,633 to 14.9 million documents, average query lengths from 3 to 192 words, and average document lengths from 11 to 635 words. All models are evaluated without any target-domain fine-tuning, using a single unified metric (nDCG@10) that accommodates both binary and graded relevance judgements.

Our contributions are:

1. A curated, diverse evaluation benchmark of 18 retrieval datasets across 9 task types and multiple domains, with unified format and metrics.
2. A systematic zero-shot evaluation of 10 retrieval systems spanning five architecture families, revealing that in-domain performance cannot predict out-of-distribution generalisation.
3. An analysis of annotation selection bias in retrieval evaluation and a concrete demonstration that this bias understates the performance of non-lexical models.
4. A publicly released open-source Python package that standardises dataset loading, model integration, and evaluation.

---

## 2. Background: A Taxonomy of Neural Retrieval Architectures

To make the paper self-contained for readers from adjacent ML fields, this section outlines the five retrieval architecture families evaluated in BEIR.

**Lexical retrieval.** BM25 (Robertson and Zaragoza, 2009) is the canonical lexical baseline. Given a query, it scores each document by the weighted frequency of shared terms, using TF-IDF-style term weights adjusted for document length. Retrieval is exact, fast, and fully interpretable, but BM25 cannot bridge the *lexical gap*: it cannot match a document that expresses the same idea with different words (Berger et al., 2000; Lin et al., 2020).

**Sparse neural retrieval.** Sparse methods use transformer encoders to augment lexical indices. DeepCT (Dai and Callan, 2020) replaces raw term frequencies with BERT-predicted term importance weights, keeping the BM25 infrastructure. DocT5query (Nogueira et al., 2019) takes a different approach: a T5 model generates plausible query strings that are appended to each document before indexing, expanding the document's keyword vocabulary. SPARTA (Zhao et al., 2021) represents documents as 30,000-dimensional sparse token-level embedding vectors, enabling exact token-level matching in semantic space. The 30,000 dimensions correspond approximately to the vocabulary size of the underlying transformer; each active dimension encodes how strongly a token type is present in the document, so query-document matching reduces to a sparse inner product over shared vocabulary entries—fast because most dimensions are zero.

**Dense retrieval.** Dense retrievers encode queries and documents independently into a shared dense vector space using dual-encoder (bi-encoder) architectures, typically built on pre-trained transformers (Karpukhin et al., 2020; Lin et al., 2020). At inference, document vectors are pre-computed and indexed; query vectors are computed on the fly and compared to documents by inner product or cosine similarity. This supports sub-millisecond search via approximate nearest-neighbour (ANN) indices. Three dense models are evaluated in BEIR: DPR (Karpukhin et al., 2020), trained on four QA datasets; ANCE (Xiong et al., 2020), trained with hard negatives mined from an ANN index; and TAS-B (Hofstätter et al., 2021), trained with knowledge distillation from a cross-encoder and a late-interaction model using a combined Margin-MSE and in-batch negative loss.

**Late-interaction retrieval.** ColBERT (Khattab and Zaharia, 2020) represents queries and documents as *sets* of contextualised token vectors rather than single vectors. Relevance is scored by summing, over each query token, the maximum dot-product similarity to any document token (MaxSim). This is more expressive than a single-vector dot product but requires storing multiple vectors per document and is substantially more expensive at inference.

**Re-ranking.** Re-ranking pipelines first retrieve candidate documents with a fast first stage (BM25 in BEIR) and then score the top-*k* candidates with a cross-encoder, which reads query and document jointly and computes a relevance score through full bidirectional attention across the concatenation (Nogueira and Cho, 2020). The evaluated model (BM25+CE) uses a 6-layer MiniLM cross-encoder (Wang et al., 2020) trained with knowledge distillation from an ensemble of larger BERT models. It re-ranks the top-100 BM25 results.

---

## 3. The BEIR Benchmark

### 3.1 Dataset Selection Criteria

The benchmark is constructed around four selection principles: (i) **task diversity**—nine qualitatively distinct retrieval tasks; (ii) **domain diversity**—from encyclopaedic Wikipedia to specialised biomedical literature, financial forums, Twitter, news, and online debate platforms; (iii) **difficulty**—each included task remains unsolved by existing approaches; and (iv) **annotation diversity**—datasets created by crowd workers, domain experts, and community feedback are each included, to reduce the influence of any single annotation style on conclusions.

### 3.2 Dataset Overview

Table 1 summarises the 18 datasets. The nine task families are:

- **Bio-medical IR** (TREC-COVID, NFCorpus, BioASQ): Queries are scientific or clinical questions; corpora are PubMed or CORD-19 articles.
- **Question answering** (Natural Questions, HotpotQA, FiQA-2018): NQ retrieves Wikipedia passages for factoid queries; HotpotQA requires multi-hop reasoning across paragraphs; FiQA-2018 retrieves financial opinion posts.
- **Tweet retrieval** (Signal-1M): Given a news headline, retrieve relevant tweets.
- **News retrieval** (TREC-NEWS, Robust04): Background linking and robust topic retrieval over news archives.
- **Argument retrieval** (ArguAna, Touché-2020): Retrieval of counterarguments and argumentative texts.
- **Duplicate question retrieval** (CQADupStack, Quora): Find semantically duplicate questions in StackExchange subforums and Quora.
- **Entity retrieval** (DBPedia): Retrieve Wikipedia entity pages for entity-bearing queries.
- **Citation prediction** (SCIDOCS): Given a paper title, retrieve the papers it cites.
- **Fact checking** (FEVER, Climate-FEVER, SciFact): Retrieve evidence passages for a factual claim.

The datasets vary substantially in scale (3,633 to 14.9 million documents—for context, most NLP classification and span-extraction benchmarks contain a few thousand test examples, and even large-scale generation benchmarks rarely exceed hundreds of thousands of reference items; retrieval over 14.9 million documents is two to three orders of magnitude more demanding in scale), query length (3 to 192 average words), document length (11 to 635 average words), relevance granularity (binary or multi-level), and training data availability (only 8 of 18 include labelled training pairs).

**Table 1. Summary statistics for BEIR datasets (test split).** Avg. D/Q = average relevant documents per query.

| Dataset | Task | Domain | #Queries | #Corpus | Avg. D/Q |
|---|---|---|---:|---:|---:|
| MS MARCO | Passage retrieval | Web | 6,980 | 8.84M | 1.1 |
| TREC-COVID | Bio-medical IR | Scientific | 50 | 171K | 493.5 |
| NFCorpus | Bio-medical IR | Scientific | 323 | 3.6K | 38.2 |
| BioASQ | Bio-medical IR | Scientific | 500 | 14.9M | 4.7 |
| NQ | Question answering | Wikipedia | 3,452 | 2.68M | 1.2 |
| HotpotQA | Question answering | Wikipedia | 7,405 | 5.23M | 2.0 |
| FiQA-2018 | Question answering | Finance | 648 | 57K | 2.6 |
| Signal-1M | Tweet retrieval | Twitter | 97 | 2.86M | 19.6 |
| TREC-NEWS | News retrieval | News | 57 | 595K | 19.6 |
| Robust04 | News retrieval | News | 249 | 528K | 69.9 |
| ArguAna | Argument retrieval | Misc. | 1,406 | 8.67K | 1.0 |
| Touché-2020 | Argument retrieval | Misc. | 49 | 382K | 19.0 |
| CQADupStack | Duplicate questions | StackExchange | 13,145 | 457K | 1.4 |
| Quora | Duplicate questions | Quora | 10,000 | 523K | 1.6 |
| DBPedia | Entity retrieval | Wikipedia | 400 | 4.63M | 38.2 |
| SCIDOCS | Citation prediction | Scientific | 1,000 | 25K | 4.9 |
| FEVER | Fact checking | Wikipedia | 6,666 | 5.42M | 1.2 |
| Climate-FEVER | Fact checking | Wikipedia | 1,535 | 5.42M | 3.0 |
| SciFact | Fact checking | Scientific | 300 | 5K | 1.1 |

### 3.3 Domain Diversity Quantification

To verify that the benchmark genuinely requires generalisation across distinct vocabularies, the authors compute pairwise weighted Jaccard similarity on unigram word overlap across all dataset pairs. The resulting heatmap shows predominantly low overlap across different domains, with higher overlap only between datasets drawn from the same corpus (e.g., FEVER and Climate-FEVER share the Wikipedia corpus). This confirms that models cannot rely on vocabulary overlap to succeed across datasets. [MISSING: pairwise Jaccard overlap summary statistics (e.g., median cross-domain similarity value) are not reported in the source materials; the heatmap figure is not reproduced here.]

### 3.4 Evaluation Metric

The benchmark standardises on nDCG@10 (Normalised Discounted Cumulative Gain at rank 10), evaluated using the official TREC evaluation tool (Van Gysel and de Rijke, 2018). This metric is chosen over precision, recall, MRR, and MAP because it handles both binary and graded relevance, is rank-aware, and provides a theoretically well-grounded ranking measure (Wang et al., 2013). Concretely: nDCG@10 assigns a graded relevance gain to each of the top-10 retrieved documents, discounts each gain by the log of its rank position (so rank 1 contributes more than rank 10), sums these discounted gains, and normalizes by the maximum achievable sum (the ideal ranking). A score of 1.0 means the system returned the best possible top-10 list; a score of 0.0 means none of its top-10 documents were relevant. All ten systems are evaluated on each of the 18 datasets using a single, consistent protocol.

### 3.5 Software Framework

BEIR is distributed as an open-source Python package (`pip install beir`) that provides a standardised corpus/query/qrels format, dataset downloading and loading utilities, and evaluation wrappers for Sentence-Transformers (Reimers and Gurevych, 2019), Transformers (Wolf et al., 2020), Anserini (Yang et al., 2017), DPR (Karpukhin et al., 2020), ColBERT (Khattab and Zaharia, 2020), and Elasticsearch. The unified format enables a new model to be evaluated across all 18 datasets with minimal code changes.

---

## 4. Experimental Setup

All models are evaluated on publicly released pre-trained checkpoints without any target-domain fine-tuning. The majority of neural models were fine-tuned on MS MARCO (Nguyen et al., 2016), with the exception of DPR (Karpukhin et al., 2020), which was trained on four question-answering datasets (NQ, TriviaQA, WebQuestions, CuratedTREC). All transformer-based models are limited to 512 word-pieces per document, which truncates a minority of long documents. The five architecture families tested are:

- **Lexical:** BM25 (Anserini, default Lucene parameters k=0.9, b=0.4).
- **Sparse:** DeepCT, SPARTA, DocT5query.
- **Dense:** DPR (Multi), ANCE (RoBERTa, 600K steps on MS MARCO), TAS-B (DistilBERT, Margin-MSE + in-batch negatives), GenQ (TAS-B fine-tuned on synthetic target-domain queries, capped at 100K documents per target dataset).
- **Late-interaction:** ColBERT (BERT-base, 300K steps on MS MARCO, max sequence 300).
- **Re-ranking:** BM25 + MiniLM-L6 cross-encoder (6-layer, 384 hidden dims, knowledge distillation from BERT-base, BERT-large, ALBERT-large ensemble; re-ranks top-100 BM25 results).

In-domain performance on MS MARCO is reported separately and excluded from zero-shot averages. Efficiency measurements (Section 5.2) were conducted on a single Nvidia Tesla V100 (GPU) and an 8-core Intel Xeon Platinum 8168 CPU @ 2.70GHz, on a random sample of 1 million documents from DBPedia.

---

## 5. Results

### 5.1 Zero-Shot Performance

**Table 2. nDCG@10 on BEIR (zero-shot) and MS MARCO (in-domain, marked ‡). Bold = best; underline = second best. Avg. performance vs. BM25 excludes MS MARCO.**

| Dataset | BM25 | DeepCT | SPARTA | docT5q | DPR | ANCE | TAS-B | GenQ | ColBERT | BM25+CE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| MS MARCO | 0.228 | 0.296‡ | 0.351‡ | 0.338‡ | 0.177 | 0.388‡ | 0.408‡ | 0.408‡ | 0.401‡ | 0.413‡ |
| TREC-COVID | 0.656 | 0.406 | 0.538 | **0.713** | 0.332 | 0.654 | 0.481 | 0.619 | 0.677 | 0.757 |
| NFCorpus | 0.325 | 0.283 | 0.301 | 0.328 | 0.189 | 0.237 | 0.319 | 0.319 | 0.305 | **0.350** |
| BioASQ | 0.465 | 0.407 | 0.431 | 0.399 | 0.127 | 0.306 | 0.383 | 0.398 | **0.474** | **0.523** |
| NQ | 0.329 | 0.188 | 0.398 | 0.399 | 0.474‡ | 0.446 | 0.463 | 0.358 | **0.524** | **0.533** |
| HotpotQA | 0.603 | 0.503 | 0.492 | 0.580 | 0.391 | 0.456 | 0.584 | 0.534 | 0.593 | **0.707** |
| FiQA-2018 | 0.236 | 0.191 | 0.198 | 0.291 | 0.112 | 0.295 | 0.300 | 0.308 | 0.317 | **0.347** |
| Signal-1M | 0.330 | 0.269 | 0.252 | 0.307 | 0.155 | 0.249 | 0.289 | 0.281 | 0.274 | **0.338** |
| TREC-NEWS | 0.398 | 0.220 | 0.258 | 0.420 | 0.161 | 0.382 | 0.377 | 0.396 | 0.393 | **0.431** |
| Robust04 | 0.408 | 0.287 | 0.276 | 0.437 | 0.252 | 0.392 | 0.427 | 0.362 | 0.391 | **0.475** |
| ArguAna | 0.315 | 0.309 | 0.279 | 0.349 | 0.175 | 0.415 | 0.429 | **0.493** | 0.233 | 0.311 |
| Touché-2020 | **0.367** | 0.156 | 0.175 | 0.347 | 0.131 | 0.240 | 0.162 | 0.182 | 0.202 | 0.271 |
| CQADupStack | 0.299 | 0.268 | 0.257 | 0.325 | 0.153 | 0.296 | 0.314 | 0.347 | **0.350** | 0.370 |
| Quora | 0.789 | 0.691 | 0.630 | 0.802 | 0.248 | 0.852 | 0.835 | 0.830 | **0.854** | 0.825 |
| DBPedia | 0.313 | 0.177 | 0.314 | 0.331 | 0.263 | 0.281 | 0.384 | 0.328 | 0.392 | **0.409** |
| SCIDOCS | 0.158 | 0.124 | 0.126 | 0.162 | 0.077 | 0.122 | 0.149 | 0.143 | 0.145 | **0.166** |
| FEVER | 0.753 | 0.353 | 0.596 | 0.714 | 0.562 | 0.669 | 0.700 | 0.669 | 0.771 | **0.819** |
| Climate-FEVER | 0.213 | 0.066 | 0.082 | 0.201 | 0.148 | 0.198 | 0.228 | 0.175 | 0.184 | **0.253** |
| SciFact | 0.665 | 0.630 | 0.582 | 0.675 | 0.318 | 0.507 | 0.643 | 0.644 | 0.671 | **0.688** |
| **Avg. vs. BM25** | — | −27.9% | −20.3% | +1.6% | −47.7% | −7.4% | −2.8% | −3.6% | +2.5% | **+11%** |

The central finding is a striking inversion: **in-domain performance does not predict zero-shot performance**. BM25, which scores 0.228 on MS MARCO, performs competitively or wins outright on many zero-shot datasets. Neural models that substantially outperform BM25 in-domain (by 7–18 nDCG points) often fall below it in zero-shot settings. Five key patterns emerge.

**Term-weighting fails; document expansion generalises.** DeepCT and SPARTA both use transformers to re-weight terms for BM25 indexing. Both perform well in-domain (0.296 and 0.351 respectively), but their zero-shot performance collapses: on average, DeepCT is 27.9% below BM25 and SPARTA is 20.3% below across the zero-shot datasets. The reweighting learned from MS MARCO does not transfer to other domains. In contrast, DocT5query's document expansion approach—which appends synthetically generated queries to documents, enriching the keyword vocabulary—achieves an average of +1.6% over BM25 and outperforms it on 11 of 18 datasets. Adding relevant keywords that the original document lacks generalises across domains because the added vocabulary targets the query distribution rather than term weights in a specific corpus.

**Dense models struggle with distribution shift.** DPR, trained on four QA datasets rather than MS MARCO, shows the poorest zero-shot generalisation overall (−47.7% vs BM25). The MS MARCO-trained ANCE and TAS-B show intermediate performance (−7.4% and −2.8% on average) and outperform BM25 on many individual datasets—particularly those similar in distribution to their training data—but fail on datasets with large domain or task shifts such as BioASQ, SCIDOCS, and Touché-2020. Dense retrievers compress queries and documents into fixed-size vectors independently; this architecture may encode distribution-specific features that do not transfer when the target domain is genuinely different from the training domain.

**Re-ranking and late-interaction generalise best.** BM25+CE achieves the best zero-shot performance, outperforming BM25 on 16 of 18 datasets and improving average nDCG@10 by 11%. The two failure cases—ArguAna and Touché-2020—are argument retrieval tasks that are semantically unlike MS MARCO passages. ColBERT outperforms BM25 on 9 of 18 datasets (+2.5% on average), achieving second place overall. The common feature of both models is cross-attention (or cross-attention-like MaxSim) between query and document tokens, which allows relevance signals to be computed at inference time from actual token content rather than from pre-compressed representations encoded during training.

**Training setup matters within the dense family.** TAS-B outperforms ANCE on 14 of 18 zero-shot datasets and DPR on 17 of 18. TAS-B combines topic-aware sampling, in-batch negatives, and Margin-MSE loss with knowledge distillation from a cross-encoder and ColBERT. These patterns are correlational: no controlled ablation separates the contributions of topic-aware sampling, Margin-MSE distillation, and in-batch negatives, and TAS-B also differs from ANCE in backbone architecture (DistilBERT vs. RoBERTa), so the training-objective explanation—while the most plausible—is not experimentally isolated.

**Domain adaptation helps on specialist domains.** GenQ fine-tunes TAS-B on synthetic queries generated over the target domain corpus. It outperforms TAS-B on specialised domains such as scientific publications, finance, and StackExchange forums, but underperforms TAS-B on broad Wikipedia-based domains. This suggests domain adaptation is beneficial when the target domain is genuinely out of distribution, but may hurt when the base model is already well-calibrated for a broad domain.

### 5.2 Efficiency: Latency and Storage

The first finding—that cross-attention architectures generalise better—leads immediately to a practical question: can practitioners afford those architectures? Generalisation and cost jointly determine deployment value.

Real-world retrieval systems must balance performance against latency and storage constraints. Table 3 summarises efficiency measurements on a random sample of 1 million documents from DBPedia.

**Table 3. Estimated retrieval latency and index size for 1M DBPedia documents (ranked by zero-shot BEIR performance). Lower latency or memory is preferred.**

| Rank | Model | GPU Latency | CPU Latency | Index Size |
|---:|---|---:|---:|---:|
| 1 | BM25+CE | 450ms | 350ms | 0.4GB |
| 2 | ColBERT | — | 6,100ms | 20GB (≈900GB at BioASQ scale) |
| 3 | DocT5query | 14ms | 20ms | 0.4GB |
| 4 | BM25 | 14ms | 20ms | 0.4GB |
| 5 | TAS-B | 19ms | 125ms | 3GB |
| 6 | GenQ | 19ms | 125ms | 3GB |
| 7 | ANCE | — | 275ms | 3GB |
| 8 | SPARTA | — | 20ms | 12GB |
| 9 | DeepCT | — | 25ms | 0.4GB |
| 10 | DPR | — | 230ms | 3GB |

There is a clear trade-off between performance and cost. Re-ranking (BM25+CE) has the best zero-shot performance but requires cross-encoder inference over 100 candidates per query, yielding latency above 350ms on GPU. Dense models are 20–30x faster (under 20ms on GPU) but sacrifice performance. ColBERT occupies an intermediate position: its MaxSim scoring is more expressive than a single dot product, but storing multiple 128-dimensional token vectors per document requires 20GB for 1M documents—and approximately 900GB for the BioASQ corpus of 15M documents, compared to 18GB for BM25. DocT5query offers a compelling efficiency profile: it retains BM25's 0.4GB index and fast lookup while improving generalisation through expanded document vocabulary.

---

## 6. Annotation Selection Bias

The zero-shot comparisons in Section 5 rest on the assumption that the existing relevance judgements are unbiased. Before treating those comparisons as definitive, a structural property of how retrieval benchmarks are constructed demands attention: if the systems used to pool annotation candidates were predominantly lexical, non-lexical models may be systematically disadvantaged not by performance but by measurement.

A critical but often overlooked threat to the validity of retrieval benchmarks is annotation selection bias (Lipani, 2019): evaluation datasets are constructed by pooling the top-*k* results from a set of retrieval systems, judging those results for relevance, and treating all unjudged documents as non-relevant. If the retrieval systems used for pooling are predominantly lexical, then non-lexical models will retrieve documents that were never presented to annotators—documents that are assumed non-relevant but may in fact be relevant. This directly penalises non-lexical approaches in evaluation.

To quantify this bias, the authors measure the *Hole@10* rate for each model on TREC-COVID: the fraction of top-10 retrieved documents that were never shown to annotators. Table 4 shows that lexical systems have substantially lower Hole@10 than non-lexical systems. BM25 and DocT5query have Hole@10 rates of 6.4% and 2.8% respectively, while TAS-B has 31.8%, ANCE 14.4%, and ColBERT 12.4%. TREC-COVID was constructed with a relatively diverse pooling strategy (using results from many participating teams), yet this bias is still clearly present.

**Table 4. Hole@10 analysis on TREC-COVID: nDCG@10 before (original) and after (annotated) manually annotating 980 missing query-document pairs.**

| Model | Hole@10 | nDCG@10 (original) | nDCG@10 (annotated) | Change |
|---|---:|---:|---:|---:|
| BM25 | 6.4% | 0.656 | 0.668 | +0.012 |
| DeepCT | 19.4% | 0.406 | 0.472 | +0.066 |
| SPARTA | 12.4% | 0.538 | 0.624 | +0.086 |
| DocT5query | 2.8% | 0.713 | 0.714 | +0.001 |
| DPR | 30.6% | 0.332 | 0.445 | +0.113 |
| ANCE | 14.4% | 0.654 | 0.735 | +0.081 |
| TAS-B | 31.8% | 0.481 | 0.555 | +0.074 |
| ColBERT | 12.4% | 0.677 | 0.735 | +0.058 |
| BM25+CE | 1.6% | 0.757 | 0.760 | +0.003 |

After manual annotation of 980 previously unjudged query-document pairs, the performance of ANCE increases from 0.654 to 0.735 (an 8.1-point gain), and ColBERT increases from 0.677 to 0.735 (a 5.8-point gain). BM25, with few missing judgements, improves only from 0.656 to 0.668. The corrected scores place ANCE and ColBERT decisively above BM25 on this dataset—a ranking reversal that is entirely invisible in the original evaluation. This demonstrates that lexical selection bias can give a false impression of BM25 dominance on certain datasets and highlights the importance of using diverse retrieval systems during annotation pool construction.

It is important to note that this finding does not overturn the main BEIR conclusions: the analysis is restricted to one dataset, and the manual annotation was performed by the paper's authors following the original TREC-COVID annotation guidelines. Across all 18 BEIR datasets, BM25 remains a strong overall baseline, and the bias analysis should be understood as a warning about interpreting individual dataset scores rather than a systematic correction of the benchmark.

---

## 7. Discussion

**Why does in-domain performance fail to predict zero-shot performance?** A retrieval model trained on MS MARCO is optimised to distinguish relevant from non-relevant passages for Bing web search queries. The model learns to exploit the statistical regularities of that query-document distribution—the vocabulary of web queries, the structure of Wikipedia passages, the density of relevant terms in passage-length documents. When deployed on, say, BioASQ (biomedical questions against 15M PubMed articles) or Touché-2020 (argumentative texts about controversial topics), those regularities do not hold. Dense models, which compress the entire semantic content of a document into a single vector, are particularly vulnerable: fine-tuning on a single domain risks encoding features specific to that domain. BM25 avoids this trap entirely—it does not learn domain-specific representations.

**Why do cross-attention models generalise better?** Both BM25+CE and ColBERT score query-document pairs using operations that compare query tokens and document tokens directly (cross-attention and MaxSim respectively), rather than comparing pre-compressed representations. This means that query-specific relevance signals are computed at inference time, based on the actual token content of query and document, rather than being baked into fixed embeddings during training. This inference-time flexibility is the most parsimonious explanation for the observed generalisation advantage—but the attribution is correlational, not causal. Confounds include model size (MiniLM cross-encoder vs. bi-encoders), distillation training, and the quality of BM25's candidate pool that is fed to the re-ranker; no ablation isolates the cross-attention mechanism from these other factors.

**An additional complication: similarity function choice.** An ablation study embedded in the paper reveals that even the choice of similarity function within a dense model—cosine similarity versus dot product—substantially alters which document lengths are preferred and thereby affects performance on different datasets. For TREC-COVID, switching from cosine similarity to dot product improves nDCG@10 from 0.482 to 0.635 (+15.3 points), while on Signal-1M the same switch decreases performance from 0.261 to 0.243. This sensitivity arises because cosine similarity normalises for vector magnitude, giving no advantage to longer documents, while dot-product similarity naturally gives higher scores to longer documents whose vectors have larger magnitudes. The optimal choice is dataset-specific, which complicates claims about which dense architecture is universally better.

**What should practitioners do?** The results suggest a practical hierarchy for zero-shot deployment. When latency constraints allow, cross-encoder re-ranking over BM25 candidates is the most reliable choice, outperforming BM25 on 16 of 18 datasets. When low-latency retrieval is required, DocT5query offers an excellent trade-off: it matches BM25's indexing footprint and lookup speed while improving generalisation on the majority of datasets. Dense retrieval with strong training (TAS-B, ANCE) is competitive on datasets similar to MS MARCO in structure but may fail on specialist domains; domain-specific fine-tuning (GenQ) can recover performance in those cases.

---

## 8. Limitations

Several limitations bound the conclusions that can be drawn from BEIR.

**English only.** All 18 datasets are English. Cross-lingual and multilingual generalisation—an equally important dimension of out-of-distribution generalisation for deployed systems—is not measured.

**Annotation selection bias.** As documented in Section 6, many BEIR datasets were created with lexical retrieval systems for annotation pooling. While the bias analysis on TREC-COVID is informative, it does not extend to all 18 datasets, and the magnitude of bias for each dataset is unknown without similar manual annotation efforts.

**Document truncation.** All neural models are truncated at 512 word-pieces per document. For datasets with long documents (e.g., Robust04 with average document length 466 words), this may disadvantage neural models relative to BM25, which processes the full document.

**Single training source.** Almost all neural models are trained on MS MARCO. The conclusions about generalisation therefore measure how well MS MARCO-trained systems transfer, not whether neural retrieval can generalise in principle. A model trained with broader supervision might show different patterns.

**No statistical significance testing.** Because all models are evaluated from fixed pre-trained checkpoints, no error bars or significance tests are provided.

---

## 9. Conclusion

BEIR provides the first broad, heterogeneous benchmark for zero-shot IR evaluation, designed to expose a gap that in-domain benchmarking systematically conceals. Its central message is that standard IR leaderboards are poor proxies for deployed performance: models that lead on MS MARCO can fall below a classical BM25 baseline on biomedical, financial, or argumentative retrieval without any change beyond the deployment domain. The practical implication follows: cross-encoder re-ranking and document expansion (DocT5query) are the most reliable zero-shot strategies; dense bi-encoders require domain-targeted training or adaptation to close the gap. An analysis of annotation selection bias on TREC-COVID—the one dataset for which manual annotation was performed—further indicates that BM25's apparent lead on that dataset is partly a measurement artefact: correcting for incomplete relevance judgements substantially improves the standing of non-lexical models on that dataset specifically.

BEIR and its open-source Python package provide the community with a tool for measuring and improving the generalisation of retrieval systems. The results demonstrate that zero-shot performance is a distinct, underexplored capability—and that closing the gap between efficient dense retrieval and robust cross-attention-based methods is a productive direction for future research. More broadly, BEIR illustrates a general lesson relevant across NLP: evaluating models within a single distributional regime systematically overestimates their reliability in deployment.

---

## References

- Berger et al., 2000. Bridging the lexical chasm: statistical approaches to answer-finding. *SIGIR 2000*.
- Dai and Callan, 2020. Context-Aware Term Weighting For First Stage Passage Retrieval. *SIGIR 2020*.
- Guo et al., 2020. MultiReQA: A Cross-Domain Evaluation for Retrieval Question Answering Models.
- Hofstätter et al., 2021. Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling. *SIGIR 2021*.
- Karpukhin et al., 2020. Dense Passage Retrieval for Open-Domain Question Answering. *EMNLP 2020*.
- Khattab and Zaharia, 2020. ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. *SIGIR 2020*.
- Kwiatkowski et al., 2019. Natural Questions: a Benchmark for Question Answering Research. *TACL*.
- Lin et al., 2020. Pretrained Transformers for Text Ranking: BERT and Beyond.
- Lipani, 2019. On Biases in Information retrieval models and evaluation. PhD thesis, TU Wien.
- Nguyen et al., 2016. MS MARCO: A Human Generated MAchine Reading COmprehension Dataset.
- Nogueira and Cho, 2020. Passage Re-ranking with BERT.
- Nogueira et al., 2019. From doc2query to docTTTTTquery.
- Petroni et al., 2020. KILT: a Benchmark for Knowledge Intensive Language Tasks.
- Reimers and Gurevych, 2019. Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. *EMNLP 2019*.
- Robertson and Zaragoza, 2009. The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval*, 3(4):333–389.
- Thakur et al., 2021. BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models. *NeurIPS 2021, Datasets and Benchmarks Track*.
- Thorne et al., 2018. FEVER: a Large-scale Dataset for Fact Extraction and VERification. *NAACL 2018*.
- Van Gysel and de Rijke, 2018. Pytrec_eval: An Extremely Fast Python Interface to trec_eval. *SIGIR 2018*.
- Wang et al., 2013. A theoretical analysis of NDCG ranking measures. *COLT 2013*.
- Wang et al., 2020. MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers. *NeurIPS 2020*.
- Wolf et al., 2020. Transformers: State-of-the-Art Natural Language Processing. *EMNLP 2020*.
- Xiong et al., 2020. Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval.
- Yang et al., 2017. Anserini: Enabling the Use of Lucene for Information Retrieval Research. *SIGIR 2017*.
- Zhang et al., 2015. Multi-factor duplicate question detection in stack overflow. *JCST*, 30(5).
- Zhao et al., 2021. SPARTA: Efficient Open-Domain Question Answering via Sparse Transformer Matching Retrieval. *NAACL 2021*.
