import json
claims = []


def C(cid, stmt, ctype, ev, conf, reasons, verbs, conf_status="confirmed", origin=None, rationale=None,
      sources=None, lims=None, basis="project_file", scope=None):
    c = {"id": cid, "statement": stmt, "claim_type": ctype, "evidence": ev, "confidence": conf,
         "confidence_reasons": reasons, "permitted_verbs": verbs, "author_confirmation": conf_status,
         "basis": basis, "status": "VERIFIED", "licenses": []}
    if origin:
        c["origin"] = origin
    if rationale:
        c["rationale"] = rationale
    if sources:
        c["sources"] = sources
    if lims:
        c["limitations"] = lims
    if scope:
        c["scope"] = scope
    claims.append(c)


AS = "author_stated"
C("C001", "The authors state that continued TinyML progress is limited by the lack of a widely accepted, easily reproducible benchmark, and that because deployment requires co-optimization at every layer of the stack, direct comparison of solutions is challenging and the impact of individual optimizations is difficult to measure, so a fair and reliable method of comparison is needed.",
  "interpretation", ["E043", "E044"], "moderate", ["stated by the authors as motivation", "no external evidence for the claim is offered in the paper"],
  ["the authors state", "the authors argue"], origin=AS, rationale="motivation", lims=["L001"])
C("C002", "The authors name five challenges for a TinyML benchmark: low power (very different power levels and unclear measurement scope), limited memory (about two orders of magnitude below smartphones), hardware heterogeneity (missing system clock or debug interface; porting effort), software heterogeneity (tightly coupled inference stacks; optimality versus portability) and a cross-product of options at every level of the stack.",
  "interpretation", ["E035", "E036", "E037", "E038", "E039"], "moderate", ["authors' own statements", "not tested by experiment"],
  ["the authors identify", "the authors describe"], origin=AS)
C("C003", "The authors characterize three existing benchmarks as not meeting TinyML needs: CoreMark does not profile full programs nor represent ML inference workloads; MLMark uses real ML workloads but its models are far too large for MCU-class devices and it lacks power measurement; the MLPerf inference benchmark precludes MCUs for lack of small benchmarks and compatible implementations.",
  "literature", ["E040", "E041", "E042", "E065"], "moderate", ["authors' characterization of others' work", "sources registered from abstract-level information only"],
  ["the authors characterize", "the authors state"], sources=["SRC-001", "SRC-002"], basis="literature", origin=AS)
C("C004", "MLPerf Tiny specifies four benchmarks, each with a dataset, a model and a quality target: keyword spotting (Speech Commands, DS-CNN, 90% Top-1), visual wake words (VWW dataset, MobileNetV1, 80% Top-1), image classification (CIFAR-10, ResNet, 85% Top-1) and anomaly detection (ToyADMOS, FC-autoencoder, AUC 0.85).",
  "observed", ["E001", "E004", "E005", "E006", "E007", "E008", "E010", "E012", "E013", "E015", "E016"], "high",
  ["specified directly in the paper text and Table 1", "Table 1 layout damaged but confirmed by section 4 text (except two model sizes)"],
  ["the suite specifies", "the paper describes"], lims=["L004"], sources=["SRC-005", "SRC-007", "SRC-008", "SRC-009", "SRC-010", "SRC-011", "SRC-012", "SRC-013", "SRC-014", "SRC-015", "SRC-016"])
C("C005", "The reference implementations run the reference models in TFLite format with TensorFlow Lite for Microcontrollers on the NUCLEO-L4R5ZI board, using a known-good TFLM snapshot and a bare-metal MBED project built with the GCC-ARM toolchain, and are open source.",
  "observed", ["E018", "E003"], "high", ["stated directly"], ["the paper describes", "the reference implementation runs"], sources=["SRC-006"])
C("C006", "MLPerf Tiny has a closed division (same models, datasets and quality targets; post-training quantization allowed, retraining and weight replacement prohibited) and an open division (model, training scripts and dataset may change; same test dataset; accuracy threshold not required; deviations documented).",
  "observed", ["E019"], "high", ["stated directly"], ["the paper defines", "the rules specify"])
