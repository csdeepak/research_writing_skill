# Gold Account v1: MLPERF_TINY (verified, snapshot-only)

Sources: `evaluation/external_projects/MLPERF_TINY/snapshot/paper.txt` (arXiv 2106.07597v4, pdftotext) and
`README__mlcommons__tiny.md` (mlcommons/tiny README at commit `4addd0fa…`). "L##" = paper.txt line; "R##" = README line.
**The paper is authoritative for research claims. The README is authoritative only for artifact facts** (versions,
dates, repository and results pointers, citation/venue). Detailed issues are in `VERIFICATION.md`.

## Changes from draft
1. **Removed extraction-artifact content from scoring.** "Figure 5 values not in snapshot" is now a *scoring note*
   (below). It is no longer a result, limitation or nugget. gold_story: Q9a removed; Q6b clause removed.
2. **Green/orange division rule** (§5): the draft's "opposite/internally inconsistent" claim is downgraded. L86 is
   incomplete and probably a typo ("open" for "closed"), but it does not contradict the Figure 2 caption. The draft's unsupported
   claim that PTQ is a "green" component is removed, because component colors are not in the text.
3. **KWS 92.2%**: the unsupported "(unquantized)" qualifier is removed.
4. **README separation**: §1 no longer uses the README's device list. The venue is now cited to README R34–38, not an
   external site. A **Source conflicts** section is added.
5. **Drafter critique removed from limitations**: the "closed division cannot show retraining effects" scope boundary
   and "tension … do not resolve" are moved or rewritten. The validation/test wording note is moved to source-text notes.
6. **Coverage added**: §2 Challenges (new §2a); the full §8 streaming/pre-processing limitation (40 feature-extraction
   cycles, joint-optimization, distortion); the KWS feature-choice limitation (L68); design rationale for quality targets,
   the AD model and Toy-car; submission process (L101); energy-measurement rules (L240–243); §7 Impact claims.
7. **Label fixes**: the §6.2 flexibility claim is interpretation; "each reference meets target" is observed (L97); §8 plans
   are future work, not speculation; the KWS quote is "to allow for", not "to accommodate".
8. gold_story: Q2a de-conflated; Q2d, Q5e, Q11e added; Q4a made atomic; Q10c (duplicate) and Q9d (drafter critique)
   removed; Q6a, Q8a, Q8b, Q9b, Q9c corrected. 40 nuggets, `"verified": true`.

**Scoring note (not a research claim):** the numeric values in Figure 5 (reference latency/energy) and the check-mark
("modified") cells of Table 2 are not present in `paper.txt`. Reader statements about those specific values or
modifications are **unscorable**. Neither reward nor penalize them.

## 1. Problem
TinyML progress is "limited by the lack of a widely accepted and easily reproducible benchmark" (L10). Maximum
efficiency needs co-optimization of every layer of the deployment stack, which makes direct comparison of solutions
challenging and "the impact of individual optimizations is difficult to measure". A fair, reliable comparison method
is needed (L12, L17).

## 2. Motivation
- Edge ML inference has "potential for increasing energy efficiency [4], privacy, responsiveness, and autonomy" (L12). *Interpretation.*
- TinyML "achieves ML inference under a milliWatt," breaking the traditional power barrier (L12). *Context.*
- On-device, near-sensor inference gives responsiveness and privacy while avoiding the energy cost of wireless
  communication, "which at this scale is far higher than that of compute [5]" (L12). *Cited context.*
- It enables smart, battery-powered, always-on applications (L12). *Interpretation.*

## 2a. Benchmarking challenges (§2, L20–28)
The paper says "four primary obstacles" but gives five headings:
- **Low power**: energy must be profiled, but power varies drastically across devices. The measurement scope is hard to define when
  data paths and pre-processing differ, and peripherals and firmware affect the measurements.
- **Limited memory**: resources are about two orders of magnitude smaller than smartphones' few GBs. Any benchmark overhead
  can be too big to fit. Multiple quantization/precision levels and a variety of benchmarks are needed.
- **Hardware heterogeneity**: devices range from general-purpose MCUs to novel architectures. The SUT may lack a system clock or debug
  interface. Standardizing the interface while minimizing porting effort is key.
