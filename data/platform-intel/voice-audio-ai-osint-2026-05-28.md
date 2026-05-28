# Voice/Audio AI — Pre-Survey SALUTE + Platform Intel Update
**Date:** 2026-05-28
**Purpose:** SALUTE synthesis from 4-squad OSINT platoon run. Addendum to voice-audio-ai-osint-2026-05-27.md. Covers new platforms and CVE batch discovered after the 2026-05-27 initial intel pass.
**Squads:** Alpha (web recon), Bravo (infra fingerprints), Charlie (community intel), Weapons (API surface + CVEs)
**Status:** Pre-survey. Intelligence feeds into aimap fingerprint work and Shodan harvest design.

---

## SALUTE

**S — Size**
14 new platform instances identified beyond the 2026-05-27 catalog. 11 carry CVSS 9.8 CVEs (RVC-WebUI command injection + pickle deserialization chain). 1 cross-platform CVE (BadHost/Starlette) affects every FastAPI-wrapped TTS/ASR server simultaneously.

**A — Activity**
Rapid Docker image proliferation on Kokoro-FastAPI (5+ competing images, GHCR + Docker Hub), Chatterbox (multiple forks within weeks of open-source release), Orpheus-TTS. The trajectory mirrors Ollama's Docker Hub explosion in late 2024. Community is self-hosting voice AI at increasing velocity with zero auth in every default config.

**L — Location**
Same tier-2 cloud operator concentration as Ollama: Hetzner, Contabo, OVH, DigitalOcean. EU GPU VPS providers are actively marketing to voice AI builders. US deployments cluster on AWS (Whisper webservice) and GCP.

**U — Unit**
Mix of framework categories:
- OpenAI-compat TTS servers: Kokoro-FastAPI, Chatterbox, Orpheus, Dia, Parler-TTS, Voxtral-via-vLLM
- Real-time ASR streams: WhisperLive WebSocket (port 9090), wyoming-whisper (TCP port 10300)
- Enterprise on-prem: Deepgram self-hosted, NVIDIA NIM/Parakeet
- Voice-cloning RCE surfaces: RVC-WebUI (11 CVEs), GPT-SoVITS (5 CVEs)

**T — Time**
Kokoro (Jan 2026), Chatterbox (Mar 2025 OS release / rapid 2025-2026 self-host forks), Orpheus (HN front page 2026), Dia (2026), Voxtral (Mar 2026). Population growing now.

**E — Equipment**
Primary attack primitives:
- FastAPI/Uvicorn, no auth concept — Kokoro, Chatterbox, Orpheus, Parler-TTS
- Gradio, no auth — F5-TTS, StyleTTS2, RVC (+ RCE CVEs)
- Wyoming TCP protocol, no auth — wyoming-whisper (ambient audio)
- WebSocket stream, no auth — WhisperLive (live audio capture)

---

## New Platforms (not in 2026-05-27 doc)

### Kokoro-FastAPI

**Category:** TTS (OpenAI-compatible)
**Default Port:** 8880
**HTTP Server:** FastAPI + Uvicorn
**Auth Default:** OFF — API key field accepts `"not-needed"` with no validation. No auth option in default config.
**Docker Images:** `ghcr.io/remsky/kokoro-fastapi-cpu:latest`, `ghcr.io/remsky/kokoro-fastapi-gpu:latest`, `hwdsl2/kokoro-server`, `sebastianboehler/kokoro-tts` — 5+ competing images

**Endpoints:**
- `POST /v1/audio/speech` — TTS synthesis (OpenAI-compat)
- `GET /v1/audio/voices` — voice list (JSON array with `id` fields)
- `GET /v1/models`
- `POST /v1/audio/voices/combine`
- `POST /dev/captioned_speech` — word-level timestamps (project-unique path)
- `GET /debug/system` — CPU/GPU metrics (project-unique path)
- `GET /web` — embedded web UI
- `GET /docs` — Swagger UI

**Definitive Verification Probe:**
```
GET /debug/system HTTP/1.1
Host: <target>:8880
```
Returns JSON with CPU/GPU metrics — no other TTS server exposes this path. Combine with `GET /v1/audio/voices` for belt-and-suspenders.

**Shodan Dorks:**
```
port:8880 http.html:"Kokoro"
port:8880 http.html:"/dev/captioned_speech"
http.title:"Kokoro" port:8880
```

