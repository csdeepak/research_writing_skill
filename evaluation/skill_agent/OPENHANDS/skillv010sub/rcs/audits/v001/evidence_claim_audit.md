# Step 12 -- Evidence/claim audit

**Tag coverage.** `tools/lint_draft.py --rcs .rcs` run against the assembled draft: 0 errors.
Every `{C###}`/`{L###}` tag resolves against `claims/claim_evidence_map.json` (no
`tag-unresolved` findings). Remaining `C1-orphan-claim` WARNs (11) were individually reviewed;
all are either (a) the Abstract, which is conventionally untagged because it is a compressed
mirror of already-tagged body claims, (b) roadmap/transition/methodology sentences with no
number or comparative finding of their own, or (c) titles of cited works quoted verbatim inside
the References section, which must not be edited. None is an unresolved evidentiary claim.
`B4-verb-vs-type` check: 0 findings (no interpretation/speculation/hypothesis/future-tagged
sentence uses a strong "shows/proves/demonstrates/establishes" verb -- see
`audits/v001/overclaim_audit.md` for the full vocabulary scan).

**Numeric fidelity.** Every percentage figure in the draft body (51 distinct values, 58
occurrences) was programmatically cross-checked against the numeric values recorded in
`evidence/research_evidence.json`: **100% matched exactly** (script in this audit's working
notes; zero unmatched values). The one evidence value that must *not* appear, E004's superseded
6.3 (the Table 3/Table 4 conflict, see `state.json` AR003), does not appear anywhere in the
draft -- confirmed by its absence from the extracted value set. The four dollar-cost figures in
Table 1 and prose ($0.01, $1.10, $1.67, $1.72) and the two cost estimates ($6,900; $600) match
`evidence/research_evidence.json` E003 exactly.

**Claim-type / verb match.** Spot-checked all 21 claims in `claims/claim_evidence_map.json`
against their `permitted_verbs` and the verbs actually used in the draft:
- Measured claims (C001, C003-C013) use "resolved/reached/fixed/above/below" -- no "proves" or
  "demonstrates" attached to any of them.
- Derived claims (C002, C014) use "falls within/comparable to/exceeded" with the comparison
  scoped to the named baseline set, not to "all methods" generally.
- The one high-stakes interpretation (C016) is stated with "is consistent with" both in the
  Abstract and the Discussion, and is explicitly walked back from the paper's own "demonstrates"
  language (E025) precisely because C016 is `confidence: low` (evidence_model.md S4: low-confidence
  claims may appear in the abstract only if explicitly hedged -- satisfied).
- Literature claims (C017-C019) are attributed to their sources ("credited by the authors",
  "characterized... as") rather than asserted as this paper's own finding.

**Negative-result coverage.** All four `negative_result` evidence items (E011 ToolQA collapse,
E014 MiniWoB++ vs. CC-NET, E020 MINT-code, E023 Entity Deduction Arena) appear in Results, each
adjacent to the claim it qualifies, matching their `reported_main` decisions in
`claims/claim_evidence_map.json`. No `SELECTIVE_REPORTING` flag raised.

**Result: PASS.** No orphan claims in the evidentiary sense, no numeric drift, no claim-type/verb
mismatch, negative results fully reported.
