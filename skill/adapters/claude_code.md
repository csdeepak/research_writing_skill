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
| VERIFIER | Subagent `rce-verifier` (model: opus; tools: Read, Glob, Grep, Bash, Write). Writes only the verifier report. |
| PANEL (field analyst, five seats, synthesizer) | Subagent `rce-panel`, one fresh invocation per member and phase (model: opus; tools: Read, Write). Dispatch the five commitments before any review, and the reviews before the synthesizer. |
| COACH | Subagent `rce-coach` (model: sonnet; tools: Read). Questions only. |
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

## The panel through subagents
Run the panel in this order, each step in a fresh `rce-panel` invocation:
1. the field analyst writes `panel/cards.json`
2. each seat writes its `panel/<seat>.commitment.json`, without opening the paper. Hash every commitment now, before
   any seat sees the paper
3. each seat writes its `panel/<seat>.review.json`. Check that each commitment still has its recorded hash, then add
   it to the review as `commitment_sha256`, with the packet id as `packet_id`
4. the synthesizer writes `editorial_decision.json`

Then run `python tools/panel_check.py .rcs --round <round>`. It fails a review that was not made against the commitment
on disk, and a decision the findings do not give. Subagent isolation is soft: a seat that could read another seat's
report is not blind. Label that in `open_issues.md`, or run the panel through `rce_roles.py panel` instead.

**Rebuttals** (step 18): a fresh invocation of the devil's-advocate seat reads only the rebutted findings, the
AUTHOR's `revisions/<round>/rebuttals.json` and the packet's `paper.md`, and writes
`panel/devils_advocate.rebuttal.json`.

**Round 2** (verification): copy `panel/cards.json` unchanged into the new round. Write the previous round's
`roadmap` list alone to the new round's `panel/previous_roadmap.json`, and give the seats that file, not
`editorial_decision.json`. The decision also carries the other seats' merged findings and dissent, and a file reader
returns the whole file. Then five fresh seat invocations write `panel/<seat>.verification.json`, and the synthesizer
writes the round's `editorial_decision.json` with `kind: "verification"` and `previous_round`.

## Alternative: any model for the single-shot roles
The reviewer, grader, readers, panel and VERIFIER do not have to be Claude models. Bind them in `.rcs/models.json`
(`templates/models.json`) and run `python tools/rce_roles.py review|calibrate|run-tasks|panel|rebut|verify`. For release
gates, a reviewer from a different model family than the AUTHOR reduces same-model preference bias.
