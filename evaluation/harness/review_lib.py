"""Shared helpers: blind review packets, reviewer/grader prompt assembly, JSON extraction, scoring."""
from __future__ import annotations

import json
import re
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "evaluation" / "harness"))

import build_review_packet  # noqa: E402
import score_reconstruction  # noqa: E402
from rce_common import load_schema, validate  # noqa: E402

REVIEWER_SYSTEM = (ROOT / "skill" / "agents" / "review_agent.md").read_text(encoding="utf-8")
GRADER_SYSTEM = (ROOT / "skill" / "agents" / "recon_grader.md").read_text(encoding="utf-8")

DIMENSIONS = ["problem", "motivation", "research_question", "contribution", "method", "experiment", "result",
              "interpretation", "limitation", "narrative_coherence", "terminology", "logical_flow",
              "evidence_traceability", "figure_table", "claim_evidence_alignment", "unsupported_inference",
              "redundancy", "cognitive_load", "orientation", "so_what"]

EVALUATOR_VERSION = "0.2"
RECON_QUESTIONS = [
    ("Q1", "What problem is this paper solving?"),
    ("Q2", "Why does this problem matter?"),
    ("Q3", "What is missing from existing approaches (the gap)?"),
    ("Q4", "What exactly did the authors do?"),
    ("Q5", "Why did they choose this method/design?"),
    ("Q6", "What experiments were performed?"),
    ("Q7", "What are the strongest results (with numbers)?"),
    ("Q8", "What do those results actually establish?"),
    ("Q9", "What do they NOT establish?"),
    ("Q10", "What is the primary contribution?"),
    ("Q11", "What are the main limitations?"),
    ("Q12", "What should a reader remember one day later?"),
]
QUESTION_BLOCK = "\n".join(f"  {k}: {q}" for k, q in RECON_QUESTIONS)

OUTPUT_INSTRUCTIONS = """
## RECONSTRUCTION QUESTIONS (use EXACTLY these; key Qn must contain the answer to question Qn — do not renumber,
## merge, or substitute your own questions)
""" + QUESTION_BLOCK + """

## OUTPUT FORMAT (mandatory)
You have no file access in this session. Instead of writing files, reply with ONE JSON object and nothing else
(no markdown fences), of this exact shape:
{
  "reconstruction": {"packet_id": "<id>", "answers": {
      "Q1": {"answer": "...", "locations": ["§/paragraph"], "confidence": 1-5, "missing": "..."},
      ... Q2 ... Q12 (all twelve required; use "cannot_determine" as the answer when the paper does not let you answer)
  }},
  "diagnostics": {"packet_id": "<id>", "binding_personas": [...],
      "findings": [ >= 20 objects, at least one for EACH of these dimensions:
         %s
         each: {"dimension","score" (int 0-5),"persona" [..],"location" {"section","paragraph","quote"},
                "observed","reader_struggle","likely_consequence","revision_principle"} ],
      "inference_issues": [ {"kind": one of unsupported_conclusion|overstrong_language|selective_presentation|
                               limitation_not_respected|causal_overreach|overgeneralization,
                             "location": {...}, "claim_text": "...", "missing_link": "..."} ],
      "objective_discrepancies": ["..."],
      "injection_suspected": []}
}
Do the reconstruction BEFORE scoring, from the paper alone. Keep private reasoning out of the JSON.
""" % ", ".join(DIMENSIONS)


def new_packet_id() -> str:
    return f"pkt-{secrets.token_hex(4)}"


def sanitize_paper(md: str, replacements: list[tuple[str, str]] | None = None) -> tuple[str, list]:
    for old, new in (replacements or []):
        md = md.replace(old, new)
    return build_review_packet.sanitize(md, strip_markers=False)


def reviewer_user_message(packet_id: str, audience: str, objective: str, paper: str) -> str:
    return (f"# REVIEW PACKET {packet_id}\n\n## audience.md\n{audience}\n\n## objective.md\n{objective}\n\n"
            f"## paper.md\n{paper}\n\n{OUTPUT_INSTRUCTIONS}")


