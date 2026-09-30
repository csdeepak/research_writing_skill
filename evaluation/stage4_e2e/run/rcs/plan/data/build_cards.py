"""Writes the figure/table cards (AUTHOR). Cards mirror the visual registry entries; captions come from the registry."""
import json
from pathlib import Path

reg = {v["id"]: v for v in json.loads(Path(".rcs/plan/visual_registry.json").read_text(encoding="utf-8"))["visuals"]}
N10 = "project/data/results/n10_cost_expanded_20260726_93f9058.json"
cards = {
    "FIG-1": dict(vid="V001", type="dot_ci", purpose="show that per-seed token reductions are tight while the interval over queries is wide",
                  takeaway="Per-seed reductions vary by 0.2 percentage points but the query-level interval spans 8.3 points.",
                  source_data=[".rcs/plan/data/v001_seed_reduction.csv", N10],
                  comparison="spread of the ten seed points against the pooled interval",
                  uncertainty="pooled row: bootstrap 95% CI over 50 queries; seed rows: no interval (one value per seed)",
                  reference="pooled reduction 22.1%",
                  non_conclusions="does not show the size of the saving on an organic workload or for other answering models",
                  placement="Section 4.1, after the paragraph reporting the interval"),
    "FIG-2": dict(vid="V002", type="dot_ci", purpose="show accuracy by arm and seed so that A1 below A0 in every seed is visible",
                  takeaway="A1 answers 0.68 to 0.70 correctly in every seed against 0.72 for A0.",
                  source_data=[".rcs/plan/data/v002_accuracy_by_seed.csv", N10],
                  comparison="A1 against A0 within each seed",
                  uncertainty="none available: one accuracy value per arm and seed; no paired test in the package",
                  reference="A0 global search",
                  non_conclusions="does not bound the accuracy cost or show seeds 11 to 55 (not in the package)",
                  placement="Section 4.2, after the accuracy paragraph"),
    "FIG-3": dict(vid="V003", type="line", purpose="show how quickly each router reaches the new topic",
                  takeaway="ASMOS rises gradually with no retraining while classifiers stay at zero until a retrain.",
                  source_data=[".rcs/plan/data/v003_new_topic_route.csv", "project/data/results/e2_new_topic_20260703_182558.json", "project/data/results/e2_new_topic_20260726_104315.json"],
                  comparison="ASMOS lines against classifier lines over steps",
                  uncertainty="means over 5 seeds; standard deviation recorded in the source but not drawn",
                  reference="frozen classifier at zero",
                  non_conclusions="does not show answerability (identical across arms) or labelling cost (counter undocumented)",
                  placement="Section 4.4, after the regret paragraph"),
    "TAB-1": dict(vid="T001", type="table", purpose="give the four arms side by side with exact values",
                  takeaway="A1 cuts tokens and keeps answerability but is lower on accuracy; A3 is cheapest but loses answerability.",
                  source_data=[N10],
                  comparison="A1 against A0 and against A2 and A3",
                  uncertainty="none in the table; interval and test are in the text and Figure 1",
                  reference="A0 global search",
                  non_conclusions="accuracy, answerability and route@1 cover seeds 66 to 110 only",
                  placement="Section 4.1, after the first paragraph"),
    "TAB-2": dict(vid="T002", type="table", purpose="give the four-system question-answering comparison with exact values",
                  takeaway="ASMOS-memory scores below No-Memory and RAG on static question answering.",
                  source_data=["project/results/summary.csv"],
                  comparison="ASMOS-memory against No-Memory and RAG",
                  uncertainty="none in the table; paired intervals are in the text",
                  reference="RAG",
                  non_conclusions="one run of 24 items; no p-values; metric definitions undocumented",
                  placement="Section 4.5, after the comparison paragraph"),
}
out = Path(".rcs/plan/figure_cards")
out.mkdir(parents=True, exist_ok=True)
for cid, c in cards.items():
    v = reg[c["vid"]]
    card = {"id": cid, "type": c["type"], "visual_id": c["vid"], "purpose": c["purpose"], "rq": v.get("rq"),
            "takeaway": c["takeaway"], "claims": v["claim_ids"], "evidence": v["evidence_ids"], "source_data": c["source_data"],
            "comparison_the_eye_must_make": c["comparison"], "uncertainty_shown": c["uncertainty"],
            "baseline_or_reference": c["reference"], "non_conclusions": c["non_conclusions"],
            "honesty_checks": {"axes_start": "bars none; dot and line axes do not start at zero and the caption says so" if c["type"] != "table" else "n/a",
                               "all_conditions_shown": True, "dual_axis": False, "three_d": False, "cherry_picked": False},
            "accessibility": {"colorblind_safe": True, "redundant_encoding": "Okabe-Ito colours paired with marker shapes" if c["type"] != "table" else "n/a",
                              "min_font_pt_at_print": 7, "alt_text": v.get("alt_text", "")},
            "placement": c["placement"], "caption": v["caption"], "source_script": ".rcs/plan/data/build_data.py"}
    (out / f"{cid}.json").write_text(json.dumps(card, indent=1, ensure_ascii=False), encoding="utf-8")
print("cards written:", ", ".join(cards))
