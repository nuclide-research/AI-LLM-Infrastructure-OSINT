# 113.240.68.47 — Full Attack-Surface Enumeration

**Role:** NICE 541 Vulnerability Assessment Analyst
**Target:** `113.240.68.47` (China Telecom Hunan, Changsha)
**Date:** 2026-06-08
**Methodology:** Banner-grab + TLS-cert harvest + read-only HTTP GET + aimap fingerprint. No auth attempts, no exploitation, no NSE scripts.

---

## Open Ports Table (full TCP/65535 swept)

| Port  | State | Service             | Version / Banner                                            | Auth   |
|-------|-------|---------------------|-------------------------------------------------------------|--------|
| 22    | open  | OpenSSH             | `SSH-2.0-OpenSSH_8.9p1 Ubuntu-3ubuntu0.15` (Ubuntu 22.04)   | n/a    |
| 8188  | open  | ComfyUI             | `Python/3.13 aiohttp/3.13.5`, app version **0.23.0**         | NONE   |
| 20111 | open  | FastAPI/uvicorn TTS | `server: uvicorn`, OpenAPI 3.1.0 "Edge Runtime API v0.1.0"   | NONE   |
| 20112 | open  | FastAPI/uvicorn TTS | `server: uvicorn`, OpenAPI 3.1.0 "Edge Runtime API v0.1.0"   | NONE   |
| 42113 | open  | unknown TCP         | TCP-accept then silent (timeout on HTTP/TLS/empty-write)    | unknown|

Shodan saw 2 ports (22 + 8188). Active nmap full-port discovered **3 additional services** that the operator never advertised through Shodan’s passive cache: two unauthenticated voice-cloning TTS APIs (20111, 20112) and a fifth listener (42113) that accepts the TCP handshake but does not respond to HTTP, TLS, or null writes within 6s.

Filtered (firewalled) ports observed: 25, 53, 135-139, 445, 1900, 2869, 3333, 4444, 5554 — the operator drops Windows / NetBIOS / SMTP scanners explicitly, the rest of the 65,535 TCP port space returned RST (closed). Verdict: deliberate egress-list firewall, not "everything open by default."

---

## TLS Certificates

`113.240.68.47` itself **has no TLS-bearing ports.** 8188 is plain HTTP (aiohttp), 20111/20112 are plain HTTP (uvicorn), 443 returns RST. **No certificate-based attribution available on the target IP.**

Attribution gold lives one hop sideways — see "/24 shadow scan" below.

---

## aimap Fingerprint (raw/aimap-report.json)

aimap v1.9.53 confirms:

```
113.240.68.47:8188 — ComfyUI 0.23.0
  Auth: NONE   Risk: CRIT
  Python 3.13.13 (Anaconda)
  PyTorch 2.12.0+cu130
  argv: main.py --listen 0.0.0.0 --port 8188
  GPU: 8 x NVIDIA A100-SXM4-80GB (cuda:0..7)
  VRAM per GPU: 79.2 GB  (total ~640 GB GPU VRAM)
  RAM: 1.08 TB total / 1.05 TB free

  Findings:
  ✗✗ ComfyUI API unauthenticated — /system_stats returns operator config + GPU
  ✗✗ ComfyUI-Manager present — unauth custom-node install = pre-auth RCE
```

Manager confirmed at `/manager/version` → **V3.38.1**. ComfyUI-Manager exposes `POST /manager/install/git_url` and `/manager/queue/install` which clone arbitrary git repos and import them as Python custom nodes → arbitrary code execution as the ComfyUI process user. We did **not** invoke either; existence of the endpoint is the finding.

Additional read-only ComfyUI extraction (no auth, no writes):

- `/api/users` → `{"storage": "server", "migrated": true}` — multi-user mode is enabled
- `/api/userdata` → `["jnodes.settings.json", "comfy.settings.json"]` — user settings world-readable
- `/api/userdata/comfy.settings.json` → InstalledVersion `1.43.18`, custom color palette "obsidian", queue history expanded
- `/api/extensions` → confirms loaded custom-node packs: **ComfyUI-KJNodes, ComfyUI-Advanced-ControlNet, ComfyUI_LayerStyle**, plus the 3D / load3d stack (FastPLY, GS Splat, model exporter, recording manager) — this host is doing video / 3D / multi-modal generation, not just image diffusion
- `/models` → 56 model directories enumerated including `t5`, `llm`, `LLM`, `mmaudio`, `wav2vec2`, `insightface`, `facexlib`, `pulid`, `instantid` — face-targeting + audio + LLM models present
- `/queue`, `/history` → empty (idle at scan time)
- `/object_info` → 3.8 MB JSON, indicates full node graph available

