# LLM Safety / Guardrail Engines — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (12 platforms)_
_Updated: 2026-05-31 — added LlamaRisk "LlamaGuard AI Firewall" vendor + Meta-model disambiguation (Censys CT discovery; findings #36162-36163)_
_See: data/platform-intel/safety-guardrail-osint-2026-05-27.md for full intel_

**Category theme:** Guardrail engines deployed as API servers almost universally ship with auth off — they assume trusted-network placement. An exposed guardrail server = safety bypass (route around it), prompt log access, and policy config disclosure. The irony: security tools with no security on themselves.

---

## LlamaGuard / Llama Guard 3 (Meta)
**Auth default:** off (no auth concept on hosting server unless explicitly configured)
**Exposure class:** model roster reveals safety classifier; unauth inference endpoint usable to probe bypass
**⚠ Disambiguation:** "LlamaGuard" the *model* (this section, Meta `meta-llama/Llama-Guard-3-*`) is NOT "LlamaGuard AI Firewall," a commercial guardrail *vendor* by LlamaRisk (see its own section below). A bare-string search for `LlamaGuard` returns the **vendor brand** (cert `subject_dn`), not the model. The model lives in the inference server's `/v1/models` body and is Shodan/Censys-body-dark; it surfaces via **Censys CT cert names** (`"Llama-Guard"` full-text = 130 hits, 2026-05-31, finding #36162). Match the model by the data layer, never by the name.

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"Llama-Guard-3"` | Model name as indexed by Shodan from `/v1/models` JSON | Low |
| secondary | `http.html:"meta-llama/Llama-Guard" port:8000` | Full HuggingFace model path in vLLM responses | Low |
| tertiary | `http.html:"llama-guard-2-8b" OR http.html:"llama-guard-3-8b"` | Specific model variant names | Low |
| ollama | `http.html:"llama-guard" port:11434` | Ollama deployments serving the model | Med (name collision) |
| identity-probe | `GET /v1/models` → `id` field containing `"Llama-Guard"` | Confirms model loaded on inference server | — |

---

## LlamaGuard AI Firewall (LlamaRisk) — commercial vendor, NOT the Meta model
**Auth default:** SaaS/self-hosted firewall product; auth posture per-deployment (unknown, not tested)
**Exposure class:** commercial AI-firewall/guardrail product. Cataloged for disambiguation: this is the brand the bare string "LlamaGuard" resolves to, the name-collision flagged in the Meta section above. Distinct vendor (LlamaRisk), distinct from `meta-llama/Llama-Guard-*`.
**Discovery:** Censys, not Shodan html. Bare full-text `"LlamaGuard"` returns this vendor via cert `subject_dn`/`names` (0 hosts, 5 certs, 14 web properties, 2026-05-31). Finding #36163.

| Label | Query (Censys CenQL) | Rationale | FP Risk |
|-------|-------|-----------|---------|
| brand-domains | `cert.names: "llamarisk.com" or cert.names: "llamaguard.com"` | Vendor + product domains | Low |
| product-title | `web.endpoints.http.html_title= "LlamaGuard AI Firewall"` | Product UI title | Low |
| deployed-instance | `host.ip: "129.151.137.216"` | `llamaguard.129-151-137-216.nip.io` proof/staging deploy (Oracle Cloud) | — |
| known assets | `llamaguard.com`, `www.llamaguard.com`, `llamaguard-firewall.arhaamali.com`, `llamaguard-proof.llamarisk.com`, `dashboard.llamarisk.com` | Observed CT assets | — |

**Note:** auth state and product surface NOT tested (vendor out of any engagement scope; observation only). If a guardrail survey later includes commercial AI-firewall vendors, this is the LlamaRisk entry.

---

## NeMo Guardrails (NVIDIA)
**Auth default:** off (no built-in auth; Authorization header forwarded to upstream LLM only)
**Exposure class:** rail config names (`/v1/rails/configs`), Colang policy structure, upstream LLM config, conversation state

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"/v1/rails/configs"` | Unique NeMo endpoint path — appears in Swagger UI and error pages | Low |
| secondary | `http.html:"nemoguardrails" port:8000` | Python package name in server responses | Low |
| tertiary | `http.html:"colang" port:8000` | NeMo's policy DSL name — distinctive to NeMo ecosystem | Low |
| quaternary | `http.html:"/v1/rails/generate"` | NeMo rails-generate endpoint path | Low |
| product-name | `http.html:"NeMo Guardrails"` | Full product name | Med (docs/blog pages) |
| cert | `ssl.cert.subject.cn:"nemoguardrails"` | TLS cert CN for dedicated deployments | Low |
| identity-probe | `GET /v1/rails/configs` → 200 + JSON array | Returns `[]` or list of config names; unique to NeMo | — |

---

## Lakera Guard (self-hosted enterprise)
**Auth default:** on for SaaS; self-hosted details gated (assume API key required)
**Exposure class:** caller-side: which orgs use Lakera (API URL in JS bundles); self-hosted: guard policy config

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"lakera-guard"` | Hyphenated product name — appears in caller-side HTML | Low |
| header | `"Server: lakera"` | Response header on self-hosted instances | Low |
| endpoint | `http.html:"/v1/guard" http.html:"lakera"` | Guard endpoint path combined with vendor name | Low |
| caller-side | `http.html:"api.lakera.ai"` | SaaS API URL hardcoded in customer apps | Med (legitimate refs) |
| response-field | `http.html:"prompt_injection" http.html:"lakera"` | Lakera response category name in customer HTML | Med |
| cert | `ssl.cert.subject.cn:"lakera.ai"` | Vendor TLS cert CN | Low |
| identity-probe | `POST /v1/guard {"input": "test"}` → JSON with `"flagged"`, `"categories"` keys | Lakera-specific response shape | — |

---

## Guardrails AI
**Auth default:** off (`GUARDRAILS_API_KEY` is optional env var; unset = open)
**Exposure class:** all guard definitions (validation logic + schemas), guard names, LLM proxy config, OpenAPI spec

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"guardrails-ai" port:8000` | Package identifier on default port | Med (string common) |
| secondary | `http.html:"guardrailsai.com" port:8000` | Vendor domain in Swagger UI | Low |
| endpoint | `http.html:"/guards" http.html:"guardrails"` | Guards endpoint + vendor name | Med |
| openapi | `http.html:"guardrails" http.html:"/openapi.json"` | FastAPI schema endpoint + vendor | Med |
| health | `http.html:"health-check" http.html:"guardrails"` | Health endpoint + vendor | Med |
| hub | `http.html:"hub.guardrailsai.com"` | Guardrails Hub URL in server HTML | Low |
| identity-probe | `GET /guards` → 200 + JSON array of guard objects | Confirms open Guardrails AI server; guard definitions exposed | — |
| confirm-probe | `GET /health-check` → `{"status": "ok"}` | Faster liveness check | — |

---

## LLM Guard (Protect AI)
**Auth default:** off (`AUTH_TOKEN` is optional; when unset, all `/analyze/*` endpoints open)
**Exposure class:** scanner config (which scanners active, thresholds, model names), scan result cache (100 recent prompts), OpenAPI spec

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"LLM Guard API"` | Exact string from OpenAPI `info.title` field | Low |
| secondary | `http.html:"laiyer/llm-guard"` | Docker image name in deployment artifacts | Low |
| tertiary | `http.html:"protectai/llm-guard"` | GitHub repo reference in server responses | Low |
| swagger | `http.html:"llm-guard" http.html:"swagger"` | Swagger UI exposed for LLM Guard | Med |
| port | `port:8000 http.html:"llm-guard"` | Default port + product name | Med |
| identity-probe | `GET /swagger.json` → JSON with `info.title = "LLM Guard API"` | Definitive identification | — |
| scan-probe | `POST /analyze/prompt {"prompt": "test"}` → JSON with `is_valid`, `scanners_results` | Confirms scanner endpoint open | — |

---

## Rebuff (Protect AI — archived)
**Auth default:** off (dev default); `MASTER_API_KEY=12345` in example config = default creds risk
**Exposure class:** injection detection history, canary token corpus, VectorDB contents, embedded API keys (OpenAI, Pinecone, Supabase) in leaked env config

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:3000 http.html:"rebuff"` | Product name on default Node.js port | Med |
| secondary | `port:3000 http.html:"rebuff.ai"` | Vendor domain reference | Low |
| api | `port:3000 http.html:"/api/detect"` | Primary detection endpoint path | Low |
| canary | `port:3000 http.html:"canary"` | Canary token endpoint reference | High (generic word) |
| env-leak | `http.html:"MASTER_API_KEY" port:3000` | Exposed env config — default creds indicator | Low |
| identity-probe | `POST /api/detect {"userInput": "test"}` → JSON with `injectionScore`, `heuristicScore`, `vectorScore` | Confirms Rebuff API open | — |

---

## ShieldLM (Tsinghua University / thu-coai)
**Auth default:** off (no built-in server; inherits from vLLM/hosting framework with no default auth)
**Exposure class:** safety classifications with explanations, bilingual (CN/EN) content flags, model reasoning output

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"ShieldLM" port:8000` | Model name in vLLM `/v1/models` response | Low |
| secondary | `http.html:"thu-coai/ShieldLM"` | HuggingFace model path reference | Low |
| model-id | `http.html:"shieldlm" port:8000` | Lowercase variant | Low |
| identity-probe | `GET /v1/models` → `id` containing `"ShieldLM"` | Confirms ShieldLM loaded via vLLM | — |
| confirm | `POST /v1/chat/completions` → response text containing `"safe"`, `"unsafe"`, or `"controversial"` | ShieldLM three-class output | — |

---

## Llama-Recipes Safety Demos (Meta)
**Auth default:** off (demo code, no auth)
**Exposure class:** demo API keys, prompt/response logs, accidental production deployment of test code

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"llama-recipes"` | Meta's recipe collection identifier | Low |
| secondary | `http.html:"PurpleLlama" port:8000 OR port:5000` | PurpleLlama safety demo suite | Low |
| tertiary | `http.html:"llama-recipes" http.html:"safety"` | Safety-specific demo page | Low |
| identity-probe | `GET /` → HTML with `"llama-recipes"` or `"PurpleLlama"` reference | Demo server running | — |

---

## OpenShield (AI Firewall — archived 2026-02-03)
**Auth default:** on for main API (port 8080); Adminer DB UI on port 8085 has no separate auth layer
**Exposure class:** port 8085 Adminer = full DB access — content filter rules, request logs, API key entries, rate limit configs

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.html:"openshield"` | Product name on API port | Low |
| adminer | `port:8085 http.html:"adminer" http.html:"openshield"` | DB management UI exposed | Low |
| adminer-generic | `port:8085 http.html:"adminer"` | Broader Adminer sweep (verify OpenShield via DB schema) | High |
| secondary | `http.html:"openshieldai" port:8080` | GitHub org name in server responses | Low |
| identity-probe | `GET /openai/v1/models` → 401 (auth required on main API) | Confirms OpenShield proxy presence | — |
| db-probe | `GET :8085` → Adminer login page → check for `openshield` schema | DB UI accessible, confirms OpenShield | — |

---

## PromptGuard / Llama Prompt Guard 2 (Meta)
**Auth default:** off (reference deployments carry no auth; `HF_TOKEN` is startup-only, not API auth)
**Exposure class:** prompt injection/jailbreak classification results, confidence scores per class (benign/injection/jailbreak), model version

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"Llama-Prompt-Guard" port:8000` | Model name in server responses | Low |
| secondary | `http.html:"Prompt-Guard-86M"` | Original model variant name | Low |
| tertiary | `http.html:"prompt-guard" http.html:"injection" port:8000` | Model name + injection detection context | Med |
| llamafirewall | `http.html:"LlamaFirewall" port:8000` | Parent suite name in server HTML | Low |
| identity-probe | `GET /v1/models` → `id` containing `"Prompt-Guard"` | Confirms PromptGuard model loaded | — |
| confirm | `POST /v1/chat/completions {"messages":[{"role":"user","content":"test"}]}` → response with `"INJECTION"`, `"JAILBREAK"`, or `"BENIGN"` | PromptGuard classification output | — |

---

## AIShield Guardian (Bosch)
**Auth default:** on (`GUARDIAN_API_KEY` required; enterprise contact provisioning)
**Exposure class:** caller-side: customer apps embedding guardian endpoint URLs; Watchtower scan results if exposed via Jupyter/Streamlit

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"AIShield Guardian"` | Product name in customer integrations | Low |
| secondary | `http.html:"aishield" http.html:"guardian"` | Vendor + product name conjunct | Med |
| watchtower | `http.html:"AIShield Watchtower"` | Open-source companion product | Low |
| bosch | `http.html:"bosch-aisecurity"` | GitHub org reference | Low |
| caller-side | `http.html:"GUARDIAN_API_ENDPOINT"` | Env variable reference in exposed config | Low |
| identity-probe | N/A — no known public default endpoint; enterprise product | — | — |

---

## Vigil (deadbits/vigil-llm)
**Auth default:** off (zero auth implemented in any version; Flask bound to 0.0.0.0:5000)
**Exposure class:** full scanner config via `/settings` (scanner list, model names, thresholds, embedding API key), prompt scan cache (100 recent entries), YARA rule paths, VectorDB collection names

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5000 http.html:"vigil"` | Product name on Flask default port | Med (common word) |
| secondary | `port:5000 http.html:"prompt injection" http.html:"analyze"` | Injection detection context on default port | Med |
| endpoint | `port:5000 http.html:"/analyze/prompt"` | Primary scan endpoint path | Low |
| settings | `port:5000 http.html:"/settings"` | Settings endpoint path | Med |
| scanner | `port:5000 http.html:"vigil" http.html:"scanner"` | Scanner config context | Med |
| identity-probe | `GET /settings` → JSON with `scanner`, `embedding`, `cache` keys | Definitive identification + config leak | — |
| scan-probe | `POST /analyze/prompt {"prompt": "test"}` → JSON with `uuid`, `prompt_entropy`, `results` | Confirms open scan endpoint | — |
| write-probe | `POST /add/texts {"texts": ["test"], "metadatas": [{}]}` → 200 | Confirms unauthenticated write to VectorDB | — |

---

## Cross-Platform Notes

**Conjunctive matching required.** Most platform names (`"guardrails"`, `"vigil"`, `"rebuff"`, `"guard"`) are common English words. Every query above uses conjunctive signals — port + name, or name + endpoint path. Single-term body matches will produce population-scale noise.

**Port 8000 congestion.** Six of these 12 platforms default to port 8000. Any port:8000 sweep must confirm platform identity via the verification probe before claiming a finding.

**Zero-auth is the class-level finding.** NeMo Guardrails, Guardrails AI, LLM Guard, Vigil, PromptGuard, LlamaGuard hosting servers, and Rebuff all ship with auth off. This is not individual misconfiguration — it is the default posture for the category. Any internet-exposed instance is likely unintentionally open.

**Cross-reference with existing surveys.** LlamaGuard and PromptGuard surface in model-serving surveys (§3). Port 8000 sweeps from prior LLM-orchestration and model-serving surveys (`01-llm-orchestration.md`, `03-model-serving.md`) may already contain guardrail-server hits. Re-query those corpora for `Llama-Guard`, `rails/configs`, and `LLM Guard API` before running fresh Shodan harvests.

**See also:** `shodan/queries/24-llm-safety-guardrail-policy.md` — broader categorical coverage including OPA, content moderation SaaS, and AI governance platforms.
