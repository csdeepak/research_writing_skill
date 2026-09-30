#!/usr/bin/env python3
"""Visual gates V1-V6 (vNext Stage 2; docs/06_VNEXT_SPEC.md sections 4.5, 6, 7) for .rcs/plan/visual_registry.json.

  V1 provenance      source files exist and are unchanged since rendering; evidence/claim IDs are live;
                     every plotted value occurs in the declared upstream `source_text`; no decorative
                     visuals; hand-made external figures cannot pass without a recorded human check
  V2 numerical       the SVG's marks equal a fresh re-run of the declared transform; every number in the
                     caption traces to the plotted data, n, or the cited evidence
  V3 semantic        bar axes start at zero and bar lengths match their values; every in-scope row is shown;
                     V3_AXIS_ENCODING: the labelled value axis agrees with where every mark sits (renderer-independent:
                     the value axis is found from the tick layout, pixel = a + b*value is fitted from the ticks, and each
                     mark must lie on it; Stage 4 e2e found a line chart whose value ticks were on the x axis)
                     or excluded with a reason; duplicated rows need a declared aggregation; available
                     uncertainty is shown; captions carry no unlicensed implication; adverse results are not
                     demoted to the supplement while favourable ones stay in the main text
  V4 text alignment  (needs --draft) the paper refers to "Figure N", and that prose carries the figure's
                     claim tags; caption opens with a declarative takeaway and meets its requirements
  V5 usability       machine part: alt text, fonts >= 11 px, <= 6 series, colour-independent encoding.
                     The human part (1-second topic, 10-second takeaway, 1-minute detail) is recorded
                     separately in `human_review`; without it V5 is NOT_RUN, never "passed"
  V6 regeneration    re-rendering from the recorded inputs reproduces the figure byte for byte

Also M06 (a visual is not needed / duplicates a table) and M10 (main-text budget) as warnings.

Usage: python tools/validate_visuals.py .rcs [--project-root DIR] [--draft paper.md] [--out REPORT] [--json]
Exit code 1 if any ERROR.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint_draft  # noqa: E402
import visuals  # noqa: E402
from rce_common import CLAIM_ID_RE, CLAIM_TAG_RE, split_sentences  # noqa: E402
from verify_numbers import numbers_in  # noqa: E402

GATES = ("V1", "V2", "V3", "V4", "V5", "V6")
KINDS = {"EXPLANATORY", "ANALYTICAL", "COMPARATIVE", "QUALITATIVE", "STRUCTURAL", "CONTEXTUAL", "DECORATIVE"}
NON_TAKEAWAY_RE = re.compile(r"^\s*(comparison|plot|graph|chart|figure|overview|illustration|visuali[sz]ation|"
                             r"results?|summary|table)\s+(of|showing|for)\b", re.I)
# "95% confidence interval": the interval level is a method parameter, not a data value
LEVEL_RE = re.compile(r"\b\d{2}(?:\.\d)?%\s*(?:bootstrap\s+)?(?:CIs?|confidence|credible|prediction|intervals?)", re.I)
MARK_RE = re.compile(r'<g class="mark" ([^>]*)>(.*?)</g>', re.S)
ATTR_RE = re.compile(r'([\w-]+)="([^"]*)"')
REQUIREMENTS = {
    "n": re.compile(r"\bn\s*=\s*\d|\b\d+\s+(questions|queries|runs|seeds|samples|items|participants)\b", re.I),
    "uncertainty": re.compile(r"\b(CIs?|confidence intervals?|std|standard deviations?|standard errors?|SE|error bars?|whiskers?|intervals?)\b", re.I),
    "metric": None,       # checked against the entry's value_label / y column
    "units": None,        # checked against the entry's units
    "source": re.compile(r"\b(source|from|data:|table \d|reported in)\b", re.I),
    "split": re.compile(r"\b(test|validation|dev|held[- ]out|train(ing)?)\s+(split|set)\b", re.I),
    "models": re.compile(r"\b(model|system|method|baseline)s?\b", re.I),
}


class Rep:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, gate: str, level: str, vid: str, code: str, msg: str) -> None:
        self.items.append({"gate": gate, "level": level, "visual": vid, "code": code, "message": msg})

    def errors(self, gate: str | None = None) -> int:
        return sum(1 for i in self.items if i["level"] == "ERROR" and (gate is None or i["gate"] == gate))


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))


def _traces(v: float, pool: list[float], token: str | None = None) -> bool:
    """v equals a pool value, or is that value rounded to v's own precision (0.42 from 0.4155), or the
    same value as % <-> fraction."""
    s = token.rstrip("%") if token else f"{v:.10g}"
    dec = len(s.split(".")[1]) if "." in s else 0
    tol = 0.5 * 10 ** (-dec) + 1e-9
    return any(abs(v - c) <= tol for p in pool for c in (p, p * 100, p / 100))


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


TICK_RE = re.compile(r'<text class="tick" ([^>]*)>([-\d.]+)</text>')
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")
SHAPE_RE = re.compile(r"<(?:circle|rect|polygon|path)\b[^>]*>")


def _center(attrs: dict, inner: str) -> tuple[float, float] | None:
    """Mark centre: declared data-cx/data-cy, a bar's end, or the bounding-box centre of the first shape."""
    if "data-cx" in attrs and "data-cy" in attrs:
        return float(attrs["data-cx"]), float(attrs["data-cy"])
    shape = SHAPE_RE.search(inner)          # the marker itself, not its value label or error bar
    if shape is None:
        return None
    a = dict(ATTR_RE.findall(shape.group(0)))
    if "data-px-end" in a and "y" in a and "height" in a:
        return float(a["data-px-end"]), float(a["y"]) + float(a["height"]) / 2
    if "cx" in a and "cy" in a:
        return float(a["cx"]), float(a["cy"])
    if "x" in a and "y" in a and "width" in a and "height" in a:
        return float(a["x"]) + float(a["width"]) / 2, float(a["y"]) + float(a["height"]) / 2
    geo = a.get("points") or a.get("d")
    if geo:
        n = [float(v) for v in NUM_RE.findall(geo)]
        xs, ys = n[0::2], n[1::2]
        if xs and ys:
            return (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    return None


def axis_encoding(svg: str, tol: float = 1.5) -> list[str]:
    ticks = []
    for m in TICK_RE.finditer(svg):
        a = dict(ATTR_RE.findall(m.group(1)))
        ticks.append((float(m.group(2)), a))
    if len(ticks) < 2:
        return []
    axis = ticks[0][1].get("data-axis")
    if axis not in ("x", "y"):
        if len({t[1].get("y") for t in ticks}) == 1:
            axis = "x"
        elif len({t[1].get("x") for t in ticks}) == 1:
            axis = "y"
        else:
            return ["value-axis ticks lie on no single axis"]
    pos = [float(t[1].get("data-pos", t[1].get(axis, "nan"))) for t in ticks]
    (v0, p0), (v1, p1) = (ticks[0][0], pos[0]), (ticks[-1][0], pos[-1])
    if v1 == v0:
        return []
    b = (p1 - p0) / (v1 - v0)
    a0 = p0 - b * v0
    bad = []
    for m in MARK_RE.finditer(svg):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        c = _center(attrs, m.group(2))
        if c is None or "data-y" not in attrs:
            continue
        coord = c[0] if axis == "x" else c[1]
        want = a0 + b * float(attrs["data-y"])
        if abs(coord - want) > tol:
            bad.append(f"{attrs.get('data-series', '')}@{attrs.get('data-x')}: value {attrs['data-y']} drawn at {coord:.1f}px "
                       f"on the {axis} axis, where the tick labels put it at {want:.1f}px")
    return bad


def parse_marks(svg: str) -> list[dict]:
    out = []
    for m in MARK_RE.finditer(svg):
        attrs = dict(ATTR_RE.findall(m.group(1)))
        inner = dict(ATTR_RE.findall(m.group(2)))
        out.append({"x": attrs.get("data-x"), "y": float(attrs["data-y"]), "series": attrs.get("data-series", ""),
                    "err_low": float(attrs["data-err-low"]) if "data-err-low" in attrs else None,
                    "err_high": float(attrs["data-err-high"]) if "data-err-high" in attrs else None,
                    "px_start": float(inner["data-px-start"]) if "data-px-start" in inner else None,
                    "px_end": float(inner["data-px-end"]) if "data-px-end" in inner else None})
    return out


def check(rcs: Path, root: Path, draft: str | None, rep: Rep) -> dict:
    reg = visuals.load_registry(rcs)
    entries = reg.get("visuals", [])
    ev = {e.get("id"): e for e in load_json(rcs / "evidence" / "research_evidence.json", {}).get("items", [])}
    cm = load_json(rcs / "claims" / "claim_evidence_map.json", {})
    claims = {c["id"]: c for c in cm.get("claims", []) + [dict(l, claim_type="limitation") for l in cm.get("limitations", [])]}
    license_mode = any("licenses" in c for c in claims.values())
    human = {}
    budget = (load_json(rcs / "state.json", {}) or {}).get("max_main_figures", 6)
    main_rq: dict[str, list[str]] = {}
    for e in entries:
        vid = e.get("id", "?")
        kind = str(e.get("kind", "")).upper()
        rpr = e.get("representation", "")
        if kind not in KINDS:
            rep.add("V1", "ERROR", vid, "V1_KIND_MISSING", f"kind must be one of {sorted(KINDS)}")
        if kind == "DECORATIVE":
            rep.add("V1", "ERROR", vid, "DECORATIVE_VISUAL", "decorative visuals carry no information: remove it (M04)")
            continue
        if e.get("status") in ("BLOCKED", "NO_VALID_VISUAL"):
            rep.add("V1", "WARN", vid, "VISUAL_BLOCKED", f"status {e.get('status')}: not published (fail-closed)")
            continue
        # ---- V1 provenance
        for r in e.get("evidence_ids", []) or []:
            if r not in ev or ev[r].get("status") in ("superseded",):
                rep.add("V1", "ERROR", vid, "V1_EVIDENCE_UNKNOWN", f"evidence {r} unknown or superseded")
            elif ev[r].get("status") == "conflicting" and not any(
                    isinstance(x.get("resolution"), dict) for x in [ev[r]] + [ev.get(c, {}) for c in ev[r].get("conflicts_with") or []]):
                rep.add("V1", "ERROR", vid, "V1_EVIDENCE_CONFLICTING", f"evidence {r} is in an unresolved conflict")
        for c in e.get("claim_ids", []) or []:
            if c not in claims:
                rep.add("V1", "ERROR", vid, "V1_CLAIM_UNKNOWN", f"claim {c} not in the claim map")
            elif claims[c].get("status") == "BLOCKED":
                rep.add("V1", "ERROR", vid, "V1_CLAIM_BLOCKED", f"claim {c} is BLOCKED")
        if not e.get("evidence_ids"):
            rep.add("V1", "ERROR", vid, "V1_NO_EVIDENCE", "a published visual needs >= 1 evidence ID")
        if not e.get("reader_question"):
            rep.add("V1", "ERROR", vid, "V1_NO_READER_QUESTION", "every visual answers one reader question (M09)")
        if e.get("external_figure"):
            hr = e.get("human_review") or {}
            rep.add("V1", "WARN" if hr.get("provenance_checked") else "ERROR", vid, "V1_EXTERNAL_FIGURE",
                    "figure not generated from a declared transform: provenance cannot be machine-verified"
                    + ("" if hr.get("provenance_checked") else "; record a human provenance check or regenerate it"))
            continue
        if rpr == "table":
            continue
        spec = e.get("data") or {}
        files = [spec.get("file")] + ([spec["source_text"]] if spec.get("source_text") else [])
        missing = [f for f in files if not f or not (root / f).is_file()]
        if missing:
            rep.add("V1", "ERROR", vid, "V1_SOURCE_MISSING", f"source file(s) missing: {missing}")
            continue
        for f in files:
            rec = (e.get("source_hashes") or {}).get(f)
            if rec and rec != visuals.sha256(root / f):
                rep.add("V1", "ERROR", vid, "V1_SOURCE_CHANGED", f"{f} changed since the figure was rendered: re-render and re-check")
        try:
            data = visuals.transform(spec, root)
        except Exception as exc:  # noqa: BLE001
            rep.add("V1", "ERROR", vid, "V1_TRANSFORM_FAILED", str(exc))
            continue
        pts = data["points"]
        values = [p[k] for p in pts for k in ("y", "err_low", "err_high") if p.get(k) is not None]
        if spec.get("source_text"):
            pool = numbers_in((root / spec["source_text"]).read_text(encoding="utf-8", errors="replace"))
            for v in values:
                if not _traces(v, pool):
                    rep.add("V1", "ERROR", vid, "V1_UNTRACED_VALUE",
                            f"plotted value {v:g} does not occur in {spec['source_text']} (re-typed or invented)")
        # ---- V3 data scope
        for x in spec.get("exclude", []) or []:
            if len(str(x.get("reason", "")).strip()) < 10:
                rep.add("V3", "ERROR", vid, "V3_EXCLUSION_UNEXPLAINED", f"excluded {x.get('x')!r} without a reason (>= 10 chars)")
        keys = [(p["x"], p["series"]) for p in pts]
        if len(keys) != len(set(keys)) and not spec.get("aggregation"):
            rep.add("V3", "ERROR", vid, "V3_UNDECLARED_AGGREGATION", "several rows map to the same mark: declare `aggregation`")
        has_n = any(str(r.get("n", "")).strip() not in ("", "1") for r in data["universe"])
        if has_n and not spec.get("err_low") and rpr != "table" and len(str(spec.get("uncertainty_note", ""))) < 10:
            rep.add("V3", "WARN", vid, "V3_UNCERTAINTY_HIDDEN", "rows have n > 1 but no interval is drawn: show it or say why")
        # ---- render-level checks (V2, V3 geometry, V5, V6)
        fp = root / e.get("figure_path", "")
        if not e.get("figure_path") or not fp.is_file():
            rep.add("V6", "ERROR", vid, "V6_NOT_RENDERED", "figure file missing: run tools/visuals.py render")
            continue
        svg = fp.read_text(encoding="utf-8")
        try:
            fresh, _ = visuals.render_entry(e, root)
        except Exception as exc:  # noqa: BLE001
            rep.add("V6", "ERROR", vid, "V6_NOT_REPRODUCIBLE", f"cannot re-render: {exc}")
            fresh = None
        if fresh is not None and hashlib.sha256(fresh.encode()).hexdigest() != hashlib.sha256(svg.encode()).hexdigest():
            rep.add("V6", "ERROR", vid, "V6_NOT_REPRODUCIBLE", "re-rendering from the recorded inputs does not reproduce the file "
                                                               "(edited by hand, or inputs changed)")
        marks = parse_marks(svg)
        want = sorted((p["x"], p["series"], p["y"]) for p in pts)
        got = sorted((m["x"], m["series"], m["y"]) for m in marks)
        if len(want) != len(got) or any(a[:2] != b[:2] or not _close(a[2], b[2]) for a, b in zip(want, got)):
            rep.add("V2", "ERROR", vid, "V2_MARK_MISMATCH", f"figure shows {len(got)} marks {got[:4]}... but the data gives "
                                                             f"{len(want)} {want[:4]}...")
        if rpr == "bar_h":
            lo = float(re.search(r'data-domain-lo="([^"]+)"', svg).group(1))
            hi = float(re.search(r'data-domain-hi="([^"]+)"', svg).group(1))
            pl = float(re.search(r'data-plot-left="([^"]+)"', svg).group(1))
            pr = float(re.search(r'data-plot-right="([^"]+)"', svg).group(1))
            if lo != 0:
                rep.add("V3", "ERROR", vid, "V3_TRUNCATED_AXIS", f"bar axis starts at {lo:g}, not 0")
            for m in marks:
                if m["px_start"] is None:
                    continue
                expect = (m["y"] - lo) / (hi - lo) * (pr - pl)
                if abs((m["px_end"] - m["px_start"]) - expect) > 0.6:
                    rep.add("V3", "ERROR", vid, "V3_ENCODING_MISMATCH",
                            f"bar for {m['x']} is {m['px_end'] - m['px_start']:.1f}px but its value implies {expect:.1f}px")
        enc = axis_encoding(svg)
        if enc:
            rep.add("V3", "ERROR", vid, "V3_AXIS_ENCODING", f"{len(enc)} mark(s) disagree with the labelled value axis, "
                                                             f"e.g. {enc[0]}")
        if not re.search(r"<desc[^>]*>[^<]{20,}</desc>", svg) or len(str(e.get("alt_text", "")).split()) < 8:
            rep.add("V5", "ERROR", vid, "V5_NO_ALT_TEXT", "alt text missing or under 8 words (type, variables, takeaway)")
        ticks = [float(t) for t in re.findall(r'<text class="tick"[^>]*>([-\d.]+)</text>', svg)]
        steps = {round(b - a, 9) for a, b in zip(ticks, ticks[1:])}
        if ticks and (len(steps) > 1 or not steps or not any(
                abs(next(iter(steps)) - m * 10 ** k) < 1e-9 for m in (1, 2, 2.5, 5) for k in range(-6, 7))):
            rep.add("V5", "ERROR", vid, "V5_UNREADABLE_TICKS", f"axis ticks {ticks} are not evenly spaced round numbers")
        for lab in re.findall(r'<text class="(?:legend|category)"[^>]*>([^<]*)</text>', svg):
            if "_" in lab:
                rep.add("V5", "ERROR", vid, "V5_RAW_LABEL", f"label {lab!r} is a raw column value: add x_labels/series_labels")
        dom = e.get("domain")
        if dom and ticks and (min(ticks) < dom[0] - 1e-9 or max(ticks) > dom[1] + 1e-9):
            rep.add("V3", "ERROR", vid, "V3_DOMAIN_VIOLATION", f"axis {min(ticks)}..{max(ticks)} leaves the declared domain {dom}")
        fonts = [float(x) for x in re.findall(r'font-size="([\d.]+)"', svg)]
        if fonts and min(fonts) < visuals.MIN_FONT:
            rep.add("V5", "ERROR", vid, "V5_FONT_TOO_SMALL", f"font size {min(fonts)} px < {visuals.MIN_FONT}")
        hr = e.get("human_review") or {}
        human[vid] = all(hr.get(k) is True for k in ("one_second_topic", "ten_second_takeaway", "one_minute_detail"))
        if hr and hr.get("render_sha256_reviewed") and hr["render_sha256_reviewed"] != e.get("render_sha256"):
            human[vid] = False       # the figure changed after the person reviewed it
            rep.add("V5", "WARN", vid, "V5_REVIEW_STALE", "the figure was re-rendered after the human review: review it again")
        # ---- caption (V2 numbers, V3 implications, V4/M09 contract)
        cap = str(e.get("caption", "")).strip()
        first = split_sentences(cap)[0] if cap else ""
        if not cap:
            rep.add("V4", "ERROR", vid, "M09_NO_CAPTION", "caption missing")
        elif NON_TAKEAWAY_RE.search(first):
            rep.add("V4", "ERROR", vid, "M09_CAPTION_NO_TAKEAWAY",
                    f"caption opens with a description ({first[:50]!r}); open with the finding (M09)")
        pool = values + [float(r.get("n")) for r in data["universe"] if visuals._num(r.get("n")) is not None]
        for r in e.get("evidence_ids", []) or []:
            if r in ev:
                pool += numbers_in(json.dumps(ev[r].get("value")))
        for m in re.finditer(r"(?<![\w.])\d+(?:\.\d+)?%?", LEVEL_RE.sub(" ", CLAIM_TAG_RE.sub("", cap))):
            tok = m.group(0)
            v = float(tok.rstrip("%"))
            if (not tok.endswith("%") and "." not in tok and v <= 12) or 1900 <= v <= 2100:
                continue
            if not _traces(v, pool, tok):
                rep.add("V2", "ERROR", vid, "V2_CAPTION_NUMBER", f"caption number {tok} is not in the plotted data or cited evidence")
        vclaims = [claims[c] for c in e.get("claim_ids", []) or [] if c in claims]
        L = lint_draft.Lint()
        for s in split_sentences(cap):
            lint_draft.check_licenses(s, [c["id"] for c in vclaims], {c["id"]: c for c in vclaims}, L, 0, license_mode)
        for f in L.findings:
            rep.add("V3", f["level"], vid, "V3_UNLICENSED_CAPTION", f"caption: {f['message']}")
        for fi in e.get("forbidden_implications", []) or []:
            rx = lint_draft.LICENSE_TERMS.get(fi)
            hit = rx.search(cap) if rx else (str(fi).lower() in cap.lower())
            if hit:
                rep.add("V3", "ERROR", vid, "V3_FORBIDDEN_IMPLICATION", f"caption implies {fi!r}, which this figure forbids")
        for req in e.get("caption_requirements", []) or []:
            ok = True
            if req == "metric":
                norm = re.sub(r"[^a-z0-9]", "", cap.lower())
                if spec.get("series"):     # multi-metric figure: every series (metric) must be named
                    names = {p["series"] for p in pts}
                else:
                    names = {str(e.get("value_label") or spec.get("y", "")).split(" (")[0]}
                ok = all(re.sub(r"[^a-z0-9]", "", n.lower()) in norm for n in names)
            elif req == "units":
                ok = not e.get("units") or str(e["units"]).lower() in cap.lower()
            elif req in REQUIREMENTS and REQUIREMENTS[req] is not None:
                ok = bool(REQUIREMENTS[req].search(cap))
            if not ok:
                rep.add("V4", "ERROR", vid, "M09_CAPTION_INCOMPLETE", f"caption lacks required element '{req}'")
        # ---- M06 / M10
        if rpr != "table" and len(pts) <= 3 and len({p["series"] for p in pts}) == 1 and not spec.get("err_low"):
            rep.add("V3", "WARN", vid, "M06_PROSE_SUFFICES", f"{len(pts)} values: state them in a sentence instead (M06)")
        if e.get("tier", "main") == "main":
            main_rq.setdefault(str(e.get("rq", "")), []).append(vid)
    # tables duplicated as charts
    tables = {(t["data"].get("file"), json.dumps(t["data"].get("scope"), sort_keys=True), t["data"].get("y"))
              for t in entries if t.get("representation") == "table" and t.get("data")}
    for e in entries:
        d = e.get("data") or {}
        if e.get("representation") != "table" and (d.get("file"), json.dumps(d.get("scope"), sort_keys=True), d.get("y")) in tables \
                and not e.get("distinct_value"):
            rep.add("V3", "WARN", e["id"], "M06_DUPLICATES_TABLE", "same data as a table: state the figure's distinct reader value or drop it")
    mains = [e for e in entries if e.get("tier", "main") == "main" and e.get("status") not in ("BLOCKED", "NO_VALID_VISUAL")]
    if len(mains) > budget:
        rep.add("V3", "WARN", "*", "M10_OVER_BUDGET", f"{len(mains)} main-text visuals exceed the budget of {budget}")
    for e in entries:
        adverse = any(claims.get(c, {}).get("negative_results") for c in e.get("claim_ids", []) or []) or \
            any(ev.get(r, {}).get("kind") == "negative_result" for r in e.get("evidence_ids", []) or [])
        if adverse and e.get("tier") == "supplementary" and main_rq.get(str(e.get("rq", ""))):
            rep.add("V3", "ERROR", e["id"], "M10_ADVERSE_DEMOTED",
                    f"adverse result moved to the supplement while {main_rq[str(e.get('rq', ''))]} on the same question "
                    "stay in the main text: never hide material adverse findings")
    # ---- V4 draft alignment
    v4_run = draft is not None
    if draft is not None:
        paras = [q.replace("\n", " ") for q in re.split(r"\n\s*\n", draft) if q.strip()]   # a reference's paragraph
        for e in entries:
            if e.get("status") in ("BLOCKED", "NO_VALID_VISUAL") or e.get("kind", "").upper() == "DECORATIVE" \
                    or e.get("tier") == "supplementary":
                continue
            num = e.get("number")
            label = "Table" if e.get("representation") == "table" else "Figure"
            refs = [q for q in paras if num is not None and re.search(rf"\b{label}\s+{num}\b", q)]
            if not refs:
                rep.add("V4", "ERROR", e["id"], "V4_NOT_REFERENCED", f"the paper never refers to {label} {num}")
                continue
            tags = set(CLAIM_ID_RE.findall(" ".join(m.group(0) for q in refs for m in CLAIM_TAG_RE.finditer(q))))
            if e.get("claim_ids") and not tags & set(e["claim_ids"]):
                rep.add("V4", "WARN", e["id"], "V4_UNBOUND_REFERENCE",
                        f"prose referring to {label} {num} carries none of its claims {e['claim_ids']}")
    # ---- gate summary
    status = {}
    for g in GATES:
        if g == "V4" and not v4_run:
            status[g] = "NOT_RUN"
        elif g == "V5":
            status[g] = "FAILED" if rep.errors("V5") else ("PASSED" if human and all(human.values()) else "NOT_RUN")
        else:
            status[g] = "FAILED" if rep.errors(g) else "PASSED"
    return status


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rcs")
    ap.add_argument("--project-root")
    ap.add_argument("--draft")
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    root = Path(a.project_root) if a.project_root else rcs.resolve().parent
    rep = Rep()
    draft = Path(a.draft).read_text(encoding="utf-8") if a.draft else None
    status = check(rcs, root, draft, rep)
    reg_p = rcs / "plan" / "visual_registry.json"
    report = {"tool": "validate_visuals", "errors": rep.errors(),
              "registry_sha256": visuals.sha256(reg_p) if reg_p.exists() else None,
              "draft_sha256": hashlib.sha256(draft.encode()).hexdigest() if draft is not None else None,
              "gates": {g: {"status": status[g], "errors": rep.errors(g)} for g in GATES}, "items": rep.items}
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(report, indent=2), encoding="utf-8")
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        for i in rep.items:
            print(f"{i['level']:5} {i['gate']} {i['visual']:6} {i['code']:28} {i['message']}")
        print("gates: " + ", ".join(f"{g}={status[g]}" for g in GATES))
        print(f"\n{rep.errors()} error(s)")
    return 1 if rep.errors() else 0


if __name__ == "__main__":
    sys.exit(main())
