# Verification of the Gold Account: SWE_BENCH

Verifier: independent check against the frozen snapshot only (`snapshot/paper.txt` = arXiv:2310.06770v3, `snapshot/README__SWE-bench__SWE-bench.md`). `PROJECT_ASSESSMENT.md` was read for context only.
Files verified: `GOLD_ACCOUNT_DRAFT.md`, `gold_story.json`. The draft files were not modified.

## Method
- I checked every number in the draft and in `gold_story.json` against the extracted tables and text.
- I checked the table values against each other where the extraction scrambled the layout:
  - Table 14 counts divided by 2,294 or 574 reproduce the Table 6, 18 and 20 "% Apply" values: 1441/2294 = 62.82, 1564/2294 = 68.18, 1116/2294 = 48.65, 195/574 = 34.0, 85/574 = 14.8.
  - The Table 23 "Resolved" counts (110 and 91) reproduce Table 18: 110/2294 = 4.80, 91/2294 = 3.97.
  - The Table 8 "All Gold" row reproduces Table 1: 22.3 + 10.5 = 32.8 lines, 3.0 functions, 1.7 files.
- I checked each claim-strength label against the wording in the paper.
- I checked that README-only facts are kept separate from paper claims.

## Issue table

| # | Item | Problem | Evidence (snapshot quote) | Sev. | Correction |
|---|---|---|---|---|---|
| 1 | gold_story Q7a; draft §11 bullet 1, §16 (4), claim table row 2 | The nugget calls Claude 2 "the best-performing model under BM25 retrieval". In the same paper, the v3 Table 5 lists Claude 3 Opus at 3.79% on the full set with BM25, above Claude 2 (1.97%). The abstract's sentence dates from before Claude 3 Opus was added, and the draft repeats it as fact. The draft's own §11 bullet 3 names Claude 3 Opus as best, so the draft contradicts itself. | Table 5: "Claude 3 Opus Claude 2 ... 3.79 46.56 1.97 43.07"; Abstract: "The best-performing model, Claude 2, is able to solve a mere 1.96%" | high | Q7a now says only that Claude 2 resolved 1.96% with BM25 (Abstract, Table 2; 1.97 in Table 5). New nugget Q7e: Claude 3 Opus 3.79%, the highest full-set BM25 result. The account records that the abstract's "best" claim is stale against v3 Table 5. |
| 2 | gold_story Q12b | "Even the best model tested (Claude 2, under realistic BM25 retrieval) resolved under 2%" is false for this version: the best BM25 result is 3.79% (Claude 3 Opus). | Table 5 (as above) | high | Rewritten: every evaluated model resolves only a small fraction of issues (at most 3.79% with BM25 on the full set, at most 9.39% even with "oracle"-collapsed context). |
| 3 | draft §11 bullet 1; Q7a evidence | The draft attributes 1.96% to "Table 5/Table 2", but Table 5 reports 1.97. 1.96 comes from the Abstract, §1, §5 text and Table 2. This is a rounding inconsistency inside the paper, and the draft does not flag it. | Table 2: "Claude 2 ... 1.96 1.87 1.22"; Table 5: "1.97" | low | Cite 1.96 to the Abstract and Table 2, and note that Table 5 gives 1.97. |
| 4 | Q7d; draft §12 bullet 1 ("for all four models tested") | The paper gives an "oracle" (non-collapsed) result only for Claude 2, ChatGPT-3.5, GPT-4 and the SWE-Llama models. Claude 3 Opus has no oracle baseline, so an improvement for Claude 3 Opus, and therefore "all tested models", cannot be established. | Table 18 lists only "Claude 2 ChatGPT-3.5 GPT-4∗ SWE-Llama 7b SWE-Llama 13b"; Table 6 adds "Claude 3 Opus" | med | Limit the claim to models with both settings: Claude 2 4.80 to 5.93; ChatGPT-3.5 0.52 to 1.09; GPT-4 see #5. |
| 5 | Q7d; draft §10 Table 6 line, §12, claim row 4 | The draft passes on "GPT-4 jumping from 1.3% to 3.4%" without noting three problems. (a) The oracle GPT-4 value in Table 18 is 1.74, not 1.3; 1.3 matches the BM25 "GPT-4-turbo" value in Table 5 (1.31). (b) GPT-4 oracle ran on the 25% subset, but GPT-4 oracle-collapsed ran on the full set, so the jump compares different instance sets. (c) This is an inconsistency inside the paper. | §5: "GPT-4 jumping from 1.3% to 3.4%"; Table 18: "1.74"; Table 14 caption: "The GPT-4 'Oracle'-collapsed setting was run on the full SWE-bench test set." | med | Take the GPT-4 before/after out of the scored nugget. Record the paper's sentence verbatim and mark it as internally inconsistent. |
| 6 | draft §10 Table 8 line; §12 bullet 3; §17 bullet 3 | (a) The draft calls Table 8 "column-ambiguous" and "not confidently usable". It can in fact be parsed: the All Gold row gives 22.3 + 10.5 = 32.8 lines, 3.0 functions and 1.7 files, which exactly matches Table 1. (b) The draft reverses the subject of the sentence ("gold patches are described ... as less than half"). It is the model patches that are less than half. (c) 30.1 is the ChatGPT-3.5 model-patch total, not "an average model-generated applied patch". | §5: "model generated patch files that apply correctly are less than half the total length (74.5 versus 30.1 lines)"; Table 8 rows "ChatGPT-3.5 Gold 30.1 3.8 2.7 39.6 ..."; "All Gold 74.5 22.3 10.5 ... 3.0 1.7" | med | Report the parsed Table 8. Model totals: Claude 2 19.6, ChatGPT-3.5 30.1, GPT-4 20.9, SWE-Llama 13b 17.6, SWE-Llama 7b 16.7. Gold: Avg Gold 39.1, All Gold 74.5. Model patches edit about 1.0–1.1 files. Remove §17 bullet 3. |
| 7 | Q12c; draft §12 bullet 3 | The "shorter, simpler edits" claim holds only for patches that applied successfully (Table 8). Across all patches (Table 24), SWE-Llama edits are longer than gold. Q12c also bundles two findings (context-length degradation and patch length). | C.6: "the SWE-Llama models edits are on average longer in most respects"; Table 24: "SWE-Llama 13b 68.9 ... Gold 61.5"; "SWE-Llama 7b 78.9 ... Gold 65.1" | med | Q12c now covers patch length only and is qualified with "that apply successfully". Context length moves to Q8b. |
| 8 | Q12d | This is a README-only, post-paper fact (Verified, Multimodal, Multilingual) used as a gold nugget. It cannot be answered from a good paper about this research, and it breaks the rule of keeping README and paper facts separate. | README: "[Aug. 13, 2024]: Introducing SWE-bench Verified!" (none of these appear in paper.txt) | med | Removed from the nuggets. Kept in the account as an artifact fact only. |
| 9 | Q8a strength "measured" | "Can resolve only the simplest issues" is the authors' summary interpretation. No measurement of issue simplicity supports it. | Abstract: "can resolve only the simplest issues" | med | Relabelled `interpretation`. |
| 10 | Q8b | The nugget is not atomic. It mixes an observation (performance falls as context grows; Figure 5, Table 2) with the authors' explanation (localization failure), and labels the whole thing as interpretation. | §5: "as total context length increases, Claude 2's performance drops considerably"; "as models are simply ineffective at localizing problematic code" | med | Split in two. Q8b is the observed drop (`observed`). Q8d is the localization explanation (`interpretation`). |
| 11 | draft §13 bullet 1; claim-table row "Context length increase reduces model performance / interpretation" | Measured observations are labelled as interpretation. "Models perform best on the shortest context window" is read off Table 2. | §4.1: "From observation, models perform best on the shortest context window, as shown in Table 2." | low | Relabelled observed. Only the localization and "lost in the middle" explanation stays as interpretation. |
| 12 | Q11c; draft §15 scope boundary 3 | The "only 11 generations" limitation is the drafter's own critique, not a limitation the authors state. The draft also says "hand-selected"; the paper says only "select". | §5.1: "We select 11 generations from SWE-Llama and Claude 2" (no limitation claim) | med | Q11c removed from the nuggets. The account keeps it under "Verifier/drafter notes (not author-stated)". |
| 13 | Q6d, Q11b evidence; draft §8, §15, claim row "GPT-4 25% subset" | Cited to a "Table 5 footnote", which does not exist in the extracted Table 5 caption. The subset statement appears in the captions of Tables 7, 18, 20 and 23. | Table 7 caption: "∗Due to budget constraints, GPT-4 is evaluated on a 25% random subset of SWE-bench tasks, which may impact performance." | low | Re-cite to the Table 7, 18, 20 and 23 captions. |
| 14 | draft §15 scope boundary 1; Q6d, Q11b | The draft overstates the subset's scope ("GPT-4 results in Tables 5, 7, 14, 18, 20"). The subset applies only to the "Oracle" and BM25 27K settings. GPT-4 oracle-collapsed (Tables 6 and 14) ran on the full set. | Table 18 caption: "25% random subset ... in the 'Oracle' and BM25 27K retriever settings only"; Table 14 caption (as in #5) | med | Scope corrected in Q6d, Q11b and the account. |
| 15 | draft §8 and §10 (GPT-4 vs GPT-4-turbo) | The draft does not flag that the paper names GPT-4 inconsistently. §4.3 names gpt-4-32k-0613, while Table 5 labels the row "GPT-4-turbo" (1.31 / 26.90). Table 20 gives GPT-4 BM25 on the subset as 0.00 / 14.82 with a "−0.00" difference from Table 5, which is incompatible with 1.31 / 26.90. Table 14 (85/574 = 14.8% apply) agrees with Table 20, not with Table 5. | §4.3: "GPT-4 (gpt-4-32k-0613)"; Table 5: "GPT-4-turbo ... 1.31 26.90"; Table 20: "0.00 −0.00 ... 14.82 −0.00" | med | The account records this as an unresolved conflict inside the paper. Table 5 "GPT-4-turbo" is kept as a separately labelled row and is not merged with "GPT-4". |
| 16 | draft §8 model list; Q6c evidence | Claude 3 Opus is cited to "§4.3, Table 4", but it does not appear in §4.3 or Table 4. It appears only in Tables 5 and 6, and its context limit is not given. | §4.3: "we evaluate ChatGPT-3.5 (gpt-3.5-turbo-16k-0613), GPT-4 (gpt-4-32k-0613), Claude 2, and SWE-Llama" | low | Re-cite. State that Claude 3 Opus appears only in Tables 5 and 6. |
| 17 | draft §15 (limitation coverage) | Several limitations the authors do state are missing: (a) oracle context "not necessarily comprehensive"; (b) models with shorter context windows are "inherently disadvantaged"; (c) image-containing issues may need multimodal models or tools, which the baselines leave unexplored; (d) the baselines have a limited view of the codebase (inter-file dependencies). | §4.1: "this setting is also not necessarily comprehensive since edited files alone may not include all the required context"; Table 4 caption: "Models with shorter context lengths are thus inherently disadvantaged."; §5: "Solving these instances may require multi-modal LMs or some kind of external tool use" | med | Added to account §15. (b) is added as new nugget Q11e, replacing the removed Q11c. |
| 18 | draft §12 bullet 4; Q8c | The draft omits the GPT-4 exception that the paper names explicitly. | §5: "for most models there's little difference in performance before or after this date, with the exception of GPT-4" | low | Exception added in Q8c and in the account. |
| 19 | Q2c | The draft adds "rigorously". The paper says "easily". | §1: "generated solutions can be easily verified by running unit tests" | low | Wording corrected. |
| 20 | Q5a, Q5b strength; Q5b and Q9c overlap | These are design rationale and design facts labelled `interpretation`. Q5b also repeats the realism caveat in Q9c. | §4.1 | low | Q5a and Q5b relabelled `context`. Q5b now covers only the design fact. |
| 21 | Q9a and Q11a | The same "Python-only" nugget appears twice. | §7 | low | Q11a removed; Q9a kept. |
| 22 | draft §6 schema | The field name `environment_setup_commit` is not in the snapshot. Paper Table 9 lists "env install commit". | Table 9: "version repo FAIL TO PASS PASS TO PASS env install commit" | low | Use the paper's name. |
| 23 | draft claim table last row | "ICLR 2024 (oral)" is attributed to the paper header. The header says only "Published as a conference paper at ICLR 2024"; "Oral" is in the README only. | README: "[ICLR 2024 Oral]" | low | Attribute "Oral" to the README. |
| 24 | draft §7 README bullet | The draft says Multilingual is in the README download table. That table lists SWE-bench, Lite, Verified and Multimodal. Multilingual appears only as a CLI alias and in a citation. | README: "`DATASET` accepts an alias (`full`, `verified`, `multimodal`, `multilingual`)" | low | Corrected. |
| 25 | claim-table row "SWE-bench Lite ... measured (README-partial)" | The fact comes from paper §2.4, not the README. The §2.4 sentence "The full filtering criteria ... is included in" is itself truncated, not only A.7. | §2.4: "The full filtering criteria and dataset information is included in SWE-bench Lite covers 11 ..." | low | Label is now "paper §2.4 (A.7 and part of §2.4 truncated)". |
| 26 | draft §9 metrics | The automatic patch-repair step, which affects % Apply, is omitted. | A.4: "If applying the prediction patch (Step 5) fails, we attempt to repair the prediction patch file by removing unnecessary context lines and recalculating the header values" | low | Added to the metrics section. |

