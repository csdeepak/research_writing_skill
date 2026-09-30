# Adapter: OpenAI-compatible chat APIs (hosted or self-hosted)

This covers OpenAI, OpenRouter, Groq, Together and Azure-compatible gateways, and every local server that exposes
`/v1/chat/completions`: Ollama, vLLM, LM Studio, the llama.cpp server and text-generation-webui.

## Single-shot roles: no code to write
Bind the roles in `.rcs/models.json`. Start from `templates/models.json`.

```json
{"roles": {"REVIEW_AGENT": {"provider": "openai", "base_url": "https://api.openai.com/v1", "model": "<model id>",
                            "api_key_env": "OPENAI_API_KEY", "temperature": 0, "json_mode": true}},
 "data_policy": {"allowed_hosts": ["api.openai.com"]}}
```

Then:
- `python tools/rce_llm.py check --rcs .rcs` shows the bindings and the policy decision.
- `python tools/rce_roles.py calibrate --rcs .rcs` calibrates the reviewer model, once.
- `python tools/rce_roles.py review --rcs .rcs --round v002_1` runs step 18 on a packet.

Each call is **one fresh conversation**: the system message is the role file, and the user message is the schemas
plus the packet files. There is no shared history between roles. The only shared state is the `.rcs/` files the
tool passes explicitly. The reply is parsed, validated against the schemas and repaired by retry if needed. JSON mode
helps, but the tool re-validates anyway, because JSON mode doesn't guarantee schema conformance.

## AUTHOR and CORPUS_AGENT
These roles need file reading and `python`. Run them in an agent runtime that uses this endpoint, for example Codex
CLI, Aider or any agent framework, with `adapters/entrypoints/AGENTS.md` as the project context. If you orchestrate
them from your own script instead, implement a file-read tool and a `python` tool. CORPUS_AGENT also needs a search
function and a DOI resolver (e.g. the Crossref REST API). Without these, literature mode stops with
`INSUFFICIENT_LITERATURE` rather than generating references.

## Transport
`rce_llm` uses Python's `urllib`. If TLS fails, for example on a Python build without a CA bundle or behind a
re-signing proxy, it falls back to `curl` automatically, with the key in a temporary header file. Set `ca_file`, or
`RCE_CA_FILE`, to use a specific CA bundle.