The combination of installed packs (`comfy-aimdo` 0.4.7, `comfy-kitchen` 0.2.10), face-targeting models (`insightface`, `facexlib`, `pulid`, `instantid`), and the adjacent TTS endpoints (next section) is **a turnkey deepfake stack:** face-swap models in the same process as voice-cloning APIs on the same host.

---

## TCP/20111 & TCP/20112 — Voice-Cloning TTS APIs

Both ports expose Swagger UI (`/docs`), ReDoc (`/redoc`), `/openapi.json`, and `/health` without authentication.

OpenAPI title: **"Edge Runtime API v0.1.0"** (identical on both).

Endpoints (Chinese-language docstrings preserved in raw/tts-openapi-schemas.json):

```
POST /tts          —  同步 TTS 接口  (sync text-to-speech)
POST /tts_url      —  兼容旧接口：直接返回 WAV 音频字节
POST /tts/stream   —  流式 TTS 接口  (streaming)
GET  /health
```

Request schema:

```json
{
  "text": "string",
  "audio_paths": ["string"],   // local-path OR http/https URL list — REFERENCE AUDIO
  "storage": "tos | oss",      // 火山引擎TOS / 阿里云OSS
  "language": "string"          // optional language hint (20112 only)
}
```

The `audio_paths` parameter accepting **arbitrary http/https URLs to reference audio** is the voice-cloning primitive: caller supplies a target voice sample (URL), supplies the text, gets back a WAV of that voice saying that text. No authentication, no rate limiting visible. `storage: "tos"` indicates the output is uploaded to Volcengine TOS (ByteDance cloud object storage).

`/health` returns operator-grade usage telemetry:

```json
// TCP/20111
{"status":"ok","stats":{
  "done": 616898,
  "failed": 361,
  "audio_seconds": 8723442.880000541,         // ~2,423 hours of synthesized audio
  "inference_seconds": 1705300.8363978863     // ~474 GPU-hours of inference
}}

// TCP/20112
{"status":"ok","stats":{
  "done": 1628,
  "failed": 0,
  "audio_seconds": 2828.17,
  "inference_seconds": 14069.68
}}
```

20111 is the production endpoint (~617K jobs, 99.94% success). 20112 is a smaller staging / language-variant endpoint (storage param missing, has extra `audio_chunk_duration`/`audio_chunk_threshold` fields for long-text chunking). The Edge Runtime API title + Chinese docstrings + TOS/OSS storage param strongly suggests this is a derivative of an open-source TTS engine (possibly **CosyVoice**, **F5-TTS**, or **GPT-SoVITS** — all have similar reference-audio + text → WAV signatures and Chinese-language UIs) wrapped in a custom FastAPI shim. Confirming the upstream is a follow-up.

This is **the operator's flagship product, not lab traffic.** 2,423 hours of voice-cloned audio is a production voice-cloning SaaS running on this host.

---

## /24 Shadow Scan — `113.240.68.0/24`

Naabu sweep of ports 22 + 8188 across the /24 found:

- **18 SSH hosts** (.10, .17, .20, .26, .28, .29, .41, .43, .44, .45, .47, .51, .52, .55, .60, .86, .92, .93) — typical China Telecom small-business / VPS-cluster /24 density (~18/256 = 7% live)
- **1 ComfyUI host** — `.47` only. **The ComfyUI box is the only image-gen host in this /24.**

Extended sweep of high-AI-signal ports (3000, 3001, 6006, 8000, 8080, 8888, 11434, etc.) found 24 additional services on neighbors. Highlights:

