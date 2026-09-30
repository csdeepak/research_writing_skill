# Contributing to RCE

Thank you for helping. RCE's identity is narrow on purpose: **evidence-grounded research communication, claim
traceability, validation, blind review, and failure-driven improvement.** Contributions that strengthen those are
welcome. Features that make it a general "AI research assistant" are out of scope.

Priority order when trade-offs appear: **evidence integrity > claim correctness > traceability > reader
reconstructability > scientific qualification > clarity > style.**

## Ways to contribute
- **Report a failure.** The most valuable contribution. Use the *Evidence integrity / unsupported claim* issue form.
  Reproduce with synthetic data where your project is private; never upload confidential research.
- **Add a failure case.** A confirmed failure becomes `cases/failures/FC-####.json`
  (`skill/schemas/failure_case.schema.json`) plus a regression test or replay fixture that fails before the fix.
- **Close a known gap** (listed in `docs/concepts/EVIDENCE_INTEGRITY.md`), add a model adapter (`tools/rce_llm.py`), or
  improve the docs.

## Development
```bash
python -m unittest discover -s tools/tests -v     # all tests (stdlib only; Python >= 3.9)
python tools/replay_fixtures.py                   # every known failure, replayed against the checkers
python tools/validate_cases.py                    # the failure-case archive
python tools/validate_artifacts.py --check-skill  # skill files, schemas, proposals
python tools/check_repo.py                        # secrets, local paths, broken links, SVGs
python tools/package_skill.py                     # build + validate the skill ZIP
```
Style: follow the surrounding code (stdlib only, type hints, docstrings that state the rule and its failure code).
Keep text files LF (`.gitattributes`).

## Pull requests
Answer the questions in the PR template. **Changes to validation rules, claim policies, the evidence hierarchy, the
review protocol, benchmark methodology or self-improvement rules** additionally need:
1. a new test that fails before the change;
2. the full replay of existing failure cases (`tools/replay_fixtures.py`), all passing;
3. a new failure case when the change was motivated by one;
4. before/after behaviour described in the PR;
5. maintainer review (`GOVERNANCE.md`).

Never regenerate expected outputs or fixtures just to make CI pass. Explain every intentional change to an expected
result. Never delete a failure case because a newer version passes it.

## Evidence standards apply to this repository too
README claims, release notes and benchmark reports follow RCE's own rules. A number needs a source file in the
repository, "significant" needs a test, and a measured difference needs its noise level. Do not strengthen the
statements in `docs/research/EVALUATION.md` without new evidence.

## Licence
By contributing you agree that your contribution is licensed under the Apache License 2.0 (`LICENSE`).
