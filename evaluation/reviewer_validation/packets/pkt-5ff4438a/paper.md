# Rolling-Window Normalization for Forecasting Under Level Shift

## Abstract

Forecasting models are usually normalized with training statistics, so a level shift after deployment mis-scales every input. We ask whether rolling-window normalization (RWN) removes that error without costing unshifted accuracy. On a synthetic hourly series, RWN matched the baseline without shift and reduced mean absolute error (MAE) by 11–29% for shifts up to 0.6, with no clear benefit at 0.8.

## 1 Introduction

Level shifts are the most common failure mode of deployed forecasters [R1]. Normalization with training statistics is used in essentially all forecasting systems [R2, R3, R4, R5, R6]. Prior work has shown that per-window normalization fixes distribution shift in general [R2].

In the evaluations we examined, normalization and model size were changed together [R3]. We therefore ask, RQ1: does per-window normalization reduce error under level shift without harming unshifted accuracy? RQ2: how much of the gain depends on continued adaptation?

Our contributions are a capacity-controlled comparison, a boundary at the largest shift, and an ablation attributing about a third of the gain to continued adaptation.

## 2 Method and experimental setup

We generated SynthLoad, a synthetic hourly series, following the protocol of [R4], and added level shifts of s in {0.2, 0.4, 0.6, 0.8} training standard deviations. The baseline uses training statistics; RWN uses the statistics of the most recent 48 steps; RWN-fixed freezes them after the first 48 post-shift steps. All use the same multilayer perceptron with 5 seeds.

## 3 Results

Without shift, RWN and the baseline were indistinguishable (0.409 ± 0.007 and 0.412 ± 0.006). Under shift, RWN reduced MAE by 11–29% across s = 0.2–0.6 (Figure 1), consistent with [R5]. At s = 0.8 we cannot claim a benefit. Freezing the statistics recovers about two thirds of the gain.

Figure 1. RWN's error stays near its unshifted level for shifts up to 0.6, while the baseline's error rises steadily.

## 4 Discussion

Because the model was fixed, the results suggest that stale statistics, rather than capacity, account for much of the error here, as also argued by [R6]. Limitations: synthetic data, fixed capacity, untuned window, level shifts only.

## References

[R1]–[R6] Reference list omitted in this manuscript version.
