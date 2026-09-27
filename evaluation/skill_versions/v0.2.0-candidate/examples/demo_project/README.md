# Demo project: rolling-window normalization under level shift

> **SYNTHETIC TEACHING EXAMPLE.** This project, its data, and its numbers are invented to
> demonstrate the skill's artifacts. It describes no real experiment. Don't cite it.

Question we were exploring: forecasters normalized with training-set statistics seem to break
when the series level shifts after deployment. Is that the normalization's fault or the
model's?

- `config/experiment.yaml`: model and experiment configuration
- `results/summary.csv`: aggregated MAE (mean/std over seeds) per method × condition
- `notes/lab_notes.md`: running notes (hypotheses, observations, TODOs)
- `.rcs/`: the skill's artifacts for this project (evidence map, claim map, story graph,
  spine, gold story)
