# Project Assessment — MLPERF_TINY

Snapshot basis: `evaluation/external_projects/MLPERF_TINY/snapshot/` (`paper.txt`, `README__mlcommons__tiny.md`). Pins from `evaluation/manifests/source_snapshots.json`. Line references ("L##") refer to `paper.txt` line numbers (pdftotext output; one paragraph per line in most places).

## 1. Project description
MLPerf Tiny is a benchmark suite for ultra-low-power "TinyML" inference systems (microcontrollers, DSPs, tiny NN accelerators). The paper (v0.5 of the suite) defines four benchmarks — keyword spotting (KWS), visual wake words (VWW), image classification (IC), anomaly detection (AD) — each with a dataset, reference model, and quality target (Table 1, L39–50); a modular reference implementation; closed and open submission divisions (§5.2); and a measurement framework for accuracy, latency, and energy (§5.3, Appendix A). It reports reference-model accuracies (§4), reference latency/energy in a figure (Figure 5), and a qualitative summary of the first submission round (Table 2, §6).

This is a **benchmark / methodology paper**, not a method-vs-baseline paper. Its "experiments" are (a) reference-model accuracy evaluations, (b) reference latency/energy runs on one board, and (c) a descriptive summary of the v0.5 submissions.

## 2. Official repository
- Repo: `mlcommons/tiny` — https://github.com/mlcommons/tiny
- Pinned commit: `4addd0fa08d216e20637637874e084895f289da4`
- Snapshot README URL: https://github.com/mlcommons/tiny/blob/4addd0fa08d216e20637637874e084895f289da4/README.md (sha256 `eea982c3…ab86`)
- The README is short (43 lines): purpose statement, device-class statement, TFLM note, version table (v0.5–v1.1), next-round deadline (v1.2, March 15 2024 "expected"), citation. It contains no benchmark details or results.

## 3. Paper / report
- arXiv: **2106.07597v4** (24 Aug 2021), cs.LG. PDF sha256 `3c4a2271…421c`; `paper.txt` 7,464 words.
- Snapshot text header says "Preprint. Under review." (L14).
- Venue (confirmed via web, outside snapshot): published in *Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks 1 (NeurIPS Datasets and Benchmarks 2021), Round 1*, with an OpenReview forum (peer-reviewed track).
  - https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/da4fb5c6e93e74d3df8527599fa62642-Abstract-round1.html
  - https://openreview.net/forum?id=8RxxwAut1BI
  - The README citation also names the NeurIPS Datasets and Benchmarks track (README L34–38).
- Note: the proceedings page lists 19 authors; the arXiv v4 snapshot lists 23 (L4–8). The snapshot text (arXiv v4) may therefore differ in minor ways from the proceedings version. The Gold Account uses arXiv v4 only.

## 4. Datasets
All four are pre-existing public datasets. MLPerf Tiny introduces no new dataset; it selects subsets and preprocessing:
| Benchmark | Dataset (paper) | Snapshot location | Availability |
|---|---|---|---|
| KWS | Speech Commands v2 (105,829 utterances, 2,618 speakers); 10 words + "unknown" + "silence" = 12 classes | §4.3 L67 | Paper: "freely available for download under the Creative Commons BY license" (L67) |
| VWW | Visual Wake Words derived from MSCOCO 2014; person >2.5% of image; resized 96x96 | §4.1 L54 | Public (MSCOCO/VWW; paper cites [6], [15]); not re-verified |
| IC | CIFAR-10 (60000 32x32x3 images, 10 classes) | §4.2 L59 | Public (URL given in ref [14]) |
| AD | DCASE2020 Task 2 data (ToyADMOS + MIMII), Toy-car machine type only | §4.4 L72 | Public (paper says "two publicly available sources", L72) |

## 5. Benchmark / evaluation material
- Table 1 (L39–50): use cases, datasets with input size, models with TFLite size, quality targets.
- §4.1–4.4: per-benchmark rationale, dataset, model, quality target (with reference accuracy numbers).
- §5 run rules: modular design, closed/open divisions, measurement procedure.
- Appendix A: framework hardware (host PC, runner GUI, DUT, IO Manager = Arduino UNO, EMON = LPM01A / Joulescope JS110 / Keysight N6705), firmware API, runner software.
- The evaluation test subsets (200 CIFAR-10 images, 1000 utterances, 248 AD samples) are described but their identities are NOT IN SNAPSHOT.

## 6. Available experimental evidence (in snapshot)
- Reference model accuracy evaluations (§4.1–4.4): stated in prose with exact numbers.
- Reference implementation latency/energy on NUCLEO-L4R5ZI: **only in Figure 5, whose values are not present in `paper.txt`** (image). Text says only that the four benchmarks "cover a wide scope" and each reference meets minimum accuracy (L97).
- v0.5 submission round summary (Table 2, §6.1–6.2): descriptive; no performance numbers in the text.
- No ablations, no statistical tests, no repeated-trial variance reported (the latency/energy procedure uses a median of five runs by design, L94–96).

