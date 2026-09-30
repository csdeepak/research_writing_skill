#!/usr/bin/env python3
"""Model-agnostic calls for the RCE's single-shot roles (REVIEW_AGENT, RECON_GRADER, READER, ...).

The skill never names a model. Each logical role is bound to a provider in `.rcs/models.json` (template:
templates/models.json). Roles that need file tools (CORPUS_AGENT, AUTHOR) run inside whatever agent runtime the user
has (see adapters/); roles that are "packet in, JSON out" run through this module with ANY model:

  provider "openai"     any OpenAI-compatible chat endpoint: OpenAI, OpenRouter, Ollama, vLLM, LM Studio, llama.cpp
                        server, Groq, Together, Azure-compatible gateways (set base_url)
  provider "anthropic"  Anthropic Messages API
  provider "gemini"     Google Gemini generateContent API
  provider "command"    any CLI that reads a prompt on stdin and prints the reply (ollama run, llm, claude -p,
                        codex exec, gemini -p, a local script)
  provider "manual"     writes the prompt to a file; you paste it into any chat UI and save the reply next to it
  provider "mock"       canned replies, for tests

Guarantees that do not depend on the model:
  * data policy: a role bound to a hosted endpoint is refused unless its host is listed in
    data_policy.allowed_hosts (loopback, command, manual and mock are local and always allowed)
  * API keys are read from the environment variable named in `api_key_env`; they are never stored in the config,
    never put in a URL or on a command line, and never logged
  * JSON roles are validated (schema and/or a check function); on failure the model gets the errors and retries
  * every call is logged content-free to .rcs/audits/llm_calls.jsonl (hashes, sizes, timing, validity);
    full transcripts are kept locally in .rcs/llm/ unless "keep_transcripts": false

CLI:  python tools/rce_llm.py check --rcs .rcs [--role REVIEW_AGENT]     show bindings + policy decision per role
      python tools/rce_llm.py ping  --rcs .rcs --role REVIEW_AGENT         one tiny call (sends a fixed test string)
"""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import shlex
import ssl
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import validate  # noqa: E402

LOCAL_PROVIDERS = {"command", "manual", "mock"}
DEFAULT_HOSTS = {"anthropic": "https://api.anthropic.com", "gemini": "https://generativelanguage.googleapis.com"}
MOCK_REPLIES: dict[str, list[str]] = {}          # role -> queued replies (tests)


class LLMError(RuntimeError):
    pass


class PolicyError(LLMError):
    pass


class ManualPending(LLMError):
    """The manual provider wrote a prompt and is waiting for the user to save a reply."""


# ------------------------------------------------------------------------------------------------ config
def load_config(rcs: Path | None = None, path: Path | None = None) -> dict:
    p = path or (rcs / "models.json" if rcs else None)
    if p is None or not p.exists():
        raise LLMError(f"no model configuration at {p}: copy templates/models.json to .rcs/models.json and bind the roles")
    cfg = json.loads(p.read_text(encoding="utf-8"))
    for role, rc in (cfg.get("roles") or {}).items():
        for secret in ("api_key", "key", "token"):
            if secret in rc:
                raise LLMError(f"roles.{role}.{secret}: never store keys in the config; use api_key_env")
    return cfg


def role_config(cfg: dict, role: str) -> dict:
    roles = cfg.get("roles") or {}
    rc = roles.get(role) or roles.get("default")
    if not rc:
        raise LLMError(f"role {role} is not bound in models.json (and there is no 'default')")
    return {"role": role, **rc}


def endpoint_host(rc: dict) -> str | None:
    if rc["provider"] in LOCAL_PROVIDERS:
        return None
    base = rc.get("base_url") or DEFAULT_HOSTS.get(rc["provider"])
    if not base:
        raise LLMError(f"role {rc['role']}: provider {rc['provider']} needs base_url")
    return (urllib.parse.urlparse(base).hostname or "").lower()


def _loopback(host: str) -> bool:
    if host in ("localhost",) or host.endswith(".localhost"):
        return True
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def check_policy(cfg: dict, rc: dict) -> str:
    """Return 'local' or the allowed host; raise PolicyError for a hosted endpoint that is not allowed."""
    host = endpoint_host(rc)
    if host is None or _loopback(host):
        return "local"
    allowed = {h.lower() for h in (cfg.get("data_policy") or {}).get("allowed_hosts", [])}
    if host not in allowed:
        raise PolicyError(f"role {rc['role']} would send project text to {host}, which is not in "
                          "data_policy.allowed_hosts in models.json. Add it only if this project's data may leave "
                          "the machine (see adapters/local_models.md, data policy).")
    return host


