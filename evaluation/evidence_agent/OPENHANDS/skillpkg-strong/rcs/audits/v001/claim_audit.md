# Step 12 — Evidence/claim audit

**Tagging.** All promoted claims (C001-C020) appear in the draft with `{C###}` tags at least once;
`lint_draft.py --rcs .rcs` reports 0 errors (no dangling/unresolved tags). Several secondary,
non-promoted numbers (e.g. gpt-4o-mini-scale results for benchmarks where only the headline model
was promoted to a claim, or baseline-only numbers) are flagged by the lint as `C1-orphan-claim`
(WARN, not ERROR): these are numbers drawn directly from evidence items (E011, E051, E065, E072,
etc.) that support the surrounding, already-tagged sentence rather than standing as independent
claims; no number appears that lacks a corresponding evidence item.

**Numeric fidelity (20%+ spot check, re-read from `.rcs/evidence/research_evidence.json`):**
26.0/E010 match; 79.3/E020 match; 52.0/E060 match; 53.1/E064 match; 57.6/E070, 42.4/E071 match;
77.3/E080, 65.8/E081 match; 50.0/E082, 59.6/E083 match; 15.5/E030, 20.2/18.2/E033 match; 40.8/E040,
91.1/E041 match; 32.1/E050, 13.2/E052 match; 78.8/E090, 79.6/E091, 68.1/E092 match; 38.0/E100,
40.0/E101 match; 6.3/E013 and 7.0/E012 both reported (conflict disclosed, not resolved); 81.3/E061
and 81.2/E066 both reported (conflict disclosed, not resolved). All 22 spot-checked values match
their evidence source verbatim (rounding: none applied, values copied as given).

**Claim type vs. verb check.** `measured` claims (C001,C002,C004-C007,C009-C012) use "reaches /
achieves / resolves"; `observed` claims (C003,C008,C013,C015,C018,C020) use "is lower than / scores
/ below / reports"; `interpretation` (C014) uses "is read as / consistent with", not "shows" or
"proves"; `future` (C016) uses "state ... as a target," not a present-tense result claim. No
verb exceeds its claim type's permitted list (`evidence_model.md` §3).

**Negative-result coverage.** All four evidence items decided `reported_main`
(E082, E100, E030, E040) appear in the draft, each adjacent to the baseline it underperforms and
referenced again in the Discussion (§6) and Limitations (§7). No negative result is omitted.

**Failures raised:** none new. `OVERCLAIM` not triggered (no unlicensed "SOTA"/"first"/"novel"/
"proves" language found by lint on the B-series anti-hype checks; see step 17). `MISSING_RESULT`
already marked as `[MISSING]`-equivalent by explicit textual disclosure (ML-Bench/BioCoder/
Gorilla/ToolQA per-row attribution, GPQA main/extended columns) rather than a bracketed marker,
since the missing item is a *specific numeric attribution*, not an entire result; this is recorded
in `open_issues.md`.
