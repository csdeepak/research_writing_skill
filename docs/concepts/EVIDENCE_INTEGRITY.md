# Evidence integrity

RCE is designed to prevent unsupported claims from silently entering a manuscript. It **cannot guarantee** that an
underlying model never hallucinates. What it does is block or flag, under explicit rules, whatever it can check
deterministically. It asks a person when evidence is missing or conflicting, and it lists its known gaps (below)
instead of hiding them.

Each rule below names its mechanism and the test that guards it. Everything runs locally
(`python tools/rce.py check PROJECT --draft DRAFT`).

## RCE must not

| Must not | Mechanism | Level | Guarded by |
|---|---|---|---|
| invent results, sample sizes, metrics or values | every number in a draft traced to evidence (`verify_numbers.py`, rounding and %↔fraction allowed; derivations only from evidence cited on the same line) | ERROR (`--strict`, G3/G5 on v0.3 projects) | T-021, T-022, REAL-02/03, FC-0001/0002 |
| invent statistical significance or p-values | `significant` needs a `significance_test` license backed by evidence; p-values never inferred | ERROR | T-023, T-071, ADV-03 |
| invent citations | author-year citations must resolve to `corpus/source_registry.json`; sources are verified, never cited from memory | ERROR (WARN without a registry) | T-065 |
| repair a garbled source title from memory | `as_cited` kept; `TITLE_REPAIRED_FROM_MEMORY` | ERROR | ADV-05 |
| invent author explanations or limitations | author-stated rationale and limitations must be carried and attributed; writer caveats go under "Additional caveats" | ERROR | T-008…T-018, T-049 |
| invent figures | figures are declared transforms of real data files, rendered deterministically and re-rendered to verify (V6); illustrations must be labelled | ERROR | T-029…T-035, VIS-*, T-050 |
| fabricate missing answers | missing facts become a human checkpoint; claims stay `BLOCKED` until a named person answers; accepted risks may not license facts | ERROR | T-043, WF-03/04 |
| silently resolve contradictory evidence | same quantity with different values → `UNRECONCILED_CONFLICT`; claims citing an unresolved side → `BLOCKED_BY_CONFLICT` | ERROR | ADV-01/02, T-064 |
| turn assumptions into facts | measured/observed/derived claims with basis `none` → `UNSUPPORTED_FACT`; hypotheses/speculation are non-asserting | ERROR | T-071 |
| upgrade correlation into causation | `causes/leads to` needs a `causal_design` license | ERROR | T-071 |
| claim "state of the art" | needs a `sota_comparison` license | ERROR | T-071, T-064 |
| generalise beyond the evaluated population | `generalizes` needs an `ood_eval` license | ERROR | T-071 |
| certify its own gates | a gate passes only from a fresh, hash-bound tool report | ERROR | T-012…T-014, T-026, ADV-10 |

## RCE must

| Must | Mechanism |
|---|---|
| preserve provenance | evidence locators and source hashes; figure `source_hashes` + `render_sha256`; role ledger with file hashes |
| distinguish observation from interpretation | `claim_type` (measured, observed, derived, interpretation, hypothesis, speculation, …) |
| distinguish measured from derived values | `claim_type` + `basis`; `verify_numbers` reports `DERIVED_MATCH` for review |
| flag uncertainty | excess-precision and dropped-interval checks (`audit_reader.py`, `skim_layer.py`) |
| ask when evidence is missing | `workflow_guard.py ask`; `[ASK AUTHOR]` / `[MISSING …]` markers fail the final gate (G5) |
| retain unresolved states | open checkpoints, `open_issues.md`, deferred dispositions, `missing_evidence.json` |
| attribute author explanations | S1/S2 attribution checks |
| preserve limitations | author-stated limitations must reach the Limitations section |
| show evidence paths | claim tags `{C###}` in drafts; claim map → evidence ids → file locators |
| fail closed for high-risk claims | once a project uses `licenses`, unlicensed strong language is an ERROR, not a warning |

The strong-language vocabulary is configurable per project, because research communities differ:
`.rcs/language_policy.json` can extend or disable existing license types (T-070). The applied policy is written into
the lint report.

## Known gaps (not detected deterministically in v0.4.0)
- **Missing sample size / denominator** for a reported value (T-064 item 4).
- **Denominator direction** of a percentage change: "25% lower" and "20% lower" are both valid ratios of the same two
  numbers with different bases. The tool flags the derivation for confirmation (`DERIVED_MATCH`) but cannot decide
  which base the sentence means (T-064 item 10).
- **Unit errors** are checked for figures (declared units) but not for prose.
- **Semantic overreach without trigger words:** a claim stronger than its evidence but phrased without a licensed term
  is left to the blind reviewer (inference issues) and to people.
- **Everything a model reads is still a model's reading.** CORPUS_AGENT extracts evidence with a model. The tools
  check consistency and traceability, not whether the extraction understood the source correctly. Hard evidence items
  point to files a person can open.

Report a gap as a failure case (`.github/ISSUE_TEMPLATE/evidence_integrity.yml`). Each confirmed case becomes a
permanent regression test (`cases/failures/`).