| Neighbor IP        | Port  | Service                           | Significance                                |
|--------------------|-------|-----------------------------------|---------------------------------------------|
| `113.240.68.55`    | 3001  | **One API** (HTTP 200, `X-Oneapi-Request-Id`) | **LLM gateway / Cat-08 multi-provider key broker** |
| `113.240.68.55`    | 3000  | Next.js app, `<title>AI</title>`  | "AI" frontend, sibling of One API           |
| `113.240.68.55`    | 6006  | uvicorn (404 root)                | TensorBoard port — but FastAPI here         |
| `113.240.68.55`    | 443   | TLS                               | OV cert `*.sgpjbg.com`, Xcc Trust OV CA     |
| `113.240.68.10`    | 8888  | `Server: WVS`, sets `ecology_JSessionid` | **Weaver / FanRuan FineReport** (Chinese ERP, NOT Jupyter) |
| `113.240.68.26`    | 8000  | uvicorn                           | FastAPI service                              |
| `113.240.68.28`    | 80    | nginx/1.26.3 welcome              | parked                                       |
| `113.240.68.28`    | 8080  | Tomcat-style 404                  | Java app server                              |
| `113.240.68.41`    | 443   | nginx, redirects to xyssltd.com   | "湖南信佑实业" (Xinyou Industrial)           |
| `113.240.68.45`    | 443   | nginx, Let's Encrypt `jilanacademy.com` | Jilan Academy (online education)         |
| `113.240.68.52`    | 443   | TrustAsia DV cert `meyyun.com`     | Independent SaaS, "Meyyun"                  |
| `113.240.68.86`    | 443   | self-signed `HTTPS-Self-Signed-Certificate-861f491a8f8224fa` | parked        |
| `113.240.68.60`    | 443   | same self-signed CN as .86         | **Cert reuse → operator overlap**           |
| `113.240.68.92`    | 80/443| `Server: Quidway`                  | **Huawei H3C router / firewall**            |
| `113.240.68.93`    | 443   | TrustAsia DV `qrhykj.com`         | "Qirenhe Tech" (potential)                  |

