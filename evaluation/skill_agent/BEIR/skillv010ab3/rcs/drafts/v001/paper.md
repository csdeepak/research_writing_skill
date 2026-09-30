# How Well Do Retrieval Models Generalize Zero-Shot? The BEIR Benchmark and a Comparison of Ten Systems

## Abstract

Retrieval models find the documents a downstream system will read. They are usually trained and tested on the same dataset, so their behavior on new tasks without training data (the zero-shot setting) is unclear. BEIR (Benchmarking Information Retrieval) is a benchmark of 18 English datasets from nine retrieval tasks, built because earlier benchmarks cover a single task or domain {C001} {C002}. The authors evaluate ten public systems from five families (lexical, sparse, dense, late-interaction and re-ranking), measure latency and index size, and re-annotate unjudged results on one dataset, TREC-COVID {C004}. Accuracy on the training-domain dataset (MS MARCO, a large passage-retrieval set) did not predict zero-shot accuracy. The word-matching baseline BM25 scored below the neural systems in-domain, yet stayed a strong zero-shot baseline {C005} {C006}. Only re-ranking with a cross-encoder (+11% relative to BM25 on average), a late-interaction model (+2.5%) and a document-expansion method (+1.6%) averaged above BM25, while the other dense and sparse systems averaged below it {C007} {C005}. The two best averaging systems were also the slowest: re-ranking and late interaction needed more than 350 ms per query, whereas dense retrievers were 20-30x faster {C016}. On TREC-COVID, the share of unjudged top-10 hits ranged from 1.6% to 31.8% across systems {C017}. Annotating them left lexical systems almost unchanged and raised dense systems (the dense system ANCE from 0.654 to 0.735), which suggests that labels built from lexical pools understate non-lexical systems {C017} {C018} {C019}. All results are single evaluations of public checkpoints without variance, so small differences cannot be interpreted {L005}.

## 1 Introduction

