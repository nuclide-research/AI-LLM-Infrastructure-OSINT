---
type: pre-assessment-intelligence
category: cat-tabby
slug: cat-tabby-stragglers
date: 2026-06-09
researcher: nuclide
stage: -1
status: complete
---

# Cat-Tabby — Code-Assistant Stragglers — Stage -1 Master OSINT

_NuClide Research · 2026-06-09 · Stage -1 pre-assessment platform intelligence_

Four parallel research squads ran the methodology §2 Stage -1 brief in parallel — one per platform. This doc synthesizes them into the master intelligence brief that drives Stage 0 dork selection, Stage 0d fingerprint scaffolding, and Stage 3v verification primitive choice.

Per-squad source briefs:

- `cat-tabby-tabby-osint-2026-06-09.md`
- `cat-tabby-continue-osint-2026-06-09.md`
- `cat-tabby-sourcegraph-cody-osint-2026-06-09.md`
- `cat-tabby-devstral-osint-2026-06-09.md`

## DCWF role-agent lane assignment (active this session)

| Lane | Role | Stages | Stance |
|---|---|---|---|
| A | NICE 541 Pentester | -1 → 0 → 0b → 0c → 1c | T0028 / S0051 / K0342 / S0001 |
| B | DCWF 623 AI/ML Specialist | 0d → 1a → 1b → 1cm → 1d | tool-building, FP-class identification |
| C | DCWF 672 AI T&E Specialist | 2 → 2b → 3v → 4 → 8 | marker-anchored verification, 200-with-data discipline |
| D | DCWF 733 AI Risk/Ethics Specialist | 3 → 6 → 7 → 9 → 10 → 11 → 12 → 12b → 13 | restraint enforcement, jurisdiction-aware disclosure |

Wardrobe outfit: `ai-infra-hunt` (13 atoms). Syllabus context anchoring restraint posture: Les Dissonances (NDSS — cross-tool harvesting in pool-of-tools LLM agents), ObliInjection (NDSS — multi-source prompt injection). The papers license the rule that drives Lane D this session: code-completion endpoints (`/v1/completions`, `/.api/completions/stream`, `/api/generate`) are the exploit primitive these papers describe; enumeration via model-list endpoints (`/v1beta/models`, `/api/tags`, `/.api/graphql site.productVersion`) is the legal-equivalent.

## Platform coverage matrix

| # | Platform | Scope verdict | Population estimate | Default auth | Fingerprint state |
|---|---|---|---|---|---|
| 1 | **Tabby** (TabbyML) | Server platform, in scope | 150–600 live :8080 | **Version-load-bearing** (pre-v0.11.0 open-API; v0.11.0+ JWT+admin-create; 3 endpoints unauth in all builds) | No aimap FP, no nuclei templates — scaffold from `tome probe tabby` |
| 2 | **Continue.dev** | **CLI/extension-only — out of scope** | 0 Continue-branded hosts | n/a (no server) | None needed |
| 3 | **Sourcegraph + Cody** | Server platform, in scope | 500–2,000 strict on `/.api/graphql`+title | Tier-C auth-on-default; `auth.public:false` default; **first-admin-wins race on fresh boot** | No aimap FP, no nuclei templates — scaffold |
| 4 | **Devstral** | **Model, not server** — fingerprint-via-serving-stack | 150–300 Devstral-loaded hosts (1–2% of 16,473 Ollamas + vLLM/llama.cpp share) | Inherited from serving stack (Ollama/vLLM/llama.cpp all no-auth-default) | aimap deep-enum extension to existing Ollama + vLLM enumerators (emit `loaded_model_family=devstral`) |

## Stage 0 Shodan harvest plan

Two platforms feed Stage 0 Shodan: **Tabby** and **Sourcegraph+Cody**. Continue.dev is skipped (CLI-only confirmed). Devstral is deferred to Stage 1 (deep-enum on existing Ollama/vLLM corpus from prior surveys).

| Platform | Tier | Dork | FP risk |
|---|---|---|---|
| Tabby | basic | `port:8080 "Tabby"` | High — bare token, Insight #15 ~50% rule; "tabby" = cat name + Eugeny terminal product |
| Tabby | strict | `port:8080 http.html:"Tabby" http.html:"AI coding"` | Low — dual-marker conjunctive |
| Tabby | version | `port:8080 http.html:"Tabby" http.html:"swagger-ui"` | Low — pulls hosts exposing the OpenAPI spec |
| Sourcegraph+Cody | basic | `http.title:"Sourcegraph"` | Medium — Insight #7 substring-FP risk on `http.title:` |
| Sourcegraph+Cody | strict | `http.html:"/.api/graphql" http.title:"Sourcegraph"` | Low — body anchor + title conjunctive |
| Sourcegraph+Cody | version | `http.html:"productVersion" http.html:"/.assets/scripts/"` | Low — version-disclosing pattern |

Both populations run strict-tier first (validates the count), then basic-tier for the ~50%-rule delta exercise. Versioned harvest catches the CVE-scoping cohort.

## Stage 0c scanner (active-banner) priorities

