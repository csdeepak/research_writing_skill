#!/usr/bin/env python3
"""Phase 6: grade each evidence package against the frozen gold nuggets (package-level, before writing).

For every gold nugget: covered | partial | missing | contradicted, plus whether the package's claim type
for that fact matches the gold strength (type_match | type_stronger | type_weaker | n/a).
Grader = Claude Sonnet (no tools); sees gold + package only; tier label hidden (random id).
Usage: python evidence_grade.py run | analyze
"""
from __future__ import annotations

import json
import secrets
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402
from run_model import run  # noqa: E402

EV = RL.ROOT / "evaluation"
OUT = EV / "evidence_agent" / "gold_coverage"
PROJECTS = ["SWE_BENCH", "WHISPER", "OPENHANDS"]
SYSTEM = """You are an evidence auditor. You compare an evidence package (extracted from a research paper by an
automated agent) against a researcher-verified list of gold facts ("nuggets") about the same paper.
You never see the paper. Judge meaning, not wording. Numbers must match exactly (unit conversions such as
1.96% = 0.0196 count as matching). Be strict and consistent; when unsure pick the less favorable label.
Strength ladder: measured > derived > observed > literature > interpretation > hypothesis > speculation > future;
"context" nuggets have no strength requirement."""
FMT = """## OUTPUT FORMAT (mandatory)
Reply with ONE JSON object only (no fences):
{"nuggets": {"<nugget id>": {"coverage": "covered|partial|missing|contradicted",
                              "type": "type_match|type_stronger|type_weaker|n/a",
                              "package_ids": ["E..."|"C..."], "note": "..."}, ... EVERY gold nugget id exactly once},
 "package_errors": [{"id": "E...", "problem": "factual error / unsupported / misclassified strength", "detail": "..."}],
 "notes": "..."}
"type": compare the package's claim_type / evidence kind for that fact with the nugget strength
(type_stronger = package states it as stronger evidence than gold, e.g. an interpretation recorded as measured)."""


def job(project: str, tier: str) -> str:
    out = OUT / f"{project}__{tier}.txt"
    if out.exists():
        return f"skip {out.name}"
    pkg = EV / "evidence_agent" / "packages" / tier / project
    gold = json.loads((EV / "ground_truth" / project / "gold_story.v1.json").read_text(encoding="utf-8"))
    rid = f"pkg-{secrets.token_hex(3)}"
    user = (f"# GOLD NUGGETS\n{json.dumps(gold['questions'], indent=1, ensure_ascii=False)}\n\n# EVIDENCE PACKAGE {rid}\n"
            f"## research_evidence.json\n{(pkg / 'research_evidence.json').read_text(encoding='utf-8')}\n\n"
            f"## claim_candidates.json\n{(pkg / 'claim_candidates.json').read_text(encoding='utf-8')}\n\n{FMT}")
    rec = run(f"EVG-{project}-{tier}", "evidence_grader", "claude", "sonnet", SYSTEM, user, out, timeout=1800)
    return f"{rec['status']} {out.name}"


def analyze() -> dict:
    res = {}
    for p in PROJECTS:
        gold = json.loads((EV / "ground_truth" / p / "gold_story.v1.json").read_text(encoding="utf-8"))
        ids = [n["id"] for ns in gold["questions"].values() for n in ns]
        for t in ("cheap", "strong"):
            f = OUT / f"{p}__{t}.txt"
            if not f.exists():
                continue
            d = RL.extract_json(f.read_text(encoding="utf-8"))
            ng = d.get("nuggets", {})
            cov = [ng.get(i, {}).get("coverage", "missing") for i in ids]
            typ = [ng.get(i, {}).get("type", "n/a") for i in ids]
            n = len(ids)
            res[f"{p}/{t}"] = {
                "nuggets": n,
                "coverage_rate": round((cov.count("covered") + 0.5 * cov.count("partial")) / n, 3),
                "covered": cov.count("covered"), "partial": cov.count("partial"),
                "missing": cov.count("missing"), "contradicted": cov.count("contradicted"),
                "type_match": typ.count("type_match"), "type_stronger": typ.count("type_stronger"),
                "type_weaker": typ.count("type_weaker"),
                "package_errors": len(d.get("package_errors", [])),
                "missing_ids": [i for i, c in zip(ids, cov) if c == "missing"],
            }
    (EV / "evidence_agent" / "gold_coverage_summary.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    return res


if __name__ == "__main__":
    if sys.argv[1] == "run":
        with ThreadPoolExecutor(max_workers=3) as ex:
            for m in ex.map(lambda j: job(*j), [(p, t) for p in PROJECTS for t in ("cheap", "strong")]):
                print(m, flush=True)
    else:
        print(json.dumps(analyze(), indent=1))
