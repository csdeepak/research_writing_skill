# Project Assessment — BEIR

## Project description
BEIR (Benchmarking-IR) is a heterogeneous benchmark for zero-shot evaluation of information retrieval (IR) models. It combines 18 publicly available retrieval datasets spanning 9 tasks and domains (bio-medical IR, open-domain QA, tweet retrieval, news retrieval, argument retrieval, duplicate-question retrieval, entity retrieval, citation prediction, fact checking), plus an open-source Python framework (`pip install beir`) that standardizes each dataset into a common corpus/queries/qrels format and provides wrappers to run and evaluate ten retrieval architectures against them (paper.txt lines 1–7, 121, 296).

## Official repository
- URL (from paper Abstract / §3.2): `https://github.com/UKPLab/beir` (paper.txt lines 7, 298). Note: the snapshot README is served from `beir-cellar/beir` (also linked to `benchmarkir/beir` images), indicating the repository has since moved/been renamed — see Risks.
- Pinned commit captured in this snapshot (per `evaluation/manifests/source_snapshots.json`): `beir-cellar/beir` @ `ef83d29307061c65d04b035b4f4e7c18bd8374af`, `README.md`.

## Paper/report
- arXiv: `2104.08663v4` (dated "21 Oct 2021" per the PDF header) (paper.txt line 1).
- Venue/peer-review status: the paper's own header says "Preprint. Under review." (paper.txt line 13). The snapshot README (an artifact-only source, captured later) states it was published as "BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models (NeurIPS 2021, Datasets and Benchmarks Track)" with an OpenReview link `https://openreview.net/forum?id=wCu6T5xFjeJ` and gives a BibTeX entry citing "Thirty-fifth Conference on Neural Information Processing Systems Datasets and Benchmarks Track (Round 2), 2021" (README lines 57–59, 401–412). This is a README (artifact) claim, not verified against the paper snapshot itself, and per the study's authority rule (README only for artifact facts) it should be treated as an artifact-level fact about publication venue, not incorporated into the Gold Account as a paper-sourced claim.
- A second, later publication is referenced in the README: "Resources for Brewing BEIR: Reproducible Reference Models and an Official Leaderboard" (SIGIR 2024 Resource Track), arXiv 2306.07471 (README lines 60, 414–433). This is a *different* paper by a partly-overlapping author set, outside the frozen snapshot's `paper.txt`, and is NOT used as evidence for the Gold Account — it is mentioned here only because it explains README content (e.g. later model examples) that postdates the BEIR paper.

## Datasets
18 zero-shot evaluation datasets across 9 tasks, sizes 3.6K–15M documents, described in detail in paper §3 and Appendix D, with per-dataset statistics in Table 1 (paper.txt lines 121, 141–290, 840–886). A 19th dataset, MS MARCO, is used for in-domain training/reporting only and excluded from the zero-shot comparison (paper.txt line 138). Four dataset licenses are unreported in the paper (NFCorpus, FiQA-2018, Quora, Climate-FEVER) (paper.txt line 885). The README's dataset table (README lines 338–358) additionally marks BioASQ, Signal-1M(RT), TREC-NEWS, and Robust04 as not publicly downloadable ("❌ Public?" / "No" download links, "How to Reproduce?" pointers instead) — an artifact-level accessibility fact not stated as such in the paper itself.

## Benchmark/evaluation material
The paper defines a single primary metric, nDCG@10, computed via the official TREC eval tool's Python interface (pytrec_eval) (paper.txt lines 352–353), plus a supplementary Recall@100 table (Table 9) and a capped-recall variant defined in Appendix G. The BEIR software package packages the standardized data format and evaluation code (paper.txt lines 295–351; README lines 62–89, 331–359).

## Available experimental evidence
The paper reports a controlled comparison of 10 retrieval systems (BM25; DeepCT, SPARTA, docT5query; DPR, ANCE, TAS-B, GenQ; ColBERT; BM25+CE) across the 18 zero-shot datasets plus in-domain MS MARCO, with full experimental setup (checkpoints, index parameters, training regime) described in §4 (paper.txt lines 354–363, Table 2). It also reports a latency/index-size study on a 1M-document DBPedia sample (§5.1, Table 3) and a manual re-annotation study of TREC-COVID to quantify annotation (lexical) bias (§6, Table 4).

## Available result evidence
- Table 2 (nDCG@10, in-domain + 18 zero-shot datasets, all 10 models) — paper.txt lines 370–533.
- Table 9 (Recall@100, same models/datasets) — paper.txt lines 1119–1252.
- Table 3 (retrieval latency, index size on 1M-doc DBPedia sample) — paper.txt lines 601–656.
- Table 4 (Hole@10 and nDCG@10 before/after manual TREC-COVID annotation) — paper.txt lines 665–705.
- Table 10 (cosine vs. dot-product SBERT variants, nDCG@10 on TREC-COVID/Signal-1M/FEVER) — paper.txt lines 1254–1286.
These are all numeric tables extracted by pdftotext; several show layout damage (see Risks) but the numeric values themselves are legible and column headers are recoverable by cross-referencing row/column order against the model and dataset lists given in the surrounding prose.