- **Software heterogeneity**: stacks are tightly coupled to the hardware. The benchmark must balance optimality against portability,
  and comparability against representativeness, and must not restrict deployment options.
- **Cross-product**: every layer of the stack (Figure 1) has options. Users should be able to show a gain at any layer.

## 3. Research gap (§3, L29–33; the authors' characterizations)
- CoreMark: does not profile full programs and does not represent ML inference (L31).
- MLMark: uses real ML workloads, but its models are too large for MCUs (GBs of memory, significant runtimes) and it has no power
  measurement (L32).
- MLPerf Inference: plans to add power, but "precludes MCUs and other resource-constrained platforms" (L33).
- The need is for a TinyML benchmark that "makes power a first-class citizen" (L33).

## 4. Objective
Present MLPerf Tiny, an open-source benchmark suite that measures accuracy, latency and energy of ML inference, with a
modular design so that submitters can show benefits "regardless of where it falls on the ML deployment stack, in a fair
and reproducible manner" (L10, L18).

## 5. System / method
- The suite targets **model inference** and excludes pre- and post-processing from the measurement window. Kernel-level benchmarks
  gloss over memory bandwidth and model-level optimizations, while application-level benchmarks obscure the target (L35).
- Four benchmarks, each with a dataset, model and quality target (Table 1, L39–50). Reference implementations include
  training scripts, pre-trained models and C code, run as TFLite models via TFLM (a known-good snapshot) on
  NUCLEO-L4R5ZI, built as a bare-metal MBED project with GCC-ARM (L36).
- **Modular design** (§5.1, L84): the reference implementation runs from training scripts to reference hardware and
  serves as both the baseline and a starting point for swapping single components (Figure 2).