# --------------------------------------------------------------------------------------------- transport
def _ssl_context(rc: dict) -> ssl.SSLContext:
    ca = rc.get("ca_file") or os.environ.get("RCE_CA_FILE")
    return ssl.create_default_context(cafile=ca) if ca else ssl.create_default_context()


def http_post(url: str, headers: dict, body: dict, rc: dict) -> dict:
    """POST JSON. transport 'auto' (default) uses urllib and falls back to curl on TLS/CA problems (some Python builds
    ship without a CA bundle; corporate proxies re-sign TLS). Secrets travel only in headers (a temp header file for curl)."""
    data = json.dumps(body).encode("utf-8")
    timeout = int(rc.get("timeout", 600))
    transport = rc.get("transport", "auto")
    if transport in ("auto", "urllib"):
        req = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_ssl_context(rc)) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise LLMError(f"HTTP {exc.code} from {urllib.parse.urlparse(url).hostname}: {exc.read()[:400]!r}") from exc
        except (ssl.SSLError, urllib.error.URLError) as exc:
            if transport == "urllib" or ("CERTIFICATE" not in str(exc).upper() and "SSL" not in str(exc).upper()):
                raise LLMError(f"request to {urllib.parse.urlparse(url).hostname} failed: {exc}") from exc
    with tempfile.TemporaryDirectory() as tmp:
        hdr = Path(tmp) / "h.txt"
        hdr.write_text("".join(f"{k}: {v}\n" for k, v in {**headers, "Content-Type": "application/json"}.items()),
                       encoding="utf-8")
        (Path(tmp) / "b.json").write_bytes(data)
        proc = subprocess.run(["curl", "-sS", "-m", str(timeout), "-H", f"@{hdr}", "--data-binary", f"@{Path(tmp) / 'b.json'}",
                               url], capture_output=True, timeout=timeout + 30)
    if proc.returncode != 0:
        raise LLMError(f"curl exit {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')[:300]}")
    return json.loads(proc.stdout.decode("utf-8"))


def _key(rc: dict) -> str | None:
    env = rc.get("api_key_env")
    if not env:
        return None
    k = os.environ.get(env)
    if not k:
        raise LLMError(f"role {rc['role']}: environment variable {env} is not set")
    return k


