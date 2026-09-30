"""AUTHOR, round v005_1: claim-map and missing-evidence updates driven by the blind review of v005."""
import json
cp = '.rcs/claims/claim_evidence_map.json'
d = json.load(open(cp, encoding='utf-8'))
L = {l['id']: l for l in d['limitations']}
# finding:8 / inference:6 -- say what the authors' multi-agent caveat is (verbatim content of E106), not that it is "withheld"
L['L007']['statement'] = ("The authors state that the routing threshold tau is tuned in-corpus rather than on a held-out split, that grading in "
    "the question-answering ladder is done by an LLM, that the deterministic ownership verification is not LLM-judged, that a "
    "memory-reuse threshold is an untuned placeholder that feeds none of the reported numbers, and that their multi-agent validation "
    "is one seedless run with an imposed partition; that run's result file is not in the package and no result from it is reported "
    "(checkpoint Q-003).")
# inference:3 -- the cited pre-registration and the single-comparison rationale
if 'L026' not in L:
    d['limitations'].append({
        "id": "L026",
        "statement": ("The pre-registration the authors cite for keeping zero differences dropped is not documented by a registry entry, "
                      "date or protocol in the package (their correction record calls the stamped result files the pre-registration "
                      "record), and the signed-rank tests of the other cost runs are reported without multiplicity correction."),
        "origin": "writer_derived",
        "affects_claims": ["C002", "C026", "C028", "C036"],
        "effect_on_interpretation": ("The one-sided test's pre-specification cannot be checked independently, and the 'single comparison' "
                                     "rationale applies to the headline test only."),
        "evidence": ["E026", "E023", "E028", "M018"]
    })
for cid in ("C002", "C026", "C028", "C036"):
    c = next(x for x in d['claims'] if x['id'] == cid)
    c.setdefault('limitations', [])
    if 'L026' not in c['limitations']:
        c['limitations'].append('L026')
open(cp, 'w', encoding='utf-8').write(json.dumps(d, indent=1, ensure_ascii=False) + "\n")

mp = '.rcs/evidence/missing_evidence.json'
m = json.load(open(mp, encoding='utf-8'))
if not any(i['id'] == 'M018' for i in m['items']):
    m['items'].append({
        "id": "M018",
        "kind": "missing_record",
        "description": ("Pre-registration record for the headline signed-rank analysis: effect_size_correction_20260807_78127c8.json and "
                        "CORRECTIONS.md say switching to Pratt 'would change an already pre-registered p-value', and CORRECTIONS.md calls the "
                        "stamped result artifacts 'the pre-registration record'; no registry entry, date or protocol document is in the package. "
                        "Added by AUTHOR after blind review v005_1 (inference:3)."),
        "referenced_in": ["project/data/results/CORRECTIONS.md", "project/data/results/effect_size_correction_20260807_78127c8.json"],
        "severity": "minor",
        "blocks_claims": []
    })
open(mp, 'w', encoding='utf-8').write(json.dumps(m, indent=1, ensure_ascii=False) + "\n")
print("ok")
