#!/usr/bin/env python3
"""Validate Research Communication Engine artifacts in a project's .rcs/ directory.

Checks
  1. JSON Schema validity of every known artifact present.
  2. Referential integrity: unique IDs; claim->evidence, limitation->claim, story->claim/evidence.
  3. Evidence locators resolve to existing files (relative to the project root).
  4. Story-graph validity rules (skill/research_story.md section 2).
  5. Spine: 7 lines, each bound to >=1 claim/limitation ID.
  6. Claim sanity: measured/observed/derived claims need evidence; low-confidence claims flagged.

Usage
  python tools/validate_artifacts.py <path/to/.rcs> [--project-root DIR] [--json]
  python tools/validate_artifacts.py --check-skill            # skill manifest + proposals

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
from rce_common import SKILL_DIR, load_json, load_schema, validate  # noqa: E402

ARTIFACTS = {
    "evidence/research_evidence.json": "research_evidence.schema.json",
    "claims/claim_evidence_map.json": "claim_evidence_map.schema.json",
    "story/story_graph.json": "story_graph.schema.json",
    "corpus/source_registry.json": "source_registry.schema.json",
    "corpus/writing_patterns.json": "writing_patterns.schema.json",
    "corpus/anti_patterns.json": "writing_patterns.schema.json",
    "evaluation/gold_story.json": "gold_story.schema.json",
}
GLOB_ARTIFACTS = {
    "diagnostics/**/diagnostics.json": "diagnostics.schema.json",
    "diagnostics/**/reconstruction.json": "reconstruction.schema.json",
}
EVIDENCE_REQUIRED_TYPES = {"measured", "observed", "derived"}


class Report:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, level: str, where: str, msg: str) -> None:
        self.items.append({"level": level, "where": where, "message": msg})

    @property
    def errors(self) -> int:
        return sum(1 for i in self.items if i["level"] == "ERROR")

    def print(self, as_json: bool) -> None:
        if as_json:
            print(json.dumps({"errors": self.errors, "items": self.items}, indent=2))
            return
        for i in self.items:
            print(f"[{i['level']}] {i['where']}: {i['message']}")
        warns = sum(1 for i in self.items if i["level"] == "WARN")
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

    # Negative results must have a decision
    decisions = {d.get("evidence") for d in (cm.get("negative_result_decisions", []) if isinstance(cm, dict) else [])}
    for e in ev_items:
        if e.get("kind") == "negative_result" and cm and e.get("id") not in decisions:
            rep.add("ERROR", f"evidence/{e.get('id')}", "negative result without reporting decision (SELECTIVE_REPORTING risk)")

    if sg:
        check_story_graph(sg, c_ids, ev_ids, rep)


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
        check_spine(rcs, rep)
    if not args.rcs and not args.check_skill:
        ap.print_help()
        return 2
    rep.print(args.json)
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
