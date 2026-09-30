# Roadmap

No dates are promised. Order follows RCE's priorities: evidence integrity first.

## v0.4.0: open-source release (current)
- [x] Apache-2.0 licence; community and governance files; security and privacy policies
- [x] Skill ZIP packaging with validation (`tools/package_skill.py`); CI; repository audit
- [x] Failure-case archive (`cases/`); synthetic adversarial example project
- [x] Citation-registry check; configurable language policy; six-state finding lifecycle
- [ ] Verify the ChatGPT installation path against current OpenAI documentation

## v0.5.x: interfaces
- `rce_version` / `schema_version` stamped in every artifact; documented compatibility policy per artifact
- optional installable package (`pip install`) exposing `rce` without polluting module names
- more adapters as people need them, each with a mock test
- close known gaps: sample-size / denominator presence; denominator direction of percentage changes; prose units

## v0.6.x: evaluation
- A/B with ≥ 3 writer runs per arm per project (single runs cannot detect ≈ 0.07 MMF effects; D-30)
- cross-family *writer* comparison (reviewers are already cross-family)
- cross-domain projects beyond ML/IR/speech/vision (biomedical, social science)

## v0.7.x: reader studies
- blinded human reader study using `skill/templates/human_study_protocol.md` and `tools/comprehension_kit.py`
- V5 human figure reviews

## v1.0: only after
stable interfaces · documented limitations · reproducible benchmark suite · robust regression corpus · community
feedback · a clear versioning policy. Being public is not a reason for 1.0.

## Versioning policy (semantic versioning)
| Bump | Meaning |
|---|---|
| **patch** (0.4.x) | fixes, docs, packaging, new failure cases and tests; no artifact or gate becomes stricter for existing projects unless it guards a confirmed integrity failure |
| **minor** (0.x.0) | new rules, gates or artifact fields (additive; old artifacts stay valid or get a documented migration); changes to review or evaluation protocol |
| **major** | breaking changes to `SKILL.md` workflow, schemas, CLI or adapter contracts |

Before 1.0, a minor release may include breaking changes; they are always listed in the changelog.

## Release checklist
1. All tests, replay fixtures, `validate_cases`, `--check-skill` and `check_repo` pass (CI green).
2. `skill/changelog.md` entry; `version:` in `skill/SKILL.md`; `python tools/snapshot_version.py <version>`.
3. `python tools/package_skill.py` builds a valid ZIP.
4. Re-verify the platform installation steps in `docs/guides/INSTALL.md`.
5. Human review of the release notes against `docs/research/EVALUATION.md` (no strengthened claims).
6. Tag `skill-v<version>`; publish a GitHub release with the source, the skill ZIP, the changelog excerpt, the test
   status and the known limitations.
