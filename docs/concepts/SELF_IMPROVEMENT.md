# Self-improvement: a human-governed regression system

RCE improves from real failures. It does **not** rewrite its own rules.

<p align="center"><img src="../assets/self-improvement.svg" alt="Real failure, reproduction, regression case, proposed rule, cheap tests, full evaluation, human decision, release" width="720"></p>

```text
failure → case → test → proposal → evaluation → HUMAN DECISION → release
```

| Step | What happens | Where |
|---|---|---|
| 1. Detect | A failure is seen in real use: a gate, a blind reviewer, a user report, or a live model run | issues, runs |
| 2. Record | A durable case: what happened, what should have happened, evidence | `cases/failures/FC-####.json` (`skill/schemas/failure_case.schema.json`) |
| 3. Reproduce | A minimal fixture, synthetic where the data are private | `tools/tests/fixtures/` |
| 4. Test | A regression test that fails before the fix | `tools/tests/`; `python tools/validate_cases.py` checks that every case names an existing test |
| 5. Screen cheaply | Tier 1 replays every known failure against the checkers (`tools/replay_fixtures.py`). Tier 2 runs paragraph-level reader screens for writing rules (`tools/micro_recon.py`) | local |
| 6. Evaluate | Tier 3 is a pre-registered live A/B against the current release (decision rule written before the run) | `evaluation/`, `DECISIONS.md` |
| 7. Propose | A proposal record with evidence, root cause, expected improvement and possible regressions | `skill/versions/proposals/*.json` (`skill_change.schema.json`) |
| 8. Decide | **A maintainer decides.** A proposal gate never promotes itself | `DECISIONS.md` |
| 9. Release | Changelog entry, version manifest (`tools/snapshot_version.py`), tag | `skill/changelog.md`, `skill/versions/<v>/` |

Local, opt-in diagnostics (`tools/rce_diagnostics.py record --opt-in`) store counts only. They are never sent anywhere.

## It must never
- silently modify its own rules or evidence standards;
- auto-merge model-generated policy changes;
- delete a failure case because a newer version passes it;
- redefine success from one model run. Single runs are noisy: D-30 measured 0.05–0.19 MMF between two runs of the same
  version.

## History
- v0.2.0 was proposed through this loop and **rejected** by its pre-registered rule (D-22).
- v0.3.0 was released as a process upgrade by an explicit human decision, with its reader-level benefit stated as
  not shown (D-32).
