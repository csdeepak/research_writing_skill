#!/usr/bin/env python3
"""Draft the AI-use statement for the authors to edit (workflow step 22; skill/finalize.md section 3).

  python tools/disclosure.py .rcs --out disclosure.md

The rules come from ai_policy in plan/venue_profile.yaml (recorded from the venue's official page at step 11), never from
memory. The facts come from the run: .rcs/provenance.jsonl, .rcs/models.json and the checkpoint answers. A fact the record
does not hold becomes [ASK AUTHOR: ...]. A sentence about a check appears only when that check's report exists with 0 errors,
so the statement cannot imply a check that did not run. With no policy on file the statement is generic and marked
assumed (VENUE_UNKNOWN). Exit 1 in that case, so a pipeline notices.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import load_json, yaml_block  # noqa: E402
import workflow_guard  # noqa: E402

ROLE_WORK = {"CORPUS": "built the evidence map and the source registry", "AUTHOR": "drafted the story, claims, plan and text",
             "REVIEW": "reviewed a blind packet of the draft", "VERIFIER": "checked the draft against the project's records",
             "PANEL": "critiqued the draft as simulated reviewers", "GRADER": "graded reader reconstruction"}
MODEL_ROLES = {"REVIEW": "REVIEW_AGENT", "GRADER": "RECON_GRADER"}
CHECKS = [("G5_numbers.json", "Every number in the final text was traced to a project file by a deterministic tool."),
          ("GL_citations.json", "Every cited source was looked up in bibliographic indexes, and its existence and retraction status were recorded."),
          ("G5_invariance.json", "A deterministic tool confirmed that language editing did not change the tagged claims.")]


def venue_rules(rcs: Path) -> tuple[str, dict]:
    p = rcs / "plan" / "venue_profile.yaml"
    if not p.exists():
        return "", {}
    text = p.read_text(encoding="utf-8")
    venue = yaml_block(text, "venue")
    policy = yaml_block(text, "ai_policy")
    return (venue.get("name") or "") if isinstance(venue, dict) else "", policy if isinstance(policy, dict) else {}


def _report_clean(rcs: Path, name: str) -> bool:
    p = rcs / "audits" / "gates" / name
    if not p.exists():
        return False
    try:
        return load_json(p).get("errors", 1) == 0
    except json.JSONDecodeError:
        return False


def role_lines(rcs: Path) -> tuple[list[str], list[str]]:
    """(what the ledger shows each role did, what the authors must still supply)."""
    roles = sorted({r.get("role") for r in workflow_guard.load_ledger(rcs)} - {"HUMAN", None})
    models = load_json(rcs / "models.json").get("roles", {}) if (rcs / "models.json").exists() else {}
    lines, asks = [], []
    for role in roles:
        bound = models.get(MODEL_ROLES.get(role, role), {}).get("model")
        who = bound if bound and "<" not in bound else None
        if not who:
            asks.append(f"[ASK AUTHOR: which AI tool and version ran the {role} role?]")
        lines.append(f"- {role}: {who or 'tool not on record'}; {ROLE_WORK.get(role, 'took part in the run')}.")
    return lines, asks


def humans(rcs: Path) -> list[str]:
    p = rcs / "checkpoints" / "answers.json"
    answers = load_json(p).get("questions", []) if p.exists() else []
    return sorted({a.get("answered_by") for a in answers if a.get("answered_by")})


def build(rcs: Path) -> tuple[str, bool]:
    venue, policy = venue_rules(rcs)
    known = bool(policy.get("source_url")) and not policy.get("assumed")
    lines, asks = role_lines(rcs)
    checks = [text for name, text in CHECKS if _report_clean(rcs, name)]
    gi = rcs / "audits" / "gates" / "GI_integrity.json"
    if gi.exists() and load_json(gi).get("stage") == "final" and load_json(gi).get("errors", 1) == 0:
        checks.append("A separate role, working from the project's records, checked the final draft for AI research failure modes.")
    people = humans(rcs)
    out = ["# AI-use disclosure", "", "**Draft for the authors to edit.** The authors are responsible for this statement and for "
           "the paper. An AI system cannot be an author.", ""]
    out += ["## Venue policy", ""]
    if known:
        out += [f"- Venue: {venue or '[ASK AUTHOR: venue name]'}", f"- Source: {policy['source_url']} (retrieved {policy.get('retrieved') or 'date not recorded'})"]
        if policy.get("disclosure_required") is not None:
            out.append(f"- Disclosure required: {'yes' if policy['disclosure_required'] else 'no'}")
        if policy.get("where"):
            out.append(f"- Place it in: {policy['where']}")
        for label, key in (("Permitted", "permitted_uses"), ("Not permitted", "prohibited_uses")):
            if policy.get(key):
                out.append(f"- {label}: {'; '.join(str(x) for x in policy[key])}")
    else:
        out += ["**VENUE_UNKNOWN: assumed.** No AI policy from an official page is on file, so this statement is generic. "
                "Read the venue's current policy before submitting. Policies change."]
    out += ["", "## Statement", "", "In preparing this work, the authors used AI systems in the roles below. "
            "[ASK AUTHOR: confirm this list, and add any other AI use.]", ""]
    out += lines or ["[ASK AUTHOR: the run recorded no roles in .rcs/provenance.jsonl. Describe what AI systems were used for.]"]
    out += [""]
    if checks:
        out += checks + [""]
    if people:
        out += [f"Human decisions during the run were recorded and made by: {', '.join(people)}.", ""]
    out += ["[ASK AUTHOR: state who reviewed the AI output and confirm that the authors take responsibility for the content.]", ""]
    if asks:
        out += ["## Still needed from the authors", "", *[f"- {a}" for a in asks], ""]
    return "\n".join(out), known


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--out", default="disclosure.md")
    a = ap.parse_args(argv)
    text, known = build(Path(a.rcs))
    Path(a.out).write_text(text, encoding="utf-8")
    print(f"wrote {a.out}: a draft for the authors to edit, with {text.count('[ASK AUTHOR')} open question(s)")
    if not known:
        print("ERROR VENUE_UNKNOWN: no AI policy from an official page is on file; the statement is generic and marked assumed")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
