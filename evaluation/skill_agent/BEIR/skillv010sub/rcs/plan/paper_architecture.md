# Paper Architecture: BEIR for adjacent ML researchers

Story pattern: question_led
Audience mode: B (adjacent ML researcher) - Binding personas: A, B, E - Venue profile: plan/venue_profile.yaml (assumed rules: structure, limits partly from task instructions [assumed:false], style from task instructions [assumed:false], required_statements not reached this run)

Each row is one paragraph slot. Word targets are approximate; see plan/skeleton.md for the sentence-level pass.

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Link forward |
|---|---------|---------------|--------------------------|----------------------|--------|---------|--------|-----------|--------------|
| AB.1 | Abstract | N01,N02,N05,N06 | What's the problem and question? | Zero-shot generalization across retrieval tasks/domains is untested by existing broad evaluations | C020 | CORE | - | zero-shot retrieval | leads to approach |
| AB.2 | Abstract | N08 | What did you do? | Built BEIR (18 datasets/9 tasks/1 format/1 metric) and evaluated 10 systems from 5 architecture families | C021 | CORE | - | - | leads to findings |
| AB.3 | Abstract | N10,N11 | What did you find? | BM25 robust; no architecture dominates; re-ranking/late-interaction best but slowest; several dense/sparse systems underperform | C001,C004,C008,C015 | CORE | - | - | leads to bias finding |
| AB.4 | Abstract | N15,N16 | Any caveat on the comparison itself? | Lexically-pooled annotation understates non-lexical systems' true performance | C018 | CORE | - | - | leads to meaning |
| AB.5 | Abstract | N11,L007(scope) | What does it mean, and what's the boundary? | In-domain accuracy is a poor generalization proxy; findings bounded to English, short/medium text | C003 | CORE | - | - | Introduction |
| I.1 | Introduction | N01 | What is the problem? | Retrieval models are usually trained/tested on one dataset, leaving zero-shot performance elsewhere unknown | - | CORE | - | zero-shot / out-of-domain (OOD) retrieval {N23} | why it matters |
| I.2 | Introduction | N02 | Why does it matter? | Building labeled data for every new domain is costly, so deployments often rely on zero-shot transfer that is currently unverified | - | CORE | - | - | what's missing |
| I.3 | Introduction | N03 | What's already known? | Neural rankers show large gains over BM25, but only when trained and tested on the same large dataset | C001(partial, in-domain half) | CORE | - | BM25 {N26} | leads to gap |
| I.4 | Introduction | N04,N05 | What's missing? | The two existing broad retrieval evaluations each cover one task type or lean on Wikipedia-scale corpora, so no evaluation compares architectures zero-shot across many tasks/domains at once | C020 | CORE | - | - | the question |
| I.5 | Introduction | N06 | What exactly do you ask? | RQ1: how well, and via what mechanism, do systems from 5 architecture families generalize zero-shot, relative to BM25? | - | CORE | - | - | the approach |
| I.6 | Introduction | N08 | What did you do? | Built BEIR and evaluated 10 systems zero-shot on 18 datasets under one format/metric | C021 | CORE | - | - | contributions |
| I.7 | Introduction | N17 | What do you contribute? | Three contributions: the benchmark/software; the comparative finding about generalization and cost; the annotation-bias case study | C021,C019,C018 | CORE | - | - | paper map |
| I.8 | Introduction | (map) | Where is this going? | Paper map by question (Related Work -> Benchmark -> Systems -> RQ1 results -> RQ2 case study -> Discussion) | - | CORE | - | - | Related Work |
| RW.1 | Related Work | N03,N04 | Why isn't an existing evaluation enough? | MultiReQA is limited to sentence-level QA over mostly-Wikipedia, mostly-small corpora | C020 | CORE | - | - | KILT |
| RW.2 | Related Work | N04 | And KILT? | KILT spans more tasks but retrieves only from Wikipedia and treats retrieval as secondary | C020 | CORE | - | - | architecture families |
| RW.3 | Related Work | (background) | What kinds of retrieval systems exist? | Five architecture families are compared: lexical, sparse, dense, late-interaction, re-ranking | - | SUPPORTING | - | lexical/sparse/dense/late-interaction/re-ranking {N24} | Benchmark section |
| BM.1 | The BEIR Benchmark | N08 | How were tasks/datasets chosen? | Four selection criteria: diverse tasks, diverse domains, sufficient difficulty, diverse annotation strategies | C021 | CORE | - | - | what resulted |
| BM.2 | The BEIR Benchmark | N08 | What resulted? | 18 datasets across 9 tasks, standardized into one format (corpus/queries/qrels) | C021 | CORE | Table 1 | pooling {N27} | scale |
| BM.3 | The BEIR Benchmark | N08 | How big/varied is it? | Corpus sizes 3.6k-15M docs; query/doc lengths 3-192/11-635 words; 8/19 have training data | C021 | CORE | (Table 1 cont.) | - | domain diversity |
| BM.4 | The BEIR Benchmark | N08 | Are the domains actually different? | Domain overlap is generally low, concentrated within shared-domain dataset pairs | C022 | SUPPORTING | - | - | metric choice |
| BM.5 | The BEIR Benchmark | N09(req) | Why one metric, and which? | nDCG@10 chosen to compare binary and graded relevance judgements on the same scale | - | CORE | - | nDCG@10 {N25} | systems compared |
| SY.1 | Retrieval Systems Compared | N08(req) | What are the 5 families, concretely? | One system per family (plus 3 extra dense variants) is evaluated, all mostly trained on MS MARCO | C021 | CORE | - | bi-encoder, cross-encoder, hard/in-batch negatives | per-family description |
| SY.2 | Retrieval Systems Compared | E010,E048 | Lexical/sparse: what exactly? | BM25 (no training); DeepCT and SPARTA learn term weights/representations on top of BM25; docT5query expands documents with generated queries | - | CORE | - | document expansion | dense systems |
| SY.3 | Retrieval Systems Compared | E050,E051,E052,E053 | Dense: what exactly? | DPR, ANCE, TAS-B are bi-encoders differing in negatives/loss; GenQ adapts TAS-B with synthetic in-domain queries | - | CORE | - | - | late-interaction/re-ranking |
| SY.4 | Retrieval Systems Compared | E054,E055 | Late-interaction/re-ranking: what exactly? | ColBERT keeps token-level vectors compared at query time; BM25+CE re-ranks BM25's top-100 with a cross-attention model | - | CORE | - | - | shared setup |
| SY.5 | Retrieval Systems Compared | E009,E032 | What's held constant across systems? | All documents truncated to 512 word pieces; efficiency measured on a shared 1M-document DBPedia sample and shared hardware | - | SUPPORTING | - | - | Results |
| R1.1 | Results: Generalization | N06(echo) | What question does this answer? | RQ1 restated: how do the 10 systems rank zero-shot against BM25, and does in-domain performance predict it? | C001 | CORE | Table: avg vs BM25 | - | headline result |
| R1.2 | Results: Generalization | N10,N11 | Does in-domain success transfer? | BM25 trails neural systems in-domain by 7-18 points but is a strong zero-shot baseline; no architecture dominates all 18 datasets | C001,C002,C003 | CORE | (table) | - | the winners |
| R1.3 | Results: Generalization | N10 (C004,C005) | Which systems generalize best? | Re-ranking (+11%, 16/18) and late-interaction (+2.5%, 9/18) generalize best, failing mainly on the two most MS-MARCO-dissimilar tasks | C004,C005 | CORE | - | - | the cost |
| R1.4 | Results: Generalization | N10 (C015,C016) | At what cost? | The best generalizers are also slowest (>350ms) and (for ColBERT) largest to index; dense/sparse are far cheaper | C015,C016 | CORE | - | - | the strugglers |
| R1.5 | Results: Generalization | N10 (C006,C008) | Which systems struggle, and why is that informative? | Term-reweighting sparse methods and most dense bi-encoders underperform BM25 on average despite strong in-domain scores; DPR worst overall | C006,C008 | CORE | - | - | the exception |
| R1.6 | Results: Generalization | N10 (C007,C009) | Any exceptions among the cheaper families? | docT5query (sparse) and TAS-B (dense) buck their families' trend and generalize comparatively well | C007,C009 | CORE | - | - | a specific failure mode |
| R1.7 | Results: Generalization | C011,C012,C013 | Why does TAS-B sometimes lose to a weaker-average system? | TAS-B underperforms ANCE specifically on two datasets, tied to a document-length preference partly traced to the similarity function | C011,C012,C013 | SUPPORTING | - | - | domain adaptation |
| R1.8 | Results: Generalization | C014 | Does adapting to the target domain help? | GenQ's synthetic-query adaptation helps specialized domains but hurts broad/generic ones relative to its base model | C014 | SUPPORTING | - | - | interpretation |
| R1.9 | Results: Generalization | N11 | So what explains the ranking? | Robust generalization tracks cross-attention(-like) interaction more than embedding architecture, at a compute cost {answers RQ1} | C019 | CORE | - | - | RQ2 |
| R2.1 | Bias Case Study | N12,N13 | Could the RQ1 ranking itself be distorted? | Some BEIR test collections were pooled mainly from lexical systems, which could make non-lexical systems look artificially worse | - | CORE | - | Hole@k | the test |
| R2.2 | Bias Case Study | N14 | How was this tested? | On TREC-COVID: measure each system's Hole@10, then manually judge the 980 missing pairs blind to source system | - | CORE | - | - | the result |
| R2.3 | Bias Case Study | N15 (C017) | What did Hole@10 show? | Lexical systems' top hits were mostly already judged (6.4%/2.8% missing); non-lexical systems' were not (up to 31.8%) | C017 | CORE | Table: Hole@10 | - | after re-annotation |
| R2.4 | Bias Case Study | N15 (C018) | What happened after fixing the gap? | Lexical scores barely moved; non-lexical scores rose substantially (ANCE +8 points, ColBERT +5.8) | C018 | CORE | (table cont.) | - | the qualified conclusion |
| R2.5 | Bias Case Study | N16 | What does this establish, and what not? | Confirms lexical pooling bias measurably affects this comparison on this dataset; does not overturn the overall RQ1 ranking, but qualifies it {answers RQ2} | C018 | CORE | - | - | Discussion |
| D.1 | Discussion | N06,N11 | Answer to RQ1? | In-domain accuracy does not predict zero-shot generalization; interaction mechanism matters more than embedding family, at a cost | C003,C019 | CORE | - | - | RQ2 answer |
| D.2 | Discussion | N13,N16 | Answer to RQ2? | Annotation pooling bias is real and measurable, but is a qualification of specific comparisons, not a reversal of the overall ranking | C018 | CORE | - | - | implications |
| D.3 | Discussion | N21 | What follows for practice/research? | Report zero-shot/cross-domain results as standard practice; build future test collections with diverse pooling | C019,C018 | CORE | - | - | limitations |
| Lim.1 | Limitations | N18 | What's out of scope? | English-only, mostly-short documents, text-only signals, single/dual-field only | L001-L004 | CORE | - | - | scope of ranking |
| Lim.2 | Limitations | N19 | What else bounds the ranking? | Generalist-only comparison; no error bars; compute not fully reported | L005-L007 | CORE | - | - | bias-study scope |
| Lim.3 | Limitations | N20 | How far does the bias finding reach? | Measured on one dataset (TREC-COVID); argued, not measured, elsewhere in BEIR | L008 | CORE | - | - | Conclusion |
| C.1 | Conclusion | N17 | What is now understood/available that wasn't before? | BEIR gives one standardized way to measure zero-shot retrieval generalization across tasks/domains | C021 | CORE | - | - | key boundary |
| C.2 | Conclusion | N11,N16 | What changed in understanding? | In-domain accuracy misleads about generalization; part of the apparent gap for non-lexical systems is a measurement artifact | C003,C018 | CORE | - | - | future |
| C.3 | Conclusion | N22 | What's next? | Multilingual/long-document/multi-field extensions and more diverse pooling for future test collections | - | CORE | - | - | (end) |

