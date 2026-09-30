# AdaptNorm: window re-normalisation under sensor drift (clean control)

## Results

Error is the mean absolute error (MAE) over the evaluation windows.
AdaptNorm reached a mean MAE of 0.80 against 1.00 for StaticNorm {C001}.
Its mean error is 20% lower than StaticNorm's {C002}.
The evaluation covers three datasets {C003}.
Re-normalising inputs is a known approach to distribution shift (Rivera et al., 2019).
