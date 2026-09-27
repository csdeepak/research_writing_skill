# Verification of the BEIR Gold Account draft

Verifier: independent check against the frozen snapshot only (`snapshot/paper.txt`, arXiv 2104.08663v4, and `snapshot/README__beir-cellar__beir.md`). `PROJECT_ASSESSMENT.md` was read for context only.
Draft files checked: `GOLD_ACCOUNT_DRAFT.md`, `gold_story.json` (not modified).
Outputs: `gold_story.v1.json` (40 nuggets, `"verified": true`) and `GOLD_ACCOUNT_v1.md`.

## Method
- Every number in the draft and nuggets was checked against paper.txt. Tables 2, 3, 4, 9 and 10 were reflowed by pdftotext. I rebuilt Table 2's column order from the value blocks: each block ends with its "Avg. Performance vs. BM25" entry, and the blocks follow the §4 model order. The TREC-COVID column of Table 2 matches the "Original" row of Table 4 for all 9 models (0.656, 0.406, 0.538, 0.713, 0.332, 0.654, 0.481, 0.677, 0.757), which independently confirms the draft's model-to-number mapping.
- Per-dataset spot checks: TAS-B vs ANCE on TREC-COVID, 0.654 − 0.481 = 17.3 ✓. On Touché-2020, 0.240 − 0.162 = 7.8 ✓. BM25+CE < BM25 only on ArguAna (0.311 vs 0.315) and Touché-2020 (0.271 vs 0.367) ✓. Table 10: 0.635 − 0.482 = 15.3 ✓. In-domain MS MARCO gap: BM25 0.228 vs 0.296 to 0.413 = "7-18 points" ✓.
- All of the following matched the paper: the Table 2 averages (+11%, +2.5%, −3.6%, −2.8%, −7.4%, +1.6%, −47.7%, −20.3%, −27.9%), win counts (16/18, 11/18, 9/18, 14/18, 17/18), Hole@10 values, 980 pairs, 1M DBPedia docs, hardware, ~900GB vs 18GB, 3.6k–15M docs, query lengths 3–192 words, document lengths 11–635 words, 8/19 datasets with training data, and the model hyperparameters (k=0.9/b=0.4, 2,000 non-zero entries, 40 queries/doc, 600K and 300K steps, 5 queries/doc, top-k 25/top-p 0.95, 100K cap, faiss depth 100, max length 300, 14 cross-encoders, 6-layer 384-h MiniLM).

## Issue table

