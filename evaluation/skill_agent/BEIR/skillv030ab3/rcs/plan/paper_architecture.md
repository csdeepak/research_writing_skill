# Paper Architecture: BEIR (presented to adjacent ML researchers)

Story pattern: question_led · Audience mode B · Binding personas A, B, E · Venue profile: plan/venue_profile.yaml (all rules assumed)
Length limit (main text): 4500 · Planned total: 3720 words prose + 4 tables (<= 90% of limit including tables)

| # | Section | Story nodes | Reader question | Point | Claims | Density | Visual | New terms | Words |
|---|---------|-------------|-----------------|-------|--------|---------|--------|-----------|-------|
| A.1 | Abstract | N01-N23 | whole spine | stand-alone miniature | C043 C032 C040 C052 | CORE | - | BEIR, zero-shot | 200 |
| I.1 | Introduction | N01 N02 | What is the problem, why care? | retrieval, zero-shot, cost of training data | C001 C002 | CORE | - | retrieval, corpus, query, zero-shot | 130 |
| I.2 | Introduction | N03 N04 N05 | What is missing? | prior evaluation same-dataset; prior benchmarks narrow | C003 C004 C005 | CORE | - | benchmark | 120 |
| I.3 | Introduction | N06 N07 N08 | What is asked? | RQ1-RQ3 | C056 | CORE | - | - | 80 |
| I.4 | Introduction | N09 N10 | What was done, why? | BEIR + design reasons | C010 C020 C022 | CORE | - | - | 70 |
| I.5 | Introduction | N23 | Contributions | four numbered contributions with pointers | C020 C021 C043 C052 | CORE | - | - | 80 |
| B.1 | Background | N03 N30 | What is BM25, lexical gap, five families? | families by where scoring happens | C006 | CORE | - | BM25, lexical gap, bi-encoder, cross-encoder | 200 |
| B.2 | Background | N04 | How do prior benchmarks differ? | dimensions: task, domain, corpus size | C005 | SUPPORTING | - | - | 120 |
| M.1 | Benchmark | N10 | What datasets, why these? | 18/9, four selection factors | C010 C020 | CORE | TAB-1 | qrels, relevance judgement | 200 |
| M.2 | Benchmark | N10 | Are they really different? | weighted Jaccard low overlap | C023 C024 | SUPPORTING | - | - | 80 |
| M.3 | Benchmark | N10 N30 | Which metric, why? | nDCG@10 | C011 | CORE | - | nDCG | 120 |
| M.4 | Benchmark | N10 | What does the package give? | format, wrappers | C021 | SUPPORTING | - | - | 70 |
| S.1 | Setup | N11 | Which systems, how configured? | ten systems, MS MARCO training, choices | C022 C014 C015 C012 C013 | CORE | - | - | 260 |
| S.2 | Setup | N12 N13 N14 | Other experiments | efficiency, annotation study, cos/dot | C016 C017 C040 | CORE | - | pooling, hole | 170 |
| R.1 | Results | N15 | RQ1 in-domain vs zero-shot | MS MARCO vs BEIR | C030 C044 | CORE | TAB-2 | - | 150 |
| R.2 | Results | N15 | RQ2 which families | BM25+CE, ColBERT, docT5query, learned sparse, dense | C031-C036 C043 | CORE | TAB-2 | - | 330 |
| R.3 | Results | N15 N18 | Why dense differ | TAS-B vs ANCE lengths, cos vs dot, GenQ | C037 C038 C039 | CORE | - | - | 220 |
| R.4 | Results | N16 | RQ2 cost | latency/index | C040 | CORE | TAB-3 | - | 110 |
| R.5 | Results | N17 | RQ3 annotation bias | Hole@10; re-annotation | C041 C042 | CORE | TAB-4 | - | 150 |
| D.1 | Discussion | N19-N22 | Answers to RQs | RQ1-RQ3, mechanisms typed | C044-C052 | CORE | - | - | 380 |
| L.1 | Limitations | N24 N25 N26 | What do the authors concede? | L001-L013 | L001-L013 | CORE | - | - | 260 |
| L.2 | Limitations | N27 | Additional caveats | writer-derived | L101-L108 | CORE | - | - | 140 |
| C.1 | Conclusion | N23 N28 N29 | What now? | synthesis | C043 C052 C053 C054 | CORE | - | - | 130 |

Checks: every RQ has results (R.1-R.5), interpretation and discussion rows; every author_stated limitation has row L.1; every rationale claim has an Introduction/Setup row (I.4, M.1, M.3, S.1, S.2); Table numbering by order; question debt 0 (forward pointers only in I.5).
Planned term introductions precede first use (retrieval and zero-shot in I.1; BM25 and lexical gap in B.1; qrels in M.1; nDCG in M.3; pooling and hole in S.2 before R.5).
