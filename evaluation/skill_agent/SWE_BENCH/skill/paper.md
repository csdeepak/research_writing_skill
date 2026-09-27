# SWE-bench: Evaluating Language Models on Real-World GitHub Issue Resolution

**Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan**
*Princeton University; University of Chicago*
*Published at ICLR 2024*

---

## Abstract

Benchmarks for language model (LM) code generation have largely relied on self-contained tasks solvable in a few lines, leaving open the question of whether LMs can handle the complexity of real software engineering. We present SWE-bench, an evaluation framework of 2,294 task instances drawn from real GitHub issues and pull requests across 12 popular Python repositories. Given a codebase and an issue description, a model must produce a *patch* — a diff file specifying line-level code changes — that passes pre-existing unit tests associated with the issue. SWE-bench tasks require navigating codebases averaging 3,010 files and 438K lines, localizing the relevant code, and making coordinated changes across multiple functions or files. We evaluate ChatGPT-3.5, GPT-4, Claude 2, Claude 3 Opus, and two fine-tuned models (SWE-Llama 7b and 13b, based on CodeLlama). The best BM25-retrieval result is Claude 3 Opus at 3.79% of issues resolved; even with ideally retrieved context, the best result is 9.39% (Claude 3 Opus, oracle-collapsed). Models consistently produce shorter, simpler patches than human reference solutions and struggle to localize relevant code as context length grows. Performance shows no clear difference between instances created before versus after January 2023, offering no evidence that models solve issues by exploiting memorized codebase states. We also release SWE-bench-train (19,000 instances), SWE-Llama, and SWE-bench Lite (a focused 300-instance subset) to support further research. SWE-bench is continuously updatable and represents a challenging long-term testbed for practical LM capabilities.

---

## 1. Introduction

Language models are increasingly deployed in software development contexts — as coding assistants, automated debuggers, and autonomous agents [CITATION NEEDED: quantified statistic on LM deployment in software development]. Despite this deployment pressure, standard evaluation benchmarks have not kept pace: widely used code benchmarks like HumanEval (Chen et al., 2021) and its descendants test self-contained functions solvable in tens of lines of code, while real software maintenance involves navigating entire repositories, understanding interdependencies, and generating changes coordinated across multiple modules.

Real software engineering differs from standard code generation in several important ways. First, the input is a natural-language issue report (a bug description or feature request), not a formal specification. Second, the codebase is large — often thousands of files, hundreds of thousands of lines. Third, the model must decide *where* in the codebase to make changes, not just *what* to write. Fourth, correctness is evaluated by the repository's own test suite, not a benchmark-authored checker. These properties together make repository-level issue resolution a qualitatively harder problem than isolated code synthesis.

We introduce SWE-bench to fill this gap. SWE-bench is built by mining GitHub: we identify pull requests that (a) resolve a reported issue and (b) introduce new tests, then verify each instance by executing the tests before and after the patch. This yields 2,294 task instances from 12 popular Python libraries, each fully grounded in real development history. The benchmark is continuously updatable by applying the same pipeline to new repositories or new pull requests, ensuring it will not saturate as models improve.

Our primary contribution is the benchmark itself, together with a systematic evaluation of five state-of-the-art LMs and two fine-tuned models (SWE-Llama). We find that all evaluated models resolve only a small fraction of issues — the best result under realistic retrieval conditions is 3.79%, and even with an idealized, pre-computed context window the best result is 9.39% — revealing a large gap between current capabilities and practical software engineering competence. We also release SWE-bench-train (a 19,000-instance training dataset), SWE-Llama (open fine-tuned models), and SWE-bench Lite (a focused 300-instance subset) to enable open-model research in this domain.

---

## 2. The SWE-bench Benchmark

### 2.1 Task Formulation

A SWE-bench instance consists of three components: (1) a **codebase** C — the repository at a specific commit, before any PR modifications; (2) a **problem statement** P — an aggregated natural-language description drawn from the linked GitHub issue and any comments made before the PR's first commit; and (3) a **test patch** T — new or modified tests introduced by the PR, withheld from the model but used for evaluation.

