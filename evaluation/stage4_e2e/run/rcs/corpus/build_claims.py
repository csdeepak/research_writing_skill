#!/usr/bin/env python3
"""CORPUS_AGENT: writes .rcs/evidence/missing_evidence.json and .rcs/claims/claim_candidates.json (references evidence by key via id_map.json)."""
import json, os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")
GEN = "CORPUS_AGENT (rce/skill/agents/corpus_agent.md; .rcs/corpus/build_claims.py)"
ids = json.load(open(".rcs/corpus/id_map.json"))


def E(*keys):
    return [ids[k] for k in keys]


CL = []


def claim(cid, statement, ctype, ev, origin, status, basis="project_file", quote=None, scope=None, notes=None, blocked_by=None, rationale=None,
          licenses=None, quote_src=None):
    c = {"id": cid, "statement": statement, "claim_type": ctype, "evidence": ev, "origin": origin, "basis": basis, "status": status}
    if rationale:
        c["rationale"] = rationale
    if quote:
        c["author_quote"] = {"text": quote, "source": quote_src}
    if scope:
        c["scope"] = scope
    if licenses:
        c["suggested_licenses"] = licenses
    if blocked_by:
        c["blocked_by_checkpoint"] = blocked_by
    if notes:
        c["notes"] = notes
    c["author_confirmation"] = "pending"
    CL.append(c)


N10S = {"datasets": ["constructed asymmetric two-agent transactive corpus, 50 queries"], "conditions": "openai/gpt-4o-mini, temperature 0, 10 seeds (11-110), frozen tau 0.351493; seeds 11-55 pooled from an artifact absent from the package"}

claim("C001", "On the constructed 50-query transactive corpus (gpt-4o-mini, 10 seeds), A1 transactive routing used 22.0911% fewer LLM total tokens per query than A0 global search (bootstrap 95% CI 17.9313% to 26.2675%; per-seed range 21.932% to 22.154%).",
      "derived", E("n10_headline", "n10_ci", "n10_seed_pct", "n10_design", "n10_arm_means"), "author_stated", "VERIFIED",
      quote="Cost -22.09% (n=50/N=10), CI [17.93,26.27], Wilcoxon p=6.79e-9, rank-biserial r=0.941 (n_eff=48 of 50)", quote_src="project/REPRODUCIBILITY.md section 3", scope=N10S,
      notes="Reproduced by CORPUS from the stored per-query arrays (22.0911). Constructed corpus: do not generalise to organic populations. The 23.84% figure is a different experiment (see C020, blocked).")
claim("C002", "The one-sided Wilcoxon signed-rank test on the 50 per-query A0-A1 token deltas gave W = 1141.5 and p = 6.788e-09 (n_eff = 48 non-zero pairs); the matched-pairs rank-biserial correlation is r = 0.9413 (T+ = 1141.5, T- = 34.5), z = 5.6786.",
      "derived", E("n10_wilcoxon", "n10_r_corr", "n10_z_corr", "n10_design"), "author_stated", "VERIFIED",
      quote="The Wilcoxon statistic W = 1141.5, the one-sided p = 6.79x10^-9, the point estimate and the bootstrap confidence interval are unchanged.", quote_src="project/data/results/CORRECTIONS.md", scope=N10S,
      licenses=[{"type": "significance_test", "evidence": E("n10_wilcoxon")}],
      notes="Must state n_eff = 48 of 50 beside r. NEVER use the superseded r = 0.6881 or z = 4.8653 (E-n10_r_stored, E-n10_z_stored). Rosenthal z/sqrt(N) is retired. p is one-sided and there is a single comparison.")
claim("C003", "The width of the N=10 confidence interval (8.3362 percentage points) is set by inter-query heterogeneity, not seed noise: per-seed std is 0.069 percentage points, so adding seeds does not narrow it.",
      "observed", E("n10_ci_diag", "n10_seed_pct", "n10_ci"), "author_stated", "VERIFIED",
      quote="More seeds cannot narrow a CI driven by inter-query heterogeneity.", quote_src="project/data/results/n10_cost_expanded_20260726_93f9058.json ci_variance_diagnosis.conclusion", scope=N10S)
