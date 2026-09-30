# Reader reconstruction self-test (from draft only, tags ignored)

Q1 Problem: neural retrieval models are trained and tested on one dataset, but are often used zero-shot; their behavior there is unclear (Abstract; Sec 1 para 2).
Q2 Why it matters: retrieval is the first stage of QA, claim verification and duplicate detection; training data are costly (Sec 1 paras 1-2).
Q3 Missing: earlier benchmarks are single-task, single-domain or small-corpus, as characterized by the authors (Sec 1 para 3; Sec 2).
Q4 What they did: BEIR with 18 datasets and 9 tasks scored with nDCG@10; 10 systems from 5 families; latency and index size; TREC-COVID re-annotation (Sec 1 para 4; Secs 3-4).
Q5 Why this method: selection criteria (diversity, difficulty, annotation strategies), one rank-aware metric, public checkpoints. Why exactly these ten systems is not given by the authors beyond "diverse, recent"; the paper says nothing more (M009). Partial by design.
Q6 Experiments: X1-X4 in Sec 4, each mapped to RQs.
Q7 Strongest results: in-domain did not predict zero-shot; BM25+CE +11%, ColBERT +2.5%, docT5query +1.6%; 16/18 wins; cost; Hole@10 1.6%-31.8% and ANCE 0.654 to 0.735 (Sec 5; Abstract).
Q8 Establishes: for these ten checkpoints the ranking differs in-domain vs zero-shot; label bias on TREC-COVID.
Q9 Does not establish: that in-domain accuracy never predicts generalization; causes (cross-attention, loss, length); bias size elsewhere; whether small differences are real (Secs 5.1, 5.2, 5.4, 7).
Q10 Contribution: benchmark + comparison + accuracy-cost picture + label-bias analysis (Sec 1 list).
Q11 Limitations: Sec 7.
Q12 One-day memory: zero-shot ranking differs from in-domain; BM25 is strong; the best-averaging systems cost most; labels can understate non-lexical systems.

Result: all 12 answerable from the draft. Mismatches with spine: none. Q5 partial by design.