> **Background — key version-control concepts.** A *GitHub issue* is a structured bug report or feature request filed by any user of a repository. A *pull request (PR)* is a proposed set of code changes submitted by a contributor; when a project maintainer accepts and incorporates the changes, the PR is *merged*. A *diff* (or *patch*) is a text file describing exact line-level changes to source files. The standard representation is the *unified diff format*, which marks deleted lines with `−` and added lines with `+` alongside a small window of unchanged surrounding context. In SWE-bench, the model's task is to produce a patch in this format.

Given C and P, the model's task is to generate a patch such that applying it and running T produces no test failures. The evaluation metric is the **resolve rate**: the percentage of task instances where all fail-to-pass tests (tests that failed before the PR and pass after it) and all pass-to-pass tests (tests that passed before and continue to pass after) pass following the model's patch.

This formulation has a key property: grading is fully automated and deterministic. Passing the test suite is a necessary, though not sufficient, condition for a correct solution — a model may pass all tests with a patch that is inefficient, fragile, or stylistically inconsistent with the codebase. We discuss this limitation in Section 7.

### 2.2 Benchmark Construction

Starting from GitHub's public API, we scraped approximately 90,000 pull requests from the top 100 most downloaded Python packages on PyPI. A three-stage pipeline filtered this set to the final 2,294 instances.

**Stage I — Repository selection and scraping.** We selected widely downloaded packages because they tend to be well-maintained, have structured contributor guidelines, and have broad test coverage. Initial scraping yielded roughly 90,000 candidate PRs across 12 repositories.

**Stage II — Attribute-based filtering.** We retained only merged PRs that (a) explicitly resolve a GitHub issue (identified via keywords such as "fixes #N" in the title, body, or commit messages) and (b) modify one or more test files, indicating that the contributor added or updated tests to verify the fix. This step reduced the candidate set to 11,407 instances.

**Stage III — Execution-based validation.** For each remaining candidate, we installed the repository at the base commit in a version-specific virtual environment, applied the test patch, ran the tests before and after applying the PR's code changes, and checked that at least one test transitioned from **fail to pass**. Instances with installation errors, runtime errors, or no fail-to-pass tests were discarded. This step brought the dataset to its final size of 2,294 instances.

Table 1 summarizes key statistics of the resulting task instances. The typical instance presents a codebase of over 3,000 files and 438,000 lines; the reference solution edits an average of 1.7 files, 3 functions, and 32.8 lines. Each instance has at least one fail-to-pass test, and 40% have at least two. A median of 51 additional pass-to-pass tests verify that the proposed change does not break existing functionality.

**Table 1. SWE-bench Task Instance Statistics** (micro-averages across all 2,294 instances)

| Attribute | Mean | Max |
|---|---|---|
| Issue text length (words) | 195.1 | 4,477 |
| Codebase non-test files | 3,010 | 5,890 |
| Codebase non-test lines | 438K | 886K |
| Gold patch lines edited | 32.8 | 5,888 |
| Gold patch files edited | 1.7 | 31 |
| Gold patch functions edited | 3.0 | 36 |
| Fail-to-pass tests | 9.1 | 1,633 |
| Total tests | 120.8 | 9,459 |

### 2.3 Properties of the Benchmark

Several properties distinguish SWE-bench from prior code generation benchmarks.

**Real-world grounding.** Every task instance is derived from an actual development event: an issue filed by a user, a patch authored by a contributor, and tests written to verify the fix. No synthetic problem formulation is introduced.

**Diverse inputs.** The benchmark covers 12 repositories spanning scientific computing (astropy, sympy, xarray), web frameworks (django, flask, requests), machine learning (scikit-learn), data visualization (matplotlib, seaborn), and developer tooling (pytest, sphinx, pylint), totaling 2,294 unique instances. The largest contributor is django (850 instances) and the smallest is flask (11).

