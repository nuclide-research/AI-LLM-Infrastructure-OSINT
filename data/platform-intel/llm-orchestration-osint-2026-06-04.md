# Cat-01 LLM Orchestration — Pre-Assessment Platform Intelligence

**Date:** 2026-06-04
**Slug:** `01-llm-orchestration`
**Stage:** -1 (agentic pre-assessment OSINT — run before any harvest)
**Method:** 6-squad parallel OSINT fan-out (OSINT Platoon doctrine), one cluster each,
all six methodology research lanes per platform, primary-source grounded.
**Status:** Cat-01 treated as a **virgin category**. No prior Stage -1 intel doc existed
(the 2026-05-15 Ollama walk and 2026-05-19 re-run jumped straight to harvest on inherited
dorks). This document is the category's first proper birth.

> **Verification caveat (read first).** Several CVE IDs and live population counts below are
> **squad-reported from web research and are NOT independently verified by the operator**.
> Anything dated CVE-2026-* or any "N instances exposed" figure is an agent-sourced lead,
> not an asserted fact. Verify against primary advisory + live probe before any finding
> claim or disclosure (per `feedback_reverify_cross_session_claims`,
> `feedback_verify_before_claiming_exploitable`). They are recorded here as research
> leads to drive probe design, nothing more.

---

## 1. Roster (25 platforms, 6 clusters)

| Squad | Cluster | Platforms |
|---|---|---|
| Alpha | Low-code flow builders | Flowise, Langflow, Dify |
| Bravo | Western chat/app front-ends | Open WebUI, LibreChat, LobeChat, big-AGI, Chatbot UI |
| Charlie | Chinese-OSS orchestrators | FastGPT, BISHENG, Coze Studio, RAGFlow |
| Delta | App frameworks / visual builders | Chainlit, Rivet, PromptFlow, Botpress |
| Echo | Workflow + agent gateways (RCE-class) | n8n, OpenClaw/Clawdbot, Khoj, Cheshire Cat |
| Foxtrot | Local/self-host model runtimes | Ollama, Jan, LocalAI, GPT4All, oobabooga, h2oGPT |

Scope boundary: pure RAG stacks (Cat-07: AnythingLLM, Quivr, Danswer, Verba, R2R, Kotaemon,
LightRAG, Perplexica), pure agent frameworks (Cat-06: CrewAI, Agno, SuperAGI, AgentGPT, Letta),
and gateways (Cat-32: LiteLLM, Portkey, Kong) are **out of scope here** — they have or will get
their own category births. Ollama/n8n/Open WebUI carry prior survey history; included for
completeness and fingerprint-currency check, not re-derived from zero.

---

## 2. Auth-on-default posture map (the thesis variable)

| Platform | Shipped default | Effective state | Notes |
|---|---|---|---|
| Flowise | no `FLOWISE_USERNAME/PASSWORD` set | **OPEN** | all `/api/v1/*` readable incl. `/credentials` |
| Langflow | `AUTO_LOGIN=True` | **OPEN** | `/api/v1/auto_login` mints superuser JWT, no creds; fallback creds `langflow/langflow` |
| Dify | `INIT_PASSWORD` empty | **CLAIMABLE** | `/console/api/setup` POST claims admin on fresh install |
| Open WebUI | `WEBUI_AUTH=True`, `ENABLE_SIGNUP=True` | **CLAIMABLE** | first signup → admin, then signup auto-closes |
| LibreChat | `ALLOW_REGISTRATION=true` | **OPEN-REG** | Mongo runs `--noauth` in compose |
| LobeChat (Mode-A) | no `ACCESS_CODE` | **OPEN** | server keys usable by anyone; catastrophic-leak tier |
| LobeChat (Mode-B) | auth provider required | **AUTH** | architecture mandates user IDs — thesis counter-example |
| big-AGI | no `HTTP_BASIC_AUTH_*` | **OPEN** | tRPC `publicProcedure` surface; server keys shared |
| Chatbot UI | Supabase RLS mandatory | **AUTH** | thesis counter-example; risk shifts to Supabase key leak |
| FastGPT | `DEFAULT_ROOT_PSW=1234` | **DEFAULT-CRED** | re-inits `root/1234` every restart |
| BISHENG | first-register-admin | **CLAIMABLE** | MySQL root `1234` in compose |
| Coze Studio | open registration | **OPEN-REG** | README warns; MySQL `coze/coze123` |
| RAGFlow | `admin@ragflow.io/admin`, `REGISTER_ENABLED=1` | **DEFAULT-CRED** | service pw reuse `infini_rag_flow` across MySQL/MinIO/Redis/ES/Kibana |
| Chainlit | no auth callback | **OPEN** | `chainlit run` = public app unless dev adds callback |
| Rivet | desktop app; debugger `localhost` | **N/A-ish** | only `rivet-node` debugger ws:21888 if bound 0.0.0.0 |
| PromptFlow (flow-serve) | no auth on `/score` | **OPEN** | container deploy on `0.0.0.0:8080` |
| Botpress v12 | first-user race | **CLAIMABLE** | EoL; `/api/v1/admin/auth/register/basic` before first user |
| n8n | owner-setup flow | **CLAIMABLE/pre-setup** | `/rest/settings` always unauth; Execute-Command node = RCE |
| OpenClaw | gateway token required | **OPEN in practice** | squad-reported 92% deploy `auth_mode:none` |
| Khoj | `--anonymous-mode` in compose | **OPEN** | default creds `password`, Django key `secret` if auth on |
| Cheshire Cat | `CCAT_API_KEY` empty, `admin/admin` | **OPEN** | `CCAT_JWT_SECRET=secret` → forgeable JWT; `/plugins/upload` RCE |
| Ollama | no auth (by design) | **OPEN** | maintainers refuse server-side auth |
| Jan | API key empty | **OPEN** | binds 0.0.0.0; `Host: localhost` guard bypassable |
| LocalAI | no key | **OPEN** | `LOCALAI_API_KEY` opt-in |
| GPT4All | no key, **127.0.0.1 only** | **OPEN-but-local** | friction layer: localhost-bound default |
| oobabooga | no `--gradio-auth/--api-key` | **OPEN** | Docker compose ships `--listen` |
| h2oGPT | `--auth_access=open` | **OPEN** | OpenAI proxy unauth by default |

