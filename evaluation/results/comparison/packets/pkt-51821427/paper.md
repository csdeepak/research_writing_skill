# BEIR: A Heterogeneous Benchmark for Zero-Shot Evaluation of Information Retrieval Models

*This paper presents, for readers from adjacent machine-learning subfields, the benchmark and findings originally reported by Thakur, Reimers, Rücklé, Srivastava, and Gurevych (Ubiquitous Knowledge Processing Lab, TU Darmstadt).*

## Abstract

Neural retrieval systems are usually trained and evaluated on a single dataset, so it is unclear how well they generalize to other tasks and domains without further training — a zero-shot setting many real deployments require. Existing broad evaluations do not resolve this: the closest prior efforts, MultiReQA and KILT, are each limited to one task type or lean heavily on Wikipedia-scale corpora. We address this gap with BEIR, a benchmark unifying 18 datasets across 9 heterogeneous retrieval tasks into one data format and metric (nDCG@10), and use it to compare 10 systems spanning five architecture families: lexical, sparse, dense, late-interaction, and re-ranking. No single architecture dominates, and BM25 — despite trailing neural systems in-domain by 7–18 nDCG@10 points — remains a strong zero-shot baseline. Re-ranking and late-interaction systems generalize best (11% and 2.5% average improvement over BM25) but are the slowest and, for one system, the most memory-intensive to index, while several dense and sparse systems underperform BM25 on average despite strong in-domain scores. A case study on TREC-COVID further shows that lexically biased annotation pools understate non-lexical systems' true zero-shot performance by several points of nDCG@10. Together, these results suggest that in-domain accuracy is a poor predictor of zero-shot generalization, that robust generalization tracks query–document interaction mechanisms more than embedding architecture, and that some apparent weakness of non-lexical retrieval is itself a measurement artifact. Findings are bounded to English-language, short-to-medium-length text retrieval.

## 1. Introduction

A retrieval system ranks the documents most relevant to a query out of a large collection. Most recent progress on this problem comes from fine-tuning a pretrained Transformer encoder, such as BERT (Devlin et al., 2018), on one large labeled dataset — typically MS MARCO (Nguyen et al., 2016) or Natural Questions (Kwiatkowski et al., 2019) — and evaluating it on that same dataset. Deployed systems, however, are routinely pointed at problems the model never saw in training: a new product's documentation, a specialized literature, a different news archive. In each case the system runs zero-shot, receiving no training data for the task and domain it now must handle. Because building labeled data for every new domain is slow and expensive, this untested zero-shot setting is often the only realistic option, and it is exactly what in-domain evaluation does not check.

Under in-domain evaluation, neural rankers show large, well-documented gains over classical lexical scoring functions such as BM25 (Robertson and Zaragoza, 2009), which ranks documents by weighted term overlap with the query rather than by any learned representation. Whether those gains survive outside the training domain is much less established. The two evaluations that span more than one retrieval dataset do not settle this. MultiReQA compares systems on eight question-answering datasets at sentence level; five of the eight are Wikipedia-based, and six of the eight are small enough (under 100,000 candidate sentences) to structurally favor dense retrieval over lexical matching (Guo et al., 2020). KILT spans five knowledge-intensive tasks and eleven datasets, but retrieves only from Wikipedia and treats retrieval as a supporting step rather than the measured capability (Petroni et al., 2020). Neither compares retrieval architectures — lexical, sparse, dense, late-interaction, re-ranking — zero-shot across many task types and domains at once.

This leaves a basic question open: across diverse retrieval tasks and domains, how well do systems from different architectures generalize with no in-domain training data, relative to BM25, and what explains the differences? A second question follows from how test collections are built: because judging every possible query–document pair is infeasible, only the candidates some existing system retrieves are ever judged, and if that system is lexical, the resulting judgements could be biased against non-lexical systems in exactly this comparison.

We address both questions with BEIR (Benchmarking-IR). We select 18 datasets spanning 9 retrieval tasks and domains, convert them into one standardized data format, and score every system with one metric, nDCG@10. We then evaluate ten systems, drawn from five architecture families and mostly trained on MS MARCO, zero-shot on all 18 datasets, and separately profile their latency and index size. To test whether the comparison is itself distorted by how test collections are annotated, we measure and manually correct annotation gaps on one dataset, TREC-COVID.