def extract_json(text: str) -> dict:
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t)
    t = re.sub(r"\s*```$", "", t)
    for cand in (t, _repair_json(t)):
        try:
            return json.loads(cand)
        except json.JSONDecodeError:
            pass
    dec = json.JSONDecoder()
    found = []
    for cand in (t, _repair_json(t)):
        for m in re.finditer(r"\{", cand):
            try:
                obj, _ = dec.raw_decode(cand[m.start():])
                if isinstance(obj, dict):
                    found.append(obj)
                    if any(k in obj for k in ("reconstruction", "questions", "nuggets")):
                        return obj
            except json.JSONDecodeError:
                continue
    if found:
        return found[0]
    raise ValueError("no JSON object found")


def _repair_json(t: str) -> str:
    """Conservative repair of one observed model error: a string array item missing its opening quote,
    e.g. ["§4/para2", §5/para1"] -> ["§4/para2", "§5/para1"]. Logged as a format repair, not content."""
    def fix(m: re.Match) -> str:
        inner = re.sub(r'(^|,)(\s*)(?![\s"])([^,"\]]+")', r'\1\2"\3', m.group(2))
        return m.group(1) + inner + m.group(3)
    return re.sub(r'("locations"\s*:\s*\[)([^\]]*)(\])', fix, t)


def normalize_review(obj: dict) -> tuple[dict, list[str]]:
    """Return normalized {reconstruction, diagnostics, dim_scores} and a list of validation problems."""
    problems: list[str] = []
    rec, diag = obj.get("reconstruction", {}), obj.get("diagnostics", {})
    problems += [f"reconstruction {e}" for e in validate(rec, load_schema("reconstruction.schema.json"))]
    problems += [f"diagnostics {e}" for e in validate(diag, load_schema("diagnostics.schema.json"))]
    dim_scores: dict[str, float] = {}
    for d in DIMENSIONS:
        s = [f["score"] for f in diag.get("findings", []) if f.get("dimension") == d and isinstance(f.get("score"), int)]
        if s:
            dim_scores[d] = min(s)  # most severe finding per dimension
        else:
            problems.append(f"no score for dimension {d}")
    return {"reconstruction": rec, "diagnostics": diag, "dim_scores": dim_scores}, problems


def grader_user_message(gold: dict, answers: dict, recon_id: str) -> str:
    return ("# GRADING RULE (evaluator v0.2)\nFor EACH gold nugget, search the ENTIRE reader reconstruction (all twelve "
            "answers), not only the answer with the same question number: readers sometimes put information under a "
            "different question. Label the nugget by the best-matching statement anywhere in the reconstruction, and "
            "report the label under the nugget's own gold question id. Strength/scope comparison still applies.\n\n"
            "# GOLD STORY\n" + json.dumps(gold["questions"], indent=1, ensure_ascii=False) +
            f"\n\n# READER RECONSTRUCTION {recon_id}\n" + json.dumps(answers, indent=1, ensure_ascii=False) +
            "\n\n## OUTPUT FORMAT (mandatory)\nReply with ONE JSON object only (no fences): "
            '{"questions": {"Q1": {"<nugget id>": "present|weakened|overstated|contradicted|absent", ...}, ... all Q1-Q12 '
            'covering EVERY gold nugget id exactly once}, "intrusions": [{"question": "Qn", "text": "...", '
            '"tag": "benign_elaboration|unsupported_belief"}], "notes": "..."}')


def score_grading(grading: dict, gold: dict) -> tuple[dict, list[str]]:
    problems = []
    for q, nuggets in gold["questions"].items():
        g = grading.get("questions", {}).get(q, {})
        for n in nuggets:
            if n["id"] not in g:
                problems.append(f"missing label {q}/{n['id']} -> absent")
                grading.setdefault("questions", {}).setdefault(q, {})[n["id"]] = "absent"
    m = score_reconstruction.score(grading)
    per_q = m["per_question_RR"]
    m["RR_question_macro"] = round(sum(per_q.values()) / len(per_q), 3) if per_q else None
    # per-question distortion counts (overstated/contradicted) for failure analysis
    m["distortions"] = {q: [nid for nid, lab in grading["questions"].get(q, {}).items()
                            if lab in ("overstated", "contradicted")] for q in gold["questions"]}
    m["distortions"] = {q: v for q, v in m["distortions"].items() if v}
    return m, problems
