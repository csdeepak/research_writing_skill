"""Re-types values from project result files into flat CSVs for the visual registry (AUTHOR).
Every value is copied from the project file named in each registry entry's data.source_text; nothing is computed
except selecting and reshaping rows. Run from the working directory: python .rcs/plan/data/build_data.py"""
import csv, json
from pathlib import Path

root = Path(".")
n10 = json.loads((root / "project/data/results/n10_cost_expanded_20260726_93f9058.json").read_text(encoding="utf-8"))
mp = json.loads((root / "project/data/results/e2_new_topic_20260703_182558.json").read_text(encoding="utf-8"))
bg = json.loads((root / "project/data/results/e2_new_topic_20260726_104315.json").read_text(encoding="utf-8"))
out = root / ".rcs/plan/data"

# V001: per-seed token reduction (A0 vs A1) and the pooled bootstrap interval
with open(out / "v001_seed_reduction.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["seed", "reduction_pct", "ci_low_pct", "ci_high_pct"])
    for seed, v in n10["per_seed_headline_pct"].items():
        w.writerow([seed, v, "", ""])
    w.writerow(["pooled", n10["n10_headline_pct"], n10["bootstrap_ci"]["ci_lo_pct"], n10["bootstrap_ci"]["ci_hi_pct"]])

# V002: answer accuracy per arm and seed (seeds 66-110)
with open(out / "v002_accuracy_by_seed.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["seed", "arm", "answer_accuracy"])
    for seed, arms in n10["per_seed_aggregate_new"].items():
        for arm, agg in arms.items():
            w.writerow([seed, arm, agg["answer_accuracy"]])

# V003: route@1 by step in the new-topic regime
with open(out / "v003_new_topic_route.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["step", "arm", "route_at_1"])
    for i, r in enumerate(mp["per_step_route@1"]["A1_ASMOS_ADAPTIVE"]):
        w.writerow([i, "asmos_mpnet", r["mean"]])
    for i, r in enumerate(bg["per_step_route@1"]["A1_ASMOS_ADAPTIVE"]):
        w.writerow([i, "asmos_bge_m3", r["mean"]])
    for arm, key in (("classifier_frozen", "A4_CLASSIFIER_FROZEN"), ("classifier_every_5", "A4_CLASSIFIER_RETRAIN_EVERY_5"),
                     ("classifier_every_10", "A4_CLASSIFIER_RETRAIN_EVERY_10")):
        for i, r in enumerate(mp["per_step_route@1"][key]):
            w.writerow([i, arm, r["mean"]])
# consistency note: classifier per-step route@1 in the bge-m3 run
same = all(bg["per_step_route@1"][k] == mp["per_step_route@1"][k] for k in
           ("A4_CLASSIFIER_FROZEN", "A4_CLASSIFIER_RETRAIN_EVERY_5", "A4_CLASSIFIER_RETRAIN_EVERY_10"))
print("classifier per-step route@1 identical across the two embedder runs:", same)