**Execution-based evaluation.** Correctness is determined by running the repository's own test suite, avoiding the ambiguity of semantic similarity metrics or human annotation.

**Continuous updatability.** The pipeline can be re-applied to any Python repository or to new PRs created after any model's training cutoff, providing an ongoing supply of held-out instances. This is a design affordance of the construction methodology: because every instance is anchored to a specific PR and its associated tests, new instances can be added without changing the task formulation. We compare model performance on pre- and post-2023 instances in Section 4.6 as one empirical check on this property.

**Cross-file, cross-function edits.** Unlike benchmarks that constrain changes to a single function or require fill-in-the-blank completions (Chen et al., 2021; Cassano et al., 2022), SWE-bench requires models to identify which parts of a large codebase to modify. Reference solutions average edits across 1.7 files and 3 functions, and models receive no guidance about edit location.

### 2.4 SWE-bench Lite

Because evaluation can be computationally and financially expensive, we also provide **SWE-bench Lite**, a 300-instance subset sampled to include more self-contained instances focused on functional bug fixes. SWE-bench Lite covers 11 of the 12 repositories with a similar diversity of task types.

---

## 3. Models and Experimental Setup

### 3.1 Retrieval-Based Context Construction

The full codebase averages 438,000 lines, far exceeding the context window of any current LM. A key design decision in evaluation is how to select which portions of the codebase to provide to the model.

Two retrieval strategies are studied:

**BM25 retrieval.** BM25 (Robertson et al., 2009) is a classical term-frequency-based document ranking method. Each repository file is treated as a document and ranked by relevance to the issue description (treated as a query). Files are prepended with their paths to help retrieval based on filenames mentioned in the issue. Each model is evaluated at multiple context limits (13k, 27k, and 50k tokens depending on model capacity); we report the best-performing limit per model without separately disclosing which limit produced the reported number. As discussed in Section 4.3, larger context limits improve retrieval recall but hurt solve rates.

**"Oracle" retrieval.** As an upper bound on retrieval quality, models are also tested receiving exactly the files modified by the reference solution. This setting is unrealistic in practice — a developer working on an issue would not know in advance which files need to change — but it isolates model capability from retrieval quality. A further variant, **"oracle-collapsed"** context, trims oracle files to show only the ±15 lines surrounding the actually edited lines, minimizing distracting surrounding code.

Table 2 shows that BM25 retrieval quality is modest: at the 27k-token limit, only 51.27% of instances have any oracle file retrieved, and in approximately half of instances with a 27k limit, none of the oracle files are retrieved at all.

**Table 2. BM25 Recall of Oracle Files at Different Context Lengths**

| BM25 Context | Avg Recall | All Oracle Files | Any Oracle File |
|---|---|---|---|
| 13k tokens | 29.58% | 26.09% | 34.77% |
| 27k tokens | 44.41% | 39.83% | 51.27% |
| 50k tokens | 51.06% | 45.90% | 58.38% |

### 3.2 Models Evaluated

Models with sufficiently large context windows are selected: **ChatGPT-3.5** (gpt-3.5-turbo-16k-0613, 16,385 tokens), **GPT-4** (gpt-4-32k-0613, 32,768 tokens; evaluated on a 25% subset due to budget constraints), **Claude 2** (100,000 tokens), **Claude 3 Opus**, and **SWE-Llama 7b** and **SWE-Llama 13b** (≥100,000 tokens). Models receive an instruction prompt, the issue text, retrieved code files, and an example patch; they are asked to generate a patch in unified diff format. Greedy decoding is used throughout (Pass@1).

### 3.3 SWE-Llama: Fine-Tuning for Repository Editing

Off-the-shelf CodeLlama (Rozière et al., 2023) variants failed at this task — they could not follow instructions to produce repository-level patches and typically output placeholder responses. To evaluate fine-tuned open models, SWE-Llama is trained on a dedicated training dataset.

