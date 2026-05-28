# Voice/Audio AI — Shodan Query Catalog
_Generated: 2026-05-27 from pre-survey OSINT pass (12 platforms)_
_See: data/platform-intel/voice-audio-ai-osint-2026-05-27.md for full intel_

---

## Whisper / faster-whisper / whisper.cpp
**Auth default:** none (no auth concept across all variants)
**Exposure class:** Transcribed audio content, free GPU compute abuse, audio upload cache

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `"openai-whisper-asr-webservice" port:9000` | Exact Docker image banner from onerahmet/openai-whisper-asr-webservice; appears in HTTP server header | Low |
| secondary | `"whisper.cpp" port:8080` | whisper.cpp literal string in HTTP response + canonical port | Low |
| title-filtered | `http.title:"Whisper" "uvicorn" -product:"Microsoft IIS"` | Gradio/FastAPI Whisper UIs; uvicorn confirms Python stack | Med |
| faster-whisper | `http.html:"faster-whisper" -http.html:"wakehealth"` | faster-whisper string in HTML source | Med |
| wyoming-tcp | `port:10300` | Wyoming protocol port (TCP, not HTTP — limited Shodan coverage) | High |
| cpp-inference | `"whisper.cpp" "/inference"` | C++ server endpoint literal in banner | Low |
| html-anchor | `http.html:"WhisperX"` | WhisperX word-level alignment variant | Low |
| identity-probe | `GET /` on port 9000 → `"ASR"` in title; `POST /inference` on 8080 → JSON `{"text":"..."}` | — |

**FP note:** `http.title:"Whisper"` alone returns Wake Forest WHISPER clinical portal (ColdFusion/IIS), government-authorized-use banners, and unrelated chat apps. Required filters: `-http.html:"wakehealth"` `-http.html:"actLogin.cfm"` `-product:"Microsoft IIS"`. Never run the bare title dork without anchors.

---

## Coqui TTS
**Auth default:** none (binds 0.0.0.0:5002, no auth shipped)
**Exposure class:** Free TTS compute, deepfake audio generation, speaker-embedding upload path traversal

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5002 http.html:"api/tts"` | Port + endpoint path combination; `/api/tts` is Coqui-specific at this port | Low |
| secondary | `port:5002 "coqui"` | Port + brand string in banner | Low |
| openai-compat | `port:5002 http.html:"v1/audio/speech"` | OpenAI-compatible endpoint path in HTML docs | Low |
| marytts | `port:5002 http.html:"/locales"` | MaryTTS-compatible endpoint on Coqui server | Med |
| port-only | `port:5002 http.html:"tts"` | Broad — catches Coqui + AllTalk + Mozilla TTS legacy | Med |
| identity-probe | `GET /api/tts?text=test` → 200 + audio/wav; `GET /` → HTML containing `"Coqui"` | — |

**FP note:** Port 5002 also used by VMware vCenter; `http.html:"api/tts"` kills VMware FPs cleanly. Port 5002 + `"tts"` alone still catches Mozilla TTS legacy — acceptable since same exposure class.

---

## AllTalk TTS
**Auth default:** none (no auth concept; API port 7851 + Gradio port 7852 both open)
**Exposure class:** Full TTS engine control, voice inventory, GPU/DeepSpeed runtime control, RVC voice conversion

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7851 http.json:"engines_available"` | AllTalk-specific JSON field in `/api/currentsettings` response | Low |
| secondary | `port:7851 http.json:"current_engine_loaded"` | Second AllTalk-unique JSON field | Low |
| tertiary | `port:7851 http.json:"manufacturer_name"` | Third distinctive field; value is always `"Coqui"` | Low |
| gradio-ui | `port:7852 http.html:"AllTalk"` | Gradio UI port with AllTalk title | Low |
| combined | `port:7851 "alltalk"` | Brand string in banner | Low |
| identity-probe | `GET /api/currentsettings` → 200 + JSON with `engines_available`, `current_engine_loaded`, `manufacturer_name:"Coqui"` | — |

