# Research Communication Skill vNext
## Evidence-locked writing, truthful visualization, and measurable reader comprehension

**Status:** Implementation brief for Claude; proposed additions, not validated capabilities.  
**Purpose:** Extend the existing research-writing skill without weakening its current evidence and audit machinery.

## 1. Executive objective
Build a repository-aware research communication skill that produces accurate, readable, venue-appropriate papers and reproducible visuals. Optimize for readers accurately understanding the research quickly, not merely for reviewer impressions or decorative attractiveness. Treat repository material and approved literature as evidence; treat all generated prose and figures as claims that require validation.

**Non-negotiable rule:** Never invent a fact, measurement, reference, model component, experiment, image, result, explanation of causality, or implication. If evidence is absent or ambiguous, stop and ask or mark the point as unresolved; do not silently make the prose sound complete.

## 2. Current baseline: preserve, do not assume more
The existing documented workflow has 21 steps in five phases: evidence planning, context planning, drafting, revision, and editing. Its artifacts include the E### evidence map, C### typed claim-evidence graph, literature-to-gap chain, story spine, skeleton, paper.md, seven audits, disclosure.md, and five gates G1-G5.

Reported live checks: OpenHands v0.1.0 traced 51/51 distinct draft numbers to evidence and caught a conflicting table value; BEIR v0.2.0 caught an 18-vs-17 dataset inconsistency; MLPerf Tiny v0.2.0 caught dropped citations, an omitted evidenced claim, and an unjustified reference-title correction. G1-G3 ran in six reported subagent runs with zero validator errors; separate unit suites passed 21/21 and 44/44 tests. These are session-reported observations, not independent verification.

**Open limitations:** Real CORPUS/ AUTHOR/ REVIEW agent isolation was not exercised; human ASK/STOP checkpoints were automatically resolved in unattended runs; images were disabled; G4/G5 and steps 18-21 were outside the cited comparison. v0.1.0 did not demonstrate a reader-reconstruction improvement over a plain agent; v0.2.0 results were pending when reported. Never describe untested parts as working.

## 3. System design principles
1. Evidence before language. Repository files and supplied materials are inputs, not automatic truth: check provenance, version, run identity, and contradictions.
2. A plausible sentence is not necessarily a supported sentence. Check implications, adjectives, comparisons, causal verbs, novelty claims, and universal quantifiers.
3. Visuals are evidence-bearing communication artifacts, not decoration. Prefer the least complex representation that answers a reader question.
4. Keep source data, derived calculations, generated explanatory schematics, and illustrative mockups explicitly separate.
5. Audience and venue change explanation and presentation, never the underlying factual content.
6. Preserve the existing G1-G5 gates and add visual checks; do not replace executed checks with agent self-certification.

## 4. Primary guardrail: evidence-locked, non-hallucinating generation
### 4.1 Source-of-truth policy
Allowed inputs: (a) identified project files and experiment outputs with recorded paths/hashes/run IDs; (b) user-confirmed factual statements; (c) externally verified, accurately cited literature when literature use is authorized; (d) explicitly labeled hypotheses, proposals, or schematic explanations. Outside knowledge can suggest what to investigate, but cannot silently fill project-specific facts. A README and a results CSV may conflict: log and resolve using the checkable primary record, or mark unresolved.

Every substantive sentence must be assigned one of: `OBSERVED`, `DERIVED`, `LITERATURE`, `METHOD_FROM_CODE`, `USER_CONFIRMED`, `HYPOTHESIS`, `PROPOSED`, or `UNRESOLVED`. `HYPOTHESIS` and `PROPOSED` must be linguistically marked and cannot appear as observed findings. `UNRESOLVED` cannot enter a submission-ready manuscript as a factual claim.

### 4.2 Banned unsupported language patterns
Flag and demand evidence for: "significantly improves" (statistical test needed), "state of the art" (defined benchmark and current comparison needed), "robust" (appropriate stress testing needed), "real-time" (measured latency and target hardware needed), "clinically validated" (appropriate study needed), "generalizes" (out-of-distribution evaluation needed), "first/novel" (bounded literature review needed), "proves" (usually replace with bounded evidence language), "causes" (causal design needed), "outperforms" (matched evaluation needed), "all/always/never" (scope and evidence needed). This is an evidence requirement, not a simplistic word blacklist: permitted only when the stated standard is met.