This paper makes three contributions: BEIR itself, 18 datasets across 9 tasks unified into one open-source evaluation framework; a comparative study showing that in-domain accuracy does not predict zero-shot generalization, that cross-attention-like interaction between query and document generalizes best but at higher computational cost, and that BM25 remains a strong, low-cost baseline; and a case study showing some test collections are annotated in a way that disadvantages non-lexical systems, understating their true performance.

Section 2 gives background on retrieval architectures. Section 3 describes how BEIR's datasets were selected and standardized. Section 4 describes the ten systems compared. Section 5 answers the first question: how they generalize zero-shot and at what cost. Section 6 answers the second question with the TREC-COVID case study. Section 7 discusses what both results establish, and Section 8 states the main limitations.

## 2. Background: Retrieval Architectures

To our knowledge, BEIR is the first benchmark to compare retrieval architectures zero-shot across this many task types and domains at once, against the two prior broad evaluations discussed above (Guo et al., 2020; Petroni et al., 2020).

Retrieval systems fall into five families, distinguished by how they represent and compare queries and documents. **Lexical** systems, e.g. BM25 (Robertson and Zaragoza, 2009), score a document by weighted term overlap with the query and need no training; their weakness is the lexical gap, missing relevant documents that share no vocabulary with the query (Berger et al., 2000). **Sparse** systems keep a lexical, inverted-index backend but use a trained model to re-weight or expand a document's terms before indexing. **Dense** systems embed query and document independently into a shared vector space with a bi-encoder — two encoders, often sharing weights, that never attend to each other — and rank by vector similarity, pre-computing document vectors at the cost of compressing each document into one vector. **Late-interaction** systems keep a separate vector per token instead of per document, comparing many token pairs at a larger index cost. **Re-ranking** systems shortlist candidates with a first-stage retriever (usually BM25), then re-score only that list with a cross-encoder — a model that encodes query and document jointly, letting every token attend to every other; this cross-attention is the most expressive of the five, affordable only because it runs on a short list, not the whole collection.

## 3. The BEIR Benchmark

Assembling a benchmark that fairly tests generalization requires more than collecting many datasets. BEIR's selection follows four criteria: *diverse tasks* (query/document length varying widely, from keyword queries to full news articles, from single sentences to book-length collections); *diverse domains* (from broad domains such as Wikipedia or news to specialized ones such as a single scientific field, reflecting real problems rather than one kind of text); *sufficient task difficulty* (a task any simple method already solves does not usefully compare systems); and *diverse annotation strategies* (since annotation choices can themselves bias a comparison, Section 6, datasets come from several different processes — crowd-sourced, expert-annotated, and derived from large online communities' own feedback).

Applying these criteria yields 18 zero-shot evaluation datasets across 9 retrieval tasks: bio-medical search, open-domain question answering, tweet retrieval, news retrieval, argument retrieval, duplicate-question retrieval, entity retrieval, citation prediction, and fact-checking (Table 1). Each dataset, whatever its original file format, is converted into the same standard structure: a document corpus, a set of queries, and a query-relevance file (qrels) recording which documents are relevant to which query.

