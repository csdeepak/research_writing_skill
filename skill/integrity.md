# Integrity: the check the author does not run

This is P5 (step 15, gate GI) and step 20 of P7. It runs twice because a revision can introduce what
the first pass cleared.

These failures can read as competent work. A made-up result looks the same on the page as a real
one, and a Methods section that drifted from the code can read better than an honest one. So before
anyone reviews the prose, a role that did not write the paper checks it against the project's own
records. This needs RCE's evidence map: the check is against what happened, not against what sounds
likely.

---

## 1. Who does what

| Who | Does | Never |
|---|---|---|
| `tools/integrity_check.py` | Collects the evidence for each mode, computes the deterministic results, selects the alignment sample, writes the gate report | Decides a semantic question |
| VERIFIER (isolated context) | Reads the bundle, the draft and the source quotes, and judges each mode | Edits the paper. Sees the AUTHOR's reasoning or conversation |
| AUTHOR | Fixes the paper and its artifacts | Rules on its own draft |
| A named person | May record a decision on a block (§6) | Is replaced by an agent |

A run with no separate context runs VERIFIER in a fresh session. If even that is impossible, label
the report `isolation: none`. GI still applies, and the label goes in `open_issues.md`.

---

## 2. The seven failure modes

The seven modes are adapted from the checklist in ARS (S32) and mapped onto RCE artifacts. The
checklist draws on the limits reported for an end-to-end automated research system (S33), which
include incorrect implementations, errors in experimental implementation and inaccurate citations.

| Mode | The failure | What is checked |
|---|---|---|
| **M1** | An implementation bug passes self-review | Result claims whose producing code or run log is absent. Pipeline-correctness claims with no test or log behind them. Values too round or too uniform to be measurements |
| **M2** | Hallucinated citation | GL results. Any draft citation missing from the registry. Claim↔reference alignment (§4) |
| **M3** | Hallucinated result | `tools/verify_numbers.py`. Every result claim has `hard` evidence. Stated seed and run counts match the run records |
| **M4** | Shortcut reliance | Leakage or overlap notes, untuned or unmatched baselines, evaluation on development data, the `matched_evaluation` license |
| **M5** | A bug reframed as an insight | Surprising deltas and flipped negatives, and "surprisingly" or "unexpectedly" in the prose, interpreted without robustness evidence (seeds, ablation, a fresh rerun) |
| **M6** | Methodology fabrication | Method sentences whose claims have no `code` or `project_file` basis. Hyperparameters and preprocessing that the configs do not contain |
| **M7** | Frame-lock | An RQ or spine that changed silently. No alternative explanation considered for the central claim |

**M7 needs a record to check.** Every RQ or spine change is noted in `state.json` under
`story_changes`, as `{what, reason}`. For the central claim, `story/alternatives.md` lists the alternative explanations considered and
what speaks for and against each. The list may be short. It may not be silently empty.

---

## 3. Status and blocking

Each mode gets exactly one status, with the evidence behind it.

| Status | Meaning |
|---|---|
| `CLEAR` | Evidence shows the failure does not apply. Cite that evidence |
| `SUSPECTED` | Something concrete points to the failure. Cite it |
| `INSUFFICIENT_EVIDENCE` | The available records cannot rule it in or out |

`CLEAR` is earned. A mode with nothing to look at is `INSUFFICIENT_EVIDENCE`.

| Status | Effect at `--stage pre` | Effect at `--stage final` |
|---|---|---|
| `CLEAR` | None | None |
| `SUSPECTED`, any mode | **Blocks** | **Blocks** |
| `INSUFFICIENT_EVIDENCE` on M1, M3, M5, M6 | **Blocks** | **Blocks** |
| `INSUFFICIENT_EVIDENCE` on M2, M4, M7 | Warning. Listed in `open_issues.md` | **Blocks** |

**A blocked mode raises `INTEGRITY_SUSPECTED`.**

**Declared no-experiments papers.** When `paper_config.no_experiments` is true and the user
confirmed it at C0, `INSUFFICIENT_EVIDENCE` on M1, M3, M5 and M6 does not block. Quote the
declaration as the reason. It does not outrank the paper, though. A paper that declares no
experiments but reports a run or a result as the authors' own has contradicted itself: mark M3 and
M6 `SUSPECTED` and put the contradiction in front of the user.

---

## 4. Claim↔reference alignment

Does the cited source's support quote actually back this sentence, at this strength? This is a
judgment, so VERIFIER makes it from the sentence, the quote and its location.

