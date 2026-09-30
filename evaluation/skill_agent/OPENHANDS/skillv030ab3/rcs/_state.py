import json, sys
p = '.rcs/state.json'
s = json.load(open(p, encoding='utf-8'))
cmd = sys.argv[1]
if cmd == 'risks':
    s['accepted_risks'] = [
        {'kind': 'workflow', 'id': 'AR1', 'text': 'No human available at G1: claims C033, C040, C041 (soft table alignment or writer-derived patterns) stay author_confirmation pending; C033 is NEEDS_REVIEW and is reported with an explicit alignment caveat. Author-stated claims are marked confirmed because they are quoted from the authors\' own paper.'},
        {'kind': 'workflow', 'id': 'AR2', 'text': 'Conflicts resolved without a human, by the agent, with written reasons in the evidence map: SWE-bench Lite gpt-4o-mini 7.0 (Tab.4) vs 6.3 (Tab.3): Table 4 chosen; GPQA diamond expert human 81.3 (Tab.6) vs 81.2 (Tab.7): Table 6 chosen. Both discrepancies are disclosed in the paper text.'},
        {'kind': 'workflow', 'id': 'AR3', 'text': 'VENUE_UNKNOWN: a generic conference-style profile with assumed rules is used; the task fixes only audience (adjacent ML researchers) and length (3000-4500 words main text).'},
        {'kind': 'workflow', 'id': 'AR4', 'text': 'INSUFFICIENT_LITERATURE: no web; the literature is limited to works cited in the project paper, registered from the project text at abstract depth with user_supplied_file verification. The gap is scoped to the authors\' own characterization of prior work.'},
        {'kind': 'workflow', 'id': 'AR5', 'text': 'No explicit research questions exist in the paper; the two questions in the spine (design, evaluation) are the writer\'s framing of the authors\' stated goal (C003) and are labelled as such in the draft.'},
    ]
    s['open_failures'] = [
        {'state': 'CONFLICTING_EVIDENCE', 'id': 'F1', 'location': 'E039/E040; E058/E059', 'detail': 'Table 3 vs Table 4; Table 6 vs Table 7', 'raised_by': 'CORPUS', 'raised_at_step': 2, 'class': 'ASK', 'resolution': 'resolved by agent with documented reason (AR2)'},
        {'state': 'MISSING_RESULT', 'id': 'F2', 'location': '.rcs/evidence/missing_evidence.json', 'detail': 'M001-M008: Table 1 marks, alignment, variance, ablations, reference tuning', 'raised_by': 'CORPUS', 'raised_at_step': 2, 'class': 'MARK', 'resolution': None},
        {'state': 'INSUFFICIENT_LITERATURE', 'id': 'F3', 'location': 'corpus/', 'detail': 'gap scoped to authors\' characterization', 'raised_by': 'AUTHOR', 'raised_at_step': 7, 'class': 'ASK', 'resolution': 'accepted as workflow risk AR4'},
        {'state': 'VENUE_UNKNOWN', 'id': 'F4', 'location': 'plan/venue_profile.yaml', 'detail': 'generic profile', 'raised_by': 'AUTHOR', 'raised_at_step': 6, 'class': 'MARK', 'resolution': 'accepted as workflow risk AR3'},
    ]
elif cmd == 'set':
    k, v = sys.argv[2], sys.argv[3]
    try:
        v = json.loads(v)
    except Exception:
        pass
    if '.' in k:
        a, b = k.split('.')
        s.setdefault(a, {})[b] = v
    else:
        s[k] = v
json.dump(s, open(p, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(json.dumps(s)[:300])
