#!/usr/bin/env python3
"""Run the RCE's single-shot roles on ANY model (bindings in .rcs/models.json; see tools/rce_llm.py).

  review     REVIEW_AGENT (workflow step 17) on a sanitized packet (tools/build_review_packet.py). Only the packet is
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
  panel      the five-seat review panel (workflow step 17b; skill/review_panel.md) on the same packet. The field analyst
             writes reviewer cards; each seat commits to its criteria from the card and the paper's metadata only, then
             reviews the packet against that commitment; the SYNTHESIZER merges. Every call is a fresh context. The tool
             stamps each review with its commitment's hash and the packet id, and tools/panel_check.py must agree with
             the decision. Role PANEL (or PANEL_<SEAT> for one seat) in .rcs/models.json.
               python tools/rce_roles.py panel --rcs .rcs --round v002_1 [--packet ...] [--verify-from v001_1]
  rebut      the devil's advocate scores the author's rebuttals (revisions/<round>/rebuttals.json) in a fresh call
               python tools/rce_roles.py rebut --rcs .rcs --round v002_1
  verify     the VERIFIER (workflow steps 15 and 20; agents/integrity_agent.md) on the bundle integrity_check.py collect
             wrote. It sees the draft and the project's records, so it is bound like any role that receives project text.
               python tools/rce_roles.py verify --rcs .rcs --stage pre [--round 1]

Roles that need file tools (CORPUS_AGENT, AUTHOR) are not run here: they run in whatever agent runtime you use
(adapters/). Every gate check (validate_artifacts, lint_draft, verify_numbers, visuals, g4_check, panel_check,
integrity_check) is deterministic and independent of the model.
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
import panel_check  # noqa: E402
import rce_llm  # noqa: E402
from rce_common import SKILL_DIR, load_json, load_schema, yaml_block  # noqa: E402

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


# ------------------------------------------------------------------------------------------------- panel
PANEL_DIR = SKILL_DIR / "agents" / "panel"


def _text(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _panel_role(cfg: dict, name: str) -> str:
    """A binding for one seat (PANEL_METHODOLOGY) wins over the panel's (PANEL); rce_llm then falls back to default."""
    specific = f"PANEL_{name.upper()}"
    return specific if specific in (cfg.get("roles") or {}) else "PANEL"


def _schema_block(name: str) -> str:
    return f"# OUTPUT SCHEMA ({name})\n{_text(SKILL_DIR / 'schemas' / name)}\n"


def _files_block(files: dict[str, str]) -> str:
    return "".join(f"\n## FILE {n}\n\n{t}\n" for n, t in sorted(files.items()))


def _seat_system(seat: str) -> str:
    return _text(PANEL_DIR / "seat_protocol.md") + "\n\n" + _text(PANEL_DIR / f"{seat}.md")


def _venue_context(rcs: Path) -> dict:
    """Public facts about the venue and the paper type. Nothing from the project's records reaches the panel."""
    ctx: dict = {}
    cfg = rcs / "plan" / "paper_config.json"
    if cfg.exists():
        c = load_json(cfg)
        ctx.update({k: c[k] for k in ("venue", "paper_type") if c.get(k)})
    vp = rcs / "plan" / "venue_profile.yaml"
    if vp.exists():
        text = _text(vp)
        venue = yaml_block(text, "venue")
        if isinstance(venue, dict) and venue.get("name"):
            ctx["venue"] = venue["name"]
        crit = yaml_block(text, "review_criteria")
        if crit:
            ctx["published_review_criteria"] = crit
    return ctx


def _metadata(files: dict[str, str], cards: dict, ctx: dict) -> dict:
    paper = files.get("paper.md", "")
    title = next((l.lstrip("#").strip() for l in paper.splitlines() if l.startswith("# ")), "")
    return {"title": title, "field": cards.get("field"), "subfield": cards.get("subfield"), "venue": ctx.get("venue"),
            "article_type": cards.get("article_type"), "word_count": len(paper.split())}


def _write(p: Path, obj) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    return p


def _record(rcs: Path, role: str, paths: list[Path]) -> None:
    if (rcs / "provenance.jsonl").exists():
        import workflow_guard
        workflow_guard.record(rcs, role, [str(p) for p in paths])


def _check_with(schema_name: str, extra):
    schema = load_schema(schema_name)

    def check(obj) -> list[str]:
        if not isinstance(obj, dict):
            return ["reply with one JSON object"]
        return [f"schema: {e}" for e in rce_llm.validate(obj, schema)] + extra(obj)
    return check


