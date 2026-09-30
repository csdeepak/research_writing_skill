# Task: Project assessment + Gold Account draft for project {P}

You are building the **factual scoring authority** for an experiment that measures how accurately readers reconstruct research from papers written about it. Accuracy and restraint matter more than completeness or polish.

Repository root: `C:/Users/<user>/PESU/research_skill/research_writing_skill`
Frozen evidence snapshot (the ONLY basis for the Gold Account): `evaluation/external_projects/{P}/snapshot/` (`paper.txt` = official arXiv paper text extracted by pdftotext; `README__*.md` = official repo README(s) at pinned commits). Pins/URLs: `evaluation/manifests/source_snapshots.json`.

Do NOT read anything under `skill/`, `docs/`, or other projects' folders. You don't need them.

## Output 1 — `evaluation/external_projects/{P}/PROJECT_ASSESSMENT.md`
Sections: project description · official repository (URL, pinned commit) · paper/report (arXiv id+version, venue/peer-review status — you MAY use web search to confirm venue/peer review and dataset availability; cite URLs) · datasets · benchmark/evaluation material · available experimental evidence · available result evidence · source quality (authoritative vs secondary) · reproducibility/accessibility · suitability for this evaluation (can methodology be reconstructed? are experiments & results identifiable? can a factual Gold Account be written without guessing?) · risks (e.g. repo diverged from paper, results later superseded, pdftotext extraction damage to tables) · **recommendation: ACCEPT / ACCEPT WITH CAVEATS / REJECT** with reasons. If REJECT, propose one replacement project of equivalent evaluation value with justification (do not build it).

## Output 2 — `evaluation/ground_truth/{P}/GOLD_ACCOUNT_DRAFT.md` (snapshot-only)
Not a paper — a factual ledger. Sections 1–18:
1 Problem · 2 Motivation · 3 Research gap · 4 Research question/objective · 5 System/method · 6 Architecture · 7 Dataset/data · 8 Experimental setup · 9 Metrics · 10 Results (exact numbers, with table/section) · 11 Supported claims (directly measured/observed) · 12 Derived claims (computed/comparative) · 13 Interpretations (authors' explanations — label as interpretation) · 14 Hypotheses/speculation · 15 Limitations (only those stated by the authors, or strict scope boundaries that follow from explicitly stated conditions — label the latter "scope boundary (derived from stated conditions)") · 16 Actual contribution · 17 Unsupported or weakly supported claims (claims in the snapshot whose support in the snapshot is thin; say why — do not add outside criticism) · 18 Claim → evidence → source table (claim | type | evidence | snapshot location | ≤25-word quote).

Rules (critical):
- Never infer that an experiment happened because code exists. README features ≠ paper experiments; keep them separate and label README-only statements.
- Never infer or round-trip a number; copy numbers exactly with their location. If pdftotext garbled a table, say so and record only what is legible.
- Never convert an author interpretation into measured evidence. Never strengthen a claim. Never invent missing information — write "NOT IN SNAPSHOT".
- If paper and README conflict (e.g. newer results/versions in README), record the conflict explicitly and state which is authoritative for this study: **the paper is authoritative for research claims; README only for artifact facts.**

## Output 3 — `evaluation/ground_truth/{P}/gold_story.json`
Scoring nuggets for 12 reconstruction questions, valid against `skill/schemas/gold_story.schema.json` (you may read that one schema file). Format:
```json
{"project": "{P}", "approved_by_researcher": false, "approval_date": null,
 "questions": {"Q1": [{"id": "Q1a", "text": "...", "strength": "context", "evidence_ids": ["paper §1 ¶2"]}], ... "Q12": [...]}}
```
Questions: Q1 problem · Q2 why it matters · Q3 what is missing in existing approaches · Q4 what exactly was done · Q5 why this method/design · Q6 which experiments · Q7 strongest results · Q8 what the results establish · Q9 what they do NOT establish · Q10 primary contribution · Q11 main limitations · Q12 what a reader should remember a day later.
Nugget rules: 1–4 nuggets per question, 25–40 total; each atomic (one fact), phrased neutrally, at the authors' own strength or weaker; `strength` ∈ measured|observed|derived|literature|interpretation|hypothesis|speculation|future|context; numbers exact; include the most important numbers in Q7. Q9/Q11 nuggets must come from the snapshot (stated limitations or explicit scope conditions), never from your own critique. Every nugget's `evidence_ids` gives a snapshot location.

Finish by printing a 5-line summary: recommendation, #nuggets, #conflicts found, biggest uncertainty, any extraction problems.
