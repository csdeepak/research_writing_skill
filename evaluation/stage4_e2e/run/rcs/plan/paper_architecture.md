# Paper Architecture: Learning Which Agent to Ask (working title)

Story pattern: question_led
Audience mode: B · Binding personas: A, B, E · Venue profile: plan/venue_profile.yaml (all rules assumed)
Length limit (main text): 4500 · Planned total: 3885 excluding captions (86.3% of the limit; captions and table notes add about 200)

Each row is one paragraph slot. The skeleton (plan/skeleton.md) has one topic sentence per row.

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Words | Link forward |
|---|---------|---------------|--------------------------|----------------------|--------|---------|--------|-----------|-------|--------------|
| A.1 | Abstract | N01-N23 | What is this paper, in miniature? | Spine in 270 words with magnitudes and the main limit | C032 C001 C002 C007 C006 C005 C009 C010 C015 L004 | CORE | - | ASMOS, regret | 260 | Introduction |
| I.1 | Introduction | N01, N02, N09 | What is the problem, why care, what is ASMOS? | Global search costs tokens; ASMOS learns owners; no accuracy-saturation reason (authors rejected C024 in answering Q-002) | C033 C032 | CORE | - | ownership, global search | 170 | gap and questions |
| I.2 | Introduction | N03-N08 | What is missing and what do you ask? | A measurement gap; four RQs and a boundary check | C032 | CORE | - | RQ1-RQ4 | 200 | contributions |
| I.3 | Introduction | N23 | What do you contribute? | Five contributions with result references | C001 C002 C007 C006 C005 C009 C010 C012 C015 C030 | CORE | - | - | 150 | paper map |
| I.4 | Introduction | - | Where is what? | Paper map | - | CORE | - | - | 30 | Section 2 |
| R.1 | Related work | N03 | Where does this sit? | By dimension: routing, answering, adaptation; no novelty claim; citations missing | C032 C009 | CORE | - | RAG | 130 | Method |
| M.1 | Method | N09 | What is the system and what are the arms? | Checkpoints, router, A0 and A1 | C038 C032 | CORE | - | A0, A1 | 100 | ablation and similarity arms |
| M.2 | Method | N09, N10 | What are A2 and A3? | Frozen-ownership ablation and similarity routing | C005 C004 | CORE | - | A2, A3 | 50 | corpus and metrics |
| M.3 | Method | N10 | What data, model, seeds? | Constructed 50-query corpus, gpt-4o-mini, 10 seeds | C033 C034 C001 C006 L004 | CORE | - | - | 140 | statistics |
| M.4 | Method | N10 | Which metrics? | Tokens, accuracy, answerability, route@1 | C007 C008 L008 | CORE | - | answerability, route@1 | 100 | statistics |
| M.5 | Method | N10 | Which statistics and why? | Bootstrap, one-sided Wilcoxon, Kerby r, n_eff, no correction: the authors' reasons | C001 C002 C025 C026 C027 C028 (rationale: design_choice) | CORE | - | signed-rank | 165 | adaptation |
| M.6 | Method | N11 | How were adaptation runs set up? | New-topic regime with two embedders and classifier baselines; MiniLM rationale | C009 C010 C029 L009 | CORE | - | regret | 145 | QA setup |
| M.7 | Method | N12 | How was static QA set up? | Four systems on 24 items, single run | C013 L002 | CORE | - | RULER | 65 | Results |
| S.1 | Results 4.1 | N05, N13 | How much fewer tokens? | 22.1% fewer, with table of arms | C004 C001 C033 | CORE | Table 1 | - | 70 | certainty |
| S.2 | Results 4.1 | N13 | How certain is that? | CI 17.9% to 26.3%, W, p, r with n_eff, per-seed spread | C001 C002 C003 C035 | CORE | Fig 1 | - | 160 | RQ1 answer |
| S.3 | Results 4.1 | N19, N18 | What does RQ1 not show; other models? | Not organic, not other models, not equal accuracy; three further runs' statistics | C001 C036 C027 | CORE | - | - | 120 | accuracy |
| S.4 | Results 4.2 | N06, N14 | What did routing do to accuracy? | Answerability equal, accuracy lower in every seed | C006 C007 | CORE | Fig 2 | - | 90 | RQ2 answer |
| S.5 | Results 4.2 | N20 | Answer to RQ2 | Not a saving at equal accuracy; A3 trade-off; route@1 | C006 C007 C004 C008 | CORE | - | - | 100 | ablation |
| S.6 | Results 4.3 | N07, N15, N21 | Is the saving tied to ownership evolution? | Frozen ownership removes almost all of the saving; consistent with, low confidence | C004 C005 C008 | CORE | - | - | 110 | adaptation |
| S.7 | Results 4.4 | N08, N16 | New topic: regret and retrains? | ASMOS regret 3.24 and 0.92 with 0 retrains versus 4.8 to 10.0; zero retraining, 10 labels consumed as recorded (Q-004) | C009 C010 C022 | CORE | Fig 3 | - | 150 | qualifications |
| S.8 | Results 4.4 | N16, N22 | What qualifies the adaptation result? | Embedder dependence, labels counter, identical answerability, lexical-hash negative result; RQ4 answer | C009 C010 C011 C012 | CORE | - | - | 190 | QA boundary |
| S.9 | Results 4.5 | N12, N17 | Does ASMOS help on static QA? | No: scores below No-Memory and RAG; paired intervals; tokens | C013 C014 C015 C037 L003 | CORE | Table 2 | - | 200 | statistics correction |
| S.10 | Results 4.6 | N18 | Were any statistics corrected? | Stored r and z superseded; W, p, interval unchanged | C030 | CORE | - | - | 75 | Discussion |
| D.1 | Discussion | N19-N22 | What are the four answers? | One line each | C001 C006 C007 C005 C009 C010 | CORE | - | - | 65 | interpretation |
| D.2 | Discussion | N21, N27 | What explains the pattern? | Ownership between global and similarity routing; untested explanation | C004 C006 C005 C007 | CORE | - | - | 100 | implications |
| D.3 | Discussion | N27 | What follows in practice? | Candidate cost tool within limits; no evidence for QA quality | C001 C009 C015 | CORE | - | - | 75 | Limitations |
| L.1 | Limitations 6.1 | N24-N26 | What do the authors concede? | Interval, constructed corpus, QA scope, metric gaps | L001 L004 L003 L002 | CORE | - | - | 120 | further concessions |
| L.2 | Limitations 6.1 | N24-N26 | What else do the authors concede? | Convergence, descoped items, tuning, embedders, CI artifact | L005 L006 L007 L008 L009 L010 | CORE | - | - | 220 | additional caveats |
| L.3 | Limitations 6.2 | N25 | What further caveats apply? | Additional caveats (writer-derived) | L011-L020 | CORE | - | - | 200 | Conclusion |
| C.1 | Conclusion | N23, N28 | What should the reader remember? | Saving, accuracy cost, boundary, next questions | C001 C007 C005 C009 L004 C015 | CORE | - | - | 100 | - |
| V.1 | Availability | - | Where are data and code? | Markers for the authors | - | CORE | - | - | 35 | - |

