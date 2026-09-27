# SWE-bench: A Benchmark for Real-World GitHub Issue Resolution, and Evidence That Context Selection Limits Today's Language Models

## Abstract

Large language models (LLMs) are routinely scored on short, self-contained coding problems, but it is untested whether they can perform the kind of software engineering (SWE) that real developers do: read a real bug report, navigate a large, unfamiliar codebase, and produce a change that actually fixes the problem without breaking anything else. We describe SWE-bench, a benchmark built directly from real-world GitHub history that tests exactly this. Each of its 2,294 task instances pairs a real issue report with a snapshot of the repository it was filed against, a reference ("gold") patch, and an executable test suite that verifies whether a candidate fix resolves the issue without introducing regressions {C001}. Evaluating several current LLMs, given retrieved repository context, we find resolution rates are low across the board: from 3.79% for the highest-scoring model down to 0.17% for the lowest {C002}{C015}. For the model studied in the most depth, Claude 2, resolution rate nearly triples, from 1.96% to 4.80%, when it is given the exact files a human editor changed instead of files chosen by a retriever {C004}, and performance falls further as the amount of retrieved context grows even though retrieval recall itself improves {C003}{C010}. These patterns are consistent with the conclusion that current models' central limitation on this benchmark is not only generating correct code, but finding and using the right context within a large, realistic codebase {C017}. We report these findings, together with a fine-tuned open model's difficulty transferring between context distributions {C005}, characteristics of the patches models do produce {C006}{C008}, and a set of limitations, scoped to what this evidence package documents (SWE-bench instances are Python-only, and resolution rate measures test-passing rather than independently assessed code quality {L004}{L005}).

## 1. Introduction

Coding benchmarks for language models typically ask a model to write a short, self-contained function from a natural-language description, and check the output against a handful of unit tests. This format is convenient to score, but it leaves open a different and more practically important question: can a model act as a software engineer on a real, evolving codebase, where the task is not "write function f" but "understand this bug report, find the relevant part of a large system, and change it correctly without breaking anything else"? {N01}{N02} The materials available for this project characterize prior evaluation practice as testing short, self-contained problems rather than the kind of large-scale, real-world engineering task that determines whether a model is actually useful to a developer {C001}.

This gap matters because the two settings can dissociate. A model that reliably solves isolated function-writing problems has not thereby been shown to locate the right file among thousands, reason about how a change interacts with the rest of a large system, or satisfy a pre-existing regression test suite it never wrote. Nothing in the isolated-function setting forces a model to demonstrate any of that. Closing this evaluation gap requires three things that isolated-function benchmarks do not provide: real, large codebases; tasks drawn from actual developer activity rather than synthesized from a description; and an executable, objective standard for "resolved" that does not depend on a human judge.

This paper asks: **given a real GitHub issue and full access to the repository it concerns, can current language models generate a patch that resolves the issue — and what determines whether they succeed or fail?** {N05}

To answer it, we constructed SWE-bench, a benchmark of 2,294 validated task instances built from real GitHub issues and pull requests across 12 popular, large, mostly-Python open-source repositories {C001}{C009}. Each instance is paired with an executable test-based verification procedure (defined in §3) so that "resolved" has an objective, reproducible meaning. We then evaluated several widely used LLMs — accessing the repository through automated retrieval, since a real user cannot hand a model the exact files it needs to edit — and a smaller open model, SWE-Llama, that we fine-tuned specifically for this task {C012}.

**Contribution.** We contribute (1) SWE-bench, a validated, executable benchmark of 2,294 real-world issue-resolution tasks, and (2) an evaluation showing that every tested model resolves only a small fraction of these real issues — from 3.79% down to 0.17% under a realistic retrieval setting {C002}{C015} — together with evidence that context selection, not solely coding ability, accounts for a sizable part of that gap {C004}. This alone might be read as evidence that current LLMs simply cannot yet do this kind of software engineering. But a second set of results complicates that reading: when Claude 2, the model we study in the most depth, is given the exact files a human developer changed rather than files selected by a retriever, its resolution rate nearly triples, from 1.96% to 4.80% {C004}. Resolution rate also falls as the amount of retrieved context grows, even as the raw fraction of relevant files retrieved goes up {C003}{C010}{C013}. Together, these results are consistent with much of current models' apparent weakness on this benchmark (a roughly 2.4x resolution-rate gap between retrieved and ground-truth context, detailed in §4) being attributable to difficulty finding and using the right context inside a large codebase, not solely to an inability to write the correct fix once the right context is in view {C017}.

