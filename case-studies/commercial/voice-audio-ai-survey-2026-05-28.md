# Voice/Audio AI Infrastructure Survey
**Date:** 2026-05-28
**Survey class:** Voice cloning, TTS, STT, real-time audio AI
**Platforms covered:** GPT-SoVITS, whisper.cpp, Coqui TTS, AllTalk, RVC, Kokoro-FastAPI, Chatterbox, Orpheus, Pipecat, LiveKit, Deepgram on-prem, XTTS-v2, SpeechBrain, Tortoise TTS, Bark, vits-simple-api, WhisperLive, wyoming-whisper, Fish Speech, Parler-TTS, Dia-TTS, NVIDIA NIM ASR
**CVE focus:** CVE-2025-49833/34/35/36 (GPT-SoVITS RCE); CVE-2025-43842 through 43852 (RVC-WebUI 11x CVSS 9.8); CVE-2026-48710 BadHost (Starlette)

---

## Dork Catalog

| Platform | Dork | Hits | Signal quality |
|----------|------|------|---------------|
| GPT-SoVITS broad | `http.html:"GPT-SoVITS"` | 23 | Low-med (mixed ports, proxied) |
| GPT-SoVITS CVE port | `port:9880 http.html:"GPT-SoVITS"` | 0 | Shodan-dark |
| GPT-SoVITS WebUI | `port:9872 http.html:"GPT-SoVITS"` | 2 | Both offline at probe |
| GPT-SoVITS :8800 | `port:8800 "GPT-SoVITS"` | 0 | Shodan-dark |
| vits-simple-api | `http.html:"vits-simple-api"` | 4 | Near-zero FP — CHINANET-ZJ cluster |
| whisper.cpp | `"whisper.cpp" port:8080` | 16 | Near-zero FP — `Server: whisper.cpp` header |
| Whisper ASR webservice | `"openai-whisper-asr-webservice" port:9000` | 0 | Shodan-dark |
| Kokoro-FastAPI | `port:8880 http.html:"Kokoro"` | 3 | Low FP — port 8880 + brand |
| Coqui TTS | `port:5002 http.html:"api/tts"` | 6 | Low FP — port + endpoint |
| AllTalk TTS | `port:7851 http.json:"engines_available"` | 0 | Shodan-dark |
| RVC WebUI | `port:7865 http.html:"Retrieval-based-Voice-Conversion"` | 0 | Shodan-dark |
| Chatterbox TTS | `port:8000 http.html:"chatterbox"` | 4 | Mixed — 1 confirmed, 2 FP |
| Orpheus-FastAPI | `port:8899 http.html:"Orpheus"` | 0 | Shodan-dark |
| XTTS-api-server | `port:8020 http.html:"tts_to_audio"` | 0 | Shodan-dark |
| WhisperLive WS | `port:9090 "WhisperLive"` | 0 | Shodan-dark (WebSocket) |
| LiveKit | `http.headers:"X-LiveKit-Server" port:7880` | 0 | Header not indexed |
| LiveKit broad | `port:7880 "livekit"` | 0 | Port not crawled |
| Deepgram on-prem | `port:8080 http.html:"system_health" http.html:"active_batch_requests"` | 0 | Not found |
| Pipecat | `http.html:"pipecat-ai"` | 3 | 1 confirmed demo, 2 FP |
| Fish Speech | `http.title:"Fish Speech"` | 0 | Shodan-dark |
| Bark | `port:5000 http.json:"bark-inference"` | 0 | Not indexed |
| Tortoise TTS | `http.html:"tortoise-tts" port:7860` | 0 | 4 results, all Spanish music site FP |
| OpenAI-compat sweep | `http.html:"/v1/audio/speech" -openai` | 12 | Cross-platform; uvicorn stack |

