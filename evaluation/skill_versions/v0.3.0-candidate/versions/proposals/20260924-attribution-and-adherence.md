# 20260924-attribution-and-adherence: rationale (0.1.0 → 0.2.0, gate pending)

**Clusters addressed:** S1 + S2 (attribution), S3 (adherence), S4 (length). S5 is on the watch-list (1 case) and S6 is not a failure, so neither gets a change.

## What readers got wrong
- **S1 (5/6 projects, F1 reader):** readers lost the authors' own concessions (Q11 net −7 nuggets; mean Q11 recall 0.536 skill vs 0.749 plain). The skill papers kept writer-derived methodological caveats and dropped the authors' broad limitations, which put the writer's critique in the authors' voice.
- **S2 (4/6, F1 only):** readers lost the authors' motivation and design reasons (Q2 −3, Q5 −3; interpretation nuggets lost 6 vs gained 2). The writer rebuilt the rationale from its own spine.
- **S3 (6/6):** the validator and the lint never ran. `section_rules.md` was never opened. Every gate was self-certified, and the artifacts had 141–227 schema errors. The rules that should have caught S1/S2 never reached the writer.
- **S4:** 2/6 skill papers were over the 4,500-word limit, against 0/6 plain papers.

## Root causes → mechanisms (smallest first)
| Part | Root cause | Mechanism |
|------|-----------|-----------|
| 1 | `missing_artifact`: no field distinguished author-stated from writer-derived content, and author rationale had no evidence kind. `conflicting_rules`: "no generic limitations" and "draft the limitation from the claim graph" together pushed broad author limitations out | Required `limitation.origin`. New evidence kind `rationale_stated`. `claim.rationale` + `claim.origin`. Validator coverage rules (every `limitation_noted`/`rationale_stated` item is carried; `author_stated` must cite author evidence). Lint on the assembled draft: author limitations and rationale must be tagged (ERROR); writer caveats go in an "Additional caveats" paragraph (WARN). Limitations contract: all author limitations first; broad ones attach to the central claim, not to the "generic" bin |
| 2 | `weak_gate` (honor system) + rules placed in unread files | G1/G3/G5 need a tool report (`--out`) with 0 errors and matching input hashes. `validate_artifacts.py .rcs` flags `SELF_CERTIFIED_GATE` and malformed `state.json`. SKILL.md now inlines only what the audit shows was unread but load-bearing: the attribution rules, a one-table section-contract summary, the claim-type/confidence enums, and the gate commands |
| 3 | `missing_check` | `length_limit_words`. A main-text word count (without back matter) in the lint (`S4-over-length`), which blocks G5. The step-21 procedure is relocation, never deletion of claims, negative results, author limitations, or rationale. Planned-words column at step 8 |

## Why these mechanisms, not wording
S3 shows that the writer reads SKILL.md and workflow.md and little else, and that it self-reports compliance. So every rule here is either (a) in SKILL.md or a schema, where the writer meets it while building artifacts, or (b) checked by a tool whose output file the gate needs. More exhortation in `section_rules.md` would repeat the v0.1.0 failure.

## Predicted effect (F1 reader; held-out set)
- **Q11:** +0.10 to +0.20 absolute recall. This is the most direct link: author limitations can't silently disappear from the claim map or the assembled draft.
- **Q2 / Q5:** +0.05 to +0.10 each. Less certain, because coverage depends on the extractor recording `rationale_stated` items, and no tool can check that against the source text. The F2 reader showed no S2 loss, so expect ≈0 there.
- **DR:** flat or lower. **Length:** 0 papers over the limit. **Process:** tool invocations > 0 in every run and schema errors near 0.

## Risks
More words in Limitations (counteracted by the length gate, but secondary results may move to the appendix, so watch Q7/Q9). SKILL.md grows by ~700 words. The "Additional caveats" label may read as unusual or may lead readers to discount real caveats. The extractor may over-record rationale. Tool cost, or stalls where Python is missing (the gate becomes "unverified"). The mixed-caveat WARN is noisy on v0.1.0-style text, including `A_clean.md`.

## Tests
T-008…T-018 in `tools/tests/test_v020_attribution_gates.py` (23 cases). There are two new fixtures, derived from `A_clean.md`, under `tools/tests/fixtures/`. They are not benchmark items, and promoting them to `perturbations/` is a human decision. On v0.1.0, 21/23 cases fail or error; the 2 that pass are negative controls. On the candidate, 44/44 pass. No benchmark item, rubric anchor, or reviewer prompt was edited. The demo claim map gained only the additive `origin` field on its four limitations.

## Scope note
The coordinator asked for one proposal. Parts 1–3 are independent: each has its own tests and can be reverted alone. The gate should report the Q11, Q2/Q5, and length effects separately so that each part can be accepted or rejected on its own evidence.
