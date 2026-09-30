# BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models

## Abstract

Neural retrieval systems, which find the documents relevant to a text query, are usually trained and tested on the same dataset, so how they behave on other tasks and domains, where no training data exist, is largely unknown {C002}{C004}. This paper presents BEIR (Benchmarking-IR), a benchmark of 18 English datasets from 9 retrieval tasks that evaluates systems zero-shot, without adapting them to each dataset {C020}. The authors compare ten publicly available systems from five architecture families with one ranking score computed from human relevance judgements (nDCG@10), and add measurements of latency and index size and a manual re-annotation of one dataset {C022}{C011}. No system has the highest score on every dataset, and the classic keyword method BM25 remains a strong baseline. A re-ranking pipeline (BM25 followed by a cross-encoder, BM25+CE) scores above BM25 on 16 of 18 datasets and the late-interaction model ColBERT on 9 of 18, yet both are the slowest systems, while several learned sparse and dense systems that score above BM25 on their training dataset fall below it on many others {C043}{C032}{C033}{C040}. On TREC-COVID, a search dataset over COVID-related papers, judging previously unjudged results raised the dense retriever ANCE from 0.654 to 0.735 nDCG@10 while lexical systems barely moved, suggesting that existing labels favour keyword-based systems {C042}{C052}. Every score is a single evaluation without variance estimates, the benchmark is English-only, and the label-bias measurement covers one dataset {C042}{L007}{L001}.

## 1 Introduction

Information retrieval is the task of returning, for a text query, the documents in a large collection (the corpus) that are relevant to it. Retrieval is usually the first step of larger systems such as question answering and duplicate-question detection (Chen et al., 2017; Zhang et al., 2015) {C006}. Neural retrieval systems, built on pre-trained transformers such as BERT (Devlin et al., 2019), are typically trained on a large labelled dataset such as MS MARCO (Nguyen et al., 2016), a web-search dataset, or Natural Questions (NQ) (Kwiatkowski et al., 2019) and then tested on that same dataset, where they are reported to score above the classic keyword method BM25 (Karpukhin et al., 2020; Nogueira et al., 2020) {C004}.

The authors motivate the study with two observations. Creating a large training corpus is time-consuming and expensive, so many retrieval systems are applied zero-shot, meaning that no training data from the target task are available {C001}. And it is unclear how well trained neural retrieval models perform on other text domains or tasks, or how systems that represent text with sparse versus dense vectors behave on out-of-distribution data {C002}.

According to the paper, earlier benchmarks do not fill this need. MultiReQA (Guo et al., 2020) covers one task, question answering, mostly on Wikipedia and over small candidate pools, and KILT (Petroni et al., 2020) covers eleven datasets from five knowledge-intensive tasks in which retrieval is not the primary task and documents come only from Wikipedia {C005}. The authors regard this narrowness as limiting what can be learned about out-of-distribution behaviour {C003}. Among the benchmarks the paper cites, none evaluates zero-shot retrieval across many tasks and domains {C005}.

This paper asks three research questions about zero-shot retrieval {C056}. RQ1: does a model's score on the dataset it was trained on predict its score on other datasets? RQ2: which architectures hold up across heterogeneous datasets, and at what computational cost? RQ3: do the relevance labels of existing datasets treat systems that differ from the labelling systems fairly?

To answer them, the authors built BEIR, a collection of 18 English datasets from 9 retrieval tasks, and evaluated ten public systems from five architecture families on it {C020}{C022}. They chose datasets to differ in task, domain, difficulty and annotation method, so that no single kind of data dominates {C010}, and report one metric, nDCG@10, on all of them {C011}.

The study makes four contributions.

1. A benchmark and software: 18 datasets in one format with a Python package (Section 3) {C020}{C021}.
2. A ten-system comparison in which no system is best everywhere, BM25 remains a strong baseline, and scores on the training dataset do not order systems as zero-shot scores do (Section 5.1 and 5.2) {C043}{C044}.
3. A cost analysis in which the systems with the best average zero-shot scores are the slowest and, for ColBERT, need the largest index (Section 5.4) {C040}.
4. An annotation-bias study on TREC-COVID in which filling in unjudged results raises ANCE from 0.654 to 0.735 but docT5query only from 0.713 to 0.714 (Section 5.5) {C042}.

Section 2 gives background, Section 3 the benchmark, Section 4 the set-up, Section 5 the results by question, Section 6 their meaning, and Section 7 the limitations the authors concede plus further caveats.

