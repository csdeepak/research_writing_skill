# Step 11 — Reader reconstruction self-test (paper.md v001, tags stripped mentally)

Answered from the draft alone, then compared with `story/spine.md` and `claims/claim_evidence_map.json`.

Q1 What problem is this paper solving? Whether current language models can resolve real, repository-scale software-engineering issues in large codebases, not just write short functions. (Intro §1, Abstract) — matches spine line 1. **Present.**
Q2 Why does this problem matter? Coding assistants are being asked to do real engineering work; prior benchmarks don't test this. (Intro ¶1) — **Present.**
Q3 What is missing from existing approaches? Function-level benchmarks don't require codebase search or real regression-test verification. (Intro ¶2, Related Work) — **Present.**
Q4 What exactly did the authors do? Built SWE-bench (2,294 instances, 12 repos, execution-verified), evaluated models under BM25/oracle retrieval. (Intro ¶4, §3-4) — **Present.**
Q5 Why did they choose this method? BM25 is the realistic automatic setting; oracle isolates generation from localization. (§4) — **Present.**
Q6 What experiments were performed? Six sub-experiments in §5 (BM25 rate, oracle rate, context-collapsed, context-length, temporal check, fine-tuning). Each stated with rationale in story_graph.json experiment_chains. — **Present.**
Q7 What are the strongest results? Claude 2: 1.96-1.97% BM25, 4.80% oracle; consistent low rates for all models (§5.1-5.2, Tables 2-3). — **Present**, matches C001/C002/C004.
Q8 What do those results actually establish? Repository-scale issue resolution is largely unsolved; localization/context length matter substantially (Discussion). — **Present**, matches C006.
Q9 What do they NOT establish? No statistical testing of differences (L001), Python-only (L002), GPT-4 on a subset only (L004), oracle setting is not realistic deployment (L003). (§7 Limitations) — **Present**, matches limitation set.
Q10 What is the primary contribution? An execution-verified, extensible benchmark showing the gap between current model capability and repository-scale issue resolution (Intro contribution paragraph, Conclusion). — **Present**, matches C011/spine line 5-6.
Q11 What are the main limitations? Single-run estimates, Python-only, GPT-4 subset, oracle unrealistic, execution-testing insufficient alone, baseline-only methods (§7). — **Present**, matches L001-L006.
Q12 What should the reader remember one day later? Current LMs resolve well under 5% of real repository issues even with perfect file localization, and most of the shortfall traces to finding/using the right code, not just generating code. — matches spine lines 5-6.

**Core RR (Q1, Q4, Q7, Q10, Q11):** all answerable and matching the spine/claim map without distortion → Core RR = 1.0 (5/5).
**Distortions found:** none. **Intrusions:** none (no private/internal references).
**Result:** no blocking defects found in this self-administered pass. Exit criteria for step 20 (Core RR ≥0.8, audits pass) are met on the self-test; full REVIEW_AGENT blind evaluation (step 18) is deferred to the external review this run hands off to (see state.json).
