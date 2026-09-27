# Paper Spine

**Problem:** Neural information retrieval models are routinely trained and evaluated on a single in-domain dataset (typically MS MARCO), giving no reliable signal about how well they generalize to new tasks or domains. {C001}

**Gap:** No broad, heterogeneous zero-shot evaluation benchmark exists for information retrieval; prior multi-dataset benchmarks (MultiReQA, KILT) cover a single task type or a single domain (Wikipedia), and neither evaluates zero-shot generalization systematically. {C002}

**Question:** How well do state-of-the-art neural retrieval architectures—lexical, sparse, dense, late-interaction, and re-ranking—generalize to out-of-distribution retrieval tasks and domains when given no in-domain training data? {C003}

**Approach:** Build BEIR: 18 publicly available retrieval datasets across 9 task types and diverse domains; define a unified evaluation protocol using nDCG@10; evaluate 10 retrieval systems of five architecture types; analyse efficiency trade-offs; and study annotation selection bias. {C004}

**Key finding:** In-domain performance (MS MARCO) does not predict zero-shot generalization: BM25—which underperforms neural models by 7–18 nDCG points in-domain—becomes a strong zero-shot baseline that many neural models fail to beat; re-ranking (BM25+CE) and late-interaction (ColBERT) generalize best on average (+11% and +2.5% vs BM25), but at high computational cost, while dense models frequently underperform BM25. {C005}

**Meaning:** Existing neural retrieval training and evaluation practice systematically overstates generalization capability; BEIR exposes this gap and provides the community with a standard benchmark for developing truly generalizable retrieval systems. {C006}

**Main limit:** All datasets are English-only; annotation pools for several datasets were constructed with lexical methods, introducing a selection bias that underestimates non-lexical model performance; document truncation at 512 word-pieces disadvantages long-document retrieval. {C007, L001}
