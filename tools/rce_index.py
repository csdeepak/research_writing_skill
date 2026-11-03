"""Literature index clients for lit_search.py and verify_citations.py (stdlib only).

Talks to the DOI resolver, Crossref, OpenAlex, Semantic Scholar and arXiv. Every answer is reduced to one of three
outcomes, so a failed lookup can never read as a negative result (skill/literature.md section 1):

  found       the index returned at least one record
  not_found   the index answered, and has no such record
  skipped     no answer: offline with nothing cached, refused by data policy, rate-limited, 5xx, network error

Only the DOI resolver and arXiv can prove that an identifier does not exist. A miss in Crossref, OpenAlex or Semantic
Scholar is a coverage gap: Crossref holds Crossref DOIs only, and all three miss real works.

Network is opt-in: without online=True the client answers only from .rcs/cache/. Online, each host must be listed in
data_policy.allowed_hosts (.rcs/models.json). Secrets come from the environment and go only into request headers: never
into a URL, the cache, the query log or a command line.
  RCE_CONTACT_EMAIL          polite-pool contact, sent in the User-Agent header
  SEMANTIC_SCHOLAR_API_KEY   optional
  OPENALEX_API_KEY           optional; without one, OpenAlex shares a small daily budget per IP address
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, NamedTuple

HOSTS = {"doi": "doi.org", "crossref": "api.crossref.org", "openalex": "api.openalex.org",
         "semantic_scholar": "api.semanticscholar.org", "arxiv": "export.arxiv.org"}
SEARCH_INDEXES = ("openalex", "crossref", "semantic_scholar", "arxiv")
MIN_INTERVAL = {"export.arxiv.org": 3.0, "api.semanticscholar.org": 1.1}    # seconds between calls to a host
MAX_ATTEMPTS = 3
MAX_RETRY_WAIT = 30.0
TIMEOUT = 30
TITLE_THRESHOLD = 0.70
CACHE_DAYS = 30
ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"
ARXIV_NEW_RE = re.compile(r"\b(\d{4}\.\d{4,5})(?:v\d+)?\b")
ARXIV_OLD_RE = re.compile(r"\b([a-z-]+(?:\.[A-Z]{2})?/\d{7})(?:v\d+)?\b")
ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+)$", re.I)
RETRACTED_PREFIX_RE = re.compile(r"^\s*(\[?\s*(retracted|retraction|withdrawn)\s*\]?\s*[:\-.]?\s*)+", re.I)
TAG_RE = re.compile(r"<[^>]+>")
PREPRINT_TYPES = {"posted-content", "preprint"}
# Semantic Scholar labels arXiv preprints "JournalArticle" (venue "arXiv.org"), so the type alone is not enough: the venue
# and the preprint servers' DOI prefixes say it too. bioRxiv shares 10.1101 with journals such as Genome Research, so only
# its own DOI forms count.
PREPRINT_VENUE_RE = re.compile(r"\b(arxiv|biorxiv|medrxiv|ssrn|research square|preprints\.org|chemrxiv|techrxiv|osf preprints)\b", re.I)
PREPRINT_DOI_RE = re.compile(r"^10\.(48550|2139|21203|20944|26434|36227|31219)/|^10\.1101/(\d{4}\.\d{2}\.\d{2}\.|\d{6}$)", re.I)
PEER_TYPES = {"journal-article", "proceedings-article", "article", "conference-paper", "JournalArticle", "Conference", "book-chapter"}


class Outcome(NamedTuple):
    status: str                 # found | not_found | skipped
    records: list
    reason: str = ""
    checked_at: str = ""


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ------------------------------------------------------------------------------ identifiers and titles
def normalize_doi(doi: str | None) -> str | None:
    if not doi:
        return None
    d = re.sub(r"^\s*(https?://(dx\.)?doi\.org/|doi:\s*)", "", str(doi).strip(), flags=re.I)
    return d.rstrip(" .").lower() or None


def arxiv_id_of(src: dict) -> str | None:
    """The source's arXiv identifier, from its own field, an arXiv URL, or an arXiv DataCite DOI."""
    m = ARXIV_DOI_RE.match(normalize_doi(src.get("doi")) or "")
    if m:
        return m.group(1)
    raw = str(src.get("arxiv_id") or "").replace("arXiv:", "").strip()
    url = str(src.get("url") or "")
    for text in (raw, url if "arxiv.org" in url.lower() else ""):
        for rx in (ARXIV_NEW_RE, ARXIV_OLD_RE):
            m = rx.search(text)
            if m:
                return m.group(1)
    return None


