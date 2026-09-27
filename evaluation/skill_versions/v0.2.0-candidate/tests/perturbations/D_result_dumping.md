<!-- SYNTHETIC TEST ITEM: variant D (result dumping). Same science as A; interpretation removed from Results/Discussion. -->
# Rolling-Window Normalization for Forecasting Under Level Shift

## Abstract

We evaluate rolling-window normalization (RWN) against training-statistics normalization on a synthetic hourly load series with level shifts. We report mean absolute error (MAE) for shifts of 0.0, 0.2, 0.4, 0.6 and 0.8 training standard deviations, and an ablation with frozen statistics (RWN-fixed) {C001, C002, C003, C004}.

## 1 Introduction

Forecasters deployed on streams such as electricity demand meet level shifts [CITATION NEEDED: prevalence of level shifts in deployed load forecasting]. Most pipelines normalize inputs with the mean and standard deviation of the training data [CITATION NEEDED: standard normalization practice]. The error after a shift could come from the normalization or from model capacity [CITATION NEEDED: literature search not yet run].

We ask two questions. RQ1: does RWN reduce error under level shift without harming unshifted accuracy? RQ2: how much of the gain depends on continued adaptation? We hold the model fixed to separate normalization from capacity.

## 2 Method and experimental setup

We generated SynthLoad, a synthetic hourly series with daily and weekly cycles plus Gaussian noise, and added level shifts of s in {0.2, 0.4, 0.6, 0.8} training standard deviations. The baseline uses training statistics. RWN uses the statistics of the most recent 48 steps. RWN-fixed freezes statistics after the first 48 post-shift steps. All use the same multilayer perceptron, trained with the same budget, with 5 seeds.

## 3 Results

Table 1 lists all results.

| Method | s=0.0 | s=0.2 | s=0.4 | s=0.6 | s=0.8 |
|---|---|---|---|---|---|
| Baseline | 0.412 ± 0.006 | 0.471 ± 0.008 | 0.553 ± 0.010 | 0.641 ± 0.012 | 0.731 ± 0.015 |
| RWN | 0.409 ± 0.007 | 0.421 ± 0.007 | 0.433 ± 0.008 | 0.452 ± 0.009 | 0.712 ± 0.021 |
| RWN-fixed | – | – | – | 0.518 ± 0.011 | – |

Table 1. MAE results.

The baseline obtained an MAE of 0.412 without shift and RWN obtained 0.409 {C001}. At s = 0.2 the baseline obtained 0.471 and RWN 0.421 {C002}. At s = 0.4 the baseline obtained 0.553 and RWN 0.433 {C002}. At s = 0.6 the baseline obtained 0.641, RWN 0.452 and RWN-fixed 0.518 {C002, C004}. At s = 0.8 the baseline obtained 0.731 and RWN 0.712 {C003}. Standard deviations ranged from 0.006 to 0.021 {C002}.

Figure 1. MAE versus shift magnitude for the baseline and RWN.

## 4 Discussion

RWN is a simple change to the normalization step and can be added to existing pipelines. The experiments used a synthetic generator {L001} and a single model {L002}. The window length was 48 {L003}. Only level shifts were used {L004}.

## 5 Conclusion

We evaluated RWN under level shifts and reported MAE for three normalizations {C001, C002, C003, C004}. Future work could use real data {C007}.