| Task | Domain | Dataset | Test Queries | Corpus | Rel. Docs/Query | Query Words | Doc Words |
|---|---|---|---|---|---|---|---|
| Bio-medical IR | Bio-medical | TREC-COVID (Voorhees et al., 2021) | 50 | 171,332 | 493.5 | 10.60 | 160.77 |
| Bio-medical IR | Bio-medical | NFCorpus (Boteva et al., 2016) | 323 | 3,633 | 38.2 | 3.30 | 232.26 |
| Bio-medical IR | Bio-medical | BioASQ (Tsatsaronis et al., 2015) | 500 | 14,914,602 | 4.7 | 8.05 | 202.61 |
| Question answering | Wikipedia | NQ (Kwiatkowski et al., 2019) | 3,452 | 2,681,468 | 1.2 | 9.16 | 78.88 |
| Question answering | Wikipedia | HotpotQA (Yang et al., 2018) | 7,405 | 5,233,329 | 2.0 | 17.61 | 46.30 |
| Question answering | Finance | FiQA-2018 (Maia et al., 2018) | 648 | 57,638 | 2.6 | 10.77 | 132.32 |
| Tweet retrieval | Twitter | Signal-1M(RT) (Suarez et al., 2018) | 97 | 2,866,316 | 19.6 | 9.30 | 13.93 |
| News retrieval | News | TREC-NEWS (Soboroff et al., 2019) | 57 | 594,977 | 19.6 | 11.14 | 634.79 |
| News retrieval | News | Robust04 (Voorhees, 2005) | 249 | 528,155 | 69.9 | 15.27 | 466.40 |
| Argument retrieval | Misc. | ArguAna (Wachsmuth et al., 2018) | 1,406 | 8,674 | 1.0 | 192.98 | 166.80 |
| Argument retrieval | Misc. | Touché-2020 (Bondarenko et al., 2020) | 49 | 382,545 | 19.0 | 6.55 | 292.37 |
| Duplicate-question | StackExchange | CQADupStack (Hoogeveen et al., 2015) | 13,145 | 457,199 | 1.4 | 8.59 | 129.09 |
| Duplicate-question | Quora | Quora | 10,000 | 522,931 | 1.6 | 9.53 | 11.44 |
| Entity retrieval | Wikipedia | DBPedia (Hasibi et al., 2017) | 400 | 4,635,922 | 38.2 | 5.39 | 49.68 |
| Citation prediction | Scientific | SCIDOCS (Cohan et al., 2020) | 1,000 | 25,657 | 4.9 | 9.38 | 176.19 |
| Fact checking | Wikipedia | FEVER (Thorne et al., 2018) | 6,666 | 5,416,568 | 1.2 | 8.13 | 84.76 |
| Fact checking | Wikipedia | Climate-FEVER (Diggelmann et al., 2020) | 1,535 | 5,416,593 | 3.0 | 20.13 | 84.76 |
| Fact checking | Scientific | SciFact (Wadden et al., 2020) | 300 | 5,183 | 1.1 | 12.37 | 213.63 |

*Table 1. The 18 BEIR zero-shot evaluation datasets. Corpus size and text length vary by orders of magnitude across the nine tasks. Values are as reported in the source study.*

The datasets vary by design: corpus size ranges from 3,633 documents (NFCorpus) to nearly 15 million (BioASQ); query length from 3.30 words (NFCorpus) to 192.98 (ArguAna, whose "queries" are themselves full arguments); document length from 11.44 words (Quora) to 634.79 (TREC-NEWS). Only 8 of these 18 datasets, plus MS MARCO, provide any training data, underscoring that most of this evaluation is necessarily zero-shot.

A benchmark of superficially different datasets could still share most of its vocabulary, so word overlap between every pair was measured with a weighted Jaccard similarity over unigram frequencies. Overlap is generally low, and concentrated among datasets sharing a source domain: two Wikipedia-derived datasets, DBPedia and HotpotQA, overlap at about 0.89, versus about 0.13 between DBPedia and the biomedical NFCorpus. A system cannot rely on shared vocabulary alone to transfer across most of BEIR's 18 datasets.

A single metric comparable across binary and graded relevance judgements is also needed: Precision and Recall ignore rank order, and Mean Reciprocal Rank and Mean Average Precision cannot score graded judgements. Normalised Discounted Cumulative Gain at rank 10 (nDCG@10) scores both, crediting a relevant document more when it ranks higher among the top 10 results (Wang et al., 2013), so it is used throughout.

## 4. Retrieval Systems Compared

Ten systems were evaluated, one to four per architecture family, summarized alongside the main results in Table 2. With one exception — DPR, trained on four question-answering datasets including NQ — every system is trained on MS MARCO, so a zero-shot performance difference mostly reflects architecture and training procedure rather than the training dataset.

