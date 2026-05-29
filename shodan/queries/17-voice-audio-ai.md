# 17. Voice / Audio AI

_Section created: 2026-05-08_

Self-hosted voice and audio AI surfaces — speech-to-text, text-to-speech, voice cloning, real-time voice agents, speaker diarization, music generation. Distinct from the broader model-serving survey (`03-model-serving.md`) because the abuse profile is different: a free-compute hit on a Whisper transcription endpoint is one class of harm; an unauth voice-cloning model is a substantively different class (deepfake-fraud, social engineering, voice impersonation).

Auth posture across this category skews **Tier-A** ("no auth concept" in the framework default). Most of these projects ship as research code or "self-host the demo" Gradio/Streamlit wrappers. Operators rarely add auth in front because most hosting tutorials don't bother.

## CVE / advisory watch

- **CVE-2025-43842 through CVE-2025-43852 — RVC-WebUI (11x CVSS 9.8, RCE)**: GitHub Security Lab GHSL-2025-012 to GHSL-2025-022. Command injection via `preprocess_dataset`, `extract_f0_feature`, `click_train` endpoints; code injection via `eval()` in `change_info_`; pickle RCE via `torch.load(weights_only=False)` in 6 model-handling functions. Chain: unauth Gradio API → malicious `.pth` model path → pickle deserialization → OS command execution. **Every exposed RVC-WebUI instance is an RCE target.**
- **CVE-2025-49837 through CVE-2025-49841 — GPT-SoVITS (5x Critical RCE)**: GitHub Security Lab GHSL-2025-049 to GHSL-2025-053. Same command injection + pickle deserialization class. Port 9880, unauth FastAPI.
- **CVE-2026-48710 "BadHost" — Starlette < 1.0.1 (auth bypass)**: Affects every FastAPI-wrapped TTS/ASR server — Kokoro-FastAPI, Orpheus-FastAPI, Chatterbox-TTS-Server, Parler-TTS, and any custom Whisper wrapper using Starlette path-based auth middleware. Host header injection bypasses auth without credentials. Patch: Starlette 1.0.1+. Research/homelab deploys (no reverse proxy) = fully exploitable.
- **CVE-2025-23242 / CVE-2025-23243 — NVIDIA Riva ASR**: Default config exposes HTTP 9000 + gRPC 50051 on 0.0.0.0; 54 cloud IPs identified by researchers. Unauthorized access to GPU resources and API key theft.
- `GHSA-pending` — `coqui-ai/TTS` arbitrary file write via crafted speaker-embedding upload (advisory pending; older Coqui servers shipped with `/api/tts` accepting arbitrary file params).
- **Trademark/identity abuse:** voice-cloning servers serving celebrity-voice models without licensing fall under right-of-publicity (US) / GDPR Art. 9 biometric data (EU) — disclosure framing differs from typical security findings.

---

## Known false-positive classes (filter at query time)

The keyword `Whisper` collides with several non-AI products that share the name. These are not voice/audio AI services and should be excluded from any `http.title:"Whisper"` survey to keep the result set clean.

### Wake Forest WHISPER — clinical research portal (discovered 2026-05-08)

`whisper.phs.wakehealth.edu` (152.11.242.118) hosts a **federally-funded clinical research data portal at Wake Forest University Health Sciences, Division of Public Health Sciences (PHS-BDS)**. ColdFusion-on-IIS, login-gated, federal-government-system warning banner. The acronym predates the OpenAI model. Cert SAN cluster covers 9 hostnames under `*.phs.wakehealth.edu` (`whisper`, `guardian`, `ccrbis`, `mdsetaa`, `medsdb`, `oldphs`, `phs`, `web7a`, `libweb7`).

**Filter recipe:** add `-http.html:"wakehealth" -http.html:"WFUHS" -http.html:"phs.wakehealth" -http.html:"WHISPERLogo" -http.html:"actLogin.cfm"` to broad `http.title:"Whisper"` queries.

Pre-filtered Shodan queries:

| Filtered Shodan Query | Notes |
|---|---|
| `http.title:"Whisper" -http.html:"wakehealth" -http.html:"WHISPERLogo"` | Whisper title minus Wake Forest WHISPER |
| `http.title:"Whisper" -http.html:"actLogin.cfm" -http.html:"federal government"` | Title minus US-fed-gov authorized-use banners |
| `http.title:"Whisper" "uvicorn"` | Positive: only Whisper *with* uvicorn FastAPI signature (kicks out IIS/ColdFusion entirely) |
| `http.title:"Whisper" "fastapi"` | Same approach — anchor on the actual stack |
| `http.title:"Whisper" -product:"Microsoft IIS"` | Stack-level negative filter |

