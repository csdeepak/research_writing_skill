# Skeleton (one topic sentence per slot)
A.1 BEIR is a benchmark that tests retrieval systems zero-shot on 18 datasets; no system wins everywhere, BM25 stays strong, the best systems are the slowest, and labels favour lexical systems. {C043}{C032}{C040}{C052}
I.1 Retrieval finds relevant documents for a query, and neural retrievers are usually trained and tested on one dataset, although many deployments have no training data. {C001}{C002}
I.2 Prior work evaluates on the training dataset and prior benchmarks are narrow, so zero-shot behaviour across tasks is untested. {C004}{C003}{C005}
I.3 The paper asks three questions: does in-domain performance predict zero-shot; which architectures hold up at what cost; is annotation fair to non-lexical systems. {C056}
I.4 The authors built BEIR from 18 datasets and evaluated ten systems, choosing datasets for task, domain, difficulty and annotation diversity. {C010}{C020}{C022}
I.5 Contributions: the benchmark and software; the ten-system comparison; the cost analysis; the annotation-bias study. {C020}{C021}{C043}{C052}
B.1 Lexical retrieval such as BM25 matches words and suffers a lexical gap; five neural families differ in where query and document interact. {C006}
B.2 Earlier benchmarks differ from BEIR on task count, domain and corpus size. {C005}
M.1 BEIR contains 18 datasets from 9 tasks chosen for four reasons. {C020}{C010}
M.2 Weighted Jaccard overlap between domains is low. {C023}{C024}
M.3 A single metric, nDCG@10, is used because it handles graded relevance and rank. {C011}
M.4 The package provides a common format and wrappers. {C021}
S.1 Ten systems from five families, mostly trained on MS MARCO, with recorded configuration reasons. {C022}{C014}{C015}{C012}{C013}
S.2 Three further experiments: efficiency, annotation holes, cosine versus dot product. {C016}{C017}{C040}
R.1 In-domain MS MARCO ordering differs from zero-shot ordering. {C030}{C044}
R.2 BM25+CE, ColBERT and docT5query lead; DeepCT, SPARTA, DPR fall below BM25. {C031}{C032}{C033}{C034}{C035}{C036}{C043}
R.3 TAS-B and ANCE retrieve documents of different lengths tied to similarity function; GenQ helps specialised domains only. {C037}{C038}{C039}
R.4 The best systems are the slowest and largest. {C040}
R.5 Holes differ by system; filling them lifts ANCE from 0.654 to 0.735. {C041}{C042}
D.1 The answers to RQ1-RQ3 with typed mechanisms. {C044}{C045}{C046}{C047}{C048}{C049}{C052}
L.1 Authors concede scope, variance, compute, pool bias limits. {L001}{L007}{L011}
L.2 Additional caveats. {L101}{L103}
C.1 Synthesis and next steps. {C043}{C052}{C053}{C054}
