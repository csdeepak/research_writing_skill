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

T-019 to T-071 are listed in the docstrings of the `tools/tests/test_v0*.py` files that hold them.

**Unified workflow (proposal `20261102-unified-workflow`).** The network is mocked in every test, so CI stays offline
and needs no keys.

| ID | Guards against | Where |
|----|----------------|-------|
| T-072 | A title read as a different work because of case, punctuation or a `RETRACTED:` prefix | `test_v050_literature.py::TitleTests` |
| T-073 | An outage, a refusal by data policy or a rate limit read as "not found"; a skip replayed offline from cache; arXiv called too fast; a key leaking into a URL, the cache or the log | `…::ClientTests` |
| T-074 | A wrong verdict: a fabricated or wrong-paper ID passing, a Crossref miss treated as proof, an outage treated as `unresolvable`, near-identical titles decided without a person | `…::VerdictTests` |
| T-075 | Retraction status taken from a title match, from the oldest event, or from one resolver when they disagree | `…::RetractionTests` |
| T-076 | Flags missing, too noisy (a one-year gap) or overwriting what a person set | `…::FlagTests` |
| T-077 | Metadata repaired from memory or across a conflict; a fabricated candidate registered; a new source citable before anyone read it | `…::RegistryTests` |
| T-078 | GL passing a fabricated, unverified, unquoted, retracted or unlisted source, or an unscoped gap; GL using the network | `…::GateTests` |
| T-079 | Intake changing the user's library or failing quietly; a search sent before its terms were reviewed; fewer than two indexes per query unreported; injected text followed | `…::IntakeTests`, `…::SearchTests` |
| T-080 | The GI blocking matrix applied wrongly at either stage | `test_v050_integrity.py::BlockingTests` |
| T-081 | A VERIFIER `CLEAR` overruling a tool finding, standing without evidence, or judging another draft | `…::VerifierLimitTests` |
| T-082 | An alignment sample that cannot be replayed, misses a high-impact sentence, or does not widen after a failed sentinel | `…::AlignmentTests` |
| T-083 | A no-experiments declaration used to hide reported experiments | `…::NoExperimentTests` |
| T-084 | An integrity block lifted without a named person, a reason, an `open_issues.md` entry, or within the round cap | `…::DecisionTests` |
| T-085 | A final paper that differs from the checked draft; a pre-stage suspicion left unresolved, or a pre-stage block settled by a later CLEAR alone; a stale retraction check | `…::FinalStageTests` |
| T-086 | The AUTHOR writing its own integrity verdict | `…::RoleTests` |
| T-087 | The per-mode evidence missing a planted defect (M1–M7) | `…::EvidenceTests` |
| T-088 | A reference field invented, unescaped or of the wrong type; uncited works in the bibliography | `test_v050_finalize.py::BibTests` |
| T-089 | A citation mapped to the wrong key or to none, silently; a review packet with no reference list, or one sorted by first name | `…::MappingTests`, `…::PacketReferenceTests` |
| T-090 | A missing tool replaced silently, PDF through HTML, a default style chosen silently, content lost in conversion | `…::FormatTests` |
| T-091 | A disclosure that states a policy from memory, invents facts, or claims a check that did not run | `…::DisclosureTests` |
| T-092 | The venue-profile reader misreading the templates | `…::YamlTests` |
| T-093 | GL or GI self-certified, failed or stale but counted as passed; G5 without a final GI; legacy projects asked for GI | `…::WiringTests` |
| T-094 | A schema change breaking v0.4 registries; a new schema accepting bad values; a `$ref` that validates nothing | `test_v050_roles.py::SchemaTests` |
| T-095 | An invalid VERIFIER report reaching GI; a widened check with nothing to widen to | `…::VerifierReportTests` |
| T-096 | A panel seat seeing the paper before committing; a commitment hash or packet id written by the model | `…::PanelRunTests` |
| T-097 | A synthesizer stating a decision the findings do not give, or citing a finding no seat made | `…::PanelRunTests` |
| T-098 | A panel round with a missing seat, a rewritten commitment, an unjudged criterion, an invented finding, an unquoted downgrade | `…::PanelCheckTests` |
| T-099 | The decision rule or the rebuttal rule drifting | `…::RuleTests` |
| T-100 | G4 passing with a standing panel finding, a declined devil's-advocate finding without a sufficient rebuttal, an unanswered Reject, no panel in paper mode, or a third round; a round-2 re-review failed for having no reader review, or passed with a blocking item still unaddressed | `…::G4PanelTests` |
| T-101 | A re-review with new cards or an unchecked roadmap item | `…::VerificationRoundTests` |
| T-102 | Rebuttals scored out of order, or a concession run wearing findings away | `…::RebutTests` |
| T-103 | A VERIFIER report whose hash, round or isolation comes from the model; a VERIFIER run that is not recorded | `…::VerifyCommandTests` |
| T-104 | A prompt, adapter, template or schema the docs name that does not exist | `…::FilesTests` |
| T-105 | A planted fabricated DOI, wrong-paper DOI, retracted source, hallucinated result or method without basis passing the citation and integrity tools; a false alarm on the clean control | `test_v050_benchmark.py::IntegrityBenchmarkTests` |
| T-106 | The integrity benchmark changing the reviewer calibration variants | `…::IntegrityBenchmarkTests` |

Fixtures `H_author_limitations_replaced.md` and `I_attributed_limitations.md` are derived from
`A_clean.md` and live in `tools/tests/fixtures/`. They are test inputs, not benchmark items;
promoting them to `perturbations/` needs a human decision.

## 4. Not automated (requires real projects; see `docs/04_EVALUATION_FRAMEWORK.md` §11)
The final quality test (baseline vs skill) and the human-comprehension study.
