# Step 17 -- Scientific overclaim audit

**Vocabulary scan** (`anti_patterns.md` S B and `evidence_model.md` S3's global watch-list),
run programmatically against the draft body (References excluded, since cited titles cannot be
edited):

| Term class | Hits | Disposition |
|---|---|---|
| prove/proof | 0 | -- |
| novel/first/unprecedented | 0 | -- |
| state-of-the-art/SOTA | 0 (1 hit is inside a quoted, unalterable reference title) | Accepted: reference title only |
| significant(ly) | 0 | -- |
| always/never | 1 ("always" -- a stipulative definition of how this paper uses the term "success rate", not an empirical universal claim) | Reviewed, kept |
| dramatically/remarkably/substantially/huge/massive/vastly/drastic/tremendous | 0 (one earlier instance of "substantially restructured" was rewritten to name the concrete, dated evidence instead -- E040-E042, SDK change dated November 2025) | Fixed during drafting |
| clearly/obviously | 1 found during drafting ("clearly behind it on a few") | **Fixed**: removed "clearly" (Discussion paragraph 1) |
| causes/leads to/drives | 2 ("drive(s)" describing how LLMs power an agent's decision loop -- an architectural/definitional statement, not a causal claim about a measured outcome) | Reviewed, kept |
| generalizes | 1 ("how far the platform's competitiveness generalizes across backbone models" -- immediately followed by a counter-example, the ToolQA collapse, so the sentence questions and bounds generalization rather than asserting it) | Reviewed, kept |
| shows that / proves / demonstrates / establishes | 4 uses of "establish(ed)", all either (a) attributing a finding to prior cited work (SWE-Agent's own established result) or (b) a negation ("is not established", "does and does not establish") stating a limitation -- none asserts this paper's own claim with unwarranted certainty | Reviewed, kept |

**B-series anti-pattern review** (`anti_patterns.md` S B):
- B2 unsupported superiority: every "above/below/exceeded/trails" statement names the metric,
  the specific comparison system, and the two numbers being compared (e.g. "57.6% vs. 42.4%");
  none is bare "outperforms".
- B6 over-generalization: the central claim (C016) is explicitly scoped in its own statement
  ("bounded to the 15 evaluated benchmarks, the specific backbone LLMs used, and the platform
  version evaluated") and hedged with "is consistent with" rather than asserted as established
  fact; the Abstract carries the same hedge and the same scope.
- B7 selective reporting: see `evidence_claim_audit.md` -- all four negative results reported.
- B8 benchmark cherry-picking: Table 2 shows all 15 evaluated benchmarks, including the 4 where
  OpenHands trails its comparison baseline; no selection rule was needed because nothing was
  excluded.
- B10 unequal baselines: disclosed explicitly as Limitation L002 (backbone-model confound) and
  L004 (protocol heterogeneity), in the Results/Evaluation Setup text itself, not only in
  Limitations.
- B11 explanation vs. speculation: the mechanism paragraph (Discussion P2) is phrased "is some
  evidence that... though Limitations below explains why this cannot be stated more strongly" --
  explicitly marked as a bounded inference, not asserted as demonstrated.
- B15 spin in abstract: the Abstract leads with the primary, already-qualified finding (the
  above/within/below breakdown) before the interpretive sentence, and includes the same hedges
  and limitations named in the body, not only positive framing.

**Result: PASS**, after one in-draft fix ("clearly" removed) and one in-draft rewrite
("substantially restructured" -> concrete, dated fact). No claim's language exceeds its
`claim_evidence_map.json` claim type or `confidence` level.