| # | Item | Problem | Evidence (snapshot quote) | Sev. | Type | Correction |
|---|---|---|---|---|---|---|
| 1 | Draft §11 bullet 4; nugget Q8c | Says re-annotation gave "the largest gains for high-Hole@10 systems (ANCE, ColBERT)". The paper makes no such claim, and Table 4 contradicts it. ColBERT gains +5.8, the smallest of any non-lexical system, with Hole@10 of 12.4%. DPR gains most (+11.3). TAS-B has the highest Hole@10 (31.8%) but gains less (+7.4) than DPR, SPARTA (+8.6) and ANCE (+8.1). A derived claim was presented as "measured". | Table 4, lines 687–695: "0.332 0.654 0.481 0.677" → "0.445 0.735 0.555 0.735"; line 705: "Similar improvements are noticed in ColBERT (5.8 points)" | **High** | numerical / claim-evidence | Replaced with the paper's claim (lexical systems barely change, non-lexical systems gain substantially). Added the full before/after table with the gains marked as computed by the verifier. |
| 2 | Nugget Q8c | "ANCE improved from 0.654 to 0.735, a 6.7-point gain over BM25". ANCE's gain is 8.1 points. The 6.7 is its margin above BM25 *after re-annotation* (0.735 − 0.668). As written, a reader who reports "+8.1" would be marked wrong. | line 705: "improves from 0.654 (slightly below BM25) to 0.735, which is 6.7 points above the BM25 performance" | Med | numerical | Reworded: "moving from slightly below BM25 to 6.7 points above it". |
| 3 | Draft §10, Table 9 | Says the second 0.658 is the "'Avg. Performance vs. BM25' bottom-row MS MARCO column". Table 9 has no such row. The second 0.658‡ is BM25+CE's in-domain Recall@100, identical to BM25's because BM25+CE only re-ranks BM25's top-100. The block at line 1242 is BM25+CE's zero-shot column, not an MS MARCO value. | lines 1137–1141: "ColBERT BM25+CE … 0.865‡ … 0.658‡"; line 363: "reranks the top-100 retrieved hits from a first-stage BM25" | Med | numerical / factual | Rewrote Table 9 entry with all in-domain Recall@100 values and the explanation. |
| 4 | Draft §13, TAS-B/ANCE length preference | Attributes the TAS-B/ANCE difference to "cosine vs. dot-product". The main text blames the *loss function*. Appendix H says the source is hard to identify and tests similarity function only on two new proxy DistilBERT models. The paper never states which similarity function TAS-B or ANCE uses. The drafter's inference was presented as the authors' interpretation, and the source's internal inconsistency was hidden. | line 539: "this preference for shorter or longer documents is due to the used loss function"; line 930: "Identifying the source for this contrasting behaviour is difficult" | Med | claim-evidence / methodology | Rewritten to show both statements, the proxy nature of the ablation, and the inconsistency. |
| 5 | Draft §17 (missing) | The main-text causal claim "is due to the used loss function" is stated as fact but only indirectly supported. It was not listed as weakly supported. | line 539 (as above); line 950: "only changed the similarity function" | Med | unsupported claims | Added to §17. |
| 6 | Nugget Q9c | "Because all neural models truncated documents … comparisons do not establish how these models would compare on full, untruncated long documents." This is the drafter's own scope inference (the draft §15 admits it is "not an authors' explicit limitation statement"), turned into a scoring nugget that a good paper need not contain. | draft §15: "a boundary that follows directly from the stated 512-word-piece condition, not an authors' explicit limitation statement" | Med | limitation coverage | Replaced with an author-stated scope condition: bias study limited to TREC-COVID, annotated blind by the authors (lines 703–704, 825). |
| 7 | Nugget Q11b | Not atomic. It bundles "pure textual search" (which is the separate multi-factor limitation, already Q9b), long-document retrieval, and multi-field retrieval. | lines 834–836 (three separately numbered limitations) | Med | atomicity | Split into Q11b (long documents) and Q11e (multi-field). The pure-text part stays in Q9b. |
| 8 | Nugget Q12c | "Many retrieval benchmark annotations carry a lexical bias". This widens the paper's claim from BEIR datasets to retrieval benchmarks in general. | line 661: "Many BEIR datasets are found to be subject to a lexical bias" | Med | claim strengthened | Changed to "Many BEIR datasets …". |
| 9 | Draft §15 (missing) | Author-stated caveats were missing from the limitations: lexical annotation bias of the benchmark itself; annotations done by the authors; GenQ capped at 100K documents for resource reasons; "not feasible to include all datasets"; checklist "No" answers on negative societal impact and PII/offensive content. | line 123: "can give an unfair disadvantage to non-lexical approaches"; line 825: "Annotations were done by the authors of the paper"; line 361: "Due to resource constraints, we cap …"; line 821: "Checking for offensive content in more than 50 million documents is difficult" | Med | limitation coverage | Added as items 8–11 in §15 and to §8/§17. |
| 10 | Nuggets Q7a, Q7d | Q7d was non-atomic and mislabelled "Dense/sparse models such as DeepCT, SPARTA, and DPR": three models across two families and two separate paper findings (term-weighting failure, and DPR worst). | lines 535–536 | Low | atomicity | Split into Q7d (DPR −47.7%, worst, only non-MS MARCO model) and Q7e (DeepCT −27.9%, SPARTA −20.3%). Q7a–Q7c are kept as one-model headline results. |
| 11 | Nuggets Q9a / Q11a | Duplicates (English-only). | line 833 | Low | atomicity / redundancy | Removed Q11a and kept Q9a. |
| 12 | Nugget strength labels | Q4a–Q4d and Q5c were labelled "measured" but describe what was built or done (method facts). Q5a was labelled "interpretation" but is a design criterion. Q8d used a non-standard "observed" label and dropped the authors' hedge "likely". | line 123: "likely as lexical models are pre-dominantly used" | Low | claim-evidence alignment | Q4a–d, Q5a and Q5c relabelled "context". Q8d relabelled "interpretation", with "likely" restored. |
| 13 | Nugget Q5b | Conflates the two rationales. Precision and Recall are rejected as *rank-unaware*, and only MRR/MAP are rejected for failing on graded relevance. | line 353 | Low | methodology | Reworded. |
| 14 | Draft §7 "four factors" | The paper says "three factors" but enumerates (i)–(iv). The draft silently fixed this without flagging the inconsistency. | line 137: "motivated by the following three factors: (i) … (iv)" | Low | factual (source inconsistency) | Note added. |
| 15 | Draft §11 DPR note | The drafter calls "non-MSMARCO trained" "unusual". It is fully consistent with §4 (Multi-DPR trained on four QA datasets). The draft also omits that NQ is in-domain for DPR (0.474‡). | line 361; line 458: "0.474‡" | Low | factual | Note fixed; in-domain caveat added to §8. |
| 16 | Draft §15 item 2 | Misquote: "a fundamentally different setup". | line 834: "a fundamental different setup would be required" | Low | factual (quotation) | Fixed. |
| 17 | Draft §13 / Appendix H | Not flagged: Appendix H lists the losses as "(InfoNCE vs. Margin-MSE …)" in TAS-B-then-ANCE order, which contradicts §4 (TAS-B trained with Margin-MSE). | line 930 vs line 361 | Low | source conflict | Flagged in §13. |
| 18 | Nugget Q1a | "mostly" strengthens the paper's "often". | line 7: "have often been studied in homogeneous and narrow settings" | Low | claim strengthened | Changed to "often". |
| 19 | Nugget Q12b | "cheap baseline" is the drafter's addition, and the abstract/intro claim does not say it. The per-model Table 3 latency columns are too damaged to anchor BM25's latency reliably. | line 122: "Overall, BM25 remains a strong baseline for zero-shot text retrieval." | Low | unsupported wording | "cheap" removed. |
| 20 | Draft §17 bullet 1 | The significance-testing critique is the drafter's own. That is acceptable in §17, but it was not labelled as such. | line 816 (authors disclose no error bars) | Low | limitation attribution | Label note added. |
| 21 | Draft §17 (missing) | "significant performance improvement" (line 123) is reported without any significance test, from one dataset. Lexical bias in other datasets is inferred from how they were created, not measured. | line 123; line 661 | Low | unsupported claims | Added to §17. |

