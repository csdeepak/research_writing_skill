# Step 17 — Scientific overclaim audit (anti_patterns.md §B)

Ran `lint_draft.py` (surface screen) then manually checked every flag and every high-risk term
against the claim map. **One fix applied; all others reviewed and either already compliant or not
applicable.**

| ID | Check | Finding | Action |
|---|---|---|---|
| B1 exaggerated novelty | "first" used once (Background §2: "BEIR is the first benchmark to compare...") | Scoped explicitly ("to our knowledge", named against the two specific comparators) and matches claim C020 (`claim_type: literature`, hedge preserved from the source's own "to our knowledge") | No change needed; scoping already present |
| B2 unsupported superiority | "outperform(s)"/"beat(s)" used throughout Results | Every instance names the metric (nDCG@10), the conditions (18 zero-shot datasets or a named subset), and the margin (a percentage or a count of datasets) | Compliant |
| B3 unbacked SOTA | "state-of-the-art"/"SOTA" | Not used anywhere in the draft | N/A |
| B4 proof language | "shows that" used for interpretation-typed claims C003/C019 in the Abstract | **Overclaim found and fixed**: downgraded to "suggest that" (evidence_model.md §3 permitted verb for `interpretation`). Re-ran `lint_draft.py`: the `B4-verb-vs-type` error is gone (0 errors). `confirms`/`establishes` remain twice, both attached to `derived`-typed C018 (a direct, low-inferential-distance before/after re-measurement); left as is, since `derived` is not restricted by this rule and the verb matches the evidence's directness |
| B5 causal from correlational | "traces part of this to...", "this shows the similarity function is one contributing factor, not the sole explanation" (Section 5, TAS-B/ANCE length-preference ablation) | Already hedged: explicitly says "one contributing factor, not the sole explanation", and names the confounds (base model, loss, negative mining) the source itself flags. Matches claim C013's `derived` type and its recorded confidence reasoning | Compliant, no change |
| B6 over-generalization | Claim scope vs. evidence conditions | Checked C019 (the cross-attention interpretation): scope explicitly restricted to "the systems compared here" in its own claim statement and echoed in the draft ("a pattern observed across the systems compared, not a claim isolated by ablation... an interpretation, not a proof"); Limitations §8 restates the English-only/short-document/generalist-only scope | Compliant |
| B7 selective reporting | Negative-result coverage | All 4 negative-result evidence items reported main (see claim_evidence_audit.md) | Compliant |
| B8 benchmark cherry-picking | All 18 datasets / all 10 systems shown in Table 2; no subset selection | No selection rule needed since nothing is subset | Compliant |
| B9 vague significance | "significant(ly)" | Not used anywhere in the draft (checked by search) | N/A |
| B9 intensifiers | "substantially" (x2: Section 6 re-annotation deltas; Section 7 Discussion) | Section 6 instance is immediately followed by the exact numbers in the same sentence (compliant on inspection despite the lint flag). Section 7 instance is a Discussion-level callback to numbers already given in Section 5 (TAS-B 14/18, docT5query 11/18); re-stating the numbers again would violate the "Discussion does not repeat Results" rule (section_rules.md), so the summary word is kept | Reviewed, no change |
| B10 unequal baselines | Baseline tuning | Draft does not claim equal tuning budgets; Section 3/4 describe each system's own training procedure without asserting parity beyond the explicitly shared conditions (truncation, hardware) named in Section 4's last paragraph | Compliant (no false parity claim made) |
| B11 explanation vs. speculation | TAS-B training-setup attribution (C010) | Explicitly tagged `speculation` and written with "the authors attribute... speculatively" | Compliant |
| B12 unattributed gains | GenQ (multiple changes: synthetic queries + continued fine-tuning) | Attributed only to what the source itself attributes it to (domain-specific synthetic query adaptation), no stronger attribution added | Compliant |
| B13 invented consensus | "reviewers will expect", "the community agrees" | Not used | N/A |
| B14 decorative citation | Every citation | Audited individually in citation_audit.json; none found decorative | Compliant |
| B15 spin in abstract | Abstract's ordering of findings | Abstract leads with the primary finding (no architecture dominates / BM25 robust), not a secondary positive result; the bias case study and its qualification are both included, not omitted | Compliant |
| B16 mathiness | Equations | No equations used; the draft describes the similarity-function ablation in prose only, since the underlying formula does not change the reported claim | Compliant |
| B17 hedge inflation | Hedging pattern across the draft | Hedges (`suggest`, `is consistent with`, `speculatively`, `not... the sole explanation`) are placed only where the claim map records `interpretation`/`speculation`/`derived-with-caveat`; `measured` claims (e.g. the Table 2 numbers) are stated plainly. Hedging is not uniform, so real uncertainty remains distinguishable | Compliant |

## Generalization-scope check (population / dataset / scale / conditions)
Re-read every claim in `claims/claim_evidence_map.json` against its `scope` field and the
corresponding draft sentence. No claim's stated scope in the draft is broader than its recorded
`scope`/`limitations` fields. In particular: the cross-attention interpretation (C019) is not
stated as a property of "dense retrieval" in general (Discussion §7 explicitly disclaims that
reading); the bias finding (C017/C018) is not stated as established for "BEIR" as a whole, only for
TREC-COVID, with the broader claim explicitly marked as argued-not-measured (L008).

## Outcome
One overclaim found and corrected (B4, abstract). No claim was strengthened to resolve a flag; the
one fix downgraded language. `python rce/tools/lint_draft.py .rcs/drafts/v001/paper.md --rcs .rcs`
now returns 0 errors.