**Thesis verdict (pre-scan):** auth-off-or-claimable is the default across the entire
builder / chat-UI / local-runtime tier. The only two architectural counter-examples
(Chatbot UI, LobeChat Mode-B) are exactly the ones that cannot persist data without a
user identity. This is Insight #13 (shipping defaults are load-bearing) reproduced across
a 25-platform population before a single probe is sent.

---

## 3. Verification primitives (one definitive probe per platform)

Per Insight #16 — each probe distinguishes *alive* from *unauth-with-data*, not just a 200.

| Platform | Probe | Hit criterion |
|---|---|---|
| Flowise | `GET /api/v1/chatflows` :3000 | 200 + JSON array w/ `"flowData"` |
| Langflow | `GET /api/v1/auto_login` :7860 | 200 + `"access_token"` = AUTO_LOGIN open |
| Dify | `GET /console/api/setup` | `{"step":"not_started"}` = admin-claimable |
| Open WebUI | `GET /api/config` | `{"auth":false}` open / `{"enable_signup":true}` claimable |
| LibreChat | `GET /api/config` | `registration.enabled`, `buildInfo.commit` present |
| LobeChat | `GET /api/config/global` | 200 JSON no 401 = Mode-A open |
| big-AGI | `GET /api/trpc/backend.listCapabilities?batch=1&input={}` | 200 always; `capabilities.llms` = providers configured |
| Chatbot UI | `GET /` | `NEXT_PUBLIC_SUPABASE_URL` in body; auth-bypass = 200 on `/api/chat/openai` |
| FastGPT | `GET /api/v1/core/dataset/list` :3000 | 401 `{"code":501}` = present-gated; 200 array = unauth |
| BISHENG | `GET /docs` :7860 | 200 + `openapi` + `bisheng` = schema exposed |
| Coze Studio | `GET /` :8888 + `GET /v1/conversations` | body `Coze Studio`; 401 = gated |
| RAGFlow | `POST /api/v1/user/login` `{admin@ragflow.io/admin}` | 200 + `access_token` = unrotated default |
| Chainlit | `GET /auth/config` :8000 | `{"requireLogin":false}` = open |
| Rivet | ws connect :21888 | handshake accepted = no-auth debugger |
| PromptFlow svc | `GET /heartbeat` :23333 | `{"promptflow":"X.Y.Z"}` |
| PromptFlow serve | `GET /health` :8080 | `{"status":"Healthy","version":...}` |
| Botpress | `GET /version` :3000 | plaintext `BOTPRESS_VERSION` |
| n8n | `GET /rest/settings` :5678 | 200 + `"n8nVersion"` field |
| OpenClaw | `GET /` :18789 body `clawdbot-app`; ws upgrade | `auth_mode:none` in schema |
| Khoj | `GET /server/admin/` :42110 | Django admin page; `GET /` 200 no-redirect = anon mode |
| Cheshire Cat | `GET /openapi.json` :1865 | `info.title` ~ "Cheshire Cat API" |
| Ollama | `GET /api/tags` :11434 | `models[].details.family` populated |
| Jan | `GET /v1/models` :1337 | populated list (Host: localhost guard) |
| LocalAI | `GET /system` :8080 | `backends[]` array = LocalAI-exclusive |
| GPT4All | `GET /v1/models` :4891 | 200 list on 4891 |
| oobabooga | `GET /v1/internal/model/list` | 200 = t-g-webui-exclusive path, zero FP |
| h2oGPT | `GET /gradio_api/openapi.json` | body `submit_nochat_plain_api` |

