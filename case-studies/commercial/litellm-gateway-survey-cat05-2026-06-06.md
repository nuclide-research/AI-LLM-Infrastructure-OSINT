---
type: case-study
category: cat-05
platform: LiteLLM / Langfuse / Arize Phoenix
date: 2026-06-06
findings: 6 critical, 4 medium
status: verified
---

# Cat-05: LiteLLM Gateway Survey — Open Proxies Exposing Commercial LLM API Keys

_NuClide Research · 2026-06-06_

---

## Discovery

The hunt started with a single Shodan dork: `http.title:"LiteLLM" port:4000`. It returned 2,219 results in under a second.

LiteLLM is an OpenAI-compatible proxy layer that sits in front of every major LLM provider — Anthropic, OpenAI, Google Vertex, AWS Bedrock. Operators configure it with their provider API keys, deploy it on a VPS, and route all their LLM calls through one unified endpoint. The problem: without `LITELLM_MASTER_KEY` set in the environment, the proxy accepts all requests unauthenticated. The admin UI at `/ui`, the model configuration at `/model/info`, and the completion endpoint at `/v1/chat/completions` are all publicly accessible.

`/health/readiness` returns `{"master_key_hash": null}` when no key is configured. That's a one-request auth check — no scanning required, just a single GET.

---

## Methodology

**Stage -1 (OSINT Platoon):** Pre-survey intel run 2026-06-05. Established CVE catalog: CVE-2026-42208 (Critical, SQLi via Authorization header, CISA KEV), CVE-2026-49468 (Critical, Host header auth bypass), CVE-2026-35030 (Critical, OIDC JWT cache collision). Also documented the default credential pattern: `UI_USERNAME=ishaan-litellm / UI_PASSWORD=langchain` appears in LiteLLM documentation examples and gets copy-pasted into production configs.

**Stage 0 (Shodan):** Shodan API (`shodan download`) with Freelance-tier key. 2,219 results for `http.title:"LiteLLM" port:4000`. Downloaded 1,000 IPs across two batches.

**Stage 0c (liveness):** Direct probe of `/health/liveliness` and `/health/readiness` against batches of 80-110 IPs in parallel. ~40% live rate on the sampled population (better than the 29% baseline, likely because LiteLLM operators on Scaleway/Hetzner VPS tend to leave instances running).

**Stage 3v (verify):** For each live instance: check `/health/readiness` for `master_key_hash=null`, then `/v1/models` for model list, then `/model/info` for `litellm_params.api_base` to identify the actual provider backend. Cross-referenced with `/health` to confirm backend health status.

The 50% rule applied here differently than usual: the ~50% FP pattern was model name aliasing — operators alias local Ollama models under Claude/GPT-4o names. `51.255.95.37` listed `claude-3-5-sonnet-20241022` in `/v1/models` but `/model/info` showed `ollama/qwen2.5-coder:32b @ http://localhost:11434`. The model name is not the provider. `/model/info.litellm_params.api_base` is the primary source.

---

## Findings

### F-001 — Anthropic API Open Proxy (Dallas TX)

`23.238.9.142:4000` — Hostwinds, Dallas, United States

No master key. `/v1/models` returns `claude-sonnet-4-6` and `claude-haiku-4-5-20251001`. `/model/info` confirms both route to `anthropic/` at the default API endpoint — a direct Anthropic API key configured in the environment. `/health` returns healthy=1. No credentials in the litellm_params response (key is env-variable-injected), but the backend is actively serving requests.

Anyone on the internet who sends a standard OpenAI-format POST to `http://23.238.9.142:4000/v1/chat/completions` gets Claude responses billed to the operator's Anthropic account.

**Verification:** inner-B/outer-1. `/health/readiness` master_key_hash=null; `/health` healthy=1; restraint: no completion issued.

---

### F-002 — AWS Bedrock EU with Claude opus-4-7 (Strategion, Berlin)

`85.214.93.104:4000` — Strato Rechenzentrum, Berlin, Germany  
Operator: **Strategion GmbH** (`dev-strategion.de`)

No master key. `/model/info` reveals three AWS Bedrock EU models: `eu.anthropic.claude-haiku-4-5-20251001-v1:0`, `eu.anthropic.claude-sonnet-4-6`, and `eu.anthropic.claude-opus-4-7`. All three backends healthy.

Passive DNS (HackerTarget) returned 45 subdomains under `dev-strategion.de`, including:

- `api-kardiointerakt.dev-strategion.de` — cardiac AI interaction API
- `federated-learning.dev-strategion.de` — federated ML training
- `digiwoh-voicebot-demo.dev-strategion.de` — voice bot
- `airflow.dev-strategion.de`, `airbyte.dev-strategion.de` — pipeline infra
- `dashboard.dev-strategion.de`, `data-catalog.dev-strategion.de`

