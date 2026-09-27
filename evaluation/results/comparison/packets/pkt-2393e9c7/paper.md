# SWE-bench: Evaluating Language Models on Real-World, Repository-Scale Software Engineering Issues

## Abstract

Coding assistants built on language models are increasingly asked to do more than write a short function from a description: to fix bugs and implement requests inside large, pre-existing codebases. Whether current models can do this has been hard to measure, because standard code-generation benchmarks score a self-contained function against a handful of unit tests, never requiring a model to search a large repository, understand its structure, or satisfy the project's own regression tests. We describe SWE-bench, a benchmark of 2,294 task instances built from real, merged GitHub pull requests across 12 popular Python repositories, each validated by re-running the repository's own test suite before and after the reference fix. Each task instance pairs a real issue report and repository snapshot with a reference patch and an automated, execution-based check of whether a candidate patch resolves the issue. We report evaluations of several general-purpose and fine-tuned language models under two retrieval settings that control how much of the repository the model sees. With automatically retrieved context, the best-performing model resolves about 1.96-1.97% of issues; with the exact files the reference fix touched given directly ("oracle" context), the same model resolves 4.80%. Performance falls further as the amount of retrieved context grows, and a smaller model fine-tuned specifically for this task performs poorly once its evaluation context no longer matches its training context. These results indicate that repository-scale, test-verified issue resolution is far from solved by current models, and that the gap between oracle and automatic retrieval suggests locating the relevant code, not only generating a plausible edit, is itself a major source of difficulty. All reported figures are single-run point estimates with no repeated trials, and the benchmark currently covers only Python repositories.

## 1. Introduction

Language models are increasingly deployed as coding assistants, and the natural next question is not whether they can write a short function, but whether they can do the kind of work a professional software engineer does every day: read an issue report, find the relevant part of a large, unfamiliar codebase, make a correct and minimal change, and have that change verified by the project's own tests. This distinction matters because a model that performs well on isolated function-writing tasks tells us little about whether it can operate inside the much larger, messier context of a real software project.

Most existing evaluations of code-generating language models ask the model to produce a short, self-contained function given a docstring or a small number of unit tests. This format is useful for measuring raw code-synthesis ability, but it does not require a model to search a codebase for the file and function that need to change, to reconcile an edit with existing code style, or to have that edit checked against a project's actual regression-test suite. It therefore leaves open the question motivating this paper: can a model that writes good isolated functions also resolve a real, previously unaddressed issue when the relevant code is buried inside a large repository, and how much does its success depend on how much and which surrounding code it is shown?

This paper asks: **can current language models resolve real, previously unresolved GitHub issues in large Python repositories, and how does their performance depend on how much and which surrounding code they are given as context?**

To answer this, we built SWE-bench, a benchmark of 2,294 task instances mined from real, merged pull requests across 12 popular Python repositories, each pairing an issue description and codebase snapshot with a held-out reference patch and an automated, execution-based check of success. We evaluate several general-purpose language models (Claude 2, Claude 3 Opus, ChatGPT-3.5, GPT-4/GPT-4-turbo) and SWE-Llama, a pair of open models fine-tuned for this task, under two retrieval settings: an automatic setting using a lexical search method (BM25) that selects candidate files the way an unassisted tool would, and an "oracle" setting that hands the model exactly the files the reference patch edited, isolating generation difficulty from localization difficulty.

The paper's contribution is a large, execution-verified benchmark demonstrating that repository-scale issue resolution is largely unsolved by current language models: the best general-purpose model we test resolves under 2% of issues with automatically retrieved context and under 5% even with perfect file localization, and the sizable gap between these numbers points to localization and long-context reasoning, not only patch quality, as major open problems.

Section 2 places SWE-bench relative to the evaluation it is meant to complement, in the authors' own terms (no external prior-work citations are available in the source materials; see the note at the start of Related Work). Section 3 describes how task instances were built and characterizes their difficulty. Section 4 describes the experimental setup. Section 5 reports resolve rates under automatic and oracle retrieval, the effect of context length, a memorization check, patch structure, and the fine-tuning negative result. Section 6 discusses what the results mean, Section 7 states the limitations, and Section 8 concludes.

