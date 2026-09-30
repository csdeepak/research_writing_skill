# Literature -> Gap -> Question chain

```
DIMENSION: broad-coverage retrieval evaluation efforts (SRC-019 MultiReQA, SRC-050 KILT)
  ACHIEVES: cross-domain / multi-dataset evaluation beyond a single retrieval dataset {N04}
  SHARED ASSUMPTION: one task type (question answering, for MultiReQA) or one corpus domain
    (Wikipedia, for both) is a sufficient stand-in for retrieval breadth
  EVIDENCE OF FAILURE (i.e. of insufficient breadth): MultiReQA covers only sentence-level QA
    retrieval, 5/8 datasets from Wikipedia, 6/8 with <100k candidate sentences (E045); KILT covers
    5 tasks/11 datasets but only from Wikipedia and with retrieval as a secondary task, not the
    evaluated object (E046) -- 2 sources
  UNRESOLVED: neither shows how different retrieval ARCHITECTURES (lexical vs. sparse vs. dense
    vs. late-interaction vs. re-ranking) compare when generalizing zero-shot across many tasks and
    domains at once
GAP (scoped): "Among the two broad-coverage retrieval evaluations available in the project
  materials (MultiReQA, KILT), neither evaluates retrieval zero-shot across many task types and
  domains at once, so it is unknown whether the large in-domain gains neural rankers show over
  BM25 (established on MS MARCO/NQ-style single-dataset evaluation, SRC-045/SRC-034) transfer
  out of domain, and which architecture family generalizes best." {N05}
QUESTION: RQ1 (N06) = "How well, and via which architectural mechanisms, do ten representative
  retrieval systems from five architecture families generalize zero-shot across diverse tasks and
  domains, relative to the lexical baseline BM25?"
```

```
DIMENSION: pooling / annotation-bias literature (SRC-039 Lipani 2019; SRC-040 Lipani et al. 2016)
  ACHIEVES: names and studies selection bias arising from how retrieval test-collection candidate
    pools are built (only documents retrieved by some existing system are ever judged) {N28}
  SHARED ASSUMPTION: a pool built from a diverse-enough set of systems is approximately fair to
    all architecture types
  EVIDENCE OF FAILURE: several BEIR datasets are documented to have been pooled predominantly
    with lexical term-matching systems (BioASQ, SRC-061; Signal-1M, SRC-059) (E036) -- 2 sources
  UNRESOLVED: whether this pooling practice measurably disadvantages non-lexical systems in a
    benchmark comparison such as RQ1's, and by how much
GAP (scoped): "Among the pooling-bias literature available in the project materials, it is
  documented that pools are commonly built with the help of existing (often lexical) systems, but
  the size of the resulting disadvantage to non-lexical systems specifically within a BEIR-style
  zero-shot comparison is not established." {N12}
QUESTION: RQ2 (N13) = "Do existing pooling/annotation practices for retrieval test collections
  systematically disadvantage non-lexical systems in a way that affects the RQ1 comparison?"
```

**Chain rule check:** each GAP rests on ≥2 sources for its "achieves"/"shared assumption" parts
(MultiReQA+KILT; Lipani 2019 + Lipani et al. 2016), each "evidence of failure" cites a source that
actually shows the limitation (not merely a source that didn't test it), and each QUESTION, if
answered, narrows exactly the stated gap. The novelty claim C020 ("to the authors' knowledge, BEIR
is the first...") is scoped to these two specific comparison points, matching the hedge in the
source (E047), per citation_rules.md §5.