C("C007", "Each benchmark's reference implementation covers everything from training scripts to a reference hardware platform, and a submitter can modify one component to show the performance of a single hardware or software component.",
  "observed", ["E020"], "high", ["stated directly"], ["the paper describes"])
C("C008", "Measurement procedure: latency is the median inferences per second over five runs, each running inference for at least 10 seconds and 10 iterations; accuracy is Top-1 percent or AUC from a single inference over the whole validation set, with a minimum accuracy required for a valid score; energy repeats the latency procedure and adds total energy in the timing window to give micro-Joules per inference, again as the median of five measurements.",
  "observed", ["E021", "E022", "E023"], "high", ["stated directly, twice (section 5.3 and appendix A.3)"], ["the framework measures", "the procedure specifies"], lims=["L002", "L003"])
C("C009", "The benchmark framework consists of a host PC running a runner GUI, the device under test with a thin firmware shim, and two hardware configurations (latency/accuracy over a serial port; energy adding an IO Manager on an Arduino UNO and an energy monitor), with the device implementing five API functions and a timestamp of at least one millisecond resolution in performance mode.",
  "observed", ["E024"], "high", ["stated directly in appendix A"], ["the framework provides", "the paper describes"])
C("C010", "On the visual wake words benchmark the reference model reaches about 86% accuracy on the preprocessed MSCOCO 2014 test dataset, and closed-division submissions must reach at least 80%.",
  "measured", ["E009"], "moderate", ["single value reported", "no spread reported", "value 'about 86%' is approximate"], ["the reference model reaches", "the target is"], lims=["L006"])
C("C011", "On the image classification benchmark the reference model reaches 86.5% accuracy on 200 images selected from the CIFAR-10 test set, and the quality target is 85% top-1.",
  "measured", ["E011"], "moderate", ["single value on a 200-image subset", "no spread reported"], ["the reference model reaches", "the target is"], lims=["L006"])
C("C012", "On the keyword spotting benchmark the quantized reference model reaches 91.6% accuracy on the full test set and 91.7% on a 1000-utterance subset, against an accuracy requirement of 90%; the model achieved 92.2% in the authors' experiments.",
  "measured", ["E013", "E014"], "moderate", ["single values", "no spread reported", "conditions of the 92.2% figure not stated beyond 'in our experiments'"], ["the reference model reaches", "the requirement is"], lims=["L006"])
C("C013", "On the anomaly detection benchmark, on an evaluation set from four different machines totalling 248 samples, the fp32 reference model reaches an AUC of 0.88 and the quantized model 0.86; the benchmark threshold is AUC 0.85.",
  "measured", ["E017"], "moderate", ["single values on 248 samples", "no spread reported"], ["the reference model reaches", "the threshold is"], lims=["L006"])
C("C014", "The authors state that the four reference implementations cover a wide scope in terms of latency and energy on the NUCLEO-L4R5ZI board and that each reference meets the minimum accuracy; the latency and energy values are shown only in a figure that is not available in the project materials.",
  "observed", ["E025"], "low", ["prose statement only; underlying figure values unavailable", "soft evidence"], ["the authors state"], conf_status="confirmed", lims=["L005"])
C("C015", "The v0.5 submission round (June 2021) produced five rows in the authors' Table 2: four closed-division entries (ARM MCU with TFLM; RISC-V MCU; software-only LEIP toolchain on a Raspberry Pi 4; Syntiant neural network accelerator) and one open-division FPGA entry (QKeras, Int-6/8 QAT, HLS4ML); results are peer-reviewed by submitters and a review committee and are public.",
  "observed", ["E026", "E027", "E030"], "moderate", ["descriptive table rows; check-mark columns illegible in extraction"], ["the round included", "Table 2 lists"], lims=["L007", "L008"], sources=["SRC-018"])
