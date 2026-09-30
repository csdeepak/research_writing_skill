# Skeleton (one topic sentence per paragraph slot)

**Abstract.** Learned-ownership routing cut LLM tokens per query by 22.1% on a constructed corpus, at a small accuracy cost in every measured seed, and adapted to a new topic without retraining, but it is a routing tool and not a question-answering method {C001, C007, C009, C015}.

**I.1** A team of LLM agents with a shared memory must decide whom to ask, global search is costly, and ASMOS learns owners from verified outcomes {C033, C032}.
**I.2** The gap is a missing measurement of saving, cost and adaptation, so we ask four questions and check one boundary {C032}.
**I.3** The contributions are a token saving, an accuracy accounting, a consistent-with ablation, new-topic adaptation and two scope-setting results {C001, C007, C005, C009, C015, C030}.
**I.4** Sections follow the questions.

**R.1** Context is organized by routing, answering and adaptation, with no novelty claim and no verified citations {C032, C009}.

**M.1** ASMOS keeps checkpoints in a shared store and routes on similarity times ownership {C038, C032}.
**M.2** A2 freezes ownership and A3 routes on similarity alone {C005, C004}.
**M.3** The corpus is constructed with 50 queries, gpt-4o-mini and 10 seeds {C033, C034, C001}.
**M.4** We report tokens, accuracy, answerability and route@1 {C007, C008}.
**M.5** The statistics follow the authors' stated reasons {C025, C026, C027, C028}.
**M.6** Adaptation runs use a new topic, two embedders and three classifier baselines {C009, C010, C029}.
**M.7** Static question answering compares four systems once on 24 items {C013}.

**S.1** Routing to a learned owner used 22.1% fewer tokens per query {C001, C004}.
**S.2** The interval is 17.9% to 26.3%, set by queries, not seeds {C001, C002, C003}.
**S.3** This answers RQ1 for this corpus and model only {C001, C036}.
**S.4** Answerability was equal but accuracy was lower in every seed {C006, C007}.
**S.5** So the saving is not at equal accuracy {C006, C007, C008}.
**S.6** Freezing ownership removes almost all of the saving, which is consistent with ownership evolution {C004, C005}.
**S.7** With a new topic ASMOS reaches regret 3.24 and 0.92 with 0 retrains {C009, C010}.
**S.8** The result depends on the embedder and does not extend to the degraded embedder {C009, C010, C011, C012}.
**S.9** ASMOS-memory scores below No-Memory and RAG on static question answering {C013, C014, C015, C037}.
**S.10** The stored effect size was wrong and is superseded; W, p and the interval did not move {C030}.

**D.1** RQ1 to RQ4 are answered at the strengths above {C001, C007, C005, C009}.
**D.2** Learned ownership sits between global and similarity routing, with an untested explanation {C004, C006, C005}.
**D.3** It is a candidate cost tool within the limits, and not evidence for question-answering quality {C001, C009, C015}.

**L.1** The authors concede the query-set interval, the constructed corpus, the QA scope and the metric gaps {L001, L004, L003, L002}.
**L.2** They also concede a withheld convergence test, descoped items, in-corpus tuning, embedders and the CI artifact {L005, L006, L007, L008, L009, L010}.
**L.3** Additional caveats: absent files, ungraded accuracy, no A1 versus A2 test, undocumented tuning, small regimes {L011-L020}.

**C.1** Routing saved 22.1% at a small accuracy cost, on a constructed corpus, and does not improve static question answering {C001, C007, C005, C009, C015}.
