#!/usr/bin/env python3
"""Phase 5/6 writers: plain agent vs Research Communication Skill, identical conditions.

Constants across conditions: project snapshot, base model (Claude Sonnet via headless `claude -p`),
tools (Read, Write, Edit, Glob, Grep, Bash(python *)), no web, same task/audience/requirements text,
workspace outside the repo, permission-mode dontAsk. Only difference: skill files present + skill instruction.

Every session is run with stream-json so all tool calls are logged; any file access outside the
workspace is flagged as ISOLATION_BREACH in the audit.

Usage:
  python writers.py prep <PROJECT> <condition>          # condition: plain | skill | skillpkg-cheap | skillpkg-strong
  python writers.py plain <PROJECT>
  python writers.py skill-draft <PROJECT> [--cond skill]
  python writers.py skill-review <PROJECT> [--cond skill]
  python writers.py skill-revise <PROJECT> [--cond skill]
  python writers.py collect <PROJECT> <condition>
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_lib as RL  # noqa: E402
from run_model import LOG, run  # noqa: E402

ROOT = RL.ROOT
EV = ROOT / "evaluation"
import os, tempfile  # noqa: E401
WS_ROOT = Path(os.environ.get("RCE_TMP", tempfile.gettempdir())) / "rce_ws"   # outside the repository (override with RCE_TMP)
WRITER_MODEL = "sonnet"
TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash(python *)", "Bash(python3 *)", "PowerShell(python *)"]

AUDIENCE = ("Machine-learning researchers from OTHER subfields (adjacent researchers): they know general ML, "
            "deep learning, standard evaluation practice and statistics, but not this project's subfield-specific "
            "terminology, datasets or prior work.")

TASK_COMMON = f"""You are given a research project folder at ./project/. It contains the official evidence for one
research project: `paper.txt` (text extracted from the project's official research paper; tables and figures may be
damaged by extraction) and `README_*.md` (the official repository README(s)).

TASK: Write a research paper that presents this project's research to the audience below, as a standalone
Markdown file at ./paper.md.

AUDIENCE: {AUDIENCE}

REQUIREMENTS (all mandatory):
- Length: 3,000–4,500 words of main text (excluding references).
- Structure: a complete research paper with title, abstract and the sections you judge appropriate.
- Tables may be written in Markdown. No images.
- Use only the evidence in ./project/. Do not use outside knowledge about this project, and do not use the web.
- Cite only works that are cited in the project materials, in the form (FirstAuthor et al., Year) as they appear there.
- Report numbers exactly as they appear in the evidence.
- You are presenting the authors' research; you are not reviewing it.
- Work only inside the current directory. Do not read or write any file outside it.
"""

PLAIN_PROMPT = TASK_COMMON + "\nWhen ./paper.md is complete, reply with DONE and the word count."

SKILL_PROMPT = TASK_COMMON + """
METHOD: Use the Research Communication Engine skill in ./rce/skill/ (entry point ./rce/skill/SKILL.md; tools in
./rce/tools/, run with python). Follow its workflow from step 1 through step 17, writing its artifacts under ./.rcs/.

Run-specific constraints (these override the skill where they conflict):
- No human is available. Wherever the skill says ASK or STOP for user input, choose the most defensible option
  from the evidence, record the assumption in ./.rcs/state.json (accepted_risks) and continue.
- There are no subagents. Perform the CORPUS_AGENT role yourself (you may read ./rce/skill/agents/corpus_agent.md).
  Do NOT read ./rce/skill/agents/review_agent.md, recon_grader.md or skill_agent.md.
- No web: literature mode is limited to works cited in ./project/paper.txt; register them with
  verification.method = "user_supplied_file" and read_depth = "abstract" (you cannot read them).
- Step 18 (blind review) is performed externally. After step 17, write the current draft to
  ./.rcs/drafts/v001/paper.md (claim tags kept) and ALSO to ./paper.md, write ./.rcs/packets/audience.md and
  ./.rcs/packets/objective.md per ./rce/skill/templates/packet_audience_objective.md, then stop and reply DONE.
