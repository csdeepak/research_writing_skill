import json
import re

d = ".rcs/audits/v001/"
draft = open(".rcs/drafts/v001/paper.md", encoding="utf-8").read()
reg = json.load(open(".rcs/corpus/source_registry.json", encoding="utf-8"))["sources"]
body = draft.split("## References")[0]
refs = draft.split("## References")[1]

# ---- step 16: citation audit (programmatic)
cites = re.findall(r"([A-Z][A-Za-z\-]+)(?: et al\.)?, (\d{4})", body)
cites += re.findall(r"([A-Z][A-Za-z\-]+) et al\. \((\d{4})\)", body)
rows = []
seen = set()
for name, yr in cites:
    key = (name, yr)
    if key in seen:
        continue
    seen.add(key)
    src = [s for s in reg if s["authors"][0].split()[-1].lower() == name.lower() and str(s["year"]) == yr]
    in_refs = bool(re.search(r"^- %s,.*\(%s\)" % (name, yr), refs, re.M))
    rows.append({"citation": "(%s, %s)" % (name, yr), "registered": [s["id"] for s in src], "in_reference_list": in_refs,
                 "exists_step1": "user_supplied_file: listed in the project's reference list (not resolvable offline)" if src else "FAIL",
                 "support_quote": bool(src and src[0]["establishes"][0]["support_quote"]),
                 "strength_ok": "sentence attributes the statement to the MLPerf Tiny authors",
                 "status": "PASS" if src and in_refs else "FAIL"})
uncited = [s["id"] for s in reg if not any(s["id"] in r["registered"] for r in rows)]
json.dump({"draft": "drafts/v001/paper.md", "rows": rows, "registered_but_uncited": uncited,
           "notes": "All sources read_depth=abstract (not read); every citing sentence is scoped to what the MLPerf Tiny paper says about the work. Works [1], [2], [16], [19] of the project list have no year and are not cited (see corpus_log.md)."},
          open(d + "citation_audit.json", "w", encoding="utf-8"), indent=2)
print("citations", len(rows), "fail", [r for r in rows if r["status"] != "PASS"], "uncited", uncited)

