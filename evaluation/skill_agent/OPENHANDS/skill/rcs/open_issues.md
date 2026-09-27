# Open Issues — OpenHands Manuscript

Generated after step 21 (final edit + tag strip). Issues are grouped by severity.

---

## Must resolve before submission

**OI-001: GPQA tool-use ablation missing**
The paper shows 52.0% (claude-3-5-sonnet + tools) vs 38.8% (GPT-4, no tools), but both the backbone and tool access differ. A same-backbone with/without-tools comparison on GPQA is needed to substantiate the "tool use amplifies capability" claim. Currently the paper correctly flags this limitation, but the underlying evidence gap remains. *Source: diagnostics inference_issues — causal_overreach.*

**OI-002: Variance estimates absent for all reported numbers**
All benchmark results are from single runs with no seed variance or temperature sweep reported. Differences of less than ~5 percentage points (including the 26.0% vs 26.3% SWE-Bench Lite comparison with Aider) cannot be interpreted as meaningful. Authors should add multi-run variance for at least the headline numbers (SWE-Bench Lite, WebArena, GPQA) before final submission. *Source: diagnostics — experiment score 3, limitation_not_respected.*

**OI-003: Moatless Tools (26.7%) comparison lacks citation**
Claim C003 references Moatless Tools (26.7%) as a SWE-Bench Lite comparator. This number is in the source PDF but has no citable reference in the paper's bibliography and was not included in the final manuscript. Either add the reference and Table 1 entry, or remove the comparison from claim C003. *Source: diagnostics — evidence_traceability score 2.*

---

## Should resolve before submission

**OI-004: Consolidated results table absent**
Tables 1–3 cover only selected rows; numbers for ML-Bench (64.4%), Gorilla (47.2%), BIRD (47.3%), AgentBench OS (57.6%), MINT math (77.3%), ProofWriter (78.8%), and Entity Deduction Arena (38.0%) appear only in prose. A consolidated appendix table listing every reported number with all baselines would eliminate the "selected" perception and improve reproducibility. *Source: diagnostics — figure_table score 3.*

**OI-005: Title mismatch (objective vs. draft)**
objective.md records the title as "OpenHands: An Open Platform for AI Software Developers as Generalist Agents"; the v001 draft used "An Open Platform for Building and Evaluating Generalist AI Software Agents." The final manuscript uses the objective.md title. Authors should confirm this matches the final arXiv submission. *Source: diagnostics — objective_discrepancies.*

**OI-006: Agent-runtime loop figure absent**
The paper describes the event-stream agent loop in §3.1 but has no diagram. An annotated diagram of the loop (user → event stream → agent step function → action → runtime → observation → event stream) would lower cognitive load for adjacent readers. *Source: diagnostics — method score 4.*

**OI-007: Capability matrix for related frameworks not provided**
§1 asserts "None combines safe sandboxed code execution, modular extensibility, multi-agent delegation, and systematic evaluation" but provides no comparison table. Adding a 5×4 matrix (frameworks × capabilities) would make this gap auditable. *Source: diagnostics — problem score 4.*

---

## Low priority / accepted

**OI-008: Number of runs and temperature not reported in §5**
Evaluation setup does not state sampling temperature or confirm single-run status in the method section. The limitation is disclosed in §7 Limitations; authors may wish to make it explicit in §5 as well for reproducibility. *Source: diagnostics — experiment score 3.*

**OI-009: Action-space ablation absent**
The generality thesis is attributed to code-based actions, but no ablation compares code actions vs. structured API actions on the same benchmarks. The paper correctly frames this as a hypothesis, not a tested claim. No new experiment is possible post-hoc, but the qualification is now clearly marked in the manuscript. *Source: diagnostics — unsupported_inference.*

---

*No [MISSING ...] or [CITATION NEEDED ...] markers remain in paper.md. All open issues above are either resolved by editorial fixes in this run or require new experimental data or author clarification.*
