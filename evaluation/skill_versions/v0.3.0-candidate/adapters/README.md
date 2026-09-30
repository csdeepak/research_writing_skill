# Running the skill on any model

The skill is model-agnostic by construction. It has three layers, and only the last one touches a model.

| Layer | What it is | Model dependence |
|---|---|---|
| 1. Rules | `SKILL.md`, `workflow.md`, `agents/*.md`, schemas: plain Markdown and JSON | none: any model that can read instructions |
| 2. Gates | `tools/*.py`: validator, lint, number tracing, visuals, G4, gate runner (stdlib Python ≥ 3.9) | **none**: deterministic checks that catch a weak model's mistakes the same way they catch a strong one's |
| 3. Roles | who writes what, each in its own context | bound per project, never named in the rules |

## Roles and where they run

| Role | Needs file tools? | Run it with |
|---|---|---|
| AUTHOR | yes | the agent runtime you are using: Claude Code, Codex CLI, Gemini CLI, Cursor, Aider, or any agent that can read/write files and run `python` |
| CORPUS_AGENT | yes | a second session or subagent of that runtime (Claude Code: `claude_code/agents/rce-corpus.md`) |
| REVIEW_AGENT | no (packet in, JSON out) | **any model** via `python tools/rce_roles.py review` (bindings in `.rcs/models.json`), or a runtime subagent |
| RECON_GRADER, READER | no | **any model** via `tools/rce_roles.py run-tasks` |

`tools/rce_llm.py` supports these providers:
- **OpenAI-compatible endpoints:** OpenAI, OpenRouter, Ollama, vLLM, LM Studio, llama.cpp server, Groq, Together.
- **APIs:** Anthropic and Gemini.
- **`command`:** any CLI that reads stdin, such as `ollama run`, `llm`, `claude -p`, `codex exec` or `gemini -p`.
- **`manual`:** paste the prompt into any chat UI and save the reply.

Start from `templates/models.json`. Its defaults point at a local server, so no project text leaves the machine.

## Setup in four steps
1. **Rules.** Make `SKILL.md` your agent's instructions. Copy `entrypoints/AGENTS.md` into the project root. Codex,
   Cursor, Amp and most agent CLIs read it. For Gemini CLI, also save it as `GEMINI.md`. Claude Code discovers the skill
   from its frontmatter (`claude_code.md`).
2. **Bindings.** `cp templates/models.json .rcs/models.json`, then bind REVIEW_AGENT, RECON_GRADER and READER.
   `python tools/rce_llm.py check --rcs .rcs` shows each binding and whether the data policy allows it.
3. **Calibrate the reviewer, once per reviewer model:** `python tools/rce_roles.py calibrate --rcs .rcs`.
   - It needs dimension sensitivity ≥ 0.90 and false alarms ≤ 0.10 on the planted-defect benchmark.
   - Reviews from an uncalibrated model are labelled in `reviewer_log.json`. Treat them as exploratory.
4. **Run.** Steps 1–17 run in your agent runtime. Step 18 is `python tools/build_review_packet.py ...`, then
   `python tools/rce_roles.py review --rcs .rcs --round <round>`. The gates are identical everywhere
   (`python tools/run_workflow.py gates ...`).

## Choosing models (capability, not brand)
- **REVIEW_AGENT:** your strongest reasoning model. A weak reviewer caps the whole loop, and calibration tells you
  whether yours is good enough. For release gates, use a reviewer from a different model family than the AUTHOR, to
  reduce same-model preference bias.
- **AUTHOR / CORPUS_AGENT:** a model that reliably follows long instructions and uses tools. Smaller models work
  because the gates catch invented numbers, unlicensed claims, broken attributions, mislabelled axes and bypassed
  checkpoints. Expect more gate failures and repair rounds.
- **READER / RECON_GRADER:** fast, capable models. Graders are checked by agreement (Krippendorff's α,
  `comprehension_kit.py`), not trusted.
- **JSON reliability:** `rce_llm` extracts JSON from fenced or chatty replies and sends validation errors back for a
  retry (`json_retries`). It retries rate limits and overloads with backoff (`transport_retries`, `retry_wait`).

## Data policy (enforced)
Hosted endpoints are refused until their host is listed in `data_policy.allowed_hosts`. Keys come only from the
environment variable named in `api_key_env`. They are never stored in the config, never put in a URL or on a command
line, and never logged. Every call is logged content-free to `.rcs/audits/llm_calls.jsonl`; transcripts stay local in
`.rcs/llm/`.

Runtime notes: `claude_code.md`, `codex.md`, `gemini.md`, `openai_compatible.md`, `local_models.md`.