**Attribution: the /24 is a heterogeneous customer block, NOT a single-operator AI cluster.** Different cert issuers (TrustAsia DV, Let's Encrypt, DigiCert DV, Xcc Trust OV, self-signed), different domains (meyyun, qrhykj, jilanacademy, xyssltd, sgpjbg), one Huawei perimeter device, no SAN overlap with `.47`. The `.86`/`.60` self-signed CN reuse is the only operator-overlap signal in the block — both look parked / staging.

**The interesting neighbor is `.55` — sgpjbg.com.** "sgpjbg" is the public domain of Changsha Jinglüe Zhichuang Information Technology Co., Ltd. (长沙景略智创信息技术有限公司). One API on 3001 + Next.js "AI" frontend on 3000 + OV cert with the company name in the `O=` field → this is a Changsha-based AI gateway / LLM SaaS operator. Whether `.47` belongs to the same operator is **not** establishable from cert data alone — no SAN overlap, no shared Server header, different cert chains. The colocation in the same /24 is suggestive but not load-bearing (China Telecom Hunan customer blocks pool unrelated customers).

`.47` operator attribution remains **open** — no TLS cert, no HTTP `Server` brand string beyond stock aiohttp/uvicorn, no rDNS PTR record published, no operator name in any HTTP body. The TTS endpoints' Chinese docstrings and Volcengine TOS / Aliyun OSS storage params confirm **Chinese mainland operator**, but not which one. Follow-up: WHOIS the IP allocation block at the /24 level, query passive DNS for any hostname that has resolved to `113.240.68.47`, check JA3/JA4 fingerprint of the ComfyUI / FastAPI TLS clients calling out (if observable).

---

## Total Attack-Surface Assessment

### Confirmed unauthenticated surfaces (verified 200-with-data)

1. **ComfyUI 0.23.0 on TCP/8188** — full UI, queue control, history, custom-node install (via Manager v3.38.1), userdata read, model directory listing. Pre-auth RCE class via ComfyUI-Manager `install/git_url`. 8 × A100-80GB visible.
2. **Voice-cloning TTS on TCP/20111** — `/tts`, `/tts/stream`, `/tts_url` accept arbitrary text + reference audio URLs, return WAV. 616,898 prior jobs in `/health` telemetry. **Production endpoint.**
3. **Voice-cloning TTS on TCP/20112** — second instance (staging / language-variant). Same schema, 1,628 prior jobs.

### Verified hardened surfaces

- **TCP/22 OpenSSH 8.9p1 Ubuntu 22.04** — banner only; no auth attempted; CVE-relevant version is current 3ubuntu0.15 patchset (June 2025-era), no known unauth pre-CVE-2024-6387 trigger.
- **TCP/42113** — accepts TCP handshake then silent. Could be a custom protocol, a TLS server requiring SNI, or a proxy listener gated on first-byte. Not enumerable without active probing past the restraint line.

### Unverified / cannot enumerate

- TCP/42113 service identity. Possible candidates: Triton Inference Server gRPC (8001), vLLM admin, OpenAI-compatible API backend, internal SSH tunnel. Will require either a TLS-SNI rotation or a binary protocol fuzz to identify; both exceed the read-only restraint of this assessment.

### Risk Summary

| # | Finding                                            | Severity | Verified | Class                          |
|---|----------------------------------------------------|----------|----------|--------------------------------|
| 1 | ComfyUI 8188 unauthenticated + Manager → RCE       | CRITICAL | Yes      | Pre-auth RCE                   |
| 2 | TTS API 20111 unauthenticated voice-cloning       | CRITICAL | Yes      | Disinformation / fraud surface |
| 3 | TTS API 20112 unauthenticated voice-cloning       | CRITICAL | Yes      | Disinformation / fraud surface |
| 4 | TCP/42113 unidentified accept-then-silent listener | UNKNOWN  | partial  | Surface open, identity opaque  |
| 5 | 8 × A100-80GB GPU exposed via unauth ComfyUI       | CRITICAL | Yes      | LLMjacking / cryptojacking surface |
| 6 | Multi-modal model inventory (face + TTS + LLM)     | CRITICAL | Yes      | Deepfake toolkit colocation    |

### Why this matters

The single host runs:
- 640 GB of A100 GPU VRAM (top 1% of any exposed-AI-infra finding in our corpus)
- a face-swap / face-conditioning model directory (insightface, facexlib, pulid, instantid)
- a production voice-cloning API with ~617K jobs of prior history
- a ComfyUI workflow runner with arbitrary-code-execution surface via the Manager extension

A single anonymous HTTP caller can: synthesize the voice of any sample audio URL, generate face-conditioned images via ComfyUI, and execute arbitrary Python by registering a custom-node via the Manager. This is a **turnkey deepfake-generation stack** sitting open on the public internet on a Chinese commercial /24.

The /24 shadow scan rules out "obvious cluster head" — there is no ssh+8188+20111 sibling. `.47` is the single endpoint exposed for these services.

---

## Raw Evidence (this directory, `raw/`)

- `nmap-full-tcp.txt` — full 65535 TCP scan, 5 open ports
- `naabu-ai-ports.txt` — AI-port targeted scan confirms 22 + 8188 only on the AI-port list
- `aimap-report.json` + `aimap-run.txt` — aimap v1.9.53 fingerprint + deep enum
- `banners-22-8188.txt` — SSH + HTTP banners
- `comfyui-api-probes.txt` — /system_stats, /queue, /history, /api/users, /api/userdata, /models
- `comfyui-deep-probes.txt` — /manager/version (3.38.1), /api/userdata file dump, /api/extensions
- `extra-ports-banners.txt` — 20111/20112/42113 banner grabs
- `uvicorn-discovery.txt` — Swagger/OpenAPI confirmation + /health telemetry
- `tts-openapi-schemas.json` — full OpenAPI 3.1.0 spec for both TTS APIs
- `port-42113-probe.txt` — null-response confirmation
- `tls-certs.txt` — TLS cert subjects/issuers across the /24
- `neighbor-cert-sans.txt` — SAN harvest for attribution clustering
- `naabu-slash24.txt` — /24 sweep on 22+8188 (only .47 has 8188)
- `naabu-slash24-ai-ports.txt` — /24 sweep on 16 AI-relevant ports
- `neighbor-banners.txt` — HTTP banners for neighbor services (incl. One API @ .55:3001)

---

## Restraint Ledger

What was **NOT** done, by design:

- No SSH auth attempts (no creds, no keys, no public-key probe)
- No POST to any TTS endpoint (no synthesized audio generated)
- No POST to any ComfyUI workflow endpoint (no GPU cycles consumed)
- No POST to `/manager/install/*` (RCE surface confirmed by version-endpoint only)
- No NSE script invocation (`nmap -p- -sV -sC` was avoided; bare `nmap -p- -Pn` only)
- No port 42113 fuzzing past first-byte HTTP/TLS probe
- No model file downloads from `/models/<dir>/<file>`
- No `/view`, `/api/view`, or output-image fetches

Surface open, access not exercised. The finding is the surface map, not the exploit chain.
