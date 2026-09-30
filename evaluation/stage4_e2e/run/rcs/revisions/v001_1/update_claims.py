"""AUTHOR, step 19 (round v001_1): structural revision of the claim map before regenerating prose."""
import json
from pathlib import Path

p = Path(".rcs/claims/claim_evidence_map.json")
m = json.loads(p.read_text(encoding="utf-8"))
C = {c["id"]: c for c in m["claims"]}
L = {l["id"]: l for l in m["limitations"]}

# inference:2 / finding:5 / finding:10 -- the ablation contrasts routing with no routing
c = C["C005"]
c["statement"] = ("With ownership frozen at its prior (A2) the router never routes to a single owner (route@1 0.0), falls back to "
                  "global search and recovers almost none of the saving; because A2 collapses to global search, the ablation "
                  "contrasts routing with no routing. It is consistent with the saving requiring ownership that has moved above "
                  "the routing threshold, but it cannot separate ownership evolution from, for example, a correctly set static ownership.")
c["scope"]["conditions"] = "one ablation (A1 versus A2) in which A2 falls back to global search; within this corpus"
c["confidence_reasons"] = ["A2 collapses to global search, so the contrast is routing versus no routing",
                           "no arm with static but informative ownership",
                           "no test or per-seed gap for A1 versus A2 at n=50",
                           "threshold tuned on the same corpus", "one constructed corpus"]
c.pop("licenses", None)
c["revision_note"] = "v001_1 review (inference:2, finding:5, finding:10): narrowed from 'consistent with ownership evolution producing the saving'."

# inference:7 -- single run, no seeds, query count unstated
c = C["C012"]
c["statement"] = ("In a single stationary-regime run with no seeds and no stated query count (the recorded values are multiples of 1/11), "
                  "ASMOS with the MiniLM-L6-v2 embedder and the classifier both had route@1 1.0, and the recorded answerability was "
                  "0.909 for ASMOS against 0.727 for the classifier, with no test; with the lexical-hash fallback embedder ASMOS "
                  "route@1 was 0.667 against 1.0 for the classifier, so ASMOS was not routing-competitive there.")
c["permitted_verbs"] = ["was", "recorded"]
c["revision_note"] = "v001_1 review (inference:7): 'higher answerability' restated as recorded values of a single run."

# tool change: an author rationale blocked behind a checkpoint is withheld, not required in the draft.
C["C024"]["rationale"] = "motivation"
C["C024"]["notes"] = ("Carries the authors' stated reason for foregrounding cost and answerability (E111); withheld from the draft "
                      "while checkpoint Q-002 is open (lint S1/S2-author-statement-withheld).")
m["claims"] = [x for x in m["claims"] if x["id"] != "C031"]
m.setdefault("removed_claims", []).append({
    "id": "C031", "removed_in": "v002",
    "reason": "Placeholder that existed only to satisfy the old S2 rule; the rationale it pointed to (E111) is carried by C024, "
              "which is BLOCKED behind Q-002 and is now reported by the lint as withheld. The blind review (finding:1) found the "
              "sentence confusing because it named a reason without giving it."})

# new writer-derived claim: embedder mapping (finding:6, inference:10)
m["claims"].append({
    "id": "C039",
    "statement": ("The 10-seed cost result file does not record which embedder was used; the two new-topic runs record "
                  "all-mpnet-base-v2 and bge-m3; the single stationary run records MiniLM-L6-v2 and a lexical-hash fallback; "
                  "the classifier baselines give identical new-topic results under both embedders, and their input features are not recorded."),
    "claim_type": "observed",
    "evidence": ["E001", "E058", "E062", "E059", "E063", "E073", "E072"],
    "confidence": "moderate",
    "confidence_reasons": ["read from the result files' recorded conditions; absence of a field is an observation about the file"],
    "author_confirmation": "pending", "origin": "writer_derived", "basis": "project_file", "status": "NEEDS_REVIEW",
    "limitations": ["L008", "L011"], "permitted_verbs": ["records", "does not record"]})

def lim(i, statement, affects, effect, evidence):
    m["limitations"].append({"id": i, "statement": statement, "origin": "writer_derived", "affects_claims": affects,
                             "effect_on_interpretation": effect, "evidence": evidence})

lim("L021", "The token measure is the LLM usage recorded per query; the result file reports no separate cost for computing "
            "embeddings, updating ownership or producing verification outcomes.",
    ["C001", "C004"], "The saving is a saving in recorded LLM usage per query, not a measured net saving for the whole system.",
    ["E001", "E004"])
lim("L022", "No classifier updated online from the same labels is included; ASMOS and the retrained classifiers each consumed 10 "
            "labels, and ASMOS used the corpus-tuned threshold 0.351493 while the classifiers used 0.5.",
    ["C009", "C010"], "The regret comparison contrasts ASMOS with scheduled retraining, not with a like-for-like online baseline, "
                      "and is not matched on tuning or update access.", ["E058", "E059", "E063"])
lim("L023", "The per-seed results agree closely (per-seed token reduction std 0.07 percentage points), so the recorded seeds are not "
            "independent replications, and the accuracy difference is 1 to 2 of 50 questions per seed.",
    ["C007"], "Even the direction of the accuracy difference rests on few questions under an undocumented grader.", ["E006", "E015"])
lim("L024", "The cost corpus has two agents, and the new-topic runs do not record how many agents take part.",
    ["C001", "C009", "C010", "C032"], "Nothing is measured for larger teams of agents.", ["E002", "E058"])
lim("L025", "Route@1 is recorded as a proportion without its denominator, and the criterion for a seed having routed the new "
            "topic is not recorded.", ["C008", "C009", "C010"],
    "Route@1 values and the 5-of-5 counts cannot be traced to query counts.", ["E017", "E058"])

C["C001"]["limitations"] = sorted(set(C["C001"]["limitations"]) | {"L021", "L024"})
C["C004"]["limitations"] = sorted(set(C["C004"]["limitations"]) | {"L021"})
C["C007"]["limitations"] = sorted(set(C["C007"].get("limitations", [])) | {"L023"})
C["C008"]["limitations"] = sorted(set(C["C008"]["limitations"]) | {"L025"})
for k in ("C009", "C010"):
    C[k]["limitations"] = sorted(set(C[k]["limitations"]) | {"L022", "L024", "L025"})

L["L008"]["effect_on_interpretation"] = ("The counting is exact, but the quantity counted depends on routing and hence on the "
                                        "embedder; the statement concerns an earlier run that is not reported here and does not "
                                        "establish which embedder the pooled seeds 11 to 55 used.")
L["L012"]["effect_on_interpretation"] = ("The size of the accuracy cost of routing cannot be bounded; the cost saving is not a "
                                        "saving at equal accuracy.")
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("claims", len(m["claims"]), "limitations", len(m["limitations"]))
