# Role: AUTHOR (steps 19-21)
Your working directory for this entire task is `C:/Users/csdee/AppData/Local/Temp/rce_ws/ASMOS_e2e`. Use absolute paths under it. Hard rules: never read, list,
search or write anything outside that directory; do not use the web; do not spawn agents; you may run `python` on the
tools in `C:/Users/csdee/AppData/Local/Temp/rce_ws/ASMOS_e2e/rce/tools/`. Do NOT read `rce/skill/agents/review_agent.md`, `recon_grader.md` or `skill_agent.md`.
No human is available during this run: wherever the skill says ASK or STOP, create a checkpoint
(`python rce/tools/workflow_guard.py ask --rcs .rcs --id Q-00N --question "..." --blocks <claim ids>`) and keep the
blocked claims `status: BLOCKED` and out of the paper. NEVER answer a checkpoint yourself. Accepted risks in
`.rcs/state.json` must have `"kind": "workflow"` (never license a fact). Evidence locator paths are relative to the
working directory, e.g. `project/results/summary.csv`.
After writing or changing any artifact, record it for your role:
`python rce/tools/workflow_guard.py record --rcs .rcs --role AUTHOR <files...>`.

The blind review of `.rcs/drafts/v001/paper.md` is in `.rcs/diagnostics/v001_1/` (diagnostics.json, reconstruction.json).
1. Step 19: revise structure-first into `.rcs/drafts/v002/paper.md` (tags kept). For EVERY blocking finding (any score <= 2;
   evidence_traceability / claim_evidence_alignment / unsupported_inference < 4) and EVERY inference issue, write a
   disposition to `.rcs/revisions/v001_1/dispositions.json`: {"items": [{"item": "finding:<index>" | "inference:<index>",
   "disposition": "fixed", "where": "..."} | {"disposition": "declined", "reason": ">= 20 chars"} | {"disposition":
   "deferred"} (and list it in `.rcs/open_issues.md`)]}. Indexes are positions in the diagnostics arrays.
   Then `python rce/tools/g4_check.py .rcs --round v001_1 --revised .rcs/drafts/v002/paper.md --out .rcs/audits/gates/G4_review.json`.
2. Step 21: line-edit a copy into `.rcs/drafts/v003/paper.md` (tags KEPT), check
   `python rce/tools/claim_invariance.py .rcs/drafts/v002/paper.md .rcs/drafts/v003/paper.md` (revert any drift), then write
   the final manuscript without tags to `paper/paper.md` (keep genuinely unresolved markers), and `.rcs/open_issues.md`.
3. Run all gates: `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v002/paper.md --round v001_1 --revised .rcs/drafts/v002/paper.md --final paper/paper.md --before .rcs/drafts/v002/paper.md --edited .rcs/drafts/v003/paper.md`
   and fix until they pass, or record exactly which gate fails and why in `.rcs/open_issues.md`.
Record everything you wrote as role AUTHOR. Reply DONE with the final word count and the effective gate statuses.

Tool changes made by the orchestrator after your draft (bug fixes found by this run; read nothing else about them):
- `workflow_guard.py record` now accepts the final manuscript `paper/paper.md` (it previously crashed on paths outside `.rcs`).
- `build_review_packet.py` now copies and hashes the figures a paper links.
- `lint_draft.py`: an author rationale or author-stated limitation whose claim is BLOCKED behind an open checkpoint is
  reported as withheld (WARN `S1/S2-author-statement-withheld`) instead of being required in the draft. Placeholder
  claims that existed only to satisfy the old rule may be reconsidered on their merits.
- `visuals.py` / `validate_visuals.py`: line charts now draw the value axis vertically, with x ticks and an x-axis title
  (optional registry field `x_label`, default: the x column name). A new check, `V3_AXIS_ENCODING`, fails any figure
  whose marks disagree with its labelled value axis. Existing figures must be re-rendered (`python rce/tools/visuals.py
  render .rcs --project-root .`, which the gate runner also does) and their registry hashes re-recorded.
