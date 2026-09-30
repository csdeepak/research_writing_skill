#!/usr/bin/env python3
"""Validate Research Communication Engine artifacts in a project's .rcs/ directory.

Checks
  1. JSON Schema validity of every known artifact present.
  2. Referential integrity: unique IDs; claim->evidence, limitation->claim, story->claim/evidence.
  3. Evidence locators resolve to existing files (relative to the project root).
  4. Story-graph validity rules (skill/research_story.md section 2).
  5. Spine: 7 lines, each bound to >=1 claim/limitation ID.
  6. Claim sanity: measured/observed/derived claims need evidence; low-confidence claims flagged.
  7. Attribution (v0.2.0): every limitation has an origin; every author-stated limitation and
     author-stated rationale in the evidence map survives into the claim map; nothing
     writer-derived is labelled author_stated.
  8. Executable gates (v0.2.0): a gate marked "passed" in .rcs/state.json must be backed by the
     tool report(s) it requires under .rcs/audits/gates/, error-free and not stale. The report's
     `effective_gates` shows what each gate really is: PASSED, NOT_RUN (self-certified), FAILED, STALE.
  9. Truth guardrail (v0.3.0, tools/truth_guardrail.py): evidence conflicts, claim licenses and
     provenance, source titles repaired from memory, fail-closed figure/table cards.

Usage
  python tools/validate_artifacts.py <path/to/.rcs> [--project-root DIR] [--json] [--out REPORT.json]
  python tools/validate_artifacts.py --check-skill            # skill manifest + proposals

  --out writes the machine-readable report (with SHA-256 of the checked artifacts) that gates
  G1 and G5 require, e.g.  --out .rcs/audits/gates/G1_validate.json

Exit code 1 if any ERROR is found.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rce_common import CLAIM_TAG_RE, SKILL_DIR, length_limit, load_json, load_schema, validate  # noqa: E402
import truth_guardrail  # noqa: E402
import workflow_guard  # noqa: E402

ARTIFACTS = {
    "evidence/research_evidence.json": "research_evidence.schema.json",
    "claims/claim_evidence_map.json": "claim_evidence_map.schema.json",
    "story/story_graph.json": "story_graph.schema.json",
    "corpus/source_registry.json": "source_registry.schema.json",
    "corpus/writing_patterns.json": "writing_patterns.schema.json",
    "corpus/anti_patterns.json": "writing_patterns.schema.json",
    "plan/visual_registry.json": "visual_registry.schema.json",
    "plan/reader_model.json": "reader_model.schema.json",
    "evaluation/gold_story.json": "gold_story.schema.json",
}
GLOB_ARTIFACTS = {
    "diagnostics/**/diagnostics.json": "diagnostics.schema.json",
    "diagnostics/**/reconstruction.json": "reconstruction.schema.json",
}
EVIDENCE_REQUIRED_TYPES = {"measured", "observed", "derived"}
HASHED_INPUTS = list(ARTIFACTS) + ["story/spine.md"]

# Gate -> tool reports that must exist (relative to .rcs) before the gate may be marked passed.
GATE_REPORTS = {
    "G1": [("audits/gates/G1_validate.json", "validate")],
    "G3": [("audits/gates/G3_lint.json", "lint")],
    "G5": [("audits/gates/G5_validate.json", "validate"), ("audits/gates/G5_lint.json", "lint_final")],
}
# Visual gates (v0.3 Stage 2): one report, per-gate status inside it.
GATE_REPORTS.update({g: [("audits/gates/V_visuals.json", "visuals")] for g in ("V1", "V2", "V3", "V4", "V5", "V6")})
GATE_REPORTS["G4"] = [("audits/gates/G4_review.json", "g4")]
# v0.3 truth guardrail: projects that declare "guardrail": "v0.3" in state.json also need these reports.
V03_GATE_REPORTS = {
    "G3": [("audits/gates/G3_numbers.json", "numbers")],
    "G5": [("audits/gates/G5_numbers.json", "numbers"), ("audits/gates/G5_invariance.json", "invariance")],
}
GATE_COMMANDS = {
    "validate": "python tools/validate_artifacts.py .rcs --out .rcs/audits/gates/{gate}_validate.json",
    "lint": "python tools/lint_draft.py <assembled paper.md> --rcs .rcs --out .rcs/audits/gates/{gate}_lint.json",
    "lint_final": "python tools/lint_draft.py <final paper.md> --rcs .rcs --final --out .rcs/audits/gates/{gate}_lint.json",
    "numbers": "python tools/verify_numbers.py <paper.md> --rcs .rcs --out .rcs/audits/gates/{gate}_numbers.json",
    "invariance": "python tools/claim_invariance.py <tagged draft before edit> <tagged draft after edit> "
                  "--out .rcs/audits/gates/{gate}_invariance.json",
    "g4": "python tools/g4_check.py .rcs --round <round> --revised <revised draft> --out .rcs/audits/gates/G4_review.json",
    "visuals": "python tools/visuals.py render .rcs && python tools/validate_visuals.py .rcs --draft <paper.md> "
               "--out .rcs/audits/gates/V_visuals.json",
}
G1_REQUIRED = ["evidence/research_evidence.json", "claims/claim_evidence_map.json", "story/spine.md"]


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []
        self.effective_gates: dict[str, str] = {}

    def add(self, level: str, where: str, msg: str) -> None:
        self.items.append({"level": level, "where": where, "message": msg})

    @property
    def errors(self) -> int:
        return sum(1 for i in self.items if i["level"] == "ERROR")

    def print(self, as_json: bool) -> None:
        if as_json:
            print(json.dumps({"errors": self.errors, "effective_gates": self.effective_gates,
                              "items": self.items}, indent=2))
            return
        for i in self.items:
            print(f"[{i['level']}] {i['where']}: {i['message']}")
        warns = sum(1 for i in self.items if i["level"] == "WARN")
        if self.effective_gates:
            print("effective gates: " + ", ".join(f"{g}={st}" for g, st in sorted(self.effective_gates.items())))
        print(f"\n{self.errors} error(s), {warns} warning(s)")


def check_schemas(rcs: Path, rep: Report) -> dict[str, object]:
    loaded: dict[str, object] = {}
    targets = [(rcs / rel, schema) for rel, schema in ARTIFACTS.items()]
    for pattern, schema in GLOB_ARTIFACTS.items():
        targets += [(p, schema) for p in rcs.glob(pattern)]
    for path, schema_name in targets:
        if not path.exists():
            continue
        rel = str(path.relative_to(rcs)).replace("\\", "/")
        try:
            data = load_json(path)
        except json.JSONDecodeError as exc:
            rep.add("ERROR", rel, f"invalid JSON: {exc}")
            continue
        for err in validate(data, load_schema(schema_name)):
            rep.add("ERROR", rel, err)
        loaded[rel] = data
    return loaded


def _ids(items: list[dict], where: str, rep: Report) -> set[str]:
    seen: set[str] = set()
    for it in items:
        i = it.get("id")
        if i in seen:
            rep.add("ERROR", where, f"duplicate id {i}")
        seen.add(i)
    return seen


def check_references(rcs: Path, project_root: Path, loaded: dict, rep: Report) -> None:
    ev = loaded.get("evidence/research_evidence.json", {}) or {}
    cm = loaded.get("claims/claim_evidence_map.json", {}) or {}
    sg = loaded.get("story/story_graph.json", {}) or {}
    sr = loaded.get("corpus/source_registry.json", {}) or {}

    ev_items = ev.get("items", []) if isinstance(ev, dict) else []
    ev_ids = _ids(ev_items, "evidence", rep)
    ev_by_id = {e.get("id"): e for e in ev_items}

    # Locators resolve
    for e in ev_items:
        loc = (e.get("locator") or {}).get("path")
        if loc and not (project_root / loc).exists():
            rep.add("ERROR", f"evidence/{e.get('id')}", f"locator path does not exist: {loc}")
        for c in e.get("conflicts_with", []) or []:
            if c not in ev_ids:
                rep.add("ERROR", f"evidence/{e.get('id')}", f"conflicts_with unknown {c}")
        if e.get("status") == "conflicting" and not e.get("conflicts_with"):
            rep.add("WARN", f"evidence/{e.get('id')}", "status=conflicting but no conflicts_with")

    claims = cm.get("claims", []) if isinstance(cm, dict) else []
    lims = cm.get("limitations", []) if isinstance(cm, dict) else []
    c_ids = _ids(claims, "claims", rep)
    l_ids = _ids(lims, "limitations", rep)
    src_ids = {s.get("id") for s in (sr.get("sources", []) if isinstance(sr, dict) else [])}

    for c in claims:
        cid = c.get("id")
        for ref in c.get("evidence", []):
            if ref.startswith("E") and ev_items and ref not in ev_ids:
                rep.add("ERROR", f"claims/{cid}", f"unknown evidence {ref}")
            if ref.startswith("C") and ref not in c_ids:
                rep.add("ERROR", f"claims/{cid}", f"unknown claim {ref}")
        for ref in c.get("limitations", []) or []:
            if ref not in l_ids:
                rep.add("ERROR", f"claims/{cid}", f"unknown limitation {ref}")
        for ref in c.get("sources", []) or []:
            if src_ids and ref not in src_ids:
                rep.add("ERROR", f"claims/{cid}", f"unknown source {ref}")
        ctype = c.get("claim_type")
        if ctype in EVIDENCE_REQUIRED_TYPES and not c.get("evidence"):
            rep.add("ERROR", f"claims/{cid}", f"{ctype} claim has no evidence (NO_EVIDENCE)")
        if ctype == "literature" and not c.get("sources"):
            rep.add("ERROR", f"claims/{cid}", "literature claim has no verified source")
        if ctype == "measured":
            strengths = {ev_by_id.get(r, {}).get("strength") for r in c.get("evidence", []) if r.startswith("E")}
            if ev_items and "hard" not in strengths:
                rep.add("WARN", f"claims/{cid}", "measured claim not backed by any 'hard' evidence item")
        if ctype == "interpretation" and not any(r.startswith(("E", "C")) for r in c.get("evidence", [])):
            rep.add("ERROR", f"claims/{cid}", "interpretation must rest on evidence or other claims")
        if c.get("author_confirmation") == "pending":
            rep.add("WARN", f"claims/{cid}", "author_confirmation pending")
    for lim in lims:
        for ref in lim.get("affects_claims", []):
            if ref not in c_ids:
                rep.add("ERROR", f"limitations/{lim.get('id')}", f"affects unknown claim {ref}")
        for ref in lim.get("evidence", []) or []:
            if ref.startswith("E") and ev_items and ref not in ev_ids:
                rep.add("ERROR", f"limitations/{lim.get('id')}", f"unknown evidence {ref}")

    if cm:
        check_attribution(ev_items, ev_by_id, claims, lims, rep)

    # Negative results must have a decision
    decisions = {d.get("evidence") for d in (cm.get("negative_result_decisions", []) if isinstance(cm, dict) else [])}
    for e in ev_items:
        if e.get("kind") == "negative_result" and cm and e.get("id") not in decisions:
            rep.add("ERROR", f"evidence/{e.get('id')}", "negative result without reporting decision (SELECTIVE_REPORTING risk)")

    if sg:
        check_story_graph(sg, c_ids, ev_ids, rep)


def _live(e: dict) -> bool:
    return e.get("status") != "superseded"


def check_attribution(ev_items: list, ev_by_id: dict, claims: list, lims: list, rep: Report) -> None:
    """S1/S2: the authors' own concessions and reasons must survive, correctly attributed."""
    def kinds(refs) -> set:
        return {ev_by_id.get(r, {}).get("kind") for r in refs or [] if isinstance(r, str) and r.startswith("E")}

    covered_lim: set = set()
    for lim in lims:
        lid = lim.get("id")
        if lim.get("origin") == "author_stated":
            covered_lim.update(lim.get("evidence", []) or [])
            if ev_items and "limitation_noted" not in kinds(lim.get("evidence")):
                rep.add("ERROR", f"limitations/{lid}",
                        "origin author_stated but cites no limitation_noted evidence item "
                        "(ATTRIBUTION_ERROR: a writer-derived caveat must not be presented as the authors')")
    for e in ev_items:
        if e.get("kind") == "limitation_noted" and _live(e) and e.get("id") not in covered_lim:
            rep.add("ERROR", f"evidence/{e.get('id')}",
                    "author-stated limitation is not carried into the claim map as an author_stated "
                    "limitation (AUTHOR_STATEMENT_DROPPED)")

    covered_rat: set = set()
    for c in claims:
        if not c.get("rationale"):
            continue
        cid = c.get("id")
        covered_rat.update(c.get("evidence", []) or [])
        if c.get("origin") != "author_stated":
            rep.add("ERROR", f"claims/{cid}",
                    "rationale claim must have origin author_stated (never invent a rationale; use [ASK AUTHOR])")
        if ev_items and "rationale_stated" not in kinds(c.get("evidence")):
            rep.add("ERROR", f"claims/{cid}", "rationale claim cites no rationale_stated evidence item")
    for e in ev_items:
        if e.get("kind") == "rationale_stated" and _live(e) and e.get("id") not in covered_rat:
            rep.add("ERROR", f"evidence/{e.get('id')}",
                    "author-stated motivation/design rationale is not carried into the claim map as a "
                    "rationale claim (AUTHOR_STATEMENT_DROPPED)")


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def hash_inputs(rcs: Path) -> dict[str, str]:
    return {rel: sha256_file(rcs / rel) for rel in HASHED_INPUTS if (rcs / rel).exists()}