### General methodology lesson

Repeating the lesson from Session 9's Garak / `Garakuta no Kamisama` collision: **a single keyword in `http.title` or `http.html` is unsound at population scale.** Whisper, Garak, Bark, and Piper all collide with non-AI products. Anchor every keyword match to a structural signal that confirms the AI stack:

- `"uvicorn"` or `"fastapi"` for the FastAPI Whisper variants
- `"whisper.cpp"` literal for the C++ HTTP server
- `"openai-whisper-asr-webservice"` for the canonical Docker image
- `body_contains:"/inference"` + `body_contains:"audio file"` for the whisper.cpp UI template
- Kick out `Microsoft IIS`, `ColdFusion`, `.cfm`, and government-banner strings

The aimap fingerprints in `fingerprints.go` already enforce this discipline (conjunctive matching on `body_contains`+`status_code`+`json_field`), but the Shodan dorks here are the *first* filter — the cleaner the dork, the less waste downstream.

---

## Whisper ecosystem (ASR / Speech-to-Text)

OpenAI Whisper and its derivatives. Most expose `/inference`, `/v1/audio/transcriptions`, or a Gradio interface.

| Shodan Query | Notes |
|---|---|
| `http.title:"Whisper"` | Broad — Whisper web UIs across all ports |
| `http.title:"Whisper" port:8080` | Default port for many Whisper deployments |
| `http.title:"Whisper" port:9000` | onerahmet/openai-whisper-asr-webservice default |
| `http.title:"Whisper" port:7860` | Gradio interface default |
| `http.title:"Whisper" -port:443` | Non-HTTPS only |
| `http.html:"faster-whisper"` | faster-whisper accelerated derivative in HTML |
| `"faster-whisper"` | Banner form |
| `http.html:"WhisperX"` | WhisperX (word-level alignment) |
| `"whisper.cpp" "/inference"` | whisper.cpp C++ HTTP server |
| `"whisper.cpp" port:8080` | whisper.cpp default port |
| `http.html:"whisper-streaming"` | Whisper-Streaming live ASR |
| `http.html:"WhisperLive"` | WhisperLive WebSocket transcription |
| `http.html:"insanely-fast-whisper"` | Vaibhavs10 fast Whisper wrapper |
| `"openai-whisper-asr-webservice"` | onerahmet's standard webservice |
| `"openai-whisper-asr-webservice" port:9000` | Above + canonical port |
| `http.title:"Whisper" country:US` | Geo-scoped |
| `http.title:"Whisper" country:DE` | |
| `http.title:"Whisper" country:CN` | |
| `http.title:"Whisper" org:"university"` | Academic deployments |
| `http.title:"Whisper" org:"hospital"` | Healthcare deployments (HIPAA-relevant) |
| `http.title:"Whisper" org:"amazon"` | AWS deployments |
| `http.title:"Whisper" org:"hetzner"` | Hetzner-hosted |

## Vosk

Kaldi-based offline speech recognition.

| Shodan Query | Notes |
|---|---|
| `http.html:"vosk"` | Vosk in HTML |
| `"vosk-server"` | Vosk server banner |
| `"vosk-api"` | Vosk API banner |

---

## Coqui TTS family

Coqui Inc. shut down 2024 but XTTS-v2 model + servers remain widely deployed.

| Shodan Query | Notes |
|---|---|
| `http.html:"coqui"` | Coqui in HTML — broadest |
| `"coqui" "tts"` | Banner + term |
| `http.html:"xtts"` | XTTS v2 deployments |
| `http.html:"XTTS"` | Mixed-case |
| `"xtts-v2"` | XTTS-v2 model name in banner |
| `http.title:"Coqui"` | Coqui-themed pages |
| `http.title:"XTTS"` | XTTS UI title |
| `port:5002 http.html:"tts"` | Mozilla TTS / Coqui legacy default port |
| `port:8020 http.html:"tts"` | Coqui XTTS server typical port |
| `http.html:"coqui" port:5002` | Coqui legacy on default port |

## Piper

Rhasspy Piper — fast neural TTS popular on Raspberry Pi / edge.

