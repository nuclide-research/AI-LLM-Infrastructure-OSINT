# Voice/Audio AI Platform OSINT — Pre-Survey Intelligence
**Date:** 2026-05-27
**Purpose:** Tune dork queries, understand auth posture, identify verification probes, document data exposure classes before Shodan harvests.
**Scope:** 12 platforms — voice processing, TTS, STT, voice cloning, audio AI.
**Status:** Pre-survey. No active probing conducted.

---

## Whisper / faster-whisper / whisper.cpp

**Category:** STT (Speech-to-Text)
**Default Ports:**
- whisper.cpp HTTP server: 8080
- openai-whisper-asr-webservice (onerahmet Docker): 9000
- faster-whisper Wyoming protocol: 10300
- Gradio-wrapped variants: 7860

**Auth Default:** off — no auth concept in any of the three canonical implementations. whisper.cpp server README explicitly warns "do not run with administrative privileges" but ships with zero auth.

**Shodan Dork (primary):** `"whisper.cpp" port:8080`
**Shodan Dork (secondary):** `"openai-whisper-asr-webservice" port:9000`
**Shodan Dork (tertiary):** `http.title:"Whisper" "uvicorn" -product:"Microsoft IIS"`

**Verification Probe:**
- whisper.cpp: `POST /inference` with multipart audio → 200 + JSON `{"text":"..."}` field
- faster-whisper Wyoming: TCP connect port 10300 → Wyoming protocol handshake (binary, not HTTP)
- onerahmet webservice: `GET /` → 200 + `"ASR"` in HTML title

**Data Exposure Class:** Transcribed audio content (potentially sensitive speech), model info, compute abuse (free GPU transcription), audio files if upload cache is accessible.

**Known CVEs:** None specific to whisper.cpp or faster-whisper. Wyoming protocol has no CVEs. Gradio wrappers inherit Gradio CVEs: CVE-2024-4941 (path traversal), CVE-2024-47872 (XSS), CVE-2024-51751 (arbitrary file read).

**Default Credentials:** None.

**Notes:**
- `http.title:"Whisper"` is a **high-FP dork** — collides with Wake Forest WHISPER clinical portal (152.11.242.118), government systems with "authorized-use" banners, and unrelated chat apps. Always add stack-anchoring negatives: `-product:"Microsoft IIS" -http.html:"wakehealth" -http.html:"actLogin.cfm"`.
- faster-whisper Wyoming is TCP not HTTP — Shodan may not index port 10300 effectively; HTTP-based wrappers (LinuxServer.io Docker image exposes port 10300 but also a REST API on 10300 for some builds) are better targets.
- `"openai-whisper-asr-webservice"` is a near-zero-FP string — it appears in the HTTP banner of the canonical onerahmet Docker image and nowhere else.

---

## Coqui TTS

**Category:** TTS (Text-to-Speech)
**Default Ports:**
- Demo server: 5002
- OpenAI-compatible endpoint: also on 5002
- MaryTTS-compat endpoint: also on 5002

**Auth Default:** off — no auth concept. Server binds `0.0.0.0:5002` by default. Documentation recommends adding a reverse proxy for production but ships nothing.

**Shodan Dork (primary):** `port:5002 http.html:"api/tts"`
**Shodan Dork (secondary):** `port:5002 "coqui"`

**Verification Probe:** `GET /api/tts?text=test` → 200 + audio/wav binary. `GET /` → 200 + HTML with `"Coqui"` in page source.

**Data Exposure Class:** Free TTS compute abuse, synthesis of arbitrary text (deepfake audio generation), voice model inventory via `/api/voices` (AllTalk fork — see below), speaker-wav upload endpoint potentially writable.

**Known CVEs:** No CVEs for Coqui TTS itself. Older servers accepted arbitrary `speaker_wav` file path parameter without sanitization — path traversal class. Coqui Inc. shut down 2024; no active CVE program. GHSA advisory pending on speaker-embedding upload.

**Default Credentials:** None.

