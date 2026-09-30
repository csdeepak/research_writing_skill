# Research skeleton (Step 9)

One topic sentence per paragraph slot from plan/paper_architecture.md, with claim tags. Read
top-to-bottom only, before any paragraph is expanded.

**ABS.1** Retrieval models are normally evaluated on one dataset, but we show that in-domain accuracy on that one dataset does not predict zero-shot performance elsewhere {C001,C004}, that the systems which generalize best zero-shot cost far more to run {C006,C007}, and that the benchmark's own relevance judgments can themselves be biased toward the kind of system that helped build them {C018,C019}.

**I.1** Retrieval is a first step in many NLP pipelines, but neural retrieval models are usually trained and tested on a single dataset, leaving their behavior elsewhere unknown {C001}.

**I.2** Because collecting in-domain training data for every new domain or task is costly, retrieval systems are often deployed zero-shot, so we built BEIR to find out which architectures actually generalize {C020}.

**I.3** The closest existing multi-dataset resources each relax only one axis of narrowness -- one task over mostly small, Wikipedia-heavy corpora, or several tasks but retrieval only from Wikipedia -- so broad cross-domain, cross-task zero-shot generalization is still untested {C002}.

**I.4** We ask which retrieval architectures generalize best zero-shot across diverse tasks and domains, at what computational cost, and how much in-domain accuracy predicts this {C003}.

**I.5** We built BEIR by selecting 18 datasets across 9 tasks to jointly maximize diversity of task, domain, difficulty, and annotation method, and evaluated 10 public systems spanning five retrieval architecture families under one shared protocol {C021}.

**I.6** Our contributions are: (1) BEIR itself, a standardized 18-dataset/9-task benchmark {C001}; (2) the finding that in-domain accuracy misleads about zero-shot performance and that generalization trades off against compute {C004,C006}; and (3) a case study showing the benchmark's own judgments can carry annotation bias {C018}.

**RW.1** Five retrieval architecture families exist, nearly all built by fine-tuning a BERT-family encoder on the same large training set.

**RW.2** The two closest prior multi-dataset resources, MultiReQA and KILT, each cover only one axis of diversity, not both task type and domain {C002}.

**RW.3** BEIR is, to the authors' knowledge, the first benchmark to test cross-task and cross-domain zero-shot generalization jointly, at this scale {C002}.

**M.1** BEIR's 18 datasets were chosen to jointly satisfy four criteria: diverse tasks, diverse domains, sufficient difficulty, and diverse annotation strategies {C021}.

**M.2** The result is a benchmark spanning 3.6 thousand to 15 million documents per corpus, 3-192-word queries, and 11-635-word documents, with training data available for only 8 of 19 datasets {C001}.

**M.3** We score every system with nDCG@10, the only metric among those considered that handles both binary and graded relevance judgments comparably {C022}.

**M.4** Every neural system truncates documents to 512 word pieces, and BM25 is used as the shared zero-shot reference point throughout.

**ES.1** The ten evaluated systems span five families: lexical (BM25), sparse-neural (DeepCT, SPARTA, docT5query), dense bi-encoders (DPR, ANCE, TAS-B, GenQ), late-interaction (ColBERT), and cross-encoder re-ranking (BM25+CE).

**ES.2** Nearly every system is fine-tuned from a BERT-family encoder on MS MARCO; DPR is the one exception trained only on non-MS-MARCO question-answering data, and GenQ further adapts TAS-B per target dataset using synthetic queries.

**ES.3** Every number in this paper is a single evaluation run, because most systems are public checkpoints without accessible training code, so no seed variance or significance test is available {L006}.

**R.1** In-domain accuracy does not predict zero-shot performance: BM25 trails the neural systems by 7-18 points nDCG@10 on in-domain MS MARCO, yet averaged over the 18 BEIR datasets it beats six of the nine neural systems tested {C004,C005}.

**R.2** Averaged over the 18 datasets, only re-ranking (+11%), late-interaction (+2.5%), and one sparse method (docT5query, +1.6%) beat BM25; the other six systems score below it {C006}.

**R.3** The two best-generalizing families are also the most expensive: about 450ms per query on GPU versus under 20ms for the tested dense retrievers {C007}.

