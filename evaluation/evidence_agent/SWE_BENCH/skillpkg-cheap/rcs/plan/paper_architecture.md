# Paper Architecture: SWE-bench (working title: see skeleton)

Story pattern: method_first (new benchmark artifact → properties → evaluation → interpretation)
Audience mode: B (adjacent ML researcher) · Binding personas: A, B, E · Venue profile: plan/venue_profile.yaml (assumed rules: all; VENUE_UNKNOWN)

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Link forward |
|---|---------|---------------|---------------------------|-----------------------|--------|---------|--------|-----------|--------------|
| I.1 | Introduction | N01, N02 | What is the problem and why care? | Whether LLMs can do realistic software engineering, not just isolated coding, is untested. | — | CORE | — | task instance (foreshadow) | existing benchmarks don't test this |
| I.2 | Introduction | N03, N04 | What is missing from existing evaluation? | Prior coding benchmarks use short, self-contained problems, not real repositories with executable verification. | C001 | CORE | — | — | so we ask... |
| I.3 | Introduction | N05 | What exactly do you ask? | Can current LLMs, given a real issue and full repository, generate a patch that resolves it, and what determines success? | — | CORE | — | — | how we answer it |
| I.4 | Introduction | N06, N07 | What did you do? | We built SWE-bench from real GitHub history and evaluated several LLMs plus a fine-tuned model. | C001, C009, C012 | CORE | — | — | what we found |
| I.5 | Introduction | N19 | What did you find / contribute? | Every model resolves only a small fraction of issues, and context selection is a major, addressable bottleneck. | C002, C004 | CORE | — | — | paper map |
| I.6 | Introduction | — | Where is it in the paper? | Paper map by question. | — | CORE | — | — | Related Work |
| RW.1 | Related Work | N03, N04 | Why is this gap real? | Contrast with short, self-contained coding-benchmark practice (from the evidence package's own framing) and long-context literature (SRC-001). | C001 | CORE | — | — | Methods |
| M.1 | Methods | N23, N07 | What is a task instance and how is correctness verified? | Define task instance, gold patch, FAIL_TO_PASS/PASS_TO_PASS tests. | — | CORE | — | task instance, gold patch, F2P/P2P | how instances were selected |
| M.2 | Methods | N07 | How were instances selected? | Three-stage filter: scrape → attribute-based → execution-based, 90k PRs → 11,407 → 2,294. | C009 | CORE | Table 1 | — | what the resulting set looks like |
| M.3 | Methods | N04 | What does the resulting benchmark look like? | Scale statistics: repos, issue length, codebase size, patch size; category diversity. | C001, C008, C011 | CORE | Table 2 | — | SWE-bench Lite |
| M.4 | Methods | — | What is SWE-bench Lite? | 300-instance self-contained subset. | — | SUPPLEMENTARY-pointer | — | SWE-bench Lite | how models were evaluated |
| M.5 | Methods (Experimental Setup) | N08 | Which models, how did they access the repo, what's the metric? | Models list, BM25/oracle/oracle-collapsed settings, resolution rate metric, context-window coverage. | C014 | CORE | Table 3 | BM25, oracle, resolution rate | SWE-Llama |
| M.6 | Methods | N07 | How was SWE-Llama trained? | Fine-tuned via LoRA on 10,000 instances from 37 disjoint repos. | C012 | CORE | — | LoRA | Results |
| R.1 | Results | N09 | How well do current LLMs do? | All models resolve a small fraction; 3.79% (best) to 0.17% (lowest). | C002, C015 | CORE | Table 4 | — | is this a capability or context problem? |
| R.2 | Results | N10 | Is it capability or context? | Oracle retrieval more than doubles Claude 2's rate (1.96%→4.80%). | C004 | CORE | — | — | does more context help or hurt? |
| R.3 | Results | N11, N12, N13 | Does more context help? | Performance falls with longer context; trimming to the edited region helps further; BM25 recall vs. precision mismatch. | C003, C010, C013, C018 | CORE | Table 5 | — | what do the patches look like? |
| R.4 | Results | N14 | What do successful patches look like? | Applied patches are much shorter than gold patches and rarely multi-file. | C006, C008 | CORE | — | — | does fine-tuning help? |
| R.5 | Results | N15 | Does a fine-tuned open model do better? | SWE-Llama trained on oracle context transfers poorly to BM25 context. | C005 | CORE | — | — | Lite vs full, model overlap |
| R.6 | Results | N16, N17 | What about the easier subset, and do models fail on the same problems? | SWE-bench Lite yields higher resolution; Claude 2 and SWE-Llama 13b overlap only partially. | C007, C019 | SUPPLEMENTARY | — | — | Discussion |
| D.1 | Discussion | N18 | So what does this mean? | Converging evidence is consistent with a context-selection bottleneck, not solely a capability gap. | C004, C013, C017, C018 | CORE | — | — | relation to prior work |
| D.2 | Discussion | N21 | What follows for the field? | Better retrieval/context handling may matter as much as raw generation capability. | C017 | CORE | — | — | limitations |
| L.1 | Limitations | N20 | What can't this show? | Python-only, single generation per instance, resolution ≠ quality, conflicting figures disclosed. | L001, L003, L004, L005, L006 | CORE | — | — | conclusion |
| C.1 | Conclusion | N19, N22 | What's the takeaway and what's next? | SWE-bench establishes a hard, realistic benchmark; today's models leave large headroom, much of it in context use. | C001, C002, C004 | CORE | — | — | — |

## Checks (ticked)
- [x] Every story-graph node appears in ≥1 row (N01–N23 covered above or via M.1/M.5 for N23/N08).
- [x] The RQ (N05) has result rows (R.1–R.6), interpretation rows (D.1), and discussion rows (D.1–D.2).
- [x] No row without a story node.
- [x] Question ledger: no planned debt beyond forward references resolved in story/question_ledger.json.
- [x] Term ledger: defining rows (M.1, M.5, M.6) precede first-use rows.
- [x] Visuals (Tables 1–5) each have a card below; no images used (Markdown tables only, per TASK.md).
- [x] SUPPLEMENTARY items (M.4, R.6) have a destination (kept brief in main text; no separate supplement exists in this run) and a main-text pointer.
- [x] Negative results (E018 ChatGPT-3.5 low score, E068 GPT-4 after-2023 zero score) placed per claims/claim_evidence_map.json negative_result_decisions.