def normalize_title(title: str) -> str:
    t = unicodedata.normalize("NFKD", RETRACTED_PREFIX_RE.sub("", title or ""))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return " ".join(re.sub(r"[^\w\s]", " ", t).split())


def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def title_similarity(a: str, b: str) -> float:
    """Normalized Levenshtein on lowercased titles with punctuation stripped. A 'RETRACTED:' prefix is ignored: it is
    what the index does to a real paper, and must not read as a different paper."""
    x, y = normalize_title(a), normalize_title(b)
    if not x or not y:
        return 0.0
    return 1 - levenshtein(x, y) / max(len(x), len(y))


def surname(author: str) -> str:
    a = (author or "").strip()
    return (a.split(",")[0] if "," in a else a.split()[-1] if a.split() else a).lower()


# ------------------------------------------------------------------------------ record parsing
def _first(xs) -> str:
    return xs[0] if isinstance(xs, list) and xs else ""


def _text(s) -> str:
    return " ".join(TAG_RE.sub(" ", s or "").split())


def _date_year(d: dict | None) -> int | None:
    parts = (d or {}).get("date-parts") or [[]]
    return parts[0][0] if parts and parts[0] and isinstance(parts[0][0], int) else None


def parse_crossref(m: dict) -> dict:
    authors = [", ".join(x for x in (a.get("family"), a.get("given")) if x) or a.get("name", "") for a in m.get("author", [])]
    return {"index": "crossref", "doi": normalize_doi(m.get("DOI")), "title": _text(_first(m.get("title"))),
            "authors": [a for a in authors if a], "venue": _first(m.get("container-title")) or None,
            "year": _date_year(m.get("issued")) or _date_year(m.get("published")), "type": m.get("type"),
            "abstract": _text(m.get("abstract")), "updated_by": m.get("updated-by") or []}


def _inverted_abstract(idx: dict | None) -> str:
    if not idx:
        return ""
    pos = sorted((p, w) for w, ps in idx.items() for p in ps)
    return " ".join(w for _, w in pos)


def parse_openalex(w: dict) -> dict:
    ids = w.get("ids") or {}
    source = (w.get("primary_location") or {}).get("source") or {}
    return {"index": "openalex", "id": str(w.get("id") or "").rsplit("/", 1)[-1], "doi": normalize_doi(w.get("doi") or ids.get("doi")),
            "title": _text(w.get("display_name") or w.get("title")),
            "authors": [(a.get("author") or {}).get("display_name", "") for a in w.get("authorships", []) if (a.get("author") or {}).get("display_name")],
            "year": w.get("publication_year"), "venue": source.get("display_name"), "type": w.get("type"),
            "source_type": source.get("type"), "abstract": _inverted_abstract(w.get("abstract_inverted_index")),
            "is_retracted": w.get("is_retracted")}


def parse_s2(p: dict) -> dict:
    ext = p.get("externalIds") or {}
    return {"index": "semantic_scholar", "id": p.get("paperId"), "doi": normalize_doi(ext.get("DOI")), "arxiv_id": ext.get("ArXiv"),
            "title": _text(p.get("title")), "authors": [a.get("name", "") for a in p.get("authors") or [] if a.get("name")],
            "year": p.get("year"), "venue": p.get("venue") or None, "type": _first(p.get("publicationTypes")),
            "abstract": _text(p.get("abstract"))}