**FP note:** Port 7851 is distinctive — low ambient use. `engines_available` as a JSON field is AllTalk-unique. No significant FP classes identified.

---

## RVC (Retrieval-based Voice Conversion)
**Auth default:** none (Gradio, no auth; `--host 0.0.0.0` exposes all interfaces)
**Exposure class:** Voice model files, arbitrary voice conversion, training pipeline, uploaded celebrity voice models

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:7865 http.html:"Retrieval-based-Voice-Conversion"` | Full project name in Gradio HTML; specific to RVC | Low |
| secondary | `port:7865 http.html:"rvc-webui"` | Docker image name appears in source | Low |
| rvc-boss | `http.html:"RVC-Boss" port:7865` | GPT-SoVITS/RVC-Boss variant | Low |
| title | `port:7865 http.title:"RVC"` | UI title; shorter but FP-prone without port anchor | Med |
| gradio-api | `port:7865 http.html:"/run/predict"` | Gradio API endpoint always present; anchored to RVC port | Med |
| port-7897 | `port:7897 http.html:"voice"` | Alternative RVC port in some forks | High |
| identity-probe | `GET /` → Gradio HTML; `GET /info` → JSON `{"label":"RVC..."}` | — |

**FP note:** Port 7865 is Gradio fallback when 7860 is occupied — other Gradio apps can land here. `http.html:"Retrieval-based-Voice-Conversion"` is the reliable discriminator; never drop it.

---

## GPT-SoVITS
**Auth default:** none (API localhost by default but Docker exposes 0.0.0.0 on all five ports; four WebUI ports have unauthenticated RCE CVEs)
**Exposure class:** Voice cloning (1-min audio), model file path traversal, command injection RCE (CVE-2025-49833/34/35/36)

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:9880 http.html:"GPT-SoVITS"` | API port + brand name; tight combination | Low |
| secondary | `port:9872 http.html:"GPT-SoVITS"` | Inference WebUI port | Low |
| api-endpoint | `port:9880 http.html:"/set_gpt_weights"` | API endpoint path distinctive to GPT-SoVITS | Low |
| docker-range | `port:9874 http.html:"GPT-SoVITS"` | Main training WebUI port | Low |
| cve-rce | `port:9871 http.html:"GPT-SoVITS"` | Proofreading tool port; CVE-affected | Low |
| broad | `http.html:"GPT-SoVITS"` | Any port — catches all five exposed ports | Med |
| identity-probe | `GET /` on 9872 → Gradio HTML with `"GPT-SoVITS"` title; `GET /control` on 9880 → JSON `{"message":"..."}` | — |

**FP note:** `GPT-SoVITS` is a distinctive brand string with no collision class. Port range 9871-9874 and 9880 is specific to this project. Low FP risk across all queries.

**CVE note:** Hosts matching port 9871-9874 dorks are candidates for CVE-2025-49833/34/35/36 (unauthenticated RCE via command injection). Verify before asserting exploitability.

---

