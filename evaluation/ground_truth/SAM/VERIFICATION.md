# Verification: SAM Gold Account

Verifier: independent check of `GOLD_ACCOUNT_DRAFT.md` and `gold_story.json` against the frozen snapshot only (`external_projects/SAM/snapshot/paper.txt`, arXiv 2304.02643v1, and `README__facebookresearch__segment-anything.md`). `PROJECT_ASSESSMENT.md` was read for context only. The draft files were not modified. Line references ("L##") are `paper.txt` line numbers.

Method: I re-derived every number in draft §10 and every Q7 nugget from the snapshot text. I checked each experiment, dataset and protocol against §2–§7 and Appendices A–E. I checked each limitation against §8, App. C and the Model/Data cards (App. F). I checked each strength label against how the paper phrases the claim.

## Issues

| # | Item | Problem | Evidence (snapshot quote) | Severity | Correction |
|---|---|---|---|---|---|
| 1 | GA §10 Table 4; GA §17 bullet 4 | The draft mis-maps the LVIS AR@1000 values. It records ViTDet-H medium as 76.7, which is actually SAM single-output's medium value; ViTDet-H medium is 80.8. It records SAM "com=59.8/62.0, rare=63.9/65.8", mixing single-output SAM's values into SAM's row. The extraction can in fact be resolved: each line holds the per-row continuation in column order. | L583–587: "med. large freq. 80.8 87.0 63.1 / 76.7 74.4 54.7 81.6 86.9 59.1 / com. rare 63.3 58.3 / 59.8 62.0 63.9 65.8" | high | ViTDet-H: 63.0 / 51.7 / 80.8 / 87.0 / 63.1 / 63.3 / 58.3. SAM single-out.: 54.9 / 42.8 / 76.7 / 74.4 / 54.7 / 59.8 / 62.0. SAM: 59.3 / 45.5 / 81.6 / 86.9 / 59.1 / 63.9 / 65.8 (all / small / med / large / freq / com / rare). This mapping agrees with the prose for med, com, rare, small and freq, and with the statement that single-output SAM is worse "on all AR metrics". |
| 2 | GA §10 Table 4 prose | The draft does not flag a conflict inside the paper. The text says SAM outperforms ViTDet-H on large objects, but the table gives SAM large = 86.9 against ViTDet-H 87.0. | L593: "it outperforms ViTDet-H on medium and large objects"; L583–584: ViTDet large 87.0, SAM 86.9 | med | Record the table value as authoritative for the number. Treat "large" as essentially tied (−0.1), not as an outperformance. |
| 3 | gold_story Q7e; GA §8 (instance seg.), §11 | The human-rating study did not use the same inputs as the AP comparison. AP used ViTDet-H boxes; the rating study prompted both models with LVIS ground-truth boxes and was subsampled to 794 inputs. The draft implies a like-for-like comparison. | Fig. 11 caption L652: "both applied to LVIS ground truth boxes"; L1363: "the model input was the LVIS ground truth box"; L1654: "subsampled to the same 794 inputs" | med | State the input condition in Q7e and GA §8. |
| 4 | gold_story Q8b; GA §11 bullet 3 | The draft strengthens the claim. The paper only sets 94%/97% (a share of pairs above an IoU threshold) beside prior inter-annotator estimates of 85–91% (an IoU level). The two statistics differ, and the paper never says that SA-1B "exceeds" prior consistency. | L142: "For comparison, prior work estimates inter-annotator consistency at 85-91% IoU" | med | Rephrase as "set alongside", not "exceeding". |
| 5 | gold_story Q11e | Listed as a limitation, but the paper presents automatic-only SA-1B as a deliberate, justified design choice, not a limitation. | L141: "Motivated by these findings, SA-1B only includes automatically generated masks"; L674: "only marginally lower than using all data (∼0.5 mIoU)" | med | Remove from Q11. Keep it as a fact in the GA dataset section. |
| 6 | gold_story Q9c; GA §15 scope boundary 1; GA §18 row | The "cannot be independently reproduced" point about the proprietary skin-tone dataset is the drafter's reproducibility critique. The paper states only that the dataset is proprietary. | L288: "we use a proprietary dataset that contains annotations for the perceived Fitzpatrick skin type" | med | Keep "proprietary" as a dataset fact. Remove the non-reproducibility claim from the gold nuggets. Replace Q9c with an author-stated gap (clothing bias). |
| 7 | GA §15 scope boundary 2 | This is speculation by the drafter ("any model trained purely on the released dataset should be expected to reproduce only the fully-automatic-stage distribution"). It is neither author-stated nor derivable from the paper. | L141; L674 (the paper reports automatic-only training is only ∼0.5 mIoU lower) | med | Delete. |
| 8 | GA §15 (omissions) | Several limitations that the authors state are missing: (a) clothing-segmentation bias by perceived gender presentation, which the authors explicitly call a "limitation"; (b) under-representation of Africa and low-income countries in SA-1B; (c) possible downstream biases, with a recommendation that users run their own fairness evaluation; (d) a segmentation foundation model is "an inherently limited scope"; (e) image-encoder scaling gains saturate; (f) training cost and environmental impact (256 A100 GPUs for 68 h, ~6963 kWh, ~2.8 t CO2); (g) possible objectionable content in SA-1B; (h) country inference from captions is ambiguous and may be biased. | L1033: "we encourage users of SAM to be mindful of this limitation"; L256: "underrepresented in all datasets"; L1827: "we recommend users run their own fairness evaluation"; L732: "an inherently limited scope"; L728: "meaningful, yet saturating gains"; L1827: "trained on 256 A100 GPUS for 68 hours"; L1678; L1020 | med | Add these to GA §15. Add (a) and (c) to gold Q9. |
| 9 | gold_story Q7 (6 nuggets), Q11 (5 nuggets); Q9b/Q11b, Q9d/Q11c, Q7f/Q8b | Over the 1–4 per-question limit. Three pairs of nuggets duplicate each other across questions, so the same fact would be scored twice. | n/a (structure) | med | Merge Q7a and Q7b into a single RITM comparison. Fold Q7f into Q8b. Drop Q11e. Replace duplicate Q9b and Q9d with non-overlapping author-stated gaps. Final total: 36. |
| 10 | gold_story Q4c | Wording error: "together collected 1.1B masks". The 1.1B masks came from the fully automatic stage alone, since stages 1–2 gave 10.2M masks, and SA-1B contains only automatic masks. | L135: "applied fully automatic mask generation to all 11M images… producing a total of 1.1B"; L134: "(for a total of 10.2M masks)" | med | Say that the fully automatic stage produced SA-1B's 1.1B masks. |
| 11 | gold_story Q4b | Strength is "measured", but this is a design description. | L122: "We found 3 mask outputs is sufficient" | low | Change to context. |
| 12 | gold_story Q5a–Q5c | Strength is "interpretation", but these are the authors' stated design rationales, not interpretations of results. Q5c also cites only §A, while the rationale first appears in §3. | L57; L119: "Motivated by scalability and powerful pretraining methods" | low | Change to context. Add L119. |
| 13 | gold_story Q8c | Strength is "measured", but "reasonably close" is the authors' comparative characterization of measured AP gaps. | L596: "SAM is reasonably close, though certainly behind ViTDet" | low | Change to derived. |
| 14 | gold_story Q12b | Overgeneralized: "generally trails specialist models on strict AP metrics". | L43; Table 5 | low | Narrow to "trails… on some benchmark metrics such as instance-segmentation mask AP". Label derived. |
| 15 | gold_story Q4d | Omits "on CPU", which the paper states. | L125: "run in a web browser, on CPU, in ∼50ms" | low | Add. |
| 16 | GA §6 mask decoder | The order of steps inside the decoder layer is misstated. The actual order is self-attention, then token→image cross-attention, then MLP, then image→token cross-attention. | L988: "(1) self-attention… (2) cross-attention from tokens… (3) a point-wise MLP… (4) cross-attention from the image embedding" | low | Correct the order. |
| 17 | GA §8 single-point | Says the datasets were "subsampled to ~10k masks each". Only datasets with more than 15k masks were subsampled. | L1036: "we subsampled datasets with more than 15k masks" | low | Correct. |
| 18 | GA §7 / §12 | The draft does not flag a conflict inside the paper: Fig. 6 calls Open Images the "largest existing" segmentation dataset, while the §5 text calls it the "second largest". | L190 vs L222 | low | Note it. The comparison (11× images, 400× masks vs Open Images) is the same in both. |
| 19 | GA §13 vs §14 | The same COCO-bias statement is classified as both an interpretation and a hypothesis. The authors frame it as "We hypothesize". The Fig. 11 caption's "suggesting" is an interpretation. | L654: "We hypothesize that on COCO…"; L652: "suggesting that ViTDet exploits biases" | low | Keep one entry under hypotheses. Keep the Fig. 11 "suggesting" line as the interpretation. |
| 20 | GA §11 edge bullet | The wording "close to or exceeds the two learned baselines" is muddled. R50 exceeds HED but not EDETR. | Table 3: HED R50 .923, EDETR .930, SAM .928 | low | Rephrase. |