**Known CVEs:** None filed against kokoro-fastapi. Inherits supply-chain risk from pickle/safetensors model loading.

**Severity Class:** Compute theft (GPU TTS on attacker text). Voice cloning via `/v1/audio/voices/combine` if model upload paths exposed.

**aimap Fingerprint Priority:** HIGH — distinctive port + unique endpoint anchors.

---

### Chatterbox TTS Server

**Category:** TTS (voice cloning, zero-shot)
**Default Ports:** 8000 (devnen/Chatterbox-TTS-Server) or 4123 (travisvn/chatterbox-tts-api)
**HTTP Server:** FastAPI + Uvicorn
**Auth Default:** OFF — `documentation.md` explicitly notes auth requires manual addition.
**Docker Images:** `babanovac1980/chatterbox-tts-server` (~234 pulls), plus travisvn fork

**Endpoints (devnen variant, port 8000):**
- `GET /api/model-info` — returns JSON with `"engine"` field (e.g., `"chatterbox-turbo"`) — identity anchor
- `GET /get_predefined_voices`
- `POST /tts` — primary synthesis endpoint
- `POST /v1/audio/speech` — OpenAI-compat
- `GET /v1/audio/voices`
- `GET /docs`

**Endpoints (travisvn variant, port 4123):**
- `GET /health` — health check
- `GET /config` — JSON with chatterbox-specific model fields
- `POST /v1/audio/speech`
- `POST /upload_reference` — upload reference audio for voice cloning (UNAUTH)

**Definitive Verification Probe:**
```
GET /api/model-info HTTP/1.1
Host: <target>:8000
```
`"engine"` field value confirms Chatterbox. Secondary: `GET /get_predefined_voices`.

**Shodan Dorks:**
```
port:8000 http.html:"chatterbox"
port:4123 http.html:"Chatterbox"
http.title:"Chatterbox TTS"
```

**Known CVEs:** None filed. `/upload_reference` is unauthenticated upload surface — resource exhaustion + abuse class.

**Severity Class:** Voice-clone fraud (zero-shot cloning from uploaded reference audio, no auth required). CVSS would be HIGH/CRITICAL if confirmed at population scale.

**aimap Fingerprint Priority:** HIGH — voice-clone fraud class elevates above compute-theft TTS servers.

---

### Orpheus-FastAPI

**Category:** TTS (emotional, 8 voices)
**Default Port:** 8899
**HTTP Server:** FastAPI + Uvicorn
**Auth Default:** OFF
**Docker Images:** `olilanz/ai-orpheus-tts`, `moe003/orpheus-tts`, `nexslerdev/orpheus-fastapi-tts`

**Endpoints:**
- `POST /v1/audio/speech` — OpenAI-compat
- `GET /docs` — Swagger UI
- OpenAPI with emotion tags in model parameters

**Definitive Verification Probe:**
```
GET /docs HTTP/1.1
Host: <target>:8899
```
Port 8899 is near-unique to Orpheus deployments. Swagger will confirm "Orpheus" in schema.

**Shodan Dorks:**
```
port:8899 http.html:"Orpheus"
port:8899 http.html:"/v1/audio/speech"
http.title:"Orpheus TTS"
```

**Known CVEs:** None.

**Severity Class:** Compute theft.

**aimap Fingerprint Priority:** MEDIUM — unique port but smaller population than Kokoro.

---

### Dia-TTS-Server

**Category:** TTS (dialogue, voice cloning)
**Default Port:** 7860 (Gradio) + API port
**HTTP Server:** Gradio + FastAPI (devnen/Dia-TTS-Server wrapper)
**Auth Default:** OFF
**Models:** Dia2-1B (streaming), Dia2-2B (high quality)

**Definitive Verification Probe:**
```
GET /docs HTTP/1.1
Host: <target>:<port>
```
Look for "Dia TTS" in Swagger schema. Gradio variant: `GET /` → HTML with `"Dia TTS"` in title.

**Shodan Dorks:**
```
http.title:"Dia TTS"
http.html:"dialogue" "gradio" port:7860
```

**Known CVEs:** None.

**Severity Class:** Voice cloning (dialogue voice synthesis). Compute theft secondary.

**aimap Fingerprint Priority:** MEDIUM — shares Gradio port with many other platforms; title differentiation needed.

---

### WhisperLive (WebSocket Real-Time ASR)

