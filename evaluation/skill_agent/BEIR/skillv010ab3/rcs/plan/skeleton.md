# Skeleton (one sentence per slot)
I.1 Retrieval finds the documents that downstream NLP systems read, and many deployments must use it on tasks with no training data, yet retrieval models are usually judged on the dataset they were trained on {C006}.
I.2 Earlier benchmarks that touch retrieval cover one task, one domain or small corpora, so they cannot show how retrieval architectures generalize {C002}.
I.3 We therefore ask three questions: does in-domain accuracy predict zero-shot accuracy (RQ1), which architectures generalize best and at what cost (RQ2), and are relevance labels fair to non-lexical systems (RQ3) {C006} {C024} {C019}.
I.4 The authors build BEIR from 18 English datasets over nine tasks and evaluate ten public systems from five families {C001} {C004}.
I.5 The contributions are the benchmark, the finding that in-domain accuracy does not predict zero-shot accuracy, the accuracy-cost picture, and the label-bias analysis on TREC-COVID {C007} {C024} {C019} {C021}.
B.1 Lexical retrieval scores documents by shared words (BM25); neural systems differ in how they represent queries and documents: sparse, dense, late interaction, re-ranking {C004}.
B.2 MultiReQA and KILT are the two benchmarks the authors compare with {C002}.
D.1 Datasets were chosen for diverse tasks, domains, difficulty and annotation strategies {C001}.
D.2 The result is 18 datasets over nine tasks with very different corpus and text lengths {C001}.
D.3 Word overlap between datasets from different domains is low {C020}.
D.4 Every dataset is scored with nDCG@10 because it handles ranking and graded labels {C003}.
D.5 BEIR ships as open-source software with a standard format {C021}.
S.1 Ten systems from five families are evaluated from public checkpoints {C004}.
S.2 Key training and configuration details differ across systems, and neural systems read 512 word pieces {C004}.
S.3 Each experiment is tied to one research question {C004}.
R.1 In-domain MS MARCO ranks the neural systems above BM25, but the zero-shot averages do not {C005} {C006}.
R.2 BM25+CE, ColBERT and docT5query outperform BM25 on 16, 9 and 11 of 18 datasets, and DeepCT and SPARTA fail {C007} {C008}.
R.3 Among dense models TAS-B generalizes best, DPR worst, and GenQ helps in specialized domains and hurts on Wikipedia {C009} {C010}.
R.4 TAS-B retrieves much shorter documents than ANCE, and a similarity-function change alone shifts length and accuracy {C011} {C012} {C013}.
R.5 The most effective systems are the slowest and have the largest indexes {C016}.
R.6 Filling unjudged hits on TREC-COVID barely changes lexical systems but lifts dense ones {C017} {C018} {C019}.
X.1 RQ1: no; RQ2: no single winner and a cost trade-off; RQ3: labels favour lexical systems on TREC-COVID {C006} {C024} {C019}.
X.2 Cross-attention and training loss are hypothesized explanations, not tested {C014} {C015}.
X.3 Later work by others argues for effect-size analyses across datasets {C022}.
L.1 Limitations: single evaluations, one-dataset bias study, English, truncation, confounded systems {L005} {L006} {L001} {L002} {L008}.
Z.1 Zero-shot ranking differs from in-domain ranking, effectiveness and cost trade off, and fairer datasets are needed {C024} {C023}.
