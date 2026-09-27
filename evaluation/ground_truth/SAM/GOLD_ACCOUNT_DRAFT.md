# Gold Account Draft — SAM (Segment Anything)

Snapshot-only factual ledger. Basis: `evaluation/external_projects/SAM/snapshot/paper.txt` (arXiv 2304.02643v1, pdftotext) and `README__facebookresearch__segment-anything.md` (pinned commit `dca509fe793f601edb92606367a655c15ac00fdf`). **The paper is authoritative for all research claims; the README is used only for artifact facts** (checkpoints, license, dataset JSON schema). Line refs ("L##") are `paper.txt` line numbers.

## 1. Problem
Build a foundation model for image segmentation: a model that can be prompted (analogous to NLP prompting) to produce valid segmentation masks and can generalize zero-shot to new image distributions and downstream segmentation tasks (L42–43, L49, L55).

## 2. Motivation
Foundation models pre-trained on web-scale data have driven strong zero-/few-shot generalization in NLP and, to a lesser extent, vision-language pairs (e.g., CLIP, ALIGN) (L45, L48). The authors want to extend this paradigm to segmentation, a broad computer-vision problem for which "abundant training data does not exist" (L48).

## 3. Research gap
- No web-scale data source exists for segmentation masks, unlike text or paired image-text data (L48, L55: "there is no web-scale data source for segmentation").
- Prior segmentation systems are multi-task systems with a fixed set of training/test tasks, not models designed for open-ended prompt-driven generalization to unseen tasks (L92: "An important distinction in our work is that a model trained for promptable segmentation can perform a new, different task at inference time").

## 4. Research question / objective
Stated as three entangled questions the paper sets out to answer (L50–51):
1. What task will enable zero-shot generalization?
2. What is the corresponding model architecture?
3. What data can power this task and model?

## 5. System / method
- **Promptable segmentation task** (§2): given any prompt (points, boxes, mask, or free-form text) return a "valid" mask — a reasonable mask for at least one object the prompt could refer to, even under ambiguity (L84–86).
- **SAM model** (§3): image encoder (MAE-pretrained ViT-H/16, run once per image) + prompt encoder (points/boxes via positional encodings + learned embeddings; masks via convolutions; free-form text via CLIP text encoder) + lightweight mask decoder (modified 2-layer Transformer decoder with prompt self-attention and bidirectional cross-attention, then upsampling + dynamic linear mask classifier) (§3, §A, L117–121, L947–996).
- **Ambiguity handling**: predicts 3 output masks per prompt by default plus a predicted IoU confidence score per mask; trains with minimum loss over the 3 masks (L122–124, L997).
- **Losses**: 20:1 weighted combination of focal loss and dice loss for masks; MSE loss for IoU prediction head, added with scale factor 1.0 (L999).
- **Training simulation**: interactive-style training with up to 11 rounds of sampled prompts per mask (1 initial + 8 iterative points + 2 no-new-info refinement rounds) (L126, L1001–1003).

## 6. Architecture
- Image encoder: MAE-pretrained ViT-H/16 with 14×14 windowed attention + 4 global attention blocks; input 1024×1024 (padded/rescaled); output embedding 64×64×256 after 1×1 then 3×3 conv + layer norm (L947–948).
- Prompt encoder: sparse prompts → 256-d embeddings (points/boxes via positional encoding + learned type embeddings; text via CLIP text encoder); dense (mask) prompts embedded via 2×(2×2, stride-2) convolutions + 1×1 conv, summed element-wise with image embedding (L949–950, L120).
- Mask decoder: 2-layer modified Transformer decoder (self-attn on tokens → token↔image cross-attn both directions → point-wise MLP), then 2× transposed-conv 4× upsampling, then dynamic linear classifier from output token via 3-layer MLP (L121, L987–996, Fig. 14 description).
- Attention: embedding dim 256, MLP internal dim 2048 (applied to prompt tokens only), 8 heads; cross-attention channel dim reduced to 128 for efficiency (L995).
- Runtime: given a precomputed image embedding, prompt encoder + mask decoder run in ∼50ms in a browser on CPU (L57, L125).
- Scale variants: ViT-B (91M params), ViT-L (308M), ViT-H (636M) (Fig. 13 caption, L719–726).

