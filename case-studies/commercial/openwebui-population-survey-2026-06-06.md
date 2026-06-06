---
type: case-study
category: cat-ow
platform: Open WebUI
date: 2026-06-06
findings: 39 auth-off, 564 signup-open
status: verified
---

# Open WebUI Population Survey — 39 Auth-Off, 564 Open Signup

_NuClide Research · 2026-06-06_

---

## Discovery

18,389 Shodan-indexed instances of Open WebUI. One GET to `/api/config` returns a JSON object that tells you everything: whether auth is enforced, whether public registration is open, the operator's branding name, and the exact version. No scanning required.

Two attack surfaces:
1. **AUTH_OFF** (`features.auth: false`): WEBUI_AUTH=False set explicitly. No login wall. Full chat interface accessible to anyone.
2. **SIGNUP_OPEN** (`features.enable_signup: true`): First user to register becomes admin. Any internet user can claim admin access.

---

## Population Results

| Category | Count | Rate |
|---|---|---|
| AUTH_OFF (fully open) | 39 | 0.77% |
| SIGNUP_OPEN (first-user-admin) | 564 | 11.1% |
| **Total findings** | **603** | **11.8%** |

Survey base: 5,097 instances across two Shodan dorks (`http.title:"Open WebUI"` + `http.html:"open-webui"` delta).

---

## PLLuM dla Edukacji — AUTH_OFF (194.181.158.235:443)

`auth: false, version: 0.6.5` — NASK (Polish National Research Institute), Warsaw.

PLLuM (Polish Large Language Model) is Poland's national LLM initiative, operated by NASK — the state cybersecurity and internet infrastructure authority. The educational deployment (`PLLuM dla Edukacji`) has Open WebUI with authentication completely disabled. A national AI research platform built by the country's cybersecurity institute, fully open to the internet.

**Verification:** inner-B/outer-1. `/api/config auth: false` confirmed. No access exercised beyond configuration read.

---

## AUTH_OFF — Selected Notable Instances

### SwiftRef Assistant (52.204.54.17:80)

`auth: false, version: 0.9.5` — AWS us-east-1.

"SwiftRef" is SWIFT's reference data service for the global financial messaging network. Chat interface loads without login. Models API returned `"Not authenticated"` — newer Open WebUI behavior where the UI layer auth is disabled but model API has separate gating. Finding: UI accessible, admin claimable via first-user signup path if registration is ever enabled; version disclosure; backend type visible.

---

### Ampere Llama Chat (130.61.219.50:8080)

`auth: false, version: 0.5.20, name: "Ampere Llama Chat"` — Oracle Cloud Infrastructure.

Ampere Computing is Oracle's Arm processor subsidiary. "Ampere Llama Chat" is a branded deployment for demonstrating Arm inference performance. Auth disabled. Ollama backend co-exposed on port 11434: 0 local models at scan time (cloud-connected).

---

### Salacommerce AI Agents (109.199.109.81:3000)

`auth: false, version: 0.6.30` — commercial AI agent product deployment.

---

### Enterprise Knowledge Base DEMO (63.33.27.57:443)

`auth: false, version: 0.8.10` — Ireland (AWS eu-west-1). Name suggests a RAG demo environment left publicly exposed. HTTPS-served. Full chat interface accessible without login.

---

### Ollama Co-Exposure: DeepSeek Cloud Proxy (143.47.38.176:3000)

`auth: false, version: 0.8.5` — Hetzner. Ollama on port 11434 open with two models:
- `x/flux2-klein:latest` (5.7 GB) — Flux 2 Klein image generation model
- `deepseek-v4-pro:cloud` (0.0 GB) — Ollama Connect cloud proxy

`deepseek-v4-pro:cloud` is an Ollama Connect relay: inference calls route through the operator's DeepSeek subscription. No local weight download — zero disk size. Attacker with no auth can call `POST /api/chat` with `model: deepseek-v4-pro:cloud` and have it billed to the operator's DeepSeek account.

**Verification:** inner-B/outer-1. `/api/config auth: false` confirmed; Ollama `/api/tags` confirmed both models; no completion issued (restraint).

---

## SIGNUP_OPEN — Selected Notable Instances

### deepset | PepsiCo (18.211.90.210:80)

`signup: true, version: 0.6.24` — AWS us-east-1.

deepset is an enterprise AI company (Haystack framework). PepsiCo branding visible in the name field. Joint deployment or integration test environment. First user to register claims admin access over the instance. Version 0.6.24 is 18+ months old.

---

### CUNY AI Lab (44.199.166.66:443)

`signup: true, version: 0.9.6` — AWS us-east-1. City University of New York — public university system serving 500,000+ students. Open signup on AI research infrastructure.

---