## 2. Related Work

*A note on sourcing:* no resolvable list of cited prior works (author-year citations) could be identified in the evidence used to produce this paper. Rather than invent citations, we describe the gap this benchmark addresses in the authors' own terms; no specific prior benchmark is named or attributed here.

The category of evaluation this paper responds to asks a model to generate a short, self-contained function, typically from a docstring, and checks it against a small, hand-written set of unit tests. This format has two properties relevant to the gap SWE-bench targets. First, the function is self-contained: the model does not need to locate it within a larger codebase. Second, correctness is checked against tests written for the benchmark, not the regression-test suite of a real, actively maintained project. Both properties make the format tractable to build and evaluate at scale, but they also mean a high score on it does not establish that a model can find the right code to change inside a large, pre-existing system, or that its change would satisfy the checks a real project actually applies to it.

SWE-bench is built to close this specific gap: every task instance requires operating on a real, large codebase (Section 3), and every task instance's check is the project's own tests re-run around a candidate patch, not a bespoke test written for the benchmark. This construction is what lets Section 5's results speak to repository-scale, verifiably-correct issue resolution specifically, rather than to code synthesis in isolation.

## 3. The SWE-bench Benchmark

### 3.1 Construction

SWE-bench task instances are built through a three-stage pipeline: (I) scraping pull requests, (II) filtering candidates by simple attributes, and (III) validating candidates by execution. Source repositories were drawn from the top 5,000 most-downloaded PyPI packages as of August 2023, from which the 100 most popular were selected for pull-request scraping. Across the 12 repositories that survived to the final benchmark, the pipeline crawled 93,139 pull requests (Stage I). Stage II kept only pull requests that resolved a linked GitHub issue and included at least one new or modified test file, reducing the pool to 11,407 candidates. Stage III re-ran each repository's test suite before and after applying the candidate's reference patch, keeping only instances with a well-defined change in test outcomes; this removes about half of the Stage II candidates, with moderate variation by repository. The final benchmark contains 2,294 task instances spanning 12 repositories, from 11 instances (flask) to 850 (django), as Table 1 shows in full.

| Repository | Task instances |
|---|---|
| astropy | 95 |
| django | 850 |
| flask | 11 |
| matplotlib | 184 |
| pylint | 57 |
| pytest | 119 |
| requests | 44 |
| scikit-learn | 229 |
| seaborn | 22 |
| sphinx | 187 |
| sympy | 386 |
| xarray | 110 |
| **Total** | **2,294** |

*Table 1. Final task-instance counts by repository, after the three-stage construction and validation pipeline.*

Two companion sets were also built. SWE-bench-train contains 19,000 task instances from 37 additional, disjoint repositories; unlike the evaluation set, these are not required to include a new test, and were used to fine-tune SWE-Llama (Section 4). A 300-instance subset, SWE-bench Lite, covers 11 of the 12 evaluation repositories and emphasizes more self-contained, functional bug fixes; its full selection criteria are not resolvable from the evidence available to this paper. A 225-instance development set from 6 repositories, filtered to issues after January 1, 2019, is also described, though no model results on it are reported in the evidence used here.

Each task instance also carries a "hints" field drawn from discussion on the issue before the fix was proposed; it is retained for possible future use but was not used in the experiments reported here.

### 3.2 What counts as "resolved"

For each task instance, a candidate patch is first checked for whether it *applies* — merges into the repository snapshot without error. An applied patch is then checked for whether it is *resolved*: after applying it, the tests the reference patch was designed to fix (FAIL_TO_PASS) now pass, while tests already passing (PASS_TO_PASS) continue to pass. "Applied" is a precondition for "resolved," not a measure of correctness, and the two are reported separately in Section 5. Roughly 40% of instances require at least two FAIL_TO_PASS tests, and a median of 51 additional PASS_TO_PASS tests are checked per instance, so the resolve check is typically more demanding than satisfying a single test.

