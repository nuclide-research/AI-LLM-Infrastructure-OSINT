# herald

**Repository:** https://github.com/nuclide-research/herald
**Status:** v0.1.1 public, MIT licensed.
**Built:** 2026-06-06.

## What it is

Declarative HTTP auth-probe tool for AI/LLM infrastructure surveys. Reads platform YAML configs, sweeps IP lists, outputs NDJSON findings.

## Why it exists (capability gap analysis)

By 2026-06-06 the research program had completed surveys of 7+ AI/LLM infrastructure platforms (Open WebUI, Dify, Flowise, n8n, Streamlit, AnythingLLM, LiteLLM). Each survey was producing a one-off Python probe script that:

1. Iterated `ip:port:scheme` lines
2. Hit 2-3 endpoints per host
3. Parsed JSON field values
4. Classified each host as OPEN / CLOSED / CONFIG_DISC
5. Wrote structured output

The pattern was identical. Only the endpoint paths and field semantics differed. This is exactly the kind of capability gap that the 661 R&D Specialist role exists to close: a recurring manual pattern that should be a tool.

## Design decisions

| Decision | Source |
|---|---|
| **Declarative YAML platform configs** | Domain insight — probe semantics are data, not code |
| **Channel-semaphore concurrency** | "Security with Go" (Packt, 2018), Chapter 10 DirBuster pattern |
| **`http.NewRequest` + `Do` instead of `Get`** | "Powerful Command-Line Applications in Go" (Pragmatic, 2021), Chapter 8 |
| **NDJSON output** | Composability — pipes to `jq`, `wc -l`, `visorlog ingest`, downstream tooling |
| **Dot-path JSON field traversal** | Required for nested configs like Open WebUI `features.auth` |
| **TLS skip verify** | Necessary for self-signed certs at population scale |
| **Body-size cap at 1MB** | Defense against silent slow drops + memory exhaustion (Insight from aimap LLaMA-Factory FP fix) |
| **Custom User-Agent: `herald/0.1.0 (nuclide-research.com)`** | Transparency in probe identification |

## Platforms supported (v0.1.1)

| Platform | Probes | Validated against |
|---|---:|---|
| dify | 3 | 1,600-host Cat-DF survey |
| open-webui | 4 | 5,097-host Cat-OW survey |
| flowise | 1 | 841-host Cat-FW survey |
| langfuse | 2 | 1,140-host Cat-LF survey |
| litellm | 2 | 2,209-host Cat-05 survey |
| anythingllm | 1 | 232-host survey (all closed) |
| ragflow | 2 | 1,905-host Cat-RF survey |
| phoenix | 3 | 89-host Cat-PX survey |

## Change history

### v0.1.1 (2026-06-06)

Fix: `matchValue` numeric type coercion. YAML unmarshals integer constants as `int`, but `encoding/json` unmarshals JSON numbers as `float64`. `reflect.DeepEqual(int(1), float64(1))` returns `false`. Added `toFloat` helper that normalizes `int / int64 / float64 / float32` before equality check.

Add: `platforms/ragflow.yaml` with `register_enabled` and `config_disc` probes.

Add: `platforms/phoenix.yaml` with `projects_unauth`, `users_unauth`, `health_open` probes.

### v0.1.0 (2026-06-06)

Initial public release. 6 platforms. Channel-semaphore concurrency, YAML config schema, NDJSON output, dot-path field traversal, body_contains matching, array probes, field extraction.

## Roadmap

### Known bugs

1. **Array-nonempty extract scoping.** When `array_nonempty: true` matches, `extractFields` is called with the whole response object, not the matched array. Field extracts like `array_count: true` and `array_field` look at the wrong level. Workaround: herald sets `fields["count"]` explicitly. Fix: pass the matched array (not response) into `extractFields` from the array_nonempty branch.

2. **No retry on transient failures.** A single timeout = no finding. For population sweeps where reachability is the primary signal, this is correct. For verification re-probes, a retry config would reduce false negatives.

### v0.2 candidates

- **Output to visorlog directly** (skip the NDJSON-then-ingest step)
- **Concurrent multi-platform probe** (`-platforms a,b,c` runs all platforms against same IP list)
- **Per-probe rate limiting** (politeness budget per ASN / per `/24`)
- **TLS SNI handling** when scheme is `https` (currently bypasses SNI)
- **Status-code-based probes** (some platforms signal auth via status, not body — e.g. AnythingLLM 403 vs 200)
- **GraphQL support** (Phoenix uses GraphQL; current probe is REST-only)
- **Output formatter** for case-study draft generation (skeleton .md per platform from herald output)

### v0.3 candidates

- **Tome integration** — pull probe configs from `tome` platform corpus instead of per-repo YAML
- **OWASP LLM Top 10 (2025) tagging** in finding output (`llm_owasp_class: LLM02`)
- **Source-code verification helper** — given a platform YAML and an upstream Git URL, validate that the probe endpoint paths and field names exist in the source

## Research-program contribution

herald replaces the per-survey Python probe scripts that were eating ~30 minutes of calibration time per platform. The first three surveys using herald (Dify, Langfuse, RAGFlow) collectively swept 4,645 hosts in under 5 minutes wall-clock time across all probes. The per-platform marginal cost of a new survey is now: write a YAML file. That is the capability gap closure.

The platform-cohort hypothesis (Insight #76) became testable because herald made same-day cross-platform surveys cheap.
