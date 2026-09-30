# BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

## Abstract

Neural retrieval systems, which find the documents relevant to a text query, are usually trained and tested on the same dataset, so how they behave on other tasks and domains, where no training data exist, is largely unknown. This paper presents BEIR (Benchmarking-IR), a benchmark of 18 English datasets from 9 retrieval tasks that evaluates systems zero-shot, without adapting them to each dataset. The authors compare ten publicly available systems from five architecture families with one ranking score computed from human relevance judgements (nDCG@10), and add measurements of latency and index size and a manual re-annotation of one dataset. No system has the highest score on every dataset, and the classic keyword method BM25 remains a strong baseline. A re-ranking pipeline (BM25 followed by a cross-encoder, BM25+CE) scores above BM25 on 16 of 18 datasets and the late-interaction model ColBERT on 9 of 18, yet both are the slowest systems, while several learned sparse and dense systems that score above BM25 on their training dataset fall below it on many others. On TREC-COVID, a search dataset over COVID-related papers, judging previously unjudged results raised the dense retriever ANCE from 0.654 to 0.735 nDCG@10 while lexical systems barely moved, suggesting that existing labels favour keyword-based systems. Every score is a single evaluation without variance estimates, the benchmark is English-only, and the label-bias measurement covers one dataset.

## 1 Introduction

Information retrieval is the task of returning, for a text query, the documents in a large collection (the corpus) that are relevant to it. Retrieval is usually the first step of larger systems such as question answering and duplicate-question detection (Chen et al., 2017; Zhang et al., 2015). Neural retrieval systems, built on pre-trained transformers such as BERT (Devlin et al., 2019), are typically trained on a large labelled dataset such as MS MARCO (Nguyen et al., 2016), a web-search dataset, or Natural Questions (NQ) (Kwiatkowski et al., 2019) and then tested on that same dataset, where they are reported to score above the classic keyword method BM25 (Karpukhin et al., 2020; Nogueira et al., 2020).

The authors motivate the study with two observations. Creating a large training corpus is time-consuming and expensive, so many retrieval systems are applied zero-shot, meaning that no training data from the target task are available. And it is unclear how well trained neural retrieval models perform on other text domains or tasks, or how systems that represent text with sparse versus dense vectors behave on out-of-distribution data.

According to the paper, earlier benchmarks do not fill this need. MultiReQA (Guo et al., 2020) covers one task, question answering, mostly on Wikipedia and over small candidate pools, and KILT (Petroni et al., 2020) covers eleven datasets from five knowledge-intensive tasks in which retrieval is not the primary task and documents come only from Wikipedia. The authors regard this narrowness as limiting what can be learned about out-of-distribution behaviour. Among the benchmarks the paper cites, none evaluates zero-shot retrieval across many tasks and domains.

This paper asks three research questions about zero-shot retrieval. RQ1: does a model's score on the dataset it was trained on predict its score on other datasets? RQ2: which architectures hold up across heterogeneous datasets, and at what computational cost? RQ3: do the relevance labels of existing datasets treat systems that differ from the labelling systems fairly?

To answer them, the authors built BEIR, a collection of 18 English datasets from 9 retrieval tasks, and evaluated ten public systems from five architecture families on it. They chose datasets to differ in task, domain, difficulty and annotation method, so that no single kind of data dominates, and report one metric, nDCG@10, on all of them.

The study makes four contributions.

1. A benchmark and software: 18 datasets in one format with a Python package (Section 3).
2. A ten-system comparison in which no system is best everywhere, BM25 remains a strong baseline, and scores on the training dataset do not order systems as zero-shot scores do (Section 5.1 and 5.2).
3. A cost analysis in which the systems with the best average zero-shot scores are the slowest and, for ColBERT, need the largest index (Section 5.4).
4. An annotation-bias study on TREC-COVID in which filling in unjudged results raises ANCE from 0.654 to 0.735 but docT5query only from 0.713 to 0.714 (Section 5.5).

Section 2 gives background, Section 3 the benchmark, Section 4 the set-up, Section 5 the results by question, Section 6 their meaning, and Section 7 the limitations the authors concede plus further caveats.

## 2 Background and related work

### 2.1 Retrieval systems by where query and document meet

Lexical retrieval scores a document by the words it shares with the query. BM25 (Robertson et al., 2009), the standard lexical method, weights matching words by frequency and rarity and is the reference for every neural system in this study. Its limitation is the lexical gap: a relevant document that shares no keyword with the query cannot be found by matching words alone (Berger et al., 2000). The five families in the study differ in how they try to close this gap and in how much computation they spend per query (Lin et al., 2020 give a survey).

