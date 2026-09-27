# Step 17 — Scientific overclaim audit (anti_patterns.md §B)

Checked every B-series watch-list term against the draft.

- **B1 exaggerated novelty** ("novel", "first", "unprecedented"): not used anywhere in the draft.
  The Introduction explicitly declines a novelty claim ("we make no claim here about how
  OpenHands's platform design compares to alternative platforms") because the comparison table is
  unverifiable in this evidence package. Pass.
- **B2 unsupported superiority** ("outperforms", "superior", "better"): the draft uses "reaches /
  above / below / exceeds / trails" with the specific metric, conditions, and margin stated
  in-line every time (e.g. "57.6%... above the AgentBench baseline agent's 42.4%"). Pass.
- **B3 unbacked SOTA**: "state-of-the-art"/"SOTA" is not used anywhere in the draft. Pass.
- **B4 proof language** ("prove", "demonstrate conclusively", "establish"): not used. The
  Conclusion uses "read... as," "demonstrated," is avoided; checked "demonstrated" usage in draft —
  not present as a verb applied to OpenHands's own claims. Pass.
- **B5 causal language** ("causes", "leads to", "drives"): the lint flagged one instance at §2 ¶1
  ("Readers outside this subfield need three conventions before the results... are readable") —
  reviewed and this is a pedagogical statement about the reader, not a causal claim about the
  research; not a B5 violation, logged as a lint false positive.
- **B6 over-generalization**: claim scope statements are qualified to the tested conditions
  throughout (e.g. C014 is stated as a category-level pattern, not "in general" or "in practice");
  §7 explicitly states the scope boundary for each limitation. Pass.
- **B7 selective reporting**: all four `reported_main` negative results (E082, E100, E030, E040)
  appear in the draft (see step 12). Pass.
- **B8 benchmark cherry-picking**: all nine safely-attributable benchmarks are reported (Table 1);
  the four unsafely-attributable ones are named and excluded with a stated reason, not silently
  dropped. Pass.
- **B9 vague significance**: "significant(ly)" is not used to describe any result; magnitudes are
  given as percentage-point differences instead (e.g. "1.3 percentage points"), paired with the
  no-variance caveat (L001). Pass.
- **B10 unequal baselines**: disclosed as a limitation (L004) rather than ignored or smoothed over.
  Pass (flagged, not silently accepted).
- **B11 explanation vs. speculation blur**: the WebArena/MiniWoB++ training-paradigm explanation
  (§6) is marked as a partial, qualified account ("at least in part") and is grounded in a stated
  factual difference (trained vs. zero-shot), not an unmarked causal story. Pass.
- **B13 invented reviewer expectations**: not present. Pass.
- **B14 decorative citation**: every citation states what its source contributes (see citation
  audit step 7 column). Pass.
- **B15 spin in abstract**: the abstract states the below-baseline WebArena/MiniWoB++ results and
  the two internal conflicts in the same paragraph as the positive results, not deferred to later
  sections only. Pass.

**Generalization-scope check (claim vs. evidence conditions).** For every `measured`/`observed`
claim reused in the Discussion (C001, C002, C009, C010, C014, C015), the scope stated in the
Discussion matches the scope recorded in `claims/claim_evidence_map.json` (dataset, instance
count, model, shot setting) — no claim is generalized beyond its tested condition in the move from
Results to Discussion.

**Conclusion:** no B-series flags require downgrading language beyond what step 12-14 already
adjusted (the direction fix on Workflow Guided Exploration). No flag was resolved by strengthening
evidence or searching for post-hoc support, consistent with the hard rule.
