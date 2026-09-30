import json
N=[]
def n(t,text,claims=None,ev=None,src=None,note=None):
    d={"id":"N%02d"%(len(N)+1),"type":t,"text":text}
    if claims:d["claims"]=claims
    if ev:d["evidence"]=ev
    if src:d["sources"]=src
    if note:d["audience_note"]=note
    N.append(d)
n("PROBLEM","Ultra-low-power ML systems (TinyML) lack an accepted, reproducible way to compare accuracy, latency and energy across very different hardware and software stacks.",["C009"],note="define TinyML, MCU, inference")
n("SIGNIFICANCE","Without fair comparison, the impact of individual optimizations at any layer of the stack is hard to measure and progress is slowed.",["C009"])
n("KNOWN","CoreMark, MLMark and MLPerf inference exist, per the authors, but each falls short for TinyML (no ML workload, models too large or no power measurement, no MCU support).",["C009"],src=["SRC-001","SRC-002"])
n("GAP","No existing benchmark, in the authors' account, gives a suite of small ML tasks with power as a first-class measure and a methodology suited to TinyML.",["C009"],src=["SRC-001","SRC-002"])
n("RQ","RQ1: Can a benchmark specification give comparable accuracy, latency and energy results across heterogeneous TinyML systems while leaving room for submitters to show different kinds of improvement?",["C001","C006","C007"])
n("RQ","RQ2: Did the first round of submissions show that the specification accommodates diverse submitters, and what did it reveal about the field?",["C010","C011","C014"])
n("OBJECTIVE","Provide four reference tasks, a closed and an open division, a shared measurement procedure and a runner framework, all open source.",["C001","C007","C008"])
n("APPROACH","Choose four use cases with datasets, small reference models and accuracy targets; measure inference only; standardize measurement with a host-side runner and optional energy hardware.",["C001","C006","C008"])
n("DESIGN","Benchmark design: tasks, datasets, models and quality targets set from reference model accuracy.",["C002","C003","C004","C005"],ev=["E002","E005","E008","E011"])
n("DESIGN","Measurement and division rules: median-of-five latency and energy, closed/open divisions.",["C006","C007","C008"])
n("RESULT","Reference models reach their reported accuracy figures, and targets sit below them by 0.01 AUC to about 6 points.",["C004","C005"],ev=["E004","E007","E010","E013","E038"])
n("RESULT","First round: five Table 2 rows across ARM, RISC-V, Raspberry Pi 4, accelerator and FPGA, closed and open; INT8 most common; power from microWatts to Watts; no dataset modification.",["C010","C011","C012"],ev=["E024","E025","E026"])
n("INTERPRETATION","The authors attribute the diversity of submissions to modular design; consistent with, not isolated by, the evidence.",["C014"])
n("INTERPRETATION","The specification appears to serve RQ1 in the sense of accommodating varied submissions; comparability across submissions is not shown in the evidence.",["C014","C010"])
n("CONTRIBUTION","An open, industry-and-academia-built specification and reference suite for measuring TinyML accuracy, latency and energy with closed/open divisions.",["C001","C007","C010"])
n("LIMITATION","Inference-only scope; no streaming; feature extraction excluded.",["C016"])
n("LIMITATION","Latency/energy numbers and per-submission results are not in the evidence; one round only.",["C013","C010"])
n("IMPLICATION","Future rounds can track the evolution of TinyML, e.g. whether data-centric changes appear.",["C015","C018"])
n("FUTURE","New domains, more layer types, pre-processing in scope, a stable long-term subset.",["C018"])
n("BACKGROUND_CONCEPT","TinyML, MCU, device under test, quantization (post-training vs quantization-aware), inferences per second.",note="defined in section 2")
E=lambda a,b,t:{"from":a,"to":b,"type":t}
edges=[E("N01","N05","motivates"),E("N02","N05","motivates"),E("N01","N06","motivates"),E("N03","N04","establishes"),E("N05","N04","addresses"),E("N06","N04","addresses"),
E("N07","N05","operationalizes"),E("N08","N07","implements"),E("N09","N05","produces"),E("N10","N05","produces"),E("N09","N11","produces"),E("N10","N12","produces"),
E("N11","N13","supports"),E("N12","N13","supports"),E("N12","N14","supports"),E("N14","N05","answers"),E("N13","N06","answers"),E("N11","N05","supports"),
E("N11","N15","grounds"),E("N12","N15","grounds"),E("N04","N15","grounds"),E("N16","N11","limits"),E("N16","N12","limits"),E("N17","N12","limits"),E("N17","N13","limits"),
E("N13","N18","implies"),E("N17","N19","opens"),E("N18","N19","opens"),E("N01","N20","requires"),E("N10","N11","requires")]
# fix: DESIGN tests/produces requirement satisfied by produces
chains=[
{"experiment":"Reference implementations","rq":"N05","hypothesis":"Small reference models on a common board can meet stated quality targets and span a wide latency/energy range","falsifier":"a reference model falling below its own quality target","design_rationale":"A reference baseline lets submitters show improvement relative to it","observations":["E004","E007","E010","E013","E027"],"claims":["C004","C005","C013"],"limitations":["L001","L002"],"next":"Do external submitters use the suite in varied ways?"},
{"experiment":"First submission round (June 2021)","rq":"N06","hypothesis":"The modular closed/open design lets varied submitters demonstrate different contributions","falsifier":"only near-identical submissions","design_rationale":"Two divisions balance comparability and flexibility","observations":["E024","E025","E026"],"claims":["C010","C011","C012","C014"],"limitations":["L001","L005"],"next":"What should future versions add?"}]
json.dump({"pattern":"method_first","nodes":N,"edges":edges,"experiment_chains":chains},open(".rcs/story/story_graph.json","w"),indent=1)
open(".rcs/story/spine.md","w").write("""# Paper Spine

1. **Problem.** Engineers and researchers building machine learning for microcontroller-class, ultra-low-power devices (TinyML) cannot compare accuracy, latency and energy across very different hardware and software stacks {C009}.
2. **Gap.** In the authors' account, CoreMark, MLMark and MLPerf inference each miss what TinyML needs (small ML workloads, power measurement, MCU compatibility) {C009, L008}.
3. **Question.** Can one benchmark specification give comparable results across heterogeneous TinyML systems while letting submitters show improvements at any layer, and did its first round show this? {C001, C007, C010}
4. **Approach.** Four tasks with reference models, inference-only measurement, closed and open divisions, and a runner framework with optional energy measurement {C001, C006, C007, C008}.
5. **Key finding.** The first round (June 2021) drew closed and open submissions on ARM and RISC-V MCUs, a Raspberry Pi 4, a neural-network accelerator and an FPGA, and reference models sit 0.01 AUC to about 6 points above their quality targets {C010, C005}.
6. **Meaning.** The authors attribute the breadth of submissions to the modular design; the evidence is consistent with that but does not isolate it {C014}.
7. **Main limit.** Latency and energy values are absent from the available text, evidence is one round, and feature extraction and streaming are outside the measurement {L001, L003, L005}.
""")
