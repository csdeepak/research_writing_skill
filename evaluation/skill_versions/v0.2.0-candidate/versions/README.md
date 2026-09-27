# Versions

- `<version>/MANIFEST.json`: SHA-256 of every skill file at release (made by
  `tools/snapshot_version.py`). Together with the git tag `skill-v<version>`, it makes each
  version reproducible.
- `proposals/`: amendment proposals (`*.json` validated against
  `schemas/skill_change.schema.json`, plus `*.md` rationale and patches).

## Release procedure
1. A SKILL_AGENT (or human) proposal lands in `proposals/` with its tests.
2. Apply the patch on a branch. Run `python -m unittest discover -s tools/tests`.
3. Run the release gate (`docs/04_EVALUATION_FRAMEWORK.md` §12) on the held-out set. Record the
   numbers in the proposal's `gate` field.
4. Add the changelog entry `## [x.y.z] — date`, bump `version:` in `SKILL.md`, then run
   `python tools/snapshot_version.py x.y.z`, commit, and `git tag skill-vx.y.z`.
5. Rejected proposals stay in `proposals/` with `gate.status: failed` (negative results are
   kept here too).