claim("C004", "Across 50 queries and 10 seeds, the mean per-query LLM tokens were A0 180.154, A1 140.356, A2 (frozen ownership) 179.278 and A3 (similarity only) 123.444; A2 is within 0.876 tokens of A0 and 38.922 tokens above A1.",
      "derived", E("n10_arm_means", "n10_a1_a2_gap", "n10_perq", "n10_tokens_arm"), "inferred", "VERIFIED", scope=N10S,
      notes="Computed by CORPUS_AGENT (arithmetic mean of stored arrays). No per-seed gap or test for A1-A2 at n=50.")
claim("C005", "The saving is attributable to ownership evolution: with ownership frozen at the prior (A2) the router falls back to global search (route@1 0.0) and recovers essentially none of the saving.",
      "interpretation", E("n10_a1_a2_gap", "n10_route", "n10_design"), "author_stated", "NEEDS_REVIEW",
      quote="Cost cause = ownership *evolution* (A1 vs A2 frozen-prior ablation)", quote_src="project/README.md Key results row 2", scope=N10S,
      licenses=[{"type": "causal_design", "evidence": E("n10_design")}],
      notes="Rests on one constructed corpus; the README's own A1-A2 statistic (+39.14 +/- 0.43, min +38.6) is from an absent artifact and is not cited here. No significance test or per-seed gap for A1-A2 at n=50. Ablation design licenses 'attributable within this corpus', not organic-population claims.")
claim("C006", "In the five newest seeds (66-110), answerability was 0.98 for A0, A1 and A2 and 0.58 for the similarity-only arm A3 in every seed.",
      "measured", E("n10_answerability"), "inferred", "VERIFIED", scope=dict(N10S, conditions="seeds 66-110 only"))
claim("C007", "In the five newest seeds (66-110), answer accuracy was 0.72 for A0 and A2 in every seed, 0.68 to 0.70 for A1 (below A0 in every seed) and 0.54 to 0.56 for A3; no paired test of the accuracy difference is available.",
      "measured", E("n10_acc"), "inferred", "VERIFIED", scope=dict(N10S, conditions="seeds 66-110 only"),
      notes="Negative/qualifying result for any 'equal accuracy' wording. Needs a reporting decision (negative_result_decisions).")
claim("C008", "In the five newest seeds (66-110), route@1 was 0.909 for A1, 0.0 for A0 and A2 (which do not route to a single owner) and 0.614 for A3.",
      "measured", E("n10_route"), "inferred", "VERIFIED", scope=dict(N10S, conditions="seeds 66-110 only"))
claim("C009", "E2 new-topic regime with the MPNet embedder (5 seeds): ASMOS cumulative regret was 3.24 +/- 1.2986 with 0 retrains and the new topic routed in 5 of 5 seeds; the frozen classifier never routed it (regret 10.0), retrain-every-5 had regret 4.8 +/- 0.4 (2 retrains) and retrain-every-10 had regret 9.0 (1 retrain).",
      "measured", E("nt_mpnet_asmos", "nt_mpnet_clf", "nt_mpnet_curve"), "inferred", "VERIFIED",
      scope={"conditions": "E2 non-stationary new-topic, embedder all-mpnet-base-v2, 10 steps, seeds 0-4, 5 eval queries per step"},
      notes="Do not pool with C010: different embedder. ASMOS consumed 10 labels in this artifact (see C022/Q-004).")
claim("C010", "E2 new-topic regime with the BGE-M3 embedder (5 seeds): ASMOS cumulative regret was 0.92 +/- 0.4118 with 0 retrains and the new topic routed in 5 of 5 seeds; classifier baselines were identical to the MPNet run (10.0, 4.8, 9.0).",
      "measured", E("nt_bge_asmos", "nt_bge_clf", "nt_bge_curve"), "inferred", "VERIFIED",
      scope={"conditions": "E2 non-stationary new-topic, embedder BAAI/bge-m3, 10 steps, seeds 0-4, 5 eval queries per step"})
claim("C011", "In both E2 new-topic runs, per-step answerability is identical for all four arms (0.0 at step 0 rising to 1.0 at step 10), so it does not separate ASMOS from the classifiers in that regime.",
      "observed", E("nt_mpnet_answer", "nt_bge_answer"), "inferred", "VERIFIED")
