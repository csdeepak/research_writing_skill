# Literature → Gap → Question chain

DIMENSION: realism and verification of coding-evaluation tasks (evidence: the project's own framing, N03/N04 in story_graph.json; no external source verifies this dimension in this run — see corpus/source_registry.json)
  ACHIEVES: (as characterized in the evidence package) prior coding benchmarks provide tractable, checkable problems {C001 context}.
  SHARED ASSUMPTION (as characterized in the evidence package): problems are short and self-contained, with a scope much narrower than an engineer's real task of navigating a large codebase.
  EVIDENCE OF SCALE MISMATCH: SWE-bench's own codebases average 3,010 non-test files and 438,000 lines of code (E005, E007) — far beyond a self-contained function-level problem.
  UNRESOLVED (per the evidence package): whether models' coding ability, independent of context-finding ability, is sufficient for realistic repository-scale tasks is untested by prior short-problem benchmarks.

GAP (scoped to this evidence package, not a systematic search): the evidence package documents no existing benchmark, among those it discusses, that grounds tasks in real GitHub issues and pull requests against full repositories with executable, test-based verification (fail-to-pass / pass-to-pass tests) of correctness (C001, N04).

QUESTION (RQ, story_graph.json N05): Given a real GitHub issue and its full repository, can current language models generate a patch that resolves the issue — and what determines whether they succeed?

Chain rules followed: the GAP statement above is explicitly scoped to what this evidence package documents, not to a systematic search (no web access in this run); "first"/"novel" language is avoided in the paper unless directly licensed by an evidence item. SRC-001 is used only as corroboration for one interpretive claim (C017), not to establish the gap itself.
