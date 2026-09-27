# Step 14 — Terminology / cognitive-load audit

**Term ledger check.** All entries in `story/term_ledger.json` have `defined_at` preceding
`first_used_at` in the final draft ordering (agent loop -> §1 ¶1; agent hub -> §1 ¶4 before §3;
CodeActAgent/BrowsingAgent -> §1 ¶4 before §3 detail; resolve rate, 0-/1-shot -> §2 ¶1 before §5.1
uses them). Benchmark proper nouns (SWE-Bench Lite, HumanEvalFix, WebArena, MiniWoB++, GAIA, GPQA,
AgentBench, MINT, ProofWriter, Entity Deduction Arena, ML-Bench) are each given a one-clause gloss
at first mention in §4, before §5 uses them by name only.

**Synonym drift (A5).** "Resolve rate" is used consistently for SWE-Bench-style scoring; "success
rate" / "accuracy" are used only where the underlying benchmark itself defines that metric name
(not as free variation for the same concept). "Agent hub" is never renamed "toolkit" or "library"
after its definition. No drift found.

**New-concept rate (mode B: <=2 new terms/paragraph).** Re-checked §2 ¶1 (three conventions
introduced: resolve rate, shot setting, success-rate/accuracy split) — this exceeds the soft budget
of 2, but the paragraph exists specifically to front-load these three conventions before Section 5,
which is the paragraph's stated job (skeleton B.1); flagged and accepted rather than split, since
splitting would separate closely related conventions the reader needs together. Recorded as an
accepted deviation, not silently ignored.

**Sentence length (>35 words).** `lint_draft.py` flags 40 sentences over 35 words (INFO level).
Reviewed the five longest (79, 84, 82, 73, 71 words): each carries one qualified idea (a number
plus its immediate qualifying clause) rather than two unrelated ideas joined by "and"; kept as is
per `information_design.md` §3's guidance that sentence splitting is a judgment call, not a hard
rule, when the ideas are tightly coupled (a value and the caveat that must travel with it, e.g. the
gpt-4o-mini SWE-Bench-Lite conflict sentence). No sentence was found joining two independent claims
that should be split into separate paragraphs.

**Density classes.** Hyperparameter-level detail (turn limits, solution-attempt counts) is kept in
Table 1/§4 (SUPPORTING, in a table) rather than narrated in §5 prose. Cost estimates (E018, E019)
are SUPPORTING, placed once in §4 and referenced once in §6, not repeated. No DISTRACTING content
(project chronology, tool trivia) was found in the draft.
