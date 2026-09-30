## What changed?

## Why? What evidence supports the change?
<!-- link the issue, failure case (cases/failures/FC-####.json), log entry or measurement -->

## Tests
- [ ] new test(s) that fail before this change:
- [ ] `python -m unittest discover -s tools/tests` passes
- [ ] `python tools/replay_fixtures.py` passes (no existing failure case regressed)
- [ ] `python tools/validate_cases.py`, `python tools/check_repo.py` pass

## Integrity impact
- Could this alter evidence-integrity behaviour (a check's level, a license, the evidence hierarchy, the review protocol)? **yes / no**
- If yes: before/after behaviour, and the proposal record in `skill/versions/proposals/` (see `GOVERNANCE.md`)
- Did an existing failure case or expected output change? Why?

## Documentation
- [ ] docs updated (or not needed); no public claim strengthened without new evidence (`docs/research/EVALUATION.md`)
- [ ] no private research data, keys or local paths added
