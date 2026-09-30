# Evaluation: what has and has not been demonstrated

Every number here comes from a file in `evaluation/`, and the source is named in each row. The protocols and decision
rules are in `evaluation/logs/DECISIONS.md`: D-17 and D-29 were written **before** their runs. Nothing below is a claim
of statistical significance. Most results come from single runs on small numbers of projects.

**Primary reader metric.** *MMF* = recall − distortion − ½·intrusions. A blind LLM reader reconstructs the paper and
is graded against a frozen gold account. *MMF_src* counts an intrusion only if the frozen source does not state it
(evaluator v0.3; D-24).

## Track A: evidence fidelity
| Task | Result | n | Source |
|---|---|---|---|
| Evidence extraction by a cheap vs a strong model (numbers traceable to source) | cheap 0.78 / 0.97 / 0.98 vs strong 1.00 / 1.00 / 1.00 | 3 projects | `evaluation/results/FINAL_EXTERNAL_VALIDATION_REPORT.md` §5 |
| Conflict detection on 13 real evidence maps | 0 false conflict alarms; 1 true unrecorded conflict | 6 Phase 9 drafts + maps | D-25 |

**Limitation:** extraction quality is measured against gold nuggets for public papers only.

## Track B: numerical fidelity
| Task | Result | n | Source |
|---|---|---|---|
| Fabricated-number probe | 35 of 40 caught (the earlier lenient matcher caught 2 of 40) | 40 planted numbers | D-25, FC-0001 |
| Untraceable numbers, tier-3 A/B drafts | v0.1.0: 9 → v0.3.0: 3 (the remaining 3 are writer-derived margins in both arms) | 3 projects × 2 arms | `evaluation/results/AB3_REPORT.md` |

**Known gaps:** denominator direction and missing sample sizes (see `docs/concepts/EVIDENCE_INTEGRITY.md`).

## Track C: claim overreach
- Deterministic license rules (7 types) are tested (T-071, T-064).
- The blind reviewer reports overreach as inference issues (19 blocking items in the end-to-end run).
- No rate of overreach in the wild has been measured.

## Track D: figure fidelity
| Task | Result | Source |
|---|---|---|
| Stage 2 acceptance: figures from real data | PASS on 2 projects: MLPerf Tiny (public; reproducible from `evaluation/stage2_acceptance/`) and one private project (data not published) | `evaluation/stage2_acceptance/ACCEPTANCE.json` |
| Mislabelled axis | missed by all six figure gates, caught by a blind reviewer; now a renderer-independent check (V3_AXIS_ENCODING) | FC-0006, T-050 |

V5 (human usability review) has **not** been performed by a person on any figure.

## Track E: blind reviewer reliability
Planted-defect benchmark (7 synthetic papers). Pass bar: dimension sensitivity ≥ 0.90 and false alarms on the clean
paper ≤ 0.10.

| Reviewer | Sensitivity | False alarms | Seeds | Source |
|---|---|---|---|---|
| Claude Opus, harness prompt (Phase 4) | 0.956 | 0.05 | 2 | FINAL report §2 |
| NVIDIA Nemotron, harness prompt (Phase 4) | 0.933 | 0.00 | 1 | FINAL report §2 |
| Claude Opus, the skill's own `review_agent.md` (v0.3.0) | 0.933 | 0.05 | 1 | D-30 |
| NVIDIA Nemotron-3-Ultra via `rce_roles.py` | 0.945 | 0.00 | 1 | `evaluation/model_agnostic/RESULTS.md` |
| Qwen3.8-27B via `rce_roles.py` | 0.911 | 0.00 | 1 | same |

**Limitations:**
- 7 items and 1–2 seeds; the thresholds are provisional.
- LLM readers were **insensitive to structural defects** (ordering, jargon, buried contribution scored about 1.0).
- The Phase 4/5 CLI reviewer runs had the operator's personal assistant memory in context. The reviewers flagged
  and ignored it (FC-0018), so those runs were not fully isolated.

## Track F: reader comprehension (the question that matters most, and **not established**)
| Comparison | Result | n | Source |
|---|---|---|---|
| v0.1.0 skill vs a plain agent (Phase 5), MMF with an Opus reader | better on **2 of 6** projects, worse on 4 (up to −0.350) | 6 public projects, 1 run each | FINAL report §3 |
| same, MMF_src | mean −0.095; skill better on 2 of 6 | 6 | D-24 |
| v0.2.0 vs v0.1.0 (Phase 9) | not shown better; rejected | 3 projects | D-22, D-24 |
| v0.3.0 vs v0.1.0 (tier-3 A/B, pre-registered D-29) | better beyond noise on **1 of 3** projects, worse on none; mean +0.066 MMF_src; verdict **NOT SHOWN** | 3 projects, 1 run per arm | `evaluation/results/AB3_REPORT.md` |
| run-to-run noise of v0.1.0 | 0.05–0.19 MMF_src | 3 projects | D-30 |
| Human readers | **not run.** The kit exists (`skill/templates/human_study_protocol.md`, `tools/comprehension_kit.py`) | 0 | n/a |

**Reading:** RCE's demonstrated value is process integrity (tracks A–E), not better reader comprehension. Detecting
effects of about 0.07 needs at least 3 writer runs per arm per project, and ideally human readers.

## Track G: cross-model robustness
- Three reviewer families were calibrated (Track E).
- Writers so far: Claude models only (Phase 5/9 and the A/B).
- Evidence agent: cheap vs strong Claude models (Track A).
- A cross-family *writer* comparison has **not** been run.

## Track H: cross-domain robustness
- 6 public ML/IR/speech/vision/agent papers, 1 private systems project, and synthetic fixtures.
- **Not established** for other fields (biomedical, social science, humanities).

## End-to-end process run (private project)
Separate role agents ran the full workflow on the author's unpublished project. Its data are not published; these are
the process results only:
- 0 validator errors and 0 role violations in the provenance ledger (199 entries).
- No agent answered a human checkpoint. All blocked claims stayed out of the paper until a named person answered
  3 of the 5 checkpoints.
- 2 blind-review rounds. Blocking findings went from 8 to 2, and every finding received a disposition. G4 passed on
  the second round.
- G5 fails correctly while author-only gaps remain.
- The run found 10 tool defects that the unit tests had missed (5 during the first pass, 5 while applying human answers and running review round 2); all are fixed and regression-tested, and the substantive ones are failure cases in `cases/`.

Source: `evaluation/logs/DECISIONS.md` D-28, D-31 (process metrics only).

## Reproducibility
- For each run: `evaluation/logs/experiments.jsonl` (model, role, prompt hash, timing), `DECISIONS.md` (protocol,
  decision rule), harness scripts in `evaluation/harness/`.
- Frozen third-party inputs: `evaluation/harness/snapshot_sources.py restore` (pinned arXiv versions and README
  commits, SHA-256).
- Model versions behind hosted endpoints can change without notice, so exact reproduction of model outputs is not
  guaranteed. Tool behaviour is (tests).
