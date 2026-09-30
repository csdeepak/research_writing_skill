#!/usr/bin/env python3
"""CORPUS_AGENT build script (steps 1-2). Reads project/ only; writes .rcs/evidence and .rcs/claims/claim_candidates.json.
Numbers from JSON/CSV files are pulled programmatically (verbatim); numbers from prose are typed with their quote."""
import csv, hashlib, json, os, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
GEN = "CORPUS_AGENT (rce/skill/agents/corpus_agent.md; .rcs/corpus/build_corpus.py)"

P = "project/"
F_README = P + "README.md"
F_REPRO = P + "REPRODUCIBILITY.md"
F_CORR = P + "data/results/CORRECTIONS.md"
F_TECH = P + "ASMOS_technical_report.md"
F_CONTRACT = P + "CONTRACT.md"
F_N10 = P + "data/results/n10_cost_expanded_20260726_93f9058.json"
F_ESC = P + "data/results/effect_size_correction_20260807_78127c8.json"
F_NT1 = P + "data/results/e2_new_topic_20260703_182558.json"
F_NT2 = P + "data/results/e2_new_topic_20260726_104315.json"
F_CM = P + "data/results/e2_cross_model_summary_20260630_045130.json"
F_CSV = P + "results/summary.csv"
F_CMPT = P + "results/comparison_table.md"
F_STAT = P + "results/statistics.md"
F_SUMM = P + "results/summary.md"

n10 = json.load(open(F_N10, encoding="utf-8"))
esc = json.load(open(F_ESC, encoding="utf-8"))
nt1 = json.load(open(F_NT1, encoding="utf-8"))
nt2 = json.load(open(F_NT2, encoding="utf-8"))
cm = json.load(open(F_CM, encoding="utf-8"))
csvrows = {r["system"]: r for r in csv.DictReader(open(F_CSV, encoding="utf-8"))}


def sha(path):
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


items = []
ids = {}


def add(key, kind, summary, path, anchor=None, value=None, conditions=None, strength="hard", status="ok", quantity=None,
        run_id=None, notes=None, conflicts_with=None, derived_from=None, resolution=None):
    assert key not in ids, key
    e = {"id": "E%03d" % (len(items) + 1), "kind": kind, "summary": summary}
    if value is not None:
        e["value"] = value
    if conditions is not None:
        e["conditions"] = conditions
    e["locator"] = {"path": path}
    if anchor:
        e["locator"]["anchor"] = anchor
    e["strength"] = strength
    e["status"] = status
    if quantity:
        e["quantity"] = quantity
    if run_id:
        e["run_id"] = run_id
    e["source_hash"] = sha(path)
    if notes:
        e["notes"] = notes
    e["_conflicts_with"] = conflicts_with or []
    e["_derived_from"] = derived_from or []
    e["_resolution"] = resolution
    ids[key] = e["id"]
    items.append(e)
    return e


# ---------------------------------------------------------------------------------------------------------------
# Spot-check of the N=10 rank statistics (own midrank implementation; scipy not installed here)
dl = n10["per_query_a0_a1_deltas_n10"]
nz = [x for x in dl if x != 0]
order = sorted(range(len(nz)), key=lambda i: abs(nz[i]))
rank = [0.0] * len(nz)
i = 0
while i < len(nz):
    j = i
    while j + 1 < len(nz) and abs(nz[order[j + 1]]) == abs(nz[order[i]]):
        j += 1
    for k in range(i, j + 1):
        rank[order[k]] = (i + j) / 2 + 1
    i = j + 1
Tp = sum(r for x, r in zip(nz, rank) if x > 0)
Tm = sum(r for x, r in zip(nz, rank) if x < 0)
print("SPOTCHECK N=10 stored deltas: n_eff=%d T+=%s T-=%s r=%.4f (artifact W=%s)" % (len(nz), Tp, Tm, (Tp - Tm) / (Tp + Tm), n10["wilcoxon_n10"]["W_statistic"]))
q = n10["per_query_mean_llm_tokens_n10"]
arm_mean = {k: sum(v) / len(v) for k, v in q.items()}
print("SPOTCHECK arm means", arm_mean, "pct", 100 * (arm_mean["A0_global"] - arm_mean["A1_transactive"]) / arm_mean["A0_global"])

RUN_N10 = "n10_cost_expanded_20260726_93f9058"
COND_N10 = "constructed asymmetric two-agent transactive corpus; 50 queries; openai/gpt-4o-mini temperature 0; seeds 11,22,33,44,55,66,77,88,99,110; frozen tau 0.351493"

# ================================================================= N=10 cost experiment (hard)
add("n10_design", "experiment",
    "N=10 cost experiment: 50 queries, four routing arms (A0 global, A1 transactive, A2 static, A3 similarity), gpt-4o-mini, 10 seeds, frozen tau",
    F_N10, "keys=description,n_queries,seeds_*,frozen_tau,model",
    value={"n_queries": n10["n_queries"], "seeds_prior": n10["seeds_prior"], "seeds_new": n10["seeds_new"], "seeds_all": n10["seeds_all"],
           "frozen_tau": n10["frozen_tau"], "model": n10["model"], "arms": ["A0_global", "A1_transactive", "A2_static", "A3_similarity"],
           "design": "ablation"},
    conditions=COND_N10, run_id=RUN_N10,
    notes='description (verbatim): "N=10 seed extension of transactive_cost_expanded_20260724_a274137". The five prior seeds are pooled from that N=5 '
          'artifact, which is NOT in the package; per-seed token arrays and per-seed aggregates in this file are for the five new seeds only (66-110). '
          'A2 (static) is the frozen-ownership ablation arm (README: "single-variable ablation"); arm semantics for A0-A2 are in README, A3 only in the archived report. '
          'REPRODUCIBILITY.md corroborates the design with "Cost -22.09% (n=50/N=10)".')
add("n10_dataset", "dataset",
    "The transactive evaluation set has 50 queries in five query classes Q1-Q5; global search consults a candidate set of 32.0 on average",
    F_N10, "keys=n_queries; per_seed_aggregate_new.66.A0_global.routing_by_class,mean_candidate_set_size",
    value={"n_queries": 50, "query_classes": ["Q1", "Q2", "Q3", "Q4", "Q5"],
           "mean_candidate_set_size_A0": n10["per_seed_aggregate_new"]["66"]["A0_global"]["mean_candidate_set_size"]},
    conditions=COND_N10, run_id=RUN_N10,
    notes="The corpus and query files themselves (src/asmos/evaluation/transactive_corpus.py, data/populations/) are not in the package. "
          "README says the corpus is 'deliberately constructed' (asymmetry is imposed, not organic).")
add("n10_sep", "result",
    "Domain separability go/no-go: mean within-domain cosine 0.2666, mean cross-domain 0.1024, max cross-domain 0.2072, go = true",
    F_N10, "key=separability", value=n10["separability"], conditions="same corpus as the cost experiment", run_id=RUN_N10,
    notes="README says the 2026-07-07 MiniLM rerun reproduces separability 0.2666/0.1024 to 4 dp. Archived report gives 0.267/0.102 (rounded).")
add("n10_headline", "result",
    "N=10 headline: LLM total tokens per query were 22.0911 percent lower under A1 transactive than A0 global search (10 seeds, 50 queries)",
    F_N10, "key=n10_headline_pct",
    value={"metric": "llm_token_reduction_pct_A0_vs_A1", "value": n10["n10_headline_pct"], "unit": "percent", "n_seeds": 10, "n_queries": 50},
    conditions=COND_N10, run_id=RUN_N10, quantity="cost_reduction_pct_A0_vs_A1|n_queries=50|N=10|gpt-4o-mini",
    notes="REPRODUCIBILITY.md section 0 quotes 'reduction 22.09%' and the section 3 map row says 'Cost -22.09% (n=50/N=10)'; consistent. "
          "Independently reproduced by CORPUS_AGENT from per_query_mean_llm_tokens_n10: 100*(180.154-140.356)/180.154 = 22.0911. Pointed out by CORRECTIONS.md: this percentage did NOT move in the effect-size correction.")
add("n10_n5_headline", "result",
    "The N=5 headline recorded inside the N=10 artifact was 22.109 percent; the shift from N=5 to N=10 was -0.0179 percentage points",
    F_N10, "keys=n5_headline_pct,headline_shift_n5_to_n10_pp",
    value={"metric": "llm_token_reduction_pct_A0_vs_A1", "value": n10["n5_headline_pct"], "unit": "percent", "n_seeds": 5,
           "headline_shift_n5_to_n10_pp": n10["headline_shift_n5_to_n10_pp"]},
    conditions="same corpus, seeds 11-55 only", run_id="transactive_cost_expanded_20260724_a274137 (via " + RUN_N10 + ")",
    quantity="cost_reduction_pct_A0_vs_A1|n_queries=50|N=5|gpt-4o-mini",
    notes="Different seed count than E-headline, so a different quantity, not a conflict (22.109 at N=5 vs 22.0911 at N=10).")
add("n10_seed_pct", "result", "Per-seed token-reduction percentages for the ten seeds range from 21.932 to 22.154 (std 0.069 percentage points)",
    F_N10, "keys=per_seed_headline_pct,spread",
    value={"per_seed_headline_pct": n10["per_seed_headline_pct"], "spread": n10["spread"]},
    conditions=COND_N10, run_id=RUN_N10)
