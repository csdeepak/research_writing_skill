# Installing and running RCE

RCE needs **Python ≥ 3.9** (standard library only) for its tools, plus any model you choose for the writing and review
roles. Platform instructions were checked against official documentation on 2026-09-30. User interfaces change, so
re-check the linked pages if a step does not match.

## 1. From Git (developers, any model)
```bash
git clone https://github.com/csdeepak/research_writing_skill.git
cd research_writing_skill
python -m unittest discover -s tools/tests          # the full test suite
python tools/rce.py check examples/synthetic_project --draft examples/synthetic_project/drafts/flawed.md
```
Your agent's instructions are `skill/SKILL.md`. For agent CLIs that read `AGENTS.md` (Codex, Cursor, Amp, …), copy
`skill/adapters/entrypoints/AGENTS.md` into your research project's root and adjust `<RCE>` to this checkout. For
Gemini CLI, save the same file as `GEMINI.md`.

## 2. Claude Code
Skills in Claude Code are folders containing `SKILL.md` under `~/.claude/skills/` (personal) or `.claude/skills/`
(project); no upload is needed ([Anthropic: Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)).
Unzip the release asset `research-communication-engine-v<version>.zip` there. It contains the folder
`research-communication-engine/` with `SKILL.md` and `tools/`. Optional role subagents are in
`skill/adapters/claude_code/agents/`.

## 3. Claude apps (claude.ai)
Custom skills are uploaded as a ZIP whose top-level folder contains `SKILL.md`, and the folder name must match the
skill's `name` ([How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills),
[Use skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude)). According to those pages
(verified 2026-09-30):
1. Download `research-communication-engine-v<version>.zip` from the GitHub release (or build it:
   `python tools/package_skill.py`).
2. In Claude, open **Customize → Skills**, choose **+** and then **Upload a skill**, and select the ZIP.
3. Skills require **code execution** to be enabled. On individual plans: Settings → Capabilities. On Team/Enterprise:
   organisation settings.

Custom skills uploaded to claude.ai are individual to each user. They do not sync to the API or to Claude Code.

## 4. ChatGPT (OpenAI)
OpenAI documents skills for ChatGPT at
[help.openai.com/en/articles/20001066-skills-in-chatgpt](https://help.openai.com/en/articles/20001066-skills-in-chatgpt).
That page could not be retrieved automatically when this guide was written, so the following is **UNVERIFIED**:
- If your ChatGPT product, plan and workspace support uploading skills, the same ZIP (Agent Skills format: a folder
  with `SKILL.md` and supporting files) is the candidate package.
- Availability varies by product, plan and workspace. Check the page above before relying on it, and report what you
  find in an issue.

## 5. Any model, without installing a runtime (manual mode)
1. Your writing agent follows `skill/SKILL.md`. Any chat model can read it.
2. Run the deterministic checks locally: `python tools/rce.py check <project> --draft <draft>`.
3. For the blind review, bind `REVIEW_AGENT` to `{"provider": "manual"}` in `.rcs/models.json`. Then run
   `python tools/rce_roles.py review --rcs .rcs --round <round>`. It writes a prompt file; paste it into any chat
   model, save the reply next to it as `reply.md`, and run the command again. The reply is validated and recorded
   exactly like an API call.

## 6. Any model through an API
Copy `skill/templates/models.json` to `<project>/.rcs/models.json` and bind the single-shot roles:
- OpenAI-compatible: OpenAI, OpenRouter, Ollama, vLLM, LM Studio, llama.cpp server, Groq, Together;
- Anthropic; Gemini;
- any CLI (`command`).

Put keys in environment variables (`.env.example`). Hosted hosts must be listed in `data_policy.allowed_hosts`. Then
calibrate your reviewer model once:
```bash
python tools/rce_llm.py check --rcs .rcs
python tools/rce_roles.py calibrate --rcs .rcs      # needs sensitivity >= 0.90 and false alarms <= 0.10
```
Details: `skill/adapters/README.md`.
