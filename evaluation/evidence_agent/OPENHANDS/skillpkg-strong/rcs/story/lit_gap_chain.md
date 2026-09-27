# Literature -> Gap -> Question chain

DIMENSION: per-domain baseline agents and specialist systems (SRC-001..SRC-009)
  ACHIEVES: strong results within their own single domain (e.g. Agentless leads SWE-Bench Lite
  among reported baselines at 27.3%; CC-NET leads MiniWoB++ at 91.1%) {C001}{C010}.
  SHARED ASSUMPTION: each baseline is built and evaluated for one task family (code repair, or
  web micro-tasks, or one reasoning benchmark) with its own harness and, in several cases,
  benchmark-specific training (CC-NET, Workflow Guided Exploration).
  EVIDENCE AVAILABLE: the nine registered sources (SRC-001..SRC-009) collectively span software,
  web, and misc.-assistance domains but none is evaluated across all three in the material
  available to this run.
  UNRESOLVED: whether a single general agent, run unmodified, can be assessed across all three
  domains at once is not addressed by any one of these sources individually.

GAP (scoped to the works cited in the available evidence): among the nine sources this run can
verify, none reports one unmodified agent evaluated across software-engineering, web-interaction,
and miscellaneous-assistance benchmarks through a shared harness. This paper does not claim this
is true of the wider field (the source paper's own framework-comparison table, which might
substantiate a broader novelty claim, is unreadable in this evidence package; see Limitations).

QUESTION: Can one general-purpose agent, evaluated through a single open platform and harness,
be measured across all three categories, and does its performance pattern support treating the
platform itself (rather than a single top score) as the contribution?