- Sparse systems keep a keyword (inverted) index but change what is indexed. docT5query (Nogueira et al., 2019b) appends queries generated by a sequence-to-sequence model to each document, DeepCT (Dai et al., 2020) learns term weights with BERT, and SPARTA (Zhao et al., 2021) turns contextual token representations into a precomputed index.
- Dense systems encode the query and the document separately into vectors (a bi-encoder) and rank by cosine similarity or dot product. DPR (Karpukhin et al., 2020), ANCE (Xiong et al., 2020) and TAS-B (Hofstätter et al., 2021a) differ mainly in how training negatives and losses are chosen; GenQ fine-tunes TAS-B on synthetic queries generated for the target corpus, an instance of unsupervised domain adaptation (Ma et al., 2021; Liang et al., 2020).
- Late interaction keeps one vector per token: ColBERT (Khattab et al., 2020) scores each query token against its best-matching document token (a maximum-similarity operation).
- Re-ranking uses a cross-encoder, which reads query and document together with attention across both, to re-score the top results of a first-stage retriever such as BM25; it is accurate but has a high computational overhead (Nogueira et al., 2020).

### 2.2 Earlier benchmarks

Earlier benchmarks differ from BEIR in task breadth (MultiReQA has one task; retrieval is secondary in KILT), in domain (KILT is Wikipedia only; five of MultiReQA's eight datasets are from Wikipedia) and in corpus size (six of MultiReQA's eight tasks have fewer than 100k candidate sentences, a setting that the paper, citing Reimers et al. (2020), says favours dense over lexical retrieval).

## 3 Benchmark design

### 3.1 Datasets and the reasons for choosing them

BEIR contains 18 English datasets from nine tasks: fact checking, citation prediction, duplicate-question retrieval, argument retrieval, news retrieval, question answering, tweet retrieval, bio-medical retrieval and entity retrieval. Table 1 lists them. Corpus sizes range from 3.6K to 14.91M documents, average query length from 3 to 192 words and average document length from 11 to 635 words. Each dataset has a corpus, test queries and qrels: labelled (query, document) pairs, binary or graded, that say which documents are relevant (the relevance judgements). Counting MS MARCO, 19 datasets in all, only 8 have training data.

**Table 1.** BEIR spans 9 tasks and corpora from 3.6K to 14.91M documents, with 1.0 to 493.5 relevant documents per query. Test queries, corpus size and relevant documents per query are from the repository README; domains follow Figure 1 of the paper.

| Task | Dataset | Domain | Test queries | Corpus | Relevant docs per query |
|---|---|---|---|---|---|
| Fact checking | FEVER (Thorne et al., 2018) | Wikipedia | 6,666 | 5.42M | 1.2 |
| Fact checking | Climate-FEVER (Diggelmann et al., 2020) | Wikipedia | 1,535 | 5.42M | 3.0 |
| Fact checking | SciFact (Wadden et al., 2020) | Scientific | 300 | 5K | 1.1 |
| Citation prediction | SCIDOCS (Cohan et al., 2020) | Scientific | 1,000 | 25K | 4.9 |
| Duplicate questions | Quora | Quora | 10,000 | 523K | 1.6 |
| Duplicate questions | CQADupStack (Hoogeveen et al., 2015) | StackExchange | 13,145 | 457K | 1.4 |
| Argument retrieval | Touché-2020 (Bondarenko et al., 2020) | Miscellaneous | 49 | 382K | 19.0 |
| Argument retrieval | ArguAna (Wachsmuth et al., 2018) | Miscellaneous | 1,406 | 8.67K | 1.0 |
| News retrieval | TREC-NEWS (Soboroff et al., 2019) | News | 57 | 595K | 19.6 |
| News retrieval | Robust04 (Voorhees, 2005) | News | 249 | 528K | 69.9 |
| Question answering | NQ (Kwiatkowski et al., 2019) | Wikipedia | 3,452 | 2.68M | 1.2 |
| Question answering | HotpotQA (Yang et al., 2018) | Wikipedia | 7,405 | 5.23M | 2.0 |
| Question answering | FiQA-2018 (Maia et al., 2018) | Finance | 648 | 57K | 2.6 |
| Tweet retrieval | Signal-1M (RT) (Suarez et al., 2018) | Twitter | 97 | 2.86M | 19.6 |
| Bio-medical | TREC-COVID (Voorhees et al., 2021) | Scientific | 50 | 171K | 493.5 |
| Bio-medical | BioASQ (Tsatsaronis et al., 2015) | Scientific | 500 | 14.91M | 4.7 |
| Bio-medical | NFCorpus (Boteva et al., 2016) | Scientific | 323 | 3.6K | 38.2 |
| Entity retrieval | DBPedia (Hasibi et al., 2017) | Wikipedia | 400 | 4.63M | 38.2 |


