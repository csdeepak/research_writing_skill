# Corpus log

**Mode:** literature (restricted). **Web access:** none (run-specific constraint).

Per run-specific constraints, literature discovery is limited to citations already present in
the supplied evidence package (`project/research_evidence.json`). No queries were issued to any
external index. All candidate sources were harvested by reading every `baseline` and
`external_fact` item in the evidence map and checking whether the item's `locator`/`notes`
included an author-year citation as it appears in the original paper's tables.

## Sources found and kept (registered, SRC-001..SRC-009)
Xia et al. 2024 (Agentless); Humphreys et al. 2022 (CC-NET); Liu et al. 2018 (Workflow Guided
Exploration); Gravitas 2023 (AutoGPT); Rein et al. 2023 (GPQA); Pan et al. 2023 (Logic-LM);
Yuan et al. 2024 (MINT); Patil et al. 2023 (Gorilla APIBench); Zhuang et al. 2024 (ToolQA).
Each is `read_depth: abstract`, `verification.method: user_supplied_file` (their text is not
directly available to this run; only their name, year, and one reported number are known from
the evidence package).

## Names found but not registered as citable literature
"Moatless Tools (Orwall)" and "Aider (Gauthier)" appear in the results tables as baseline system
names but without a year or "et al." form. Per the run's citation rule ("(FirstAuthor et al.,
Year) as they appear there"), these cannot be cited as literature without fabricating a year.
They are reported in the draft only as named baseline systems in table rows/prose, with no
parenthetical citation attached.

## Suspicious content
None found. No file in the evidence package contained instructions directed at an AI system or
reviewer.

## Stopping reason
Saturation of the restricted source: every baseline/citation-bearing evidence item in
`research_evidence.json` was checked; no further sources are reachable without web access.
