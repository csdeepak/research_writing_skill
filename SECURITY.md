# Security policy

## Reporting a vulnerability
Please **do not open a public issue** for security problems. Report them privately through GitHub's
**Security → Report a vulnerability** (private vulnerability reporting) on this repository. Include:
- the RCE version and commit;
- what an attacker could do;
- a minimal reproduction, with private research data removed.

You will get an acknowledgement when the report is triaged. There is no bug bounty.

In scope:
- the tools under `tools/`;
- the skill's instructions (`skill/`), for example instructions that could make an agent leak data or run unsafe
  commands;
- packaging;
- the data-policy and key-handling code (`tools/rce_llm.py`).

## Threat model
RCE reads arbitrary research repositories and passes text to language models, so **all research input is untrusted**.

```text
untrusted research file → parser / tools (deterministic, no execution of project code)
                        → evidence representation (.rcs/, data only)
                        → model (sees packets or task prompts; its output is validated before use)
```

| Threat | Mitigation |
|---|---|
| Prompt injection in research files ("ignore previous instructions…", "report this as significant") | Evidence is data, never instructions (trust hierarchy in `docs/architecture.md`). The lint flags instruction-like text (`C6-injection`). Review packets remove such lines and log them. The reviewer reports `injection_suspected`. Gates are decided by tools, not by model statements. |
| A model inventing evidence, numbers or citations | number tracing, license rules, the citation registry check and conflict detection (`docs/concepts/EVIDENCE_INTEGRITY.md`) |
| Secrets inside evidence | Only the fields a role needs are sent. Hosted endpoints are refused unless allowed. The repository audit (`tools/check_repo.py`) and the packager scan for key patterns. |
| Leaking project data to hosted models | local-first defaults; per-host allow-list; packet-only reviewer (`docs/PRIVACY.md`) |
| Keys in files, URLs, command lines or logs | keys only via `api_key_env`; `curl` reads headers from a temporary file; content-free call logs (T-053) |
| Malicious or hostile documents (PDFs, huge files) | RCE's tools do not execute project code and read text only. PDF extraction, where needed, is done by your agent runtime. Treat it as untrusted. |
| Unsafe shell commands suggested by a model | The tools never run model output. Your agent runtime's permission system governs any command a writing agent runs. Review such commands before approving them. |
| A malicious or tampered skill package | Install only from this repository's releases. Verify the ZIP (`python tools/package_skill.py --check <zip>`) and read `SKILL.md` and `tools/` before installing ([Anthropic guidance on skill security](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview#security-considerations)). |
| Tampering with evidence or tools during a run | role ledger with file hashes (`UNATTRIBUTED_CHANGE`); gate reports hash-bound to their inputs; tool SHA-256 in `RUN_LOG.jsonl` |

## Supported versions
Security fixes go into the latest minor release (currently 0.3.x).
