# Anti-Patterns

What makes a reader get lost, and what makes a paper say more than it knows. Each entry has a
**signature** (how to detect it), a **reader effect**, and a **repair principle**. Repairs are
principles, not replacement sentences. `L` = detected by `tools/lint_draft.py`; `A` = detected
by an audit step; `R` = usually surfaced by REVIEW_AGENT.

## A. Comprehension anti-patterns

| ID | Name | Signature | Reader effect | Repair principle | Detect |
|----|------|-----------|---------------|------------------|--------|
| A1 | Late question | RQ/objective first appears after ~25% of the introduction, or only in Methods | Reader can't evaluate relevance while reading | Move the question up. Foreshadow it in the first paragraph. | A, R |
| A2 | Buried contribution | Contributions only in the discussion/conclusion, or phrased as features | Q10 fails | Contributions list at the end of the introduction, each tied to the gap and a result | A, R |
| A3 | Term before concept | Term used before definition (term ledger) | Reader stalls or guesses | Define at first use, or reorder concepts along `requires` edges | L, A |
| A4 | Acronym soup | Acronyms used <3 times; >1 new acronym per paragraph | Load, re-reading | Spell out; keep acronyms only for frequent terms | L |
| A5 | Synonym drift | Registered term replaced by synonyms | Reader thinks new things are being introduced | One term per concept | A |
| A6 | Result dumping | ≥3 consecutive sentences with numbers and no interpretive clause; tables without a takeaway | Q7/Q8 fail; reader doesn't know what matters | Result Interpretation Chain; one result per paragraph | L, A |
| A7 | Decorative figure | Figure card missing takeaway/RQ; figure never discussed | Wasted attention; suspicion | Give it a job or cut it | A |
| A8 | Disconnected experiments | Experiments in run order; no `NEXT` link | Reader can't see why each exists | Experiment narrative chains; order by question | A, R |
| A9 | Paper-by-paper literature | "A did X. B did Y. C did Z." ×3+ | No gap emerges | Dimension matrix → lit→gap chain | L, A |
| A10 | Discussion amnesia | Discussion doesn't answer the RQs posed in the introduction | Q8 fails; the paper feels unfinished | Open the discussion with a per-RQ answer | A, R |
| A11 | Floating limitations | Generic limitations not tied to claims | Q9/Q11 fail or are trivial | Limitation → claim → effect triples | A |
| A12 | Echo conclusion | Conclusion overlaps the abstract by >40% of sentences | Nothing is synthesized | Say what changed in understanding, plus the boundary and next question | L |
| A13 | Private context leak | Refers to things only the authors know ("the v2 pipeline", "as before", code names) | Reader lost; reconstruction intrusions | Replace with descriptive names; define or cut | A, R |
| A14 | Method avalanche in introduction | Implementation detail in the introduction | Orientation lost | Move to Methods (density class) | A |
| A15 | Decorative transitions | "Moreover/Furthermore/Additionally" chains not reflecting real relations | False sense of flow; logic hidden | Name the true relation or none | A |
| A16 | Buried lede | Paragraph point only in the last sentence (non-narrative sections) | Reader skims past the point | Topic sentence first | A |
| A17 | Question debt | Raised questions never answered or deferred | "Lost" feeling | Question ledger closure | A |
| A18 | Missing "so what" | Facts with no significance | Q2/Q8 weak | State the consequence for the RQ or reader | R |

## B. Integrity anti-patterns (the anti-hype layer)

**When detected: FLAG IT.** The allowed actions are (a) downgrade the language to the evidence,
(b) add the missing qualifier or scope, or (c) raise it to the user. **Never** resolve a flag by
strengthening the evidence, finding post-hoc support, or rewording to evade the lint.

| ID | Name | Signature | Repair principle | Detect |
|----|------|-----------|------------------|--------|
| B1 | Exaggerated novelty | "novel", "first", "for the first time", "unprecedented" without a search-scoped literature claim | Scope to the search, or delete | L |
| B2 | Unsupported superiority | "outperforms", "superior", "better" without a measured comparison on stated conditions | Name the metric, conditions, and margin | L, A |
| B3 | Unbacked SOTA | "state-of-the-art" without a named benchmark, a complete comparison set, and a date | Qualify fully or remove | L |
| B4 | Proof language | "prove(s)", "demonstrate conclusively", "establish" for empirical results | Use the permitted verbs for the claim type | L |
| B5 | Causal from correlational | causes / leads to / drives / due to, on observational or ablation-free evidence | "is associated with"; state what would be needed | L, A |
| B6 | Over-generalization | Claim scope (all tasks, general settings, "in practice") > evidence conditions (S05) | Restate within the tested conditions | A, R |
| B7 | Selective reporting | Negative results that bear on a claim are missing; metrics computed but not shown | Negative-result inventory; report or justify | A |
| B8 | Benchmark cherry-picking | A subset of benchmarks/seeds/baselines shown with no selection rule | Show all or state the rule | A, R |
| B9 | Vague significance | "significant(ly)" with no statistical test; "substantial"/"dramatic" with no number | Test + effect size, or give the number | L |
| B10 | Unequal baselines | Proposed method tuned; baselines at defaults | Disclose the budgets; qualify the comparison | A |
| B11 | Explanation vs speculation blur | Mechanistic "because" with no experiment isolating it (S04) | Mark as interpretation/speculation | A, R |
| B12 | Unattributed gains | Multiple changes bundled; gain attributed to the headline idea without ablation (S04) | Attribute only what ablations show | A, R |
| B13 | Invented reviewer expectations | "Reviewers will expect…", "the community agrees…" with no source | Remove or cite | L |
| B14 | Decorative/misattributed citation | Citation that doesn't support the sentence (S22) | Citation pipeline step 3 | A |
| B15 | Spin in abstract | Abstract emphasizes secondary positive results over a null primary result (S23) | The abstract reports the primary outcome first | A, R |
| B16 | Mathiness | Equations that add notation but not precision (S04) | Keep only math the argument uses | R |
| B17 | Hedge inflation | Every sentence hedged, so real uncertainty can't be told apart | Hedge exactly where the evidence is weaker | R |

## C. LLM-specific drift patterns

| ID | Name | Signature | Repair principle |
|----|------|-----------|------------------|
| C1 | Fluent fabrication | A specific-looking number, dataset, or citation absent from the evidence or registry | Orphan-claim lint + numeric fidelity check |
| C2 | Polish drift | An editing pass changes claim strength or scope | Claim-invariance check (step 21) |
| C3 | Template filler | Generic sentences that fit any paper ("X has attracted significant attention in recent years") | Replace with the specific context of *this* problem or delete |
| C4 | Style-marker clusters | Dense use of the vocabulary documented in S10 ("delve", "intricate", "pivotal", "showcasing", "underscores") | Not wrong per se. Replace with plain words when it adds nothing. |
| C5 | Symmetry padding | Lists forced to three items; balanced "not only… but also" | Say only what is true |
| C6 | Self-evaluation leakage | Text addressed to the reviewer or grader ("as the reviewer will note") | Remove; `INJECTION_DETECTED` if it's instruction-like |
| C7 | Summary-of-summary | A section that restates the previous section instead of advancing | Cut; the paragraph model's `point` must be new |