### 4.3 Fail-closed handling
If missing: create `missing_evidence.md` with claim, needed artifact, owner/question, and effect on paper; ask the human at an actual checkpoint in interactive mode. In unattended mode, omit the unsupported claim or retain a visibly labeled unresolved placeholder outside the final manuscript; log an accepted risk only for non-factual workflow decisions, never to license invented facts. Contradictions remain blocked until reconciled with a documented reason. Never silently correct a citation title, number, or garbled text from model memory.

### 4.4 Numerical and citation integrity
Extract every number and unit from draft, tables, captions, axes, and supplementary material. Resolve each to an E### source span or a reproducible calculation with code, input hash, and output. Verify denominators, aggregation method, split identity, units, rounding, uncertainty, and comparison baseline. References must match an accessible source record; no fabricated authors, titles, DOIs, years, or quotation text. Check every in-text citation against the registry and every bibliography entry against an actual consulted source.

### 4.5 Visual non-fabrication
A generated chart must be derived from real recorded project data; an annotated result image must use an authentic permitted sample and genuine model output; a conceptual architecture diagram must be checked against actual code/docs and labeled schematic. Never generate photorealistic patient images, simulated model predictions, fake heatmaps, fabricated learning curves, or representative examples and present them as research evidence. Synthetic demonstration visuals, if useful, require prominent `ILLUSTRATIVE - NOT EXPERIMENTAL EVIDENCE` labeling and venue permission.

### 4.6 Proposed traceability record
```yaml
claim_id: C018
statement: "..."
type: OBSERVED
source_ids: [E034, E035]
source_locations: ["results/run_07/metrics.csv:row=macro_f1"]
source_hashes: ["sha256:..."]
experiment_id: run_07
transformation: "macro mean; see scripts/compute_metrics.py"
confidence_basis: "verified from primary experiment output"
limitations: ["single test split"]
status: VERIFIED  # VERIFIED | NEEDS_REVIEW | BLOCKED
```
A confidence score never substitutes for source evidence. Record actual evidence quality and unresolved conflicts separately.

## 5. Fifteen prioritized development modules
**M01 - Repository ingestion and provenance.** Inventory docs, code, data, logs, notebooks, screenshots, model outputs, existing figures, licenses and version history. Produce an artifact manifest with hash, source type, experimental run, and privacy/license restrictions.

**M02 - Reader knowledge model.** Extend audience A-E with prerequisite concepts, terminology familiarity, likely misconceptions, reader questions, and venue-specific expectations. Do not assume every expert knows adjacent-domain jargon.

**M03 - Claim/story/attention graph.** Connect problem -> gap -> question -> method -> evaluation -> result -> bounded contribution. For each section, specify first takeaway, required evidence, reader question, and intended next inference.

**M04 - Visual opportunity planner.** For each claim and difficult concept, identify whether a visual would improve comprehension. Distinguish explanatory, analytical, comparative, qualitative, structural, contextual, and purely decorative visuals; reject decoration without information value.

**M05 - Visual evidence registry.** Map every candidate V### to C### and E###, source files, proposed placement, reader question, transformations, caption obligations, restrictions, and verification state.

**M06 - Table-versus-figure decision engine.** Use tables for exact lookup and many precise values; charts for trend, distribution, spatial pattern and quick comparison; diagrams for processes and structure. Avoid duplicating a table as a chart without distinct reader value.

**M07 - Code-driven visualization generation.** Generate maintainable Matplotlib/Seaborn/Plotly, Graphviz, SVG, or other venue-compatible scripts using real repository inputs, pinned dependencies, deterministic seeds where relevant, and export to vector plus accessible raster formats. Prefer editable source and reproducible commands.

**M08 - Qualitative sample selection.** For image-based work, select authentic representative successes, failures, edge cases, and uncertainty cases using declared criteria. Preserve sample IDs, permissions, privacy checks, actual predictions, ground truth, and any explanation-map generation method. Do not cherry-pick without disclosure.

**M09 - Visual hierarchy and caption contracts.** Every visual has a single primary reader question, restrained emphasis, accurate units/legend, and a self-contained caption explaining dataset, protocol, result and limits without implying unsupported causality.

**M10 - Progressive disclosure and figure selection.** Choose a compact main-paper set using claim importance, evidence strength, comprehension value, redundancy and page budget. Put useful exhaustive breakdowns in appendix/supplementary material; never hide material adverse findings.

**M11 - Information-density and terminology auditor.** Flag overloaded paragraphs, unexplained abbreviations, inconsistent synonyms, excessive precision, and concept ordering errors. Preserve meaning when simplifying; no claim-strengthening during editing.

