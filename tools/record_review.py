#!/usr/bin/env python3
"""Record a HUMAN usability/provenance review of a figure (vNext Stage 3: V5; spec 7: "record machine results and human
review separately").

V5 can only pass through this record: a named person looked at the rendered figure and answered three questions
(docs/06_VNEXT_SPEC.md V5): can the topic be recognised in about one second, the takeaway in about ten seconds, and the
detail in about a minute? An agent must never run this on a person's behalf -- that would be a self-certified gate.

Usage: python tools/record_review.py .rcs V001 --reviewer "Name" --topic yes --takeaway yes --detail no
                                     [--provenance-checked] [--note "..."]
"""
from __future__ import annotations

import argparse
import getpass
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

YES = {"yes": True, "y": True, "no": False, "n": False}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("visual_id")
    ap.add_argument("--reviewer", required=True, help="the person who looked at the figure")
    ap.add_argument("--topic", required=True, choices=YES)
    ap.add_argument("--takeaway", required=True, choices=YES)
    ap.add_argument("--detail", required=True, choices=YES)
    ap.add_argument("--provenance-checked", action="store_true", help="for external figures: the reviewer verified the source")
    ap.add_argument("--note", default="")
    a = ap.parse_args(argv)
    p = Path(a.rcs) / "plan" / "visual_registry.json"
    reg = json.loads(p.read_text(encoding="utf-8"))
    entry = next((v for v in reg.get("visuals", []) if v.get("id") == a.visual_id), None)
    if entry is None:
        print(f"{a.visual_id} not in {p}", file=sys.stderr)
        return 2
    entry["human_review"] = {
        "reviewer": a.reviewer, "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "recorded_by_os_user": getpass.getuser(), "one_second_topic": YES[a.topic],
        "ten_second_takeaway": YES[a.takeaway], "one_minute_detail": YES[a.detail],
        "provenance_checked": bool(a.provenance_checked), "note": a.note,
        "render_sha256_reviewed": entry.get("render_sha256"),
    }
    p.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    ok = all(entry["human_review"][k] for k in ("one_second_topic", "ten_second_takeaway", "one_minute_detail"))
    print(f"recorded review of {a.visual_id} by {a.reviewer}: {'V5 can pass' if ok else 'V5 will fail -> revise the figure'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