**Training data.** SWE-bench-train comprises 19,000 issue-PR pairs from 37 additional Python repositories, disjoint from the evaluation set. Unlike the evaluation set, these instances do not require the PR to contribute new tests, enabling a much larger dataset. After filtering sequences exceeding 30,000 tokens, approximately 10,000 instances are used for training.

**Training procedure.** The 7B- and 13B-parameter CodeLlama-Python models are fine-tuned using LoRA (Hu et al., 2022), a parameter-efficient technique that inserts small trainable adapter matrices into the model's attention layers while leaving base model weights frozen, so only a fraction of total parameters are updated. Specifically, we used rank r=16, α=16, and 5% dropout on all attention projection matrices. Training used a learning rate of 6×10⁻⁴ and batch size 32 for up to 4 epochs. Long-context training was enabled by DeepSpeed Ulysses (Jacobs et al., 2023) and FlashAttention (Dao et al., 2022). SWE-Llama 7b trained for 20 hours on 4 A100 GPUs; SWE-Llama 13b for 47 hours on 8 A100s. The best checkpoint was selected by validation loss on a 100-instance held-out set.

---

## 4. Results

### 4.1 Main Results Under BM25 Retrieval

Table 3 reports resolve rates for all models under BM25 retrieval (best context length per model). All models resolve only a small fraction of issues. Claude 3 Opus achieves the best performance at 3.79%, followed by Claude 2 at 1.97%, GPT-4 at 1.31%, SWE-Llama 7b and 13b each at 0.70%, and ChatGPT-3.5 at 0.17%. Because all resolve rates are below 5% and no variance is reported (see Section 7), small absolute differences in rank should be interpreted cautiously — a handful of additional resolved instances could shift relative positions. On SWE-bench Lite, numbers are slightly higher: Claude 3 Opus reaches 4.33%, Claude 2 reaches 3.00%.

**Table 3. Model Resolve and Apply Rates (BM25 Retrieval)**

| Model | SWE-bench % Resolved | SWE-bench % Apply | Lite % Resolved | Lite % Apply |
|---|---|---|---|---|
| Claude 3 Opus | 3.79% | 46.56% | 4.33% | 51.67% |
| Claude 2 | 1.97% | 43.07% | 3.00% | 33.00% |
| GPT-4 | 1.31% | 26.90% | 2.67% | 29.67% |
| ChatGPT-3.5 | 0.17% | 26.33% | 0.33% | 10.00% |
| SWE-Llama 13b | 0.70% | 53.62% | 1.00% | 38.00% |
| SWE-Llama 7b | 0.70% | 51.74% | 1.33% | 38.00% |

The **apply rate** — the fraction of generated patches that could be applied to the codebase at all — varies substantially. SWE-Llama models apply patches more reliably (50–54%) despite lower resolve rates, reflecting the effect of fine-tuning on patch formatting. Proprietary models apply only 26–47% of generated patches, even after a post-processing repair step that strips extraneous context lines and recalculates headers.

### 4.2 Effect of Retrieval Quality

Table 4 shows performance under oracle and oracle-collapsed retrieval. Moving from BM25 to oracle retrieval roughly doubles Claude 2's resolve rate (1.97% → 4.80%), demonstrating that retrieval quality is a major bottleneck. Moving to oracle-collapsed context — which removes distracting surrounding code while retaining the edit locations — provides a further improvement: Claude 2 reaches 5.93%, Claude 3 Opus reaches 9.39%, and GPT-4 jumps from 1.3% (BM25) to 3.4% (oracle-collapsed).

**Table 4. Model Performance Under Oracle and Oracle-Collapsed Context**

| Model | Oracle % Resolved | Oracle-Collapsed % Resolved |
|---|---|---|
| Claude 3 Opus | — *(not evaluated)* | 9.39% |
| Claude 2 | 4.80% | 5.93% |
| GPT-4 | 1.74% | 3.40% |
| ChatGPT-3.5 | 0.52% | 1.09% |
| SWE-Llama 13b | 3.97% | — *(not evaluated)* |
| SWE-Llama 7b | 3.01% | — *(not evaluated)* |

