# Step 17 -- Scientific overclaim audit

Ran the anti-hype layer (`anti_patterns.md` Section B) via `tools/lint_draft.py --rcs .rcs`
(final run: 0 errors, 22 warnings, 47 info -- see `.rcs/audits/gates/G3_lint.json`) and reviewed
every flag by hand. No flag was resolved by strengthening the evidence or searching for post-hoc
support; every fix downgraded language or added the missing qualifier.

| Anti-pattern | Found? | Action |
|---|---|---|
| B1 Exaggerated novelty ("novel"/"first"/"unprecedented") | Found once in an early draft of Related Work ("BEIR is the first benchmark to test... jointly") | Rewritten to "Among these two prior multi-dataset resources, neither tests... jointly... Closing that gap... is the contribution this paper makes," removing the unscoped "first" claim entirely (see `corpus/anti_patterns.json` ANT-001, which flagged the *source* paper's own unqualified use of "state-of-the-art" in its Abstract as a pattern to avoid repeating) |
| B2 Unsupported superiority ("outperforms"/"better" without a measured comparison) | Not found | every "outperforms"/"underperforms" instance names the metric (nDCG@10), the comparator (BM25 or another named system), and either a percentage or a dataset count |
| B3 Unbacked SOTA | Not found | the draft never uses "state-of-the-art"; the ten systems are introduced by architecture family and citation instead (see `corpus/anti_patterns.json` ANT-001) |
| B4 Proof language ("prove"/"demonstrate conclusively"/"establish") | Not found (0 `B4-proof` lint findings) | -- |
| B5 Causal from correlational | Reviewed 0 `B5-causal` lint findings; the one mechanism claim (similarity function -> length preference, C015/C016) is based on an actual controlled ablation (architecture/data/loss held fixed, only the similarity function varied), so causal framing there is licensed by the design, and is still hedged ("is one identifiable source of", not "causes") | no change needed |
| B6 Over-generalization (claim scope > evidence conditions) | Checked C004/C006 (18-dataset average) against L001-L002/L005/L008 (English-only, short documents, generalist-only, 2021 snapshot) | scope boundaries are stated in Limitations and referenced from the Conclusion; no claim asserts beyond English, short/512-token documents, or the ten evaluated systems |
| B7 Selective reporting | Checked against `evidence/missing_evidence.json` and the negative-result inventory | all six recorded negative results are reported in the main text (see `claim_audit.md`) |
| B8 Benchmark cherry-picking | Checked: does the draft show all 18 datasets' aggregate, or a favorable subset? | Table 1 reports the full 18-dataset average for every system; no subset selection |
| B9 Vague significance / intensifiers | Found "substantially more compute" (Introduction) and "substantially more computation" (Conclusion) | both rewritten to give the actual number ("up to 20-30x more compute per query"); re-run of the lint shows 0 remaining `B9-intensifier` findings |
| B10 Unequal baselines undisclosed | Checked Experimental Setup | the draft discloses that DPR was trained on different data than the rest, and that GenQ receives dataset-specific further fine-tuning that the other systems do not; this asymmetry is stated, not hidden |
| B11 Explanation vs. speculation blur | Checked C013 vs. C015/C016 | C013 (TAS-B's overall training-setup advantage) is explicitly marked as the authors' speculation; C015/C016 (length preference) is derived from an actual isolating ablation and is worded accordingly ("is consistent with", "is one identifiable source of", not "is the reason") |
| B12 Unattributed gains (bundled changes) | Checked GenQ (C017) | the draft attributes GenQ's domain-specific gains/losses only to the fine-tuning step actually tested, without claiming which of GenQ's several changes (synthetic queries, per-dataset adaptation, document cap) is responsible |
| B13 Invented reviewer/consensus expectations | Not found (0 `B13-invented-consensus` lint findings) | -- |
| B14 Decorative/misattributed citation | Checked in `citation_audit.json` | 0 decorative citations found |
| B15 Spin in abstract (secondary result emphasized over primary) | Checked Abstract | the Abstract leads with the primary finding (in-domain accuracy does not predict zero-shot performance) before the secondary annotation-bias case study |
| B16 Mathiness | Not applicable | draft contains no equations |
| B17 Hedge inflation (every sentence hedged) | Checked | hedging is concentrated on the `interpretation`/`speculation` claims (C005, C008, C013, C016, C019) and the Limitations section; `measured`/`observed` claims (the majority of the draft) are stated plainly with their numbers, so real uncertainty remains distinguishable from confident reporting |

## Generalization-scope check
Re-read every claim's `scope` field in `claims/claim_evidence_map.json` against the sentence that
carries it in the draft. No claim's stated scope (population/dataset/conditions) exceeds what its
`evidence` field supports. The two claims scoped narrowest (C018, C019: TREC-COVID only) are
explicitly flagged as such in both the claim map and the draft text ("we checked this assumption
on one dataset"; "we did not re-run this check on the other 17 datasets").

## Outcome
No open `OVERCLAIM` flag remains. Two flags were found and fixed (B1, B9); both fixes downgraded
language or added a qualifier, per the repair principle -- neither the evidence nor the claim map
was changed to accommodate the wording.