## Counts

- By severity: **high 1, medium 9, low 10** (20 issues).
- By type:

| Type | Count | Issue numbers |
|---|---|---|
| Numerical | 2 | #1, #2 |
| Experiment/methodology | 3 | #3, #16, #17 |
| Factual | 2 | #10, #15 |
| Claim/evidence alignment | 7 | #4, #11, #12, #13, #14, #19, #20 |
| Limitation coverage | 4 | #5, #6, #7, #8 (both drafter-own critiques and missing author limitations) |
| Structure (nugget count/duplication) | 1 | #9 |
| Source-conflict handling | 1 | #18 |

- Q7 numbers that were checked and are exact: 16/23 and ∼47 IoU; the oracle beats RITM on all 23; Table 3 SAM .768/.786/.794/.928 and HED .788/.808/.840/.923; Table 5 COCO 46.5 vs 51.0 and LVIS 44.7 vs 46.6; Fig. 11 8.1 vs 7.9; §5 94%/97%. These were all correct in the draft.
- Also verified as correct: Tables 1, 2, 5 and 6; Fig. 11 means and CIs; data-engine yields (4.3M/120k, +5.9M/180k, 10.2M total, 1.1B/11M); annotation times (34→14 s, back to 34 s); masks per image (20→44→72); training recipe (App. A); ViT-B/L/H parameter counts (91M/308M/636M); the losses (20:1 focal:dice); and 11 training rounds.

