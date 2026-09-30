# Paper Architecture: MLPerf Tiny (working title)

Story pattern: method_first (problem -> gap -> question -> design -> results -> discussion), with the three questions RQ1-RQ3 as the organizing frame
Audience mode: B (adjacent researcher) · Binding personas: B · Venue profile: plan/venue_profile.yaml (assumed rules: all)
Length limit (main text): 4500 · Planned total: 3950 (<= 90% = 4050)

| # | Section | Story node(s) | Reader question answered | Point | Claims | Density | Visual | New terms | Words | Link forward |
|---|---------|---------------|--------------------------|-------|--------|---------|--------|-----------|-------|--------------|
| A.1 | Abstract | N01-N23 | Whole paper in miniature | spine 1-7 | C001 C003 C012 C015 C018 C023 L002 L003 | CORE | - | TinyML | 190 | - |
| I.1 | Introduction | N01 N02 | What is the problem and why care? | comparing TinyML systems is hard and needed | C001 C024 | CORE | - | TinyML, MCU | 130 | why existing benchmarks do not solve it |
| I.2 | Introduction | N03 N04 | What is missing? | existing benchmarks do not fit | C003 | CORE | - | - | 100 | so we present the question |
| I.3 | Introduction | N05-N07 | What does the paper ask? | three questions | C023 C025 C028 | CORE | - | closed/open division | 90 | approach |
| I.4 | Introduction | N08 N18 | What did the authors do? | four tasks, framework, divisions, >50 orgs | C023 C005 | CORE | - | reference implementation | 90 | contributions and map |
| I.5 | Introduction | N18 | Contributions and map | numbered contributions with result pointers; section map | C004 C006 C008 C012 C015 | CORE | - | - | 100 | challenges |
| S2.1 | 2 Challenges | N01 | Why is fair comparison hard? | five challenges | C002 | CORE | - | DUT, system under test | 260 | related work |
| R.1 | 3 Related work | N03 N04 | How do prior benchmarks fall short? | CoreMark, MLMark, MLPerf inference by dimension | C003 | CORE | - | - | 220 | design |
| M.1 | 4.1 Tasks | N09 N24 | Which tasks, data, models? | four tasks; Table 1 | C004 C030 C031 C032 C033 | CORE | TAB-1 | keyword spotting, visual wake words, log-mel spectrogram | 380 | targets |
| M.2 | 4.1 Tasks | N09 | Design details per task | KWS / AD specifics and reasons | C030 C031 | SUPPORTING | - | - | 140 | quality targets |
| M.3 | 4.2 Quality targets | N09 N24 | How were targets set? | slack for quantization | C029 | CORE | - | PTQ, QAT | 170 | rules |
| M.4 | 4.3 Divisions and modularity | N10 | What may submitters change? | closed and open; modular | C006 C007 C027 C028 C005 | CORE | - | closed/open division | 200 | measurement |
| M.5 | 4.4 Measurement | N10 N25 | How are latency, accuracy, energy measured? | median of five; framework | C008 C009 C025 C026 C034 | CORE | - | IPS, uJ per inference | 300 | results |
| R.2 | 5.1 Reference results | N12 N15 | Do the references clear targets, by how much? | Table 2 | C010 C011 C012 C013 C035 | CORE | TAB-2 | - | 320 | board results |
| R.3 | 5.2 Reference implementations | N13 | What do the references measure on the board? | statement only; values unavailable | C014 | CORE | - | - | 100 | submissions |
| R.4 | 5.3 v0.5 round | N14 N17 | What did the first round show? | Table 3; trends; no dataset modified | C015 C016 C017 C018 | CORE | TAB-3 | - | 320 | discussion |
| D.1 | 6 Discussion | N15-N17 | Answers to RQ1-RQ3, meaning | RQ answers at authors' strength | C018 C029 C027 C028 | CORE | - | - | 220 | implications |
| D.2 | 6 Discussion | N22 | Implications, adoption, impact | authors' expectations flagged as such | C020 C021 C019 | SUPPORTING | - | - | 110 | limitations |
| L.1 | 7 Limitations | N19 N20 | What do the authors concede? | L001-L004 | L001 L002 L003 L004 | CORE | - | - | 270 | additional caveats |
| L.2 | 7 Limitations | N21 | Additional caveats | L005-L009 | L005 L006 L007 L008 L009 | CORE | - | - | 150 | conclusion |
| K.1 | 8 Conclusion | N18 N23 | Synthesis and next steps | finding, boundary, future | C023 C022 | CORE | - | - | 120 | - |

Checks
- [x] Every story-graph node appears in >= 1 row
- [x] Every RQ has result, interpretation and discussion rows (RQ1: R.2/D.1; RQ2: R.3/D.1; RQ3: R.4/D.1)
- [x] No row without a story node
- [x] Question ledger: no planned debt beyond forward pointers (story/question_ledger.json)
- [x] Term ledger: definitions precede first use (story/term_ledger.json)
- [x] Every visual has a card (TAB-1, TAB-2, TAB-3; FIG-5 blocked, not drawn)
- [x] SUPPLEMENTARY items have a destination: framework hardware detail is compressed in 4.4 (full detail stays in the authors' appendix A, cited as such)
- [x] Negative results: none recorded in evidence; absent items (no variance, no Figure 5 values, no submission measurements) are stated as limitations
- [x] Every author-stated limitation has a Limitations row (L.1); writer-derived caveats sit in L.2 ("Additional caveats")
- [x] Every rationale claim has a row: motivation C001 in I.1; design_choice C025 C026 C027 C028 C029 C030 C031 C032 C033 C034 in Introduction/Design sections
- [x] Sum of words 3950 <= 4050
