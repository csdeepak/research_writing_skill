# SWE-bench: Can Language Models Resolve Real-World GitHub Issues?

**Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan**
Princeton University, Princeton Language and Intelligence, University of Chicago

---

## Abstract

Existing benchmarks for evaluating large language models (LLMs) on code have become saturated and fail to capture the frontier of model capabilities. Real-world software engineering presents a richer, more demanding testbed: fixing a bug or implementing a feature in a production codebase requires navigating thousands of files, understanding cross-module dependencies, and generating structured edits rather than short snippets. We introduce **SWE-bench**, an evaluation framework consisting of 2,294 task instances drawn from real GitHub issues and their corresponding pull requests across 12 popular Python repositories. Given a codebase and an issue description, a model must generate a patch that resolves the issue and passes the repository's automated test suite. We show that state-of-the-art proprietary models and a purpose-built fine-tuned model (SWE-Llama) all struggle severely: the best-performing model, Claude 2, resolves only 1.96% of issues under realistic retrieval conditions. Our analysis identifies context length sensitivity, poor localization of relevant code, and a tendency to generate overly simple patches as key failure modes, pointing toward richer evaluation and training paradigms for future LM development.

---

## 1. Introduction

Language models are increasingly deployed in software development tooling—autocomplete assistants, refactoring tools, and automated bug-fixers. Yet the benchmarks used to track LM progress on code remain largely disconnected from the complexity of real software engineering. Benchmarks like HumanEval (Chen et al., 2021) measure the ability to write self-contained functions from docstrings, a setting that omits most of what makes software engineering hard: large codebases, inter-file dependencies, iterative debugging against test suites, and the need to produce structured change representations rather than complete files.

We identify a natural, high-quality source of real-world coding problems in GitHub pull requests (PRs). A merged PR that (1) resolves a reported issue and (2) contributes new tests provides both a well-defined problem statement and an execution-based oracle for correctness. By harvesting such PRs from popular Python libraries, we construct **SWE-bench**: a benchmark where each task instance presents a model with an issue description and a full codebase snapshot, and asks it to produce a patch file that passes all relevant unit tests.

Several properties distinguish SWE-bench from prior coding benchmarks:

- **Realistic complexity.** Reference solutions edit an average of 1.7 files, 3.0 functions, and 32.8 lines simultaneously.
- **Execution-based evaluation.** Correctness is determined by running the project's own test suite, not by surface-level text matching.
- **Continual updatability.** The collection pipeline can harvest new instances from any Python repository with minimal human effort, ensuring tasks can always postdate a model's training cutoff.
- **Diversity.** Instances span 12 repositories covering web frameworks, scientific computing, visualization, documentation, and computer algebra.

We evaluate ChatGPT-3.5, GPT-4, Claude 2, and fine-tuned variants of CodeLlama we call SWE-Llama. All models fail to resolve the vast majority of issues, with the best result at 1.96% under realistic conditions, establishing SWE-bench as a meaningful long-range challenge for LM research.

---

## 2. Benchmark Construction

### 2.1 Data Collection Pipeline

Task instances are produced by a three-stage pipeline applied to pull requests from 12 popular open-source Python repositories on GitHub (approximately 90,000 PRs in total). We deliberately target popular, well-maintained repositories because they tend to have clear contributor guidelines, comprehensive test coverage, and structured issue-tracking practices.

**Stage I: Repository selection and scraping.** We selected the 12 repositories from the top 100 most-downloaded PyPI packages (as of August 2023) with open-source licenses permitting research use. All PRs from each repository are collected via the GitHub API.

**Stage II: Attribute-based filtering.** From the full PR collection we retain only merged PRs that (a) explicitly resolve one or more GitHub issues (identified by keywords such as "fixes #N" in the PR title, body, or commit messages) and (b) modify at least one file whose path contains a testing-related keyword (e.g., "test", "testing"), indicating that the contributor added or modified tests to verify the fix.

