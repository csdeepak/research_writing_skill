# Paper Architecture: BEIR (audience mode B)

Story pattern: question_led. Audience mode: B. Binding personas: A, B, E. Venue profile: plan/venue_profile.yaml (generic). Word budget: about 4,100 total (tables included).

| # | Section | Nodes | Reader question answered | Point | Claims | Density | Visual | New terms | Link forward |
|---|---------|-------|--------------------------|-------|--------|---------|--------|-----------|--------------|
| I.1 | 1 Introduction | N01,N02 | What is the problem and why care? | Retrieval is the first stage of many NLP pipelines, models trained on one dataset get used on tasks without training data | C006 | CORE | - | retrieval, query, document, zero-shot | why existing benchmarks do not tell us |
| I.2 | 1 | N03,N04 | What is missing? | Earlier benchmarks are single-task/domain | C002 | CORE | - | lexical vs neural retrieval | so we ask |
| I.3 | 1 | N05-N07 | What exactly do you ask? | RQ1-RQ3 | C006,C024,C019 | CORE | - | in-domain | how we answer |
| I.4 | 1 | N08,N09 | What did you do? | BEIR and ten systems | C001,C004 | CORE | - | - | findings |
| I.5 | 1 | N21 | What do you contribute? | Contribution list with results | C007,C024,C019,C021 | CORE | - | - | paper map |
| B.1 | 2 Background | N27 | What must I know? | Lexical retrieval and BM25, neural families | C004 | CORE | - | BM25, sparse, dense, late interaction, re-ranking | benchmark |
| B.2 | 2 | N03 | Related benchmarks | MultiReQA and KILT | C002 | SUPPORTING | - | - | design |
| D.1 | 3 Benchmark | N09 | How chosen? | Selection criteria | C001 | CORE | - | - | tasks |
| D.2 | 3 | N09 | What is in it? | 18 datasets, 9 tasks | C001 | CORE | Table 1 | relevance judgments (qrels) | diversity |
| D.3 | 3 | N09 | Is it diverse? | word overlap | C020 | SUPPORTING | - | weighted Jaccard | metric |
| D.4 | 3 | N09 | How scored? | nDCG@10 | C003 | CORE | - | nDCG@10 | software |
| D.5 | 3 | N09 | Can I use it? | software | C021 | SUPPORTING | - | - | setup |
| S.1 | 4 Setup | N10 | Which systems? | five families | C004 | CORE | Table 2 (systems) | - | training details |
| S.2 | 4 | N10 | How trained/configured? | key details | C004 | SUPPORTING | - | - | experiments |
| S.3 | 4 | N10-N12 | Which experiment answers which RQ? | plan | C004 | CORE | Table 2 (plan, merged) | - | results |
| R.1 | 5.1 Results RQ1 | N13,N18 | Does in-domain predict zero-shot? | No, in this comparison | C005,C006 | CORE | Table 3 (nDCG) | - | which architectures |
| R.2 | 5.2 RQ2 | N14 | Which generalize? | re-ranking, ColBERT, docT5query | C007,C008 | CORE | - | - | dense |
| R.3 | 5.2 | N15 | Dense and adaptation | TAS-B, DPR, GenQ | C009,C010 | CORE | - | - | why |
| R.4 | 5.2 | N15 | Length preference | length, cosine vs dot | C011,C012,C013 | SUPPORTING | Table 4 | - | cost |
| R.5 | 5.3 Cost | N16 | What does it cost? | latency/index | C016 | CORE | Table 5 | ANN | labels |
| R.6 | 5.4 RQ3 | N17,N20 | Are labels fair? | holes | C017,C018,C019 | CORE | Table 6 | Hole@10, pooling | discussion |
| X.1 | 6 Discussion | N18-N20 | Answer to each RQ | RQ1-RQ3 | C006,C024,C019 | CORE | - | - | mechanism |
| X.2 | 6 | N19 | Why? | cross-attention, loss | C014,C015,C013 | SUPPORTING | - | - | prior work |
| X.3 | 6 | N26 | Related | later work | C022 | SUPPORTING | - | - | limits |
| L.1 | 7 Limitations | N22-N24 | What bounds the claims? | triples | L001-L012 | CORE | - | - | conclusion |
| Z.1 | 8 Conclusion | N21,N25 | What now? | synthesis, future | C024,C023 | CORE | - | - | - |

## Checks
- [x] Every story node appears in >=1 row (N02 in I.1, N27 in B.1, N25 in Z.1, N26 in X.3)
- [x] Every RQ has results (R.1, R.2-R.5, R.6), interpretation and discussion rows (X.1)
- [x] Question ledger: no planned debt beyond 3 introduction forward references
- [x] Term ledger: defining rows precede first use
- [x] Visuals have cards
- [x] Negative results (E015, E017, E023) placed in main text (R.2, R.3)