def parse_arxiv_feed(xml: str) -> list[dict]:
    out = []
    for e in ET.fromstring(xml).findall(f"{ATOM}entry"):
        ident = e.findtext(f"{ATOM}id") or ""
        title = " ".join((e.findtext(f"{ATOM}title") or "").split())
        if "/api/errors" in ident or title == "Error":     # arXiv reports a malformed id as an error entry
            continue
        m = ARXIV_NEW_RE.search(ident) or ARXIV_OLD_RE.search(ident)
        published = e.findtext(f"{ATOM}published") or ""
        out.append({"index": "arxiv", "arxiv_id": m.group(1) if m else None, "doi": normalize_doi(e.findtext(f"{ARXIV_NS}doi")),
                    "title": title, "authors": [(a.findtext(f"{ATOM}name") or "") for a in e.findall(f"{ATOM}author")],
                    "year": int(published[:4]) if published[:4].isdigit() else None, "venue": "arXiv", "type": "preprint",
                    "abstract": " ".join((e.findtext(f"{ATOM}summary") or "").split())})
    return out


def is_preprint(rec: dict) -> bool:
    return (rec.get("index") == "arxiv" or rec.get("type") in PREPRINT_TYPES or rec.get("source_type") == "repository"
            or bool(PREPRINT_VENUE_RE.search(rec.get("venue") or "")) or bool(PREPRINT_DOI_RE.match(rec.get("doi") or "")))


# ------------------------------------------------------------------------------ transport, cache, policy
def _urllib_transport(url: str, headers: dict, timeout: int) -> tuple[int, str, dict]:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", "replace"), dict(resp.headers)
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace"), dict(exc.headers or {})


def allowed_hosts(rcs: Path) -> set[str]:
    p = rcs / "models.json"
    if not p.exists():
        return set()
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return set()
    return {h.lower() for h in (cfg.get("data_policy") or {}).get("allowed_hosts", [])}