def _passed(val) -> bool:
    status = val.get("status") if isinstance(val, dict) else val
    return isinstance(status, str) and status.strip().lower().startswith("passed")


def check_gates(rcs: Path, project_root: Path, rep: Report) -> dict[str, str]:
    """S3: gates are executable. 'passed' without the required, fresh, error-free tool report is
    a self-certified gate and an ERROR."""
    sp = rcs / "state.json"
    eff = rep.effective_gates
    if not sp.exists():
        return eff
    try:
        state = load_json(sp)
    except json.JSONDecodeError as exc:
        rep.add("ERROR", "state.json", f"invalid JSON: {exc}")
        return eff
    gates = state.get("gates") or {}
    limit = length_limit(rcs, state)
    rank = {"PASSED": 0, "STALE": 1, "FAILED": 2, "NOT_RUN": 3}

    def mark(gate: str, status: str) -> None:
        if rank[status] > rank.get(eff.get(gate, "PASSED"), 0):
            eff[gate] = status

    for gate, val in gates.items():
        if not _passed(val):
            raw = str((val.get("status") if isinstance(val, dict) else val) or "")
            if not raw.strip() or re.match(r"\s*not[ _]run", raw, re.I):
                eff[gate] = "NOT_RUN"
            elif re.search(r"pending|not[ _]reached|not attempted|out of scope|skipped", raw, re.I):
                eff[gate] = "PENDING"
            elif re.search(r"fail", raw, re.I):
                eff[gate] = "FAILED"
            else:
                eff[gate] = "UNVERIFIED"    # free-text self-description, no executable check behind it
            continue
        eff[gate] = "PASSED"
        if gate not in GATE_REPORTS and gate != "G1":
            mark(gate, "NOT_RUN")
            rep.add("WARN", f"state.json/{gate}", "marked passed, but this gate has no executable report; "
                                                  "effective status NOT_RUN")
        if gate == "G1":
            for rel in G1_REQUIRED:
                if not (rcs / rel).exists():
                    mark(gate, "FAILED")
                    rep.add("ERROR", "state.json", f"G1 marked passed but required artifact {rel} is missing")
        reports = list(GATE_REPORTS.get(gate, []))
        if str(state.get("guardrail", "")).lower() == "v0.3":
            reports += V03_GATE_REPORTS.get(gate, [])
        for rel, kind in reports:
            where = f"state.json/{gate}"
            path = rcs / rel
            if not path.exists():
                mark(gate, "NOT_RUN")
                rep.add("ERROR", where, f"marked passed but tool report {rel} is missing (SELF_CERTIFIED_GATE). "
                                        f"Run: {GATE_COMMANDS[kind].format(gate=gate)}")
                continue
            try:
                r = load_json(path)
            except json.JSONDecodeError as exc:
                mark(gate, "NOT_RUN")
                rep.add("ERROR", where, f"{rel} is not valid JSON: {exc}")
                continue
            if kind == "g4":
                if r.get("errors", 1) != 0:
                    mark(gate, "FAILED")
                    rep.add("ERROR", where, f"marked passed but {rel} reports {r.get('errors')} error(s)")
                dp = rcs / "revisions" / str(r.get("round")) / "dispositions.json"
                if r.get("dispositions_sha256") and (not dp.exists() or sha256_file(dp) != r["dispositions_sha256"]):
                    mark(gate, "STALE")
                    rep.add("ERROR", where, f"{rel} is stale: dispositions changed after the G4 check")
                    continue
                drafts = sorted((rcs / "drafts").glob("v*/paper.md"), key=lambda p: int(re.sub(r"\D", "", p.parent.name) or 0)) \
                    if (rcs / "drafts").exists() else []
                if drafts and r.get("claims_covered") is None and state.get("guardrail") == "v0.3":
                    mark(gate, "STALE")
                    rep.add("ERROR", where, f"{rel} predates the post-review claim check: re-run {GATE_COMMANDS['g4']}")
                elif drafts and r.get("claims_covered") is not None:
                    added = sorted({i for m in CLAIM_TAG_RE.finditer(drafts[-1].read_text(encoding="utf-8"))
                                    for i in re.findall(r"[CL]\d{3,}", m.group(0))} - set(r["claims_covered"]))
                    if added:
                        mark(gate, "STALE")
                        rep.add("ERROR", where, f"{rel} is stale: {drafts[-1].parent.name} states {', '.join(added)}, "
                                                "which no blind review covered; run another review round (step 20)")
                continue
            if kind == "visuals":
                g = (r.get("gates") or {}).get(gate, {})
                reg = rcs / "plan" / "visual_registry.json"
                if g.get("status") != "PASSED":
                    mark(gate, "FAILED" if g.get("status") == "FAILED" else "NOT_RUN")
                    rep.add("ERROR", where, f"marked passed but {rel} reports {gate} = {g.get('status', 'absent')}"
                            + (" (V5 needs a recorded human review)" if gate == "V5" else ""))
                elif not reg.exists() or "sha256:" + sha256_file(reg) != r.get("registry_sha256"):
                    mark(gate, "STALE")
                    rep.add("ERROR", where, f"{rel} is stale: the visual registry changed after validation")
                continue
            if r.get("errors", 1) != 0:
                mark(gate, "FAILED")
                rep.add("ERROR", where, f"marked passed but {rel} reports {r.get('errors')} error(s)")
            if kind == "validate":
                current = hash_inputs(rcs)
                recorded = r.get("inputs", {}) or {}
                stale = sorted(k for k in set(current) | set(recorded) if current.get(k) != recorded.get(k))
                if stale:
                    mark(gate, "STALE" if gate != "G5" else "FAILED")
                    rep.add("ERROR" if gate == "G5" else "WARN", where,
                            f"{rel} is stale: {', '.join(stale)} changed since it was written; re-run the validator")
                continue
            draft = r.get("after") if kind == "invariance" else r.get("draft")
            if kind == "invariance" and not draft:
                mark(gate, "NOT_RUN")
                rep.add("ERROR", where, f"{rel}: no edited draft recorded (run claim_invariance.py with --out)")
                continue
            dp = None
            for cand in ([project_root / draft, Path(draft)] if draft else []):
                if cand.exists():
                    dp = cand
                    break
            if dp is None:
                mark(gate, "NOT_RUN")
                rep.add("ERROR", where, f"{rel}: linted draft {draft!r} not found")
            elif sha256_file(dp) != r.get("after_sha256" if kind == "invariance" else "draft_sha256"):
                mark(gate, "STALE")
                rep.add("ERROR", where, f"{rel} is stale: {draft} changed after it was checked")
            if kind in ("numbers", "invariance"):
                continue
            if not r.get("rcs_used"):
                mark(gate, "FAILED")
                rep.add("ERROR", where, f"{rel}: lint was run without --rcs (claim tags not resolved)")
            if kind == "lint_final":
                if not r.get("final"):
                    mark(gate, "FAILED")
                    rep.add("ERROR", where, f"{rel}: lint was not run in --final mode")
                if limit is not None:
                    words = r.get("words_main")
                    if not isinstance(words, int):
                        rep.add("ERROR", where, f"{rel}: no main-text word count recorded (length gate)")
                    elif words > limit:
                        mark(gate, "FAILED")
                        rep.add("ERROR", where, f"main text is {words} words, limit {limit} (LENGTH_EXCEEDED)")
    return eff