**Notes:**
- Project is archived; `idiap/coqui-ai-TTS` is the maintained fork. Both share the same server code and port.
- `port:5002 http.html:"api/tts"` is a tight signal: port 5002 is otherwise used by VMware vCenter (different HTML signature entirely). Adding `http.html:"api/tts"` drops the VMware FPs.
- Successor is XTTS-v2 / xtts-api-server (see below) — different port, different endpoints.

---

## AllTalk TTS

**Category:** TTS (Coqui/XTTS backend, Gradio UI)
**Default Ports:**
- API server: 7851
- Gradio web UI: 7852

**Auth Default:** off — no auth concept. API documented as `http://127.0.0.1:7851/` but ships with no authentication layer. `--listen` flag or `ip_address` config value `0.0.0.0` exposes to all interfaces.

**Shodan Dork (primary):** `port:7851 http.json:"engines_available"`
**Shodan Dork (secondary):** `port:7851 http.json:"manufacturer_name"`
**Shodan Dork (tertiary):** `port:7851 http.json:"current_engine_loaded"`

**Verification Probe:** `GET /api/currentsettings` → 200 + JSON with fields `engines_available`, `current_engine_loaded`, `manufacturer_name` (value: `"Coqui"`), `audio_format`, `deepspeed_capable`.

**Data Exposure Class:** Full TTS engine config (models loaded, VRAM state, DeepSpeed status), voice inventory (`/api/voices` → list of voice files), RVC voice conversion pipeline if enabled (`/api/rvcvoices`), arbitrary TTS generation, server restart/reload via control endpoints.

**Known CVEs:** None specific. Inherits Gradio CVEs on port 7852 (CVE-2024-4941, CVE-2024-51751).

**Default Credentials:** None.

**Notes:**
- `engines_available` and `current_engine_loaded` are AllTalk-specific JSON field names not used by any other TTS server. Either alone on port 7851 is near-zero-FP.
- `manufacturer_name` value of `"Coqui"` in JSON is also distinctive but could theoretically appear in other Coqui-derived servers.
- The `/api/deepspeed` and `/api/lowvramsetting` endpoints allow runtime GPU config changes with no auth — not just data exposure but compute-control exposure.
- Port 7852 is the Gradio UI — separate Shodan target from port 7851 API.

---

## RVC (Retrieval-based Voice Conversion)

**Category:** Voice Conversion / Voice Cloning
**Default Ports:**
- Gradio WebUI: 7865
- Alternative/conflict port: 7897 (some forks)

**Auth Default:** off — Gradio with no authentication. Running `python infer-web.py --host 0.0.0.0` binds to all interfaces.

**Shodan Dork (primary):** `port:7865 http.html:"Retrieval-based-Voice-Conversion"`
**Shodan Dork (secondary):** `port:7865 http.html:"RVC"` 
**Shodan Dork (tertiary):** `http.html:"rvc-webui" port:7865`

**Verification Probe:** `GET /` → 200 + Gradio HTML with title containing `"RVC"` or `"Retrieval"`. Gradio API: `GET /info` → JSON with Gradio metadata.

**Data Exposure Class:** Voice model files (uploaded/trained voice models), inference API for cloning any voice model on the server, full Gradio API (`/run/predict`) allowing arbitrary voice conversion, training pipeline access.

**Known CVEs:** No RVC-specific CVEs. Gradio CVEs apply (CVE-2024-4941 path traversal allows reading arbitrary server files including trained voice models and audio samples).

**Default Credentials:** None.

**Notes:**
- Port 7865 is Gradio's default when 7860 is taken. Not exclusively RVC — any Gradio app on 7865 will match. Must combine with `http.html:"RVC"` or `"Retrieval-based-Voice-Conversion"`.
- The Gradio API endpoint `/run/predict` is always present and unauthenticated by default, enabling API-level voice conversion without the UI.
- High abuse potential: trained celebrity or public-figure voice models are commonly uploaded to public RVC instances.

---

## GPT-SoVITS

**Category:** Voice Cloning / TTS (few-shot, Mandarin-optimized)
**Default Ports:**
- API server: 9880
- WebUI inference: 9872
- UVR5 (vocal separation): 9873
- Main training WebUI: 9874
- Proofreading tool: 9871
- Docker exposes all five: 9871-9874, 9880