## 7. Dataset / data
- **SA-1B**: 1.1B (1,129M) masks, 11M images, licensed from a provider working directly with photographers; avg native resolution 3300×4950 px, released downsampled to 1500 px shortest side; faces and license plates blurred (L60, L138–140, L146).
- 99.1% of SA-1B masks generated fully automatically (only the final data-engine stage) (L141).
- Data engine, 3 stages (§4): (1) assisted-manual — professional annotators + SAM-assisted browser tool, no semantic label constraints, 4.3M masks from 120k images, per-mask time dropped 34→14s as model retrained 6 times (L129–133); (2) semi-automatic — SAM-prefilled confident masks + annotators label the rest, +5.9M masks / 180k images (10.2M total), per-mask time back to 34s, masks/image 44→72, model retrained 5 times (L134); (3) fully automatic — 32×32 point grid prompting + confidence/stability filtering + NMS + crop-based zoom-in, applied to all 11M images → 1.1B masks (L135, App. B).
- Mask-quality check: on a 500-image (~50k-mask) sample, automatic vs. professionally-corrected mask pairs — 94% of pairs >90% IoU, 97% >75% IoU, vs. prior-work inter-annotator consistency of 85–91% IoU (L142).
- 23-dataset zero-shot evaluation suite compiled by the authors from prior work, spanning egocentric, microscopy, X-ray, underwater, aerial, simulation, driving, painting domains (App. D.1, L1036, Table 7 names in App.).
- README-only artifact fact: SA-1B is downloadable under a separate "SA-1B Dataset Research License"; per-image mask annotations are stored as JSON with COCO RLE-encoded segmentations (README L116–156). [README-only — not a paper claim.]

## 8. Experimental setup
- **Single-point valid mask** (§7.1): sample points from mask "center" (max interior-distance-transform point) by default, or random-point sampling as an alternate protocol; evaluate SAM's most-confident mask by default, plus an "oracle" (best of 3) variant; compare to RITM, SimpleClick, FocalClick baselines; 23 datasets, subsampled to ~10k masks each; supplemented with a 1–10 human quality-rating study on a 7-dataset subset (§7.1, App. D.1, App. E).
- **Edge detection** (§7.2): BSDS500, 16×16 point grid → 768 masks → Sobel filtering + NMS post-processing; metrics ODS/OIS/AP/R50; compared to HED, EDETR (learned) and Sobel/Canny/Felz-Hutt (classical zero-shot) (App. D.2).
- **Object proposals** (§7.3): LVIS v1 validation, AR@1000 metric, modified automatic mask-generation pipeline (64×64 point grid, NMS 0.9, no crop-processing), baseline cascade ViTDet-H (App. D.3).
- **Instance segmentation** (§7.4): SAM prompted with ViTDet-H's predicted boxes on COCO/LVIS v1 validation, one mask-refinement iteration; compared to ViTDet-H by AP and by a human 1–10 rating study (App. D.4).
- **Text-to-mask** (§7.5): SAM variant trained with CLIP image-embedding prompts (masks area >100², first-two data-engine stages only, 120k iterations, batch 128), inference with CLIP text embeddings; qualitative only, no quantitative metric reported (App. D.5).
- **Ablations** (§7.6): trained on cumulative data-engine stages, on 0.1M/1M/11M-image subsamples of SA-1B, and with ViT-B/L/H encoders; evaluated with the single center-point protocol on the 23-dataset suite (Fig. 13).
- **RAI fairness study** (§6): simulated interactive segmentation with 1 and 3 random points; MIAP dataset for gender/age; proprietary dataset for Fitzpatrick skin-tone (1=lightest…6=darkest) (App. C).
- **Training recipe** (App. A): AdamW (β1=0.9, β2=0.999), linear warmup 250 iters, lr 8e-4 initial, step decay ×10 at 60k and 86,666 iters, 90k total iterations (~2 SA-1B epochs), batch size 256, weight decay 0.1, drop path 0.4, layer-wise lr decay 0.8, 256 GPUs, ≤64 masks/GPU, no data augmentation, initialized from MAE-pretrained ViT-H.

