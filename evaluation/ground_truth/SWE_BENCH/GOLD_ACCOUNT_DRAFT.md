# Gold Account Draft — SWE_BENCH

Source basis: `evaluation/external_projects/SWE_BENCH/snapshot/paper.txt` (arXiv:2310.06770v3, ICLR 2024) and `evaluation/external_projects/SWE_BENCH/snapshot/README__SWE-bench__SWE-bench.md` (repo commit `02e7a74`). Paper is authoritative for research claims; README is used only for artifact/tooling facts, and conflicts are flagged explicitly.

## 1. Problem
Existing benchmarks used to evaluate language models (LMs) have become saturated and fail to capture the frontier of what state-of-the-art LMs can and cannot do (paper §1, citing Kiela et al. 2021, Ott et al. 2022). Traditional coding benchmarks like HumanEval mostly involve "self-contained problems that can be solved in a few lines of code" (paper §1), which does not reflect the complexity of real-world software engineering, where "fixing a bug might involve navigating a large repository, understanding the interplay between functions in different files, or spotting a small error in convoluted code" (paper §1).

## 2. Motivation
"Language models have outpaced our ability to evaluate them effectively, but for their future development it is essential to study the frontier of their capabilities" (paper Abstract). The authors state real-world software engineering is "a rich, sustainable, and challenging testbed for evaluating the next generation of language models" (paper Abstract). A good benchmark must be "challenging enough to stump existing models, but model predictions must also be easy to verify" (paper §1, citing Martínez-Plumed et al. 2021); coding tasks fit this because solutions can be automatically verified via unit tests (paper §1).

## 3. Research gap
Existing LM programming benchmarks (e.g., HumanEval) involve short, self-contained problems, not realistic repository-scale editing. Existing "potpourri"-style multi-task benchmark collections (paper §6, Related Work) "narrowly focus on one or a few skills, resulting in challenges that are typically too simple, pigeonhole the model into a reduced role" (paper §6). No prior automated-program-repair dataset "present[s] code context at the scale of SWE-bench" (paper §6).

## 4. Research question/objective
To introduce and evaluate "SWE-bench, an evaluation framework consisting of 2,294 software engineering problems drawn from real GitHub issues and corresponding pull requests across 12 popular Python repositories" (paper Abstract), and to measure how well current LMs (proprietary and fine-tuned open models) can resolve such real-world issues (paper §1, §4, §5).

## 5. System/method
Three-stage construction pipeline (paper §2.1, Figure 2, elaborated Appendix A.1–A.3):
1. **Stage I — Repo selection and data scraping**: Collect PRs from 12 popular open-source Python repositories (~90,000 PRs total per running text; Table 10 gives 93,139 PRs crawled in total across the 12 repos).
2. **Stage II — Attribute-based filtering**: Keep merged PRs that (1) resolve a GitHub issue and (2) modify test files (indicating the contributor added tests).
3. **Stage III — Execution-based filtering**: Apply the PR's test content, run tests before/after the PR, and keep only instances with at least one "fail-to-pass" test and no install/runtime errors.
Task formulation (paper §2.2): the model receives an issue description and a codebase, and must output a patch file; the patch is applied with the Unix `patch` program and scored by whether the associated tests pass (paper §2.2).
Two retrieval-based context-selection approaches were evaluated as baselines (paper §4.1): BM25 sparse retrieval (Robertson et al. 2009) at three context limits (13k/27k/50k tokens), and an "oracle" retrieval setting that uses exactly the files edited by the reference PR.
SWE-Llama fine-tuning (paper §3): CodeLlama-Python 7b/13b fine-tuned via LoRA (Hu et al. 2022) on 19,000 collected issue-PR pairs from 37 additional repositories (SWE-bench-train), reduced to 10,000 instances after excluding sequences >30,000 tokens.