def _cards_extra(obj: dict) -> list[str]:
    seats = [c.get("seat") for c in obj.get("cards", []) if isinstance(c, dict)]
    errs = [f"no card for seat {s}" for s in panel_check.SEATS if s not in seats]
    errs += [f"two cards for seat {s}" for s in set(seats) if seats.count(s) > 1]
    for c in obj.get("cards", []):
        prefix = panel_check.PREFIX.get(c.get("seat"), "")
        errs += [f"{c.get('seat')}: criterion id {x.get('id')} must start with {prefix}" for x in c.get("criteria", []) if not str(x.get("id", "")).startswith(prefix)]
    return errs


def _seat_extra(seat: str, phase: str, card: dict, roadmap: list | None = None):
    own = {c["id"] for c in card.get("criteria", [])}

    def extra(obj: dict) -> list[str]:
        errs = []
        if obj.get("seat") != seat or obj.get("phase") != phase:
            errs.append(f'set "seat": "{seat}" and "phase": "{phase}"')
        if phase == "commitment":
            errs += [f"commit to criterion {c}" for c in sorted(own - {p.get('criterion_id') for p in obj.get('plan', [])})]
        if phase == "review":
            judged = {c.get("criterion_id") for c in obj.get("criteria", [])}
            errs += [f"judge criterion {c}" for c in sorted(own - judged)]
        if phase == "verification":
            done = {c.get("roadmap_id") for c in obj.get("checks", [])}
            errs += [f"check roadmap item {r['id']}" for r in roadmap or [] if r.get("id") not in done]
        errs += [f"finding id {f.get('id')} must start with {panel_check.PREFIX[seat]}-" for f in obj.get("findings", [])
                 if not str(f.get("id", "")).startswith(panel_check.PREFIX[seat] + "-")]
        return errs
    return extra


def _synth_extra(findings: dict[str, dict], judgements: list[str], paper: str, kind: str, roadmap_prev: list, checks: dict):
    def extra(obj: dict) -> list[str]:
        errs = []
        sev = panel_check.effective(findings, obj)
        derived = panel_check.derive_full(sev, judgements) if kind == "full" else panel_check.derive_verification(roadmap_prev, checks, sev)
        if obj.get("kind") != kind:
            errs.append(f'set "kind": "{kind}"')
        if obj.get("decision") != derived:
            errs.append(f"by the decision rule these findings give {derived!r}, not {obj.get('decision')!r}")
        known = set(findings) | {x for r in roadmap_prev for x in r.get("from_findings", [])}
        for r in obj.get("roadmap", []):
            errs += [f"roadmap {r.get('id')} cites {x}, which no seat reported" for x in r.get("from_findings", []) if x not in known]
        norm = panel_check._norm(paper)
        errs += [f"downgrade of {d.get('finding_id')}: the quote must be copied from the paper" for d in obj.get("downgrades", []) or []
                 if panel_check._norm(d.get("quote", "")) not in norm]
        return errs
    return extra


def _ask(cfg: dict, rcs: Path, role: str, system: str, user: str, check) -> dict:
    obj, meta = rce_llm.complete_json(cfg, role, system, user, rcs=rcs, check=check)
    return obj