def check_story_graph(sg: dict, c_ids: set, ev_ids: set, rep: Report) -> None:
    nodes = {n["id"]: n for n in sg.get("nodes", []) if "id" in n}
    edges = sg.get("edges", [])
    for e in edges:
        for end in ("from", "to"):
            if e.get(end) not in nodes:
                rep.add("ERROR", "story_graph", f"edge {e} references unknown node {e.get(end)}")

    def incoming(nid: str, etype: str) -> list[dict]:
        return [e for e in edges if e.get("to") == nid and e.get("type") == etype]

    def outgoing(nid: str, etype: str) -> list[dict]:
        return [e for e in edges if e.get("from") == nid and e.get("type") == etype]

    for nid, n in nodes.items():
        t = n.get("type")
        for cref in n.get("claims", []) or []:
            if c_ids and cref not in c_ids:
                rep.add("ERROR", f"story/{nid}", f"unknown claim {cref}")
        for eref in n.get("evidence", []) or []:
            if ev_ids and eref not in ev_ids:
                rep.add("ERROR", f"story/{nid}", f"unknown evidence {eref}")
        if t == "RQ":
            if not incoming(nid, "addresses") and not outgoing(nid, "addresses"):
                rep.add("ERROR", f"story/{nid}", "RQ is not linked to a GAP via 'addresses'")
            if not incoming(nid, "answers"):
                rep.add("ERROR", f"story/{nid}", "RQ has no INTERPRETATION that 'answers' it")
        if t == "CONTRIBUTION":
            srcs = {nodes.get(e["from"], {}).get("type") for e in incoming(nid, "grounds")}
            if "RESULT" not in srcs or "GAP" not in srcs:
                rep.add("ERROR", f"story/{nid}", "CONTRIBUTION must be grounded by both a RESULT and a GAP")
        if t == "LIMITATION" and not outgoing(nid, "limits"):
            rep.add("ERROR", f"story/{nid}", "LIMITATION does not 'limit' anything")
        if t == "DESIGN" and not (outgoing(nid, "tests") or outgoing(nid, "produces")):
            rep.add("ERROR", f"story/{nid}", "DESIGN neither 'tests' nor 'produces'")
        if t == "RESULT" and not n.get("evidence"):
            rep.add("ERROR", f"story/{nid}", "RESULT has no evidence IDs")

    # Path PROBLEM -> CONTRIBUTION (undirected reachability over edges is enough for coherence)
    adj: dict[str, set] = {k: set() for k in nodes}
    for e in edges:
        if e.get("from") in adj and e.get("to") in adj:
            adj[e["from"]].add(e["to"])
            adj[e["to"]].add(e["from"])
    probs = [k for k, n in nodes.items() if n.get("type") == "PROBLEM"]
    contribs = [k for k, n in nodes.items() if n.get("type") == "CONTRIBUTION"]
    if not probs:
        rep.add("ERROR", "story_graph", "no PROBLEM node")
    if not contribs:
        rep.add("ERROR", "story_graph", "no CONTRIBUTION node (CONTRIBUTION_UNCLEAR)")
    if probs and contribs:
        seen, stack = set(), [probs[0]]
        while stack:
            cur = stack.pop()
            if cur in seen:
                continue
            seen.add(cur)
            stack.extend(adj[cur] - seen)
        for c in contribs:
            if c not in seen:
                rep.add("ERROR", f"story/{c}", "CONTRIBUTION not connected to PROBLEM")
        orphans = [k for k in nodes if k not in seen]
        for k in orphans:
            rep.add("WARN", f"story/{k}", "node disconnected from the main story")
    for ch in sg.get("experiment_chains", []) or []:
        if not ch.get("next", "").strip():
            rep.add("WARN", f"story/chain/{ch.get('experiment')}", "empty NEXT link (possible orphan experiment)")


