# Prompt for the next session

Paste everything inside the fence below into a new Claude Code session on the new machine. Start
the session in an empty working folder.

```text
I'm continuing a build that was designed in an earlier session on another machine. The full plan is
already written; your job is to set up, confirm a few decisions with me, then build it stage by stage.

SET UP
1. Clone my repo and switch to the work branch:
     git clone https://github.com/csdeepak/research_writing_skill
     cd research_writing_skill
     git checkout rce-unified-workflow
2. Read docs/plans/UNIFIED_WORKFLOW_HANDOFF.md completely before doing anything else. It is the
   source of truth: the research findings, the unified 8-phase workflow, roles, the mode registry,
   what to leave out, the staged build plan, the engineering rules and the decisions to confirm.
3. Clone the third-party Academic Research Skills (ARS) repo NEXT TO this repo (never inside it),
   pinned to the commit that was studied:
     git clone https://github.com/Imbad0202/academic-research-skills ../academic-research-skills
     git -C ../academic-research-skills checkout a41f3b28bbde77e6537d5a141665d0c8475e1fe1
4. Check the environment: python --version (needs 3.9+), git and gh auth status. Then run the
   baseline checks from .github/workflows/ci.yml and tell me whether they pass before you change
   anything:
     python -m unittest discover -s tools/tests
     python tools/replay_fixtures.py
     python tools/validate_cases.py
     python tools/validate_artifacts.py --check-skill
     python tools/check_repo.py

BEFORE BUILDING
5. Ask me the open decisions in section 8 of the handoff, in one batched question, with the
   defaults shown. My "adaptive representation" update is already merged into this branch (section
   0.4 of the handoff): build on top of it and keep everything it adds.

RULES
- Read ARS for design only. Don't copy its text, prompts, tables or code: ARS is CC BY-NC 4.0 and
  this repo is Apache-2.0. Write everything fresh in this repo's own style and credit ARS as a
  design source.
- RCE is the spine; ARS capabilities slot into it as described in the handoff. All memory lives in
  .rcs/ artifacts; gates are only "passed" with a fresh, clean tool report.
- New tools are stdlib-only Python 3.9+, network calls only behind --online, and tests mock the
  network (CI must stay offline and need no keys). No absolute local paths or broken relative links
  in docs/, skill/, tools/, examples/ or cases/ (tools/check_repo.py enforces this).
- Work only on the rce-unified-workflow branch. Commit at the end of every stage and update the
  Progress log at the bottom of the handoff file in the same commit, so the work can be handed off
  again at any time. Push after each stage. Open the PR to main only at Stage E.

BUILD
6. Build Stage A, then stop and show me the result (what changed, which checks pass, anything not
   verified) before starting Stage B. Repeat for each stage through Stage E.
```