**Stage III: Execution-based validation.** Each candidate task instance undergoes automated validation in a dedicated virtual environment. The test patch (modifications to test files) is applied to the base codebase, and tests are run before and after applying the solution patch. A candidate is kept only if (a) the codebase installs successfully, (b) the patches apply cleanly, and (c) at least one test transitions from *fail* before the patch to *pass* after—a "fail-to-pass" test that directly verifies resolution of the issue.

After all three stages, 90,000 PRs are filtered down to **2,294 task instances**. Table 1 summarizes how many candidates survived each stage per repository.

**Table 1. Candidate task instances at each pipeline stage.**

| Repository | PRs Crawled | Post-Conversion | Final |
|---|---|---|---|
| astropy | 9,469 | 1,016 | 95 |
| django | 16,914 | 2,880 | 850 |
| flask | 2,434 | 107 | 11 |
| matplotlib | 16,545 | 1,057 | 184 |
| pylint | 3,848 | 787 | 57 |
| pytest | 5,147 | 750 | 119 |
| requests | 2,344 | 84 | 44 |
| scikit-learn | 15,159 | 1,169 | 229 |
| seaborn | 1,004 | 203 | 22 |
| sphinx | 4,931 | 645 | 187 |
| sympy | 11,928 | 1,897 | 386 |
| xarray | 3,416 | 812 | 110 |
| **Total** | **93,139** | **11,407** | **2,294** |

### 2.2 Task Formulation

Each task instance contains:

- **Problem statement** — an aggregation of the issue's title, body, and any comments posted before the PR's initial commit. Issues average 195 words.
- **Codebase snapshot** — identified by a repository name and base commit hash. Codebases average 3,010 non-test files and 438K lines of non-test code.
- **Test patch** — the new or modified test files introduced by the PR, used as the evaluation oracle.
- **Gold patch** — the PR's non-test code changes, stored as a standard `.patch` file. This is never shown to the model during evaluation; it serves only as a reference.

A model receives the problem statement and some portion of the codebase (determined by a retrieval step; see Section 4) and must output a `.patch`-formatted prediction. The prediction is applied to the codebase with unix `patch`, the test suite is executed, and the instance is considered **resolved** if and only if all fail-to-pass tests now pass *and* all previously passing tests (pass-to-pass tests) continue to pass.

### 2.3 Benchmark Characteristics

**Table 2. Average statistics for SWE-bench task instances (micro-averages across all instances).**

| Attribute | Mean | Max |
|---|---|---|
| Issue text length (words) | 195.1 | 4,477 |
| Codebase files (non-test) | 3,010 | 5,890 |
| Codebase lines (non-test) | 438K | 886K |
| Gold patch: lines edited | 32.8 | 5,888 |
| Gold patch: files edited | 1.7 | 31 |
| Gold patch: functions edited | 3.0 | 36 |
| Fail-to-pass tests | 9.1 | 1,633 |
| Total tests | 120.8 | 9,459 |

The task requires models to navigate large, multi-file codebases under conditions that differ fundamentally from typical code generation benchmarks:

- **Cross-context editing.** Unlike fill-in-the-blank or function-level generation, SWE-bench requires identifying what to change across a large codebase with no explicit pointers to the relevant locations.
- **Robust evaluation.** 40% of instances have at least two fail-to-pass tests, and a median of 51 pass-to-pass tests verify that prior behavior is maintained.
- **Diverse issue types.** Issue tags show that the majority of instances involve bug fixes, but the dataset also includes feature requests, regressions, and other enhancement categories.

### 2.4 SWE-bench Lite

To support iterative development where the full benchmark may be prohibitively expensive to run, the authors also release **SWE-bench Lite**: a curated subset of 300 task instances selected to be more self-contained and focused on functional bug fixes. SWE-bench Lite covers 11 of the 12 repositories and preserves a similar distribution across them.