## 6. Architecture
SWE-bench itself is a benchmark/dataset-and-evaluation-harness, not a model architecture. Its "architecture" is the task-instance data schema (Table 9: base_commit, created_at, hints_text, instance_id, issue_numbers, patch, problem_statement, pull_number, test_patch, version, repo, FAIL_TO_PASS, PASS_TO_PASS, environment_setup_commit) plus the execution-based validation/evaluation pipeline (Appendix A.3–A.4, Figures 7–8): checkout base commit → install codebase → apply test patch → run tests (pre) → apply solution patch → run tests (post) → compare fail-to-pass/pass-to-pass status.
SWE-Llama models are CodeLlama-Python 7b/13b base models fine-tuned with LoRA (r=16, α=16, dropout=0.05) on query/key/value/output projection matrices of every attention sublayer (Appendix B.1), using DeepSpeed Ulysses and FlashAttention for long-context training.

## 7. Dataset/data
- **SWE-bench (main/evaluation)**: 2,294 task instances, 12 repositories (astropy, django, flask, matplotlib, pylint, pytest, requests, scikit-learn, seaborn, sphinx, sympy, xarray) (paper §2.1, Figure 3, Table 10).
- **SWE-bench-train**: 19,000 non-testing task instances, 37 repositories disjoint from the evaluation set (paper §1, §3).
- **SWE-bench Lite**: 300 instances, 11 of the 12 repositories, "sampled to be more self-contained, with a focus on evaluating functional bug fixes" (paper §2.4). Full filtering criteria referenced as "Appendix A.7" are **NOT IN SNAPSHOT** — the appendix section is truncated by pdftotext extraction after one incomplete sentence.
- **Development set**: 225 instances, 6 repositories (astroid, marshmallow, pvlib, pydicom, pyvista, sqlfluff), filtered to PRs created after Jan 1, 2019 (Appendix A.6).
- Per-repository PR funnel (Table 10): e.g. django 16,914 PRs crawled → 2,880 post-conversion → 850 post-validation (final); sympy 11,928 → 1,897 → 386; overall 93,139 → 11,407 → 2,294.
- README-only (artifact fact, post-paper): dataset accessible via `datasets.load_dataset('princeton-nlp/SWE-bench', split='test')`; additional datasets SWE-bench Verified (500 instances), SWE-bench Multimodal, SWE-bench Multilingual are listed in the README download table but are **not described or evaluated in this paper version** and must not be attributed to it.

## 8. Experimental setup
- Models evaluated (paper §4.3, Table 4): ChatGPT-3.5 (gpt-3.5-turbo-16k-0613, 16,385 max tokens), GPT-4 (gpt-4-32k-0613, 32,768 max tokens), Claude 2 (100,000 max tokens), Claude 3 Opus, SWE-Llama 7b/13b (≥100,000 max tokens).
- Two retrieval settings: BM25 (13k/27k/50k token limits) and "oracle" (files edited by the reference PR) (paper §4.1).
- An "oracle-collapsed" ablation collapses retrieved-but-unedited code, keeping only lines edited by the true PR ±15 lines buffer (paper §5, Table 6).
- GPT-4 was evaluated on only a 25% random subset (574 instances) of SWE-bench "due to budget constraints" (Table 5 footnote, Table 20 caption).
- Qualitative analysis: 11 generations from SWE-Llama and Claude 2 manually inspected under "oracle" retrieval (paper §5.1).

## 9. Metrics
- **% Resolved**: percentage of task instances where the applied patch causes all FAIL_TO_PASS and PASS_TO_PASS tests to pass (paper §2.2, Appendix A.4).
- **% Apply**: percentage of generated patches that apply successfully to the codebase (Table 5 and others).
- BM25 Recall (Table 3): "Avg", "All", "Any" recall of oracle files by BM25 retrieval at given context limits.

