---
type: survey
---

# Speech & Audio AI on Tier-2 Cloud: Auth Posture Survey

_NuClide Research · 2026-05-04_
_Sibling tier-2 expansions: [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md), [`milvus-tier2-cloud-survey-2026-05.md`](milvus-tier2-cloud-survey-2026-05.md), [`chromadb-tier2-cloud-survey-2026-05.md`](chromadb-tier2-cloud-survey-2026-05.md)_

---

## Summary

Mass-scan of port 9000 (whisper-asr-webservice default + faster-whisper-server common) across the same **76 tier-2 /16 ranges (3.55M IPs), Scaleway + OVH + Linode**. **10,991 port-open candidates → 6 confirmed Speech & Audio AI services after honeypot filtering.**

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6935, K7003, S7065

<!-- ksat-tag:auto-generated:end -->

Modest sample size, but the operator pattern is distinctive:

- 3 instances of **whisper-asr-webservice** (Swagger-fronted ASR API, `/asr` + `/detect-language` endpoints)
- 3 instances of **faster-whisper-server** (OpenAI-compat audio API, `/v1/audio/transcriptions` + `/v1/audio/translations`)
- All 6 unauth, anyone on the internet can submit audio to be transcribed at the operator's compute cost
- **2 of 6 are dual-stack with unauth Ollama on the same host**, operators building "local AI swiss army knives" with multi-modal exposure

Speech & Audio AI services are an emerging Tier-A "no auth concept" platform class. Whisper-ASR-Webservice and faster-whisper-server both ship without authentication. They're the audio analog to Ollama: framework default is auth-off, operators who put them on the public internet are exposed.

---

## Methodology

```
masscan -iL <76 tier-2 /16 CIDRs> -p 9000 --rate 8000
  → 10,991 port-9000 candidates

audio-probe.py (200-thread fingerprint)
  GET /            → check for Swagger UI + "asr"/"whisper" strings
  GET /openapi.json → enumerate audio paths (asr, transcriptions, tts, etc.)
  Filter: AS63949 honeypot fleet via salt strings + kitchen-sink JSON
  → 6 confirmed Speech & Audio AI instances
```

Read-only metadata enumeration only. NuClide:
- Did NOT submit any audio file to `/asr` or `/v1/audio/transcriptions`
- Did NOT submit any text to `/api/tts`
- Did NOT exercise `/api/pull/{model_name}` (which would write to operator disk)

---

## Findings Summary

| Metric | Value |
|---|---|
| Tier-2 /16 ranges scanned | 76 |
| Total IPs scanned | 3,550,208 |
| Masscan hits on :9000 | 10,991 |
| AS63949 honeypot pollution filtered | yes (salt-detector applied) |
| Confirmed Speech & Audio AI | 6 |
| Unauthenticated | **6 (100%)**, by framework design |
| whisper-asr-webservice | 3 |
| faster-whisper-server (OpenAI-compat) | 3 |
| Dual-stack with Ollama on same host | 2 |

### Confirmed services with capabilities exposed

| Host | Service | Models | Audio paths |
|---|---|---|---|
| 146.59.218.236 (OVH) | faster-whisper-server | tiny.en, tiny, base, small, **large-v3** (Systran/faster-whisper-*) | `/v1/audio/transcriptions`, `/v1/audio/translations`, `/api/pull/{model_name}`, `/api/ps` |
| 158.69.116.128 (OVH-CA) | faster-whisper "Whisper API" 1.0.0 | (model list endpoint not exposed) | `/v1/audio/transcriptions`, `/health`, `/` |
| 151.80.234.190 (OVH) | whisper-asr-webservice 1.9.1 | (built-in whisper, model selectable per-request) | `/asr`, `/detect-language` |
| 167.114.208.54 (OVH-CA) | whisper-asr-webservice | similar | `/asr`, `/detect-language` |
| 217.182.205.98 (OVH) | whisper-asr-webservice | similar | `/asr`, `/detect-language` |
| 23.239.118.238 (Linode) | faster-whisper variant | similar | `/v1/audio/transcriptions` |

### Dual-stack finding: 146.59.218.236 (OVH)

Single OVH host running **both** unauth Ollama (port 11434) and unauth faster-whisper-server (port 9000):