The authors give four reasons for their choices. Systems should be tested on different query and document lengths (diverse tasks) and on domains from generic to specialised (diverse domains). A task that any algorithm solves easily cannot discriminate between models, so they picked tasks believed to be challenging and unsolved (difficulty). Because datasets carry annotation biases that hinder fair comparison, they picked datasets created by crowd-workers, experts and online communities to reduce the impact of any one bias (diverse annotation). The text announces three factors but lists these four.

### 3.2 How different are the domains?

To check domain diversity, the authors compute a weighted Jaccard similarity (Ioffe, 2010) on unigram word overlap for every pair of datasets and observe rather low overlap across different domains. They read this as an indication that BEIR is challenging for systems that must handle out-of-distribution domains. The measure is lexical; difficulty is not tested directly.

### 3.3 The metric

All scores are nDCG@10, normalised discounted cumulative gain over the top 10 results, computed with the Python interface of the official TREC evaluation tool (Van Gysel et al., 2018). The metric rewards placing relevant documents high in the ranking, accepts graded relevance labels, and lies between 0 and 1. The authors report differences in points, one point being 0.01. They wanted one metric comparable across all tasks: precision and recall ignore rank, mean reciprocal rank and mean average precision cannot handle graded relevance, and nDCG balances both (Wang et al., 2013 give the theory).

### 3.4 Software

The accompanying Python package (pip install beir) converts every dataset into one format (corpus, queries, qrels), wraps existing retrieval toolkits and computes standard retrieval metrics. The README lists 17 preprocessed datasets for download; four (BioASQ, Signal-1M (RT), TREC-NEWS, Robust04) are not public and come with reproduction instructions.

## 4 Experimental setup

### 4.1 Setup: systems and configuration

The authors evaluate public checkpoints of ten systems. All neural systems except DPR are trained on MS MARCO and applied to BEIR without adaptation. Only the first 512 word pieces of each document are used, because of the length limits of transformer networks. Because most systems were trained on MS MARCO, its scores are reported but excluded from the zero-shot comparison.

BM25 uses the Anserini toolkit (Yang et al., 2017) with default Lucene parameters (k=0.9, b=0.4). docT5query appends 40 generated queries per document, and SPARTA keeps 2,000 non-zero entries of a 30k-dimensional vector. DPR is the Multi checkpoint, trained on NQ, TriviaQA, WebQuestions and CuratedTREC. TAS-B combines a pairwise Margin-MSE loss with in-batch negatives and is supervised by a cross-encoder and ColBERT. GenQ generates 5 queries per document with a T5 model and continues to train TAS-B on them, yielding one model per dataset. ColBERT runs end-to-end: candidates from approximate nearest-neighbour search (depth 100) are re-scored by late interaction. BM25+CE re-ranks the BM25 top 100 with a 6-layer MiniLM cross-encoder (Wang et al., 2020).

The authors describe how they chose several settings but do not report the comparisons behind them. Anserini BM25 was kept because it performed better than Elasticsearch BM25 and RM3 query expansion; DeepCT uses default BM25 parameters because they worked better than parameters tuned on MS MARCO; the DPR Multi model replaced the NQ-only model because it performed better in their setting; and the MiniLM cross-encoder was the best on MS MARCO among 14 public re-rankers. Practical constraints shaped three more settings: SPARTA was re-implemented because the original code is not public, GenQ was capped at 100K target documents per dataset for lack of resources, and the TREC-NEWS and Touché-2020 label formats were converted for simplicity.

### 4.2 Setup: further experiments

Three further experiments address specific questions. For RQ2, the authors measure latency and index size on 1 million randomly sampled DBPedia documents, using exact search for dense models and approximate nearest-neighbour search for ColBERT, on an 8-core Intel Xeon Platinum 8168 CPU and a single Nvidia Tesla V100 GPU.

