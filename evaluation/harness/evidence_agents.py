#!/usr/bin/env python3
"""Phase 6: cheap vs strong CORPUS_AGENT (mode=evidence) on the same frozen snapshot.

  run <PROJECT> <cheap|strong>   : headless claude session (Haiku / Opus) in an isolated workspace
                                  reading only the snapshot; writes the evidence package
  score <PROJECT>                : objective package metrics (numeric grounding vs paper text,
                                  hallucinated numbers, counts by kind/claim_type, schema validity);
                                  gold-coverage grading is done separately by the grader.
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import writers as W  # noqa: E402
from rce_common import load_schema, validate  # noqa: E402

EV = W.EV
MODELS = {"cheap": "haiku", "strong": "opus"}

PROMPT = """You are the CORPUS_AGENT of the Research Communication Engine. Your full role instructions are in
./rce/skill/agents/corpus_agent.md and the evidence model in ./rce/skill/evidence_model.md — read both first.

Run mode = `evidence` on project_root = ./project/ (official paper text `paper.txt` + README(s)), out_dir = ./out/.
Produce exactly these files (valid JSON; schemas in ./rce/skill/schemas/):
  ./out/research_evidence.json   (schema research_evidence.schema.json; locator.path must be "paper.txt" or a README
                                  file name, anchor = section/table/page text)
  ./out/claim_candidates.json    ({"claims": [...]} using the claim fields of claim_evidence_map.schema.json:
                                  id, statement, claim_type, evidence, confidence, author_confirmation="pending",
                                  plus "origin": author_stated|inferred and "quote" (<=25 words) for author_stated)
  ./out/missing_evidence.json    ({"missing": [{"what": "...", "why_it_matters": "...", "location": "..."}]})
  ./out/RUN_SUMMARY.md
Constraints: no web; no subagents; work only inside this directory; copy numbers verbatim; never upgrade strength;
record negative results and author-stated limitations; mark conflicts. Do not read ./rce/skill/agents/review_agent.md,
recon_grader.md or skill_agent.md. Reply DONE when finished."""


def run_agent(project: str, tier: str) -> dict:
    w = W.WS_ROOT / f"{project}__evidence_{tier}"
    if w.exists():
        raise SystemExit(f"workspace exists: {w}")
    (w / "project").mkdir(parents=True)
    snap = EV / "external_projects" / project / "snapshot"
    shutil.copy2(snap / "paper.txt", w / "project" / "paper.txt")
    for i, r in enumerate(sorted(snap.glob("README__*.md")), 1):
        shutil.copy2(r, w / "project" / f"README_{i}.md")
    (w / "rce" / "skill").mkdir(parents=True)
    for rel in ["agents/corpus_agent.md", "evidence_model.md", "schemas"]:
        src = W.ROOT / "skill" / rel
        dst = w / "rce" / "skill" / rel
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    (w / "out").mkdir()
    old = W.WRITER_MODEL
    W.WRITER_MODEL = MODELS[tier]
    try:
        rec = W.run_session(f"EVID-{project}-{tier}", w, PROMPT, timeout=5400)
    finally:
        W.WRITER_MODEL = old
    dest = EV / "evidence_agent" / tier / project
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(w / "out", dest)
    for s in w.parent.glob(f"{w.name}__*.stream.jsonl"):
        shutil.copy2(s, dest / "session.stream.jsonl")
    return rec


NUM_RE = re.compile(r"(?<![\w.])-?\d+(?:[.,]\d+)*(?:\.\d+)?")


def numbers_in(obj) -> list[str]:
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("id", "evidence", "conflicts_with", "derived_from", "locator"):
                continue
            out += numbers_in(v)
    elif isinstance(obj, list):
        for v in obj:
            out += numbers_in(v)
    elif isinstance(obj, (int, float)) and not isinstance(obj, bool):
        out.append(repr(obj))
    elif isinstance(obj, str):
        out += NUM_RE.findall(obj)
    return out


def norm_num(s: str) -> str:
    s = s.replace(",", "")
    try:
        f = float(s)
    except ValueError:
        return s
    return ("%.6f" % f).rstrip("0").rstrip(".")


def score(project: str) -> dict:
    paper = (EV / "external_projects" / project / "snapshot" / "paper.txt").read_text(encoding="utf-8", errors="replace")
    readmes = " ".join(p.read_text(encoding="utf-8", errors="replace")
                       for p in (EV / "external_projects" / project / "snapshot").glob("README__*.md"))
    source_nums = {norm_num(n) for n in NUM_RE.findall(paper + " " + readmes)}
    res = {}
    for tier in ("cheap", "strong"):
        d = EV / "evidence_agent" / tier / project
        r = {"present": d.exists()}
        if not d.exists():
            res[tier] = r
            continue
        try:
            ev = json.loads((d / "research_evidence.json").read_text(encoding="utf-8"))
            r["evidence_schema_errors"] = len(validate(ev, load_schema("research_evidence.schema.json")))
            items = ev.get("items", [])
            r["n_evidence"] = len(items)
            kinds = {}
            for it in items:
                kinds[it.get("kind")] = kinds.get(it.get("kind"), 0) + 1
            r["kinds"] = kinds
            r["n_negative_results"] = kinds.get("negative_result", 0)
            r["n_limitations_noted"] = kinds.get("limitation_noted", 0)
            nums = [n for it in items for n in numbers_in({k: it.get(k) for k in ("value", "summary", "conditions")})]
            nn = [norm_num(n) for n in nums if len(n.replace(".", "").replace(",", "").lstrip("-")) >= 2]
            ungrounded = sorted({n for n in nn if n not in source_nums})
            r["numbers_checked"] = len(nn)
            r["numbers_not_in_source"] = len([n for n in nn if n not in source_nums])
            r["numeric_grounding_rate"] = round(1 - r["numbers_not_in_source"] / len(nn), 4) if nn else None
            r["ungrounded_examples"] = ungrounded[:25]
            r["strength_counts"] = {s: sum(1 for it in items if it.get("strength") == s) for s in ("hard", "soft")}
        except Exception as exc:  # noqa: BLE001
            r["evidence_error"] = str(exc)
        try:
            cc = json.loads((d / "claim_candidates.json").read_text(encoding="utf-8"))
            claims = cc.get("claims", [])
            r["n_claims"] = len(claims)
            r["claim_types"] = {t: sum(1 for c in claims if c.get("claim_type") == t) for t in
                                ("measured", "observed", "derived", "literature", "interpretation", "hypothesis",
                                 "speculation", "future")}
            ev_ids = {it.get("id") for it in ev.get("items", [])} if "items" in ev else set()
            r["claims_with_unresolved_evidence"] = sum(1 for c in claims if any(
                e.startswith("E") and e not in ev_ids for e in c.get("evidence", [])))
            r["claims_without_evidence_needing_it"] = sum(1 for c in claims if c.get("claim_type") in
                                                         ("measured", "observed", "derived") and not c.get("evidence"))
        except Exception as exc:  # noqa: BLE001
            r["claims_error"] = str(exc)
        try:
            r["n_missing"] = len(json.loads((d / "missing_evidence.json").read_text(encoding="utf-8")).get("missing", []))
        except Exception as exc:  # noqa: BLE001
            r["missing_error"] = str(exc)
        res[tier] = r
    out = EV / "evidence_agent" / f"objective_scores_{project}.json"
    out.write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "run":
        print(json.dumps(run_agent(sys.argv[2], sys.argv[3])))
    elif sys.argv[1] == "score":
        print(json.dumps(score(sys.argv[2]), indent=1))
