# Literature -> Gap -> Question chain

```
DIMENSION: does the workload represent real ML inference? (SRC-002 CoreMark)
  ACHIEVES: a simple, portable, widely-adopted MCU-class performance benchmark {C003}
  SHARED ASSUMPTION: a short, fixed, generic workload is representative enough of MCU performance
  EVIDENCE OF FAILURE: the authors state directly that it "does not profile full programs, nor
    does it accurately represent machine learning inference workloads" (project/paper.txt,
    Section 3) -- 1 source
  UNRESOLVED: whether any generic-code MCU benchmark could be adapted to ML workloads at all (not
    addressed by the retrieved source)

DIMENSION: does the memory/compute envelope match MCU-class devices, and is power measured?
  (SRC-003 MLMark, SRC-004 MLPerf Inference)
  ACHIEVES: MLMark uses real ML inference workloads {C004}; MLPerf Inference is a broad,
    community-governed inference-benchmarking effort {C005}
  SHARED ASSUMPTION: edge/server/mobile-class devices have on the order of gigabytes of memory
    and can run production-scale models
  EVIDENCE OF FAILURE: the authors state that MLMark's "supported models are far too large for
    MCU-class devices...require far too much memory (GBs)" and that MLMark itself has no power
    measurement; separately, that "the current MLPerf inference benchmark precludes MCUs and
    other resource-constrained platforms due to a lack of small benchmarks and compatible
    implementations" (project/paper.txt, Section 3) -- 2 sources
  UNRESOLVED: whether a smaller model set alone would suffice, or whether power measurement
    needs its own methodology (this is exactly what MLPerf Tiny's own Section 2 "Challenges"
    argues requires new design, not just smaller models)

GAP (scoped to the three benchmarks the source paper itself compares against): "Among the prior
  benchmarks the authors discuss, none both (a) uses real ML inference workloads and (b) fits
  the memory/power envelope of microcontroller-class devices while (c) measuring power as a
  first-class metric. The authors state this directly: 'there is a clear and distinct need for
  a TinyML benchmark that caters to the unique needs of ML workloads, makes power a first-class
  citizen and prescribes a methodology that suits TinyML' {C006}."

QUESTION: "Can one benchmark suite fit the extreme memory and power constraints of
  microcontroller-class devices, measure accuracy, latency, and energy together, and still let
  a fair comparison be made across the field's highly heterogeneous hardware and software
  stacks?" (spine line 3; story graph node N05)
```

**Scope note.** This chain is built only from the three prior benchmarks the source paper
itself names and critiques (project/paper.txt, Section 3), not from an independent, systematic
literature search -- no web access is available in this run (accepted risk AR-003, recorded in
`.rcs/state.json`). The Gap statement above is worded to match: it says "among the prior
benchmarks the authors discuss," not "no prior work anywhere," and the new paper's Introduction
and Related Work sections use the same scoped wording.
