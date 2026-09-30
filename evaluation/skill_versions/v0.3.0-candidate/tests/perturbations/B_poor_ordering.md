<!-- SYNTHETIC TEST ITEM: variant B (poor information ordering). Same science as A. -->
# Rolling-Window Normalization for Forecasting Under Level Shift

## Abstract

We use a multilayer perceptron with 64 hidden units, 168 hours of history and a 24-hour horizon, trained on a synthetic hourly series with daily and weekly cycles. We compare three normalizations over 5 seeds each. Rolling-window normalization (RWN) matched the baseline without shift {C001} and reduced mean absolute error (MAE) by 11–29% for shifts up to 0.6 {C002}. It gave no clear benefit at 0.8 {C003}. RWN-fixed reached 0.518 {C004}. Stale statistics rather than capacity may account for much of the error {C005}.

## 1 Introduction

We generated SynthLoad, a synthetic hourly series with daily and weekly cycles plus Gaussian noise. After a training year we added a level shift of magnitude s, measured in training standard deviations, for s in {0.2, 0.4, 0.6, 0.8}. The baseline uses the training mean and standard deviation. RWN normalizes each input window with the mean and standard deviation of its most recent 48 steps. RWN-fixed estimates the statistics once from the first 48 steps after the shift and then freezes them.

Forecasters deployed on streams such as electricity demand meet level shifts [CITATION NEEDED: prevalence of level shifts in deployed load forecasting]. Most pipelines normalize inputs with training statistics [CITATION NEEDED: standard normalization practice].

## 2 Results

RWN-fixed gave MAE 0.518 at s = 0.6, between the baseline and RWN {C004}. Re-estimating once thus recovers about two thirds of RWN's gain {C004}.

At s = 0.8, RWN reached 0.712 ± 0.021 against 0.731 ± 0.015, a gap of about one standard deviation {C003}.

Figure 1. RWN's error stays near its unshifted level for shifts up to 0.6, while the baseline's error rises steadily. Mean MAE over 5 seeds; bars show one standard deviation.

Without shift, RWN and the baseline were indistinguishable, with MAE of 0.409 ± 0.007 and 0.412 ± 0.006 {C001}. Under shift, at s = 0.6, RWN reduced MAE from 0.641 to 0.452, and across s = 0.2–0.6 the reduction was 11–29% {C002}, as Figure 1 shows.

## 3 Method

All three use the same multilayer perceptron, trained with the same budget. Each configuration ran with 5 seeds, and we report the mean and standard deviation of MAE on the test period. We chose the window of 48 in a quick trial and did not tune it [ASK AUTHOR: any rationale for window length 48 beyond the trial?].

## 4 Discussion

Because the model was identical across conditions, these results suggest that stale normalization statistics, rather than model capacity, account for much of the baseline's shift-induced error in this setting {C005}. Capacity was held constant, not varied {L002}. All data came from one synthetic generator {L001}. The window length was not tuned {L003}. Only level shifts were studied {L004}.

Two explanations for shift error compete: fixed normalization statistics, or a model too small for the new regime. In the evaluations we examined, the two were changed together [CITATION NEEDED: literature search not yet run]. We therefore asked, RQ1: does normalizing each window with its own recent statistics reduce error under level shift without harming unshifted accuracy? RQ2: how much of the gain depends on continued adaptation?

## 5 Conclusion

Our contributions are a capacity-controlled comparison showing an 11–29% MAE reduction under moderate level shifts at no unshifted cost {C001, C002}, a boundary at the largest shift {C003}, and an ablation attributing about a third of the gain to continued adaptation {C004}.
