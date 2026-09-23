# Adapter: local / open-weight models (Ollama, llama.cpp, vLLM, LM Studio, …)

Most local servers expose an OpenAI-compatible endpoint, so use `openai_compatible.md` with
`base_url` pointed at the local server.

## Adjustments for smaller models
1. **Chunk the work.** Run CORPUS_AGENT per file or per directory. Merge with a deterministic
   script, not with the model.
2. **Tighten output formats.** Use grammar- or JSON-constrained decoding if the server supports
   it, with the schemas in `skill/schemas/`.
3. **Push checks into tools.** Rely more on `validate_artifacts.py` and `lint_draft.py`, and on
   scripted numeric fidelity checks (compare every number in the draft against
   `research_evidence.json`).
4. **Keep REVIEW_AGENT strong.** If only one strong model is available, use it for REVIEW_AGENT.
   A weak reviewer caps the whole loop. Run the calibration on `tests/perturbations/` first. If
   the local reviewer fails calibration (<90% sensitivity), label its reviews `exploratory`.
5. **Literature needs retrieval.** Without web or index access, literature mode stops with
   `INSUFFICIENT_LITERATURE`, and the user supplies the sources (as PDFs or a BibTeX file with
   DOIs to verify).

## Data policy
Local models are the default choice for confidential Level-0 data. If some roles run on hosted
APIs, set `data_policy.allowed_endpoints` in `.rcs/config.yaml`, and send only packets
(the paper text) to hosted reviewers, never raw project files.