For RQ3, note how relevance labels arise. Judges cannot label every (query, document) pair, so they label the documents returned by some existing systems (pooling) and treat every unjudged document as irrelevant. A system unlike the pooled ones can be penalised for finding relevant documents nobody judged. Hole@10, the share of a system's top-10 results that no annotator judged, measures this exposure. On TREC-COVID the authors judged all such holes for the systems in Table 4, without knowing which system returned each document, to avoid preference bias, and recomputed nDCG@10.

Finally, TAS-B and ANCE differ in backbone, loss and negative mining, which makes the cause of their different behaviour hard to isolate. The authors therefore trained two otherwise identical models that differ only in similarity function, cosine or dot product.

## 5 Results

### 5.1 RQ1: does training-set performance predict zero-shot performance?

Table 2 gives nDCG@10 per system on MS MARCO and the 18 BEIR datasets. On the MS MARCO development set, BM25 scores 0.228 and every MS-MARCO-trained neural system scores higher, from 0.296 (DeepCT) to 0.413 (BM25+CE); the authors describe the gap as 7-18 points. Zero-shot the order changes. Measured relative to BM25 and averaged over the 18 datasets (last row of Table 2; the paper does not define the averaging), BM25+CE is +11%, ColBERT +2.5% and docT5query +1.6%, whereas TAS-B is -2.8%, GenQ -3.6%, ANCE -7.4%, SPARTA -20.3%, DeepCT -27.9% and DPR -47.7%. DeepCT, SPARTA and ANCE score above BM25 on MS MARCO yet fall below it zero-shot, so for these systems training-set performance does not predict zero-shot performance. The paper reports no rank correlation, and each score is one evaluation of one checkpoint.

**Table 2.** BM25+CE is above BM25 on 16 of 18 zero-shot datasets, while DeepCT, SPARTA and DPR are below it on nearly all; no system is best everywhere. nDCG@10 per system, single evaluation each. ‡ marks in-domain scores (MS MARCO for the MS MARCO-trained systems, NQ for DPR). The last row is the paper's 'Avg. Performance vs. BM25' as printed.

| Dataset | BM25 | DeepCT | SPARTA | docT5query | DPR | ANCE | TAS-B | GenQ | ColBERT | BM25+CE |
|---|---|---|---|---|---|---|---|---|---|---|
| MS MARCO (in-domain) | 0.228 | 0.296‡ | 0.351‡ | 0.338‡ | 0.177 | 0.388‡ | 0.408‡ | 0.408‡ | 0.401‡ | 0.413‡ |
| TREC-COVID | 0.656 | 0.406 | 0.538 | 0.713 | 0.332 | 0.654 | 0.481 | 0.619 | 0.677 | 0.757 |
| BioASQ | 0.465 | 0.407 | 0.351 | 0.431 | 0.127 | 0.306 | 0.383 | 0.398 | 0.474 | 0.523 |
| NFCorpus | 0.325 | 0.283 | 0.301 | 0.328 | 0.189 | 0.237 | 0.319 | 0.319 | 0.305 | 0.350 |
| NQ | 0.329 | 0.188 | 0.398 | 0.399 | 0.474‡ | 0.446 | 0.463 | 0.358 | 0.524 | 0.533 |
| HotpotQA | 0.603 | 0.503 | 0.492 | 0.580 | 0.391 | 0.456 | 0.584 | 0.534 | 0.593 | 0.707 |
| FiQA-2018 | 0.236 | 0.191 | 0.198 | 0.291 | 0.112 | 0.295 | 0.300 | 0.308 | 0.317 | 0.347 |
| Signal-1M (RT) | 0.330 | 0.269 | 0.252 | 0.307 | 0.155 | 0.249 | 0.289 | 0.281 | 0.274 | 0.338 |
| TREC-NEWS | 0.398 | 0.220 | 0.258 | 0.420 | 0.161 | 0.382 | 0.377 | 0.396 | 0.393 | 0.431 |
| Robust04 | 0.408 | 0.287 | 0.276 | 0.437 | 0.252 | 0.392 | 0.427 | 0.362 | 0.391 | 0.475 |
| ArguAna | 0.315 | 0.309 | 0.279 | 0.349 | 0.175 | 0.415 | 0.429 | 0.493 | 0.233 | 0.311 |
| Touche-2020 | 0.367 | 0.156 | 0.175 | 0.347 | 0.131 | 0.240 | 0.162 | 0.182 | 0.202 | 0.271 |
| CQADupStack | 0.299 | 0.268 | 0.257 | 0.325 | 0.153 | 0.296 | 0.314 | 0.347 | 0.350 | 0.370 |
| Quora | 0.789 | 0.691 | 0.630 | 0.802 | 0.248 | 0.852 | 0.835 | 0.830 | 0.854 | 0.825 |
| DBPedia | 0.313 | 0.177 | 0.314 | 0.331 | 0.263 | 0.281 | 0.384 | 0.328 | 0.392 | 0.409 |
| SCIDOCS | 0.158 | 0.124 | 0.126 | 0.162 | 0.077 | 0.122 | 0.149 | 0.143 | 0.145 | 0.166 |
| FEVER | 0.753 | 0.353 | 0.596 | 0.714 | 0.562 | 0.669 | 0.700 | 0.669 | 0.771 | 0.819 |
| Climate-FEVER | 0.213 | 0.066 | 0.082 | 0.201 | 0.148 | 0.198 | 0.228 | 0.175 | 0.184 | 0.253 |
| SciFact | 0.665 | 0.630 | 0.582 | 0.675 | 0.318 | 0.507 | 0.643 | 0.644 | 0.671 | 0.688 |
| Avg. vs. BM25 | – | -27.9% | -20.3% | +1.6% | -47.7% | -7.4% | -2.8% | -3.6% | +2.5% | +11% |