### 3.3 Task difficulty

SWE-bench task instances are larger and less self-contained than the short, docstring-sized functions typical of prior code-generation benchmarks. Issue descriptions average 195.1 words (maximum 4,477). The repositories are large: the non-test portion of a task instance's codebase averages 3,010 files (max 5,890) and 438 thousand lines (max 886 thousand). Despite this scale, reference (gold) solutions are typically small and localized: they edit 1.7 files, 3.0 functions, and 32.8 lines on average, though the maxima are far larger (31 files, 36 functions, 5,888 lines), a long tail of bigger fixes. No spread is reported alongside these means, so how typical the average edit is cannot be assessed beyond the median and maximum; the median edit touches a single function and about 15 lines. Issues are heterogeneous: of 2,289 categorized tags, 442 are "Bug," 167 "Feature," 39 "Regression," and 1,641 fall outside these categories. About 2% of instances overall contain embedded images in the issue text, concentrated in visualization libraries: 32% of matplotlib and 10% of seaborn instances.

## 4. Experimental Setup

Because SWE-bench task instances involve entire codebases, no model's context window can hold the full repository for most instances, so a *retrieval* step selects which files the model sees before it generates a patch. We evaluate two retrieval settings that bound the problem from opposite directions:

- **BM25 retrieval.** A standard lexical (keyword-overlap) search ranks and selects files from the repository automatically, up to a fixed maximum context length, without knowledge of which files the reference patch actually edited. This is the setting a fully automated tool would have to use in practice, since the correct files are not known in advance.
- **"Oracle" retrieval.** The model is instead given exactly the files the reference patch edited. This is less realistic — a real engineer does not know in advance which files need changing, and the edited files may not include all the context needed to write a correct fix — but it isolates how well a model can generate a correct edit once localization is solved for it.

For BM25, three maximum context lengths were tested (13,000, 27,000, and 50,000 tokens); recall of the oracle file set at these limits ranges from about 30% to 51% on average (up to 58% when retrieving "any" oracle file counts as success), so BM25 frequently misses at least part of the correct file set even at the largest budget tested. At the 27,000-token limit specifically, BM25 retrieves a strict superset of the oracle files for roughly 40% of instances but none of them for almost half of instances. Because models have different maximum context windows, the fraction of instances whose oracle file set fits at all varies: 58.1% for ChatGPT-3.5 (16,385 tokens), 84.1% for GPT-4 (32,768 tokens), and 96.4% for Claude 2 (100,000 tokens).

Models evaluated include Claude 2, Claude 3 Opus, ChatGPT-3.5, GPT-4/GPT-4-turbo, and SWE-Llama 7b and 13b. SWE-Llama is obtained by supervised fine-tuning of CodeLlama-Python (7b and 13b) on SWE-bench-train, using low-rank adaptation (LoRA) restricted to the attention sublayers' projection matrices, with training sequences longer than 30,000 tokens excluded, leaving an effective training set of 10,000 instances. This fine-tuning was motivated by a preliminary observation that off-the-shelf CodeLlama variants could not follow the instructions needed to produce repository-wide edits, typically emitting placeholder responses or unrelated code. GPT-4 was evaluated on only a 25% random subset (574 instances) in the oracle and BM25-27k settings, due to budget constraints, so its numbers below are not directly comparable to the full-set numbers for other models. Every model generates a single patch per instance with greedy decoding (Pass@1); no repeated sampling or seed variation is reported, so every percentage below is a single-run point estimate.

## 5. Results

### 5.1 Automatically retrieved context yields very low resolve rates

With BM25-retrieved context on the full 2,294-instance benchmark, the best-performing model tested, Claude 2, resolves about 1.96-1.97% of issues; the source reports both 1.97% (main results table) and 1.96% (prose and a separate context-length table) for the same setting, and we report both rather than silently choosing one. Every model tested resolves only a small fraction of issues under BM25 retrieval: across the six models, full-benchmark resolve rates range from 0.17% (ChatGPT-3.5) to 3.79% (Claude 3 Opus), as Table 2 details.