- **Divisions** (§5.2): Figure 2 caption: green components can be modified in either division; orange components only in the open division
  (L76). L86 repeats that modifying any orange component requires the open division. Its preceding sentence ("only
  green … can submit to the open division") is incomplete or likely a typo. Which components are green or orange is visible only
  in the figure.
  - Closed: same models, datasets and quality targets as the reference. PTQ with the provided calibration data is allowed. "Prohibits
    any retraining or weight replacement" (L87).
  - Open: may change the model, training scripts and dataset. Uses the same test dataset but does not need to meet the accuracy
    threshold. Each submission must document its deviations (L88).
  - An organization may submit to either or both divisions (L86).
- **Submission process**: results are accepted twice a year and peer-reviewed by the submitters and a review committee (L101).

## 6. Architecture (benchmark framework, Appendix A)
- Host PC + runner GUI + DUT + thin firmware shim (L236). Based on EEMBC's software development platform (L93).
- Two configurations (Figure 3): (a) latency/accuracy: the host talks directly to the DUT over serial; (b) energy: adds an IO Manager
  (electrical-isolation serial proxy, Arduino UNO, 5 V GPIO with level shifters) and an energy monitor (EMON) (L237–239).
- EMON drivers: STMicroelectronics LPM01A, Joulescope JS110, Keysight N6705 (L240). Only power delivered to the core is
  measured. Level-shifter power is excluded. A single supply powers the core, and no batteries, supercaps or harvesters are allowed. The user may lower the
  voltage, which exposes the performance-vs-energy tradeoff (L240). The EMON reporting rate has no impact on the score (L241).
- DUT API (L243–250): a timestamp (≥1 ms resolution in performance mode; a GPIO falling edge in energy mode), UART Tx/Rx, load input
  tensor, run one inference, print results. Code is split into "internally implemented" and "submitter implemented" parts (L244).
- Runner (L253–260): gives a consistent interface, standardizes execution and measurement, and downloads the many accuracy input files
  (targets have < 1 MB flash). It also visualizes energy (Figure 4, Figure 6 energy viewer).

## 7. Datasets (all pre-existing public datasets; subsets/preprocessing chosen by MLPerf Tiny)
| Benchmark | Dataset | Loc. |
|---|---|---|
| KWS | Speech Commands v2: 105,829 utterances, 2,618 speakers, 30 words + background noise, speaker-disjoint splits, CC BY. Uses 10 words; the remaining 20 words + noise form "unknown"; plus "silence" = 12 classes. Input 49x10 | L67, L42 |
| VWW | Visual Wake Words from MSCOCO 2014. Preprocessed to train on images containing at least one person occupying >2.5% of the source image. Resized to 96x96 | L54 |
| IC | CIFAR-10 (subset of 80M Tiny Images): 60,000 32x32x3 images, 10 classes, 6,000/class, 5 training batches + 1 test batch of 10,000 each. Chosen for continuity with prior TinyML work | L59 |
| AD | DCASE2020 Task 2 data (ToyADMOS + MIMII), 6 machine types. **Toy-car only** ("benchmarking would not benefit" from per-type models). Training: normal sounds of 7 toy-cars × 1,000 samples mixed with environmental noise. Input 5×128 | L72, L42 |

## 8. Experimental setup
- Models: DS-CNN from [22] (KWS, 38.6K params, 52.5 KB). MobileNetV1 α=0.25, 96x96 input, 2 classes (VWW, 325 KB). Custom
  ResNetv1 with 3 residual stacks vs 4, no pooling after the first convolution, fewer filters and smaller strides (IC, 96 KB). FC autoencoder: I/O 640,
  encoder and decoder each four 128-unit FC layers (BatchNorm in training, ReLU), bottleneck 8 (AD, 270 KB) (L55, L60, L68, L77; Table 1).
- AD model choice: it is the DCASE2020 reference model, widely used as a baseline in the literature, and it adds an all-FC model type (L73, L77). AD pipeline:
  10 s audio → log-mel spectrogram (128 bands, 32 ms frames) → AE over a sliding window of 5 frames → MSE averaged over the central 6.4 s
  = anomaly score (L77).
- KWS: feature extraction excluded from measurement; three pre-computed feature choices for the open division (L68).
- Accuracy evaluation sets: VWW, the preprocessed MSCOCO 2014 test set (L56). IC, 200 CIFAR-10 test images, run via the runner (L61).
  KWS, the full test set and 1,000 randomly selected utterances (L69). AD, 248 normal and anomalous samples from four machines (L77).
- Measurement procedure (L94–96, repeated L262–264). Latency: 5 times, load a stimulus and run inference for ≥10 s and ≥10
  iterations; score = median IPS. Accuracy: one inference per validation input; Top-1 / AUC; a minimum is required for a valid score.
  Energy: as latency, plus total energy in the window → µJ/inference, median of 5.
- Reference latency/energy measured on NUCLEO-L4R5ZI (Figure 5, L91).

## 9. Metrics
Top-1 accuracy (KWS, VWW, IC). AUC-ROC (AD), chosen because it is "parameterless" and the anomaly score otherwise needs a threshold
(L77). Latency = inferences per second (median of 5). Energy = µJ per inference (median of 5).

## 10. Results (exact)
| Benchmark | Result | Target | Loc. |
|---|---|---|---|
| VWW | "about 86%" on the preprocessed MSCOCO 2014 test set (precision not stated) | 80% Top-1 | L56 |
| IC | 86.5% on 200 CIFAR-10 test images | 85% Top-1 | L61, L64 |
| KWS | 92.2% "in our experiments" (precision and evaluation set not stated). Quantized: 91.6% full test set, 91.7% 1,000-utterance subset | 90% | L68–69 |
| AD | AUC 0.88 fp32, 0.86 quantized, 248 samples | AUC 0.85 | L77 |
| Reference latency/energy | Figure 5 only. Text: the four benchmarks "cover a wide scope in terms of latency and energy" | n/a | L97 |
| v0.5 round | 5 entries in Table 2 (4 closed, 1 open): ARM MCU/TFLM/INT-8 PTQ (baseline on the reference platform); RISC-V MCU/TFLM/INT-8 PTQ; RasPi 4/LEIP/FP-32 & INT-8 PTQ; NN accelerator/Syntiant TDK/INT-8 PTQ; FPGA/hls4ml/QKeras INT-6/8 QAT (open) | n/a | L104–184 |
| Submission power range | "from µWatts to Watts" | n/a | L189 |

## 11. Supported claims (stated in the snapshot as observed or measured)
- Each reference meets its minimum accuracy (L97; consistent with §10).
- First submission round in June 2021; results were published externally, with reproduction instructions on GitHub (L186).
- INT-8 was the most common inference format (L189). The frameworks range from the open-source interpreter TFLM to hardware-specific compilers (L189).
  Results came from MCUs, accelerators and FPGAs (L189).
- No first-round submission modified the training dataset (L191).

## 12. Derived claims
- Every reference accuracy is above its target (compare each §4.x result with its target).
- Target rationale, as stated by the authors: VWW 80% "to accommodate changes in accuracy due to quantization and rounding differences
  between platforms" (L56). IC 85% "to accommodate minor differences in quantization and various other optimizations" (L64).
  KWS 90% "to allow for slight variations in quantization strategies" (L69). AD 0.85 "based on these two numbers" (0.88/0.86) (L77).

## 13. Interpretations (the authors')
- The edge-inference benefits in §2 (L12).
- The modular design lets submitters show their benefit at any stack layer, fairly and reproducibly (L10, L84).
- The closed division "enables a more direct comparison"; the open division broadens scope (L87–88).
- Excluding KWS feature extraction has minor impact because it is "a small fraction of the overall compute cost" (L68).
- The v0.5 submissions "demonstrated the desired flexibility," which was accommodated "due to its modular design" (L188).
- INT-8 is common because it "offers a performance boost with little impact to the model accuracy". The spread of frameworks indicates a
  continuing optimization-vs-portability trade-off. The FPGA exploits variable precision (L189).
- Descriptions of what individual submitters used the benchmark to demonstrate: a hardware-agnostic SDK; "outstanding performance" of an NN
  accelerator; RISC-V AI MCUs; the hls4ml workflow (L190). These are the authors' descriptions, with no supporting numbers in the text.
- TinyML design "is still largely focused on models, frameworks, and hardware" (L191).
- Impact (L195): the benchmarks have already served as a standard task set in TinyML research [4] and as public projects on a TinyML
  development platform [16].

## 14. Hypotheses, speculation, future work
- Speculation: the lack of data-centric submissions will shift in future versions (L191). The benchmark "will standardize" the field (L195).
- Speculation (§7 Impact, L195): TinyML may democratize AI and preserve privacy, but could be misused for tracking and could increase
  e-waste. A collaborative community could help set responsible-deployment standards.
- Future work: new benchmarks (wearables, medical, environmental monitoring) (L197). Include pre-processing in future versions (L198).
  Possibly RNNs and other architectures (L199).

## 15. Limitations (author-stated only)
1. **New benchmarks & long-term stability** (L197): the suite must evolve while also supporting historical tracking, which requires stability.
   Authors' mitigations: stay open source, keep a subset of benchmarks long-term stable, and rely on continued MLCommons support.
2. **Streaming inputs & pre-processing** (L198):
   - Time-domain tasks (KWS, AD) typically stream, and past time steps could improve the performance-efficiency tradeoff. However, runner↔DUT
     bandwidth makes streaming hard to recreate without data-transfer delays.
   - Whether pre-processing is included can distort results. Excluding it while letting submitters choose their feature extraction allows a degenerate
     case: "an entire model up to the penultimate layer" defined as feature extraction. Rigidly defined features instead preclude joint
     feature/model optimization.
   - Including it in a non-streaming benchmark over-emphasizes its cost: 1 s of audio = 1 inference cycle but **40 feature-extraction cycles**.
3. **Layer/architecture coverage** (L199): the closed-division models are mainly FC and CNN layers. Only open-division submissions may deviate.
4. **KWS features** (L68): "the pre-selected feature choices somewhat limit innovation in the overall KWS system" (mitigated by choosing the
   most commonly used features).

## 16. Actual contribution
- MLPerf Tiny, presented by the authors as "the first industry-standard benchmark suite for ultra-low-power tiny machine learning systems,"
  built by more than 50 organizations (L10).
- Four benchmarks (KWS, VWW, IC, AD) with open-source reference implementations (github.com/mlcommons/tiny) (L36).
- Closed and open run rules and a measurement framework for accuracy, latency and energy, including an energy-measurement harness (§5, App. A).
- A first submission round (June 2021) with 5 entries across diverse stacks (Table 2).

## 17. Weakly supported claims and source-text notes
- L33 "As Table 1 summarizes, there is a clear and distinct need …". Table 1 lists the benchmarks and does not compare prior work. This looks like a
  cross-reference slip.
- The L86 green → "open" sentence is incomplete or a likely typo (see §5). Not a substantive contradiction.
- The §6.2 submitter descriptions (L190) come with no numbers in the text.
- "Wide scope in terms of latency and energy" (L97) rests on Figure 5, and the figure's values are not in the text.
- The citation "citekim20191" is unresolved (L23).
- §2 announces "four primary obstacles" but lists five headings (L20–28).
- The accuracy procedure says "validation inputs" (L95), while §4 describes test sets or subsets (L56, L61, L69).

### Verifier/drafter scope notes (not author claims; not scored)
- Closed-division rules forbid retraining, so closed results say nothing about training-side improvements.
- The paper text reports no per-submission performance numbers. Those numbers live in external results repositories.

## 18. Source conflicts
| Topic | Paper | README | Authoritative |
|---|---|---|---|
| Status/venue | "Preprint. Under review." (L14) | NeurIPS Datasets & Benchmarks track, 2021 (R34–38) | README (citation = artifact fact) |
| Device/power scope | TinyML inference "under a milliWatt" (L12); platforms µW–W (L189) | MCUs/DSPs/tiny NN accelerators, 10–250 MHz, <50 mW (R4–7) | Paper (research scope). The README description is not used |
| Versions | v0.5, four benchmarks | v0.5–v1.1 table, v1.2 deadline (R18–27) | Paper for research content. README for version history only |
| Results URL | mlcommons.org/en/inference-tiny-05/ (L186) | mlcommons.org/benchmarks/inference-tiny/ (R20) | README (pointer) |
| v0.5 date | June 2021 (L186) | Jun 16, 2021 (R24) | Consistent |

## 19. Claim → evidence table
| Claim | Type | Location | Quote (≤25 words) |
|---|---|---|---|
| First industry-standard TinyML benchmark | author claim | L10 | "the first industry-standard benchmark suite for ultra-low-power tiny machine learning systems" |
| KWS accuracy | measured | L68 | "achieving accuracy of 92.2% in our experiments" |
| KWS quantized | measured | L69 | "91.6% accuracy on the full test set and 91.7% on the 1000-utterance subset" |
| IC accuracy | measured | L61–64 | "The model reaches 86.5% accuracy across the 200 testing raw images" |
| VWW accuracy | measured | L56 | "the model reaches about 86% accuracy across the preprocessed MSCOCO 2014 test dataset" |
| AD AUC | measured | L77 | "the fp32 version of the reference model achieves an AUC of 0.88 while the AUC after quantization is 0.86" |
| References meet targets | observed | L97 | "each reference meets the minimum accuracy" |
| Closed division | rule | L87 | "prohibits any retraining or weight replacement" |
| Open division | rule | L88 | "allow submitters to change the model, training scripts, and dataset" |
| Median of five | method | L94 | "report the median IPS of the five runs as the score" |
| First round | observed | L186 | "which took place in June 2021" |
| INT-8 most common | observed | L189 | "the most common numerical format is 8-bit integer for inference" |
| No dataset changes | observed | L191 | "none of the submissions in the first round modified the training dataset" |
| Power range | observed | L189 | "ranged from µWatts to Watts" |
| Streaming limitation | limitation | L198 | "difficult to recreate a streaming scenario without adding delays incurred by data transfer" |
| Feature-extraction cost | limitation | L198 | "one inference cycle and 40 feature extraction cycles, over-emphasizing the cost of feature extraction" |
| Architecture coverage | limitation | L199 | "models based mainly on FC and CNN layers" |
| KWS features | limitation | L68 | "the pre-selected feature choices somewhat limit innovation in the overall KWS system" |
| Venue | artifact fact | R34–38 | "Proceedings of the Neural Information Processing Systems Track on Datasets and Benchmarks" |
| Version history | artifact fact | R24–27 | "v0.5 … Jun 16, 2021 … v1.1 … Jun 27, 2023" |