## Pipecat
**Auth default:** none (WebSocket transport; "best suited for prototyping and controlled network environments" per docs)
**Exposure class:** Live voice agent interaction, LLM API key exposure via file-read CVEs, audio stream interception

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"pipecat-ai"` | GitHub org name in page source; Pipecat-specific | Low |
| secondary | `http.html:"pipecat" "daily.co"` | Framework + parent company API co-occurrence in demos | Low |
| websocket | `port:8765 "pipecat"` | Default WebSocket transport port + brand | Med |
| gradio | `port:7860 http.html:"pipecat"` | Gradio-wrapped Pipecat demos | Med |
| identity-probe | WebSocket connect port 8765 → server accepts upgrade; HTTP `GET /` → FastAPI docs page if dev runner active | — |

**FP note:** Port 8765 is widely used for WebSocket development servers. Without the `"pipecat"` anchor this is useless. `http.html:"pipecat-ai"` is the cleanest signal.

---

## LiveKit
**Auth default:** JWT required for room operations; but health endpoint on port 7880 accessible; many self-hosters expose API directly without reverse proxy
**Exposure class:** Room metadata, participant telemetry via Prometheus (port 6789), TURN credential leaks, SIP trunk exposure

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.headers:"X-LiveKit-Server" port:7880` | Response header confirmed in LiveKit SDK docs; version-bearing | Low |
| secondary | `port:7880 "livekit"` | Port + brand string in banner | Low |
| html | `port:7880 http.html:"livekit"` | HTML content on API port | Low |
| prometheus | `port:6789 "livekit"` | Prometheus metrics endpoint, unauthenticated by default | Low |
| sip | `port:5060 "livekit"` | SIP integration, optional | Med |
| identity-probe | `GET /` on port 7880 → HTTP 200 + `X-LiveKit-Server: livekit/x.x.x` response header | — |

**FP note:** `X-LiveKit-Server` header is the near-zero-FP fingerprint. Port 7880 has low ambient traffic. Prometheus on 6789 is unauthenticated — separate survey target worth running independently.

---

## Deepgram Self-Hosted
**Auth default:** API key required (enterprise licensing); but response headers leak on any request including auth-failed requests
**Exposure class:** Enterprise transcription at no cost if misconfigured; model/version disclosure; medical/legal audio data

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8080 http.headers:"dg-request-id"` | Deepgram-specific response header present on all requests | Low |
| secondary | `port:8080 http.headers:"dg-model-name"` | Second Deepgram-specific header | Low |
| tertiary | `port:8080 "deepgram"` | Brand in banner | Low |
| license-proxy | `port:8443 "deepgram"` | License proxy port | Low |
| identity-probe | `GET /v1/listen` → response headers contain `dg-request-id`, `dg-model-name`, `dg-model-uuid` regardless of auth status | — |

**FP note:** `dg-request-id` and `dg-model-name` are Deepgram-specific header names confirmed in official API documentation. Near-zero FP. Enterprise deployment profile means small population.

---

## XTTS-v2 / xtts-api-server
**Auth default:** none (FastAPI, no auth; auto-docs at /docs always open)
**Exposure class:** Voice cloning synthesis, speaker reference audio uploads, arbitrary text synthesis in cloned voice

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:8020 http.html:"tts_to_audio"` | Endpoint name from FastAPI auto-docs; XTTS-specific | Low |
| secondary | `port:8020 "/docs" http.html:"xtts"` | FastAPI docs page with XTTS brand | Low |
| tertiary | `port:8020 http.json:"language_iso_codes"` | JSON field from `/languages` endpoint | Low |
| broad | `port:8020 http.html:"tts"` | Port + TTS term; catches all xtts-api-server variants | Med |
| docs-leak | `port:8020 "swagger"` | FastAPI Swagger docs page open | Med |
| identity-probe | `GET /docs` → Swagger UI listing `tts_to_audio`, `tts_to_file` endpoints; `GET /languages` → JSON `{"language_iso_codes":[...]}` | — |

**FP note:** Port 8020 has low ambient usage. `tts_to_audio` as an HTML string in FastAPI docs is XTTS-api-server-specific. Low FP risk.

---