## 2 Background and related work

### 2.1 Retrieval systems by where query and document meet

Lexical retrieval scores a document by the words it shares with the query. BM25 (Robertson et al., 2009), the standard lexical method, weights matching words by frequency and rarity and is the reference for every neural system in this study {C006}. Its limitation is the lexical gap: a relevant document that shares no keyword with the query cannot be found by matching words alone (Berger et al., 2000) {C006}. The five families in the study differ in how they try to close this gap and in how much computation they spend per query (Lin et al., 2020 give a survey) {C006}.

- Sparse systems keep a keyword (inverted) index but change what is indexed. docT5query (Nogueira et al., 2019b) appends queries generated by a sequence-to-sequence model to each document, DeepCT (Dai et al., 2020) learns term weights with BERT, and SPARTA (Zhao et al., 2021) turns contextual token representations into a precomputed index {C006}.
- Dense systems encode the query and the document separately into vectors (a bi-encoder) and rank by cosine similarity or dot product. DPR (Karpukhin et al., 2020), ANCE (Xiong et al., 2020) and TAS-B (Hofstätter et al., 2021a) differ mainly in how training negatives and losses are chosen; GenQ fine-tunes TAS-B on synthetic queries generated for the target corpus, an instance of unsupervised domain adaptation (Ma et al., 2021; Liang et al., 2020) {C006}.
- Late interaction keeps one vector per token: ColBERT (Khattab et al., 2020) scores each query token against its best-matching document token (a maximum-similarity operation) {C006}.
- Re-ranking uses a cross-encoder, which reads query and document together with attention across both, to re-score the top results of a first-stage retriever such as BM25; it is accurate but has a high computational overhead (Nogueira et al., 2020) {C006}.

### 2.2 Earlier benchmarks

Earlier benchmarks differ from BEIR in task breadth (MultiReQA has one task; retrieval is secondary in KILT), in domain (KILT is Wikipedia only; five of MultiReQA's eight datasets are from Wikipedia) and in corpus size (six of MultiReQA's eight tasks have fewer than 100k candidate sentences, a setting that the paper, citing Reimers et al. (2020), says favours dense over lexical retrieval) {C005}.

## 3 Benchmark design

### 3.1 Datasets and the reasons for choosing them

BEIR contains 18 English datasets from nine tasks: fact checking, citation prediction, duplicate-question retrieval, argument retrieval, news retrieval, question answering, tweet retrieval, bio-medical retrieval and entity retrieval {C020}. Table 1 lists them. Corpus sizes range from 3.6K to 14.91M documents, average query length from 3 to 192 words and average document length from 11 to 635 words {C020}. Each dataset has a corpus, test queries and qrels: labelled (query, document) pairs, binary or graded, that say which documents are relevant (the relevance judgements). Counting MS MARCO, 19 datasets in all, only 8 have training data {C020}.

{{TABLE1}}

The authors give four reasons for their choices {C010}. Systems should be tested on different query and document lengths (diverse tasks) and on domains from generic to specialised (diverse domains). A task that any algorithm solves easily cannot discriminate between models, so they picked tasks believed to be challenging and unsolved (difficulty). Because datasets carry annotation biases that hinder fair comparison, they picked datasets created by crowd-workers, experts and online communities to reduce the impact of any one bias (diverse annotation) {C010}. The text announces three factors but lists these four.

### 3.2 How different are the domains?

To check domain diversity, the authors compute a weighted Jaccard similarity (Ioffe, 2010) on unigram word overlap for every pair of datasets and observe rather low overlap across different domains {C023}. They read this as an indication that BEIR is challenging for systems that must handle out-of-distribution domains {C024}. The measure is lexical; difficulty is not tested directly.

### 3.3 The metric

All scores are nDCG@10, normalised discounted cumulative gain over the top 10 results, computed with the Python interface of the official TREC evaluation tool (Van Gysel et al., 2018). The metric rewards placing relevant documents high in the ranking, accepts graded relevance labels, and lies between 0 and 1. The authors report differences in points, one point being 0.01. They wanted one metric comparable across all tasks: precision and recall ignore rank, mean reciprocal rank and mean average precision cannot handle graded relevance, and nDCG balances both (Wang et al., 2013 give the theory) {C011}.

### 3.4 Software