BM25 (Robertson and Zaragoza, 2009) needs no training. Two sparse systems try to close part of the lexical gap while keeping BM25's inverted-index backend: DeepCT learns, with a fine-tuned BERT model, a per-term weight used to build a re-weighted pseudo-document retrieved with BM25 (Dai and Callan, 2020); SPARTA learns contextualized token representations converted into a large, 30,000-dimensional but sparse per-document vector (Zhao et al., 2021). docT5query instead generates synthetic queries a document is likely to answer with a sequence-to-sequence model, appends them to the document, and retrieves with ordinary BM25 over the expanded text (Nogueira and Lin, 2019).

Four systems are dense bi-encoders, embedding query and document independently and comparing their vectors. DPR trains with one hard negative mined from BM25 plus in-batch negatives (Karpukhin et al., 2020). ANCE mines hard negatives from an approximate-nearest-neighbor index that is itself continually updated during training (Xiong et al., 2020). TAS-B combines in-batch negatives with a distillation loss against a cross-encoder and a late-interaction teacher (Hofstätter et al., 2021); the authors attribute its comparatively strong generalization, speculatively, to this training setup rather than to the bi-encoder architecture itself. GenQ pushes domain adaptation further: for each target dataset, a sequence-to-sequence model generates synthetic queries for that dataset's documents, and TAS-B is further fine-tuned on these synthetic pairs — so, unlike the other nine systems, GenQ trains a different model per target dataset.

The remaining two systems keep more query–document interaction than a single vector allows. ColBERT represents query and document as bags of token-level vectors, scores a pair with a sum of per-query-token maximum similarities, and retrieves via an approximate-nearest-neighbor search re-scored with the full interaction score (Khattab and Zaharia, 2020). BM25+CE re-ranks BM25's top 100 candidates with a cross-encoder — a compact, six-layer MiniLM model (Wang et al., 2020) — that lets every query token attend to every document token before producing one relevance score.

Every system truncates each document to the same 512 word pieces, the limit set by the underlying Transformer encoders; retrieval latency and index size are measured on the same one-million-document sample and the same CPU/GPU hardware (Section 5).

## 5. Results: Zero-Shot Generalization Across Architectures

The first question is simple to state and, given the decades of research behind BM25, not obvious to answer: does any more sophisticated architecture reliably beat the lexical baseline with no in-domain training data at all? Table 2 summarizes each system's in-domain nDCG@10 on MS MARCO and its average zero-shot change relative to BM25 across the 18 datasets; no seed or replicate variance is available for either column, since most systems are third-party pre-trained checkpoints without accessible retraining code.

| System | Family | MS MARCO (in-domain) | Avg. zero-shot Δ vs. BM25 |
|---|---|---|---|
| BM25 | Lexical | 0.228 | — (reference) |
| DeepCT | Sparse | 0.296 | −27.9% |
| SPARTA | Sparse | 0.351 | −20.3% |
| docT5query | Sparse | 0.338 | +1.6% |
| DPR | Dense | 0.177 | −47.7% |
| ANCE | Dense | 0.388 | −7.4% |
| TAS-B | Dense | 0.408 | −2.8% |
| GenQ | Dense | 0.408 | −3.6% |
| ColBERT | Late-interaction | 0.401 | +2.5% |
| BM25+CE | Re-ranking | 0.413 | +11% |

*Table 2. In-domain score and average zero-shot change vs. BM25 (nDCG@10) for all 10 evaluated systems. No replicate/seed variance is available for these figures.*

In-domain, BM25 trails every neural system on MS MARCO by 7–18 nDCG@10 points. Zero-shot, the picture largely reverses: BM25 is beaten on average by only three of the nine other systems, and no architecture beats it on every one of the 18 datasets. In-domain accuracy, in other words, does not predict zero-shot generalization: systems fine-tuned on the same MS MARCO data end up on opposite sides of the BM25 baseline once evaluated outside that domain.

The two systems that keep the most query–document interaction generalize best. BM25+CE, the cross-encoder re-ranker, improves on BM25 by 11% on average and beats it on 16 of the 18 datasets, failing only on ArguAna and Touché-2020 — the two argument-retrieval tasks least like MS MARCO's short web queries. ColBERT improves by 2.5% on average and beats BM25 on 9 of the 18. That generalization is not free: on a shared one-million-document sample, BM25+CE's re-ranking and ColBERT's late-interaction scoring are both slowest at inference, over 350 milliseconds per query, while dense bi-encoders are 20–30 times faster (under 20ms) and sparse systems are fastest of all on CPU (20–25ms). ColBERT's index is also the largest of the ten, storing several 128-dimensional vectors per document rather than one; at BioASQ's roughly 15-million-document scale this is estimated at about 900GB, versus about 18GB for BM25.

