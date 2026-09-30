# G2: skeleton self-reconstruction (AUTHOR, no executable check exists for G2)

Answered from plan/skeleton.md alone. All twelve questions are answerable; this is a self-assessment and is not a tool-verified gate.

- Q1 Problem: which agent to ask in a shared-memory team of LLM agents, given that global search costs tokens (I.1).
- Q2 Why it matters: global search considers a mean candidate set of 32.0 and the cost is paid on every query (I.1).
- Q3 What is missing: a measurement of the saving, the accuracy cost and the behaviour under topic change (I.2).
- Q4 What was done: four routing arms on a constructed corpus with 10 seeds, then a new-topic run and a static QA comparison (M.1 to M.7).
- Q5 Why this method: the statistics follow the authors' stated reasons (M.5); the authors' reason for foregrounding cost over accuracy is withheld (I.1).
- Q6 Experiments: cost and ablation, new-topic adaptation, static question answering (M.3, M.6, M.7).
- Q7 Strongest results: 22.1% fewer tokens per query; regret 3.24 and 0.92 with 0 retrains (S.1, S.7).
- Q8 What they establish: a saving on a constructed corpus, consistent with ownership evolution at low confidence (S.3, S.6).
- Q9 What they do not establish: equal accuracy, organic workloads, other answering models, any QA advantage (S.4, S.5, S.9, D.3).
- Q10 Primary contribution: the audited token-saving estimate reported with the accuracy cost (I.3).
- Q11 Main limitations: constructed corpus, lower accuracy, single ablation without a test, absent files (L.1 to L.3).
- Q12 Remember one day later: routing on learned ownership saves about a fifth of tokens on a constructed corpus, at a small accuracy cost (C.1).

Gate G2 is recorded as pending (no executable check); this file is its audit.