## Counts

By severity: **High 1 · Med 8 · Low 12 (total 21)**

By type:
| Type | Count | Issues |
|---|---|---|
| Numerical correctness | 3 | 1, 2, 3 |
| Claim/evidence alignment (incl. strength labels, strengthened claims) | 5 | 4, 8, 12, 18, 19 |
| Unsupported claims (missing from §17) | 2 | 5, 21 |
| Limitation coverage / attribution | 3 | 6, 9, 20 |
| Atomicity / nugget redundancy | 3 | 7, 10, 11 |
| Methodology correctness | 1 | 13 |
| Factual / quotation / source inconsistency | 4 | 14, 15, 16, 17 |
| Experiment correctness | 0 | — (all four experiments exist in the paper as described) |
| Dataset correctness | 0 | — (dataset counts, sizes, lengths, licences verified) |
| README-vs-paper separation | 0 | — (handled correctly) |

## Items verified as correct (no change)
- The main zero-shot comparison, efficiency study, TREC-COVID re-annotation and cosine/dot-product ablation all happened as described (§4, §5.1, §6, App. H).
- Every Table 2 average, win count and TAS-B/ANCE value; all Hole@10 values; all Table 10 values; Table 3 prose figures (>350 ms, 20–30x, <20 ms, 20–25 ms, <3GB, ~900GB vs 18GB).
- Dataset facts: 18 + MS MARCO, 9 tasks, 3.6k–15M docs, 8/19 datasets with training data, ArguAna has the only long queries, 4 datasets have no reported licence.
- Model configurations in draft §5 (every hyperparameter checked).
- The five Appendix B limitations and the Checklist 3c/3d disclosures.