### 5.2 RQ2: which architectures hold up?

BM25+CE scores higher than BM25 on 16 of 18 datasets. It falls below BM25 only on ArguAna (0.311 versus 0.315) and Touché-2020 (0.271 versus 0.367), two tasks the authors call extremely different from MS MARCO. ColBERT scores higher than BM25 on 9 of 18 datasets and is a bit weaker than the re-ranker. Among sparse systems, docT5query scores above BM25 on 11 of 18 datasets and is competitive on the rest (Section 7 notes a count discrepancy), whereas DeepCT and SPARTA, good on MS MARCO, are below BM25 on nearly all datasets.

Dense retrievers vary. TAS-B is the best of them: it scores higher than ANCE on 14 of 18 datasets and higher than DPR on 17 of 18. Even so, dense systems fall below BM25 on some datasets, for example BioASQ (BM25 0.465, TAS-B 0.383, ANCE 0.306, DPR 0.127), and DPR, the only dense system not trained on MS MARCO, performs worst overall.

Taken together, no system has the highest score on every dataset, BM25 remains a strong baseline, and only BM25+CE scores above it on nearly all datasets. Small differences, such as ArguAna's 0.311 versus 0.315, come without intervals. The results do not isolate which component is responsible, because the systems differ in several respects at once (Section 7).

### 5.3 Why do dense systems differ?

TAS-B scores below ANCE by 17.3 points on TREC-COVID and by 7.8 points on Touché-2020. The documents they return differ in length: the median top-10 document has 10 words for TAS-B and 160 for ANCE on TREC-COVID, and 14 versus 89 words on Touché-2020. About 42k of the 171k TREC-COVID documents consist of a title without an abstract, and TAS-B returns many of them.

In the controlled comparison, switching from cosine similarity to dot product raised TREC-COVID nDCG@10 from 0.482 to 0.635 (15.3 points) but lowered it on a majority of other datasets, for example Signal-1M (RT) from 0.261 to 0.243. The cosine-similarity model preferred shorter documents on all datasets.

GenQ, which adapts TAS-B to each corpus, scores higher than TAS-B on specialised domains (TREC-COVID 0.619 versus 0.481, FiQA-2018 0.308 versus 0.300, CQADupStack 0.347 versus 0.314) and lower on the Wikipedia-based NQ (0.358 versus 0.463) and HotpotQA (0.534 versus 0.584), and on SCIDOCS (0.143 versus 0.149).

### 5.4 RQ2: what do the systems cost?

Table 3 gives estimated single-query latency and index size on 1 million DBPedia documents. The best average zero-shot systems are the slowest: BM25+CE takes 450 ms per query on the GPU and 6100 ms on the CPU, and ColBERT 350 ms on the GPU, against 14 ms for TAS-B on the GPU and 20 ms for BM25 on the CPU. ColBERT also has the largest index (20GB, against 12GB for SPARTA, 3GB for dense models and 0.4GB for BM25), and at the scale of BioASQ (about 15M documents) it requires about 900GB, where BM25 requires 18GB. Accuracy and cost therefore trade off for the two best families.

**Table 3.** The best zero-shot systems are the slowest and, for ColBERT, the largest. Estimated single-query latency and index size on 1 million DBPedia documents; – = not reported.

