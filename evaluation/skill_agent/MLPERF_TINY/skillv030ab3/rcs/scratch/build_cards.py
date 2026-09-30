import json
D = ".rcs/plan/figure_cards/"
cards = {
    "TAB-1": {"id": "TAB-1", "type": "table", "status": "planned",
              "purpose": "Show the four benchmarks side by side: task, dataset, model, size, quality target.",
              "rq": "RQ1", "takeaway": "The suite pairs four tasks with four small models, each with a quality target between 80% and 90% Top-1 or AUC 0.85.",
              "claims": ["C004"], "evidence": ["E004", "E005", "E006", "E007"], "source_data": ["project/paper.txt"],
              "comparison_the_eye_must_make": "across tasks: input size, model size, target metric",
              "non_conclusions": "Does not show measured latency or energy for the models.",
              "placement": "Section 4.1", "caption": "Table 1. The four benchmarks."},
    "TAB-2": {"id": "TAB-2", "type": "table", "status": "planned",
              "purpose": "Put each reference accuracy next to its quality target.",
              "rq": "RQ1", "takeaway": "Every reference result sits above its target by 0.01 AUC to about 6 accuracy points.",
              "claims": ["C010", "C011", "C012", "C013", "C035"], "evidence": ["E009", "E011", "E014", "E017"], "source_data": ["project/paper.txt"],
              "comparison_the_eye_must_make": "reference value vs target per task",
              "non_conclusions": "No spread reported; the evaluation subsets are small; not a comparison of submissions.",
              "placement": "Section 5.1", "caption": "Table 2. Reference results and quality targets."},
    "TAB-3": {"id": "TAB-3", "type": "table", "status": "planned",
              "purpose": "List the five v0.5 submission rows and what each set out to demonstrate.",
              "rq": "RQ3", "takeaway": "The round mixed four closed-division entries and one open-division entry across MCU, RISC-V, single-board computer, accelerator and FPGA hardware.",
              "claims": ["C015"], "evidence": ["E026"], "source_data": ["project/paper.txt"],
              "comparison_the_eye_must_make": "division, numerics, framework, hardware, demonstrated aim",
              "non_conclusions": "Shows no measured accuracy, latency or energy; modification marks of the original table are illegible and omitted.",
              "placement": "Section 5.3", "caption": "Table 3. The v0.5 submission round."},
    "FIG-5": {"id": "FIG-5", "type": "chart", "status": "blocked",
              "purpose": "Would show latency and energy of the four reference implementations.",
              "rq": "RQ2", "takeaway": "not available",
              "claims": ["C014"], "evidence": ["E025"], "source_data": ["project/figure5_data_not_available.csv"],
              "non_conclusions": "Blocked: the plotted values are not in any project file; nothing is drawn (NO_VALID_VISUAL).",
              "placement": "not placed", "caption": "none"},
}
for k, v in cards.items():
    json.dump(v, open(D + k + ".json", "w", encoding="utf-8"), indent=2)
st = json.load(open(".rcs/state.json", encoding="utf-8"))
st["accepted_risks"] = [
    {"kind": "workflow", "risk": "No human available: wherever the skill asks for author confirmation (G1 spine and claim confirmation), the run proceeds. Claims stated in the authors' own paper are marked confirmed; C035 (writer-computed differences) stays pending."},
    {"kind": "workflow", "risk": "No human available for venue choice: the generic venue profile is used, every rule assumed."},
    {"kind": "workflow", "risk": "V5 (human visual usability review) and any human comprehension study are not performed. No visuals other than three Markdown tables are used."},
    {"kind": "workflow", "risk": "Citations are registered with user_supplied_file and abstract read depth because the sources cannot be read (no web); they are used only to say what the MLPerf Tiny paper states about each work."},
    {"kind": "workflow", "risk": "Step 18 (blind review) is performed externally; G4 and G5 are recorded as not run by this agent."}]
st["step"] = 4
json.dump(st, open(".rcs/state.json", "w", encoding="utf-8"), indent=2)