## 10. Results (exact numbers, with table/section)
- Headline (Abstract): "The best-performing model, Claude 2, is able to solve a mere 1.96% of the issues."
- Table 5 (BM25 retrieval, full SWE-bench, % Resolved / % Apply): Claude 3 Opus 3.79 / 46.56; Claude 2 1.97 / 43.07; ChatGPT-3.5 0.17 / 26.33; GPT-4-turbo 1.31 / 26.90; SWE-Llama 7b 0.70 / 51.74; SWE-Llama 13b 0.70 / 53.62.
- Table 5 (BM25 retrieval, SWE-bench Lite, % Resolved / % Apply): Claude 3 Opus 4.33 / 51.67; Claude 2 3.00 / 33.00; ChatGPT-3.5 0.33 / 10.00; GPT-4-turbo 2.67 / 29.67; SWE-Llama 7b 1.33 / 38.00; SWE-Llama 13b 1.00 / 38.00.
- Table 2 (BM25 retrieval, resolve rate by max context, full set): Claude 2 — 13k: 1.96, 27k: 1.87, 50k: 1.22; SWE-Llama 7b — 13k: 0.70, 27k: 0.31, 50k: 0.00; SWE-Llama 13b — 13k: 0.70, 27k: 0.48, 50k: 0.00.
- Table 3 (BM25 recall vs. oracle files, by context limit): Avg — 13k: 29.58, 27k: 44.41, 50k: 51.06; All — 13k: 26.09, 27k: 39.83, 50k: 45.90; Any — 13k: 34.77, 27k: 51.27, 50k: 58.38.
- Table 18 (Appendix, "oracle" retrieval, full set, % Resolved / % Apply): Claude 2 4.80 / 62.82; ChatGPT-3.5 0.52 / 21.80; GPT-4* 1.74 / 34.00 (*25% subset); SWE-Llama 7b 3.01 / 65.52; SWE-Llama 13b 3.97 / 66.78. Paper §5 body text states: "Claude 2 is able to resolve 4.8% of issues using the 'oracle' retriever."
- Table 6 ("oracle"-collapsed, % Resolved / % Apply): Claude 3 Opus 9.39 / 48.00; Claude 2 5.93 / 68.18; GPT-4 3.40 / 48.65; ChatGPT-3.5 1.09 / 40.93. Body text (§5): "GPT-4 jumping from 1.3% to 3.4% and Claude 2 from 4.8% to 5.9%" (oracle → oracle-collapsed).
- Table 7 (oracle retrieval, % Resolved, before/after 2023): Claude 2: 4.87 (before) / 4.23 (after); ChatGPT-3.5: 0.49 / 0.77; GPT-4*: 1.96 / 0.0; SWE-Llama 7b: 2.95 / 3.46; SWE-Llama 13b: 3.98 / 3.85.
- Regenerate-whole-file ablation (§5 body text): "Claude 2 scores at 2.2% compared to 4.8% in the main table for 'oracle' retrieval [when regenerating whole files vs. patches]." On the shorter half of instances by input tokens: "3.9% compared to 7.8% for generating patches with Claude 2."
- Table 8 (avg lines edited, oracle retrieval, successfully-applied patches): Claude 2 generated total lines 19.6 (added 4.2? — NOTE: extraction of this table is column-ambiguous; the raw text interleaves "Total / Added / Removed / Functions / Files" values for model vs. gold rows without a clean grid; treated as low-confidence and given only as: gold patches are described in body text as "less than half the total length (74.5 versus 30.1 lines) of gold edit patch files" comparing "All Gold" avg (74.5) vs. an average model-generated applied patch (30.1 lines), per §5 body text "Language models tend to generate shorter, simpler edits").
- Repository-level qualitative case study (§5.1, Figure 6): task instance `sphinx-doc__sphinx-8713`; model input "1,558 lines of context or 20,882 tokens"; model edits the correct function but the fix is incorrect (behaves as if `napoleon_use_param` were always True); test run result shown: "2 failed, 45 passed, 8 warnings in 5.16s".
- Cross-repository performance differs (Figure 4, described qualitatively in §5): "in the 'oracle' setting Claude 2 and SWE-Llama 13b perform comparably, with each model resolving 110 and 91 instances respectively. Yet of these instances, Claude 2 only solves 42% of the instances solved by SWE-Llama."
- Image-containing issues (§5): "32% of matplotlib and 10% of seaborn instances contain embedded images in their issue text compared to just 2% of all instances."
- Dataset characterization numbers (Table 1 / §2.3): issue text mean 195.1 words (max 4,477); codebase mean 3,010 non-test files (max 5,890), mean 438K non-test lines (max 886K); gold patch mean 32.8 lines edited (max 5,888), 1.7 files edited (max 31), 3 functions edited (max 36); mean 9.1 fail-to-pass tests (max 1,633), mean 120.8 total tests (max 9,459). Body text (§2.3) restates: "SWE-bench's reference solutions average editing 1.7 files, 3.0 functions, and 32.8 lines (added or removed)."
- "40% of instances have at least two fail-to-pass tests" and "a median of 51 additional [pass-to-pass] tests run" (§2.3).
- Median dataset attributes (Appendix A.5, Figure 9 description): "median SWE-bench task instance has a problem description of 140 words, and will take place within a codebase containing just shy of 1900 files and 400K lines."