| System | GPU latency | CPU latency | Index size |
|---|---|---|---|
| BM25+CE | 450ms | 6100ms | 0.4GB |
| ColBERT | 350ms | – | 20GB |
| docT5query | – | 30ms | 0.4GB |
| BM25 | – | 20ms | 0.4GB |
| TAS-B | 14ms | 125ms | 3GB |
| GenQ | 14ms | 125ms | 3GB |
| ANCE | 20ms | 275ms | 3GB |
| SPARTA | – | 20ms | 12GB |
| DeepCT | – | 25ms | 0.4GB |
| DPR | 19ms | 230ms | 3GB |


### 5.5 RQ3: do the labels treat systems fairly?

In Table 4, Hole@10 on TREC-COVID varies by system: 6.4% for BM25, 2.8% for docT5query, 14.4% for ANCE and 31.8% for TAS-B. After the authors judged the 980 missing query-document pairs, lexical systems changed little (docT5query from 0.713 to 0.714), while ANCE rose from 0.654, slightly below BM25, to 0.735, 6.7 points above the annotated BM25 score, and ColBERT improved by 5.8 points. The added judgements cover one dataset and are the authors' own (Section 7), so this illustrates that label bias can change a comparison, not how far it does so elsewhere.

**Table 4.** Filling TREC-COVID holes barely changes lexical systems but raises dense ones. Hole@10 (share of top-10 results never judged) and nDCG@10 before and after the authors judged the missing pairs; GenQ is not in the source table.

| System | Hole@10 | nDCG@10 original | nDCG@10 annotated |
|---|---|---|---|
| BM25 | 6.4% | 0.656 | 0.668 |
| DeepCT | 19.4% | 0.406 | 0.472 |
| SPARTA | 12.4% | 0.538 | 0.624 |
| docT5query | 2.8% | 0.713 | 0.714 |
| DPR | 30.6% | 0.332 | 0.445 |
| ANCE | 14.4% | 0.654 | 0.735 |
| TAS-B | 31.8% | 0.481 | 0.555 |
| ColBERT | 12.4% | 0.677 | 0.735 |
| BM25+CE | 1.6% | 0.757 | 0.760 |


## 6 Discussion

### 6.1 Answers to the research questions

RQ1: for the systems studied, training-set scores do not predict zero-shot ordering. RQ2: no system is best everywhere; the two best on average, BM25+CE and ColBERT, are the most expensive, and BM25 is a strong baseline. RQ3: on TREC-COVID, the annotation pool, although built from many systems, still favours lexical approaches, so part of the dense systems' shortfall there reflects missing judgements.

### 6.2 Explanations offered by the authors

None of these explanations was tested by ablation. The authors read the strength of re-ranking and ColBERT as pointing to cross-attention and cross-attention-like operations as important for out-of-distribution performance. They explain docT5query's result by document expansion adding relevant keywords, unlike learned term weighting. They speculate that TAS-B's strength among dense systems comes from its training set-up, with in-batch negatives and a Margin-MSE loss with strong teacher models. They attribute TAS-B's preference for short documents to its loss function, and the cosine versus dot-product experiment is consistent with this.

### 6.3 Relation to prior work and implications

Earlier reports of gains over BM25 were measured on the training dataset, and the zero-shot results indicate that for several systems these gains do not carry over. The authors call for datasets built with diverse pooling strategies, and note that integrating many systems into BEIR simplifies building such pools.

## 7 Limitations

The authors state the following limitations.

Scope of the benchmark. All datasets are English, because multilingual retrieval datasets are scarce. Most tasks have documents of a few hundred words, and longer documents would need a fundamentally different set-up because transformers often have a 512 word-piece limit. BEIR covers pure text search, whereas real applications also use signals such as PageRank, recency, authority scores and click-through rates that are hard to integrate. Only datasets with one or two text fields are included. BEIR evaluates models meant to work across tasks, while task-specific models can easily beat generic ones on their own task. The authors add that no benchmark is perfect. Together these bound the central finding: it concerns general-purpose systems on English, text-only datasets of moderate document length.

Evidence. No error bars or seed variance are reported, because the systems are existing checkpoints that often come without training code, so retraining is not feasible. The total amount of compute is not reported, only the CPU and GPU types. Differences of a few points between systems therefore cannot be checked against run-to-run variation, and cost is described only by latency and index size.

Data. The authors did not check the more than 50 million documents for offensive content or personally identifiable information, because removing content would alter the datasets. They did not discuss potential negative societal impacts. The repository README says that the maintainers do not vouch for dataset quality or fairness and do not claim that users hold licences.