C("C016", "The authors read these trends from the v0.5 submissions: 8-bit integer was the most common numerical format because it offers a performance boost with little impact to model accuracy; software stacks ranged from open-source interpreters to hardware-specific compilers, indicating a trade-off between optimization and portability; hardware spanned MCUs, accelerators and FPGAs; and power consumption ranged from µWatts to Watts.",
  "observed", ["E029", "E026"], "low", ["drawn from a single round with five table rows", "no submission measurements shown"], ["the authors read", "the submissions indicate"], lims=["L007", "L008"])
C("C017", "None of the first-round submissions modified the training dataset, so the data-centric side of the benchmark was not exercised in that round.",
  "observed", ["E031", "E026"], "moderate", ["stated directly; the second clause follows from the open-division rules that allow dataset changes (E019)"], ["none of the submissions modified"], lims=["L007"])
C("C018", "The authors conclude that the diverse v0.5 submissions show the benchmark meeting a variety of needs, and they attribute its ability to accommodate submitters' different goals to its modular design.",
  "interpretation", ["C015", "E028", "E030"], "low", ["authors' interpretation resting on descriptive evidence", "no comparison against a non-modular alternative", "alternative explanations not discussed"],
  ["the authors attribute", "the authors conclude", "is consistent with"], origin=AS, lims=["L007", "L008"])
C("C019", "The repository README lists released versions v0.5 (Jun 16, 2021), v0.7 (April 6, 2022), v1.0 (Nov 9, 2022) and v1.1 (Jun 27, 2023), expects the deadline of the next round v1.2 on March 15, 2024 (dates not yet finalized), and describes target devices as running at between 10MHz and 250MHz with inference in less than 50mW.",
  "observed", ["E032", "E033"], "moderate", ["README is soft evidence", "postdates the paper"], ["the README lists", "the README states"], lims=["L009"])
C("C020", "The authors state that the benchmarks have already acted as a standard set of tasks for TinyML research and have been made into public projects on a TinyML development platform.",
  "observed", ["E034"], "low", ["authors' statement; the paper gives one citation and no adoption data"], ["the authors state"], sources=["SRC-003"], lims=["L009"])
C("C021", "The authors expect the benchmark to standardize the field and enable progress through competition and comparability, and expect a collaborative community to help create standards for responsible deployment; they also name misuse (tracking unwilling individuals) and electronic waste as possible harms of TinyML.",
  "speculation", ["E062"], "low", ["forward-looking statements", "untested"], ["the authors expect", "the authors warn"], origin=AS, lims=["L009"])
C("C022", "The authors plan to add benchmarks for new application domains (wearables, medical devices, environmental monitoring), to keep a subset of benchmarks long-term stable, to widen the scope to include pre-processing, and to consider additional architectures such as RNNs.",
  "future", ["E056", "E060", "E061"], "low", ["stated intentions"], ["the authors aim", "future versions may"], origin=AS)
C("C023", "MLPerf Tiny is an open-source benchmark suite, developed as a collaboration of more than 50 organizations from industry and academia, that measures accuracy, latency and energy of ML inference on four benchmarks and provides complete reference implementations.",
  "observed", ["E001", "E002", "E003", "E064"], "high", ["stated directly", "organization count is the authors' figure"], ["the authors present", "the suite provides"], lims=["L001", "L002", "L003", "L004", "L008"])
C("C024", "The authors describe TinyML as ML inference under a milliWatt, and state that on-device near-sensor inference avoids wireless communication energy, which at this scale is far higher than that of compute.",
  "literature", ["E063"], "moderate", ["authors' background statement citing a sensor-node energy study"], ["the authors state"], sources=["SRC-004"], basis="literature", origin=AS)
C("C025", "The suite measures latency, energy and accuracy together because the authors want to capture the tradeoffs inherent to TinyML, and they treat power as a first-class concern.",
  "interpretation", ["E045"], "moderate", ["stated design reason"], ["the authors state"], origin=AS, rationale="design_choice")
