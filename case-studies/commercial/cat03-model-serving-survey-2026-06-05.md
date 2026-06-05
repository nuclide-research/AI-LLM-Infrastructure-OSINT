---
title: "Cat-03 Model Serving & Inference — Survey 2026-06-05"
date: 2026-06-05
type: survey
sector: commercial
tags: [llama.cpp, vllm, koboldcpp, ollama, sillytavern, one-api, newapi, comfyui, ollama-connect, model-serving, inference, false-positive]
---

# Cat-03 Model Serving & Inference — Survey 2026-06-05

_NuClide Research · 2026-06-05 · Consumer OpenAI-compat inference servers. 6 verified unauthenticated exposures; a high false-positive rate in the verification sample drove most aimap CRITICAL/HIGH candidates down to FP or surface-only._

## Summary

Survey of 5,018 IPs across 17 Shodan and 9 Censys queries targeting Cat-03 (model serving and inference: llama.cpp, KoboldCpp, LM Studio, vLLM, SillyTavern, faster-whisper, One API, New API, Open WebUI, SGLang, GPT4All, HuggingFace TGI). 158 hosts responded live; aimap fingerprinted 72 services and flagged 20 CRITICAL / 19 HIGH. Verification of the flagged candidates refuted the majority: the One API/New API default-credential thesis did not hold at population scale (0/9), and four "GPT Researcher", one "Lunary", one "h2oGPT", and two TTS fingerprints were misattributions. Six hosts confirmed genuinely unauthenticated with a 200-with-data read. The most material finding is an unauthenticated Ollama instance proxying a paid Ollama Connect cloud subscription (`deepseek-v4-pro:cloud`), callable by any internet host.

## Thesis fit

