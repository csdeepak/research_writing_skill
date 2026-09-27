# External Validation — Status Record (Phase 0)

Created 2026-09-24 before any experiment. Frozen baseline = git commit `437a385`, tag `skill-v0.1.0`.

## 1. Versions under test
| Component | Version | Identity |
|-----------|---------|----------|
| Skill | 0.1.0 | `skill/versions/0.1.0/MANIFEST.json` (63 files, sha256); `validate_artifacts.py --check-skill` = 0 errors, 0 warnings at start |
| Evaluator (REVIEW_AGENT prompt + rubric + schemas) | 0.1.0 | `skill/agents/review_agent.md`, `skill/evaluation_rubric.md`, `skill/schemas/{diagnostics,reconstruction}.schema.json` |
| Grader (RECON_GRADER) | 0.1.0 | `skill/agents/recon_grader.md`, `tools/score_reconstruction.py` |
| Tools | 0.1.0 | 21/21 unit tests pass at start |

## 2. Existing tests
- `tools/tests/test_tools.py`: 21 tests (lint must/must-not rules on 7 perturbation variants; validator negative cases; packet sanitization; metric arithmetic; schema parsing).
- Perturbation benchmark: 1 synthetic base (`A_clean.md`) × 6 degraded variants (B ordering, C jargon, D result dumping, E overclaiming, F buried contribution, G citation misuse), ground truth in `skill/tests/perturbations/EXPECTED.json`; reconstruction gold = `skill/examples/demo_project/.rcs/evaluation/gold_story.json` (synthetic study, correct by construction).

## 3. Existing thresholds (all PROVISIONAL — design choices, not empirical)
| Threshold | Value | Where defined |
|-----------|-------|---------------|
| Reviewer calibration sensitivity | ≥ 0.90 | docs/04 §8 step 9 |
| Reviewer false-alarm rate on clean variant | ≤ 0.10 | docs/04 §8 step 9 |
| Inner-loop exit: Core RR | ≥ 0.8 | docs/04 §7 |
| Blocking defect | any binding-persona dimension ≤ 2; dims 13/15/16 < 4 | evaluation_rubric §3 |
| Release gate non-inferiority margin (MMF) | 0.03 | docs/04 §12 |
| Final test success | ΔMMF > 0 with CI excl. 0 (or ≥80% projects same direction if underpowered); DR(B) ≤ DR(A) in every project | docs/04 §11 |

## 4. Known assumptions
1. Reconstruction fidelity against a frozen gold account is a valid proxy for reader understanding (to be cross-checked with humans later — not possible in this autonomous run).
2. LLM readers approximate careful expert readers; persona simulation approximates audience diversity.
3. Nugget-level grading by an LLM grader is reliable enough (checked here with a second grader on a subset).
4. External projects' official paper + repository README constitute the "project evidence" (see decision D-03 in `logs/DECISIONS.md`).

## 5. Known limitations at start
- No real-project validation; perturbation set is one domain, one base text.
- Lint is English regex heuristics.
- Skill v0.1.0 had never been executed end-to-end by an agent on a real project before this study.
- Public projects arrive with a polished narrative already (their paper) — this likely *compresses* the measurable difference between conditions (ceiling effect), making the plain-vs-skill test conservative.
- No human readers are available in this autonomous run; the human-comprehension protocol (docs/04 §10) cannot be executed. All reader results here are LLM-reader results.