## 7. Available result evidence (numbers legible in snapshot)
- VWW: "about 86%" (L56); target 80%.
- IC: 86.5% on 200 test images (L61–64); target 85%.
- KWS: 92.2% "in our experiments" (L68); quantized 91.6% full test set, 91.7% 1000-utterance subset (L69); target 90%.
- AD: AUC 0.88 fp32, 0.86 quantized on 248 samples (L77); target 0.85.
- Model sizes: DS-CNN 52.5 KB, MobileNetV1 325 KB, ResNet 96 KB, FC-AutoEncoder 270 KB (Table 1); DS-CNN 38.6K parameters (L68).
- Submission power range "from µWatts to Watts" (L189).
- Latency/energy numbers: NOT IN SNAPSHOT.
- External results pages (mlcommons.org, tiny_results_v0.5 GitHub) are referenced but not in snapshot.

## 8. Source quality
- **Authoritative:** `paper.txt` (official arXiv v4 text by the benchmark authors) for all research claims.
- **Authoritative for artifact facts only:** README at pinned commit (versions, release dates, citation, repository pointers).
- **Secondary / outside snapshot:** NeurIPS proceedings page and OpenReview (used only for venue confirmation in this assessment, not in the Gold Account's research content).
- Much of §6.2 ("Insights") is qualitative author description of submitters' goals, partly phrased in promotional terms by or about submitters (e.g., "outstanding performance", L190). These are recorded as interpretation / reported statements, not measured evidence.

## 9. Reproducibility / accessibility
- Code: open source at mlcommons/tiny; v0.5 tag exists per README (L24). Paper states reference implementations include training scripts, pre-trained models, C code (L36).
- Submissions: paper says each is public on GitHub with reproduction instructions (L186); README confirms `tiny_results_v0.5` repo (L24).
- Hardware dependency: energy measurement requires physical EMON and IO Manager hardware (App. A.1); reproduction by readers is hardware-bound. This is an accessibility observation, not a claim from the paper.
- Not re-executed for this assessment.

## 10. Suitability for this evaluation
- **Methodology reconstructable?** Yes. Benchmark definitions, models, datasets, quality targets, divisions, and measurement procedure are all described in prose.
- **Experiments & results identifiable?** Partially. Accuracy results are clear and numeric. The latency/energy results exist only in a figure and are not recoverable from the snapshot text; submission results are external. The "results" of the paper are therefore mostly (i) reference accuracies/thresholds and (ii) qualitative observations about the first round.
- **Gold Account without guessing?** Yes, provided the Gold Account records Figure 5 values and Table 2 check marks as NOT IN SNAPSHOT / illegible. The resulting story is distinctive and testable (four benchmarks, three metrics, two divisions, specific thresholds and accuracies).
- Evaluation value: a useful contrast case to method papers — the reader must reconstruct a *benchmark design* and avoid inventing performance comparisons that the paper does not make.

## 11. Risks
1. **Figure-only results (pdftotext):** Figure 5 (reference latency/energy), Figures 1–4 and 6 are images; no values extracted. Readers who saw the PDF could cite Figure 5 numbers the Gold Account cannot score.
2. **Table 2 extraction damage:** check marks (modification indicators) were dropped; only "X" (unmodified) and text cells survive (L104–184). Which components were modified in the open-division row is only partially legible.
3. **Table 1 flattened:** column cells extracted row-wise; alignment is recoverable by order and is cross-validated by §4 prose (all four sizes/targets match).
4. **Repo diverged from paper:** README lists v0.7 (Apr 2022), v1.0 (Nov 2022), v1.1 (Jun 2023), and upcoming v1.2 (README L18–27). Later versions and results supersede the paper's v0.5 content for current use; the paper remains authoritative for this study's research claims.
5. **Venue status mismatch in snapshot:** paper text says "Preprint. Under review."; README citation and web sources show NeurIPS 2021 Datasets & Benchmarks publication.
6. **Internal inconsistencies in paper text** (see Gold Account §17): §5.2 sentence about green components vs Figure 2 caption; §3 referencing Table 1 as summarizing the need; accuracy procedure says "validation inputs" while §4 describes test subsets; broken citation "citekim20191" (L23).
7. **Author-list difference** between arXiv v4 and proceedings (outside snapshot; low impact).

## 12. Recommendation: **ACCEPT WITH CAVEATS**
Reasons:
- Methodology, benchmark definitions, and numeric accuracy results are fully legible and exact; a factual Gold Account can be written without guessing.
- The paper is short (~7.5k words), well-structured, and has an explicit Limitations section (§8), which supports Q9/Q11 scoring from the snapshot.
- Caveats: (a) latency/energy results (Figure 5) are NOT IN SNAPSHOT — scorers must not reward or penalize specific latency/energy numbers; (b) Table 2 check marks are lost; (c) README reflects later versions (v0.7–v1.2) — README content must not be scored as paper findings; (d) the "results" are thin by design (benchmark paper), so Q7/Q8 nuggets rely on reference accuracies and qualitative submission observations.

Sources used for venue/peer-review confirmation:
- https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/hash/da4fb5c6e93e74d3df8527599fa62642-Abstract-round1.html
- https://openreview.net/forum?id=8RxxwAut1BI
- https://arxiv.org/abs/2106.07597