At the other end, several systems that scored well in-domain generalize poorly. DeepCT and SPARTA both do well on MS MARCO but underperform BM25 on nearly every dataset, averaging 27.9% and 20.3% below it. Among the dense bi-encoders, DPR — the one system not trained on MS MARCO — generalizes worst overall; ANCE and TAS-B also underperform BM25 on average, by 7.4% and 2.8%.

Two systems buck their family's trend. docT5query is the only sparse system to generalize well, beating BM25 on 11 of the 18 datasets (+1.6% on average) — plausibly because, unlike DeepCT and SPARTA's learned re-weighting, its generated queries add new, domain-appropriate vocabulary a document lacked. TAS-B is the best-generalizing dense system, beating ANCE on 14 of the 18 datasets and DPR on 17 of the 18. It still loses to the weaker-on-average ANCE on two datasets: it trails ANCE by 17.3 points on TREC-COVID and 7.8 on Touché-2020, where its top-ranked documents are much shorter than ANCE's — a median of about 10 words versus 160 on TREC-COVID, 14 versus 89 on Touché-2020. A controlled follow-up traces part of this to the training similarity function: two otherwise identical models differing only in cosine-similarity versus dot-product comparison show the same length preference, with the dot-product model scoring 15.3 points higher on TREC-COVID. Because TAS-B and ANCE also differ in base model, loss, and negative mining, this shows the similarity function is one contributing factor, not the sole explanation, for the original gap.

Adapting a model to its target domain with synthetic queries does not uniformly help either: GenQ, TAS-B further fine-tuned on synthetic in-domain queries, improves over TAS-B on specialized domains (scientific, financial, community-forum text) but underperforms it on broader domains such as Wikipedia.

Read together, these results point to a mechanism rather than to model size or embedding sophistication in general. Of the ten systems, the two that keep some form of cross-attention — comparing query and document representations directly rather than compressing each into an independent vector first — generalize best, while every purely single-vector dense system underperforms BM25 on average. This is a pattern observed across the systems compared, not a claim isolated by ablation across architectures, so it is an interpretation, not a proof, and it comes at a real cost: the two best-generalizing systems are also the two slowest.

## 6. Annotation Selection Bias: A Case Study on TREC-COVID

The comparison above assumes BEIR's relevance judgements are equally fair to every architecture — an assumption that is not automatic. Judging every possible query–document pair in a multi-million-document corpus is infeasible, so test collections are instead built by pooling: only the top candidates some existing system retrieves are ever judged, and everything else is assumed irrelevant, a documented source of selection bias in retrieval evaluation (Lipani, 2019). If the pooling system is itself lexical, a non-lexical system's genuinely relevant but lexically dissimilar results may never have been judged, making it look worse than it is in exactly the comparison Section 5 makes. Several BEIR datasets, including BioASQ and Signal-1M(RT), were pooled predominantly with lexical term-matching, raising this concern more broadly.

TREC-COVID, built through a large, multi-system pooling effort during the COVID-19 pandemic (Voorhees et al., 2021), was used to test this directly. For nine systems, Hole@10 — the share of a system's top-10 results never seen by any annotator — was computed (Table 3). All 980 previously unjudged query–document pairs across every system were then manually annotated, following the original guidelines and blind to which system had retrieved each pair to avoid a new preference bias, after which nDCG@10 was recomputed with the completed judgements.

| System | Hole@10 | nDCG@10 (original) | nDCG@10 (annotated) |
|---|---|---|---|
| BM25 | 6.4% | 0.656 | 0.668 |
| DeepCT | 19.4% | 0.406 | 0.472 |
| SPARTA | 12.4% | 0.538 | 0.624 |
| docT5query | 2.8% | 0.713 | 0.714 |
| DPR | 30.6% | 0.332 | 0.445 |
| ANCE | 14.4% | 0.654 | 0.735 |
| TAS-B | 31.8% | 0.481 | 0.555 |
| ColBERT | 12.4% | 0.677 | 0.735 |
| BM25+CE | 1.6% | 0.757 | 0.760 |