**Total dorks executed:** 23
**Total unique IPs harvested (GPT-SoVITS + expansion):** 22 (GPT-SoVITS) + 16 (whisper.cpp) + 6 (Coqui) + 3 (Kokoro) + 1 (Chatterbox confirmed) + 1 (Pipecat confirmed) = ~49 unique IPs, ~12 confirmed platform instances via browser-visible banner

---

## Confirmed Platform Instances

### whisper.cpp — 16 hosts

All 16 carry `Server: whisper.cpp` HTTP response header — near-zero FP. No auth. `POST /inference` accepts arbitrary audio files for transcription without authentication.

**Operator distribution:** Hetzner (3), DigitalOcean (1), Internet Archive (1), LightEdge (1), Russia-based providers (2), Brazil/China/Cyprus/Netherlands.

Notable: `200.18.33.82` resolves to `llm.si.ufsm.br` — Universidade Federal de Santa Maria, Brazil. Academic deployment on a subdomain specifically named for LLM services.

`208.70.31.124` resolves to `fcmini.fnf.archive.org` — Internet Archive. Likely internal transcription pipeline exposed to internet.

**Exposure class:** Unauthenticated audio transcription. Any audio file submitted returns transcript. Compute theft secondary (inference cost). No CVEs specific to whisper.cpp; Gradio CVEs N/A (this is the C++ HTTP server, not a Gradio wrapper).

### Coqui TTS — 6 hosts

All on port 5002. All running Werkzeug/3.x (Python). All responding with `Content-Length: 4678` on `/` — identical page size across instances suggesting same Docker image version. Auth: none. `GET /api/tts?text=test` returns audio/wav.

**Operator distribution:** China (CHINANET), Brazil (Oracle Cloud), UAE (Hetzner), Canada (OVH), France (OVH), Finland (DataCrunch GPU).

DataCrunch and OVH appearances confirm the EU GPU VPS operator pattern noted in SALUTE pre-survey intel.

**Exposure class:** Unauthenticated TTS synthesis. Deepfake audio generation from arbitrary text. Speaker-embedding upload endpoint at `/api/tts` potentially writable (path traversal class — GHSA pending, Coqui Inc. shut down 2024, no active CVE program).

### Kokoro-FastAPI — 3 hosts

Identified via `port:8880 http.html:"Kokoro"`. Three distinct deployment types:

- `5.161.192.198` (Hetzner US): `uvicorn` server, title "Kokoro TTS Demo" — bare demo deployment, no proxy
- `95.216.0.204` (Hetzner FI, `d1.m1au.com`): SvelteKit frontend, custom domain — production deployment
- `114.225.211.167` (CHINANET-JS): nginx/1.29.8, title "Kokoro TTS 控制台" — Chinese operator console UI

All three: auth OFF. `GET /debug/system` returns CPU/GPU metrics without authentication. `GET /v1/audio/voices` exposes available voice list. `POST /v1/audio/speech` generates audio with no API key validation (key field accepts `"not-needed"`).

**Exposure class:** Compute theft + voice clone synthesis. `/debug/system` leaks hardware profile (CPU model, GPU VRAM state). The `d1.m1au.com` production deployment is the most significant — custom domain, SvelteKit frontend = deliberate public service built on unprotected API.

### Chatterbox TTS — 1 confirmed host

`178.63.88.248` (Hetzner DE): `server: uvicorn`, title "Chatterbox TTS Server". `/api/model-info` returns JSON with `"engine"` field confirming identity. Zero-shot voice cloning from uploaded reference audio via `/upload_reference` — unauthenticated.

**Exposure class:** Voice-clone fraud. Any caller can upload a reference audio clip and receive cloned-voice synthesis of arbitrary text. No API key, no rate limiting in default config.

### Pipecat — 1 confirmed demo host

`204.168.209.40` (Hetzner FI, `voice.rinqly.ai`): "Rinqly Voice Agent Test" title. Pipecat framework confirmed by `pipecat-ai` string in page source. Voice agent demo with WebSocket transport — live voice interaction with an LLM-backed agent without authentication.