def panel_round(cfg: dict, rcs: Path, rnd: str, packet: Path, verify_from: str | None = None) -> dict:
    files = packet_files(packet)
    pid = json.loads(_text(packet / "packet_manifest.json"))["packet_id"]
    root = rcs / "diagnostics" / rnd
    pdir = root / "panel"
    written: list[Path] = []
    paper = files.get("paper.md", "")
    seat_schema = _schema_block("panel_review.schema.json")
    if verify_from:
        prev = rcs / "diagnostics" / verify_from
        cards_text = _text(prev / "panel" / "cards.json")
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "cards.json").write_text(cards_text, encoding="utf-8")       # the same standard as the round it checks
        written.append(pdir / "cards.json")
        cards = json.loads(cards_text)
        roadmap = load_json(prev / "editorial_decision.json").get("roadmap", [])
    else:
        ctx = _venue_context(rcs)
        user = (_schema_block("reviewer_cards.schema.json") + "\n# CONTEXT\n" + json.dumps(ctx, indent=1)
                + "\n\n# THE PACKET (read it only to place the paper)" + _files_block(files) + "\nReply with ONE JSON object.")
        cards = _ask(cfg, rcs, _panel_role(cfg, "field_analyst"), _text(PANEL_DIR / "field_analyst.md"), user,
                     _check_with("reviewer_cards.schema.json", _cards_extra))
        written.append(_write(pdir / "cards.json", cards))
        roadmap = []
    by_seat = panel_check._cards(cards)
    meta = _metadata(files, cards, _venue_context(rcs))
    findings: dict[str, dict] = {}
    judgements: list[str] = []
    checks: dict[str, str] = {}
    for seat in panel_check.SEATS:
        card = by_seat[seat]
        role, system = _panel_role(cfg, seat), _seat_system(seat)
        if verify_from:
            commitment = _text(rcs / "diagnostics" / verify_from / "panel" / f"{seat}.commitment.json")
            user = (seat_schema + f"\n# PHASE 3: verification\n## Your card\n{json.dumps(card, indent=1)}\n## Your round-1 commitment\n{commitment}\n"
                    f"## The previous roadmap\n{json.dumps(roadmap, indent=1)}\n\n# THE PACKET" + _files_block(files) + "\nReply with ONE JSON object.")
            out = _ask(cfg, rcs, role, system, user, _check_with("panel_review.schema.json", _seat_extra(seat, "verification", card, roadmap)))
            out["packet_id"] = pid
            written.append(_write(pdir / f"{seat}.verification.json", out))
            for c in out.get("checks", []):
                rid = c.get("roadmap_id")
                if panel_check.CHECK_RANK.get(c.get("verdict"), 2) >= panel_check.CHECK_RANK.get(checks.get(rid, "addressed"), 0):
                    checks[rid] = c.get("verdict")
        else:
            # Phase 1 sees the card and the metadata only. The paper is not in this prompt: that is the point.
            user = (seat_schema + f"\n# PHASE 1: commitment (you have not seen the paper)\n## Your card\n{json.dumps(card, indent=1)}\n"
                    f"## The paper's metadata\n{json.dumps(meta, indent=1)}\n\nReply with ONE JSON object.")
            commitment = _ask(cfg, rcs, role, system, user, _check_with("panel_review.schema.json", _seat_extra(seat, "commitment", card)))
            cp = _write(pdir / f"{seat}.commitment.json", commitment)
            written.append(cp)
            user = (seat_schema + f"\n# PHASE 2: review\n## Your card\n{json.dumps(card, indent=1)}\n## Your commitment, as recorded\n{_text(cp)}\n\n"
                    "# THE PACKET (the only files you may use)" + _files_block(files) + "\nReply with ONE JSON object.")
            out = _ask(cfg, rcs, role, system, user, _check_with("panel_review.schema.json", _seat_extra(seat, "review", card)))
            out["commitment_sha256"], out["packet_id"] = panel_check.sha_file(cp), pid
            written.append(_write(pdir / f"{seat}.review.json", out))
            judgements += [c.get("judgement") for c in out.get("criteria", [])]
        for f in out.get("findings", []):
            findings[f["id"]] = {**f, "seat": seat}
    kind = "verification" if verify_from else "full"
    reports = {p.name: _text(p) for p in sorted(pdir.glob(f"*.{'verification' if verify_from else 'review'}.json"))}
    user = (_schema_block("editorial_decision.schema.json") + f"\n# KIND: {kind}" + (f" (previous_round: {verify_from})" if verify_from else "")
            + ("\n## The previous roadmap\n" + json.dumps(roadmap, indent=1) if verify_from else "")
            + "\n\n# THE SEAT REPORTS" + _files_block(reports) + "\n\n# THE PAPER (only to check a quote)\n" + paper + "\nReply with ONE JSON object.")
    decision = _ask(cfg, rcs, _panel_role(cfg, "synthesizer"), _text(PANEL_DIR / "synthesizer.md"), user,
                    _check_with("editorial_decision.schema.json", _synth_extra(findings, judgements, paper, kind, roadmap, checks)))
    if verify_from:
        decision["previous_round"] = verify_from
    written.append(_write(root / "editorial_decision.json", decision))
    _record(rcs, "PANEL", written)
    items, summary = panel_check.check_round(rcs, rnd, pid)
    return {"decision": decision["decision"], "findings": len(findings), "blocking": summary["blocking"],
            "problems": [i for i in items if i[0] == "ERROR"]}