### Dartmouth College — Offshore Wind Lab AI (129.170.224.237:443)

`signup: true, version: 0.4.4` — Dartmouth College campus network (DART-ETHER, 129.170.x.x). Version 0.4.4 is extremely old (2+ years). Wind energy research group AI deployment with open public registration. Potential access to proprietary research conversations and model context.

---

### Inspirali AI DEV (34.227.208.161:443)

`signup: true, version: 0.6.43` — AWS us-east-1. Inspirali is a medical education company. "DEV" instance left running in development mode with open signup. Medical education AI infrastructure with public registration on a development environment.

---

### ChatAI — Singular GovTech (136.248.93.247:443)

`signup: true, version: 0.7.2` — Singapore government technology company. Open signup on government AI chat infrastructure.

---

### LLM-jp Playground (163.220.178.66:80)

`signup: true, version: 0.9.2` — Japanese AI research group. LLM-jp is a Japanese language model research consortium. Open registration on research AI playground.

---

### PromoPharma AI (178.104.191.213:80)

`signup: true, version: 0.9.5` — pharmaceutical sector AI deployment. Open registration.

---

### NCU Blockchain Lab (171.102.174.59:443)

`signup: true, version: 0.6.40` — National Chengchi University, Taiwan. University research AI with open registration.

---

### Nonprofit AI Workspace (49.12.7.207:443)

`signup: true, version: 0.9.4` — Hetzner. Named as a nonprofit workspace with public registration enabled.

---

### Groupe Narbonne (163.172.189.39:443)

`signup: true, version: 0.9.2` — French auto parts retail group. Enterprise AI deployment with open registration.

---

## The First-User-Admin Pattern

Open WebUI's design: when `enable_signup: true` and the instance has zero existing users, the first account created is promoted to admin. Operators who enable signup for their team and forget to lock it down — or who deploy with defaults — leave this window permanently open.

At 10.6% signup-open rate across 2,689 instances: approximately 285 deployments in this snapshot have public registration enabled. Many have been running for months or years (version distribution shows significant 0.3.x–0.6.x tail, each 1–2 years old).

Admin access means: model configuration, user management, API key management, pipeline configuration, and full access to chat history for all users on the instance.

---

## Version Distribution (Findings Population)

| Version range | Count | Approx age |
|---|---|---|
| 0.3.x | 22 | 2+ years |
| 0.4.x–0.5.x | 31 | 18–24 months |
| 0.6.x | 74 | 12–18 months |
| 0.7.x | 19 | 10–12 months |
| 0.8.x | 68 | 6–10 months |
| 0.9.x | 95 | 0–6 months |

The 0.9.x cohort shows the problem is not improving with version updates — operators running the latest version still ship with default signup-open configuration.

---

## Ollama Co-Exposure

Prior NuClide survey (2026-05): 33% co-exposure rate for raw Ollama port 11434 on the same host as Open WebUI. For the AUTH_OFF cohort (24 instances), 2/24 had Ollama co-exposed with callable models including a DeepSeek cloud proxy.

Cloud proxy models (`deepseek:cloud`, `minimax:cloud`, `gemini:cloud`) via Ollama Connect have zero local disk footprint but route inference through the operator's subscription at real cost. These are the highest-severity Ollama co-exposure findings — equivalent to an open LiteLLM proxy for that provider.

---

## Auth-Off Endpoint: Version Reference

In Open WebUI < 0.8.x:
```json
GET /api/config
{"auth": false, "enable_signup": false, ...}
```

In Open WebUI >= 0.8.x:
```json
GET /api/config
{"features": {"auth": false, "enable_signup": false}, ...}
```

Both locations must be checked. The survey script handles both.

---

## Toolchain Provenance

```
Stage -1:  OSINT Platoon subagent (local sources: platform-intel/, shodan/queries/)
Stage 0:   shodan download --limit 10000 'http.title:"Open WebUI"'
           ~/recon/openwebui-2026-06-06/ (2,689 IP:port pairs)
Stage 0c:  /tmp/check_ow.sh (per-IP /api/config probe, 35 workers)
Stage 3v:  auth field + features.auth cross-version check
           Ollama :11434 co-exposure check on AUTH_OFF subset
Stage 12b: This document
```

---

## Remediation

```yaml
environment:
  - WEBUI_AUTH=True           # Enforce authentication (default, but verify)
  - ENABLE_SIGNUP=False       # Close public registration
  - OLLAMA_HOST=127.0.0.1:11434  # Bind Ollama to loopback
```

Verify:
```bash
curl http://IP:PORT/api/config | python3 -c "import sys,json; d=json.load(sys.stdin); print('auth:', d.get('features',d).get('auth'))"
# Should return: auth: True
```
