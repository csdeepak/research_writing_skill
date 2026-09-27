#!/usr/bin/env python3
"""Audit how faithfully each skill-condition run executed the v0.1.0 workflow (process adherence).

For each run under evaluation/skill_agent/<P>/skill/ (and evidence_agent/<P>/skillpkg-*):
  - which core artifacts exist (anywhere under rcs/, since agents sometimes misplace them)
  - validator result on the run's .rcs (errors/warnings), after locating files
  - claim / limitation / evidence counts; spine present; story graph nodes
  - tool usage from stream logs: did the agent run validate_artifacts / lint_draft / build_review_packet?
  - accepted_risks recorded (no-human assumptions), open_issues length
  - final paper: residual claim tags, markers, words
Writes evaluation/results/skill_process_audit.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EV = ROOT / "evaluation"
sys.path.insert(0, str(ROOT / "tools"))
import validate_artifacts as VA  # noqa: E402

ARTS = {"research_evidence": "research_evidence.json", "claim_map": "claim_evidence_map.json",
        "story_graph": "story_graph.json", "spine": "spine.md", "architecture": "paper_architecture.md",
        "skeleton": "skeleton.md", "question_ledger": "question_ledger.json", "term_ledger": "term_ledger.json",
        "lit_gap_chain": "lit_gap_chain.md", "source_registry": "source_registry.json",
        "audience_profile": "audience_profile.json", "venue_profile": "venue_profile.yaml",
        "open_issues": "open_issues.md"}


def find(rcs: Path, name: str) -> Path | None:
    hits = sorted(rcs.rglob(name))
    return hits[0] if hits else None


def audit(run_dir: Path) -> dict:
    rcs = run_dir / "rcs"
    out: dict = {"run": str(run_dir.relative_to(EV))}
    if not rcs.exists():
        out["rcs"] = False
        return out
    arts = {k: (str(p.relative_to(rcs)).replace("\\", "/") if (p := find(rcs, v)) else None) for k, v in ARTS.items()}
    out["artifacts"] = arts
    out["artifact_coverage"] = round(sum(1 for v in arts.values() if v) / len(arts), 2)
    out["figure_cards"] = len(list(rcs.rglob("*card*")))
    out["audit_files"] = sorted(str(p.relative_to(rcs)).replace("\\", "/") for p in rcs.rglob("*") if p.is_file() and "audit" in str(p).lower())[:15]
    cm = find(rcs, "claim_evidence_map.json")
    if cm:
        try:
            d = json.loads(cm.read_text(encoding="utf-8"))
            cl = d.get("claims", [])
            out["n_claims"] = len(cl)
            out["claim_types"] = {t: sum(1 for c in cl if c.get("claim_type") == t) for t in
                                  ("measured", "observed", "derived", "literature", "interpretation", "hypothesis", "speculation", "future")}
            out["n_limitations"] = len(d.get("limitations", []))
            out["n_limitations_linked"] = sum(1 for l in d.get("limitations", []) if l.get("affects_claims"))
            out["negative_result_decisions"] = len(d.get("negative_result_decisions", []))
        except Exception as exc:  # noqa: BLE001
            out["claim_map_error"] = str(exc)[:200]
    re_ = find(rcs, "research_evidence.json")
    if re_:
        try:
            out["n_evidence"] = len(json.loads(re_.read_text(encoding="utf-8")).get("items", []))
        except Exception as exc:  # noqa: BLE001
            out["evidence_error"] = str(exc)[:200]
    # validator on a normalized copy of the expected layout
    rep = VA.Report()
    loaded = {}
    for rel, schema in VA.ARTIFACTS.items():
        p = find(rcs, Path(rel).name)
        if p:
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                loaded[rel] = data
                for e in VA.validate(data, VA.load_schema(schema)):
                    rep.add("ERROR", rel, e)
            except Exception as exc:  # noqa: BLE001
                rep.add("ERROR", rel, f"unreadable: {exc}")
    try:
        VA.check_references(rcs, run_dir / "_no_project_root", {k: v for k, v in loaded.items()}, rep)
    except Exception as exc:  # noqa: BLE001
        rep.add("ERROR", "check_references", str(exc)[:200])
    errs = [i for i in rep.items if i["level"] == "ERROR" and "locator path does not exist" not in i["message"]]
    out["validator_errors_excl_locators"] = len(errs)
    out["validator_error_examples"] = [f"{i['where']}: {i['message']}"[:160] for i in errs[:8]]
    st = find(rcs, "state.json")
    if st:
        try:
            s = json.loads(st.read_text(encoding="utf-8"))
            out["accepted_risks"] = len(s.get("accepted_risks", []))
            out["state_step"] = s.get("step") or s.get("current_step")
            out["gates"] = s.get("gates")
        except Exception as exc:  # noqa: BLE001
            out["state_error"] = str(exc)[:200]
    oi = find(rcs, "open_issues.md")
    if oi:
        out["open_issue_bullets"] = sum(1 for l in oi.read_text(encoding="utf-8").splitlines() if l.strip().startswith(("-", "*")))
    # tool usage
    tools = {"validate_artifacts": 0, "lint_draft": 0, "build_review_packet": 0, "snapshot": 0}
    reads = set()
    for s in run_dir.glob("*.stream.jsonl"):
        for line in s.read_text(encoding="utf-8", errors="replace").splitlines():
            if '"tool_use"' not in line:
                continue
            for k in tools:
                if k in line:
                    tools[k] += 1
            for m in re.findall(r"rce[\\/]+skill[\\/]+([\w/\\.-]+?\.md)", line):
                reads.add(m.replace("\\", "/"))
    out["tool_invocations"] = tools
    out["skill_files_read"] = sorted(reads)
    paper = run_dir / "paper.md"
    if paper.exists():
        t = paper.read_text(encoding="utf-8")
        out["paper_words_main"] = len(re.split(r"(?im)^#+\s*references\b", t)[0].split())
        out["residual_tags"] = len(re.findall(r"\{[CL]\d{3}", t))
        out["markers"] = len(re.findall(r"\[(MISSING|CITATION NEEDED|ASK AUTHOR)", t))
        out["has_limitations_section"] = bool(re.search(r"(?im)^#+.*limitation", t))
    return out


def main() -> None:
    runs = sorted(list((EV / "skill_agent").glob("*/skill")) + list((EV / "evidence_agent").glob("*/skillpkg-*")))
    res = [audit(r) for r in runs]
    (EV / "results").mkdir(exist_ok=True)
    (EV / "results" / "skill_process_audit.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for r in res:
        print(r["run"], "coverage", r.get("artifact_coverage"), "claims", r.get("n_claims"), "val_err", r.get("validator_errors_excl_locators"),
              "tools", r.get("tool_invocations"), "words", r.get("paper_words_main"), "tags", r.get("residual_tags"), "risks", r.get("accepted_risks"))


if __name__ == "__main__":
    main()