The headline result is a verification-stage correction, not a discovery. This survey is a clean illustration of the load-bearing-verification principle: the scan produced 39 CRITICAL/HIGH candidates; the verified-true unauth set is 6. The auth-on-default thesis (Insight #40) is *confirmed* here — One API / New API enforce first-run password setup and the population rejected the documented default — the opposite of the pre-verification framing. Cand #79 (Ollama Connect subscription hijack) is confirmed with hard proof.

---

## Per-finding entries — VERIFIED UNAUTH (200-with-data)

### F1. `121.28.161.118:3000` — One API (operator outlier, not class default)

#### What was found

POST `/api/user/login` with `{"username":"root","password":"123456"}` returned HTTP 200 with `data.role: 100` (root admin). Confirmed admin session on a single host.

#### Why it is bad

Default credentials on this one host expose the admin panel of an LLM API multiplexer (user + upstream-key management). Verified: admin credential works, role:100 returned. NOT exercised: upstream API keys in the admin UI were not read (restraint ethic).

#### Caveat (corrected)

This was the ONLY host of the surveyed One API / New API population that accepted `root/123456`. A 9-host population sweep returned 0/9 (see Cand #78, refuted). This is a lazy-operator outlier, not a class-level default-credential condition.

#### Who it affects

Bare IP, no RDNS, no bounty program. aimap-profile: unclassified.

---

### F2. `121.153.39.157:11434` — Ollama (40 models, cloud-proxied)

#### What was found

GET `/api/tags` → 200 with 40 models including `qwen3-embedding:latest`, `minimax-m2.5:cloud`, `deepseek-v4-pro:cloud`. The `:cloud` models are Ollama Connect remote models served through the operator's subscribed account.

#### Why it is bad

Unauthenticated model inventory disclosure plus an active Ollama Connect subscription reachable by any host. Listing verified; inference not exercised.

#### Who it affects

`ai-open.kr` — Korean research lab. aimap-profile: research_lab, MX `mail.ai-open.kr`.

---

### F3. `176.9.85.172:7860` — ComfyUI

#### What was found

GET `/system_stats` → 200, `{"ram_total":67108864000,"cuda_version":"12.8","comfyui_version":"0.17.0"}`. 64GB RAM, CUDA 12.8.

#### Why it is bad

Unauth hardware/profile disclosure. No workflow or model-weight access exercised.

#### Who it affects

`your-server.de` Hetzner VPS. aimap-profile: unclassified.

---

### F4. `51.15.140.250:8000` — vLLM 0.12.0

#### What was found

GET `/v1/models` → 200, `{"id":"meta-llama/Llama-3.2-3B-Instruct","owned_by":"vllm","max_model_len":512}`. GET `/version` → `{"version":"0.12.0"}`.

#### Why it is bad

Open vLLM inference server, no auth. Model name + version disclosed; free inference available. Synthesis not exercised.

#### Who it affects

Scaleway range (51.15.x). Bare IP.

---

### F5+F6. `108.210.175.159` — home AI-roleplay rig: front door locked, inference backends open (MOST MATERIAL)

A single AT&T residential host (`108-210-175-159.lightspeed.nworla.sbcglobal.net`, Kenner LA) running an enthusiast local-LLM stack on home broadband, alongside a Minecraft server. This is the survey's best chain: the operator secured the UI and left the backends it depends on wide open.

#### What was found

Four services on one box (Shodan saw three; the fourth was Shodan-dark and surfaced only on active probe):

| Port | Service | Auth | Source |
|------|---------|------|--------|
| 8000 | **SillyTavern** (chat front-end) | **Basic auth ON** — `HTTP 401`, `WWW-Authenticate: Basic realm="SillyTavern"` | Shodan |
| 5001 | **KoboldCpp** / KoboldAI Lite | **none** — `Server: KoboldCppServer 1`, `access-control-allow-origin: *` | Shodan |
| 11434 | **Ollama** 0.17.4, cloud-proxied | **none** | active probe only (Shodan-dark) |
| 25565 | Minecraft 1.21.11 "New Bloodsquirrelia" | n/a | Shodan |

- KoboldCpp `:5001` — GET `/openai_api/v1/models` → 200, `{"id":"koboldcpp/gemma-4-31B-it-UD-Q8_K_XL","owned_by":"koboldcpp"}`. Wildcard CORS, allow-headers include `apikey, genkey, Authorization`.
- Ollama `:11434` — GET `/api/tags` → 200, 5 models, one cloud-proxied: `{"name":"deepseek-v4-pro:cloud","remote_model":"deepseek-v4-pro","remote_host":"https://ollama.com:443"}`. Local: `deepseek-r1:70b`, `deepseek-r1:32b`, `llama3:latest`, `smollm2:135m`.

#### Why it is bad

The operator is not naive — SillyTavern (the thing they log into via browser) enforces basic auth. But SillyTavern is only the front-end; it drives the inference backends, and those (KoboldCpp `:5001`, Ollama `:11434`) are independently internet-reachable with no auth. An attacker never touches the authed front door:

```
SillyTavern :8000  [Basic auth OK]  --drives-->  KoboldCpp :5001  [unauth]
                                          \-----> Ollama   :11434 [unauth, cloud-proxied]
```

Direct hits on `:5001`/`:11434` yield the same model access SillyTavern has, plus theft of the paid Ollama Connect cloud subscription (`deepseek-v4-pro:cloud` → ollama.com) — billing/resource drain with zero operator awareness — and unauth access to a local 70B. The auth on SillyTavern is decorative once the dependency graph is exposed. KoboldCpp's wildcard CORS additionally makes `:5001` drive-by-capable from a malicious page in the operator's browser. visorgoose flagged a Connect takeover URL embedding an ed25519 key (host DESKTOP-8SFE9EN); the key was NOT fetched or used (restraint ethic) — the cloud-model listing alone proves the subscription surface.

#### Who it affects

AT&T residential broadband (home user), Kenner LA. Not a business or infra target. aimap mislabelled `:5001` as `h2oGPT` (see FP catalog); the host is genuinely unauth, the fingerprint name was wrong.

#### Tool attribution

- `:5001` discovered by aimap (mislabelled h2oGPT); `:11434` discovered by visorgoose as a shadow port beyond the corpus portlist (Shodan-dark — confirms Insight #77, scanner non-skippable after Shodan)
- Verified: GET `/openai_api/v1/models` (KoboldCpp) and GET `/api/tags` (Ollama cloud-proxied) — both 200 unauth
- `:8000` SillyTavern basic-auth state and `:25565` Minecraft from Shodan host record

---

## Surface-open (access not exercised, not findings)

| Host | Service | State |
|------|---------|-------|
| 108.62.161.37:8080 | sub2api | 401 `API_KEY_REQUIRED` — key-gated (downgrade from CRITICAL) |
| 80.225.185.157:8080 | sub2api | 401 `API_KEY_REQUIRED` — key-gated (downgrade from CRITICAL) |
| 31.192.104.158:8000 | MCP Server | uvicorn streamable-HTTP; mints `mcp-session-id` pre-auth; `initialize` not sent |
| 15.235.9.143:3000 | Grafana 12.4.2 | login surface exposed; anonymous org access OFF (401) |

## False-positive catalog (verification refutations)

The codify-every-survey value of this survey is the FP set. Of the actively-verified CRITICAL/HIGH candidates, the following were refuted:

| Candidate | aimap label | Reality | FP class |
|-----------|-------------|---------|----------|
| 9 hosts (port 3000) | One API/New API default-cred | 0/9 accept root/123456; New API ships first-run password setup | thesis over-extrapolation |
| 129.213.81.173:8888 | unauth Jupyter | `/api/contents` → 403; token-protected | non-404 version banner read as open |
| 37.59.123.209:3000 | Flowise unauth | `/api/v1/chatflows` → 401 | auth-on-default holds |
| 5.9.249.102:3000 | Lunary | CheckRef (scholarly reference app) | `/api/v1/health`+port-3000 too generic |
| 15.235.9.143 / 88.198.67.137 / 34.47.31.176 / 91.99.202.219 :8000 | GPT Researcher (x4) | all the same Gradio "Whisper Playground" | `/api/report` 405 (Gradio FastAPI catch-all) read as endpoint-exists |
| 108.210.175.159:5001 | h2oGPT | KoboldCpp / KoboldAI Lite | label wrong (host IS unauth — F5) |
| 61.171.112.92:8000 | Coqui XTTS + Chatterbox TTS | ZenTao project-management app | two TTS fingerprints collided on port 8000 |
| 172.182.235.102:3000 | Grafana | HTTPS-only; plain-HTTP → 400 | scheme mismatch |
| 121.28.161.118 (10250/8001) | menlohunt kubelet `/exec` + K8s Dashboard | 10250 connection-refused; 8001 is a One API key proxy | menlohunt asserted /exec on a port with no listener |

## Survey statistics

| Metric | Count |
|--------|-------|
| Shodan IPs | 4,284 |
| Censys IPs | 1,025 |
| Combined unique | 5,018 |
| Live hosts | 158 (3.1%) |
| Services fingerprinted | 72 |
| aimap CRITICAL / HIGH candidates | 20 / 19 |
| **Verified unauth (hard proof)** | **6** |
| Surface-open (access not exercised) | 4 |
| Refuted in verification sample | ~21 candidates across 9 FP classes |

## Candidate insights

**Cand #78 — REFUTED.** One API / New API do NOT ship an exploitable factory default at population scale. A 9-host sweep returned 0/9 for `root/123456`; New API requires first-run password setup (`setup:true`, no shipped password to leave unchanged). The single confirmed host (F1) is an operator outlier. This is a textbook verification-stage save: the pre-verification framing ("10/10 class-level default") was an extrapolation from one host and is false. Auth-on-default (Insight #40) is *confirmed*, not bucked.

**Cand #79 — CONFIRMED (hard proof).** Ollama Connect cloud-model proxying is an unauthenticated subscription-hijack surface. Verified on 108.210.175.159:11434 (`deepseek-v4-pro:cloud` → ollama.com, unauth) and 121.153.39.157:11434 (cloud models in a 40-model listing). The `:cloud` suffix + `remote_host` field in unauth `/api/tags` is a reliable marker. Impact: paid cloud-subscription drain with zero operator awareness. Related to Insight #49 (shared Ollama Connect portfolio).

**Cand #80 — RETRACTED.** The "Indonesian government AI exposure" hosts (jatengprov.go.id, kaltaraprov.go.id) are NOT in the Cat-03 corpus. They surfaced because VisorScuba `assess` scores ledger-wide over nuclide.db (all prior surveys, ~25k events) with no per-survey filter; those are prior Ollama-survey carryover. Not a Cat-03 finding. Lesson: scope VisorScuba output to the survey's own ingested events before attributing a finding to the survey.

**Cand #81 (new) — Framework catch-all FP class recurs in model-serving.** Three of this survey's FPs (GPT Researcher via Gradio `/api/report` 405, Lunary via generic `/api/v1/health`, TTS via ZenTao on :8000) are the same structural class as the dcm4chee ASP.NET-catchall and CVAT-IAP-200 FPs: a generic web framework echoing a truthy/non-404 status on the probed path, read by the fingerprint as "endpoint exists." Fix pattern: anchor fingerprints on a positive body marker (vendor string / real JSON shape), not a non-404 status, and add framework negative-matches (e.g. `gradio_config`, ZenTao `zentaosid` cookie).

**Cand #82 (new) — Front-end-secured / backend-exposed asymmetry in enthusiast local-LLM stacks.** The hobbyist roleplay stack (SillyTavern + KoboldCpp + Ollama) exhibits a recurring failure shape: the operator authenticates the UI they personally log into (SillyTavern basic auth) and leaves the inference backends that UI depends on (KoboldCpp `:5001`, Ollama `:11434`) unauthenticated and independently internet-reachable. The defender tried — this is not naivety — but secured the front door while the dependency graph stayed open. An attacker bypasses the authed UI entirely by hitting the backends directly. The attack surface is the dependency graph, not the front door. Verified on 108.210.175.159 (F5+F6). Severity is amplified when a backend carries a paid Ollama Connect cloud subscription (subscription theft, Cand #79) and/or wildcard CORS (browser drive-by). Defensive framing for reporting: securing the UI is necessary but not sufficient; every inference backend needs its own auth and bind-to-localhost.
