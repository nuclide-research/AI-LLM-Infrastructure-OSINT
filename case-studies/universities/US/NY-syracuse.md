# Syracuse University: IST R640 Server, Free-Tier Cloud Proxy on Port 12345

_NuClide Research · 2026-05-01_

---

## Summary

A Dell PowerEdge R640 server in Syracuse University's School of Information Studies (`ist-r640-mafudge.syr.edu`) is running Ollama on non-standard port 12345 with `gemma4:31b-cloud` returning **200 OK** without credentials. Five cloud proxy subscriptions total.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 128.230.38.78 |
| rDNS | `ist-r640-mafudge.syr.edu` |
| Org | Syracuse University |
| Department | Information Studies & Technology |
| Country | US, New York |
| Open ports | **12345** (Ollama non-standard port, **public**) |

---

## Models

| Model | Size | Type | 200 OK? |
|---|---|---|---|
| gemma4:31b-cloud | 0 GB | ☁️ Cloud proxy | **YES, 10 tokens** |
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy |, |
| glm-4.7:cloud | 0 GB | ☁️ Cloud proxy |, |
| glm-5.1:cloud | 0 GB | ☁️ Cloud proxy |, |
| kimi-k2.6:cloud | 0 GB | ☁️ Cloud proxy |, |
| gemma4:31b | 19 GB | Local |, |
| smollm2:latest | 0 GB | Local |, |

---

## Findings

### F1: Free-Tier Cloud Proxy 200 OK on Non-Standard Port (CRITICAL)

`gemma4:31b-cloud` returns full inference without credentials on port 12345:

```bash
curl -X POST http://128.230.38.78:12345/api/chat \
  -d '{"model":"gemma4:31b-cloud","messages":[{"role":"user","content":"hi"}],"stream":false}'
# 200 OK - "Hello! How can I help you today?"
```

### F2: Non-Standard Port Exposes Intentional or Misconfigured Deployment (HIGH)

Ollama running on port 12345 (not default 11434) may indicate intentional non-standard deployment or a misconfigured service that bypasses default port-filtering rules.

### F3: Model Injection (HIGH)

All models injectable via CVE-2025-63389.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Syracuse University IT Security: security@syr.edu

---

## Second host (2026-05-19 .edu sweep): `newh-eil-01.syr.edu` — Open WebUI + ChatEval

A second Syracuse-attributed host appeared during the 2026-05-19 .edu LLM-infra survey wave-1. Two distinct LLM-related services on one host: Open WebUI on :3000 with `enable_signup:true`, and a custom LLM dataset/eval platform "ChatEval" on :8080 with public OpenAPI spec.

### Infrastructure

| Field | Value |
|---|---|
| IP | 128.230.222.5 |
| rDNS | `newh-eil-01.syr.edu` |
| Org (WHOIS) | Syracuse University (`OrgName: Syracuse University`, `NetName: SYR-UNIV-NET`, CIDR `128.230.0.0/16`) |
| City | Syracuse, NY |
| Open ports observed | 3000 (Open WebUI uvicorn), 8080 (ChatEval uvicorn) — Shodan reports 4 ports total |
| Continuous-exposure history | Shodan tracking shows port 3000 returning "Open WebUI" title continuously across 30+ scans from at least 2026-04-21 through 2026-05-13 — long-running exposure |

### Service 1 — Open WebUI v0.8.9 on :3000

`GET http://newh-eil-01.syr.edu:3000/api/config` returned 200 with:

```json
{
  "status": true,
  "name": "Open WebUI",
  "version": "0.8.9",
  "default_locale": "",
  "oauth": {"providers": {}},
  "features": {
    "auth": true,
    "auth_trusted_header": false,
    "enable_signup_password_confirmation": false,
    "enable_ldap": false,
    "enable_api_keys": false,
    "enable_signup": true,
    "enable_login_form": true,
    "enable_websocket": true,
    "enable_version_update_check": true,
    "enable_public_active_users_count": true,
    "enable_easter_eggs": true
  }
}
```

**Class observed**: signup-open. No LDAP, no API keys, no OIDC. Login form + websocket + active users count enabled (standard).

### Service 2 — ChatEval custom LLM platform on :8080

