# Gold Account Draft — BEIR (snapshot-only factual ledger)

Source authority: the paper (`paper.txt`, arXiv 2104.08663v4) is authoritative for all research claims. The README (`README__beir-cellar__beir.md`) is used only for artifact facts (installation, package availability, dataset public-download status, citation metadata) and is explicitly labeled wherever used.

## 1. Problem
Existing neural IR models had "often been studied in homogeneous and narrow settings, which has considerably limited insights into their out-of-distribution (OOD) generalization capabilities" (paper.txt line 7). It was "unclear how well existing trained neural models will perform for other text domains or textual retrieval tasks," and "even more important, unclear how well different approaches, like sparse embeddings vs. dense embeddings, generalize to out-of-distribution data" (line 120).

## 2. Motivation
Most prior neural retrieval work trains on large datasets like Natural Questions (133k examples) or MS MARCO (533k examples) and then evaluates "on the same dataset, where significant performance gains over lexical approaches like BM25 are demonstrated" (paper.txt line 10). Building large training corpora is "time-consuming and expensive," so "many retrieval systems are applied in a zero-shot setup, with no available training data" (line 11) — motivating the need for a standardized way to measure zero-shot generalization.

## 3. Research gap
"To our knowledge, BEIR is the first broad, zero-shot information retrieval benchmark" (paper.txt line 127). Prior benchmarks are described as narrower: MultiReQA covers a single QA task, is mostly Wikipedia-sourced (5/8 datasets), and evaluates over small corpora (6/8 tasks have <100k candidate sentences) (lines 127, quoting authors' description); KILT covers five knowledge-intensive tasks/eleven datasets but retrieves only from Wikipedia and treats retrieval as a secondary component, not the primary task (lines 127, 131).

## 4. Research question/objective
To build "a novel robust and heterogeneous benchmark called BEIR ... comprising of 18 retrieval datasets for comparison and evaluation of model generalization" (paper.txt line 121), and to use it to evaluate how ten diverse retrieval architectures perform in a zero-shot (out-of-domain) setting, including examining whether in-domain performance predicts out-of-domain generalization (lines 122, 366).

## 5. System/method
BEIR standardizes retrieval datasets into a common corpus/queries/qrels format and provides evaluation wrappers for multiple retrieval libraries (Sentence-Transformers, Transformers, Anserini, DPR, Elasticsearch, ColBERT, Universal Sentence Encoder) (paper.txt line 296). Ten retrieval systems were evaluated, grouped into five architecture families (paper.txt lines 356–363):
- **Lexical**: BM25 (Anserini, default Lucene params k=0.9, b=0.4; title+passage indexed as separate fields).
- **Sparse**: DeepCT (bert-base-uncased trained on MS MARCO, term-weight pseudo-documents, combined with BM25); SPARTA (re-implemented by the authors — "the original implementation is not publicly available" — DistilBERT fine-tuned on MS MARCO, 2,000 non-zero sparse dims); docT5query (T5-base trained on MS MARCO, 40 generated queries per document appended for BM25 search).
- **Dense**: DPR (bert-base-uncased two-tower bi-encoder, "Multi" variant trained on NQ, TriviaQA, WebQuestions, CuratedTREC); ANCE (RoBERTa bi-encoder with ANN-mined hard negatives, trained on MS MARCO for 600K steps); TAS-B (bi-encoder trained with Balanced Topic Aware Sampling, combined pairwise Margin-MSE + in-batch negative losses); GenQ (unsupervised domain adaptation: T5-base fine-tuned on MS MARCO for 2 epochs to generate 5 synthetic queries per target document, top-k=25/top-p=0.95 sampling, capped at 100K target documents, then TAS-B continued-trained on synthetic pairs per target dataset).
- **Late-interaction**: ColBERT (bert-base-uncased, max sequence length 300, trained on MS MARCO for 300K steps; used end-to-end with faiss ANN top-k retrieval at faiss depth=100, then MaxSim re-aggregation).
- **Re-ranking**: BM25+CE (BM25 top-100 candidates re-ranked by a 6-layer, 384-hidden MiniLM cross-encoder, chosen from 14 evaluated public re-ranking models as the best-performing on MS MARCO; trained via knowledge distillation from an ensemble of BERT-base, BERT-large, and ALBERT-large teachers).

## 6. Architecture
Not a neural architecture paper in itself; BEIR is a benchmark + software framework. Documents are truncated to "the first 512 word pieces within all documents in our experiments across all neural architectures" due to transformer length limits (paper.txt line 355). The BEIR software is described as "an easy to use Python framework (pip install beir)" (line 296) — this pip-installability is corroborated as a current artifact fact by the README ("pip install beir", README line 67), but the package's present feature list in the README (e.g., "17 already-preprocessed benchmark datasets") reflects the later codebase and is NOT attributed to the paper.

## 7. Dataset/data
18 English zero-shot evaluation datasets across 9 tasks (paper.txt line 138), plus MS MARCO used for in-domain training reference only (not included in the zero-shot comparison) (line 138). Selection methodology driven by four factors: diverse tasks, diverse domains, sufficient task difficulty, and diverse annotation strategies (crowd-workers, experts, online-community feedback) (paper.txt line 137). Full per-dataset statistics are given in Table 1 (paper.txt lines 141–290); NOTE — pdftotext reflowed this table, separating column headers from values, so per-cell dataset↔number pairing below is reconstructed by row order rather than read directly from an intact grid:
- Dataset sizes range "3.6k - 15M documents"; query lengths average "between 3 and 192 words"; document lengths average "between 11 and 635 words" (paper.txt line 121).
- "Only 8 out of 19 datasets (including MS MARCO) have training data" (paper.txt line 290).
- "All datasets except ArguAna have short queries (either a single sentence or 2-3 keywords)" (paper.txt line 290).
- Dataset domain-overlap was measured via pairwise weighted Jaccard similarity on unigram word overlap (§3.1, paper.txt lines 292–349); the paper reports "a rather low weighted Jaccard word overlap across different domains," interpreted as showing the benchmark requires generalization across diverse domains (line 293) — labeled as interpretation, see §13.
- Dataset licensing: reported for most datasets in Appendix E (paper.txt line 886); NOT reported for NFCorpus, FiQA-2018, Quora, and Climate-FEVER (line 885).
- README-only artifact fact: of the datasets, the README's table marks BioASQ, Signal-1M(RT), TREC-NEWS, and Robust04 as not directly downloadable ("❌ Public?"), requiring separate reproduction steps (README lines 343, 347–349). This is an artifact/accessibility fact, not stated in the paper itself.

## 8. Experimental setup
Primary comparison: 10 models × 18 zero-shot datasets + in-domain MS MARCO, using publicly available pre-trained checkpoints (links given in Table 6, paper.txt lines 968–976) (§4, paper.txt lines 354–363). Additional experiments:
- **Efficiency study** (§5.1): retrieval latency and index size measured on a random 1M-document sample from DBPedia; CPU = "8 core Intel Xeon Platinum 8168 CPU @ 2.70GHz"; GPU = "single Nvidia Tesla V100, CUDA 11.0" (paper.txt lines 592–596). Dense models used exact search; ColBERT used approximate nearest-neighbor search per its original setup (line 594).
- **Annotation-bias study** (§6): manual re-annotation of missing (Hole@10) relevance judgments for TREC-COVID, following the original TREC-COVID annotation guidelines, with annotators blind to which system retrieved each candidate ("we were unaware of the system who retrieved the missing annotation to avoid a preference bias") (paper.txt line 704). "In total, we annotated 980 query-document pairs in TREC-COVID" (line 704).
- **Length-preference ablation** (Appendix H): two distilbert-base-uncased models trained identically on MS MARCO, differing only in similarity function (cosine-similarity vs. dot-product), compared on TREC-COVID, Signal-1M(RT), and FEVER (paper.txt lines 950–954, Table 10).

## 9. Metrics
Primary metric: nDCG@10, computed with the official TREC eval tool's Python interface (paper.txt line 353), chosen because "Decision support metrics such as Precision and Recall which are both rank unaware are not suitable. Binary rank-aware metrics such as MRR ... and MAP ... fail to evaluate tasks with graded relevance judgements" (§3.3, paper.txt lines 352–353) — this rationale is an authors' interpretation/justification, see §13. Secondary metric: Recall@100 (Table 9). A capped-recall variant R_cap@k is defined in Appendix G to address the "counterintuitive" behavior of plain recall when a dataset has more relevant documents than k (paper.txt lines 893–926). Hole@10 (rate of top-10 retrieved documents unseen by annotators) used in the bias study (§6, Table 4).

## 10. Results (exact numbers, with table/section)
Caveat: Tables 2, 3, 4, 9, 10 were reflowed by pdftotext extraction; numbers below are transcribed from the extracted text and cross-checked against surrounding prose narration where possible. Where a number is stated both in prose and in a table, the prose-confirmed value is used.

**Table 2 (nDCG@10), paper.txt lines 370–533** — selected values corroborated in prose:
- BM25 on MS MARCO (in-domain): 0.228 (paper.txt line 372; §5 states BM25 "heavily underperforms neural approaches by 7-18 points on in-domain MS MARCO," line 366).
- Average zero-shot performance vs. BM25 (Table 2 bottom row, "Avg. Performance vs. BM25"): BM25+CE +11%; ColBERT +2.5%; GenQ −3.6%; TAS-B −2.8%; ANCE −7.4%; docT5query +1.6%; DPR −47.7%; SPARTA −20.3%; DeepCT −27.9% (paper.txt lines 422–531, row order matched to model column order given in §4).
- "It [BM25+CE] outperform[s] BM25 on almost all (16/18) datasets. It only fails on ArguAna and Touché-2020" (paper.txt line 537).
- "docT5query ... outperforms BM25 on 11/18 datasets" (paper.txt line 535).
- "ColBERT ... is still able to outperform BM25 on 9/18 datasets" (paper.txt line 537).
- "TAS-B ... outperforms ANCE on 14/18 and DPR on 17/18 datasets" (paper.txt line 538).
- TAS-B vs. ANCE on TREC-COVID: TAS-B underperforms "by 17.3 points"; on Touché-2020: "by 7.8 points" (paper.txt line 539).
- On TREC-COVID, "TAS-B retrieves documents with a median length of mere 10 words versus ANCE with 160 words." On Touché-2020: "14 words vs. 89 words with TAS-B and ANCE respectively" (paper.txt line 539).

**Table 3 (retrieval latency / index size, 1M-doc DBPedia sample), paper.txt lines 601–656**: reranking/late-interaction "come at the cost of high latency (> 350 ms)"; dense retrievers are "20-30x faster (< 20ms)"; sparse models on CPU are fastest at "20-25ms" (paper.txt line 598). Index sizes: "Lexical, re-ranking and dense methods have the smallest index sizes (< 3GB)"; SPARTA requires the second largest (30k-dim sparse vector); ColBERT requires the largest (multiple 128-dim vectors per document) (lines 649–654). At scale: "ColBERT requires ~900GB to store the BioASQ (~15M documents) index, whereas BM25 only requires 18GB" (line 656).

**Table 4 (Hole@10 / TREC-COVID re-annotation), paper.txt lines 665–705**: Hole@10 — BM25 6.4%, docT5query 2.8%, DeepCT 19.4%, SPARTA 12.4%, DPR 30.6%, ANCE 14.4%, TAS-B 31.8%, ColBERT 12.4%, BM25+CE 1.6% (lines 669–697, row order matched to model list). nDCG@10 before → after re-annotation: docT5query 0.713 → 0.714 (line 705, "just from 0.713 to 0.714"); ANCE 0.654 → 0.735, "which is 6.7 points above the BM25 performance" (line 705); ColBERT improvement "5.8 points" (line 705); BM25+CE 0.757 → 0.760 (line 698).

**Table 9 (Recall@100)**, paper.txt lines 1119–1252: full model×dataset grid present but reflowed by extraction; BM25 in-domain MS MARCO Recall@100 = 0.658 (line 1127, 1242 — value repeats identically at both the model-row position and the "Avg. Performance vs. BM25" bottom-row MS MARCO column, consistent with BM25 being the baseline).

**Table 10 (cosine vs. dot-product ablation), paper.txt lines 1254–1286**: nDCG@10 — TREC-COVID: cosine 0.482, dot-product 0.635; Signal-1M(RT): cosine 0.261, dot-product 0.243; FEVER: cosine 0.670, dot-product 0.685 (lines 1274–1284). "For TREC-COVID, the dot-product model achieves the biggest improvement with 15.3 points" (line 950; consistent with 0.635 − 0.482 = 0.153).

## 11. Supported claims (directly measured/observed)
- BM25 is a "robust baseline" for zero-shot retrieval in this benchmark (directly observed from Table 2 average-vs.-BM25 comparisons) (paper.txt lines 7, 122).
- Re-ranking (BM25+CE) and late-interaction (ColBERT) models achieve the best average zero-shot nDCG@10 performance among the ten tested, at higher computational cost (measured in Tables 2 and 3) (paper.txt lines 7, 598).
- Dense (DPR, ANCE, TAS-B) and sparse (DeepCT, SPARTA) models are computationally cheaper but, except for docT5query, generally underperform BM25 on average (measured, Table 2 bottom row) (paper.txt line 7).
- Manual re-annotation of TREC-COVID measurably raises nDCG@10 for all tested systems, with the largest gains for high-Hole@10 systems (ANCE, ColBERT) (measured, Table 4) (paper.txt lines 705).
- DPR performs worst in generalization among tested models overall (paper.txt line 536: "DPR, the only non-MSMARCO trained dataset overall performs the worst in generalization on the benchmark" — note: as literally quoted, though the labeling "non-MSMARCO trained" is unusual since DPR is described in §4 as trained on QA datasets, not MS MARCO; recorded verbatim as written).

## 12. Derived claims (computed/comparative)
- docT5query outperforms BM25 on 11/18 datasets while remaining competitive elsewhere (derived by the authors from per-dataset Table 2 comparisons) (paper.txt line 535).
- BM25+CE outperforms BM25 on 16/18 datasets, failing only on ArguAna and Touché-2020 (derived comparative count) (paper.txt line 537).
- ColBERT outperforms BM25 on 9/18 datasets (derived comparative count) (paper.txt line 537).
- TAS-B outperforms ANCE on 14/18 and DPR on 17/18 datasets (derived comparative counts) (paper.txt line 538).
- In-domain MS MARCO performance does not correlate with zero-shot generalization performance across models (a comparative/derived observation drawn from contrasting Table 2's MS MARCO column against the "Avg. Performance vs. BM25" row) (paper.txt lines 122, 366).

## 13. Interpretations (authors' explanations — label as interpretation)
- INTERPRETATION: the low pairwise weighted Jaccard word overlap across dataset domains is offered as evidence that "BEIR is a challenging benchmark where approaches must generalize well to diverse out-of-distribution domains" (paper.txt line 293).
- INTERPRETATION: nDCG@10 is claimed to "provide a good balance suitable for both tasks involving binary and graded relevance judgements," justifying its choice as the single primary metric (paper.txt lines 352–353).
- INTERPRETATION: TAS-B's stronger zero-shot generalization vs. ANCE/DPR is attributed by the authors to "a strong training setup in combination of both in-domain batch negatives and Margin-MSE losses ... with strong ensemble teachers in a Knowledge Distillation setup," explicitly hedged as speculation: "We speculate that the reason lies in..." (paper.txt line 538) — see also §14.
- INTERPRETATION: TAS-B's and ANCE's differing preference for retrieving short vs. long documents is attributed to differences in similarity function (cosine vs. dot-product): "Cosine-similarity uses vectors of unit length, thereby having no notion of the encoded text length. In contrast, for dot-product, longer documents result in vectors with higher magnitudes which can yield higher similarity scores" (paper.txt line 952).
- INTERPRETATION: cross-attention/cross-attentional-like operations are proposed as important for good OOD generalization, based on re-ranking and late-interaction models' comparatively strong performance ("It appears that cross-attention and cross-attentional like operations are important for a good out-of-distribution generalization") (paper.txt line 537).
- INTERPRETATION (authors' explanation of relevance-length correlation): differences in whether shorter/longer documents are annotated as more relevant "can be either due to the annotation process ... or due to the task itself" (paper.txt line 954) — presented explicitly as an open, unresolved explanation.

## 14. Hypotheses/speculation
- SPECULATION (explicitly hedged by authors): "We speculate that the reason lies in a strong training setup..." for TAS-B's generalization advantage (paper.txt line 538).
- Authors state as future work: "future work requires better unbiased datasets that allow a fair comparison for all types of retrieval systems" (paper.txt line 123), following from the observed lexical-bias effect in annotation.
- Authors pose an open research question without answering it definitively: "Does domain adaptation help improve generalization of dense-retrievers?" — investigated via GenQ but with a mixed answer (outperforms TAS-B on specialized domains, underperforms on broader/generic domains like Wikipedia) (paper.txt lines 590).

## 15. Limitations
Authors' explicitly stated limitations (Appendix B, paper.txt lines 831–837):
1. Multilingual tasks: "all datasets covered in the BEIR benchmark are currently English"; multilingual/cross-lingual extension left to future work (line 833).
2. Long document retrieval: "Most of our tasks have average document lengths up-to a few hundred words," and transformer length limits (512 word pieces) would require "a fundamentally different setup" to compare approaches on longer documents (line 834).
3. Multi-factor search: the benchmark "focused on pure textual search"; other real-world relevance signals (PageRank, recency, authority score, click-through rate) are not integrated (line 835).
4. Multi-field retrieval: the benchmark "focused only on datasets that have one or two fields," not the multiple fields (title, abstract, body, authors, journal) sometimes available in practice (line 836).
5. Task-specific models: the benchmark evaluates generalist models; "task-specific models... do not necessarily need to generalize across all diverse tasks" and can outperform generalist models on a single task (line 837).

Additional stated limitation from the paper's own Checklist (§ Checklist, paper.txt lines 816–817):
6. No error bars/multiple-seed results are reported: "We evaluate existing available pre-trained models that often come without suitable training code. Hence, in many cases, re-training the model is not feasible" (line 816).
7. Total compute is not reported, only hardware type used (line 817).

Scope boundary (derived from stated conditions): because all evaluated neural models truncate documents to "the first 512 word pieces" (paper.txt line 355), the reported comparisons apply specifically to that truncation regime and do not establish how these models would compare without truncation on the longer-document subset of BEIR (a boundary that follows directly from the stated 512-word-piece condition, not an authors' explicit limitation statement).

## 16. Actual contribution
As stated by the authors: (1) "a novel robust and heterogeneous benchmark called BEIR" comprising 18 zero-shot IR datasets across 9 tasks for evaluating model generalization (paper.txt line 121); (2) a comparative zero-shot evaluation of 10 diverse retrieval architectures on this benchmark, finding no single approach consistently outperforms others, that in-domain performance does not predict OOD generalization, and a performance/efficiency trade-off where the best-generalizing approaches (re-ranking, late-interaction) are the most computationally expensive (paper.txt lines 122, 366); (3) an analysis of annotation selection bias via manual TREC-COVID re-annotation, showing non-lexical approaches are disadvantaged by lexically-biased annotation pools (paper.txt lines 123, 660–705); (4) release of "BEIR and an integration of diverse retrieval systems and datasets in a well-documented, easy to use and extensible open-source package" (paper.txt line 124).

## 17. Unsupported or weakly supported claims
- The statement that BM25 "remains a strong baseline for zero-shot text retrieval" (paper.txt line 122) is well supported by the presented average comparisons, but the paper does not report statistical significance testing or variance across the compared systems' average performance deltas (e.g., "+11%", "−47.7%" in Table 2's bottom row) — the underlying per-dataset spread is visible in the extracted table but no significance test or confidence interval accompanies these aggregate percentages in the snapshot. This weakens (without invalidating) the strength with which cross-model average comparisons can be treated as robust rather than descriptive.
- The claim that "in-domain performance of a model does not correlate well with its generalization capabilities: models fine-tuned with identical training data might generalize differently" (paper.txt line 122) is illustrated with examples (e.g., ANCE vs. TAS-B vs. DPR, all MS MARCO-trained dense models with differing zero-shot results) but the paper does not report a correlation coefficient or formal statistical test of this claim in the snapshot — it is presented as an observed pattern from Table 2, not as a statistically quantified correlation.
- NOT IN SNAPSHOT: no held-out human evaluation or inter-annotator agreement statistics are given for the manual TREC-COVID re-annotation beyond the count of 980 annotated pairs and the blinding procedure described.

## 18. Claim → evidence → source table

| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| BEIR provides 18 zero-shot datasets across 9 tasks | measured/described | dataset count and task taxonomy | paper.txt line 121 | "comprising of 18 retrieval datasets for comparison and evaluation of model generalization" |
| No single approach outperforms all others across all datasets | derived | Table 2 per-dataset comparison | paper.txt line 122 | "we find that no single approach consistently outperforms other approaches on all datasets" |
| BM25+CE outperforms BM25 on 16/18 datasets | derived | Table 2 | paper.txt line 537 | "able to outperform BM25 on almost all (16/18) datasets" |
| BM25+CE average performance vs BM25 is +11% | measured | Table 2 bottom row | paper.txt line 531 | "+11%" (Table 2, Avg. Performance vs. BM25 row) |
| DeepCT average performance vs BM25 is −27.9% | measured | Table 2 bottom row | paper.txt line 433 | "- 27.9%" (Table 2, Avg. Performance vs. BM25 row) |
| ColBERT requires ~900GB to index BioASQ (~15M docs) vs BM25's 18GB | measured | Table 3 discussion | paper.txt line 656 | "ColBERT requires ~900GB ... BM25 only requires 18GB" |
| ANCE nDCG@10 on TREC-COVID rose from 0.654 to 0.735 after re-annotation | measured | Table 4 | paper.txt line 705 | "for the dense retrieval system ANCE, the performance improves from 0.654 ... to 0.735" |
| 980 query-document pairs were manually annotated in TREC-COVID study | measured | §6 annotation study | paper.txt line 704 | "we annotated 980 query-document pairs in TREC-COVID" |
| Dot-product model improves TREC-COVID nDCG@10 by 15.3 points over cosine model | measured | Appendix H, Table 10 | paper.txt line 950 | "the dot-product model achieves the biggest improvement with 15.3 points" |
| nDCG@10 chosen as primary metric because it suits both binary and graded relevance | interpretation | §3.3 | paper.txt lines 352-353 | "nDCG@k) provides a good balance suitable for both tasks involving binary and graded relevance" |
| TAS-B's generalization advantage attributed to training setup | speculation | §5 analysis point 5 | paper.txt line 538 | "We speculate that the reason lies in a strong training setup" |
| Benchmark limited to English-only datasets | limitation (stated) | Appendix B | paper.txt line 833 | "all datasets covered in the BEIR benchmark are currently English" |
| Benchmark does not integrate multi-factor signals (PageRank, recency, CTR) | limitation (stated) | Appendix B | paper.txt line 835 | "further signals ... such as PageRank, recency ... click-through rates" not integrated |
| No error bars reported due to infeasibility of retraining pre-trained checkpoints | limitation (stated) | Checklist §3c | paper.txt line 816 | "in many cases, re-training the model is not feasible" |
| Documents truncated to first 512 word pieces for all neural models | scope condition | §4 | paper.txt line 355 | "we use only the first 512 word pieces within all documents" |
| Contribution: released open-source package integrating datasets/models | actual contribution | §1 conclusion of intro | paper.txt line 124 | "well-documented, easy to use and extensible open-source package" |
| Repository is pip-installable as `beir` (artifact fact, README) | context (artifact) | README Installation | README line 67 | "pip install beir" |
| Paper published at NeurIPS 2021 Datasets and Benchmarks Track (artifact-sourced claim) | context (artifact, unverified in paper.txt) | README citation block | README lines 57-59 | "(NeurIPS 2021, Datasets and Benchmarks Track)" |
| Paper header states preprint/under-review status | context | arXiv preprint header | paper.txt line 13 | "Preprint. Under review." |
| Four dataset licenses (NFCorpus, FiQA-2018, Quora, Climate-FEVER) not reported | limitation (stated) | Appendix E | paper.txt line 885 | "do not report the dataset license in the paper or a repository" |