Even with ideally retrieved and precisely collapsed context, the best model resolves fewer than 1 in 10 issues, indicating that retrieval is not the only bottleneck: the models themselves cannot reliably perform the reasoning and code editing required by these tasks.

### 4.3 Context Length Is a Primary Bottleneck

Under BM25 retrieval, Claude 2's resolve rate was highest at the 13k-token context limit (1.96%) and declined at larger context limits, even as retrieval recall increased from 34.77% (13k) to 51.27% (27k) to 58.38% (50k, Table 2). This inverse pattern indicates that the additional code retrieved at larger limits is predominantly irrelevant, and that it distracts the model from the edit locations it does need. The finding is consistent with prior work showing that LMs underperform when target information is diluted among irrelevant text in long contexts (Liu et al., 2023b).

The oracle-collapsed experiment confirms this interpretation: when context is trimmed to ±15-line windows around each edited location (plus the full issue text), performance increases markedly compared to full oracle files — Claude 2 improves from 4.80% (oracle) to 5.93% (oracle-collapsed) — even though the information needed to make the correct edit is identical. The bottleneck is not understanding what to change once shown precisely, but locating the relevant code within a larger input.

### 4.4 Characteristics of Model-Generated Patches

Models that generate applicable patches systematically produce shorter, simpler edits than the reference solutions. Successfully applied patches average about 30 total lines of change, compared with 74.5 lines for the gold patches on those same instances. (The overall mean gold patch across all 2,294 instances is 32.8 lines per Table 1; the 74.5 figure is the mean specifically over the applied-patch subset, which may differ from the full benchmark in difficulty or in how diff lines are counted.) Models rarely edit more than one file, while gold patches average 1.7 files.

Qualitative review of selected instances (illustrative only; selection criteria and representativeness are not established) identifies recurring patterns: models tend to write primitive Python code without leveraging existing utilities in the codebase; they take a "greedy" approach of fixing the immediate symptom without anticipating downstream effects; and they rarely make the structural improvements that human contributors often include alongside a fix.

Table 5 categorizes outcomes for all successfully applied patches. For Claude 2, of 1,078 applied patches: 110 fully resolved the issue; 26 were "breaking resolved" (issue fixed but pre-existing tests broken); 15 were "partially resolved" (some fix tests pass, all pre-existing tests pass); and 907 were No-Op (471) or Regression (436). The dominance of No-Op and Regression outcomes suggests that for most instances models neither locate the relevant code nor understand the issue at the depth required.

**Table 5. Outcomes for Successfully Applied Patches**

| Model | Applied | Resolved | Breaking Res. | Partially Res. | Work in Prog. | No-Op | Regression |
|---|---|---|---|---|---|---|---|
| Claude 2 | 1,078 | 110 | 26 | 15 | 20 | 471 | 436 |
| ChatGPT-3.5 | 284 | 12 | 2 | 4 | 2 | 174 | 90 |
| GPT-4* | 76 | 10 | 3 | 3 | 1 | 30 | 29 |
| SWE-Llama 13b | 1,196 | 91 | 10 | 10 | 16 | 672 | 397 |
| SWE-Llama 7b | 1,257 | 69 | 17 | 17 | 17 | 716 | 421 |

*GPT-4 evaluated on 25% subset.

### 4.5 Fine-Tuned Models and Context Distribution Shift

Under oracle retrieval, SWE-Llama 13b achieves 3.97%, comparable to Claude 2 (4.80%) — a notable result for an open model runnable on consumer hardware. This parity holds *only under oracle retrieval*: under BM25 retrieval, both SWE-Llama models fall to 0.70%. We attribute this to a context distribution shift: training used oracle-retrieved files, so SWE-Llama learned to edit every file present in the context window; under BM25 retrieval, many irrelevant files appear in context, and the model attempts to edit them all, producing incorrect changes.

