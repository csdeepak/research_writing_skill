# Adapter: Claude Code

## Install
- Copy or symlink `skill/` to `~/.claude/skills/research-communication-engine/` (user level) or
  `<project>/.claude/skills/research-communication-engine/` (project level). The frontmatter in
  `SKILL.md` makes it discoverable.
- Copy `tools/` next to it, or keep this repo checked out and call the tools by absolute path.
- Install the subagents: copy `adapters/claude_code/agents/*.md` to `<project>/.claude/agents/`
  (or `~/.claude/agents/`). They reference the prompts in `skill/agents/`.

## Role mapping
Model names below are this runtime's bindings, not requirements of the skill (see `README.md`).
| Logical role | Claude Code mechanism |
|--------------|-----------------------|
| AUTHOR | The main session running the skill |
| CORPUS_AGENT | Subagent `rce-corpus` (model: sonnet; tools: Read, Glob, Grep, Bash, WebSearch, WebFetch, Write) |
| REVIEW_AGENT | Subagent `rce-reviewer` (model: opus; tools: Read, Write, restricted to the packet dir by instruction) for soft isolation. For hard isolation, a headless run (below). |
| SKILL_AGENT | Subagent `rce-skill-architect` (model: opus) |
| RECON_GRADER | Subagent `rce-grader` (model: sonnet; tools: Read, Write) |

Subagents start with a fresh context and see only their own system prompt plus the task
message. AUTHOR must pass only the packet path to `rce-reviewer`, never excerpts of the claim
map, sources, or scores.

## Hard isolation (benchmarks, release gates)
Run the reviewer as a separate headless process whose working directory is the packet:

```bash
cd .rcs/packets/review_v002_1 && claude -p "$(cat /path/to/skill/agents/review_agent.md) Review the packet in the current directory. Write diagnostics.json, reconstruction.json, reviewer_notes.private.md here." --model opus --allowedTools "Read,Write"
```

Check the flag names with `claude --help` for your version. Afterwards, confirm that the packet
directory contains only the expected outputs. Write access outside it would be an
`ISOLATION_BREACH`.

## Tool policy
- Filesystem inspection: Read/Glob/Grep. PDFs: Read with page ranges, or `pdftotext` if it's
  available.
- Literature: WebSearch/WebFetch, or scholarly MCP servers if they're configured. Verify every
  DOI.
- Quantitative checks: run Python on the result files (never compute numbers "in your head").
- Validation: `python tools/validate_artifacts.py .rcs` and `python tools/lint_draft.py …`
  after each step.

## Alternative: any model for the single-shot roles
The reviewer, grader and readers do not have to be Claude models. Bind them in `.rcs/models.json` (`templates/models.json`)
and run `python tools/rce_roles.py review|calibrate|run-tasks`. For release gates, a reviewer from a different model
family than the AUTHOR reduces same-model preference bias.