---

## 3. SWE-Llama: Fine-Tuning a Long-Context Model

Off-the-shelf open models at the time of writing cannot reliably generate well-formed patch files in response to software engineering prompts; they tend to output placeholder responses or unrelated code. To produce a meaningful open-model baseline, we fine-tune two sizes of CodeLlama-Python (Rozière et al., 2023)—the 7B and 13B parameter variants—on task instances collected from an additional 37 repositories not included in the evaluation set. The resulting models are called **SWE-Llama 7b** and **SWE-Llama 13b**.

**Training data.** 19,000 issue–PR pairs are collected following the same procedure as Section 2.1, but without requiring that PRs contribute test changes. This relaxation allows a much larger training corpus. Repositories in the training set are strictly disjoint from those in the evaluation set to prevent contamination. After filtering sequences exceeding 30,000 tokens, the effective training set contains approximately 10,000 instances.

**Training procedure.** Each training example presents the model with task instructions, the issue text, and the oracle-retrieved relevant files; the target output is the gold patch. Parameter-efficient fine-tuning is applied using LoRA (Hu et al., 2022) with rank r = 16, α = 16, and dropout 0.05, targeting the query, key, value, and output projection matrices of every attention layer. Training uses a learning rate of 6e−4 and a batch size of 32 sequences for up to 4 epochs. DeepSpeed Ulysses (Jacobs et al., 2023) and Flash Attention (Dao et al., 2022) enable training over the required long sequences. SWE-Llama 7b was trained in 20 hours on 4 NVIDIA A100s; SWE-Llama 13b was trained in 47 hours on 8 A100s.

A key design consideration is that both models can process sequences exceeding 100,000 tokens, which is essential given codebases that run to hundreds of thousands of lines.

---

## 4. Experimental Setup

### 4.1 Retrieval-Based Context Construction

A central challenge is that codebases contain far more tokens than any model's context window. A model must therefore be provided with a selected subset of files. We consider two retrieval settings:

**Sparse retrieval (BM25).** We use BM25 (Robertson et al., 2009), a classical term-frequency-based ranking method, to retrieve the most relevant files given the issue text as a query. File paths are prepended to file content to improve retrieval on filenames mentioned in the issue. We evaluate multiple maximum context lengths (13k, 27k, and 50k tokens) and report best performance for each model. Across models, shorter context limits tend to yield better performance despite lower recall.

**Oracle retrieval.** For diagnostic purposes, we also evaluate a setting where the model is given exactly the files that are edited by the reference patch. This setting is not realistic (a developer does not know which files to change before fixing an issue), but it provides an upper bound on performance under perfect file selection. Oracle files are not sufficient to guarantee success; they may not include all context needed to understand inter-module dependencies.

With a 27k-token context limit, BM25 retrieves a superset of the oracle files in approximately 40% of instances, but retrieves none of the oracle files in almost half of instances—highlighting the difficulty of file localization from natural language queries.

### 4.2 Models Evaluated

Due to the long-context requirements of SWE-bench, only a handful of models are suitable. We evaluate:

- **ChatGPT-3.5** (gpt-3.5-turbo-16k-0613): 16,385-token context; covers 58.1% of instances within window.
- **GPT-4** (gpt-4-32k-0613): 32,768-token context; covers 84.1% of instances.
- **Claude 2**: 100,000-token context; covers 96.4% of instances.
- **SWE-Llama 7b and 13b**: ≥100,000-token context; covers ≥94.8% of instances.

Models with shorter context windows are inherently disadvantaged because they cannot see all oracle files even with perfect retrieval. All models generate a single patch per instance using greedy decoding, following standard evaluation practice for code generation at Pass@1 (Chen et al., 2021).

---

## 5. Results

### 5.1 Main Results

**Table 3. Model performance on SWE-bench and SWE-bench Lite with BM25 retrieval.**

