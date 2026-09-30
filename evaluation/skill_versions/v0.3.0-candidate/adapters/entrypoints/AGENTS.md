# Research paper writing: Research Communication Engine

This file is the project context for agent runtimes. Codex CLI, Cursor, Amp and most agent CLIs read `AGENTS.md`.
Gemini CLI reads it when it is saved as `GEMINI.md`. Adjust `<RCE>` to where the skill lives.

For any task that writes, revises, reviews, shortens or presents a research paper from this project's evidence:

1. Read `<RCE>/skill/SKILL.md` and follow it. Its hard rules override style requests. Artifacts go in `./.rcs/`.
2. Run the deterministic gates yourself; never self-certify a gate:
   `python <RCE>/tools/run_workflow.py gates .rcs --project-root . --draft <draft>`.
3. Do not read `<RCE>/skill/agents/review_agent.md`, `recon_grader.md` or `skill_agent.md`. They belong to other roles.
4. Blind review (step 18):
   - build a packet: `python <RCE>/tools/build_review_packet.py <draft> --out .rcs/packets/review_<round> --audience .rcs/packets/audience.md --objective .rcs/packets/objective.md --strip-markers`;
   - then `python <RCE>/tools/rce_roles.py review --rcs .rcs --round <round>`.

   The reviewer model is bound in `.rcs/models.json`, and it must not be you, in this session.
5. When the skill says ASK or STOP and no person is present, open a checkpoint and keep the affected claims `BLOCKED`:
   `python <RCE>/tools/workflow_guard.py ask --rcs .rcs --id Q-00N --question "..." --blocks <claim ids>`.
   Never answer a checkpoint yourself.
6. Never cite from memory, never invent a number, and never state a claim stronger than its evidence licenses. The
   gates will reject it.