class Client:
    """One run's view of the indexes. `transport` and `sleep` exist so that tests never touch the network."""

    def __init__(self, rcs: Path, online: bool = False, refresh: bool = False, transport: Callable | None = None,
                 sleep: Callable = time.sleep) -> None:
        self.rcs, self.online, self.refresh = rcs, online, refresh
        self.transport = transport or _urllib_transport
        self.sleep = sleep
        self.hosts = allowed_hosts(rcs)
        self.calls: list[dict] = []
        self._last: dict[str, float] = {}

    def _headers(self, index: str) -> dict:
        email = os.environ.get("RCE_CONTACT_EMAIL", "").strip()
        h = {"User-Agent": "research-communication-engine" + (f" (mailto:{email})" if email else ""), "Accept": "application/json"}
        if index == "semantic_scholar" and os.environ.get("SEMANTIC_SCHOLAR_API_KEY"):
            h["x-api-key"] = os.environ["SEMANTIC_SCHOLAR_API_KEY"]
        if index == "openalex" and os.environ.get("OPENALEX_API_KEY"):
            h["Authorization"] = "Bearer " + os.environ["OPENALEX_API_KEY"]
        return h

    def _cache_path(self, index: str, url: str) -> Path:
        return self.rcs / "cache" / index / (hashlib.sha256(url.encode()).hexdigest() + ".json")

    def _cache_read(self, index: str, url: str) -> dict | None:
        p = self._cache_path(index, url)
        if not p.exists():
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def _cache_write(self, index: str, url: str, code: int, body: str, at: str) -> None:
        p = self._cache_path(index, url)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps({"url": url, "code": code, "body": body, "fetched_at": at}), encoding="utf-8")

    def _pace(self, host: str) -> None:
        gap = MIN_INTERVAL.get(host, 0.0)
        wait = self._last.get(host, -1e9) + gap - time.monotonic()
        if wait > 0:
            self.sleep(wait)
        self._last[host] = time.monotonic()

    def get(self, index: str, url: str) -> tuple[int | None, str, str, str]:
        """(http status, body, reason, checked_at). Status None means no answer, which callers report as `skipped`."""
        cached = self._cache_read(index, url)
        if cached:
            age = datetime.now(timezone.utc) - datetime.fromisoformat(cached["fetched_at"])
            if not self.online or (not self.refresh and age <= timedelta(days=CACHE_DAYS)):
                return cached["code"], cached["body"], "", cached["fetched_at"][:10]
        if not self.online:
            return None, "", "offline: no cached response", ""
        host = urllib.parse.urlparse(url).hostname or ""
        if host not in self.hosts:
            return None, "", f"policy: {host} is not in data_policy.allowed_hosts", ""
        reason = ""
        for attempt in range(MAX_ATTEMPTS):
            self._pace(host)
            try:
                code, body, headers = self.transport(url, self._headers(index), TIMEOUT)
            except (OSError, ValueError) as exc:         # URLError and timeouts are OSError
                detail = str(getattr(exc, "reason", "") or "")
                detail = "" if "://" in detail else f" ({detail[:60]})"       # never echo a URL into the log
                return None, "", f"network error: {type(exc).__name__}{detail}", ""
            if code == 429:
                reason = "rate limited (429)"
                raw = str((headers or {}).get("Retry-After", "") or "")
                wait = float(raw) if raw.replace(".", "", 1).isdigit() else 2.0 * 2 ** attempt
                if attempt + 1 < MAX_ATTEMPTS and wait <= MAX_RETRY_WAIT:
                    self.sleep(wait)
                    continue
                return None, "", reason, ""
            if code >= 500:
                return None, "", f"server error ({code})", ""
            if code in (401, 403):
                return None, "", f"refused ({code})", ""
            at = datetime.now(timezone.utc).isoformat(timespec="seconds")
            if code == 200 or code == 404:              # definitive answers only: a skip must never be replayed offline
                self._cache_write(index, url, code, body, at)
            return code, body, "", at[:10]
        return None, "", reason, ""

    def _record(self, index: str, query: str, filters: str, oc: Outcome) -> Outcome:
        self.calls.append({"date": today(), "index": index, "query": query, "filters": filters, "hits": len(oc.records),
                           "status": "ok" if oc.status != "skipped" else f"skipped: {oc.reason}"})
        return oc

    def _json(self, index: str, url: str, query: str, parse: Callable, filters: str = "") -> Outcome:
        code, body, reason, at = self.get(index, url)
        if code is None:
            return self._record(index, query, filters, Outcome("skipped", [], reason))
        if code == 404:
            return self._record(index, query, filters, Outcome("not_found", [], "", at))
        if code != 200:
            return self._record(index, query, filters, Outcome("skipped", [], f"unexpected status {code}"))
        try:
            recs = parse(json.loads(body))
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError, IndexError) as exc:
            return self._record(index, query, filters, Outcome("skipped", [], f"unreadable response: {type(exc).__name__}"))
        recs = [r for r in recs if r.get("title")]
        return self._record(index, query, filters, Outcome("found" if recs else "not_found", recs, "", at))

    # ---------------------------------------------------------------- identifier lookups
    def doi_exists(self, doi: str) -> Outcome:
        """The DOI resolver is the proof of (non-)existence. A 404 proves absence only when the handle service itself
        says so (responseCode 100): any other 404 is a proxy or an outage, which is a skip."""
        q = f"doi:{doi}"
        code, body, reason, at = self.get("doi", "https://doi.org/api/handles/" + urllib.parse.quote(doi))
        if code is None:
            return self._record("doi", q, "", Outcome("skipped", [], reason))
        try:
            rc = json.loads(body).get("responseCode")
        except (json.JSONDecodeError, AttributeError):
            rc = None
        if code == 200 and rc == 1:
            return self._record("doi", q, "", Outcome("found", [{"index": "doi", "doi": doi}], "", at))
        if code == 404 and rc == 100:
            return self._record("doi", q, "", Outcome("not_found", [], "", at))
        return self._record("doi", q, "", Outcome("skipped", [], f"unclear resolver answer ({code}, {rc})"))

    def crossref_doi(self, doi: str) -> Outcome:
        return self._json("crossref", "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""), f"doi:{doi}",
                          lambda d: [parse_crossref(d["message"])])

    def openalex_doi(self, doi: str) -> Outcome:
        return self._json("openalex", "https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/()"), f"doi:{doi}",
                          lambda d: [parse_openalex(d)])

    def s2_doi(self, doi: str) -> Outcome:
        fields = "title,year,authors,venue,externalIds,publicationTypes,abstract"
        return self._json("semantic_scholar", "https://api.semanticscholar.org/graph/v1/paper/DOI:"
                          + urllib.parse.quote(doi, safe="/()") + "?fields=" + fields, f"doi:{doi}", lambda d: [parse_s2(d)])

    def arxiv_id(self, arxiv: str) -> Outcome:
        """arXiv answers 200 with an empty feed for an id it does not have, so an empty feed is proof of absence."""
        q = f"arxiv:{arxiv}"
        code, body, reason, at = self.get("arxiv", "https://export.arxiv.org/api/query?max_results=1&id_list=" + urllib.parse.quote(arxiv))
        if code is None:
            return self._record("arxiv", q, "", Outcome("skipped", [], reason))
        if code != 200:
            return self._record("arxiv", q, "", Outcome("skipped", [], f"unexpected status {code}"))
        try:
            recs = parse_arxiv_feed(body)
        except ET.ParseError:
            return self._record("arxiv", q, "", Outcome("skipped", [], "unreadable response: ParseError"))
        return self._record("arxiv", q, "", Outcome("found" if recs else "not_found", recs, "", at))

    # ---------------------------------------------------------------- searches
    def search(self, index: str, query: str, rows: int = 10, since: int | None = None) -> Outcome:
        q = urllib.parse.quote(query)
        filters = f"from {since}" if since else ""
        if index == "crossref":
            url = f"https://api.crossref.org/works?query.bibliographic={q}&rows={rows}" + (f"&filter=from-pub-date:{since}" if since else "")
            return self._json(index, url, query, lambda d: [parse_crossref(m) for m in d["message"]["items"]], filters)
        if index == "openalex":
            url = f"https://api.openalex.org/works?search={q}&per-page={rows}" + (f"&filter=from_publication_date:{since}-01-01" if since else "")
            return self._json(index, url, query, lambda d: [parse_openalex(w) for w in d["results"]], filters)
        if index == "semantic_scholar":
            fields = "title,year,authors,venue,externalIds,publicationTypes,abstract"
            url = f"https://api.semanticscholar.org/graph/v1/paper/search?query={q}&limit={rows}&fields={fields}" + (f"&year={since}-" if since else "")
            return self._json(index, url, query, lambda d: [parse_s2(p) for p in d.get("data") or []], filters)
        if index == "arxiv":
            code, body, reason, at = self.get(index, f"https://export.arxiv.org/api/query?search_query=all:{q}&max_results={rows}")
            if code is None:
                return self._record(index, query, filters, Outcome("skipped", [], reason))
            try:
                recs = [r for r in parse_arxiv_feed(body) if not since or (r.get("year") or 0) >= since] if code == 200 else None
            except ET.ParseError:
                recs = None
            if recs is None:
                return self._record(index, query, filters, Outcome("skipped", [], f"unreadable response ({code})"))
            return self._record(index, query, filters, Outcome("found" if recs else "not_found", recs, "", at))
        raise ValueError(f"unknown index {index}")

    def snowball(self, doi: str, direction: str, rows: int = 25) -> Outcome:
        """One level of citation chasing through OpenAlex: 'backward' = what the work cites, 'forward' = what cites it."""
        base = self.openalex_doi(doi)
        if base.status != "found":
            return base
        work = base.records[0].get("id")
        relation = "cited_by" if direction == "backward" else "cites"
        url = f"https://api.openalex.org/works?filter={relation}:{work}&per-page={rows}"
        return self._json("openalex", url, f"snowball {direction} {doi}", lambda d: [parse_openalex(w) for w in d["results"]])