*Table 3. Hole@10 and nDCG@10 before/after manually annotating 980 previously unjudged pairs on TREC-COVID.*

Hole@10 differs sharply by system type. BM25 and docT5query, both lexical at their core, had only 6.4% and 2.8% of their top-10 results unjudged; BM25+CE, re-ranking BM25's own candidates, had just 1.6%. DPR and TAS-B, by contrast, had 30.6% and 31.8% unjudged. After the missing judgements were added, the lexical systems' scores barely moved — docT5query from 0.713 to 0.714 — while the non-lexical systems' rose substantially: ANCE from 0.654 to 0.735 (about 8 points), ColBERT by 5.8.

This confirms that, on TREC-COVID, lexically biased pooling had measurably understated non-lexical systems' true zero-shot performance. It does not overturn Section 5's overall ranking: BM25+CE and BM25 itself were barely affected, and the correction was measured on this one dataset, not benchmark-wide. What it establishes is that some part of the apparent gap between lexical and non-lexical systems, in datasets built this way, is a property of the test collection and not only of the retrieval system.

## 7. Discussion

Taken together, the answer to the first question is that in-domain accuracy is a poor predictor of zero-shot generalization. The property most associated with generalizing well here is not embedding architecture in the abstract but whether a system compares query and document representations directly — through re-ranking or late interaction — rather than through independently computed vectors. This is not a general argument that dense retrieval cannot generalize: TAS-B and docT5query show that training procedure and document-expansion strategy can move a system's generalization substantially within its own family. It is, at minimum, evidence that architecture choice alone is not decisive, and that a system's in-domain leaderboard position should not be trusted as a forecast of its zero-shot performance.

The answer to the second question is more qualified. Annotation-pool bias toward lexical systems is real and, on TREC-COVID, large enough to change a system's apparent standing relative to BM25 by several points of nDCG@10. But it is a correction to specific comparisons on specifically pooled datasets, established here for one dataset, not a reason to discard the overall pattern from Section 5, which held across 18 datasets built in many different ways.

Two practical implications follow. Researchers building or fine-tuning retrieval systems should report zero-shot, cross-domain evaluation as standard practice, not an afterthought to an in-domain leaderboard number, and should weigh a generalization gain's latency/index-size cost against its deployment setting. Researchers building new test collections should pool candidates from a deliberately diverse set of systems — lexical and non-lexical alike — rather than whichever is convenient, so future comparisons do not inherit the same bias.

## 8. Limitations

This comparison's scope is bounded in ways that matter for how far its conclusions travel. Every BEIR dataset is in English; multilingual and cross-lingual zero-shot retrieval are not tested. Transformer encoders here truncate at 512 word pieces, so every document is effectively limited to at most a few hundred words, and the architecture ranking in Section 5 is not established for genuinely long documents. Only pure text matching is evaluated: no compared system uses auxiliary signals such as recency, authority, or click-through data that a deployed search engine might also use. And retrieval covers at most two document fields (typically title and body), not the fuller multi-field retrieval a scientific-literature search might require.

The comparison is also one of generalist systems: it does not rule out a model built and tuned specifically for one task outperforming every generalist system compared here on that task. No error bars are available for the zero-shot numbers in Section 5, since most evaluated systems are third-party checkpoints without accessible retraining code, so close rankings — e.g. among TAS-B, ColBERT, and docT5query — are point estimates from a single run, not statistically distinguished results. Total compute used is not fully reported, only the hardware types involved.

Finally, the annotation-bias case study in Section 6 measured Hole@10 and its effect on scores for one dataset, TREC-COVID. Similar lexical pooling is documented for at least two other BEIR datasets, but the size of its effect there was not separately measured, so the exact scale of this bias across the benchmark as a whole remains an open question.

## 9. Conclusion

