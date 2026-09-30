"""Stage 1 truth guardrail (skill 0.3.0 candidate; docs/06_VNEXT_SPEC.md sections 4 and 10).

Artifact-level checks that fail closed instead of letting prose sound complete:

  UNRECONCILED_CONFLICT     two live evidence items report different values for the same quantity
                            (same `quantity`, or same metric + conditions + run_id) and are not linked
  BLOCKED_BY_CONFLICT       a claim cites an item whose conflict has no documented resolution
  CITES_REJECTED_EVIDENCE   a claim cites the side of a resolved conflict that was not chosen
  UNLICENSED_CLAIM          a claim license (e.g. significance_test) is not backed by qualifying evidence
  UNSUPPORTED_FACT          a measured/observed/derived claim declares basis "none"
  TITLE_REPAIRED_FROM_MEMORY a source title differs from the project's own citation text without an
                            index/DOI/publisher lookup
  NO_VALID_VISUAL           an evidence-bearing figure/table card has no live, traceable data
  UNTRACED_COMPONENT        a schematic's component does not resolve to project code/docs
  BLOCKED_PERMISSION        an image sample lacks usage permission or contains identifying data
  UNLABELLED_ILLUSTRATION   a synthetic/illustrative visual lacks the mandatory label

Everything here is additive: artifacts without the new fields validate exactly as in 0.2.0.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

LIVE_STATUSES = {"ok", "incomplete", "conflicting", "unverifiable"}   # everything but "superseded"
VERIFIED_LOOKUPS = {"doi_lookup", "index_lookup", "publisher_page"}
NON_EVIDENCE_VISUALS = {"diagram", "schematic", "conceptual", "illustrative", "flowchart", "architecture"}
IMAGE_VISUALS = {"image", "image panel", "image_panel", "qualitative", "photo", "sample grid"}
ILLUSTRATIVE_LABEL = "ILLUSTRATIVE - NOT EXPERIMENTAL EVIDENCE"
CARD_SUFFIXES = (".json", ".yaml", ".yml", ".md")

# license type -> (what it needs, predicate over the cited evidence items)
def _vals(e: dict) -> dict:
    v = e.get("value")
    return v if isinstance(v, dict) else {}


def _cond_text(e: dict) -> str:
    return (json.dumps(e.get("conditions") or "") + " " + json.dumps(e.get("value") or "")).lower()


LICENSES: dict[str, tuple[str, Any]] = {
    "significance_test": ("a result item whose value names a statistical test and a p-value or CI",
                          lambda items: any("test" in _vals(e) and ({"p", "p_value", "ci"} & set(_vals(e))) for e in items)),
    "sota_comparison": ("an item naming the benchmark, the complete comparison set and a date",
                        lambda items: any({"benchmark", "comparison_set", "date"} <= set(_vals(e)) for e in items)),
    "stress_test": ("an item recording a stress/perturbation evaluation",
                    lambda items: any(re.search(r"stress|perturb|adversarial|robustness", _cond_text(e)) for e in items)),
    "latency_measured": ("an item with a measured latency and the target hardware",
                         lambda items: any("hardware" in _vals(e) and any("latency" in k for k in _vals(e)) for e in items)),
    "clinical_study": ("an item describing a clinical study (study_type)",
                       lambda items: any("study_type" in _vals(e) for e in items)),
    "ood_eval": ("an item evaluated out of distribution (conditions/value mark OOD)",
                 lambda items: any(re.search(r"\bood\b|out[- ]of[- ]distribution|held[- ]out domain", _cond_text(e)) for e in items)),
    "literature_search": ("an item recording a bounded, logged literature search",
                          lambda items: any(e.get("kind") == "external_fact" and "search" in _cond_text(e) for e in items)),
    "causal_design": ("an experiment item with a causal design (randomized, controlled, ablation, intervention)",
                      lambda items: any(str(_vals(e).get("design", "")).lower() in {"randomized", "controlled", "ablation", "intervention"} for e in items)),
    "matched_evaluation": ("an item recording matched/tuned baselines under the same protocol",
                           lambda items: any(_vals(e).get("matched") is True or "baseline_tuning" in _vals(e) for e in items)),
    "complete_enumeration": ("an item enumerating all cases the universal claim covers",
                             lambda items: any("enumerated" in _vals(e) or "n_cases" in _vals(e) for e in items)),
}


# --------------------------------------------------------------------------------------- helpers
def number_of(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, dict):
        for k in ("value", "mean", "count", "n_items", "total"):
            if isinstance(value.get(k), (int, float)) and not isinstance(value.get(k), bool):
                return float(value[k])
    return None


def quantity_key(e: dict) -> str | None:
    if e.get("quantity"):
        return f"q:{e['quantity']}"
    v = e.get("value")
    if isinstance(v, dict) and v.get("metric"):
        cond = json.dumps(e.get("conditions") or {}, sort_keys=True)
        return f"m:{v['metric']}|{cond}|{v.get('run_id') or e.get('run_id') or ''}"
    return None


def _norm_title(t: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", t or "").lower()).strip()


# ------------------------------------------------------------------ evidence conflicts (cases 1-2)
def check_conflicts(ev_items: list[dict], claims: list[dict], rep) -> None:
    by_id = {e.get("id"): e for e in ev_items}
    live = [e for e in ev_items if e.get("status") in LIVE_STATUSES]

    def linked(a: dict, b: dict) -> bool:
        return b.get("id") in (a.get("conflicts_with") or []) or a.get("id") in (b.get("conflicts_with") or [])

    groups: dict[str, list[dict]] = {}
    for e in live:
        k = quantity_key(e)
        if k and number_of(e.get("value")) is not None:
            groups.setdefault(k, []).append(e)
    for k, items in groups.items():
        for i, a in enumerate(items):
            for b in items[i + 1:]:
                va, vb = number_of(a.get("value")), number_of(b.get("value"))
                if va is None or vb is None or abs(va - vb) <= 1e-9 * max(1.0, abs(va)):
                    continue
                if not linked(a, b):
                    rep.add("ERROR", f"evidence/{a.get('id')}+{b.get('id')}",
                            f"same quantity reported as {va:g} ({a.get('locator', {}).get('path')}) and {vb:g} "
                            f"({b.get('locator', {}).get('path')}) but not recorded as a conflict (UNRECONCILED_CONFLICT). "
                            "Mark both status=conflicting with conflicts_with, then add a documented resolution or leave blocked; "
                            "never silently pick one")

    # resolution state per conflicting item
    def resolution(e: dict) -> dict | None:
        for x in [e] + [by_id.get(c, {}) for c in e.get("conflicts_with") or []]:
            r = x.get("resolution")
            if isinstance(r, dict) and r.get("chosen") and len(str(r.get("reason", "")).strip()) >= 10:
                return r
        return None

    for e in ev_items:
        r = e.get("resolution")
        if r is not None and (not isinstance(r, dict) or not r.get("chosen") or len(str(r.get("reason", "")).strip()) < 10):
            rep.add("ERROR", f"evidence/{e.get('id')}", "resolution needs 'chosen' and a documented 'reason' (>=10 chars)")
    for c in claims:
        for ref in c.get("evidence", []) or []:
            e = by_id.get(ref)
            if not e or e.get("status") != "conflicting":
                continue
            r = resolution(e)
            if r is None:
                rep.add("ERROR", f"claims/{c.get('id')}",
                        f"cites {ref}, whose conflict with {', '.join(e.get('conflicts_with') or ['?'])} is unreconciled "
                        "(BLOCKED_BY_CONFLICT): reconcile with a documented reason, or keep the claim out of the paper")
            elif r.get("chosen") != ref:
                rep.add("ERROR", f"claims/{c.get('id')}",
                        f"cites {ref}, but the documented resolution chose {r.get('chosen')} (CITES_REJECTED_EVIDENCE)")


# ------------------------------------------------------------- provenance and licenses (case 3)
def check_claim_provenance(ev_items: list[dict], claims: list[dict], rep) -> None:
    by_id = {e.get("id"): e for e in ev_items}
    for c in claims:
        cid = c.get("id")
        if c.get("basis") == "none" and c.get("claim_type") in {"measured", "observed", "derived"}:
            rep.add("ERROR", f"claims/{cid}", f"{c.get('claim_type')} claim with basis 'none' (UNSUPPORTED_FACT): "
                                              "a factual claim needs a project, code, user or literature basis")
        if c.get("status") == "VERIFIED" and c.get("basis") == "none":
            rep.add("ERROR", f"claims/{cid}", "status VERIFIED with basis 'none' is contradictory")
        for lic in c.get("licenses", []) or []:
            ltype = lic.get("type") if isinstance(lic, dict) else lic
            if ltype not in LICENSES:
                rep.add("ERROR", f"claims/{cid}", f"unknown license type {ltype!r} (known: {', '.join(sorted(LICENSES))})")
                continue
            refs = lic.get("evidence", []) if isinstance(lic, dict) else []
            items = [by_id[r] for r in refs if r in by_id and by_id[r].get("status") in {"ok", "incomplete"}]
            need, pred = LICENSES[ltype]
            if not items or not pred(items):
                rep.add("ERROR", f"claims/{cid}", f"license {ltype} is not backed by qualifying evidence "
                                                  f"(UNLICENSED_CLAIM): needs {need}")


# ------------------------------------------------------------------ source titles (case 5)
def check_sources(sources: list[dict], rep) -> None:
    for s in sources:
        cited = s.get("as_cited")
        if not cited:
            continue
        method = (s.get("verification") or {}).get("method")
        if _norm_title(cited) != _norm_title(s.get("title", "")) and method not in VERIFIED_LOOKUPS:
            rep.add("ERROR", f"sources/{s.get('id')}",
                    f"title {s.get('title')!r} differs from the project's own citation text {cited!r} but was not "
                    f"verified by an index/DOI/publisher lookup (method {method!r}) (TITLE_REPAIRED_FROM_MEMORY): keep the "
                    "project's text and mark title_status 'unverifiable', or verify the correction")


# ----------------------------------------------------------------- figure cards (cases 4, 6-8)
def _scalar(v: str) -> Any:
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if re.fullmatch(r"-?\d+\.\d*", v):
        return float(v)
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [] if not inner else [_scalar(x) for x in re.split(r",(?![^\[]*\])", inner)]
    return v


def parse_mini_yaml(text: str) -> Any:
    """Subset YAML: mappings, block lists (of scalars or mappings), inline [a, b] lists, scalars.
    Comments after ' #' are dropped. Enough for figure cards; not a general YAML parser."""
    lines = []
    for raw in text.splitlines():
        line = re.sub(r"\s+#.*$", "", raw) if not raw.lstrip().startswith("#") else ""
        if line.strip():
            lines.append((len(line) - len(line.lstrip(" ")), line.strip()))

    def block(i: int, indent: int) -> tuple[Any, int]:
        if i < len(lines) and lines[i][1].startswith("- "):
            out: list = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                body = lines[i][1][2:]
                if re.match(r"^[\w\-]+:\s", body + " ") and not body.startswith(("[", "\"", "'")):
                    # list item that is a mapping: re-read its first key at a virtual indent
                    lines[i] = (indent + 2, body)
                    item, i = mapping(i, indent + 2)
                    out.append(item)
                else:
                    out.append(_scalar(body))
                    i += 1
            return out, i
        return mapping(i, indent)

    def mapping(i: int, indent: int) -> tuple[dict, int]:
        out: dict = {}
        while i < len(lines) and lines[i][0] == indent and not lines[i][1].startswith("- "):
            m = re.match(r"^([\w\-]+):\s*(.*)$", lines[i][1])
            if not m:
                i += 1
                continue
            key, rest = m.group(1), m.group(2)
            i += 1
            if rest == "" and i < len(lines) and lines[i][0] > indent:
                out[key], i = block(i, lines[i][0])
            elif rest == "" and i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                out[key], i = block(i, indent)
            else:
                out[key] = _scalar(rest)
        return out, i

    if not lines:
        return {}
    val, _ = block(0, lines[0][0])
    return val


def load_card(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)
    if path.suffix == ".md":
        m = re.search(r"```(?:yaml|yml)?\s*\n(.*?)```", text, re.S)
        text = m.group(1) if m else ""
    data = parse_mini_yaml(text)
    return data if isinstance(data, dict) else None


def _as_list(v: Any) -> list:
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


def _resolves(project_root: Path, ref: str) -> bool:
    """'path' or 'path::anchor': the file exists and (if given) the anchor text occurs in it."""
    path, _, anchor = str(ref).partition("::")
    p = project_root / path.strip()
    if not path.strip() or not p.is_file():
        return False
    if not anchor.strip():
        return True
    return anchor.strip().lower() in p.read_text(encoding="utf-8", errors="replace").lower()


def check_figure_cards(rcs: Path, project_root: Path, ev_items: list[dict], rep) -> None:
    d = rcs / "plan" / "figure_cards"
    if not d.is_dir():
        return
    by_id = {e.get("id"): e for e in ev_items}
    tickets = ""
    me = rcs / "evidence" / "missing_evidence.json"
    if me.exists():
        tickets = me.read_text(encoding="utf-8")
    for path in sorted(p for p in d.iterdir() if p.suffix in CARD_SUFFIXES):
        try:
            card = load_card(path)
        except Exception as exc:  # noqa: BLE001
            rep.add("ERROR", f"figure_cards/{path.name}", f"unparsable card: {exc}")
            continue
        if not card:
            continue
        cid = str(card.get("id") or path.stem)
        where = f"figure_cards/{cid}"
        ftype = str(card.get("type") or card.get("kind") or "").strip().lower()
        blocked_ok = str(card.get("status", "")).lower() == "blocked" and cid in tickets
        if ftype == "illustrative" or card.get("illustrative") is True:
            if str(card.get("label", "")).strip().upper() != ILLUSTRATIVE_LABEL:
                rep.add("ERROR", where, f"illustrative visual without the label '{ILLUSTRATIVE_LABEL}' (UNLABELLED_ILLUSTRATION)")
            continue
        if ftype in NON_EVIDENCE_VISUALS:
            comps = _as_list(card.get("components"))
            if not comps:
                rep.add("WARN", where, "schematic lists no components: nothing can be checked against code/docs")
            for comp in comps:
                comp = comp if isinstance(comp, dict) else {"name": comp}
                if str(comp.get("status", "")).lower() == "proposed":
                    if "proposed" not in str(card.get("label", "")).lower():
                        rep.add("ERROR", where, f"component {comp.get('name')!r} is proposed but the visual is not labelled as "
                                                "showing proposed components (UNTRACED_COMPONENT)")
                    continue
                refs = _as_list(comp.get("traced_to"))
                if not refs or not all(_resolves(project_root, r) for r in refs if r):
                    rep.add("ERROR", where, f"component {comp.get('name')!r} does not trace to project code/docs "
                                            f"({refs or 'no traced_to'}) (UNTRACED_COMPONENT): remove it or mark it proposed")
            continue
        if ftype in IMAGE_VISUALS or card.get("samples"):
            for s in _as_list(card.get("samples")):
                s = s if isinstance(s, dict) else {"id": s}
                if str(s.get("permission", "")).lower() != "granted" or \
                        (s.get("identifying_data") is not False and s.get("privacy_cleared") is not True):
                    rep.add("ERROR", where, f"sample {s.get('id')!r}: permission={s.get('permission')!r}, "
                                            f"identifying_data={s.get('identifying_data')!r} (BLOCKED_PERMISSION): "
                                            "block publication until permission and privacy are resolved")
            if card.get("samples") and not card.get("selection_rule"):
                rep.add("WARN", where, "qualitative samples without a declared selection_rule (cherry-picking risk)")
        # evidence-bearing visual (chart, table, image of real outputs)
        evs = [by_id.get(r) for r in _as_list(card.get("evidence"))]
        live = [e for e in evs if e and e.get("status") in {"ok", "incomplete"}]
        bad_refs = [r for r, e in zip(_as_list(card.get("evidence")), evs) if not e]
        data = _as_list(card.get("source_data"))
        missing_data = [p for p in data if not (project_root / str(p)).exists()]
        problems = []
        if not live:
            problems.append("no live evidence item")
        if bad_refs:
            problems.append(f"unknown evidence {', '.join(map(str, bad_refs))}")
        if missing_data:
            problems.append(f"source data missing: {', '.join(map(str, missing_data))}")
        if problems:
            if blocked_ok:
                rep.add("WARN", where, f"fail-closed: blocked with a missing-evidence ticket ({'; '.join(problems)}) (VISUAL_BLOCKED)")
            else:
                rep.add("ERROR", where, f"{'; '.join(problems)} (NO_VALID_VISUAL): do not draw it; set status 'blocked' "
                                        "and add a missing_evidence ticket naming this figure")


# ------------------------------------------------------------------------------ entry point
def run(rcs: Path, project_root: Path, loaded: dict, rep) -> None:
    ev = loaded.get("evidence/research_evidence.json") or {}
    cm = loaded.get("claims/claim_evidence_map.json") or {}
    sr = loaded.get("corpus/source_registry.json") or {}
    ev_items = ev.get("items", []) if isinstance(ev, dict) else []
    claims = cm.get("claims", []) if isinstance(cm, dict) else []
    check_conflicts(ev_items, claims, rep)
    check_claim_provenance(ev_items, claims, rep)
    check_sources(sr.get("sources", []) if isinstance(sr, dict) else [], rep)
    check_figure_cards(rcs, project_root, ev_items, rep)