Additionally, Claude 2 and SWE-Llama 13b resolve largely non-overlapping sets of instances even under oracle retrieval: Claude 2 solves only 42% of the instances solved by SWE-Llama 13b. This complementarity suggests that different model types have distinct strengths, which could potentially be exploited by ensemble or multi-agent strategies.

### 4.6 Temporal Analysis

To test whether models could be exploiting memorized codebase states, resolve rates are compared on instances created before versus after January 2023. For most models, performance is similar on both sides of this boundary: Claude 2 achieves 4.87% on pre-2023 instances and 4.23% on post-2023 instances; SWE-Llama 13b achieves 3.98% and 3.85% respectively. These comparisons use only two coarse time buckets at sub-5% resolve rates with no instance counts or variance reported, and the retrieval setting used is not separately disclosed; they do not constitute a formal memorization test. They offer no evidence, however, that older instances are substantially easier to solve or that models are exploiting memorized codebase history.

---

## 5. Analysis

### 5.1 What Makes SWE-bench Hard?

Our results identify several compounding sources of difficulty.

**Localization within context.** Section 4.3 shows that models perform worse with larger context windows under BM25 despite better recall, and better when oracle context is collapsed to relevant lines only. Even under oracle-collapsed context, the best model resolves fewer than 1 in 10 issues. Models can apparently benefit when shown the precise edit location, but they cannot reliably identify it themselves within a large input.

**Complexity of required edits.** Gold patches often involve structural improvements beyond the minimum fix: they modify helper functions, add new abstractions, or refactor related code. Model patches consistently stay close to the literal symptom described in the issue, a strategy that succeeds on simple bugs but fails when the fix requires broader understanding of the codebase's invariants.

**Multi-file reasoning.** While gold patches edit an average of 1.7 files, model patches rarely stray beyond one file. Many partial failures appear to arise because a change that correctly addresses the immediate issue does not account for other modules that depend on the changed code.

**Patch formatting.** Only 26–54% of model-generated patches apply to the codebase without error. Even logically correct patches with formatting errors are scored as failures in standard evaluation, though a post-processing repair step can recover some cases.

### 5.2 Beyond Test Passage: Software Complexity Metrics

We explore using software engineering complexity metrics to evaluate code quality beyond test passage. Using the Radon library to compute Cyclomatic complexity (McCabe, 1976) and Halstead complexity (Halstead, 1977) for modified functions, we find that model patches can introduce greater Cyclomatic complexity than reference solutions despite being shorter. Cyclomatic complexity counts the number of independent control paths through a function — a higher value indicates more complex, harder-to-maintain code. In one illustrative case from the `requests` library, a 6-line model patch raised the Cyclomatic complexity of a widely used class from 3 to 5 by adding a conditional check, while the 11-line reference solution defined a new, logically isolated exception type, keeping the main class's complexity unchanged. This single case illustrates a potential divergence between passing tests and solution quality; a corpus-wide analysis would be needed to determine how frequently such divergences occur.

### 5.3 Implications for Future Work

The results point to several directions, ordered by expected near-term impact on resolve rates.

**Retrieval and localization** — the single largest addressable bottleneck. BM25 fails to retrieve any relevant file in roughly half of instances; even when it succeeds, larger context windows hurt resolve rates. Learned retrieval models trained on SWE-bench instances, or line-level localization steps that collapse retrieved files before passing them to the model, could yield substantial gains even with current model architectures. The oracle-collapsed ceiling (6–9%) provides a rough estimate of what perfect localization might unlock.

**Agent-based and interactive approaches.** Our baselines are single-pass retrieval systems. The outcome breakdown in Table 5 suggests that execution feedback could be highly valuable: many partially resolved cases fail because the model did not anticipate the effect of its change on adjacent code; an agent that can run tests iteratively and inspect tracebacks might correct many of these errors.