**Category:** STT (real-time streaming)
**Default Ports:** 9090 (WebSocket), 8000 (REST)
**HTTP Server:** Custom web server + WebSocket handler
**Auth Default:** OFF — CORS configurable but no auth token mechanism.
**Docker Images:** `collabora/whisperlive`, `hwdsl2/docker-whisper-live`

**WebSocket Verification Probe:**
```
ws://<target>:9090/
```
After connect, send:
```json
{"uid": "<uuid>", "language": "en", "task": "transcribe", "model": "tiny.en"}
```
Server responds:
```json
{"uid": "<uuid>", "message": "SERVER_READY"}
```
`"SERVER_READY"` string in WebSocket JSON response is the definitive fingerprint — unique to WhisperLive.

Segment responses: `{"uid":"...","segments":[{"text":"...","start":0.0,"end":2.4,"completed":true}]}`

**REST Verification Probe:**
```
GET /docs HTTP/1.1
Host: <target>:8000
```
Swagger with `POST /v1/audio/transcriptions`.

**Shodan Dorks:**
```
port:9090 "WhisperLive"
port:8000 http.html:"WhisperLive"
port:9090 http.html:"nearly-live implementation"
```

**Known CVEs:** None filed against WhisperLive directly.

**Severity Class:** PII (live audio transcription of users). Any operator running this for meeting transcription, call centers, or ambient monitoring = real-time audio stream accessible without auth.

**aimap Fingerprint Priority:** HIGH — PII severity class, unique WebSocket fingerprint.

---

### wyoming-whisper (Home Assistant / TCP Protocol)

**Category:** STT (TCP protocol, not HTTP)
**Default Port:** 10300
**Protocol:** Wyoming JSONL over raw TCP (NOT HTTP)
**Auth Default:** OFF — Wyoming protocol has no auth layer by design.

**TCP Verification Probe:**
```
# Send over raw TCP (nc/socat):
{"type":"describe"}\n
```
Server responds:
```json
{"type":"info","data":{"asr":[{"models":[{"name":"tiny","languages":["en"],"attribution":{"name":"Systran","url":"https://github.com/guillaumekln/faster-whisper"}}],"installed":true}]}}\n
```
`type == "info"` + `data.asr` is non-empty array = confirmed wyoming-whisper.

nmap probe bytes: `\x7b\x22\x74\x79\x70\x65\x22\x3a\x22\x64\x65\x73\x63\x72\x69\x62\x65\x22\x7d\x0a`

**Shodan:** Does not index raw TCP JSONL. Requires masscan + custom probe. Banner grab only.

**Known CVEs:** None. No encryption, no auth by design.

**Severity Class:** PII — home/office ambient audio transcription pipeline exposed to internet. Domestic surveillance potential. Low compute value; high privacy impact.

**aimap Fingerprint Priority:** MEDIUM — requires non-HTTP probe path; worth adding as a TCP probe module.

---

### Deepgram Self-Hosted (Updated — Auth Confirmed OFF)

**Note:** The 2026-05-27 doc listed Deepgram as "API key required." Weapons squad clarified: NGC key required to PULL the container image, but the HTTP API endpoints themselves (`/v1/status`, `/v1/listen`) require NO per-request auth once the container is running.

**Definitive Verification Probe:**
```
GET /v1/status HTTP/1.1
Host: <target>:8080
```
Response (no auth required):
```json
{
  "system_health": "Healthy",
  "active_batch_requests": 0,
  "active_stream_requests": 0,
  "active_listen_v2_stream_requests": 0
}
```
`"system_health"` + `"active_batch_requests"` in JSON body = definitive Deepgram on-prem identity. No other platform returns this schema.

**Shodan Dorks:**
```
port:8080 http.html:"system_health" http.html:"active_batch_requests"
http.html:"active_stream_requests" http.html:"active_listen_v2_stream_requests"
port:8080 port:9991
```

**Severity Class:** PII + compute theft. Enterprise deployment may process call center audio, medical dictation, legal proceedings at enterprise scale.

**aimap Fingerprint Priority:** HIGH — clean passive indicator, enterprise data exposure class, unique JSON schema.

---

### NVIDIA NIM Parakeet ASR

**Category:** ASR (enterprise grade)
**Default Ports:** 9000 (HTTP), 50051 (gRPC)
**Auth Default:** OFF at runtime — NGC API key required for image pull, but HTTP API does not enforce per-request auth once running.