| Shodan Query | Notes |
|---|---|
| `http.title:"Piper"` | Piper UI title |
| `"piper" "tts"` | Banner + term |
| `http.html:"piper-tts"` | Hyphenated form in HTML |
| `"piper-http"` | Piper HTTP wrapper |

## Bark / MusicGen / AudioCraft

Suno Bark and Meta's AudioCraft / MusicGen.

| Shodan Query | Notes |
|---|---|
| `http.title:"Bark"` | Bark UI |
| `http.html:"suno-ai"` | Suno-AI banner |
| `http.html:"audiocraft"` | AudioCraft in HTML |
| `http.html:"MusicGen"` | MusicGen UI |
| `http.html:"musicgen"` | Lowercase |
| `"audiogen"` | AudioGen |

## OpenVoice

MyShell.ai OpenVoice — multi-language voice cloning.

| Shodan Query | Notes |
|---|---|
| `http.html:"openvoice"` | OpenVoice in HTML |
| `http.title:"OpenVoice"` | OpenVoice UI title |
| `"OpenVoice" "myshell"` | OpenVoice + MyShell brand |
| `http.html:"se_extractor"` | OpenVoice speaker-embedding extractor module |

## F5-TTS / E2-TTS

Recent (2024-25) flow-matching TTS.

| Shodan Query | Notes |
|---|---|
| `http.html:"f5-tts"` | F5-TTS in HTML |
| `http.html:"F5_TTS"` | Underscore form |
| `http.html:"e2-tts"` | E2-TTS sibling project |
| `"swivid/f5-tts"` | HF model path in banner |

## ChatTTS

2noise/ChatTTS — conversational TTS, viral mid-2024.

| Shodan Query | Notes |
|---|---|
| `http.html:"ChatTTS"` | Brand title |
| `http.html:"chattts"` | Lowercase |
| `http.title:"ChatTTS"` | UI title |
| `"2noise"` | GitHub org name often appears in source |

## Tortoise TTS

| Shodan Query | Notes |
|---|---|
| `http.html:"tortoise-tts"` | Tortoise in HTML |
| `http.title:"Tortoise"` | UI title |
| `"tortoise-tts"` | Banner |

## StyleTTS2

| Shodan Query | Notes |
|---|---|
| `http.html:"StyleTTS"` | StyleTTS in HTML |
| `http.html:"styletts2"` | Version-2 lowercase |

## Mozilla TTS / legacy

| Shodan Query | Notes |
|---|---|
| `http.html:"mozilla-tts"` | Mozilla TTS legacy |
| `port:5002 http.html:"api/tts"` | Default port + endpoint path |

---

## Voice cloning / conversion

These are the highest-abuse-potential surfaces.

## RVC (Retrieval-based Voice Conversion)

| Shodan Query | Notes |
|---|---|
| `http.html:"rvc-webui"` | RVC WebUI |
| `http.html:"Retrieval-based-Voice-Conversion"` | Full project name |
| `http.title:"RVC"` | UI title |
| `http.html:"rvc-project"` | Project banner |
| `http.html:"RVC-Boss"` | RVC-Boss-GPT-SoVITS variant |
| `http.html:"GPT-SoVITS"` | GPT-SoVITS (Mandarin-focused) |
| `http.title:"GPT-SoVITS"` | UI title |
| `port:7865 http.html:"voice"` | RVC default Gradio port |
| `port:7897 http.html:"voice"` | GPT-SoVITS typical port |

## so-vits-svc

| Shodan Query | Notes |
|---|---|
| `http.html:"so-vits-svc"` | so-vits-svc in HTML |
| `http.title:"SoftVC"` | SoftVC UI title |

## Applio

| Shodan Query | Notes |
|---|---|
| `http.html:"Applio"` | Applio (RVC fork) |
| `http.title:"Applio"` | UI title |

---

## Real-time voice agents

WebRTC + LLM + STT + TTS pipelines for live phone/video conversations. Highest-impact misuse class (live impersonation, scam-call automation).

## Pipecat

Daily.co's open-source voice-agent framework.

| Shodan Query | Notes |
|---|---|
| `http.html:"pipecat"` | Pipecat in HTML |
| `http.title:"Pipecat"` | UI title |
| `"pipecat-ai"` | Project banner |
| `port:7860 http.html:"pipecat"` | Default Gradio port |

## LiveKit Agents

| Shodan Query | Notes |
|---|---|
| `http.html:"livekit-agents"` | LiveKit Agents framework |
| `http.html:"livekit"` | LiveKit broader |
| `http.title:"LiveKit"` | UI title |
| `"livekit-server"` | Server banner |