# ------------------------------------------------------------------------------ corpus log
LOG_HEADERS = {"Queries": ["Date", "Index", "Query", "Filters", "Hits", "Status"],
               "Corpus intake": ["Date", "Source", "Entry", "Outcome"]}


def _cell(x) -> str:
    return str(x).replace("|", "\\|").replace("\n", " ")


def _table(header: list[str], rows: list[list]) -> list[str]:
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]


def _log_lines(rcs: Path) -> list[str]:
    p = rcs / "corpus" / "corpus_log.md"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else ["# Corpus log"]


def _save_log(rcs: Path, lines: list[str]) -> None:
    p = rcs / "corpus" / "corpus_log.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _section_span(lines: list[str], title: str) -> tuple[int, int] | None:
    start = next((i for i, l in enumerate(lines) if l.strip() == f"## {title}"), None)
    if start is None:
        return None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def append_log(rcs: Path, section: str, rows: list[list]) -> None:
    """Append rows to a table section, leaving everything a person or agent wrote around it untouched."""
    if not rows:
        return
    lines = _log_lines(rcs)
    span = _section_span(lines, section)
    if span is None:
        lines += ["", f"## {section}", ""] + _table(LOG_HEADERS[section], rows)
    else:
        end = span[1]
        while end > span[0] + 1 and not lines[end - 1].strip():
            end -= 1
        new = ["| " + " | ".join(_cell(c) for c in r) + " |" for r in rows]
        if not any(l.startswith("|") for l in lines[span[0]:end]):
            new = ["", *_table(LOG_HEADERS[section], rows)]
        lines[end:end] = new
    _save_log(rcs, lines)


