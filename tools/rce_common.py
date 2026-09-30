"""Shared helpers for Research Communication Engine tools (stdlib only).

Provides a small JSON-Schema subset validator. If the `jsonschema` package is installed,
it is used instead for full draft 2020-12 support.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterator

_BASE = Path(__file__).resolve().parent.parent
# Repository layout: <repo>/tools + <repo>/skill. Skill-version layout: <skill>/tools beside SKILL.md.
SKILL_DIR = _BASE if (_BASE / "SKILL.md").exists() else _BASE / "skill"
SCHEMA_DIR = SKILL_DIR / "schemas"

# Inline tags in drafts: {C007} for claims, {L002} for limitation sentences, {C001, C002} for several.
CLAIM_TAG_RE = re.compile(r"\{([CL]\d{3,})(?:\s*,\s*([CL]\d{3,}))*\}")
CLAIM_ID_RE = re.compile(r"[CL]\d{3,}")
# the note after the colon is optional: a bare [CITATION NEEDED] is still an unresolved gap (it used to pass G5 unseen)
MARKER_RE = re.compile(r"\[(MISSING RESULT|MISSING|CITATION NEEDED|ASK AUTHOR)(?:\s*:[^\]]*)?\]")
ZERO_WIDTH_RE = re.compile("[​‌‍⁠﻿]")
INJECTION_RE = re.compile(
    r"(ignore (all |any )?(previous|prior|above) instructions"
    r"|disregard (the )?(previous|prior|above)"
    r"|as an ai (language model|reviewer)"
    r"|note to (the )?(ai|llm|language model|reviewer model)"
    r"|(give|assign|rate) (this|the) (paper|manuscript|submission) (a )?(high|top|maximum|perfect)"
    r"|you are (now )?an? (ai|llm) reviewer)",
    re.IGNORECASE,
)


def load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_schema(name: str) -> dict:
    return load_json(SCHEMA_DIR / name)


# ----------------------------------------------------------------------------------------
# Minimal JSON Schema validator (subset: type, enum, required, properties, items,
# additionalProperties (schema form), pattern, minLength, maxLength, minItems, minimum, maximum)
# ----------------------------------------------------------------------------------------
_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value: Any, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, _TYPES[t])


def _validate_subset(inst: Any, schema: dict, path: str) -> Iterator[str]:
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(inst, t) for t in types):
            yield f"{path}: expected type {types}, got {type(inst).__name__}"
            return
    if "enum" in schema and inst not in schema["enum"]:
        yield f"{path}: {inst!r} not in {schema['enum']}"
    if isinstance(inst, str):
        if "pattern" in schema and not re.search(schema["pattern"], inst):
            yield f"{path}: {inst!r} does not match /{schema['pattern']}/"
        if "minLength" in schema and len(inst) < schema["minLength"]:
            yield f"{path}: shorter than {schema['minLength']}"
        if "maxLength" in schema and len(inst) > schema["maxLength"]:
            yield f"{path}: longer than {schema['maxLength']}"
    if isinstance(inst, (int, float)) and not isinstance(inst, bool):
        if "minimum" in schema and inst < schema["minimum"]:
            yield f"{path}: {inst} < minimum {schema['minimum']}"
        if "maximum" in schema and inst > schema["maximum"]:
            yield f"{path}: {inst} > maximum {schema['maximum']}"
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            yield f"{path}: fewer than {schema['minItems']} items"
        if "items" in schema:
            for i, item in enumerate(inst):
                yield from _validate_subset(item, schema["items"], f"{path}[{i}]")
    if isinstance(inst, dict):
        for req in schema.get("required", []):
            if req not in inst:
                yield f"{path}: missing required '{req}'"
        props = schema.get("properties", {})
        for key, val in inst.items():
            if key in props:
                yield from _validate_subset(val, props[key], f"{path}.{key}")
            elif isinstance(schema.get("additionalProperties"), dict):
                yield from _validate_subset(val, schema["additionalProperties"], f"{path}.{key}")


def validate(instance: Any, schema: dict) -> list[str]:
    try:
        import jsonschema  # type: ignore

        validator = jsonschema.Draft202012Validator(schema)
        return [f"$.{'.'.join(map(str, e.path))}: {e.message}" for e in validator.iter_errors(instance)]
    except ImportError:
        return list(_validate_subset(instance, schema, "$"))


# ----------------------------------------------------------------------------------------
# Length (v0.2.0 length gate)
# ----------------------------------------------------------------------------------------
_NON_MAIN_HEADING_RE = re.compile(r"\b(references|bibliography|appendi(x|ces)|supplement\w*|acknowledg\w*)\b", re.I)


def length_limit(rcs: Path | None, state: dict | None = None) -> int | None:
    """Main-text word limit: state.json 'length_limit_words' wins, else .rcs/plan/venue_profile.yaml words_main."""
    if rcs is None:
        return None
    if state is None and (rcs / "state.json").exists():
        try:
            state = load_json(rcs / "state.json")
        except json.JSONDecodeError:
            state = None
    if isinstance(state, dict) and isinstance(state.get("length_limit_words"), int):
        return state["length_limit_words"]
    vp = rcs / "plan" / "venue_profile.yaml"
    if vp.exists():
        m = re.search(r"^\s*words_main:\s*(\d+)", vp.read_text(encoding="utf-8"), re.M)
        if m:
            return int(m.group(1))
    return None


TABLE_RULE_RE = re.compile(r"^\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?$")


def main_text_words(md: str, mode: str = "prose") -> int:
    """Words outside References/Appendix/Supplement/Acknowledgments (and their subsections).

    mode "prose": prose only; headings, tables, code, HTML comments and inline claim tags are not counted.
    mode "all":   prose + headings + table cell text (v0.3; what most venues and word-count tools count). The
                  tier-3 A/B found a writer at 3,751 "prose" words whose paper was 4,808 words by the task's count.
    """
    words = 0
    excluded_level: int | None = None
    in_code = False
    for line in md.splitlines():
        st = line.strip()
        if st.startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        if st.startswith("#"):
            level = len(st) - len(st.lstrip("#"))
            if excluded_level is not None and level > excluded_level:
                continue
            excluded_level = level if _NON_MAIN_HEADING_RE.search(st) else None
            if mode == "all" and excluded_level is None:
                words += len(CLAIM_TAG_RE.sub("", st.lstrip("#")).split())
            continue
        if excluded_level is not None or not st or st.startswith("<!--"):
            continue
        if st.startswith("|"):
            if mode == "all" and not TABLE_RULE_RE.match(st):
                words += len(CLAIM_TAG_RE.sub("", st.replace("|", " ")).split())
            continue
        words += len(CLAIM_TAG_RE.sub("", st).split())
    return words


def length_mode(rcs: Path | None, state: dict | None = None) -> str:
    """How the length gate counts: state.json 'length_count' ('prose' | 'all') wins; projects on the v0.3 guardrail
    default to 'all' (conservative); legacy projects keep 'prose'."""
    if rcs is None:
        return "prose"
    if state is None and (rcs / "state.json").exists():
        try:
            state = load_json(rcs / "state.json")
        except json.JSONDecodeError:
            state = None
    state = state if isinstance(state, dict) else {}
    if state.get("length_count") in ("prose", "all"):
        return state["length_count"]
    return "all" if state.get("guardrail") == "v0.3" else "prose"


# ----------------------------------------------------------------------------------------
# Markdown helpers
# ----------------------------------------------------------------------------------------
_SENT_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[\(\"'])")


def split_sentences(text: str) -> list[str]:
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    return [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]


def iter_paragraphs(md: str) -> Iterator[tuple[int, str, str]]:
    """Yield (start_line_no, current_section_heading, paragraph_text) for prose paragraphs.

    Skips headings, code fences, tables, and HTML comments.
    """
    section = ""
    buf: list[str] = []
    start = 0
    in_code = False
    for no, line in enumerate(md.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            if buf:
                yield start, section, " ".join(buf)
                buf = []
            continue
        if in_code:
            continue
        if stripped.startswith("#"):
            if buf:
                yield start, section, " ".join(buf)
                buf = []
            section = stripped.lstrip("#").strip()
            continue
        if not stripped or stripped.startswith("|") or stripped.startswith("<!--"):
            if buf:
                yield start, section, " ".join(buf)
                buf = []
            continue
        if not buf:
            start = no
        buf.append(stripped)
    if buf:
        yield start, section, " ".join(buf)
