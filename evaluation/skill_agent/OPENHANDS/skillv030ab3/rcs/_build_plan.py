import json
W = lambda p, o: json.dump(o, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

W('.rcs/plan/audience_profile.json', {
    'mode': 'B',
    'primary': 'Machine-learning researchers from other subfields (for example vision, optimization, theory or NLP outside agents) who want to understand what the OpenHands platform is, what was evaluated and what the numbers show',
    'secondary': 'Reviewers and replicators checking whether reported numbers match the source tables and whether claims stay within the evidence',
    'tertiary': 'Future readers and practitioners looking for a self-contained account of the platform, its evaluation and its stated limits',
    'assumed_known': ['LLM', 'prompting (zero-shot, few-shot, chain-of-thought)', 'benchmarks and accuracy-style metrics', 'train and test splits', 'API', 'Docker as a concept', 'statistics basics (variance, seeds, confidence intervals)'],
    'not_assumed': ['LLM-agent terminology (action, observation, event stream, delegation)', 'SWE-bench, HumanEvalFix, WebArena, MiniWoB++, GAIA, GPQA, AgentBench, MINT', 'CodeAct, BrowserGym, Playwright, IPython, accessibility tree', 'prior agent frameworks and their features'],
    'binding_personas': ['A', 'B', 'E'],
    'term_budget': {'per_paragraph': 2, 'abstract_acronyms': 1},
    'source': 'task statement (audience given: adjacent ML researchers), 2026-09-29'})

W('.rcs/plan/reader_model.json', {'personas': [{
    'id': 'B',
    'description': 'Adjacent-field ML researcher: knows general ML, deep learning, standard evaluation and statistics; not the LLM-agent subfield terms, datasets or prior work.',
    'binding': True,
    'known_terms': ['ML', 'LLM', 'GPU', 'API', 'CI', 'accuracy', 'precision', 'recall', 'benchmark', 'zero-shot', 'few-shot', 'chain-of-thought', 'prompt', 'fine-tuning', 'HTML', 'DOM', 'Docker', 'REST', 'OS', 'PDF', 'UI', 'GUI', 'MIT', 'GitHub', 'SQL', 'BM25', 'RL', 'MD5', 'SDK', 'README', 'CPU', 'URL', 'JSON', 'Python', 'bash', 'shell'],
    'prerequisite_concepts': [
        {'concept': 'delegation', 'needs': ['generalist agent']},
        {'concept': 'SWE-bench Lite', 'needs': ['SWE-bench']},
        {'concept': 'BrowsingAgent', 'needs': ['browser']},
        {'concept': '1-shot', 'needs': ['0-shot']}],
    'likely_misconceptions': [
        {'misconception': 'competitive means best or state of the art',
         'trigger_terms': ['competitive'], 'corrective_point': 'several listed references score higher than OpenHands on several benchmarks', 'corrective_terms': ['below', 'higher']},
        {'misconception': 'OpenHands is a model or a single agent rather than a platform',
         'trigger_terms': ['OpenHands'], 'corrective_point': 'OpenHands is a platform on which agents run; scores belong to an agent plus a base model', 'corrective_terms': ['platform', 'base model']},
        {'misconception': 'reference numbers were re-run by the authors under matched conditions',
         'trigger_terms': ['reference'], 'corrective_point': 'reference numbers are reported values from other systems with different models and prompting', 'corrective_terms': ['reported', 'differ']},
        {'misconception': 'success, resolve and pass rates are comparable across benchmarks',
         'trigger_terms': ['success rate'], 'corrective_point': 'each benchmark defines its own metric', 'corrective_terms': ['defines', 'own metric']}],
    'reader_questions': ['What problem does this solve and for whom?', 'What is the platform made of?', 'Why were these design choices made?', 'How was it evaluated and against what?', 'Is the difference from the references bigger than noise?', 'What does the paper not show?'],
    'venue_expectations': ['limitations stated by the authors reported first', 'numbers exactly as in the source'],
    'new_term_budget': 3}]})

open('.rcs/plan/venue_profile.yaml', 'w', encoding='utf-8').write("""# Generic fallback profile (VENUE_UNKNOWN). Every rule is assumed; see state.json accepted_risks AR3.
venue: {name: "generic research article (conference style)", type: conference, guideline_urls: []}
structure:
  section_template: [Title, Abstract, Introduction, Related Work, Method, Experimental Setup, Results, Discussion, Limitations, Conclusion, References]
  results_discussion: separate
  related_work_position: after_intro
  limitations_section_required: true
  assumed: true
limits: {pages_main: null, words_main: 4500, abstract_words: 250, supplement_allowed: true, assumed: true}
style:
  citation_style: "author-year, (FirstAuthor et al., Year) as in the project materials"
  voice_preference: "active voice; 'we' avoided because this paper presents the authors' work in the third person"
  spelling: US
  abstract_format: unstructured
  abstract_citations_allowed: false
  assumed: true
required_statements:
  data_availability: true
  code_availability: true
  ai_use_disclosure: "disclosure.md (AI-assisted presentation of the authors' research)"
  assumed: true
checklists: []
reporting_guideline: null
""")

# ---- literature
W('.rcs/corpus/literature_map.json', {
 'dimensions': [
  {'dimension': 'General agent and multi-agent frameworks', 'sources': ['SRC-001', 'SRC-002', 'SRC-003', 'SRC-033', 'SRC-034', 'SRC-035', 'SRC-024'],
   'achieves': 'reusable building blocks, conversation frameworks, standardized operating procedures, customizable agent architectures (as described by the OpenHands authors)',
   'shared_assumption_or_limit': 'AutoGen: Python and bash execution with stateless command execution; CrewAI: sandboxed but limited code interpreter (SRC-002, SRC-035; authors\' description)',
   'relation_to_openhands': 'OpenHands positions itself as adding sandboxed, stateful shell, Python and browser execution to a general framework; Table 1 feature marks not recoverable'},
  {'dimension': 'Software-engineering agents', 'sources': ['SRC-004', 'SRC-005', 'SRC-025'],
   'achieves': 'automated GitHub issue fixing (SWE-Agent, AutoCodeRover, Agentless)',
   'shared_assumption_or_limit': 'domain-specific (Table 1 domain column: SWE); SWE-Agent stresses a carefully crafted agent-computer interface',
   'relation_to_openhands': 'reference systems on SWE-bench Lite; source of edit utilities adapted into AgentSkills'},
  {'dimension': 'Web agents', 'sources': ['SRC-009', 'SRC-010', 'SRC-026', 'SRC-027', 'SRC-028', 'SRC-029', 'SRC-030', 'SRC-012'],
   'achieves': 'WebArena and MiniWoB++ results with trained or reflective agents',
   'shared_assumption_or_limit': 'several reference agents are trained specialists or use reward models, against domain-general prompting for OpenHands agents',
   'relation_to_openhands': 'references for the web results; BrowserGym supplies the action language'},
  {'dimension': 'Benchmarks used for evaluation', 'sources': ['SRC-006', 'SRC-011', 'SRC-013', 'SRC-014', 'SRC-015', 'SRC-016', 'SRC-018', 'SRC-019', 'SRC-020', 'SRC-021', 'SRC-022', 'SRC-023', 'SRC-008', 'SRC-012', 'SRC-009'],
   'achieves': 'task suites for software, web and assistance abilities',
   'shared_assumption_or_limit': 'each defines its own metric and subset conventions',
   'relation_to_openhands': 'the 15 integrated benchmarks'}],
 'note': 'All entries are works cited in the OpenHands paper, registered at abstract depth from the project text; nothing was read beyond how the project describes them.'})

open('.rcs/story/lit_gap_chain.md', 'w', encoding='utf-8').write("""# Literature -> Gap -> Question chain (scoped to the project's own related work)

DIMENSION: general agent frameworks (SRC-001, SRC-002, SRC-003, SRC-033, SRC-034, SRC-035)
  ACHIEVES: building blocks and multi-agent conversation (authors' description) {C004}
  SHARED LIMIT: AutoGen has stateless command execution; CrewAI has a limited code interpreter (SRC-002, SRC-035; two sources, both as characterized by the OpenHands authors) {C005}
  EVIDENCE OF FAILURE: none beyond the authors' characterization; no source was read.
DIMENSION: software-engineering agents (SRC-004, SRC-005)
  ACHIEVES: GitHub issue fixing {C005}
  SHARED LIMIT: domain-specific per Table 1 domain column {C005}
GAP (scoped): In the OpenHands authors' own description of related work, no single listed framework is described as combining a stateful sandboxed shell, Python and browser runtime, a shared tool library, delegation and a benchmark harness. The Table 1 feature marks that would support this are not recoverable from the extracted text, so the paper states the gap as the authors' positioning and not as a finding of a literature search.
QUESTION: RQ1 (design) and RQ2 (evaluation), derived from the authors' stated goal {C003}.
STATUS: INSUFFICIENT_LITERATURE accepted as workflow risk AR4 (no web, works cited in the project only).
""")

open('.rcs/corpus/corpus_log.md', 'w', encoding='utf-8').write("""# Corpus log
Mode: literature limited to works cited in project/paper.txt (no web). No search queries were run.
Registered: 35 sources from the project's reference list and text, each with a support quote copied from project/paper.txt (verification method user_supplied_file, read_depth abstract, i.e. described by the citing authors only).
Screening: registered only the works that the draft may cite (frameworks, reference systems, benchmarks, action-language and metric sources). Excluded: works cited only in passing (for example LLM model reports, generic surveys, household-robot and scientific-agent examples).
Titles are kept exactly as the project cites them; the BrowserGym citation carries the WorkArena title as cited and is marked title_status unverifiable.
## Suspicious content
None found. No instruction-like text aimed at models or reviewers in paper.txt, README_1.md or README_2.md.
""")
W('.rcs/corpus/writing_patterns.json', {'patterns': []})
W('.rcs/corpus/anti_patterns.json', {'patterns': []})
open('.rcs/corpus/RUN_SUMMARY.md', 'w', encoding='utf-8').write("""# Run summary
Evidence items: 82 (see research_evidence.json). Conflicts: 2 pairs, both resolved by the agent with reasons (state.json AR2). Missing items: 9 (missing_evidence.json). Sources registered: 35 (all abstract-depth, described-by-citing-authors). Suspicious content: none. Not opened: nothing in project/ was skipped.
Patterns mode: no exemplar papers are available without the web; writing_patterns.json and anti_patterns.json are empty by design.
""")
print('ok')