**Multi-modal inputs.** Roughly 32% of matplotlib issues and 10% of seaborn issues contain embedded images in the issue text, compared to 2% overall. Solving such instances likely requires multi-modal LMs capable of interpreting screenshots referenced in the bug report.

---

## 6. Related Work

**Code generation benchmarks.** HumanEval (Chen et al., 2021) remains the standard for self-contained function synthesis from docstrings. Subsequent work extended it to additional programming languages (Cassano et al., 2022), class-level generation (Du et al., 2023), and code infilling (Fried et al., 2023). These benchmarks provide valuable controlled evaluations but restrict scope to isolated functions with explicit specifications. SWE-bench addresses the complementary challenge: repository-scale editing driven by natural-language issue reports, evaluated by the repository's own tests.

**Multi-task and agent benchmarks.** Multi-task suites (Hendrycks et al., 2021; Liang et al., 2022; Srivastava et al., 2023) provide broad coverage of LM capabilities, while interactive environments (Yao et al., 2022; Zhou et al., 2023; Liu et al., 2023d) require sequential decision-making. SWE-bench differs from these in grounding every task in real development history rather than constructed scenarios, and in using the repository's own test suite as the evaluator.

**Automated program repair.** The software engineering community has studied automated program repair for decades (Monperrus, 2018; Goues et al., 2019), with recent interest in applying LMs (Xia and Zhang, 2022; Fan et al., 2023; Sobania et al., 2023). Existing benchmarks like Defects4J (Just et al., 2014) cover smaller Java codebases with manually curated bugs. SWE-bench provides larger-scale, more diverse, and automatically extensible coverage in Python, with natural-language issue descriptions as the primary input.

---

## 7. Limitations

**Python only.** All task instances come from Python repositories. The construction pipeline is general and could be applied to other languages, but doing so requires language-specific execution environments and may encounter different challenges in patch parsing.

**Single-pass baseline evaluation.** All experimental results use retrieval-then-generate pipelines, the simplest possible approach. Agent-based systems that interact with execution environments, call search tools, or iteratively refine patches are not evaluated. Our results establish a floor on current performance, not a ceiling on what SWE-bench can reveal.

**Test passage as a proxy for correctness.** A generated patch that passes all tests may still be less efficient, less readable, or less robust than a human-written solution, as our preliminary complexity analysis (Section 5.2) illustrates on individual cases. Test passage is a necessary but not sufficient condition for solution quality.

**No variance reporting.** We use greedy decoding (Pass@1) for all models and do not report variance across sampling seeds. Given that all BM25 resolve rates are below 5%, small absolute differences between models may not be statistically distinguishable.

**GPT-4 subset evaluation.** Due to API cost constraints, GPT-4 was evaluated on a 25% random subset (574 instances). Subset results are consistent with full-set trends for other models, but the smaller sample increases uncertainty.

---

## 8. Conclusion

SWE-bench demonstrates that the challenge of real-world software engineering — locating, understanding, and correctly modifying a large, evolving codebase in response to a natural-language issue report — lies substantially beyond the current capabilities of even the strongest LMs. The best results, 3.79% resolved under realistic retrieval and 9.39% under idealized context, leave vast room for improvement and define a clear research frontier.

The benchmark's design ensures it will remain relevant as models improve: continuous updatability, execution-based evaluation, and diversity across repositories prevent the saturation that has affected simpler code benchmarks (Kiela et al., 2021; Ott et al., 2022). Our analysis identifies three compounding bottlenecks, in order of near-term addressability: (1) retrieval and localization — BM25 misses all relevant files in roughly half of instances and large contexts distract models even when the right files are present; (2) multi-file reasoning — model patches rarely extend beyond one file while gold patches average 1.7; (3) patch formatting — roughly half of generated patches cannot be applied without repair. The release of SWE-bench-train, SWE-Llama, and SWE-bench Lite provides an open foundation for the community to explore fine-tuning strategies, retrieval improvements, and agent-based approaches on this challenging and practically relevant task.