| Model | % Resolved (BM25) | % Applied (BM25) |
|---|---|---|
| Claude 3 Opus | 3.79 | 46.56 |
| Claude 2 | 1.97 | 43.07 |
| ChatGPT-3.5 | 0.17 | 26.33 |
| GPT-4-turbo | 1.31 | 26.90 |
| SWE-Llama 7b | 0.70 | 51.74 |
| SWE-Llama 13b | 0.70 | 53.62 |

*Table 2. Resolve and apply rates on the full SWE-bench with BM25 retrieval.*

On the smaller, 300-instance SWE-bench Lite subset, the same ordering roughly holds, with somewhat higher rates: Claude 3 Opus resolves 4.33%, Claude 2 3.00%, ChatGPT-3.5 0.33%, GPT-4-turbo 2.67%, and SWE-Llama 7b/13b 1.33%/1.00%. "Applied" rates are consistently much higher than "resolved" rates for every model — SWE-Llama models apply more than half the time but resolve well under 1% of issues — so most patches that merge cleanly still fail to make the required tests pass.

### 5.2 Oracle retrieval roughly doubles resolve rates, but performance stays low

When models are instead given exactly the files the reference patch edited ("oracle" retrieval), resolve rates rise but remain modest for every model. Claude 2 resolves 4.80% of issues under oracle retrieval, versus 1.96-1.97% under BM25, as Table 3 reports alongside the other models. The same rise from BM25 to oracle context appears for every other model: ChatGPT-3.5 to 0.52%, SWE-Llama 7b/13b to 3.01%/3.97% (versus 0.70% each under BM25), and GPT-4 (25% subset) to 1.74% — the localization benefit is not specific to Claude 2.

| Model | % Resolved (Oracle) | % Applied (Oracle) |
|---|---|---|
| Claude 2 | 4.80 | 62.82 |
| ChatGPT-3.5 | 0.52 | 21.80 |
| GPT-4\* | 1.74 | 34.00 |
| SWE-Llama 7b | 3.01 | 65.52 |
| SWE-Llama 13b | 3.97 | 66.78 |

*Table 3. Resolve and apply rates under "oracle" retrieval. \*GPT-4 evaluated on a 25% random subset (574 instances).*

The rise from BM25 to oracle retrieval across every model is consistent with an interpretation that finding the correct file(s) to edit, not only writing a plausible fix once they are found, is a meaningful part of the difficulty, given the 2- to 4-fold rise in resolve rate from BM25 to oracle retrieval. This is an interpretation, not something the data isolate directly: the oracle setting changes both what code the model sees and how much of it, so the gain cannot be attributed to localization alone without a design varying one factor at a time.

Trimming the oracle context further — showing only the regions the reference patch edited plus a small buffer, rather than the full files — increases resolve rates again: Claude 2 rises from 4.80% to 5.93%, and GPT-4 rises from 1.31% to 3.40%. This "oracle-collapsed" result reinforces the same interpretation: even after the correct files are identified, reducing the amount of surrounding, non-edited code the model must read appears to help.

### 5.3 Longer retrieved context is associated with lower resolve rates

Holding retrieval method fixed and varying only the maximum context length tested (13,000, 27,000, and 50,000 tokens) under BM25 retrieval, resolve rates fall as the length limit grows: Claude 2 falls from 1.96% (13k) to 1.87% (27k) to 1.22% (50k); SWE-Llama 7b falls from 0.70% to 0.31% to 0.00%; SWE-Llama 13b falls from 0.70% to 0.48% to 0.00%. A qualitative analysis by total input length and by issue length shows the same direction of effect for Claude 2 and other models, though the underlying figure's source values are unavailable and so are reported only qualitatively, not with specific numbers. A plausible explanation, consistent with but not directly tested here, is that as more surrounding code is added, models find it harder to localize the lines that actually need to change amid distracting context.

### 5.4 No consistent evidence that models are recalling newer repository states