**R.4** Sparse term-weighting methods (DeepCT, SPARTA) fail to generalize despite strong in-domain scores, while the sparse document-expansion method docT5query instead beats BM25 on 11 of 18 datasets {C009}.

**R.5** Dense bi-encoders do well on some datasets but drop sharply under domain or task shift; DPR, trained only on QA data, generalizes worst of all ten systems {C010}.

**R.6** Even the two best-generalizing families are not universal: BM25+CE fails only on ArguAna and Touche-2020 (16/18 wins), while ColBERT wins on just 9 of 18 despite a strong average {C011}.

**R.7** TAS-B generalizes best among the dense models, but its two losses to ANCE trace to a documented mechanism -- a similarity-function-driven document-length preference, confirmed by a controlled ablation -- rather than only to the training-setup difference the authors speculate about {C012,C013,C014,C015,C016}.

**R.8** Domain-adaptive fine-tuning (GenQ) is not uniformly beneficial: it helps TAS-B on specialized domains but hurts it on broad domains like Wikipedia {C017}.

**R.9** A manual check on TREC-COVID shows dense systems had far more unjudged top-10 hits than lexical systems, and their scores rose far more once those hits were added {C018}.

**D.1** In-domain accuracy is a poor proxy for zero-shot retrieval performance, and a simple, untrained lexical baseline remains a meaningful reference point that most trained neural systems do not clear on average {C005}.

**D.2** Currently, the best zero-shot robustness requires the most expensive per-query computation, so architectures should be compared on both accuracy and cost, not accuracy alone {C008}.

**D.3** Because TREC-COVID's judgment pool undercounted non-lexical systems' hits, part of the lexical-vs-non-lexical gap reported anywhere in this paper may reflect annotation bias rather than pure retrieval quality, though this is confirmed on only one of the eighteen datasets {C019}.

**D.4** A 2024 follow-up on this benchmark makes a related point: averaging scores across such heterogeneous datasets into one number is itself hard to interpret, and proposes effect-size analyses instead (Kamalloo et al., 2024).

**D.5** Retrieval architectures should be compared on broad, heterogeneous suites, reported on both accuracy and cost, with fairer multi-strategy annotation pooling.

**L.1** We state five scope boundaries directly: English only; short, 512-word-piece-limited documents; text-only ranking signals; one-to-two document fields; and a generalist-only comparison, so task-specific models we did not evaluate can still beat every system here on its one task {L001,L002,L003,L004,L005}.

**L.2** No comparative number in this paper carries a variance or significance estimate, because most evaluated systems are checkpoints we did not train ourselves {L006}.

**L.3** Additional caveats: the annotation-bias case study covers one of eighteen datasets and was carried out by us, blinded to system identity but not by independent annotators; and our comparison is a fixed snapshot of 10 systems, while the released software has since grown to cover more {L007,L008}.

**C.1** In-domain accuracy is a poor guide to zero-shot retrieval performance, generalization trades off against compute, and simple lexical matching remains a meaningful reference point {C005,C008}.

**C.2** The annotation-bias finding and the scope boundaries above bound how far to read these rankings; fairer annotation pooling and broader-language, longer-document benchmarks are named next steps {C019,L007}.

---

## Skeleton self-reconstruction (Gate G2, manual -- no tool for this gate)

Read top-to-bottom only, against `evaluation_rubric.md` Section 1 (Q1-Q12):

- Q1 problem: I.1. Q2 motivation: I.2. Q3 missing: I.3. Q4 what was done: I.5/M.1-M.4/ES.1-ES.3.
  Q5 why this method: I.5/M.1/M.3 (rationale claims). Q6 experiments: R.1-R.9 titles name each one.
  Q7 strongest results: R.1-R.3 (with the Abstract already flagging magnitudes). Q8 what results
  establish: D.1-D.3. Q9 what they do not establish: L.1-L.3. Q10 primary contribution: I.6.
  Q11 main limitations: L.1-L.3 (spine line 7 matches L.1/L.2/L.3). Q12 one-day-later memory:
  C.1 restates the spine's key finding/meaning at claim strength.
- All 12 answerable from the skeleton alone. **Gate G2: passed** (recorded in `state.json`; no
  tool exists for this gate per `SKILL.md`, so the audit trail is this note itself).