def check_spine(rcs: Path, rep: Report) -> None:
    spine = rcs / "story" / "spine.md"
    if not spine.exists():
        return
    lines = spine.read_text(encoding="utf-8").splitlines()
    found: dict[int, str] = {}
    for line in lines:
        m = re.match(r"^\s*(?:\|\s*)?([1-7])[\.\)\s]", line)
        if m:
            found.setdefault(int(m.group(1)), line)
    for k in range(1, 8):
        if k not in found:
            rep.add("ERROR", "story/spine.md", f"spine line {k} missing")
        elif not re.search(r"\b[CL]\d{3,}\b", found[k]):
            rep.add("ERROR", "story/spine.md", f"spine line {k} not bound to a claim/limitation ID")


def check_skill(rep: Report) -> None:
    versions = sorted((SKILL_DIR / "versions").glob("*/MANIFEST.json"))
    if not versions:
        rep.add("WARN", "skill", "no version manifest found; run tools/snapshot_version.py")
    else:
        latest = max(versions, key=lambda p: tuple(int(x) for x in re.findall(r"\d+", p.parent.name)[:3]))
        manifest = load_json(latest)
        for rel, digest in manifest.get("files", {}).items():
            p = SKILL_DIR / rel
            if not p.exists():
                rep.add("ERROR", f"skill/{rel}", f"missing (listed in {latest.parent.name})")
                continue
            if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
                rep.add("WARN", f"skill/{rel}", f"modified since {latest.parent.name} (unreleased change: needs a proposal + changelog entry)")
        current = {str(p.relative_to(SKILL_DIR)).replace("\\", "/") for p in SKILL_DIR.rglob("*")
                   if p.is_file() and "versions" not in p.relative_to(SKILL_DIR).parts}
        for rel in sorted(current - set(manifest.get("files", {}))):
            rep.add("WARN", f"skill/{rel}", f"new file not in {latest.parent.name}")
    schema = load_schema("skill_change.schema.json")
    for prop in (SKILL_DIR / "versions" / "proposals").glob("*.json"):
        for err in validate(load_json(prop), schema):
            rep.add("ERROR", f"proposals/{prop.name}", err)
    for sch in (SKILL_DIR / "schemas").glob("*.json"):
        try:
            load_json(sch)
        except json.JSONDecodeError as exc:
            rep.add("ERROR", f"schemas/{sch.name}", f"invalid JSON: {exc}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs", nargs="?", help="path to .rcs directory")
    ap.add_argument("--project-root", help="project root (default: parent of .rcs)")
    ap.add_argument("--check-skill", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", help="write the JSON report (required by gates G1/G5) to this path")
    args = ap.parse_args(argv)
    rep = Report()
    if args.check_skill:
        check_skill(rep)
    if args.rcs:
        rcs = Path(args.rcs).resolve()
        if not rcs.is_dir():
            print(f"not a directory: {rcs}", file=sys.stderr)
            return 2
        root = Path(args.project_root).resolve() if args.project_root else rcs.parent
        loaded = check_schemas(rcs, rep)
        check_references(rcs, root, loaded, rep)
        truth_guardrail.run(rcs, root, loaded, rep)
        workflow_guard.run(rcs, root, loaded, rep)
        check_spine(rcs, rep)
        if args.out:
            # The report certifies the artifacts only; gate bookkeeping is checked separately
            # below so that a report never depends on the gate it is meant to certify.
            out = Path(args.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            warns = sum(1 for i in rep.items if i["level"] == "WARN")
            out.write_text(json.dumps({"tool": "validate_artifacts", "errors": rep.errors, "warnings": warns,
                                       "inputs": hash_inputs(rcs), "items": rep.items},
                                      indent=2), encoding="utf-8")
        check_gates(rcs, root, rep)
    elif args.out:
        print("--out requires an .rcs path", file=sys.stderr)
        return 2
    if not args.rcs and not args.check_skill:
        ap.print_help()
        return 2
    rep.print(args.json)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
