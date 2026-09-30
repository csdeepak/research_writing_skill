#!/usr/bin/env python3
"""Visual-only and multimodal reconstruction tests, and the human-reader protocol (vNext Stage 3: M13, docs/04 section 10).

Measures whether readers understand the research -- not whether they like the paper. Answers are scored against a
PRE-DECLARED key built from the claim map before anyone reads.

  key      <.rcs>                         build + freeze .rcs/evaluation/comprehension_key.json (hash recorded)
  packets  <.rcs> --paper P [--root R]    blinded packets in .rcs/comprehension_runs/packets/<pkt-id>/:
                                          visual_only (title, headings, figures, captions, tables; no prose) and
                                          full (sanitized paper with figures). HTML (humans) + Markdown (LLM readers).
                                          The condition map is sealed in SEALED.json.
  form     <.rcs>                         participant instructions + answer form (HTML) and responses.csv template
  sheets   <.rcs> --responses CSV         blind grading sheet (CSV): one row per (response, nugget) + intrusions
  llm      <.rcs> --out DIR               task folders for LLM proxy readers (answers) -- clearly a proxy, not humans
  ingest   <.rcs> --answers DIR           turn LLM proxy answers into responses.csv rows
  grade-tasks <.rcs> --out DIR [--graders 2]   task folders for independent LLM proxy graders (see the reference paper)
  ingest-grades <.rcs> --answers DIR          turn LLM grader outputs into grades_llm_gr-N.csv
  score    <.rcs> --grades G1.csv [G2.csv ...]
                                          RR/DR/IR/MMF per response (tools/score_reconstruction.py), per-condition means
                                          with bootstrap CIs, Krippendorff's alpha (nominal) across graders, unsealed only
                                          at this step; report written even when there is no difference.

Questions (spec M13): what was done; on what data; what was found; what remains uncertain; what are the limits.
Grading labels: present | weakened | overstated | contradicted | absent (docs/04 section 2). An intrusion counts as an
unsupported belief only if the PAPER does not state it (evaluator v0.3; a detail the key omits is not an error).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import random
import re
import secrets
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_reconstruction  # noqa: E402
from build_review_packet import sanitize  # noqa: E402
from rce_common import CLAIM_ID_RE  # noqa: E402

QUESTIONS = [
    ("DONE", "What did the authors do? (the approach or system, in one or two sentences)"),
    ("DATA", "On what data or setting was it evaluated? (datasets, number of items, conditions)"),
    ("FOUND", "What did they find? Give the main results with their numbers."),
    ("UNCERTAIN", "What remains uncertain about these results? (intervals, variance, conflicting evidence)"),
    ("LIMITS", "What does the work NOT show, or where does it not apply?"),
]
LABELS = ["present", "weakened", "overstated", "contradicted", "absent"]
TIME_LIMIT = {"visual_only": 3, "full": 20}          # minutes, per docs/04 section 10 (first-read vs full-read)
DATA_RE = re.compile(r"\b(n\s*=\s*\d+|\d+\s+(questions|queries|items|samples|datasets|tasks|runs|seeds|participants)|"
                     r"dataset|benchmark|split|corpus|test set)\b", re.I)
UNC_RE = re.compile(r"(\bCI\b|confidence interval|±|\bstd\b|bootstrap|variance|no clear|indistinguishable|within noise)", re.I)


def load(p: Path, default=None):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def _csv(path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return [dict(r) for r in csv.DictReader(fh)]


# --------------------------------------------------------------------------------------- key
def build_key(rcs: Path) -> dict:
    ev = {e["id"]: e for e in (load(rcs / "evidence" / "research_evidence.json", {}) or {}).get("items", [])}
    cm = load(rcs / "claims" / "claim_evidence_map.json", {}) or {}
    q: dict[str, list[dict]] = {k: [] for k, _ in QUESTIONS}

    def nug(qid, text, src):
        q[qid].append({"id": f"{qid[0]}{len(q[qid]) + 1}", "text": text, "source": src})

    seen_data = set()
    for e in ev.values():
        if e.get("status") == "superseded":
            continue
        if e.get("kind") in ("method_detail", "experiment"):
            nug("DONE", e["summary"], e["id"])
        if e.get("kind") == "dataset":
            nug("DATA", e["summary"], e["id"])
        cond = e.get("conditions")
        if isinstance(cond, dict):
            setting = ", ".join(f"{k} = {v}" for k, v in sorted(cond.items())
                                if k in ("benchmark", "dataset", "split", "n", "task", "domain") and v not in (None, ""))
            if setting and setting.lower() not in seen_data:
                seen_data.add(setting.lower())
                nug("DATA", f"Evaluation setting: {setting}", e["id"])
    for c in cm.get("claims", []):
        st, ct = c.get("statement", ""), c.get("claim_type")
        if ct in ("measured", "derived", "observed") and c.get("status") != "BLOCKED":
            nug("FOUND", st, c["id"])
            if UNC_RE.search(st):
                nug("UNCERTAIN", st, c["id"])
            for m in DATA_RE.finditer(st):
                if m.group(0).lower() not in seen_data:
                    seen_data.add(m.group(0).lower())
                    nug("DATA", f"Evaluation setting includes: {m.group(0)} ({c['id']})", c["id"])
        elif ct in ("interpretation", "hypothesis", "speculation"):
            nug("UNCERTAIN", f"{st} (this is {ct}, not an established result)", c["id"])
    for lim in cm.get("limitations", []):
        nug("LIMITS", lim.get("statement", ""), lim["id"])
    for e in ev.values():
        if e.get("kind") in ("negative_result", "limitation_noted"):
            nug("LIMITS", e["summary"], e["id"])
        if e.get("status") in ("conflicting", "unverifiable", "incomplete"):
            nug("UNCERTAIN", f"{e['summary']} (evidence status: {e['status']})", e["id"])
    empty = [k for k, v in q.items() if not v]
    key = {"questions": {k: v for k, v in q.items() if v}, "questions_text": dict(QUESTIONS),
           "unscorable_questions": empty,
           "note": "Pre-declared from the claim map; do not edit after packets are sent to readers."}
    body = json.dumps(key, sort_keys=True).encode()
    key["key_sha256"] = hashlib.sha256(body).hexdigest()
    (rcs / "evaluation").mkdir(parents=True, exist_ok=True)
    (rcs / "evaluation" / "comprehension_key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False), encoding="utf-8")
    return key


def verify_key(rcs: Path) -> dict:
    key = load(rcs / "evaluation" / "comprehension_key.json")
    if not key:
        raise SystemExit("no comprehension key: run `key` first")
    body = {k: v for k, v in key.items() if k != "key_sha256"}
    if hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != key.get("key_sha256"):
        raise SystemExit("comprehension key was modified after it was frozen (hash mismatch)")
    return key


# ----------------------------------------------------------------------------------- packets
def _figures(rcs: Path, root: Path) -> list[dict]:
    reg = load(rcs / "plan" / "visual_registry.json", {"visuals": []})
    out = []
    for v in sorted(reg.get("visuals", []), key=lambda v: (v.get("representation") == "table", v.get("number", 0))):
        if v.get("status") in ("BLOCKED", "NO_VALID_VISUAL") or v.get("tier") == "supplementary":
            continue
        svg = (root / v["figure_path"]).read_text(encoding="utf-8") if v.get("figure_path") and (root / v["figure_path"]).exists() else ""
        out.append({"label": f"{'Table' if v.get('representation') == 'table' else 'Figure'} {v.get('number', '?')}",
                    "caption": v.get("caption", ""), "svg": svg, "alt": v.get("alt_text", ""), "drawn": _drawn(v, svg)})
    return out


def _drawn(v: dict, svg: str) -> str:
    """What a sighted reader sees on the figure, as text (for text-only readers): labels, values, intervals.
    Without it, an LLM proxy reader of the visual-only packet sees less than a human does."""
    from validate_visuals import parse_marks
    import visuals
    xl, sl = v.get("x_labels") or {}, v.get("series_labels") or {}
    parts = []
    for m in parse_marks(svg):
        s = f"{xl.get(m['x'], m['x'])}{' / ' + sl.get(m['series'], m['series']) if m['series'] else ''}: {visuals.value_label(m['y'])}"
        if m["err_low"] is not None:
            s += f" (interval {visuals.value_label(m['err_low'])} to {visuals.value_label(m['err_high'])})"
        parts.append(s)
    unit = f" {v['units']}" if v.get("units") else ""
    return f"[values drawn in the figure ({v.get('value_label', '')}{unit}): " + "; ".join(parts) + "]" if parts else ""


def _strip_tags(md: str) -> str:
    return sanitize(md, strip_markers=True)[0]


def _visual_only_md(paper: str, figs: list[dict]) -> str:
    lines = [ln for ln in paper.splitlines() if ln.startswith("#")]
    out = ["# " + (lines[0].lstrip("# ").strip() if lines else "Paper"), "", "Section headings:"]
    out += [f"- {ln.lstrip('#').strip()}" for ln in lines[1:]]
    for f in figs:
        out += ["", f"## {f['label']}", "", f"[figure: {f['alt']}]", f["drawn"], "", f"*{f['label']}.* {f['caption']}"]
    return "\n".join(out) + "\n"


def _html(title: str, md_body: str, figs: list[dict], full: bool) -> str:
    esc = html.escape
    parts = [f"<!doctype html><html><head><meta charset='utf-8'><title>{esc(title)}</title>"
             "<style>body{max-width:760px;margin:2em auto;font:16px/1.5 Georgia,serif;padding:0 16px}"
             "figure{margin:1.5em 0}figcaption{font-size:14px}</style></head><body>"]
    if full:
        for block in re.split(r"\n\s*\n", md_body):
            b = block.strip()
            if not b:
                continue
            m = re.match(r"^(#+)\s*(.*)", b)
            parts.append(f"<h{min(len(m.group(1)), 4)}>{esc(m.group(2))}</h{min(len(m.group(1)), 4)}>" if m else f"<p>{esc(b)}</p>")
    else:
        parts.append(f"<pre style='white-space:pre-wrap;font-family:inherit'>{esc(md_body.split('## ')[0])}</pre>")
    for f in figs:
        parts.append(f"<figure>{f['svg']}<figcaption><b>{esc(f['label'])}.</b> {esc(f['caption'])}</figcaption></figure>")
    parts.append("</body></html>")
    return "\n".join(parts)


def build_packets(rcs: Path, paper_path: Path, root: Path) -> dict:
    paper = _strip_tags(paper_path.read_text(encoding="utf-8"))
    figs = _figures(rcs, root)
    base = rcs / "comprehension_runs" / "packets"
    base.mkdir(parents=True, exist_ok=True)
    sealed = {}
    for cond in ("visual_only", "full"):
        pid = f"cpk-{secrets.token_hex(3)}"
        d = base / pid
        d.mkdir()
        if cond == "full":
            md = paper + "".join(f"\n\n**{f['label']}.** {f['caption']} [figure: {f['alt']}] {f['drawn']}" for f in figs)
        else:
            md = _visual_only_md(paper, figs)
        (d / "packet.md").write_text(md, encoding="utf-8")
        (d / "packet.html").write_text(_html(pid, paper if cond == "full" else md, figs, cond == "full"), encoding="utf-8")
        sealed[pid] = {"condition": cond, "time_limit_min": TIME_LIMIT[cond], "sha256": hashlib.sha256(md.encode()).hexdigest()}
    (rcs / "comprehension_runs" / "SEALED.json").write_text(json.dumps(sealed, indent=1), encoding="utf-8")
    return sealed


# -------------------------------------------------------------------------------------- form
def build_form(rcs: Path) -> Path:
    sealed = load(rcs / "comprehension_runs" / "SEALED.json", {})
    d = rcs / "comprehension_runs"
    qs = "".join(f"<li><p><b>{html.escape(t)}</b></p><textarea name='{k}' rows='4' cols='80'></textarea>"
                 f"<br>Confidence (1-5): <input name='{k}_conf' size='2'></li>" for k, t in QUESTIONS)
    (d / "participant_form.html").write_text(
        "<!doctype html><meta charset='utf-8'><title>Reading study</title><body style='max-width:760px;margin:2em auto;font:16px Georgia'>"
        "<h1>Reading study</h1><p><b>Consent.</b> You are asked to read a short research document and answer five questions "
        "from memory. Participation is voluntary; you may stop at any time; no personal data is recorded beyond an anonymous "
        "participant id.</p><p><b>Procedure.</b> Open the packet you were given (packet id on the envelope). Read it within the "
        "time limit printed on it, close it, then answer below without looking back. Write 'cannot tell' if the document "
        "didn't let you answer.</p><p>Participant id: <input name='participant'> Packet id: <input name='packet'> "
        f"Minutes spent: <input name='minutes' size='3'></p><ol>{qs}</ol></body>", encoding="utf-8")
    with open(d / "responses_template.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["participant", "packet", "question", "answer", "confidence", "minutes", "reader_type"])
        for pid in sealed:
            for k, _ in QUESTIONS:
                w.writerow(["P01", pid, k, "", "", "", "human"])
    return d / "participant_form.html"


# ------------------------------------------------------------------------------- LLM proxies
LLM_READER = ("You are a careful reader taking part in a reading-comprehension study. Read the document below once, then "
              "answer the five questions from what the document says. Do not use outside knowledge. If the document does "
              "not let you answer, write 'cannot tell'.\n\nReply with ONE JSON object only: "
              '{"DONE": "...", "DATA": "...", "FOUND": "...", "UNCERTAIN": "...", "LIMITS": "..."}')


def build_llm_tasks(rcs: Path, out: Path) -> list[str]:
    sealed = load(rcs / "comprehension_runs" / "SEALED.json", {})
    ids = []
    for pid in sealed:
        md = (rcs / "comprehension_runs" / "packets" / pid / "packet.md").read_text(encoding="utf-8")
        tid = f"rd-{pid}"
        d = out / tid
        d.mkdir(parents=True, exist_ok=True)
        qs = "\n".join(f"{k}: {t}" for k, t in QUESTIONS)
        (d / "prompt.md").write_text(f"{LLM_READER}\n\n# QUESTIONS\n{qs}\n\n# DOCUMENT ({pid})\n\n{md}\n\n---\nWrite your "
                                     "complete reply (only the JSON) to the file output.txt in this same folder.", encoding="utf-8")
        ids.append(tid)
    return ids


LLM_GRADER = ("You grade reading-comprehension answers against a pre-declared answer key. For each (response, nugget) pair, "
              "label how the ANSWER conveys the NUGGET: present (conveyed, same strength and scope), weakened (partly or more "
              "hedged), overstated (stronger or broader than the nugget), contradicted (incompatible), absent (not conveyed, "
              "including 'cannot tell'). Then list, per (response, question), statements in the answer that the REFERENCE "
              "PAPER does not support; a correct detail that the key merely omits is NOT an unsupported belief.\n\nReply with "
              'ONE JSON object only: {"labels": {"<response_id>|<nugget_id>": "<label>", ...}, '
              '"unsupported": {"<response_id>|<question>": ["<statement>", ...]}} covering every pair exactly once.')


def build_grade_tasks(rcs: Path, out: Path, n_graders: int, paper: Path) -> list[str]:
    rows = _csv(rcs / "comprehension_runs" / "grading_sheet.csv")
    items = [{"pair": f"{r['response_id']}|{r['nugget_id']}", "question": r["question"], "nugget": r["nugget"],
              "answer": r["answer"]} for r in rows]
    # Reference = everything any reader could see (the full packet: paper + figures + captions + drawn values).
    # Using the paper text alone repeats the D-24 defect: true, caption-sourced statements get flagged as unsupported.
    sealed = load(rcs / "comprehension_runs" / "SEALED.json", {})
    full = [k for k, v in sealed.items() if v["condition"] == "full"]
    ref = (rcs / "comprehension_runs" / "packets" / full[0] / "packet.md").read_text(encoding="utf-8") if full \
        else _strip_tags(paper.read_text(encoding="utf-8"))
    ids = []
    for g in range(1, n_graders + 1):
        tid = f"gr-{g}"
        d = out / tid
        d.mkdir(parents=True, exist_ok=True)
        shuffled = items[:]
        random.Random(g).shuffle(shuffled)
        (d / "prompt.md").write_text(f"{LLM_GRADER}\n\n# REFERENCE PAPER\n\n{ref}\n\n# PAIRS TO GRADE\n"
                                     f"{json.dumps(shuffled, indent=1, ensure_ascii=False)}\n\n---\nWrite your complete reply "
                                     "(only the JSON) to the file output.txt in this same folder.", encoding="utf-8")
        ids.append(tid)
    return ids


def ingest_grades(rcs: Path, answers: Path) -> list[Path]:
    sheet = _csv(rcs / "comprehension_runs" / "grading_sheet.csv")
    outs = []
    for d in sorted(answers.glob("gr-*")):
        txt = (d / "output.txt").read_text(encoding="utf-8") if (d / "output.txt").exists() else ""
        m = re.search(r"\{.*\}", txt, re.S)
        g = json.loads(m.group(0)) if m else {}
        labels, unsup = g.get("labels", {}), g.get("unsupported", {})
        out = rcs / "comprehension_runs" / f"grades_llm_{d.name}.csv"
        with open(out, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(list(sheet[0].keys()) if sheet else [])
            for r in sheet:
                r = dict(r)
                r["label"] = labels.get(f"{r['response_id']}|{r['nugget_id']}", "")
                r["unsupported_beliefs_in_answer"] = "; ".join(unsup.get(f"{r['response_id']}|{r['question']}", []))
                w.writerow(r.values())
        outs.append(out)
    return outs


def ingest_llm(rcs: Path, answers: Path, reader: str) -> Path:
    out = rcs / "comprehension_runs" / "responses.csv"
    new = not out.exists()
    with open(out, "a", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["participant", "packet", "question", "answer", "confidence", "minutes", "reader_type"])
        for d in sorted(answers.glob("rd-cpk-*")):
            txt = (d / "output.txt").read_text(encoding="utf-8") if (d / "output.txt").exists() else ""
            m = re.search(r"\{.*\}", txt, re.S)
            ans = json.loads(m.group(0)) if m else {}
            for k, _ in QUESTIONS:
                w.writerow([reader, d.name[3:], k, ans.get(k, "cannot tell"), "", "", "llm_proxy"])
    return out


# ------------------------------------------------------------------------------ grading sheets
def build_sheets(rcs: Path, responses: Path) -> Path:
    key = verify_key(rcs)
    rows = _csv(responses)
    random.Random(0).shuffle(rows)
    out = rcs / "comprehension_runs" / "grading_sheet.csv"
    with open(out, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["response_id", "question", "nugget_id", "nugget", "answer", "label", "unsupported_beliefs_in_answer"])
        for r in rows:
            rid = hashlib.sha256(f"{r['participant']}|{r['packet']}".encode()).hexdigest()[:8]
            for n in key["questions"].get(r["question"], []):
                w.writerow([rid, r["question"], n["id"], n["text"], r["answer"], "", ""])
    (rcs / "comprehension_runs" / "RESPONSE_IDS.json").write_text(json.dumps(
        {hashlib.sha256(f"{r['participant']}|{r['packet']}".encode()).hexdigest()[:8]: [r["participant"], r["packet"], r["reader_type"]]
         for r in rows}, indent=1), encoding="utf-8")
    return out


# ------------------------------------------------------------------------------------- scoring
def krippendorff_alpha_nominal(units: dict[str, list[str]]) -> float | None:
    """units: item -> labels from different graders (>=2 to be pairable)."""
    from collections import Counter
    pairable = {u: v for u, v in units.items() if len(v) >= 2}
    if not pairable:
        return None
    o: Counter = Counter()
    for vals in pairable.values():
        m = len(vals)
        for i, a in enumerate(vals):
            for j, b in enumerate(vals):
                if i != j:
                    o[(a, b)] += 1 / (m - 1)
    n_c: Counter = Counter()
    for (a, _), v in o.items():
        n_c[a] += v
    n = sum(n_c.values())
    d_o = sum(v for (a, b), v in o.items() if a != b) / n
    d_e = sum(n_c[a] * n_c[b] for a in n_c for b in n_c if a != b) / (n * (n - 1)) if n > 1 else 0
    return 1.0 if d_e == 0 else round(1 - d_o / d_e, 3)


def _boot_ci(xs: list[float], seed: int = 0, n: int = 5000) -> list[float] | None:
    if len(xs) < 2:
        return None
    rng = random.Random(seed)
    means = sorted(statistics.mean(rng.choice(xs) for _ in xs) for _ in range(n))
    return [round(means[int(0.025 * n)], 3), round(means[int(0.975 * n)], 3)]


def score(rcs: Path, grade_files: list[Path]) -> dict:
    ids = load(rcs / "comprehension_runs" / "RESPONSE_IDS.json", {})
    sealed = load(rcs / "comprehension_runs" / "SEALED.json", {})
    per_grader: dict[str, dict[str, dict]] = {}
    units: dict[str, list[str]] = {}
    for gf in grade_files:
        g = gf.stem
        for r in _csv(gf):
            lab = (r.get("label") or "").strip().lower()
            if lab not in LABELS:
                continue
            per_grader.setdefault(g, {}).setdefault(r["response_id"], {"questions": {}, "intrusions": []})
            per_grader[g][r["response_id"]]["questions"].setdefault(r["question"], {})[r["nugget_id"]] = lab
            units.setdefault(f"{r['response_id']}|{r['nugget_id']}", []).append(lab)
            for belief in filter(None, (r.get("unsupported_beliefs_in_answer") or "").split(";")):
                per_grader[g][r["response_id"]]["intrusions"].append({"question": r["question"], "text": belief.strip(),
                                                                      "tag": "unsupported_belief"})
    rows = []
    for g, resp in per_grader.items():
        for rid, grading in resp.items():
            # de-duplicate intrusions repeated on each nugget row of the same question
            seen, uniq = set(), []
            for i in grading["intrusions"]:
                if (i["question"], i["text"]) not in seen:
                    seen.add((i["question"], i["text"]))
                    uniq.append(i)
            grading["intrusions"] = uniq
            m = score_reconstruction.score(grading)
            part, pkt, rtype = ids.get(rid, ["?", "?", "?"])
            rows.append({"grader": g, "response": rid, "participant": part, "reader_type": rtype,
                         "condition": sealed.get(pkt, {}).get("condition", "?"), **{k: m[k] for k in ("RR", "DR", "IR", "MMF")}})
    by_cond: dict[str, dict] = {}
    for cond in sorted({r["condition"] for r in rows}):
        # Average graders within a response first: two graders of one answer are not two readers.
        per_resp: dict[str, list[dict]] = {}
        for r in rows:
            if r["condition"] == cond:
                per_resp.setdefault(r["response"], []).append(r)
        mmf = [statistics.mean(g["MMF"] for g in gs) for gs in per_resp.values()]
        rr = [statistics.mean(g["RR"] for g in gs) for gs in per_resp.values()]
        by_cond[cond] = {"n_readers": len(per_resp), "n_gradings": sum(len(g) for g in per_resp.values()),
                         "MMF_mean": round(statistics.mean(mmf), 3),
                         "MMF_ci95_over_readers": _boot_ci(mmf),   # None with < 2 readers: no interval is honest
                         "RR_mean": round(statistics.mean(rr), 3),
                         "reader_types": sorted({r["reader_type"] for rs in per_resp.values() for r in rs})}
    alpha = krippendorff_alpha_nominal(units)
    rep = {"per_grading": rows, "by_condition": by_cond, "graders": sorted(per_grader), "krippendorff_alpha_nominal": alpha,
           "alpha_interpretation": None if alpha is None else ("firm (>= 0.80)" if alpha >= 0.8 else
                                                               "tentative (>= 0.67)" if alpha >= 0.67 else "unreliable (< 0.67)"),
           "note": "Reported regardless of direction. LLM-proxy rows are not human evidence (reader_type)."}
    (rcs / "comprehension_runs" / "report.json").write_text(json.dumps(rep, indent=1), encoding="utf-8")
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["key", "packets", "form", "sheets", "llm", "ingest", "grade-tasks", "ingest-grades", "score"])
    ap.add_argument("--graders", type=int, default=2)
    ap.add_argument("rcs")
    ap.add_argument("--paper")
    ap.add_argument("--root")
    ap.add_argument("--responses")
    ap.add_argument("--out")
    ap.add_argument("--answers")
    ap.add_argument("--reader", default="llm")
    ap.add_argument("--grades", nargs="*", default=[])
    a = ap.parse_args(argv)
    rcs = Path(a.rcs)
    root = Path(a.root) if a.root else rcs.resolve().parent
    if a.cmd == "key":
        k = build_key(rcs)
        print(json.dumps({q: len(v) for q, v in k["questions"].items()}), "unscorable:", k["unscorable_questions"])
    elif a.cmd == "packets":
        verify_key(rcs)
        print(json.dumps(build_packets(rcs, Path(a.paper or root / "paper.md"), root), indent=1))
    elif a.cmd == "form":
        print(build_form(rcs))
    elif a.cmd == "sheets":
        print(build_sheets(rcs, Path(a.responses or rcs / "comprehension_runs" / "responses.csv")))
    elif a.cmd == "llm":
        print("\n".join(build_llm_tasks(rcs, Path(a.out))))
    elif a.cmd == "ingest":
        print(ingest_llm(rcs, Path(a.answers), a.reader))
    elif a.cmd == "grade-tasks":
        print("\n".join(build_grade_tasks(rcs, Path(a.out), a.graders, Path(a.paper or root / "paper.md"))))
    elif a.cmd == "ingest-grades":
        print("\n".join(str(p) for p in ingest_grades(rcs, Path(a.answers))))
    elif a.cmd == "score":
        print(json.dumps(score(rcs, [Path(g) for g in a.grades]), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