Labels and attribution. Even though many systems contributed to the TREC-COVID annotation pool, it remains biased towards lexical approaches, which gives non-lexical approaches an unfair disadvantage; the authors call for less biased datasets. Because TAS-B and ANCE differ in backbone, loss and negative mining, the authors state that identifying the source of their contrasting behaviour is difficult.

Additional caveats. The following points are ours, not the authors':
- The annotation-bias study covers one dataset, so the size of the effect on the other 17 is unknown. The added judgements were made by the paper's own authors, blind to system, not by independent assessors.
- Latency and index size come from one 1M-document DBPedia sample and one CPU and GPU pair, so only the broad ordering is supported.
- The systems differ in training data, backbone and first stage at once (DPR was trained on other data; BM25+CE re-ranks the BM25 top 100), so differences cannot be assigned to architecture family alone.
- The last row of Table 2 averages heterogeneous datasets into one relative number whose computation is not defined; a later study cited by the README (Kamalloo et al., 2024) names single-average comparisons of BEIR scores as a shortcoming.
- The text's docT5query count (11 of 18 datasets) differs from the 12 obtained from the reconstructed Table 2; the text count is used.
- Several datasets have few test queries (TREC-COVID 50, Touché-2020 49, TREC-NEWS 57, Signal-1M (RT) 97), and small per-dataset differences are reported without intervals.
- SPARTA was re-implemented and GenQ capped at 100K documents per dataset, so conclusions about these two are conclusions about these implementations.

## 8 Conclusion

BEIR turns the question of whether a retrieval model works on data it was not trained for into a measurement across 18 datasets and 9 tasks. In that measurement the best system depends on the dataset, keyword matching with BM25 is hard to match cheaply, and the systems that score above it on most datasets pay in latency and index size. Training-set scores are a poor guide, and on TREC-COVID missing relevance labels understated dense systems. The findings concern English text and single evaluations. The authors point to diverse pooling for fairer labels and to multilingual, long-document, multi-factor, multi-field and task-specific evaluation as extensions.

## References