| Verdict | Meaning | Effect |
|---|---|---|
| `supported` | A reader of the quote would agree with the sentence | None |
| `overstated` | The source is weaker than the sentence (`evidence_model.md` §3) | M2 `SUSPECTED` |
| `understated` | The sentence silently weakens or drops the source's qualifiers | Fix the sentence |
| `unsupported` | The source does not say this | M2 `SUSPECTED` |
| `not_checkable` | No quote, no access, or an `unresolvable` source | Listed; high-impact rows count as `INSUFFICIENT_EVIDENCE` on M2 |

**Sample at `--stage pre`:**

- **High-impact claims, 100%:** claims bound to the spine, numerical claims, causal or
  licensed-language claims, methods-critical claims, and claims touching a recorded conflict.
- **Random sentinels:** 10% of the remaining cited sentences, at least 3 and at most 10. The seed is
  the draft's SHA-256, so anyone can replay the selection and nobody can tune it.
- **A failed sentinel** means the error rate is unknown. Extend to every cited sentence in that
  section.

**At `--stage final`:** every cited sentence.

---

## 5. The two stages

**`--stage pre` (step 15)** runs on the tagged draft that passed G3, before any reviewer sees it.

**`--stage final` (step 20)** is a fresh pass, not a re-check of the first pass's findings. A new
VERIFIER context judges the edited draft without the earlier report, then the two are compared. Any
mode that was `SUSPECTED` before must now be `CLEAR`, not merely unmentioned. It runs on the
edited, still-tagged draft from step 19, because the claim tags are what it traces, and it confirms
that `paper/paper.md` is that same text with the tags removed.

---

## 6. Fixing, and deciding not to

1. Each `SUSPECTED` item becomes a correction. Fix the artifact first, then the prose. If evidence
   is missing, use `[MISSING …]`. Never write around it.
2. Re-verify the corrected items, in a fresh VERIFIER context. At most **3 rounds** per stage.
3. After round 3, or sooner if the user prefers, a named person records a decision with a reason:

   ```
   python tools/workflow_guard.py ask --rcs .rcs --id Q-012 --question "M5 is SUSPECTED on C014 ..." --blocks C014
   python tools/workflow_guard.py answer --rcs .rcs --id Q-012 --answer "..." --by "Name"
   ```

Then name the checkpoint in `audits/integrity/<stage>/decisions.json`:
`{"decisions": [{"mode": "M5", "checkpoint": "Q-012"}]}`. The gate accepts it only if a named person
answered that checkpoint with a reason of at least 20 characters, and the id appears in
`open_issues.md`.

A decision is not a pass. The mode keeps its status, the decision is recorded beside it, and it
goes into `open_issues.md`. Only a person can make it, never an agent on anyone's behalf. It cannot
be an accepted risk: those cover workflow decisions, not facts (`ACCEPTED_RISK_FACTUAL`). An
unattended run stops at the block and continues only with what the block does not affect.

---

## 7. Commands and report

```
python tools/integrity_check.py collect .rcs --stage pre --draft drafts/vNNN/paper.md
python tools/rce_roles.py verify --rcs .rcs --stage pre            # or dispatch agents/integrity_agent.md
python tools/integrity_check.py gate .rcs --stage pre --draft drafts/vNNN/paper.md \
       --out .rcs/audits/gates/GI_integrity.json
```

The VERIFIER reads `audits/integrity/<stage>/bundle.json` and writes
`audits/integrity/<stage>/verifier_report.json` (schema `integrity_report`). The single-shot
`rce_roles.py verify` sends the bundle, the draft, the claim and evidence maps and the story files.
It cannot open project files, so it marks a mode `INSUFFICIENT_EVIDENCE` where a judgment needs one. A
VERIFIER with file access (`adapters/claude_code/agents/rce-verifier.md`) can open them.

`verifier_report.json` holds `draft_sha256` (copied from the bundle), `round`, `isolation`, `modes`
(for each of M1–M7: `status`, `evidence`, `detail`) and `alignment` (a list of `{row, verdict, note}`).

`GI_integrity.json` names its `stage` and carries one entry per mode, the alignment summary and sample
seed, the draft's SHA-256, the round, and any recorded decisions. The per-stage reports stay under
`audits/integrity/<stage>/`, so `--stage final` can compare with `--stage pre`.

GI is passed only by a report with 0 errors for the current draft. A VERIFIER's words alone never
pass it: a tool finding overrides a `CLEAR` (`GI_CONTRADICTS_TOOL`), and in a project with a
provenance ledger the report must be recorded under the VERIFIER role. G5 needs a report with
`stage: final`.

**Limit of this gate.** GI checks what is on record. It can show that a number matches a log. It
cannot show that the log came from a correct experiment. Say so where it matters, and leave the
scientific judgment to the authors.
