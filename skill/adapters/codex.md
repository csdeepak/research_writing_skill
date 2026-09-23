# Adapter: OpenAI Codex CLI

## Install
- Keep this repo available in the workspace, or copy `skill/` and `tools/` into the project.
- Add to the project's `AGENTS.md`: *"For research-paper writing tasks, follow
  `skill/SKILL.md` (Research Communication Engine). Artifacts go in `.rcs/`."* If your Codex
  version supports skills directories, install `skill/` there instead. Check the current Codex
  docs.

## Role mapping
| Logical role | Mechanism |
|--------------|-----------|
| AUTHOR | The interactive Codex session |
| CORPUS_AGENT / SKILL_AGENT / RECON_GRADER | Separate non-interactive runs: `codex exec "<contents of skill/agents/<role>.md> <task>"` in the project directory |
| REVIEW_AGENT | A separate `codex exec` run **with the working directory set to the packet** and a read-only sandbox where possible |

Example (check `codex exec --help` for the current flag names):

```bash
cd .rcs/packets/review_v002_1 && codex exec "$(cat /path/to/skill/agents/review_agent.md) Review the packet in the current directory and write the output files here."
```

## Notes
- Separate `exec` runs don't share conversation context. That is the isolation mechanism, so
  never paste reviewer outputs other than `diagnostics.json`/`reconstruction.json` back into
  AUTHOR's session.
- If web search is disabled in your configuration, CORPUS_AGENT(literature) must be run where
  search is available, or the user must supply the sources. Otherwise raise
  `INSUFFICIENT_LITERATURE`. Never fall back to citations from memory.
