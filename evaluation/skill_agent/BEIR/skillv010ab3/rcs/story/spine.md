# Paper spine

1. Problem: Neural retrieval models are usually trained and tested on the same dataset, yet many real applications have no training data for their target task, so it is unknown how well these models work zero-shot on new tasks and domains {C006}.
2. Gap: Earlier retrieval benchmarks cover a single task or domain, or small corpora, so they cannot show how retrieval architectures generalize out of distribution {C002}.
3. Question: How do lexical, sparse, dense, late-interaction and re-ranking retrieval systems compare zero-shot across heterogeneous tasks and domains, at what computational cost, and how trustworthy are the existing relevance labels for judging non-lexical systems {C024}?
4. Approach: We assemble BEIR, 18 English datasets from 9 retrieval tasks scored with nDCG@10, evaluate ten public systems from five families, measure latency and index size, and re-annotate unjudged top-10 hits on TREC-COVID {C001} {C003} {C004}.
5. Key finding: In-domain accuracy on MS MARCO did not predict zero-shot accuracy: BM25 remained a strong baseline, re-ranking with a cross-encoder was + 11% relative to BM25 on average, and most dense and sparse models fell below BM25 on average {C005} {C007} {C009}.
6. Meaning: Retrieval methods need broad evaluation, the systems that generalize best cost the most to run, and lexical bias in the labels can understate non-lexical systems {C024} {C019}.
7. Main limit: Each system was evaluated once from public checkpoints without variance, the label-bias study covers one dataset, and mechanistic explanations remain untested {L005} {L006} {L010}.