## Checks (ticked before Gate G2)
- [x] Every story-graph node N01-N28 appears in >=1 row above (background nodes N23-N27 appear via "New terms" column at their first-use row; N28 appears via RW.1/RW.2's citations feeding into R2.1's setup).
- [x] RQ1 (N06) has result rows (R1.1-R1.9), interpretation rows (R1.9, D.1), and discussion rows (D.1, D.3).
- [x] RQ2 (N13) has result rows (R2.1-R2.5), interpretation row (R2.5), and discussion row (D.2, D.3).
- [x] No row without a story node, except SY.1-SY.5 which implement N08's `requires` background edges (architecture taxonomy) -- justified: methods detail rows always attach to the APPROACH node's requirements.
- [x] Question ledger: no planned debt beyond intro forward-references (see story/question_ledger.json).
- [x] Term ledger: every term's defining row precedes its first-use row (see story/term_ledger.json).
- [x] Visuals: dataset-statistics table (BM.2), zero-shot-summary table (R1.1), Hole@10/before-after table (R2.3) each have a card in plan/figure_cards/.
- [x] No SUPPLEMENTARY items planned (paper has no separate appendix/supplement per venue_profile.yaml `supplement_allowed: false`); OPTIONAL/SUPPLEMENTARY-density source material (Appendix E licenses, F/G formula derivations, per-dataset method minutiae) is not included in any row, consistent with information_design.md §2.
- [x] Negative results placed: E017/E019/E020 -> R1.5; E026 -> R1.7 (per claims/claim_evidence_map.json negative_result_decisions, all `reported_main`).