**M12 - Claim compression and skimming layer.** Produce evidence-locked one-sentence findings, descriptive headings, abstract takeaways and a 30-second paper outline. Verify that compression preserves conditions, denominators and uncertainty.

**M13 - Visual-only and multimodal reconstruction tests.** Give a blinded reviewer headings, figures and captions without prose; separately give the full paper. Ask what was done, on what data, what was found, what remains uncertain, and what the limits are. Score against a predeclared answer key, not aesthetic impressions.

**M14 - Automated truthfulness and accessibility audits.** Execute number/citation/figure consistency checks, axis integrity, color-independent encodings, legible typography, alt text, grayscale and small-format readability, and regeneration checks. Record machine results and human review separately.

**M15 - Real role separation and human checkpoints.** Run CORPUS, AUTHOR, and REVIEW roles with separate context and artifact permissions where feasible. Reviewer must inspect evidence independently and challenge unsupported claims and visuals. Implement real interactive ASK/STOP for consequential gaps; unattended runs must omit or block, not invent.

## 6. Visual decision and production contract
For each proposed V###: identify reader question -> supported claim -> available data -> candidate representation -> misleading-encoding risks -> chosen format -> generated code -> render -> source/semantic audit -> caption -> paper placement -> reviewer comprehension check. An empty or weak evidence source should produce `NO_VALID_VISUAL`, not a fabricated substitute.

```yaml
visual_id: V007
reader_question: "How does per-class F1 differ across evaluated models?"
claim_ids: [C018]
evidence_ids: [E034, E035]
source_files: ["results/run_07/per_class_metrics.csv"]
source_hashes: ["sha256:..."]
kind: COMPARATIVE
representation: grouped_horizontal_bar
transform_script: "visuals/generators/per_class_f1.py"
figure_path: "visuals/rendered/V007.svg"
placement: "Results / per-class analysis"
caption_requirements: ["split", "metric definition", "models", "uncertainty if available"]
forbidden_implications: ["statistical significance without test"]
checks: ["numeric_match", "labels", "scale", "grayscale", "regeneration"]
status: PROPOSED
```

## 7. Executable gates: preserve G1-G5, extend with V-gates
- **G1 existing:** Every factual claim evidenced or explicitly typed; block unresolved factual assertions.
- **G2 existing:** Independent reconstruction answers the existing 12 comprehension questions.
- **G3 existing:** `lint_draft.py` passes with actual execution logs.
- **G4 existing:** External blind review completed and findings addressed; not just an agent declaring success.
- **G5 existing:** Final lint clean; re-extracted claim set unchanged after line edit.
- **V1 provenance:** Every visual element traces to project data or an accurately labeled conceptual derivation.
- **V2 numerical fidelity:** Plot/table/caption values match evidence and declared transformations.
- **V3 semantic integrity:** No misleading axes, aggregation, cherry-picking, unexplained exclusions or causal insinuation.
- **V4 text alignment:** Every visual supports its attached claim; prose and captions do not overstate it.
- **V5 usability:** One-second topic recognition, ten-second takeaway, one-minute detail comprehension, accessibility checks.
- **V6 regeneration:** Clean-environment script reproduces figure from versioned permitted inputs; report meaningful render differences.

Submission is blocked by any unresolved material G1, V1-V4, or citation-integrity failure. V5 should trigger revision and documented review, not fake a pass by subjective self-certification. Retain full check logs and before/after diffs.

## 8. Proposed repository deliverables
```text
.rcs/
  artifact_manifest.yaml
  evidence_map.yaml
  claim_graph.yaml
  missing_evidence.md
  literature_registry.yaml
  reader_model.yaml
  story_attention_graph.yaml
  visual_opportunities.yaml
  visual_registry.yaml
  figure_text_contracts.yaml
  visual_audit.json
  comprehension_answer_key.yaml
  comprehension_runs/
  gate_reports/
visuals/
  generators/
  validators/
  rendered/
  source_data_manifest.yaml
scripts/
  scan_repository.py
  extract_claims.py
  verify_numbers.py
  validate_visuals.py
  regenerate_visuals.py
  check_citations.py
paper.md
supplementary.md
disclosure.md
```
These are suggested interfaces; reuse existing equivalents rather than duplicating files or breaking v0.2.0 compatibility. Keep derived files outside raw experiment output folders.