| Model | SWE-bench % Resolved | SWE-bench % Apply | Lite % Resolved | Lite % Apply |
|---|---|---|---|---|
| Claude 3 Opus | 3.79 | 46.56 | 4.33 | 51.67 |
| Claude 2 | 1.97 | 43.07 | 3.00 | 33.00 |
| GPT-4-turbo | 1.31 | 26.90 | 2.67 | 29.67 |
| ChatGPT-3.5 | 0.17 | 26.33 | 0.33 | 10.00 |
| SWE-Llama 13b | 0.70 | 53.62 | 1.00 | 38.00 |
| SWE-Llama 7b | 0.70 | 51.74 | 1.33 | 38.00 |

All models fail to resolve the vast majority of issues. Under BM25 retrieval, Claude 2 achieves 1.96% resolution on the full set (1.97% is reported in Table 3 with a minor rounding difference in the paper). The "% Apply" column shows what fraction of generated patches can even be applied syntactically to the codebase; patch applicability is a separate hurdle from semantic correctness.

Under oracle retrieval (perfect file selection), performance improves but remains low. Claude 2 resolves 4.80% of instances with oracle files, compared to 1.97% with BM25. SWE-Llama 13b reaches 3.97% with oracle retrieval, nearly matching Claude 2.

**Table 4. Model performance under oracle retrieval.**

| Model | % Resolved | % Apply |
|---|---|---|
| Claude 2 | 4.80 | 62.82 |
| SWE-Llama 13b | 3.97 | 66.78 |
| SWE-Llama 7b | 3.01 | 65.52 |
| GPT-4 | 1.74 | 34.00 |
| ChatGPT-3.5 | 0.52 | 21.80 |

### 5.2 Difficulty Varies Across Repositories

Resolution rates differ substantially by repository. Under oracle retrieval, Claude 2 resolves 15.91% of instances from the `requests` library but 0% of instances from `seaborn` and `flask`. Performance patterns are correlated across models: repositories that are harder for one model tend to be harder for all. However, models do not solve the same individual instances. Claude 2 and SWE-Llama 13b each resolve similar numbers of instances in the oracle setting (110 and 91 respectively), yet Claude 2 solves only 42% of the instances solved by SWE-Llama—models appear to differ qualitatively in which instances they can handle.

One driver of variation is image content in issue descriptions. 32% of matplotlib instances and 10% of seaborn instances contain embedded image links in their issue text, compared to just 2% overall. Models without vision capabilities cannot process these images, which may explain lower performance on visual repositories.

### 5.3 Context Length Sensitivity

As total input length increases, model performance drops considerably. Claude 2's resolution rate falls substantially as input size grows beyond 20k tokens, and other models show similar trends. This behavior is consistent with the "lost in the middle" phenomenon (Liu et al., 2023b), wherein models struggle to utilize information located far from the beginning or end of their context.

Importantly, increasing the context limit for BM25 retrieval—which does increase recall of oracle files—does not improve and often worsens performance. Despite better coverage, models cannot effectively localize the relevant code within a larger context.

**Table 5. Claude 2 resolution rates by BM25 context limit.**

| Context Limit | % Resolved |
|---|---|
| 13k tokens | 1.96 |
| 27k tokens | 1.87 |
| 50k tokens | 1.22 |

The collapsed oracle experiment illustrates this sharply. When oracle files are provided but all code not directly edited by the gold patch (±15 lines of buffer) is removed, performance increases substantially:

**Table 6. Performance under "oracle-collapsed" retrieval (oracle files, non-edited code removed).**

| Model | % Resolved | % Apply |
|---|---|---|
| Claude 3 Opus | 9.39 | 48.00 |
| Claude 2 | 5.93 | 68.18 |
| GPT-4 | 3.40 | 48.65 |
| ChatGPT-3.5 | 1.09 | 40.93 |