claim("C012", "In the E2 cross-model summary (single run), with MiniLM ASMOS matched the classifier on route@1 (1.0 vs 1.0) with higher answerability (0.909 vs 0.727, lead 0.182); with the lexical-hash fallback embedder ASMOS route@1 was 0.667 versus 1.0, so ASMOS was not routing-competitive.",
      "measured", E("cm_obs_minilm", "cm_obs_lexical", "cm_minilm_A1_ASMOS_SHARED_TAU", "cm_lexical_A1_ASMOS_SHARED_TAU"), "inferred", "NEEDS_REVIEW",
      scope={"conditions": "shared-tau arms; single deterministic run; query count not stated"},
      notes="Incomplete: no variance/seeds. REPRODUCIBILITY.md says the lexical-hash p@1 is 0.778; the checkable JSON says 0.667 (recorded conflict, resolved to the JSON with a written reason).")
claim("C013", "On 24 RULER QA questions (gpt-4o-mini), containment/EM was 0.3333 for No-Memory, 0.7083 for RAG, 0.1667 for ASMOS-memory and 0.625 for ASMOS+RAG, with token-F1 0.5642, 0.7513, 0.4155 and 0.4329.",
      "measured", E("fs_no_memory_acc", "fs_rag_acc", "fs_asmos_acc", "fs_system_d_acc", "fs_summary_spread"), "author_stated", "VERIFIED",
      quote="RAG over No-Memory: EM 0.3333 -> 0.7083, token-F1 0.5642 -> 0.7513", quote_src="project/results/summary.md Findings 1",
      scope={"datasets": ["RULER QA n=24"], "conditions": "keyed run, single run, no seeds"},
      notes="EM equals containment in every row and system D has F1 below EM: metric definitions unknown (missing_evidence M005). Single run.")
claim("C014", "Paired token-F1 differences on the 24 questions: RAG exceeds ASMOS-memory by 0.3358 (bootstrap 95% CI 0.1494 to 0.5228); ASMOS+RAG is below RAG by 0.3184 (CI -0.4990 to -0.1406); ASMOS+RAG minus ASMOS-memory is +0.0174 (CI -0.1546 to +0.1862, spans zero).",
      "derived", E("fs_stats"), "author_stated", "NEEDS_REVIEW",
      quote="ASMOS+RAG (System D) over ASMOS-memory: ... (Delta not significant, CI spans 0).", quote_src="project/results/summary.md Findings 2",
      scope={"datasets": ["RULER QA n=24"]},
      notes="Soft source (statistics.md); no p-values, W = -94 has undefined sign convention: do NOT write 'significant'; the CI-excludes-zero wording is what the file supports.")
claim("C015", "On this static single-agent span-retrieval QA task ASMOS-memory alone scored below No-Memory and below RAG, and ASMOS did not beat RAG; the authors state ASMOS is not a QA-accuracy method.",
      "observed", E("fs_asmos_acc", "fs_no_memory_acc", "fs_rag_acc", "fs_stats", "fs_findings", "rd_lim_rag"), "author_stated", "VERIFIED",
      quote="ASMOS does **not** beat RAG on span-retrieval QA (it is not a QA-accuracy method)", quote_src="project/README.md",
      notes="Negative result; must be reported near the cost claims (SELECTIVE_REPORTING).")
claim("C016", "README-reported E2 results (MiniLM): stationary route@1 1.000 vs 1.000 with answerability 0.909 vs 0.727; drift regret 7.90 with 0 retrains vs classifier 1-3 retrains; refutation regret 25.23 recovering 3/5 with 0 retrains; new-topic regret 4.32, routes 5/5, 0 retrains.",
      "measured", E("rd_e2_stat", "rd_e2_drift", "rd_e2_refut", "rd_e2_newtopic"), "author_stated", "BLOCKED", blocked_by="Q-003",
      notes="Only the stationary row is corroborated (by the MiniLM row of e2_cross_model_summary). Source artifacts are absent; values are soft and unverifiable.")
claim("C017", "README-reported E7 cross-embedder replication: ASMOS used 0 retrains in every completed cell (MiniLM 4/4, MPNet 4/4, BGE 3/4).",
      "measured", E("rd_e7", "rp_misc"), "author_stated", "BLOCKED", blocked_by="Q-003", notes="Artifact absent; REPRODUCIBILITY.md later lists 4 families and a reversal at step 26 (superset).")
