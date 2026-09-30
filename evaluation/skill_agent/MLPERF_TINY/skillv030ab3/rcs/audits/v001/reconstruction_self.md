# Step 11 - reconstruction self-test (from the tag-free text of drafts/v001/paper.md)

Q1 Problem: fair, reproducible comparison of ML inference on ultra-low-power devices (Abstract, 1). Matches spine 1.
Q2 Why it matters: always-on private low-energy inference; the authors say progress is limited without a benchmark (1). Matches.
Q3 Missing: CoreMark, MLMark, MLPerf inference fall short, in the authors' account (1, 3). Matches; worded as the authors' characterization.
Q4 What was done: four benchmarks with reference implementations, quality targets, closed/open divisions, measurement framework (1, 4). Matches.
Q5 Why: the authors' reasons are given per design choice (1, 4.1-4.4). Matches.
Q6 Experiments: reference models against targets (5.1), reference implementations on the board (5.2), June 2021 round (5.3). Matches.
Q7 Strongest results: every reference above its target; five varied submissions (5.1, 5.3). Matches.
Q8 Establishes: the specification and reference numbers; the authors' reading of the round (6). Matches.
Q9 Does not establish: fairness across submissions, sensitivity of targets, reference latency/energy magnitudes (5, 6, 7). Matches.
Q10 Contribution: the suite, targets, rules, framework (1). Matches.
Q11 Limits: streaming, pre-processing, stability, model coverage; plus the additional caveats (7). Matches spine 7.
Q12 One-day memory: an open four-task benchmark with a modular two-division design, read by its authors as fitting diverse submitters, within stated limits. Matches spine 5-7.

First-read subset (title, abstract, introduction): Q1-Q4, Q10, Q12 answerable. Mismatches found: none. Term check with tools/audit_reader.py: only product and dataset names remain flagged (reviewed, kept verbatim; see term_audit.md).
Skim layer: the abstract keeps every number and scope of its tagged claims (91.6%, 90%, more than 50, five, June 2021); its hedges ("the authors say", "read as") are kept.