GPT-4 jumps from 1.31% (BM25) to 3.40% (oracle-collapsed), and Claude 2 from 1.97% to 5.93%. The gap between oracle-collapsed and oracle (full oracle files) results confirms that the bottleneck is not just retrieving the right file, but identifying the right lines within it.

### 5.4 Temporal Robustness

A concern for any code benchmark is that models may have seen repository content during pretraining and can exploit memorization rather than reasoning. Table 7 compares performance on task instances from before versus after 2023 under oracle retrieval.

**Table 7. Resolution rates before and after 2023 (oracle retrieval).**

| Model | Before 2023 | After 2023 |
|---|---|---|
| Claude 2 | 4.87% | 4.23% |
| ChatGPT-3.5 | 0.49% | 0.77% |
| SWE-Llama 7b | 2.95% | 3.46% |
| SWE-Llama 13b | 3.98% | 3.85% |

Performance is consistent across the temporal split for all models except GPT-4 (which was evaluated on only a 25% random subset). The absence of a temporal gap suggests models are genuinely reasoning about code changes rather than reciting memorized solutions.

### 5.5 Fine-Tuned Models Are Sensitive to Distribution Shift

SWE-Llama models perform comparably to Claude 2 under oracle retrieval but dramatically worse under BM25 retrieval (0.70% vs. 1.97% for Claude 2). The models were fine-tuned exclusively on oracle-retrieved contexts, so the shift to noisier BM25 context—which includes irrelevant files—disrupts their behavior. Notably, SWE-Llama was trained to edit all files included in context, while BM25 context includes many files that should not be changed. This mismatch manifests as lower performance even though the fine-tuned model has stronger patch formatting skills.

### 5.6 Patch Characteristics of Model Generations

Model-generated patches are consistently shorter and simpler than reference solutions.

**Table 8. Average patch statistics for successfully applied model patches (oracle retrieval).**

| Model | Lines (pred) | Lines (gold) | Files (pred) | Files (gold) |
|---|---|---|---|---|
| Claude 2 | 19.6 | 44.1 | 1.1 | 1.2 |
| ChatGPT-3.5 | 30.1 | 39.6 | 1.0 | 1.2 |
| GPT-4 | 20.9 | 33.6 | 1.0 | 1.1 |
| SWE-Llama 13b | 17.6 | 37.8 | 1.2 | 1.1 |

Model patches that do apply tend to be less than half the length of reference patches. Models rarely edit more than a single file even when the reference solution modifies multiple. Gold patches average 74.5 total lines and 1.7 files edited; the best model averages 30.1 lines and 1.0 files. This pattern suggests models default to minimal, targeted changes rather than the broader structural improvements common in human-authored patches.

Qualitative inspection reveals several recurring failure modes: (a) models write primitive Python without leveraging existing utilities or patterns in the codebase, (b) models take a "greedy" approach that fixes the reported symptom without anticipating related edge cases that gold patches address, and (c) models use absolute imports where the codebase uses relative imports, violating local style conventions.

Asking models to regenerate entire files rather than generating diff-format patches yields worse results across the board. Claude 2 scores 2.2% (full-file regeneration) versus 4.8% (patch format) under oracle retrieval.

### 5.7 Outcome Taxonomy

Beyond the binary resolved/unresolved distinction, we categorize successfully applied patches into six outcomes based on the fate of fail-to-pass (F2P) and pass-to-pass (P2P) tests:

- **Resolved**: all F2P and P2P tests pass.
- **Breaking Resolved**: all F2P tests pass, but some P2P tests fail (issue fixed, regression introduced).
- **Partially Resolved**: all P2P tests pass, but not all F2P tests pass (no regression, partial fix).
- **Work in Progress**: neither all F2P nor all P2P tests pass.
- **No-Op**: 0 F2P tests pass, all P2P pass (patch has no meaningful effect).
- **Regression**: 0 F2P tests pass, some P2P fail (patch worsens the codebase).