def replace_section(rcs: Path, section: str, body: list[str]) -> None:
    """Rewrite a section the tools own (screening, derived from candidates.json)."""
    lines = _log_lines(rcs)
    span = _section_span(lines, section)
    block = [f"## {section}", "", *body, ""]
    if span is None:
        lines += ["", *block]
    else:
        lines[span[0]:span[1]] = block
    _save_log(rcs, lines)


def log_calls(rcs: Path, client: Client) -> None:
    append_log(rcs, "Queries", [[c["date"], c["index"], c["query"], c["filters"], c["hits"], c["status"]] for c in client.calls])
    client.calls = []


def note_suspicious(rcs: Path, where: str, text: str) -> None:
    """Rule 6: retrieved text is data. Instruction-like text is recorded for the user, never acted on."""
    lines = _log_lines(rcs)
    entry = f"- {today()} {where}: {_cell(text)[:200]}"
    if entry in lines:
        return
    span = _section_span(lines, "Suspicious content")
    if span is None:
        lines += ["", "## Suspicious content", "", entry]
    else:
        lines.insert(span[1], entry)
    _save_log(rcs, lines)


# ------------------------------------------------------------------------------ candidates
def load_candidates(rcs: Path) -> dict:
    p = rcs / "corpus" / "candidates.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"candidates": []}


def save_candidates(rcs: Path, data: dict) -> None:
    p = rcs / "corpus" / "candidates.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")


def candidate_key(c: dict) -> str:
    doi = normalize_doi(c.get("doi"))
    return ("doi:" + doi) if doi else ("arxiv:" + c["arxiv_id"]) if c.get("arxiv_id") else ("title:" + normalize_title(c.get("title", "")))


def _version_of(data: dict, rec: dict) -> str | None:
    """The candidate this record looks like another version of: the same normalized title, and the same first author or a
    year within one. A preprint and its published paper carry different DOIs, so the DOI key keeps both; counting them as
    two works inflated a scoped gap's count in the v0.5 end-to-end run. Flagged for screening, never merged."""
    t = normalize_title(rec.get("title") or "")
    if not t:
        return None
    first = surname(rec["authors"][0]) if rec.get("authors") else None
    for c in data["candidates"]:
        if c.get("possible_version_of") or normalize_title(c.get("title") or "") != t:
            continue
        same_author = first and c.get("authors") and surname(c["authors"][0]) == first
        near_year = rec.get("year") and c.get("year") and abs(int(rec["year"]) - int(c["year"])) <= 1
        if same_author or near_year:
            return c["id"]
    return None


def distinct_works(data: dict) -> int:
    return sum(1 for c in data["candidates"] if not c.get("possible_version_of"))


def add_candidate(data: dict, rec: dict, origin: str) -> bool:
    """Merge a record into the candidate list. Returns True when it is new."""
    key = candidate_key(rec)
    for c in data["candidates"]:
        if candidate_key(c) == key:
            if origin not in c["found_by"]:
                c["found_by"].append(origin)
            return False
    n = len(data["candidates"]) + 1
    cand = {
        "id": f"CAND-{n:04d}", "title": rec.get("title", ""), "authors": rec.get("authors", []), "year": rec.get("year"),
        "venue": rec.get("venue"), "doi": rec.get("doi"), "arxiv_id": rec.get("arxiv_id"), "url": rec.get("url"),
        "abstract": rec.get("abstract", ""), "as_cited": rec.get("as_cited"), "found_by": [origin], "decision": "pending", "reason": None}
    version_of = _version_of(data, rec)
    if version_of:
        cand["possible_version_of"] = version_of
    data["candidates"].append(cand)
    return True