## 9. Metrics
- mIoU (mean IoU between predicted and ground-truth masks), including per-dataset and averaged-across-23-datasets variants, and "oracle" (best-of-3) mIoU (§7.1).
- Human mask-quality rating, 1 (nonsense) to 10 (pixel-perfect), by professional annotators (§7.1, App. E, App. G).
- ODS, OIS, AP, R50 for edge detection (Table 3).
- AR@1000 (average recall at 1000 proposals), broken out by object size (small/medium/large) and LVIS frequency bucket (frequent/common/rare) (Table 4).
- AP, APS, APM, APL for instance segmentation (Table 5).
- mIoU at 1-point and 3-point prompts, broken out by perceived gender presentation, age group, and Fitzpatrick skin tone, with 95% confidence intervals (Tables 2 and 6).

## 10. Results (exact numbers, with table/section)
- **Table 3 — BSDS500 edge detection**: SAM ODS .768 / OIS .786 / AP .794 / R50 .928. HED (2015) .788/.808/.840/.923. EDETR (2022) .840/.858/.896/.930. Sobel filter (1968) ODS .539 only. Canny (1986) .600/.640/.580/–. Felz-Hutt (2004) .610/.640/.560/– (L481–560).
- **Table 4 — LVIS v1 AR@1000**: ViTDet-H all=63.0, small=51.7, med=76.7, large=87.0, freq=63.1, com=63.3, rare=58.3 [note: pdftotext row/column mapping in this table is ambiguous — see PROJECT_ASSESSMENT.md Risk 2; values recorded as extracted, in author-given order]. SAM (single-out.) all=54.9, small=42.8. SAM all=59.3, small=45.5, med=81.6, large=86.9, freq=59.1, com=59.8/62.0, rare=63.9/65.8 (L569–587). Text states SAM "outperforms ViTDet-H on medium and large objects, as well as rare and common objects" and "underperforms ViTDet-H on small objects and frequent objects" (L593).
- **Table 5 — instance segmentation AP**: ViTDet-H COCO AP 51.0 (APS 32.0, APM 54.3, APL 68.9), LVIS v1 AP 46.6 (APS 35.0, APM 58.0, APL 66.3). SAM COCO AP 46.5 (APS 30.8, APM 51.0, APL 61.7), LVIS v1 AP 44.7 (APS 32.5, APM 57.6, APL 65.5) (L600–616).
- **Fig. 11 — human ratings (mean ± 95% CI)**: LVIS GT 8.6±0.06; SAM 8.1±0.07; ViTDet-H 7.9±0.08; COCO GT 7.6±0.12 (L622–630).
- **§7.1 text results**: SAM yields higher mIoU than RITM on 16 of 23 datasets, "by as much as ∼47 IoU"; with the oracle, "SAM outperforms RITM on all datasets" (L461). Human study: "SAM's mean ratings fall between 7 and 9"; ablated single-output SAM rates consistently lower than full SAM but higher than RITM; "all differences are significant" (L462–464).
- **Table 2 — RAI, person segmentation, mIoU (1pt/3pt, ±95% CI)**: gender feminine 54.4±1.7/90.4±0.6, masculine 55.7±1.7/90.1±0.6; age older 62.9±6.7/92.6±1.3, middle 54.5±1.3/90.2±0.5, young 54.2±2.2/91.2±0.7; skin tone 1: 52.9±2.2/91.0±0.9, 2: 51.5±1.4/91.1±0.5, 3: 52.2±1.9/91.4±0.7, 4: 51.5±2.7/91.7±1.0, 5: 52.4±4.2/92.5±1.4, 6: 56.7±6.3/91.2±2.4 (L262–286). Caption: "all confidence intervals overlap except older vs. middle" (L286).
- **Table 6 — RAI, clothing segmentation, mIoU (App. C)**: gender feminine 76.3±1.1/90.7±0.5, masculine 81.0±1.2/92.3±0.4 (disjoint intervals at 1pt); age older 81.9±3.8/92.8±1.6, middle 78.2±0.8/91.3±0.3, young 77.3±2.7/91.5±0.9 (L1026–1033).
- **Table 1 — RAI geographic/income (recorded with caution — see PROJECT_ASSESSMENT.md Risk 4)**: Africa 54 countries, 300k images, 28M masks, 2.8% SA-1B / 3.0% COCO / 1.7% Open Images. Asia & Oceania 70/3.9M/423M/36.2%/11.4%/14.3%. Europe 47/5.4M/540M/49.8%/34.2%/36.2%. Latin America & Carib. 42/380k/36M/3.5%/3.1%/5.0%. North America 4/830k/80M/7.7%/48.3%/42.8%. High-income countries 81/5.8M/598M/54.0%/89.1%/87.5%. Middle-income 108/4.9M/499M/45.0%/10.5%/12.0%. Low-income 28/100k/9.4M/0.9%/0.4%/0.5% (L232–254).
- **Mask-quality validation (§5)**: 94% of automatic/corrected pairs >90% IoU, 97% >75% IoU (L142).
- **Ablations (Fig. 13, prose only — plotted axis values are NOT IN SNAPSHOT)**: each data-engine stage improves mIoU; automatic-only data is "only marginally lower... (∼0.5 mIoU)" than all-stage data (L674); 1M images (~10% of SA-1B) gives results "comparable to using the full dataset" while 0.1M shows "a large mIoU decline" (L675); ViT-H "improves substantially" over ViT-B but has only "marginal gains" over ViT-L (L730).
- **Data-engine yields**: stage 1 = 4.3M masks/120k images; stage 2 = +5.9M masks/180k images (10.2M cumulative); stage 3 = 1.1B masks/11M images (L133–135).

