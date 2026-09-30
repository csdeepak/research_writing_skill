# Step 17: scientific overclaim audit

- Watch-list grep over the draft (prove, significant, state-of-the-art, novel, first, robust, generalize, outperform, always, never, substantial, dramatic, clearly, causes/leads to/results in/drives, demonstrates/establishes/confirms/shows that): only the ordinal "first"/"First" and the benchmark name ProofWriter remain. Lint UNLICENSED-*: 0. The authors' own word "significantly" (HumanEvalFix, GAIA) was not reproduced because no test is reported.
- "Competitive" is always attributed to the authors and paired with rows below references (Section 5.4, abstract).
- No causal claim about which platform component produces the scores; L012 states the missing ablation.
- Generalization scope: claims limited to the listed benchmarks, subsets, agent versions and base-model snapshots; the same-agent-across-categories reading is qualified (L015).
- Safety: the authors' risk-mitigation statements are reported as expectations, with the note that no safety evaluation exists (C027, L005).
- Community numbers and README descriptions are labelled self-reported or later documentation, not results.
- No evidence was strengthened and no support was searched for after the fact.
