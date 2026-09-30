# Paper Architecture: MLPerf Tiny (working)
Story pattern: method_first · Audience mode B · Binding personas A,B,E · Venue: generic (all assumed)

| # | Section | Nodes | Reader question | Point | Claims | Density | Visual | New terms |
|---|---------|-------|-----------------|-------|--------|---------|--------|-----------|
| I.1 | 1 Intro | N01,N02 | What problem, why care? | TinyML systems cannot be compared fairly | C009 | CORE | - | TinyML, MCU |
| I.2 | 1 Intro | N03,N04 | What is missing? | existing benchmarks miss TinyML needs | C009 | CORE | - | - |
| I.3 | 1 Intro | N05,N06 | What is asked? | RQ1, RQ2 | C001 | CORE | - | - |
| I.4 | 1 Intro | N15 | Contribution + map | spec, divisions, framework, first round | C001,C007,C010 | CORE | - | - |
| B.1 | 2 Background | N01,N20 | why is it hard? | five obstacles | C009 | CORE | - | DUT, TFLM |
| B.2 | 2 Related | N03 | what exists? | three benchmarks, authors' account | C009 | CORE | - | - |
| D.1 | 3 Design | N08,N09 | What are the tasks? | four tasks | C001,C002,C003 | CORE | Tab 1 | - |
| D.2-5 | 3 Design | N09 | per-task detail | KWS, VWW, IC, AD | C003 | SUPPORTING | - | log-mel, AUC |
| D.6 | 3 Design | N09,N11 | How are targets set? | targets below reference | C004,C005 | CORE | Tab 2 | quantization |
| M.1 | 4 Rules | N10 | how compared? | closed/open | C007 | CORE | Tab 3 | PTQ, QAT |
| M.2 | 4 Rules | N10 | how measured? | latency/accuracy/energy | C006 | CORE | - | IPS |
| M.3 | 4 Framework | N10 | how is hardware driven? | runner, energy | C008,C017 | SUPPORTING | - | EMON |
| R.1 | 5 Round | N12,N13 | what happened? | Table 4, insights | C010,C011,C012,C013 | CORE | Tab 4 | - |
| R.2 | 5 Round | N13,N14 | what does it mean? | RQ2 answer | C014 | CORE | - | - |
| X.1 | 6 Discussion | N14 | RQ answers | RQ1/RQ2 | C014 | CORE | - | - |
| X.2 | 6 Limits | N16,N17 | boundaries | L001-L008 | C016.. | CORE | - | - |
| X.3 | 6 Impact | - | impact | C019 | SUPPORTING | - |
| K.1 | 7 Conclusion | N18,N19 | what next | C018 | CORE | - | - |
All checks ticked: every node has a slot; RQ1 has design/discussion rows, RQ2 results/interp/discussion.
