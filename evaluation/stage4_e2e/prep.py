#!/usr/bin/env python3
"""Prepare the vNext Stage 4 end-to-end run: the full workflow with SEPARATE role agents on a real, raw-evidence project.

Project: the user's ASMOS repository (read-only). A curated evidence set (docs + result artifacts, no per-query
question/answer data, no finished paper) is copied into a workspace outside both repositories:
  <RCE_TMP>/rce_ws/ASMOS_e2e/{project/, rce/skill, rce/tools, .rcs/state.json, TASK_*.md}

Roles (each run as its own agent with its own context): CORPUS (steps 1-2) -> AUTHOR (3-17) -> REVIEW (18, packet
only) -> AUTHOR (19-21). The orchestrator records the REVIEW role's outputs in the ledger (the reviewer itself may
read nothing outside its packet).

Usage: python evaluation/stage4_e2e/prep.py [--asmos DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAND = HERE.parents[0] / "skill_versions" / "v0.3.0-candidate"
W = Path(os.environ.get("RCE_TMP", tempfile.gettempdir())) / "rce_ws" / "ASMOS_e2e"
FILES = ["README.md", "REPRODUCIBILITY.md", "CONTRACT.md", "ASMOS_technical_report.md",
         "results/summary.csv", "results/summary.md", "results/statistics.md", "results/comparison_table.md",
         "data/results/CORRECTIONS.md", "data/results/effect_size_correction_20260807_78127c8.json",
         "data/results/n10_cost_expanded_20260726_93f9058.json", "data/results/e2_cross_model_summary_20260630_045130.json",
         "data/results/e2_new_topic_20260703_182558.json", "data/results/e2_new_topic_20260726_104315.json"]

COMMON = """Your working directory for this entire task is `{W}`. Use absolute paths under it. Hard rules: never read, list,
search or write anything outside that directory; do not use the web; do not spawn agents; you may run `python` on the
tools in `{W}/rce/tools/`. Do NOT read `rce/skill/agents/review_agent.md`, `recon_grader.md` or `skill_agent.md`.
No human is available during this run: wherever the skill says ASK or STOP, create a checkpoint
(`python rce/tools/workflow_guard.py ask --rcs .rcs --id Q-00N --question "..." --blocks <claim ids>`) and keep the
blocked claims `status: BLOCKED` and out of the paper. NEVER answer a checkpoint yourself. Accepted risks in
`.rcs/state.json` must have `"kind": "workflow"` (never license a fact). Evidence locator paths are relative to the
working directory, e.g. `project/results/summary.csv`.
After writing or changing any artifact, record it for your role:
`python rce/tools/workflow_guard.py record --rcs .rcs --role {role} <files...>`.
"""

TASKS = {
    "TASK_CORPUS.md": """# Role: CORPUS_AGENT (steps 1-2 only)
""" + COMMON + """
Read `rce/skill/SKILL.md` (hard rules and the "Truth guardrail" section), `rce/skill/agents/corpus_agent.md` and
`rce/skill/evidence_model.md` (including section 8). Then perform workflow steps 1-2 on `project/`:
- `.rcs/evidence/project_inventory.json`, `.rcs/evidence/research_evidence.json`, `.rcs/evidence/missing_evidence.json`,
  `.rcs/claims/claim_candidates.json`. You may write ONLY those (and `.rcs/corpus/` if needed).
- Be alert: some documents are stale. A document that says it is archived or superseded must not be used as the source
  of numbers (mark such items `status: superseded` with a note). `project/data/results/CORRECTIONS.md` records superseded
  values: keep both, mark the superseded one, and give conflicting values `quantity`/`conflicts_with`/`resolution`.
- Give each numeric item a `quantity` (or metric + conditions + `run_id`). Different runs with different conditions are
  not conflicts; the same quantity with different values is.
- Before finishing, `python rce/tools/validate_artifacts.py .rcs --project-root .` must show 0 errors for your artifacts
  (errors about artifacts other roles have not written yet are expected only if they refer to those files).
Reply DONE with the number of evidence items, conflicts found, superseded items, and checkpoints asked.
""",
    "TASK_AUTHOR_DRAFT.md": """# Role: AUTHOR (steps 3-17)
""" + COMMON + """
The CORPUS role has already built `.rcs/evidence/` and `.rcs/claims/claim_candidates.json`; do not edit them (if you
find an evidence problem, record a checkpoint or note it in `.rcs/open_issues.md`).
TASK: write a research paper presenting this project to machine-learning researchers from other subfields (audience
mode B), 3,000-4,500 words of main text, Markdown, following `rce/skill/SKILL.md` workflow steps 3-17 with the v0.3
truth guardrail (`state.json` already has `"guardrail": "v0.3"`), including:
- claim map with `basis`, `status`, and `licenses` for any licensed wording (significant, outperforms, generalizes, ...);
- `.rcs/plan/reader_model.json` for persona B (templates/reader_model.json) and `python rce/tools/audit_reader.py`;
- figures only through `.rcs/plan/visual_registry.json` from real project data (`python rce/tools/plan_visuals.py .rcs`
  first; re-typed values go into a CSV you write under `.rcs/plan/data/` with `data.source_text` pointing to the project
  file they come from); `python rce/tools/visuals.py render .rcs --project-root .`;
