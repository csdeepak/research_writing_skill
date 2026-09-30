# Step 17: Scientific overclaim audit (draft v001)

Anti-hype layer per `anti_patterns.md` SS B. Disposition rule followed throughout: **downgrade
the language or flag it; never strengthen the evidence or search for post-hoc support.**

| ID | Check | Finding | Action |
|----|-------|---------|--------|
| B1 Exaggerated novelty | grep for novel/first/unprecedented + `lint_draft.py` `B1-novelty` | One instance in step 10 draft ("genuinely novel architectures", Background P2) | Reworded to "unconventional architectures" (not a claim about MLPerf Tiny's own novelty at all -- it described the general hardware landscape -- but the word was removed rather than justified, since no search-scoped novelty claim was intended). 0 remaining. |
| B2 Unsupported superiority | grep for outperform/superior/better than | None found | No submission-vs-submission ranking is made anywhere (consistent with L004: no per-submission scores are available to rank). |
| B3 Unbacked SOTA | grep for state-of-the-art/SOTA | None found | -- |
| B4 Proof language | `lint_draft.py` `B4-proof`, `B4-verb-vs-type` | 0 findings after the step-10 fix (an `{C030}`-tagged sentence used "establish", tripping the interpretation-vs-strong-verb rule; reworded to "show") | Resolved by downgrading language, not by removing the tag. |
| B5 Causal from correlational | grep for causes/leads to/drives/due to | None found | The mechanism explanation in Discussion P2 uses "let"/"is consistent with", not causal verbs, and is explicitly hedged (see B11 below). |
| B6 Over-generalization | manual scope check: claim vs. evidence conditions | Discussion P4's general takeaway ("a workable way to standardize... a genuinely fragmented... landscape") could read as claiming this for TinyML benchmarking in general | Already bounded in the same paragraph: "Whether that same design choice would work as well in a more mature, more contested benchmarking setting... is not something this first, cooperative round can show on its own." Scope matches the evidence (one round). No change needed. |
| B7 Selective reporting | cross-check against `evidence/missing_evidence.json` and the one `negative_result` item | The one negative result (E054, no dataset changes) is reported in the main text (Results P4) and interpreted (Discussion P3), per its `reported_main` decision | No selective reporting found. |
| B8 Benchmark cherry-picking | do Table 1 / Table 2 show all items, or a subset? | All 4 benchmarks and all 5 submissions shown; both table cards record `selection_rule: "all ... shown"` | -- |
| B9 Vague significance / intensifiers | `lint_draft.py` `B9-significance`, `B9-intensifier` | 0 findings after step 10 fix ("a substantial amount of prior TinyML work" -> "prior TinyML work", dropping the unquantified intensifier rather than inventing a count) | -- |
| B10 Unequal baselines | manual check | Not applicable: this paper does not itself run or compare a proposed method against baselines; it presents a benchmark-design paper's own reported figures | -- |
| B11 Explanation vs. speculation blur | manual check for mechanistic "because" without an isolating experiment | Found: Discussion P2 explained *why* modularity let heterogeneous stacks report comparable results, as a flat mechanistic claim with no `{C###}` tag and no hedge, when the evidence is one round with no isolating ablation of "modularity" as a factor | **Fixed in this pass.** Reworded to "A plausible mechanism..., though not one this round was designed to isolate on its own" and tagged `{C030}` (`interpretation`) throughout, so it inherits `interpretation`'s permitted verbs and is auditable the same way every other interpretive claim is. |
| B12 Unattributed gains | manual check | Not applicable: no bundled changes with gains attributed to one cause; the paper does not measure a "gain" at all (no per-submission scores available, L004) | -- |
| B13 Invented reviewer expectations | grep for "reviewers will"/"the community agrees" | None found | -- |
| B14 Decorative/misattributed citation | citation audit (step 16) | 0 findings; 2 real citation bugs found and fixed (missing CoreMark/MLPerf-Inference citations, missing adoption paragraph) -- see `citation_audit.json` | -- |
| B15 Spin in abstract | manual check: does the Abstract lead with the primary outcome or a secondary positive? | Abstract states the positive finding (reference implementations met targets; five comparable results) and the limiting finding (no dataset changes; practice stayed non-data-centric) in the same weight, in the order the paper itself develops them | No spin found. |
| B16 Mathiness | manual check | The only numeric formula in the draft (640 = 5x128, describing the AD sliding window) is copied directly from the evidence (E039) to explain a real architectural constraint, not decorative | -- |
| B17 Hedge inflation | manual check: are hedges differentiated by actual confidence, or applied uniformly? | `measured` claims (accuracy figures) are stated plainly with only the source's own hedge word ("about 86%"); `interpretation` claims (C006, C030) carry explicit hedges ("suggests", "is better read as... than as a settled property", "a plausible mechanism... not one this round was designed to isolate"); `future` claims use "remains to be seen" | Hedging tracks claim type, not applied uniformly -- no inflation found. |

## Generalization-scope check (population / dataset / scale / conditions)
Re-checked every claim carrying a scope beyond "this suite as built": C030 (the central
interpretive claim) is scoped to "the case it was actually able to test" and "this first,
cooperative round" throughout its three occurrences (Discussion P1, P2, P4); C006 (the gap claim)
is scoped to "the three [benchmarks] the authors discuss" per `story/lit_gap_chain.md`'s scoped
GAP wording, not "no benchmark anywhere." No claim's stated scope exceeds its evidence's
conditions.

**Result: 1 defect found and fixed (B11, Discussion P2's unhedged mechanism explanation); 1
already-adequate scope hedge confirmed (B6, Discussion P4). 0 remaining overclaim flags.**
