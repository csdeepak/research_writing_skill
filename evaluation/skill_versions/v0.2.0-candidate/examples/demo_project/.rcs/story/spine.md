# Paper Spine (SYNTHETIC TEACHING EXAMPLE)

1. **Problem.** Forecasters normalized with training-set statistics lose accuracy when the level of the series shifts after deployment {C006}.
2. **Gap.** In the evaluations we examined, normalization and model capacity were changed together, so it is unclear which one causes the error [CITATION NEEDED: literature search not yet run] {C005}.
3. **Question.** Does normalizing each input window with its own recent statistics (RWN) reduce error under level shift without harming unshifted accuracy, and how much of any gain needs continued adaptation? {C006}
4. **Approach.** Compare the baseline, RWN, and a frozen-statistics ablation with the same model and training budget, on a synthetic series with controlled level shifts {C002, C004}.
5. **Key finding.** RWN reduced MAE by 11–29% for shifts up to 0.6 training-std units with no unshifted cost, but gave no clear benefit at 0.8 {C001, C002, C003}.
6. **Meaning.** Because capacity was fixed, this suggests stale statistics, not capacity, account for much of the shift-induced error in this setting. About a third of the gain needs continued adaptation {C005, C004}.
7. **Main limit.** One synthetic generator, one small architecture, capacity held rather than varied, and level shifts only {L001, L002, L004}.
