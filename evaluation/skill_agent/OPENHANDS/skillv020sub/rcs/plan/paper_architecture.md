# Paper Architecture: OpenHands as a general platform for software-interacting agents

Story pattern: method_first (Problem -> Method/Approach -> Properties -> Experiments), with an
explicit two-part research question (question_led flavor) inside it.
Audience mode: B (adjacent researcher) - Binding personas: A, B, E - Venue profile: plan/venue_profile.yaml (VENUE_UNKNOWN; run-specific rules applied directly; other rules assumed:true)
Length limit (main text): 4500 words (floor 3000) - Planned total: ~4000 words (89% of the limit)

Each row is one paragraph slot. drafts/v001/paper.md expands each into a paragraph.

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Words | Link forward |
|---|---------|---------------|---------------------------|----------------------|--------|---------|--------|-----------|-------|--------------|
| T.1 | Title | N17,N18 | What is this about and what did it find? | A truthful promise: an open platform + one generalist agent competitive across categories | C013 | CORE | - | - | 15 | - |
| AB.1 | Abstract | N01,N02 | Context/problem | Building software-interacting agents needs 5 pieces no single open framework combined | C021 | CORE | - | agent, sandbox | 40 | the gap |
| AB.2 | Abstract | N04 | Gap | Existing frameworks each cover only part of this | C021 | CORE | - | - | 30 | the question |
| AB.3 | Abstract | N05,N06 | Question/approach | OpenHands supplies all 5 pieces; tests whether one unmodified agent is then competitive across categories | - | CORE | - | - | 40 | the results |
| AB.4 | Abstract | N11,N12,N13 | Key results with magnitudes | Headline numbers across all 3 categories | C001,C003,C007,C008,C013 | CORE | - | - | 60 | meaning |
| AB.5 | Abstract | N14,N27 | Meaning + scope | Suggests interface generality, not per-task engineering, drives the result; scope/limit named | C013,L002,L008 | CORE | - | - | 30 | - |
| I.1 | Introduction | N01,N33 | What is the problem, for whom? | Building agents that act through real software requires assembling many separate pieces | - | CORE | - | agent/action/observation loop | 130 | why it matters |
| I.2 | Introduction | N02 | Why does it matter? | Software is already the most general interface humans have for acting on the world (authors' own motivation) | C030 | CORE | - | - | 90 | what's missing |
| I.3 | Introduction | N03,N04 | What's missing from existing approaches? | Prior frameworks each supply some pieces but none combines all five, dimension by dimension | C021 | CORE | - | ACI | 160 | the question |
| I.4 | Introduction | N05,N06,N07 | What exactly do you ask? | RQ1 (one platform, five pieces?) and RQ2 (one unmodified agent, competitive across categories?), explicit | - | CORE | - | - | 90 | the approach |
| I.5 | Introduction | N08,N09 | What did you do, and why this way? | OpenHands's architecture in one paragraph, with the code-execution design rationale | C031,C032,C033 | CORE | - | sandbox, event stream | 140 | what you found |
| I.6 | Introduction | N14,N18,N17 | What do you contribute? | Numbered contributions: the platform; the cross-category competitiveness result; each tied to a result | C013,C001,C003,C007,C008 | CORE | - | - | 130 | paper map |
| I.7 | Introduction | (map) | Where is it in the paper? | One-sentence map of Method/Results/Discussion/Limitations by question | - | CORE | - | - | 40 | Related Work |
| RW.1 | Related Work | N03 | What already exists, organized how? | Organize prior frameworks by which of the five pieces they supply, not paper-by-paper | C021 | CORE | - | - | 60 | dimension 1 |
| RW.2 | Related Work | N03 | General orchestration frameworks | LangChain/AutoGen/CrewAI: basic runtime, stateless execution, or a limited interpreter | C021 | CORE | - | - | 90 | dimension 2 |
| RW.3 | Related Work | N03 | Single-capability specialists | BrowserGym / DSPy: excel at one piece, supply none of the rest | C021 | CORE | - | - | 60 | dimension 3 |
| RW.4 | Related Work | N03 | Collaboration-pattern frameworks | MetaGPT / GPTSwarm: strong on agent-collaboration patterns, not on the execution substrate; OpenHands' own workflow is comparatively handcrafted | C021,L005 | CORE | - | - | 70 | dimension 4 |
| RW.5 | Related Work | N03,N04 | SWE-issue specialists | SWE-Agent/AutoCodeRover/Agentless: strong, but scoped to one task family; ACI insight OpenHands generalizes | C021,C031 | CORE | Table 1 (TAB-1 preview) | - | 80 | Method |
| M.1 | Method | N09,N34 | How does an OpenHands agent act on the world? | Event-stream architecture; three actions (bash/Python/browser); background on sandboxing | C032 | CORE | - | sandboxed execution | 120 | why this design |
| M.2 | Method | N09,N36 | Why this action space, and how is it kept safe? | Code-execution design rationale; Docker sandbox isolation rationale; arbitrary base images | C032,C033 | CORE | - | ACI (defined) | 130 | the tool library |
| M.3 | Method | N09 | How is the tool library kept from growing unbounded? | AgentSkills' explicit inclusion rule, with examples | C034 | CORE | - | - | 90 | multi-agent pieces |
| M.4 | Method | N09 | How do agents collaborate? | AgentDelegateAction; AgentHub agents (CodeActAgent, BrowsingAgent, GPTSwarm, micro agents) | C037 | CORE | - | delegation | 110 | keeping it reliable |
| M.5 | Method | N09 | How is quality controlled without re-running everything? | Mocked-LLM integration tests, rationale, and what they check | C035 | SUPPORTING | - | - | 70 | evaluation setup |
| ES.1 | Experimental Setup | N10,N35 | What exactly was run, and against what? | One CodeActAgent (BrowsingAgent/GPTSwarm via delegation), 0-shot, 15 benchmarks, 3 categories, vs. each benchmark's own baselines | C036 | CORE | - | resolve rate / pass rate | 130 | why SWE-Bench Lite | 
| ES.2 | Experimental Setup | N10 | Why this specific software-engineering setup? | SWE-Bench Lite subset, no hint text, for cost and realism | C036 | CORE | - | - | 70 | software results |
| R.1 | Results | N11 | RQ2 in software engineering: what happened? | SWE-Bench Lite: 26.0% (claude-3.5-sonnet), in the specialists' range; scales with backbone model | C001,C002 | CORE | Table 1 (TAB-1) | - | 130 | how robust |
| R.2 | Results | N11 | How large/robust, and what does it mean here? | Interpretation at measured strength + link to RQ2 + single-run caveat | C001,C002 | CORE | - | - | 90 | the other SWE benchmark |
| R.3 | Results | N11,N22 | HumanEvalFix: what happened, and what can't we conclude? | 79.3% 0-shot; vs. non-agentic and vs. SWE-Agent's 1-shot 87.7%, with the shot-count caveat in place | C003,C004,L004 | CORE | (TAB-1 cont.) | - | 130 | web browsing |
| R.4 | Results | N12 | RQ2 in web browsing: what happened? | WebArena: at/above the domain-general baseline, below trained specialists | C005 | CORE | Table 2 (TAB-2) | accessibility tree (gloss) | 120 | the counter-example |
| R.5 | Results | N12,N26 | Where does the pattern break, and why report it? | MiniWoB++: a trained RL specialist clearly wins; named as the paper's clearest negative result | C006 | CORE | (TAB-2 cont.) | - | 100 | the remaining categories |
| R.6 | Results | N13 | RQ2 in the remaining, more varied tasks: what happened? | GAIA, GPQA, AgentBench, MINT, ProofWriter, EDA -- one RIC pass across the six | C007,C008,C009,C010,C011,C012 | CORE | Table 3 (TAB-3) | - | 220 | one exception here too |
| R.7 | Results | N13,N15 | What ties all these numbers together? | Same pattern as software/web: mostly competitive, scales with backbone, one code-subset exception | C010,C014 | CORE | - | - | 90 | Discussion |
| D.1 | Discussion | N14,N06 | Does the evidence answer RQ2? | Yes, for most of the 11 confidently-measured benchmarks across all 3 categories | C013 | CORE | - | - | 90 | mechanism |
| D.2 | Discussion | N15,N27 | Why does this pattern hold -- mechanism? | Backbone-model capability, not category-specific engineering, explains most of the residual gap; alternative (architecture-is-category-specific) considered and set aside | C014 | CORE | - | - | 110 | RQ1 |
| D.3 | Discussion | N16,N05 | Does the evidence answer RQ1? | The platform closes the gap by construction; each of the five pieces is demonstrated in one run | - | CORE | - | - | 70 | relation to prior work |
| D.4 | Discussion | N04,C021 | How does this relate to prior frameworks? | Confirms the dimension-by-dimension gap argument; extends the ACI idea from one task to a general library | C021,C031 | SUPPORTING | - | - | 80 | implications |
| D.5 | Discussion | N28,C040,C041 | What are the practical implications? | Open, extensible infrastructure plus a large community; continued expansion since publication | C040,C041 | SUPPORTING | - | - | 90 | limitations |
| Lim.1 | Limitations | N19,N20,N21,N23 | What do the authors themselves concede? | Multi-modality, complex-task struggles (central), long-file editing, handcrafted workflows -- each tied to what it bounds | L001,L002,L003,L005 | CORE | - | - | 150 | the HumanEvalFix caveat |
| Lim.2 | Limitations | N22 | What specific comparison did the authors flag as unequal? | HumanEvalFix 0-shot vs. 1-shot, restated with its effect on C003/C004 | L004 | CORE | - | - | 60 | additional caveats |
| Lim.3 | Limitations | N24,N25,N26 | What further caveats does the writer add? | "Additional caveats": uncontrolled baselines, no variance reported, non-universal pattern | L006,L007,L008 | CORE | - | - | 130 | Conclusion |
| Con.1 | Conclusion | N14,N18 | What is now understood that wasn't before? | One unmodified generalist agent is competitive across categories; states the finding at claim strength | C013 | CORE | - | - | 70 | meaning |
| Con.2 | Conclusion | N27 | What does that change? | Interface generality, not per-task engineering, is the more direct explanation offered here | C014 | CORE | - | - | 50 | the boundary |
| Con.3 | Conclusion | N20,N26 | What is the key boundary? | Competitive on most, not all, benchmarks; agents (this one included) still struggle with complex tasks | L002,L008 | CORE | - | - | 50 | next questions |
| Con.4 | Conclusion | N29,N30,N31 | What follows? | Stronger agents, automatic workflow generation, principled multi-modality, named as the authors' own next steps | - | CORE | - | - | 50 | - |

## Checks (ticked before Gate G2)
- [x] Every story-graph node appears in >=1 row (N01-N36 all covered above or via background-concept glosses inline; N32 is folded into the M.4/D.5 openness point rather than its own row, since it is a minor future item -- justified: SUPPLEMENTARY-tier, one clause suffices, added inline in Discussion D.5's paragraph rather than a dedicated slot).
- [x] Every RQ (N05, N06) has result rows (R.1-R.7), interpretation rows (D.1-D.3), and discussion rows (D.1-D.5).
- [x] No row without a story node.
- [x] Question ledger: no planned debt beyond the paper map (I.7); RQ1/RQ2 both raised in I.4, both answered in D.1/D.3.
- [x] Term ledger: every term's defining row precedes its first-use row (checked against story/term_ledger.json).
- [x] Every visual has a figure/table card with a takeaway and an RQ (plan/figure_cards/TAB-1.md, TAB-2.md, TAB-3.md).
- [x] SUPPLEMENTARY items (Docker image-tagging mechanics, full AgentSkills/BrowserGym API lists, GPQA sub-splits, per-instance cost tables) have a destination: omitted from the main text entirely (no appendix/supplement exists in this deliverable; TASK.md asks for a single ./paper.md), noted as such in open_issues.md rather than drafted.
- [x] Negative results (E073 MiniWoB++, E097 MINT-code) placed per their decisions (reported_main): R.5 and R.6/R.7.
- [x] Every `author_stated` limitation (L001-L005) has a Limitations row (Lim.1, Lim.2); writer-derived caveats (L006-L008) have a separate "Additional caveats" row (Lim.3).
- [x] Every rationale claim (C030-C037) has an Introduction (motivation: C030, C031) or Introduction/Method (design_choice: C032-C037) row.
- [x] Sum of Words column ~= 4000 <= 90% of 4500-word limit (4050); overflow policy: if the draft exceeds this, trim SUPPORTING-density rows (D.4, D.5, M.5) first, never CORE rows or limitation/rationale content.