**Verification Probe:**
```
GET /v1/health/ready HTTP/1.1
Host: <target>:9000
```
Response: `{"status":"ready"}`

Port 9000 (HTTP) + port 50051 (gRPC) co-presence = strong NIM speech indicator.

Transcription:
```
POST /v1/audio/transcriptions HTTP/1.1
Content-Type: multipart/form-data
[file=<audio>, language=multi]
```

**Known CVEs:** NeMo CVE-2025-23304 — pickle deserialization via `safe_instantiate` bypass.

**Shodan Dorks:**
```
port:9000 http.html:'"status":"ready"' port:50051
port:9000 http.html:"NIM"
```

**Severity Class:** Compute theft (GPU inference costs). PII secondary if transcription logs retained.

**aimap Fingerprint Priority:** MEDIUM — two-port co-presence is the cleanest signal but NIM serves multiple model classes on same ports.

---

### Parler-TTS Server

**Category:** TTS (controllable voice attributes)
**Default Port:** 8000 (server variant), 7860 (Gradio variant)
**HTTP Server:** FastAPI (server) / Gradio
**Auth Default:** OFF
**Docker Images:** `fedirz/parler-tts-server`, `feiticeir0/parler_tts` (~210 pulls)

**Verification Probe:**
```
GET /docs HTTP/1.1
Host: <target>:8000
```
The `/v1/audio/speech` request schema includes a natural-language `voice` description field (e.g., `"A female voice with a warm tone"`) — distinctive differentiator from other OpenAI-compat wrappers that use voice IDs.

**Shodan Dorks:**
```
port:8000 http.html:"parler"
http.title:"Parler TTS"
```

**Severity Class:** Compute theft.

**aimap Fingerprint Priority:** MEDIUM.

---

### Fish Speech

**Category:** TTS (SOTA multilingual)
**Default Port:** 7860 (Gradio)
**HTTP Server:** Gradio
**Auth Default:** OFF
**Docker Images:** `fishaudio/fish-speech` (official)

**Verification Probe:**
```
GET / HTTP/1.1
Host: <target>:7860
```
Gradio interface with `"Fish Speech"` in page title.

**Shodan Dorks:**
```
http.title:"Fish Speech"
port:7860 http.html:"fish-speech"
```

**Severity Class:** Compute theft + voice cloning.

**aimap Fingerprint Priority:** LOW — Gradio port collision; title differentiation only.

---

## CVE Batch — Voice/Audio AI (Critical)

### RVC-WebUI (11x CVSS 9.8 — RCE)

All 11 CVEs filed by GitHub Security Lab (GHSL-2025-012 through GHSL-2025-022), published May 2025.

| CVE | Class | Entry Point |
|-----|-------|-------------|
| CVE-2025-43842 | Command Injection | `preprocess_dataset` endpoint |
| CVE-2025-43843 | Command Injection | `extract_f0_feature` endpoint |
| CVE-2025-43844 | Command Injection | `click_train` endpoint |
| CVE-2025-43845 | Code Injection via `eval()` | `change_info_` function |
| CVE-2025-43846 | Unsafe `torch.load` (pickle RCE) | `show_info` |
| CVE-2025-43847 | Unsafe `torch.load` (pickle RCE) | `extract_small_model` |
| CVE-2025-43848 | Unsafe `torch.load` (pickle RCE) | `change_info` |
| CVE-2025-43849 | Unsafe `torch.load` (pickle RCE) | `merge` |
| CVE-2025-43850 | Unsafe `torch.load` (pickle RCE) | `export.py` |
| CVE-2025-43851 | Unsafe `torch.load` (pickle RCE) | `vr.py AudioPre` |
| CVE-2025-43852 | Unsafe `torch.load` (pickle RCE) | `vr.py AudioPreDeEcho` |

**Chain:** Unauth Gradio API → supply malicious `.pth` model path → pickle deserialization → OS command execution.

**This upgrades RVC from "compute theft + voice cloning" to RCE severity class.** Every exposed RVC-WebUI instance is a remote code execution target, not just a compute-theft surface.

### GPT-SoVITS (5x Critical RCE)

| CVE | Source |
|-----|--------|
| CVE-2025-49837 | GHSL-2025-049 |
| CVE-2025-49838 | GHSL-2025-050 |
| CVE-2025-49839 | GHSL-2025-051 |
| CVE-2025-49840 | GHSL-2025-052 |
| CVE-2025-49841 | GHSL-2025-053 |

