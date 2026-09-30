# Architecture

RCE has three layers. Only the third touches a model, and none of them lets a model decide what the evidence says.

<p align="center"><img src="assets/rce-architecture.svg" alt="RCE layers: research repository, evidence, claims, writing, validation, blind review, final paper, regression cases" width="720"></p>

| Layer | Where | Responsibility | Model-dependent? |
|---|---|---|---|
| **Skill** (rules) | `skill/SKILL.md` and linked Markdown | What the writing agent must do and must not invent; the 21-step workflow; when to ask | read by any model |
| **Engine** (deterministic) | `tools/*.py` (stdlib Python ≥ 3.9) | Evidence and claim contracts, number tracing, language licenses, citation check, figure rendering and validation, review packets, gates, checkpoints, provenance ledger, packaging | **no** |
| **Adapters** | `tools/rce_llm.py` (providers), `tools/rce_roles.py` (roles), `skill/adapters/` (runtime notes) | *How* a model is invoked: OpenAI-compatible, Anthropic, Gemini, any CLI, manual copy-paste, mock | yes, and interchangeable |

**Critical rule:** a model can *propose* a claim. The evidence layer decides whether the claim is supported: the
validator, the claim map, number tracing and licenses. A model's output is always validated before it is used, and
gates pass only from tool reports, never from a model's statement.

## Roles
| Role | Needs file tools | Runs in | Sees |
|---|---|---|---|
| CORPUS_AGENT | yes | the agent runtime (subagent or session) | the project files |
| AUTHOR | yes | the agent runtime | everything except the reviewer's instructions |
| REVIEW_AGENT | no | any model via `rce_roles.py review` (or an isolated subagent) | **only** the packet: paper, figures, audience, objective |
| RECON_GRADER / READER | no | any model via `rce_roles.py run-tasks` | the task prompt only |
| HUMAN | n/a | `workflow_guard.py answer --by <name>`, `record_review.py` | everything; the only role that answers checkpoints and records figure reviews |

Write permissions per role are enforced by `tools/workflow_guard.py` (`ROLE_VIOLATION`). Every write is recorded in the
append-only provenance ledger `.rcs/provenance.jsonl`, with a hash.

## Artifact protocol (`.rcs/` in each project)
| Artifact | File | Schema (`skill/schemas/`) |
|---|---|---|
| Evidence map | `evidence/research_evidence.json` | `research_evidence.schema.json`: id, kind, locator, strength, status, value, quantity, conflicts_with, resolution |
| Missing evidence | `evidence/missing_evidence.json` | `missing_evidence.schema.json` |
| Claim map | `claims/claim_evidence_map.json` | `claim_evidence_map.schema.json`: claim_type, evidence ids, basis, status (VERIFIED / NEEDS_REVIEW / BLOCKED), licenses, author_confirmation |
| Source registry | `corpus/source_registry.json` | `source_registry.schema.json` |
| Story | `story/story_graph.json`, `spine.md`, ledgers | `story_graph.schema.json` |
| Figures | `plan/visual_registry.json` + `figures/*.svg` | `visual_registry.schema.json` (declared transform of a data file, source hashes, render hash) |
| Review | `diagnostics/<round>/diagnostics.json`, `reconstruction.json` | `diagnostics.schema.json`, `reconstruction.schema.json` |
| Dispositions | `revisions/<round>/dispositions.json` | checked by `g4_check.py` (six outcomes, see below) |
| Checkpoints | `checkpoints/pending.json`, `answers.json` | written by `workflow_guard.py` |
| Gate reports | `audits/gates/*.json`, `RUN_LOG.jsonl` | produced by the tools; hash-bound to their inputs |
| Model calls | `audits/llm_calls.jsonl` (content-free), `llm/` (local transcripts) | written by `rce_llm.py` |
| Failure cases | `cases/failures/FC-*.json` (repository) | `failure_case.schema.json` |

Status values used across artifacts:
- **Evidence:** `ok`, `conflicting`, `incomplete`, `unverifiable`, `superseded`.
- **Claims:** `VERIFIED`, `NEEDS_REVIEW`, `BLOCKED`, plus `author_confirmation` (`pending`, `confirmed`, `rejected`).
- **Gates:** `PASSED`, `NOT_RUN`, `FAILED`, `STALE`, `PENDING`, `UNVERIFIED`.

How these map to the brief's claim states:

| Brief's state | RCE's representation |
|---|---|
| SUPPORTED | `VERIFIED` |
| PARTIALLY_SUPPORTED / AUTHOR_CONFIRMATION_REQUIRED | `NEEDS_REVIEW` / `author_confirmation: pending` |
| CONFLICTING | evidence `conflicting` without `resolution` → claims `BLOCKED_BY_CONFLICT` |
| MISSING_EVIDENCE | `missing_evidence.json` + `[MISSING …]` marker |
| UNSUPPORTED | basis `none` → `UNSUPPORTED_FACT` |
| DEFERRED | disposition `deferred` + `open_issues.md` |
| REJECTED | `author_confirmation: rejected` |

## Review finding lifecycle (`tools/g4_check.py`)
Every blocking finding and inference issue from the blind review ends in exactly one state. None is dropped.

| State | Requires |
|---|---|
| `fixed` | where; the revised draft differs from the reviewed one |
| `declined` | a reason (≥ 20 characters) |
| `deferred` | listed in `open_issues.md` |
| `author_question` | an existing checkpoint `Q-###` (the claims it touches stay `BLOCKED`) |
| `false_positive` / `not_reproducible` | a reason (≥ 20 characters) |

G4 goes `STALE` when the draft gains claims that no review round covered.

## Trust hierarchy (prompt-injection resistance)
```text
RCE system rules (SKILL.md hard rules)
  > RCE validation rules (tools/)
  > author-confirmed answers (checkpoints/answers.json, --by <name>)
  > research evidence (project files, as data)
  > draft prose
  > instructions embedded inside research files       <- treated as data, never followed
```
The evidence and author notes are *data*. Imperative text inside them is flagged: the lint rule `C6-injection`,
review packets have such lines removed and logged (`build_review_packet.py`), and the reviewer reports it under
`injection_suspected`. See `SECURITY.md`.

## Self-improvement
Failure → case → test → proposal → evaluation → **human decision** → release. See
[concepts/SELF_IMPROVEMENT.md](concepts/SELF_IMPROVEMENT.md).