## 11. Supported claims (directly measured/observed)
- Claude 2 resolves 1.96% of SWE-bench issues under BM25 13k retrieval (Table 5/Table 2, directly measured).
- Claude 2 resolves 4.80% under "oracle" retrieval (Table 18, directly measured).
- All evaluated proprietary and fine-tuned models perform far below 100%, with the best full-set BM25 result being Claude 3 Opus at 3.79% (Table 5, directly measured).
- SWE-Llama 13b and 7b, fine-tuned on oracle-style context, perform poorly (≤0.70% resolved) when given BM25-retrieved context instead (Table 5, directly measured).
- 32% of matplotlib issues and 10% of seaborn issues contain embedded images vs. 2% of all instances (§5, directly measured/observed statistic).

## 12. Derived claims (computed/comparative)
- "Oracle"-collapsed context improves resolve rate relative to full "oracle" context for all four models tested (GPT-4 1.3%→3.4%, Claude 2 4.8%→5.9%) — a computed comparison across two experimental settings (Table 6 vs. Table 18/body text).
- Generating whole files performs worse than generating patches for Claude 2 (2.2% vs. 4.8% oracle; 3.9% vs. 7.8% on shorter-input subset) — a derived, controlled comparison (§5 body text).
- Model-generated patches are shorter than gold patches ("less than half the total length (74.5 versus 30.1 lines)") — a derived comparison across generated vs. reference patch statistics (§5 body text, Table 8).
- Difficulty does not correlate strongly with issue year (Table 7) — a derived interpretation-adjacent comparative claim across the before/after-2023 partition.

## 13. Interpretations (authors' explanations — label as interpretation)
- INTERPRETATION: "models perform best on the shortest context window" and are "simply ineffective at localizing problematic code" as context grows (§5), offered as an explanation for the observed drop in performance with longer context (cites Liu et al. 2023b, "Lost in the middle").
- INTERPRETATION: The finetuned SWE-Llama models' poor BM25 performance is attributed to "a shift in context" between training (oracle-only) and BM25 evaluation distributions (§5, "Finetuned models are sensitive to context distribution shifts").
- INTERPRETATION: Authors state models "tend to write primitive Python code and do not leverage existing third-party libraries or the rest of the codebase," reflecting a "greedy" problem-solving approach, based on manual inspection of "all the examples we consider" (§5.1) — this is an authors' qualitative interpretation from a small (11-generation) manual sample, not a broad quantitative measurement.
- INTERPRETATION: Authors state (§5) that stable performance before/after 2023 is "largely promising" evidence models are "unlikely to 'cheat'" via memorized recent code — an inferential claim from the before/after comparison, not a direct measurement of memorization.

## 14. Hypotheses/speculation
- SPECULATION/future direction: Authors "hope to apply SWE-bench's task instance collection procedure to expand its coverage to more programming languages and domains" (§7, Discussion — stated as a limitation-driven future direction, not a finding).
- SPECULATION: Authors state they "do not intend to constrain future methodologies to the same type of approach and encourage future work to investigate different methods (e.g., agent-based approaches, tool augmented LMs)" (§7) — an explicit forward-looking suggestion, not a result.