The accompanying Python package (pip install beir) converts every dataset into one format (corpus, queries, qrels), wraps existing retrieval toolkits and computes standard retrieval metrics {C021}. The README lists 17 preprocessed datasets for download; four (BioASQ, Signal-1M (RT), TREC-NEWS, Robust04) are not public and come with reproduction instructions {C021}.

## 4 Experimental setup

### 4.1 Setup: systems and configuration

The authors evaluate public checkpoints of ten systems {C022}. All neural systems except DPR are trained on MS MARCO and applied to BEIR without adaptation. Only the first 512 word pieces of each document are used, because of the length limits of transformer networks {C013}. Because most systems were trained on MS MARCO, its scores are reported but excluded from the zero-shot comparison {C012}.

BM25 uses the Anserini toolkit (Yang et al., 2017) with default Lucene parameters (k=0.9, b=0.4) {C022}. docT5query appends 40 generated queries per document, and SPARTA keeps 2,000 non-zero entries of a 30k-dimensional vector {C022}. DPR is the Multi checkpoint, trained on NQ, TriviaQA, WebQuestions and CuratedTREC {C022}. TAS-B combines a pairwise Margin-MSE loss with in-batch negatives and is supervised by a cross-encoder and ColBERT {C022}. GenQ generates 5 queries per document with a T5 model and continues to train TAS-B on them, yielding one model per dataset {C022}. ColBERT runs end-to-end: candidates from approximate nearest-neighbour search (depth 100) are re-scored by late interaction {C022}. BM25+CE re-ranks the BM25 top 100 with a 6-layer MiniLM cross-encoder (Wang et al., 2020) {C022}.

The authors describe how they chose several settings but do not report the comparisons behind them {C014}. Anserini BM25 was kept because it performed better than Elasticsearch BM25 and RM3 query expansion; DeepCT uses default BM25 parameters because they worked better than parameters tuned on MS MARCO; the DPR Multi model replaced the NQ-only model because it performed better in their setting; and the MiniLM cross-encoder was the best on MS MARCO among 14 public re-rankers {C014}. Practical constraints shaped three more settings {C015}: SPARTA was re-implemented because the original code is not public, GenQ was capped at 100K target documents per dataset for lack of resources, and the TREC-NEWS and Touché-2020 label formats were converted for simplicity.

### 4.2 Setup: further experiments

Three further experiments address specific questions. For RQ2, the authors measure latency and index size on 1 million randomly sampled DBPedia documents, using exact search for dense models and approximate nearest-neighbour search for ColBERT, on an 8-core Intel Xeon Platinum 8168 CPU and a single Nvidia Tesla V100 GPU {C040}.

For RQ3, note how relevance labels arise. Judges cannot label every (query, document) pair, so they label the documents returned by some existing systems (pooling) and treat every unjudged document as irrelevant. A system unlike the pooled ones can be penalised for finding relevant documents nobody judged. Hole@10, the share of a system's top-10 results that no annotator judged, measures this exposure. On TREC-COVID the authors judged all such holes for the systems in Table 4, without knowing which system returned each document, to avoid preference bias {C017}, and recomputed nDCG@10.

Finally, TAS-B and ANCE differ in backbone, loss and negative mining, which makes the cause of their different behaviour hard to isolate. The authors therefore trained two otherwise identical models that differ only in similarity function, cosine or dot product {C016}.

## 5 Results

### 5.1 RQ1: does training-set performance predict zero-shot performance?

Table 2 gives nDCG@10 per system on MS MARCO and the 18 BEIR datasets. On the MS MARCO development set, BM25 scores 0.228 and every MS-MARCO-trained neural system scores higher, from 0.296 (DeepCT) to 0.413 (BM25+CE); the authors describe the gap as 7-18 points {C030}. Zero-shot the order changes. Measured relative to BM25 and averaged over the 18 datasets (last row of Table 2; the paper does not define the averaging), BM25+CE is +11%, ColBERT +2.5% and docT5query +1.6%, whereas TAS-B is -2.8%, GenQ -3.6%, ANCE -7.4%, SPARTA -20.3%, DeepCT -27.9% and DPR -47.7% {C031}. DeepCT, SPARTA and ANCE score above BM25 on MS MARCO yet fall below it zero-shot, so for these systems training-set performance does not predict zero-shot performance {C044}. The paper reports no rank correlation, and each score is one evaluation of one checkpoint {L007}.

{{TABLE2}}

### 5.2 RQ2: which architectures hold up?