add("n10_ci", "result",
    "Bootstrap 95% CI for the mean per-query token reduction: 32.304 to 47.322 tokens (17.9313 to 26.2675 percent), mean delta 39.798 tokens",
    F_N10, "key=bootstrap_ci", value=dict(n10["bootstrap_ci"], test="bootstrap over queries", ci=[n10["bootstrap_ci"]["ci_lo_pct"], n10["bootstrap_ci"]["ci_hi_pct"]]),
    conditions=COND_N10 + "; 2000 resamples; rng_seed 42", run_id=RUN_N10, quantity="bootstrap_ci_pct_A0_vs_A1|N=10|n=50",
    notes="CORRECTIONS.md: the confidence interval is correct and unchanged by the effect-size correction.")
add("n10_wilcoxon", "result",
    "One-sided Wilcoxon signed-rank test on per-query A0-A1 token deltas: W = 1141.5, p = 6.788e-09 (n_pairs 50, median delta 50.4 tokens)",
    F_N10, "key=wilcoxon_n10 (W_statistic,p_value,median_delta_tokens,iqr_tokens)",
    value={"test": "Wilcoxon signed-rank, one-sided, H1 median delta > 0, zero_method=wilcox (zero deltas dropped), normal approximation",
           "W_statistic": n10["wilcoxon_n10"]["W_statistic"], "p_value": n10["wilcoxon_n10"]["p_value"], "p": n10["wilcoxon_n10"]["p_value"],
           "n_pairs": 50, "median_delta_tokens": n10["wilcoxon_n10"]["median_delta_tokens"], "iqr_tokens": n10["wilcoxon_n10"]["iqr_tokens"],
           "q25": n10["wilcoxon_n10"]["q25"], "q75": n10["wilcoxon_n10"]["q75"], "single_comparison_no_multiplicity_correction": True},
    conditions=COND_N10, run_id=RUN_N10,
    notes="W and p are unchanged by the 2026-08-07 correction (CORRECTIONS.md 'What did NOT move'). CORPUS spot-check with an independent midrank implementation on the stored deltas: T+ = 1141.5, T- = 34.5. "
          "bh_correction (verbatim): 'Not applicable: single comparison (A0 vs A1). No comparison family.' The p-value is one-sided.")
add("n10_z_stored", "result",
    "SUPERSEDED stored z-statistic for the N=10 headline test (4.8653); computed with null moments parameterised by 50 pairs instead of 48",
    F_N10, "key=wilcoxon_n10.z_statistic", value={"metric": "wilcoxon_z", "value": n10["wilcoxon_n10"]["z_statistic"]},
    conditions=COND_N10, run_id=RUN_N10, status="superseded", quantity="wilcoxon_z|N=10 n=50 A0-A1 gpt-4o-mini",
    conflicts_with=["n10_z_corr"],
    notes="Superseded per project/data/results/CORRECTIONS.md (Correction 1): 'any document quoting ... z = 4.8653 is stale.' Kept beside the correction, never edited in place.")
add("n10_r_stored", "result",
    "SUPERSEDED stored effect size for the N=10 headline test (r = 0.6881, labelled rank-biserial); it was neither rank-biserial nor Rosenthal r",
    F_N10, "key=wilcoxon_n10.effect_size_r", value={"metric": "effect_size_r", "value": n10["wilcoxon_n10"]["effect_size_r"]},
    conditions=COND_N10, run_id=RUN_N10, status="superseded", quantity="effect_size_r|N=10 n=50 A0-A1 gpt-4o-mini",
    conflicts_with=["n10_r_corr"],
    notes="CORRECTIONS.md: 'The stored 0.6881 is therefore not Kerby's r (0.9413) ... It is an unnamed quantity.' Do not use; do not describe it as a rank-biserial correlation.")
a3 = esc["artifacts"][3]["corrected"]
add("n10_z_corr", "result",
    "Corrected z-statistic for the N=10 headline test: 5.6786 (5.677 without tie correction), computed over n_eff = 48 non-zero pairs",
    F_ESC, "artifacts[3].corrected.z_statistic", value={"metric": "wilcoxon_z", "value": a3["z_statistic"], "z_no_tie_correction": a3["z_statistic_no_tie_correction"]},
    conditions=COND_N10, run_id="effect_size_correction_20260807_78127c8", quantity="wilcoxon_z|N=10 n=50 A0-A1 gpt-4o-mini",
    conflicts_with=["n10_z_stored"],
    resolution={"chosen": "n10_z_corr", "reason": "CORRECTIONS.md declares this file the authority: the stored z used null mean/variance built on 50 pairs while the statistic ranks 48; corrected value recomputed offline from rebuilt per-seed deltas.", "by": "agent"},
    notes="Recorded resolution follows the authors' own correction record; the agent did not choose between values on its own judgment.")
add("n10_r_corr", "result",
    "Corrected effect size for the N=10 headline test: Kerby matched-pairs rank-biserial r = 0.9413 (T+ = 1141.5, T- = 34.5, n_eff = 48 of n = 50; 43 positive, 5 negative, 2 zero deltas)",
    F_ESC, "artifacts[3].corrected", value={"metric": "rank_biserial_r_kerby", "value": a3["rank_biserial_r_kerby"], "full_precision": a3["rank_biserial_r_kerby_full_precision"],
                                          "n_eff": a3["n_eff"], "n_pairs": a3["n_pairs"], "T_plus": a3["T_plus"], "T_minus": a3["T_minus"],
                                          "n_positive": a3["n_positive"], "n_negative": a3["n_negative"], "n_zero_deltas": a3["n_zero_deltas"],
                                          "closure_identity_holds": a3["closure_identity_holds"]},
    conditions=COND_N10, run_id="effect_size_correction_20260807_78127c8", quantity="effect_size_r|N=10 n=50 A0-A1 gpt-4o-mini",
    conflicts_with=["n10_r_stored"],
    resolution={"chosen": "n10_r_corr", "reason": "CORRECTIONS.md: the stored 0.6881 is z/sqrt(n) on a malformed z and is not rank-biserial; Kerby r from rank sums is the reported estimator. REPRODUCIBILITY.md also quotes 0.941 with n_eff = 48 of 50.", "by": "agent"},
    notes="Always report n_eff (48 of 50) beside r (CORRECTIONS.md). Rosenthal z/sqrt(N) is retired and must not be reported. CORPUS spot-check on stored deltas: 43 positive, 5 negative, 2 zero; T+ 1141.5, T- 34.5, r 0.9413.")

# ---- per-arm aggregates for the 5 new seeds
seeds_new = [str(s) for s in n10["seeds_new"]]
agg = n10["per_seed_aggregate_new"]


def per_seed(arm, field):
    return {s: agg[s][arm][field] for s in seeds_new}


