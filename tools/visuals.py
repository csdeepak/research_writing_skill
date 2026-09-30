#!/usr/bin/env python3
"""Evidence-bound figure generation (vNext Stage 2: M05 registry, M07 code-driven generation).

A figure is never drawn by hand and never from remembered numbers. Each visual is an entry V### in
.rcs/plan/visual_registry.json whose `data` block is a *declarative* transform of a real project file:

  "data": {"file": "data/aggregates.json",          # csv, or json list of records
           "scope": {"metric": "token_f1"},          # the universe of rows this figure is about
           "exclude": [{"x": "D System+RAG", "reason": "different model, not comparable"}],
           "x": "system", "y": "mean",               # category/position and value columns
           "err_low": "ci_low", "err_high": "ci_high", "series": null,
           "source_text": "project/paper.txt"}       # optional upstream document every value must occur in

Every row in `scope` is drawn unless it is excluded *with a reason* (V3). The renderer is stdlib-only and
deterministic, so re-rendering from the same inputs yields byte-identical SVG (V6). Marks carry their data
values as attributes (data-x, data-y, ...) so the validator can check the drawing against the data (V2/V3).

Representations: bar_h (horizontal bars, zero baseline), dot_ci (dots with interval whiskers), line
(ordered x, markers). Colour: Okabe-Ito palette, always paired with a marker shape (colour-independent).

Usage:
  python tools/visuals.py render .rcs [--project-root DIR] [--only V001]   # render + record hashes
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import math
import sys
from pathlib import Path

WIDTH = 640
FONT = 12                    # px at 640 px width; V5 requires >= 11
MIN_FONT = 11
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00"]   # Okabe-Ito
MARKERS = ["circle", "square", "triangle", "diamond", "cross", "star"]
MAX_SERIES = 6
REPRESENTATIONS = ("bar_h", "dot_ci", "line")


# ------------------------------------------------------------------------------------ data
def sha256(p: Path) -> str:
    return "sha256:" + hashlib.sha256(p.read_bytes()).hexdigest()


def load_records(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with open(path, encoding="utf-8", newline="") as fh:
            return [dict(r) for r in csv.DictReader(fh)]
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = data.get("records", [])
    if not isinstance(data, list) or not all(isinstance(r, dict) for r in data):
        raise ValueError(f"{path}: expected a list of records")
    return data


def _num(v) -> float | None:
    if isinstance(v, bool):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip().replace(",", ""))
    except ValueError:
        return None


def _match(row: dict, cond: dict) -> bool:
    for k, want in (cond or {}).items():
        got = str(row.get(k, ""))
        if isinstance(want, list):
            if got not in [str(w) for w in want]:
                return False
        elif got != str(want):
            return False
    return True


def transform(spec: dict, root: Path) -> dict:
    """Apply the declarative data spec. Returns universe, shown points, excluded rows."""
    rows = load_records(root / spec["file"])
    universe = [r for r in rows if _match(r, spec.get("scope", {}))]
    excl = {str(e.get("x")): e.get("reason", "") for e in spec.get("exclude", []) or []}
    x, y = spec["x"], spec["y"]
    pts, dropped = [], []
    for r in universe:
        if str(r.get(x)) in excl:
            dropped.append({"x": str(r.get(x)), "reason": excl[str(r.get(x))]})
            continue
        p = {"x": str(r.get(x)), "y": _num(r.get(y)), "series": str(r.get(spec["series"])) if spec.get("series") else ""}
        for k in ("err_low", "err_high"):
            if spec.get(k):
                p[k] = _num(r.get(spec[k]))
        pts.append(p)
    return {"universe": universe, "points": pts, "excluded": dropped}


# ---------------------------------------------------------------------------------- render
def _fmt(v: float) -> str:
    return f"{v:.6g}"


def value_label(v: float, sig: int = 3) -> str:
    """Round half-up on the decimal value as written (0.4155 -> 0.416), not on the binary float
    (f"{0.4155:.3g}" gives 0.415), so figure labels agree with rounded numbers in the prose."""
    from decimal import ROUND_HALF_UP, Decimal
    d = Decimal(repr(v))
    if d == 0:
        return "0"
    q = Decimal(1).scaleb(d.adjusted() - sig + 1)
    return format(d.quantize(q, rounding=ROUND_HALF_UP).normalize(), "f")


def _nice_max(v: float) -> float:
    if v <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * e:
            return m * e
    return 10 * e


def nice_step(span: float, n: int = 5) -> float:
    raw = (span or 1.0) / n
    e = 10 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * e + 1e-12:
            return m * e
    return 10 * e


def _ticks(lo: float, hi: float, step: float) -> list[float]:
    k0, k1 = round(lo / step), round(hi / step)
    return [round(k * step, 10) for k in range(k0, k1 + 1)]


def _tick_label(v: float, step: float) -> str:
    dec = max(0, -math.floor(math.log10(step) + 1e-9)) + (1 if round(step / 10 ** math.floor(math.log10(step)), 6) == 2.5 else 0)
    return f"{v:.{dec}f}"


def _marker(kind: str, cx: float, cy: float, r: float, color: str) -> str:
    if kind == "square":
        return f'<rect x="{cx - r:.2f}" y="{cy - r:.2f}" width="{2 * r:.2f}" height="{2 * r:.2f}" fill="{color}"/>'
    if kind == "triangle":
        return f'<polygon points="{cx:.2f},{cy - r:.2f} {cx - r:.2f},{cy + r:.2f} {cx + r:.2f},{cy + r:.2f}" fill="{color}"/>'
    if kind == "diamond":
        return f'<polygon points="{cx:.2f},{cy - r:.2f} {cx + r:.2f},{cy:.2f} {cx:.2f},{cy + r:.2f} {cx - r:.2f},{cy:.2f}" fill="{color}"/>'
    if kind == "cross":
        return (f'<path d="M{cx - r:.2f},{cy - r:.2f}L{cx + r:.2f},{cy + r:.2f}M{cx - r:.2f},{cy + r:.2f}L{cx + r:.2f},{cy - r:.2f}" '
                f'stroke="{color}" stroke-width="2"/>')
    if kind == "star":
        pts = " ".join(f"{cx + (r if i % 2 == 0 else r / 2) * math.sin(i * math.pi / 5):.2f},"
                       f"{cy - (r if i % 2 == 0 else r / 2) * math.cos(i * math.pi / 5):.2f}" for i in range(10))
        return f'<polygon points="{pts}" fill="{color}"/>'
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{color}"/>'


def render_svg(entry: dict, data: dict) -> str:
    rep = entry["representation"]
    if rep not in REPRESENTATIONS:
        raise ValueError(f"unsupported representation {rep!r} (supported: {', '.join(REPRESENTATIONS)})")
    pts = data["points"]
    if not pts or any(p["y"] is None for p in pts):
        raise ValueError("no plottable numeric values (check the x/y columns)")
    series = sorted({p["series"] for p in pts}, key=lambda s: [p["series"] for p in pts].index(s))
    if len(series) > MAX_SERIES:
        raise ValueError(f"{len(series)} series exceed the limit of {MAX_SERIES}: split the figure")
    cats = list(dict.fromkeys(p["x"] for p in pts))
    xlab = entry.get("x_labels") or {}
    slab = entry.get("series_labels") or {}
    xlabel = entry.get("value_label", entry["data"]["y"])
    units = entry.get("units", "")
    vals = [p["y"] for p in pts] + [p[k] for p in pts for k in ("err_low", "err_high") if p.get(k) is not None]
    label_w = min(220, 16 + 7 * max(len(xlab.get(c, c)) for c in cats)) if rep != "line" else 64
    plot_l, plot_r = label_w + 10, WIDTH - 24
    top = 40
    row_h = 28 if rep != "line" else 0
    n_rows = len(cats) * max(1, len(series)) if rep != "line" else 0
    plot_h = row_h * n_rows if rep != "line" else 240
    height = top + plot_h + 70 + (18 * len(series) if len(series) > 1 else 0)
    dom = entry.get("domain")           # declared natural bounds, e.g. [0, 1] for a proportion
    if rep == "bar_h":
        if min(vals) < 0:
            raise ValueError("bar_h needs non-negative values; use dot_ci for signed quantities")
        step = nice_step(max(vals))
        lo, hi = 0.0, math.ceil(max(vals) / step - 1e-9) * step          # V3: bars always start at zero
    else:
        span = max(vals) - min(vals) or abs(max(vals)) or 1.0
        step = nice_step(span * 1.2)
        lo = math.floor((min(vals) - 0.05 * span) / step) * step
        hi = math.ceil((max(vals) + 0.05 * span) / step) * step
        if entry.get("axis_from_zero"):
            lo = min(0.0, lo)
    if dom:
        if min(vals) < dom[0] or max(vals) > dom[1]:
            raise ValueError(f"values outside the declared domain {dom}")
        lo, hi = max(lo, dom[0]), min(hi, dom[1])

    def sx(v: float) -> float:
        return plot_l + (v - lo) / (hi - lo) * (plot_r - plot_l)

    title = html.escape(entry.get("title", entry["id"]))
    alt = html.escape(entry.get("alt_text", ""))
    meta = json.dumps({"visual_id": entry["id"], "representation": rep, "domain": [lo, hi],
                       "source_file": entry["data"]["file"]}, sort_keys=True)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" '
           f'font-family="Helvetica, Arial, sans-serif" font-size="{FONT}" role="img" aria-labelledby="t d" '
           f'data-visual-id="{entry["id"]}" data-representation="{rep}" data-domain-lo="{_fmt(lo)}" data-domain-hi="{_fmt(hi)}" '
           f'data-plot-left="{plot_l}" data-plot-right="{plot_r}" data-min-font="{FONT}">',
           f'<title id="t">{title}</title>', f'<desc id="d">{alt}</desc>',
           f'<metadata>{html.escape(meta)}</metadata>',
           f'<rect width="{WIDTH}" height="{height}" fill="#ffffff"/>',
           f'<text x="{plot_l}" y="22" font-size="{FONT + 1}" font-weight="bold">{title}</text>']
    axis_y = top + plot_h
    xl = html.escape(f"{xlabel} ({units})" if units else xlabel)
    if rep != "line":            # value axis is horizontal: bars and dots run along x
        for t in _ticks(lo, hi, step):
            x = sx(t)
            out.append(f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{axis_y}" stroke="#dddddd"/>')
            out.append(f'<text class="tick" data-axis="x" data-pos="{x:.2f}" x="{x:.2f}" y="{axis_y + 16}" '
                       f'text-anchor="middle">{_tick_label(t, step)}</text>')
        out.append(f'<line x1="{plot_l}" y1="{axis_y}" x2="{plot_r}" y2="{axis_y}" stroke="#333333"/>')
        out.append(f'<text x="{(plot_l + plot_r) / 2:.2f}" y="{axis_y + 36}" text-anchor="middle">{xl}</text>')

    if rep in ("bar_h", "dot_ci"):
        i = 0
        for c in cats:
            for si, s in enumerate(series):
                p = next((q for q in pts if q["x"] == c and q["series"] == s), None)
                if p is None:
                    continue
                cy = top + row_h * i + row_h / 2
                color, mk = PALETTE[si % len(PALETTE)], MARKERS[si % len(MARKERS)]
                lab = xlab.get(c, c) if si == 0 else ""
                if lab:
                    out.append(f'<text class="category" x="{label_w}" y="{cy + 4:.2f}" text-anchor="end">{html.escape(lab)}</text>')
                attrs = f'data-x="{html.escape(c)}" data-y="{_fmt(p["y"])}" data-series="{html.escape(s)}"'
                attrs += f' data-cx="{sx(p["y"]):.2f}" data-cy="{cy:.2f}"'
                if p.get("err_low") is not None and p.get("err_high") is not None:
                    attrs += f' data-err-low="{_fmt(p["err_low"])}" data-err-high="{_fmt(p["err_high"])}"'
                if rep == "bar_h":
                    x0, x1 = sx(0.0), sx(p["y"])
                    out.append(f'<g class="mark" {attrs}><rect x="{x0:.2f}" y="{cy - 9:.2f}" width="{x1 - x0:.2f}" '
                               f'height="18" fill="{color}" data-px-start="{x0:.2f}" data-px-end="{x1:.2f}"/>'
                               + (_marker(mk, x1, cy, 4, "#000000") if len(series) > 1 else "") + "</g>")
                else:
                    g = [f'<g class="mark" {attrs}>']
                    if p.get("err_low") is not None and p.get("err_high") is not None:
                        g.append(f'<line x1="{sx(p["err_low"]):.2f}" y1="{cy:.2f}" x2="{sx(p["err_high"]):.2f}" '
                                 f'y2="{cy:.2f}" stroke="{color}" stroke-width="2"/>')
                    g.append(_marker(mk, sx(p["y"]), cy, 5, color))
                    g.append(f'<text x="{min(sx(p["y"]) + 8, plot_r):.2f}" y="{cy - 7:.2f}" font-size="{MIN_FONT}">'
                             f'{value_label(p["y"])}</text></g>')
                    out.append("".join(g))
                i += 1
    else:  # line
        xs = [_num(c) for c in cats]
        if any(v is None for v in xs):
            raise ValueError("line needs a numeric, ordered x column")
        xlo, xhi = min(xs), max(xs)

        def px(v: float) -> float:
            return plot_l + (v - xlo) / ((xhi - xlo) or 1) * (plot_r - plot_l)

        def py(v: float) -> float:
            return axis_y - (v - lo) / (hi - lo) * plot_h
        # value axis is VERTICAL for a line chart (Stage 4 e2e: the value ticks and label had been drawn on the
        # horizontal axis, which encodes x; a reviewer read the figure as route@1 vs route@1)
        for t in _ticks(lo, hi, step):
            y = py(t)
            out.append(f'<line x1="{plot_l}" y1="{y:.2f}" x2="{plot_r}" y2="{y:.2f}" stroke="#dddddd"/>')
            out.append(f'<text class="tick" data-axis="y" data-pos="{y:.2f}" x="{plot_l - 6}" y="{y + 4:.2f}" '
                       f'text-anchor="end">{_tick_label(t, step)}</text>')
        out.append(f'<line x1="{plot_l}" y1="{top}" x2="{plot_l}" y2="{axis_y}" stroke="#333333"/>')
        out.append(f'<line x1="{plot_l}" y1="{axis_y}" x2="{plot_r}" y2="{axis_y}" stroke="#333333"/>')
        mid = top + plot_h / 2
        out.append(f'<text x="14" y="{mid:.2f}" text-anchor="middle" transform="rotate(-90 14 {mid:.2f})">{xl}</text>')
        xstep = nice_step(xhi - xlo) if xhi > xlo else 1.0
        for t in _ticks(math.ceil(xlo / xstep - 1e-9) * xstep, math.floor(xhi / xstep + 1e-9) * xstep, xstep):
            out.append(f'<text class="xtick" x="{px(t):.2f}" y="{axis_y + 16}" text-anchor="middle">{_tick_label(t, xstep)}</text>')
        xname = entry.get("x_label") or entry["data"]["x"].replace("_", " ")
        out.append(f'<text x="{(plot_l + plot_r) / 2:.2f}" y="{axis_y + 36}" text-anchor="middle">{html.escape(xname)}</text>')
        for si, s in enumerate(series):
            color, mk = PALETTE[si % len(PALETTE)], MARKERS[si % len(MARKERS)]
            sp = sorted((q for q in pts if q["series"] == s), key=lambda q: _num(q["x"]))
            d = " ".join(f'{"M" if k == 0 else "L"}{px(_num(q["x"])):.2f},{py(q["y"]):.2f}' for k, q in enumerate(sp))
            out.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"/>')
            for q in sp:
                out.append(f'<g class="mark" data-x="{html.escape(q["x"])}" data-y="{_fmt(q["y"])}" data-series="{html.escape(s)}" '
                           f'data-cx="{px(_num(q["x"])):.2f}" data-cy="{py(q["y"]):.2f}">'
                           + _marker(mk, px(_num(q["x"])), py(q["y"]), 4, color) + "</g>")
    if len(series) > 1:
        ly = axis_y + 52
        for si, s in enumerate(series):
            out.append(_marker(MARKERS[si % len(MARKERS)], plot_l + 6, ly - 4 + 18 * si, 5, PALETTE[si % len(PALETTE)]))
            out.append(f'<text class="legend" x="{plot_l + 16}" y="{ly + 18 * si}">{html.escape(slab.get(s, s))}</text>')
    out.append("</svg>")
    return "\n".join(out) + "\n"


# -------------------------------------------------------------------------------- registry
def load_registry(rcs: Path) -> dict:
    p = rcs / "plan" / "visual_registry.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"visuals": []}


def render_entry(entry: dict, root: Path) -> tuple[str, dict]:
    data = transform(entry["data"], root)
    return render_svg(entry, data), data


def cmd_render(rcs: Path, root: Path, only: str | None) -> int:
    reg_path = rcs / "plan" / "visual_registry.json"
    reg = load_registry(rcs)
    rc = 0
    for e in reg.get("visuals", []):
        if only and e["id"] != only:
            continue
        if e.get("status") in ("BLOCKED", "NO_VALID_VISUAL") or e.get("external_figure") or e.get("representation") == "table":
            continue
        try:
            svg, _ = render_entry(e, root)
        except Exception as exc:  # noqa: BLE001
            print(f"{e['id']}: cannot render ({exc}) -> status NO_VALID_VISUAL")
            e["status"], rc = "NO_VALID_VISUAL", 1
            continue
        out = root / e["figure_path"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        files = [e["data"]["file"]] + ([e["data"]["source_text"]] if e["data"].get("source_text") else [])
        e["source_hashes"] = {f: sha256(root / f) for f in files}
        e["render_sha256"] = sha256(out)
        e["status"] = "RENDERED"
        print(f"{e['id']}: rendered {e['figure_path']}")
    reg_path.write_text(json.dumps(reg, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return rc


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render")
    r.add_argument("rcs")
    r.add_argument("--project-root")
    r.add_argument("--only")
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    return cmd_render(rcs, Path(a.project_root) if a.project_root else rcs.resolve().parent, a.only)


if __name__ == "__main__":
    sys.exit(main())
