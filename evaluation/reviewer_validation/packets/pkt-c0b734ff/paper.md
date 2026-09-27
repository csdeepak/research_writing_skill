# Experiments with Normalization in Forecasting

## Abstract

Normalization is a standard step in forecasting pipelines. We study several normalization variants on a synthetic hourly load series and report mean absolute error (MAE) under different conditions, including level shifts and an ablation.

## 1 Introduction

Forecasting is widely used in energy systems [CITATION NEEDED: forecasting use in energy systems]. Inputs are normalized before training, most often with the mean and standard deviation of the training data [CITATION NEEDED: standard normalization practice]. Many normalization variants exist [CITATION NEEDED: survey of normalization variants]. Deployed series can change their level after training [CITATION NEEDED: prevalence of level shifts in deployed load forecasting].

In this paper we describe our setup, then our results, and then discuss them.

## 2 Method and experimental setup

We generated SynthLoad, a synthetic hourly series with daily and weekly cycles plus Gaussian noise, and added level shifts of s in {0.2, 0.4, 0.6, 0.8} training standard deviations. We compared three normalizations: training statistics (baseline); rolling-window normalization (RWN), which uses the statistics of the most recent 48 steps; and RWN-fixed, which freezes them after the first 48 post-shift steps. All use the same multilayer perceptron with 64 hidden units, trained with the same budget, over 5 seeds.

## 3 Results

Without shift, RWN and the baseline were indistinguishable (0.409 ± 0.007 and 0.412 ± 0.006), so adapting the normalization cost no measurable accuracy.

Under shift, the baseline's error grew with shift magnitude while RWN's stayed close to its unshifted level (Figure 1). Across s = 0.2–0.6, RWN reduced MAE by 11–29%, and seed spread was small next to these differences.

Figure 1. RWN's error stays near its unshifted level for shifts up to 0.6, while the baseline's error rises steadily. Mean MAE over 5 seeds; bars show one standard deviation.

At s = 0.8, RWN reached 0.712 ± 0.021 against 0.731 ± 0.015, so we cannot claim a benefit there. Freezing the statistics gave 0.518 at s = 0.6, recovering about two thirds of RWN's gain.

## 4 Discussion

The model was identical across conditions, so these results suggest that stale normalization statistics, rather than model capacity, account for much of the shift-induced error in this setting. Capacity was held constant rather than varied. Data were synthetic, the window was untuned, and only level shifts were studied.

Looking back, what this work contributes is a capacity-controlled answer to a question we had not stated: whether error under level shift comes from normalization or from capacity. Per-window normalization removes most of it for moderate shifts at no unshifted cost, fails at the largest shift, and depends on continued adaptation for about a third of its gain.

## 5 Conclusion

We reported several normalization experiments on synthetic data. Future work could consider real data.