The `kardiointerakt` subdomain is load-bearing: Strategion is operating medical AI infrastructure. An open LLM proxy in this context means the AWS Bedrock credentials — which also access whatever medical data flows through that pipeline — can be abused by anyone who finds the Shodan result.

**Verification:** inner-B/outer-1. AWS Bedrock EU model ARNs confirmed; healthy=3; no completion issued.

---

### F-003 — Azure OpenAI Open Proxy (Netherlands)

`23.100.4.60:4000` — Microsoft Azure, Netherlands

No master key. `/model/info` reveals three Azure OpenAI deployments at `https://uksdoai673aif02.openai.azure.com/`: `azure/gpt-4o-1`, `azure/gpt-4o-mini`, and `azure/gpt-5.4-1`. All three healthy.

The Azure resource name `uksdoai673aif02` in the endpoint URL — returned by the unauthenticated `/model/info` endpoint — uniquely identifies the Azure Cognitive Services resource. This is a named operator artifact accessible to anyone.

**Verification:** inner-B/outer-1. Azure endpoint confirmed; healthy=3; no completion issued.

---

### F-004 — Vertex AI Gemini 2.5 Pro Open Proxy (inquinion-code)

`159.203.3.89:4000` — DigitalOcean, Toronto, Canada  
GCP project: **inquinion-code** (us-central1)

No master key. `/model/info` shows `vertex_ai/gemini-2.5-pro` with `vertex_project=inquinion-code`. Backend healthy. The GCP project name leaks from the unauthenticated endpoint, attributing the operator's Google Cloud project to a bare DigitalOcean VPS.

**Verification:** inner-B/outer-1.

---

### F-005 — Vertex AI Gemini + Chirp STT Open Proxy (IPEX, Brazil)

`35.184.137.52:4000` — Google Cloud, Council Bluffs (GCP), Brazil operator  
GCP project: **tdsipex**  
Domains: `chat-ia.ipexdesenvolvimento.cloud`, `curso-ia.ipexdesenvolvimento.cloud`

