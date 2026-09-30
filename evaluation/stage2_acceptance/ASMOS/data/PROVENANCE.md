# Provenance

Source repository: `C:/Users/csdee/PESU/CDSAML/ASMOS` (read-only; not modified).
Run: four-system keyed comparison, openai/gpt-4o-mini, n = 24 RULER QA questions (per ASMOS `results/summary.md`).
`System D` = `system_d.json` (canonical per ASMOS `results/summary.md`; `asmos_rag.json` is a pointer to it).

| Original file | What was taken | SHA-256 of original |
|---|---|---|
| `results/no_memory.json` | `aggregate` block only | sha256:22688db30139a2bd7fade5143474ecad3fe711ca6181e6b9d7f0380c2a6c797e |
| `results/rag.json` | `aggregate` block only | sha256:fe8ce353f386f4e5683541b4fa63daba9684567c9e878895a4f56ee3f47547ae |
| `results/asmos.json` | `aggregate` block only | sha256:b39139b194a24f1871663bfd97cab5f755871ec5463959d0248aeec95fe88afc |
| `results/system_d.json` | `aggregate` block only | sha256:8fe3fae5a982f704e51a6e930baf81df9b1a533b6a3e5093022b808b6500117b |
| `results/summary.csv` | copied verbatim (aggregates only) | sha256:c117fe07f292a4ce83957896f422688c09afa3ae121911ed5fd40db494def730 |
| `results/statistics.md` | copied verbatim | sha256:44e2ee60c8fffdecc3359774eeb40f2df15806438179e0abec618885ed02386b |

Per-query questions/answers were deliberately NOT copied.
