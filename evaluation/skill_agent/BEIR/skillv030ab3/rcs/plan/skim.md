# Skim sheet (generated; claim text verbatim, do not paraphrase here)

## 30-second outline (paper spine)

- 1. Problem: Neural retrieval models are usually trained and tested on the same dataset, so how they behave on other domains and tasks (where no training data exist) is unknown, although zero-shot use is common because training data are costly. {C001} {C002} {C004}
- 2. Gap: The benchmarks the paper cites cover a single task or domain, small corpora or Wikipedia only, so they cannot compare retrieval systems zero-shot across many tasks and domains. {C003} {C005}
- 3. Question: Does in-domain performance predict zero-shot performance, which architectures hold up across heterogeneous datasets and at what computational cost, and does relevance annotation treat non-lexical systems fairly? {C056}
- 4. Approach: BEIR collects 18 English datasets from 9 retrieval tasks in one format with software, and evaluates ten systems from five architecture families zero-shot with nDCG@10, plus latency, index size and a manual re-annotation of TREC-COVID. {C020} {C021} {C022}
- 5. Key finding: No system wins on every dataset and BM25 remains a strong baseline; BM25+CE (16 of 18 datasets above BM25) and ColBERT (9 of 18) are best on average but slowest, while learned sparse and dense systems that beat BM25 in-domain often fall below it zero-shot. {C043} {C032} {C040}
- 6. Meaning: In-domain scores do not order systems as zero-shot scores do, and part of the dense systems' shortfall on TREC-COVID reflects missing relevance judgements (ANCE 0.654 to 0.735 after annotation). {C044} {C052}
- 7. Main limit: Results are single runs on English text-only datasets without variance estimates, and the TREC-COVID pool remains lexically biased, so score differences between systems are not backed by intervals. {L007} {L001} {L011}

## Findings in one sentence each

- The authors motivate zero-shot evaluation by the cost of training data: creating a large training corpus is time-consuming and expensive, so many retrieval systems are applied zero-shot. {C001}
- The authors state that it is unclear how well trained neural retrieval models perform on other text domains or tasks, and how sparse versus dense embeddings behave on out-of-distribution data. {C002}
- According to the BEIR paper, most prior work evaluates neural retrievers on the same dataset they were trained on (for example Natural Questions or MS MARCO), where gains over BM25 are reported. {C004}
- The authors motivate BEIR by the narrowness of prior evaluation: prior retrieval benchmarks focus on a single task or domain, and neural retrievers have been studied in homogeneous, narrow settings. {C003}
- The BEIR paper describes two earlier benchmarks: MultiReQA (eight question-answering datasets, sentence-level answers, five of eight from Wikipedia, small candidate pools) and KILT (five knowledge-intensive tasks, eleven datasets, retrieval not the primary task, Wikipedia only). {C005}
- The paper asks (i) whether in-domain performance predicts zero-shot performance, (ii) which architectures hold up across heterogeneous datasets, (iii) at what computational cost, and (iv) whether relevance annotation treats non-lexical systems fairly. {C056}
- BEIR has 18 English zero-shot datasets from 9 retrieval tasks, ranging from 3.6k to 15M documents, with average query lengths of 3 to 192 words and average document lengths of 11 to 635 words; 8 of the 19 datasets (counting MS MARCO) have training data. {C020}
- BEIR supplies a standard data format (corpus, queries, qrels), a Python package (pip install beir) with wrappers for existing retrieval toolkits and IR metrics, and a planned leaderboard; the README lists 17 preprocessed datasets, four of which are not public and come with reproduction instructions. {C021}
- Ten public systems from five architecture families are evaluated: lexical (BM25), sparse (DeepCT, SPARTA, docT5query), dense (DPR, ANCE, TAS-B, GenQ), late-interaction (ColBERT) and re-ranking (BM25+CE). {C022}
- No single system has the highest zero-shot score on every dataset; BM25 remains a strong baseline, with BM25+CE (16 of 18) the one system scoring above it on nearly all datasets, while the two best systems on average (BM25+CE and ColBERT) are the most costly. {C043}
- BM25+CE scores higher than BM25 on 16 of 18 zero-shot datasets and falls below it on exactly two, ArguAna (0.311 vs 0.315) and Touche-2020 (0.271 vs 0.367). {C032}
- On 1M DBPedia documents the estimated single-query latency is 450 ms on GPU and 6100 ms on CPU for BM25+CE, 350 ms on GPU for ColBERT, 14 ms on GPU for TAS-B and 20 ms on CPU for BM25; index sizes are 20GB for ColBERT, 12GB for SPARTA, 3GB for dense models and 0.4GB for BM25. For BioASQ (~15M documents) ColBERT needs ~900GB and BM25 18GB. {C040}
- The MS MARCO in-domain ordering of systems does not match their zero-shot ordering (BM25 is last in-domain among MS-MARCO-trained systems yet above most of them zero-shot), which the authors take to mean that in-domain performance does not predict zero-shot performance; the paper gives no correlation statistic. {C044}
- The authors conclude that the TREC-COVID annotation pool, although built from many systems, still favours lexical approaches and disadvantages non-lexical ones, so part of the dense retrievers' shortfall there reflects missing judgements. {C052}

## Figure takeaways

