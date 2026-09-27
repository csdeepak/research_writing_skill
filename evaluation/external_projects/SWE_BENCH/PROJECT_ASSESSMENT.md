# Project Assessment — SWE_BENCH

## Project description
SWE-bench is an evaluation benchmark/framework consisting of 2,294 software engineering task instances drawn from real GitHub issues and their corresponding merged pull requests, sourced from 12 popular Python repositories. Given an issue description and a codebase snapshot, a language model must generate a patch that resolves the issue; success is measured by running the repository's own test suite (`paper.txt` Abstract, §2).

## Official repository
- URL: https://github.com/SWE-bench/SWE-bench
- Pinned commit (per `evaluation/manifests/source_snapshots.json`): `02e7a74ffd0b707aab73d203fe87bdc7c76afc8e`
- README snapshot file: `README__SWE-bench__SWE-bench.md`, README path in repo: `README.md`

## Paper/report
- arXiv id: 2310.06770, version pinned: v3 (per manifest; paper header text itself reads "arXiv:2310.06770v3 [cs.CL] 11 Nov 2024" — matches manifest)
- Title: "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?"
- Venue/peer-review status: header states "Published as a conference paper at ICLR 2024" (paper.txt line 1). The README (snapshot) independently corroborates: "[ICLR 2024 Oral]" and links an OpenReview forum entry (`https://openreview.net/forum?id=VTF8yNQM66`). The paper's own Reproducibility Statement (§9) also references anonymized submission materials consistent with a conference review process. I did not perform a live web search beyond reading the snapshot; the README's own citation block (BibTeX) states: "booktitle={The Twelfth International Conference on Learning Representations}, year={2024}". This is treated as authoritative evidence of peer-reviewed conference publication (ICLR 2024), sourced from the snapshot itself, so no external web search was necessary for this fact.
- Authors: Carlos E. Jimenez, John Yang, Alexander Wettig, Shunyu Yao, Kexin Pei, Ofir Press, Karthik Narasimhan (Princeton University / Princeton Language and Intelligence; Kexin Pei at University of Chicago).

