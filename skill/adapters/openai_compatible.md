# Adapter: generic OpenAI-compatible chat APIs (hosted or self-hosted)

Use this when you orchestrate the roles yourself from a script.

## Pattern
Each role invocation is **one new conversation**:

```
messages = [
  {"role": "system", "content": read("skill/agents/<role>.md")},
  {"role": "user",   "content": task_message + serialized_input_files}
]
```

- **No shared history between roles.** The only shared state is the `.rcs/` files your script
  passes explicitly.
- REVIEW_AGENT gets only the packet files, and nothing else is serialized into its message.
- Use structured-output / JSON mode where the provider supports it, with the schemas in
  `skill/schemas/`. Always re-validate with `tools/validate_artifacts.py`, because JSON mode
  doesn't guarantee schema conformance.
- Tools (file reading, web search) are implemented by your script. CORPUS_AGENT needs a
  search function and a DOI resolver (e.g. the Crossref REST API). If they're unavailable,
  literature mode must stop with `INSUFFICIENT_LITERATURE` rather than generate references.

## Minimal orchestration loop (pseudocode)
```
state = load(".rcs/state.json")
for step in workflow_steps[state.step:]:
    role, inputs, outputs, validator = STEP_TABLE[step]
    result = call_model(role, inputs)            # fresh conversation
    write(outputs, result)
    if not run(validator): repair_or_raise_failure_state(step)
    if gate_after(step) and not gate_passes(step): ask_user(); break
    state.step = step + 1; save(state)
```
