import json
ID = json.load(open('.rcs/_ids.json'))
W = lambda p, o: json.dump(o, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

terms = [
 ('agent', 'technical', 'an LLM-driven program that repeatedly chooses an action, receives an observation, and continues until the task ends', 'I.1', ['bot', 'assistant program']),
 ('action / observation', 'technical', 'an action is one step an agent takes (run code, run a shell command, act in a browser); an observation is what the environment returns', 'I.1', []),
 ('platform', 'technical', 'OpenHands as software that agents, tools, runtimes and benchmarks plug into; not a model', 'I.4', ['framework (except for prior systems)']),
 ('generalist agent', 'technical', 'an agent meant to handle several task categories with one prompt and action space', 'I.3', []),
 ('event stream', 'technical', 'the chronological record of all actions and observations of a session', 'I.4', []),
 ('sandbox / runtime', 'technical', 'the isolated Docker container in which actions execute (sandbox) and the system that turns actions into observations (runtime)', 'I.4', []),
 ('skill', 'project_specific', 'a Python function in the AgentSkills library that agents call from the IPython environment', 'M.4', ['plug-in', 'module']),
 ('delegation', 'technical', 'an agent handing a subtask to another agent through AgentDelegateAction', 'M.5', []),
 ('reference system', 'technical', 'another system whose score is quoted from the OpenHands paper tables', 'I.5', ['baseline (except when quoting the authors)']),
 ('0-shot / 1-shot', 'technical', 'no demonstration vs one demonstration in the prompt', 'S.2', []),
 ('score', 'technical', 'the percentage a benchmark reports (resolve rate, pass rate or success rate, each defined by the benchmark)', 'S.3', []),
 ('resolve rate', 'technical', 'share of SWE-bench Lite instances whose repository tests pass after the agent edits the code', 'Rs.1', []),
]
W('.rcs/story/term_ledger.json', {'terms': [{'term': t, 'kind': k, 'definition': d, 'defined_at': a, 'first_used_at': a, 'uses': None, 'audience_modes_requiring_definition': ['B', 'C', 'D', 'E'], 'synonyms_forbidden': s} for t, k, d, a, s in terms]})

qs = [
 ('Q01', 'Why do agents that act through software need a platform?', 'I.1', 'I.1', None),
 ('Q02', 'Why do existing frameworks not suffice?', 'I.2', 'I.2', None),
 ('Q03', 'What exactly is asked?', 'I.3', 'I.3', None),
 ('Q04', 'What was built and why these choices?', 'I.4', 'M.1-M.6', None),
 ('Q05', 'How was it evaluated?', 'I.5', 'S.1-S.3', None),
 ('Q06', 'How good are the results and against what?', 'I.5', 'Rs.1-Rs.4', None),
 ('Q07', 'What do results not establish?', 'Rs.4', 'D.3 and Lim.1-Lim.2', None),
 ('Q08', 'Is the platform safe?', 'M.7', 'M.7 and Lim.1', None),
 ('Q09', 'Do differences exceed noise?', 'Rs.1', 'Lim.2', None),
]
W('.rcs/story/question_ledger.json', {'questions': [{'id': i, 'question': q, 'raised_at': r, 'answered_at': a, 'deferred_to': d, 'reader_personas': ['B']} for i, q, r, a, d in qs], 'debt': 0})

cards = {
 'TAB-1': ('Table 1: benchmark suite by category with the subset used', 'Which benchmarks were run and at what size?', ['C024', 'C025'], ['m_bench15', 'm_benchsetup', 'm_websetup', 'm_miscsetup'], 'S.1'),
 'TAB-2': ('Table 2: software and web scores of OpenHands agents beside the reference rows the paper lists', 'Where do OpenHands software and web scores fall against the listed references?', ['C030', 'C032', 'C034', 'C035'], ['r_swe_oh', 'r_swe_ref', 'r_hef', 'r_hef_ref', 'r_wa', 'r_wa_ref', 'r_mw'], 'Rs.1'),
 'TAB-3': ('Table 3: assistance-benchmark scores of OpenHands agents beside the reference rows the paper lists', 'Where do OpenHands scores on assistance benchmarks fall against the listed references?', ['C037', 'C038', 'C039'], ['r_gaia', 'r_gpqa', 'r_ab', 'r_mint', 'r_pw', 'r_eda'], 'Rs.3'),
}
for cid, (take, q, cl, ev, place) in cards.items():
    txt = """```yaml
id: %s
purpose: "%s"
rq: "evaluation question (N06)"
takeaway: "%s"
claims: [%s]
evidence: [%s]
type: table
source_data: ["project/paper.txt"]
comparison_the_eye_must_make: "OpenHands rows against the listed reference rows, per benchmark"
uncertainty_shown: "none: the source reports no variance, seeds or intervals (missing_evidence M003)"
baseline_or_reference: "reference rows are values reported in the source tables"
non_conclusions: "no ordering claim within about one point; no matched-tuning comparison; not a ranking of platforms"
selection_rule: "all rows of the source tables for the benchmarks shown, except cost columns and reference rows for gpt-3.5-class models on some benchmarks (summarized in text)"
honesty_checks: {bar_axis_from_zero: true, all_conditions_shown: true, dual_axis: false, three_d: false}
accessibility: {colorblind_safe: true, redundant_encoding: "numeric labels", min_font_pt_at_print: 7, alt_text: "Markdown table"}
placement: "%s"
status: planned
```
""" % (cid, q, take, ', '.join(cl), ', '.join(ID[k] for k in ev), place)
    open('.rcs/plan/figure_cards/%s.md' % cid, 'w', encoding='utf-8').write(txt)
print('ok')