The rest of the paper is organized by these questions. §2 situates the gap this benchmark targets relative to prior evaluation practice and a related finding about long-context language model use. §3 describes how SWE-bench was built and how models were evaluated. §4 presents the headline resolution rates, the oracle-versus-retrieved comparison, the context-length and retrieval-precision results, patch characteristics, the fine-tuned model's context-transfer difficulty, and two supplementary comparisons (a smaller self-contained subset, and how much two models' successes overlap). §5 discusses what these results are consistent with, and what they are not. §6 states the benchmark's and the evaluation's limitations explicitly. §7 concludes.

## 2. Related Work

The gap this paper targets is best understood relative to two things documented in the materials available for this project. First, the evidence characterizes standard coding-benchmark practice as testing short, self-contained problems — a setting quite different in scale from SWE-bench's codebases, which average 3,010 non-test files and 438,000 non-test lines of code per instance {C001}. Nothing in a short-problem evaluation requires a model to locate relevant code within a repository of that scale, so such evaluations cannot by themselves speak to whether a model can do so. SWE-bench is designed to close specifically this part of the gap: it keeps the executable, objective pass/fail verification that makes short-problem benchmarks easy to score, while replacing the synthetic, self-contained problem with a real issue set against its real, large repository.

Second, one external finding is directly relevant to interpreting the context-length results in §4: (Liu et al., 2023b) is cited in the source material as corroborating evidence that language models have difficulty making full use of information placed within long input contexts. We rely on this only as corroboration for an interpretive point in §5, not as the basis for the benchmark's design; we did not conduct a systematic literature search for this project (see Limitations), so we make no claim that SWE-bench is the first or only benchmark of its kind, only that the evidence available to us does not document a prior benchmark combining real-issue provenance, full-repository scale, and executable verification in the way SWE-bench does.

## 3. Methods

### 3.1 Task instance definition

A SWE-bench **task instance** pairs a real GitHub issue with a snapshot of the codebase it was filed against, a **gold patch** (the code change from the pull request that actually resolved the issue, drawn from the real merge history), and an executable test suite split into two roles: **FAIL_TO_PASS tests**, which must fail before a fix and pass after a correct one, and **PASS_TO_PASS tests**, which must continue to pass throughout, so that a candidate fix is not credited unless it resolves the issue without introducing a regression. This construction gives "resolved" an objective, automatically checkable meaning: a candidate patch is scored as resolving an instance only if it applies cleanly and the specified tests behave as required.

### 3.2 Benchmark construction

SWE-bench instances were built by a three-stage filtering pipeline applied to roughly 90,000 pull requests collected across 12 popular Python repositories {C009}. Stage I scraped pull requests linked to an issue. Stage II kept only merged pull requests that both resolve an issue and add or modify at least one test, reducing the pool to 11,407 candidates {C009}. Stage III executed each candidate's test suite before and after the patch and kept only instances where the fail-to-pass and pass-to-pass tests behave as specified, yielding the final validated set of 2,294 instances {C009}. Table 1 summarizes the counts surviving each stage.

| Pipeline stage | Instance count |
|---|---|
| Initial pull requests scraped | ~90,000 |
| After attribute-based filtering (Stage II) | 11,407 |
| After execution-based validation (Stage III, final) | 2,294 |

*Table 1. Construction pipeline: instance counts before and after each filtering stage {C009}.*

The resulting benchmark spans real engineering scale, summarized in Table 2. Issue descriptions average 195.1 words (maximum 4,477); codebases average 3,010 non-test files (maximum 5,890) and 438,000 non-test lines of code (maximum 886,000); gold patches average 1.7 files, 3.0 functions, and 32.8 lines changed; and instances carry an average of 9.1 fail-to-pass tests and 120.8 total tests, with a median of 51 additional pass-to-pass tests beyond the fail-to-pass set {C001}{C008}.