claim("C018", "The convergence / sample-efficiency hypothesis returned a FLAT null: 0 of 12 win cells against the trust-only ablation.",
      "measured", E("rd_e5", "rd_lim_conv"), "author_stated", "BLOCKED", blocked_by="Q-003", notes="Negative result. Artifact and decision memo absent; REPRODUCIBILITY.md repeats '0/12 win cells'.")
claim("C019", "In a single seedless multi-agent run, route@1 was 0.917 (22/24) and ownership moved off the 0.42 prior on all four topics.",
      "measured", E("rd_multi", "rd_lim_tau"), "author_stated", "BLOCKED", blocked_by="Q-003", notes="Artifact absent; imposed partition, one seedless run (author-stated caveat).")
claim("C020", "A1 transactive routing reduced LLM tokens per query by 23.84% +/- 0.15 versus global search at equal answer accuracy 0.545 (N=5, 11-query corpus).",
      "measured", E("rd_cost", "rd_token_audit"), "author_stated", "BLOCKED", blocked_by="Q-001",
      quote="Routing cost reduction (A1 transactive vs A0 global), equal accuracy 0.545 | -23.84% +/- 0.15 LLM tokens/query", quote_src="project/README.md Key results row 1",
      notes="Artifact absent; README/archived-report snapshot predates the n=50/N=10 headline. Which figure is the paper headline is undecided.")
claim("C021", "The A1-A2 gap on the 11-query corpus was +39.14 +/- 0.43 tokens per query and never inverted (min +38.6), a SUPPORTED cause attribution.",
      "measured", E("rd_ablation"), "author_stated", "BLOCKED", blocked_by="Q-001", notes="Artifact absent. The n=50 analogue is C004 (38.922).")
claim("C022", "ASMOS adapts to changing conditions at zero retraining and zero added labels, whereas a supervised classifier needs 1-6 retrains or fails.",
      "measured", E("nt_mpnet_asmos", "nt_bge_asmos", "nt_mpnet_clf", "rd_e2_drift"), "author_stated", "BLOCKED", blocked_by="Q-004",
      quote="at **zero retraining and zero added labels** where a supervised classifier needs 1-6 retrains or fails", quote_src="project/README.md",
      notes="The new-topic artifacts record labels_consumed = 10 for ASMOS (same as the retraining classifiers, 0 for the frozen classifier). 'Zero retraining' is supported (retrain_events 0); 'zero added labels' is contradicted or defined differently.")
claim("C023", "Routing on evolved ownership reduces cost at equal answer accuracy and answerability.",
      "measured", E("n10_acc", "n10_answerability", "rd_cost"), "author_stated", "BLOCKED", blocked_by="Q-002",
      quote="a **-23.8% LLM-token routing-cost** reduction at equal answer accuracy and answerability", quote_src="project/README.md",
      notes="Answerability is equal (0.98) in seeds 66-110; accuracy is not (A1 0.68-0.70 vs A0 0.72). The 'equal accuracy 0.545' figure is from the absent 11-query artifact.")
claim("C024", "Answer accuracy saturates under parametric model knowledge, so cost and answerability are the discriminative metrics for routing.",
      "interpretation", E("n10_acc", "fs_no_memory_acc", "fs_rag_acc", "rd_rat_metric"), "author_stated", "BLOCKED", blocked_by="Q-002",
      quote="answer accuracy saturates under parametric model knowledge, making cost and answerability the discriminative metrics", quote_src="project/README.md",
      notes="In the four-system RULER QA run accuracy is far from saturated (No-Memory EM 0.3333 vs RAG 0.7083), so the statement can hold at most for the transactive corpus.")
claim("C025", "The reported effect size is Kerby's matched-pairs rank-biserial correlation because it is the direct companion of the signed-rank test and has a single definition; Rosenthal z/sqrt(N) is not reported because its N is read three ways (0.803, 0.819, 0.568).",
      "measured", E("rat_kerby", "esc_estimator"), "author_stated", "VERIFIED", rationale="design_choice", basis="project_file",
      quote="Kerby is the direct companion to the signed-rank test actually run", quote_src="project/data/results/effect_size_correction_20260807_78127c8.json estimator_ruling")