## 11. Supported claims (directly measured/observed)
- SAM's zero-shot single-point mIoU exceeds RITM on 16/23 datasets, by up to ~47 IoU (L461) — measured.
- With oracle mask selection, SAM exceeds RITM on all 23 datasets (L461) — measured.
- SAM's automatic masks achieve 94%/97% IoU agreement thresholds (>90%/>75%) against professional corrections, exceeding stated prior inter-annotator consistency (85–91%) (L142) — measured.
- SAM's zero-shot AP trails the fully-supervised ViTDet-H on both COCO and LVIS instance segmentation (Table 5) — measured.
- SAM receives higher human quality ratings than ViTDet-H on LVIS despite lower AP (Fig. 11) — measured.
- Zero-shot edge detection: SAM's R50 (.928) is close to or exceeds the two learned baselines (HED .923, EDETR .930 is higher) while its ODS/OIS/AP trail both learned methods but exceed classical zero-shot methods (Table 3) — measured.
- Fairness: within each of gender/age/skin-tone groupings for person segmentation, confidence intervals mostly overlap except older vs. middle age (Table 2 caption, L286) — measured/observed.
- Fairness: for clothing segmentation, gender-presentation confidence intervals are disjoint at 1-point (masculine higher) (Table 6, L1033) — measured/observed.

## 12. Derived claims (computed/comparative)
- "SA-1B has 400× more masks than any existing segmentation dataset" (L60) — comparative/derived from dataset size figures.
- "SA-1B has 11× more images and 400× more masks than the second largest, Open Images. On average, it has 36× more masks per image than Open Images" (L222) — derived ratios.
- Average annotation time was "6.5× faster than mask annotation for COCO... and only 2× slower than bounding-box labeling with extreme points" (L133) — derived comparison.
- "the gap [between SAM and baselines] shrinks on the higher-quality LVIS masks" relative to COCO (Table 5 caption) — derived/comparative interpretation of the AP gap sizes.