The scanner step is **standing and non-skippable** after every Shodan/Censys harvest (Insight #77 active-banner prefilter). For Cat-Tabby:

- Tabby identity: `GET /v1/health` returns the unique HealthState JSON shape `{"model":..., "chat_model":..., "device":..., "webserver":...}` — high-confidence-low-FP identity. This is the **marker probe** the methodology requires (Insight #6 conjunctive marker-anchored matchers).
- Sourcegraph identity: `GET /.api/graphql` schema introspection enabled by default (Sourcegraph treats it as a "debug API"). Pure metadata leak — restraint-clean. The single safe verify-rung probe: `POST {"query":"{ site { productVersion } }"}` returns semver unauth on most installs.

Shadow ports (Insight #12 IP-direct-shadow): per Devstral cat-coherence finding, when an exposed Ollama on 11434 advertises `devstral` on a /32, Tabby/OpenHands on the same host (ports 8080, 3000) is a strong predictor — prioritize `11434, 8000, 8080, 3000, 4000` on every confirmed Tabby/Cody host. Standard NuClide IP-direct shadow set (5432, 6379, 9000, 9090, 3000, 5601, 8025) still applies.

## Stage 0d aimap fingerprint debt

Both Tabby and Sourcegraph need fresh aimap fingerprints scaffolded from their tome probe configs. Reference: existing `enumOllama` / `enumVLLM` style — read the tome JSON, write `aimap/fingerprints/tabby.json` and `aimap/fingerprints/sourcegraph-cody.json`, plus deep enumerators (`enumTabby`, `enumSourcegraph`) that emit the auth-state classification per host.

For Devstral: extend `enumOllama` and `enumVLLM` to parse the model-list response and tag any host with `Devstral`/`devstral`/`Devstral-Small`/`Devstral-21B`/`Devstral-2` in a model id as `loaded_model_family=devstral`. No new fingerprint, just an enumerator extension.

## Lane D restraint rules (carried by the rest of the survey)

Two ethical-stop boundary moves established during Stage -1 that govern Stages 1b through 12:

1. **Tabby `POST /` admin-create on first-visit = host takeover.** Equivalent severity class to MCP `tools/call`. The *unclaimed-admin state* IS the finding; the POST is not exercised against any survey-set host. Reading `/v1beta/server_setting` (or the equivalent admin-setup-status indicator) is enumerate-equivalent.
2. **Tabby + Sourcegraph completion endpoints are compute-exfil primitives.** `POST /v1/completions`, `POST /v1/chat/completions`, `POST /.api/completions/stream`, `POST /.api/cody/context`, `POST /.api/sg/embeddings`, `POST /.api/llm/v1/chat/completions` — none get called against the survey set. Model id from `/v1beta/models` or `/.api/graphql site.codyLLMConfiguration` is sufficient to confirm severity; the completion itself stays gated.

GraphQL mutation requests are state-changing — all GraphQL traffic restricted to introspection + the `{ site { productVersion } }` read-only query.

## CVE / prior-research baseline

| Platform | Published CVEs | NuClide research-gap finding |
|---|---|---|
| Tabby | **0** CVEs, **0** GHSAs on TabbyML/tabby | No aimap FP, no nuclei templates, no prior public Shodan/Censys census. Greenfield. **Do not cross-attribute Eugeny/tabby terminal CVEs (CVE-2024-55950, CVE-2024-48460) — different product.** |
| Continue.dev | CVE-2026-8770 (lsTool path traversal, local AV) | CLI-only verdict means a Continue JSON-RPC channel ever reachable across the network is itself the finding (CVE-2026-8770 becomes remotely exploitable). |
| Sourcegraph + Cody | CVE-2022-23642 + scattered. **2023-08 admin-token leak → LLM-billing-theft chain** is the canonical Cody-era class. No CVE issued, but the impact class (leaked-admin → free LLM proxy off victim's billing) is the unauth-on-misconfig hunt for Stage 3v. | The `auth.public:true` cohort + first-admin-race-window cohort have no prior public census. |
| Devstral | CVEs inherited from serving stack (Ollama CVE-2024-37032 / 39719–22, vLLM CVEs, llama.cpp CVEs). | No prior NuClide-style population survey of *which model families* are loaded across exposed Ollama/vLLM. Devstral is the clean test case (unique vendor string, stable id). |

## Insight candidates surfaced at Stage -1

1. **Candidate Insight (continue.dev squad):** Client-side-only platforms produce server-side findings via upstream-gateway exposure. The platform-class survey for a CLI-only product is a redirection survey — the brand is the lookup key for the *upstream gateway population* the operator is fronting.
2. **Candidate Insight (devstral squad):** Model-fingerprint deep-enum over serving-stack identity fingerprints is a separate axis from server-fingerprint identity. Cat-NIM / Cat-53 / Cat-Tabby (this survey) share the pattern. The thesis can be sharpened: auth-on-default failures concentrate at the *serving-stack* layer, but the *model-fingerprint* layer is the operator-attribution + impact-class differentiator.
3. **Candidate Insight (tabby squad):** A platform with auth-on-default *for the main path* and three auth-off-by-design endpoints (health, model-list, server_setting) creates a hybrid Tier-A*/C surface that escapes the existing tier vocabulary. Worth a separate insight if Stage 3v confirms population behaves accordingly.

## Toolchain provenance

Wardrobe outfit: `ai-infra-hunt` (T0028 / S0051 / K0342 / S0001 / T0188 / T0247 / K0107 / K0118).
Syllabus context: Les Dissonances (USENIX/NDSS), ObliInjection (NDSS) — informed the do-not-call endpoint scoping for code-completion surfaces.
Squads dispatched via Agent tool with `general-purpose` subagent type — parallel research lanes per methodology §2 Stage -1 (intelligence-at-input principle).
Tome corpus writes: `~/tome/platforms/{tabby,continue-dev,sourcegraph-cody,devstral}.json` (all status `CANDIDATE` until Stage 3v promotes them to `CONFIRMED` per the §7 codify discipline).
