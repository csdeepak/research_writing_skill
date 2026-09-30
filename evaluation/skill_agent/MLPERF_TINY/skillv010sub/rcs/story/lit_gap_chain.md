# Literature -> Gap -> Question chain

```
DIMENSION: general-purpose MCU benchmarking (SRC-009)
  ACHIEVES: an easy-to-port, widely adopted way to compare raw MCU-class compute performance {C009}
  SHARED ASSUMPTION: a handful of fixed general-purpose algorithms is a sufficient performance proxy
  EVIDENCE OF GAP: does not profile full programs and does not represent ML inference workloads (SRC-009, as characterized in project/paper.txt Sec.3) -- 1 source, stated by MLPerf Tiny's own authors
  UNRESOLVED: no MCU-class benchmark in this dimension touches ML workloads at all

DIMENSION: real-workload ML inference benchmarking (SRC-019, SRC-018)
  ACHIEVES: benchmarking with actual trained ML models rather than synthetic kernels, plus (for SRC-018) a broad, community-governed submission/review process {C010, C011}
  SHARED ASSUMPTION: the target device has gigabyte-scale memory and can run standard-scale reference models
  EVIDENCE OF FAILURE: SRC-019's models are far too large for MCU-class devices and it has no power measurement; SRC-018 explicitly precludes MCUs and other resource-constrained platforms for lack of small benchmarks and compatible implementations -- 2 sources, both stated by MLPerf Tiny's own authors (project/paper.txt Sec.3)
  UNRESOLVED: whether a benchmark could keep real-workload realism and community governance while dropping the gigabyte-scale assumption -- no retrieved source in this closed corpus attempts it

GAP (scoped to the 22 works cited in project/paper.txt, MLPerf Tiny's own reference list):
  "As Table 1 summarizes, there is a clear and distinct need for a TinyML benchmark that caters
  to the unique needs of ML workloads, makes power a first-class citizen, and prescribes a
  methodology that suits TinyML" {C012} -- none of the three examined efforts (SRC-009, SRC-019,
  SRC-018) jointly measures ML-inference accuracy, latency, AND energy on MCU-class hardware with
  a reproducible, modular methodology.

QUESTION (RQ, story node N05):
  Can one benchmark suite fairly measure accuracy, latency, and energy for representative ML
  workloads on MCU-class hardware, while still letting a specific hardware or software
  contribution be demonstrated and directly compared against a common reference?
```

## Chain-rule check
- The "achieves"/"shared assumption" parts each rest on reading MLPerf Tiny's own Related Work
  section (project/paper.txt, Section 3), which itself names 3 distinct prior efforts (>=2 sources
  for the ML-inference dimension) -- satisfies citation_rules.md S5's "≥2 sources" rule for that
  dimension; the general-MCU-benchmarking dimension rests on 1 source (SRC-009) because only one
  such benchmark (CoreMark) is discussed in the evidence, so the GAP wording below avoids implying
  a systematic multi-source survey for that dimension specifically.
- The GAP statement is scoped to "the three efforts MLPerf Tiny's authors discuss," not to "no
  prior work anywhere" -- this run performed no independent literature search (no web), so a
  stronger, search-scoped "first/no prior work" claim is not licensed and is not made anywhere in
  the paper.
- Answering the QUESTION (building and field-testing such a suite) directly targets the GAP: a
  suite that measures all three metrics on MCU hardware with a reproducible protocol closes
  exactly the shortfall identified above.
