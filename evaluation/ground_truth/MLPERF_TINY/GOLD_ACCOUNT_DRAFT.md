# Gold Account Draft — MLPERF_TINY (snapshot-only)

Not a paper — a factual ledger built only from `evaluation/external_projects/MLPERF_TINY/snapshot/`
(`paper.txt` = arXiv 2106.07597v4, pdftotext extraction; `README__mlcommons__tiny.md` = mlcommons/tiny
README at commit `4addd0fa08d216e20637637874e084895f289da4`). Line refs ("L##") are `paper.txt` line
numbers unless marked README. Per the assessment: **the paper is authoritative for research claims;
the README is authoritative only for artifact facts** (versions, dates, repo pointers, citation).

## 1. Problem
TinyML systems (ultra-low-power microcontrollers, DSPs, tiny NN accelerators) lack "a widely accepted
and easily reproducible benchmark," which limits continued progress in the field (Abstract, L10).
Comparing TinyML solutions directly is "challenging," and "the impact of individual optimizations is
difficult to measure" without a fair, reliable comparison method (§1, L17).

## 2. Motivation
Edge/near-sensor ML inference is attractive for "increasing energy efficiency..., privacy,
responsiveness, and autonomy of edge devices," and avoids the energy cost of wireless communication,
which is "far higher than that of compute" at this scale (§1, L12) — authors' interpretation/motivating
claim, not a measured result in this paper. TinyML is said to enable "a class of smart, battery-powered,
always-on applications that can revolutionize the real-time collection and processing of data" (§1, L12)
— interpretation.

## 3. Research gap
§3 Related Work (L29–33) states no existing hardware benchmark accurately represents TinyML workloads:
- EEMBC CoreMark: does not profile full programs, "nor does it accurately represent machine learning
  inference workloads" (L31).
- EEMBC MLMark: uses models "far too large for MCU-class devices," requiring "far too much memory
  (GBs)"; lacks power measurement (L32).
- MLPerf (large-scale): "precludes MCUs and other resource-constrained platforms due to a lack of small
  benchmarks and compatible implementations" (L33).
These are the paper's own characterizations of prior work, not independently verified here.

## 4. Research question / objective
Present "MLPerf Tiny, an open-source benchmark suite for TinyML systems" that "measures the accuracy,
latency, and energy of machine learning inference to properly evaluate the tradeoffs between systems"
(Abstract L10; §1 L18), with a modular design so submitters can demonstrate value "regardless of where
it falls on the ML deployment stack" (Abstract, L10).

## 5. System / method
- Four benchmarks, each specifying a dataset, a reference model, and a quality target (§4, L35; Table 1,
  L39–50): Keyword Spotting (KWS), Visual Wake Words (VWW), Image Classification (IC), Anomaly Detection
  (AD).
- Reference implementations include training scripts, pre-trained models, and C code, run as TFLite
  models via TFLite for Microcontrollers (TFLM) on the NUCLEO-L4R5ZI board, "built using a bare-metal
  MBED project with the GCC-ARM toolchain" (§4, L36).