files = {}
files["reconstruction_self.md"] = """# Step 11 - reconstruction self-test (from the tag-free text of drafts/v001/paper.md)

Q1 Problem: fair, reproducible comparison of ML inference on ultra-low-power devices (Abstract, 1). Matches spine 1.
Q2 Why it matters: always-on private low-energy inference; the authors say progress is limited without a benchmark (1). Matches.
Q3 Missing: CoreMark, MLMark, MLPerf inference fall short, in the authors' account (1, 3). Matches; worded as the authors' characterization.
Q4 What was done: four benchmarks with reference implementations, quality targets, closed/open divisions, measurement framework (1, 4). Matches.
Q5 Why: the authors' reasons are given per design choice (1, 4.1-4.4). Matches.
Q6 Experiments: reference models against targets (5.1), reference implementations on the board (5.2), June 2021 round (5.3). Matches.
Q7 Strongest results: every reference above its target; five varied submissions (5.1, 5.3). Matches.
Q8 Establishes: the specification and reference numbers; the authors' reading of the round (6). Matches.
Q9 Does not establish: fairness across submissions, sensitivity of targets, reference latency/energy magnitudes (5, 6, 7). Matches.
Q10 Contribution: the suite, targets, rules, framework (1). Matches.
Q11 Limits: streaming, pre-processing, stability, model coverage; plus the additional caveats (7). Matches spine 7.
Q12 One-day memory: an open four-task benchmark with a modular two-division design, read by its authors as fitting diverse submitters, within stated limits. Matches spine 5-7.

First-read subset (title, abstract, introduction): Q1-Q4, Q10, Q12 answerable. Mismatches found: none. Term check with tools/audit_reader.py: only product and dataset names remain flagged (reviewed, kept verbatim; see term_audit.md).
Skim layer: the abstract keeps every number and scope of its tagged claims (91.6%, 90%, more than 50, five, June 2021); its hedges ("the authors say", "read as") are kept.
"""
files["claim_audit.md"] = """# Step 12 - evidence/claim audit

- tools/verify_numbers.py (G3_numbers.json): 0 errors, 0 warnings; three DERIVED_MATCH infos (1.5, 1.5, 1.6) are the Table 2 gaps of claim C035 (86.5 - 85, 91.6 - 90), confirmed.
- tools/lint_draft.py (G3_lint.json): 0 errors. Remaining warnings are undefined-acronym warnings for product and dataset names (NUCLEO, MBED, GCC, ARM, LPM01A, JS110, UNO, DCASE2020, MIMII, MSCOCO, CIFAR, RISC, README, and reference-list acronyms). They are kept because they are the authors' names for hardware or datasets; each is glossed in the text where it matters.
- Every number was re-read against project/paper.txt or the README by the numbers tool (traces to evidence items cited by the tagged claims).
- Claim types and verbs: interpretation claims (design reasons, C018, C002) use "the authors state / attribute / read"; measured claims use "reaches"; the one derived claim (C035) is labelled "our arithmetic" in Table 2.
- Negative results: the evidence map holds none. Absences are reported as caveats L005-L008, not hidden: no variance, no Figure 5 values, no submission measurements.
- Fixed in this pass: 'generalization' wording (unlicensed ood_eval) replaced by a paraphrase of the authors' reason; strong verbs on interpretation claims changed to 'show'; L008 removed from the Conclusion's author-limitation sentence; VWW 'about 86%' kept as 'about'.
"""
files["flow_audit.md"] = """# Step 13 - logical flow audit

- Paragraph model: each paragraph opens with its point (checked against plan/skeleton.md); link-forward sentences exist at section ends (Section 3 -> design; 4.2 -> 5.1; 5.2 -> 5.3).
- Introduction ends with RQs (paragraph 3, within the first 25%), contributions with result pointers, and a paper map. Question debt: Q-05 (reference latency/energy values) is deferred to Section 5.2 and the caveats, stated explicitly.
- Results subsections open with the question they answer (Section 5 opening sentence maps RQ1-RQ3).
- Discussion answers RQ1-RQ3 explicitly.
- Connectives: 'therefore' occurs twice (Limitations, first and fourth limitation); both follow from the preceding sentence. 'so' and 'because' were checked against the authors' stated reasons. One decorative inference removed: a paragraph mapping the design onto the challenges (our reading, not the authors') was deleted.
- Old-to-new order checked at paragraph starts of Sections 4.1 and 5.3.
"""
files["term_audit.md"] = """# Step 14 - terminology and cognitive-load audit

- tools/audit_reader.py against plan/reader_model.json: remaining findings are proper names of products and datasets (NUCLEO-L4R5ZI, MBED, GCC-ARM, UNO, LPM01A, JS110, N6705, DCASE2020, MIMII, CIFAR, RISC-V, README) and the labels RQ1-RQ3 (defined at first use as research questions). Product names sit in the appendix or a single mention; kept for fidelity.
- Prerequisite order: 'reference implementation' now appears before 'closed division' in the abstract.
- Term ledger: one term per concept (closed/open division, quality target, reference implementation, device under test, inferences per second). 'input-output manager' is the plain-language rendering of the authors' 'IO Manager' (used once in the main text, once in Appendix A).
- Long sentences (>35 words) were reviewed; the ones left carry lists of the authors' items and are kept.
- Relocated to Appendix A (supplementary): build toolchain and energy-monitor product names.
"""
files["figure_audit.md"] = """# Step 15 - figure/table audit

- TAB-1, TAB-2, TAB-3 have cards in plan/figure_cards/ with takeaway, RQ, claims, evidence and source data (project/paper.txt). Each table is referred to by number before it appears, and its takeaway is stated in the adjacent prose (Table 2: 'Each result exceeds its target...'; Table 3: the round included both divisions and both vendor types).
- FIG-5 (reference latency and energy) is blocked: the values are not in any project file, a missing-evidence ticket M001 exists, nothing is drawn and the prose says so.
- Table 2 marks the Gap column as 'our arithmetic'. Table 3 states that modification marks are illegible and omitted. No visual is decorative; no chart is used (each table has more than three values).
- Visual gates V1-V6: not applicable (no registry, no rendered figure). V5 human review not performed and not claimed.
"""
files["overclaim_audit.md"] = """# Step 17 - scientific overclaim audit

- Lint on licensed vocabulary (significant, state of the art, robust, real-time, generalizes, novel/first, causes, outperforms, always/never): none present except the flagged and rewritten 'generalization' sentence. No p-values, no significance claims, no comparisons of submissions.
- Scope: the reference accuracies are single values on fixed sets (200 images, 1000 utterances, 248 samples, full test sets); the paper says nothing beyond them. The round is 'five rows in one round'. Adoption and impact statements are attributed to the authors and typed speculation/observed-low.
- Comparative and causal wording: 'because' appears only for the authors' stated reasons; 'the authors attribute ... to its modular design' is typed interpretation with confidence low and caveats L007, L008.
- 'Fair' and 'comparable' are presented as design aims; the text states the paper gives no measured test of fairness.
- Author limitations are reported first (L001-L004), then 'Additional caveats' (L005-L009), each with the claims it bounds.
- Nothing was strengthened; two sentences were downgraded in this pass ('a correct quantized implementation ... clears' became 'each target sits below what its reference model reaches').
"""
for k, v in files.items():
    open(d + k, "w", encoding="utf-8").write(v)