**Table 9. Outcome distribution for successfully applied patches (oracle retrieval).**

| Model | Applied | Resolved | No-Op | Regression | Other |
|---|---|---|---|---|---|
| Claude 2 | 1,078 | 110 | 471 | 436 | 61 |
| ChatGPT-3.5 | 284 | 12 | 174 | 90 | 8 |
| GPT-4 | 76 | 10 | 30 | 29 | 7 |
| SWE-Llama 13b | 1,196 | 91 | 672 | 397 | 36 |
| SWE-Llama 7b | 1,257 | 69 | 716 | 421 | 51 |

The majority of unsuccessfully applied patches either do nothing (No-Op: the patch applies but has no meaningful effect on test outcomes) or introduce regressions. Only a small fraction represent partial progress on the underlying issue. This pattern suggests that models often do not engage with the core semantics of an issue; patches that do engage tend to do so incorrectly, breaking existing behavior.

---

## 6. Related Work

**Evaluation of language models.** Multiple benchmarks aggregate diverse tasks spanning many domains (Hendrycks et al., 2021; Liang et al., 2022; Srivastava et al., 2023), or use interactive web environments requiring multi-step planning (Yao et al., 2022; Zhou et al., 2023; Deng et al., 2023). SWE-bench differs in that each instance is a single, deep, realistic engineering problem rather than a narrowly scoped skill probe.

**Code generation benchmarks.** HumanEval (Chen et al., 2021) remains the standard for function-level code synthesis from docstrings. Extensions to multiple programming languages (Cassano et al., 2022; Athiwaratkun et al., 2023), class-level generation (Du et al., 2023), and code-editing settings (Yu et al., 2023) expand coverage. Unlike these datasets—which typically present self-contained or bounded problems—SWE-bench involves repository-scale context, multi-file edits, and evaluation against pre-existing test suites designed by the library authors rather than by the benchmark creators.

**Automated program repair.** A long line of work applies neural models to automated bug repair (Monperrus, 2018; Goues et al., 2019; Xia & Zhang, 2022; 2023; Fan et al., 2023). Prior datasets (Just et al., 2014; Karampatsis & Sutton, 2019) do not present code context at the scale of SWE-bench and are primarily oriented toward small, isolated defects rather than the open-ended, system-wide changes required by real-world issues.

**ML for software engineering.** Broader uses of LMs in software engineering include commit message generation (Jung, 2021), code review (Yang et al., 2016; Tufano et al., 2021), bug localization (Kim et al., 2019), and testing (Kang et al., 2023). SWE-bench provides a unifying evaluation surface that can probe all of these competencies simultaneously as they arise naturally in issue resolution workflows.

---

## 7. Discussion

### 7.1 Key Findings

SWE-bench surfaces three central challenges for current LMs operating in real software engineering settings:

1. **Localization is the bottleneck.** Even when provided with the exact files that need to be edited (oracle retrieval), models resolve fewer than 5% of issues. The oracle-collapsed experiment, which further removes irrelevant code, boosts performance substantially—confirming that models struggle to identify the relevant lines within a file, not just the relevant files within a repository.

2. **Patch formatting and completeness.** Models generate shorter, simpler patches than human developers. They tend to address the immediate symptom without making the broader structural changes that would anticipate related edge cases. This reflects a gap between solving the stated problem and producing production-quality solutions.

3. **Context length is a double-edged sword.** More context increases the probability that the relevant code is present, but also increases the noise through which models must navigate. Performance degrades with context length even when recall improves, indicating that current architectures do not yet effectively utilize very long contexts for code comprehension tasks.

### 7.2 Limitations

SWE-bench is currently Python-only, limiting cross-language generalizability. The baseline models use simple BM25 retrieval and a single-pass generation approach; the authors explicitly encourage future exploration of agentic methods, iterative tool-augmented LMs, and richer context construction strategies. Execution-based testing, while robust, may not fully capture solution quality dimensions like efficiency, readability, or maintainability—a limitation acknowledged in the paper and explored briefly through Cyclomatic and Halstead complexity metrics (McCabe, 1976; Halstead, 1977).

