# Project Assessment — SAM

Snapshot basis: `evaluation/external_projects/SAM/snapshot/` (`paper.txt`, `README__facebookresearch__segment-anything.md`). Pins from `evaluation/manifests/source_snapshots.json`. Line references ("L##") refer to `paper.txt` line numbers (pdftotext output; figures/tables are frequently interleaved with surrounding prose as separate short lines).

## 1. Project description
Segment Anything (SA) is a project introducing three interconnected components for image segmentation: a **promptable segmentation task** (§2), a **segmentation model** — the Segment Anything Model (SAM) (§3) — that can be prompted with points, boxes, masks, or (experimentally) text to produce valid object masks, and a **data engine** (§4) used to collect the **SA-1B dataset** (§5) of over 1 billion masks on 11M licensed, privacy-respecting images. SAM is evaluated zero-shot on five downstream tasks (§7) and the paper includes a Responsible AI (RAI) fairness analysis (§6).

## 2. Official repository
- Repo: `facebookresearch/segment-anything` — https://github.com/facebookresearch/segment-anything
- Pinned commit: `dca509fe793f601edb92606367a655c15ac00fdf`
- Snapshot README URL: https://github.com/facebookresearch/segment-anything/blob/dca509fe793f601edb92606367a655c15ac00fdf/README.md (sha256 `cab2c490…4cdbce1`)
- The README is a code/checkpoint/dataset-format usage guide (installation, `SamPredictor`/`SamAutomaticMaskGenerator` API, ONNX export, three checkpoint links by backbone size, SA-1B JSON annotation schema, Apache 2.0 license, citation). It contains no experimental results.
- The README's top banner ("Latest updates") announces **SAM 2** (a successor project, video segmentation, arXiv 2408.00714) as of the pinned commit — this is a repo-only fact, not part of the SAM paper.

## 3. Paper / report
- arXiv: **2304.02643v1** (5 Apr 2023), cs.CV. PDF sha256 `c6ca524e…d90cfb`; `paper.txt` 26,591 words.
- Venue (confirmed via web, outside snapshot): published in *Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV) 2023*, pp. 4015–4026 — a peer-reviewed venue.
  - https://openaccess.thecvf.com/content/ICCV2023/html/Kirillov_Segment_Anything_ICCV_2023_paper.html
  - https://arxiv.org/abs/2304.02643
- The snapshot text itself carries no "under review" / venue marker (no header banner in `paper.txt`); the ICCV publication is a web-confirmed fact and is recorded here for context only — the Gold Account (Output 2) treats the snapshot arXiv v1 text as authoritative for all research content and does not assume ICCV camera-ready wording matches v1 verbatim.

