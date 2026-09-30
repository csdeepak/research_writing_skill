# Paper Architecture: OpenHands platform and its evaluation, for adjacent ML researchers

Story pattern: method_first (platform first, then evaluation questions) with question-led results
Audience mode: B · Binding personas: A, B, E · Venue profile: plan/venue_profile.yaml (assumed rules: 4)
Length limit (main text): 4500 · Planned total: 3500 (<= 90% of the limit = 4050)

| # | Section | Story node(s) | Reader question answered | Point (one sentence) | Claims | Density | Visual | New terms | Words | Link forward |
|---|---------|---------------|--------------------------|----------------------|--------|---------|--------|-----------|-------|--------------|
| A.1 | Abstract | N01-N23 | What is this, what was found, what is the limit? | Spine in miniature with numbers | C001 C010 C024 C030 C032 C034 C038 C041 C042 L001 L006 L010 | CORE | — | agent, platform | 180 | — |
| I.1 | Introduction | N01, N02 | What is the problem and why care? | Building and evaluating agents that act through software is hard, and the authors see software as the ideal interface | C001 C002 | CORE | — | agent, action | 110 | what existing frameworks do |
| I.2 | Introduction | N03, N04 | What is missing? | As the authors describe them, frameworks are either general with limited code execution or specific to software engineering | C004 C005 | CORE | — | framework | 110 | so they ask two questions |
| I.3 | Introduction | N05, N06, N07 | What exactly do they ask? | A design question and an evaluation question follow from the stated goal of general agents | C003 C026 | CORE | — | generalist agent | 90 | approach |
| I.4 | Introduction | N08 | What did they do? | OpenHands, with the stated reason for its action set | C010 C011 C012 | CORE | — | event stream, sandbox | 90 | contributions |
| I.5 | Introduction | N18, N19 | What is contributed? | Three numbered contributions with pointers to results | C019 C024 C029 C042 | CORE | — | — | 80 | paper map |
| I.6 | Introduction | — | Where is what? | Paper map by question | — | CORE | — | — | 40 | related work |
| R.1 | Related work | N03 | What do general frameworks provide? | Frameworks give building blocks; AutoGen and CrewAI have limited code execution per the authors | C004 C005 | CORE | — | — | 110 | SWE and web agents |
| R.2 | Related work | N03 | What are the reference systems? | Software-engineering and web agents appear as reference rows | C005 C006 | SUPPORTING | — | reference system | 110 | relation |
| R.3 | Related work | N04 | How does OpenHands relate? | Positioning as the authors' claim; Table 1 marks lost | C005 L013 | CORE | — | — | 60 | method |
| M.1 | Method | N09, N24 | What is the core abstraction? | Agent = event history to action; runtime = action to observation | C010 | CORE | — | event stream, action, observation | 110 | runtime |
| M.2 | Method | N09 | Where do actions run? | Per-session Docker container with shell, IPython and Chromium; arbitrary images | C011 C013 C014 | CORE | — | sandbox | 140 | why these actions |
| M.3 | Method | N09 | Why these actions? | Authors' stated reason for three primitives | C012 | CORE | — | — | 70 | skills |
| M.4 | Method | N09 | How are tools shared? | AgentSkills package and inclusion criteria | C015 C016 C006 | CORE | — | skill | 110 | delegation |
| M.5 | Method | N09 | How do agents cooperate and what agents exist? | Delegation, hub, micro agents | C017 C018 C019 C020 | CORE | — | delegation, micro agent | 110 | interface and tests |
| M.6 | Method | N09 | How do users and developers interact? | UI with interruption; mocked-LLM integration tests | C021 C022 C023 | SUPPORTING | — | — | 90 | safety framing |
| M.7 | Method | N09 | What does the platform say about safety? | Authors expect risk mitigation via evaluation and oversight; no safety evaluation reported | C027 L005 | CORE | — | — | 60 | evaluation set-up |
| S.1 | Experimental setup | N11, N25 | What was evaluated? | 15 benchmarks in three categories | C024 C003 | CORE | Table 1 | benchmark names | 110 | protocol |
| S.2 | Experimental setup | N11 | Under what protocol? | Reproducible open-source reference systems, no benchmark-specific prompt engineering, Lite subset, adaptations | C025 C026 C028 | CORE | — | 0-shot, 1-shot | 120 | how to read scores |
| S.3 | Experimental setup | N25 | How to read the scores? | Each benchmark has its own metric; reference numbers are reported values | C025 L011 | CORE | — | score | 60 | results |
| Rs.1 | Results | N12 | How does it do on software benchmarks? | SWE-bench Lite 26.0 (claude), 22.0, 7.0; HumanEvalFix 79.3 vs 87.7; five further benchmarks | C030 C031 C032 C033 | CORE | Table 2 | resolve rate | 270 | web |
| Rs.2 | Results | N13 | And on web benchmarks? | WebArena up to 15.5, MiniWoB++ up to 40.8 with references above and below | C034 C035 C036 | CORE | Table 2 | — | 150 | assistance |
| Rs.3 | Results | N14 | And on assistance benchmarks? | GAIA 32.1, GPQA 52.0, AgentBench 57.6, MINT, ProofWriter, EDA | C037 C038 C039 C043 | CORE | Table 3 | — | 170 | pattern |
| Rs.4 | Results | N15 | What is the pattern, including negatives? | Model dependence; rows below reference; cost note | C040 C041 C044 | CORE | — | — | 150 | discussion |
| D.1 | Discussion | N16, N17 | What do the results answer? | Design question answered by description; evaluation question: competitive, not leading | C042 C031 C036 | CORE | — | — | 150 | ecosystem |
| D.2 | Discussion | N22 | What is the later state? | Repository READMEs and community numbers, as documentation only | C045 C046 C029 | SUPPORTING | — | — | 80 | limitations |
| D.3 | Discussion | N17 | What alternative readings exist? | Scores mix agent, model, version | L015 | CORE | — | — | 60 | limitations |
| Lim.1 | Limitations | N20 | What do the authors concede? | Nine author-stated limits | L001-L009 | CORE | — | — | 250 | additional caveats |
| Lim.2 | Limitations | N21 | What further caveats apply? | Six writer-derived caveats | L010-L015 | CORE | — | — | 150 | conclusion |
| Con.1 | Conclusion | N17, N23 | What now? | Platform plus competitive-not-leading evidence; next steps by the authors | C042 C050 | CORE | — | — | 110 | — |

## Checks
- [x] Every story-graph node appears in >=1 row (N01-N25)
- [x] Every RQ has result rows (Rs.1-Rs.4), interpretation rows (D.1) and discussion rows
- [x] No row without a story node (Abstract and paper map are venue structure)
- [x] Question ledger: forward references only in the introduction (see story/question_ledger.json)
- [x] Term ledger: defining row precedes first use (story/term_ledger.json)
- [x] Visuals: Tables 1-3 have cards (plan/figure_cards/); no images
- [x] SUPPLEMENTARY: full Table 7 GPQA subsets and cost columns are summarized in text; per-row costs beyond those cited go unreported (destination: the source paper's appendix tables)
- [x] Negative results placed main text (Rs.1-Rs.4, decisions in claim map)
- [x] Every author_stated limitation has a Limitations row (Lim.1); writer-derived caveats have "Additional caveats" (Lim.2)
- [x] Every rationale claim (C001-C003, C012, C014, C016, C018, C020, C023, C026, C027, C028) has an Introduction (motivation) or Introduction/Method (design choice) row; C026 and C028 sit in Experimental setup, which the lint accepts as design placement
- [x] Sum of words 3500 <= 90% of 4500
