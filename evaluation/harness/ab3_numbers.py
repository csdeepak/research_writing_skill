#!/usr/bin/env python3
"""D-29 secondary measure: numbers in each A/B packet paper that cannot be traced to the frozen source snapshot.

Uniform for both arms: the reference is the project's frozen snapshot (paper.txt + README_*.md), not the writer's own
evidence map (v0.1.0 and v0.3.0 maps differ in format). Uses v0.3.0's verify_numbers matching (rounding, % <-> fraction,
K/M/B); the packet papers carry no claim tags, so no derived-value matching is allowed. A count, not a verdict: an
untraced number can still be a legitimate derivation the writer explains in the text.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402

EV = RL.ROOT / "evaluation"
CMP = EV / "results" / "comparison"
sys.path.insert(0, str(EV / "skill_versions" / "v0.3.0-candidate" / "tools"))
import verify_numbers as VN  # noqa: E402

CONDS = ("skillv010ab3", "skillv030ab3")


def source_text(project: str) -> str:
    snap = EV / "external_projects" / project / "snapshot"
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in [snap / "paper.txt", *sorted(snap.glob("README__*.md"))])


def main() -> int:
    mapping = json.loads((CMP / "SEALED_MAPPING.json").read_text(encoding="utf-8"))
    rows = []
    for pid, m in sorted(mapping.items(), key=lambda kv: (kv[1]["project"], kv[1]["condition"])):
        if m["condition"] not in CONDS:
            continue
        with tempfile.TemporaryDirectory() as tmp:
            rcs = Path(tmp) / ".rcs"
            (rcs / "evidence").mkdir(parents=True)
            (rcs / "evidence" / "research_evidence.json").write_text(json.dumps(
                {"items": [{"id": "E001", "kind": "result", "summary": source_text(m["project"])}]}), encoding="utf-8")
            out = Path(tmp) / "r.json"
            VN.main([str(CMP / "packets" / pid / "paper.md"), "--rcs", str(rcs), "--project-root", tmp, "--out", str(out)])
            rep = json.loads(out.read_text(encoding="utf-8"))
        items = rep.get("items") or rep.get("findings") or []
        untraced = [i for i in items if "UNTRACED" in json.dumps(i)]
        rows.append({"project": m["project"], "condition": m["condition"], "pid": pid,
                     "numbers_checked": rep.get("numbers_checked", rep.get("checked")),
                     "untraced": len(untraced), "untraced_examples": [i.get("text") or i.get("message") for i in untraced[:8]]})
    (CMP / "scores" / "ab3_numbers.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    for r in rows:
        print(f"{r['project']:12s} {r['condition']:14s} checked {r['numbers_checked']}  untraced {r['untraced']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