## Vocode

| Shodan Query | Notes |
|---|---|
| `"vocode"` | Vocode banner |
| `http.html:"vocode"` | HTML form |
| `http.html:"vocode-python"` | Python SDK form |

## Retell AI / open-call

| Shodan Query | Notes |
|---|---|
| `http.html:"retell-ai"` | Retell AI |
| `"retell-sdk"` | SDK banner |

---

## Speaker recognition / diarization

## Pyannote

Pyannote speaker diarization servers.

| Shodan Query | Notes |
|---|---|
| `http.html:"pyannote"` | Pyannote in HTML |
| `"pyannote/audio"` | HF model path |
| `http.html:"pyannote-audio"` | Hyphenated form |

## SpeechBrain

| Shodan Query | Notes |
|---|---|
| `http.html:"speechbrain"` | SpeechBrain framework |
| `"speechbrain"` | Banner |

## NeMo (NVIDIA)

| Shodan Query | Notes |
|---|---|
| `http.html:"nemo-toolkit"` | NeMo toolkit |
| `http.html:"NVIDIA NeMo"` | Brand form |
| `"nvidia-nemo"` | Banner |

---

## Aggregate / wrapper UIs

UIs that wrap multiple voice models behind one interface.

## AI TTS Server (rsxdalv/tts-generation-webui)

| Shodan Query | Notes |
|---|---|
| `http.html:"tts-generation-webui"` | rsxdalv project banner |
| `http.title:"TTS Generation Web UI"` | UI title |
| `"/v1/audio/voices"` | OpenAI-compatible voices listing |
| `port:10087 http.html:"audio"` | rsxdalv default port |

## Open-source ElevenLabs alternatives

| Shodan Query | Notes |
|---|---|
| `http.html:"elevenlabs-clone"` | Clones |
| `http.html:"open-tts"` | Generic open-tts banner |
| `"OpenAI-compatible" "audio/speech"` | OpenAI-compatible TTS proxies |

---

## Gradio / Streamlit voice-AI interfaces (port 7860)

Many voice-AI projects ship as Gradio demos. Port 7860 is shared with image-gen surveys; voice-specific filtering:

| Shodan Query | Notes |
|---|---|
| `port:7860 http.html:"audio"` | Gradio + audio component |
| `port:7860 http.html:"speech"` | Gradio + speech mention |
| `port:7860 http.html:"voice"` | Gradio + voice mention |
| `port:7860 http.html:"tts"` | Gradio + TTS |
| `port:7860 http.html:"ASR"` | Gradio + ASR |
| `port:7860 http.html:"clone"` | Gradio + voice-cloning UI |

---

## Kokoro TTS (NEW — 2026-05-28)

Kokoro-FastAPI: OpenAI-compatible TTS, port 8880, no auth, multiple Docker images in the wild.

| Shodan Query | Notes |
|---|---|
| `port:8880 http.html:"Kokoro"` | Primary — Kokoro-FastAPI Swagger/docs page |
| `port:8880 http.html:"/dev/captioned_speech"` | **Near-zero-FP** — project-unique endpoint path |
| `http.title:"Kokoro" port:8880` | Swagger UI title anchor |
| `port:8880 http.html:"/v1/audio/voices"` | OpenAPI schema reference |

Verification probe: `GET /debug/system` → JSON with CPU/GPU metrics. **Unique to kokoro-fastapi — no other TTS server exposes this path.**

---

## Chatterbox TTS (NEW — 2026-05-28)

Zero-shot voice cloning, 15.9K GitHub stars, multiple Docker forks. Two distinct deployment surfaces.

| Shodan Query | Notes |
|---|---|
| `port:8000 http.html:"chatterbox"` | devnen/Chatterbox-TTS-Server (port 8000) |
| `port:4123 http.html:"Chatterbox"` | travisvn/chatterbox-tts-api (port 4123) |
| `http.title:"Chatterbox TTS"` | Title match either variant |

Verification probe (devnen): `GET /api/model-info` → JSON with `"engine"` field (e.g., `"chatterbox-turbo"`).
**Severity elevated:** `/upload_reference` (voice cloning) is unauth on both variants.

---

## Orpheus-FastAPI (NEW — 2026-05-28)

3B-param Llama TTS, 8 voices, emotion tags, HN front-page release. Port 8899 near-unique.