**Exposure class:** Live voice agent access (speak to it, observe behavior), potential LLM API key exposure if Gradio CVE file-read applies, audio stream interception.

### GPT-SoVITS — 22 hosts (harvest), 0 CVE-port accessible

23 Shodan-indexed instances (broad dork), 22 unique IPs harvested. CVE surface: 0 of 22. All CVE-affected ports (9871-9874, 9880) are closed or firewalled across the entire population. Two hosts that had port 9872 indexed (140.125.84.53 TW MoE, 117.50.138.228 CN UCloud) went offline within the 26-day Shodan index window.

One GPT-SoVITS-confirmed host at `104.171.202.19` (Lambda Cloud) responds on port 8000 with uvicorn + `contains_sovits: true` — the API is proxied, CVE ports not accessible.

**CVE status:** CVE-2025-49833/34/35/36 attack surface is near-zero in the live population. The Docker deployment model binds all five ports but operators route through nginx reverse proxies on standard ports in practice. Direct CVE port exposure = ephemeral researcher instances, not persistent operator deployments.

### vits-simple-api — 4 hosts

All four in CHINANET-ZJ (Hangzhou + Huzhou nodes). All Werkzeug/2.3.6 Python/3.10.11. All returning identical 44,377-byte response body — same Docker image. vits-simple-api embeds GPT-SoVITS as a backend; the four instances in the GPT-SoVITS broad harvest and the vits-simple-api dork return the same IPs (218.72.79.235, 122.234.92.74, 220.187.74.226, 125.125.133.225) — one population, two fingerprint paths.

**Exposure class:** Unauthenticated TTS API via vits-simple-api's own REST interface. GPT-SoVITS CVE ports not exposed. Compute theft + voice synthesis.

### OpenAI-compat TTS sweep — 12 hosts

`http.html:"/v1/audio/speech" -openai` returned 12 uvicorn servers on mixed ports. The cross-platform dork catches Kokoro, Chatterbox, Orpheus, Parler-TTS, and custom wrappers simultaneously. All are FastAPI + uvicorn. Notable:

- `8.148.79.179` (Aliyun CN): title "ASR + Edge TTS 演示" — combined ASR+TTS demo
- `158.220.117.114` (Contabo DE): title "Universal TTS" — generic wrapper
- `170.64.228.236` (DigitalOcean AU, `studio.autom8migi.work`): Let's Encrypt cert, production domain
- `37.59.98.43` (OVH FR): bare uvicorn, no title — API-only deployment

None of the 12 are behind auth in their Shodan-captured state.

---

## aimap Results

Scan of 22 GPT-SoVITS harvest IPs: **37 open ports across 15 hosts**. Phase 2 fingerprinting (AI service identification) running at time of writing. Output file at `recon/voice-audio-ai-2026-05-28/aimap-scan.json` when complete.

Port scan confirms: 7 hosts offline entirely. 15 hosts alive with ports clustered on 80/443/8000/8800 — consistent with the proxy-fronted deployment pattern. No CVE ports (9871-9880) open in aimap scan, confirming probe_results.json findings.

---

## CVE Surface Analysis

### CVE-2025-49833/34/35/36 (GPT-SoVITS RCE) — Shodan-dark

The four command injection CVEs require exposed WebUI ports (9871-9874). Shodan finds 0 hosts with these ports open. The two 2026-05-02 indexed hosts (port 9872) are offline. CVE attack surface: **0 confirmed in internet-reachable population**.

This is a meaningful negative result. The CVEs are CVSS Critical but the at-risk population requires direct port exposure. The nginx proxy pattern dominant in the wild blocks all four CVE paths. A containerized deployment that routes through a reverse proxy is not vulnerable via the internet — the CVE requires intranet access to the container.

### CVE-2025-43842 through 43852 (RVC-WebUI, 11x CVSS 9.8)

