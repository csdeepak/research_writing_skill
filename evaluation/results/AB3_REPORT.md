# Tier-3 live A/B: skill v0.1.0 vs candidate v0.3.0 (D-29 protocol, D-30 result)

**Verdict under the pre-registered rule: NOT SHOWN.** v0.3.0 is better than v0.1.0 beyond run-to-run noise on
1 of 3 projects (OpenHands) and worse on none. The rule needed 2 of 3.
- The direction is favourable on 2 of 3 projects; the mean effect is +0.066 MMF_src.
- The attribution target (Q11, author-stated limitations) improved on all 3 projects.
- The sample (3 projects × 1 run) cannot distinguish effects of this size from noise.

## Protocol (fixed before any draft; `logs/DECISIONS.md` D-29)
- **Arms:**
  - `skillv010ab3`: the canonical `skill/`.
  - `skillv030ab3`: `evaluation/skill_versions/v0.3.0-candidate`.
- **Writers:**
  - In-session Sonnet subagents on OPENHANDS, MLPERF_TINY and BEIR, running workflow steps 1-17.
  - The task text (TASK v2) was identical for both arms. Its no-human clause defers to the skill's own unattended
    procedure, where one exists.
  - "No images" held for both arms, so figures were not tested.
- **Readers and graders:**
  - One blind Opus review per paper, graded by Sonnet against frozen gold v1.
  - Unsupported-belief intrusions were checked against the frozen source by a blinded verifier (evaluator v0.3
    sensitivity metric, D-24).
- **Rule:**
  - effect = MMF_src(v030) - MMF_src(v010).
  - noise = max(0.05, |MMF_src(v010 ab3) - MMF_src(v010 Phase 9)|).
  - "Better" means effect > noise. The benefit is shown if a project is better on at least 2/3 and worse on none.

## Results

| project | MMF_src v0.1.0 | MMF_src v0.3.0 | effect | noise (v0.1.0 run-to-run) | call |
|---|---|---|---|---|---|
| OPENHANDS | 0.562 | 0.712 | **+0.150** | 0.050 (0.049) | better |
| MLPERF_TINY | 0.600 | 0.575 | -0.025 | 0.187 | no detectable difference |
| BEIR | 0.813 | 0.887 | +0.074 | 0.076 | no detectable difference |

The frozen evaluator-v0.2 MMF gives the same verdict:

| project | effect | noise | call |
|---|---|---|---|
| OPENHANDS | +0.163 | 0.050 | better |
| MLPERF_TINY | -0.025 | 0.162 | no detectable difference |
| BEIR | +0.074 | 0.088 | no detectable difference |

**Secondary measures** (reported, not decisive):

| | OPENHANDS v010 → v030 | MLPERF_TINY v010 → v030 | BEIR v010 → v030 |
|---|---|---|---|
| RR (recall) | 0.625 → 0.787 | 0.713 → 0.675 | 0.863 → 0.950 |
| DR (distortion) | 0 → 0 | 0.025 → 0.025 | 0 → 0 |
| IR_src | 0.125 → 0.150 | 0.175 → 0.150 | 0.100 → 0.125 |
| Q11 author limitations | 0.8 → **0.9** | 0.5 → **0.6** | 0.333 → **1.0** |
| Q2 motivation | 0.5 → 0.75 | 0.375 → **0.125** | 1.0 → 1.0 |
| Q5 design rationale | 0.5 → 1.0 | 0.7 → 0.6 | 1.0 → 1.0 |
| Q7 results | 0.625 → 0.75 | 0.875 → 0.875 | 1.0 → 1.0 |
| Q9 not established | 0.167 → 0.333 | 0.5 → 0.5 | 0.833 → 1.0 |
| words (packet, harness count) | 4,282 → 4,234 | 4,306 → 4,480 | 4,284 → 4,808 (4,403 without table pipes/rules: within limit) |
| numbers not in source | 4 → **0** | 3 → 3 (writer-derived gaps, both arms) | 2 → **0** |

## What this does and does not show
- **Not shown: reader benefit.**
  - Only OpenHands clears its noise bar, and BEIR misses by 0.002. With one run per arm, v0.1.0's own run-to-run
    spread (0.05-0.19 MMF) is as large as the effects being measured.
  - Detecting a +0.07 effect reliably would need several runs per arm per project. At least 3 is recommended, which
    means about 18 writer runs per arm.
- **Not shown: a regression.** No project is worse beyond noise. Distortion is unchanged, and IR_src moves by
  ±0.025, about 1 statement.
- **Consistent with the design:**
  - Q11 (author-stated limitations, the loss that motivated v0.2.0 and v0.3.0) improved on 3/3.
  - v0.2.0 had regressed Q11 on MLPerf; v0.3.0 improves it there.
  - Numbers not traceable to the source fell from 9 to 3. The remaining 3 are the same writer-computed margins
    that v0.1.0 also adds.
- **Watch points:**
  - MLPerf Q2 (motivation) fell from 0.375 to 0.125.
  - Length. The harness counts whitespace tokens, so table pipes and `---` rows count as words; that puts BEIR
    v0.3.0 at 4,808. Counting prose, headings and table text gives 4,403, within the limit. The skill's own lint
    counted only prose (3,751), so the writer could not see its real length. Fixed after the run: v0.3 projects now
    count headings and table text (`length_count`, T-051).
  - BEIR v0.3.0 is still about 120 words longer than v0.1.0 by the same count. Part of its recall gain may come from
    that extra length.
- **Evaluator note for v0.3 (future runs):**
  - Many "unsupported belief" intrusions in this round are the reader's own critical judgements ("the paper does not
    establish that comparisons are fair"). No source states them, so they count as NOT_FOUND.
  - Such meta-judgements should be tagged separately rather than counted as factual intrusions.

## Process notes
- **Interruptions:** 2 usage-limit interruptions and 1 TLS/connection interruption (D-19 pattern). All were resumed
  with no work lost. No certificate settings were changed.
- **Out-of-folder read:** one writer (MLPerf v0.3.0) reported a single read outside its workspace. It was the harness's
  overflow copy of the skill's own `section_rules.md`, which contains no project evidence, and the writer recorded
  it in `open_issues.md`.
- **Isolation audit:** reviewer and grader subagents used 3-4 tool calls each (one chunked Read plus one Write).
- **Reviewer calibration** (separate from the A/B, `reviewer_validation/scores/v030_calibration.json`):
  - v0.3.0's own `review_agent.md` passes its stated bar: dimension sensitivity 0.933 (at least 0.90 required) and
    false alarms 0.05 (at most 0.10 allowed).
  - All 7 outputs are schema-valid and use Q1-Q12 exactly.
  - One miss (result dumping: result and figure_table) is a floor effect: the clean paper already scored those
    dimensions low.

Files:
- Protocol and rule: `harness/prep_ab3.py` and `harness/ab3_decide.py`.
- Scores: `results/comparison/scores/ab3_decision.json`, `ab3_numbers.json` and `intrusion_sensitivity.json`.
- Drafts: `skill_agent/<P>/skillv0{10,30}ab3/`.
