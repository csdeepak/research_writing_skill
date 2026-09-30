import json
prof = {
    "mode": "B",
    "primary": "Machine-learning researchers from other subfields (adjacent researchers) who know general ML, deep learning, standard evaluation practice and statistics",
    "secondary": "Reviewers and replicators checking that numbers and rules match the project's paper",
    "tertiary": "Later readers and practitioners looking for what MLPerf Tiny v0.5 specifies",
    "assumed_known": ["supervised learning", "train/test split", "top-1 accuracy", "AUC-ROC", "CNN and residual networks", "autoencoder", "quantization as a general idea", "benchmark and leaderboard practice", "median and repeated runs"],
    "not_assumed": ["microcontrollers and DSPs", "TinyML", "TFLM", "post-training quantization versus quantization-aware training in embedded toolchains", "keyword spotting and visual wake words tasks", "DCASE, ToyADMOS, MIMII", "EEMBC, CoreMark, MLMark", "energy monitors and device-under-test setups", "RISC-V, FPGA, hls4ml"],
    "binding_personas": ["B"],
    "term_budget": {"per_paragraph": 2, "abstract_acronyms": 1},
    "source": "task statement of this run (audience given; no human available)"
}
json.dump(prof, open(".rcs/plan/audience_profile.json", "w", encoding="utf-8"), indent=2)

reader = {"personas": [{
    "id": "B",
    "description": "Adjacent-field ML researcher: knows general ML, deep learning, standard evaluation and statistics; not TinyML terms, datasets or prior work.",
    "binding": True,
    "known_terms": ["ML", "CNN", "ResNet", "MobileNet", "autoencoder", "top-1", "AUC", "ROC", "accuracy", "benchmark", "quantization", "fp32", "dataset", "test set", "median", "batch normalization", "ReLU", "FC", "MSE", "GPU", "API", "seed", "leaderboard"],
    "prerequisite_concepts": [
        {"concept": "closed division", "needs": ["reference implementation"]},
        {"concept": "micro-Joules per inference", "needs": ["device under test"]},
        {"concept": "post-training quantization", "needs": ["quantization"]}],
    "likely_misconceptions": [
        {"misconception": "MLPerf Tiny is a leaderboard of new models by accuracy",
         "trigger_terms": ["leaderboard"],
         "corrective_point": "The closed division fixes models, datasets and quality targets so that stacks, not models, are compared.",
         "corrective_terms": ["closed division", "same models"]}],
    "reader_questions": ["What problem does this solve, and why can existing benchmarks not solve it?", "What exactly is measured, and how?", "How were the quality targets chosen and how big are the margins?", "What did the first submission round show and what did it not show?", "What does the benchmark not capture?"],
    "venue_expectations": ["Generic research article: abstract, introduction, related work, method, results, discussion, limitations, conclusion"],
    "new_term_budget": 2}]}
json.dump(reader, open(".rcs/plan/reader_model.json", "w", encoding="utf-8"), indent=2)

open(".rcs/plan/venue_profile.yaml", "w", encoding="utf-8").write("""# Generic fallback profile (VENUE_UNKNOWN). No venue was given; every rule is assumed.
venue: {name: "generic research article", type: journal, guideline_urls: []}
structure:
  section_template: [Title, Abstract, Introduction, Related Work, Benchmark design and measurement method, Results, Discussion, Limitations, Conclusion, References]
  results_discussion: separate
  related_work_position: after_intro
  limitations_section_required: true
  assumed: true
limits: {pages_main: null, words_main: 4500, abstract_words: 250, supplement_allowed: true, assumed: true}
style:
  citation_style: "(FirstAuthor et al., Year)"
  voice_preference: "active voice; 'we' for the presenter of the authors' work is avoided: the authors are 'the authors'"
  spelling: US
  abstract_format: unstructured
  abstract_citations_allowed: false
  assumed: true
required_statements:
  data_availability: true
  code_availability: true
  ai_use_disclosure: "assumed; see disclosure.md"
  assumed: true
checklists: []
reporting_guideline: null
""")
