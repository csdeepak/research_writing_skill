#!/usr/bin/env python3
"""Deterministic checks on one review-panel round (skill/review_panel.md). Used by g4_check.py and rce_roles.py panel.

  python tools/panel_check.py .rcs --round v002_1

A round lives in .rcs/diagnostics/<round>/: panel/cards.json, panel/<seat>.commitment.json, panel/<seat>.review.json (a
full round) or panel/<seat>.verification.json (a re-review), optional panel/devils_advocate.rebuttal.json, and
editorial_decision.json. The checks:

  PANEL_SHRUNK              a seat is missing: a round is never synthesized from fewer than five seats
  PANEL_INVALID             an output fails its schema
  PANEL_COMMITMENT_MISMATCH a review was not made against the commitment on disk (its hash differs): the seat could
                            have fitted its standard to the paper
  PANEL_COMMITMENT_INCOMPLETE  a commitment skips a criterion on the seat's card
  PANEL_CRITERION_UNJUDGED  a committed criterion has no judgment, or a judgment has no location
  PANEL_FAILS_WITHOUT_FINDING  a criterion judged "fails" with no finding on it
  PANEL_FINDING_ID          a finding id lacks the seat's prefix, repeats, or names a criterion the seat does not own
  PANEL_PACKET_MISMATCH     a seat reviewed another packet
  PANEL_INVENTED_FINDING    a roadmap item cites a finding no seat made: the synthesizer adds nothing
  PANEL_ROADMAP_INCOMPLETE  a standing major or fatal finding has no blocking roadmap item
  PANEL_DOWNGRADE_UNQUOTED  a downgrade's quote is not in the paper
  PANEL_DECISION_MISMATCH   the stated decision is not the one the findings give
  PANEL_CARDS_CHANGED       a re-review used different reviewer cards from the round it checks
  PANEL_ITEM_UNCHECKED      a re-review left a roadmap item unchecked

The decision rule has no arithmetic: reject on any standing fatal finding, major on any major, minor on any minor or any
criterion judged partly or not_assessed, accept only when every criterion meets with a location. A re-review decides
accept, minor or major from its checks and new findings.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import load_json, load_schema, validate  # noqa: E402

SEATS = ("journal_fit", "methodology", "domain", "perspective", "devils_advocate")
PREFIX = {"journal_fit": "JF", "methodology": "ME", "domain": "DO", "perspective": "PE", "devils_advocate": "DA"}
LEVELS = ("withdrawn", "minor", "major", "fatal")
BLOCKING = {"major", "fatal"}
CHECK_RANK = {"addressed": 0, "partly": 1, "cannot_verify": 1, "not_addressed": 2, "worsened": 2}


def sha_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _norm(s: str) -> str:
    return " ".join(re.sub(r"[^\w\s]", " ", s or "").lower().split())


def lower(severity: str) -> str:
    return LEVELS[max(0, LEVELS.index(severity) - 1)]


def rebuttal_outcomes(scores: list[dict]) -> dict[str, int]:
    """finding id -> the score that counts. Right after any concession the next one needs a 5, so a run of 4s cannot
    wear findings away: a 4 that follows a concession counts as a 3."""
    out, conceded = {}, False
    for s in scores:
        score = s.get("score", 1)
        if score == 4 and conceded:
            score = 3
        out[s.get("finding_id")] = score
        conceded = score >= 4
    return out


def effective(findings: dict[str, dict], decision: dict | None, rebuttals: dict[str, int] | None = None) -> dict[str, str]:
    """Each finding's standing severity after the synthesizer's quoted downgrades and the devil's advocate's scores."""
    sev = {fid: f.get("severity", "minor") for fid, f in findings.items()}
    for d in (decision or {}).get("downgrades", []) or []:
        if d.get("finding_id") in sev and d.get("to") in LEVELS and LEVELS.index(d["to"]) < LEVELS.index(sev[d["finding_id"]]):
            sev[d["finding_id"]] = d["to"]
    for fid, score in (rebuttals or {}).items():
        if fid in sev and fid.startswith("DA-"):
            sev[fid] = "withdrawn" if score >= 5 else lower(sev[fid]) if score == 4 else sev[fid]
    return sev


def derive_full(sev: dict[str, str], judgements: list[str]) -> str:
    standing = {s for s in sev.values() if s != "withdrawn"}
    if "fatal" in standing:
        return "reject"
    if "major" in standing:
        return "major"
    if "minor" in standing or any(j in ("partly", "not_assessed", "fails") for j in judgements):
        return "minor"
    return "accept"


def derive_verification(roadmap: list[dict], checks: dict[str, str], new_sev: dict[str, str]) -> str:
    blocking_items = {r["id"] for r in roadmap if r.get("priority") == "blocking"}
    new = {s for s in new_sev.values() if s != "withdrawn"}
    if any(CHECK_RANK.get(checks.get(i, "not_addressed"), 2) == 2 for i in blocking_items) or new & BLOCKING:
        return "major"
    if any(CHECK_RANK.get(v, 2) >= 1 for v in checks.values()) or "minor" in new:
        return "minor"
    return "accept"


def _load(p: Path, schema: str, items: list, label: str) -> dict | None:
    if not p.exists():
        return None
    try:
        obj = load_json(p)
    except json.JSONDecodeError as exc:
        items.append(("ERROR", "PANEL_INVALID", f"{label}: invalid JSON: {exc}"))
        return None
    for e in validate(obj, load_schema(schema))[:5]:
        items.append(("ERROR", "PANEL_INVALID", f"{label}: {e}"))
    return obj


def _cards(obj: dict | None) -> dict[str, dict]:
    return {c.get("seat"): c for c in (obj or {}).get("cards", []) if isinstance(c, dict)}


def check_round(rcs: Path, rnd: str, packet_id: str | None = None) -> tuple[list[tuple], dict]:
    """(items as (level, code, message), summary). The summary carries the derived decision, the standing blocking
    findings and the effective severities, for g4_check.py."""
    items: list[tuple] = []
    root = rcs / "diagnostics" / rnd
    pdir = root / "panel"
    decision = _load(root / "editorial_decision.json", "editorial_decision.schema.json", items, "editorial_decision.json")
    kind = (decision or {}).get("kind", "verification" if list(pdir.glob("*.verification.json")) else "full")
    cards = _load(pdir / "cards.json", "reviewer_cards.schema.json", items, "cards.json")
    by_seat = _cards(cards)
    summary = {"kind": kind, "decision": (decision or {}).get("decision"), "derived": None, "blocking": [], "severity": {},
               "findings": {}}
    if cards is None:
        items.append(("ERROR", "PANEL_SHRUNK", f"no reviewer cards in diagnostics/{rnd}/panel/"))
    findings: dict[str, dict] = {}
    judgements: list[str] = []
    checks: dict[str, str] = {}
    paper = rcs / "packets" / f"review_{rnd}" / "paper.md"
    for seat in SEATS:
        card = by_seat.get(seat)
        if cards is not None and not card:
            items.append(("ERROR", "PANEL_SHRUNK", f"cards.json has no card for {seat}"))
        own = {c.get("id") for c in (card or {}).get("criteria", [])}
        out = _load(pdir / f"{seat}.{'review' if kind == 'full' else 'verification'}.json", "panel_review.schema.json", items, f"{seat}")
        if out is None:
            items.append(("ERROR", "PANEL_SHRUNK", f"{seat} has no {'review' if kind == 'full' else 'verification'}: never synthesize a smaller panel"))
            continue
        if packet_id and out.get("packet_id") not in (None, packet_id):
            items.append(("ERROR", "PANEL_PACKET_MISMATCH", f"{seat} reviewed packet {out.get('packet_id')}, not {packet_id}"))
        if kind == "full":
            cp = pdir / f"{seat}.commitment.json"
            commitment = _load(cp, "panel_review.schema.json", items, f"{seat}.commitment")
            if commitment is None:
                items.append(("ERROR", "PANEL_COMMITMENT_MISMATCH", f"{seat} has no commitment on disk"))
                committed: set = set()
            else:
                committed = {p.get("criterion_id") for p in commitment.get("plan", [])}
                if out.get("commitment_sha256") != sha_file(cp):
                    items.append(("ERROR", "PANEL_COMMITMENT_MISMATCH", f"{seat}: the review was not made against the commitment on disk"))
                if own - committed:
                    items.append(("ERROR", "PANEL_COMMITMENT_INCOMPLETE", f"{seat} committed nothing for {', '.join(sorted(own - committed))}"))
            judged = {c.get("criterion_id"): c for c in out.get("criteria", [])}
            for cid in sorted(committed - set(judged)):
                items.append(("ERROR", "PANEL_CRITERION_UNJUDGED", f"{seat}: {cid} was committed but not judged"))
            for cid, c in judged.items():
                judgements.append(c.get("judgement"))
                if c.get("judgement") != "not_assessed" and not (c.get("location") or {}).get("section"):
                    items.append(("ERROR", "PANEL_CRITERION_UNJUDGED", f"{seat}: {cid} is judged {c.get('judgement')} with no location"))
                if c.get("judgement") == "fails" and not any(f.get("criterion_id") == cid for f in out.get("findings", [])):
                    items.append(("ERROR", "PANEL_FAILS_WITHOUT_FINDING", f"{seat}: {cid} fails with no finding on it"))
        else:
            for c in out.get("checks", []):
                rid = c.get("roadmap_id")
                if CHECK_RANK.get(c.get("verdict"), 2) >= CHECK_RANK.get(checks.get(rid, "addressed"), 0):
                    checks[rid] = c.get("verdict")
        for f in out.get("findings", []):
            fid = f.get("id", "")
            if not fid.startswith(PREFIX[seat] + "-") or fid in findings:
                items.append(("ERROR", "PANEL_FINDING_ID", f"{seat}: finding id {fid!r} must be unique and start with {PREFIX[seat]}-"))
            elif kind == "full" and own and f.get("criterion_id") not in own:
                items.append(("ERROR", "PANEL_FINDING_ID", f"{seat}: {fid} names {f.get('criterion_id')}, which is not on this seat's card"))
            findings[fid] = {**f, "seat": seat}
    reb = load_json(pdir / "devils_advocate.rebuttal.json") if (pdir / "devils_advocate.rebuttal.json").exists() else {}
    rebuttals = rebuttal_outcomes(reb.get("scores", []))
    # Rebuttals come during revision, after the synthesis: the decision is checked against severities as they stood then,
    # while what still blocks G4 is judged after the rebuttals.
    sev = effective(findings, decision)
    now = effective(findings, decision, rebuttals)
    summary.update(severity=now, findings=findings, rebuttals=rebuttals)

    if kind == "verification":
        prev = (decision or {}).get("previous_round")
        prev_dir = rcs / "diagnostics" / str(prev)
        prev_dec = load_json(prev_dir / "editorial_decision.json") if prev and (prev_dir / "editorial_decision.json").exists() else None
        if prev_dec is None:
            items.append(("ERROR", "PANEL_ITEM_UNCHECKED", f"a re-review needs the previous round's decision (previous_round: {prev})"))
            roadmap = []
        else:
            roadmap = prev_dec.get("roadmap", [])
            for r in roadmap:
                if r.get("id") not in checks:
                    items.append(("ERROR", "PANEL_ITEM_UNCHECKED", f"roadmap item {r.get('id')} of {prev} was not checked"))
            pc = prev_dir / "panel" / "cards.json"
            if not pc.exists() or not (pdir / "cards.json").exists() or sha_file(pc) != sha_file(pdir / "cards.json"):
                items.append(("ERROR", "PANEL_CARDS_CHANGED", "a re-review must use the same reviewer cards as the round it checks"))
        summary["derived"] = derive_verification(roadmap, checks, sev)
        summary["checks"] = checks
    else:
        summary["derived"] = derive_full(sev, judgements)

    if decision is not None:
        known = set(findings)
        prev_ids = set()
        if kind == "verification" and decision.get("previous_round"):
            pd = rcs / "diagnostics" / str(decision["previous_round"]) / "editorial_decision.json"
            prev_ids = {x for r in (load_json(pd).get("roadmap", []) if pd.exists() else []) for x in r.get("from_findings", [])}
        for r in decision.get("roadmap", []):
            for fid in r.get("from_findings", []):
                if fid not in known | prev_ids:
                    items.append(("ERROR", "PANEL_INVENTED_FINDING", f"roadmap {r.get('id')} cites {fid}, which no seat reported"))
        covered = {fid for r in decision.get("roadmap", []) if r.get("priority") == "blocking" for fid in r.get("from_findings", [])}
        merged = [set(m.get("finding_ids", [])) for m in decision.get("merged", []) or []]
        for fid, s in sev.items():
            group = next((g for g in merged if fid in g), {fid})
            if s in BLOCKING and not group & covered:
                items.append(("ERROR", "PANEL_ROADMAP_INCOMPLETE", f"{fid} stands at {s} but no blocking roadmap item covers it"))
        text = _norm(paper.read_text(encoding="utf-8")) if paper.exists() else None
        for d in decision.get("downgrades", []) or []:
            if d.get("finding_id") not in known:
                items.append(("ERROR", "PANEL_INVENTED_FINDING", f"downgrade of unknown finding {d.get('finding_id')}"))
            elif text is not None and _norm(d.get("quote", "")) not in text:
                items.append(("ERROR", "PANEL_DOWNGRADE_UNQUOTED", f"downgrade of {d['finding_id']}: its quote is not in the paper"))
        if decision.get("decision") != summary["derived"]:
            items.append(("ERROR", "PANEL_DECISION_MISMATCH", f"decision {decision.get('decision')!r}, but the findings give {summary['derived']!r}"))
    else:
        items.append(("ERROR", "PANEL_SHRUNK", f"no editorial_decision.json for {rnd}"))
    summary["blocking"] = sorted(fid for fid, s in now.items() if s in BLOCKING)
    return items, summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--round", required=True)
    a = ap.parse_args(argv)
    items, s = check_round(Path(a.rcs), a.round)
    for level, code, msg in items:
        print(f"{level:5} {code:28} {msg}")
    errors = sum(1 for i in items if i[0] == "ERROR")
    print(f"\npanel {a.round} ({s['kind']}): stated {s['decision']}, derived {s['derived']}; "
          f"{len(s['blocking'])} blocking finding(s); {errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