**Auth Default:** off — default bind is `127.0.0.1:9880` for the API but Docker deployments expose all ports with `0.0.0.0` binding. No auth in API or WebUI.

**Shodan Dork (primary):** `port:9880 http.html:"GPT-SoVITS"`
**Shodan Dork (secondary):** `port:9872 http.html:"GPT-SoVITS"`
**Shodan Dork (tertiary):** `http.json:"set_gpt_weights" port:9880`

**Verification Probe:**
- API: `GET /control` → JSON `{"message": "..."}` (command endpoint)
- WebUI: `GET /` on 9872 → Gradio HTML with `"GPT-SoVITS"` in title

**Data Exposure Class:** Arbitrary voice cloning (1-minute audio sufficient), model swap via `/set_gpt_weights` and `/set_sovits_weights` (path traversal risk — parameters are file paths), reference audio swap via `/set_refer_audio`, full TTS synthesis of any text in cloned voice.

**Known CVEs:**
- CVE-2025-49833, CVE-2025-49834, CVE-2025-49835, CVE-2025-49836 (GitHub Security Lab GHSL-2025-045/048) — command injection in `open_slice`, `open_denoise`, `open_asr`, `change_label` WebUI functions. User-controlled file path parameters concatenated into shell commands via `Popen(cmd, shell=True)`. Insufficient `clean_path` sanitization. Unauthenticated RCE on exposed WebUI ports (9871-9874).

**Default Credentials:** None.

**Notes:**
- The four command-injection CVEs are unauthenticated RCE on any internet-exposed GPT-SoVITS WebUI instance — this is not just compute abuse, it is full shell access.
- `/set_gpt_weights` and `/set_sovits_weights` accept file path parameters — additional path traversal vector on API port 9880.
- `http.json:"set_gpt_weights"` would match if Shodan captures the API docs endpoint (`/docs` via FastAPI auto-docs) — worth testing.
- Chinese-operator-heavy deployment profile; expect significant CN/HK/TW ASN concentration.

---

## Pipecat

**Category:** Voice AI Agent Framework
**Default Ports:**
- WebSocket server transport: 8765
- FastAPI dev runner: 7860 (Gradio default, varies)
- Example bots: 7860, 8000

**Auth Default:** off for WebSocket transport. The framework docs explicitly state it is "best suited for prototyping and controlled network environments." No built-in auth in WebSocketServerTransport. Production Bearer token auth is only implemented in Pipecat Cloud (managed), not in the self-hosted framework.

**Shodan Dork (primary):** `http.html:"pipecat-ai"` 
**Shodan Dork (secondary):** `port:8765 "pipecat"`
**Shodan Dork (tertiary):** `http.html:"pipecat" "daily.co"`

**Verification Probe:** HTTP upgrade to WebSocket on port 8765 → connection accepted. HTTP GET `GET /` → may return FastAPI docs if running with dev runner. No standard health endpoint documented.

**Data Exposure Class:** Live voice agent (speak to it, harvest conversation logs), LLM API keys in process environment (exposed via Gradio CVE file-read if wrapped in Gradio), audio stream interception.

**Known CVEs:** None specific to Pipecat. Depends entirely on transport layer and how keys are handled.

**Default Credentials:** None.