## 9. Claude execution protocol for an unfamiliar project
1. Read the existing skill documents, workflow and actual validator code; identify implemented vs documented-only behavior.
2. Inventory project inputs read-only. Hash and label primary experiment evidence, secondary narrative docs, literature, generated assets and untrusted files. Do not execute unknown repository code without reviewing it.
3. Build a conflict report and ask only consequential factual questions. In unattended runs, explicitly omit/block unresolved content.
4. Produce E###, C###, reader model, story graph, and V### opportunities before drafting.
5. Present a figure plan with source and placement for approval when interactive; generate only figures supported by real inputs.
6. Draft with internal claim tags; keep uncertainty and negative findings visible.
7. Run real G1-G3 and V1-V4 scripts; have an independent reviewer attempt to falsify key claims and captions.
8. Run comprehension tests and iterative revisions. Do not claim G4/G5 unless executed.
9. Freeze verified claims; line edit; re-extract and diff claims, tables, captions and visuals.
10. Deliver paper, visuals, source scripts, manifests, unresolved-issue log, gate reports, and disclosure statements.

## 10. Adversarial tests the guardrail must pass
- README says 18 datasets; verifiable experiment manifest says 17 -> flag conflict and document resolution; never silently select.
- Table A says 0.91; Table B says 0.93 for the same run/metric -> block pending reconciliation.
- Missing significance test -> replace unsupported "significant" claim or request a valid test; do not infer a p-value.
- No saved training logs -> refuse to generate an empirical learning curve.
- Source reference title is corrupted -> mark unverifiable; do not repair from model memory.
- A generated architecture diagram includes an imagined attention block -> detect code/docs mismatch and remove or mark proposed.
- Real image lacks usage permission or contains identifying data -> block publication until permissions/privacy are resolved.
- Requested attractive results figure has no underlying data -> produce a missing-evidence ticket, not invented bars.
- A line edit changes "on one split" to "across datasets" -> claim-invariance diff fails.
- An agent self-reports "passed" without validator output -> gate remains NOT_RUN.

## 11. Evaluation: prove comprehension, not just perceived polish
Compare matched projects and fixed evidence bundles across: A plain agent; B existing skill; C skill plus visual intelligence; D skill plus visual intelligence and reader simulation. Randomize/blind evaluation where feasible. Keep prompts, model/version, tool access, time budget, evidence, venue and audience controlled. Pre-register primary outcome as reader reconstruction accuracy on a held-out answer key, with time-to-correct-understanding as a secondary measure. Separately track unsupported factual claims, numeric errors, citation errors, visual data errors, missing adverse results, reviewer-rated clarity, accessibility and generation cost. Use multiple projects and readers; report confidence intervals and failures. Avoid treating aesthetic preference or self-grading as proof of comprehension gains.

## 12. Implementation roadmap and acceptance criteria
**Stage 0 - Baseline freeze:** Snapshot v0.2.0 and reproduce its actual tests; record current missing capabilities and open reader-reconstruction result.

**Stage 1 - Truth guardrail:** Implement provenance schema, forbidden-implication checks, source conflicts, numeric/citation audits and fail-closed ASK/STOP. Acceptance: all ten adversarial cases behave as specified, with machine logs and no invented evidence.

**Stage 2 - Visual intelligence:** Implement M04-M10 and V1-V4. Acceptance: on at least two real projects, every published figure has reproducible source, evidence IDs, an accurate caption, and no unresolved material integrity failure.

**Stage 3 - Reader comprehension:** Implement M02, M11-M13, V5, and independent review. Acceptance: collect blinded human reconstruction results and report outcomes even if there is no improvement.

**Stage 4 - Full workflow:** Exercise real agent separation, real human checkpoints, G4/G5 and final edit invariance. Acceptance: end-to-end artifacts, executed gate logs, versioned scripts and an honest limitation report.

**Definition of done:** No unsupported material factual claims; no invented visual evidence; every published quantitative visual regenerates from permitted inputs; all required gates have executable records; unresolved issues are surfaced, not buried; comprehension improvements are claimed only when independently measured.

## 13. Claude handoff instruction
Continue optimizing the existing skill in the repository. Do not rewrite it from scratch or claim that documented-only features work. First inspect and map existing files to this specification. Implement Stage 1 before expanding visualization. Use real project artifacts for every empirical assertion and every empirical visual; generate visualization code rather than fictional results. Maintain backward compatibility where feasible, run actual tests, record failures, and preserve unresolved evidence gaps. Treat this document as an implementation target, not as proof that its proposed features already exist.