## Datasets
- **SWE-bench (main)**: 2,294 task instances from 12 repositories (astropy, django, flask, matplotlib, pylint, pytest, requests, scikit-learn, seaborn, sphinx, sympy, xarray), constructed via a 3-stage filter from ~90,000 (paper text: "∼90,000"; Table 10 gives a more precise "93,139" total PRs crawled) scraped PRs. Downloadable at HuggingFace `princeton-nlp/SWE-bench` per README snapshot (also loadable via `datasets.load_dataset('princeton-nlp/SWE-bench', split='test')` per README).
- **SWE-bench-train**: 19,000 non-testing task instances from 37 additional (disjoint) repositories, used for SWE-Llama fine-tuning (paper §1, §3).
- **SWE-bench Lite**: 300-instance subset, 11 of the 12 repositories, "sampled to be more self-contained, with a focus on evaluating functional bug fixes" (paper §2.4). NOTE: Appendix A.7 ("SWE-BENCH LITE CHARACTERIZATION") is truncated/garbled by pdftotext extraction — the section header appears followed by one incomplete sentence ("SWE-bench Lite is a canonical subset for more efficient evaluation of languag models on the SWEbench task. SWE-bench is") that cuts off mid-sentence directly into Appendix B, so the full Lite filtering criteria referenced in §2.4 ("Full details of the Lite split and filtering details are included in Appendix A.7") are NOT recoverable from this snapshot.
- **Development set**: 225 instances from 6 additional repositories (astroid, marshmallow, pvlib, pydicom, pyvista, sqlfluff), filtered to instances created after Jan 1, 2019 (Appendix A.6, Table 15).
- README (current, post-paper) lists additional datasets not described in the paper: **SWE-bench Verified** (500 instances, per README news item dated Aug 13, 2024 — after the paper's version), **SWE-bench Multimodal** (per README, a separate ICLR 2025 paper, arXiv:2410.03859), and **SWE-bench Multilingual** (per README, cites a separate arXiv:2504.21798 work). These are REPO/ARTIFACT facts only — they postdate and are not described in the pinned paper (v3, Nov 2024) and must not be attributed to it.

## Benchmark/evaluation material
- Evaluation metric: "% Resolved" (percentage of task instances where the applied patch causes all FAIL_TO_PASS and PASS_TO_PASS tests to pass) and "% Apply" (percentage where the generated patch applies successfully) (paper §2.2, §5, Appendix A.4).
- Task instance schema documented in Table 9 (fields: base_commit, created_at, hints_text, instance_id, issue_numbers, patch, problem_statement, pull_number, test_patch, version, repo, FAIL_TO_PASS, PASS_TO_PASS, environment_setup_commit).
- README (current) describes a `swebench` CLI (`swebench eval`, `swebench infer`, `swebench images`, `swebench report`, `swebench submit`) built on Docker containers. This is a substantially different, later evaluation harness than what the paper describes (paper's Appendix A.3/A.4 describe conda-env-based validation, not Docker). README itself flags this shift: "[Jun. 27, 2024]: ... We're moving to a fully containerized evaluation harness using Docker for more reproducible evaluations!" — i.e., the artifact evolved after the paper was written. This is a README-only (artifact) fact, not a paper claim.

## Available experimental evidence
The paper reports its own experiments (not merely described features): BM25-retrieval and "oracle"-retrieval evaluations of ChatGPT-3.5, GPT-4, Claude 2, Claude 3 Opus, SWE-Llama 7b/13b across multiple context-length settings (Tables 2–8, 14, 18–23), a qualitative analysis of 11 hand-inspected generations (§5.1), and SWE-Llama fine-tuning details (§3, Appendix B). These are clearly labeled as experiments the authors ran themselves, distinguishable from README-described tooling that has no associated paper-reported experiment (e.g., the newer Docker harness, SWE-agent, sb-cli).

## Available result evidence
Numeric results are present directly in the paper text as tables (Tables 2–8, 10, 11, 14, 17–23) reproduced (with OCR/layout noise in places — see Risks) in `paper.txt`. Headline result: "The best-performing model, Claude 2, is able to solve a mere 1.96% of the issues" (Abstract) using BM25 retrieval on the full SWE-bench set (Table 5).

## Source quality: authoritative vs secondary
- Paper (`paper.txt`, pdftotext extraction of arXiv:2310.06770v3, ICLR 2024): **authoritative for research claims, method, experiments, and results.**
- README (`README__SWE-bench__SWE-bench.md`, pinned repo commit): **authoritative for current artifact/tooling facts only** (how to install, current CLI commands, current dataset download links, current model/dataset zoo). The README is dated well after the paper (it contains news items through "Sep. 1, 2026") and describes later work (SWE-bench Verified, Multimodal, Multilingual, SWE-agent, sb-cli, Docker harness, v5 CLI) that the pinned paper version does not mention. Per task rules, the paper is authoritative for research claims and the README is used only for artifact facts, with conflicts recorded explicitly (see GOLD_ACCOUNT_DRAFT §15/§17 and the claim table).

## Reproducibility/accessibility
- Paper's own Reproducibility Statement (§9) claims the anonymized submission included the full source code, organized by contribution, with inline documentation, and the full set of 2,294 task instances.
- README documents public dataset downloads (HuggingFace) and model weight downloads (SWE-Llama 7b/13b, plus PEFT variants) and installable pip package `swebench`.
- Caveat: because the current repo/README reflects a much later, reorganized codebase (Docker-based harness, new CLI, new datasets) than what existed at paper-writing time, a literal attempt to reproduce the paper's exact conda-based validation/evaluation pipeline as described in Appendix A.3/A.4 may not directly correspond to the current tooling in the pinned README.

## Suitability for this evaluation
- **Can methodology be reconstructed?** Yes, in detail — the 3-stage construction pipeline (Stage I scraping, Stage II attribute filtering, Stage III execution filtering; §2.1, elaborated in Appendix A.1–A.4) and the evaluation procedure (Appendix A.4, Figure 8) are both described with enough procedural detail to reconstruct.
- **Are experiments & results identifiable?** Yes — results are cleanly tabulated (Tables 2–8, 18–23) with associated model names, retrieval settings, and metrics.
- **Can a factual Gold Account be written without guessing?** Yes for the vast majority of content. One clear gap: Appendix A.7 (SWE-bench Lite's full filtering criteria) is truncated by extraction damage, so Lite's exact construction criteria beyond the one-sentence summary in §2.4 are NOT IN SNAPSHOT (recorded as such, not guessed).

## Risks
- **Repo diverged substantially from paper.** The pinned README reflects a 2024–2026 evolution of the project (Docker-based harness, `swebench` CLI, SWE-bench Verified/Multimodal/Multilingual, SWE-agent, sb-cli, SWE-smith) well beyond the ICLR 2024 paper's scope. Any README-only claim must be kept clearly separated from paper claims.
- **Results later superseded/extended.** SWE-bench Verified (500 "confirmed solvable" instances, released with OpenAI Preparedness per README) post-dates and is not evaluated in the paper; using SWE-bench Verified numbers to describe "the paper's results" would be an error.
- **pdftotext extraction damage.** Several tables are visibly reflowed/interleaved during extraction (e.g., Table 1/Figure 3 repository counts run together with axis labels at lines 96–119; Table 5's paired "% Resolved / % Apply" values are extracted as separate stacked numbers rather than a clean row/column grid, requiring careful positional matching; Appendix A.7 is truncated mid-sentence as noted above). Numbers that could be confidently matched to their row/column context were used; numbers with ambiguous alignment were treated cautiously or omitted.
- **Figure/table figure-caption ordering.** Several figures/tables (e.g. Figure 3/Table 1, Table 2/Table 3) are extracted with garbled interleaving of caption and data — required cross-referencing against the narrative text description to disambiguate values (e.g., Claude 2 BM25 13k = 1.96% cross-checked against Abstract's "1.96%" statement).

## Recommendation
**ACCEPT WITH CAVEATS.**

Reasons: The paper provides a clean, well-organized, fully tabulated set of experiments, methodology, and results suitable for reconstruction-question scoring. The caveat is that the companion README describes a substantially evolved, later project state (new datasets, new harness, new CLI) that must be firmly excluded from "paper" claims and used only for artifact/tooling facts — this separation is maintained throughout the Gold Account and claim table. A secondary caveat is the extraction damage to Appendix A.7 (SWE-bench Lite details), which is recorded as NOT IN SNAPSHOT rather than guessed.
