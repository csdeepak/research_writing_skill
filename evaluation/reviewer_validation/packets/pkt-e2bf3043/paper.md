# RWN for LS-Robust TSF Under PCM Drift

## Abstract

Z-scored TSF pipelines with TSD-anchored moments are brittle under OOD LS regimes because the IID assumption on first and second moments is violated post-deployment. We ask whether RWN, i.e. per-window moment re-estimation, eliminates the LS-induced MAE inflation without IID-regime degradation. On SynthLoad with PCM LS injection and a capacity-matched MLP, RWN attains IID parity and cuts MAE 11–29% for s ≤ 0.6σ, with no clear gain at 0.8σ. An RWN-F ablation isolates the adaptive-moment term at about one third of the gain. This suggests moment staleness, not representational capacity, dominates LS error in this regime. Transfer to non-synthetic corpora and larger backbones is open.

## 1 Introduction

Deployed TSF systems encounter LS [CITATION NEEDED: prevalence of level shifts in deployed load forecasting]. Canonical pipelines apply TSD-anchored z-scoring [CITATION NEEDED: standard normalization practice], so post-LS inputs are mis-scaled.

Moment staleness and capacity insufficiency are confounded in the evaluations we examined [CITATION NEEDED: literature search not yet run]. We deconfound them via capacity matching. RQ1: does RWN reduce LS-regime MAE with IID parity? RQ2: what fraction of the gain is attributable to the adaptive-moment term versus one-shot re-estimation?

Contributions: (1) capacity-matched evidence of 11–29% MAE reduction under LS up to 0.6σ at IID parity; (2) a boundary at 0.8σ; (3) an RWN-F ablation attributing about one third of the gain to adaptivity.

## 2 Setup

SynthLoad is an hourly generator with diurnal and hebdomadal components plus AWGN. We inject PCM LS of magnitude s ∈ {0.2, 0.4, 0.6, 0.8}σ post-TSD. Baseline: TSD moments. RWN: trailing-48 moments. RWN-F: moments frozen after the first post-LS window. Backbone: MLP (h = 64, L = 168, H = 24), iso-budget, 5 seeds; MAE mean ± sd on the test period.

## 3 Results

IID: RWN 0.409 ± 0.007 vs 0.412 ± 0.006, i.e. parity (RQ1b). LS: baseline MAE grows monotonically in s while RWN remains near IID level (Figure 1). At s = 0.6σ, 0.641 → 0.452; across 0.2–0.6σ the reduction is 11–29%, with sd ≤ 0.012, so ordering is seed-stable.

Figure 1. RWN stays near IID MAE up to 0.6σ, whereas the baseline degrades monotonically. Mean over 5 seeds; ±1 sd.

At 0.8σ, 0.712 ± 0.021 vs 0.731 ± 0.015, about 1 sd, so no gain can be claimed. RWN-F at 0.6σ: 0.518, i.e. about two thirds of the gain is from one-shot re-estimation and about one third from adaptivity.

## 4 Discussion

RQ1 holds for moderate LS only; for RQ2, adaptivity contributes about one third. Under capacity matching, moment staleness rather than capacity plausibly dominates LS error here, though capacity was fixed, not varied. Caveats: synthetic-only, untuned window, LS-only (no variance or seasonality drift).

## 5 Conclusion

Under capacity matching, LS-induced MAE inflation appears to be mostly moment staleness. RWN removes most of it for moderate LS at IID parity, but not at 0.8σ. Non-synthetic validation remains open.