```
Ollama models on this host:
  llama3.2:3b (3.2B Q4_K_M)
  qwen3:8b (8.2B Q4_K_M)
  qwen3:30b (30.5B Q4_K_M)
  qwen3:30b-a3b (30.5B Q4_K_M)
  qwen3:32b (32.8B Q4_K_M)
  qwen3.6:35b (36.0B Q4_K_M)
  qwen3:235b (235.1B Q4_K_M)   ← serious GPU footprint
  minimax-m2.7:cloud           ← Ollama Cloud quota-theft target

Whisper models on this host:
  Systran/faster-whisper-tiny.en
  Systran/faster-whisper-tiny
  Systran/faster-whisper-base
  Systran/faster-whisper-small
  Systran/faster-whisper-large-v3
```

The operator is running a **multi-modal local AI stack**: ASR (whisper-large-v3) + LLMs up to 235B params + embedding-cloud routing. Anyone can:
1. Submit audio for free transcription using their compute
2. Generate text completions using their 235B-param Qwen or other models
3. Burn the operator's Ollama Cloud subscription via `minimax-m2.7:cloud` prompts

This is the canonical pattern for "operator built a local AI playground and forgot to firewall it." Cost-of-attack: ~$0. Cost-to-operator: variable per-request, scales with usage.

---

## Cross-platform correlations

The audio-AI population is small but meaningfully overlaps with other surveys:

| Cross-cut | Hits |
|---|---|
| Audio host AND Ollama unauth on same IP | 2 of 6 (33%) |
| Audio host on AS63949 honeypot fleet | 0 (filtered) |
| Audio host with cert SAN identifying operator | 1 of 6 (151.80.234.190 → cognistark.com cert) |

The audio-host + Ollama overlap is particularly telling: operators building hybrid AI stacks (transcription + LLM) are doubling their attack surface and giving attackers two free compute pipelines on a single host.

---

## Threat-class taxonomy

For unauth Speech & Audio AI services, three threat classes apply:

### 1. Compute / quota theft
- Submitting audio for transcription consumes operator GPU/CPU at no attacker cost
- For faster-whisper-large-v3, transcription of 1-hour audio takes ~10-30s on GPU, meaningful theft over hours
- Specifically problematic when the operator is paying for GPU rental (e.g., Vast.ai, RunPod), since the bill is per-hour

### 2. Adversarial transcription (generally not applicable to Whisper)
- Whisper isn't a content-classification model, so adversarial-prompt-injection risks are lower than for LLMs
- BUT: whisper-asr-webservice + LLM on the same host (the dual-stack pattern) means adversarial audio that contains spoken instructions can be transcribed → fed to LLM → indirect prompt injection on the operator's stack

### 3. Model-disk-write via `/api/pull`
- faster-whisper-server's `/api/pull/{model_name}` endpoint accepts requests to download additional Whisper models (similar to Ollama's pull). Anyone can trigger arbitrary model downloads on the operator's disk, filling /var/cache/whisper or wherever models are stored. Disk-fill DoS.

---

## Why the small sample?

Two factors:

1. **Port 9000 is not the dominant Speech & Audio AI port across the broader population.** Coqui XTTS commonly runs on 8020. Bark/MusicGen Gradio UIs run on 7860 (which we surveyed in [`gradio-port-7860-survey-2026-05.md`](gradio-port-7860-survey-2026-05.md) but didn't filter for audio specifically). LiveKit/Pipecat voice agents use WebRTC + signaling on various ports. A wider sweep would cover multiple ports.

2. **Speech & Audio AI is still less commonly self-hosted than LLM inference or vector DBs.** The operator population for self-hosted Whisper / TTS is smaller than for self-hosted LLMs (Ollama). Most of the speech/audio audience uses managed services (OpenAI Audio API, Deepgram, AssemblyAI) rather than self-hosting.

The 6 confirmed instances are likely a small fraction of total exposed audio infra. A future expansion would sweep ports 7860, 8020, 5002, 5003, 5005, 6900, plus deeper fingerprinting on port 8000 (Whisper services co-located with vLLM uvicorn).

---

## Disclosure posture

- Per-host disclosures NOT drafted (per the parent project's "no more emails" directive)
- Aggregate finding documented here for the synthesis paper
- One operator identifiable (Cognistark via cert pivot), left for follow-up

If self-hosting speech/audio AI on the public internet:
- Add `--api-key` on startup for whisper-asr-webservice or faster-whisper-server
- Front with a reverse proxy (nginx + basic_auth, Caddy + basicauth, Cloudflare Access)
- Bind to `127.0.0.1` and access only from same-host LLM (the canonical use case for these services)

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis
- [`REMEDIATION-GUIDE.md`](REMEDIATION-GUIDE.md), operator fix-it guide
- [`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md), sibling Tier-A survey, dual-stack overlaps with this one
