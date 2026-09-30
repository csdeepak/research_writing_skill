# Role: CORPUS_AGENT (steps 1-2 only)
Your working directory for this entire task is `C:/Users/csdee/AppData/Local/Temp/rce_ws/ASMOS_e2e`. Use absolute paths under it. Hard rules: never read, list,
search or write anything outside that directory; do not use the web; do not spawn agents; you may run `python` on the
tools in `C:/Users/csdee/AppData/Local/Temp/rce_ws/ASMOS_e2e/rce/tools/`. Do NOT read `rce/skill/agents/review_agent.md`, `recon_grader.md` or `skill_agent.md`.
No human is available during this run: wherever the skill says ASK or STOP, create a checkpoint
(`python rce/tools/workflow_guard.py ask --rcs .rcs --id Q-00N --question "..." --blocks <claim ids>`) and keep the
blocked claims `status: BLOCKED` and out of the paper. NEVER answer a checkpoint yourself. Accepted risks in
`.rcs/state.json` must have `"kind": "workflow"` (never license a fact). Evidence locator paths are relative to the
working directory, e.g. `project/results/summary.csv`.
After writing or changing any artifact, record it for your role:
`python rce/tools/workflow_guard.py record --rcs .rcs --role CORPUS <files...>`.

Read `rce/skill/SKILL.md` (hard rules and the "Truth guardrail" section), `rce/skill/agents/corpus_agent.md` and
`rce/skill/evidence_model.md` (including section 8). Then perform workflow steps 1-2 on `project/`:
- `.rcs/evidence/project_inventory.json`, `.rcs/evidence/research_evidence.json`, `.rcs/evidence/missing_evidence.json`,
  `.rcs/claims/claim_candidates.json`. You may write ONLY those (and `.rcs/corpus/` if needed).
- Be alert: some documents are stale. A document that says it is archived or superseded must not be used as the source
  of numbers (mark such items `status: superseded` with a note). `project/data/results/CORRECTIONS.md` records superseded
  values: keep both, mark the superseded one, and give conflicting values `quantity`/`conflicts_with`/`resolution`.
- Give each numeric item a `quantity` (or metric + conditions + `run_id`). Different runs with different conditions are
  not conflicts; the same quantity with different values is.
- Before finishing, `python rce/tools/validate_artifacts.py .rcs --project-root .` must show 0 errors for your artifacts
  (errors about artifacts other roles have not written yet are expected only if they refer to those files).
Reply DONE with the number of evidence items, conflicts found, superseded items, and checkpoints asked.