Because SWE-bench issues have creation dates, and a model's training data has a cutoff date, one might worry that apparent success partly reflects having seen a newer, already-fixed version of the repository during training rather than reasoning about the issue. Splitting issues by creation date under oracle retrieval, most models show little difference before versus after 2023, with GPT-4 an exception (1.96% before 2023 versus 0.00% after, on its 25% subset). For example, Claude 2 resolves 4.87% of pre-2023 issues and 4.23% of post-2023 issues, and SWE-Llama 13b resolves 3.98% and 3.85% — small differences relative to the overall resolve rates. An extended six-partition analysis likewise shows no consistent correlation between issue-resolution year and performance. This absence of a temporal trend is consistent with models not resolving issues merely by reproducing a memorized, more recent version of the repository, though it is an indirect check, not a direct test for memorization.

### 5.5 Model-generated patches are shorter and simpler than reference patches

Among successfully applied patches under oracle retrieval, model-generated edits are consistently smaller than the reference patches: averaged across all models' respective gold patches, reference edits total 74.5 lines (22.3 added, 10.5 removed) across 3.0 functions and 1.7 files, while, for example, ChatGPT-3.5's generated patches that successfully applied total 30.1 lines across 1.6 functions and 1.0 files. The paper's own prose compares these two numbers directly (74.5 versus 30.1 lines) to argue models "tend to generate shorter, simpler edits"; this mixes an aggregate figure (all models' gold patches) with one model's generated-patch figure rather than comparing each model to its own gold patches, so the "less than half" framing is illustrative rather than a precise like-for-like statistic. The qualitative pattern — models rarely edit more than a single file, while many gold fixes touch more — held consistently across the models examined.

### 5.6 Fine-tuning for the task does not transfer across retrieval settings

SWE-Llama 7b and 13b, fine-tuned on oracle-context training data, resolve a respectable 3.01% and 3.97% of issues under matching oracle retrieval (Section 5.2) — competitive with, and in the 13b case exceeding, several general-purpose models. Under BM25 retrieval, however, both perform surprisingly poorly, resolving only 0.70% each, a clear drop from their oracle-setting performance and lower than most general-purpose models under BM25. The authors attribute this to distribution shift: SWE-Llama was fine-tuned exclusively on clean, exactly-relevant oracle context, and evaluating it on the noisier, sometimes off-target files BM25 retrieves puts it in a context distribution it never saw in training, which they suspect makes reliable performance difficult. This is a stated suspicion, not something isolated by a dedicated ablation, but it directly qualifies how much fine-tuning, by itself, narrows the gap to general-purpose models: it does so only within the retrieval setting matching how the fine-tuning data was built, not across settings.

Resolve rates also vary by repository. Under oracle retrieval, models resolve the largest share of issues in requests (e.g., Claude 2 at 15.91%, SWE-Llama 7b at 18.18%) and none in seaborn for every model. Seaborn contributes only 22 of the 2,294 instances, so this 0% reflects a small sample and repository-specific difficulty rather than evidence that seaborn-style issues are categorically unsolvable. Claude 2 and SWE-Llama 13b, the two strongest oracle-setting models, resolve 110 and 91 instances respectively, but Claude 2 solves only 42% of the instances SWE-Llama 13b solves, indicating "resolve rate" as a single number obscures real differences in which issues each model handles.

## 6. Discussion

**Does automatic retrieval let current models resolve real issues?** Largely no: the best model tested resolves under 2% of the full benchmark with automatically retrieved context (Section 5.1), and every model tested falls below 4%. This is the headline answer to the paper's research question under the realistic, fully automated setting.

**Is the difficulty mainly about generating a correct edit, or about finding the right code?** Both appear to matter, but the data point toward localization and context length as at least as important as generation quality. Moving from BM25 to oracle retrieval — giving the model the exact files to edit, changing nothing about its generation ability — roughly doubles Claude 2's resolve rate (1.96-1.97% to 4.80%), and trimming oracle context to just the edited regions raises it further still. Resolve rates also fall as the retrieved context grows longer at fixed retrieval quality. Together, these are consistent with an account in which models' patch-generation ability, once the right code is in front of them and not buried in surrounding text, is meaningfully better than their end-to-end resolve rate suggests. We state this as an interpretation, not a demonstrated mechanism: the oracle-versus-BM25 comparison changes more than one factor at once, and no ablation in the available evidence isolates localization from context volume directly.

