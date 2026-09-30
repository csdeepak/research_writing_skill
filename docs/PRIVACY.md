# Privacy

RCE is local-first. By default, research data stay on your machine.

```text
research data → local files (.rcs/)            always
research data → deterministic tools (tools/)    always, locally
research data → a model                         only when you invoke a role bound to that model
```

- **No telemetry.** RCE sends nothing anywhere by itself. `tools/rce_diagnostics.py` is opt-in (`--opt-in`), stores
  counts only (no text, numbers or paths), and writes to a local file.
- **Model endpoints are opt-in per host.** The template `skill/templates/models.json` binds every role to a local
  server (`localhost`). A hosted endpoint (OpenAI, OpenRouter, Anthropic, Gemini, …) is **refused** until you list its
  host in `data_policy.allowed_hosts` in your project's `.rcs/models.json` (`tools/rce_llm.py`, T-052).
- **What a role sends.** The blind reviewer, graders and readers receive only their packet or task prompt (the paper
  text, figures, audience and objective), never raw project files, the evidence map or notes
  (`tools/rce_roles.py`, `tools/build_review_packet.py`). The writing agent (AUTHOR/CORPUS) runs in the agent runtime
  you choose, which applies that runtime's own data handling.
- **Keys.** API keys are read from the environment variable named in `api_key_env`. They are never stored in config
  files, never placed in URLs or command lines, and never logged. `.env` files are git-ignored; see `.env.example`.
- **Logs.** `.rcs/audits/llm_calls.jsonl` records hashes, sizes and timing, not content. Transcripts are kept locally
  in `.rcs/llm/` (disable with `"keep_transcripts": false`). Nothing under `.rcs/` of a real project is committed by
  this repository's `.gitignore`.
- **Before sharing an artifact** (an issue, a failure case, a fixture), remove private data. Failure cases can be
  synthetic reproductions; see `CONTRIBUTING.md`.

This repository practises the same policy. The author's own unpublished project, used in the end-to-end evaluation,
is kept out of the public tree, and third-party paper texts are recreated from their original sources rather than
redistributed (`docs/OPEN_SOURCE_MIGRATION_ASSESSMENT.md`).
