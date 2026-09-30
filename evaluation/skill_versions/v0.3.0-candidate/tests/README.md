# Tests and benchmark

## 1. Automated tests (run on every change)
```bash
python -m unittest discover -s tools/tests -v
python tools/validate_artifacts.py skill/examples/demo_project/.rcs
python tools/validate_artifacts.py --check-skill
```
They cover lint rules on the perturbation set (must-fire / must-not-fire from `EXPECTED.json`),
validator negative cases (missing locator, unsupported claim, unreported negative result,
ungrounded contribution, unanswered RQ, unbound spine line), packet sanitization (tags,
comments, hidden characters, injection lines, no provenance in the claims list), and the
reconstruction metrics.

## 2. Perturbation benchmark (`perturbations/`)
| File | Manipulation |
|------|--------------|
| `A_clean.md` | reference |
| `B_poor_ordering.md` | question and contributions moved late; setup opens the introduction |
| `C_jargon.md` | undefined acronyms and specialist phrasing |
| `D_result_dumping.md` | numbers without interpretation; undiscussed figure |
| `E_unsupported_interpretation.md` | proof/causal/SOTA language; null result misreported; limitations dropped |
| `F_buried_contribution.md` | no RQ or contribution until late in the discussion |
| `G_citation_misuse.md` | placeholder citations that don't support their sentences |

All variants report the **same synthetic study** (`examples/demo_project`). The ground truth
is in `perturbations/EXPECTED.json`, which is **never** placed in a review packet.

### Reviewer calibration run
For each variant: build a packet (`tools/build_review_packet.py`) with the same `audience.md`
and `objective.md`, run REVIEW_AGENT in hard isolation, and compare its dimension scores with
A's. Sensitivity = the fraction of `reviewer_expected_drop` dimensions scored ≥1 lower than on
A. False-alarm rate = the fraction of blocking defects (≤2) reported on A. Required: sensitivity
≥ 0.90 and false alarms ≤ 0.10, averaged over ≥3 seeds.

### Skill regression run
Give the skill variant X as a "prior draft" together with the demo project. After the revision
loop, the lint's must-fire rules for X must no longer fire. The claim map must be unchanged,
and reconstruction (graded against `demo_project/.rcs/evaluation/gold_story.json`) must be ≥
A's.

## 3. Regression-case registry
Every accepted skill amendment adds a test here or in `tools/tests/`. The link is recorded in
`changelog.md` (`tests_added`).

| ID | Guards against | Where |
|----|----------------|-------|
| T-001 | Result dumping undetected | `tools/tests/test_tools.py::PerturbationLintTests` (variant D) |
| T-002 | Interpretation claims written with proof verbs | variant E → `B4-verb-vs-type` |
| T-003 | Missing RQ or contribution in the introduction | variants B, F → `A1`, `A2` |
| T-004 | Negative result silently dropped | `ValidatorTests.test_negative_result_needs_decision` |
| T-005 | Contribution not grounded in gap + result | `ValidatorTests.test_contribution_must_be_grounded` |
| T-006 | Reviewer-directed injection reaching the reviewer | `PacketTests.test_sanitize` |
| T-007 | Provenance leaking to the reviewer through the claims list | `PacketTests.test_claims_list_has_no_provenance` |
| T-008 | Limitation without `origin` | `test_v020_attribution_gates.py::AttributionValidatorTests.test_T008_*` |
| T-009 | Author-stated limitation dropped from the claim map (S1) | `…::test_T009_*` (T-009b: a `superseded` item is exempt) |
| T-010 | Writer-derived caveat labelled `author_stated` (S1) | `…::test_T010_*` |
| T-011 | Author rationale dropped, or invented as writer-derived (S2) | `…::test_T011_*`, `test_T011b_*` |
| T-012 | Self-certified gate; malformed `state.json` (S3) | `GateTests.test_T012_*`, `test_T012b_*` |
| T-013 | Gate report with errors or stale (G1 warns, G5 blocks) (S3) | `GateTests.test_T013_*` |
| T-014 | G3 lint report stale, without `--rcs`, or with errors (S3) | `GateTests.test_T014_*` |
| T-015 | Over-length draft not flagged; back matter counted (S4) | `LengthGateTests.test_T015_*` |
| T-016 | G5 passed while over the length limit (S4) | `LengthGateTests.test_T016_*` |
| T-017 | Author limitations replaced by writer caveats in the draft (S1) | `AttributionLintTests.test_T017_*` (fixtures `tools/tests/fixtures/H_*.md` must fire, `I_*.md` must be clean; variant E must fire) |
| T-018 | Author rationale missing from, or misplaced in, the draft (S2) | `AttributionLintTests.test_T018_*` |

Fixtures `H_author_limitations_replaced.md` and `I_attributed_limitations.md` are derived from
`A_clean.md` and live in `tools/tests/fixtures/`. They are test inputs, not benchmark items;
promoting them to `perturbations/` needs a human decision.

## 4. Not automated (requires real projects; see `docs/04_EVALUATION_FRAMEWORK.md` §11)
The final quality test (baseline vs skill) and the human-comprehension study.