- a skim sheet (`python rce/tools/skim_layer.py build .rcs`) and `check` of your abstract;
- the gates: `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v001/paper.md`; fix and
  re-run until G1, G3, V1-V4 and V6 pass, or record in `.rcs/open_issues.md` exactly which gate fails and why.
Write the draft to `.rcs/drafts/v001/paper.md` (claim tags kept), `.rcs/packets/audience.md` and `.rcs/packets/objective.md`
(templates/packet_audience_objective.md), then build the blind review packet:
`python rce/tools/build_review_packet.py .rcs/drafts/v001/paper.md --out .rcs/packets/review_v001_1 --audience .rcs/packets/audience.md --objective .rcs/packets/objective.md --strip-markers`
Record everything you wrote as role AUTHOR. Reply DONE with the word count and the effective gate statuses.
""",
    "TASK_AUTHOR_REVISE.md": """# Role: AUTHOR (steps 19-21)
""" + COMMON + """
The blind review of `.rcs/drafts/v001/paper.md` is in `.rcs/diagnostics/v001_1/` (diagnostics.json, reconstruction.json).
1. Step 19: revise structure-first into `.rcs/drafts/v002/paper.md` (tags kept). For EVERY blocking finding (any score <= 2;
   evidence_traceability / claim_evidence_alignment / unsupported_inference < 4) and EVERY inference issue, write a
   disposition to `.rcs/revisions/v001_1/dispositions.json`: {"items": [{"item": "finding:<index>" | "inference:<index>",
   "disposition": "fixed", "where": "..."} | {"disposition": "declined", "reason": ">= 20 chars"} | {"disposition":
   "deferred"} (and list it in `.rcs/open_issues.md`)]}. Indexes are positions in the diagnostics arrays.
   Then `python rce/tools/g4_check.py .rcs --round v001_1 --revised .rcs/drafts/v002/paper.md --out .rcs/audits/gates/G4_review.json`.
2. Step 21: line-edit a copy into `.rcs/drafts/v003/paper.md` (tags KEPT), check
   `python rce/tools/claim_invariance.py .rcs/drafts/v002/paper.md .rcs/drafts/v003/paper.md` (revert any drift), then write
   the final manuscript without tags to `paper/paper.md` (keep genuinely unresolved markers), and `.rcs/open_issues.md`.
3. Run all gates: `python rce/tools/run_workflow.py gates .rcs --project-root . --draft .rcs/drafts/v002/paper.md --round v001_1 --revised .rcs/drafts/v002/paper.md --final paper/paper.md --before .rcs/drafts/v002/paper.md --edited .rcs/drafts/v003/paper.md`
   and fix until they pass, or record exactly which gate fails and why in `.rcs/open_issues.md`.
Record everything you wrote as role AUTHOR. Reply DONE with the final word count and the effective gate statuses.
""",
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--asmos", default="C:/Users/csdee/PESU/CDSAML/ASMOS")
    a = ap.parse_args()
    src = Path(a.asmos)
    if W.exists():
        shutil.rmtree(W)
    prov = []
    for f in FILES:
        (W / "project" / f).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src / f, W / "project" / f)
        prov.append({"file": f, "sha256": hashlib.sha256((src / f).read_bytes()).hexdigest()})
    shutil.copytree(CAND, W / "rce" / "skill", ignore=shutil.ignore_patterns("tools", "versions", "__pycache__", "tests"))
    shutil.copytree(CAND / "tools", W / "rce" / "tools", ignore=shutil.ignore_patterns("__pycache__", "tests"))
    (W / ".rcs").mkdir()
    (W / ".rcs" / "state.json").write_text(json.dumps({"step": 0, "guardrail": "v0.3", "length_limit_words": 4500,
                                                       "gates": {}, "accepted_risks": []}, indent=1), encoding="utf-8")
    for name, text in TASKS.items():
        role = "CORPUS" if "CORPUS" in name else "AUTHOR"
        (W / name).write_text(text.replace("{W}", str(W).replace("\\", "/")).replace("{role}", role), encoding="utf-8")
    (HERE / "INPUT_MANIFEST.json").write_text(json.dumps({"source": str(src), "workspace": str(W), "files": prov}, indent=1),
                                              encoding="utf-8")
    print(W)


if __name__ == "__main__":
    main()