No master key. `/model/info` shows `vertex_ai/gemini-2.5-flash` and `vertex_ai/chirp-3` (Google's speech-to-text model) both routing to GCP project `tdsipex`. Both healthy.

`curso-ia.ipexdesenvolvimento.cloud` ("AI course") alongside `chat-ia` suggests IPEX operates an AI education platform. Chirp-3 STT access means speech processing workloads billed to their GCP account are open to anyone.

TLS cert attribution: `CN=chat-ia.ipexdesenvolvimento.cloud` (Let's Encrypt) confirms operator.

**Verification:** inner-B/outer-1.

---

### F-006 — Stacked Exposure: Open WebUI + LiteLLM + Qdrant + Prometheus (UQConnect)

`203.101.230.35` — UQConnect (University of Queensland Connect cloud), Australia

This is the methodology's stacked-catastrophe pattern (Insight #12): one operator, four exposed services, none authenticated.

**Inventory:**

| Port | Service | Auth | Data |
|------|---------|------|------|
| 3000 | Open WebUI v0.7.2 | `auth_enabled=False` | Full chat UI |
| 4000 | LiteLLM | no master_key | LLM proxy |
| 6333 | Qdrant | none | Research paper vectors |
| 9090 | Prometheus | none | LiteLLM metrics |
| 9000 | MinIO | **GATED** | Object storage |

**Open WebUI** with `auth_enabled=False` means the chat interface loads without login. The application's `/api/config` endpoint returns `{"features":{"auth":false,"enable_signup":false}}`.

**Qdrant** exposes four collections:
- `papers-test2`: 1,639 vectors — plant biology research papers (jasmonate, brassinosteroids, ethylene signal transduction, ABA, GA regulation). Payload fields: `text`, `name`, `media`, `doc`.
- `papers-test`: 28 vectors — botanical/agricultural research (GA, branching regulation)
- `qdrant-web-docs`: 18,828 vectors — Qdrant documentation
- `test_collection`: empty

The research paper content suggests a University of Queensland research group built a RAG system over plant biology literature. Pre-publication research data could be in the vector store.

**Prometheus** `job=litellm` target reveals the Docker Compose network topology (service named `litellm` at internal hostname `litellm:4000`).

**Verification:** inner-B/outer-1. All four services verified via direct probe; Open WebUI title confirmed; Qdrant scroll returned plant biology content; no chat completion issued.

---

## The LiteLLM Auth-Default Problem at Scale

The 2,219 LiteLLM Shodan population represents the baseline — every operator who deployed LiteLLM and left it indexed. The population running on private ranges, behind NAT, or after Shodan's crawl window is larger.

Of the ~430 IPs checked:
- ~40% live
- ~85% of live instances: no master_key
- ~5-10% of live no-key instances: commercially-backed healthy endpoints

The Shodan-indexed population at this exposure rate projects to 80-100 open LiteLLM proxies actively routing to commercial providers at any given crawl snapshot. Most have unhealthy backends (rotated or expired keys), but the subset with working backends is the live attack surface for compute theft.

LiteLLM is Tier-A: no auth concept in default deploy. The framework works without any key. Operators who follow the quickstart — copy-paste docker-compose.yml, `docker-compose up` — get a fully open proxy.

---

## Langfuse: signUpDisabled=False at Population Scale

Langfuse is the other major finding in this survey. Of 1,141 Shodan hits on `"Langfuse" port:3000`, every instance checked (25/25) had `signUpDisabled=false`.

This is the "effective unauth" pattern (Insight #8): any internet user can create an account, and depending on the instance's organization structure, may gain access to existing LLM trace data. Notable instances:

- **Arizona State University** (206.206.192.179, v3.132.0)
- **Google Cloud** (34.21.132.39, v3.166.0 — latest as of survey)
- **Safespring AB** (Swedish research cloud provider, 192.121.133.92)

Langfuse's auth model means open signup does not automatically grant access to other users' traces — each user is in an organization. But university deployments often function as shared instances where all faculty/students are in one org, meaning signup grants full trace visibility.

---

## Northeastern University: Arize Phoenix Essaybot

`129.10.224.226:6006` — Northeastern University, Boston, MA

Arize Phoenix instance with two registered projects: `Essaybot` and `default`. No trace data accessible at scan time (0 spans returned via REST and GraphQL). The project name `Essaybot` indicates a Phoenix-instrumented LLM application for essay writing. This is a live LLM observability dashboard with no auth wall.

---

## Pattern: The Control Plane is the Crown Jewel

Individual LLM server exposure (Ollama, vLLM) has been surveyed extensively in prior categories. This category proves the worse scenario: the *gateway* is exposed, not the model.

A gateway proxy centralizes provider keys. One open LiteLLM instance exposes every API key configured in it — Anthropic, OpenAI, Azure, Bedrock, Vertex — as a single unauthenticated target. The blast radius is the entire provider portfolio of the operator, not one model endpoint.

F-002 (Strategion, Berlin) makes this concrete: the same IP that has an open LiteLLM also has `api-kardiointerakt.dev-strategion.de`. The medical AI pipeline and the open LLM proxy share an operator. The Bedrock EU credentials that power the cardiac AI application are the same credentials freely callable by anyone with the Shodan result.

---

## Toolchain Provenance

```
Stage -1:  data/platform-intel/gateways-observability-docloaders-osint-2026-06-05.md
           (4-lane OSINT Platoon: LiteLLM, Kong, Langfuse, Tika)
Stage 0:   shodan download × 8 dorks (API key)
           ~/recon/05-gateways-observability-docloaders-2026-06-05/
Stage 0c:  tiptoe -f ips.txt -p 4000,3000,6006,8001 (liveness sweep)
           + curl /health/readiness batch (parallel xargs, 20 threads)
Stage 1a:  visorplus assess × 5 critical hosts
           (attribution: dev-strategion.de 45 subdomains; ipexdesenvolvimento.cloud)
Stage 1b:  aimap -list live-critical.txt -o aimap-critical.json
           (11 hosts, 18 services, 15 unauth, 27 findings)
Stage 3v:  /health/readiness master_key_hash check + /model/info api_base
           verification on all live candidates
Stage 6:   visorlog add × 6 findings
Stage 7:   visorscuba assess (BLUE-EXP-001 violations on all 6)
Stage 12b: findings-breakdown.txt (this session)
```

---

## Remediation

**For LiteLLM operators:**
Set `LITELLM_MASTER_KEY` in the environment before any public-facing deployment. Even a randomly generated key eliminates the unauthenticated surface. The quickstart should not be followed verbatim in production.

```yaml
environment:
  - LITELLM_MASTER_KEY=sk-<random-32-char>
```

**For Langfuse operators:**
Set `AUTH_DISABLE_SIGNUP=true` in the environment to prevent open registration. Single-user instances should also set a strong `NEXTAUTH_SECRET`.

**For Open WebUI operators:**
Set `WEBUI_AUTH=true` (the default in recent versions). Never deploy with `auth_enabled=False` on a public IP.