## Source quality (authoritative vs. secondary)
- `paper.txt` (arXiv 2104.08663v4) is the authoritative source for all research claims: motivation, method, experimental design, and results.
- `README__beir-cellar__beir.md` is a secondary/artifact source. It documents the current state of the code repository (installation, usage examples, dataset download table, citations) but is snapshotted at a commit that post-dates the paper by years — it references models (e.g., Qwen2.5, LoRA/vLLM, gte-modernbert-base, Cohere embed-v4.0) that did not exist when the paper was written, and a second, later publication (SIGIR 2024). It is used only for artifact-level facts (installation, package name, dataset public-availability list, citation/venue metadata) per the study's authority rule.

## Reproducibility/accessibility
The paper states code, data, and instructions are provided via the repository URL in the abstract, and that all results can be reproduced from the released code (paper.txt lines 814–815, Checklist §3a–b). However, the paper's own Checklist also discloses: no error bars are reported because many evaluated models are pre-trained checkpoints not retrained by the authors (line 816), and total compute is not reported, only hardware type (line 817). Several datasets used in the paper (BioASQ, Signal-1M, TREC-NEWS, Robust04) are not directly downloadable and require separate reconstruction steps per the README (README lines 343, 347–349), which is an artifact-level accessibility fact, not a paper claim.

## Suitability for this evaluation
- Methodology can be reconstructed: yes. §3–§4 and Appendix C–D give explicit selection criteria, dataset construction/splitting details, model configurations, and metric definitions.
- Experiments and results are clearly identifiable: yes, with exact tables and section locations as listed above.
- A factual Gold Account can be written without guessing: yes, for the paper's own content. Some care is needed around numeric table extraction due to pdftotext column misalignment (see Risks) — legible values can still be safely recorded, but full table reconstruction (which model/dataset each number belongs to) is inferential in places (see Risks) and is called out below rather than presented as exact fact.

## Risks
1. **pdftotext table damage**: Tables 2, 3, 4, 9, and 10 lost their grid structure — model/dataset headers and numeric cell columns became separated flowing text blocks (e.g., paper.txt lines 370–533 for Table 2). Row order (dataset order) and column order (model order) can be reconstructed by matching against the dataset list order given in Table 1 and the model list in §4, but this reconstruction is an inference from layout, not a literal read of a table cell; the Gold Account draft records this explicitly and treats exact model↔number↔dataset triples with caution, quoting only values that can be confidently anchored (e.g., single-model summary rows, values repeated in prose).
2. **Repository/paper divergence**: The snapshot README is captured from `beir-cellar/beir`, not the paper-cited `UKPLab/beir`, at a commit reflecting years of subsequent development (post-2021 model integrations, a 2024 companion paper). README "features" (e.g., "preprocess 17 benchmark datasets", specific pip-installable API, LoRA/vLLM examples) must not be treated as paper-described experiments.
3. **Preprint vs. published record**: `paper.txt` itself is headed "Preprint. Under review." (line 13) and is v4 of the arXiv submission; the NeurIPS 2021 Datasets and Benchmarks Track acceptance is known only via the README's citation block, not from the paper text itself.
4. **Table 1 statistics formatting**: Table 1 (dataset statistics, lines 141–290) is also visibly reflowed by pdftotext (column labels separated from values); the Gold Account records only values that can be unambiguously matched to a dataset/column via the row order in the source list.
5. **Figures rendered as disordered text**: Figure 1 (task/dataset overview) and Figure 2 (domain-overlap heatmap) content appears as scattered OCR-like fragments (lines 15-118, 302-349); only prose-stated facts about these figures are used, not attempted numeric reconstruction beyond what is legible.

## Recommendation: ACCEPT WITH CAVEATS
The BEIR paper snapshot is unusually rich and self-contained: it states its own selection methodology, task/dataset taxonomy, exact experimental setup for 10 models, a single well-defined primary metric, and multiple distinct result tables plus a dedicated bias-analysis experiment (TREC-COVID re-annotation) with before/after numbers. This gives strong material for reconstructing a "what was done / what was found" account. The caveats are: (a) five of the paper's numeric tables suffered pdftotext layout damage requiring careful, conservative extraction (documented above and handled explicitly in the Gold Account and evidence table), and (b) the companion README reflects a substantially evolved, later codebase and must be firmly separated from paper-era claims. Neither caveat prevents building an accurate, guess-free Gold Account; both are manageable by explicit labeling, which is done throughout Output 2.