claim("C026", "The signed-rank test keeps zero_method = wilcox (zero differences dropped) because switching to Pratt would change an already pre-registered p-value.",
      "measured", E("rat_wilcox", "esc_estimator"), "author_stated", "VERIFIED", rationale="design_choice",
      quote="NOT switched to Pratt: that would change an already pre-registered p-value after the fact.", quote_src="project/data/results/effect_size_correction_20260807_78127c8.json zero_handling")
claim("C027", "n_eff is reported beside every effect size because a bare r = 1.0 invites the false reading that every query improved.",
      "measured", E("rat_neff", "esc2_block"), "author_stated", "VERIFIED", rationale="design_choice",
      quote="a bare \"r = 1.0\" invites the reading \"every query improved\", which is false for 28% of that set", quote_src="project/data/results/CORRECTIONS.md")
claim("C028", "No multiplicity correction is applied because the analysis is a single comparison (A0 vs A1).",
      "measured", E("rat_single_comp", "n10_wilcoxon"), "author_stated", "VERIFIED", rationale="design_choice",
      quote="Not applicable: single comparison (A0 vs A1). No comparison family.", quote_src="project/data/results/n10_cost_expanded_20260726_93f9058.json bh_correction")
claim("C029", "MiniLM is required for the reported routing numbers because the lexical-hash fallback is a degraded offline mode and not the evaluation baseline.",
      "measured", E("rd_rat_embedder", "cm_obs_lexical", "cm_obs_minilm"), "author_stated", "NEEDS_REVIEW", rationale="design_choice",
      quote="a degraded offline mode, **not** the evaluation baseline", quote_src="project/README.md Installation")
claim("C030", "The originally stored effect size (r = 0.688 for the headline, labelled rank-biserial) and z (4.8653) were computed incorrectly and are superseded by r = 0.9413 and z = 5.6786; W, p, the percentage reduction, the CI and per-seed spread did not change.",
      "derived", E("n10_r_stored", "n10_z_stored", "n10_r_corr", "n10_z_corr", "esc_unchanged", "n10_wilcoxon"), "author_stated", "VERIFIED",
      quote="That value was neither a rank-biserial correlation nor a correctly computed Rosenthal r", quote_src="project/data/results/CORRECTIONS.md",
      notes="Intended for a reproducibility/statistics note; keeps both values visible and marks the stale one, as the authors do.")