C("C026", "The measurement window covers model inference only, without pre- or post-processing, because the authors judge that application-level benchmarks obscure the target behind other pipeline stages while low-level kernel benchmarks gloss over memory bandwidth and model-level optimization.",
  "interpretation", ["E046"], "moderate", ["stated design reason"], ["the authors state"], origin=AS, rationale="design_choice", lims=["L003"])
C("C027", "The design is modular so that hardware and software users can demonstrate the competitive advantage of their specific contribution, targeting one component such as quantization or offering an end-to-end solution.",
  "interpretation", ["E047"], "moderate", ["stated design reason"], ["the authors state"], origin=AS, rationale="design_choice")
C("C028", "There are two divisions, closed and open, because the authors want to balance comparability and flexibility.",
  "interpretation", ["E048"], "moderate", ["stated design reason"], ["the authors state"], origin=AS, rationale="design_choice")
C("C029", "Quality targets are set slightly below the reference accuracy to accommodate differences from quantization and rounding across platforms (VWW 80% versus about 86%, IC 85% versus 86.5%, KWS 90% versus 91.6%), and the AD threshold of AUC 0.85 is based on the fp32 (0.88) and quantized (0.86) reference values.",
  "interpretation", ["E049", "E009", "E011", "E014", "E017"], "moderate", ["stated design reason with the reference numbers"], ["the authors state"], origin=AS, rationale="design_choice", lims=["L006"])
C("C030", "For keyword spotting the authors chose a small depthwise-separable CNN because its 38.6K parameters fit the memory of most microcontrollers and it uses standard layers, and they excluded feature extraction from the measurement because it is typically a small fraction of the overall compute cost.",
  "interpretation", ["E050", "E051"], "moderate", ["stated design reasons"], ["the authors state"], origin=AS, rationale="design_choice", lims=["L002", "L003"])
C("C031", "For anomaly detection the authors use only the Toy-car machine type because separate models per machine type would add complexity the benchmark would not benefit from, chose the DCASE2020 reference autoencoder because it is a literature reference and adds a model type based entirely on FC layers, use the parameterless AUC-ROC because it avoids selecting a threshold, and evaluate on four different machines so that models have generalization characteristics.",
  "interpretation", ["E052"], "moderate", ["stated design reasons"], ["the authors state"], origin=AS, rationale="design_choice", lims=["L002"])
C("C032", "For image classification the authors chose CIFAR-10 because its low resolution suits tiny models and because prior TinyML work used it, giving a point of reference that relates future results to historical ones.",
  "interpretation", ["E053"], "moderate", ["stated design reasons"], ["the authors state"], origin=AS, rationale="design_choice", sources=["SRC-017"])
C("C033", "For visual wake words the authors chose the task because it is directly relevant to smart doorbell and occupancy applications and because the challenge's reference network fits on most 32-bit microcontrollers.",
  "interpretation", ["E054"], "moderate", ["stated design reasons"], ["the authors state"], origin=AS, rationale="design_choice")
C("C034", "The framework design follows stated reasons: a known-good TFLM snapshot for stability; two configurations because energy measurement is more complex and energy scores may not be desired; level-shifter power excluded as a framework cost; a single supply for the core so that no other energy source defeats the measurement; and a host runner to give a consistent interface, standardize execution and download the many input files a platform with under a megabyte of flash cannot hold.",
  "interpretation", ["E055"], "moderate", ["stated design reasons"], ["the authors state"], origin=AS, rationale="design_choice")
C("C035", "The gap between reference accuracy and quality target is about 6 points for VWW (about 86% versus 80%), 1.5 points for IC (86.5% versus 85%), 1.6 points for KWS on the full test set (91.6% versus 90%), and, for AD, 0.03 AUC for the fp32 model (0.88 versus 0.85) and 0.01 AUC for the quantized model (0.86 versus 0.85).",
  "derived", ["E009", "E011", "E014", "E017"], "moderate", ["simple differences of single reported values", "VWW reference is approximate ('about 86%')"], ["a gap of", "corresponds to"], conf_status="pending", lims=["L006"])

