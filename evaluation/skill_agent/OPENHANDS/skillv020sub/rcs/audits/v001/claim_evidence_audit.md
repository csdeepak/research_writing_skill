# Step 12 -- Evidence / claim audit

## Numeric fidelity spot-check (programmatic, 100% of result-bearing evidence, not just the 20% minimum)
Every numeric value in every `result`/`negative_result` evidence item (62 distinct values) was
checked against `.rcs/drafts/v001/paper.md` by exact string match. 41 appear verbatim in the
draft. The 21 that do not are all **deliberate, scope-motivated omissions**, never a wrong number:
- Cost values (`avg_cost_usd`): omitted throughout -- the draft does not discuss per-instance
  cost, so no cost figure needed to appear.
- E152/E153 (the disputed SWE-Bench-Lite gpt-4o-mini value, 6.3% vs 7.0%): correctly excluded
  per `accepted_risks` (MISS-003).
- Weaker/redundant rows dropped to keep each table to one representative baseline-vs-OpenHands
  comparison per benchmark, rather than every backbone-model row: WebArena's gpt-3.5-turbo and
  gpt-4o-mini/gpt-4o rows for OpenHands (6.2, 8.3, 8.5, 14.5, 14.8 -- the claude-3-5-sonnet rows
  are kept as the strongest-configuration comparison); HumanEvalFix's three weaker non-agentic
  baselines (16.6, 30.4, 47.5 -- StarCoder2-15B at 48.6 is kept as "the strongest non-agentic
  baseline," which is arithmetically correct: 16.6 < 30.4 < 47.5 < 48.6); GAIA's gpt-4-0125-preview
  row (30.2, kept: gpt-4o's 32.1); GPQA's gpt-3.5-turbo-16k few-shot-CoT row (29.6, kept: gpt-4's
  38.8); AgentBench's gpt-3.5-turbo baseline row (32.6, kept: gpt-4's 42.4); MINT math subset's
  weak-backbone row (33.8, the code-subset scaling example 5.2->50.0 is used instead in
  Discussion to avoid repeating the same point twice); MiniWoB++'s delegated-CodeActAgent row
  (39.8, near-duplicate of BrowsingAgent's own 40.8, which is kept); Entity Deduction Arena's
  weak-backbone row (24.0 vs 27.0, the gpt-4o/gpt-4 comparison 38.0 vs 40.0 is kept).
- Aider (26.3) and Moatless Tools (26.7): correctly excluded per `accepted_risks` (MISS-005, no
  citable year).
No number that *does* appear in the draft was found to be altered, rounded differently than the
source (all keep the source's one decimal place), or mismatched to the wrong agent/model/
benchmark triple.

## Claim type vs. permitted verbs
Spot-checked every `{C0##}` tag's surrounding verb against `evidence_model.md` section 3 and the
claim's own `claim_type`:
- `measured` claims (C001, C003, C005-C012) use "reaches / resolves / fixes / scores" plus the
  number -- permitted.
- `derived` claims (C002, C004, C014) use "raises ... from ... to", "compares with", "scales
  with" -- permitted; none use "proves"/"shows that"/"demonstrates".
- `interpretation` claims (C013, C021, C030-C037) use "suggests", "is consistent with", "is
  competitive with", or state the authors' own rationale directly -- none use a disallowed
  strong verb (checked against the lint's `STRONG_VERB_RE`; 0 hits on any tagged sentence).
- `observed` claim C015 (folded into C013/C006/C010 in the drafted prose rather than kept as a
  separate tag) is expressed through the two negative-result sentences, both hedged
  appropriately ("trails", "is not universal").
The lint's `B4-verb-vs-type` check (claim type vs. strong verb) reported **0 hits** on the final
draft (see `audits/gates/G3_lint.json`).

## Negative-result coverage
Both `negative_result`-kind evidence items (E073 MiniWoB++, E097 MINT code subset) are reported
`reported_main` (per `claims/claim_evidence_map.json -> negative_result_decisions`) and appear in
the draft's Results, Discussion, and Limitations sections, not only in a buried aside. No
negative result was found excluded without a recorded reason.

## Author-confirmation status carried into the draft
C014, C021, and C041 remain `author_confirmation: pending` (no human available, per
`accepted_risks`). Each is phrased in the draft with hedged language ("suggests," "is
consistent with," -- never "shows" or "proves"), so the draft does not overstate their status
even though the claim map itself is not human-confirmed.

**Result: no `OVERCLAIM`, `SELECTIVE_REPORTING`, or `MISSING_RESULT` failure found.** Proceeding
to step 13.