## Counts by type
| Type | Issues | Count |
|---|---|---|
| Factual correctness | 1, 2, 15, 16, 22 | 5 |
| Numerical correctness | 3, 5, 6 | 3 |
| Claim/evidence alignment (strength, strengthening, interpretation vs measurement) | 4, 7, 9, 10, 11, 18, 19, 20 | 8 |
| Limitation coverage / drafter critique posing as a stated limitation | 12, 14, 17 | 3 |
| README-vs-paper separation | 8, 23, 24, 25 | 4 |
| Methodology / citation location | 13, 26 | 2 |
| Nugget atomicity / duplication | 21 | 1 |
| **Total** | | **26** (high 2 / med 11 / low 13) |

Checks that passed with no issue: the stage I–III pipeline, and all of Table 10 (93,139 → 11,407 → 2,294 and every per-repo value quoted). Also correct: all Table 1 values; the median statistics (40%, 51, 140 words, ~1900 files, 400K lines); Tables 2, 3, 5 (apart from #1, #3 and #15), 6, 7 and 18; the whole-file ablation (2.2 vs 4.8; 3.9 vs 7.8); the Figure 6 sphinx-8713 details; 110 and 91 instances with 42% overlap; the image statistics (32/10/2%); the SWE-Llama training set (19,000 pairs, 37 repos, the 30,000-token cut, 10,000 instances) and the LoRA hyperparameters; the dev set (225 instances, 6 repos, post-2019 filter); Lite (300 instances, 11 repos); the limitations the authors state in §7; and the paper-vs-README conflict log entries about the harness and the datasets.

## Nugget changes (gold_story.json to gold_story.v1.json)
- The v1 file has 40 nuggets, all with unique IDs. Existing IDs are kept wherever the content survived.
- Removed:
  - Q11a (duplicate of Q9a).
  - Q11c (drafter critique).
  - Q12d (README-only).
  - Q3c. It was correct, but it overlapped Q1b and was dropped to stay within the 40-nugget cap. Its content is kept in account §3.
- Added:
  - Q7e: Claude 3 Opus 3.79% with BM25.
  - Q7f: whole-file vs patch generation, 2.2 vs 4.8.
  - Q8d: localization interpretation, split out of Q8b.
  - Q11e: shorter-context disadvantage, a limitation the authors state.
- Rewritten: Q2c, Q4b, Q4c, Q5a, Q5b, Q6c, Q6d, Q7a, Q7d, Q8a, Q8b, Q8c, Q9b, Q11b, Q12b, Q12c.
- Relabelled: Q3b from `context` to `literature`, since it is a claim about prior datasets.
- Q7 number check. Every value in Q7 is exact to the snapshot:
  - 1.96 (Abstract, Table 2), with 1.97 in Table 5.
  - 3.79 and 4.33 (Table 5).
  - 4.80, 0.52 and 3.97 (Table 18).
  - 5.93 (Table 6).
  - 2.2 and 4.8 (§5).

## Source conflicts and which source is authoritative
| Conflict | Sources | Treated as authoritative | Why |
|---|---|---|---|
| Evaluation harness: conda envs per repo version vs a Docker-based `swebench` CLI (v5) | Paper A.3/A.4 vs README "Set Up"/"Usage" | Paper for what was done in the study; README for the current artifact | Research claims come from the paper. The README describes a later migration ("[Jun. 27, 2024] ... moving to a fully containerized evaluation harness"). |
| Dataset family: SWE-bench, train, Lite, dev vs additional Verified (500), Multimodal, Multilingual | Paper vs README | Paper for what was evaluated; README only for artifact existence | The README items postdate the paper or belong to separate papers. |
| Venue detail "Oral" | README only | README (artifact/bibliographic fact) | The paper header does not state oral status. It does not conflict, but should not be attributed to the paper. |
| Dataset ID: `princeton-nlp/SWE-bench` (load_dataset) vs `SWE-bench/SWE-bench` (download table) | Inside the README | README (artifact fact); both recorded | The paper names no HF ID. |
| Best BM25 model: "Claude 2, 1.96%" (Abstract, §1, §5) vs Claude 3 Opus 3.79% (Table 5) | Inside the paper | Table 5 for the numbers; Abstract recorded verbatim as the authors' claim | The v3 table data supersedes stale prose. |
| GPT-4 oracle: "1.3%" (§5 text) vs 1.74 (Table 18) | Inside the paper | Table 18 value (subset); the text sentence is flagged | The table is the primary measurement. The text value matches a different row (Table 5 GPT-4-turbo BM25). |
| GPT-4 BM25: Table 5 "GPT-4-turbo 1.31/26.90" vs Table 20 GPT-4 0.00/14.82 "−0.00" | Inside the paper | Unresolved; both recorded with their labels | The snapshot does not allow a reconciliation. |
| Claude 2 BM25: 1.96 (Table 2, Abstract) vs 1.97 (Table 5) | Inside the paper | Both recorded (rounding) | The difference is immaterial but both are recorded for exactness. |

## Verdict
**ACCEPT AFTER CORRECTIONS.** The draft is mostly accurate and quotes the paper faithfully. The two high-severity errors are both in scored nuggets (Q7a, Q12b): they repeat the abstract's stale "Claude 2 is best" claim when the paper's own v3 Table 5 shows otherwise. The corrected files are `gold_story.v1.json` and `GOLD_ACCOUNT_v1.md`.
