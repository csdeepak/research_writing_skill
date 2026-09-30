# Model-agnostic runtime: live results (2026-09-30, D-31)

**Question.** Does the skill's blind reviewer work on models other than Claude when it runs through the skill's own
tools (`tools/rce_llm.py` + `tools/rce_roles.py`), with no Claude-specific code?

**Test.** `python tools/rce_roles.py calibrate` on the skill's planted-defect benchmark (`skill/tests/perturbations/`):
- 7 synthetic papers: 1 clean and 6 with a known defect;
- blinded, with a fresh random packet id per paper;
- the same `review_agent.md`, schemas and scoring for every model.

The pass bar is the one `review_agent.md` sets: dimension sensitivity ≥ 0.90 and false alarms on the clean paper
≤ 0.10. Only synthetic benchmark papers were sent to the hosted endpoint (OpenRouter), and each config listed only
`openrouter.ai` in `data_policy.allowed_hosts`.

| Reviewer model | Family | Route | Sensitivity | False alarms | Verdict | Valid first time | Repairs |
|---|---|---|---|---|---|---|---|
| Claude Opus (reference) | Anthropic | subagent task folder | 0.933 | 0.05 | calibrated | 7/7 | none |
| `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA | `rce_roles` → OpenAI-compatible API | **0.945** | **0.00** | **calibrated** | 2/7 | 15 calls for 7 reviews; 32 over-long quotes shortened |
| `qwen/qwen3.8-27b` (open weights, 27B) | Alibaba Qwen | `rce_roles` → OpenAI-compatible API | **0.911** | **0.00** | **calibrated** | 6/7 | 8 calls for 7 reviews |
| `google/gemma-4-31b-it` | Google | `rce_roles` → OpenAI-compatible API | not measured | | | | the free pool stayed rate-limited (HTTP 429) through 5 minutes of backoff; a provider limit, not a tool failure |

Misses:
- **Nemotron:** jargon paper, method (0.667).
- **Qwen:** jargon paper, method; poor-ordering paper, contribution.

## What the live runs changed in the tools
Each of these fixes has a regression test.

1. **Rate limits crashed the run.** Transient failures (429, 5xx, timeouts, overloads) are now retried with backoff and
   kept separate from JSON repair attempts (T-058). The calibration also resumes per paper.
2. **Truncated JSON.** Nemotron dropped its final `}` on every reply. `extract_json` now completes only the missing
   closing brackets, never content, and schema validation still decides (T-054).
3. **Over-long quotes.** Nemotron quoted whole sentences where the schema allows 20 words, even after four rounds of
   error feedback. A narrow normalisation now shortens location quotes to 19 words plus "…". It never touches scores,
   findings or answers, and the count is reported per review (T-062).

## Reading
- The deterministic gates (validator, lint, number tracing, visuals, G4) never depended on a model.
- These runs show the judgement role also transfers. Two non-Claude families, one of them a 27B open-weight model,
  meet the same calibration bar as Claude on the same benchmark.
- Weaker instruction-following shows up as more repair calls, not as worse reviews. That is why the tool validates
  and repairs instead of trusting output.
- **Caveats:**
  - one seed per model;
  - 7 benchmark papers;
  - free-tier endpoints.
- Calibrating a model once does not guarantee every later review is good. The skill still gates on the review's
  schema and G4 dispositions, and calibration should be re-run when the model or `review_agent.md` changes.

Files:
- configs: `<model>/.rcs/models.json`;
- content-free call logs: `<model>/.rcs/audits/llm_calls.jsonl`;
- results: `<model>/.rcs/audits/reviewer_calibration.json`;
- local transcripts: `<model>/.rcs/llm/`.
