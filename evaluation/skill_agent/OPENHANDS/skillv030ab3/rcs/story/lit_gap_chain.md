# Literature -> Gap -> Question chain (scoped to the project's own related work)

DIMENSION: general agent frameworks (SRC-001, SRC-002, SRC-003, SRC-033, SRC-034, SRC-035)
  ACHIEVES: building blocks and multi-agent conversation (authors' description) {C004}
  SHARED LIMIT: AutoGen has stateless command execution; CrewAI has a limited code interpreter (SRC-002, SRC-035; two sources, both as characterized by the OpenHands authors) {C005}
  EVIDENCE OF FAILURE: none beyond the authors' characterization; no source was read.
DIMENSION: software-engineering agents (SRC-004, SRC-005)
  ACHIEVES: GitHub issue fixing {C005}
  SHARED LIMIT: domain-specific per Table 1 domain column {C005}
GAP (scoped): In the OpenHands authors' own description of related work, no single listed framework is described as combining a stateful sandboxed shell, Python and browser runtime, a shared tool library, delegation and a benchmark harness. The Table 1 feature marks that would support this are not recoverable from the extracted text, so the paper states the gap as the authors' positioning and not as a finding of a literature search.
QUESTION: RQ1 (design) and RQ2 (evaluation), derived from the authors' stated goal {C003}.
STATUS: INSUFFICIENT_LITERATURE accepted as workflow risk AR4 (no web, works cited in the project only).