## 13. Interpretations (authors' explanations — label as interpretation)
- Authors interpret the human-rating vs. AP discrepancy on COCO/LVIS as: "ViTDet learns the specific biases of COCO masks... SAM, being a zero-shot method, is unable to exploit these (generally undesirable) biases" (L654) — interpretation.
- "these results indicate that SAM has learned to segment valid masks from a single point" (L464) — interpretation drawn from the human study.
- On fairness findings: "We believe our findings stem from the nature of the task, and acknowledge biases may arise when SAM is used as a component in larger systems" (L288) — interpretation.
- On why SAM predicts more edges than BSDS500 ground truth: attributed to SAM not learning "the biases of BSDS500, i.e., which edges to suppress" (L565) — interpretation.
- "we anticipate that composable system design... will enable a wider variety of applications than systems trained specifically for a fixed set of tasks" (L93, Discussion) — interpretation/expectation, not a measured result.

## 14. Hypotheses / speculation
- "We hypothesize that SAM's ability to output multiple masks is especially valuable for this [object-proposal] task, since recall should benefit from proposals generated at multiple scales" (L1321, App. D.3) — explicit hypothesis framing, tested via the single-output ablation.
- "We hypothesize that on COCO, where the mask AP gap is larger... ViTDet learns the specific biases of COCO masks" (L654) — explicitly labeled hypothesis by the authors.
- Latent-space probing (App. D.6) is explicitly called "an initial investigation" / "preliminary": "these results are preliminary, they indicate that the representations from SAM may be useful for a variety of purposes" (L1349–1353) — speculative, author-labeled as preliminary.
- "Whether SAM achieves the status of a foundation model remains to be seen by how it is used in the community" (Conclusion, L736) — explicit open question, not resolved by the paper.

## 15. Limitations (only those stated by the authors, or scope boundaries derived from stated conditions)
Stated directly in the Limitations paragraph (§8, L735):
- SAM "can miss fine structures, hallucinates small disconnected components at times, and does not produce boundaries as crisply as more computationally intensive methods that 'zoom-in'."
- Dedicated interactive segmentation methods are expected to outperform SAM "when many points are provided" — SAM is "designed for generality and breadth of use rather than high IoU interactive segmentation."
- "SAM's overall performance is not real-time when using a heavy image encoder" (only the prompt encoder/mask decoder stage is ~50ms; the image encoder is not).
- The text-to-mask capability is explicitly called "exploratory and not entirely robust."
- "it is unclear how to design simple prompts that implement semantic and panoptic segmentation."
- Domain-specific tools (e.g., ilastik [7]) are expected to outperform SAM "in their respective domains."
- **Scope boundary (derived from stated conditions)**: the fairness analysis by skin tone relies on a "proprietary dataset" (L288) not released with the paper — findings on that axis cannot be independently reproduced from released artifacts.
- **Scope boundary (derived from stated conditions)**: SA-1B "only includes automatically generated masks" (L141), so any model trained purely on the released dataset should be expected to reproduce only the fully-automatic-stage data distribution, not the full data-engine's manual/semi-automatic mask distribution described in the ablation (Fig. 13 left panel, L674).

## 16. Actual contribution
As explicitly stated in the Conclusion (L736): "Our principal contributions are a new task (promptable segmentation), model (SAM), and dataset (SA-1B) that make this leap [toward foundation models for segmentation] possible." Supporting concrete contributions documented in the snapshot: the SA-1B dataset (1.1B masks / 11M images) and its accompanying data engine; the SAM architecture (image encoder / prompt encoder / mask decoder) enabling near-real-time promptable mask prediction; empirical zero-shot transfer results across five tasks; and an RAI fairness analysis of both dataset and model.