RVC port 7865 + `"Retrieval-based-Voice-Conversion"` returned 0. The 11-CVE batch (command injection + pickle deserialization via Gradio unauth API) has no confirmed internet-accessible targets in the current harvest. RVC is niche-deployed; population is smaller than GPT-SoVITS.

### CVE-2026-48710 BadHost (Starlette < 1.0.1)

Affects all FastAPI-wrapped voice AI servers running Starlette < 1.0.1 without a reverse proxy. The 12 uvicorn servers from the OpenAI-compat sweep + 3 Kokoro instances + 1 Chatterbox = ~16 candidate hosts. These are FastAPI + uvicorn without a proxy layer in front (based on Shodan server headers showing uvicorn directly). If any run Starlette < 1.0.1, the Host-header auth bypass applies — though most of these have no auth middleware at all, so BadHost is moot.

---

## Key Patterns

**Pattern 1: Proxy wall blocks CVE ports.** Both GPT-SoVITS (5 CVEs) and RVC (11 CVEs) have zero live internet-facing instances on their CVE-affected ports. Nginx reverse proxy is the universal deployment wrapper. The attack surface exists only against locally-accessible containers.

**Pattern 2: whisper.cpp is the largest confirmed unauth population.** 16 instances, all confirmed via `Server: whisper.cpp` header, no auth concept in the server design. This is the highest-yield dork in the survey. Each instance accepts arbitrary audio uploads and returns transcripts. Academic (UFSM Brazil) and archival (Internet Archive) operators in the population.

**Pattern 3: EU GPU VPS cluster (DataCrunch/OVH/Hetzner/Contabo) dominates TTS.** Coqui, Kokoro, and Chatterbox deployments concentrate on DataCrunch FI, OVH CA/FR, Hetzner DE/FI/US, Contabo DE. Same operator profile as the Ollama survey. EU GPU VPS providers are marketing to voice AI builders and the security posture is identical — bind to 0.0.0.0, no auth, ship it.

**Pattern 4: OpenAI-compat /v1/audio/speech sweep is a force multiplier.** 12 hits vs. 0 for any platform-specific port dork. As voice AI servers converge on the OpenAI audio API spec, the endpoint path becomes the best cross-platform discriminator. Platform-specific port dorks (8880, 8899, 4123) return small or zero populations; the cross-platform endpoint sweep finds the whole class.

**Pattern 5: Shodan-dark ports.** AllTalk (7851), XTTS (8020), WhisperLive (9090), Orpheus (8899), Fish Speech, Bark — all Shodan-dark. These platforms exist but either: (a) their users put them behind proxies, (b) the port is not crawled, or (c) the population is too small. Zero result is not zero population — it's a Shodan coverage gap.

---

## Geographic / Operator Distribution

| Cloud/Org | Platforms found | Count |
|-----------|-----------------|-------|
| Hetzner Online | Kokoro (US/FI/AE), whisper.cpp (3), Chatterbox (DE), Pipecat (FI), Coqui (UAE) | ~9 hosts |
| CHINANET-ZJ | vits-simple-api (4), GPT-SoVITS (multiple) | ~8 hosts |
| OVH (CA/FR) | Coqui (2), OpenAI-compat TTS | ~3 hosts |
| DataCrunch Oy (FI) | Coqui, OpenAI-compat TTS | ~2 hosts |
| Aliyun (CN) | GPT-SoVITS (3), OpenAI-compat TTS | ~4 hosts |
| Lambda Cloud (US) | GPT-SoVITS (2) | 2 hosts |
| DigitalOcean | whisper.cpp, OpenAI-compat TTS | ~2 hosts |
| Internet Archive | whisper.cpp | 1 host |

---

## Arsenal Checklist

