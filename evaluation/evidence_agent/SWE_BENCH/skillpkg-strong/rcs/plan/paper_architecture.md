# Paper Architecture

Pattern: question-led (single RQ, five experiments answering it from different angles; `research_story.md` Sec.6).
Venue: generic (assumed). Audience: mode B (adjacent ML researcher).

| # | Section | Story node(s) | Reader question | Claims | Density | Terms introduced |
|---|---------|---------------|------------------|--------|---------|-------------------|
| 1 | Title | N19 | What is this about? | C011 | CORE | SWE-bench |
| 2 | Abstract | N01-N05,N10,N11,N19,N20 | Whole-paper summary | C011,C001,C002,C004 | CORE | issue resolution, resolve rate |
| 3 | Intro P1 | N01,N02 | What's the problem, why care? | C011 | CORE | — |
| 4 | Intro P2 | N03,N04 | What's missing from prior evaluation? | C011,C012 | CORE | function-level code generation |
| 5 | Intro P3 | N05 | What does this paper ask? | — | CORE | — |
| 6 | Intro P4 | N06,N07,N25 | What did they do (one idea)? | C011 | CORE | BM25 retrieval, oracle retrieval |
| 7 | Intro P5 (contributions) | N19 | What's the contribution? | C011,C001,C002 | CORE | — |
| 8 | Intro P6 (paper map) | — | Where is what? | — | CORE | — |
| 9 | Related Work | N03,N04 | Why is this question necessary? | C011,C012 | CORE | — |
| 10 | Method: benchmark construction | N07,N08,N24 | How was SWE-bench built and checked? | C011 | CORE/SUPP split | task instance, FAIL_TO_PASS/PASS_TO_PASS, patch |
| 11 | Method: dataset characterization | N09 | How hard/realistic are the tasks? | C012 | CORE | — |
| 12 | Experimental setup | N08,N25 | How are models evaluated? | — | CORE | Pass@1, resolved vs applied |
| 13 | Results RQ-BM25 | N10 | How well do models do with automatic retrieval? | C001,C015,C004 | CORE | — |
| 14 | Results RQ-oracle | N11,N12 | Does perfect localization change this? | C002,C006 | CORE | — |
| 15 | Results RQ-collapsed | N14 | Does removing clutter help further? | C003 | CORE | — |
| 16 | Results RQ-context length | N13 | Does more context help or hurt? | C005 | CORE | — |
| 17 | Results RQ-temporal | N15,N16 | Could models be memorizing solutions? | C007,C008 | CORE | — |
| 18 | Results RQ-patch-style | N17 | How do model edits compare structurally to gold edits? | C009 | SUPPLEMENTARY (brief) | — |
| 19 | Results RQ-finetuning | N18 | Does fine-tuning a smaller model close the gap? | C010 | CORE | LoRA (glossed) |
| 20 | Discussion: answers to RQ | N12,N16,N19 | So what does it all mean? | C001,C002,C006,C008 | CORE | — |
| 21 | Discussion: implications | N22 | What does this change going forward? | C006 | CORE | — |
| 22 | Limitations | N20,N21 | What shouldn't we conclude? | L001-L006 | CORE | — |
| 23 | Conclusion | N19,N23 | What's the takeaway and what's next? | C011,C001,C002,C014 | CORE | — |

Question ledger check: RQ (N05) raised in slot 5, answered incrementally in slots 13-19, closed explicitly in slot 20. No debt >3 beyond the paper map (slot 8 defers implementation and full statistics to slots 10-12, matplotlib/repo detail to slot 11 — 2 deferrals, within budget).

Term ledger check: BM25/oracle defined at slot 6 before first quantitative use in slot 13. "resolved" vs "applied" defined at slot 10/12 before Results. No undefined acronym used >=3 times without expansion (LoRA glossed once, used once in slot 19 — spelled out, not treated as a load-bearing acronym).

No figures are used (task forbids images); all visual content is presented as Markdown tables with a stated takeaway sentence before each table, satisfying figure_table_rules.md's "reference before appearance" rule for tables.
