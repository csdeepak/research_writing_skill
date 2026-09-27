# Skeleton (one sentence per paragraph slot, step 9)

**Title.** SWE-bench: a benchmark for evaluating language models on real-world GitHub issue resolution, and evidence that context selection, not only coding ability, limits current performance.

**Abstract.** SWE-bench tests whether LLMs can resolve real GitHub issues against full repositories with executable verification; across several models resolution rates are low (0.17-3.79%), and for the most-studied model (Claude 2) giving ground-truth context nearly triples resolution rate, indicating context selection is a major bottleneck {C001}{C002}{C004}.

**I.1** Whether LLMs can act as software engineers on realistic, repository-scale tasks -- not just isolated functions -- remains untested by standard coding benchmarks {N01}{N02}.
**I.2** Existing benchmark practice, as characterized in the evidence available for this project, tests short self-contained problems rather than real issues against real, large repositories with executable verification {C001}.
**I.3** This paper asks: given a real GitHub issue and its full repository, can current LLMs generate a patch that resolves it, and what determines success or failure? {N05}
**I.4** We built SWE-bench, 2,294 validated task instances from real GitHub history across 12 Python repositories, and evaluated several LLMs (with retrieval) plus a fine-tuned open model, SWE-Llama {C001}{C009}{C012}.
**I.5** Every evaluated model resolves only a small fraction of issues, and giving Claude 2 the ground-truth edited files nearly triples its resolution rate, pointing to context selection as a major, addressable bottleneck {C002}{C004}.
**I.6** Paper map: Related Work, Methods (benchmark construction and evaluation setup), Results (headline rates, oracle-vs-BM25, context-length effects, patch characteristics, SWE-Llama, Lite, model overlap), Discussion, Limitations, Conclusion.

**RW.1** Relative to the short, self-contained coding-benchmark practice this evidence package characterizes, and consistent with reported long-context degradation in LLMs generally (Liu et al., 2023b), SWE-bench's gap is that no prior evaluation in this material grounds tasks in real repositories with executable, test-based verification {C001}.

**M.1** A SWE-bench task instance pairs a real GitHub issue with a codebase snapshot, a gold patch, and FAIL_TO_PASS/PASS_TO_PASS tests that verify a fix without rewarding regressions.
**M.2** Instances were built by a three-stage pipeline that reduced ~90,000 candidate pull requests to 11,407 attribute-filtered candidates to 2,294 execution-validated instances {C009}.
**M.3** The resulting benchmark spans large codebases and modest gold fixes: issues average 195.1 words, codebases average 3,010 files/438,000 lines, and gold patches average 1.7 files/3.0 functions/32.8 lines {C001}{C008}; a 300-instance self-contained subset, SWE-bench Lite, is also defined.
**M.4** [table TAB-1, TAB-2]
**M.5** Evaluation covers ChatGPT-3.5, GPT-4/GPT-4-turbo, Claude 2, Claude 3 Opus, and SWE-Llama 7b/13b, each given repository context via BM25 retrieval (realistic), oracle retrieval (ground-truth files), or oracle-collapsed retrieval (ground-truth region only), scored by resolution rate {C014}. [table TAB-3]
**M.6** SWE-Llama was fine-tuned with LoRA on 10,000 issue-PR pairs from 37 repositories disjoint from the 12 evaluation repositories {C012}.

**R.1** Under BM25 retrieval on the full benchmark, resolution rates are low across the board, from 3.79% (Claude 3 Opus, the highest reported figure) down to 0.17% (ChatGPT-3.5) {C002}{C015}. [table TAB-4]
**R.2** Giving Claude 2 the ground-truth edited files directly (oracle retrieval) more than doubles its resolution rate, from 1.96% to 4.80%, consistent with context selection -- not only coding ability -- limiting BM25 performance {C004}.
**R.3** Performance is sensitive to how much and how precisely relevant context is shown: Claude 2's rate falls as BM25 context grows (1.96%->1.87%->1.22% at 13k/27k/50k tokens) even as raw BM25 recall of oracle files rises (29.58%->44.41%->51.06%), and trimming oracle context to the edited region raises resolution further, to 5.93% {C003}{C010}{C013}{C018}. [table TAB-5]
**R.4** Applied patches are consistently shorter and narrower than gold patches (19.6 vs. 74.5 total lines for Claude 2; models rarely edit more than one file) {C006}{C008}.
**R.5** SWE-Llama, fine-tuned on oracle-retrieval context, transfers poorly to BM25-retrieved context at evaluation time (0.70%), consistent with sensitivity to the shift between training and evaluation context distributions {C005}.
**R.6** On the smaller, self-contained SWE-bench Lite subset resolution rates are higher for both models with direct evidence (Claude 2: 3.00% vs. 1.96-1.97%; Claude 3 Opus: 4.33% vs. 3.79%), and under oracle retrieval Claude 2 and SWE-Llama 13b resolve comparable overall numbers of instances but overlap on only 42% of the specific instances SWE-Llama 13b solves {C007}{C019}.

**D.1** Together, the oracle-vs-BM25 gap, the context-length sweep, the oracle-collapsed improvement, and the qualitative localization failures are consistent with current models' bottleneck being substantially about finding and using the right context, not only about generating correct code {C004}{C013}{C017}{C018}.
**D.2** This suggests that improving real-world coding-agent performance may depend as much on better retrieval and long-context robustness as on raw generation capability {C017}.

**L.1** SWE-bench instances are Python-only; each model produced a single generation per instance with no reported run-to-run variance; "resolved" measures test-passing, not independently assessed code quality; and the source material itself contains two unresolved discrepancies (a 1.96%/1.97% rounding conflict, and a conflict between prose calling Claude 2 best-performing and a higher Claude 3 Opus table figure), both disclosed rather than silently resolved {L001}{L003}{L004}{L005}{L006}.

**C.1** SWE-bench establishes a realistic, executable, currently far-from-saturated benchmark; today's evaluated models leave most of it unsolved, and a substantial share of that gap traces to context selection rather than coding ability alone, pointing to concrete directions -- better retrieval, longer-context robustness, and broader-language coverage -- for future work {C001}{C002}{C004}.

## Gate G2 self-check (Q1-Q12, evaluation_rubric.md §1)
Read top-to-bottom, the skeleton alone answers: what the problem is (I.1-I.2), why it matters (I.1), what's missing (I.2/RW.1), the question (I.3), the approach (I.4/M.1-M.6), the headline finding with magnitude (I.5/R.1-R.2), robustness/consistency (R.3-R.6), what it means (D.1-D.2), the main limit (L.1), and the takeaway (C.1). All 12 reconstruction questions are answerable from this skeleton; passes without returning to step 8.