| Shodan Query | Notes |
|---|---|
| `port:8899 http.html:"Orpheus"` | Primary |
| `port:8899 http.html:"/v1/audio/speech"` | OpenAPI path |
| `http.title:"Orpheus TTS"` | Swagger title |

---

## WhisperLive WebSocket (NEW — 2026-05-28)

Real-time streaming ASR via WebSocket. Distinct from batch Whisper — separate fingerprint class.

| Shodan Query | Notes |
|---|---|
| `port:9090 "WhisperLive"` | WebSocket port + product name |
| `port:8000 http.html:"WhisperLive"` | REST companion port |
| `port:9090 http.html:"nearly-live implementation"` | README text in HTML |

Verification probe: WebSocket connect to `:9090` → send `{"uid":"x","language":"en","task":"transcribe","model":"tiny.en"}` → server responds `{"uid":"x","message":"SERVER_READY"}`. **`SERVER_READY` string is definitive.**

---

## Deepgram Self-Hosted (UPDATED — 2026-05-28)

Runtime auth is OFF — NGC key only gates image pull. HTTP API including `/v1/status` and `/v1/listen` requires no per-request auth once container is running.

| Shodan Query | Notes |
|---|---|
| `port:8080 http.html:"system_health" http.html:"active_batch_requests"` | **Near-zero-FP** — unique JSON schema |
| `http.html:"active_stream_requests" http.html:"active_listen_v2_stream_requests"` | Secondary field pair |
| `port:8080 port:9991` | Two-port co-presence (API + engine) |

Verification probe: `GET /v1/status` → JSON with `"system_health"` field. **No auth required. Field name is unique to Deepgram on-prem.**

---

## NVIDIA NIM ASR (Parakeet / Canary) (NEW — 2026-05-28)

Enterprise ASR. HTTP 9000 + gRPC 50051. Runtime auth OFF per-request. CVE-2025-23242/23243 on older Riva deployments.

| Shodan Query | Notes |
|---|---|
| `port:9000 port:50051 http.html:'"status":"ready"'` | Two-port co-presence + health response |
| `port:9000 http.html:"NIM"` | NIM banner in headers |
| `port:50051` | gRPC only — narrow by country/org to reduce noise |

---

## Combined / cross-platform

| Shodan Query | Notes |
|---|---|
| `http.html:"/v1/audio/speech" -openai` | **NEW HIGH-YIELD** — catches entire OpenAI-compat TTS category (Kokoro + Orpheus + Chatterbox + Parler + Dia + Voxtral) in one query |
| `(http.title:"Whisper" OR http.title:"Coqui" OR http.title:"Piper" OR http.title:"Bark")` | Major TTS/ASR umbrella |
| `(http.html:"openvoice" OR http.html:"chattts" OR http.html:"f5-tts" OR http.html:"xtts")` | New-generation voice cloning umbrella |
| `(http.html:"rvc-webui" OR http.html:"GPT-SoVITS" OR http.html:"so-vits-svc" OR http.html:"Applio")` | Voice-cloning umbrella |
| `(http.html:"pipecat" OR http.html:"vocode" OR http.html:"livekit-agents")` | Real-time voice-agent umbrella |
| `(http.title:"Whisper" OR http.html:"coqui") country:US` | Geographic scoping |
| `(http.title:"Whisper" OR http.html:"coqui") org:"hospital"` | Healthcare exposure (HIPAA) |
| `(http.title:"Whisper" OR http.html:"coqui") org:"university"` | Academic exposure |
| `port:9000 port:11434` | Compound stack: Whisper ASR webservice + Ollama on same host |

---

## Probe semantics for live verification

| Endpoint pattern | Confirms |
|---|---|
| `GET /v1/audio/voices` → JSON `{"voices":[...]}` | OpenAI-compatible TTS server (rsxdalv, AI TTS Server) |
| `POST /v1/audio/transcriptions` (no auth) → 200 with text | Unauth Whisper-compatible ASR — confirmed compute theft |
| `POST /api/tts` (Coqui legacy) → audio bytes | Coqui TTS legacy compute open |
| `POST /api/tts/speakers` (Coqui XTTS) → speakers list | XTTS speaker enumeration |
| `GET /info` (TGI / TEI / Whisper variants) → model JSON | Model identification |
| `GET /system_stats` (Pipecat / Gradio) → GPU info | Resource fingerprint |
| `WS /audio` or `/listen` (real-time) → 101 Upgrade | Voice-agent live channel |

