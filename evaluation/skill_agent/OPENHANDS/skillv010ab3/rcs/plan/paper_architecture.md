# Paper Architecture: OpenHands (method-first; audience B; generic venue with task rules)

Story pattern: method_first. Audience mode B. Word target 3,800-4,300 main text.

| # | Section | Story nodes | Reader question answered | Point | Claims | Density | Visual | New terms | Link forward |
|---|---------|-------------|--------------------------|-------|--------|---------|--------|-----------|--------------|
| I.1 | 1 Introduction | N01,N02,N24 | What problem and why care? | Agents acting through software need shared infrastructure | C001 | CORE | - | agent, sandbox | what existing frameworks do |
| I.2 | 1 | N03,N04 | What is missing? | As the authors describe, frameworks are building blocks, limited runtimes, or single-domain | C002 | CORE | - | - | so the authors build a platform |
| I.3 | 1 | N05,N06,N07 | What is asked? | RQ1 platform, RQ2 generalist competitiveness | C027,C021 | CORE | - | generalist agent | approach |
| I.4 | 1 | N08,N18 | What was done, contributed? | five components; 15 benchmarks; contributions | C027,C009 | CORE | - | - | map |
| I.5 | 1 | - | Where is what? | paper map by question | - | CORE | - | - | background |
| B.1 | 2 Background | N03,N24 | What vocabulary needed? | event stream, CodeAct, SWE-Bench basics | C003 | SUPPORTING | - | CodeAct, resolve rate | frameworks |
| B.2 | 2 | N03,N04 | How do frameworks differ? | dimensions: runtime, domain | C002 | CORE | - | - | platform |
| P.1 | 3 Platform | N09 | What is an agent here? | function history->action | C003 | CORE | - | event stream | actions |
| P.2 | 3 | N09,N10 | How do actions run? | three actions, per-session docker sandbox, API | C004 | CORE | - | action execution API | images |
| P.3 | 3 | N10 | How reproduce environments? | arbitrary image; tags | C005 | SUPPORTING | - | - | skills |
| P.4 | 3 | N10 | Which tools? | AgentSkills, criteria | C006 | CORE | - | skill | delegation |
| P.5 | 3 | N10 | Multi-agent, hub? | delegation, hub | C007,C008 | CORE | - | delegation | QC |
| P.6 | 3 | N10 | Users and QC? | GUI, integration tests | C023 | OPTIONAL | - | - | evaluation |
| S.1 | 4 Setup | N11 | What is evaluated and how? | 15 benchmarks, 0-shot, baselines | C009 | CORE | Table 1 | benchmark names | results |
| S.2 | 4 | N11 | Per-benchmark setup caveats | subsets, shots | C009 | SUPPORTING | Table 1 | - | results |
| R.1 | 5 Results | N12 | Software results | SWE 26.0 etc | C011,C012 | CORE | Table 2 | - | HumanEvalFix |
| R.2 | 5 | N12 | HumanEvalFix | 79.3 | C013 | CORE | Table 2 | - | web |
| R.3 | 5 | N13 | Web | WebArena, MiniWoB++ | C014,C015 | CORE | Table 2 | - | misc |
| R.4 | 5 | N14 | Misc | GAIA GPQA etc | C016-C019 | CORE | Table 3 | - | negatives |
| R.5 | 5 | N15 | Where not leading | negative list | C020 | CORE | Table 3 | - | discussion |
| D.1 | 6 Discussion | N16,N17 | Answers to RQ1, RQ2 | RQ1 by description; RQ2 consistent with | C027,C021 | CORE | - | - | limits |
| D.2 | 6 | N16 | What not established | single-run, heterogeneous | C021 | CORE | - | - | limitations |
| D.3 | 6 Limitations | N19-N21 | Which bounds? | triples | L001-L006 | CORE | - | - | later |
| D.4 | 6 | N22,N23 | Implications, future | catalyst expectation; roadmap | C022,C024,C025 | SUPPORTING | - | - | later state |
| D.5 | 7 Later state | N23 | Since the paper? | READMEs | C026 | OPTIONAL | - | Agent Canvas | conclusion |
| K.1 | 8 Conclusion | N18 | What now? | synthesis | C027,C021,C020 | CORE | - | - | - |

## Checks
- [x] every node placed (N24 in I.1/B.1); [x] RQ1 and RQ2 have result, interpretation, discussion slots (RQ1's "result" is the system description P.1-P.6)
- [x] negative results reported in main text (R.5); conflicts reported in table notes
- [x] SUPPLEMENTARY destination: Table 4 rows with unrecoverable mapping omitted; docker tagging in one sentence; skills list in one sentence