# ---------------------------------------------------------------------------------------------- providers
def _openai(rc: dict, system: str, user: str) -> str:
    base = rc["base_url"].rstrip("/")
    body = {"model": rc["model"], "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "max_tokens": int(rc.get("max_tokens", 16000))}
    if "temperature" in rc:
        body["temperature"] = rc["temperature"]
    if rc.get("json_mode"):
        body["response_format"] = {"type": "json_object"}
    k = _key(rc)
    d = http_post(f"{base}/chat/completions", {"Authorization": f"Bearer {k}"} if k else {}, body, rc)
    if "error" in d:
        raise LLMError(f"provider error: {json.dumps(d['error'])[:400]}")
    return d["choices"][0]["message"].get("content") or ""


def _anthropic(rc: dict, system: str, user: str) -> str:
    base = (rc.get("base_url") or DEFAULT_HOSTS["anthropic"]).rstrip("/")
    body = {"model": rc["model"], "max_tokens": int(rc.get("max_tokens", 16000)), "system": system,
            "messages": [{"role": "user", "content": user}]}
    if "temperature" in rc:
        body["temperature"] = rc["temperature"]
    d = http_post(f"{base}/v1/messages", {"x-api-key": _key(rc) or "", "anthropic-version": "2023-06-01"}, body, rc)
    if d.get("type") == "error":
        raise LLMError(f"provider error: {json.dumps(d.get('error'))[:400]}")
    return "".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text")


def _gemini(rc: dict, system: str, user: str) -> str:
    base = (rc.get("base_url") or DEFAULT_HOSTS["gemini"]).rstrip("/")
    body = {"systemInstruction": {"parts": [{"text": system}]}, "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"maxOutputTokens": int(rc.get("max_tokens", 16000))}}
    if "temperature" in rc:
        body["generationConfig"]["temperature"] = rc["temperature"]
    if rc.get("json_mode"):
        body["generationConfig"]["responseMimeType"] = "application/json"
    d = http_post(f"{base}/v1beta/models/{urllib.parse.quote(rc['model'])}:generateContent",
                  {"x-goog-api-key": _key(rc) or ""}, body, rc)
    if "error" in d:
        raise LLMError(f"provider error: {json.dumps(d['error'])[:400]}")
    return "".join(p.get("text", "") for p in d["candidates"][0]["content"].get("parts", []))


def _command(rc: dict, system: str, user: str) -> str:
    cmd = rc["command"]
    argv = cmd if isinstance(cmd, list) else shlex.split(cmd)
    proc = subprocess.run(argv, input=f"{system}\n\n---\n\n{user}".encode("utf-8"), capture_output=True,
                          timeout=int(rc.get("timeout", 1800)))
    if proc.returncode != 0:
        raise LLMError(f"command exit {proc.returncode}: {proc.stderr.decode('utf-8', 'replace')[:300]}")
    return proc.stdout.decode("utf-8", "replace")


def _manual(rc: dict, system: str, user: str) -> str:
    d = Path(rc.get("dir", ".rcs/llm/manual")) / rc["role"] / hashlib.sha256((system + user).encode()).hexdigest()[:12]
    d.mkdir(parents=True, exist_ok=True)
    reply = d / "reply.md"
    if reply.exists() and reply.read_text(encoding="utf-8").strip():
        return reply.read_text(encoding="utf-8")
    (d / "prompt.md").write_text(f"# SYSTEM\n\n{system}\n\n# USER\n\n{user}\n", encoding="utf-8")
    raise ManualPending(f"paste {d / 'prompt.md'} into any chat model and save its reply as {reply}, then re-run")


def _mock(rc: dict, system: str, user: str) -> str:
    q = MOCK_REPLIES.get(rc["role"]) or MOCK_REPLIES.get("default")
    if not q:
        if rc.get("responses"):
            return rc["responses"].pop(0)
        raise LLMError(f"mock provider has no reply queued for {rc['role']}")
    r = q.pop(0)
    return r(system, user) if callable(r) else r


PROVIDERS: dict[str, Callable[[dict, str, str], str]] = {
    "openai": _openai, "anthropic": _anthropic, "gemini": _gemini, "command": _command, "manual": _manual, "mock": _mock}


# ----------------------------------------------------------------------------------------------- calling
TRANSIENT = ("429", "rate-limit", "rate limit", "rate_limit", "overloaded", "timed out", "timeout", "temporarily",
             "HTTP 500", "HTTP 502", "HTTP 503", "HTTP 504", "connection reset", "curl exit 28", "curl exit 52", "curl exit 56")


def _call(rc: dict, system: str, user: str, sleep=time.sleep) -> str:
    """One provider call, retrying transient failures (rate limits, overloaded or busy servers, timeouts) with a linear
    backoff. These retries are separate from JSON-repair attempts: a throttled call is not the model's mistake."""
    tries = 1 + int(rc.get("transport_retries", 4))
    for attempt in range(1, tries + 1):
        try:
            return PROVIDERS[rc["provider"]](rc, system, user)
        except (ManualPending, PolicyError):
            raise
        except (LLMError, OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
            msg = str(exc)
            transient = isinstance(exc, (subprocess.TimeoutExpired, json.JSONDecodeError)) or any(t.lower() in msg.lower() for t in TRANSIENT)
            if not transient or attempt == tries:
                raise LLMError(msg) if not isinstance(exc, LLMError) else exc
            sleep(float(rc.get("retry_wait", 30)) * attempt)
    raise LLMError("unreachable")


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _log(rcs: Path | None, rc: dict, system: str, user: str, reply: str, meta: dict, keep: bool) -> None:
    if rcs is None:
        return
    rec = {"at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "role": rc["role"], "provider": rc["provider"],
           "model": rc.get("model") or rc.get("command") and "command" or rc["provider"], "host": endpoint_host(rc) or "local",
           "prompt_sha256": _sha(system + "\n" + user), "prompt_chars": len(system) + len(user),
           "reply_sha256": _sha(reply), "reply_chars": len(reply), **meta}
    (rcs / "audits").mkdir(parents=True, exist_ok=True)
    with open(rcs / "audits" / "llm_calls.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    if keep:
        d = rcs / "llm" / rc["role"]
        d.mkdir(parents=True, exist_ok=True)
        stem = rec["at"].replace(":", "") + "_" + rec["prompt_sha256"][:8] + f"_a{meta.get('attempt', 1)}"
        (d / f"{stem}_prompt.md").write_text(f"# SYSTEM\n\n{system}\n\n# USER\n\n{user}\n", encoding="utf-8")
        (d / f"{stem}_reply.md").write_text(reply, encoding="utf-8")


def complete(cfg: dict, role: str, system: str, user: str, rcs: Path | None = None) -> str:
    rc = role_config(cfg, role)
    check_policy(cfg, rc)
    if rc["provider"] not in PROVIDERS:
        raise LLMError(f"unknown provider {rc['provider']!r} (known: {', '.join(PROVIDERS)})")
    t0 = time.time()
    reply = _call(rc, system, user)
    _log(rcs, rc, system, user, reply, {"seconds": round(time.time() - t0, 2), "attempt": 1, "kind": "text"},
         cfg.get("keep_transcripts", True))
    return reply


def extract_json(text: str):
    """First JSON value in a reply: tolerates code fences, prose before/after, and trailing text."""
    t = text.strip()
    if t.startswith("```"):
        t = t.split("\n", 1)[1] if "\n" in t else t
        t = t.rsplit("```", 1)[0]
    starts = [i for i in (t.find("{"), t.find("[")) if i >= 0]
    if not starts:
        raise ValueError("no JSON object in the reply")
    t = t[min(starts):]
    try:
        obj, _ = json.JSONDecoder().raw_decode(t)
    except json.JSONDecodeError:
        # common with smaller models: the reply stops before its last closing brackets. Complete ONLY the missing
        # closers (never change content); schema validation then decides whether the result is acceptable.
        obj, _ = json.JSONDecoder().raw_decode(t.rstrip() + _missing_closers(t.rstrip()))
    return obj


def _missing_closers(t: str) -> str:
    stack, in_str, esc = [], False, False
    for ch in t:
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
        elif ch == '"':
            in_str = True
        elif ch in "{[":
            stack.append("}" if ch == "{" else "]")
        elif ch in "}]" and stack:
            stack.pop()
    return ('"' if in_str else "") + "".join(reversed(stack))


def complete_json(cfg: dict, role: str, system: str, user: str, rcs: Path | None = None, schema: dict | None = None,
                  check: Callable[[object], list[str]] | None = None, retries: int | None = None,
                  normalize: Callable[[object], int] | None = None) -> tuple[object, dict]:
    """Call the role, parse JSON, validate; on failure send the errors back and retry (weaker models need this).
    `normalize` may fix purely cosmetic deviations before validation and returns how many it changed (reported in
    meta["normalized"]); it must never change substance (scores, findings, answers)."""
    rc = role_config(cfg, role)
    check_policy(cfg, rc)
    tries = 1 + (retries if retries is not None else int(rc.get("json_retries", 2)))
    prompt, history = user, []
    for attempt in range(1, tries + 1):
        t0 = time.time()
        reply = _call(rc, system, prompt)
        errors: list[str] = []
        obj = None
        normalized = 0
        try:
            obj = extract_json(reply)
            if normalize is not None:
                normalized = normalize(obj)
            if schema is not None:
                errors += validate(obj, schema)
            if check is not None:
                errors += check(obj)
        except ValueError as exc:
            errors = [f"not parseable as JSON: {exc}"]
        _log(rcs, rc, system, prompt, reply, {"seconds": round(time.time() - t0, 2), "attempt": attempt, "kind": "json",
                                              "valid": not errors, "n_errors": len(errors)}, cfg.get("keep_transcripts", True))
        history.append(len(errors))
        if not errors:
            return obj, {"attempts": attempt, "errors_per_attempt": history, "model": rc.get("model"), "provider": rc["provider"],
                         "normalized": normalized}
        prompt = (f"{user}\n\n---\nYour previous reply was:\n{reply[:20000]}\n\n---\nIt failed validation:\n- "
                  + "\n- ".join(errors[:25]) + "\n\nReply again with ONE corrected JSON value only, no other text.")
    raise LLMError(f"role {role}: no valid JSON after {tries} attempts; last errors: {errors[:5]}")


# ---------------------------------------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["check", "ping"])
    ap.add_argument("--rcs", default=".rcs")
    ap.add_argument("--config")
    ap.add_argument("--role")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    cfg = load_config(rcs, Path(a.config) if a.config else None)
    roles = [a.role] if a.role else sorted(cfg.get("roles") or {})
    rc_code = 0
    for role in roles:
        rc = role_config(cfg, role)
        try:
            where = check_policy(cfg, rc)
            status = f"OK ({where})"
        except PolicyError as exc:
            status, rc_code = f"REFUSED: {exc}", 1
        print(f"{role:14s} {rc['provider']:9s} {rc.get('model') or rc.get('command') or '':40s} {status}")
        if a.cmd == "ping" and status.startswith("OK"):
            print("   reply:", complete(cfg, role, "Reply with the single word: ready", "ping", rcs).strip()[:80])
    return rc_code


if __name__ == "__main__":
    sys.exit(main())