Open-domain question answering, claim verification and duplicate-question detection all begin with a retrieval component that takes a query (the user's input) and returns documents (text of any length) from a collection, the corpus {C006}. Traditionally, retrieval has been dominated by lexical methods such as term frequency-inverse document frequency (TF-IDF) and BM25 (Robertson et al., 2009), which score documents by the words they share with the query. Such methods return only documents containing the query's keywords, a limitation known as the lexical gap (Berger et al., 2000). Neural retrievers based on pre-trained Transformers are now popular. The authors note that prior work usually trains them on a large dataset such as MS MARCO (Nguyen et al., 2016) and evaluates them on the same dataset, where gains over BM25 are reported {C005}.

Creating a large training corpus is expensive, so many deployed retrievers run zero-shot, on a task or domain for which they saw no training data {C006}. Testing on the training dataset (in-domain evaluation) says little about that situation, and how different neural designs generalize to unlike data is unclear.

Earlier benchmarks do not close this gap. As the authors describe them, MultiReQA (Guo et al., 2020) tests one task, question answering, mostly on small corpora. KILT (Petroni et al., 2020) retrieves only from Wikipedia and treats retrieval as a secondary task {C002}.

BEIR (Benchmarking IR) was built to answer three questions. RQ1: does in-domain performance predict zero-shot performance? RQ2: which retrieval architectures generalize best zero-shot, and at what latency and memory cost? RQ3: do the relevance labels in existing datasets, created with particular retrieval systems, favour some kinds of systems? The authors assembled 18 English datasets from nine retrieval tasks, evaluated ten public systems from five architecture families, measured speed and index size, and manually annotated missing relevance judgments on one dataset {C001} {C004}.

The contributions, as the evidence supports them, are:

1. A benchmark of 18 datasets from nine tasks, scored with one metric and released as open-source software with a standard data format {C001} {C003} {C021}.
2. A comparison showing that MS MARCO accuracy did not predict zero-shot accuracy for these ten systems, and that BM25 remained a strong baseline {C005} {C006} {C007}.
3. An accuracy-cost picture: the two best-averaging systems were the slowest, and one of the three systems above BM25 (docT5query) was as small as BM25 {C016} {C024}.
4. A label-bias analysis on TREC-COVID showing that unjudged top hits fall unevenly across systems and that annotating them changes the picture for dense systems {C017} {C018}.

Sections 2 to 4 give background, the benchmark and the setup; Section 5 reports results by research question; Sections 6 to 8 discuss, bound and conclude.

## 2 Background: retrieval architectures and earlier benchmarks

Five kinds of retrieval system are evaluated {C004}. A lexical system, here BM25, scores each document by weighted word matches with the query. A sparse neural system still retrieves through word matching but uses a network to improve it {C004}. DeepCT (Dai et al., 2020) learns term weights. SPARTA (Zhao et al., 2021) learns token-level representations stored as an inverted index. docT5query (Nogueira et al., 2019) appends synthetic queries, generated by a sequence-to-sequence model, to each document before BM25 is applied {C004}.

A dense system maps queries and documents independently into one vector space and retrieves the nearest vectors, so document vectors can be pre-computed and indexed. DPR (Karpukhin et al., 2020), ANCE (Xiong et al., 2020) and TAS-B (Hofstätter et al., 2021) differ in training data and in how they choose negative examples. GenQ, added by the authors, adapts TAS-B to each target corpus by fine-tuning on synthetic queries; related adaptation is described by Liang et al. (2020) and Ma et al. (2021). A late-interaction system, ColBERT (Khattab et al., 2020), keeps one vector per token for query and document and scores a pair with a maximum-similarity operation. A re-ranking system first retrieves candidates with BM25 and then scores each query-document pair jointly with a cross-encoder, a Transformer reading both texts together; the authors used a small MiniLM model (Wang et al., 2020). They note that such joint scoring brought large improvements but with a high computational overhead {C004}.

The authors report that five of MultiReQA's eight datasets come from Wikipedia and six of eight have fewer than 100k candidate sentences, a size range they say favours dense over lexical retrieval (Reimers et al., 2020) {C002}. KILT has five tasks and eleven datasets, but is Wikipedia-only and not primarily about retrieval {C002}. These are the authors' characterizations of works not read here {L011}.

## 3 The BEIR benchmark

**Selection criteria.** The authors chose datasets for diverse tasks, diverse domains (from news or Wikipedia to COVID-19 publications), sufficient difficulty (a task solved by any algorithm cannot separate models) and diverse annotation strategies (crowd-workers, experts, online communities), to reduce the effect of any one annotation bias {C001}.

**Contents.** BEIR contains 18 English datasets from nine tasks (Table 1). MS MARCO is also reported, as the in-domain training dataset, but is not part of the zero-shot comparison {C001}. Corpus sizes range from 3.6k to 15M documents; average query length ranges from 3 to 192 words and average document length from 11 to 635 words {C001}. Datasets carry relevance judgments (qrels), human labels stating which documents are relevant to which query; most are binary and a few are graded. Only 8 of the 19 datasets, counting MS MARCO, provide training data, and all except ArguAna have short queries; relevant documents per query average about one for some datasets and 493.5 for TREC-COVID {C001}.

**Table 1. The nine tasks and 18 datasets** {C001}

| Task | Datasets |
|---|---|
| Fact checking | FEVER, Climate-FEVER, SciFact |
| Citation prediction | SCIDOCS |
| Duplicate-question retrieval | Quora, CQADupStack |
| Argument retrieval | Touché-2020, ArguAna |
| News retrieval | TREC-NEWS, Robust04 |
| Question answering | NQ, HotpotQA, FiQA-2018 |
| Tweet retrieval | Signal-1M |
| Bio-medical retrieval | TREC-COVID, BioASQ, NFCorpus |
| Entity retrieval | DBPedia |

**Domain diversity.** The authors computed a pairwise weighted Jaccard similarity of unigram word distributions between datasets (Ioffe, 2010). They observe low overlap across domains and read this as showing that models must generalize to diverse domains {C020}. Word overlap is only a proxy for domain difference {L011}.

**Metric.** Every dataset is scored with nDCG@10, computed with the Python interface of the official evaluation tool of the Text REtrieval Conference (TREC) campaigns (Van Gysel et al., 2018) {C003}. nDCG@k is a rank-aware score over the top k results that gives more credit to relevant documents ranked higher and supports graded labels; 1 is a perfect ranking. Its theory is discussed by Wang et al. (2013). The authors chose it because Precision and Recall ignore rank, and mean reciprocal rank (MRR) and mean average precision (MAP) cannot handle graded relevance {C003}.

**Software.** BEIR is a pip-installable Python package with wrappers for several retrieval toolkits and a standard format (corpus, queries, qrels) into which datasets are converted. The README lists preprocessed datasets and marks four (BioASQ, Signal-1M, TREC-NEWS, Robust04) as not directly downloadable, with reproduction instructions {C021}.

## 4 Experimental setup

**Systems.** Ten systems from five families were evaluated from public pre-trained checkpoints, and neural models read only the first 512 word pieces of each document {C004}. Table 2 lists the reported settings.

**Table 2. Systems and reported configuration** {C004}

| Family | System | Reported configuration |
|---|---|---|
| Lexical | BM25 | Anserini (Yang et al., 2017), k=0.9, b=0.4, title and passage as separate fields |
| Sparse | DeepCT | bert-base-uncased on MS MARCO; BM25 defaults |
| Sparse | SPARTA | re-implemented (original not public); DistilBERT on MS MARCO; 2,000 non-zero entries |
| Sparse | docT5query | T5 (base) on MS MARCO; 40 generated queries per document; BM25 |
| Dense | DPR | Multi model, bert-base-uncased, trained on NQ, TriviaQA, WebQuestions, CuratedTREC |
| Dense | ANCE | RoBERTa on MS MARCO, 600K steps |
| Dense | TAS-B | topic-aware sampling; Margin-MSE plus in-batch negatives; cross-encoder and ColBERT supervision |
| Dense | GenQ | TAS-B fine-tuned per dataset on 5 synthetic queries per document; corpus capped at 100K documents |
| Late interaction | ColBERT | bert-base-uncased, MS MARCO, 300K steps; faiss ANN depth 100, then re-scoring |
| Re-ranking | BM25+CE | top-100 BM25 hits re-scored by a 6-layer 384-h MiniLM cross-encoder, best of 14 public cross-encoders on MS MARCO |

In the authors' tests, the DPR Multi model beat the single-NQ model, and Anserini BM25 beat Elasticsearch BM25 and Anserini with RM3 expansion {C004}. Most systems are trained on MS MARCO (532,761 training pairs), which is why it is treated as in-domain; DPR is the exception {C004}.

**Experiments and questions.** X1 (RQ1, RQ2): zero-shot evaluation of all ten systems on the 18 datasets, with MS MARCO scores as the in-domain reference. X2 (RQ2): the length of retrieved documents for TAS-B and ANCE, plus a controlled comparison of two identically trained models that differ only in similarity function. X3 (RQ2): latency and index size on a random sample of 1 million DBPedia documents, on an 8-core Intel Xeon Platinum 8168 CPU at 2.70GHz and one Nvidia Tesla V100 GPU; dense models use exact search and ColBERT approximate nearest-neighbour search {C016}. X4 (RQ3): for each system on TREC-COVID, Hole@10 (the share of its top-10 hits that no annotator judged); the authors then judged the missing pairs following the original guidelines, unaware of which system retrieved them, and recomputed nDCG@10 {C017} {C018}. TREC-COVID's labels come from pooling, which judges the union of documents returned by many participating systems (Voorhees et al., 2021), a method the authors describe as intended to reduce this kind of bias {C019}.

## 5 Results

### 5.1 RQ1: does in-domain accuracy predict zero-shot accuracy?

Table 3 gives nDCG@10 for every system and dataset. Its column layout was damaged in extraction and reconstructed by cross-checking against values quoted in the text; the paper's marks for best scores were lost {L005}.

**Table 3. nDCG@10 (MS MARCO is in-domain for systems trained on it, not DPR; NQ is in-domain for DPR)** {C005}

| Dataset | BM25 | DeepCT | SPARTA | docT5query | DPR | ANCE | TAS-B | GenQ | ColBERT | BM25+CE |
|---|---|---|---|---|---|---|---|---|---|---|
| MS MARCO | 0.228 | 0.296 | 0.351 | 0.338 | 0.177 | 0.388 | 0.408 | 0.408 | 0.401 | 0.413 |
| TREC-COVID | 0.656 | 0.406 | 0.538 | 0.713 | 0.332 | 0.654 | 0.481 | 0.619 | 0.677 | 0.757 |
| BioASQ | 0.465 | 0.407 | 0.351 | 0.431 | 0.127 | 0.306 | 0.383 | 0.398 | 0.474 | 0.523 |
| NFCorpus | 0.325 | 0.283 | 0.301 | 0.328 | 0.189 | 0.237 | 0.319 | 0.319 | 0.305 | 0.350 |
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
| Avg. vs. BM25 | | -27.9% | -20.3% | +1.6% | -47.7% | -7.4% | -2.8% | -3.6% | +2.5% | +11% |

*What would count against the expectation.* If in-domain accuracy predicted generalization, systems beating BM25 on MS MARCO would also beat it on the 18 datasets. *What happened.* On MS MARCO, BM25 scored 0.228 and the trained neural systems 0.296 to 0.413, 7 to 18 points higher {C005}. On the zero-shot datasets, the paper's summary row (average performance relative to BM25; the formula is not defined in the text) places DeepCT at -27.9%, SPARTA at -20.3%, ANCE at -7.4%, TAS-B at -2.8% and GenQ at -3.6%, and DPR, which was not trained on MS MARCO, at -47.7% {C005}. Only docT5query (+1.6%), ColBERT (+2.5%) and BM25+CE (+11%) averaged above BM25, so most systems fell below the word-matching baseline {C007}. DeepCT and SPARTA are the clearest reversals: both improved on BM25 in-domain (0.296 and 0.351 against 0.228) and fell below it on nearly all zero-shot datasets {C008}.

*Robustness and meaning.* The reversal appears for four separately built systems, so it is not one outlier, but every score is a single evaluation and the systems differ in more than architecture {L005} {L008}. In this comparison in-domain accuracy therefore did not predict zero-shot accuracy, and the authors conclude that models fine-tuned on identical data can generalize differently and that methods should be evaluated on many datasets {C006}. This answers RQ1 negatively for these systems; it does not show that in-domain accuracy is uninformative in general, since ten systems and one training set were tested.

### 5.2 RQ2 (effectiveness): which architectures generalize best?

*Re-ranking, late interaction and expansion.* Table 3 shows BM25+CE above BM25 on 16 of 18 datasets, docT5query on 11 of 18 and ColBERT on 9 of 18 {C007}. The two BM25+CE shortfalls are negative results that qualify its ranking: ArguAna (0.311 versus 0.315) and Touché-2020 (0.271 versus 0.367), which the authors describe as tasks extremely different from the MS MARCO training data {C008}. They read the strength of BM25+CE and ColBERT as suggesting that cross-attention and cross-attention-like operations matter for out-of-distribution generalization {C014}; this is a low-confidence interpretation, since no ablation removes the operation and the systems differ in many other ways {L010}. DeepCT and SPARTA, which learn term weights, fail to generalize, whereas docT5query, which adds keywords by generating queries, is competitive {C008}.

*Dense systems and domain adaptation.* TAS-B outperformed ANCE on 14 of 18 datasets and DPR on 17 of 18, and DPR generalized worst {C009}. Dense models underperformed BM25 under large domain shift, as on BioASQ (BM25 0.465; ANCE 0.306; TAS-B 0.383), and under task shift, as on Touché-2020 {C009}. The authors speculate that TAS-B's training setup, combining in-batch negatives with the Margin-MSE loss and strong teacher models, explains its advantage; this is untested {C015}. GenQ outperformed TAS-B on specialized domains (TREC-COVID 0.619 versus 0.481; CQADupStack 0.347 versus 0.314) and was weaker on Wikipedia-based datasets (NQ 0.358 versus 0.463); the pattern is not uniform, since on the scientific dataset SCIDOCS it scored 0.143 against 0.149 {C010}. In this comparison adaptation helped in some specialized domains and cost accuracy on broad ones, with the caveat that GenQ used at most 100K documents per corpus {L008}.

*Length preference.* TAS-B scored 17.3 points below ANCE on TREC-COVID and 7.8 points below on Touché-2020 {C011}. The two models retrieve documents of very different length: median top-10 length on TREC-COVID was 10 words for TAS-B versus 160 for ANCE, and on Touché-2020 14 versus 89 {C011}. On TREC-COVID about 42k of 171k documents are titles without an abstract, and TAS-B retrieved many of them. To test whether the similarity function alone can change such a preference, the authors trained two distilbert-base-uncased models identically on MS MARCO except for cosine similarity versus dot product (Table 4). The cosine model retrieved shorter documents on all datasets {C012}.

**Table 4. Cosine versus dot-product similarity, otherwise identical models (nDCG@10)** {C012}

| Dataset | Cosine | Dot product |
|---|---|---|
| TREC-COVID | 0.482 | 0.635 |
| Signal-1M | 0.261 | 0.243 |
| FEVER | 0.670 | 0.685 |

The dot-product model gained 15.3 points on TREC-COVID, lost 1.8 on Signal-1M and gained 1.5 on FEVER; the text adds that on a majority of other datasets it performed worse, but those values are unavailable {C012} {L012}. One design choice can thus change retrieved length and accuracy, and the better choice depends on the task, since in Touché-2020 longer documents receive higher relevance labels {C012}. It leaves open whether the similarity function accounts for the TAS-B and ANCE gap, because those models also differ in backbone, loss and negative mining {C013} {L010}.

### 5.3 RQ2 (cost): what do the best systems cost?

Re-ranking and late interaction were the slowest systems, needing more than 350 ms per query, whereas dense retrievers were 20-30x faster (below 20ms) and on CPU sparse models took 20-25ms {C016}. For 1 million DBPedia documents, the index of BM25, docT5query, DeepCT and BM25+CE was 0.4GB, of DPR, ANCE, TAS-B and GenQ 3GB, of SPARTA 12GB (a 30k-dimensional sparse vector per document) and of ColBERT 20GB (several 128-dimensional vectors per document) {C016}. At larger scale the gap grows: for BioASQ, with about 15M documents, ColBERT needs about 900GB against 18GB for BM25 {C016}. These figures come from one corpus sample and one hardware configuration {L007}. Taken with Section 5.2, these figures suggest that the two best-averaging systems, BM25+CE and ColBERT, are also the most costly at inference, whereas docT5query, the third system above BM25, has a BM25-sized index, and the cheaper dense and sparse retrievers often fell below BM25 {C024}.

### 5.4 RQ3: are the relevance labels fair to non-lexical systems?

Datasets are labeled by judging a limited pool of candidates returned by some retrieval systems, and unjudged documents are assumed irrelevant. This is a source of selection bias (Lipani, 2019): a system that returns different documents than the pool's systems is penalized for hits nobody looked at. The authors report that many BEIR datasets were built with lexical retrieval: BioASQ candidates came from term matching (Tsatsaronis et al., 2015), and seven of eight techniques used for Signal-1M rely on lexical term matching (Suarez et al., 2018) {C019}. They measured the effect on TREC-COVID, whose pool comes from many participating systems {C019}.

Hole@10 ranged from 1.6% for BM25+CE and 2.8% for docT5query to 31.8% for TAS-B and 30.6% for DPR {C017}. The authors then judged 980 query-document pairs and recomputed nDCG@10 (Table 5) {C018}.

**Table 5. TREC-COVID: Hole@10 and nDCG@10 before and after annotating holes** {C017} {C018}

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

Lexical systems changed little (docT5query 0.713 to 0.714). ANCE rose from 0.654, slightly below BM25, to 0.735, which is 6.7 points above BM25, and the authors report a similar improvement for ColBERT (5.8 points) {C018}. The gain tracks the hole size: TAS-B and DPR, with about 31% holes, rose by 7.4 and 11.3 points, while BM25+CE, with 1.6%, moved by 0.3, which is consistent with unjudged hits explaining part of the dense systems' deficit {C018}. The authors conclude that even a pool contributed by many systems remains biased toward lexical approaches, and they expect the same mechanism elsewhere, though only TREC-COVID was measured {C019} {L006}. This answers RQ3 for TREC-COVID: the labels understated non-lexical systems. It does not show the size of the effect in other datasets, and the annotation was done by the authors without reported agreement statistics {L006}.

## 6 Discussion

**Answers to the research questions.** RQ1: in-domain accuracy did not predict zero-shot accuracy, since several systems that beat BM25 on MS MARCO averaged below it on BEIR {C006}. RQ2: no single approach was best on every dataset; re-ranking, late interaction and document expansion generalized best on average, and the two best averaging systems were the slowest {C024}. RQ3: on TREC-COVID, unjudged hits fell mainly on dense systems and annotating them raised their scores, so labels built from lexical pools can understate non-lexical systems {C019}.

**Mechanisms, with caution.** Three explanations are offered: cross-attention-like scoring supports generalization {C014}, TAS-B's loss and teachers explain its lead among dense models {C015}, and length preference may account for part of TAS-B's gap to ANCE {C013}. None was tested by removing the suspected factor, so they are hypotheses and not findings {L010}. The label-bias result also bears on RQ2: part of the dense systems' deficit on TREC-COVID may be a measurement effect, since annotation moved ANCE from 0.654 to 0.735 {C018} {C019}. This reading is limited to the one re-annotated dataset {L006}.

**Relation to later work.** The README points to a later publication (Kamalloo et al., 2024) with reproducible reference implementations for learned dense and sparse models and meta-analyses of effect sizes across datasets; its abstract says that BEIR comparisons reduce heterogeneous scores to a single average that is difficult to interpret {C022}. This matches a caveat here: the summary row in Section 5.1 is one number over 18 datasets, so per-dataset counts and Table 3 should be read alongside it {L009}.

**Implications.** For an unseen domain, BM25 is a hard baseline to beat without target-domain training data, and gains from re-ranking or late interaction carry the costs shown in Section 5.3 {C024}. For dataset builders, the authors argue that labels should be pooled from diverse systems, which is easier when many systems sit in one framework {C023}.

## 7 Limitations

- **Single evaluations, no variance {L005}.** Each system was scored once from a public checkpoint, with no seeds, intervals or tests. Only large or consistent patterns (the BM25+CE win count, the DeepCT and SPARTA reversal, the Hole@10 spread) are interpreted; differences such as 0.643 versus 0.644 on SciFact are not {C005} {C007} {C009} {C010}.
- **Confounded systems {L008}.** Systems differ in backbone, training data, negative mining and corpus caps, SPARTA was re-implemented, and total compute is not reported, so conclusions about families concern these checkpoints {C006} {C009} {C024}.
- **Undefined average {L009}.** The summary row's formula is not given {C005} {C007}.
- **One-dataset bias study {L006}.** Hole analysis covers TREC-COVID only, and the authors annotated the pairs themselves {C018} {C019}.
- **Efficiency on one sample {L007}.** Latency and index sizes come from 1 million DBPedia documents on one CPU and one GPU type {C016}.
- **Untested mechanisms {L010}.** The cross-attention, training-loss and length-preference explanations are hypotheses {C013} {C014} {C015}.
- **Benchmark scope {L001} {L002} {L003} {L004}.** All datasets are English, long documents are not covered and neural models read the first 512 word pieces, only text search over one or two fields is tested, and task-specific models are excluded {C001} {C004}.
- **Second-hand literature {L011}.** Related-work statements and the diversity analysis rest on the authors' descriptions and unigram overlap {C002} {C020}.

## 8 Conclusion

BEIR asks how retrieval systems behave when no training data exist for the target task, and answers with 18 English datasets from nine tasks and ten public systems from five families {C001} {C004}. In this comparison, accuracy on the training-domain dataset did not predict zero-shot accuracy, BM25 remained a strong baseline, and only re-ranking, late interaction and document expansion averaged above it {C005} {C006} {C007}. The two best averaging systems were the slowest, and on TREC-COVID the labels understated dense systems {C024} {C019}. The practical lesson is to evaluate retrievers on many datasets, read averages with per-dataset results, and check how labels were pooled. The main boundaries are single evaluations without variance, one re-annotated dataset and untested explanations {L005} {L006} {L010}. The authors name datasets built from diverse pools, and multilingual, long-document and multi-field tasks, as next steps {C023}. BEIR is released at https://github.com/UKPLab/beir {C021}.

## References

Berger, A. et al. (2000). Bridging the lexical chasm: statistical approaches to answer-finding. SIGIR 2000.
Dai, Z. et al. (2020). Context-Aware Term Weighting For First Stage Passage Retrieval. SIGIR 2020.
Guo, M. et al. (2020). MultiReQA: A Cross-Domain Evaluation for Retrieval Question Answering Models.
Hofstätter, S. et al. (2021). Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling. SIGIR.
Ioffe, S. (2010). Improved consistent sampling, weighted minhash and l1 sketching. IEEE ICDM 2010.
Kamalloo, E. et al. (2024). Resources for Brewing BEIR: Reproducible Reference Models and Statistical Analyses. SIGIR 2024.
Karpukhin, V. et al. (2020). Dense Passage Retrieval for Open-Domain Question Answering. EMNLP 2020.
Khattab, O. et al. (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. SIGIR 2020.
Liang, D. et al. (2020). Embedding-based Zero-shot Retrieval through Query Generation.
Lipani, A. (2019). On Biases in Information retrieval models and evaluation. Ph.D. thesis, TU Wien.
Ma, J. et al. (2021). Zero-shot Neural Passage Retrieval via Domain-targeted Synthetic Question Generation.
Nguyen, T. et al. (2016). MS MARCO: A Human Generated MAchine Reading COmprehension Dataset.
Nogueira, R. et al. (2019). From doc2query to docTTTTTquery. Online preprint.
Petroni, F. et al. (2020). KILT: a Benchmark for Knowledge Intensive Language Tasks.
Reimers, N. et al. (2020). The Curse of Dense Low-Dimensional Information Retrieval for Large Index Sizes. arXiv:2012.14210.
Robertson, S. et al. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. Foundations and Trends in Information Retrieval, 3(4).
Suarez, A. et al. (2018). A Data Collection for Evaluating the Retrieval of Related Tweets to News Articles. ECIR 2018.
Tsatsaronis, G. et al. (2015). An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition. BMC Bioinformatics, 16(1).
Van Gysel, C. et al. (2018). Pytrec_eval: An Extremely Fast Python Interface to trec_eval. SIGIR.
Voorhees, E. et al. (2021). TREC-COVID: Constructing a Pandemic Information Retrieval Test Collection. SIGIR Forum, 54(1).
Wang, W. et al. (2020). MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers. NeurIPS 2020.
Wang, Y. et al. (2013). A theoretical analysis of NDCG ranking measures. COLT 2013.
Xiong, L. et al. (2020). Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval.
Yang, P. et al. (2017). Anserini: Enabling the Use of Lucene for Information Retrieval Research. SIGIR 2017.
Zhao, T. et al. (2021). SPARTA: Efficient Open-Domain Question Answering via Sparse Transformer Matching Retrieval. NAACL 2021.