- Modular design: reference implementation components can be swapped; green components may be modified
  in either division, orange components only in the open division (Figure 2 caption, L76). NOTE: §5.2's
  prose (L86) states this the opposite way ("If only the components shaded in green are modified then
  the submitter can submit to the open division") — an apparent internal inconsistency in the snapshot;
  recorded, not resolved, here (see §17).
- Closed division: "must use the same models, datasets, and quality targets as the reference
  implementation," permits post-training quantization with provided calibration data, "prohibits any
  retraining or weight replacement" (§5.2, L87).
- Open division: allows changing model, training scripts, and dataset; still uses the same test dataset
  for accuracy but is not required to meet the accuracy threshold; each submission "must document how it
  deviates from the reference implementation" (§5.2, L88).

## 6. Architecture
(Appendix A, L233–260) Benchmark framework = host PC + a GUI "runner" application + the device under
test (DUT) + a thin firmware shim on the DUT.
- Two hardware configurations (Figure 3): (a) latency/accuracy — host PC talks directly to DUT via
  serial port; (b) energy — adds an IO Manager (electrical-isolation proxy, "deployed as an Arduino UNO
  with its own custom firmware," L239) and an energy monitor (EMON).
- EMON drivers supported: STMicroelectronics LPM01A, Jetperch Joulescope JS110, Keysight N6705 (L240).
- DUT firmware API (C code): timestamp function, UART Tx/Rx, load-input-tensor function, run-inference
  function, print-results function (L248–250).
- Runner GUI (Figure 4) provides setup/configuration, standardizes execution/measurement, downloads
  input files, and visualizes energy data (L253–258).

## 7. Dataset / data
All four datasets are pre-existing public datasets; MLPerf Tiny selects/preprocesses subsets, it does
not introduce a new dataset.
| Benchmark | Dataset (paper) | Snapshot location |
|---|---|---|
| KWS | Speech Commands v2: "105,829 utterances collected from 2,618 speakers," 30 words + background noise; used as 10 words + "unknown" (from remaining 20 words + noise) + "silence" = 12 output classes; "freely available for download under the Creative Commons BY license" | §4.3, L67 |
| VWW | Visual Wake Words, derived from MSCOCO 2014 [15]; images with a person occupying >2.5% of the source image; resized to 96x96 for training | §4.1, L54 |
| IC | CIFAR-10 [14]: 60,000 32x32x3 RGB images, 10 classes, 6,000 images/class, 5 train batches + 1 test batch of 10,000 each | §4.2, L59 |
| AD | DCASE2020 Task 2 data (combination of ToyADMOS [12] and MIMII [17]); DCASE dataset covers 6 machine types, but MLPerf Tiny uses "the Toy-car machine type only"; training uses normal sounds of "seven different toy-cars," 1,000 samples each | §4.4, L72 |

## 8. Experimental setup
- Models: DS-CNN (KWS, 38.6K parameters, TFLite size 52.5 KB), MobileNetV1 α=0.25 (VWW, 325 KB), custom
  ResNetv1 with 3 residual stacks instead of the official 4 (IC, 96 KB), FC-based autoencoder — encoder
  and decoder each four 128-unit FC layers with BatchNorm/ReLU, bottleneck size 8, input/output size 640
  (AD, 270 KB) (§4.1–4.4, Table 1 L44–45).
- AD pre-processing: audio converted to log-mel-spectrogram (128 bands, 32 ms frames); model applied over
  a sliding window of 5 frames (640 input size); MSE reconstruction error averaged over the central 6.4 s
  of the spectrogram as the anomaly score (§4.4, L77).
- Measurement procedure (§5.3, L93–96; identical text repeated at App. A.3, L261–264):
  1. Latency: 5 runs, each downloading an input stimulus, loading the input tensor, running inference
     "for a minimum of 10 seconds and 10 iterations," measuring inferences per second (IPS); score =
     median IPS of the 5 runs.
  2. Accuracy: single inference over "the entire set of validation inputs"; compute Top-1% or AUC; each
     model has a minimum accuracy that must be met for the score to be valid.
  3. Energy: identical procedure to latency, additionally measuring total energy in the timing window and
     computing µJ/inference; score = median of 5 runs.
- Reference implementation run on NUCLEO-L4R5ZI board (Figure 5 caption, L91).

## 9. Metrics
- Top-1 accuracy (%) — VWW, IC, KWS.
- AUC (Area Under the ROC Curve) — AD; chosen because it is "parameterless" and fits an anomaly score
  that has no fixed decision threshold (§4.4, L77).
- Latency: inferences per second (IPS), median of 5 runs.
- Energy: micro-Joules per inference, median of 5 runs.

## 10. Results (exact numbers)
| Benchmark | Result | Quality target | Location |
|---|---|---|---|
| VWW | "about 86%" accuracy on preprocessed MSCOCO 2014 test set | 80% Top-1 | §4.1, L56 |
| IC | 86.5% accuracy on 200 CIFAR-10 test images | 85% Top-1 | §4.2, L61–64 |
| KWS | 92.2% "in our experiments" (unquantized); quantized: 91.6% on full test set, 91.7% on a 1000-utterance subset | 90% | §4.3, L68–69 |
| AD | AUC 0.88 (fp32), AUC 0.86 (quantized), on 248 evaluation samples | 0.85 AUC | §4.4, L77 |
| Model sizes | DS-CNN 52.5 KB, MobileNetV1 325 KB, ResNet 96 KB, FC-AutoEncoder 270 KB | — | Table 1, L44–45 |
| KWS params | DS-CNN 38.6K parameters | — | §4.3, L68 |
| Submission power range | "from µWatts to Watts" (across first-round submissions) | — | §6.2, L189 |
| Latency / energy of reference implementations | **NOT IN SNAPSHOT** — values exist only in Figure 5 (image), not extracted into `paper.txt` | — | Fig. 5, L91/97 |
| v0.5 submission-round detailed results | **NOT IN SNAPSHOT** — paper points to external page `mlcommons.org/en/inference-tiny-05/` and `github.com/mlcommons/tiny_results_v0.5`; Table 2 (L104–184) gives only descriptive/qualitative rows, no performance numbers, and check-mark ("modified") cells were lost in extraction | §6.1, L186; Table 2 |

## 11. Supported claims (directly measured/observed, in snapshot)
- Each of the four reference models meets or exceeds its own stated quality target, at the accuracy
  figures in §10 (§4.1–4.4).
- Reference model sizes and parameter counts as listed in §10 (Table 1; §4.3 L68).
- "The four benchmarks cover a wide scope in terms of latency and energy and each reference meets the
  minimum accuracy" (§5.3, L97) — this is the paper's own textual summary of Figure 5; the underlying
  numeric values are not present in the snapshot, so only the summary sentence itself, not the magnitudes
  behind it, is directly verifiable here.
- A first round of submissions occurred in "June 2021" (§6.1, L186), spanning 5 rows in Table 2 across
  closed and open divisions, on hardware including an ARM MCU, a RISC-V MCU, a Raspberry Pi 4, a "Neural
  Network Accelerator," and an FPGA (Table 2, L104–184).
- "The most common numerical format is 8-bit integer for inference" among first-round submissions
  (§6.2, L189).
- "None of the submissions in the first round modified the training dataset" (§6.2, L191).

## 12. Derived claims (computed/comparative, in snapshot)
- None of the four reference models' quality targets fail to be met by their own reference accuracy
  (derivable by comparing each §4.x accuracy sentence to its adjacent target sentence; no comparison
  across benchmarks or against other published systems is made in the snapshot).
- The AD quality target (0.85 AUC) is explicitly derived by the authors from the two measured AUC values:
  "Based on these two numbers, we've set the threshold for the benchmark to AUC 0.85" (§4.4, L77).
- The KWS/IC/VWW quality targets (90%, 85%, 80%) are each explicitly stated to be set below the observed
  reference accuracy "to accommodate" quantization/rounding differences (§4.1 L56, §4.2 L64, §4.3 L69).

## 13. Interpretations (authors' explanations — labeled as interpretation)
- Interpretation: edge/TinyML inference improves "energy efficiency..., privacy, responsiveness, and
  autonomy" and avoids wireless-transfer energy costs (§1, L12).
- Interpretation: the modular design "enables benchmark submitters to show the benefits of their
  product, regardless of where it falls on the ML deployment stack, in a fair and reproducible manner"
  (Abstract, L10; §5.1, L83–84).
- Interpretation: the closed division "enables a more direct comparison of systems" (§5.2, L87); the
  open division is "designed to broaden the scope of the benchmark and allow submitters to demonstrate
  improvements... at any stage" (§5.2, L88).
- Interpretation: excluding feature extraction from the KWS measurement window is justified because
  "feature extraction is typically a small fraction of the overall compute cost" (§4.3, L68).
- Interpretation (§6.2 "Insights," L188–191, largely descriptive/promotional prose about submitters'
  own goals): one submitter's SDK is described as "hardware agnostic, easy to use and uniquely designed
  to optimize neural network inferences..."; another vendor's accelerator is said to show "outstanding
  performance... enabled by their novel microarchitecture design." These are the authors' paraphrases of
  submitters' self-reported claims about their own products, not independently measured comparisons.
- Interpretation: reconfigurable hardware (FPGA) "is able to utilize variable precision models for
  increased performance" (§6.2, L189).

## 14. Hypotheses / speculation
- Speculation: "despite a general trend in AI towards data-centric design," the authors "anticipate this
  will shift in future versions" of submissions (§6.2, L191).
- Speculation (§7 Impact, L194): TinyML "can preserve privacy by keeping user's data on the device," but
  "could be misused to more efficiently track and monitor unwilling individuals," and "can lead to
  increased electronic waste" because devices are inexpensive.
- Speculation: future benchmark versions aim "to widen the scope of the benchmarks to include
  pre-processing as well" (§8, L198).
- Speculation: future reference implementations "may include" additional architectures, e.g., RNNs
  (§8, L199).

## 15. Limitations
Authors' own Limitations section (§8, L196–199), three named sub-limitations:
1. **New benchmarks & long-term stability** (L197): the suite must evolve (new domains: wearables,
   medical devices, environmental monitoring) while also keeping "a subset of benchmarks... long-term
   stable" for historical tracking — an inherent tension the authors name but do not resolve.
2. **Streaming inputs & pre-processing** (L198): limited bandwidth between the runner (host PC) and the
   DUT "makes it difficult to recreate a streaming scenario without adding delays incurred by data
   transfer"; excluding feature extraction from measurement while letting submitters choose their own
   feature extraction "creates the possibility of a degenerate case where an entire model up to the
   penultimate layer is defined as 'feature extraction'."
3. **Extended coverage of layer types and model architectures** (L199): "The closed division of the
   current benchmark suite includes models based mainly on FC and CNN layers... allowing only open
   division submissions to deviate from these."

Scope boundary (derived from stated conditions): because the closed division "prohibits any retraining
or weight replacement" and requires the same model/dataset/quality target as the reference (§5.2, L87),
closed-division results in this snapshot cannot be read as evidence about retraining or architecture-
search effects — that is out of scope by the closed division's own rules.

Scope boundary (derived from stated conditions): because the accuracy procedure is run "a single
inference on the entire set of validation inputs" (§5.3, L95) while §4's per-benchmark descriptions refer
to "test" images/subsets (e.g., "200 images from the CIFAR-10 test set," §4.2 L61), the snapshot's own
terminology is inconsistent between "validation" and "test," and this Gold Account does not resolve which
split each reported number actually used beyond what each §4.x paragraph states.

## 16. Actual contribution
- MLPerf Tiny: "the first industry-standard benchmark suite for ultra-low-power tiny machine learning
  systems," described as "the collaborative effort of more than 50 organizations from industry and
  academia" (Abstract, L10).
- Four benchmarks (KWS, VWW, IC, AD), each with an open-source reference implementation (training
  scripts, pre-trained models, C code) hosted at `github.com/mlcommons/tiny` (§4, L36).
- A modular run-rule structure (closed/open divisions) and a measurement framework/harness for accuracy,
  latency, and energy (§5, Appendix A).
- A first submission round (June 2021) exercising the suite across 5 diverse hardware/software stacks
  (Table 2, §6.1).

## 17. Unsupported or weakly supported claims (thin support in snapshot; no outside criticism added)
- §3 states "As Table 1 summarizes, there is a clear and distinct need for a TinyML benchmark..." (L33),
  but Table 1 (L39–50) is a specification table of the four chosen benchmarks/datasets/models/targets —
  it does not itself compare MLPerf Tiny to prior benchmarks or demonstrate a "need." The referenced
  support for this sentence is thin/likely a cross-reference slip in the source text.
- §5.2's prose (L86, "If only the components shaded in green are modified then the submitter can submit
  to the open division") is internally inconsistent with the Figure 2 caption (L76, "components in green
  can be modified in either division") and with the closed-division definition itself (L87, which permits
  green-type modifications such as post-training quantization while remaining closed). The snapshot does
  not let us determine which statement the authors intended as authoritative; this Gold Account records
  both and does not adjudicate.
- §6.2's characterizations of individual submitters' products ("outstanding performance," "uniquely
  designed," L188–191) are the authors' paraphrases of self-reported submitter claims, not measurements
  made or verified by this paper; no supporting numbers accompany them in the snapshot.
- "The four benchmarks cover a wide scope in terms of latency and energy" (§5.3, L97) references Figure 5,
  whose numeric content is not present in `paper.txt`; the qualitative claim itself cannot be checked
  against data in this snapshot.
- The broken in-text citation "citekim20191" (§2, L23) points to an unresolved reference; the associated
  claim about "memory compute" architectures has no verifiable citation in the snapshot.

## 18. Claim → evidence → source table
| Claim | Type | Evidence | Snapshot location | Quote (≤25 words) |
|---|---|---|---|---|
| First industry-standard TinyML benchmark suite | context/contribution | Abstract statement | paper.txt L10 | "we present MLPerf Tiny, the first industry-standard benchmark suite for ultra-low-power tiny machine learning systems" |
| KWS reference accuracy | measured | §4.3 | paper.txt L68 | "achieving accuracy of 92.2% in our experiments" |
| KWS quantized accuracy (full/subset) | measured | §4.3 | paper.txt L69 | "demonstrated 91.6% accuracy on the full test set and 91.7% on the 1000-utterance subset" |
| IC reference accuracy | measured | §4.2 | paper.txt L61–64 | "The model reaches 86.5% accuracy across the 200 testing raw images" |
| VWW reference accuracy | measured | §4.1 | paper.txt L56 | "the model reaches about 86% accuracy across the preprocessed MSCOCO 2014 test dataset" |
| AD AUC (fp32/quantized) | measured | §4.4 | paper.txt L77 | "the fp32 version of the reference model achieves an AUC of 0.88 while... quantization is 0.86" |
| KWS dataset size | measured/context | §4.3 | paper.txt L67 | "105,829 utterances collected from 2,618 speakers with a variety of accents" |
| IC dataset size | measured/context | §4.2 | paper.txt L59 | "It consists of 60000 32x32x3 RGB images, with 6000 images per class" |
| Closed division rules | context | §5.2 | paper.txt L87 | "prohibits any retraining or weight replacement" |
| Open division rules | context | §5.2 | paper.txt L88 | "allow submitters to change the model, training scripts, and dataset" |
| Measurement procedure (median of 5 runs) | context | §5.3 | paper.txt L94–96 | "report the median IPS of the five runs as the score" |
| Latency/energy values not extractable | risk/gap | Fig. 5 reference | paper.txt L91, L97 | "Figure 5 illustrates the reference implementation results" (values in image only) |
| First submission round timing | observed | §6.1 | paper.txt L186 | "first round of submissions to MLPerf Tiny (which took place in June 2021)" |
| No dataset modification in round 1 | observed | §6.2 | paper.txt L191 | "none of the submissions in the first round modified the training dataset" |
| Submitter power range | observed | §6.2 | paper.txt L189 | "power consumption of these platforms ranged from µWatts to Watts" |
| Streaming limitation | limitation (author-stated) | §8 | paper.txt L198 | "limited bandwidth... makes it difficult to recreate a streaming scenario without adding delays" |
| Architecture-coverage limitation | limitation (author-stated) | §8 | paper.txt L199 | "includes models based mainly on FC and CNN layers" (closed division) |
| Venue (outside snapshot, web-confirmed) | context | NeurIPS Datasets & Benchmarks 2021 | external (see PROJECT_ASSESSMENT.md §3) | n/a — confirmed via openreview.net/forum?id=8RxxwAut1BI |
| README version history (artifact fact only) | context | README table | README__mlcommons__tiny.md L22–27 | "v0.5 ... Jun 16, 2021 ... v1.1 ... Jun 27, 2023" |
