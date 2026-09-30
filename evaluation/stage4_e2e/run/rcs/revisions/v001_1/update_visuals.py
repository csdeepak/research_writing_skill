"""AUTHOR, step 19 (round v001_1): figure fixes (finding:18 axis encoding; finding:19 / inference:9 Table 2 caption)."""
import json
from pathlib import Path

p = Path(".rcs/plan/visual_registry.json")
r = json.loads(p.read_text(encoding="utf-8"))
V = {v["id"]: v for v in r["visuals"]}
v = V["V003"]
v["x_label"] = "Step"
v["title"] = "Route@1 on the new topic by step"
v["caption"] = ("Without any retraining, the share of new-topic queries that ASMOS sends first to the right owner rises gradually "
                "over the steps, whereas a frozen classifier stays at zero and the retrained classifiers stay at zero until their "
                "first retrain. The vertical axis is route@1 on the new topic (0 to 1) and the horizontal axis is the step (0 to 10); "
                "lines are means over 5 seeds, and ASMOS starts at 0.0 (all-mpnet-base-v2) or 0.2 (bge-m3) at step 0; classifier "
                "lines are from the all-mpnet-base-v2 run and are the same in the bge-m3 run. No error bars are drawn; the source "
                "records the standard deviation across seeds. Source: the project's new-topic result files.")
v["alt_text"] = ("Line plot with step 0 to 10 on the horizontal axis and route@1 on the new topic (0 to 1) on the vertical axis: "
                 "ASMOS with two embedders rises gradually from 0.0 or 0.2 to 1.0, a frozen classifier stays at 0.0, and retrained "
                 "classifiers stay at 0.0 until a retrain.")
v2 = V["V002"]
v2["series_labels"]["A1_transactive"] = "A1 learned-ownership routing"
v2["caption"] = v2["caption"].replace("Transactive routing (A1)", "Learned-ownership routing (A1)")
V["T001"]["caption"] = ("Global search (A0) and ownership frozen at its prior (A2) cost about the same, learned-ownership routing (A1) "
                        "costs fewer tokens per query with equal answerability but lower accuracy, and similarity routing (A3) is "
                        "cheapest but answers far fewer queries.")
V["T002"]["caption"] = ("In a single run of static question answering, ASMOS-memory scores below both No-Memory and RAG on both "
                        "metrics; ASMOS combined with RAG is close to RAG on exact match but far below it on token-F1, and its exact "
                        "match exceeds its token-F1, which standard definitions of the two metrics do not allow.")
p.write_text(json.dumps(r, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