| Statistic | Mean | Max / Median |
|---|---|---|
| Issue text length (words) | 195.1 | 4,477 (max) |
| Non-test files in codebase | 3,010 | 5,890 (max) |
| Non-test lines of code | 438,000 | 886,000 (max) |
| Files edited (gold patch) | 1.7 | — |
| Functions edited (gold patch) | 3.0 | — |
| Lines edited (gold patch) | 32.8 | — |
| Fail-to-pass tests | 9.1 | — |
| Total tests | 120.8 | 51 (median pass-to-pass) |

*Table 2. Descriptive statistics for SWE-bench task instances {C001}{C008}.*

Among the 2,289 instances with an assigned issue-category tag, 442 are categorized as bug fixes and 167 as feature requests, indicating the benchmark spans a range of engineering task types rather than bug-fixing alone; the remaining categories are not broken out with a directly traceable count in the evidence available for this paper {C011}. A held-out development set of 225 instances from 6 repositories, with an average of 19.9 fail-to-pass tests per instance (median 2) and 171.3 pass-to-pass tests on average, was used for hyperparameter tuning ahead of the reported evaluation, and a 300-instance subset emphasizing self-contained, functional bug fixes, SWE-bench Lite, is defined for lower-cost evaluation {C007}{C016}. A minority of instances embed images in the issue text (32% for the matplotlib repository, 10% for seaborn, 2% overall); such instances may implicitly require multi-modal handling, though this is not directly tested by the reported evaluation {C020}.

### 3.3 Experimental setup

We evaluated OpenAI's Generative Pre-trained Transformer (GPT) family — ChatGPT-3.5, GPT-4, and GPT-4-turbo — alongside Claude 2, Claude 3 Opus, and two sizes of SWE-Llama (7b and 13b, described below) on SWE-bench. Because a real user cannot supply a model with the exact files it needs to change, our primary setting retrieves candidate files automatically using a classical lexical, term-frequency-based retrieval method (BM25), and gives the model a resolution-rate score based only on retrieved context. To separate a model's ability to use context from its ability to find context, we additionally evaluated an **oracle retrieval** setting, in which the model is given exactly the files the gold patch edits, and an **oracle-collapsed** setting, in which code outside a narrow window (±15 lines) around each edited region is omitted from those oracle files. Resolution rate is the fraction of instances for which a model's generated patch applies and satisfies both the FAIL_TO_PASS and PASS_TO_PASS tests.

Because models differ sharply in context-window size, not every model can be shown the same amount of retrieved context: at their respective maximum context lengths, only 58.1% of instances fit within ChatGPT-3.5's 16,385-token window and 84.1% fit within GPT-4's 32,768-token window, compared with 96.4% for Claude 2's 100,000-token window {C014}, as Table 3 shows.

| Model | Max. context (tokens) | % of instances covered |
|---|---|---|
| ChatGPT-3.5 | 16,385 | 58.1% |
| GPT-4 | 32,768 | 84.1% |
| Claude 2 | 100,000 | 96.4% |

*Table 3. Model context windows and the fraction of SWE-bench instances they can cover under the oracle-retrieval token count {C014}.*

SWE-Llama is a fine-tuned open model produced for this evaluation. Training data was collected in the same way as the benchmark itself but from a disjoint set of 37 repositories, yielding 19,000 issue-and-pull-request (PR) pairs, of which sequences longer than 30,000 tokens were excluded, leaving an effective training set of 10,000 instances; the model was fine-tuned with LoRA (Low-Rank Adaptation), a parameter-efficient method that updates a small additional set of weights rather than the full model {C012}. GPT-4-turbo's reported figures reflect a random 25% subset of the benchmark rather than the full set, disclosed here because of evaluation budget constraints {L003}.

## 4. Results

### 4.1 Resolution rates under realistic retrieval

