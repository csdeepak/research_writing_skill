#!/usr/bin/env python3
"""Run the RCE's single-shot roles on ANY model (bindings in .rcs/models.json; see tools/rce_llm.py).

  review     REVIEW_AGENT (workflow step 18) on a sanitized packet (tools/build_review_packet.py). Only the packet is
             sent: the role file, the two output schemas and the packet files, nothing from .rcs/. Output is validated
             (schemas, all 20 dimensions, exactly Q1-Q12, packet id), written to .rcs/diagnostics/<round>/, and recorded
             in the provenance ledger as REVIEW when the ledger is in use.
               python tools/rce_roles.py review --rcs .rcs --round v002_1 [--packet .rcs/packets/review_v002_1]
  calibrate  run the configured REVIEW_AGENT on the planted-defect benchmark (tests/perturbations/) and score it:
             dimension sensitivity (>= 0.90) and false alarms on the clean paper (<= 0.10). Do this once per reviewer
             model before trusting its reviews (agents/review_agent.md, calibration note). Blinded: random packet ids.
               python tools/rce_roles.py calibrate --rcs .rcs [--out .rcs/audits/reviewer_calibration.json]
  run-tasks  execute every <dir>/*/prompt.md that has no output.txt yet with a role's model and save output.txt
             (task folders made by micro_recon.py make, comprehension_kit.py, or your own scripts)
               python tools/rce_roles.py run-tasks DIR --rcs .rcs --role READER [--json]

Roles that need file tools (CORPUS_AGENT, AUTHOR) are not run here: they run in whatever agent runtime you use
(adapters/). Every gate check (validate_artifacts, lint_draft, verify_numbers, visuals, g4_check) is deterministic
and independent of the model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import secrets
import statistics
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_review_packet  # noqa: E402
import rce_llm  # noqa: E402
from rce_common import SKILL_DIR, load_schema  # noqa: E402

DIMS = ["problem", "motivation", "research_question", "contribution", "method", "experiment", "result", "interpretation",
        "limitation", "narrative_coherence", "terminology", "logical_flow", "evidence_traceability", "figure_table",
        "claim_evidence_alignment", "unsupported_inference", "redundancy", "cognitive_load", "orientation", "so_what"]
QUESTIONS = [f"Q{i}" for i in range(1, 13)]
SENS_MIN, FA_MAX = 0.90, 0.10
PERT = SKILL_DIR / "tests" / "perturbations"
# Blinding substitution for the benchmark (a placeholder note that would reveal test-item status; D-07)
REPLACEMENTS = {"G_citation_misuse.md": [(
    "[R1]–[R6] Synthetic placeholders. The benchmark's expected-answers file defines what each placeholder actually \"contains\".",
    "[R1]–[R6] Reference list omitted in this manuscript version.")]}


# ------------------------------------------------------------------------------------------------ review
def review_prompt(files: dict[str, str], packet_id: str) -> tuple[str, str]:
    system = (SKILL_DIR / "agents" / "review_agent.md").read_text(encoding="utf-8")
    parts = ["# OUTPUT SCHEMAS\n## reconstruction.schema.json\n", (SKILL_DIR / "schemas" / "reconstruction.schema.json").read_text(encoding="utf-8"),
             "\n## diagnostics.schema.json\n", (SKILL_DIR / "schemas" / "diagnostics.schema.json").read_text(encoding="utf-8"),
             f"\n\n# YOUR PACKET (packet_id: {packet_id}); these are the only files you may use\n"]
    for name, text in sorted(files.items()):
        parts.append(f"\n## FILE {name}\n\n{text}\n")
    parts.append('\n---\nReply with ONE JSON object only: {"reconstruction": <object valid against reconstruction.schema.json>, '
                 '"diagnostics": <object valid against diagnostics.schema.json>, "reviewer_notes_private": "<your free '
                 f'reasoning>"}}. Use packet_id "{packet_id}" in both objects. Give every one of the 20 dimensions at least '
                 "one finding, and answer exactly Q1-Q12.")
    return system, "".join(parts)


def review_check(packet_id: str):
    rs, ds = load_schema("reconstruction.schema.json"), load_schema("diagnostics.schema.json")

    def check(obj) -> list[str]:
        if not isinstance(obj, dict) or "reconstruction" not in obj or "diagnostics" not in obj:
            return ["top level must be an object with 'reconstruction' and 'diagnostics'"]
        errs = [f"reconstruction: {e}" for e in rce_llm.validate(obj["reconstruction"], rs)]
        errs += [f"diagnostics: {e}" for e in rce_llm.validate(obj["diagnostics"], ds)]
        have = {f.get("dimension") for f in obj["diagnostics"].get("findings", []) if isinstance(f, dict)}
        errs += [f"diagnostics: no finding for dimension {d}" for d in DIMS if d not in have]
        keys = sorted((obj["reconstruction"].get("answers") or {}).keys())
        if keys != sorted(QUESTIONS):
            errs.append(f"reconstruction.answers must have exactly Q1-Q12 (got {keys})")
        for part in ("reconstruction", "diagnostics"):
            if obj[part].get("packet_id") not in (None, packet_id):
                errs.append(f"{part}.packet_id must be {packet_id}")
        return errs
    return check


def normalize_review(obj) -> int:
    """Cosmetic only: a location quote longer than the schema allows is cut to its first 19 words + an ellipsis (it
    remains a pointer to the same place). Scores, findings and answers are never changed. Returns the number changed.
    Found in live use: a non-Claude reviewer kept quoting whole sentences after four rounds of error feedback."""
    n = 0
    if not isinstance(obj, dict):
        return 0
    for f in (obj.get("diagnostics") or {}).get("findings", []) or []:
        loc = f.get("location") if isinstance(f, dict) else None
        q = loc.get("quote") if isinstance(loc, dict) else None
        if isinstance(q, str) and (len(q) > 200 or len(q.split()) > 20):
            words = q.split()[:19]                     # 19 words + the ellipsis = 20 tokens (idempotent)
            cut = " ".join(words)
            loc["quote"] = (cut[:196] + " …") if len(cut) > 196 else cut + " …"
            n += 1
    return n


def packet_files(packet: Path) -> dict[str, str]:
    return {p.relative_to(packet).as_posix(): p.read_text(encoding="utf-8")
            for p in sorted(packet.rglob("*")) if p.is_file() and p.name != "packet_manifest.json"}


def run_review(cfg: dict, packet: Path, packet_id: str, rcs: Path | None) -> tuple[dict, dict]:
    system, user = review_prompt(packet_files(packet), packet_id)
    return rce_llm.complete_json(cfg, "REVIEW_AGENT", system, user, rcs=rcs, check=review_check(packet_id),
                                 normalize=normalize_review)


def cmd_review(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    packet = Path(a.packet) if a.packet else rcs / "packets" / f"review_{a.round}"
    manifest = json.loads((packet / "packet_manifest.json").read_text(encoding="utf-8"))
    obj, meta = run_review(cfg, packet, manifest["packet_id"], rcs)
    d = rcs / "diagnostics" / a.round
    d.mkdir(parents=True, exist_ok=True)
    (d / "diagnostics.json").write_text(json.dumps(obj["diagnostics"], indent=1, ensure_ascii=False), encoding="utf-8")
    (d / "reconstruction.json").write_text(json.dumps(obj["reconstruction"], indent=1, ensure_ascii=False), encoding="utf-8")
    (d / "reviewer_notes.private.md").write_text(str(obj.get("reviewer_notes_private", "")), encoding="utf-8")
    rc = rce_llm.role_config(cfg, "REVIEW_AGENT")
    (d / "reviewer_log.json").write_text(json.dumps({
        "mode": "tools/rce_roles.py review: only the packet files were sent", "files_read": sorted(packet_files(packet)),
        "packet_id": manifest["packet_id"], "provider": rc["provider"], "model": rc.get("model") or rc.get("command"),
        "attempts": meta["attempts"], "quotes_shortened": meta.get("normalized", 0),
        "calibration": _calibration_status(rcs, rc)}, indent=1), encoding="utf-8")
    if (rcs / "provenance.jsonl").exists():
        import workflow_guard
        workflow_guard.record(rcs, "REVIEW", [str(d / f) for f in ("diagnostics.json", "reconstruction.json",
                                                                      "reviewer_log.json", "reviewer_notes.private.md")])
    print(f"review {a.round}: {len(obj['diagnostics'].get('findings', []))} findings, "
          f"{len(obj['diagnostics'].get('inference_issues', []))} inference issues, {meta['attempts']} attempt(s)")
    cal = _calibration_status(rcs, rc)
    if cal != "passed":
        print(f"WARN: this reviewer model's calibration is {cal}; run `rce_roles.py calibrate` before gating on its reviews")
    return 0


def _calibration_status(rcs: Path, rc: dict) -> str:
    p = rcs / "audits" / "reviewer_calibration.json"
    if not p.exists():
        return "not_run"
    c = json.loads(p.read_text(encoding="utf-8"))
    same = c.get("provider") == rc["provider"] and c.get("model") == (rc.get("model") or rc.get("command"))
    return ("passed" if c.get("calibrated") else "failed") if same else "not_run (calibrated model differs)"


# --------------------------------------------------------------------------------------------- calibrate
def dims_of(diag: dict) -> dict[str, int]:
    out: dict[str, int] = {}
    for f in diag.get("findings", []):
        if isinstance(f.get("score"), int):
            out[f["dimension"]] = min(out.get(f["dimension"], 9), f["score"])      # most severe finding per dimension
    return out


def score_calibration(dims_by_variant: dict[str, dict[str, int]], expected: dict) -> dict:
    base = dims_by_variant.get("A_clean.md")
    det = []
    for v, d in sorted(dims_by_variant.items()):
        if v == "A_clean.md" or not base:
            continue
        exp = expected[v]["reviewer_expected_drop"]
        hits = [x for x in exp if d.get(x, 9) <= base.get(x, -9) - 1]
        det.append({"variant": v, "expected": exp, "detected": hits, "missed": [x for x in exp if x not in hits],
                    "sensitivity": round(len(hits) / len(exp), 3) if exp else None})
    sens = [x["sensitivity"] for x in det if x["sensitivity"] is not None]
    fa = [x for x, s in (base or {}).items() if s <= 2]
    out = {"mean_dimension_sensitivity": round(statistics.mean(sens), 3) if sens else None,
           "false_alarm_rate_on_A": round(len(fa) / len(DIMS), 3) if base else None, "false_alarm_dims_on_A": fa,
           "thresholds": {"sensitivity_min": SENS_MIN, "false_alarm_max": FA_MAX}, "detection": det}
    out["calibrated"] = bool(sens) and base is not None and out["mean_dimension_sensitivity"] >= SENS_MIN \
        and out["false_alarm_rate_on_A"] <= FA_MAX
    return out


def cmd_calibrate(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    expected = json.loads((PERT / "EXPECTED.json").read_text(encoding="utf-8"))["variants"]
    audience = (PERT / "packet_audience.md").read_text(encoding="utf-8")
    objective = (PERT / "packet_objective.md").read_text(encoding="utf-8")
    dims_by_variant, runs = {}, {}
    rc0 = rce_llm.role_config(cfg, "REVIEW_AGENT")
    cache = rcs / "audits" / "calibration_runs" / hashlib.sha256(
        json.dumps({k: rc0.get(k) for k in ("provider", "model", "command", "base_url")}, sort_keys=True).encode()).hexdigest()[:12]
    cache.mkdir(parents=True, exist_ok=True)
    for variant in sorted(expected):
        cached = cache / f"{variant}.json"
        if cached.exists():                      # resume: a finished review of this variant by this same model
            c = json.loads(cached.read_text(encoding="utf-8"))
            dims_by_variant[variant], runs[variant] = c["dims"], c["run"]
            print(f"  {variant:32s} (cached)")
            continue
        paper = (PERT / variant).read_text(encoding="utf-8")
        for old, new in REPLACEMENTS.get(variant, []):
            paper = paper.replace(old, new)
        paper, _ = build_review_packet.sanitize(paper, False)
        pid = f"pkt-{secrets.token_hex(4)}"
        with tempfile.TemporaryDirectory() as tmp:
            pk = Path(tmp)
            (pk / "paper.md").write_text(paper, encoding="utf-8")
            (pk / "audience.md").write_text(audience, encoding="utf-8")
            (pk / "objective.md").write_text(objective, encoding="utf-8")
            obj, meta = run_review(cfg, pk, pid, rcs)
        dims_by_variant[variant] = dims_of(obj["diagnostics"])
        runs[variant] = {"packet_id": pid, "attempts": meta["attempts"], "quotes_shortened": meta.get("normalized", 0)}
        cached.write_text(json.dumps({"dims": dims_by_variant[variant], "run": runs[variant]}), encoding="utf-8")
        print(f"  {variant:32s} reviewed ({meta['attempts']} attempt(s))")
    rc = rce_llm.role_config(cfg, "REVIEW_AGENT")
    res = {"provider": rc["provider"], "model": rc.get("model") or rc.get("command"), **score_calibration(dims_by_variant, expected),
           "per_variant_dims": dims_by_variant, "runs": runs}
    out = Path(a.out) if a.out else rcs / "audits" / "reviewer_calibration.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    print(f"sensitivity {res['mean_dimension_sensitivity']} (>= {SENS_MIN}), false alarms {res['false_alarm_rate_on_A']} "
          f"(<= {FA_MAX}) -> {'CALIBRATED' if res['calibrated'] else 'NOT CALIBRATED: label its reviews exploratory'}")
    return 0 if res["calibrated"] else 1


# --------------------------------------------------------------------------------------------- run-tasks
def cmd_run_tasks(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    done = 0
    for d in sorted(p for p in Path(a.dir).iterdir() if (p / "prompt.md").exists()):
        if (d / "output.txt").exists():
            continue
        prompt = (d / "prompt.md").read_text(encoding="utf-8")
        system = "Follow the task below exactly. Reply with the requested content only."
        if a.json:
            obj, _ = rce_llm.complete_json(cfg, a.role, system, prompt, rcs=rcs)
            text = json.dumps(obj, ensure_ascii=False)
        else:
            text = rce_llm.complete(cfg, a.role, system, prompt, rcs=rcs)
        (d / "output.txt").write_text(text, encoding="utf-8")
        done += 1
        print(f"  {d.name}: {len(text)} chars")
    print(f"{done} task(s) run with role {a.role}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review")
    r.add_argument("--rcs", default=".rcs")
    r.add_argument("--round", required=True)
    r.add_argument("--packet")
    c = sub.add_parser("calibrate")
    c.add_argument("--rcs", default=".rcs")
    c.add_argument("--out")
    t = sub.add_parser("run-tasks")
    t.add_argument("dir")
    t.add_argument("--rcs", default=".rcs")
    t.add_argument("--role", default="READER")
    t.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        return {"review": cmd_review, "calibrate": cmd_calibrate, "run-tasks": cmd_run_tasks}[a.cmd](a)
    except rce_llm.ManualPending as exc:
        print(f"PENDING: {exc}")
        return 4
    except rce_llm.PolicyError as exc:
        print(f"REFUSED: {exc}")
        return 5


if __name__ == "__main__":
    sys.exit(main())