def cmd_panel(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    packet = Path(a.packet) if a.packet else rcs / "packets" / f"review_{a.round}"
    res = panel_round(cfg, rcs, a.round, packet, a.verify_from)
    print(f"panel {a.round}: decision {res['decision'].upper()}, {res['findings']} finding(s), {len(res['blocking'])} blocking")
    for level, code, msg in res["problems"]:
        print(f"{level:5} {code:28} {msg}")
    if res["decision"] == "reject":
        print("PANEL_REJECT: show the user the fatal findings and the options (back to P1 or P3, another venue, or stop).")
    return 1 if res["problems"] else 0


def cmd_rebut(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    pdir = rcs / "diagnostics" / a.round / "panel"
    rebuttals = load_json(rcs / "revisions" / a.round / "rebuttals.json").get("rebuttals", [])
    review = load_json(pdir / "devils_advocate.review.json")
    asked = [r.get("finding_id") for r in rebuttals]
    findings = [f for f in review.get("findings", []) if f.get("id") in asked]
    packet = rcs / "packets" / f"review_{a.round}"
    paper = _text(packet / "paper.md") if (packet / "paper.md").exists() else ""

    def extra(obj: dict) -> list[str]:
        got = [s.get("finding_id") for s in obj.get("scores", [])]
        errs = [] if obj.get("phase") == "rebuttal" and obj.get("seat") == "devils_advocate" else ['set "seat": "devils_advocate", "phase": "rebuttal"']
        return errs + ([] if got == asked else [f"score exactly these findings, in this order: {asked}"])

    user = (_schema_block("panel_review.schema.json") + "\n# PHASE: rebuttal (score each rebuttal, in this order)\n## Your findings\n"
            + json.dumps(findings, indent=1) + "\n## The author's rebuttals\n" + json.dumps(rebuttals, indent=1) + "\n\n# THE PAPER\n" + paper
            + "\nReply with ONE JSON object.")
    obj = _ask(cfg, rcs, _panel_role(cfg, "devils_advocate"), _seat_system("devils_advocate"), user,
               _check_with("panel_review.schema.json", extra))
    p = _write(pdir / "devils_advocate.rebuttal.json", obj)
    _record(rcs, "PANEL", [p])
    counted = panel_check.rebuttal_outcomes(obj.get("scores", []))
    for fid, score in counted.items():
        print(f"  {fid}: counts as {score}/5")
    return 0


# ------------------------------------------------------------------------------------------------ verify
def cmd_verify(a) -> int:
    rcs = Path(a.rcs)
    cfg = rce_llm.load_config(rcs)
    d = rcs / "audits" / "integrity" / a.stage
    bundle = load_json(d / "bundle.json")
    draft = next((p for p in (Path(bundle["draft"]), rcs.resolve().parent / bundle["draft"]) if p.exists()), None)
    if draft is None:
        print(f"ERROR the bundle's draft {bundle['draft']} is not on disk")
        return 1
    parts = [_schema_block("integrity_report.schema.json"), "# THE BUNDLE\n" + json.dumps(bundle, indent=1, ensure_ascii=False),
             "\n# THE TAGGED DRAFT\n" + _text(draft)]
    for rel in ("claims/claim_evidence_map.json", "evidence/research_evidence.json", "story/spine.md", "story/alternatives.md", "story/rq_check.md"):
        if (rcs / rel).exists():
            parts.append(f"\n# .rcs/{rel}\n" + _text(rcs / rel))
    state = load_json(rcs / "state.json") if (rcs / "state.json").exists() else {}
    parts.append("\n# state.json story_changes\n" + json.dumps(state.get("story_changes", []), indent=1))
    parts.append("\nYou cannot open other files in this call: where a judgment needs a file you were not given, say so and use "
                 "INSUFFICIENT_EVIDENCE. Reply with ONE JSON object.")
    rows = {r["id"] for r in bundle.get("alignment_rows", [])}

    def extra(obj: dict) -> list[str]:
        judged = {x.get("row") for x in obj.get("alignment", []) if isinstance(x, dict)}
        return [f"judge alignment row {r}" for r in sorted(rows - judged)]

    obj, meta = rce_llm.complete_json(cfg, "VERIFIER", _text(SKILL_DIR / "agents" / "integrity_agent.md"), "\n".join(parts), rcs=rcs,
                                      check=_check_with("integrity_report.schema.json", extra))
    obj.update(draft_sha256=bundle["draft_sha256"], round=a.round, isolation="isolated")    # set by the tool, not the model
    p = _write(d / "verifier_report.json", obj)
    _record(rcs, "VERIFIER", [p])
    print(f"VERIFIER ({a.stage}, round {a.round}): " + ", ".join(f"{m}={v['status']}" for m, v in sorted(obj["modes"].items()))
          + f"; {len(obj.get('alignment', []))} row(s) judged. Now run integrity_check.py gate.")
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
    p = sub.add_parser("panel")
    p.add_argument("--rcs", default=".rcs")
    p.add_argument("--round", required=True)
    p.add_argument("--packet")
    p.add_argument("--verify-from", help="the earlier round whose roadmap this re-review checks")
    b = sub.add_parser("rebut")
    b.add_argument("--rcs", default=".rcs")
    b.add_argument("--round", required=True)
    v = sub.add_parser("verify")
    v.add_argument("--rcs", default=".rcs")
    v.add_argument("--stage", required=True, choices=["pre", "final"])
    v.add_argument("--round", type=int, default=1)
    a = ap.parse_args(argv)
    try:
        return {"review": cmd_review, "calibrate": cmd_calibrate, "run-tasks": cmd_run_tasks, "panel": cmd_panel,
                "rebut": cmd_rebut, "verify": cmd_verify}[a.cmd](a)
    except rce_llm.ManualPending as exc:
        print(f"PENDING: {exc}")
        return 4
    except rce_llm.PolicyError as exc:
        print(f"REFUSED: {exc}")
        return 5
    except (FileNotFoundError, KeyError) as exc:
        print(f"ERROR: a required input is missing: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