Under BM25 retrieval on the full benchmark, every evaluated model resolves a small minority of instances, as Table 4 shows. Claude 3 Opus is the highest-scoring model reported, at 3.79%; Claude 2 follows at 1.96% (this figure appears as 1.97% in one results table in the underlying source material, a discrepancy of 0.01 percentage points that we disclose rather than silently resolve, per {L001}); GPT-4-turbo resolves 1.31% (on the 25% subset noted above); and ChatGPT-3.5 and both sizes of SWE-Llama resolve 0.70% or below {C002}{C015}.

| Model | Resolution rate (BM25, full benchmark) |
|---|---|
| Claude 3 Opus | 3.79% |
| Claude 2 | 1.96% (1.97% in one source table; see text) |
| GPT-4-turbo | 1.31% (25% subset) |
| SWE-Llama 7b | 0.70% |
| SWE-Llama 13b | 0.70% |
| ChatGPT-3.5 | 0.17% |

*Table 4. Resolution rate by model, BM25 retrieval, full SWE-bench {C002}{C015}.*

We note explicitly {L006} that the underlying source material's own prose describes Claude 2 as "the best-performing model" at 1.96%, while its results table separately reports Claude 3 Opus at the higher figure of 3.79% under what appears to be the same condition. We were not able to determine from the evidence available whether this reflects a revision in which Claude 3 Opus results were added after the surrounding text was written, and we do not resolve the conflict by omission; both figures are reported here as they appear in the source material.

### 4.2 Is the bottleneck coding ability or context selection?

The low resolution rates in §4.1 are consistent with at least two different explanations: models may lack the coding ability to produce a correct fix even when shown the relevant code, or they may lack the ability to find the relevant code among everything retrieved. To distinguish these, we compare Claude 2's BM25 resolution rate against its performance when given the ground-truth edited files directly (oracle retrieval). Resolution rate more than doubles, from 1.96% to 4.80% {C004}. Because this comparison holds the model fixed and changes only which files it is shown, the result is consistent with context selection — not solely coding ability — accounting for a sizable part (roughly 2.4x) of the gap between what these models can do and how they score under realistic retrieval {C004}.

### 4.3 Context length and retrieval precision

If context selection matters, then the amount and precision of context shown to a model should affect performance independently of whether the "correct" files are technically retrievable. We find both effects. First, Claude 2's resolution rate under BM25 retrieval falls as the context-length budget grows: 1.96% at a 13,000-token limit, 1.87% at 27,000 tokens, and 1.22% at 50,000 tokens {C003}. This happens even though BM25's raw recall of the oracle files *improves* with a larger budget — from 29.58% average recall at 13k tokens to 44.41% at 27k and 51.06% at 50k {C010} — which rules out "the retriever simply finds less at longer limits" as the explanation for the falling resolution rate.

Second, at the 27,000-token limit, BM25's retrieved set is frequently either too broad or entirely wrong relative to the oracle files: in about 40% of instances it retrieves a superset that includes the oracle files but adds others, and in about half of instances it retrieves none of the oracle files at all {C013}. A retriever can therefore show reasonable aggregate recall while still failing, instance by instance, to hand the model what it actually needs.

Third, when oracle context is trimmed even further — collapsing everything outside a narrow window around each edited region, rather than showing the full oracle files — Claude 2's resolution rate rises again, to 5.93%, above the 4.80% obtained with the full oracle files {C018}. More context, even context that includes the correct files, is not simply neutral or additive; showing less but more precisely targeted context measurably helps. Table 5 lays out these context-length and retrieval-precision conditions together.

| Condition | Claude 2 resolution rate | BM25 recall of oracle files |
|---|---|---|
| BM25, 13k-token limit | 1.96% | 29.58% |
| BM25, 27k-token limit | 1.87% | 44.41% |
| BM25, 50k-token limit | 1.22% | 51.06% |
| Oracle retrieval (full files) | 4.80% | — |
| Oracle retrieval, collapsed to edited region | 5.93% | — |

*Table 5. Effect of context length and precision on Claude 2's resolution rate and on BM25's recall of the oracle files {C003}{C010}{C018}.*

### 4.4 What successful patches look like