---

## Methodology notes

- Voice-AI servers frequently expose **VRAM/GPU info** through Gradio's `/system_stats`-style endpoints. Combine with `comfyui-cloud-survey-2026-05.md`'s VRAM-tally methodology to estimate compute exposed.
- **HIPAA risk:** Whisper transcription servers in healthcare orgs may be processing patient encounters. Treat any `org:"hospital"`-tagged hit as PHI-relevant; case studies must scrub transcript content.
- **Right-of-publicity / biometric data:** Voice-cloning servers loaded with celebrity speaker embeddings represent a different harm class. Document the existence of speaker libraries; do not attempt to enumerate or trigger generation.
- **Real-time agent abuse vector:** Pipecat / LiveKit-Agents / Vocode unauth endpoints can be hijacked to make outbound calls (the framework handles SIP/twilio/daily.co integration). Document the surface; do not invoke.

---

## Verified dork results + FP traps (re-run 2026-05-29)

Category 17 re-run via Playwright (Shodan API keys dead). 15 dorks. Key lesson:
**the high-severity voice-AI API servers are Shodan-dark behind JSON-only roots**
(Insight #67). Only demo UIs index.

### Confirmed-useful (real instances)

| Dork | Total | Yield |
|------|------:|-------|
| `http.title:"Chatterbox TTS"` | 18 | CLEAN — all real Chatterbox web UIs (ports 8004/4123/8000). Voice-clone surface. Use this, NOT the html-keyword form. |
| `http.html:"/v1/audio/speech" -openai` | 12 | Highest-yield cross-platform OpenAI-compat TTS; selects on API contract. uvicorn on tier-2 cloud. |
| `"whisper.cpp" "/inference"` | 12 | CLEAN conjunctive — real whisper.cpp ASR (ports 9000/8081/8083/8085). |
| `port:8880 http.html:"Kokoro"` | 2 | Real Kokoro demo pages (Swagger/web UI only). |
| `http.html:"xtts"` | 34 | ~50% rule — real XTTS UIs mixed with FP (lang-learning apps, GARR research, KR trading site). Needs title anchor. |

### FP traps (do NOT re-run these / filter required)

| Dork | Total | Trap |
|------|------:|------|
| `http.html:"chatterbox"` | 96 | FP SWAMP. Collides with `chatterboxwalls.com` (photo wall art), `entermediadb` DAM product, LexisNexis Digital Library, TSLM Dashboard. Single-keyword collision (Garak/Whisper lesson). Use `http.title:"Chatterbox TTS"`. |
| `http.html:"rvc-webui"` | 4 | FP — all Beijing Volcano Engine (ByteDance). Primary source: `:8000/openapi.json` title = `北京open ai relay 服务器` (Beijing OpenAI RELAY server, LLM proxy), NOT RVC. The `rvc-webui` string was incidental HTML. Would falsely confirm 11x-CVSS-9.8 RCE. Verify against `:7865/` Gradio root, not the html string. |
| `http.html:"so-vits-svc"` | 2 | FP — both CN music-platform marketing pages (Auralink, stfdlnb.cn). so-vits-svc proper is Gradio/JSON, Shodan-dark. |
| `http.html:"GPT-SoVITS"` | 22 | brand-dork, page-1 mostly FP (PixivTranslate, dir listings, AI SaaS). Ports 80/8800/8000, NOT 9880. The mentions index; the API does not. |

### Shodan-dark (0 results = the RCE/PII surfaces are unmappable passively — Insight #67)

| Dork | Total | Why dark |
|------|------:|----------|
| `http.html:"GPT-SoVITS" port:9880` | 0 | API JSON-only root; 5x critical CVE surface invisible |
| `port:8899 http.html:"Orpheus"` | 0 | Orpheus API JSON-only |
| `http.title:"Orpheus TTS"` | 0 | variant space exhausted — Orpheus fully dark |
| `port:8880 http.html:"/dev/captioned_speech"` | 0 | Kokoro unique path not in indexed HTML |
| `http.html:"system_health" http.html:"active_batch_requests"` | 0 | Deepgram `/v1/status` JSON not crawled |
| `port:9090 "WhisperLive"` | 0 | WS JSONL not indexed; 9090 = Prometheus territory |

**To survey the RCE population (GPT-SoVITS/RVC): masscan ports 9880/7865/7860 across tier-2 cloud, fingerprint by JSON API shape. Shodan only shows the demo-UI minority.**
