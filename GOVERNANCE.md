# Governance

RCE is maintained by its author, **C S Deepak** (@csdeepak), who is currently the only maintainer. Maintainers are
added by invitation after sustained, high-quality contributions.

## Decisions
| Change | Requires |
|---|---|
| Documentation, examples, adapters, bug fixes that do not change a validation outcome | one maintainer review |
| Validation rules, claim policies, evidence hierarchy, review protocol, benchmark methodology, self-improvement rules | proposal → discussion → tests (new failing test + full failure-case replay) → evaluation → maintainer decision → changelog |
| Releases (tags, packages) | maintainer decision; release checklist in `ROADMAP.md` |

A **proposal** for a scientific-policy change is a record in `skill/versions/proposals/`
(`skill/schemas/skill_change.schema.json`). It states the observed failure, the evidence, the root cause, the change,
the expected improvement and the possible regressions, and a gate decided by evidence. A proposal's gate never
promotes it by itself: a maintainer decides, and the decision is logged (see `evaluation/logs/DECISIONS.md` D-22 for a
rejection and D-32 for a promotion).

## The rule that does not change
RCE is never allowed to become an autonomous system that rewrites its own scientific standards. Model-generated rule
changes are proposals like any other, and they go through the same gate and human decision.