Among patches that apply successfully, model-generated fixes are consistently narrower than the reference solutions. For Claude 2 under oracle retrieval, applied patches average 19.6 total changed lines (4.2 added, 1.9 removed), compared with an average of 74.5 total lines (10.5 added) across all gold patches — less than a third the length {C006}{C008}. Models also rarely edit more than a single file, in contrast to the average gold patch, which touches 1.7 files {C006}{C008}. A small qualitative review of 11 generations further noted a tendency toward simple, direct code that underuses existing library or codebase idioms, and a "greedy" style oriented at satisfying the immediate fix rather than matching the surrounding codebase's broader style or constraints; given the very small, non-random sample, we report this as a suggestive qualitative observation rather than a general finding {C021}.

### 4.5 A fine-tuned open model, and its own context-transfer problem

SWE-Llama was fine-tuned on oracle-retrieval-style context, but evaluation in §4.1–4.3 uses BM25-retrieved context by default. Both SWE-Llama 7b and 13b resolve only 0.70% of instances under BM25 retrieval — a pattern consistent with sensitivity to the shift between the context distribution seen during training and the context distribution seen at evaluation, echoing at a different scale the general context-sensitivity pattern documented in §4.3 {C005}.

### 4.6 A smaller subset, and how much models' successes overlap

Two supplementary comparisons round out the picture. On SWE-bench Lite, a 300-instance subset emphasizing self-contained, functional bug fixes, resolution rates are higher than on the full benchmark for both models with directly reported figures: Claude 2 resolves 3.00% on Lite versus 1.96–1.97% on the full set, and Claude 3 Opus resolves 4.33% on Lite versus 3.79% on the full set {C007}. And under oracle retrieval, Claude 2 and SWE-Llama 13b resolve broadly comparable overall numbers of instances, yet Claude 2 solves only 42% of the specific instances that SWE-Llama 13b resolves {C019}. Read together, these two results suggest that "harder" and "easier" are not fixed properties of an instance independent of which model attempts it: different models appear to succeed on partly different subsets of problems, not simply on a shared ranking from easiest to hardest.

## 5. Discussion

**Is a 1–4% resolution rate meaningful?** {C002}{C017} Taken alone, the low headline numbers in §4.1 could be read simply as "current LLMs cannot do real software engineering." The rest of the results complicate that reading without contradicting it. Section 4.2's oracle-versus-BM25 comparison, §4.3's context-length and retrieval-precision results, and §4.6's SWE-bench Lite comparison are all consistent with a sizable part of the low resolution rate being attributable to models not being shown, or not being able to make use of, the specific context a fix requires {C004}{C013}{C018} — rather than being uniformly unable to produce a correct fix once that context is available. We interpret these converging patterns as being consistent with a **context-selection bottleneck**: performance on SWE-bench in its realistic (BM25) configuration is gated in large part by whether the right code is found and shown to the model, and by how much irrelevant material surrounds it, not solely by whether the model can write the fix {C017}.

We are careful about the strength of this interpretation. Nothing in our evaluation isolates a causal mechanism inside the model (for instance, distinguishing an attention-capacity limitation from some other consequence of long, mostly irrelevant input); the interpretation is consistent with, and corroborated by, a documented general finding that LLMs have difficulty making full use of long input contexts (Liu et al., 2023b), but we did not run a controlled ablation that isolates *why* longer or less-precise context hurts on this benchmark specifically {L002}. We also do not claim the context-selection bottleneck is the *only* limitation: the 4.80% and 5.93% oracle-setting resolution rates, while several times higher than the 1.96% BM25 figure, are still far from saturating the benchmark, and the much shorter, narrower patches models produce relative to gold patches (§4.4) indicate meaningful headroom in generation itself once context is no longer the limiting factor {C006}.

**Relation to prior work available to us.** As discussed in §2, we did not conduct a systematic literature search for this project, so we make no comparative claim relative to a broader landscape of coding or retrieval benchmarks beyond what is documented in the materials available to us. Where we do draw on an external source, for the long-context interpretation above, we do so narrowly and mark it as corroboration, not as the basis for a stronger causal claim.

