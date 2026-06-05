---
title: "Cat-03 Model Serving & Inference — Survey 2026-06-05"
date: 2026-06-05
type: survey
sector: commercial
tags: [llama.cpp, one-api, ollama, open-webui, comfyui, flowise, newapi, default-creds, model-serving, inference]
---

# Cat-03 Model Serving & Inference — Survey 2026-06-05

_NuClide Research · 2026-06-05 · Consumer OpenAI-compat inference servers, audio models, and admin proxies: 28 unauth exposures from 158 live hosts._

## Summary

Survey of 5,018 IPs across 17 Shodan and 9 Censys queries targeting Cat-03 (model serving and inference: llama.cpp, KoboldCpp, LM Studio, Aphrodite Engine, vLLM, SillyTavern, faster-whisper, One API, New API, Open WebUI, SGLang, GPT4All, HuggingFace TGI). 158 hosts responded live; aimap fingerprinted 72 services across 19 classes. One API default credentials (root/123456) confirmed on 10/10 One API instances checked — a class-level default, not individual misconfiguration. Indonesian provincial government running unauth Ollama RAG pipeline with public internet exposure.

## Thesis fit

Extends Insight #40 (auth-on-default strengthens under disclosure pressure): One API and New API bucked this trend — default credentials remain unchanged across the entire surveyed population. Also surfaces Cand #79 (Ollama Connect subscription hijack) and Cand #80 (government AI infra exposure, Cat-03 first gov hit).

---

## Per-finding entries

### F1. `121.28.161.118:3000` — One API

#### What was found

POST `/api/user/login` with `{"username":"root","password":"123456"}` returned HTTP 200, `{"code":200,"data":{"role":100,"username":"root","id":1}}`. Role 100 = full admin. Admin panel provides full user and API key management without additional auth.

#### Why it is bad

Default credentials expose the admin panel for an LLM API multiplexer. Operator has likely provisioned upstream keys (OpenAI, Anthropic) that are now accessible. Verified: admin credential works, role:100 returned. Inferred: upstream API keys may be visible in the admin key management UI.

#### Who it affects

Bare IP (121.28.161.118), no RDNS resolution, no bounty program. aimap-profile: unclassified, 2 hostnames.

#### Tool attribution

- Discovered: aimap fingerprint `one-api-login`, severity CRITICAL
- Verified: curl POST to `/api/user/login`, role:100 confirmed
- aimap-profile: unclassified, no disclosure channel

---

### F2. `121.153.39.157:11434` — Ollama (40 models)

#### What was found

GET `/api/tags` returned 200 with 40 models including `qwen3-embedding:latest`, `minimax-m2.5:cloud`, `deepseek-v4-pro:cloud`. Cloud-suffix models (`minimax-m2.5:cloud`, `deepseek-v4-pro:cloud`) are Ollama Connect remote models — pulling from cloud providers via the operator's subscribed account.

#### Why it is bad

Unauthenticated model listing exposes the operator's full model inventory. Remote cloud models confirm active Ollama Connect subscription, which an attacker could drain via inference requests. Extends Cand #79 (Ollama Connect subscription hijack surface).

#### Who it affects

`ai-open.kr` — Korean research lab (postech-adjacent DNS pattern). aimap-profile: research_lab, MX at `mail.ai-open.kr`.

#### Tool attribution

- Discovered: aimap fingerprint `ollama`, severity HIGH
- Verified: GET `/api/tags` — 40 models enumerated
- aimap-profile: research_lab, Korea

---

### F3. `176.9.85.172:7860` — ComfyUI

#### What was found

GET `/system_stats` returned 200 with `{"system":{"os":"posix","ram_total":67108864000,"cuda_version":"12.8","comfyui_version":"0.17.0"}}`. Full hardware profile: 64GB RAM, CUDA 12.8 host.

#### Why it is bad

Hardware enumeration without auth. ComfyUI 0.17.0 with unauth /system_stats exposes resource profiling useful for targeting or abuse. No access to model weights or workflow data exercised (restraint ethic).

#### Who it affects

`your-server.de` Hetzner VPS. aimap-profile: unclassified.

#### Tool attribution

- Discovered: aimap fingerprint `comfyui`, severity HIGH
- Verified: GET `/system_stats` — system stats confirmed
- VisorGraph: OVH/Hetzner VPS cluster

---

## Survey statistics

| Metric | Count |
|--------|-------|
| Shodan IPs | 4,284 |
| Censys IPs | 1,025 |
| Combined unique | 5,018 |
| Live hosts | 158 (3.1%) |
| Services fingerprinted | 72 |
| CRITICAL | 20 |
| HIGH | 19 |
| MEDIUM | 10 |
| VisorCAS dropped (FP) | 1 (Coqui XTTS) |

## Service class breakdown

| Service | Count | Severity |
|---------|-------|----------|
| llama.cpp server | 16 | MEDIUM |
| One API | 10 | CRITICAL |
| Ollama | 9 | HIGH |
| New API | 8 | CRITICAL |
| Open WebUI | 6 | MEDIUM |
| faster-whisper | 4 | HIGH |
| GPT Researcher | 4 | HIGH |
| Grafana | 2 | HIGH |
| sub2api | 2 | CRITICAL |
| Piper TTS | 2 | LOW |
| Others | 9 | VARIED |

## Candidate insights

**Cand #78** — One API / New API ship with `root/123456` factory defaults and operators do not change them. 10/10 One API instances confirmed admin login with these credentials during verification. This is a class-level default, not random operator oversight — the application defaults to no credential enforcement and operators treat the login page as decorative. Extends the auth-on-default thesis rightward for SaaS-style LLM proxy layers.

**Cand #79** — Ollama Connect cloud-model proxying creates a subscription hijack surface. Operators subscribe to remote cloud models (minimax, deepseek, qwen) via Ollama Connect; those models appear in unauth `/api/tags` and are callable by any internet host. 3 confirmed Connect-active instances in a 158-host corpus (2% hit rate). Impact: cloud subscription drain without operator awareness.

**Cand #80** — Indonesian provincial government (DINAS KOMINFO PROV. JAWA TENGAH, `jatengprov.go.id`) running unauth Ollama RAG pipeline on government infrastructure, publicly internet-indexed. VisorScuba score 2/10. Cat-03 produces the first confirmed government AI infrastructure exposure in this research program (prior surveys found commercial only). Extends the population: model-serving platforms reach government IT more readily than orchestration or vector DB platforms.
