# Literature -> Gap -> Question chain

DIMENSION: workload realism and power measurement (SRC-001, SRC-002; MLMark by name only)
  ACHIEVES: CoreMark is the standard MCU-class benchmark with a power extension; MLMark uses actual ML workloads; MLPerf inference is a community ML inference suite {C003}
  SHARED LIMITATION: none provides ML benchmarks small enough for MCU-class devices together with power measurement (per the authors' text) {C003}
  EVIDENCE OF FAILURE: as characterized by the authors only (E040, E041, E042); the sources were not read
GAP (scoped to the authors' characterization): among the benchmarks the authors discuss, none targets TinyML inference workloads on tiny hardware with power as a first-class quantity {C003, C002}
QUESTION: how can one design an open benchmark, for heterogeneous TinyML hardware and software stacks, that measures accuracy, latency and energy, and that compares fairly while letting different kinds of contribution be shown {C023, C025, C027, C028}
NOTE: this chain rests on three benchmarks (two registered sources plus MLMark by name). The gap is worded as the authors' claim, not as a search-scoped finding; "first" and "no prior work" are not used.