"""

SKILL_PKG_NOTE = """
EVIDENCE INTERFACE FOR THIS RUN: ./project/ contains ONLY an evidence package produced by a separate evidence agent
(files: research_evidence.json, claim_candidates.json, missing_evidence.json, and possibly a notes file). The
original paper is NOT available. Treat the package as the output of workflow steps 1-2 (copy it into ./.rcs/ at the
paths the skill expects) and continue from step 3. Evidence locators refer to the original paper, which you cannot
open; do not treat unresolvable locators as errors. Everything else in the instructions above still applies,
with "evidence in ./project/" meaning the package.
"""

REVISE_PROMPT = """Continue the Research Communication Engine workflow (./rce/skill/SKILL.md) for the project in this
directory. State is in ./.rcs/. The external blind review (step 18) is complete: structured diagnostics are in
./.rcs/diagnostics/v001_1/diagnostics.json and reconstruction.json. Perform step 19 (revise, structure first, fix via
artifacts) and then step 21 (final language editing, claim-invariance check, strip tags). Skip step 20 (no further
review rounds in this run). Same run-specific constraints as before: no human (record assumptions in
./.rcs/state.json), no web, no subagents, do not read ./rce/skill/agents/review_agent.md, recon_grader.md or
skill_agent.md, work only inside this directory. Write the final manuscript to ./paper.md (no claim tags; keep any
[MISSING …]/[CITATION NEEDED …] markers that remain genuinely unresolved) and ./.rcs/open_issues.md.
All original task requirements (audience, 3,000–4,500 words, evidence-only, citations) still apply.
Reply DONE when finished."""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ws(project: str, cond: str) -> Path:
    return WS_ROOT / f"{project}__{cond}"


def prep(project: str, cond: str, package_dir: Path | None = None) -> Path:
    w = ws(project, cond)
    if w.exists():
        raise SystemExit(f"workspace exists: {w}")
    (w / "project").mkdir(parents=True)
    if package_dir:
        for f in package_dir.iterdir():
            if f.is_file():
                shutil.copy2(f, w / "project" / f.name)
    else:
        snap = EV / "external_projects" / project / "snapshot"
        shutil.copy2(snap / "paper.txt", w / "project" / "paper.txt")
        for i, r in enumerate(sorted(snap.glob("README__*.md")), 1):
            shutil.copy2(r, w / "project" / f"README_{i}.md")
    if cond != "plain":
        shutil.copytree(ROOT / "skill", w / "rce" / "skill", ignore=shutil.ignore_patterns("versions", "__pycache__"))
        shutil.copytree(ROOT / "tools", w / "rce" / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    return w


def run_session(exp_id: str, w: Path, prompt: str, timeout: int = 5400) -> dict:
    t0 = time.time()
    rec = {"exp_id": exp_id, "role": "writer", "provider": "claude", "model_requested": WRITER_MODEL,
           "started": now(), "workspace": str(w)}
    cmd = [shutil.which("claude"), "-p", "--model", WRITER_MODEL, "--output-format", "stream-json", "--verbose",
           "--no-session-persistence", "--setting-sources", "", "--permission-mode", "dontAsk",
           "--allowedTools", *TOOLS]
    logf = w.parent / f"{w.name}__{exp_id}.stream.jsonl"
    try:
        with open(logf, "w", encoding="utf-8") as fh:
            proc = subprocess.run(cmd, input=prompt, stdout=fh, stderr=subprocess.PIPE, text=True,
                                  encoding="utf-8", cwd=w, timeout=timeout)
        rec["returncode"] = proc.returncode
        rec["stderr_tail"] = proc.stderr[-300:]
    except subprocess.TimeoutExpired:
        rec["returncode"] = "timeout"
    audit = audit_stream(logf, w)
    rec.update(audit)
    rec["status"] = "ok" if audit.get("result_ok") else "failed"
    rec.update(ended=now(), seconds=round(time.time() - t0, 1))
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec) + "\n")
    return rec


def audit_stream(logf: Path, w: Path) -> dict:
    tool_calls, outside, denied = 0, [], 0
    result_ok, cost, usage, models = False, None, {}, set()
    wsn = str(w).replace("\\", "/").lower()
    for line in logf.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("type") == "assistant":
            msg = ev.get("message", {})
            if msg.get("model"):
                models.add(msg["model"])
            for c in msg.get("content", []):
                if c.get("type") == "tool_use":
                    tool_calls += 1
                    inp = json.dumps(c.get("input", {})).replace("\\\\", "/").lower()
                    for p in re.findall(r'(?<![a-z])[a-z]:/[^"\s]+', inp):
                        if not p.startswith(wsn) and not p.startswith(str(WS_ROOT).replace("\\", "/").lower()):
                            outside.append(p[:160])
                    if "research_writing_skill" in inp or "ground_truth" in inp:
                        outside.append("REPO-PATH:" + inp[:160])
                    for forbidden in ("review_agent.md", "recon_grader.md", "skill_agent.md", "expected.json"):
                        if forbidden in inp and c.get("name") in ("Read", "Grep", "Glob", "Bash", "PowerShell"):
                            outside.append("FORBIDDEN-FILE:" + forbidden)
        if ev.get("type") == "user":
            for c in ev.get("message", {}).get("content", []) if isinstance(ev.get("message", {}).get("content"), list) else []:
                if c.get("type") == "tool_result" and "permission" in json.dumps(c).lower() and c.get("is_error"):
                    denied += 1
        if ev.get("type") == "result":
            result_ok = not ev.get("is_error") and ev.get("subtype") == "success"
            cost = ev.get("total_cost_usd")
            usage = ev.get("usage", {})
    return {"result_ok": result_ok, "tool_calls": tool_calls, "permission_denials": denied,
            "outside_workspace_paths": sorted(set(outside))[:20], "isolation_breach": bool(outside),
            "cost_usd": cost, "model_reported": ",".join(sorted(models)),
            "input_tokens": (usage.get("input_tokens") or 0) + (usage.get("cache_read_input_tokens") or 0)
            + (usage.get("cache_creation_input_tokens") or 0), "output_tokens": usage.get("output_tokens")}


def skill_review(project: str, cond: str) -> dict:
    """External blind in-loop review (skill step 18) with Claude Opus, hard isolation."""
    w = ws(project, cond)
    rcs = w / ".rcs"
    draft = (rcs / "drafts" / "v001" / "paper.md")
    if not draft.exists():
        draft = w / "paper.md"
    paper, _ = RL.sanitize_paper(draft.read_text(encoding="utf-8"))
    aud = (rcs / "packets" / "audience.md")
    obj = (rcs / "packets" / "objective.md")
    audience = aud.read_text(encoding="utf-8") if aud.exists() else AUDIENCE
    objective = obj.read_text(encoding="utf-8") if obj.exists() else "Not provided."
    pid = RL.new_packet_id()
    out = EV / "skill_agent" / project / cond / "inloop_review_raw.txt"
    rec = run(f"INLOOP-{project}-{cond}", "reviewer_inloop", "claude", "opus", RL.REVIEWER_SYSTEM,
              RL.reviewer_user_message(pid, audience, objective, paper), out, timeout=2400)
    if rec["status"] == "ok":
        n, problems = RL.normalize_review(RL.extract_json(out.read_text(encoding="utf-8")))
        d = rcs / "diagnostics" / "v001_1"
        d.mkdir(parents=True, exist_ok=True)
        (d / "diagnostics.json").write_text(json.dumps(n["diagnostics"], indent=1), encoding="utf-8")
        (d / "reconstruction.json").write_text(json.dumps(n["reconstruction"], indent=1), encoding="utf-8")
        rec["validation_problems"] = problems
    return rec


def collect(project: str, cond: str) -> None:
    w = ws(project, cond)
    base = "plain_agent" if cond == "plain" else ("skill_agent" if cond.startswith("skill") and not cond.startswith("skillpkg") else "evidence_agent")
    dest = EV / base / project / cond
    dest.mkdir(parents=True, exist_ok=True)
    if (w / "paper.md").exists():
        shutil.copy2(w / "paper.md", dest / "paper.md")
    if (w / ".rcs").exists():
        if (dest / "rcs").exists():
            shutil.rmtree(dest / "rcs")
        shutil.copytree(w / ".rcs", dest / "rcs")
    for s in w.parent.glob(f"{w.name}__*.stream.jsonl"):
        shutil.copy2(s, dest / s.name.split("__", 2)[-1])
    words = len(re.sub(r"(?s)#+\s*References.*", "", (dest / "paper.md").read_text(encoding="utf-8")).split()) \
        if (dest / "paper.md").exists() else 0
    print(f"collected {project}/{cond} -> {dest} ({words} words)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("step")
    ap.add_argument("project")
    ap.add_argument("condition", nargs="?", default=None)
    ap.add_argument("--cond", default="skill")
    ap.add_argument("--package", default=None)
    a = ap.parse_args()
    cond = a.condition or a.cond
    if a.step == "prep":
        print(prep(a.project, cond, Path(a.package) if a.package else None))
    elif a.step == "plain":
        print(json.dumps(run_session(f"W-{a.project}-plain", ws(a.project, "plain"), PLAIN_PROMPT)))
    elif a.step == "skill-draft":
        prompt = SKILL_PROMPT + (SKILL_PKG_NOTE if cond.startswith("skillpkg") else "")
        print(json.dumps(run_session(f"W-{a.project}-{cond}-draft", ws(a.project, cond), prompt)))
    elif a.step == "skill-review":
        print(json.dumps(skill_review(a.project, cond)))
    elif a.step == "skill-revise":
        print(json.dumps(run_session(f"W-{a.project}-{cond}-revise", ws(a.project, cond), REVISE_PROMPT)))
    elif a.step == "collect":
        collect(a.project, cond)
    return 0


if __name__ == "__main__":
    sys.exit(main())