## 15. Limitations (only author-stated, or scope boundaries derived from stated conditions)
- STATED LIMITATION: "SWE-bench task instances are all in Python" (§7, Discussion, "Limitations and future directions").
- STATED LIMITATION: The paper's baseline experiments "aim to establish a baseline of the simplest and most straight-forward approaches for this task" and do not represent an exhaustive exploration of methods (§7).
- STATED LIMITATION: "relying solely on this [execution-based testing] method is insufficient to guarantee reliable performance of model generations, as we find automated code generations from LMs can frequently be less comprehensive, efficient, or readable compared to human-written solutions" (§7).
- SCOPE BOUNDARY (derived from stated conditions): Because GPT-4 was evaluated "on a 25% random subset of SWE-bench tasks... due to budget constraints" (Table 5 footnote, Table 7 footnote), GPT-4 results in Tables 5, 7, 14, 18, 20 are not directly comparable on identical instance sets to the other models' full-set results without accounting for this subsetting.
- SCOPE BOUNDARY (derived from stated conditions): Because "oracle" retrieval "'retrieve[s]' the files edited by the reference patch that solved the issue on GitHub," which the authors describe as "less realistic, since an engineer working on addressing an issue may not know a priori which files need to be modified" (§4.1), oracle-retrieval results should not be read as reflecting realistic deployment conditions.
- SCOPE BOUNDARY (derived from stated conditions): The qualitative "greedy code" and "primitive Python" observations (§5.1) are drawn from only "11 generations from SWE-Llama and Claude 2," an explicitly small hand-selected sample, so they do not carry the statistical weight of the main quantitative results.

## 16. Actual contribution
As stated by the authors (§1, restated in Reproducibility Statement §9 and README): (1) SWE-bench itself — a 2,294-instance benchmark of real GitHub issues/PRs across 12 Python repositories with an execution-based evaluation framework; (2) SWE-bench-train, a 19,000-instance training dataset from 37 disjoint repositories; (3) SWE-Llama 7b and 13b, two fine-tuned CodeLlama-based models released as open baselines; (4) an empirical evaluation showing current LMs (as of paper writing) resolve only a small fraction of issues, with the best model (Claude 2, BM25) at 1.96%.

## 17. Unsupported or weakly supported claims
- The claim (§5.1) that models generally exhibit a "greedy" problem-solving approach and gold patches "anticipate and solve potential future issues" is based on manual inspection of only 11 generations — thin support relative to the 2,294-instance dataset; the paper itself does not claim this generalizes quantitatively beyond the qualitative sample.
- The claim that "SWE-bench should be highly reproducible" (Reproducibility Statement, §9) is an assertion about the *submitted* anonymized codebase's design, not an independently verified reproduction result within the paper itself — no reproduction-by-a-third-party is reported in the snapshot.
- The Table 8 per-model "Total/Added/Removed/Functions/Files" breakdown of average edit statistics is present in the extracted text but the row-to-column alignment is ambiguous after pdftotext extraction (numbers appear as an unstructured sequence per model without clear header-to-value mapping); only the two clearly stated body-text figures (74.5 vs. 30.1 total lines) are treated as reliable — the rest of Table 8's granular breakdown is not confidently usable as stated numeric evidence.

## 18. Claim → evidence → source table

| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| SWE-bench has 2,294 task instances from 12 repos | measured | dataset construction result | paper.txt Abstract | "2,294 software engineering problems... across 12 popular Python repositories" |
| Claude 2 resolves 1.96% under BM25 | measured | Table 5 / Abstract | paper.txt Abstract, Table 5 | "the best-performing model, Claude 2, is able to solve a mere 1.96% of the issues" |
| Claude 2 resolves 4.80% under oracle retrieval | measured | Table 18 / §5 body | paper.txt §5, Table 18 | "Claude 2 is able to resolve 4.8% of issues using the 'oracle' retriever" |
| Oracle-collapsed improves GPT-4 1.3%→3.4%, Claude 2 4.8%→5.9% | derived | Table 6 vs Table 18 comparison | paper.txt §5 | "GPT-4 jumping from 1.3% to 3.4% and Claude 2 from 4.8% to 5.9%" |
| 90K PRs filtered to 2,294 instances | measured | Table 10, §2.1 | paper.txt §2.1, Table 10 | "the original 90,000 PRs are filtered down to the 2,294 task instances" |
| Gold patches avg edit 1.7 files, 3.0 functions, 32.8 lines | measured | §2.3, Table 1 | paper.txt §2.3 | "average editing 1.7 files, 3.0 functions, and 32.8 lines (added or removed)" |
| SWE-Llama trained via LoRA on CodeLlama-Python | measured | §3, Appendix B.1 | paper.txt Appendix B.1 | "finetune using LoRA... on the query, key, value, and output projection matrices" |
| Context length increase reduces model performance | interpretation | §5 discussion, Figure 5 | paper.txt §5 | "Claude 2's performance drops considerably... behavior that is also observed in other models" |
| Models write "primitive" code, greedy solutions | interpretation | §5.1 qualitative analysis (11 samples) | paper.txt §5.1 | "Models tend to write primitive Python code and do not leverage existing third-party libraries" |
| Benchmark limited to Python | stated limitation | §7 Discussion | paper.txt §7 | "SWE-bench task instances are all in Python" |
| GPT-4 evaluated on 25% random subset | scope boundary | Table 5 footnote | paper.txt Table 5 footnote / §5 note | "GPT-4 is evaluated on a 25% random subset of SWE-bench tasks" |
| SWE-bench Lite has 300 instances, 11 repos | measured (README-partial) | §2.4; Appendix A.7 truncated | paper.txt §2.4 | "a Lite subset of 300 instances from SWE-bench... covers 11 of the original 12 repositories" |
| SWE-bench Lite full filtering criteria | gap | Appendix A.7 truncated by extraction | paper.txt Appendix A.7 | NOT IN SNAPSHOT (section cuts off mid-sentence) |
| Repo now uses Docker-based harness with `swebench` CLI | README-only artifact fact | README, conflicts with paper's conda-based Appendix A.3/A.4 | README__SWE-bench__SWE-bench.md | "We're moving to a fully containerized evaluation harness using Docker" |
| SWE-bench Verified (500 instances) exists | README-only artifact fact, post-paper | README news item, Aug 13 2024 | README__SWE-bench__SWE-bench.md | "Introducing SWE-bench Verified! ... A subset of 500 problems... real software engineers have confirmed are solvable" |
| Paper published at ICLR 2024 (oral) | measured (bibliographic) | paper header + README citation block | paper.txt line 1; README citation | "Published as a conference paper at ICLR 2024" |

## Conflict log (paper vs. README)
1. **Evaluation harness**: Paper describes conda-env, repository-version-based executable contexts (Appendix A.3). README (current) describes a Docker-containerized harness with a `swebench` CLI, explicitly noting this is a later migration ("We're moving to a fully containerized evaluation harness using Docker," dated Jun 27, 2024 news item — after the paper's initial ICLR 2024 acceptance). **Paper is authoritative for what was done in the study; README is authoritative only for the current state of the artifact.**
2. **Dataset scope**: Paper describes SWE-bench (2,294), SWE-bench-train (19,000), SWE-bench Lite (300), and the 225-instance dev set. README additionally lists SWE-bench Verified (500), SWE-bench Multimodal, and SWE-bench Multilingual, none of which are described or evaluated in this pinned paper version (v3). **These README-only datasets are recorded as artifact facts and excluded from any statement of "what the paper evaluated."**
3. **Citation/venue**: Both paper header ("Published as a conference paper at ICLR 2024") and README ("[ICLR 2024 Oral]", OpenReview link) agree — no conflict here, cross-corroborating evidence.
