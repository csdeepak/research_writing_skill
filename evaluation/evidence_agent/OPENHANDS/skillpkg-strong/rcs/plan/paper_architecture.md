# Paper Architecture: OpenHands generalist-agent platform paper

Story pattern: question_led
Audience mode: B (adjacent ML researcher) · Binding personas: A, B, E · Venue profile:
plan/venue_profile.yaml (generic, all rules assumed; VENUE_UNKNOWN, no venue specified)

| # | Section | Story node(s) | Reader question answered | Point | Claims | Density | Visual | New terms | Link forward |
|---|---------|---------------|---------------------------|-------|--------|---------|--------|-----------|--------------|
| I.1 | Introduction | N01,N20 | What is an LLM agent and why does testing one need infrastructure? | Testing an agent on real tasks needs a loop, a sandbox, and per-benchmark harnesses. | C017 | CORE | — | LLM agent | leads to: this is costly to duplicate |
| I.2 | Introduction | N02,N04 | What's missing? | Evaluation is organized as separate per-domain families; a shared, verifiable cross-domain comparison is not established in the available material. | — | CORE | — | — | so we ask |
| I.3 | Introduction | N05 | What exactly is asked? | Can one unmodified general agent be evaluated across software, web, and misc. tasks via one platform? | — | CORE | — | — | approach |
| I.4 | Introduction | N06,N07 | What did they build? | OpenHands: an agent hub + a 15-benchmark evaluation framework, MIT-licensed. | C017 | CORE | — | agent hub, CodeActAgent, BrowsingAgent | contributions |
| I.5 | Introduction | N16 | What is contributed and found? | Contributions list + headline numbers, at claim strength. | C001,C002,C004 | CORE | — | — | paper map |
| B.1 | Background | N20 | What is an agent loop, concretely? | Define agent loop, resolve rate, 0-/1-shot. | — | CORE | — | resolve rate, 0-shot/1-shot | into method families |
| B.2 | Background/Related | N03 | What existing baselines exist per domain? | Dimension matrix: code-repair, web, misc. baselines and what each assumes. | C001,C009,C010,C011,C012 | CORE | Table 1 (baseline map) | — | platform description |
| P.1 | Platform (§3) | N07,N20 | What is OpenHands, concretely? | Agent hub (>10 agents), CodeActAgent, BrowsingAgent, evaluation framework (15 benchmarks/3 categories), MIT license. | C017 | CORE | — | — | setup |
| S.1 | Evaluation setup (§4) | N08,N10,N12 | How was each category evaluated? | Per-category benchmark descriptions, instance counts, shot settings. | — | CORE/SUPPLEMENTARY split | Table 2 (benchmarks) | — | results |
| R.1 | Results §5.1 (software) | N08,N09 | What happened on code-fix tasks? | RIC for SWE-Bench Lite and HumanEvalFix. | C001,C002,C003,C018 | CORE | Table 3 | — | web results |
| R.2 | Results §5.2 (web) | N10,N11 | What happened on web tasks? | RIC for WebArena and MiniWoB++, incl. negative results. | C009,C010 | CORE | Table 4 | — | misc results |
| R.3 | Results §5.3 (misc.) | N12,N13,N14 | What happened on misc. tasks? | RIC for GAIA, GPQA, AgentBench OS, MINT, ProofWriter, EDA, incl. negative results. | C004-C008,C011-C013,C020 | CORE | Table 5 | — | discussion |
| D.1 | Discussion | N15 | What does the pattern mean? | Interpret mixed results as a generalist-platform contribution, not a single-benchmark SOTA claim. | C014,C015,C019 | CORE | — | — | limitations |
| D.2 | Discussion | N19 | What comes next? | Future directions the authors name. | C016 | CORE | — | — | limitations |
| L.1 | Limitations | N17 | What bounds these claims? | No variance; two internal conflicts; unverifiable table cells; budget parity unknown. | L001-L009,C018,C020 | CORE | — | — | conclusion |
| C.1 | Conclusion | N16,N18 | What should the reader remember? | Restate contribution and its scope at claim strength. | C017 | CORE | — | — | — |

## Checks
- [x] Every story-graph node appears in >=1 row (N01-N20 covered above; N20 also implicit in B.1)
- [x] The single RQ (N05) has result rows (R.1-R.3), interpretation rows (D.1), discussion rows (D.1-D.2)
- [x] No row without a story node
- [x] Question ledger: 0 debt at end (story/question_ledger.json)
- [x] Term ledger: defining rows precede first-use rows (story/term_ledger.json)
- [x] Tables (no images, per TASK.md) have takeaways stated in prose before/at first reference
- [x] Negative results (E082, E100, E030, E040) placed per negative_result_decisions (all reported_main)
