#!/usr/bin/env python3
"""Role separation and human checkpoints (vNext Stage 4: M15; spec 4.3 fail-closed).

Roles (logical, adapters/agent_config.yaml): CORPUS, AUTHOR, REVIEW, GRADER, HUMAN. Each may write only its own
artifacts (ROLE_WRITE below). After writing, a role records what it wrote in the append-only ledger
.rcs/provenance.jsonl (role, path, sha256, time). The validator then checks:

  ROLE_VIOLATION           a role recorded a file it may not write (e.g. the reviewer editing the claim map)
  UNATTRIBUTED_CHANGE      an artifact's current content matches no ledger record (edited outside any role)
  CHECKPOINT_BYPASSED      a claim blocked by an unanswered human checkpoint is not status BLOCKED
  ACCEPTED_RISK_FACTUAL    an accepted risk licenses a factual claim; unattended runs may accept workflow
                           risks only -- missing facts are omitted or blocked, never invented (spec 4.3)
  (WARN) ACCEPTED_RISK_UNTYPED  an accepted risk has no kind (workflow|factual)

Checks are opt-in: the role checks run once .rcs/provenance.jsonl exists; checkpoint checks once
.rcs/checkpoints/pending.json exists.

CLI
  record  --rcs .rcs --role AUTHOR <files...>                      append ledger records
  ask     --rcs .rcs --id Q-001 --question "..." [--blocks C003,C007] [--options "a|b"] [--consequence "..."]
  answer  --rcs .rcs --id Q-001 --answer "..." --by "Name"          (a person, never the agent)
  status  --rcs .rcs                                                exit 3 while a blocking question is open
"""
from __future__ import annotations

import argparse
import getpass
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROLE_WRITE = {
    "CORPUS": ["evidence/", "corpus/", "claims/claim_candidates.json"],
    "AUTHOR": ["story/", "claims/claim_evidence_map.json", "plan/", "drafts/", "audits/", "packets/", "revisions/",
               "evaluation/comprehension_key.json", "comprehension_runs/", "state.json", "open_issues.md", "config.yaml",
               "checkpoints/pending.json", "evidence/missing_evidence.json", "../paper/"],
    "REVIEW": ["diagnostics/"],
    "GRADER": ["evaluation/grading", "comprehension_runs/grades"],
    "HUMAN": ["checkpoints/answers.json", "plan/visual_registry.json", "plan/reader_model.json", "claims/claim_evidence_map.json",
              "state.json"],
}
TRACKED = ("evidence/", "corpus/", "claims/", "story/", "plan/", "drafts/", "diagnostics/", "revisions/")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def rel(rcs: Path, p: Path) -> str:
    """Ledger path: relative to .rcs; the final manuscript lives beside it (../paper/...). Anything else stays absolute,
    and absolute paths are never in ROLE_WRITE, so recording one is a ROLE_VIOLATION rather than a crash."""
    p, r = p.resolve(), rcs.resolve()
    for base, prefix in ((r, ""), (r.parent, "../")):
        try:
            return prefix + str(p.relative_to(base)).replace("\\", "/")
        except ValueError:
            continue
    return str(p).replace("\\", "/")


def allowed(role: str, path: str) -> bool:
    return any(path == a or path.startswith(a) for a in ROLE_WRITE.get(role, []))


def load_ledger(rcs: Path) -> list[dict]:
    p = rcs / "provenance.jsonl"
    if not p.exists():
        return []
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def record(rcs: Path, role: str, files: list[str]) -> list[dict]:
    if role not in ROLE_WRITE:
        raise SystemExit(f"unknown role {role}; roles: {', '.join(ROLE_WRITE)}")
    recs = []
    with open(rcs / "provenance.jsonl", "a", encoding="utf-8") as fh:
        for f in files:
            p = Path(f) if Path(f).is_absolute() or Path(f).exists() else rcs / f
            r = {"role": role, "path": rel(rcs, p), "sha256": sha(p), "at": now()}
            fh.write(json.dumps(r) + "\n")
            recs.append(r)
    return recs


# ------------------------------------------------------------------------------ checkpoints
def _cp(rcs: Path, name: str) -> dict:
    p = rcs / "checkpoints" / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"questions": []}


def ask(rcs: Path, qid: str, question: str, blocks: list[str], options: list[str], consequence: str) -> dict:
    d = _cp(rcs, "pending.json")
    d["questions"] = [q for q in d["questions"] if q["id"] != qid] + [{
        "id": qid, "question": question, "blocks_claims": blocks, "options": options, "consequence": consequence,
        "asked_at": now(), "blocking": bool(blocks)}]
    (rcs / "checkpoints").mkdir(parents=True, exist_ok=True)
    (rcs / "checkpoints" / "pending.json").write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    return d


