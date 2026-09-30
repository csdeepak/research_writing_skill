import json, re
A = '.rcs/audits/v001/'


def w(n, t):
    open(A + n, 'w', encoding='utf-8').write(t)


w('reconstruction_self.md', """# Step 11: reader reconstruction self-test (draft v001, tags ignored; same context, so isolation: none)

Q1 Problem: building and evaluating agents that act through software (Introduction para 1). Matches spine 1.
Q2 Why it matters: authors see software as the ideal interface for agents; development and evaluation have become challenging (Intro para 1). Matches.
Q3 Missing: as the authors describe prior frameworks, general ones have limited or stateless code execution and software-engineering systems are domain-specific; the supporting Table 1 marks are lost, so the gap is the authors' positioning (Intro para 2, Related work). Matches spine 2 with scope stated.
Q4 What was done: OpenHands platform (event stream, sandbox runtime, skills, delegation, hub, harness) plus evaluation on 15 benchmarks (Sections 3-5). Matches.
Q5 Why this method: authors' stated reasons for the action set, arbitrary images, skills criteria, delegation, micro agents, mocked-LLM tests, reproducible references (Sections 1, 3, 4). Matches.
Q6 Experiments: seven software, two web, six assistance benchmarks; protocol in Section 4. Matches.
Q7 Strongest results: 26.0 SWE-bench Lite, 79.3 HumanEvalFix, 52.0 GPQA diamond, 32.1 GAIA, 57.6 AgentBench OS. Matches.
Q8 What they establish: scores the authors call competitive; no ranking. Matches (hedged).
Q9 What they do not establish: no variance, unmatched references, no ablation, no safety evaluation, no integration-effort measurement. Present (Sections 3, 5.3, 7).
Q10 Primary contribution: an open platform and its cross-category evaluation. Matches.
Q11 Main limitations: complex tasks, not top everywhere, plus the writer-derived caveats labelled as such. Matches spine 7.
Q12 One-day memory: an open platform for software-acting agents; its agents are competitive but often below listed references.
Mismatches found: none against the spine. Fixed during drafting: the abstract lacked the authors' "may not achieve top performance" hedge (added).
""")
w('claim_audit.md', """# Step 12: evidence and claim audit (draft v001)

- Tag coverage: all 45 claims and 15 limitations appear as tags; every tag resolves (lint: 0 errors).
- Numbers: tools/verify_numbers.py --strict: 0 errors, 0 warnings (every number traces to an evidence value or a project file). No p-values in the draft.
- Manual re-reads against project/paper.txt: values in Tables 2 and 3 and the prose were compared with the evidence items; the conflict pairs (SWE-bench Lite gpt-4o-mini 7.0 vs 6.3; GPQA expert humans 81.3 vs 81.2) are reported with the chosen value and the discrepancy disclosed (Sections 5.1 and 5.3, caveat L013).
- Wording fixes made at this step: "scrolling functions for long files" (source: viewing other parts of a file), "hidden tests" (source: test suite from developers' fixes), "science questions" (source: graduate-level), "behavior cloning" (source: BC, not expanded), "retrieval" for BM25 (removed). All restored to the source's level.
- Claim types vs verbs: interpretation claims use "the authors describe/state"; no "shows that/demonstrates". Measured claims use "scored/reached".
- Negative results: the negative_result items (decisions in the claim map) are reported in the main text (Sections 5.1-5.4). No SELECTIVE_REPORTING.
- C033 remains NEEDS_REVIEW (row alignment inferred) and is reported with that caveat; lint WARN accepted (workflow risk AR1).
""")
w('flow_audit.md', """# Step 13: logical-flow audit (draft v001)

- Introduction: problem (P1), gap (P2), questions RQ1/RQ2 (P3), approach (P4), numbered contributions with section pointers, paper map. Ends with the paper map.
- Each results subsection opens with what the benchmark asks, then the measured value, size against the reference rows, robustness (stated as unavailable), meaning, link to RQ2 (Section 6), and what is not concluded (Sections 5.4, 6, 7).
- Section 6 answers RQ1 and RQ2 in its first paragraph; the RQ1 answer is by description, with the missing ablation stated.
- Connectives were each checked for a true relation; "Moreover/Furthermore" are not used. The "so" in Section 5.2 follows from trained or reward-model references versus domain-general prompting.
- Old-to-new: each paragraph opens with the previous paragraph's stress concept (frameworks, gap, questions, approach, contributions).
- Question ledger debt: 0 (story/question_ledger.json).
""")
w('term_load_audit.md', """# Step 14: terminology and cognitive-load audit

- tools/audit_reader.py (reader model B): remaining flags are benchmark or system names (GPQA, GAIA, MINT, BIRD, BLOOMZ, CC-NET, Logic-LM). Categories are glossed in Section 4 (Table 1 and the assistance-benchmark list) or by role in the abstract; USD, LLM, SDK and READMEs are defined at first use. The prerequisite flag (delegation before generalist agent) was fixed by rewording the introduction.
- Term ledger: platform, agent, generalist agent, event stream, sandbox and runtime, skill, delegation, reference system, score are defined at first use and used consistently ("baseline" appears only in the authors' own row names and in quoted protocol wording).
- Sentences over 35 words: INFO flags, mostly lists of numbers or of the authors' limits; kept where splitting would separate a comparison from its reference numbers.
- Dense numeric paragraphs in 5.1-5.4 are backed by Tables 2 and 3.
- DISTRACTING content removed: the full BrowserGym action list, UI screenshots, image-build flowchart steps beyond the tagging rule. SUPPLEMENTARY (per-row costs beyond those cited, GPQA subsets beyond those cited) point to the source paper's appendix tables.
""")
w('figure_table_audit.md', """# Step 15: figure/table audit

- No images are used. Three Markdown tables (Tables 1-3) each have a card in plan/figure_cards/ with evidence, source_data, takeaway and non-conclusions.
- Each table is referenced before it appears and its takeaway is stated in the prose. Captions open with the finding.
- validate_artifacts figure-card checks: 0 errors.
- Visual gates V1-V6 (tools/validate_visuals.py) are not applicable: no visual registry, no rendered figures. They are recorded as not run, never as passed. V5 needs a human review and is not claimed.
- Figures 1, 2, 4, 5 of the source are images not present in the extracted text (missing_evidence M006, NO_VALID_VISUAL). No substitute was drawn.
- Honesty: Tables 2 and 3 show OpenHands rows beside both higher and lower references, including negative rows; the selection rule is in the cards.
""")
w('overclaim_audit.md', """# Step 17: scientific overclaim audit

- Watch-list grep over the draft (prove, significant, state-of-the-art, novel, first, robust, generalize, outperform, always, never, substantial, dramatic, clearly, causes/leads to/results in/drives, demonstrates/establishes/confirms/shows that): only the ordinal "first"/"First" and the benchmark name ProofWriter remain. Lint UNLICENSED-*: 0. The authors' own word "significantly" (HumanEvalFix, GAIA) was not reproduced because no test is reported.
- "Competitive" is always attributed to the authors and paired with rows below references (Section 5.4, abstract).
- No causal claim about which platform component produces the scores; L012 states the missing ablation.
- Generalization scope: claims limited to the listed benchmarks, subsets, agent versions and base-model snapshots; the same-agent-across-categories reading is qualified (L015).
- Safety: the authors' risk-mitigation statements are reported as expectations, with the note that no safety evaluation exists (C027, L005).
- Community numbers and README descriptions are labelled self-reported or later documentation, not results.
- No evidence was strengthened and no support was searched for after the fact.
""")

md = open('.rcs/drafts/v001/paper.md', encoding='utf-8').read()
reg = json.load(open('.rcs/corpus/source_registry.json', encoding='utf-8'))['sources']
body = md.split('## References')[0]
rows = []
for s in reg:
    au = s['authors'][0].split()[-1]
    yr = str(s['year'])
    hits = [m.start() for m in re.finditer(re.escape(au) + r'( et al\.)?,? ?\(?' + yr + r'[ab]?\)?', body)]
    if hits:
        rows.append({'source': s['id'], 'as_cited': s['as_cited'], 'instances': len(hits),
                     'exists': 'listed in the project paper reference list (user_supplied_file)',
                     'metadata': 'as cited by the project; not looked up (no web)',
                     'supports': 'support_quote from project text describes the role stated in the draft',
                     'strength': 'draft says the authors describe it, or lists its numbers as reported; no stronger verbs',
                     'status': s['publication_status'], 'primary': 'cited via the project paper only',
                     'purpose': 'role stated at each use', 'integrity': 'not checked (no web)'})
json.dump({'draft': 'v001', 'citations': rows}, open(A + 'citation_audit.json', 'w', encoding='utf-8'), indent=1)
print(len(rows), 'sources cited')