BEIR gives retrieval researchers one standardized way to ask a question that in-domain benchmarks cannot answer: how well does a system generalize, zero-shot, across genuinely different retrieval tasks and domains? Unifying 18 datasets under one data format and one metric makes that question answerable for any new system with comparatively little additional engineering, and the benchmark, software, and evaluated systems are released openly for exactly this purpose.

The comparison itself changes what should be trusted about a system's in-domain score: it is not a reliable forecast of zero-shot performance, and the mechanism most associated with strong generalization here — direct query–document interaction — also comes with a real computational cost. The TREC-COVID case study adds a further caution about the comparison's own foundation: part of the apparent weakness of non-lexical systems in some datasets is a property of how those datasets were annotated, not only of the systems themselves.

The most direct next steps are the ones this evaluation could not itself take: extending coverage to more languages, to longer documents, and to multi-field retrieval, and building future test collections with deliberately diverse annotation pools, so the next benchmark starts with less of this particular bias to correct for.

## References

Berger, A., Caruana, R., Cohn, D., Freitag, D., and Mittal, V. (2000). Bridging the lexical chasm: statistical approaches to answer-finding. In *Proceedings of the 23rd Annual International ACM SIGIR Conference on Research and Development in Information Retrieval*.

Bondarenko, A., Fröbe, M., Beloucif, M., Gienapp, L., Ajjour, Y., Panchenko, A., Biemann, C., Stein, B., Wachsmuth, H., Potthast, M., and Hagen, M. (2020). Overview of Touché 2020: Argument Retrieval. In *Working Notes Papers of the CLEF 2020 Evaluation Labs*.

Boteva, V., Gholipour, D., Sokolov, A., and Riezler, S. (2016). A full-text learning to rank dataset for medical information retrieval. In *Proceedings of ECIR 2016*.

Cohan, A., Feldman, S., Beltagy, I., Downey, D., and Weld, D. (2020). SPECTER: Document-level Representation Learning using Citation-informed Transformers. In *Proceedings of ACL 2020*.

Dai, Z. and Callan, J. (2020). Context-Aware Term Weighting For First Stage Passage Retrieval. In *Proceedings of SIGIR '20*.

Devlin, J., Chang, M.-W., Lee, K., and Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805.

Diggelmann, T., Boyd-Graber, J., Bulian, J., Ciaramita, M., and Leippold, M. (2020). CLIMATE-FEVER: A Dataset for Verification of Real-World Climate Claims.

Guo, M., Yang, Y., Cer, D., Shen, Q., and Constant, N. (2020). MultiReQA: A Cross-Domain Evaluation for Retrieval Question Answering Models.

Hasibi, F., Nikolaev, F., Xiong, C., Balog, K., Bratsberg, S. E., Kotov, A., and Callan, J. (2017). DBpedia-Entity V2: A Test Collection for Entity Search. In *Proceedings of SIGIR '17*.

Hofstätter, S., Lin, S.-C., Yang, J.-H., Lin, J., and Hanbury, A. (2021). Efficiently Teaching an Effective Dense Retriever with Balanced Topic Aware Sampling. In *Proc. of SIGIR*.

Hoogeveen, D., Verspoor, K. M., and Baldwin, T. (2015). CQADupStack: A benchmark data set for community question-answering research. In *Proceedings of the 20th Australasian Document Computing Symposium*.

Karpukhin, V., Oguz, B., Min, S., Lewis, P., Wu, L., Edunov, S., Chen, D., and Yih, W. (2020). Dense Passage Retrieval for Open-Domain Question Answering. In *Proceedings of EMNLP 2020*.

Khattab, O. and Zaharia, M. (2020). ColBERT: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. In *Proceedings of SIGIR '20*.

Kwiatkowski, T., Palomaki, J., Redfield, O., Collins, M., Parikh, A., Alberti, C., Epstein, D., Polosukhin, I., Kelcey, M., Devlin, J., Lee, K., Toutanova, K. N., Jones, L., Chang, M.-W., Dai, A., Uszkoreit, J., Le, Q., and Petrov, S. (2019). Natural Questions: a Benchmark for Question Answering Research. *Transactions of the Association for Computational Linguistics*.

Lipani, A. (2019). On Biases in Information retrieval models and evaluation. Ph.D. thesis, Technische Universität Wien.

