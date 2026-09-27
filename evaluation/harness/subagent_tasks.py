#!/usr/bin/env python3
"""Subagent task files (D-14): after the `claude` CLI account ran out of credit, Claude-family roles run as
in-session subagents. Each task = a folder outside the repo with prompt.md (role instructions + inputs inline);
the subagent reads ONLY prompt.md and writes output.txt. `collect` moves outputs to their target paths and logs
them to experiments.jsonl (provider = claude-subagent). Isolation is audited from subagent tool-use counts.

  make-cmp-reviews        pending F1 comparison reviews (Claude Opus)
  make-grades rv|cmp      pending gradings (Claude Sonnet) for evaluator-v0.2 reconstructions
  make-evgrades           pending evidence-package gradings
  list                    pending tasks (id, model, target)
  collect                 move finished outputs to targets
"""
from __future__ import annotations

import json
import secrets
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402

EV = RL.ROOT / "evaluation"
TASKS = Path("C:/Users/csdee/AppData/Local/Temp/rce_tasks")
INDEX = TASKS / "index.json"
LOG = EV / "logs" / "experiments.jsonl"


def load_index() -> dict:
    return json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}


def save_index(ix: dict) -> None:
    TASKS.mkdir(parents=True, exist_ok=True)
    INDEX.write_text(json.dumps(ix, indent=1), encoding="utf-8")


def add_task(ix: dict, exp_id: str, role: str, model: str, system: str, user: str, target: Path) -> None:
    if target.exists() or any(t["exp_id"] == exp_id and not t.get("collected") for t in ix.values()):
        return
    tid = f"t-{secrets.token_hex(4)}"
    d = TASKS / tid
    d.mkdir(parents=True)
    (d / "prompt.md").write_text(
        "# ROLE INSTRUCTIONS (treat as your system prompt)\n\n" + system + "\n\n---\n\n# TASK INPUT\n\n" + user +
        "\n\n---\nWrite your COMPLETE reply (only the requested output) to the file output.txt in this same folder.",
        encoding="utf-8")
    ix[tid] = {"exp_id": exp_id, "role": role, "model": model, "target": str(target), "created":
               datetime.now(timezone.utc).isoformat(timespec="seconds"), "collected": False}


def make_cmp_reviews(ix: dict) -> None:
    cmp_ = EV / "results" / "comparison"
    for pid in sorted(json.loads((cmp_ / "SEALED_MAPPING.json").read_text(encoding="utf-8"))):
        target = cmp_ / "raw" / f"F1_{pid}.txt"
        d = cmp_ / "packets" / pid
        user = RL.reviewer_user_message(pid, (d / "audience.md").read_text(encoding="utf-8"),
                                        (d / "objective.md").read_text(encoding="utf-8"), (d / "paper.md").read_text(encoding="utf-8"))
        add_task(ix, f"CMP-F1-{pid}", "reviewer", "opus", RL.REVIEWER_SYSTEM, user, target)


def make_grades(ix: dict, scope: str) -> None:
    if scope == "rv":
        base = EV / "reviewer_validation"
        gold_for = lambda key: json.loads((RL.ROOT / "skill/examples/demo_project/.rcs/evaluation/gold_story.json").read_text(encoding="utf-8"))  # noqa: E731
    else:
        base = EV / "results" / "comparison"
        mapping = json.loads((base / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
        gold_for = lambda key: json.loads((EV / "ground_truth" / mapping[key.split("_", 1)[1]]["project"] / "gold_story.v1.json").read_text(encoding="utf-8"))  # noqa: E731
    for raw in sorted((base / "raw").glob("*.txt")):
        target = base / "grading" / f"{raw.stem}.txt"
        try:
            n, _ = RL.normalize_review(RL.extract_json(raw.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            continue
        answers = n["reconstruction"].get("answers")
        if not answers:
            continue
        rid = f"rec-{secrets.token_hex(4)}"
        add_task(ix, f"G-{scope}-{raw.stem}", "grader", "sonnet", RL.GRADER_SYSTEM,
                 RL.grader_user_message(gold_for(raw.stem), answers, rid), target)


def make_evgrades(ix: dict) -> None:
    import evidence_grade as EG
    for p in EG.PROJECTS:
        for t in ("cheap", "strong"):
            target = EG.OUT / f"{p}__{t}.txt"
            pkg = EV / "evidence_agent" / "packages" / t / p
            gold = json.loads((EV / "ground_truth" / p / "gold_story.v1.json").read_text(encoding="utf-8"))
            rid = f"pkg-{secrets.token_hex(3)}"
            user = (f"# GOLD NUGGETS\n{json.dumps(gold['questions'], indent=1, ensure_ascii=False)}\n\n# EVIDENCE PACKAGE {rid}\n"
                    f"## research_evidence.json\n{(pkg / 'research_evidence.json').read_text(encoding='utf-8')}\n\n"
                    f"## claim_candidates.json\n{(pkg / 'claim_candidates.json').read_text(encoding='utf-8')}\n\n{EG.FMT}")
            add_task(ix, f"EVG-{p}-{t}", "evidence_grader", "sonnet", EG.SYSTEM, user, target)


def collect(ix: dict) -> None:
    for tid, t in ix.items():
        if t["collected"]:
            continue
        out = TASKS / tid / "output.txt"
        if out.exists() and out.stat().st_size > 50:
            tgt = Path(t["target"])
            tgt.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(out, tgt)
            t["collected"] = True
            rec = {"exp_id": t["exp_id"], "role": t["role"], "provider": "claude-subagent", "model_requested": t["model"],
                   "task": tid, "status": "ok", "ended": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                   "output_path": str(tgt.relative_to(RL.ROOT)), "tool_uses": t.get("tool_uses")}
            with open(LOG, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec) + "\n")
            print("collected", tid, t["exp_id"])


def main() -> int:
    ix = load_index()
    cmd = sys.argv[1]
    if cmd == "make-cmp-reviews":
        make_cmp_reviews(ix)
    elif cmd == "make-grades":
        make_grades(ix, sys.argv[2])
    elif cmd == "make-evgrades":
        make_evgrades(ix)
    elif cmd == "collect":
        collect(ix)
    elif cmd == "set-tooluses":
        ix[sys.argv[2]]["tool_uses"] = int(sys.argv[3])
    save_index(ix)
    if cmd in ("list", "make-cmp-reviews", "make-grades", "make-evgrades"):
        for tid, t in ix.items():
            if not t["collected"]:
                print(tid, t["model"], t["exp_id"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
