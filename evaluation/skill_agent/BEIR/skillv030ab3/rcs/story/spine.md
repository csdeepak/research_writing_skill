# Paper spine

1. Problem: Neural retrieval models are usually trained and tested on the same dataset, so how they behave on other domains and tasks (where no training data exist) is unknown, although zero-shot use is common because training data are costly. {C001} {C002} {C004}
2. Gap: The benchmarks the paper cites cover a single task or domain, small corpora or Wikipedia only, so they cannot compare retrieval systems zero-shot across many tasks and domains. {C003} {C005}
3. Question: Does in-domain performance predict zero-shot performance, which architectures hold up across heterogeneous datasets and at what computational cost, and does relevance annotation treat non-lexical systems fairly? {C056}
4. Approach: BEIR collects 18 English datasets from 9 retrieval tasks in one format with software, and evaluates ten systems from five architecture families zero-shot with nDCG@10, plus latency, index size and a manual re-annotation of TREC-COVID. {C020} {C021} {C022}
5. Key finding: No system wins on every dataset and BM25 remains a strong baseline; BM25+CE (16 of 18 datasets above BM25) and ColBERT (9 of 18) are best on average but slowest, while learned sparse and dense systems that beat BM25 in-domain often fall below it zero-shot. {C043} {C032} {C040}
6. Meaning: In-domain scores do not order systems as zero-shot scores do, and part of the dense systems' shortfall on TREC-COVID reflects missing relevance judgements (ANCE 0.654 to 0.735 after annotation). {C044} {C052}
7. Main limit: Results are single runs on English text-only datasets without variance estimates, and the TREC-COVID pool remains lexically biased, so score differences between systems are not backed by intervals. {L007} {L001} {L011}
