# Gold Account v1 — SAM (Segment Anything)

Verified version of `GOLD_ACCOUNT_DRAFT.md`. Basis: `evaluation/external_projects/SAM/snapshot/paper.txt` (arXiv 2304.02643v1, pdftotext) and `README__facebookresearch__segment-anything.md`. **The paper is authoritative for all research claims; the README is used only for artifact facts** (checkpoints, license, dataset JSON schema). "L##" = `paper.txt` line numbers. See `VERIFICATION.md` for the issue table.

## Changes from draft
1. **Table 4 (LVIS AR@1000) re-mapped** (high). The pdftotext block is resolvable; corrected values in §10. Draft had ViTDet-H medium = 76.7 (actually single-output SAM's) and garbled SAM common/rare values. The draft's "ambiguous alignment" caveat is removed from §17.
2. **Paper-internal conflict flagged**: text says SAM outperforms ViTDet-H on large objects, but Table 4 gives 86.9 vs 87.0 (§10, §19).
3. **Human-rating study input condition added**: Fig. 11 ratings used LVIS ground-truth boxes for both models (794 subsampled inputs), not the ViTDet boxes used for AP (§8, §10, §11).
4. **De-strengthened mask-quality claim**: 94%/97% is presented *alongside* prior 85–91% inter-annotator IoU, not as "exceeding" it (§11).
5. **Limitations (§15)**: removed two drafter-authored "scope boundaries" (proprietary-dataset reproducibility; automatic-only-data distribution speculation). Added the author-stated limitations the draft missed: clothing gender-presentation bias, geographic/income under-representation, downstream bias caveat, limited scope of a segmentation foundation model, saturating encoder scaling, training environmental cost, residual objectionable content, geo-inference ambiguity.
6. "SA-1B contains only automatic masks" is recorded as a justified design choice, not a limitation.
7. Minor fixes: decoder step order (§6), subsampling rule for the 23-dataset suite (§8), "on CPU" for the 50 ms figure, Fig. 6 vs §5 "largest/second largest" wording conflict noted, COCO-bias statement classified once (hypothesis), edge-detection claim wording.
8. gold_story consolidated to 36 nuggets (≤4 per question, duplicates removed) → `gold_story.v1.json`.

## 1. Problem
Build a foundation model for image segmentation: a promptable model that returns valid segmentation masks and generalizes zero-shot to new image distributions and downstream segmentation tasks via prompt engineering (L43, L49, L55).

## 2. Motivation
Foundation models pre-trained on web-scale data show strong zero-/few-shot generalization in NLP and, to a lesser extent, in vision via image-text models (CLIP, ALIGN) (L45, L48). Computer vision includes many problems beyond vision-language encoders for which "abundant training data does not exist" (L48).

## 3. Research gap
- No web-scale data source exists for segmentation masks (L55: "there is no web-scale data source for segmentation"; L59).
- Prior multi-task segmentation systems perform a fixed set of tasks where training and test tasks are the same; a promptable model can perform a new task at inference time by acting as a component in a larger system (L92).

## 4. Research question / objective
Three entangled questions (L50–51, L55): (1) what task enables zero-shot generalization; (2) what is the corresponding model architecture; (3) what data can power this task and model.

## 5. System / method
- **Promptable segmentation task** (§2): given any prompt (foreground/background points, rough box or mask, free-form text) return a "valid" mask — reasonable for at least one object the prompt could refer to (L86). Used both as pre-training objective and for downstream transfer via prompting (L56).
- **SAM** (§3): heavyweight image encoder (MAE-pretrained ViT-H/16, run once per image) + prompt encoder + lightweight mask decoder (L118–121, L947).
- **Ambiguity handling**: 3 output masks per single prompt plus a predicted-IoU score per mask; loss backpropagated only from the lowest-loss mask; with multiple prompts a fourth output token yields a single mask (L122–124, L997–998).
- **Losses**: focal:dice 20:1 for masks; MSE for IoU head, scale factor 1.0; no auxiliary deep supervision (L999).
- **Training simulation**: 11 rounds per mask — 1 initial prompt (point or noisy box, equal probability), 8 iteratively sampled error-region points, 2 rounds with no new points (L1001–1003).
- **Automatic mask generation** (App. B): 32×32 point grid on full image + 20 zoomed crops (2×2 and 4×4 windows, 16×16 and 8×8 grids); predicted-IoU filter 88.0; stability filter ≥95.0; drop masks covering ≥95% of image; NMS 0.7 within and across crops; remove components / fill holes <100 px. The SA-1B generation model was a special SAM trained on manual + semi-automatic data only, 177,656 iterations, 3-layer decoder (L1012–1017).

## 6. Architecture
- Image encoder: MAE-pretrained ViT-H/16, 14×14 windowed attention + four equally spaced global attention blocks; input 1024×1024 (rescale + pad); 16× downscaled 64×64 embedding reduced to 256 channels via 1×1 then 3×3 conv, each followed by layer norm (L947–948).
- Prompt encoder: sparse prompts → 256-d embeddings (points = positional encoding + fg/bg learned embedding; boxes = two corner embeddings; text = CLIP text encoder). Dense (mask) prompts input at 4× lower resolution, downscaled via two 2×2 stride-2 convs (4, 16 channels) + 1×1 conv to 256, added element-wise to the image embedding; a learned "no mask" embedding otherwise (L949–950, L986).
- Mask decoder: two layers, each (1) token self-attention, (2) token→image cross-attention, (3) point-wise MLP on tokens, (4) image→token cross-attention; then 4× upsampling via two 2×2 stride-2 transposed convs (64, 32 channels), a final token→image attention, and a 3-layer MLP producing a dynamic linear classifier applied point-wise (L988–996).
- Dimensions: embedding 256, MLP internal 2048 (prompt tokens only), cross-attention q/k/v reduced to 128, 8 heads (L995).
- Runtime: given a precomputed embedding, prompt encoder + mask decoder run in a web browser, on CPU, in ∼50 ms (L125). Mask decoder uses <1% of image-encoder compute (L1003).
- Encoder variants: ViT-B 91M, ViT-L 308M, ViT-H 636M parameters (Fig. 13, L719–726).

## 7. Dataset / data
- **SA-1B**: 11M licensed, privacy-protecting images and 1.1B (1,129M) masks (L139, L146). Images from a provider working directly with photographers; avg 3300×4950 px, released with shortest side 1500 px; faces and license plates blurred (L140). ∼100 masks per image on average (L59, L81). ∼2k images withheld for testing (L1669).
- 99.1% of the data engine's masks were fully automatic; **SA-1B includes only the automatically generated masks** — a design choice justified by the mask-quality analysis and the ablation (L141, L674).
- Comparisons: 11× more images and 400× more masks than Open Images; 36× more masks per image than Open Images; ADE20K has 3.5× fewer masks per image (L222). [Wording conflict: Fig. 6 caption L190 calls Open Images the "largest existing" dataset; §5 text calls it "second largest" — same ratios either way.]
- **Data engine** (§4):
  1. Assisted-manual: professional annotators with a SAM-powered browser tool; no semantic constraints; model retrained 6 times; encoder scaled ViT-B → ViT-H; time per mask 34 → 14 s (6.5× faster than COCO mask annotation, 2× slower than extreme-point box labeling); masks/image 20 → 44; 4.3M masks from 120k images (L129–133).
  2. Semi-automatic: confident masks prefilled by a box detector trained on stage-1 masks; +5.9M masks in 180k images (10.2M total); retrained 5 times; time per mask back to 34 s (excluding automatic masks); masks/image 44 → 72 (L134).
  3. Fully automatic: 32×32 grid prompting + confidence/stability filtering + NMS + zoomed crops, applied to all 11M images → 1.1B masks (L135).
- **Mask-quality check**: 500 random images (∼50k masks) corrected by professional annotators; 94% of automatic/corrected pairs >90% IoU, 97% >75% IoU; the paper cites prior inter-annotator consistency estimates of 85–91% IoU "for comparison" (L142).
- **23-dataset evaluation suite**: compiled from prior work; domains include egocentric, microscopy, X-ray, underwater, aerial, simulation, driving, painting (L1036, Table 7). Per-dataset sample counts in Table 7 are not reliably attributable in the extraction.
- Geography: country inferred from captions with an Elmo-based NER model (ambiguities acknowledged; inferred locations not released); COCO/Open Images locations via Flickr API for 24% / 18% of training images (L1020–1021).
- README-only artifact facts: dataset download requires accepting the "SA-1B Dataset Research License"; per-image JSON with COCO RLE segmentations plus bbox, area, predicted_iou, stability_score, crop_box, point_coords; checkpoints `vit_h` (default), `vit_l`, `vit_b`; model code under Apache 2.0. The README also opens with a banner for SAM 2 (a later project) — not used for research claims.

## 8. Experimental setup
Unless stated otherwise, SAM = MAE-pretrained ViT-H trained on SA-1B (automatic masks only) (L294).
- **Single-point valid mask** (§7.1, App. D.1): first point = "center" (max of interior distance transform) by default, or random point; subsequent points from the error region; N = 1, 2, 3, 5, 9. Metric: per-dataset mIoU averaged over 23 datasets; datasets with >15k masks subsampled to ∼10k masks. Default evaluates SAM's most confident mask; "oracle" = best of 3 vs ground truth. Baselines RITM (HRNet32 IT-M, COCO+LVIS), FocalClick (SegFormerB3-S2), SimpleClick (ViT-H448); RITM is the default as strongest at 1 point (L297, L1036–1041). Human study on 7 datasets (LVIS v0.5, VISOR, DRAM, IBD, NDD20, OVIS, iShape), 1000 masks per dataset, rating 1–10, comparing RITM, single-output SAM, SAM, and ground truth (L1358–1364).
- **Edge detection** (§7.2, D.2): BSDS500 200-image test set; 16×16 grid → 768 masks; no IoU/stability filtering; NMS; Sobel on unthresholded probability maps, keep outer-boundary pixels, pixel-wise max, normalize, edge NMS. Metrics ODS/OIS/AP/R50. Compared with HED, EDETR (learned) and Sobel, Canny, Felz-Hutt (L1312–1313).
- **Object proposals** (§7.3, D.3): LVIS v1 val, mask AR@1000 (frequent/common/rare measured against category-restricted GT). Modified pipeline: no crops, no IoU/stability filtering, 64×64 grid, NMS 0.9 (∼900 masks/image). Single-output ablation: 128×128 grid, NMS 0.95, random ranking. Baseline: cascade ViTDet-H with thresholds disabled — a "Detector Masquerading as Proposal generator" that games AR (L592, L1316–1321).
- **Instance segmentation** (§7.4, D.4): SAM prompted with ViTDet-H boxes on COCO and LVIS v1 val, plus one refinement iteration feeding the most confident mask back with the box; metric mask AP (L595, L1341). **Human rating study** (Fig. 11, App. E): 1000 LVIS v1 val masks, both SAM and ViTDet-H given the **LVIS ground-truth box**; Fig. 11 subsampled to 794 inputs to match 794 COCO GT ratings (L652, L1363, L1654).
- **Text-to-mask** (§7.5, D.5): CLIP ViT-L/14@336px; SAM trained with CLIP image embeddings of manually collected masks with area >100² as the first prompt (first two data-engine stages), large-scale jitter, 120k iterations, batch 128; inference with CLIP text embeddings. Qualitative only (L656, L1343–1347).
- **Ablations** (§7.6): cumulative data-engine stages (with 10× oversampling of manual/semi masks when combined) and automatic-only; 0.1M/1M/11M images; ViT-B/L/H; 23-dataset single-center-point protocol, with oracle (L673–675, L730).
- **RAI** (§6, App. C): MIAP (3.9k person masks) for perceived gender presentation and age; proprietary dataset for perceived Fitzpatrick skin type 1–6; clothing: 6.5k Open Images clothing masks inside MIAP person boxes; simulated interactive segmentation with 1 and 3 random points (L288, L1032–1033). Geographic/income representation vs COCO and Open Images (Table 1).
- **Training recipe** (App. A): AdamW (β1 0.9, β2 0.999), 250-iteration linear warmup, lr 8e-4, ×0.1 at 60k and 86,666 iterations, 90k iterations (∼2 SA-1B epochs), batch 256 images, wd 0.1, drop path 0.4, layer-wise lr decay 0.8, no augmentation, MAE ViT-H init, 256 GPUs, ≤64 masks per GPU, drop masks covering >90% of image (L1004–1008). Model card: 256 A100 GPUs for 68 hours (L1827). ViT-B/L: 180k iterations, batch 128, 128 GPUs (L1009).

## 9. Metrics
mIoU (per-dataset and 23-dataset average; 1-point, N-point, oracle); human mask-quality rating 1–10 with 95% CIs and paired t-tests/bootstrap (Table 8); ODS/OIS/AP/R50; mask AR@1000 by size and LVIS frequency; mask AP/APS/APM/APL; RAI mIoU at 1 and 3 points with 95% CIs.

## 10. Results (exact numbers)
- **§7.1**: SAM > RITM on 16 of 23 datasets, "by as much as ∼47 IoU"; with oracle, SAM > RITM on all datasets (L461). Per-dataset deltas in Fig. 9a range from +46.9 to −21.4 (GTEA) (L387–399). Human study: SAM rated substantially higher than RITM; single-output SAM lower than SAM but higher than RITM; SAM means between 7 and 9; all differences significant (L462–464, Table 8). With more points the gap between methods decreases; with random-point sampling the gap between SAM and baselines grows (L465).
- **Table 3 — BSDS500**: SAM .768/.786/.794/.928 (ODS/OIS/AP/R50); HED .788/.808/.840/.923; EDETR .840/.858/.896/.930; Sobel .539/–/–/–; Canny .600/.640/.580/–; Felz-Hutt .610/.640/.560/– (L481–559).
- **Table 4 — LVIS v1 mask AR@1000** (all / small / med / large / freq / com / rare):
  - ViTDet-H: 63.0 / 51.7 / 80.8 / 87.0 / 63.1 / 63.3 / 58.3
  - SAM single-output: 54.9 / 42.8 / 76.7 / 74.4 / 54.7 / 59.8 / 62.0
  - SAM: 59.3 / 45.5 / 81.6 / 86.9 / 59.1 / 63.9 / 65.8
  - Text (L593): SAM "outperforms ViTDet-H on medium and large objects, as well as rare and common objects" and "only underperforms… on small objects and frequent objects". **Conflict:** the table shows large 86.9 vs 87.0 (a −0.1 tie, not an outperformance).
- **Table 5 — mask AP**: COCO ViTDet-H 51.0 (32.0/54.3/68.9), SAM 46.5 (30.8/51.0/61.7); LVIS v1 ViTDet-H 46.6 (35.0/58.0/66.3), SAM 44.7 (32.5/57.6/65.5) (L608–614).
- **Fig. 11 — ratings (mean ± 95% CI, LVIS GT-box inputs)**: LVIS GT 8.6±0.06; SAM 8.1±0.07; ViTDet-H 7.9±0.08; COCO GT 7.6±0.12 (L622–630). SAM > ViTDet is statistically significant on the full 1000 ratings (L1654).
- **Table 2 — person segmentation mIoU (1 pt / 3 pt)**: feminine 54.4±1.7 / 90.4±0.6; masculine 55.7±1.7 / 90.1±0.6; older 62.9±6.7 / 92.6±1.3; middle 54.5±1.3 / 90.2±0.5; young 54.2±2.2 / 91.2±0.7; skin 1: 52.9±2.2 / 91.0±0.9; 2: 51.5±1.4 / 91.1±0.5; 3: 52.2±1.9 / 91.4±0.7; 4: 51.5±2.7 / 91.7±1.0; 5: 52.4±4.2 / 92.5±1.4; 6: 56.7±6.3 / 91.2±2.4. Caption: all CIs overlap within each grouping except older vs. middle (L262–286).
- **Table 6 — clothing mIoU (1 pt / 3 pt)**: feminine 76.3±1.1 / 90.7±0.5; masculine 81.0±1.2 / 92.3±0.4 (disjoint at 1 pt; gap closes at 3 pt); older 81.9±3.8 / 92.8±1.6; middle 78.2±0.8 / 91.3±0.3; young 77.3±2.7 / 91.5±0.9 (age differences not significant) (L1026–1033).
- **Table 1 — geography/income** (# countries, # images, # masks, % images SA-1B / COCO / Open Images): Africa 54, 300k, 28M, 2.8/3.0/1.7; Asia & Oceania 70, 3.9M, 423M, 36.2/11.4/14.3; Europe 47, 5.4M, 540M, 49.8/34.2/36.2; Latin America & Carib. 42, 380k, 36M, 3.5/3.1/5.0; North America 4, 830k, 80M, 7.7/48.3/42.8; high income 81, 5.8M, 598M, 54.0/89.1/87.5; middle income 108, 4.9M, 499M, 45.0/10.5/12.0; low income 28, 100k, 9.4M, 0.9/0.4/0.5 (L232–254). Masks per image fairly consistent across region/income (94–108) (L258).
- **Mask quality (§5)**: 94% >90% IoU; 97% >75% IoU (L142).
- **Ablations (Fig. 13; plotted values NOT IN SNAPSHOT)**: each data-engine stage increases mIoU; automatic-only ∼0.5 mIoU below all stages (L674); 1M images (∼10%, ∼100M masks) comparable to 11M, 0.1M shows a large decline (L675); ViT-H substantially better than ViT-B, marginal gains over ViT-L; "further image encoder scaling does not appear fruitful" (L730).

## 11. Supported claims (directly measured)
- SAM beats RITM at 1 center point on 16/23 datasets (up to ∼47 IoU), and on all 23 with oracle selection (L461).
- Annotators rate SAM's single-point masks higher than RITM's on all 7 human-study datasets (Table 8, L462).
- Automatic masks: 94% of pairs >90% IoU vs professional corrections (97% >75%), reported alongside prior 85–91% inter-annotator IoU estimates (L142).
- Zero-shot instance segmentation: SAM's mask AP trails ViTDet-H on COCO (46.5 vs 51.0) and LVIS (44.7 vs 46.6) (Table 5).
- With both given LVIS GT boxes, annotators rate SAM's masks higher than ViTDet-H's (8.1 vs 7.9), significant (Fig. 11, L1654).
- Edge detection: SAM's ODS/OIS/AP trail HED and EDETR but exceed the classical zero-shot methods; its R50 (.928) is above HED (.923) and just below EDETR (.930) (Table 3).
- Object proposals: SAM's overall AR@1000 (59.3) is below ViTDet-H (63.0) but higher on medium, common and rare; the multi-output SAM beats single-output SAM on all AR metrics (Table 4).
- Fairness (person): CIs overlap within each grouping except older vs. middle; no significant skin-tone difference (L286, L288).
- Fairness (clothing): masculine > feminine at 1 point with disjoint CIs (L1033).

## 12. Derived claims (comparative)
- "400× more masks than any existing segmentation dataset" (L60); 11×/400×/36× vs Open Images, 3.5× vs ADE20K per image (L222).
- Every region, including Africa, has ≥28M masks, "10× more than the total number of masks of any previous dataset" (L258).
- Annotation at 14 s/mask is 6.5× faster than COCO and 2× slower than extreme-point boxes (L133).
- The AP gap "shrinks on the higher-quality LVIS masks" (Table 5 caption).
- SAM is "reasonably close, though certainly behind ViTDet" in AP (L596).

## 13. Interpretations (authors' explanations)
- Fig. 11 caption: SAM's higher ratings despite lower AP "suggest[s] that ViTDet exploits biases in the COCO and LVIS training data" (L652).
- Human-study results "indicate that SAM has learned to segment valid masks from a single point" (L464).
- Low absolute 1-point mIoU "is the result of ambiguity" (Fig. 9 caption, L459).
- SAM predicts more edges than BSDS500 GT because it does not learn "which edges to suppress" (L565).
- SAM underperforms on small/frequent objects because ViTDet-H can learn LVIS-specific annotation biases (L593).
- Fairness findings "stem from the nature of the task" (L288).
- The vast majority of SAM's capabilities come from large-scale supervised training, not MAE self-supervision (L732).
- Composable system design is expected to enable more applications than fixed-task systems (L93) — expectation.

## 14. Hypotheses / speculation
- "We hypothesize that on COCO, where the mask AP gap is larger and the ground truth quality is relatively low…, ViTDet learns the specific biases of COCO masks" (L654).
- Multi-mask output is hypothesized to help proposal recall; tested via the single-output ablation (L1321).
- Latent-space probing (App. D.6): 3 qualitative examples; "preliminary" (L1349–1353).
- "Whether SAM achieves the status of a foundation model remains to be seen by how it is used in the community" (L736).

## 15. Limitations (author-stated only)
From §8 Limitations (L735):
- Can miss fine structures, hallucinates small disconnected components at times, and boundaries are less crisp than computationally heavier "zoom-in" methods.
- Dedicated interactive methods are expected to outperform SAM when many points are provided; SAM targets generality rather than high-IoU interactive segmentation (also L1039, L465).
- Prompts are processed in real time, but overall performance is not real-time with a heavy image encoder.
- Text-to-mask is "exploratory and not entirely robust".
- Unclear how to design simple prompts for semantic and panoptic segmentation.
- Domain-specific tools (e.g., ilastik) are expected to outperform SAM in their domains.

Stated elsewhere by the authors:
- A foundation model for image segmentation is "an inherently limited scope" (L732).
- Clothing segmentation shows a bias across perceived gender presentation at one point; "we encourage users of SAM to be mindful of this limitation" (L1033).
- Biases may arise when SAM is used as a component in larger systems; users should run their own fairness evaluation (L288, L1827).
- Africa, Latin America & Caribbean and low-income countries are under-represented in all compared datasets, including SA-1B; "we do not have parity across all groups" (L256, L1709, L1827).
- Image-encoder scaling shows "saturating gains" (L728, L730).
- Training cost: 256 A100 GPUs × 68 h, ∼6963 kWh, ∼2.8 t CO2 (L1827).
- A small portion of SA-1B images may contain potentially offensive content that filtering did not remove (L1678).
- Country inference from captions is ambiguous and may be biased; Flickr-based locations for COCO/Open Images cover only part of each dataset (L1020–1021).
- In the zero-shot setting there may be multiple valid ground-truth masks per input (model card, L1811).

## 16. Actual contribution
Conclusion (L736): "a new task (promptable segmentation), model (SAM), and dataset (SA-1B)". Concretely: the data engine and 1.1B-mask SA-1B dataset; the amortized image-encoder / prompt-encoder / mask-decoder architecture with ambiguity-aware multi-mask output; zero-shot transfer results across five tasks plus ablations; an RAI analysis of dataset and model; release of the model (Apache 2.0) and dataset (research license).

## 17. Weakly supported claims (within the snapshot)
- Text-to-mask: qualitative figure examples only (Fig. 12); authors call it a proof-of-concept (L656, L671).
- Latent-space probing: 3 qualitative examples; authors call it preliminary (L1349–1353).
- Concavity "broadly similar" to other datasets (L222): Fig. 6 values are not in the extracted text, so this cannot be checked from the snapshot.
- Ablation magnitudes other than "∼0.5 mIoU" exist only in Fig. 13 plots (NOT IN SNAPSHOT).
- SAM "outperforms ViTDet-H on … large objects" (L593) conflicts with Table 4 (86.9 vs 87.0).

## 18. Claim → evidence → source
| Claim | Type | Location | Quote (≤25 words) |
|---|---|---|---|
| SA-1B: 11M images, 1.1B masks | measured | §5 L139 | "11M diverse, high-resolution, licensed, and privacy protecting images and 1.1B high-quality segmentation masks" |
| SAM > RITM on 16/23, up to ∼47 IoU | measured | §7.1 L461 | "SAM yields higher results on 16 of the 23 datasets, by as much as ∼47 IoU" |
| Oracle SAM > RITM on all datasets | measured | §7.1 L461 | "with the oracle to perform ambiguity resolution, SAM outperforms RITM on all datasets" |
| Mask quality 94% / 97% | measured | §5 L142 | "94% of pairs have greater than 90% IoU (and 97% of pairs have greater than 75% IoU)" |
| Instance seg. AP COCO 46.5 vs 51.0; LVIS 44.7 vs 46.6 | measured | Table 5 L608–614 | "ViTDet-H 51.0 … 46.6 … SAM 46.5 … 44.7" |
| Human rating SAM 8.1 vs ViTDet-H 7.9 (LVIS GT boxes) | measured | Fig. 11 L622–652 | "both applied to LVIS ground truth boxes" |
| Edge R50 .928 vs HED .923 | measured | Table 3 | "SAM 2023 .768 .786 .794 .928" |
| Proposals AR@1000 SAM 59.3 vs ViTDet-H 63.0 | measured | Table 4 L573–581 | "ViTDet-H [62] 63.0 … SAM 59.3" |
| ViTDet exploits COCO mask biases | hypothesis | §7.4 L654 | "We hypothesize that on COCO … ViTDet learns the specific biases of COCO masks" |
| Clothing gender bias at 1 point | measured + stated limitation | App. C L1033 | "there is a bias when segmenting clothing across perceived gender presentation with a one point prompt" |
| Misses fine structures | stated limitation | §8 L735 | "can miss fine structures, hallucinates small disconnected components at times" |
| Text-to-mask exploratory | stated limitation | §8 L735 | "exploratory and not entirely robust" |
| Stage 1: 4.3M masks / 120k images | measured | §4 L133 | "we collected 4.3M masks from 120k images in this stage" |
| Automatic-only ∼0.5 mIoU below all data | measured (value in prose only) | §7.6 L674 | "SAM performs only marginally lower than using all data (∼0.5 mIoU)" |
| Training 90k iters, batch 256, 256 GPUs | reported setup | App. A L1004 | "We train for 90k iterations (∼2 SA-1B epochs)… The batch size is 256 images" |
| Checkpoints vit_h/vit_l/vit_b; SA-1B research license | artifact fact (README) | README | "Three model versions of the model are available with different backbone sizes" |

## 19. Source conflicts
- Table 4 vs L593 on large objects → table numbers authoritative; the text claim is recorded as stated and flagged.
- Fig. 6 caption ("largest existing") vs §5 ("second largest") for Open Images → wording only; ratios identical.
- README SAM 2 banner vs paper → paper authoritative for research; README used only for artifact facts.