BM25+CE scores higher than BM25 on 16 of 18 datasets {C032}. It falls below BM25 only on ArguAna (0.311 versus 0.315) and Touché-2020 (0.271 versus 0.367), two tasks the authors call extremely different from MS MARCO {C032}. ColBERT scores higher than BM25 on 9 of 18 datasets and is a bit weaker than the re-ranker {C033}. Among sparse systems, docT5query scores above BM25 on 11 of 18 datasets and is competitive on the rest (Section 7 notes a count discrepancy) {C034}, whereas DeepCT and SPARTA, good on MS MARCO, are below BM25 on nearly all datasets {C035}.

Dense retrievers vary. TAS-B is the best of them: it scores higher than ANCE on 14 of 18 datasets and higher than DPR on 17 of 18 {C036}. Even so, dense systems fall below BM25 on some datasets, for example BioASQ (BM25 0.465, TAS-B 0.383, ANCE 0.306, DPR 0.127), and DPR, the only dense system not trained on MS MARCO, performs worst overall {C036}.

Taken together, no system has the highest score on every dataset, BM25 remains a strong baseline, and only BM25+CE scores above it on nearly all datasets {C043}. Small differences, such as ArguAna's 0.311 versus 0.315, come without intervals {L007}. The results do not isolate which component is responsible, because the systems differ in several respects at once (Section 7).

### 5.3 Why do dense systems differ?

TAS-B scores below ANCE by 17.3 points on TREC-COVID and by 7.8 points on Touché-2020. The documents they return differ in length: the median top-10 document has 10 words for TAS-B and 160 for ANCE on TREC-COVID, and 14 versus 89 words on Touché-2020 {C037}. About 42k of the 171k TREC-COVID documents consist of a title without an abstract, and TAS-B returns many of them {C037}.

In the controlled comparison, switching from cosine similarity to dot product raised TREC-COVID nDCG@10 from 0.482 to 0.635 (15.3 points) but lowered it on a majority of other datasets, for example Signal-1M (RT) from 0.261 to 0.243. The cosine-similarity model preferred shorter documents on all datasets {C038}.

GenQ, which adapts TAS-B to each corpus, scores higher than TAS-B on specialised domains (TREC-COVID 0.619 versus 0.481, FiQA-2018 0.308 versus 0.300, CQADupStack 0.347 versus 0.314) and lower on the Wikipedia-based NQ (0.358 versus 0.463) and HotpotQA (0.534 versus 0.584), and on SCIDOCS (0.143 versus 0.149) {C039}.

### 5.4 RQ2: what do the systems cost?

Table 3 gives estimated single-query latency and index size on 1 million DBPedia documents {C040}. The best average zero-shot systems are the slowest: BM25+CE takes 450 ms per query on the GPU and 6100 ms on the CPU, and ColBERT 350 ms on the GPU, against 14 ms for TAS-B on the GPU and 20 ms for BM25 on the CPU {C040}. ColBERT also has the largest index (20GB, against 12GB for SPARTA, 3GB for dense models and 0.4GB for BM25), and at the scale of BioASQ (about 15M documents) it requires about 900GB, where BM25 requires 18GB {C040}. Accuracy and cost therefore trade off for the two best families {C049}.

{{TABLE3}}

### 5.5 RQ3: do the labels treat systems fairly?

In Table 4, Hole@10 on TREC-COVID varies by system: 6.4% for BM25, 2.8% for docT5query, 14.4% for ANCE and 31.8% for TAS-B {C041}. After the authors judged the 980 missing query-document pairs, lexical systems changed little (docT5query from 0.713 to 0.714), while ANCE rose from 0.654, slightly below BM25, to 0.735, 6.7 points above the annotated BM25 score, and ColBERT improved by 5.8 points {C042}. The added judgements cover one dataset and are the authors' own (Section 7), so this illustrates that label bias can change a comparison, not how far it does so elsewhere {C042}.

{{TABLE4}}

## 6 Discussion

### 6.1 Answers to the research questions

RQ1: for the systems studied, training-set scores do not predict zero-shot ordering {C044}. RQ2: no system is best everywhere; the two best on average, BM25+CE and ColBERT, are the most expensive, and BM25 is a strong baseline {C043}{C049}. RQ3: on TREC-COVID, the annotation pool, although built from many systems, still favours lexical approaches, so part of the dense systems' shortfall there reflects missing judgements {C052}.

### 6.2 Explanations offered by the authors

