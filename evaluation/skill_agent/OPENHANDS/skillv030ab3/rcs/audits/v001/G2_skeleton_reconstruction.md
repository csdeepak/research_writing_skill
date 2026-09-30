# G2: skeleton self-reconstruction (answered from plan/skeleton.md only)

Q1 Problem: building and evaluating agents that act through software (I.1).
Q2 Why it matters: the authors see software as the ideal interface for agents to act on the world (I.1).
Q3 Missing: in the authors' description, frameworks are general with limited or stateless code execution, or specific to software engineering (I.2, R.1-R.3).
Q4 What was done: a platform with event stream, sandboxed runtime, skills, delegation and a benchmark harness, plus an evaluation on 15 benchmarks (I.4, I.5, M.*, S.*).
Q5 Why this method: three programming-language primitives covering most tasks of engineers and analysts; skills only where the model cannot write the code itself; delegation for web tasks (M.3, M.4, M.5).
Q6 Experiments: 7 software, 2 web, 6 assistance benchmarks under a reproducible-reference protocol (S.1-S.3).
Q7 Strongest results: SWE-bench Lite 26.0%, HumanEvalFix 79.3%, GPQA diamond 52.0%, GAIA 32.1% (Rs.1-Rs.3).
Q8 What they establish: scores are competitive, not consistently leading (D.1).
Q9 What they do not establish: no variance, unmatched references, no component ablation, no safety evaluation (Lim.2, M.7).
Q10 Primary contribution: the open platform with an evaluation across categories (I.5).
Q11 Main limitations: agents struggle with complex tasks; not top in every category (Lim.1).
Q12 One-day memory: an open platform for software-acting agents whose default agents are competitive but often below listed references.

All 12 answerable. Skeleton reads as the argument in miniature. G2 pass (no executable tool; this file is the record).