### 7.3 Societal Considerations

The paper notes that as LM capabilities in code generation improve, SWE-bench can serve as a testbed for studying the safety and alignment properties of code-generating agents—particularly ensuring that AI-generated edits faithfully implement human intent and do not introduce undetected regressions or security vulnerabilities.

---

## 8. Conclusion

SWE-bench establishes a challenging, realistic, and continually updatable benchmark for evaluating language models on real-world software engineering tasks. By grounding evaluation in actual GitHub issue resolution—with execution-based correctness checking via the repository's own test suite—the benchmark measures capabilities that are directly relevant to practical LM deployment in software development. The finding that state-of-the-art models resolve fewer than 2% of issues under realistic conditions underscores how far current systems are from autonomous software engineering, while the controlled analyses illuminate the specific failure modes (localization, patch completeness, context sensitivity) that future research must address.

---

## References

Athiwaratkun et al. (2023). Multilingual evaluation of code generation models.

Cassano et al. (2022). Multipl-E: A scalable and extensible approach to benchmarking neural code generation.

Chen et al. (2021). Evaluating large language models trained on code.

Dao et al. (2022). Flashattention: Fast and memory-efficient exact attention with IO-awareness. *NeurIPS*.

Deng et al. (2023). Mind2web: Towards a generalist agent for the web.

Du et al. (2023). ClassEval: A manually-crafted benchmark for evaluating LLMs on class-level code generation.

Fan et al. (2023). Automated repair of programs from large language models.

Goues et al. (2019). Automated program repair. *Communications of the ACM*.

Halstead (1977). *Elements of Software Science*. Elsevier.

Hendrycks et al. (2021). Measuring coding challenge competence with APPS.

Hu et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR*.

Jacobs et al. (2023). DeepSpeed Ulysses: System optimizations for enabling training of extreme long sequence transformer models.

Jung (2021). CommitBERT: Commit message generation using pre-trained programming language model.

Just et al. (2014). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. *ISSTA*.

Kang et al. (2023). Large language models are few-shot testers: Exploring LLM-based general bug reproduction.

Karampatsis & Sutton (2019). How often do single-statement bugs occur? The ManySStuBs4J dataset. *MSR*.

Kiela et al. (2021). Dynabench: Rethinking benchmarking in NLP.

Kim et al. (2019). Precise learn-to-rank fault localization using dynamic and static features of target programs. *TOSEM*.

Liang et al. (2022). Holistic evaluation of language models.

Liu et al. (2023a). Is your code generated by ChatGPT really correct? Rigorous evaluation of large language models for code generation.

Liu et al. (2023b). Lost in the middle: How language models use long contexts.

McCabe (1976). A complexity measure. *IEEE Transactions on Software Engineering*.

Monperrus (2018). Automatic software repair. *ACM Computing Surveys*.

Muennighoff et al. (2023). OctoPack: Instruction tuning code large language models.

Robertson et al. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*.

Rozière et al. (2023). Code Llama: Open foundation models for code.

Srivastava et al. (2023). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models.

Tufano et al. (2021). Towards automating code review activities.

Xia & Zhang (2022). Less training, more repairing please: Revisiting automated program repair via zero-shot learning. *ESEC/FSE*.

Xia & Zhang (2023). Conversational automated program repair.

Yang et al. (2016). Mining the modern code review repositories.

Yang et al. (2023). InterCode: Standardizing and benchmarking interactive coding with execution feedback.

Yao et al. (2022). WebShop: Towards scalable real-world web interaction with grounded language agents.

Yu et al. (2023). CoderEval: A benchmark of pragmatic code generation with generative pre-trained models.

Zhou et al. (2023). WebArena: A realistic web environment for building autonomous agents.