## SpeechBrain
**Auth default:** varies (toolkit; HuggingFace-hosted requires token; self-hosted wrappers typically none)
**Exposure class:** Speaker biometric verification, emotion recognition, speech enhancement, ASR — biometric-class data

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"speechbrain.pretrained" port:7860` | Python module import path in Gradio demo source | Low |
| secondary | `http.html:"speechbrain" "gradio"` | Toolkit name + Gradio framework co-occurrence | Med |
| title | `http.title:"SpeechBrain"` | UI title if demo page uses it | Med |
| huggingface | `http.html:"speechbrain" "huggingface"` | HF model hub path in source | Med |
| identity-probe | `GET /` → Gradio HTML containing `"speechbrain"` in source; no standard REST API probe | — |

**FP note:** `speechbrain.pretrained` is a Python import path specific to SpeechBrain's interface pattern. Low FP. Generic `http.html:"speechbrain"` at port 7860 is reasonable but verify against HF-hosted demos (those should be auth-gated).

---

## Tortoise TTS
**Auth default:** none (Gradio; `share=True` commonly enabled in tutorials, creating public ngrok tunnels)
**Exposure class:** High-quality voice cloning synthesis, `voice_samples/` directory with stored reference audio clips

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `http.html:"tortoise-tts" port:7860` | GitHub repo slug in Gradio source + default port | Low |
| secondary | `http.html:"voice_samples" "tortoise" port:7860` | `voice_samples` directory reference + brand | Low |
| flask-api | `port:5000 http.html:"/synthesize" "tortoise"` | Flask API endpoint + brand | Low |
| title | `http.title:"Tortoise" -http.html:"tortoise.com" -http.html:"investment"` | UI title minus financial services FPs | Med |
| tts-webui | `http.html:"tortoise" http.html:"tts-webui"` | TTS-WebUI (rsxdalv) wrapper often used for Tortoise | Low |
| identity-probe | `GET /` → Gradio HTML with `"tortoise"` in source; `GET /info` → JSON Gradio metadata | — |

**FP note:** `http.title:"Tortoise"` hits tortoise.com (investment firm) and other tortoise-themed pages. The `voice_samples` anchor is strong — it's a Tortoise-specific directory name used in UI file pickers.

---

## Bark (Suno TTS)
**Auth default:** none (FastAPI/Uvicorn; Docker runs 0.0.0.0:5000; no auth in canonical implementation)
**Exposure class:** Free audio synthesis (voice + music + sound effects), deepfake audio generation including emotional/paraverbal audio

| Label | Query | Rationale | FP Risk |
|-------|-------|-----------|---------|
| primary | `port:5000 http.json:"bark-inference"` | Endpoint name appears in FastAPI docs JSON | Low |
| secondary | `port:5000 "suno-ai" http.html:"bark"` | Docker image slug + brand | Low |
| github-slug | `http.html:"suno-ai/bark"` | GitHub path appears in requirements/source | Low |
| gradio | `port:7860 http.html:"suno-ai"` | Gradio-wrapped Bark demos | Med |
| identity-probe | `GET /docs` → Swagger UI with `/bark-inference` endpoint; `POST /bark-inference` JSON `{"text":"hi"}` → 200 + audio/wav | — |

**FP note:** Port 5000 is Flask default and heavily used. `http.json:"bark-inference"` anchors specifically to the Bark FastAPI docs response. Without this anchor, port 5000 + `"bark"` produces massive FPs (bark as in dog bark, tree bark, barking mad, etc.).

---

## Compound / Multi-Platform Dorks

| Label | Query | Covers | FP Risk |
|-------|-------|--------|---------|
| voice-cloning-stack | `http.html:"GPT-SoVITS" OR http.html:"rvc-webui" OR http.html:"so-vits-svc"` | All three major voice cloning projects | Low |
| tts-ports | `port:5002 OR port:7851 OR port:8020 http.html:"tts"` | Coqui/AllTalk/XTTS ports with TTS anchor | Med |
| gradio-voice | `port:7860 http.html:"voice" http.html:"cloning"` | Any Gradio voice cloning app | Med |
| whisper-family | `"openai-whisper-asr-webservice" OR "whisper.cpp" OR "faster-whisper"` | All three Whisper variants | Low |
| livekit-full | `"livekit" port:7880 OR port:6789` | LiveKit API + Prometheus | Low |
