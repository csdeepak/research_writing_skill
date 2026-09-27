# Gold Account v1: SWE_BENCH (verified)

Sources:
- `evaluation/external_projects/SWE_BENCH/snapshot/paper.txt`: arXiv:2310.06770v3, header "Published as a conference paper at ICLR 2024".
- `evaluation/external_projects/SWE_BENCH/snapshot/README__SWE-bench__SWE-bench.md`.

The paper is authoritative for research claims. The README is used only for artifact facts. Conflicts inside the paper and between the paper and the README are listed explicitly in the conflict log. Issue numbers (#n) refer to `VERIFICATION.md`.

## Changes from draft
1. **"Best model" corrected (#1, #2).** The paper's v3 Table 5 lists Claude 3 Opus at 3.79% with BM25 on the full set, above Claude 2 (1.97%). The abstract's "best-performing model, Claude 2 ... 1.96%" is kept as a verbatim author statement, but it is marked as stale against Table 5. Q7a and Q12b are rewritten, and Q7e is added.
2. **1.96 vs 1.97 (#3).** 1.96 comes from the Abstract, §1, §5 and Table 2. Table 5 prints 1.97. Both are recorded.
3. **Oracle-collapsed comparison narrowed (#4, #5).**
   - "Improved for all tested models" is removed, because Claude 3 Opus has no oracle baseline.
   - The paper's sentence "GPT-4 jumping from 1.3% to 3.4%" is flagged as internally inconsistent. Table 18 gives GPT-4 oracle as 1.74 on the 25% subset, while the collapsed run used the full set (Table 14).
4. **Table 8 parsed properly (#6).** It is reliable: the All Gold row reproduces Table 1 exactly. The 74.5-versus-30.1 sentence is attributed correctly: 30.1 is the ChatGPT-3.5 model-patch total. Draft §17 bullet 3 is deleted.
5. **Qualifier on "shorter edits" (#7).** The claim holds only for successfully applied patches. Across all patches (Table 24), SWE-Llama edits are longer than gold.
6. **GPT-4 subset scope corrected (#13, #14).** The subset applies to the "Oracle" and BM25 27K settings only, and is cited to the Table 7, 18, 20 and 23 captions, not a "Table 5 footnote". GPT-4 oracle-collapsed ran on the full set.
7. **GPT-4 naming conflict recorded (#15).** §4.3 names gpt-4-32k-0613. Table 5 prints "GPT-4-turbo" (1.31 / 26.90). Table 20's GPT-4 BM25 subset row (0.00 / 14.82) does not match it.
8. **Strength labels fixed (#9, #10, #11, #20).**
   - "Only the simplest issues" is now interpretation.
   - The context-length degradation is now observed, and its localization explanation is interpretation.
   - The design rationale is now context.
9. **Limitations (#12, #17).**
   - The "only 11 generations" point moves to verifier notes, because it is not stated by the authors.
   - Added author-stated limitations: oracle context is not comprehensive; shorter-context models are inherently disadvantaged; image-containing issues are unexplored; the baselines have a limited view of the codebase.
10. **README separation (#8, #23, #24, #25).**
    - The README-only nugget Q12d is removed.
    - "Oral" is attributed to the README.
    - Where Multilingual appears in the README is corrected.
    - The Lite row is re-labelled as paper-sourced.
11. **Minor fixes.**
    - The Table 9 field is named "env install commit" (#22).
    - "easily" replaces "rigorously" verified (#19).
    - The GPT-4 exception is added to the temporal claim (#18).
    - The automatic patch-repair step is added to the metrics (#26).
    - The Claude 3 Opus citation is fixed (#16).

## 1. Problem
Existing LM benchmarks "have become saturated" and "fail to capture the frontier of what state-of-the-art LMs can and cannot do" (§1). Coding benchmarks such as HumanEval "mostly involve self-contained problems that can be solved in a few lines of code" (§1). Real software engineering is different: "fixing a bug might involve navigating a large repository, understanding the interplay between functions in different files, or spotting a small error in convoluted code" (§1).

## 2. Motivation
- "Language models have outpaced our ability to evaluate them effectively, but for their future development it is essential to study the frontier of their capabilities" (Abstract).
- A good benchmark must be "challenging enough to stump existing models", and its predictions must be "easy to verify" (§1, citing Martínez-Plumed et al. 2021).
- Coding tasks suit this because "generated solutions can be easily verified by running unit tests" (§1).

## 3. Research gap
- **Multi-task collections.** "Potpourri" collections have tasks that "narrowly focus on one or a few skills, resulting in challenges that are typically too simple" (§6).
- **Code-generation benchmarks.** These either constrain the edit scope to one function or class, or use cloze-style blanks (§2.3). SWE-bench requires unconstrained edits in multiple locations.
- **Program-repair datasets.** No existing automated-program-repair dataset presents "code context at the scale of SWE-bench" (§6).

## 4. Research question/objective
The paper introduces SWE-bench: "2,294 software engineering problems drawn from real GitHub issues and corresponding pull requests across 12 popular Python repositories" (Abstract). It then measures how well proprietary LMs and fine-tuned open LMs resolve these issues (§4, §5).

## 5. System/method
**Three-stage construction pipeline** (§2.1, Figure 2, Appendix A.1–A.3):
1. **Stage I: Repo selection and scraping.** PRs are collected from 12 popular Python repositories: "∼ 90,000 PRs" in the text, 93,139 in Table 10. The repositories come from the top 100 of the 5,000 most-downloaded PyPI packages (August 2023) that have permissive licenses (A.1).
2. **Stage II: Attribute filter.** Keep merged PRs that resolve a GitHub issue, found by linked-issue keywords such as "fixes #24", and that edit test files.
3. **Stage III: Execution filter.** Apply the test patch and run the tests before and after the solution patch. Keep instances with at least one fail-to-pass test and no installation or runtime errors. A.3 adds two more filters: instances whose pre-solution log shows an ImportError or AttributeError are removed, and so are instances whose tests call functions or classes first introduced in the solution (A.1).

**Task formulation** (§2.2). The input is the issue text and the full codebase. The output is a patch file, applied with Unix `patch`, after which the instance's tests are run.

**Baseline context selection** (§4.1). The first setting is BM25 sparse retrieval, with file paths prepended to file contents (D.1), at 13k, 27k and 50k-token limits. Each model is scored at the best limit that fits its context window. The second setting is "oracle" retrieval, which uses the non-test files edited by the reference patch.

**Inference and prompt** (D.2, §4.2):
- Decoding is greedy, and each model generates a single patch per instance.
- The prompt contains the instructions, the issue, the retrieved files and documentation, and an example patch.

**SWE-Llama** (§3, B.1):
- **Base models and data.** CodeLlama-Python 7b and 13b were fine-tuned on 19,000 issue-PR pairs from 37 additional repositories that are disjoint from the evaluation set. Unlike the evaluation set, these pairs were not required to contain test changes.
- **Training input and target.** Training used "oracle"-style context: the files edited by the gold patch.
- **Length filter.** Sequences over 30,000 tokens were excluded, which left 10,000 instances.

## 6. Architecture
SWE-bench is a benchmark plus an evaluation harness, not a model.

**Task instance fields** (Table 9): base commit, created at, hints text, instance id, issue numbers, patch, problem statement, pull number, test patch, version, repo, FAIL TO PASS, PASS TO PASS, and "env install commit". The paper's field name is used here; the draft's `environment_setup_commit` does not appear in the snapshot. hints text is collected but not used in any of the experiments (A.2).

**Validation and evaluation pipeline** (A.3, A.4, Figures 7–8):
1. Create a conda environment for each repository release version.
2. Check out the base commit.
3. Install the codebase.
4. Apply the test patch.
5. Apply the prediction patch. If this fails, attempt an automatic repair (remove unnecessary context lines, recompute headers) and reapply.
6. Run the tests.
7. Mark the instance resolved if and only if every FAIL_TO_PASS and PASS_TO_PASS test passes.

**SWE-Llama** (B.1):
- **LoRA settings.** r=16, α=16, dropout 0.05, applied to the Q/K/V/O projections of every attention sublayer.
- **Optimization.** Learning rate 6e-4, batch of 32 sequences, at most 4 epochs, with the best checkpoint chosen on 100 held-out instances.
- **Compute.** The 7b model trained in 20 hours on 4 A100s; the 13b model in 47 hours on 8 A100s.
- **Long-context tools.** DeepSpeed Ulysses and FlashAttention.

## 7. Dataset/data
- **SWE-bench (test).** 2,294 instances from 12 repositories. Per-repository counts (Table 10 and Figure 3):

  | Repository | Instances |
  |---|---|
  | django | 850 |
  | sympy | 386 |
  | scikit-learn | 229 |
  | sphinx | 187 |
  | matplotlib | 184 |
  | pytest | 119 |
  | xarray | 110 |
  | astropy | 95 |
  | pylint | 57 |
  | requests | 44 |
  | seaborn | 22 |
  | flask | 11 |

- **PR funnel** (Table 10). 93,139 PRs crawled, 11,407 after conversion, 2,294 after validation. For example, django went 16,914 → 2,880 → 850 and sympy 11,928 → 1,897 → 386.
- **SWE-bench-train.** 19,000 issue-PR pairs from 37 disjoint repositories (§1, §3).
- **SWE-bench Lite.** 300 instances covering 11 of the 12 repositories, "sampled to be more self-contained, with a focus on evaluating functional bug fixes" (§2.4). The full criteria are **NOT IN SNAPSHOT**: A.7 cuts off after one sentence, and the §2.4 cross-reference sentence is also truncated.
- **Development set.** 225 instances from 6 repositories: astroid 31, marshmallow 9, pvlib 63, pydicom 56, pyvista 16, sqlfluff 50. Instances were created after January 1, 2019 (A.6, Table 15).
- **README-only artifact facts (not paper claims):**
  - Loading with `load_dataset('princeton-nlp/SWE-bench', split='test')`.
  - The download table lists SWE-bench, Lite, Verified and Multimodal, the SWE-Llama weights (including PEFT variants), and the "Oracle"/BM25 retrieval datasets.
  - Verified (500 problems) was announced on Aug 13, 2024.
  - "Multilingual" appears only as a CLI dataset alias and in a separate citation.
  - None of Verified, Multimodal or Multilingual is described or evaluated in the paper.

## 8. Experimental setup
- **Models** (§4.3, Table 4). Table 4 gives each model's context limit and the share of instances whose full "oracle" context fits in that limit:

  | Model | Max tokens | Oracle context fits |
  |---|---|---|
  | ChatGPT-3.5 (gpt-3.5-turbo-16k-0613) | 16,385 | 58.1% |
  | GPT-4 (gpt-4-32k-0613) | 32,768 | 84.1% |
  | Claude 2 | 100,000 | 96.4% |
  | SWE-Llama 7b/13b | ≥100,000 | ≥94.8% |

  Claude 3 Opus, and a row labelled "GPT-4-turbo", appear only in Tables 5 and 6, with no stated context limit. See conflict C4.
- **Retrieval settings.** BM25 at 13k, 27k or 50k tokens, and "oracle". GPT-4 ran BM25 at 27k (Table 14).
- **"Oracle"-collapsed ablation.** Code is collapsed except the lines edited by the PR plus a ±15-line buffer (Table 6).
- **GPT-4 subset.** "Due to budget constraints", GPT-4 was evaluated on a 25% random subset (574 instances) "in the 'Oracle' and BM25 27K retriever settings only" (Table 18 caption). GPT-4 oracle-collapsed "was run on the full SWE-bench test set" (Table 14 caption).
- **Other analyses:**
  - Whole-file regeneration vs patch generation (§5).
  - A temporal split of results before and after 2023 (Table 7), and by year (Table 21).
  - Per-repository results (Figure 4, Table 19).
  - F2P/P2P outcome categories (Tables 22–23).
  - Radon complexity metrics as a case study (C.7).
- **Qualitative analysis.** 11 selected generations from SWE-Llama and Claude 2, under oracle retrieval (§5.1).

## 9. Metrics
- **% Resolved.** The share of instances where the patch applies and every FAIL_TO_PASS and PASS_TO_PASS test passes (§2.2, A.4).
- **% Apply.** The share of generated patches that apply. This counts patches that applied only after the automatic repair step; Table 14 reports how many needed it.
- **BM25 recall vs oracle files** (Table 3). Reported three ways: Avg, All and Any.

## 10. Results (exact numbers)
- **Abstract.** "The best-performing model, Claude 2, is able to solve a mere 1.96% of the issues." This is stale against v3 Table 5 (see C1).
- **Table 5, BM25, full SWE-bench** (% Resolved / % Apply):

  | Model | % Resolved | % Apply |
  |---|---|---|
  | Claude 3 Opus | 3.79 | 46.56 |
  | Claude 2 | 1.97 | 43.07 |
  | ChatGPT-3.5 | 0.17 | 26.33 |
  | GPT-4-turbo | 1.31 | 26.90 |
  | SWE-Llama 7b | 0.70 | 51.74 |
  | SWE-Llama 13b | 0.70 | 53.62 |

- **Table 5, BM25, SWE-bench Lite:**

  | Model | % Resolved | % Apply |
  |---|---|---|
  | Claude 3 Opus | 4.33 | 51.67 |
  | Claude 2 | 3.00 | 33.00 |
  | ChatGPT-3.5 | 0.33 | 10.00 |
  | GPT-4-turbo | 2.67 | 29.67 |
  | SWE-Llama 7b | 1.33 | 38.00 |
  | SWE-Llama 13b | 1.00 | 38.00 |

- **Table 2, BM25 % Resolved by context limit:**

  | Model | 13k | 27k | 50k |
  |---|---|---|---|
  | Claude 2 | 1.96 | 1.87 | 1.22 |
  | SWE-Llama 7b | 0.70 | 0.31 | 0.00 |
  | SWE-Llama 13b | 0.70 | 0.48 | 0.00 |

- **Table 3, BM25 recall by context limit:**

  | Recall | 13k | 27k | 50k |
  |---|---|---|---|
  | Avg | 29.58 | 44.41 | 51.06 |
  | All | 26.09 | 39.83 | 45.90 |
  | Any | 34.77 | 51.27 | 58.38 |

  At 27k, BM25 retrieves a superset of the oracle files in about 40% of instances, and in "almost half" of instances it retrieves none of them (§4.1).
- **Table 18, "oracle"** (% Resolved / % Apply):

  | Model | % Resolved | % Apply |
  |---|---|---|
  | Claude 2 | 4.80 | 62.82 |
  | ChatGPT-3.5 | 0.52 | 21.80 |
  | GPT-4* (25% subset) | 1.74 | 34.00 |
  | SWE-Llama 7b | 3.01 | 65.52 |
  | SWE-Llama 13b | 3.97 | 66.78 |

  In counts, Claude 2 resolves 110 instances and SWE-Llama 13b resolves 91 (§5, Table 23).
- **Table 6, "oracle"-collapsed** (Resolved / Applied):

  | Model | Resolved | Applied |
  |---|---|---|
  | Claude 3 Opus | 9.39 | 48.00 |
  | Claude 2 | 5.93 | 68.18 |
  | GPT-4 (full set) | 3.40 | 48.65 |
  | ChatGPT-3.5 | 1.09 | 40.93 |

  - **Paired comparisons with Table 18.** Claude 2 rises from 4.80 to 5.93, and ChatGPT-3.5 from 0.52 to 1.09.
  - **GPT-4, as stated in the paper.** The text says "GPT-4 jumping from 1.3% to 3.4%". The 1.3 does not match GPT-4's Table 18 value of 1.74, and the before and after runs used different instance sets (see C2).
- **Table 7, oracle % Resolved, before / after 2023:**

  | Model | Before 2023 | After 2023 |
  |---|---|---|
  | Claude 2 | 4.87 | 4.23 |
  | ChatGPT-3.5 | 0.49 | 0.77 |
  | GPT-4* | 1.96 | 0.0 |
  | SWE-Llama 7b | 2.95 | 3.46 |
  | SWE-Llama 13b | 3.98 | 3.85 |

- **Whole-file vs patch generation** (§5). Claude 2 scores 2.2% when regenerating whole files vs 4.8% with patches (oracle). On the shorter half of instances by input tokens, the figures are 3.9% vs 7.8%.
- **Table 8, successfully applied patches, oracle.** Columns: Total lines / Added / Removed / Functions / Files.

  | Model | Model patch | Its gold patches |
  |---|---|---|
  | Claude 2 | 19.6 / 4.2 / 1.9 / 1.1 / 1.0 | 44.1 / 12.0 / 5.8 / 2.1 / 1.2 |
  | ChatGPT-3.5 | 30.1 / 3.8 / 2.7 / 1.6 / 1.0 | 39.6 / 9.5 / 6.1 / 1.9 / 1.2 |
  | GPT-4 | 20.9 / 4.4 / 1.5 / 1.0 / 1.0 | 33.6 / 8.4 / 3.8 / 1.9 / 1.1 |
  | SWE-Llama 13b | 17.6 / 1.6 / 1.2 / 1.2 / 1.1 | 37.8 / 10.0 / 4.4 / 1.9 / 1.1 |
  | SWE-Llama 7b | 16.7 / 1.3 / 1.2 / 1.2 / 1.1 | 40.2 / 11.3 / 4.9 / 1.9 / 1.1 |

  - Avg Gold is 39.1 / 10.2 / 5.0 / 1.9 / 1.1, and All Gold is 74.5 / 22.3 / 10.5 / 3.0 / 1.7. All Gold matches Table 1: 22.3 + 10.5 = 32.8 edited lines, 3.0 functions, 1.7 files.
  - The body text says model patches that apply are "less than half the total length (74.5 versus 30.1 lines)" of gold patches, and "rarely edit more than a single file".
  - **Caveat.** Across all patches (Table 24), SWE-Llama patches are longer than gold: 68.9 vs 61.5 for 13b, and 78.9 vs 65.1 for 7b.
- **Table 14, patch-fix rates.** Patches that needed the automatic fix generally make up a smaller share of SWE-Llama's applied patches (19.83–30.0%) than of the closed models' (24.98–69.41%). The two ranges overlap. The authors read this as a positive effect of fine-tuning on patch formatting (A.5).
- **Table 23, applied but unresolved patches.** Most do not pass a single F2P test (the "No-Op" and "Regression" categories). Within that group, 60–70% are No-Op (C.5).
- **Per repository** (Figure 4, §5):
  - In the oracle setting, Claude 2 resolves 110 instances and SWE-Llama 13b resolves 91, yet "Claude 2 only solves 42% of the instances solved by SWE-Llama".
  - 32% of matplotlib and 10% of seaborn instances embed images, compared with 2% of all instances.
- **Case study** (Figure 6, §5.1). In `sphinx-doc__sphinx-8713`, the input is 1,558 lines or 20,882 tokens. The model edits the correct function, but the change behaves as if `napoleon_use_param` were always True. Result: "2 failed, 45 passed, 8 warnings in 5.16s".
- **Dataset characterization** (Table 1, §2.3):
  - **Issue text.** Mean 195.1 words (max 4,477).
  - **Codebase.** Mean 3,010 non-test files (max 5,890) and 438K non-test lines (max 886K).
  - **Gold patch.** Mean 32.8 lines edited (max 5,888), 1.7 files (max 31) and 3 functions (max 36).
  - **Tests.** Mean 9.1 fail-to-pass tests (max 1,633) and 120.8 tests in total (max 9,459).
  - **Test coverage.** 40% of instances have at least two F2P tests, and there is a median of 51 additional P2P tests.
  - **Medians** (A.5). 140 words, "just shy of 1900 files and 400K lines", a single function edited, about 15 lines changed, 1 F2P test.

## 11. Supported claims (directly measured)
- SWE-bench contains 2,294 instances from 12 repositories (Abstract, Table 10).
- Claude 2 with BM25 resolves 1.96% (Abstract, Table 2) or 1.97% (Table 5).
- The highest full-set BM25 result is Claude 3 Opus at 3.79% (Table 5). The highest Lite result is Claude 3 Opus at 4.33%.
- Claude 2 with oracle retrieval resolves 4.80% (Table 18).
- SWE-Llama 7b and 13b resolve 0.70% each with BM25 (Table 5), against 3.01% and 3.97% with oracle retrieval (Table 18).
- 32% of matplotlib, 10% of seaborn and 2% of all instances contain images (§5).

## 12. Derived claims (computed or comparative)
- **Collapsed context helps where a baseline exists.** "Oracle"-collapsed beats full oracle context for the models that have both results: Claude 2 goes from 4.80 to 5.93 and ChatGPT-3.5 from 0.52 to 1.09. The paper states GPT-4 goes from 1.3 to 3.4, but see C2. Claude 3 Opus has no oracle baseline.
- **Patches beat whole files.** Generating patches outperforms regenerating whole files for Claude 2: 4.8 vs 2.2, and 7.8 vs 3.9 on the shorter half.
- **Model patches that apply are shorter than gold patches** (Table 8). Across all patches the gap disappears, and SWE-Llama patches are longer (Table 24).
- **Little change around 2023.** Resolve rates differ little before and after 2023 for most models, with GPT-4 the exception (Table 7). Table 21 shows "no consistent correlation" with year.

## 13. Interpretations (authors' explanations)
- **Why performance drops with more context.** Models are "simply ineffective at localizing problematic code" and become distracted by extra context (§5, citing Liu et al. 2023b). The underlying drop is an observation (Figure 5, Table 2); only the explanation is interpretation.
- **Why SWE-Llama does poorly with BM25.** It was fine-tuned on oracle context, and the authors "suspect this shift in context" hurts it (§5).
- **Style of model patches.** Models "tend to write primitive Python code" and take a "greedy" approach, whereas gold patches "anticipate and solve potential future issues" (§5.1). This is a qualitative reading of the selected examples.
- **Stable results over time.** The authors call this "largely promising" evidence that models are "unlikely to 'cheat'" by reproducing newer code (§5, C.4). This is an inference; memorization was not measured.
- **Summary judgement.** "Can resolve only the simplest issues" (Abstract) is the authors' summary.
- **Patch formatting.** Lower fix rates suggest that fine-tuning helps SWE-Llama produce well-formatted patches (A.5).

## 14. Hypotheses/speculation
- The authors hope to extend the collection procedure to more languages and domains (§7).
- They encourage future work on agent-based and tool-augmented approaches (§7).
- Execution feedback could help models (C.5).
- Software-engineering metrics could give richer evaluation signals (C.7, described as "preliminary").

## 15. Limitations
**Stated by the authors:**
- "SWE-bench task instances are all in Python" (§7).
- The experiments establish only "a baseline of the simplest and most straight-forward approaches" (§7).
- Execution-based testing alone "is insufficient to guarantee reliable performance", because LM code can be "less comprehensive, efficient, or readable" (§7).
- Oracle retrieval "is less realistic", and it is also "not necessarily comprehensive since edited files alone may not include all the required context" (§4.1).
- "Models with shorter context lengths are thus inherently disadvantaged" (Table 4 caption). Token lengths are also not directly comparable across tokenizers: Llama sequences are 42% longer.
- GPT-4 was evaluated on a 25% subset "which may impact performance" (Table 7 caption). This covers the oracle and BM25 27K settings only.
- Image-containing issues "may require multi-modal LMs or some kind of external tool use", and the initial baselines do not explore this (§5, Table 28 caption).
- The baselines have a "limited view of the codebase that does not include information such as inter-file dependencies" (C.5).

**Scope boundaries derived from stated conditions:**
- GPT-4 subset results are not instance-matched to the full-set results.
- Oracle-setting results do not reflect realistic deployment.

**Verifier/drafter notes (not stated by the authors, and not scoring content):**
- The §5.1 qualitative trends rest on 11 selected generations.
- The paper's Reproducibility Statement frames reproducibility as "our hope and belief"; no third-party reproduction is reported.

## 16. Actual contribution
1. SWE-bench: 2,294 real GitHub issue/PR tasks from 12 Python repositories, with execution-based evaluation and a collection process that can be continually updated.
2. SWE-bench-train: 19,000 pairs from 37 disjoint repositories.
3. SWE-Llama 7b and 13b.
4. An empirical baseline study showing current LMs resolve very few issues. The best full-set results are 3.79% with BM25 (Claude 3 Opus), 4.80% with oracle retrieval (Claude 2) and 9.39% with oracle-collapsed context (Claude 3 Opus). The abstract's own headline is Claude 2 at 1.96%.

## 17. Unsupported or weakly supported claims
- **"Best-performing model, Claude 2" (Abstract, §5).** Contradicted by Table 5 in the same version: Claude 3 Opus scores 3.79.
- **"GPT-4 jumping from 1.3% to 3.4%" (§5).** Does not match Table 18 (1.74), and the comparison crosses the subset and the full set.
- **Qualitative "greedy"/"primitive" code trends (§5.1).** Supported only by a small set of selected examples.
- **"SWE-bench should be highly reproducible" (§9).** Stated as a hope; no reproduction result is reported.

## 18. Claim → evidence → source table
| Claim | Type | Snapshot location | Quote (≤25 words) |
|---|---|---|---|
| 2,294 instances from 12 repos | measured | Abstract, Table 10 | "2,294 software engineering problems drawn from real GitHub issues and corresponding pull requests across 12 popular Python repositories" |
| Claude 2 BM25 1.96% (Table 5: 1.97) | measured | Abstract, Table 2, Table 5 | "Using a BM25 retriever, Claude 2 is only able to resolve 1.96% of the issues." |
| Claude 3 Opus BM25 3.79% (highest) | measured | Table 5 | "Claude 3 Opus ... 3.79 46.56" |
| Claude 2 oracle 4.80% | measured | §5, Table 18 | "Claude 2 is able to resolve 4.8% of issues using the 'oracle' retriever" |
| Claude 2 oracle-collapsed 5.93% | measured/derived | Table 6, §5 | "Claude 2 from 4.8% to 5.9%" |
| GPT-4 1.3%→3.4% (inconsistent with Table 18) | derived, flagged | §5, Table 18, Table 14 | "GPT-4 jumping from 1.3% to 3.4%" |
| ~90K PRs → 2,294 | measured | §2.1, Table 10 | "the original 90,000 PRs are filtered down to the 2,294 task instances" |
| Gold patches edit 1.7 files, 3.0 functions, 32.8 lines | measured | §2.3, Table 1 | "average editing 1.7 files, 3.0 functions, and 32.8 lines (added or removed)" |
| Applied model patches shorter than gold | observed | §5, Table 8 (qualified by Table 24) | "less than half the total length (74.5 versus 30.1 lines)" |
| Performance drops with context length | observed | §5, Figure 5, Table 2 | "as total context length increases, Claude 2's performance drops considerably" |
| Failure to localize code explains the drop | interpretation | §5 | "models are simply ineffective at localizing problematic code" |
| Models write primitive, greedy code | interpretation | §5.1 | "Models tend to write primitive Python code" |
| Python only | stated limitation | §7 | "SWE-bench task instances are all in Python" |
| GPT-4 on 25% subset (oracle, BM25 27K only) | stated scope | Table 7, 18 captions | "GPT-4 is evaluated on a 25% random subset of SWE-bench tasks, which may impact performance" |
| Lite: 300 instances, 11 repos | measured | paper §2.4 (A.7 and part of §2.4 truncated) | "a Lite subset of 300 instances from SWE-bench" |
| Lite full filtering criteria | gap | A.7 | NOT IN SNAPSHOT |
| Docker-based `swebench` CLI harness | README-only artifact fact | README | "We're moving to a fully containerized evaluation harness using Docker" |
| SWE-bench Verified (500) | README-only artifact fact, post-paper | README | "A subset of 500 problems that real software engineers have confirmed are solvable" |
| ICLR 2024 | bibliographic | paper line 1; "Oral" from README only | "Published as a conference paper at ICLR 2024" |

## Conflict log
**Paper vs README:**
- **R1. Harness.** The paper uses conda environments per release version (A.3). The README uses a Docker-based `swebench` v5 CLI, introduced in a Jun 27, 2024 news item. The paper is authoritative for the study; the README only for the current artifact.
- **R2. Datasets.** The README's Verified, Multimodal and Multilingual datasets are artifact facts and are not attributed to the paper.
- **R3. Venue.** "Oral" comes from the README only. The venue itself (ICLR 2024) is consistent across both sources.

**Inside the paper** (table values preferred; nothing is resolved by guessing):
- **C1. Best BM25 model.** The Abstract, §1 and §5 say Claude 2 (1.96%). Table 5 shows Claude 3 Opus at 3.79%, and Claude 2 at 1.97% rather than 1.96%.
- **C2. GPT-4 oracle.** The §5 text says 1.3%, but Table 18 gives 1.74 on the subset. The collapsed run (3.40) used the full set.
- **C3. GPT-4 naming.** §4.3 names gpt-4-32k-0613, while Table 5 labels the row "GPT-4-turbo" (1.31 / 26.90).
- **C4. GPT-4 BM25 on the subset.** Table 20 gives 0.00 / 14.82, consistent with Table 14 (85/574 applied), and marks it as a "−0.00" difference from Table 5, which is incompatible with Table 5's 1.31 / 26.90. Table 20's other subscripts also appear to refer to pre-v3 Table 5 values; for example, Claude 2 is shown as 2.27 ↑0.31, implying a base of 1.96. This cannot be reconciled from the snapshot.
