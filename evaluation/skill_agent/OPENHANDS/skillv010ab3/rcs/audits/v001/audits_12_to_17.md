# Audits 12-17 (draft v001)

## Step 12: evidence / claim audit
- Numeric fidelity: 80 decimal numbers in the main text were extracted; 77 occur verbatim in project/paper.txt. The three others are: the section number "3.3" and the derived differences 29.3 (81.3 - 52.0) and 50.3 (91.1 - 40.8), both recomputed. Derived differences 0.3, 1.3, 7.0, 8.0 (SWE-Bench Lite), 0.3 (WebArena delegation), 0.8 and 10.7 (ProofWriter) were recomputed by hand from the evidence values.
- Row-to-value pairings for Table 4 (HumanEvalFix), Table 5, Table 6 and Table 7 were checked against row order in the extracted text (7 rows / 7 values; 9 rows / 9 triples for GPQA). Rows that could not be mapped (BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA numbers; Table 6 cost column) are omitted.
- Claim types vs verbs: measured claims use "scored/resolved/fixed"; the interpretation (C021) is attributed ("the authors interpret", "consistent with"); speculation (C022) marked as expectation; literature claims attributed ("as the authors describe").
- Negative results: E031 (rows below comparators) reported in main text (Section 5.5, Tables 2-3); decision reported_main. Conflicts (6.3/7.0; 81.3/81.2) reported in table notes and L006.
- Failure states: no OVERCLAIM, SELECTIVE_REPORTING (five benchmarks' numbers omitted for legibility, declared in Section 4 and open issues), or orphan claims. C012 remains author_confirmation pending (accepted risk).
- Fixed in this pass: "within 0.2 points" corrected to 0.3 (14.8 vs 14.5); conclusion count of benchmarks above/below made consistent with Section 5.5 and the abstract; falsifier criterion labelled as the article's own framing, not the authors'; note about the 53.1 value corrected.

## Step 13: logical-flow audit
- Introduction ends with RQs, contributions and paper map; question stated in paragraph 3 of 6 (within first 25% is borderline; it is foreshadowed in paragraph 1 by the listed questions).
- Each Results subsection opens with its question (5.1, 5.3, 5.4); 5.2 opens with the answer since it continues 5.1.
- Connectives audited: "however" (contrast between ideal interface and engineering burden: true), "therefore" (software as interface: authors' inference), "whereas" (three uses, each a real contrast). No decorative "moreover/furthermore".
- Discussion opens with per-RQ answers.

## Step 14: terminology / load
- Terms defined at first use: agent, sandbox, event stream, success rate, generalist agent, SWE-Bench, hint text, AgentSkills, delegation. Lint flags benchmark names and API/HTML/DOM/REST as undefined acronyms; benchmark names are proper names glossed in Table 1; REST/HTML/DOM/API are general engineering vocabulary assumed for this audience (recorded in audience profile).
- Sentences over 35 words: several in Sections 3 and 5.4; kept where they enumerate components; not split further (accepted).
- Density: pass-through of skill lists, docker tagging and the authorship process condensed or omitted as SUPPLEMENTARY/DISTRACTING.

## Step 15: figure/table audit
- Tables 1-3 each have a card with takeaway and RQ link, a takeaway-first caption, are referenced before appearing, and their takeaway appears in prose (5.1-5.5). No figures (rule: no images). Table 2 and Table 3 state that values are single reported numbers.
- Check of Table 3 caption "ahead on four comparisons and behind on three": ahead: GAIA, GPQA (vs model baselines), AgentBench OS, MINT math; behind: MINT code, ProofWriter, Entity Deduction Arena. Correct as stated at best-configuration level.

## Step 16: citation audit
- Every in-text citation resolves to source_registry.json (checked by script). All registered with verification.method = user_supplied_file, read_depth = abstract. Because the cited works were not read, each citation is used only to attribute what the OpenHands authors say about it (support quotes come from project/paper.txt with line numbers). Preprints are not described as peer reviewed.
- No citation of a claim's truth rests on a source's own content. No [CITATION NEEDED] markers required.

## Step 17: overclaim audit
- Lint: 0 errors; "significant", "novel", "first", "state-of-the-art", "prove", "outperform" absent. "substantial" appears only in a quotation of the authors' limitation.
- Generalisation scope: every performance claim carries benchmark, subset, configuration and model version. The hypothesis of competitiveness is worded as the authors' interpretation with three explicit reasons for low confidence (single values, heterogeneous agents/models, uncontrolled comparators).
- The abstract contains only claims of confidence >= moderate except C021, which is attributed ("The authors interpret") and hedged in the same paragraph.
- Adoption figures are labelled as undated statements by the authors; "accelerates research" is labelled as an untested expectation.
- Result: no blocking flags. Remaining known defects for review: abstract states the gap only implicitly; several long sentences; Table 1 needs external context to define some benchmarks.
