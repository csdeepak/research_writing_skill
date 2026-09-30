# Adapter: local / open-weight models (Ollama, llama.cpp, vLLM, LM Studio, …)

Most local servers expose an OpenAI-compatible endpoint. The default `templates/models.json` already points every
single-shot role at `http://localhost:11434/v1` (Ollama); change `base_url` for vLLM, LM Studio or llama.cpp. A model
without a server works through the `command` provider (e.g. `"command": ["ollama", "run", "<model>"]`).
Local endpoints are always allowed by the data policy; nothing leaves the machine.

## Adjustments for smaller models
1. **Chunk the work.** Run CORPUS_AGENT per file or per directory. Merge with a deterministic
   script, not with the model.
2. **Tighten output formats.** Use grammar- or JSON-constrained decoding if the server supports
   it, with the schemas in `skill/schemas/`.
3. **Push checks into tools.** Rely more on `validate_artifacts.py` and `lint_draft.py`, and on
   scripted numeric fidelity checks (compare every number in the draft against
   `research_evidence.json`).
4. **Keep REVIEW_AGENT strong.** If only one strong model is available, use it for REVIEW_AGENT.
   A weak reviewer caps the whole loop. Run `python tools/rce_roles.py calibrate --rcs .rcs` first.
   It fails below 90% sensitivity or above 10% false alarms, and its reviews are then labelled uncalibrated in
   `reviewer_log.json`: treat them as `exploratory`.
5. **Literature needs retrieval.** Without web or index access, literature mode stops with
   `INSUFFICIENT_LITERATURE`, and the user supplies the sources (as PDFs or a BibTeX file with
   DOIs to verify).

## Data policy
Local models are the default choice for confidential Level-0 data. If some roles run on hosted
APIs, list their hosts in `data_policy.allowed_hosts` in `.rcs/models.json` (the tool refuses
unlisted hosts). The single-shot roles send only packets (the paper text), never raw project files.
