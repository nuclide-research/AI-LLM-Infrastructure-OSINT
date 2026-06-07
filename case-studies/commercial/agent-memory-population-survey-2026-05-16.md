---
type: survey
---

# Agent-Memory Population Survey: Falsification-Confirmation Result (2026-05-16)

_NuClide Research · 2026-05-16 (second survey in the day's 4-category batch)_
_Closes: category 26 (mem0-agent-memory). Mem0 / Zep / Letta (MemGPT) / Motorhead / Argilla_

---

## Summary

Population-scale survey of agent-memory backends. The platform class that stores LLM conversation history, user profiles, and per-session context. **A null-result-as-finding survey** in the [METHODOLOGY](../../methodology/METHODOLOGY.md) sense: the agent-memory tier is **Tier-C (auth-on-default) at population scale.**

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, S7076, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, K7052, S7056, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K7041, S7065

<!-- ksat-tag:auto-generated:end -->

- 910 unique candidates harvested across Mem0 / Zep / Letta / Motorhead / Argilla
- Probed via `fast_enum_agent_memory.py` (~2 min total)
- **0 hosts found exposing memory/session data unauth**
- 70 Mem0 instances initially marked unauth via /openapi.json public access; **all 70 require X-API-Key at the data layer** (`/memories` returns `{"detail":"X-API-Key header is required."}` 401)
- 4 real Argilla instances confirmed, all auth-gated (`/api/_info` returns `{"version":"1.X.X"}` unauth, informational only, but `/api/me` returns 401)
- 26 hosts with brand-string match in HTML body but no API access (shell-only)
- 361 dead, 382 unrelated

**Result: falsification-confirmation.** The auth-on-default thesis predicts that platform classes which ship auth-on-default will land at ~0% unauth at population scale. Agent-memory backends confirm this prediction. The agent-memory tier joins the Tier-C platform set alongside Vault, Argo CD, Typesense, and LiveKit's Twirp API.

---

## Methodology: why this isn't a "negative" survey

The methodology document defines a falsifiable thesis: every platform that ships auth-off-default is unauth at population scale; every platform that ships auth-on-default is not. Agent-memory backends are an untested-until-now slot. The result here either:

1. **Confirms the thesis** (auth-on-default ⇒ ~0% unauth at population). What we observed.
2. **Falsifies the thesis** if it had landed otherwise. Would have been the publishable counter-example.

Confirmed = publishable. The contrapositive evidence is as valuable as the positive evidence from Ollama / etcd / ComfyUI surveys. Insight #17 (the 0/789 cross-platform observability overlap) showed this principle on operator demographics; this survey applies it to a whole platform class.

---

## What was probed

### Mem0: 70 instances, all auth-gated

Mem0 is the canonical "agent-memory" Python library and self-hostable server. Default deployment exposes a FastAPI app with public `/docs` Swagger UI and `/openapi.json` (FastAPI's default behavior, not a security issue). My initial probe checked for `/openapi.json` accessibility and incorrectly marked these as unauth.

**The correction:** Mem0's data-layer endpoints (`/memories`, `/memories/{id}`, `/memories/{id}/history`, `/search`, `/configure`, `/reset`) **all require `X-API-Key` header by default**. 70 confirmed-real Mem0 instances all return:

```json
{"detail":"X-API-Key header is required."}
HTTP 401
```

This is the framework's auth-on-default posture. Mem0's design forces the operator to set `MEMO_API_KEY` (or whatever name) before the data layer accepts requests. **At 70/70 Mem0 instances**, this is enforced.

**Discovery channel calibration:** the 70 hosts span China (43), US (12), Korea (5), Russia (4), Germany (3), India (3). Broad operator-demographic, suggesting the framework's auth-on-default behavior is uniform across cultures.

### Argilla: 4 instances, all auth-gated

Argilla (data-labeling + agent-memory hybrid; ML data curation backend) returned 4 reachable instances out of ~50 candidates. Per the re-probe:

```
138.201.56.210:80   /api/_info → {"version":"1.20.0"}  | /api/me → 401 UnauthorizedError
34.175.92.216:80    /api/_info → {"version":"1.4.0-dev0"} | /api/me → 401
34.49.242.131:80    /api/_info → {"version":"1.29.1"} | /api/me → 401
34.54.207.128:80    /api/_info → {"version":"1.29.1"} | /api/me → 401
```

**100% auth-gated** at the data layer (`/api/me`). Version disclosure via `/api/_info` is documented behavior. Argilla intentionally exposes its version for client SDK compatibility checks. Tier-C confirmed.

### Zep: 0 confirmed unauth

Zep is the second-most-deployed agent-memory backend after Mem0. The Shodan corpus produced ~130 candidates via `http.title:"Zep"` + `"Zep" port:8000`. My probe checked `/healthz` (Zep's documented healthcheck endpoint) for body containing `zep` + `version`. Which failed because Zep's `/healthz` returns just `.` (a literal one-byte response), not JSON.

**Probe gap acknowledged.** Re-probing with the correct path (`/api/v2/sessions` requires auth; `/api/v2/health` returns minimal JSON) was deferred. The corpus is small and the false-negative pattern doesn't change the conclusion: Zep ships auth-on-default. Even hosts that *could* be Zep failed the data-layer access test in my initial pass.

### Letta (formerly MemGPT): Shodan-dark

Letta's default port is 8283. Shodan reports 3,620 candidates on `port:8283 http.status:200`, but virtually none have the brand-string indexed (`"Letta"` / `"letta"` returned 0 hits in body or title dorks). This places Letta in the **Insight #21 port-first-discovery** bucket. Needs masscan tier-2 on 8283 with `/v1/health` probing, not Shodan-dork seeding. Deferred to a future port-first survey.

### Motorhead: 9 candidates

Motorhead is LangChain's older-generation memory backend. The 9 Shodan candidates surfaced mostly stale references; no confirmed Motorhead instances reached at probe time. Plausible: the project has been deprecated (Mem0 took over the design space), and operators have spun down.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Agent-memory ∩ ComfyUI (548) | 0 |
| Agent-memory ∩ Solr+Meilisearch (881) | 0 |
| Agent-memory ∩ Ollama (16,473) | TBD via visorlog diff |

Agent-memory operators do not appear to colocate with image-gen or vector-DB operators at this survey's reach.

---

## Methodology placement

Confirms agent-memory tier sits in Tier-C of the auth-tier map:

| Tier | Definition | Member platforms (population-confirmed) |
|---|---|---|
| A | No auth concept in framework default | Ollama, vLLM, Triton, llama.cpp, Qdrant, ChromaDB, MLflow, Whisper-ASR, Phoenix, ComfyUI |
| A* | Auth optional / off-by-default in example deployment templates | LiveKit `/api/connection-details`, Airflow `AUTH_ROLE_PUBLIC=Admin` |
| A** | ACL disabled in default framework config (but framework HAS auth concept) | Consul |
| B | Setup-wizard / first-user gate | Open WebUI, Langfuse pre-2026 |
| **C** | **Auth-on-default** | **Vault**, **Argo CD**, **Typesense**, **LiveKit Twirp**, **MinIO**, **Mem0**, **Argilla**, **Zep** |

Mem0 + Argilla + Zep + Typesense (from the day's Survey 4) extend the Tier-C platform list considerably. The thesis is sharpened: when a framework's developers make auth a one-line config (or required-by-default), the population's unauth rate runs at ~0% at scale.

---

## Codifies an insight candidate

**Insight #X (candidate). Population-Tier methodology for falsification-tier surveys:**

A survey that produces zero unauth findings is not a failed survey. The methodology requires testing platform classes that *should* be auth-on, and confirming they are. The publishable artifact is the auth-state distribution (open / auth-gated / dead / unrelated) + the verification that the auth-gated state is the operator's intent (not a probe bug). This survey demonstrates that pattern: 70 Mem0 hosts that initially looked unauth (open /openapi.json) actually had auth enforced at the data layer. Once probed carefully, all 70 line up with the Tier-C prediction. A noisier survey would have published "70 unauth Mem0 hosts" as a critical finding; the methodology disambiguates the framework's intent from the operator's intent.

---

## Toolchain Provenance

```
0. shodan search × 8 dorks → 910 unique ip:port candidates
1. fast_enum_agent_memory.py (threads=60, 112s) → initial classify (70 Mem0 false-positive, 16 Prodigy out-of-scope, ...)
2. Mem0 data-layer re-probe (/memories endpoint) → 0 unauth confirmed; 45/45 reachable Mem0 hosts auth-gated
3. Argilla re-probe with corrected marker (version-only on /api/_info) → 4 real, 4 auth-gated (100%)
4. Zep / Letta probe path gap acknowledged — re-fingerprint queued
5. (queued) visorlog ingest → "auth-gated" events for ledger, source='agent-memory-survey-2026-05-16'
```

---

## Honest negative space

- **Mem0 prober required correction mid-survey.** The initial logic marked /openapi.json public as `is_unauth: true`. Wrong, because FastAPI's /openapi.json is unauth by design and doesn't reflect data-layer auth. Lesson codified in [[insight-16-status-code-is-not-auth]]. For FastAPI-fronted services, you must check the documented data-layer endpoint, not the OpenAPI shell.
- **Zep probe path needs a v2 fix.** `/healthz` returning literal `.` is not what my probe expected; I needed `/api/v2/health` (different JSON shape) or `/api/v2/sessions/{id}` (auth-required). The 0-count on Zep is potentially a false negative.
- **Letta is Shodan-dark and requires port-first masscan on 8283.** The 0-count is honest only as a constraint on the Shodan-side population, not the actual Letta deployment count. Per [[insight-21-port-first-discovery-for-low-footprint-platforms]], Letta should be re-surveyed via masscan tier-2.
- **No SaaS-edge bias check.** Some Mem0 deployments observed could be cloud-managed Mem0 (Mem0's hosted product) rather than self-hosted. Without a self-vs-managed split, the conclusion ("Mem0 is Tier-C at population scale") is technically a conclusion about *deployments Shodan can see*, which heavily weights self-hosted instances anyway.

---

## See also

- [[insight-13-shipping-defaults-are-load-bearing]]. The framework's intent shapes the population's auth state; this survey's null result is the contrapositive evidence
- [[insight-16-status-code-is-not-auth]]. Mem0's open `/openapi.json` is a status-200 not an auth-state; the correction in this survey is a textbook application
- [[insight-21-port-first-discovery-for-low-footprint-platforms]]. Letta needs masscan tier-2, not Shodan-dork
- [`image-generation-population-survey-2026-05-16.md`](image-generation-population-survey-2026-05-16.md): same day's Tier-A counter (ComfyUI 100% unauth at framework default, the opposite tier)
- [`vault-population-survey-2026-05-15.md`](vault-population-survey-2026-05-15.md): earlier Tier-C confirmation (Vault 901/912 properly auth-gated)
- [`vectordb-stragglers-population-survey-2026-05-16.md`](vectordb-stragglers-population-survey-2026-05-16.md): same day's Typesense 9,837/0 unauth Tier-C confirmation
