import json
N = []
Ed = []


def n(i, t, text, claims=None, ev=None, src=None, note=None):
    d = {'id': i, 'type': t, 'text': text}
    if claims:
        d['claims'] = claims
    if ev:
        d['evidence'] = ev
    if src:
        d['sources'] = src
    if note:
        d['audience_note'] = note
    N.append(d)


def e(a, b, t):
    Ed.append({'from': a, 'to': b, 'type': t})


ID = json.load(open('.rcs/_ids.json'))
SID = json.load(open('.rcs/_src_ids.json'))
n('N01', 'PROBLEM', 'Agents that act through software are hard to build and evaluate.', ['C001', 'C002'])
n('N02', 'SIGNIFICANCE', "The authors regard software as the ideal interface for agents to act on the world, and want general agents that also browse and handle auxiliary tasks.", ['C001', 'C003'])
n('N03', 'KNOWN', 'Existing open frameworks provide interfaces, environments and interaction mechanisms; general frameworks and software-engineering systems are characterized by the authors.', ['C004', 'C005', 'C006', 'C007'], src=[SID['hong'], SID['wu'], SID['chen24'], SID['yang'], SID['zhang24b'], SID['crewai']], note='reader may not know these frameworks')
n('N04', 'GAP', 'As the authors describe them, general frameworks offer limited or stateless code execution and software-engineering systems are domain-specific; no single platform is described that combines shell, Python, browser, shared tools, delegation and a benchmark harness.', ['C005'], src=[SID['wu'], SID['crewai'], SID['zhang24b'], SID['yang']])
n('N05', 'RQ', 'Design question: what infrastructure lets one open platform host community-built agents that act through code, shell and browser, run in isolation and be evaluated on many benchmarks?', ['C003'])
n('N06', 'RQ', 'Evaluation question: how does a default generalist agent (and a browsing agent and a GPTSwarm agent) fare across software, web and assistance benchmarks without benchmark-specific prompt engineering?', ['C003', 'C026'])
n('N07', 'OBJECTIVE', "The authors' goal is general digital agents that interact with the world through software interfaces.", ['C003'])
n('N08', 'APPROACH', 'OpenHands: event stream, sandboxed runtime, AgentSkills, delegation, AgentHub and an evaluation harness for 15 benchmarks.', ['C010', 'C011', 'C015', 'C017', 'C019', 'C024'])
n('N09', 'DESIGN', 'Architecture and its stated rationale: three action types, per-session Docker sandbox, arbitrary images, skills library with inclusion criteria, delegation, micro agents, integration tests.', ['C010', 'C011', 'C012', 'C013', 'C014', 'C015', 'C016', 'C017', 'C018', 'C019', 'C020', 'C021', 'C022', 'C023'])
n('N10', 'RESULT', 'Delivered platform: agent abstraction and runtime, skills, hub with over 10 agents, 15 integrated benchmarks, reported community activity.', ['C019', 'C024', 'C029'], ev=[ID['m_hub'], ID['m_bench15'], ID['m_community']])
n('N11', 'DESIGN', 'Evaluation protocol: open-source reproducible baselines without benchmark-specific prompt engineering, no hint text, Lite subset for cost, benchmark-specific adaptations.', ['C025', 'C026', 'C028'])
n('N12', 'RESULT', 'Software benchmarks: SWE-bench Lite 26.0/22.0/7.0, HumanEvalFix 79.3/20.1, and other software benchmarks (soft).', ['C030', 'C032', 'C033'], ev=[ID['r_swe_oh'], ID['r_hef'], ID['r_sw_other']])
n('N13', 'RESULT', 'Web benchmarks: WebArena up to 15.5, MiniWoB++ up to 40.8.', ['C034', 'C035'], ev=[ID['r_wa'], ID['r_mw']])
n('N14', 'RESULT', 'Miscellaneous benchmarks: GAIA 32.1, GPQA diamond 52.0, AgentBench OS 57.6, MINT, ProofWriter, Entity Deduction Arena.', ['C037', 'C038', 'C039'], ev=[ID['r_gaia'], ID['r_gpqa'], ID['r_ab'], ID['r_mint'], ID['r_pw'], ID['r_eda']])
n('N15', 'OBSERVATION', 'Negative pattern: strong dependence on the underlying model, and several rows below the best listed reference.', ['C040', 'C041'], ev=[ID['r_sw_weak'], ID['r_hef_neg'], ID['r_swe_neg'], ID['r_web_neg'], ID['r_misc_neg']])
n('N16', 'INTERPRETATION', 'The authors describe the architecture as providing the shared infrastructure the design question asks for; the paper reports no ablation isolating any component.', ['C010', 'C011', 'C012', 'C019', 'C024'])
n('N17', 'INTERPRETATION', 'The authors describe the unmodified generalist agent as competitive across three categories but not top in every one; the numbers fit competitive and not consistently leading.', ['C031', 'C036', 'C042'])
n('N18', 'CONTRIBUTION', 'An open platform combining a sandboxed multi-tool runtime, shared skills, delegation and an agent hub, released under an MIT license.', ['C010', 'C011', 'C019', 'C029'])
n('N19', 'CONTRIBUTION', 'An evaluation of default agents on 15 benchmarks, with numbers placed beside reference systems, including rows where OpenHands is lower.', ['C024', 'C030', 'C032', 'C041', 'C042'])
n('N20', 'LIMITATION', 'Author-stated limits: complex tasks, long-file editing, handcrafted workflows, multi-modality, research-artifact reliability, not top everywhere, HumanEvalFix comparison, repository compatibility and sandbox caveats.', ['C042', 'C030', 'C031', 'C015', 'C017', 'C019', 'C027', 'C032', 'C041', 'C045', 'C046', 'C011'])
n('N21', 'LIMITATION', 'Writer-derived caveats: no variance, unmatched references, no ablation, extraction damage, self-reported community numbers, mixed agent versions.', ['C030', 'C032', 'C034', 'C035', 'C037', 'C038', 'C039', 'C041', 'C042', 'C010', 'C011', 'C005', 'C033', 'C029', 'C045', 'C046', 'C036'])
n('N22', 'IMPLICATION', 'The platform can serve as a common base on which agents and benchmarks are compared, and repository READMEs show later extensions (benchmarks repository, Agent Canvas), reported as documentation only.', ['C045', 'C046'])
n('N23', 'FUTURE', 'Principled multi-modality, stronger agents, better long-file editing, Auto Eval & Refine, graph-based workflow generation, 100% on HumanEvalFix.', ['C050'])
n('N24', 'BACKGROUND_CONCEPT', 'Event stream, action, observation, sandbox.', ['C010', 'C011'], note='defined before the architecture is described')
n('N25', 'BACKGROUND_CONCEPT', 'Benchmark success rate; resolve rate, pass rate and success rate differ by benchmark.', ['C025'], note='reader may not know SWE-bench, WebArena, GPQA, 0-shot/1-shot')
e('N01', 'N05', 'motivates'); e('N02', 'N06', 'motivates'); e('N02', 'N05', 'motivates')
e('N03', 'N04', 'establishes'); e('N05', 'N04', 'addresses'); e('N06', 'N04', 'addresses')
e('N07', 'N05', 'operationalizes'); e('N07', 'N06', 'operationalizes')
e('N08', 'N07', 'implements'); e('N09', 'N05', 'tests'); e('N09', 'N10', 'produces')
e('N11', 'N06', 'tests'); e('N11', 'N12', 'produces'); e('N11', 'N13', 'produces'); e('N11', 'N14', 'produces'); e('N11', 'N15', 'produces')
e('N10', 'N16', 'supports'); e('N12', 'N17', 'supports'); e('N13', 'N17', 'supports'); e('N14', 'N17', 'supports'); e('N15', 'N17', 'supports')
e('N16', 'N05', 'answers'); e('N17', 'N06', 'answers')
e('N10', 'N18', 'grounds'); e('N04', 'N18', 'grounds'); e('N12', 'N19', 'grounds'); e('N04', 'N19', 'grounds')
e('N20', 'N17', 'limits'); e('N20', 'N16', 'limits'); e('N21', 'N17', 'limits'); e('N21', 'N19', 'limits')
e('N16', 'N22', 'implies'); e('N17', 'N22', 'implies')
e('N20', 'N23', 'opens'); e('N22', 'N23', 'opens')
e('N09', 'N24', 'requires'); e('N12', 'N25', 'requires'); e('N13', 'N25', 'requires')
chains = [
 {'experiment': 'SWE-bench Lite', 'rq': 'N06', 'hypothesis': 'Not stated by the authors as a hypothesis; the authors describe the result as competitive with other open-source specialists.', 'falsifier': 'Not stated by the authors.', 'design_rationale': 'Lite subset chosen for cost saving; hint text not used (authors).', 'observations': [ID['r_swe_oh'], ID['r_swe_ref']], 'claims': ['C030', 'C031'], 'limitations': ['L001', 'L002', 'L010', 'L011'], 'next': 'Check whether a simpler bug-fixing task shows the same picture (HumanEvalFix).'},
 {'experiment': 'HumanEvalFix', 'rq': 'N06', 'hypothesis': 'Not stated by the authors.', 'falsifier': 'Not stated by the authors.', 'design_rationale': 'Python split, multi-turn self-debug with test feedback, 0-shot (authors).', 'observations': [ID['r_hef'], ID['r_hef_ref'], ID['r_hef_neg']], 'claims': ['C032'], 'limitations': ['L007', 'L010'], 'next': 'Turn from code repair to other software tasks (BIRD, ML-Bench, BioCoder, Gorilla APIBench, ToolQA).'},
 {'experiment': 'Other software benchmarks', 'rq': 'N06', 'hypothesis': 'Not stated by the authors.', 'falsifier': 'Not stated by the authors.', 'design_rationale': 'BioCoder context prompts removed to test context retrieval (authors).', 'observations': [ID['r_sw_other'], ID['r_sw_other_ref']], 'claims': ['C033'], 'limitations': ['L013'], 'next': 'Move from code to web browsing, the second task category.'},
 {'experiment': 'Web browsing', 'rq': 'N06', 'hypothesis': 'Not stated by the authors.', 'falsifier': 'Not stated by the authors.', 'design_rationale': 'A software agent should also browse (authors); WebArena answers made concise for exact-match checking (authors).', 'observations': [ID['r_wa'], ID['r_mw'], ID['r_web_neg']], 'claims': ['C034', 'C035', 'C036'], 'limitations': ['L006', 'L010', 'L011'], 'next': 'Move to miscellaneous assistance benchmarks.'},
 {'experiment': 'Miscellaneous assistance', 'rq': 'N06', 'hypothesis': 'Not stated by the authors.', 'falsifier': 'Not stated by the authors.', 'design_rationale': 'Broad task coverage (authors).', 'observations': [ID['r_gaia'], ID['r_gpqa'], ID['r_ab'], ID['r_mint'], ID['r_pw'], ID['r_eda'], ID['r_misc_neg']], 'claims': ['C037', 'C038', 'C039', 'C040'], 'limitations': ['L010', 'L011'], 'next': 'Combine the three categories into the answer to the evaluation question.'},
]
json.dump({'pattern': 'method_first', 'nodes': N, 'edges': Ed, 'experiment_chains': chains}, open('.rcs/story/story_graph.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('ok')
