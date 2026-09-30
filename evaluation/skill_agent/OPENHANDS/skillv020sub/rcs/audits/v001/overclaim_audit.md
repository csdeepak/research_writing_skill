# Step 17 -- Scientific overclaim audit (anti_patterns.md section B)

Ran `tools/lint_draft.py --rcs .rcs --json` on the final draft and reviewed every finding by
rule (see `audits/gates/G3_lint.json` for the full machine-readable list). Full breakdown of the
72 findings: 48 `A-long-sentence` (INFO, reviewed in `term_load_audit.md`), 19
`A3-undefined-acronym` (WARN, reviewed in `term_load_audit.md`), 1 `A3-use-before-definition`
(WARN, GAIA -- the same accepted trade-off documented in `term_load_audit.md`), 1
`A4-rare-acronym` (INFO, "ACI" used once as a parenthetical gloss after being spelled out in
full -- judged fine as-is, not a soup of unexplained acronyms), 3 `C1-orphan-claim` (WARN, all
three are bibliography *titles* in the References section being misread as claim-like sentences
by the lint's regex -- false positives, not fixed), and 1 `B9-significance` (WARN, matches the
substring "Significant" inside the URL `github.com/Significant-Gravitas/Auto-GPT`, i.e. a
proper-noun GitHub organization name, not the word "significant" used evidentially -- false
positive, not fixed).

**Zero hits on every other anti-hype rule in the B section:**

| ID | Signature checked for | Result |
|----|------------------------|--------|
| B1 novelty | novel / first / unprecedented / pioneering | 0 uses anywhere in the draft |
| B2 unsupported superiority | outperform/superior/better without a measured comparison | every use ("outperforms," "exceeds," "trails") is immediately followed by the metric, the two conditions, and the margin |
| B3 unbacked SOTA | "state-of-the-art" / "SOTA" | 0 uses |
| B4 proof language | prove(s) / demonstrate conclusively / establish | 0 uses; every result is reported with "reaches / resolves / fixes / scores," matching the `measured` claim type's permitted verbs |
| B5 causal-from-correlational | causes / leads to / drives / due to | 0 uses; Discussion deliberately uses "tracks" and "the most direct explanation... is" rather than a causal verb, and explicitly names and sets aside the rival (architecture-is-category-specific) explanation |
| B6 over-generalization | claim scope wider than evidence conditions | checked every `{C0##}`-tagged sentence's scope against `claims/claim_evidence_map.json -> scope`; none broadens beyond its recorded dataset/condition scope. The central claim (C013) is explicitly scoped to "9 of 11" and "most... not... every one," not "all" |
| B7 selective reporting | negative results omitted | both negative-result evidence items (MiniWoB++, MINT code subset) are reported in Results, Discussion, and Limitations -- see `claim_evidence_audit.md` |
| B8 benchmark cherry-picking | a subset shown with no selection rule | every table's card (`plan/figure_cards/`) states its selection rule; omitted rows are logged and justified in `claim_evidence_audit.md`, not silently dropped |
| B9 vague significance/intensifiers | "significant(ly)" without a test; dramatic/substantial/huge | the two genuine `substantial` hits found by lint on the first pass were rewritten to "considerable" plus the actual number already present in the same sentence; the one remaining `B9-significance` hit is a URL substring, not prose |
| B10 unequal baselines | proposed method tuned, baselines at defaults, undisclosed | disclosed directly and repeatedly: the HumanEvalFix 0-shot/1-shot asymmetry is stated in Results *and* Limitations {L004}; the cross-benchmark backbone/shot-count/training-regime differences are stated as "Additional caveats" {L006} |
| B11 explanation-vs-speculation blur | mechanistic "because" with no isolating experiment | the backbone-capability explanation (C014) is introduced with "the most direct explanation... is," an alternative is named and the reason it is judged weaker is given, and the claim is tagged `derived`/hedged ("suggests"), never asserted as a proven mechanism |
| B12 unattributed gains | bundled changes, gain attributed to one idea without an ablation | not applicable here -- no ablation is claimed; D.2 explicitly says no controlled single-variable ablation isolates the architecture's contribution, which is the honest, weaker claim rather than an unattributed strong one |
| B13 invented consensus | "reviewers will expect" / "the community agrees" | 0 uses |
| B14 decorative citation | citation doesn't support the sentence | checked in `citation_audit.json` step 3 for all 30 sources: pass |
| B15 spin in the abstract | secondary positive result emphasized over a null primary result | the Abstract leads with the primary finding (cross-category competitiveness) and states the MiniWoB++ negative result and the authors' own "still struggle with complex tasks" concession in the same paragraph, not omitted or buried |
| B16 mathiness | equations adding notation but not precision | no equations/notation are used in the draft at all |
| B17 hedge inflation | every sentence hedged so real uncertainty can't be told apart | hedges are placed only where the evidence is actually weaker (the two `derived`/`interpretation` claims C013/C014, and the two negative-result sentences); the `measured` claims (the bulk of Results) are stated plainly with their numbers, unhedged, since they are directly transcribed hard results |

## Generalization-scope check (population / dataset / scale / conditions)
Re-read every claim in `claims/claim_evidence_map.json` against its `scope` field and the
corresponding draft sentence. No claim's drafted sentence asserts a broader population, dataset,
scale, or condition set than its `scope` field records. The central claim (C013) is the one most
at risk of over-generalization and is explicitly scoped in the draft to "9 of 11" benchmarks and
"the majority... not... every one," matching `scope.conditions` in the claim map exactly.

**Result: no unresolved overclaim flag.** Every flag the lint raised was either fixed by
downgrading the language (never by searching for post-hoc support or strengthening the
evidence) or reviewed and judged a tool false-positive, recorded here rather than silently
ignored. This completes the run-specific scope (steps 1-17); step 18 (blind REVIEW_AGENT) is
performed externally per TASK.md.