json.dump({"project_root": "project", "generated_at": NOW, "generated_by": GEN,
           "note": "Candidates only. Claim ids are proposed as C### so checkpoints can block them; the AUTHOR promotes them into claim_evidence_map.json. Blocked candidates must stay out of the paper until a named person answers the checkpoint.",
           "candidates": CL}, open(".rcs/claims/claim_candidates.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

M = []


def miss(kind, desc, refs, blocks=None, severity="major"):
    m = {"id": "M%03d" % (len(M) + 1), "kind": kind, "description": desc, "referenced_in": refs, "severity": severity}
    if blocks:
        m["blocks_claims"] = blocks
    M.append(m)


miss("missing_result", "transactive_seeds_20260621_b4b1094.json (the 11-query, N=5 centerpiece; README headline -23.84%, A1-A2 +39.14) is referenced by README, REPRODUCIBILITY and the archived report but is not in the package.", ["project/README.md", "project/REPRODUCIBILITY.md"], ["C020", "C021", "C023"])
miss("missing_result", "Cost artifacts transactive_cost_expanded_20260724_a274137, _20260725_93f9058, _20260805_437bb6b and n50_supplementary_20260724_a274137 are absent. Only their corrected Wilcoxon statistics survive (effect_size_correction json); the percentage token reductions and CIs for the qwen3-30b-a3b (N=5) and qwen-2.5-72b (N=1) second-answerer runs are recorded nowhere.", ["project/data/results/CORRECTIONS.md"])
miss("missing_result", "E2 stationary, drift (reviewer_fix), refutation and the MiniLM new-topic artifacts (20260624), the E7 cross-model artifacts, the E5 keyed sweep, eval_ladder_20260621 and the token audit are absent; the README rows citing them cannot be verified.", ["project/README.md"], ["C016", "C017", "C018", "C019"])
miss("missing_result", "REPRODUCIBILITY.md rows for held-out tau (tau_heldout 0.333), sensitivity sweep, E6 natural asymmetry (OCI 0.9943), four-system_v1 (22/24 abstention) and E7 bge-m3 have no artifacts in the package.", ["project/REPRODUCIBILITY.md"])
miss("missing_result", "results/{no_memory,rag,asmos,system_d}.json (named by summary.md as the source of the four-system numbers) and per-question outputs are absent; metric definitions for EM (identical to containment in all rows; system D token-F1 0.4329 below its EM 0.625) cannot be checked.", ["project/results/summary.md"], ["C013"])
miss("missing_variance", "Four-system results are a single run of 24 questions with no seeds; statistics.md gives Wilcoxon W but no p-values and W = -94 has an undefined sign convention. 'significant' is not licensed for any four-system difference.", ["project/results/statistics.md"], ["C014"])
miss("missing_variance", "e2_cross_model_summary_20260630_045130.json is a single run with no seeds, spread or query count (answerability values are multiples of 1/11).", ["project/data/results/e2_cross_model_summary_20260630_045130.json"], ["C012"])
miss("missing_result", "No paired test or per-seed A1-A2 gap exists for the n=50/N=10 corpus (only the pooled arm means); seeds 11-55 per-seed aggregates (accuracy, answerability, route@1) are not in the N=10 file.", ["project/data/results/n10_cost_expanded_20260726_93f9058.json"], ["C005", "C007"])
miss("missing_result", "No paired significance test of answer accuracy (A1 vs A0) at n=50 exists; the accuracy grading method for the transactive corpus is not stated in the package.", ["project/data/results/n10_cost_expanded_20260726_93f9058.json"], ["C007", "C023"])
miss("missing_result", "labels_consumed = 10 for ASMOS in both E2 new-topic artifacts contradicts README 'zero added labels'; the definition of labels_consumed and of 'added labels' is not in the package.", ["project/README.md", "project/data/results/e2_new_topic_20260703_182558.json"], ["C022"])
miss("missing_result", "Manuscript, claim ledger (docs/paper/claim_ledger_v2.md, evidence_ledger.md), docs/effect_size_audit.md, docs/w6_fix_plan_v2.md and docs/n50_cost_expansion_report.md are absent. CORRECTIONS.md says the corrected values have not been propagated to them.", ["project/data/results/CORRECTIONS.md"])
miss("figure_without_source", "Figures 1-4 (docs/paper/ASMOS/figures/image*.png; scripts fig1_e2_adaptation.py ... fig4_e5_flat_surface.py) are referenced but neither images nor source data are in the package; any figure must be drawn only from the recorded JSON/CSV data or blocked.", ["project/REPRODUCIBILITY.md"])
miss("missing_evidence", "The corpus, query set (five classes Q1-Q5), topic list, agent partition and the code (src/, scripts/, tests/) are not in the package; dataset description and baseline configuration (classifier hyperparameters, tau_classifier 0.5 choice, RAG top-k, MemGPT reimplementation) cannot be documented beyond what the result files record.", ["project/README.md"])
miss("conflict", "pytest counts differ between README (342 passed, 2 skipped) and REPRODUCIBILITY.md (412 passed, 7 skipped); no test log or CI artifact is present. Left unreconciled; no claim cites it.", ["project/README.md", "project/REPRODUCIBILITY.md"], severity="minor")
miss("missing_evidence", "No bibliography or source registry exists. Related work (RAG, MemGPT, referral networks, truth discovery, Wilcoxon/Kerby method references) appears only as names in the archived report or CORRECTIONS.md and cannot be cited without verification.", ["project/ASMOS_technical_report.md", "project/data/results/CORRECTIONS.md"])
miss("missing_evidence", "The centerpiece embedder (lexical-hash vs MiniLM) is stated as unconfirmed by the authors; the LLM-token recount under a confirmed MiniLM embedder is pending a valid API key.", ["project/README.md"], severity="minor")
miss("unresolved_marker", "Archived report carries unresolved [VERIFY] items (Single-ASMOS 16.7% with no artifact; Multi-ASMOS QA pending) and a patent assessment (prior-art scan from training knowledge, no database access). None was used.", ["project/ASMOS_technical_report.md"], severity="minor")

json.dump({"project_root": "project", "generated_at": NOW, "generated_by": GEN, "items": M},
          open(".rcs/evidence/missing_evidence.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("claims", len(CL), "blocked", sum(1 for c in CL if c["status"] == "BLOCKED"), "missing", len(M))