## Checks
- [x] Every story-graph node appears in at least one row
- [x] Every RQ has result rows, interpretation rows and discussion rows (RQ1 S.1-S.3/D.1; RQ2 S.4-S.5/D.1; RQ3 S.6/D.2; RQ4 S.7-S.8/D.1)
- [x] Question ledger: Q03 and Q09 are the only deferred questions, both with pointers
- [x] Term ledger: each defining row precedes first use (route@1 and regret defined in the abstract)
- [x] Every visual has a card in plan/figure_cards/
- [x] Negative results placed per their decisions (E015 in S.4, E072 in S.8, E078 in S.9; E094 excluded, reason recorded)
- [x] Every author_stated limitation has a Limitations row (L.1, L.2); writer-derived caveats have a separate "Additional caveats" row (L.3)
- [x] Every rationale claim has a slot: C031 in I.1 (motivation); C025-C028 in M.5 and C029 in M.6 (design choice)
- [x] Planned words sum to 3885 (86.3% of 4500) before captions

## Revision after blind review v001_1 (draft v002)

Structural changes made in the artifacts before regenerating prose (see revisions/v001_1/dispositions.json):
- M.1 now states only the recorded mechanism and lists the unspecified mechanics as [ASK AUTHOR] (checkpoint Q-005); C038 (memory contract) dropped as jargon the argument does not need.
- M.2 states that A2 collapses to global search (C005 narrowed: routing versus no routing).
- M.3/M.4 label the seed basis of every measure, the unrecorded embedder of the cost run (C039), the token-accounting scope (L021), seed dependence (L023) and the unrecorded route@1 denominator (L025); C034 and C035 dropped (over-precision).
- M.6 states the fairness conditions of the new-topic comparison before its results (L022) and gives one embedder mapping per experiment (C039); agent count unrecorded (L024).
- I.1: C031 removed (placeholder for a rationale the draft did not give); the rationale E111 is carried by C024, which the authors rejected in their answer to Q-002 (no 'equal accuracy' or 'saturation' claim), so it stays out of the paper.
- I.3: four contributions, each a result; the statistics correction (C030), the other-model statistics (C036) and the stationary MiniLM values (C012) move to Appendix A, with pointers from Sections 4.1 and 4.4 (the lexical-hash negative result stays in the main text).
- S.9 adds the exact-match versus token-F1 anomaly (L016) and an explicitly untested possibility for ASMOS-memory's shortfall (C040, speculation).
- D.3 adds the practical weight of the saving and the unmeasured cost ledger (L021, L024); "small accuracy cost" removed everywhere.
- Rationale slots: C025-C028 in M.5, C029 in M.6; C024 (motivation) rejected by the authors (Q-002) and not used.