**Notes:**
- Pipecat is a framework, not a server — exposed instances are developer demos or misconfigured production deployments. Low population but high interest (live voice interaction).
- WebSocket on port 8765 is shared with many other applications. Without HTTP content anchoring this dork is high-FP.
- Best signal: `http.html:"pipecat-ai"` if the GitHub org name appears in page source. Secondary: `"daily.co"` co-occurrence (Pipecat's parent company API often called from exposed demos).

---

## LiveKit

**Category:** Real-time Audio/Video Infrastructure
**Default Ports:**
- API / WebSocket signaling: 7880
- ICE/TCP WebRTC transport: 7881
- ICE/UDP Mux: 7882
- Prometheus metrics: 6789
- TURN/TLS: 5349
- TURN/UDP: 3478
- SIP: 5060/5061

**Auth Default:** JWT — API keys configured as `keys: {key: secret}` pairs in config. Tokens required for room creation and client connections. **However:** the `/` health endpoint and metadata endpoints on 7880 are often reachable without auth. LiveKit docs note port 7880 should be behind a reverse proxy but many self-hosters expose it directly.

**Shodan Dork (primary):** `port:7880 "livekit"`
**Shodan Dork (secondary):** `http.headers:"X-LiveKit-Server" port:7880`
**Shodan Dork (tertiary):** `port:7880 http.html:"livekit"`

**Verification Probe:** `GET /` on port 7880 → HTTP 200 with `X-LiveKit-Server` response header. Header value includes LiveKit version string (e.g., `livekit/1.x.x`).

**Data Exposure Class:** Room metadata leak (active room names, participant counts if metrics exposed), Prometheus metrics on 6789 (participant telemetry, audio/video stats), TURN credential exposure if misconfigured, SIP trunk exposure on 5060.

**Known CVEs:** None publicly documented for LiveKit server. Security model relies on proper JWT key management — leaked API keys allow full room creation/manipulation.

**Default Credentials:** None (requires explicit key configuration — no hardcoded defaults).

**Notes:**
- `X-LiveKit-Server` HTTP header is the highest-precision signal. Confirmed by LiveKit SDK documentation. Near-zero FP.
- Prometheus metrics on port 6789 are unauthenticated by default — separate Shodan target: `port:6789 "livekit"`.
- SIP integration on 5060 is optional but when enabled, exposes a SIP proxy that may accept unauthenticated REGISTER/INVITE depending on SIP auth config.

---

## Deepgram Self-Hosted

**Category:** STT (Speech-to-Text, enterprise on-premises)
**Default Ports:**
- API container: 8080
- License proxy: 8443

**Auth Default:** API key required — Deepgram self-hosted requires distribution credentials issued through their licensing system. mTLS secures the license communication channel. **However:** the API container on port 8080 in misconfigured deployments may lack network-level auth, and the license proxy port 8443 is publicly reachable for license check-in.

**Shodan Dork (primary):** `port:8080 http.headers:"dg-request-id"`
**Shodan Dork (secondary):** `port:8080 http.headers:"dg-model-name"`
**Shodan Dork (tertiary):** `port:8080 "deepgram" "transcription"`

**Verification Probe:** `GET /v1/listen` or `GET /` → response headers include `dg-request-id`, `dg-model-name`, `dg-model-uuid`. The header `dg-request-id` is present on all requests including errors.

**Data Exposure Class:** If auth misconfigured: transcription of arbitrary audio at no cost, model name/version disclosure via headers, language/model capability enumeration.

**Known CVEs:** None. Enterprise product with active security program.

**Default Credentials:** None (licensing system enforces credentials).

**Notes:**
- `dg-request-id` and `dg-model-name` are Deepgram-specific response headers confirmed in their official API documentation. Near-zero FP for these headers.
- Enterprise deployment profile means low population but high data sensitivity (medical, legal, financial transcription common use case).
- License proxy on 8443 is a distinct target — may respond to HTTPS probes and leak version/config info.

---

## XTTS-v2 / xtts-api-server

**Category:** TTS / Voice Cloning (Coqui XTTS successor)
**Default Ports:**
- xtts-api-server (daswer123): 8020
- Coqui TTS legacy with XTTS model: 5002
- Docker: `--listen` flag exposes 0.0.0.0

**Auth Default:** off — no authentication in xtts-api-server. FastAPI server with auto-generated `/docs` endpoint. No auth in any documented deployment variant.

**Shodan Dork (primary):** `port:8020 http.html:"tts_to_audio"`
**Shodan Dork (secondary):** `port:8020 "/docs" "xtts"`
**Shodan Dork (tertiary):** `port:8020 http.json:"language_iso_codes"`

**Verification Probe:** `GET /docs` → 200 + FastAPI Swagger UI with endpoints `tts_to_audio`, `tts_to_file`, `set_tts_settings`. `GET /languages` → JSON with `language_iso_codes` array.

**Data Exposure Class:** Free TTS compute with voice cloning, arbitrary text synthesis in cloned voice, voice sample uploads (speaker reference audio), language/model enumeration, server config via settings endpoint.

**Known CVEs:** None specific. Inherits FastAPI security concerns. Gradio file-read CVEs if using Gradio wrapper.

**Default Credentials:** None.

**Notes:**
- `tts_to_audio` is the canonical endpoint name used in the primary daswer123 implementation and documented in SillyTavern integration guides. Distinctive: not used in other TTS servers.
- FastAPI auto-docs at `/docs` exposes the full API surface without any auth — even if a firewall blocks the TTS endpoints, the docs page reveals everything.
- Port 8020 has low ambient traffic — much better precision than port 5002 which shares space with VMware vCenter and legacy Mozilla TTS.

---

## SpeechBrain

**Category:** Research STT/TTS/Speaker Verification Toolkit
**Default Ports:** No standard server port — SpeechBrain is a Python toolkit, not a server. Deployed as:
- Hugging Face Inference Endpoints (cloud, auth-gated)
- Custom FastAPI/Flask wrappers (port varies, typically 8000 or 7860)
- Gradio demos (7860)

**Auth Default:** Varies by wrapper. The toolkit itself has no auth concept. HuggingFace-hosted models use HF token auth. Self-hosted wrappers typically have no auth.

**Shodan Dork (primary):** `http.html:"speechbrain" port:7860`
**Shodan Dork (secondary):** `http.html:"speechbrain" "gradio"`
**Shodan Dork (tertiary):** `http.html:"speechbrain.pretrained"`

**Verification Probe:** `GET /` → Gradio HTML containing `"speechbrain"` in source. No standard REST endpoint — probe depends on wrapper.

**Data Exposure Class:** Speaker verification (identify if two audio clips are same person), emotion recognition, speech enhancement, ASR — depends on which SpeechBrain recipe is deployed. Biometric-class data if speaker-ID pipeline exposed.

**Known CVEs:** None. Research toolkit.

**Default Credentials:** None.

**Notes:**
- SpeechBrain is a toolkit, not a service — Shodan population is limited to deployments that wrapped it in a web server. Mostly academic/research instances.
- `speechbrain.pretrained` is the Python module import path that often appears in Gradio demo source code embedded in HTML — distinctive string.
- Speaker verification exposure is GDPR Art. 9 biometric data class — higher disclosure sensitivity than generic STT.

---

## Tortoise TTS

**Category:** TTS (high-quality, slow)
**Default Ports:**
- Flask API: 5000
- Gradio wrapper: 7860
- TTS-WebUI (rsxdalv): 7860

**Auth Default:** off — no auth concept in any Tortoise deployment. Gradio `share=True` option often enabled in tutorials (creates public ngrok tunnel, indexed by Gradio's own server).

**Shodan Dork (primary):** `http.html:"tortoise-tts" port:7860`
**Shodan Dork (secondary):** `http.html:"tortoise" "voice_samples" port:7860`
**Shodan Dork (tertiary):** `http.title:"Tortoise" -http.html:"tortoise.com"`

**Verification Probe:** `GET /` → Gradio HTML with `"tortoise"` in source. Gradio API: `GET /info` → JSON with Gradio metadata including app name.

**Data Exposure Class:** TTS synthesis of arbitrary text in high-quality cloned voices, `voice_samples/` directory (stored reference audio clips used for voice cloning), slow but high-quality voice impersonation.

**Known CVEs:** No Tortoise-specific CVEs. Gradio CVE-2024-4941 (path traversal) allows reading `voice_samples/` directory content — direct access to collected voice data.

**Default Credentials:** None.

**Notes:**
- `http.title:"Tortoise"` has FP risk from tortoise.com (financial services site). Add `-http.html:"tortoise.com"` or `-http.html:"investment"`.
- `voice_samples` is a Tortoise-specific directory structure referenced in UI source code — adding it to the dork significantly reduces FPs.
- Tortoise is slow (minutes per synthesis) so exposed instances are rarely used actively — but voice sample collections may persist.

---

## Bark (Suno TTS)

**Category:** TTS / Text-to-Audio (voices, music, sound effects)
**Default Ports:**
- bark-tts-api (ai-citizens): 5000
- Docker deployments: `0.0.0.0:5000`
- Gradio wrappers: 7860

**Auth Default:** off — no auth in canonical bark-tts-api implementation. FastAPI/Uvicorn with no authentication middleware.

**Shodan Dork (primary):** `port:5000 http.json:"bark-inference"`
**Shodan Dork (secondary):** `port:5000 "suno-ai" http.html:"bark"`
**Shodan Dork (tertiary):** `http.html:"suno-ai/bark" port:7860`

**Verification Probe:** `POST /bark-inference` with JSON `{"text":"test","voice":"v2/en_speaker_0"}` → 200 + audio/wav. `GET /` → FastAPI docs page or redirect. `GET /docs` → Swagger UI with `/bark-inference` endpoint listed.

**Data Exposure Class:** Free audio synthesis (voices, music, sound effects, laughter, sound design), no cost to operator, arbitrary emotional/para-linguistic audio generation (sighs, crying, laughing useful for social engineering).

**Known CVEs:** None specific. Inherits FastAPI concerns.

**Default Credentials:** None.

**Notes:**
- Port 5000 is heavily shared (Flask default, AirPlay receiver, many others). `http.json:"bark-inference"` anchors to the specific endpoint name.
- `suno-ai/bark` is the GitHub slug that appears in Docker image names and requirements.txt — often shows up in banner/HTML.
- Bark supports `[laughter]`, `[sighs]`, `♪` (music) and sound effects via special tokens — the abuse profile goes beyond voice cloning into full audio deepfakes.
- ~5.5GB VRAM requirement limits deployments to GPU servers.

---

## Cross-Platform Notes

### Gradio FP class (affects RVC, GPT-SoVITS, Tortoise, Bark, SpeechBrain, AllTalk)
All Gradio-wrapped applications return `<title>...</title>` and Gradio's own JS bundle. Generic `port:7860` dorks return everything running on Gradio. Always combine with application-specific HTML strings.

### CVE inheritance (affects all Gradio wrappers)
- CVE-2024-4941 — path traversal via `/run/predict` file parameter
- CVE-2024-47872 — XSS via HTML/JS/SVG file upload
- CVE-2024-51751 — arbitrary file read via File/UploadButton components
- CVE-2026-28414 — absolute path traversal (2026)

These CVEs apply to any Gradio application, including every TTS/STT/voice-cloning wrapper in this category.

### Port collision summary
| Port | Primary occupant | Collision risk |
|------|-----------------|----------------|
| 5000 | Flask default, Bark, Tortoise API | High — AirPlay, many Flask apps |
| 5002 | Coqui TTS | Medium — VMware vCenter |
| 7851 | AllTalk API | Low — distinctive port |
| 7852 | AllTalk Gradio | Low |
| 7860 | Gradio default | Very high — all Gradio apps |
| 7865 | RVC WebUI | Medium — Gradio fallback |
| 7880 | LiveKit API | Low — LiveKit specific |
| 8020 | XTTS-api-server | Low — distinctive |
| 8080 | whisper.cpp, Deepgram | High — web server default |
| 8765 | Pipecat WebSocket | Medium — many WebSocket apps |
| 9000 | whisper-asr-webservice | Medium — various services |
| 9880 | GPT-SoVITS API | Low — distinctive range |

### Auth posture summary
| Platform | Auth default | Notes |
|----------|-------------|-------|
| whisper.cpp | None | No auth concept |
| faster-whisper Wyoming | None | TCP protocol, no auth |
| Coqui TTS | None | Binds 0.0.0.0 |
| AllTalk TTS | None | Full engine control exposed |
| RVC | None | Gradio, no auth |
| GPT-SoVITS | None | RCE CVEs on WebUI ports |
| Pipecat | None (self-hosted) | JWT on Cloud only |
| LiveKit | JWT required | But health endpoint accessible; many misconfigs |
| Deepgram self-hosted | API key | Enterprise; low exposure rate |
| XTTS-v2 api-server | None | Full synthesis API exposed |
| SpeechBrain | Varies | Toolkit; depends on wrapper |
| Tortoise TTS | None | Gradio share=True often enabled |
| Bark | None | FastAPI, no auth |