lims = []


def L(lid, stmt, origin, affects, ev, eff, res=None):
    d = {"id": lid, "statement": stmt, "origin": origin, "affects_claims": affects, "evidence": ev, "effect_on_interpretation": eff}
    if res:
        d["resolution"] = res
    lims.append(d)


L("L001", "The authors state that MLPerf Tiny will keep evolving with new benchmarks for new application domains while also needing long-term stability to track historical progress; they envision a subset of benchmarks kept long-term stable.",
  "author_stated", ["C023", "C022", "C001"], ["E056"], "The suite described is a snapshot of an evolving benchmark; its four tasks are not presented as final coverage.")
L("L002", "The authors state that streaming inputs are hard to recreate: limited bandwidth between the test runner and the device makes it difficult to recreate a streaming scenario without adding delays incurred by data transfer; this affects the time-domain tasks (keyword spotting, anomaly detection), which in the benchmark operate on single discrete inputs in a non-streaming setting.",
  "author_stated", ["C023", "C008", "C030", "C031"], ["E057"], "Latency and energy for the time-domain tasks do not reflect the performance-efficiency gains that information from previous time steps could give.")
L("L003", "The authors state that the pre-processing choice can distort results: excluding feature extraction while letting submitters vary it permits a degenerate case in which everything up to the penultimate layer is called feature extraction; a rigid definition precludes joint optimization of features and model; including feature extraction over-emphasizes its cost (one inference cycle and 40 feature extraction cycles per second of audio); the pre-selected KWS features somewhat limit innovation.",
  "author_stated", ["C023", "C026", "C030", "C008"], ["E058", "E059", "E060"], "Measured latency and energy cover model inference only, so they can misstate whole-application cost, and the treatment of feature extraction can distort or constrain results in the ways the authors describe.")
L("L004", "The authors state that the closed division models are based mainly on FC and CNN layers, and that only open-division submissions may deviate; other architectures such as RNNs may be added in future reference implementations.",
  "author_stated", ["C023", "C004"], ["E061"], "Closed-division comparisons cover FC and CNN model families only.")
L("L005", "The latency and energy values of the reference implementations (Figure 5 of the paper) are not present in the project materials, so their magnitudes cannot be reported.",
  "writer_derived", ["C014"], ["E025"], "The statement that the references span a wide range of latency and energy is reported at the authors' strength, without magnitudes.")
L("L006", "Every accuracy or AUC value is a single number on a fixed evaluation set (200 images, 1000 utterances or 248 samples for the on-device sets) with no spread or confidence interval, and the paper does not say how sensitive the quality targets are to the choice of subset.",
  "writer_derived", ["C010", "C011", "C012", "C013", "C029", "C035"], ["E009", "E011", "E014", "E017"], "Differences of 1 to 2 points between reference accuracy and target should not be read as precise margins.")
L("L007", "The first-round trends rest on the five rows of Table 2 from a single round.",
  "writer_derived", ["C015", "C016", "C017", "C018"], ["E026", "E029", "E031"], "The trends describe that round, not the field, and cannot show how the benchmark behaves across rounds.")
L("L008", "The project materials contain no measured accuracy, latency or energy values from the submissions, so the fairness and comparability the design aims at are described but not demonstrated numerically.",
  "writer_derived", ["C018", "C023", "C015", "C016"], ["E026", "E030"], "The reading that the benchmark enables fair comparison rests on the design and rules and on the authors' qualitative assessment.")
L("L009", "The paper describes the v0.5 benchmark; the README lists later versions (v0.7 to v1.1) and an expected v1.2 round, but the project materials do not describe changes in those versions or any adoption evidence beyond the authors' statements.",
  "writer_derived", ["C019", "C020", "C021"], ["E032", "E034", "E062"], "Statements about current use, adoption and impact are the authors' own and are not independently evidenced here.")

json.dump({"claims": claims, "limitations": lims, "negative_result_decisions": []}, open(".rcs/claims/claim_evidence_map.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(claims), len(lims))