## 4. Datasets
| Dataset | Role | Snapshot location | Availability |
|---|---|---|---|
| SA-1B | Introduced by this paper; 1.1B masks, 11M images (99.1% fully-automatically generated) | §5, L138–142 | Paper: "we are releasing SA-1B" (L43, L139); README: download link + license, JSON/COCO-RLE schema (README L116–156) |
| 23-dataset zero-shot evaluation suite | Compiled by the authors from prior work for evaluating point-prompt segmentation | §7.1, Appendix Table 7, L1045–1293 | Existing public datasets (per-dataset citations); names, image type, and split legible; some per-dataset image/mask sample counts in Table 7 are extraction-damaged (see Risks) |
| LVIS v1 | Object proposal generation (§7.3) and instance segmentation (§7.4) evaluation | L589, L604 | Public, cited [44] |
| COCO | Instance segmentation evaluation (§7.4) | L602 | Public, cited [66] |
| BSDS500 | Zero-shot edge detection evaluation (§7.2) | L563, L1311 | Public, cited [72, 3] |
| MIAP (More Inclusive Annotations for People) | Fairness analysis — gender/age (§6, App. C) | L288, L1032 | Public, cited [87] |
| Proprietary skin-tone dataset | Fairness analysis — perceived skin tone (§6) | L288 | "a proprietary dataset" — **NOT publicly available** (paper's own wording) |

## 5. Benchmark / evaluation material
- §7.1–7.6 define five zero-shot transfer tasks (single-point valid mask, edge detection, object proposals, instance segmentation, text-to-mask) plus an ablation study, each with its own metric and baseline(s).
- Appendix §D gives per-task implementation details (point sampling protocol, dataset subsampling to ~10k masks, baseline model variants used).
- Appendix §E describes the human mask-quality-rating study (1–10 scale, guidelines in §G, 30 annotators, ~1000 masks/dataset, single annotator per job, inter-annotator SD of 0.83 in initial 5-annotator pilot, L1365).
- Appendix §B gives the exact automatic-mask-generation pipeline (crop grid, NMS thresholds, filtering thresholds) used to build SA-1B and to run zero-shot evaluations.

## 6. Available experimental evidence (in snapshot)
- Zero-shot single-point mIoU on 23 datasets vs. RITM/SimpleClick/FocalClick, plus an "oracle" variant and a human quality-rating study (§7.1, Fig. 9).
- Zero-shot edge detection on BSDS500 vs. HED, EDETR, Sobel, Canny, Felz-Hutt (Table 3).
- Zero-shot object proposal generation on LVIS v1 vs. ViTDet-H and an ablated single-output SAM (Table 4).
- Zero-shot instance segmentation on COCO/LVIS vs. ViTDet-H, with a supplementary human rating study (Table 5, Fig. 11).
- Zero-shot text-to-mask: qualitative only, described as "a proof-of-concept... exploratory and not entirely robust" (L671, L735) — **no quantitative metric reported**.
- Ablations (Fig. 13): data-engine stage contribution, training-data volume (0.1M/1M/11M images), image-encoder scale (ViT-B/L/H) — **plotted in a figure; no numeric axis values are present in `paper.txt`**, only the prose description of trends (e.g., "training with only the automatic data... performs only marginally lower... (∼0.5 mIoU)", L674).
- RAI fairness study: mIoU by perceived gender/age/skin tone for person segmentation (Table 2) and clothing segmentation (Table 6, Appendix C).
- Mask-quality validation: 500-image / ~50k-mask sample, IoU between automatic and professionally corrected masks (§5, L142).

## 7. Available result evidence (numbers legible in snapshot)
- Data engine: stage 1 — 4.3M masks / 120k images, annotation time 34→14 s/mask (L133); stage 2 — +5.9M masks / 180k images (10.2M total), annotation time back up to 34s, masks/image 44→72 (L134); stage 3 (fully automatic) — 1.1B masks over all 11M images (L135).
- Mask-quality check: 94% of pairs >90% IoU, 97% >75% IoU, vs. prior inter-annotator consistency of 85–91% IoU (L142).
- Table 3 (BSDS500 edge detection): SAM ODS .768 / OIS .786 / AP .794 / R50 .928; HED ODS .788/.808/.840/.923; EDETR .840/.858/.896/.930; Canny .600/.640/.580/–; Felz-Hutt .610/.640/.560/–; Sobel .539/–/–/– (L481–560).
- Table 4 (LVIS AR@1000): ViTDet-H all=63.0; SAM=59.3 (single-output=54.9); SAM outperforms ViTDet-H on medium (81.6 vs 76.7 — note: exact row/column alignment in the pdftotext extraction is ambiguous, see Risks), large, common, and rare objects, underperforms on small and frequent objects (L569–593).
- Table 5 (instance segmentation AP): ViTDet-H COCO AP 51.0 / LVIS AP 46.6; SAM COCO AP 46.5 / LVIS AP 44.7 (L600–616).
- Fig. 11 human ratings (mean ± 95% CI): LVIS GT 8.6±0.06; SAM 8.1±0.07; ViTDet-H 7.9±0.08; COCO GT 7.6±0.12 (L622–630).
- Table 2 (RAI, person segmentation, 1pt/3pt mIoU): gender feminine 54.4±1.7/90.4±0.6, masculine 55.7±1.7/90.1±0.6; age older 62.9±6.7/92.6±1.3, middle 54.5±1.3/90.2±0.5, young 54.2±2.2/91.2±0.7; skin tone (Fitzpatrick 1–6) 1: 52.9±2.2/91.0±0.9 … 6: 56.7±6.3/91.2±2.4 (L262–286). Text notes "all conﬁdence intervals overlap except older vs. middle" (caption, L286).
- Table 6 (RAI, clothing segmentation, App. C): gender feminine 76.3±1.1/90.7±0.5, masculine 81.0±1.2/92.3±0.4 (disjoint at 1pt); age older 81.9±3.8/92.8±1.6, middle 78.2±0.8/91.3±0.3, young 77.3±2.7/91.5±0.9 (L1026–1033).
- Table 1 (RAI, geographic/income representation): numbers are present but pdftotext has flattened the table into a single block per region (e.g., "Asia & Oceania 70 3.9M 423M 36.2% 11.4% 14.3%", L236–238) — legible per-row but column headers ("#countries #imgs #masks SA-1B COCO O.I.") are separated from the data rows; recorded with caution.
- Automatic mask generation thresholds (App. B): predicted-IoU filter ≥88.0, stability IoU ≥95.0, image-coverage filter <95%, small-component/hole cleanup <100 px (~4% of masks affected each) (L1010–1016).
- Training recipe (App. A): AdamW, lr 8e-4 after 250-iter warmup, 90k iterations (~2 SA-1B epochs), batch size 256, wd 0.1, drop path 0.4, layer-wise lr decay 0.8, 256 GPUs, ≤64 masks/GPU (L1004–1008). Mask decoder runs in ~50ms in a browser given a precomputed embedding (L57, L125).
- Image resolution: 3300×4950 avg native, released downsampled to 1500 px shortest side (L140).

## 8. Source quality
- **Authoritative:** `paper.txt` (official arXiv v1 text by the project authors) for all research claims — task definition, model design, data engine, dataset statistics, experiments, results, RAI analysis, limitations.
- **Authoritative for artifact facts only:** README at pinned commit (installation, checkpoint links, SA-1B annotation JSON schema, license, citation, and the SAM 2 follow-up pointer).
- **Secondary / outside snapshot:** ICCV Open Access page (used only for venue confirmation in this assessment, not folded into the Gold Account's research content).
- Numerous figures (Fig. 2, 5, 6, 7, 9, 13, 15, 16, 17) carry data or qualitative comparisons that are **not recoverable as numbers from `paper.txt`**; only prose descriptions and captions survive pdftotext extraction.

## 9. Reproducibility / accessibility
- Code: open source (`facebookresearch/segment-anything`), Apache 2.0 license, checkpoints for ViT-B/L/H publicly downloadable (README).
- Dataset: SA-1B is separately licensed under an "SA-1B Dataset Research License" (README L118) distinct from the code's Apache 2.0 license; images are released downsampled with faces/plates blurred (paper L140).
- Full training (256 GPUs, 90k iterations on 1.1B masks) is not practically reproducible by most readers; the released checkpoints and inference code are reproducible.
- Not re-executed for this assessment; assessment is based solely on the frozen snapshot text.

## 10. Suitability for this evaluation
- **Methodology reconstructable?** Yes. Task, model architecture (image encoder / prompt encoder / mask decoder), data engine (3 stages), and training recipe are described in enough prose + appendix detail to reconstruct at a design level without inventing anything.
- **Experiments & results identifiable?** Yes for five described tasks with tables (edge detection, object proposals, instance segmentation, single-point mIoU narrative, RAI fairness); the text-to-mask task is explicitly qualitative/exploratory with no metric, which the Gold Account must preserve as such. Several supporting figures (data-scaling ablation, dataset-property comparison) are not numerically recoverable and must be marked NOT IN SNAPSHOT.
- **Gold Account without guessing?** Yes, provided ablation figure values, Table 7 sample counts (which are position-ambiguous after extraction), and ViTDet-H Table 4 column alignment are flagged rather than asserted.
- Evaluation value: a large, richly detailed foundation-model paper with an explicit stated Limitations paragraph (§8, L735), multiple quantitative result tables, and a genuine paper-vs-README artifact distinction (README covers only code/checkpoints/dataset schema, no results) — a strong test of whether a reader can separate "what the paper measured" from "what the repo lets you do."

## 11. Risks
1. **Figure-only results (pdftotext):** Fig. 13 (ablations: data-engine stage, data volume, encoder scale) — trend descriptions survive in prose (L730, L674, L675) but exact mIoU values plotted are NOT IN SNAPSHOT. Fig. 5, 6, 7 (dataset property comparisons, geographic map) are images; only captions and comparative prose ("11× more images and 400× more masks than... Open Images", L190) survive.
2. **Table 4 (LVIS AR@1000) column/row alignment risk:** the pdftotext extraction interleaves header tokens ("all small... med. large freq.... com. rare") with two data rows in a way that requires care in mapping numbers to columns (L569–587); the Gold Account records the values conservatively and flags this location.
3. **Table 7 (23-dataset appendix) sample counts:** the "# images / # masks sampled" numeric block (L1227–1291) is extracted separately from the dataset name rows above it and cannot be reliably matched to individual dataset names row-by-row; recorded as illegible/not confidently attributable.
4. **Table 1 (RAI geo/income) header-data separation:** column headers and per-region data rows are pdftotext-separated (L230–256); values are legible per row but require the reader to hold the header order in mind — recorded with an explicit caveat.
5. **Repo diverged from paper:** the pinned README's banner promotes **SAM 2** (2024, video segmentation) ahead of any SAM-specific content — a later, related project, not a paper update. The Gold Account restricts all research claims to the arXiv v1 paper and uses the README only for artifact facts (checkpoints, license, JSON schema).
6. **Peer-review venue not stated in the snapshot text itself:** the ICCV 2023 publication is confirmed only via external web search, not from `paper.txt`, and is reported here for context, not scored as a snapshot fact.
7. **Skin-tone dataset is proprietary:** the fairness-by-skin-tone results (Table 2 right, Table 6 not applicable) rely on a dataset explicitly stated as "proprietary" (L288) and therefore not independently checkable — this is a source-quality caveat, not a defect in the snapshot.

## 12. Recommendation: **ACCEPT**
Reasons:
- The paper is long and unusually well-documented: task/model/data-engine design, training recipe, five distinct zero-shot experiments with numeric tables, an explicit RAI fairness study with numeric breakdowns, and an explicit author-written Limitations paragraph (§8) all fully support Q1–Q11 reconstruction from the snapshot.
- The README is a clean artifact-only source (usage, checkpoints, dataset schema) with no results, making the paper-vs-README separation rule easy to apply correctly and easy to score.
- Caveats carried into Output 2/3: (a) ablation figure values (Fig. 13) and dataset-property figures (Fig. 5–7) are NOT IN SNAPSHOT; (b) Table 4 and Table 7 numeric alignment requires conservative handling; (c) the text-to-mask "experiment" is qualitative only and must not be scored with invented metrics; (d) the skin-tone fairness dataset is proprietary, limiting independent verification of that sub-claim.

Sources used for venue/peer-review confirmation:
- https://openaccess.thecvf.com/content/ICCV2023/html/Kirillov_Segment_Anything_ICCV_2023_paper.html
- https://arxiv.org/abs/2304.02643