---

## 4. aimap fingerprint gaps + proposed specs

**Coverage status (source: `~/ai-recon/aimap`):**

| Covered | Gap (new fingerprint needed) | Tighten (existing weak) |
|---|---|---|
| Flowise, Dify, RAGFlow, n8n, OpenClaw, Ollama, LocalAI, text-generation-webui | Langflow, LibreChat, LobeChat, big-AGI, Chatbot UI, FastGPT, BISHENG, Coze, Chainlit, Rivet, PromptFlow(×2), Botpress, Jan, GPT4All, h2oGPT, Khoj, Cheshire Cat | Dify (single-word title), t-g-webui (weak `/` body), LocalAI (add `/system`), Ollama (add `/api/ps` + root string) |

**Highest-value specs (conjunctive, marker-anchored — Insight #6):**

- **Langflow** (current `http.title:"Langflow"` is ~100% FP — confirmed): probe
  `/api/v1/health_check` requiring `status_code:200` + `json_field:status` +
  `body_contains:"chat"` + `body_contains:"db"` (the `{status,chat,db}` triple is
  Langflow-exclusive). Second probe `/api/v1/config` + `body_contains:"langflow_version"`.
- **Chainlit** (framework — title is dev-set, do NOT anchor on title): probe `/auth/config`
  requiring `json_field:requireLogin` + `json_field:passwordAuth`; fallback `/` +
  `body_contains:"chainlit-cloud.s3.eu-west-3.amazonaws.com"` (framework-injected og:image).
- **LocalAI** add `/system` + `body_contains:"backends"` + `body_contains:"llama-cpp"`
  (stronger than current `/v1/models` + `"localai"`).
- **oobabooga** add `/v1/internal/model/list` (t-g-webui-exclusive path, zero FP) — current
  `/` body match is fragile.
- **Cheshire Cat** `/openapi.json` + `body_contains:"Cheshire Cat"`; severity **critical**
  (`/plugins/upload` unauth code-exec). Verify exact OpenAPI title against live instance.
- **h2oGPT** `/gradio_api/openapi.json` + `body_contains:"submit_nochat_plain_api"`; secondary
  `/openai_api/v1/` prefix is h2oGPT-unique (others use `/v1/`).
- **Western front-ends** (LibreChat/LobeChat/big-AGI): anchor on the unauth config endpoint
  JSON shape (see §3), NOT the title. big-AGI `/api/trpc/backend.listCapabilities` is the
  cleanest. LobeChat `/api/config/global` + `body_contains:"oAuthSSOProviders"`.
- **Chinese-OSS**: FastGPT data-layer `/api/v1/core/dataset/list` 401/`code:501` anchor;
  Coze `/` + `body_contains:"coze-studio"` (the `opencoze` DB name leaks in bundles);
  BISHENG `/docs` :7860 + `openapi` + `bisheng` (verify title against live — index.html
  was 404 in research, marker unconfirmed).
- **Local runtimes** sharing OpenAI-compat `/v1`: discriminate by NON-shared path — Jan
  `/llm/auth/guest-login` or `/v1/models/import`; oobabooga `/v1/internal/*`; GPT4All has no
  unique path → port 4891 is the only discriminator (medium confidence).

Full per-platform Go specs are in the squad reports (Alpha/Bravo/Charlie/Delta/Echo/Foxtrot).
Productize into aimap as new fingerprints before the second pass (manual→productize→re-run).

---

## 5. Default-credential leads (test only on confirmed in-scope, minimally)

| Platform | User | Pass | Test endpoint |
|---|---|---|---|
| RAGFlow | `admin@ragflow.io` | `admin` | `POST :9380/api/v1/user/login` |
| FastGPT | `root` | `1234` | `POST :3000/api/v1/user/account/loginByPassword` |
| Cheshire Cat | `admin` | `admin` | `POST :1865/auth/token` |
| Langflow | `langflow` | `langflow` | `POST :7860/api/v1/login` (when AUTO_LOGIN off) |
| Khoj (Django) | `username@example.com` | `password` | `:42110/server/admin` |
| (data-tier reuse) | RAGFlow `infini_rag_flow`; FastGPT/BISHENG/Coze MinIO `minioadmin*`; BISHENG/FastGPT MySQL `1234`/root | | shadow-port sweep |

Credential testing is **active**; gate behind confirmed identity + restraint ethic. Do not
brute, do not chain to data exfil — a single confirming login that returns a token is the
finding; stop there.

---

## 6. Port set (expanded for harvest + aimap)

New orchestration-specific ports beyond the standing `AIMAP_PORTS`:

```
1337  Jan            1865  Cheshire Cat   3080  LibreChat      3210  LobeChat
4891  GPT4All        5566  Flowise worker 9380  RAGFlow API    9381  RAGFlow admin
9382  RAGFlow MCP    21888 Rivet debugger 23333 PromptFlow svc 42110 Khoj
```

Already covered in the standing set: 80,443,3000,3001,5000,5001,5678,6333,7860,8000,8080,
8081,8443,8501,8888,8889,11434,18789,19530. Add the above for the cat-01 sweep.

**Shadow-sweep priorities** (IP-direct adjacent ports on every confirmed host, Insight #12):
27017 (Mongo, LibreChat `--noauth`), 5432 (pg/pgvector), 6379 (Redis), 9000/9001 (MinIO
default creds), 19530 (Milvus no-auth), 9200 (ES no-auth), 4171 (Coze NSQ admin), 3306 (MySQL
`1234`), 6601 (RAGFlow Kibana default creds).

---

## 7. Exposure ranking (pre-scan, for triage ordering)

**Agent-control / RCE tier (highest blast radius — you become the operator):**
1. **n8n** — squad-reported CVSS-10 unauth RCE (CVE-2026-21858, *unverified*) + CISA KEV
   CVE-2025-68613; credential-vault scope (every automated SaaS).
2. **OpenClaw** — squad-reported 92% unauth; shell+browser+email; MaaS targeting.
3. **Cheshire Cat** — `/plugins/upload` unauth in-process code-exec; `admin/admin`; forgeable JWT.
4. **Langflow** — CISA KEV CVE-2025-3248 (RCE) + AUTO_LOGIN structural bypass.

**Catastrophic key-leak tier (unauth proxy to paid provider keys):**
5. **LobeChat Mode-A** / **big-AGI** — open + server-side keys = free LLM proxy.
6. **LibreChat** — sleeper: key-encryption-key leak (CVE-2026-32625, *unverified*) decrypts whole key store.

**Data-disclosure tier:**
7. Flowise, RAGFlow, FastGPT, Dify, Open WebUI, Coze, BISHENG, Khoj — KB docs, flow defs,
   stored provider keys, chat history.

**Local-runtime tier (model access + LLMjacking + occasional RCE):**
8. Ollama, oobabooga, LocalAI, Jan, h2oGPT, GPT4All.

---

## 8. Honest negative space

- **SPA-invisible brands:** any platform whose brand string lives only in an unrendered
  React/Next meta tag is Shodan-dark (the AutoGen Studio class, Insight #21). big-AGI title,
  BISHENG title, Khoj SPA title, Cheshire Cat live admin title were all **unconfirmed from
  source** — these need a body/JSON-endpoint dork, not a title dork, and may be under-counted.
- **localhost-default runtimes** (GPT4All) are inherently under-represented on Shodan; absence
  is not absence of population.
- **Rivet** is a desktop app; internet population near-zero unless `rivet-node` debugger bound
  to 0.0.0.0. Likely a null-result platform — that is itself a logged outcome.
- **2026 CVEs + hit-counts are unverified leads**, not facts (see top caveat).
- **PromptFlow `local_user_only`** guard is bypassed by port-forward/container expose — the
  population that matters is the flow-serve `:8080` container tier, not the VS Code dev service.

---

## 9. Candidate Insight (#71, pending survey confirmation)

> **The unauth config endpoint collapses the identity-vs-auth-state gap for the chat-UI tier.**
> Insight #16 warned that a 200 proves identity, not auth state, forcing a separate data-layer
> probe. For modern LLM orchestration front-ends this is solved by the platform itself: each
> ships an unauthenticated config endpoint (`/api/config`, `/auth/config`,
> `/api/trpc/backend.listCapabilities`, `/console/api/setup`, `/api/v1/auto_login`) that
> returns identity AND the auth/registration/claimable state in one request. The verification
> primitive and the fingerprint are the same call. This is a *gift of the SPA architecture*:
> the frontend needs to know its own auth config before render, so it must expose it pre-auth.
> Design the fingerprint on the config endpoint, not the title — it is lower-FP, SPA-render-
> proof, and self-classifying.

---

## Toolchain provenance

Stage -1 executed as 6 parallel `general-purpose`/Sonnet research agents (OSINT Platoon
Alpha–Foxtrot) via the Agent tool, 2026-06-04. Primary sources: GitHub repos, official docs,
GHSA/NVD, default docker-compose/Helm. aimap coverage cross-checked against
`~/ai-recon/aimap`. Next: Stage 0 harvest (Shodan via Playwright per
`feedback_shodan_playwright_only`) using the §10 dork set → `empire.db` →
`visor-chain-runner.sh 01-llm-orchestration`.