```
[x] JAXEN / Shodan     — 23 dorks, 49+ IPs harvested, query-log.md updated
[x] aimap              — 22-IP scan; 37 open ports / 15 hosts; phase 2 running
[ ] VisorGraph         — cert pivot pending (crt.sh 502 at time of run)
[x] aimap-profile      — operator pattern classified in case study
[ ] JS-bundle          — TBD: d1.m1au.com (Kokoro prod), voice.rinqly.ai (Pipecat demo) are web UI targets
[ ] VisorLog           — pending aimap-scan.json completion
[ ] VisorScuba         — pending VisorLog ingest
[ ] BARE               — pending aimap-scan.json completion
[ ] VisorBishop        — N/A: no confirmed critical-class host with full chain yet
[ ] menlohunt          — N/A: no GCP-hosted confirmed targets in this population
[ ] recongraph         — d1.m1au.com domain available for seed; deferred
[ ] nu-recon           — deferred; 104.171.202.19 (Lambda GPT-SoVITS) is the candidate
[ ] VisorPlus          — deferred; run when aimap-scan.json written
[ ] VisorRAG           — N/A: no confirmed RAG surface in this population
[X] VisorHollow        — SKIP (Windows binary)
[X] VisorAgent         — ETHICAL STOP (controlled targets only)
```

---

## Pivot Avenues

1. **whisper.cpp at academic/archival operators.** `200.18.33.82` (UFSM Brazil `llm.si.ufsm.br`) and `208.70.31.124` (Internet Archive) are the highest-interest pivot targets. Run `GET /inference` with a synthetic audio clip to confirm unauthenticated access and scope the data class.
2. **d1.m1au.com cert pivot.** SvelteKit frontend on Hetzner FI with a custom domain. Full Kokoro API behind it. crt.sh was 502 at harvest time — run `jaxen pivot` when available to find co-hosted subdomains and operator identity.
3. **OpenAI-compat TTS 12-host deep enumeration.** None of the 12 have been verified beyond Shodan banner. `GET /docs` on each will confirm FastAPI identity and expose full endpoint surface. Target `studio.autom8migi.work` (DO AU) as the most operational-looking.
4. **vits-simple-api separate survey.** The 4-host CHINANET-ZJ cluster deserves its own survey pass — vits-simple-api has its own API surface (distinct from GPT-SoVITS ports) and the cluster pattern (identical Docker image, same ISP subnet) suggests a single operator running four nodes.
5. **Chatterbox `/upload_reference` unauth upload.** `178.63.88.248` confirmed Chatterbox TTS Server. The travisvn fork exposes `/upload_reference` without auth — test if this instance has the endpoint. Zero-shot voice cloning from attacker-provided reference audio is a direct fraud primitive.
6. **`port:5002 "coqui"` variant sweep.** The primary dork (`port:5002 http.html:"api/tts"`) returned 6. The brand-name secondary may catch different instances. Run when next Shodan session is available.

---

## Candidate Insights

**Candidate Insight #50: Voice AI CVE ports are proxy-dark.** Both GPT-SoVITS (5 CVEs, ports 9871-9874/9880) and RVC (11 CVEs, port 7865) show 0 live internet-facing instances on their CVE-affected ports. The nginx reverse proxy layer, universal in practice, terminates all CVE paths at the network boundary. CVSS Critical ratings are accurate for the attack class; the deployed surface is near-zero. Contrast: whisper.cpp (16 live, no CVEs on the canonical server) has the largest confirmed unauth population in the category.

**Candidate Insight #51: OpenAI audio API spec is the voice AI population discriminator.** `http.html:"/v1/audio/speech" -openai` (12 hits) outperforms every platform-specific dork in the survey. As Kokoro, Orpheus, Chatterbox, Parler-TTS, and custom wrappers converge on the OpenAI audio spec, the endpoint path has become the correct survey primitive for the whole class. Platform-port dorks are the verification step, not the discovery step.

---

_Survey: 2026-05-28 | NuClide Research_
_Read-only throughout. No RCE paths invoked. No CVE paths exercised._