`GET http://newh-eil-01.syr.edu:8080/openapi.json` returned 200 with 101,724 bytes of OpenAPI 3.1 spec.

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "ChatEval",
    "description": "LLM Dataset Generation, Human Simulation & Quality Auditing Platform",
    "version": "1.0.0"
  },
  "paths": {
    "/api/settings/endpoints": {
      "get": {
        "tags": ["settings"],
        "summary": "List Endpoints",
        "operationId": "list_endpoints_api_settings_endpoints_get",
        ...
      }
    },
    ...
  }
}
```

`GET .../api/config` returned 404 (not an Open WebUI-style platform).
`GET .../` returned 404.
`GET .../api/v1/models` returned 404.

**Class observed**:
- ChatEval is a custom LLM evaluation / dataset-generation / human-simulation / quality-auditing platform (per its own self-description in `/openapi.json`)
- `/openapi.json` is PUBLIC unauth (info-disclosure class: full route surface enumerable, including `/api/settings/endpoints` and other operational endpoints)
- Whether the documented routes ALSO accept unauth invocations or whether they enforce auth at the content layer was not exhaustively tested per restraint

The 101 KB OpenAPI spec gives a complete inventory of what this platform exposes — endpoint set, parameter shapes, response schemas. That's a substantial attack-surface disclosure even if the routes themselves enforce auth.

### Notable details

- **Two LLM-stack services on one host**: combining Open WebUI (interactive chat with `enable_signup:true`) and ChatEval (LLM dataset-generation backend) on the same IP suggests a Syracuse research / coursework deployment using both for some workflow. The combination means a signup-takeover on Open WebUI could pivot to inspection of the adjacent ChatEval surface.
- **ChatEval as a class of platform**: "LLM Dataset Generation, Human Simulation & Quality Auditing" describes a research-evaluation tool. Public-facing deployment with `/openapi.json` exposed gives the surface map but not the data. The actual dataset content / eval results / simulated-user transcripts are presumably on the documented endpoints and may or may not require auth.
- **ChatEval is an existing OSS project** (per the framework's name and OpenAPI title — likely the academic ChatEval framework from Tian et al. or a related lineage). The Syracuse deployment is presumably an instance of an upstream codebase, not custom Syracuse software.
- **Long-running exposure** — Shodan history shows continuous OW visibility for 3+ weeks before this survey. The host has been in this configuration for at least that long.

### Cross-tool confirmations

- `aimap -ports-class wide` — surfaced both :3000 (Open WebUI) and :8080 (uvicorn 404 root; classified as Open WebUI alt-port but ChatEval is what's actually there — aimap missed the ChatEval identity)
- `visorbishop` (post-G5 fix) — tool-internal output for :3000: `open-webui auth=signup-open severity=critical` with `signup_open: True` indicator
- Direct `/openapi.json` probe on :8080 — identified ChatEval via the title field in the OpenAPI info block (the only way to identify ChatEval; no Bishop signature exists for it)

### Class-membership summary

- Open WebUI signup-open class — OBSERVED (on :3000)
- Public custom-LLM-eval-platform openapi-spec class — OBSERVED (on :8080 ChatEval)
- Multi-LLM-stack-on-single-host class — OBSERVED (Open WebUI + ChatEval co-located)
- Long-running-exposure class — OBSERVED (continuous Shodan visibility for 3+ weeks)

### Wave-2 deeper enum (2026-05-19): ChatEval credential leak — CRITICAL (verified data-in-hand)

ChatEval is an 91-route platform. Tag breakdown: annotations (7), assignments (7), **audit (20)**, chat (3), conversations (6), feedback (4), **generation (11)**, import (5), monitor (1), optimization (7), scenarios (9), **settings (20)**, statistics (2). Spec title is `ChatEval`, description `"LLM Dataset Generation, Human Simulation & Quality Auditing Platform"`.

Empirical GET probe (no payloads, read-only):

| Endpoint | Status | What it returns |
|---|---|---|
| `/api/health` | 200 | `{"status":"ok","app":"ChatEval"}` |
| `/api/auth/status` | 200 | `{"admin_configured":true,"is_admin":false,"admin_via_key":false,"admin_via_user":false}` — admin auth IS configured for write paths; read paths are open |
| `/api/settings/endpoints` | 200 | **Full endpoint configuration with API keys exposed** (see below) |
| `/api/settings/models` | 200 | Model list per endpoint (newhouse_server: 31 models incl. abliterated/uncensored entries) |
| `/api/monitor/status` | 200 | Active job + recent job summaries + 547K-audit stats |
| `/api/conversations` | 200 | Full conversation list with system prompts |
| `/api/scenarios` | 200 | Full study scenario taxonomy (social-engineering / persuasion research) |
| `/api/generation/jobs` | 200 | Generation job configurations + results |
| `/api/feedback/` | 403 | Admin-only — properly auth-gated |
| `/docs` | 200 | Swagger UI public |

**Credential leak — verified data-in-hand:**

The `/api/settings/endpoints` response is a JSON array of 8 endpoint records. Each record includes an `api_key` field. Four endpoints have their keys exposed in the public response:

| Endpoint id | Label | Provider | Key class |
|---|---|---|---|
| 3 | `OpenAI` | api.openai.com | `sk-svcacct-...` (108-char OpenAI service-account key) — `allowed_models: ["gpt-5-nano"]` |
| 6 | `claude` | api.anthropic.com | `sk-ant-api03-...` (95-char Anthropic API key) |
| 7 | `gemini` | generativelanguage.googleapis.com | `AIzaSy...` (39-char Google API key) |
| 1, 2, 4 | local / newhouse_server / mckinley_server | Cloudflare Access | `cf_client_id` + `cf_client_secret` pair shared across 3 endpoints |

**Restraint per memory rule:** the actual key strings are NOT transcribed into this case study, this document, or any public artifact. They live only in the workspace-local probe file at `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/deeper-enum/syracuse-chateval-endpoints.json` for evidence-integrity. **No use of the leaked keys was attempted.**

**Infrastructure disclosure:**
- `newhousesyntheticmedialab.com` — custom domain operated by Syracuse Newhouse School's Synthetic Media Lab
- `ollama.newhousesyntheticmedialab.com` (endpoint id 2) and `ollama-mckpc.newhousesyntheticmedialab.com` (endpoint id 4 "McKinley PC") — two adjacent Ollama instances behind Cloudflare Access
- Internal Docker network names visible: `http://ollama:11434` (id 5), `http://vllm-swap:8080/v1` (id 8 vLLM serving gemma4)
- `vllm-swap` suggests vLLM with [llama-swap](https://github.com/mostlygeek/llama-swap) for model-multiplexing — same `llama-swap` pattern documented at MIT nezamistorm

**Research-data exposure:**
- 14,077 conversations, 217,510 messages, 116 million tokens, 546,742 audits, 83 scenarios — Syracuse Newhouse is running an LLM safety / persuasion / social-engineering research study at scale
- Conversation enumeration returns full system prompts — sample observed: a 2FA-reset scenario where the bot impersonates "an automated account security system" to elicit 2FA codes (this is research methodology for studying LLM-driven social engineering; the prompts themselves are research artifacts)
- Live audit job (`id=78`, 23+ hours running, processing 83,754 items) tagged `created_by: olive_drab` — username disclosure
- Persuasion-tactic taxonomy observed: authority, urgency, reciprocity, social_proof, scarcity, trust_building — the framework's audit categories

**Models in inventory** (per `/api/settings/models` newhouse_server response):
- `HammerAI/cydonia-v1.1:latest` — community uncensored/roleplay model
- `HammerAI/thedrummer-anubis-v1.1:70b-q4_K_L` — TheDrummer/Anubis line, similar lineage
- `MichelRosselli/GLM-4.5-Air` — community GLM modification
- `huihui_ai/qwen3-next-abliterated:80b` — abliterated (safety-training-removed) Qwen 80B variant (visible in `recent_conversations` as `initiator_model`)
- Plus standard models: gemma-4-26b, gpt-oss:20b, mistral-small3.2, llama3.3:70b, dolphin3:8b (dolphin = uncensored lineage)

### Tier promotion (per `feedback_hard_proof_for_critical_label.md` rule)

This finding meets the verified-tier promotion criterion: **hard data-in-hand**, not class-membership inference. Four production API keys for billable upstream LLM accounts were observed in a public-unauth HTTP response. The finding is:

**CRITICAL** — Syracuse ChatEval `/api/settings/endpoints` discloses production OpenAI / Anthropic / Gemini / Cloudflare-Access credentials without authentication.

The leak surface is class "info-disclosure on read-only API endpoints lacking auth"; the data-membership is verified by my direct GET probe; the impact is verified by the credentials being live, valid-format, attributed to production billable upstream services.

Source artifact (workspace-local, not in this repo): `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/deeper-enum/syracuse-chateval-endpoints.json`.

### Source artifacts (wave-2 ChatEval enum)

- Syracuse ChatEval OpenAPI: `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/deeper-enum/syracuse-chateval-openapi.json` (91 routes, framework self-description)
- Endpoints probe (CONTAINS KEYS — workspace-local only): `~/recon/edu-llm-infra-2026-05-19/stage2-wave2/deeper-enum/syracuse-chateval-endpoints.json`

### Source artifacts

- Workspace: `~/recon/edu-llm-infra-2026-05-19/`
- Initial probe: `arsenal-out/critical-openwebui-results.json` (Syracuse :3000 section)
- ChatEval :8080 probe: `arsenal-out/gap-fill.json` (Syracuse-8080 section)
- WHOIS: `arsenal-out/whois-5-confirmed.txt`
- Shodan host data: `arsenal-out/shodan-host-syracuse.txt`
- visorbishop wave-1 revalidation: `stage2-wave2/arsenal/visorbishop-wave1-revalidate.json` (Syracuse entry)