- Adam Berger, Rich Caruana, David Cohn et al. (2000). Bridging the lexical chasm: statistical approaches to answer-finding. Proceedings of the 23rd annual international ACM SIGIR conference.
- Alexander Bondarenko, Maik Fröbe, Meriem Beloucif et al. (2020). Overview of Touché 2020: Argument Retrieval. Working Notes Papers of the CLEF 2020 Evaluation Labs.
- Vera Boteva, Demian Gholipour, Artem Sokolov et al. (2016). A full-text learning to rank dataset for medical information retrieval. ECIR 2016.
- Danqi Chen, Adam Fisch, Jason Weston et al. (2017). Reading Wikipedia to Answer Open-Domain Questions. ACL 2017.
- Arman Cohan, Sergey Feldman, Iz Beltagy et al. (2020). SPECTER: Document-level Representation Learning using Citation-informed Transformers. ACL 2020.
- Zhuyun Dai, Jamie Callan (2020). Context-Aware Term Weighting For First Stage Passage Retrieval. SIGIR 2020.
- Jacob Devlin, Ming-Wei Chang, Kenton Lee et al. (2019). BERT: Pretraining of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT 2019.
- Thomas Diggelmann, Jordan Boyd-Graber, Jannis Bulian et al. (2020). CLIMATE-FEVER: A Dataset for Verification of Real-World Climate Claims.
- Mandy Guo, Yinfei Yang, Daniel Cer et al. (2020). MultiReQA: A Cross-Domain Evaluation for Retrieval Question Answering Models.
- Christophe Van Gysel, Maarten de Rijke (2018). Pytrec_eval: An Extremely Fast Python Interface to trec_eval. SIGIR 2018.
- Faegheh Hasibi, Fedor Nikolaev, Chenyan Xiong et al. (2017). DBpedia-Entity V2: A Test Collection for Entity Search. SIGIR 2017.
- Sebastian Hofstätter, Sheng-Chieh Lin, Jheng-Hong Yang et al. (2021a). Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling. Proc. of SIGIR.
- Doris Hoogeveen, Karin M Verspoor, Timothy Baldwin (2015). CQADupStack: A benchmark data set for community question-answering research. Proceedings of the 20th Australasian document computing symposium.
- Sergey Ioffe (2010). Improved consistent sampling, weighted minhash and l1 sketching. 2010 IEEE International Conference on Data Mining.
- Ehsan Kamalloo, Nandan Thakur, Carlos Lassance et al. (2024). Resources for Brewing BEIR: Reproducible Reference Models and Statistical Analyses. Proceedings of the 47th International ACM SIGIR Conference on Research and Development in Information Retrieval, pp. 1431-1440.
- Vladimir Karpukhin, Barlas Oguz, Sewon Min et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP 2020.
- Omar Khattab, Matei Zaharia (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. SIGIR 2020.
- Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield et al. (2019). Natural Questions: a Benchmark for Question Answering Research. Transactions of the Association of Computational Linguistics.
- Davis Liang, Peng Xu, Siamak Shakeri et al. (2020). Embedding-based Zero-shot Retrieval through Query Generation.
- Jimmy Lin, Rodrigo Nogueira, Andrew Yates (2020). Pretrained Transformers for Text Ranking: BERT and Beyond.
- Ji Ma, Ivan Korotkov, Yinfei Yang et al. (2021). Zero-shot Neural Passage Retrieval via Domain-targeted Synthetic Question Generation.
- Macedo Maia, Siegfried Handschuh, André Freitas et al. (2018). WWW'18 Open Challenge: Financial Opinion Mining and Question Answering. WWW '18 Companion.
- Tri Nguyen, Mir Rosenberg, Xia Song et al. (2016). MS MARCO: A Human Generated MAchine Reading COmprehension Dataset. choice, 2640:660.
- Rodrigo Nogueira, Jimmy Lin, AI Epistemic (2019b). From doc2query to docTTTTTquery. Online preprint.
- Rodrigo Nogueira, Kyunghyun Cho (2020). Passage Re-ranking with BERT. arXiv preprint arXiv:1901.04085.
- Fabio Petroni, Aleksandra Piktus, Angela Fan et al. (2020). KILT: a Benchmark for Knowledge Intensive Language Tasks.
- Nils Reimers, Iryna Gurevych (2020). The Curse of Dense Low-Dimensional Information Retrieval for Large Index Sizes. arXiv preprint arXiv:2012.14210.
- Stephen Robertson, Hugo Zaragoza (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4):333-389.
- Ian Soboroff, Shudong Huang, Donna Harman (2019). TREC 2019 News Track Overview. TREC.
- Axel Suarez, Dyaa Albakour, David Corney et al. (2018). A Data Collection for Evaluating the Retrieval of Related Tweets to News Articles. ECIR 2018.
- James Thorne, Andreas Vlachos, Christos Christodoulopoulos et al. (2018). FEVER: a Large-scale Dataset for Fact Extraction and VERification. NAACL-HLT 2018.
- George Tsatsaronis, Georgios Balikas, Prodromos Malakasiotis et al. (2015). An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition. BMC bioinformatics, 16(1):138.
- Ellen Voorhees (2005). Overview of the TREC 2004 Robust Retrieval Track.
- Ellen Voorhees, Tasmeer Alam, Steven Bedrick et al. (2021). TREC-COVID: Constructing a Pandemic Information Retrieval Test Collection. SIGIR Forum, 54(1).
- Henning Wachsmuth, Shahbaz Syed, Benno Stein (2018). Retrieval of the Best Counterargument without Prior Topic Knowledge. ACL 2018.
- David Wadden, Shanchuan Lin, Kyle Lo et al. (2020). Fact or Fiction: Verifying Scientific Claims. EMNLP 2020.
- Yining Wang, Liwei Wang, Yuanzhi Li et al. (2013). A theoretical analysis of NDCG ranking measures. COLT 2013, vol. 8.
- Wenhui Wang, Furu Wei, Li Dong et al. (2020). MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers. NeurIPS 2020, vol. 33.
- Lee Xiong, Chenyan Xiong, Ye Li et al. (2020). Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval.
- Peilin Yang, Hui Fang, Jimmy Lin (2017). Anserini: Enabling the Use of Lucene for Information Retrieval Research. SIGIR 2017.
- Zhilin Yang, Peng Qi, Saizheng Zhang et al. (2018). HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. EMNLP 2018.
- Yun Zhang, David Lo, Xin Xia et al. (2015). Multi-factor duplicate question detection in stack overflow. Journal of Computer Science and Technology, 30(5):981-997.
- Tiancheng Zhao, Xiaopeng Lu, Kyusong Lee (2021). SPARTA: Efficient Open-Domain Question Answering via Sparse Transformer Matching Retrieval. NAACL-HLT 2021.