## Source conflicts and authority

| Conflict | Paper says | README says | Authoritative source and reason |
|---|---|---|---|
| Publication status | "Preprint. Under review." (line 13) | "(NeurIPS 2021, Datasets and Benchmarks Track)" (README l.59; BibTeX l.408) | **README, for venue metadata only.** Publication venue is an artifact/citation fact that the later README can update. It is not a research claim. The paper text makes no venue claim, and nothing in the research account depends on it. The draft handles this correctly. |
| Repository location | `https://github.com/UKPLab/beir` (lines 7, 124) | clones `github.com/beir-cellar/beir` (README l.73) | **README, for current artifact location.** Same project, later location. |
| Number of datasets | 18 zero-shot + MS MARCO = 19 (lines 138, 290) | "already-preprocessed 17 benchmark datasets" (README l.82); its table lists 19 rows | **Paper, for research claims.** The README's "17" reflects the later codebase and is unexplained. It is not used. |
| Dataset accessibility | Links in Table 5; no statement that downloads are unavailable | BioASQ, Signal-1M(RT), TREC-NEWS, Robust04 marked ❌ / "How to Reproduce?" (README l.343, 347–349) | **README, for the artifact fact.** It does not conflict with any paper claim. The draft labels it correctly as README-only. |
| Per-dataset stats | Table 1 (e.g. BioASQ 14,914,602 docs, 500 queries) | README table (14.91M, 500) | Consistent. The paper's figures are used. |
| Paper-internal: selection factors | "three factors" then lists four (line 137) | — | Paper; enumerated list (four) treated as the content. |
| Paper-internal: cause of length preference | "due to the used loss function" (line 539) vs "similarity function" ablation, "difficult" to identify (App. H, lines 930–952) | — | Neither is treated as established. Recorded as an unresolved interpretation. |
| Paper-internal: TAS-B loss | Margin-MSE + in-batch (line 361) vs "(InfoNCE vs. Margin-MSE …)" order in App. H (line 930) | — | §4 is authoritative (it is the primary model description). App. H ordering is treated as a slip. |

## Verdict: **ACCEPT AFTER CORRECTIONS**

The draft is numerically very accurate: every Table 2, 4 and 10 value and prose figure checked out, and its README/paper separation is sound. The problems are one wrong derived claim that fed a scoring nugget (#1), one misleading number framing in the same nugget (#2), a misread Table 9 (#3), an over-extended interpretation (#4), and nugget hygiene (a drafter-inferred limitation, non-atomic and overgeneralised nuggets). All are corrected in `gold_story.v1.json` and `GOLD_ACCOUNT_v1.md`.

Nugget set changes: Q11a removed (duplicate of Q9a); Q11d removed (task-specific models, a framing remark rather than a result limitation, dropped to stay within 40); Q7e and Q11e added from splits; Q9c replaced; Q1a, Q3a, Q3c, Q5b, Q6d, Q7a–Q7d, Q8a–Q8d, Q11b, Q12b and Q12c edited; labels changed on Q4a–d, Q5a, Q5c and Q8d. Total: 40.