---

## References

Cassano, F., Gouwar, J., Nguyen, D., et al. (2022). MultiPL-E: A scalable and extensible approach to benchmarking neural code generation.

Chen, M., Tworek, J., Jun, H., et al. (2021). Evaluating large language models trained on code.

Dao, T., Fu, D., Ermon, S., et al. (2022). FlashAttention: Fast and memory-efficient exact attention with IO-awareness. *Advances in Neural Information Processing Systems*, 35, 16344–16359.

Du, X., Liu, M., Wang, K., et al. (2023). ClassEval: A manually-crafted benchmark for evaluating LLMs on class-level code generation.

Fan, Z., Gao, X., Mirchev, M., et al. (2023). Automated repair of programs from large language models.

Fried, D., Aghajanyan, A., Lin, J., et al. (2023). InCoder: A generative model for code infilling and synthesis.

Goues, C. L., Pradel, M., and Roychoudhury, A. (2019). Automated program repair. *Communications of the ACM*, 62(12), 56–65.

Halstead, M. H. (1977). *Elements of Software Science*. Elsevier.

Hendrycks, D., Basart, S., Kadavath, S., et al. (2021). Measuring coding challenge competence with APPS.

Hu, E. J., Shen, Y., Wallis, P., et al. (2022). LoRA: Low-rank adaptation of large language models. *ICLR 2022*.

Jacobs, S. A., Tanaka, M., Zhang, C., et al. (2023). DeepSpeed Ulysses: System optimizations for enabling training of extreme long sequence transformer models.

Just, R., Jalali, D., and Ernst, M. D. (2014). Defects4J: A database of existing faults to enable controlled testing studies for Java programs. *ISSTA 2014*.

Kiela, D., Bartolo, M., Nie, Y., et al. (2021). Dynabench: Rethinking benchmarking in NLP.

Liang, P., Bommasani, R., Lee, T., et al. (2022). Holistic evaluation of language models.

Liu, N. F., Lin, K., Hewitt, J., et al. (2023b). Lost in the middle: How language models use long contexts.

Liu, X., Yu, H., Zhang, H., et al. (2023d). AgentBench: Evaluating LLMs as agents.

Martínez-Plumed, F., Barredo, P., Ó hÉigeartaigh, S., and Hernández-Orallo, J. (2021). Research community dynamics behind popular AI benchmarks. *Nature Machine Intelligence*, 3, 581–589.

McCabe, T. J. (1976). A complexity measure. *IEEE Transactions on Software Engineering*, SE-2(4), 308–320.

Monperrus, M. (2018). Automatic software repair. *ACM Computing Surveys*, 51(1), 1–24.

Ott, S., Barbosa-Silva, A., Blagec, K., et al. (2022). Mapping global dynamics of benchmark creation and saturation in artificial intelligence. *Nature Communications*, 13.

Robertson, S., Zaragoza, H., et al. (2009). The probabilistic relevance framework: BM25 and beyond. *Foundations and Trends in Information Retrieval*, 3(4), 333–389.

Rozière, B., Gehring, J., Gloeckle, F., et al. (2023). Code Llama: Open foundation models for code.

Sobania, D., Briesch, M., Hanna, C., and Petke, J. (2023). An analysis of the automatic bug fixing performance of ChatGPT.

Srivastava, A., Rastogi, A., Rao, A., et al. (2023). Beyond the imitation game: Quantifying and extrapolating the capabilities of language models.

Xia, C. S. and Zhang, L. (2022). Less training, more repairing please: Revisiting automated program repair via zero-shot learning. *ESEC/FSE 2022*.

Xia, C. S. and Zhang, L. (2023). Conversational automated program repair.

Yao, S., Chen, H., Yang, J., and Narasimhan, K. (2022). WebShop: Towards scalable real-world web interaction with grounded language agents.

Zhou, S., Xu, F. F., Zhu, H., et al. (2023). WebArena: A realistic web environment for building autonomous agents.