## Source conflicts and authority

| Conflict | Sources | Treated as authoritative | Why |
|---|---|---|---|
| "large objects" outperformance vs Table 4 (86.9 vs 87.0) | paper text L593 vs paper Table 4 | Table 4 for the number; the text's characterization is recorded as stated | A table value is the direct measurement. The text is a summary of it. |
| Open Images called "largest existing" (Fig. 6) vs "second largest" (§5) | paper L190 vs L222 | Neither needs resolving. The ratios are identical, and SA-1B is the largest either way. | This is a wording difference only. |
| README banner promotes SAM 2 (2024, video) | README vs paper | Paper for all research claims. README only for artifact facts: checkpoints vit_h/vit_l/vit_b, Apache 2.0 model license, "SA-1B Dataset Research License", COCO-RLE JSON schema. | The README postdates the paper and describes a later project. |
| Model license | paper L63 "Apache 2.0" and README "Apache 2.0 license" | Consistent | n/a |

## Verdict

**ACCEPT AFTER CORRECTIONS.** The core research story, the dataset and data-engine facts, and every Q7 number are accurate. Corrections were needed for the Table 4 value mapping in the Gold Account, the input condition of the human-rating study, one strengthened claim (Q8b), limitations the drafter wrote on the authors' behalf, missing limitations the authors do state, and the nugget-count and duplication structure. The corrected files are `gold_story.v1.json` (36 nuggets) and `GOLD_ACCOUNT_v1.md`.