def answer(rcs: Path, qid: str, text: str, by: str) -> dict:
    if qid not in {q["id"] for q in _cp(rcs, "pending.json")["questions"]}:
        raise SystemExit(f"no pending question {qid}")
    d = _cp(rcs, "answers.json")
    d["questions"] = [q for q in d["questions"] if q["id"] != qid] + [{
        "id": qid, "answer": text, "answered_by": by, "os_user": getpass.getuser(), "answered_at": now()}]
    (rcs / "checkpoints" / "answers.json").write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    return d


def open_questions(rcs: Path) -> list[dict]:
    answered = {q["id"] for q in _cp(rcs, "answers.json")["questions"]}
    return [q for q in _cp(rcs, "pending.json")["questions"] if q["id"] not in answered]


# ------------------------------------------------------------------------------- validator
def run(rcs: Path, root: Path, loaded: dict, rep) -> None:
    ledger = load_ledger(rcs)
    if ledger:
        for r in ledger:
            if not allowed(r.get("role", ""), r.get("path", "")):
                rep.add("ERROR", f"provenance/{r.get('path')}", f"role {r.get('role')} may not write {r.get('path')} (ROLE_VIOLATION)")
        known = {(r["path"], r["sha256"]) for r in ledger if "sha256" in r}
        for p in sorted(rcs.rglob("*")):
            if not p.is_file():
                continue
            rp = rel(rcs, p)
            if rp.startswith(TRACKED) and (rp, sha(p)) not in known:
                rep.add("WARN", rp, "current content matches no role's ledger record (UNATTRIBUTED_CHANGE): "
                                    "record it with tools/workflow_guard.py record --role <ROLE>")
    if (rcs / "checkpoints" / "pending.json").exists():
        cm = loaded.get("claims/claim_evidence_map.json") or {}
        opened = open_questions(rcs)
        for q in opened:
            for cid in q.get("blocks_claims", []):
                c = next((c for c in cm.get("claims", []) if c.get("id") == cid), None)
                if c and c.get("status") != "BLOCKED":
                    rep.add("ERROR", f"claims/{cid}", f"blocked by open checkpoint {q['id']} ({q['question'][:60]}...) but "
                                                      f"status is {c.get('status')!r} (CHECKPOINT_BYPASSED)")
    state = {}
    if (rcs / "state.json").exists():
        try:
            state = json.loads((rcs / "state.json").read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    for i, r in enumerate(state.get("accepted_risks", []) or []):
        kind = r.get("kind") if isinstance(r, dict) else None
        if kind == "factual":
            rep.add("ERROR", f"state.json/accepted_risks[{i}]",
                    "an accepted risk may not license a factual claim (ACCEPTED_RISK_FACTUAL): omit the claim or block it "
                    "behind a human checkpoint")
        elif kind != "workflow" and state.get("guardrail") == "v0.3":
            rep.add("WARN", f"state.json/accepted_risks[{i}]", "accepted risk without kind workflow|factual (ACCEPTED_RISK_UNTYPED)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["record", "ask", "answer", "status"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--rcs", required=True)
    ap.add_argument("--role")
    ap.add_argument("--id")
    ap.add_argument("--question")
    ap.add_argument("--blocks", default="")
    ap.add_argument("--options", default="")
    ap.add_argument("--consequence", default="")
    ap.add_argument("--answer")
    ap.add_argument("--by")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    if a.cmd == "record":
        for r in record(rcs, a.role or "", a.files):
            print(f"{r['role']:7} {r['path']}")
    elif a.cmd == "ask":
        ask(rcs, a.id, a.question, [b for b in a.blocks.split(",") if b], [o for o in a.options.split("|") if o], a.consequence)
        print(f"asked {a.id}")
    elif a.cmd == "answer":
        if not a.by:
            raise SystemExit("--by is required: answers come from a named person")
        answer(rcs, a.id, a.answer, a.by)
        print(f"answered {a.id} (by {a.by})")
    else:
        q = open_questions(rcs)
        for x in q:
            print(f"OPEN {x['id']}{' [blocks ' + ','.join(x['blocks_claims']) + ']' if x['blocks_claims'] else ''}: {x['question']}")
        print(f"{len(q)} open question(s)")
        return 3 if any(x.get("blocking") for x in q) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