add("n10_tokens_arm", "result",
    "Mean LLM total tokens per query by arm and seed (seeds 66-110): A0 180.1-180.2, A1 140.2-140.6, A2 179.1-179.5, A3 123.1-123.8",
    F_N10, "per_seed_aggregate_new.<seed>.<arm>.mean_total_tokens",
    value={arm: per_seed(arm, "mean_total_tokens") for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
    conditions=COND_N10 + "; the five new seeds only", run_id=RUN_N10)
add("n10_ctx_arm", "result",
    "Mean context tokens per query by arm are constant across the five new seeds: A0 123.2, A1 83.6, A2 122.3, A3 65.9",
    F_N10, "per_seed_aggregate_new.<seed>.<arm>.mean_context_tokens",
    value={arm: sorted(set(per_seed(arm, "mean_context_tokens").values())) for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
    conditions=COND_N10 + "; the five new seeds only", run_id=RUN_N10)
add("n10_acc", "negative_result",
    "Answer accuracy in the five new seeds: A0 0.72 in every seed, A1 0.68/0.68/0.68/0.70/0.70, A2 0.72, A3 0.56/0.56/0.56/0.56/0.54; A1 is below A0 in every seed",
    F_N10, "per_seed_aggregate_new.<seed>.<arm>.answer_accuracy",
    value={arm: per_seed(arm, "answer_accuracy") for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
    conditions=COND_N10 + "; the five new seeds only; 50 queries per seed", run_id=RUN_N10,
    notes="This does not match the README/archived-report statement 'equal accuracy 0.545' (a different, 11-query corpus whose artifact is absent). "
          "No paired test of A1 vs A0 accuracy is in the package; the grading method for answer_accuracy in this artifact is not stated (README: QA-ladder grading is LLM-judged, centerpiece ownership verification is deterministic). "
          "Accuracy for seeds 11-55 is not in this file. Checkpoint Q-002.")
add("n10_answerability", "result",
    "Answerability in the five new seeds is 0.98 for A0, A1 and A2 and 0.58 for A3 in every seed",
    F_N10, "per_seed_aggregate_new.<seed>.<arm>.answerability",
    value={arm: sorted(set(per_seed(arm, "answerability").values())) for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
    conditions=COND_N10 + "; the five new seeds only", run_id=RUN_N10)
add("n10_route", "result",
    "Routing in the five new seeds: route@1 is 0.909 for A1, 0.0 for A0 and A2, 0.614 for A3; routing hit rate is 1.0 (A0, A1), 0.98 (A2), 0.54 (A3)",
    F_N10, "per_seed_aggregate_new.<seed>.<arm>.routing_precision_at_1,routing_hit_rate",
    value={"routing_precision_at_1": {arm: sorted(set(per_seed(arm, "routing_precision_at_1").values())) for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
           "routing_hit_rate": {arm: sorted(set(per_seed(arm, "routing_hit_rate").values())) for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")},
           "mean_candidate_set_size": {arm: sorted(set(per_seed(arm, "mean_candidate_set_size").values())) for arm in ("A0_global", "A1_transactive", "A2_static", "A3_similarity")}},
    conditions=COND_N10 + "; the five new seeds only", run_id=RUN_N10,
    notes="A0 route@1 = 0.0 by construction (global search routes to no single agent); do not present it as a routing failure.")
add("n10_perq", "result",
    "Per-query mean LLM tokens over 10 seeds are stored for all four arms (50 values each), together with the 50 A0-A1 deltas",
    F_N10, "keys=per_query_mean_llm_tokens_n10,per_query_a0_a1_deltas_n10",
    value={"n_queries": 50, "arms": list(q.keys())}, conditions=COND_N10, run_id=RUN_N10,
    notes="CORRECTIONS.md warns: rank statistics must be rebuilt from raw per-seed arrays, not from the rounded stored delta field, for the N=5 artifacts. For this N=10 file, an independent midrank calculation on the stored deltas reproduced W = T+ = 1141.5.")
add("n10_arm_means", "result",
    "Mean over the 50 queries of the 10-seed per-query mean tokens: A0 180.154, A1 140.356, A2 179.278, A3 123.444",
    F_N10, "per_query_mean_llm_tokens_n10 (mean of 50 values per arm)",
    value={k: round(v, 3) for k, v in arm_mean.items()}, conditions=COND_N10, run_id=RUN_N10, derived_from=["n10_perq"],
    notes="Computed by CORPUS_AGENT: arithmetic mean of the stored per-query arrays. Formula check: A0 mean - A1 mean = 39.798 = bootstrap_ci.mean_delta_tokens. Rounding 3 dp.")
add("n10_a1_a2_gap", "result",
    "Mean A2-minus-A1 gap over 50 queries and 10 seeds is 38.922 tokens per query; A2 (frozen ownership) is within 0.876 tokens of A0 (179.278 vs 180.154)",
    F_N10, "per_query_mean_llm_tokens_n10 (A2_static mean - A1_transactive mean)",
    value={"metric": "a2_minus_a1_tokens_per_query", "value": round(arm_mean["A2_static"] - arm_mean["A1_transactive"], 3), "unit": "tokens/query"},
    conditions=COND_N10, run_id=RUN_N10, quantity="a1_a2_gap_tokens_per_query|n_queries=50|N=10|gpt-4o-mini", derived_from=["n10_arm_means"],
    notes="Computed by CORPUS_AGENT. No test, spread or per-seed gap for A1-A2 is stored in this artifact (see missing_evidence). The README's '+39.14 +/- 0.43' is a different quantity (11-query corpus, N=5, artifact absent).")
add("n10_ci_diag", "observation",
    "The authors' diagnosis: the CI width (8.3362 pp) is set by inter-query variance; per-seed spread (0.222 pp range) is 37.6 times narrower, so more seeds cannot narrow it",
    F_N10, "keys=ci_variance_diagnosis,n5_vs_n10",
    value={"ci_variance_diagnosis": n10["ci_variance_diagnosis"], "ci_width_pct": n10["n5_vs_n10"]["ci_width_pct"]},
    conditions=COND_N10, run_id=RUN_N10,
    notes='conclusion (verbatim): "CI is query-variance-dominated. Per-seed spread is 0.22pp; bootstrap CI width is 8.3pp. More seeds cannot narrow a CI driven by inter-query heterogeneity." '
          'verdict (verbatim): "N=10 does NOT materially narrow the CI: the width is set by inter-query heterogeneity, not seed noise (per-seed std 0.07 pp << CI width 8.3 pp)."')
add("n10_lim_generalisation", "limitation_noted",
    "Authors' own statement that the N=10 CI is driven by inter-query heterogeneity, not seed noise; extra seeds do not tighten it",
    F_N10, "key=ci_variance_diagnosis.conclusion", strength="hard",
    notes='Verbatim: "More seeds cannot narrow a CI driven by inter-query heterogeneity."', run_id=RUN_N10)
add("rat_single_comp", "rationale_stated",
    "No multiplicity correction applied because the analysis is a single comparison (A0 vs A1)",
    F_N10, "key=bh_correction", notes='Verbatim: "Not applicable: single comparison (A0 vs A1). No comparison family."', run_id=RUN_N10)

# ================================================================= effect-size correction artifact
add("esc_estimator", "method_detail",
    "Reported effect-size estimator is Kerby (2014) matched-pairs rank-biserial r = (T+ - T-)/(T+ + T-) over the n_eff non-zero pairs; zero_method=wilcox retained; Rosenthal z/sqrt(N) retired",
    F_ESC, "keys=estimator,estimator_ruling,zero_handling",
    value={"estimator": "Kerby 2014 matched-pairs rank-biserial", "zero_method": "wilcox", "rosenthal_alternatives_on_headline": {"N=n=50": 0.803, "N=n_eff=48": 0.819, "N=2n=100": 0.568},
           "report_n_eff_beside_r": True}, run_id="effect_size_correction_20260807_78127c8",
    notes="CORRECTIONS.md: 'n_eff is reported alongside every r. \"r = 1.000 (n_eff = 36 of 50)\" is a true and complete statement; a bare \"r = 1.0\" invites the reading \"every query improved\", which is false for 28% of that set.'")
add("rat_kerby", "rationale_stated",
    "Reason given for Kerby over Rosenthal: Kerby is the direct companion of the signed-rank test and has one definition; Rosenthal's N is read three ways (0.803, 0.819, 0.568)",
    F_ESC, "key=estimator_ruling", run_id="effect_size_correction_20260807_78127c8",
    notes='Verbatim: "Kerby is the direct companion to the signed-rank test actually run ... and it has ONE definition." and "The ruling is not the magnitude-maximising choice: under Rosenthal with N = 2n the corrected headline would be 0.568, BELOW the published 0.688".')
add("rat_wilcox", "rationale_stated",
    "Reason given for keeping zero_method=wilcox rather than Pratt: switching would alter an already pre-registered p-value",
    F_ESC, "key=zero_handling", run_id="effect_size_correction_20260807_78127c8",
    notes='Verbatim: "NOT switched to Pratt: that would change an already pre-registered p-value after the fact."')
add("esc_unchanged", "observation",
    "The authors state W, the one-sided p, the headline percentage reduction, the bootstrap CI and per-seed spread are correct in every affected artifact and did not move",
    F_ESC, "key=what_did_not_move", run_id="effect_size_correction_20260807_78127c8",
    notes='Verbatim: "W, the one-sided p-value, the headline percentage reduction, the bootstrap confidence interval and the per-seed spread are CORRECT in every affected artifact and are unchanged by this correction." No experiment re-run, no API call (provenance.no_experiment_run true).')

LAB = {0: "N=5 gpt-4o-mini n=50 (transactive_cost_expanded_20260724_a274137)", 1: "N=5 qwen3-30b-a3b n=50 (transactive_cost_expanded_20260725_93f9058)",
       2: "N=1 qwen-2.5-72b n=50 (transactive_cost_expanded_20260805_437bb6b)", 4: "N=5 n50_supplementary_20260724_a274137"}
for idx in (0, 1, 2, 4):
    a = esc["artifacts"][idx]
    lab = LAB[idx]
    art = a["artifact"].replace(".json", "")
    c = a["corrected"]
    un = a["unchanged"]
    key = "esc%d" % idx
    add(key + "_block", "result",
        "Corrected signed-rank statistics for %s: n_eff %d of %d, T+ %s, T- %s, Kerby r %s, z %s, W %s, one-sided p %.4g" % (
            lab, c["n_eff"], c["n_pairs"], c["T_plus"], c["T_minus"], c["rank_biserial_r_kerby"], c["z_statistic"], un["W_statistic"], un["p_value_one_sided"]),
        F_ESC, "artifacts[%d].corrected/unchanged" % idx,
        value={"test": "Wilcoxon signed-rank, one-sided, zero_method=wilcox", "W_statistic": un["W_statistic"], "p_value": un["p_value_one_sided"], "p": un["p_value_one_sided"],
               "n_pairs": c["n_pairs"], "n_eff": c["n_eff"], "n_zero_deltas": c["n_zero_deltas"], "n_positive": c["n_positive"], "n_negative": c["n_negative"],
               "T_plus": c["T_plus"], "T_minus": c["T_minus"], "rank_biserial_r_kerby": c["rank_biserial_r_kerby"], "z_statistic": c["z_statistic"]},
        conditions=lab, run_id=art,
        notes="Source artifact %s is not in the package; the values are as recorded in the corrected-statistics file, recomputed offline from raw per-seed token arrays. "
              "Only the effect size and z are superseded; W and p were always correct." % a["artifact"]
        + (" r = 1.000 must be reported with n_eff = 36 of 50 (14 zero deltas)." if idx == 2 else ""))
    for sf in a["superseded_fields"]:
        fp = sf["field_path"]
        if sf["stored_value"] == sf["corrected_value"]:
            continue
        sq = "%s|%s" % (fp, art)
        sk = "%s_%s_stored" % (key, fp.replace(".", "_"))
        ck = "%s_%s_corr" % (key, fp.replace(".", "_"))
        stored_loc = F_N10 if idx == 3 else F_ESC
        note_extra = ""
        if "T_minus" in fp:
            note_extra = " CORRECTIONS.md: T_minus = 132.5 'was fabricated by arithmetic, not measured' (n_pairs(n_pairs+1)/2 - T+ instead of summing negative ranks); closure T+ + T- = 1176 holds only for 33.5."
        if "point_estimate" in fp:
            note_extra = " CORRECTIONS.md: the stored 22.0419 is the mean of the 2000 bootstrap resamples, not the observed statistic (22.109); the CI itself does not move."
        add(sk, "result", "SUPERSEDED stored value of %s in %s: %s" % (fp, art, sf["stored_value"]), F_ESC,
            "artifacts[%d].superseded_fields[field_path=%s].stored_value" % (idx, fp),
            value={"metric": fp, "value": sf["stored_value"]}, conditions=lab, run_id=art, status="superseded", quantity=sq, conflicts_with=[ck],
            notes="Superseded per CORRECTIONS.md Correction 1 (stored artifact %s is byte-intact and not in this package). Reason recorded in the file: %s" % (a["artifact"], sf.get("reason", "")[:400]) + note_extra)
        add(ck, "result", "Corrected value of %s in %s: %s" % (fp, art, sf["corrected_value"]), F_ESC,
            "artifacts[%d].superseded_fields[field_path=%s].corrected_value" % (idx, fp),
            value={"metric": fp, "value": sf["corrected_value"]}, conditions=lab, run_id=art, quantity=sq, conflicts_with=[sk],
            resolution={"chosen": ck, "reason": "The corrected-statistics artifact and CORRECTIONS.md declare the stored field superseded and give the offline recomputation from raw per-seed arrays.", "by": "agent"})

add("corr_outstanding", "observation",
    "CORRECTIONS.md states the corrected values have not yet been propagated to the manuscript, the claim ledger, or docs/n50_cost_expansion_report.md; until then this file is the authority",
    F_CORR, "section 'Still outstanding after this correction'", strength="soft",
    notes='Verbatim: "Until that propagation lands, this file is the authority and any document quoting r = 0.688, r = 0.79, r = 0.0389 or z = 4.8653 is stale."')
add("corr_second_answerers", "observation",
    "Second-answerer cost runs exist for qwen3-30b-a3b (N=5) and qwen-2.5-72b (N=1 pilot) with n=50 queries, but only their corrected Wilcoxon statistics are in the package",
    F_ESC, "artifacts[1],artifacts[2]", run_id="effect_size_correction_20260807_78127c8",
    notes="README says 'Single LLM ... Every LLM number uses gpt-4o-mini'; this is superseded by the existence of these two runs. Their percentage reductions are not recorded anywhere in the package.")

# ================================================================= E2 new-topic runs (hard)
for tag, nt, fpath, emb, run in (("mpnet", nt1, F_NT1, "all-mpnet-base-v2 (MPNet-base-v2)", "e2_new_topic_20260703_182558"),
                                 ("bge", nt2, F_NT2, "BAAI/bge-m3 (BGE-M3)", "e2_new_topic_20260726_104315")):
    cfg = nt["config"]
    sm = nt["scalar_metrics"]
    cond = "E2 non-stationary new-topic regime; embedder %s; new topic %s owned by %s; %d steps; seeds %s; %d eval queries per step; asmos_tau %s; classifier_tau %s; leakage_check %s" % (
        emb, cfg["new_topic"], cfg["new_owner"], cfg["n_steps"], cfg["seeds"], cfg["n_eval_queries"], cfg["asmos_tau"], cfg["classifier_tau"], cfg["leakage_check"])
    a1 = sm["A1_ASMOS_ADAPTIVE"]
    add("nt_%s_asmos" % tag, "result",
        "E2 new-topic (%s): ASMOS cumulative regret %s +/- %s over 5 seeds, adaptation lag %s +/- %s, %s retrains, %s labels consumed, routed the new topic in %s of 5 seeds" % (
            emb.split(" ")[0], a1["cumulative_regret"]["mean"], a1["cumulative_regret"]["std"], a1["adaptation_lag"]["mean"], a1["adaptation_lag"]["std"],
            a1["retrain_events"]["mean"], a1["labels_consumed"]["mean"], a1["n_seeds_routed_X"]),
        fpath, "scalar_metrics.A1_ASMOS_ADAPTIVE",
        value={"metric": "cumulative_regret", "value": a1["cumulative_regret"]["mean"], "spread": {"type": "std", "value": a1["cumulative_regret"]["std"]}, "n": 5,
               "adaptation_lag": a1["adaptation_lag"], "emergence_detection_lag": a1["emergence_detection_lag"], "retrain_events": a1["retrain_events"],
               "labels_consumed": a1["labels_consumed"], "n_seeds_routed_X": a1["n_seeds_routed_X"]},
        conditions=cond, run_id=run, quantity="e2_new_topic_asmos_cumulative_regret|embedder=%s" % emb.split(" ")[0],
        notes="Different embedders give different regret (MPNet 3.24, BGE-M3 0.92, README MiniLM 4.32): different conditions, not conflicts. "
              "labels_consumed = 10 for ASMOS in this artifact, yet README says 'zero added labels' (Checkpoint Q-004). Regret sums (1 - route@1) over steps 1-10 (CORPUS check: 3.24 and 0.92 reproduce from per_step_route@1).")
    clf = {k: sm[k] for k in sm if k.startswith("A4")}
    add("nt_%s_clf" % tag, "baseline",
        "E2 new-topic (%s): classifier baselines - frozen regret 10.0 (never routes the new topic, 0/5 seeds); retrain-every-5 regret 4.8 +/- 0.4 (2 retrains, lag 5); retrain-every-10 regret 9.0 (1 retrain, lag 10)" % emb.split(" ")[0],
        fpath, "scalar_metrics.A4_*",
        value={"metric": "cumulative_regret", "value": clf["A4_CLASSIFIER_FROZEN"]["cumulative_regret"]["mean"],
               "arms": {k: {"cumulative_regret": v["cumulative_regret"], "adaptation_lag": v["adaptation_lag"], "retrain_events": v["retrain_events"],
                            "labels_consumed": v["labels_consumed"], "n_seeds_routed_X": v["n_seeds_routed_X"]} for k, v in clf.items()}},
        conditions=cond, run_id=run, quantity="e2_new_topic_classifier_frozen_cumulative_regret|embedder=%s" % emb.split(" ")[0],
        notes="Classifier numbers are identical in the two runs (embedder-independent in this artifact); classifier_tau is 0.5, ASMOS tau is 0.351493. Whether classifier hyperparameters were tuned is not recorded.")
    r1 = [x["mean"] for x in nt["per_step_route@1"]["A1_ASMOS_ADAPTIVE"]]
    add("nt_%s_curve" % tag, "result",
        "E2 new-topic (%s): ASMOS route@1 by step (steps 0-10) rises %s" % (emb.split(" ")[0], " ".join(str(x) for x in r1)),
        fpath, "per_step_route@1.A1_ASMOS_ADAPTIVE[*].mean", value={"route_at_1_by_step": r1, "n": 5}, conditions=cond, run_id=run)
    ans = [x["mean"] for x in nt["per_step_full"]["A1_ASMOS_ADAPTIVE"]["answerability"]]
    same = all([x["mean"] for x in nt["per_step_full"][a]["answerability"]] == ans for a in nt["per_step_full"])
    add("nt_%s_answer" % tag, "observation",
        "E2 new-topic (%s): per-step answerability is identical across all four arms (%s), so it does not discriminate between arms in this regime" % (emb.split(" ")[0], " ".join(str(x) for x in ans)),
        fpath, "per_step_full.<arm>.answerability", value={"answerability_by_step": ans, "identical_across_arms": same}, conditions=cond, run_id=run,
        notes="Answerability rises from 0.0 to 1.0 with step for every arm, including the frozen classifier; it appears to track when new-topic content becomes available rather than routing. Interpretation left to the author.")

# ================================================================= E2 cross-model summary (hard, single run)
CMC = "E2 cross-model summary (stationary regime); single run, no seeds or spread recorded; number of queries not stated (answerability values are multiples of 1/11)"
for emb, arms in cm["by_embedder"].items():
    for arm, m in arms.items():
        add("cm_%s_%s" % (emb.split("-")[0].lower(), arm), "result",
            "E2 cross-model, %s, %s: route@1 %s, hit rate %s, answerability %s, mean context tokens %s" % (
                emb, arm, m["routing_precision_at_1"], m["routing_hit_rate"], m["answerability"], m["mean_context_tokens"]),
            F_CM, "by_embedder.%s.%s" % (emb, arm),
            value={"metric": "routing_precision_at_1", "value": m["routing_precision_at_1"], "routing_hit_rate": m["routing_hit_rate"],
                   "answerability": m["answerability"], "mean_context_tokens": m["mean_context_tokens"]},
            conditions=CMC + "; embedder " + emb, run_id="e2_cross_model_summary_20260630_045130",
            quantity="e2_cross_model|routing_precision_at_1|embedder=%s|arm=%s" % (emb, arm), status="incomplete",
            notes="No variance or seed count recorded, so status incomplete (see missing_evidence).")
for o in cm["observations"]:
    neg = not o["asmos_routing_competitive"]
    add("cm_obs_%s" % o["embedder"].split("-")[0].lower().replace(" ", ""), "negative_result" if neg else "observation",
        "E2 cross-model, %s: ASMOS route@1 %s vs classifier %s (routing competitive: %s); ASMOS answerability %s vs classifier %s (lead %.3f)" % (
            o["embedder"], o["asmos_route@1"], o["classifier_route@1"], str(o["asmos_routing_competitive"]).lower(), o["asmos_answerability"],
            o["classifier_answerability"], o["asmos_answerability_lead"]),
        F_CM, "observations[embedder=%s]" % o["embedder"], value=o, conditions=CMC + "; embedder " + o["embedder"] + "; shared-tau arms",
        run_id="e2_cross_model_summary_20260630_045130", status="incomplete",
        notes=("With the lexical-hash fallback embedder ASMOS is NOT routing-competitive with the classifier (0.667 vs 1.0); the README calls the fallback a degraded offline mode, not the evaluation baseline." if neg else
               "MiniLM row matches the README E2 stationary row (route@1 1.000 vs 1.000; answerability 0.909 vs 0.727)."))

# ================================================================= four-system comparison
FS = "four-system comparison, keyed run, openai/gpt-4o-mini, n=24 RULER QA questions, uniform keyed answer call"
FS_RUN = "four_system_keyed_run (results/summary.csv)"
sysname = {"A No-Memory": "no_memory", "B RAG": "rag", "C ASMOS": "asmos", "D ASMOS+RAG": "system_d"}
for s, r in csvrows.items():
    k = sysname[s]
    add("fs_%s_acc" % k, "result" if k != "asmos" else "negative_result",
        "Four-system, %s: EM %s, token-F1 %s, containment %s, answerability %s (n=24)" % (s, r["exact_match"], r["token_f1"], r["containment"], r["answerability"]),
        F_CSV, "row=%s;cols=exact_match,token_f1,containment,answerability" % s,
        value={"metric": "containment", "value": float(r["containment"]), "exact_match": float(r["exact_match"]), "token_f1": float(r["token_f1"]),
               "answerability": float(r["answerability"]), "n": int(r["n"])},
        conditions=FS, run_id=FS_RUN, quantity="containment|RULER QA n=24|gpt-4o-mini|system=%s" % k,
        notes=("ASMOS-memory alone scores below No-Memory (EM 0.1667 vs 0.3333); summary.md attributes this to missing coverage of the QA facts in the single-agent checkpoint store. " if k == "asmos" else "")
              + ("Exact-match equals containment in every row of summary.csv (0.3333/0.7083/0.1667/0.625), so 'EM' may be a containment metric; and system D has token-F1 0.4329 below its EM 0.625. Metric definitions are not in the package." if k == "system_d" else ""))
    add("fs_%s_cost" % k, "result",
        "Four-system, %s: retrieval count %s, prompt tokens %s, completion tokens %s, total tokens %s, latency %s s, estimated cost %s USD" % (
            s, r["retrieval_count"], r["prompt_tokens"], r["completion_tokens"], r["total_tokens"], r["latency_s"], r["estimated_cost_usd"]),
        F_CSV, "row=%s;cols=retrieval_count..estimated_cost_usd" % s,
        value={"retrieval_count": float(r["retrieval_count"]), "prompt_tokens": float(r["prompt_tokens"]), "completion_tokens": float(r["completion_tokens"]),
               "total_tokens": float(r["total_tokens"]), "latency_s": float(r["latency_s"]), "estimated_cost_usd": float(r["estimated_cost_usd"])},
        conditions=FS, run_id=FS_RUN, notes="Cost in USD is rounded to 4 dp and is not informative (0.0 for no-memory). Latency/token values are means over 24 questions; no spread recorded.")
add("fs_summary_spread", "result",
    "Four-system token-F1 mean +/- std and 95% CI (from summary.md): No-Memory 0.5642+/-0.3545 [0.4224, 0.706]; RAG 0.7513+/-0.3479 [0.6121, 0.8905]; ASMOS-memory 0.4155+/-0.3301 [0.2834, 0.5476]; ASMOS+RAG 0.4329+/-0.4076 [0.2698, 0.596]",
    F_SUMM, "table 'Four-System Comparison' columns token-F1 (mean+/-std), 95% CI",
    value={"No-Memory": {"mean": 0.5642, "std": 0.3545, "ci": [0.4224, 0.706]}, "RAG": {"mean": 0.7513, "std": 0.3479, "ci": [0.6121, 0.8905]},
           "ASMOS-memory": {"mean": 0.4155, "std": 0.3301, "ci": [0.2834, 0.5476]}, "ASMOS+RAG": {"mean": 0.4329, "std": 0.4076, "ci": [0.2698, 0.596]}},
    conditions=FS, run_id=FS_RUN, strength="soft", status="unverifiable",
    notes="summary.md says its numbers come from results/{no_memory,rag,asmos,system_d}.json, which are not in the package; means agree with summary.csv and comparison_table.md. Soft because the values are read from a prose/markdown table.")
add("fs_stats", "result",
    "Paired token-F1 differences (n=24): RAG minus ASMOS +0.3358 (95% bootstrap CI [+0.1494, +0.5228], Wilcoxon W=100); system D minus RAG -0.3184 (CI [-0.4990, -0.1406], W=-94); system D minus ASMOS +0.0174 (CI [-0.1546, +0.1862], W=30)",
    F_STAT, "lines 'rag - asmos', 'system_d - rag', 'system_d - asmos'",
    value={"test": "paired bootstrap (10k resamples) and Wilcoxon signed-rank on token-F1",
           "rag_minus_asmos": {"delta": 0.3358, "ci": [0.1494, 0.5228], "W": 100}, "system_d_minus_rag": {"delta": -0.3184, "ci": [-0.4990, -0.1406], "W": -94},
           "system_d_minus_asmos": {"delta": 0.0174, "ci": [-0.1546, 0.1862], "W": 30}},
    conditions=FS, run_id=FS_RUN, strength="soft", status="incomplete",
    notes="No p-values are reported, and W = -94 is negative (sign convention undefined; scipy's W is non-negative), so 'significant' cannot be written from this file. The three deltas are consistent with the token-F1 means in summary.csv (0.7513-0.4155 = 0.3358; 0.4329-0.7513 = -0.3184; 0.4329-0.4155 = 0.0174).")
add("fs_findings", "observation",
    "The authors' reading of the four-system run: RAG beats No-Memory; ASMOS+RAG recovers EM over ASMOS-memory but not token-F1 (CI spans 0); RAG still leads on token-F1; ASMOS-memory alone underperforms No-Memory on this static single-agent QA task",
    F_SUMM, "section 'Findings (measured, latest keyed run)'", strength="soft",
    notes='Verbatim: "ASMOS\'s demonstrated value (per E2) is routing/maintenance under change -- a different axis this dataset does not measure." and "no ownership/change dynamics".')
add("fs_gap_note", "limitation_noted",
    "Authors note that retrieval precision/recall and route@1/ownership accuracy are not computable on the single-agent RULER QA data (no relevant-doc labels, no owner labels); System D exercises routing with a single expert",
    F_SUMM, "section 'Gap report - metrics still not computable'", strength="soft",
    notes='Verbatim: "retrieval_precision / retrieval_recall -- no ground-truth relevant-doc labels in RULER QA." and "route@1 / ownership_accuracy -- single-agent RULER QA has no owner labels".')

# ================================================================= README (soft) - partially stale snapshot
RD = "README key-results table; gpt-4o-mini temperature 0; mean +/- std over N=5 seeds unless noted; artifact not in the package"
READ_NOTE = " Source artifact is not in the package, so this README value cannot be checked. The README predates the N=10 run and the 2026-08-07 correction."
add("rd_cost", "result",
    "README: routing cost reduction A1 vs A0 of -23.84% +/- 0.15 LLM tokens per query at equal accuracy 0.545 (N=5, corpus of 11 queries)",
    F_README, "Key results table row 1", strength="soft", status="unverifiable",
    value={"metric": "llm_token_reduction_pct_A1_vs_A0", "value": -23.84, "spread": {"type": "std", "value": 0.15}, "n": 5, "answer_accuracy": 0.545},
    conditions=RD + "; artifact transactive_seeds_20260621_b4b1094.json; query count 11 inferred from REPRODUCIBILITY.md row 'n=11'; embedder unconfirmed",
    quantity="cost_reduction_pct_A0_vs_A1|n_queries=11|N=5|gpt-4o-mini",
    notes="Different experiment from the n=50/N=10 headline (22.0911%): different query set and seed count, so a different quantity and not a conflict. REPRODUCIBILITY.md names n=50/N=10 -22.09% as the paper claim; which one is the headline is Checkpoint Q-001." + READ_NOTE)
add("rd_ablation", "result",
    "README: cost cause is ownership evolution: A1 vs A2 (frozen prior) gap +39.14 +/- 0.43 tokens per query, never inverts (min +38.6), verdict SUPPORTED",
    F_README, "Key results table row 2", strength="soft", status="unverifiable",
    value={"metric": "a1_a2_gap_tokens_per_query", "value": 39.14, "spread": {"type": "std", "value": 0.43}, "n": 5, "min": 38.6, "design": "ablation"},
    conditions=RD + "; artifact transactive_seeds_20260621_b4b1094.json; 11-query corpus", quantity="a1_a2_gap_tokens_per_query|n_queries=11|N=5|gpt-4o-mini",
    notes="The n=50 analogue (E-a1_a2_gap, 38.922) is consistent in size but is a different quantity." + READ_NOTE)
add("rd_token_audit", "result",
    "README: o200k_base context-token recount keeps the headline at 23.84% and moves context tokens from 34.33% to 34.06%",
    F_README, "Key results table row 3", strength="soft", status="unverifiable",
    value={"headline_pct": 23.84, "context_pct_before": 34.33, "context_pct_after": 34.06}, conditions=RD + "; tiktoken o200k_base; artifact token_audit_20260623_fd5d07a.md",
    notes=READ_NOTE)
add("rd_e2_stat", "result",
    "README: E2 stationary - route@1 1.000 vs 1.000, answerability 0.909 vs 0.727 (MiniLM)",
    F_README, "Key results table row 4", strength="soft", status="unverifiable",
    value={"asmos_route_at_1": 1.0, "classifier_route_at_1": 1.0, "asmos_answerability": 0.909, "classifier_answerability": 0.727}, conditions=RD + "; MiniLM; artifact e2_stationary_20260624_124855.json",
    notes="Agrees with the MiniLM shared-tau row of e2_cross_model_summary (a checkable file)." + READ_NOTE)
add("rd_e2_drift", "result", "README: E2 drift - ASMOS regret 7.90 with 0 retrains versus classifier 1-3 retrains",
    F_README, "Key results table row 5", strength="soft", status="unverifiable",
    value={"asmos_cumulative_regret": 7.90, "asmos_retrains": 0, "classifier_retrains": "1-3"}, conditions=RD + "; MiniLM; artifact e2_reviewer_fix_20260624_124952.json", notes=READ_NOTE)
add("rd_e2_refut", "result", "README: E2 refutation (weakest regime) - ASMOS regret 25.23, recovers 3 of 5, 0 retrains; only zero-retrain arm that recovers",
    F_README, "Key results table row 6", strength="soft", status="unverifiable",
    value={"asmos_cumulative_regret": 25.23, "recovers": "3/5", "asmos_retrains": 0}, conditions=RD + "; MiniLM; artifact e2_refutation_20260624_125104.json", notes=READ_NOTE)
add("rd_e2_newtopic", "result", "README: E2 new-topic (MiniLM) - ASMOS regret 4.32, routes 5/5, 0 retrains ('clean win')",
    F_README, "Key results table row 7", strength="soft", status="unverifiable",
    value={"metric": "cumulative_regret", "value": 4.32, "routes": "5/5", "retrains": 0}, conditions=RD + "; MiniLM; artifact e2_new_topic_20260624_125140.json",
    quantity="e2_new_topic_asmos_cumulative_regret|embedder=MiniLM-L6-v2",
    notes="Compare the checkable new-topic runs with MPNet (3.24) and BGE-M3 (0.92): different embedders, not conflicts. README also says the BGE (bge-small) new-topic cell was excluded as degenerate; the BGE-M3 run in the package is a later, different-model run." + READ_NOTE)
add("rd_e7", "result", "README: E7 cross-model - ASMOS 0 retrains in every completed cell (MiniLM 4/4, MPNet 4/4, BGE 3/4)",
    F_README, "Key results table row 8", strength="soft", status="unverifiable",
    value={"asmos_retrains": 0, "cells_completed": {"MiniLM": "4/4", "MPNet": "4/4", "BGE": "3/4"}}, conditions=RD + "; artifact e7_cross_model_20260704_001210_5351faf.{json,md}",
    notes="REPRODUCIBILITY.md later lists E7 as '4 families; reversal step 26' (adds bge-m3); the README cell counts are an earlier snapshot." + READ_NOTE)
add("rd_e5", "negative_result", "README: E5 convergence sample-efficiency is FLAT - 0 of 12 win cells versus the trust-only ablation (honest null)",
    F_README, "Key results table row 9", strength="soft", status="unverifiable",
    value={"win_cells": 0, "cells": 12}, conditions=RD + "; keyed, no LLM, canonical population; artifact e5_keyed_20260703_110618_29fefd3.json; docs/e5_decision_memo.md",
    notes="REPRODUCIBILITY.md agrees: 'E5 keyed sweep (0/12 win cells - honest null)'. Negative result: needs a reporting decision." + READ_NOTE)
add("rd_multi", "result", "README: multi-agent mechanism coherence (single run, no seeds) - route@1 0.917 (22/24); ownership evolves off the 0.42 prior on all 4 topics",
    F_README, "Key results table row 10", strength="soft", status="unverifiable",
    value={"metric": "route_at_1", "value": 0.917, "n_correct": 22, "n": 24, "prior": 0.42, "topics": 4}, conditions=RD + "; MiniLM; imposed partition; artifact eval_ladder_20260621_2c9a4c9.json",
    quantity="multi_agent_route_at_1|eval_ladder_20260621",
    notes="The archived technical report gives the same figure (superseded there)." + READ_NOTE)
add("rd_tau", "result", "README: 2026-07-07 MiniLM rerun reproduces the routing geometry (separability 0.2666/0.1024, tau = 0.351492) to 4 decimal places",
    F_README, "Notes on honesty, bullet 1", strength="soft", status="conflicting",
    value={"metric": "routing_tau", "value": 0.351492, "separability_within": 0.2666, "separability_cross": 0.1024}, conditions="MiniLM rerun; transactive_experiment_20260707_aed941c.{json,md} (absent)",
    quantity="routing_tau_default", conflicts_with=["n10_tau"],
    notes="README prints tau = 0.351492; the N=10 artifact and both E2 new-topic configs record 0.351493 (a 1e-6 difference, immaterial to the results but a recorded discrepancy in a headline parameter). README describes the value from a different (rerun) artifact.")
add("n10_tau", "method_detail", "Routing threshold tau frozen for the N=10 run is 0.351493 (same asmos_tau in both E2 new-topic configs)",
    F_N10, "key=frozen_tau", value={"metric": "routing_tau", "value": n10["frozen_tau"]}, conditions=COND_N10, run_id=RUN_N10,
    quantity="routing_tau_default", conflicts_with=["rd_tau"], status="conflicting",
    resolution={"chosen": "n10_tau", "reason": "The stamped N=10 result file and the two E2 configs (checkable primary records used by the reported experiments) agree on 0.351493; the README figure is a prose value from a different, absent rerun artifact.", "by": "agent"},
    notes="README limitation: tau is tuned in-corpus rather than on a held-out split; REPRODUCIBILITY.md lists a held-out tau experiment (tau_heldout 0.333) whose artifact is absent.")
add("rd_cover", "observation", "README: roughly 80-85% of the frozen v1.0 spec is implemented and unit-tested (2026-06-30 audit in docs/mem9.md)",
    F_README, "Status & limitations, bullet 1", strength="soft", status="unverifiable", value={"implementation_coverage_pct": "80-85"}, conditions="docs/mem9.md not in package")
add("rd_tests", "result", "README: local pytest run on the branch reports 342 passed, 0 failed, 2 skipped",
    F_README, "Status & limitations, 'Tests' bullet", strength="soft", status="conflicting", value=342,
    conditions="pytest, full suite; skipped 2, failed 0; README snapshot (earlier revision)", quantity="pytest_passed_count_full_suite",
    conflicts_with=["rp_tests"], notes="Same quantity as REPRODUCIBILITY.md (412 passed, 7 skipped). Both are prose claims about local runs; no CI artifact or test log is in the package (README: 'A recorded CI pass/coverage artifact is an outstanding item'). Left unreconciled; no claim may cite either.")
add("rp_tests", "result", "REPRODUCIBILITY.md: full pytest suite 412 passed, 7 skipped, 0 failed (native, Windows, python 3.12.5)",
    F_REPRO, "section 5 'Verified here'", strength="soft", status="conflicting", value=412,
    conditions="pytest, full suite; skipped 7, failed 0; native Windows python 3.12.5", quantity="pytest_passed_count_full_suite",
    conflicts_with=["rd_tests"], notes="See E-rd_tests. Unreconciled on purpose.")

# README limitations, rationale, method
def lim(key, summary, anchor, quote, status="ok", note_extra="", path=F_README):
    add(key, "limitation_noted", summary, path, anchor, strength="soft", status=status, notes='Verbatim: "%s"%s' % (quote, note_extra))


lim("rd_lim_rag", "Authors state ASMOS does not beat RAG on span-retrieval QA (it is not a QA-accuracy method)", "What it shows / what it does not",
    "ASMOS does **not** beat RAG on span-retrieval QA (it is not a QA-accuracy method)")
lim("rd_lim_organic", "Authors state ownership asymmetry does not emerge organically because the corpus is deliberately constructed", "What it shows / what it does not",
    "ownership asymmetry does **not** emerge organically (the corpus is deliberately constructed)")
lim("rd_lim_conv", "Authors state the convergence / sample-efficiency hypothesis was tested and returned a FLAT null", "What it shows / what it does not",
    "the convergence / sample-efficiency hypothesis was tested and returned an honest **FLAT null**",
    note_extra=" Also: 'Convergence is a null, not a gap ... The scope condition (discriminative refutation) is stated as future pre-registered work.'")
lim("rd_lim_descoped", "Authors list descoped items: agent-specific memory projection (no module), contradiction detection (refutation only when supplied), continuous forgetting (OFF by default)", "Status & limitations, 'Explicitly descoped'",
    "Explicitly descoped ... agent-specific memory projection (no module; the store is global); contradiction detection ... the `contradictory` flag is never computed or acted on -- refutation is claimed only when *supplied* as a verification outcome; continuous forgetting (lifecycle logic and tests exist but are OFF by default")
lim("rd_lim_llm", "Authors state every LLM number uses gpt-4o-mini and N=5 is below a publication N >= 10, with the N >= 10 rerun pending an API key", "Status & limitations, 'Single LLM; N=5'",
    "Single LLM; N=5. Every LLM number uses `gpt-4o-mini`. N=5 is tight ... but below a publication N >= 10. The N >= 10 keyed centerpiece rerun is pending a valid `OPENROUTER_API_KEY`",
    status="superseded", note_extra=" SUPERSEDED: the N=10 artifact (seeds 11-110) exists and CORRECTIONS.md records qwen3-30b-a3b and qwen-2.5-72b cost runs, so 'single LLM' and 'N=10 pending' are stale.")
lim("rd_lim_tau", "Authors state tau is tuned in-corpus rather than on a held-out split; QA-ladder grading is LLM-judged; multi-agent validation is one seedless run with an imposed partition; REUSE_THRESHOLD is an untuned placeholder (0.80) that feeds none of the reported numbers",
    "Status & limitations, 'Other flagged caveats'",
    "tau is tuned in-corpus rather than on a held-out split; QA-ladder grading is LLM-judged ... multi-agent validation is one seedless run with an imposed partition; `REUSE_THRESHOLD` ... is an untuned placeholder (0.80)")
lim("rd_lim_embedder", "Authors state the centerpiece 20260621 run's embedder (lexical-hash fallback vs MiniLM) is unconfirmed; the LLM-token headline is API-exact and embedder-independent; the token recount under confirmed MiniLM is pending a valid API key", "Notes on honesty, bullet 1",
    "The centerpiece `20260621` run's embedder (lexical-hash fallback vs MiniLM) is **unconfirmed**.")
lim("rd_lim_bge", "Authors state the BGE (bge-small) new-topic E7 cell is excluded because the run fell back to the hash embedder (embedder=None, degenerate regret 0.0)", "Notes on honesty, bullet 2",
    "The BGE new-topic E7 cell is **excluded**: its run fell back to the hash embedder (embedder=None, degenerate regret 0.0) and is reported as incomplete rather than fabricated.")
lim("rd_lim_ci", "Authors state a recorded CI pass/coverage artifact is an outstanding item", "Status & limitations, 'Tests'",
    "A recorded CI pass/coverage artifact is an outstanding item.")
add("rd_rat_method", "method_detail",
    "ASMOS ownership layer: ownership is learned online from verification-gated reputation; a verified claim raises an agent's topic ownership, a refuted claim lowers it; queries route to the learned owner with a confidence-gated fallback to global search; router scores Sim x Ownership with a tau-gated fallback",
    F_README, "opening paragraph; Repository layout (routing/router.py)", strength="soft",
    notes='Verbatim: "a verified claim raises an agent\'s ownership of a topic, a refuted claim lowers it, and queries route to the learned owner with a confidence-gated fallback to global search."')
add("rd_rat_metric", "rationale_stated",
    "Reason given for cost and answerability as the headline metrics: answer accuracy saturates under parametric model knowledge, making cost and answerability the discriminative metrics",
    F_README, "What it shows / what it does not, (3)", strength="soft",
    notes='Verbatim: "an evaluation finding that answer accuracy saturates under parametric model knowledge, making cost and answerability the discriminative metrics."')
add("rd_rat_embedder", "rationale_stated",
    "Reason given for requiring the MiniLM embedder: the lexical-hash fallback is a degraded offline mode, not the evaluation baseline; without embeddings the store falls back silently to hash",
    F_README, "Installation & requirements", strength="soft",
    notes='Verbatim: "Without it, the store degrades to an offline 64-dim **lexical-hash** provider -- a degraded offline mode, **not** the evaluation baseline."')
add("rp_p1", "result",
    "REPRODUCIBILITY.md: without the embeddings extra the store falls back to a 64-dim lexical hash embedder and precision@1 drops 1.000 to 0.778",
    F_REPRO, "section 2 Native path, embeddings extra", strength="soft", status="conflicting",
    value={"metric": "routing_precision_at_1", "value": 0.778, "with_minilm": 1.0},
    conditions="lexical-hash fallback vs MiniLM; system and regime not named in the sentence; 1.000 matches ASMOS with MiniLM in e2_cross_model_summary",
    quantity="e2_cross_model|routing_precision_at_1|embedder=lexical-hash (fallback)|arm=A1_ASMOS_SHARED_TAU", conflicts_with=["cm_lexical_A1_ASMOS_SHARED_TAU"],
    notes="e2_cross_model_summary gives ASMOS (shared tau) p@1 0.667 under lexical-hash; 0.778 is instead the A4 classifier calibrated-tau value in that file. The sentence does not name the arm, so the mapping to ASMOS is the agent's reading of '1.000'.")
# link the cross-model item back and give it the resolution
for e in items:
    if e["id"] == ids["cm_lexical_A1_ASMOS_SHARED_TAU"]:
        e["_conflicts_with"] = ["rp_p1"]
        e["status"] = "conflicting"
        e["notes"] += " Also incomplete: no variance/seed count recorded."
        e["_resolution"] = {"chosen": "cm_lexical_A1_ASMOS_SHARED_TAU", "reason": "The stamped JSON enumerates every arm and embedder explicitly (checkable primary record); the REPRODUCIBILITY sentence is prose that names no arm and whose 0.778 equals a different arm's value.", "by": "agent"}
add("rp_misc", "result",
    "REPRODUCIBILITY.md lists results with absent artifacts: held-out tau 0.333 (criteria pass); E6 natural asymmetry OCI 0.9943 with route@1 100/0; four-system 22/24 abstention; E7 four embedder families with reversal at step 26",
    F_REPRO, "section 3 headline map rows", strength="soft", status="unverifiable",
    value={"tau_heldout": 0.333, "E6_OCI": 0.9943, "E6_route_at_1": "100/0", "four_system_abstention": "22/24", "E7_families": 4, "E7_reversal_step": 26},
    conditions="artifacts heldout_tau_*.json, e6_eval_*.json, four_system_v1_*/, e7_*.json absent from the package",
    notes="'22/24 abstention' is not comparable to answerability = 1.0 for all four systems in results/summary.csv (different metric or different run). Not used for any candidate claim.")

# ================================================================= CORRECTIONS / CONTRACT rationale and method
add("rat_neff", "rationale_stated",
    "Reason for reporting n_eff beside every effect size: a bare r = 1.0 invites the false reading that every query improved",
    F_CORR, "section 'Reported estimator'", strength="soft",
    notes='Verbatim: "a bare \\"r = 1.0\\" invites the reading \\"every query improved\\", which is false for 28% of that set. A zero delta there is the mechanism working as specified -- the router correctly falls back to global search and issues a byte-identical request."')
add("corr_direction", "observation",
    "The authors argue the original defect could only understate a positive effect (mu_buggy > mu_correct and sigma_buggy > sigma_correct when n > n_eff), so the correction runs upward",
    F_CORR, "section 'What was wrong' - Direction", strength="soft",
    notes='Verbatim: "That is a theorem about the two formulas, fixed before any of this data was touched". Stored 0.688 -> 0.941; 0.5659 -> 0.9463; 0.0389 -> 1.0 all move upward; the Rosenthal N=2n reading (0.568) would have moved the headline down, which the authors say is why Kerby was chosen on principle, not size.')
add("ct_schema", "implementation_detail",
    "Memory contract v1.2 (frozen): Checkpoint with SYS/LLM/CMP field origins; lifecycle NEW -> VALIDATED -> PROMOTED -> MERGED -> ARCHIVED -> FORGOTTEN; from_agent_output rejects computed (CMP) fields (Invariant 8); immutable layer never forgotten (Invariant 4); predicted_reuse never overwritten (Invariant 6)",
    F_CONTRACT, "Checkpoint fields; Contract guarantees", strength="soft",
    value={"contract_version": "1.2", "lifecycle": ["NEW", "VALIDATED", "PROMOTED", "MERGED", "ARCHIVED", "FORGOTTEN"], "invariants_cited": [4, 6, 8]},
    notes="Specification document, not a result. Backend/ranking numbers are not in it.")
add("ct_stale", "implementation_detail",
    "CONTRACT.md 'Not in scope today' says there is no storage backend, no embeddings, no ChromaDB (Week 2)",
    F_CONTRACT, "section 'Not in scope today'", strength="soft", status="superseded",
    notes="Superseded: the same file's package-path note and README describe src/asmos/memory/store.py with Chroma and a MiniLM embedder as implemented. Do not describe the memory store as absent.")

# ================================================================= archived technical report - ALL superseded
TR = " ARCHIVED report (self-declared: 'superseded by docs/paper/paper.md ... do not cite numbers from here'); source artifact absent from the package. Do not use."
TC = "archived technical report snapshot 2026-06-23; gpt-4o-mini temperature 0; N=5 seeds 11,22,33,44,55; 11-query corpus"
add("tr_headline", "result", "SUPERSEDED (archived report): transactive routing cut LLM tokens by 23.8% +/- 0.2 (per-seed range 23.68%-24.03%) at equal accuracy 0.545 and answerability 0.909",
    F_TECH, "section 2 'The headline (A1 vs A0)'", strength="soft", status="superseded",
    value={"metric": "llm_token_reduction_pct_A0_vs_A1", "value": 23.8, "spread": {"type": "std", "value": 0.2}, "n": 5, "range_pct": [23.68, 24.03]},
    conditions=TC, quantity="cost_reduction_pct_A0_vs_A1|n_queries=11|N=5|gpt-4o-mini|archived_report", notes="Rounded restatement of the README 23.84 figure." + TR)
add("tr_table", "result", "SUPERSEDED (archived report): per-arm table A0 179.8+/-0.3, A1 136.9+/-0.1, A2 176.0+/-0.5, A3 120.5+/-0.1 tokens per query; accuracy 0.545/0.545/0.545/0.455; answerability 0.909/0.909/0.909/0.455",
    F_TECH, "section 2 table", strength="soft", status="superseded",
    value={"tokens_per_query": {"A0": 179.8, "A1": 136.9, "A2": 176.0, "A3": 120.5}, "accuracy": {"A0": 0.545, "A1": 0.545, "A2": 0.545, "A3": 0.455},
           "answerability": {"A0": 0.909, "A1": 0.909, "A2": 0.909, "A3": 0.455}}, conditions=TC, notes="Different corpus from the n=50 run (which has A0 180.154, A1 140.356 tokens per query)." + TR)
add("tr_gap", "result", "SUPERSEDED (archived report): A1-A2 gap 39.1 +/- 0.4 tokens per query, per-seed [39.7, 39.1, 38.9, 38.6, 39.4], min +38.6",
    F_TECH, "section 2 'The load-bearing result'", strength="soft", status="superseded",
    value={"gap": 39.1, "std": 0.4, "per_seed": [39.7, 39.1, 38.9, 38.6, 39.4]}, conditions=TC, notes="README states 39.14 +/- 0.43." + TR)
add("tr_multi", "result", "SUPERSEDED (archived report): multi-agent route@1 = 0.917 (22/24), ownership ~0.987 on all four owned topics, 68 of 600 verified checkpoints Class C",
    F_TECH, "section 5 'Multi-agent mechanism validation'", strength="soft", status="superseded",
    value={"route_at_1": 0.917, "ownership_after": 0.987, "class_c_no_update": "68/600"}, conditions="eval_ladder_20260621_2c9a4c9.json (absent)", notes=TR.strip())
add("tr_dens", "result", "SUPERSEDED (archived report): organic verification density measured at 31.6% (mem6)",
    F_TECH, "section 3 A-2", strength="soft", status="superseded", value={"organic_verification_density_pct": 31.6}, conditions="mem6 (absent)", notes=TR.strip())
add("tr_ladder_rag", "result", "SUPERSEDED (archived report): eval-ladder RAG containment 75.0%, token-F1 76.5% on 24 questions (eval_ladder_20260618)",
    F_TECH, "section 5 ladder table, RAG row", strength="soft", status="superseded",
    value={"metric": "containment", "value": 0.75, "token_f1": 0.765, "n": 24}, conditions="24 RULER/EventQA questions; gpt-4o-mini; older ladder run",
    quantity="containment|RULER QA n=24|gpt-4o-mini|system=rag", conflicts_with=["fs_rag_acc"],
    resolution={"chosen": "fs_rag_acc", "reason": "The archived report is self-declared superseded and its ladder run is not in the package; results/summary.csv is the current machine-written record for the same 24-question RAG containment.", "by": "agent"},
    notes="Current keyed four-system run gives RAG containment 0.7083 and token-F1 0.7513 on 24 questions. Same quantity, different value; the archived report is superseded." + TR)
add("tr_ladder_other", "result", "SUPERSEDED (archived report): No-Memory containment 29.2% (documented floor) / 33.3% (same session), MemGPT 62.5% containment and 69.2% token-F1, Single-ASMOS 16.7% flagged [VERIFY] with no committed artifact",
    F_TECH, "section 5 ladder table", strength="soft", status="superseded",
    value={"no_memory_documented": 0.292, "no_memory_same_session": 0.333, "memgpt_containment": 0.625, "memgpt_f1": 0.692, "single_asmos_containment": 0.167},
    conditions="older ladder run", notes="The report itself says the Single-ASMOS 16.7% has no committed artifact. Current four-system ASMOS-memory containment is 0.1667." + TR)
add("tr_sep", "result", "SUPERSEDED (archived report): within-domain topic-centroid cosine 0.267, cross-domain 0.102",
    F_TECH, "section 2 Setup", strength="soft", status="superseded", value={"within": 0.267, "cross": 0.102}, conditions=TC,
    notes="Matches the checkable N=10 artifact at 3 dp (0.2666, 0.1024)." + TR)
add("tr_ttco", "result", "SUPERSEDED (archived report): time-to-correct-owner in verified claims: r_architectures 2, r_benchmarks 6, r_theory 10, c_api_usage 14, c_error_handling 20, c_perf_optimization 24",
    F_TECH, "section 5 Figure 2 note", strength="soft", status="superseded",
    value={"r_architectures": 2, "r_benchmarks": 6, "r_theory": 10, "c_api_usage": 14, "c_error_handling": 20, "c_perf_optimization": 24}, conditions=TC, notes=TR.strip())
add("tr_lim_seed", "limitation_noted", "SUPERSEDED (archived report): N = 5 seeds is small though tight; context-token proxy was a whitespace word count; Multi-ASMOS QA cell unmeasured; Single-ASMOS 16.7% unbacked",
    F_TECH, "section 6", strength="soft", status="superseded", notes="Stale: N=10 exists; the live limitations are in the README." + TR)

# ================================================================= resolve references and write outputs
for e in items:
    e["conflicts_with"] = [ids[k] for k in e.pop("_conflicts_with")]
    e["derived_from"] = [ids[k] for k in e.pop("_derived_from")]
    r = e.pop("_resolution")
    if r:
        r = dict(r)
        r["chosen"] = ids[r["chosen"]]
        e["resolution"] = r
    if not e["conflicts_with"]:
        del e["conflicts_with"]
    if not e["derived_from"]:
        del e["derived_from"]
    if e["status"] == "conflicting" and "conflicts_with" not in e:
        raise SystemExit("conflicting without partner " + e["id"])

# make conflict links symmetric
byid = {e["id"]: e for e in items}
for e in items:
    for c in e.get("conflicts_with", []):
        p = byid[c]
        p.setdefault("conflicts_with", [])
        if e["id"] not in p["conflicts_with"]:
            p["conflicts_with"].append(e["id"])

Path(".rcs/evidence").mkdir(parents=True, exist_ok=True)
Path(".rcs/claims").mkdir(parents=True, exist_ok=True)
json.dump({"project_root": "project", "generated_at": NOW, "generated_by": GEN, "items": items},
          open(".rcs/evidence/research_evidence.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ================================================================= inventory
INV = {
    "project/ASMOS_technical_report.md": ("note/draft", "ARCHIVED (self-declared, 2026-06-23 snapshot): superseded by docs/paper/paper.md. All numbers marked status=superseded; no number used."),
    "project/CONTRACT.md": ("spec", "Memory contract v1.2. Method/implementation detail only; its 'Not in scope today' paragraph is stale (superseded)."),
    "project/README.md": ("readme", "Partially stale snapshot: key-results table cites artifacts absent from the package (values unverifiable); 'single LLM' and 'N>=10 pending' statements are stale (superseded)."),
    "project/REPRODUCIBILITY.md": ("readme", "Runbook dated after the 2026-08-07 correction; declares the corrected effect size authoritative. Soft; corroborates the N=10 headline."),
    "project/data/results/CORRECTIONS.md": ("note", "Authority for superseded effect-size/z values (Correction 1, 2026-08-07). Marks stored 0.6881/4.8653/0.6894/0.5659/0.0389/0.7922/132.5 as superseded."),
    "project/data/results/e2_cross_model_summary_20260630_045130.json": ("result", "Machine-written E2 cross-model summary; single run; no variance."),
    "project/data/results/e2_new_topic_20260703_182558.json": ("result", "E2 new-topic run, MPNet embedder, 5 seeds."),
    "project/data/results/e2_new_topic_20260726_104315.json": ("result", "E2 new-topic run, BGE-M3 embedder, 5 seeds (different embedder from the 0703 run, not a duplicate)."),
    "project/data/results/effect_size_correction_20260807_78127c8.json": ("result", "Corrected-statistics artifact; holds corrected and stored (superseded) values for five cost artifacts, four of which are absent."),
    "project/data/results/n10_cost_expanded_20260726_93f9058.json": ("result", "N=10 cost experiment (headline). Its stored wilcoxon_n10.z_statistic and effect_size_r are superseded; W, p, headline %, CI are unchanged."),
    "project/results/comparison_table.md": ("result", "Four-system table (rounded copy of summary.csv)."),
    "project/results/statistics.md": ("result", "Four-system paired bootstrap/Wilcoxon deltas; no p-values; W=-94 has an undefined sign convention."),
    "project/results/summary.csv": ("result", "Machine-written four-system aggregate (n=24)."),
    "project/results/summary.md": ("result", "Four-system narrative table with std and CIs; says its numbers come from per-system JSONs that are absent."),
}
files = []
for p in sorted(Path("project").rglob("*")):
    if not p.is_file():
        continue
    rp = p.as_posix()
    st = p.stat()
    tc, note = INV[rp]
    files.append({"path": rp, "type_class": tc, "size_bytes": st.st_size,
                  "modified": datetime.fromtimestamp(st.st_mtime, timezone.utc).isoformat(timespec="seconds"),
                  "opened": True, "skip_reason": None, "sha256": sha(rp)[7:], "notes": note})
json.dump({"project_root": "project", "generated_at": NOW, "generated_by": GEN, "n_files": len(files), "files": files,
           "referenced_but_absent": ["docs/paper/paper.md", "docs/paper/claim_ledger_v2.md", "docs/paper/evidence_ledger.md", "docs/effect_size_audit.md", "docs/w6_fix_plan_v2.md",
                                      "docs/n50_cost_expansion_report.md", "docs/e5_decision_memo.md", "docs/mem5-mem9.md", "data/results/transactive_seeds_20260621_b4b1094.json",
                                      "data/results/transactive_cost_expanded_20260724_a274137.json", "data/results/transactive_cost_expanded_20260725_93f9058.json",
                                      "data/results/transactive_cost_expanded_20260805_437bb6b.json", "data/results/n50_supplementary_20260724_a274137.json",
                                      "data/results/e2_stationary_20260624_124855.json", "data/results/e2_reviewer_fix_20260624_124952.json", "data/results/e2_refutation_20260624_125104.json",
                                      "data/results/e2_new_topic_20260624_125140.json", "data/results/e7_cross_model_20260704_001210_5351faf.*", "data/results/e5_keyed_20260703_110618_29fefd3.json",
                                      "data/results/eval_ladder_20260621_2c9a4c9.json", "data/results/eval_ladder_20260618_872f399.json", "data/results/token_audit_20260623_fd5d07a.md",
                                      "results/{no_memory,rag,asmos,system_d}.json", "src/, scripts/, tests/, docs/paper/ASMOS/figures/"]},
          open(".rcs/evidence/project_inventory.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

print("evidence items:", len(items), "superseded:", sum(1 for e in items if e["status"] == "superseded"),
      "conflicting:", sum(1 for e in items if e["status"] == "conflicting"))
json.dump(ids, open(".rcs/corpus/id_map.json", "w"), indent=1)
