#!/usr/bin/env python3
"""Uniform, logged, isolated model invocation for the external-validation study.

Providers
  claude      : `claude -p` headless, --tools "" (no file/web access), --setting-sources ""
                (no user/project settings or CLAUDE.md), run in an empty temp dir. Hard isolation.
  codex       : `codex exec -s read-only --ephemeral` in an empty temp dir; all content inline.
  openrouter  : HTTPS chat-completions call; the model only receives the prompt text.

Every call appends one JSON line to evaluation/logs/experiments.jsonl:
  exp_id, role, provider, model_requested, model_reported, started, ended, seconds, status,
  attempts, input_tokens, output_tokens, cost_usd, prompt_sha256, output_path, error

Usage
  python evaluation/harness/run_model.py --exp-id X --role reviewer --provider claude \
      --model opus --system sys.md --user user.md --out out.txt [--timeout 1800]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOG = ROOT / "evaluation" / "logs" / "experiments.jsonl"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def which(cmd: str) -> str:
    p = shutil.which(cmd)
    if not p:
        raise RuntimeError(f"{cmd} not found on PATH")
    return p


def call_claude(model: str, system: str, user: str, timeout: int) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        proc = subprocess.run(
            [which("claude"), "-p", "--model", model, "--tools", "", "--output-format", "json",
             "--no-session-persistence", "--setting-sources", "", "--system-prompt", system],
            input=user, capture_output=True, text=True, encoding="utf-8", cwd=tmp, timeout=timeout)
    if proc.returncode != 0 and not proc.stdout.strip():
        raise RuntimeError(f"claude exit {proc.returncode}: {proc.stderr[-500:]}")
    d = json.loads(proc.stdout)
    if d.get("is_error"):
        raise RuntimeError(f"claude error: {str(d.get('result'))[:300]}")
    u = d.get("usage", {})
    return {"text": d.get("result", ""), "model_reported": ",".join(d.get("modelUsage", {}).keys()),
            "input_tokens": u.get("input_tokens", 0) + u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0),
            "output_tokens": u.get("output_tokens"), "cost_usd": d.get("total_cost_usd")}


def call_codex(model: str, system: str, user: str, timeout: int) -> dict:
    prompt = f"<role_instructions>\n{system}\n</role_instructions>\n\n{user}\n\n" \
             "Do not run shell commands or read files; everything you need is above. " \
             "Reply with the requested output only."
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "last.txt"
        cmd = [which("codex"), "exec", "-s", "read-only", "--skip-git-repo-check", "--ephemeral",
               "-C", tmp, "-o", str(out)]
        if model and model != "default":
            cmd += ["-m", model]
        cmd.append("-")
        proc = subprocess.run(cmd, input=prompt, capture_output=True, text=True, encoding="utf-8",
                              cwd=tmp, timeout=timeout)
        text = out.read_text(encoding="utf-8") if out.exists() else ""
    blob = proc.stdout + "\n" + proc.stderr
    if not text.strip():
        raise RuntimeError(f"codex exit {proc.returncode}: {blob[-600:]}")
    m = re.search(r"^model:\s*(\S+)", blob, re.M)
    t = re.search(r"tokens used\s*\n?\s*([\d,]+)", blob)
    return {"text": text, "model_reported": m.group(1) if m else "codex-default",
            "input_tokens": None, "output_tokens": int(t.group(1).replace(",", "")) if t else None,
            "cost_usd": None}


def call_openrouter(model: str, system: str, user: str, timeout: int) -> dict:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not set")
    body = json.dumps({"model": model, "max_tokens": 32000,
                       "messages": [{"role": "system", "content": system},
                                    {"role": "user", "content": user}]}).encode()
    # curl rather than urllib: the local Python lacks a CA bundle. Key passed via header file.
    with tempfile.TemporaryDirectory() as tmp:
        hdr = Path(tmp) / "h.txt"
        hdr.write_text(f"Authorization: Bearer {key}\nContent-Type: application/json\n", encoding="utf-8")
        (Path(tmp) / "body.json").write_bytes(body)
        proc = subprocess.run(["curl", "-sS", "-m", str(timeout), "-H", f"@{hdr}", "--data-binary",
                               f"@{Path(tmp) / 'body.json'}", "https://openrouter.ai/api/v1/chat/completions"],
                              capture_output=True, timeout=timeout + 30)
    d = json.loads(proc.stdout.decode("utf-8"))
    if "error" in d:
        raise RuntimeError(f"openrouter error: {json.dumps(d['error'])[:400]}")
    u = d.get("usage", {})
    return {"text": d["choices"][0]["message"]["content"] or "", "model_reported": d.get("model"),
            "input_tokens": u.get("prompt_tokens"), "output_tokens": u.get("completion_tokens"),
            "cost_usd": u.get("cost")}


PROVIDERS = {"claude": call_claude, "codex": call_codex, "openrouter": call_openrouter}


def run(exp_id: str, role: str, provider: str, model: str, system: str, user: str, out: Path,
        timeout: int = 1800, retries: int | None = None) -> dict:
    if retries is None:
        retries = 5 if provider == "openrouter" else 3
    rec = {"exp_id": exp_id, "role": role, "provider": provider, "model_requested": model,
           "started": now(), "prompt_sha256": hashlib.sha256((system + "\n" + user).encode()).hexdigest(),
           "output_path": str(out.relative_to(ROOT)) if out.is_absolute() and ROOT in out.parents else str(out)}
    t0 = time.time()
    err = None
    for attempt in range(1, retries + 1):
        try:
            res = PROVIDERS[provider](model, system, user, timeout)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(res["text"], encoding="utf-8")
            rec.update(status="ok", attempts=attempt, **{k: v for k, v in res.items() if k != "text"})
            break
        except Exception as exc:  # noqa: BLE001 - record and retry
            err = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep((90 if provider == "openrouter" else 20) * attempt)
    else:
        rec.update(status="failed", attempts=retries, error=err)
    rec.update(ended=now(), seconds=round(time.time() - t0, 1))
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp-id", required=True)
    ap.add_argument("--role", required=True)
    ap.add_argument("--provider", choices=PROVIDERS, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--system", required=True)
    ap.add_argument("--user", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=1800)
    a = ap.parse_args()
    rec = run(a.exp_id, a.role, a.provider, a.model, Path(a.system).read_text(encoding="utf-8"),
              Path(a.user).read_text(encoding="utf-8"), Path(a.out).resolve(), a.timeout)
    print(json.dumps(rec))
    return 0 if rec["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
