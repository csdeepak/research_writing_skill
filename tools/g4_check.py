#!/usr/bin/env python3
"""Gate G4 made executable (vNext Stage 4; spec 7: "external blind review completed and findings addressed; not just an
agent declaring success").

G4 passes only when, for the latest review round:
  1. a blind review exists (.rcs/diagnostics/<round>/diagnostics.json, schema-valid; for a panel-only verification
     round, the review of the round it verifies, named as previous_round in its decision)          G4_NO_REVIEW
  2. it reviewed the draft it claims to: the packet manifest's source draft hash matches the draft on
     disk, and diagnostics.packet_id equals the manifest's packet_id                                  G4_PACKET_MISMATCH
  3. every BLOCKING finding (evaluation_rubric.md section 3: any dimension <= 2; evidence_traceability,
     claim_evidence_alignment or unsupported_inference < 4) and every inference issue has a disposition in
     .rcs/revisions/<round>/dispositions.json:                                                      G4_UNADDRESSED
       fixed     -> `where` names the revised location; the revised draft must differ from the reviewed one
       declined  -> `reason` >= 20 characters
       deferred  -> the item is listed in open_issues.md
       author_question -> `checkpoint` names a human checkpoint (Q-###) that exists in checkpoints/pending.json
                  (the finding needs a fact only the authors have; the claims it touches stay BLOCKED until answered)
       false_positive | not_reproducible -> `reason` >= 20 characters (the finding is wrong, or cannot be located
                  in the paper); it stays in the record, it does not disappear
     (v0.4.0, finding lifecycle: every finding ends in one of these six states; none is dropped)
  4. the reviewer stayed in its packet (reviewer_log.json, if the runtime recorded one, lists only packet
     files)                                                                                          G4_ISOLATION
  5. the review panel (v0.5, skill/review_panel.md), when the round has one, and always for a unified project in
     mode paper or restructure:                                                                      PANEL_*
       - tools/panel_check.py passes: five seats, reviews made against their commitments, the decision the findings
         give, a roadmap built only from seat findings
       - every standing major or fatal finding has a disposition, as `panel:<finding id>`, and in a verification
         round every blocking roadmap item the seats did not find addressed has one, as `panel:<R-#>`
       - a devil's-advocate finding is declined or marked false_positive only when its rebuttal score takes it out of
         blocking (5 withdraws it, 4 lowers it one level; right after a concession the next needs 5)  G4_DA_REBUTTAL
       - a Reject stops G4 until a named person decides: `"reject_checkpoint": "Q-###"` in dispositions.json,
         answered                                                                                     PANEL_REJECT
       - at most two panel rounds (2 revision loops in total)                                         PANEL_CAP

Usage: python tools/g4_check.py .rcs --round v001_1 [--revised drafts/v002/paper.md] [--out .rcs/audits/gates/G4_review.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import panel_check  # noqa: E402
from rce_common import CLAIM_TAG_RE, load_schema, validate  # noqa: E402

PANEL_MODES = {"paper", "restructure"}
MAX_PANEL_ROUNDS = 2

STRICT_DIMS = {"evidence_traceability", "claim_evidence_alignment", "unsupported_inference"}


def blocking(findings: list[dict]) -> list[int]:
    return [i for i, f in enumerate(findings)
            if f.get("score", 5) <= 2 or (f.get("dimension") in STRICT_DIMS and f.get("score", 5) < 4)]


def tagged_claims(md: str) -> set[str]:
    """Claim/limitation ids tagged in a draft ({C007}, {C001, L002})."""
    return {i for m in CLAIM_TAG_RE.finditer(md) for i in re.findall(r"[CL]\d{3,}", m.group(0))}


def check(rcs: Path, rnd: str, revised: Path | None) -> dict:
    items: list[dict] = []

    def err(code, msg):
        items.append({"level": "ERROR", "code": code, "message": msg})

    # Round 2 is a panel-only verification re-review (review_panel.md section 8): its blind reader review is the one from the
    # round it verifies (found in the v0.5 live run, where G4 failed G4_NO_REVIEW on a correct round 2).
    reader_rnd = rnd
    if not (rcs / "diagnostics" / rnd / "diagnostics.json").exists():
        prev = _verified_round(rcs, rnd)
        if prev and (rcs / "diagnostics" / prev / "diagnostics.json").exists():
            reader_rnd = prev
    ddir = rcs / "diagnostics" / reader_rnd
    dpath = ddir / "diagnostics.json"
    if not dpath.exists():
        err("G4_NO_REVIEW", f"no blind review for round {rnd}: run REVIEW_AGENT on a packet (workflow step 17)")
        return {"errors": 1, "items": items}
    diag = json.loads(dpath.read_text(encoding="utf-8"))
    for e in validate(diag, load_schema("diagnostics.schema.json")):
        err("G4_REVIEW_INVALID", e)
    man_p = _manifest(rcs, reader_rnd)
    reviewed = None
    if not man_p:
        err("G4_PACKET_MISMATCH", f"no packet manifest for round {rnd} under .rcs/packets/")
    else:
        man = json.loads(man_p.read_text(encoding="utf-8"))
        if man.get("packet_id") != diag.get("packet_id"):
            err("G4_PACKET_MISMATCH", f"review packet_id {diag.get('packet_id')} != manifest {man.get('packet_id')}")
        src = man.get("source_paper")
        if src:
            reviewed = (rcs.parent / src) if not Path(src).is_absolute() else Path(src)
            if not reviewed.exists() or hashlib.sha256(reviewed.read_bytes()).hexdigest() != man.get("source_sha256"):
                err("G4_PACKET_MISMATCH", f"the reviewed draft {src} changed or is missing since the packet was built")
        else:
            err("G4_PACKET_MISMATCH", "packet manifest does not record source_paper/source_sha256 (rebuild the packet)")
    log = ddir / "reviewer_log.json"
    if log.exists():
        packet_dir = man_p.parent.resolve() if man_p else None
        for f in json.loads(log.read_text(encoding="utf-8")).get("files_read", []):
            fp = Path(f) if Path(f).is_absolute() or packet_dir is None else packet_dir / f   # relative = inside the packet
            if packet_dir and not fp.resolve().is_relative_to(packet_dir):
                err("G4_ISOLATION", f"reviewer read {f} outside its packet")
    findings = diag.get("findings", [])
    need = [f"finding:{i}" for i in blocking(findings)] + [f"inference:{i}" for i in range(len(diag.get("inference_issues", [])))]
    disp_p = rcs / "revisions" / rnd / "dispositions.json"
    disp_doc = json.loads(disp_p.read_text(encoding="utf-8")) if disp_p.exists() else {}
    disp = {}
    for r in dict.fromkeys((reader_rnd, rnd)):              # the reader's round first; this round's dispositions win
        p = rcs / "revisions" / r / "dispositions.json"
        if p.exists():
            disp.update({d.get("item"): d for d in json.loads(p.read_text(encoding="utf-8")).get("items", [])})
    open_issues = (rcs / "open_issues.md").read_text(encoding="utf-8") if (rcs / "open_issues.md").exists() else ""
    asked = set()
    for cp in ("pending.json", "answers.json"):
        cpp = rcs / "checkpoints" / cp
        if cpp.exists():
            asked |= {q.get("id") for q in json.loads(cpp.read_text(encoding="utf-8")).get("questions", [])}
    panel_man = _manifest(rcs, rnd) if reader_rnd != rnd else man_p
    panel_pid = json.loads(panel_man.read_text(encoding="utf-8")).get("packet_id") if panel_man else diag.get("packet_id")
    panel = _panel(rcs, rnd, panel_pid, disp_doc, err)
    need += [f"panel:{fid}" for fid in panel.get("blocking", [])]
    any_fixed = False
    for key in need:
        d = disp.get(key)
        if key.startswith("panel:") and key.split(":", 1)[1] in panel.get("standing", {}):
            s = panel["standing"][key.split(":", 1)[1]]
            label = f"roadmap {key.split(':', 1)[1]} ({s['verdict']}; {', '.join(s['from_findings'])})"
        elif key.startswith("panel:"):
            f = panel["findings"][key.split(":", 1)[1]]
            label = f"{f.get('seat')} {panel['severity'].get(f['id'])} {f.get('criterion_id')}"
            if f["id"].startswith("DA-") and d and d.get("disposition") in ("declined", "false_positive"):
                err("G4_DA_REBUTTAL", f"{key}: a devil's-advocate finding stays blocking until a rebuttal scored 5 withdraws it, or "
                                      "4 lowers it out of blocking (rce_roles.py rebut). Otherwise fix it, defer it, or ask the author")
                continue
        else:
            label = (findings[int(key.split(":")[1])].get("dimension") if key.startswith("finding") else
                     diag["inference_issues"][int(key.split(":")[1])].get("kind"))
        if not d:
            err("G4_UNADDRESSED", f"{key} ({label}) has no disposition in revisions/{rnd}/dispositions.json")
        elif d.get("disposition") == "fixed":
            any_fixed = True
            if not str(d.get("where", "")).strip():
                err("G4_UNADDRESSED", f"{key}: 'fixed' must name where the revision is")
        elif d.get("disposition") == "declined":
            if len(str(d.get("reason", "")).strip()) < 20:
                err("G4_UNADDRESSED", f"{key}: 'declined' needs a reason (>= 20 characters)")
        elif d.get("disposition") == "deferred":
            if key not in open_issues and label not in open_issues:
                err("G4_UNADDRESSED", f"{key}: 'deferred' but not listed in open_issues.md")
        elif d.get("disposition") == "author_question":
            qid = str(d.get("checkpoint", ""))
            if qid not in asked:
                err("G4_UNADDRESSED", f"{key}: 'author_question' must name an existing checkpoint (got {qid or 'none'}); "
                                      "open one with tools/workflow_guard.py ask")
        elif d.get("disposition") in ("false_positive", "not_reproducible"):
            if len(str(d.get("reason", "")).strip()) < 20:
                err("G4_UNADDRESSED", f"{key}: '{d.get('disposition')}' needs a reason (>= 20 characters)")
        else:
            err("G4_UNADDRESSED", f"{key}: disposition must be fixed|declined|deferred|author_question|false_positive|"
                                  "not_reproducible")
    if any_fixed and reviewed is not None and revised is not None and revised.exists() and \
            hashlib.sha256(revised.read_bytes()).hexdigest() == hashlib.sha256(reviewed.read_bytes()).hexdigest():
        err("G4_UNADDRESSED", "findings marked fixed, but the revised draft is identical to the reviewed one")
    covered = set()
    for d in (reviewed, revised):
        if d is not None and d.exists():
            covered |= tagged_claims(d.read_text(encoding="utf-8"))
    return {"errors": sum(i["level"] == "ERROR" for i in items), "items": items, "round": rnd,
            "claims_covered": sorted(covered),
            "blocking_items": need, "diagnostics_sha256": hashlib.sha256(dpath.read_bytes()).hexdigest(),
            "dispositions_sha256": hashlib.sha256(disp_p.read_bytes()).hexdigest() if disp_p.exists() else None,
            "panel_decision": panel.get("decision")}


def _manifest(rcs: Path, rnd: str) -> Path | None:
    return next(iter(sorted((rcs / "packets").glob(f"*{rnd}*/packet_manifest.json"))), None) if (rcs / "packets").exists() else None


def _verified_round(rcs: Path, rnd: str) -> str | None:
    """The round a verification re-review checks, from its editorial decision; None for a full round."""
    p = rcs / "diagnostics" / rnd / "editorial_decision.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    except json.JSONDecodeError:
        return None
    return d.get("previous_round") if d.get("kind") == "verification" else None


def _panel(rcs: Path, rnd: str, packet_id: str | None, disp_doc: dict, err) -> dict:
    """The panel's part of G4. Returns panel_check's summary, or {} when the round has no panel and needs none."""
    state_p = rcs / "state.json"
    mode = (json.loads(state_p.read_text(encoding="utf-8")).get("mode") if state_p.exists() else None)
    root = rcs / "diagnostics" / rnd
    if not (root / "panel").exists() and not (root / "editorial_decision.json").exists():
        if mode in PANEL_MODES:
            err("PANEL_MISSING", f"mode {mode} needs the five-seat panel for round {rnd} (rce_roles.py panel, or the runtime's panel agents)")
        return {}
    items, summary = panel_check.check_round(rcs, rnd, packet_id)
    for level, code, msg in items:
        if level == "ERROR":
            err(code, msg)
    if summary.get("decision") == "reject":
        qid = str(disp_doc.get("reject_checkpoint", ""))
        answers = rcs / "checkpoints" / "answers.json"
        answered = {q.get("id") for q in json.loads(answers.read_text(encoding="utf-8")).get("questions", [])} if answers.exists() else set()
        if qid not in answered:
            err("PANEL_REJECT", "the panel's decision is Reject: stop, show the user the fatal findings, and record their decision "
                                "as an answered checkpoint named in dispositions.json (reject_checkpoint)")
    rounds = sorted(p.parent.name for p in (rcs / "diagnostics").glob("*/editorial_decision.json"))
    if len(rounds) > MAX_PANEL_ROUNDS:
        err("PANEL_CAP", f"{len(rounds)} panel rounds ({', '.join(rounds)}): the cap is {MAX_PANEL_ROUNDS} revision loops. Stop, and "
                         "move what remains to open_issues.md")
    return summary


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--round", required=True)
    ap.add_argument("--revised")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rep = check(Path(a.rcs), a.round, Path(a.revised) if a.revised else None)
    rep["tool"] = "g4_check"
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    for i in rep["items"]:
        print(f"{i['level']:5} {i['code']:20} {i['message']}")
    print(f"\nG4: {'PASSED' if rep['errors'] == 0 else 'FAILED'} ({rep['errors']} error(s); {len(rep.get('blocking_items', []))} blocking item(s))")
    return 1 if rep["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