Same class: command injection + pickle deserialization. GPT-SoVITS port 9880, unauth FastAPI.

### CVE-2026-48710 "BadHost" (Starlette < 1.0.1 — Auth Bypass)

**Cross-platform impact.** Starlette derives `request.url` from `Host` header without sanitization. Attacker injects extra path component to bypass path-based auth middleware. No password required, no victim interaction.

**Affected voice/audio AI servers (all FastAPI-based):**
- Kokoro-FastAPI
- Orpheus-FastAPI
- Chatterbox-TTS-Server (devnen + travisvn)
- Parler-TTS server
- Any custom whisper-asr-webservice wrapper using middleware auth
- Every OpenAI-compat TTS/ASR wrapper running Starlette < 1.0.1

**Patch:** Starlette 1.0.1+ rejects malformed Host headers.

**Population at risk:** Any of the above NOT running behind a reverse proxy (the typical research/homelab deployment pattern). Deployed-without-proxy = fully exploitable.

---

## Priority Queue for aimap Fingerprint Development

| Priority | Platform | Port | Anchor | Severity Class |
|----------|----------|------|--------|----------------|
| 1 | Kokoro-FastAPI | 8880 | `/debug/system` JSON unique | Compute theft + voice clone |
| 2 | Deepgram on-prem | 8080 | `system_health` JSON unique | PII enterprise |
| 3 | Chatterbox TTS (devnen) | 8000 | `GET /api/model-info` → `"engine"` field | Voice-clone fraud |
| 4 | WhisperLive WebSocket | 9090 | `SERVER_READY` in WS JSON | PII (live audio) |
| 5 | Chatterbox TTS (travisvn) | 4123 | `GET /health` + unique port | Voice-clone fraud |
| 6 | Orpheus-FastAPI | 8899 | Unique port + Swagger | Compute theft |
| 7 | Parler-TTS server | 8000 | Natural-language voice field in schema | Compute theft |
| 8 | NVIDIA NIM ASR | 9000+50051 | Two-port co-presence + `/v1/health/ready` | Compute theft |
| 9 | Dia-TTS-Server | 7860 | Gradio + title "Dia TTS" | Voice clone |
| 10 | Fish Speech | 7860 | Gradio + title "Fish Speech" | Compute theft |
| — | Moonshine | N/A | Library only — no HTTP surface | Skip |
| — | SpeechBrain | N/A | Library only — no HTTP surface | Skip |
| — | Distil-Whisper | — | Model identity, not server — fingerprint via faster-whisper-server `/v1/models` | N/A |

---

## Cross-Platform Dorks (New — From Platoon Intel)

```
# OpenAI-compat TTS sweep — catches Kokoro, Orpheus, Chatterbox, Parler, Dia, Voxtral simultaneously
http.html:"/v1/audio/speech" -openai

# Compound multi-modal stack: Whisper + Ollama on same host
port:9000 port:11434

# WhisperLive WebSocket
port:9090 "WhisperLive"

# Deepgram on-prem passive indicator
http.html:"system_health" http.html:"active_batch_requests"

# NVIDIA NIM Speech (HTTP + gRPC co-presence)
port:9000 port:50051 http.html:'"status":"ready"'
```

---

## What Changed From 2026-05-27 Intel

| Update | Detail |
|--------|--------|
| Deepgram runtime auth | Clarified: OFF at runtime (NGC pull only). Upgrade from "low yield" to "HIGH" fingerprint priority. |
| RVC severity class | Upgraded from "compute theft + voice clone" to **RCE** (CVE-2025-43842 to 43852, 11x CVSS 9.8) |
| GPT-SoVITS severity | Upgraded from "voice clone" to **RCE** (5x Critical CVEs) |
| New platforms | Kokoro, Chatterbox, Orpheus, Dia, WhisperLive WS, wyoming probe detail, Parler-TTS server, Fish Speech, NVIDIA NIM, Voxtral |
| Cross-platform CVE | CVE-2026-48710 BadHost (Starlette < 1.0.1) affects all FastAPI-wrapped TTS/ASR |
| Cross-platform dork | `http.html:"/v1/audio/speech" -openai` — entire OpenAI-compat TTS category in one query |

---

*Platoon squads: Alpha · Bravo · Charlie · Weapons*
*NuClide Research 2026-05-28*