None of these explanations was tested by ablation. The authors read the strength of re-ranking and ColBERT as pointing to cross-attention and cross-attention-like operations as important for out-of-distribution performance {C045}. They explain docT5query's result by document expansion adding relevant keywords, unlike learned term weighting {C046}. They speculate that TAS-B's strength among dense systems comes from its training set-up, with in-batch negatives and a Margin-MSE loss with strong teacher models {C047}. They attribute TAS-B's preference for short documents to its loss function, and the cosine versus dot-product experiment is consistent with this {C048}.

### 6.3 Relation to prior work and implications

Earlier reports of gains over BM25 were measured on the training dataset {C004}, and the zero-shot results indicate that for several systems these gains do not carry over {C044}. The authors call for datasets built with diverse pooling strategies, and note that integrating many systems into BEIR simplifies building such pools {C053}.

## 7 Limitations

The authors state the following limitations.

Scope of the benchmark. All datasets are English, because multilingual retrieval datasets are scarce {L001}. Most tasks have documents of a few hundred words, and longer documents would need a fundamentally different set-up because transformers often have a 512 word-piece limit {L002}. BEIR covers pure text search, whereas real applications also use signals such as PageRank, recency, authority scores and click-through rates that are hard to integrate {L003}. Only datasets with one or two text fields are included {L004}. BEIR evaluates models meant to work across tasks, while task-specific models can easily beat generic ones on their own task {L005}. The authors add that no benchmark is perfect {L006}. Together these bound the central finding: it concerns general-purpose systems on English, text-only datasets of moderate document length {C043}.

Evidence. No error bars or seed variance are reported, because the systems are existing checkpoints that often come without training code, so retraining is not feasible {L007}. The total amount of compute is not reported, only the CPU and GPU types {L008}. Differences of a few points between systems therefore cannot be checked against run-to-run variation, and cost is described only by latency and index size.

Data. The authors did not check the more than 50 million documents for offensive content or personally identifiable information, because removing content would alter the datasets {L009}. They did not discuss potential negative societal impacts {L010}. The repository README says that the maintainers do not vouch for dataset quality or fairness and do not claim that users hold licences {L013}.

Labels and attribution. Even though many systems contributed to the TREC-COVID annotation pool, it remains biased towards lexical approaches, which gives non-lexical approaches an unfair disadvantage; the authors call for less biased datasets {L011}. Because TAS-B and ANCE differ in backbone, loss and negative mining, the authors state that identifying the source of their contrasting behaviour is difficult {L012}.

Additional caveats. The following points are ours, not the authors':
- The annotation-bias study covers one dataset, so the size of the effect on the other 17 is unknown {L101}. The added judgements were made by the paper's own authors, blind to system, not by independent assessors {L108}.
- Latency and index size come from one 1M-document DBPedia sample and one CPU and GPU pair, so only the broad ordering is supported {L102}.
- The systems differ in training data, backbone and first stage at once (DPR was trained on other data; BM25+CE re-ranks the BM25 top 100), so differences cannot be assigned to architecture family alone {L103}.
- The last row of Table 2 averages heterogeneous datasets into one relative number whose computation is not defined; a later study cited by the README (Kamalloo et al., 2024) names single-average comparisons of BEIR scores as a shortcoming {L104}.
- The text's docT5query count (11 of 18 datasets) differs from the 12 obtained from the reconstructed Table 2; the text count is used {L105}.
- Several datasets have few test queries (TREC-COVID 50, Touché-2020 49, TREC-NEWS 57, Signal-1M (RT) 97), and small per-dataset differences are reported without intervals {L106}.
- SPARTA was re-implemented and GenQ capped at 100K documents per dataset, so conclusions about these two are conclusions about these implementations {L107}.

## 8 Conclusion

BEIR turns the question of whether a retrieval model works on data it was not trained for into a measurement across 18 datasets and 9 tasks. In that measurement the best system depends on the dataset, keyword matching with BM25 is hard to match cheaply, and the systems that score above it on most datasets pay in latency and index size {C043}{C049}. Training-set scores are a poor guide {C044}, and on TREC-COVID missing relevance labels understated dense systems {C052}. The findings concern English text and single evaluations. The authors point to diverse pooling for fairer labels {C053} and to multilingual, long-document, multi-factor, multi-field and task-specific evaluation as extensions {C054}.

## References

- Berger et al. (2000). Bridging the lexical chasm: statistical approaches to answer-finding. SIGIR.