**A note on model complementarity.** {C019} The partial (42%) overlap between the specific instances Claude 2 and SWE-Llama 13b resolve under oracle retrieval (§4.6) is a single data point, but it is suggestive: if different models were simply arranged along one difficulty axis, a stronger model's successes would be expected to be close to a superset of a weaker model's successes. That is not what we observe. This is consistent with different models bringing at least partly different strengths to this task, though we do not have the evidence in hand to characterize what drives the difference.

**Practical implication.** If context selection is indeed a major, addressable part of the gap, then improving practical large language model (LLM) performance on real-world software engineering tasks may depend as much on better retrieval and long-context robustness as on further scaling raw generation capability {C017}. We state this as an implication consistent with our results, not as an established causal finding.

## 6. Limitations

We report the following limitations, each tied to the specific claims it bounds.

- **Language scope.** SWE-bench's task instances are drawn exclusively from Python repositories. Every claim above about model resolution rates, patch characteristics, and the context-selection interpretation is scoped to Python software engineering; nothing here speaks to other languages {L004}.
- **Resolution rate is not code quality.** "Resolved" means a candidate patch passed the specified tests; it does not mean the patch is efficient, readable, or maintainable by other standards. A technically correct but stylistically poor patch counts as resolved, and (in principle) a better-engineered patch that happens to miss an edge case covered by the test suite would not {L005}.
- **Single generation per instance.** The reported evaluation generates one patch per instance (a form of Pass@1) rather than reporting variance across multiple attempts; we cannot state whether the differences between models in §4.1 (for example, 1.96% vs. 3.79%) are stable across repeated sampling, only that they are the point estimates the evidence available to us reports.
- **A 25% evaluation subset for GPT-4-turbo.** GPT-4-turbo's reported figures reflect a random 25% subset of instances rather than the full benchmark, due to evaluation budget constraints; comparisons involving this model should be read as approximate rather than on identical footing with models evaluated on the full set {L003}.
- **Two unresolved discrepancies in the source material, disclosed rather than resolved.** Claude 2's BM25 resolution rate is reported as both 1.96% (in running text, used as our primary figure) and 1.97% (in a results table) {L001}; and the source material's prose describes Claude 2 as the best-performing model while its own results table separately reports a higher figure for Claude 3 Opus under an apparently comparable condition {L006}. We report both values in each case rather than picking one silently.
- **Category breakdown is partial.** Of 2,289 tagged instances, we can directly attribute 442 to "bug fix" and 167 to "feature request" from the evidence available; the remaining categories are not independently traceable to a specific count in this evidence package, so we do not report a full category breakdown {C011}.
- **The context-selection interpretation is not a controlled mechanistic finding.** As discussed in §5, the interpretation that context selection meaningfully bottlenecks current performance is supported by several converging, controlled comparisons (oracle vs. BM25; context-length sweep; oracle-collapsed) but does not isolate a specific internal mechanism, and relies in part on corroboration from an external source we could not independently verify beyond its citation in the source material {L002}.

## 7. Conclusion

SWE-bench evaluates language models on a task closer to real software engineering than short, self-contained coding problems allow: given a real GitHub issue and its full repository, can a model produce a patch that resolves it, verified by executable tests drawn from the issue's own resolution history? Across several current LLMs, resolution rates under realistic retrieval are low, from 3.79% down to 0.17% {C002}{C015}. But the gap between this figure and the roughly 2.4x higher rate obtained when the correct files are handed to the model directly — 1.96% rising to 4.80%, and to 5.93% when context is trimmed to the immediately relevant region — indicates that a meaningful share of that gap is about finding and using the right context, not only about generating correct code {C004}{C018}. SWE-bench, and the pattern of results reported here, leave a concrete direction for future work: closing the gap between what these models can do when handed the right context and what they can do when they have to find it themselves.

## References

- Liu et al., 2023b. [Full bibliographic details (venue, title) are not independently verifiable from the evidence available to this project, which had no web access; this work is cited only as it appears in the project's source material, as corroborating evidence for language models' difficulty using long input contexts, in support of §2 and §5.]