Maia, M., Handschuh, S., Freitas, A., Davis, B., McDermott, R., Zarrouk, M., and Balahur, A. (2018). WWW'18 Open Challenge: Financial Opinion Mining and Question Answering. In *Companion Proceedings of the The Web Conference 2018*.

Nguyen, T., Rosenberg, M., Song, X., Gao, J., Tiwary, S., Majumder, R., and Deng, L. (2016). MS MARCO: A Human Generated MAchine Reading COmprehension Dataset.

Nogueira, R. and Lin, J. (2019). From doc2query to docTTTTTquery. Online preprint.

Petroni, F., Piktus, A., Fan, A., Lewis, P., Yazdani, M., De Cao, N., Thorne, J., Jernite, Y., Plachouras, V., Rocktäschel, T., and Riedel, S. (2020). KILT: a Benchmark for Knowledge Intensive Language Tasks.

Robertson, S. and Zaragoza, H. (2009). The Probabilistic Relevance Framework: BM25 and Beyond. *Foundations and Trends in Information Retrieval*, 3(4):333–389.

Soboroff, I., Huang, S., and Harman, D. (2019). TREC 2019 News Track Overview. In *TREC*.

Suarez, A., Albakour, D., Corney, D., Martinez, M., and Esquivel, J. (2018). A Data Collection for Evaluating the Retrieval of Related Tweets to News Articles. In *Proceedings of ECIR 2018*.

Thorne, J., Vlachos, A., Christodoulopoulos, C., and Mittal, A. (2018). FEVER: a Large-scale Dataset for Fact Extraction and VERification. In *Proceedings of NAACL 2018*.

Tsatsaronis, G., Balikas, G., Malakasiotis, P., Partalas, I., Zschunke, M., Alvers, M. R., Weissenborn, D., Krithara, A., Petridis, S., and Polychronopoulos, D. (2015). An overview of the BIOASQ large-scale biomedical semantic indexing and question answering competition. *BMC Bioinformatics*, 16(1):138.

Voorhees, E. (2005). Overview of the TREC 2004 Robust Retrieval Track.

Voorhees, E., Alam, T., Bedrick, S., Demner-Fushman, D., Hersh, W. R., Lo, K., Roberts, K., Soboroff, I., and Wang, L. L. (2021). TREC-COVID: Constructing a Pandemic Information Retrieval Test Collection. *SIGIR Forum*, 54(1).

Wachsmuth, H., Syed, S., and Stein, B. (2018). Retrieval of the Best Counterargument without Prior Topic Knowledge. In *Proceedings of ACL 2018*.

Wadden, D., Lin, S., Lo, K., Wang, L. L., van Zuylen, M., Cohan, A., and Hajishirzi, H. (2020). Fact or Fiction: Verifying Scientific Claims. In *Proceedings of EMNLP 2020*.

Wang, W., Wei, F., Dong, L., Bao, H., Yang, N., and Zhou, M. (2020). MiniLM: Deep Self-Attention Distillation for Task-Agnostic Compression of Pre-Trained Transformers. In *Advances in Neural Information Processing Systems*, volume 33.

Wang, Y., Wang, L., Li, Y., He, D., Chen, W., and Liu, T.-Y. (2013). A theoretical analysis of NDCG ranking measures. In *Proceedings of the 26th Annual Conference on Learning Theory (COLT 2013)*, volume 8.

Yang, Z., Qi, P., Zhang, S., Bengio, Y., Cohen, W., Salakhutdinov, R., and Manning, C. D. (2018). HotpotQA: A Dataset for Diverse, Explainable Multi-hop Question Answering. In *Proceedings of EMNLP 2018*.

Xiong, L., Xiong, C., Li, Y., Tang, K.-F., Liu, J., Bennett, P., Ahmed, J., and Overwijk, A. (2020). Approximate Nearest Neighbor Negative Contrastive Learning for Dense Text Retrieval.

Zhao, T., Lu, X., and Lee, K. (2021). SPARTA: Efficient Open-Domain Question Answering via Sparse Transformer Matching Retrieval. In *Proceedings of NAACL 2021*.
