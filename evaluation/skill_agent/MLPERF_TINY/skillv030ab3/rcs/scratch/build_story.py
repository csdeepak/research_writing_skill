import json
N = []


def n(i, t, text, claims=None, ev=None, sources=None, note=None):
    d = {"id": i, "type": t, "text": text}
    if claims:
        d["claims"] = claims
    if ev:
        d["evidence"] = ev
    if sources:
        d["sources"] = sources
    if note:
        d["audience_note"] = note
    N.append(d)


n("N01", "PROBLEM", "Diverse TinyML hardware and software stacks make fair, reproducible comparison of accuracy, latency and energy hard.", ["C001", "C002"], note="reader must know what a microcontroller and on-device inference are")
n("N02", "SIGNIFICANCE", "The authors say comparison is needed for progress: optimizations across the stack are hard to measure without it.", ["C001", "C024"])
n("N03", "KNOWN", "CoreMark, MLMark and the MLPerf inference benchmark exist, as characterized by the authors.", ["C003"], sources=["SRC-001", "SRC-002"])
n("N04", "GAP", "None of these gives small ML benchmarks for microcontroller-class devices with power measurement (authors' characterization).", ["C003"], sources=["SRC-001", "SRC-002"])
n("N05", "RQ", "RQ1: which tasks, models and quality targets define a representative, fitting benchmark?", ["C004"])
n("N06", "RQ", "RQ2: which rules and measurement procedure allow fair comparison and still show different contributions?", ["C006", "C008"])
n("N07", "RQ", "RQ3: does the v0.5 submission round show the benchmark accommodating diverse submitters?", ["C015"])
n("N08", "APPROACH", "Four benchmarks with reference implementations, quality targets, closed and open divisions and a measurement framework.", ["C023", "C005"])
n("N09", "DESIGN", "Choice of four tasks, datasets, models and quality targets, with reference accuracies.", ["C004", "C029"])
n("N10", "DESIGN", "Closed/open divisions, modular reference implementation, measurement procedure and framework.", ["C006", "C007", "C008", "C009"])
n("N11", "DESIGN", "First submission round (June 2021), peer-reviewed by submitters and a review committee.", ["C015"])
n("N12", "RESULT", "Reference models reach or exceed the quality targets: VWW about 86% vs 80%, IC 86.5% vs 85%, KWS 91.6% vs 90%, AD AUC 0.88/0.86 vs 0.85.", ["C010", "C011", "C012", "C013", "C035"], ev=["E009", "E011", "E014", "E017"])
n("N13", "RESULT", "Authors state each reference implementation meets the minimum accuracy and covers a wide scope in latency and energy (values not available).", ["C014"], ev=["E025"])
n("N14", "RESULT", "Five Table 2 rows: four closed (ARM MCU, RISC-V MCU, LEIP on RasPi 4, Syntiant accelerator) and one open FPGA; trends and no dataset modified.", ["C015", "C016", "C017"], ev=["E026", "E029", "E031"])
n("N15", "INTERPRETATION", "The chosen tasks and targets give an accuracy floor while allowing for quantization differences.", ["C029", "C035", "C004"])
n("N16", "INTERPRETATION", "The authors attribute fair yet flexible comparison to the modular, two-division design and measurement framework.", ["C025", "C026", "C027", "C028", "C034"])
n("N17", "INTERPRETATION", "The authors read the diverse round as evidence that the modular design accommodates different goals.", ["C018"])
n("N18", "CONTRIBUTION", "An open-source, four-benchmark suite measuring accuracy, latency and energy with reference implementations, divisions and a framework.", ["C023"])
n("N19", "LIMITATION", "Streaming and pre-processing limits (author-stated).", ["C008", "C026", "C030"])
n("N20", "LIMITATION", "Long-term stability and model-family coverage (author-stated).", ["C022", "C004"])
n("N21", "LIMITATION", "Writer-derived: no variance, no figure values, one round, no submission measurements.", ["C010", "C014", "C016", "C018"])
n("N22", "IMPLICATION", "The authors expect standardization and responsible-deployment standards, and name misuse and e-waste risks.", ["C021"])
n("N23", "FUTURE", "New domains, stable subset, pre-processing scope, RNNs.", ["C022"])
n("N24", "BACKGROUND_CONCEPT", "Quantization (PTQ, QAT, INT-8) and the quality metrics Top-1 and AUC-ROC.", note="define before Section 4")
n("N25", "BACKGROUND_CONCEPT", "Device under test, inferences per second, micro-Joules per inference.", note="define before Section 5")
E = []


def e(a, b, t):
    E.append({"from": a, "to": b, "type": t})


for r in ("N05", "N06", "N07"):
    e("N01", r, "motivates")
    e(r, "N04", "addresses")
e("N02", "N05", "motivates")
e("N03", "N04", "establishes")
e("N08", "N05", "implements")
e("N08", "N06", "implements")
e("N09", "N12", "produces")
e("N10", "N13", "produces")
e("N11", "N14", "produces")
e("N12", "N15", "supports")
e("N10", "N16", "supports")
e("N14", "N17", "supports")
e("N13", "N17", "supports")
e("N15", "N05", "answers")
e("N16", "N06", "answers")
e("N17", "N07", "answers")
e("N12", "N18", "grounds")
e("N04", "N18", "grounds")
e("N19", "N18", "limits")
e("N20", "N18", "limits")
e("N21", "N12", "limits")
e("N21", "N14", "limits")
e("N17", "N22", "implies")
e("N19", "N23", "opens")
e("N20", "N23", "opens")
e("N09", "N24", "requires")
e("N10", "N25", "requires")
chains = [
    {"experiment": "Reference models evaluated against candidate quality targets (four tasks)", "rq": "N05",
     "hypothesis": "Objective (writer's framing of the authors' aim): set quality targets so a correct quantized implementation passes, using measured reference accuracies.",
     "falsifier": "A reference model falling below its target (none reported).",
     "design_rationale": "Targets set slightly below reference accuracy to accommodate quantization and rounding (C029).",
     "observations": ["E009", "E011", "E014", "E017"], "claims": ["C010", "C011", "C012", "C013", "C029", "C035"], "limitations": ["L006"],
     "next": "Reference targets fix accuracy; the next question is how latency and energy are measured on the reference platform."},
    {"experiment": "Reference implementations on NUCLEO-L4R5ZI (latency, energy, accuracy)", "rq": "N06",
     "hypothesis": "Objective: show that the four references run under the framework and meet minimum accuracy.",
     "falsifier": "A reference failing its minimum accuracy (none reported).",
     "design_rationale": "Reference platform and known-good TFLM snapshot for stability (C034).",
     "observations": ["E025"], "claims": ["C014"], "limitations": ["L005"],
     "next": "With references fixed, the question is whether outside submitters can use the suite in different ways."},
    {"experiment": "v0.5 submission round", "rq": "N07",
     "hypothesis": "Objective: show the benchmark can accommodate submissions from hardware and software vendors in both divisions.",
     "falsifier": "Only one kind of submitter or division taking part (not the case in Table 2).",
     "design_rationale": "Modular design and two divisions (C027, C028).",
     "observations": ["E026", "E029", "E031"], "claims": ["C015", "C016", "C017", "C018"], "limitations": ["L007", "L008"],
     "next": "The round is a snapshot; later rounds are expected to show evolution (C022)."}]
json.dump({"pattern": "method_first", "nodes": N, "edges": E, "experiment_chains": chains}, open(".rcs/story/story_graph.json", "w", encoding="utf-8"), indent=2)
