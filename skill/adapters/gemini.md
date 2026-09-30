# Adapter: Google Gemini (Gemini CLI or API)

## Gemini CLI
- Add to the project's context file (`GEMINI.md`): *"For research-paper tasks, follow
  `skill/SKILL.md` (Research Communication Engine)."*
- Run the other roles as separate non-interactive invocations (e.g. `gemini -p "<role prompt +
  task>"`, but check `gemini --help` for your version), started from the directory each role
  may see. For REVIEW_AGENT that is the packet directory.

## Gemini API
Follow `openai_compatible.md`: one fresh conversation per role invocation, with the system
instruction set to the role file and the inputs passed explicitly. Use the API's JSON output
mode with the role's schema, then re-validate locally.

## Notes
- Long-context models make it tempting to paste the whole project into every call. Don't. The
  isolation boundaries (who sees what) matter more than the context budget, and the reviewer
  must never receive project files.
- Search grounding, where available, counts as a *discovery* tool. Every source it returns must
  still pass the verification step in `citation_rules.md` before registration.

## Single-shot roles through the skill's tools
Bind REVIEW_AGENT, RECON_GRADER and READER in `.rcs/models.json` with `"provider": "gemini"` (API key in
`GEMINI_API_KEY`, host `generativelanguage.googleapis.com` in `data_policy.allowed_hosts`), or with
`"provider": "command", "command": ["gemini", "-p", "-"]`. Then run `python tools/rce_roles.py calibrate` and `review`.
For project context, save `entrypoints/AGENTS.md` as `GEMINI.md`.
