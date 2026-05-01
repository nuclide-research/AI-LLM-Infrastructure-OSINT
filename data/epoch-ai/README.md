# Epoch AI Model Database (snapshot)

CSV snapshot of Epoch AI's notable / all-models database, maintained for cross-reference during OSINT sweeps. Source: <https://epoch.ai/data/notable-ai-models>.

## Files

| File | Rows | Use |
|------|------|-----|
| `notable_ai_models.csv` | ~8,257 | Curated notable models (frontier + significant-use) |
| `all_ai_models.csv` | ~23,807 | Full database including unreleased, low-citation, regional |

## Why This Lives in the Repo

When `aimap` / `recongraph` / a manual probe finds a model on an exposed Ollama / vLLM / Triton endpoint, we cross-reference the model name against this database to:

1. **Verify parameter counts** — Ollama tags like `:236b` / `:744b` are convention-rounded; the CSV gives the actual figures (e.g. DeepSeek-Coder-V2 236b → 236B exact, GLM-5 744b → 744B exact, qwen3.5:122b → 122B total / 10B active).
2. **Identify frontier exposure** — instantly flag whether an exposed weight set is on Epoch's "Discretionary" / frontier list.
3. **Generate niche banner-search needles** — recent low-citation open-weight models are useful as Shodan/HTTP banner search strings (e.g. `Ling-1T`, `LongCat-Flash`, `AgentFounder-30B`, `Tongyi DeepResearch`).
4. **Country-of-origin attribution** — when an exposed instance hosts e.g. a Chinese-origin frontier model, that's signal beyond the host's own geolocation.

## Tooling

Use `tools/epoch_lookup.py`:

```bash
# Fuzzy lookup
./tools/epoch_lookup.py "GLM-5"
./tools/epoch_lookup.py "qwen3-coder"

# Filter
./tools/epoch_lookup.py filter --country China --since 2026-01
./tools/epoch_lookup.py filter --org "DeepSeek"

# Niche banner-search needles
./tools/epoch_lookup.py niche

# Frontier / discretion-flag
./tools/epoch_lookup.py frontier
```

## Refresh Cadence

Refresh the CSVs from Epoch periodically; field schema is stable. Note download date in the commit when refreshing.

Current snapshot: **2026-05-01**.
