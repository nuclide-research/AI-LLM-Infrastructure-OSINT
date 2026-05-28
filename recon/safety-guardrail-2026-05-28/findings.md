# Safety / Guardrail Platform Survey — 2026-05-28

## Harvest Summary

| Dork | Hits | Live | Confirmed |
|------|------|------|-----------|
| `http.html:"LLM Guard API"` | 8 | 2 | 2 LLM Guard v0.0.10 |
| `port:8000 http.html:"llm-guard"` | 3 | 2 | same 2 (overlap) |
| `port:5000 http.html:"/settings" http.html:"scanner"` | 36 | 1 | 0 (all FP — NAS/betting panels) |
| `http.html:"vigil-llm"` | 0 | — | — |
| `port:5000 http.html:"/analyze/prompt"` | 0 | — | — |
| `port:5000 http.html:"prompt_entropy"` | 0 | — | — |
| `http.html:"/v1/rails/configs"` | 0 | — | — |
| `http.html:"nemoguardrails" port:8000` | 0 | — | — |
| `http.html:"/v1/rails/generate"` | 0 | — | — |
| `http.html:"laiyer/llm-guard"` | 0 | — | — |
| `port:3000 http.html:"rebuff.ai"` | 0 | — | — |
| `port:3000 http.html:"/api/detect" http.html:"rebuff"` | 0 | — | — |
| `port:8000 http.html:"guardrailsai.com"` | 0 | — | — |
| `http.html:"hub.guardrailsai.com"` | 0 | — | — |
| `http.html:"Llama-Guard-3"` | 0 | — | — |
| `http.html:"meta-llama/Llama-Guard" port:8000` | 0 | — | — |
| `http.html:"ShieldLM" port:8000` | 0 | — | — |
| `http.html:"Llama-Prompt-Guard" port:8000` | 0 | — | — |
| `http.html:"LlamaFirewall"` | 0 | — | — |

**Total confirmed instances: 2 (both LLM Guard)**

---

## Confirmed Findings

### F1 — LLM Guard API v0.0.10 — hellofans.ai production stack
**Host:** 15.204.46.173:8000  
**Platform:** LLM Guard API v0.0.10 (Protect AI)  
**Operator:** prod.hellofans.ai / prod2.hellofans.ai (AI fan engagement platform)  
**Auth state:** AUTH REQUIRED on `/analyze/prompt`, `/analyze/output`, `/scan/output` — auth token configured  
**Open surface:** `/docs` (Swagger UI), `/metrics` (Prometheus — UNAUTH)  
**Metrics intelligence:**
- `/scan/output` → 345,089 completed scan requests (heavily used production instance)
- Internal docker network: `172.18.0.4:8000` proxied from `10.0.0.10:8000`
- Callers: `prod.hellofans.ai`, `prod2.hellofans.ai`, `api.ipify.org` (IP lookup in scanner init)
- Python 3.12.4, process uptime indicates long-running production deployment

**Tier:** UNRATED — auth on scan endpoints. `/metrics` open leaks operator identity and request volume.

---

### F2 — LLM Guard API v0.0.10 — agke.ovh LiteLLM stack
**Host:** 57.128.58.103:8000  
**Platform:** LLM Guard API v0.0.10 (Protect AI)  
**Operator:** rtx.agke.ovh / litellm.agke.ovh / milvus.agke.ovh (private LiteLLM + Milvus deployment)  
**Auth state:** AUTH REQUIRED on scan endpoints  
**Open surface:** `/docs` (Swagger UI), `/metrics` (Prometheus — UNAUTH)  
**Metrics intelligence:**
- Stack confirmed: LiteLLM proxy + Milvus vector DB + LLM Guard — full RAG stack with guardrail layer
- Internal container: `172.18.0.4:8000`
- Callers include `litellm.agke.ovh`, `milvus.agke.ovh`, `rtx.agke.ovh`
- Python 3.12.10, fresh deployment (fewer GC collections than F1)
- IPv6 exposed: `[2001:41d0:304:400::6c8]:8000`

**Tier:** UNRATED — auth on scan endpoints. `/metrics` open leaks stack topology and operator domains.

---

## Negative Results (Platforms Not Internet-Exposed)

**Vigil (deadbits/vigil-llm):** Zero confirmed instances. Shodan does not index the specific response bodies (`prompt_entropy`, `/api/canary/ingest` content). The `/settings` dork produced 36 hits all FP (Synology NAS, Ukrainian betting bot admin panel). Vigil is either: not deployed at scale, deployed behind auth proxies, or its Flask response bodies don't get indexed.

**Rebuff:** Zero. Archived repo — no active self-hosted deployments visible.

**NeMo Guardrails:** Zero. All NeMo-specific path strings (`/v1/rails/configs`, `/v1/rails/generate`, `nemoguardrails`) return 0 from Shodan. Deployed internally or behind auth at enterprises using it.

**Guardrails AI:** Zero. Hub URL and vendor domain not indexed on port 8000.

**LlamaGuard / ShieldLM / PromptGuard / LlamaFirewall:** Zero. Model-serving deployments with these models don't expose model names in indexed HTTP bodies at scale.

---

## Operator Intelligence

### hellofans.ai (F1)
- AI-powered fan engagement platform
- Running LLM Guard on production content scanning — 345K+ scan calls
- Two environments: prod + prod2 — both routing to same LLM Guard instance
- Uses LLM Guard as output filter (`/scan/output` is the hot path, not `/scan/prompt`)

### agke.ovh (F2)
- Private deployment, likely dev/research stack
- Full stack: LiteLLM (LLM proxy) + Milvus (vector DB) + LLM Guard (guardrail)
- Domain pattern suggests operator handle "agke"
- OVH-hosted (57.128.x.x = OVH Paris range)

---

## Key Finding: /metrics Is the Open Surface

Both confirmed LLM Guard instances have auth configured on scan endpoints — the "auth off by default" class-level finding does NOT apply to these deployed instances. However, `/metrics` is open on both with no auth. The Prometheus metrics leak:
1. Operator domain names (from `http_server_name` labels)
2. Request volumes and endpoint call counts
3. Internal network topology (docker bridge IPs, upstream server names)
4. Stack composition (which services call LLM Guard)
5. Runtime details (Python version, process start time, memory usage)

This is the actual finding class for production LLM Guard deployments: not open scan endpoints, but open metrics endpoint leaking production topology.

---

## Dork Refinement Notes

- `http.html:"LLM Guard API"` — the anchor. Exact OpenAPI title string. Low FP, confirmed working.
- Vigil body-content dorks are dead — Shodan doesn't crawl Flask responses on port 5000 with enough depth to index response JSON fields.
- NeMo endpoint paths not indexed — FastAPI /v1/rails/* appears not in Shodan's index.
- All guardrail platforms except LLM Guard are Shodan-dark for their specific signals.

