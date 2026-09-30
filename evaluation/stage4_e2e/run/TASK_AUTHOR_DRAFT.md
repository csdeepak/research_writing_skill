# Role: AUTHOR (steps 3-17)
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

The CORPUS role has already built `.rcs/evidence/` and `.rcs/claims/claim_candidates.json`; do not edit them (if you
find an evidence problem, record a checkpoint or note it in `.rcs/open_issues.md`).
TASK: write a research paper presenting this project to machine-learning researchers from other subfields (audience
mode B), 3,000-4,500 words of main text, Markdown, following `rce/skill/SKILL.md` workflow steps 3-17 with the v0.3
truth guardrail (`state.json` already has `"guardrail": "v0.3"`), including:
- claim map with `basis`, `status`, and `licenses` for any licensed wording (significant, outperforms, generalizes, ...);
- `.rcs/plan/reader_model.json` for persona B (templates/reader_model.json) and `python rce/tools/audit_reader.py`;
- figures only through `.rcs/plan/visual_registry.json` from real project data (`python rce/tools/plan_visuals.py .rcs`
  first; re-typed values go into a CSV you write under `.rcs/plan/data/` with `data.source_text` pointing to the project
  file they come from); `python rce/tools/visuals.py render .rcs --project-root .`;
- a skim sheet (`python rce/tools/skim_layer.py build .rcs`) and `check` of your abstract;
- the gates: `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v001/paper.md`; fix and
  re-run until G1, G3, V1-V4 and V6 pass, or record in `.rcs/open_issues.md` exactly which gate fails and why.
Write the draft to `.rcs/drafts/v001/paper.md` (claim tags kept), `.rcs/packets/audience.md` and `.rcs/packets/objective.md`
(templates/packet_audience_objective.md), then build the blind review packet:
`python rce/tools/build_review_packet.py .rcs/drafts/v001/paper.md --out .rcs/packets/review_v001_1 --audience .rcs/packets/audience.md --objective .rcs/packets/objective.md --strip-markers`
Record everything you wrote as role AUTHOR. Reply DONE with the word count and the effective gate statuses.
