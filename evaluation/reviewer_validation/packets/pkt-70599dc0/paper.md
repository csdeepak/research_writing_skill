# Rolling-Window Normalization for Forecasting Under Level Shift

## Abstract

Forecasting models are usually normalized with statistics computed on their training data, so a shift in the level of a series after deployment mis-scales every input. We asked whether normalizing each input window with its own recent statistics, which we call rolling-window normalization (RWN), removes that error without costing accuracy when no shift occurs. On a synthetic hourly load series with controlled level shifts, and with the model held fixed, RWN matched the baseline without shift and reduced mean absolute error (MAE) by 11–29% for shifts up to 0.6 training standard deviations. It gave no clear benefit at the largest shift tested. An ablation attributes about a third of the gain to continued adaptation of the statistics. These results suggest that, in this setting, stale normalization statistics rather than model capacity account for much of the shift-induced error. Whether this holds on real data and larger models is untested.

## 1 Introduction

Forecasters deployed on streams such as electricity demand meet level shifts: after training, the series settles around a new typical value [CITATION NEEDED: prevalence of level shifts in deployed load forecasting]. Most pipelines normalize inputs with the mean and standard deviation of the training data [CITATION NEEDED: standard normalization practice], so after a level shift every input the model sees is mis-scaled.

Two explanations for the resulting error compete. The error could come from the fixed normalization statistics, or from a model too small to represent the new regime. In the evaluations we examined, normalization and model size were changed together, so their effects cannot be separated [CITATION NEEDED: literature search not yet run].

This paper separates them by holding the model fixed and changing only the normalization. We ask two questions. RQ1: does normalizing each window with its own recent statistics reduce error under level shift without harming accuracy when there is no shift? RQ2: how much of any gain depends on continuing to adapt those statistics, rather than re-estimating them once after the shift?

Our contributions are:

1. A capacity-controlled comparison showing that RWN reduced MAE by 11–29% under level shifts up to 0.6, at no cost without shift.
2. A boundary: at the largest shift tested, RWN gave no clear benefit.
3. An ablation attributing about a third of the gain to continued adaptation.

Section 2 describes the setup, Section 3 answers each question, and Section 4 discusses what the answers mean and where they stop.

## 2 Method and experimental setup

We generated SynthLoad, a synthetic hourly series with daily and weekly cycles plus Gaussian noise. After a training year, we added a level shift of magnitude s, measured in training standard deviations, for s in {0.2, 0.4, 0.6, 0.8}, and also kept an unshifted test period.

We compared three normalizations. The baseline uses the training mean and standard deviation. RWN normalizes each input window with the mean and standard deviation of its most recent 48 steps; we chose 48 in a quick trial and did not tune it [ASK AUTHOR: any rationale for window length 48 beyond the trial?]. RWN-fixed, our ablation, estimates the statistics once from the first 48 steps after the shift and then freezes them, so it re-estimates but does not keep adapting.

All three use the same multilayer perceptron with 64 hidden units, 168 hours of history and a 24-hour horizon, trained with the same budget. Holding this model fixed is what lets differences be attributed to normalization. Each configuration ran with 5 seeds, and we report the mean and standard deviation of MAE on the test period.

## 3 Results

### 3.1 RQ1: accuracy with and without level shift

Without shift, RWN and the baseline were indistinguishable, with MAE of 0.409 ± 0.007 and 0.412 ± 0.006. Adapting the normalization therefore cost no measurable accuracy here, which answers the second half of RQ1.

Under shift, the baseline's error grew with shift magnitude while RWN's stayed close to its unshifted level (Figure 1). At s = 0.6, RWN reduced MAE from 0.641 to 0.452, and across s = 0.2–0.6 the reduction was 11–29%. Seed spread was at most 0.012, small next to these differences, so the ordering held across seeds.

Figure 1. RWN's error stays near its unshifted level for shifts up to 0.6, while the baseline's error rises steadily. Mean MAE over 5 seeds on the test period; bars show one standard deviation; s is in training standard deviations.

The largest shift is the exception. At s = 0.8, RWN reached 0.712 ± 0.021 against the baseline's 0.731 ± 0.015, a gap of about one standard deviation, so we cannot claim a benefit there. RQ1 is answered yes for moderate shifts only.

### 3.2 RQ2: where the gain comes from

Freezing the statistics after one post-shift window gave MAE 0.518 at s = 0.6, between the baseline and RWN. Re-estimating once thus recovers about two thirds of RWN's gain; the remaining third depends on continuing to adapt.

## 4 Discussion

Both answers are bounded. For RQ1, rolling-window normalization reduced error under moderate level shifts at no unshifted cost, but not at the largest shift. For RQ2, most of the gain came from re-estimating the statistics after the shift at all, and about a third from continuing to adapt them.

Because the model was identical across conditions, these results suggest that stale normalization statistics, rather than model capacity, account for much of the baseline's shift-induced error in this setting. This is an interpretation: capacity was held constant, not varied, so the capacity explanation was not tested directly.

Three further limits bound these conclusions. All data came from one synthetic generator, so transfer to real load series is untested. The window length was not tuned, so the reported gains describe one untuned setting. Only level shifts were studied, so we make no claim about shifts in variance or seasonality.

## 5 Conclusion

In a capacity-controlled synthetic setting, the extra error that follows a level shift appears to stem mostly from stale normalization statistics. Re-estimating them per window removed most of that error for moderate shifts without harming unshifted accuracy. The benefit vanished at the largest shift. The open question is whether the same holds on real load data and larger models.
