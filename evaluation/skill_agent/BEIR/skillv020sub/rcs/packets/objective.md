In the authors' words, this paper is meant to show which retrieval architectures actually
generalize once evaluation leaves the single dataset most of the field trains and tests on, and
at what computational cost, because it was previously unclear how retrieval models trained on one
domain or task would perform on a different one, and no existing multi-dataset resource tested
that kind of generalization broadly. The paper introduces BEIR, a benchmark of 18 datasets across
9 retrieval tasks built to be diverse in task type, domain, difficulty, and annotation method, and
uses it to compare ten public systems spanning five retrieval architecture families under one
shared metric and protocol. A reader should come away understanding that a system's accuracy on
the field's dominant single-dataset benchmark does not predict its zero-shot accuracy elsewhere;
that the architectures which generalize best on average also cost up to 20-30 times more to run
per query than the alternatives; and that a benchmark's own relevance judgments are not automatically
neutral across architecture families, which the paper demonstrates with a manual case study on one
dataset and uses to bound how precisely its own reported margins should be read.