## 17. Unsupported or weakly supported claims (thin support in the snapshot — no outside criticism)
- The text-to-mask capability (§7.5) is presented with only qualitative figure examples (Fig. 12) and no quantitative evaluation — the authors themselves label it a "proof-of-concept" (L671), so its generalization beyond the shown examples is not established in the snapshot.
- The latent-space semantic-probing analysis (App. D.6) is based on "3 examples" (L1349) of qualitative nearest-neighbor comparison — too small a sample within the snapshot to support any general claim about SAM's representation quality; the authors themselves call it preliminary.
- The claim that concavity distribution of SA-1B masks is "broadly similar" to other datasets (§5, L222) is based on Fig. 6 (right panel), whose actual concavity values are not present in `paper.txt` — the comparison cannot be independently checked from the snapshot text alone.
- The Table 4 AR@1000 breakdown by object-size/frequency bucket has ambiguous column alignment after pdftotext extraction (see PROJECT_ASSESSMENT.md Risk 2); numeric claims sourced from this table carry elevated uncertainty about exact value-to-column mapping.

## 18. Claim → evidence → source table
| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| SA-1B has 1.1B masks / 11M images | measured/reported | dataset statistic | paper §5, L60 | "more than 1B masks from 11M licensed and privacy-preserving images" |
| SAM beats RITM on 16/23 datasets, up to ~47 IoU | measured | mIoU comparison | paper §7.1, L461 | "SAM yields higher results on 16 of the 23 datasets, by as much as ∼47 IoU" |
| SAM oracle beats RITM on all 23 datasets | measured | oracle mIoU | paper §7.1, L461 | "with the oracle to perform ambiguity resolution, SAM outperforms RITM on all datasets" |
| Automatic mask quality: 94%/97% IoU thresholds | measured | human-corrected mask comparison | paper §5, L142 | "94% of pairs have greater than 90% IoU (and 97%... greater than 75%)" |
| SAM COCO instance-seg AP 46.5 vs ViTDet-H 51.0 | measured | Table 5 | paper §7.4, L608–614 | "ViTDet-H 51.0... SAM 46.5" (Table 5, COCO AP column) |
| SAM edge detection R50 .928 vs HED .923 | measured | Table 3 | paper §7.2, Table 3 | "SAM... R50 .928" (Table 3) |
| ViTDet exploits COCO/LVIS annotation biases (SAM cannot) | interpretation | authors' explanation of AP-vs-rating gap | paper §7.4, L654 | "ViTDet learns the specific biases of COCO masks" |
| SAM misses fine structures, hallucinates small components | limitation (stated) | authors' Limitations paragraph | paper §8, L735 | "can miss fine structures, hallucinates small disconnected components at times" |
| Text-to-mask is exploratory, not robust | limitation (stated) | authors' own characterization | paper §7.5/§8, L671, L735 | "exploratory and not entirely robust" |
| Data engine: 4.3M masks from 120k images (stage 1) | measured | data collection statistic | paper §4, L133 | "we collected 4.3M masks from 120k images in this stage" |
| Training: 90k iterations, batch 256, lr 8e-4, 256 GPUs | measured | training recipe | paper App. A, L1004 | "We train for 90k iterations (∼2 SA-1B epochs)... batch size is 256 images" |
| Skin-tone fairness dataset is proprietary | scope boundary (derived) | dataset provenance statement | paper §6, L288 | "a proprietary dataset that contains annotations for the perceived Fitzpatrick skin type" |
| README covers only code/checkpoints/dataset schema, no results | artifact fact (README-only) | README structure | README L30–156 | "Installation... Model Checkpoints... Dataset" (README section headers) |
| Ablation trend: automatic-only data ~0.5 mIoU below all-stage data | derived (from figure, values NOT IN SNAPSHOT) | prose description of Fig. 13 | paper §7.6, L674 | "SAM performs only marginally lower than using all data (∼0.5 mIoU)" |
