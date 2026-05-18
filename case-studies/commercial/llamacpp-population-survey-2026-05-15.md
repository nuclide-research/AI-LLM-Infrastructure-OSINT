---
type: survey
---

# llama.cpp HTTP Server Population Survey (2026-05-15)

_NuClide Research · 2026-05-15 (evening)_
_Companion to:_
- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): the day's earlier Shodan-walk survey of Ollama
- [`alpha-miner-194-233-71-223-2026-05-15.md`](alpha-miner-194-233-71-223-2026-05-15.md): the single-host case that drove the aimap llama.cpp fingerprint addition

---

## Summary

Direct follow-on survey to the day's Ollama work and the aimap v1.9.4 release. aimap v1.9.4 added a `llama.cpp server` fingerprint after the 194.233.71.223 single-host case revealed that PHASE-2 fingerprinting was missing llama.cpp on port 11434 despite an explicit `Server: llama.cpp` HTTP header. This survey is the first population-scale exercise of that fingerprint.

- Shodan harvest: `product:"llama.cpp"` → **1,652 unique candidate IPs** (much smaller corpus than Ollama's 25K, llama.cpp's HTTP-server mode is less ubiquitous)
- Verification via `fast_enum_llamacpp.py` (direct prober, 32.5 seconds at threads=150)
- **965 confirmed unauthenticated llama.cpp servers** (58% confirm rate; 675 dead at probe time)
- **196 hosts with `/completion` + `/v1/chat/completions` unauth-reachable**: the unauthenticated-inference surface, ~20% of confirmed
- **28 hosts colocated on Ollama's port 11434**: the 194.233.71.223 colocation pattern scaled
- **746 hosts (77% of confirmed) expose their chat_template via `/props`**: the operator-customization discovery axis (mirror of Ollama's `/api/show` SYSTEM corpus)
- **29 IPs run BOTH unauthenticated llama.cpp AND unauthenticated Ollama** on the same host. Same-VPS LLMjacking-colocation at 29× the original single-host case

---

## Three macros worth pulling up

### 1. Single-operator commercial deployment: 216 hosts on AS54801 (Zillion Network Inc.)

| Field | Value |
|---|---|
| ASN | AS54801 (Zillion Network Inc., US) |
| Country | US (216 of 217) |
| Common model | `HY-MT1.5-1.8B-Q4_K_M.gguf` (Tencent **Hunyuan-MT 1.5** machine-translation model, 1.8B params, Q4 quantized) |
| Operator profile | Translation-as-a-service or bot-network inference fleet |
| Auth posture | All unauthenticated |

This is the largest operator-attributed cluster in the corpus. The 216-host concentration on a single ASN with identical model loadout is the single-operator fleet signal: one party operates this entire surface. The Hunyuan-MT 1.5 model is Tencent's translation model. Likely a commercial translation-AI deployment serving end users via the unauth HTTP endpoint, or a backend for a third-party translation product.

### 2. Cross-platform colocation: 29 IPs running BOTH llama.cpp AND Ollama unauth

Direct extension of the [194.233.71.223 alpha_miner case](alpha-miner-194-233-71-223-2026-05-15.md). 29 hosts in the corpus run both services unauth on the same VPS. Sample:

```
1.53.228.28       103.28.114.65     117.0.36.6        118.196.128.189
118.67.218.249    147.93.159.154    153.127.86.91     157.173.115.64
159.69.109.189    164.52.211.42     (+19 more)
```

Each is a candidate for the LLMjacking attribution-laundering pattern documented in [[reference_llmjacking_proxy_colocation_pattern]]. Same VPS, two unauth LLM endpoints, redundant compute surface for an attacker / abuser. The single-host case becomes a 29-host class.

### 3. chat_template corpus axis: the llama.cpp analogue of Ollama's `/api/show` SYSTEM

`POST /props` on llama.cpp returns the server's chat-completion configuration including `chat_template`, `n_ctx`, `total_slots`, and `default_generation_settings`. **746 of 965 confirmed hosts (77%) expose `chat_template`.** Frequency-counting the distinct templates:

| Frequency | Pattern | Type |
|---|---|---|
| 218 | `{% if messages[0]['role'] == 'system' %}…` (Llama-3 default) | model-baked default |
| 114 | `{%- set image_count = namespace…}` (Qwen-VL default) | model-baked default |
| 69 + 59 | `{%- if tools %}{{- '<|im_start|>system\n' }}…` (Qwen tools-aware) | model-baked default |
| 42 + 42 | (Other ChatML / im_start variants) | model-baked default |
| 26 + 26 | `{{- bos_token }} {%- if custom_tools is defined %}…` | model-baked default |
| 14 + 11 | bos_token / "thinking" templates | model-baked default |
| **33 distinct** | **operator-customized, frequency ≤ 2** | **the discovery axis** |

Operator-customized chat_template samples (singletons, paraphrased to single line):

- `{#- Copyright 2025-present the Unsloth team…`: operator using Unsloth-fine-tuned custom model
- `mistral-v7`: short-name custom template
- `{# special token variables #} {%- set toolcall_begin…`: custom tool-call surface
- `[gMASK]<sop> {%- macro visible_text(content)…`: ChatGLM-family custom

Codified as **Insight #25 candidate**: chat_template-via-/props is the llama.cpp equivalent of Ollama's Modelfile-SYSTEM-via-/api/show. Same methodology pattern: filter the canonical defaults via frequency-counting; the singleton tail is the operator-deployment corpus.

---

## Heretic / uncensored ecosystem on llama.cpp

The abliterated/uncensored finetune trend documented in the Ollama survey reproduces on llama.cpp at smaller scale. Sample of operator deployments visible via `/v1/models`:

| Host | Model |
|---|---|
| `130.241.35.123` | `Qwen3.6-35B-A3B-Uncensored.Q4_K_P`, `Qwen3.6-35B-A3B-Uncensored.Q4_K_P-think`, `gemma-4-E4B-it-uncensored-Q4_K_M`, `mmproj-Qwen3.6-35B-A3B-Uncensored.f16` |
| `198.13.56.125` | `Qwen3.5-35B-A3B-Uncensored` (+ 2 others) |
| `192.210.149.19` | `mradermacher/Qwen3-0.6B-heretic-abliterated-uncensored-GGUF:Q4_K_M` |
| `185.31.55.198` | `Qwen3-VL-30B-A3B-Thinking-Heretic.i1-Q4_K_M.gguf` (vision-language heretic) |
| `61.206.112.10` | `gemma-4-31B-Mystery-Fine-Tune-HERETIC-UNCENSORED-Thinking-Q4_K_S.gguf` |
| `14.39.148.199` | `gemma-4-26B-A4B-it-heretic.q8_0.gguf` — **n_ctx=262144 (256K context)**, 4 slots |
| **`36.50.27.19` + `161.118.178.134` + `123.19.247.244` + `2.27.62.41`** | **`Gemma-4-*-Uncensored-HauhauCS-Aggressive-Q4_K_*.gguf`** — same operator/researcher signature ("HauhauCS") across 4 hosts |
| `62.56.16.102` | `deepseek-r1-70b-abliterated` AND `gpt-oss-120b-abliterated` (double-uncensored host) |
| `62.113.194.171` | `huihui-qwen36-35b` (huihui_ai family, same operator group as Ollama corpus) |
| `142.171.30.240` | `lightningforce-ai.gguf` — operator-branded model name (on Ollama-port colocation host) |

The `HauhauCS` signature across 4 hosts is its own micro-operator-attribution finding. Same custom Gemma fine-tune family deployed on multiple instances.

---

## Operator-host distribution

| Org | Count |
|---|---|
| **Zillion Network Inc.** | **216** (the HY-MT1.5 fleet) |
| Hetzner Online GmbH | 80 |
| Contabo GmbH | 28 |
| Aliyun Computing Co., LTD | 28 |
| Oracle Corporation | 25 |
| Korea Telecom | 17 |
| OVH SAS | 15 |
| Tencent Cloud (Beijing) | 15 |
| Google LLC | 14 |
| DigitalOcean, LLC | 13 |

Without the Zillion Network single-operator cluster (216), the distribution looks similar to the Ollama corpus: Hetzner + Contabo + OVH + Aliyun + Tencent + Google + DO covering the bulk. **The HY-MT1.5 fleet is the single biggest operator anomaly**, no other survey-class has surfaced a 216-host single-ASN deployment.

---

## Geographic distribution

| CC | Count | Notes |
|---|---|---|
| 🇺🇸 US | 374 | Driven by Zillion Network HY-MT1.5 cluster (216) + AWS/Oracle |
| 🇨🇳 CN | 137 | Aliyun + Tencent backend |
| 🇩🇪 DE | 108 | Hetzner + Contabo |
| 🇫🇷 FR | 34 | |
| 🇰🇷 KR | 27 | |
| 🇫🇮 FI | 26 | |
| 🇬🇧 GB | 18 | |
| 🇯🇵 JP | 18 | |
| 🇷🇺 RU | 17 | |
| 🇮🇳 IN | 17 | |

---

## Toolchain Provenance

```
0. shodan_paginate.py 'product:"llama.cpp"'         →  1,652 unique IPs (32s, 1 dork)
1. fast_enum_llamacpp.py (threads=150, timeout=6s)  →  965 confirmed in 32.5s
2. aimap v1.9.4 -ports 11434,8080,8000 -threads 100 →  cross-validation (50-host sample, 3m2s, 5 services)
3. fast_enum_to_ndjson → visorlog ingest --db nuclide.db   →  677 events landed (288 deduped vs Ollama corpus)
4. visorscuba --db nuclide.db assess                →  AI.C1 fires; AI.C2/C4/H2 are Ollama-specific (rule gap)
5. visorbishop -ip-shadow-all                       →  shadow_unauth_count=0 on every row (Bishop's IP-shadow port set is narrow); 186 misclassified as 'promptfoo' (Bishop FP class — /v1/models endpoint shared with promptfoo)
6. cross-survey diff vs ollama-confirmed.ips        →  29 IPs running BOTH unauth llama.cpp AND unauth Ollama
7. chat_template corpus analysis                    →  61 distinct prefixes; 33 operator-customized (≤2 freq) — the discovery axis
```

---

## Honest negative space

- **aimap v1.9.4 cross-validation FP-rate** is concerning: 5 of 50 sample hosts confirmed on the aimap-v1.9.4 run vs 58% confirm-rate via fast_enum on the same population. Likely cause: aimap's matchFingerprints uses first-match-wins, and Ollama's fingerprint is registered before llama.cpp, so colocation hosts get classified as Ollama. Fix: either reorder fingerprints (llama.cpp before Ollama for port 11434) or remove first-match-wins and report all matches. Flagged for aimap v1.9.5.
- **VisorScuba's Rego rules are Ollama-specific**. AI.C1 (unauth AI service) fires; AI.C2 (Ollama Cloud Connect leak), AI.C4 (gov infra), AI.H2 (gov RAG pipeline) are Ollama-only matchers. llama.cpp survey needs Rego additions: AI.H6 candidate "unauth /completion or /v1/chat/completions = paid-quota theft" (mirror of AI.H1 for Ollama Cloud).
- **VisorBishop's `-ip-shadow-all` reported shadow_unauth_count=0 on every host**. Either Bishop's IP-shadow port set is too narrow for llama.cpp-class adjacents (Open WebUI on 8080, Ollama on 11434, web UIs on 7860 should have surfaced) or there's a probe-timeout issue. Flagged for re-run after Bishop fix.
- **No SYSTEM-prompt-equivalent inside chat_template** for credentials/internal-URLs (parallel to the Ollama null result). chat_templates are Jinja-templated chat formatting; they're not where operators inline secrets.

---

## Tool-update tracker

- **aimap v1.9.4** (shipped earlier today, commit `a888100`): the `llama.cpp server` fingerprint that made this survey possible. **Confirmed it works** on 194.233.71.223 single-host probe + the population-scale `/v1/models owned_by:llamacpp` marker; null/edge-case on the colocation hosts where Ollama wins the first-match race.

---

## Methodology Insight #25 (codify-pending)

> **llama.cpp's `/props` chat_template is the SYSTEM-prompt analogue from Insight #24 at the formatting layer.** Where Ollama's `/api/show` returns a Modelfile with a verbatim SYSTEM directive, llama.cpp's `/props` returns a Jinja chat_template + n_ctx + total_slots + default_generation_settings. The chat_template is operator-modifiable; about 77% of confirmed unauth llama.cpp servers expose it; default templates from upstream model releases account for the top frequency-counts; the singleton tail is the operator-customized deployment fingerprint. Both Insights belong to the same methodology class: **the framework discloses its operator-configured chat-formatting context via an unauthenticated endpoint, and that context is itself the discovery axis.**

To codify: needs a second cross-platform observation (one more LLM-runtime with a similar surface) to validate as a general Insight rather than two parallel observations.

---

## Raw Data

```
~/recon/llamacpp-population-2026-05-15/
├── harvest/
│   ├── shodan_paginate.py
│   ├── llamacpp-product.{jsonl,ips,ip_port,meta.json}     1,652 unique IPs (17 pages, 32s)
├── aimap/
│   ├── fast_enum_llamacpp.py                              direct prober
│   ├── fast_enum.{jsonl,log}                              965 confirmed
│   ├── high-value.jsonl                                   280 high-value subset
│   ├── confirmed.{ips,urls}
│   ├── events.ndjson                                      ECS-schema for visorlog
│   └── aimap-validate.json                                aimap v1.9.4 cross-validation (50-host sample)
├── visorbishop/bishop.{json,csv,log}                      965 targets; 0 ip-shadow hits (Bishop config caveat)
```

---

## See also

- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): the larger sibling survey of the day (Ollama, 16,473 confirmed)
- [`alpha-miner-194-233-71-223-2026-05-15.md`](alpha-miner-194-233-71-223-2026-05-15.md): the single-host case that drove aimap v1.9.4
- [`methodology/insight-24-operator-workload-visibility-via-api-show.md`](../../methodology/insight-24-operator-workload-visibility-via-api-show.md): the Ollama-side discovery axis this survey mirrors on llama.cpp
- aimap v1.9.4 release at github.com/Nicholas-Kloster/aimap (commit `a888100`)
