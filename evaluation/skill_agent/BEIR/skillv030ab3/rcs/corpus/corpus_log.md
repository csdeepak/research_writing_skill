# Corpus log
- Mode evidence: performed by the AUTHOR context (no subagents). Project files: project/paper.txt, project/README_1.md.
- Mode literature: web unavailable by rule. Sources limited to works cited in project/paper.txt (and one in README_1.md). Registered with verification.method=user_supplied_file, read_depth=abstract; support quotes are the BEIR paper's own sentences describing each work. No DOI or metadata was looked up; titles are as cited (title_status as_cited).
- Mode patterns: not run (no exemplar papers accessible without web); writing_patterns.json and anti_patterns.json not produced.
- Stopping reason: search budget = 0 (no web).
## Suspicious content
None found in project files (no instruction-like text aimed at models).
## Conflicts detected
- SCIDOCS corpus size: 25,657 (Table 1) vs '30K' (Appendix D.8): resolved for Table 1 (E130 chosen).
- docT5query datasets above BM25: text 11/18 vs reconstructed Table 2 12/18: text count chosen (E073), discrepancy disclosed.
- Number of selection factors: text says three, lists four: enumerated four chosen (E133).