**Could high performance simply reflect memorized, more recent repository states?** The available check — comparing resolve rates on issues created before and after 2023 — shows no consistent difference for most models, which does not support a memorization-based explanation, though it is an indirect check rather than a direct one.

**Does adapting a model specifically to this task close the gap to general-purpose models?** Only partially, and only within a matching context setting. SWE-Llama's oracle-setting performance is respectable relative to general-purpose models, but the same fine-tuned models perform poorly once the evaluation context no longer matches their training context (Section 5.6). This suggests closing the resolve-rate gap will require methods robust to the kind of context a real, automatic pipeline actually produces, not only methods tuned to one idealized retrieval setting.

**What does this mean going forward?** Because oracle-setting resolve rates remain low (under 5% for every model), and trimming irrelevant context helps even after the right files are found, work on automated code-context retrieval and on reasoning reliably over long code context looks likely to matter as much as raw patch-generation quality for practical, repository-scale coding assistance. SWE-bench's execution-based check also ties any future gains reported on it to a concrete, verifiable notion of "fixed the issue," not to similarity with a reference answer.

## 7. Limitations

- **No repeated trials or reported variance.** Every resolve/apply percentage is a single-run point estimate (greedy decoding, Pass@1), with no repeated sampling or seed variance. Small differences — including the 1.96% vs. 1.97% discrepancy in the source material's own reporting of Claude 2's headline BM25 result — cannot be distinguished from run-to-run noise, and no comparison in this paper is backed by a statistical test.
- **Python only.** All task instances are written in Python; results describe Python software-engineering tasks specifically and do not show how models would perform on other languages.
- **Oracle retrieval is an idealized probe, not a deployment setting.** It supplies exactly the files the reference patch edited, unavailable in real deployment; oracle numbers are an upper-bound-style probe of generation ability given solved localization, not an estimate of realistic end-to-end performance.
- **GPT-4 evaluated on a subset.** GPT-4 was evaluated on only a 25% random subset (574 instances) in the oracle and BM25-27k settings, so its percentages are not directly comparable to the full-set percentages reported for other models.
- **Execution-based checking is necessary but not sufficient.** Passing an instance's designated tests is an automated proxy for a correct fix; the authors note this alone is insufficient to guarantee reliable performance, since generated code can be less comprehensive, efficient, or readable even when it passes.
- **Experiments set a baseline, not an optimized system.** The methods evaluated (BM25 retrieval; single greedy-decoded generation) are described as the simplest, most straightforward approaches, intended to set a baseline rather than the best achievable performance with more sophisticated retrieval or agentic methods.

## 8. Conclusion

This paper introduced SWE-bench, a benchmark of 2,294 task instances built from real GitHub issues and their linked, merged pull requests across 12 popular Python repositories, each checked by an automated, execution-based test of whether a candidate patch actually resolves the issue. Evaluating a range of general-purpose and fine-tuned language models on it shows that current models resolve only a small fraction of real repository issues: under 2% with automatically retrieved context, and under 5% even when given the exact files to edit. The consistent gains from better localization and the consistent losses from longer retrieved context together point to context selection and long-context reasoning as major open problems for repository-scale coding assistance, alongside raw patch-generation quality. A fine-tuned model can approach general-purpose performance within a matching retrieval setting but does not transfer that performance across settings, underscoring that context robustness, not only task-specific training, remains unsolved. Because SWE-bench instances are timestamped, the collection procedure is designed to allow adding issues created after a given model's training cutoff, intended as a way to keep evaluating models on genuinely unseen tasks over time, though this property is only indirectly supported by the temporal analysis here rather than demonstrated directly. Taken together, repository-scale, test-verified issue resolution remains an open and difficult problem, and SWE-bench offers a concrete, extensible, automatically checkable way to measure future progress on it.

---
