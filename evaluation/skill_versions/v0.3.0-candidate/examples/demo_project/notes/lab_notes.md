# Lab notes (SYNTHETIC TEACHING EXAMPLE)

## Hypothesis
If the error under level shift comes from stale normalization stats, then normalizing each
window with its own recent stats (RWN) should fix most of it, and shouldn't hurt when there's
no shift. Keep model size fixed so capacity can't explain the difference.

## Early run (before fixing the test-split bug)
baseline at shift 0.6 gave MAE ≈ 0.66. Re-ran after the split fix → see results/summary.csv.

## Observations
- RWN seems to basically fix level shift?? At 0.6 it's way better.
- At 0.8 both are bad. RWN not really better, the std is bigger too.
- Froze the stats after the first window (rwn_fixed): gets part of the way there.

## Decisions
- window = 48 because it worked in a quick try. Didn't sweep it.

## Limitations (for the paper)
- only synthetic data (synthload), one small MLP
- only level shifts, no variance/seasonality shifts

## TODO
- run on a real load dataset  ← not done
- try a bigger model
