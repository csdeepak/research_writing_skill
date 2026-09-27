# Step 11 — Reader reconstruction self-test (AUTHOR, same context; no subagent runtime available)

Answered from `.rcs/drafts/v001/paper.md` alone (tags visible), then compared against
`story/spine.md` and `claims/claim_evidence_map.json`.

Q1 Problem: Testing an LLM agent on real digital tasks needs a loop plus sandboxing, tool
interfaces, and per-benchmark harnesses that are normally rebuilt per project. **Match: spine
line 1.**
Q2 Why it matters: Duplicated infrastructure makes it hard to know whether an agent design
generalizes or is an artifact of one benchmark. **Match.**
Q3 What's missing: A verified feature-by-feature framework comparison isn't available in this
evidence package; the documented gap is that evaluation is organized per-domain. **Match: spine
line 2, correctly hedged (no novelty claim).**
Q4 What exactly was done: OpenHands agent hub + 15-benchmark evaluation framework; CodeActAgent
and BrowsingAgent run across three categories. **Match: spine line 4.**
Q5 Why this method: Reuses existing, independently published benchmarks and their own baselines
per category, stated in §2 and §4. **Match.**
Q6 Experiments: Three category-level evaluations (software, web, misc.), each listed with
benchmarks, instances, shot settings (Table 1, §5.1-5.3). **Match.**
Q7 Strongest results: 26.0% SWE-Bench Lite, 79.3% HumanEvalFix, exceeding 4/6 misc.-assistance
baselines. **Match: spine line 5.**
Q8 What results establish: A mixed cross-domain pattern consistent with a generalist-platform
contribution, not single-benchmark superiority. **Match: spine line 6.**
Q9 What they do NOT establish: Not superiority on WebArena/MiniWoB++/MINT-code/EDA; not
statistical significance (no variance reported). **Match: §7 Limitations.**
Q10 Primary contribution: The shared platform + harness enabling one agent's cross-domain
measurement. **Match: spine line 4/N16.**
Q11 Main limitations: single-run/no-variance, two internal numeric conflicts, unattributable
table cells, unknown baseline budget parity, no raw logs available. **Match: spine line 7,
§7.**
Q12 One-day-later takeaway: "One open platform let one general LLM agent be tested across code,
web, and misc. tasks; it did well on some, trailed specialists on others, and every number is a
single unreplicated run." **Match: spine lines 5-7.**

**Distortions found:** none (no overstated/contradicted answers versus the spine/claim map).
**Result:** provisional pass (no gold story exists; graded by the author against the spine, per
run-specific instruction — no RECON_GRADER subagent available). Proceeding to step 12.
