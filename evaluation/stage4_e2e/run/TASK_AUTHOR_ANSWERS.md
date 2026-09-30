# Role: AUTHOR (checkpoint answers received)
Your working directory for this entire task is `C:/Users/csdee/AppData/Local/Temp/rce_ws/ASMOS_e2e`. Use absolute paths under it. Hard rules: never read, list,
search or write anything outside that directory; do not use the web; do not spawn agents; you may run `python` on the
tools in `rce/tools/`. Do NOT read `rce/skill/agents/review_agent.md`, `recon_grader.md` or `skill_agent.md`. NEVER answer
or edit a checkpoint yourself. Record every file you write: `python rce/tools/workflow_guard.py record --rcs .rcs --role AUTHOR <files...>`.

A named person (the project owner) has answered three checkpoints; see `.rcs/checkpoints/answers.json` (Q-001, Q-002,
Q-004). Q-003 and Q-005 are still open: everything they block stays BLOCKED and out of the paper, and their markers stay.

1. Apply each answer through the artifacts first (`.rcs/claims/claim_evidence_map.json`), exactly as answered, no further:
   - a claim the answer rules out: `author_confirmation: "rejected"` (it stays out of the paper);
   - a claim the answer narrows (Q-004: "zero retraining" only): restate it to what the answer allows, cite its evidence,
     set `status` from the evidence and `author_confirmation: "confirmed"`;
   - claims the answer confirms: `author_confirmation: "confirmed"`.
   Do not change anything an answer does not cover. Remove the "withheld pending an answer" wording for Q-001, Q-002 and
   Q-004 wherever it appears (paper, open_issues.md, story artifacts) and say instead what the authors decided.
2. Revise the paper accordingly into `.rcs/drafts/v004/paper.md` (tags kept), check
   `python rce/tools/claim_invariance.py .rcs/drafts/v003/paper.md .rcs/drafts/v004/paper.md` and make sure every change
   it reports is one an answer requires; then write the final manuscript without tags to `paper/paper.md`.
3. Run `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v004/paper.md --final paper/paper.md --before .rcs/drafts/v003/paper.md --edited .rcs/drafts/v004/paper.md`
   and report the effective gate statuses. G4 (the blind review covered v002) may now be stale: report it, do not fake it.
Reply DONE with: which claims changed and how, the invariance report summary, final word count, effective gates.
