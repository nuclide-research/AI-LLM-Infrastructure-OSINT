# 116.202.28.181 — Pantaflow Live Transcription Server

**Date:** 2026-05-22  
**Survey:** 17 — Voice/Audio AI  
**Severity:** CRITICAL  
**Operator:** Pantaflow (pantaflowai.com) — German AI transcription SaaS  
**Host:** 116.202.28.181 (Hetzner DE, AS24940)  
**PTR:** static.181.28.202.116.clients.your-server.de  
**TLS CN:** pantaflowai.com  

---

## Stack

| Port | Service | Auth | Notes |
|------|---------|------|-------|
| 8001 | Live Transcription Server (custom FastAPI v0.1.0) | **none** | German, whisper-streaming:8000 backend |
| 8000 | faster-whisper-server Gradio 4.44.0 | **none** | 15 Systran models, translate endpoint |
| 9000 | MinIO S3 API | **required** | AccessDenied on / |
| 443  | nginx reverse proxy | — | TLS CN=pantaflowai.com |

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, S7056, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6900, K6935, K7003, T5896

<!-- ksat-tag:auto-generated:end -->

---

## Five-Primitive Chain (CRITICAL)

All five primitives are unauthenticated, no token required.

**Primitive 1 — Unauth session read**  
`GET /session` returns `{"session":{"id":null,"started_at":null,"transcripts":[],"full_text":""},"transcript_count":0}` when idle.  
During an active meeting: returns session ID, start timestamp, and full live transcript.

**Primitive 2 — Unauth session start**  
`POST /session/start?meeting_id=<any>` — any caller, any ID string, instant 200.  
No validation, no HMAC, no auth header.

**Primitive 3 — Session ID collision**  
Re-POST same `meeting_id` clobbers the active session. Timestamp resets, transcript state wiped.  
Effect: interrupt any in-progress meeting transcription.

**Primitive 4 — Unauth session termination**  
`POST /session/end` terminates the active session from any IP.  
Response includes `transcript_file: /app/transcripts/<session-id>.txt` — confirms server-side persistence path.

**Primitive 5 — WebSocket passive eavesdrop**  
`WS /ws/transcripts` accepts anonymous connections.  
Streams: `session_start` event (session ID + meeting ID), audio transcription results in real-time, `session_end` event with transcript file path.  
Also: `WS /ws/audio` accepts anonymous audio push.

---

## Second Surface — Unauth Whisper Playground (:8000)

`fedirz/faster-whisper-server` behind Gradio 4.44.0. Unauthenticated audio upload or mic stream → transcription output.

- 15 Systran/faster-whisper models: tiny.en, base, small, medium, large-v1/v2/v3, distil-large-v2/v3, plus language-specific variants
- `task=translate` endpoint converts source audio (any language) to English text
- No auth, no rate limit, no file size restriction confirmed

---

## Operator Attribution

- **Domain:** pantaflowai.com (registered Namecheap, updated 2025-07-13)
- **CT log subdomains:** `transcribe.pantaflowai.com`, `cms.pantaflowai.com`, `*.transcribe.pantaflowai.com`
- **CMS:** WordPress 8.3.31/PHP (PleskLin), DE locale
- **Admin username:** `iljar_52qx2slf` (leaked via WordPress author archive)
- **Product:** `transcribe.pantaflowai.com` — the exposed server IS the product, deployed raw without auth

---

## Arsenal Chain Results

| Tool | Result |
|------|--------|
| JAXEN | In corpus (Survey 17 harvest) |
| aimap | :9000 MinIO auth-required (medium); :8001/:8000 not fingerprinted (custom platform) |
| aimap-profile | Hetzner DE bare VPS, commercial sector |
| VisorGraph | TLS CN → pantaflowai.com pivot confirmed |
| VisorBishop | MinIO:9000 adjacent (auth required) |
| VisorSD | Shodan credits exhausted |
| VisorGoose | N/A |
| menlohunt | 0 GCP surface (Hetzner, expected) |
| recongraph | Running (pending) |
| nu-recon | Running (pending) |
| VisorLog | 2 events ingested (IDs 35919, 35920) |
| VisorScuba | Pending (ECS field mapping gap) |
| BARE | No MSF coverage (top score 0.501 < 0.55 threshold) — first-party authz bug class |
| VisorCorpus | 100-case focused corpus built |
| VisorAgent | [ethical-stop] |
| VisorRAG | N/A |
| VisorHollow | [—] Windows-only |
| cortex | 0 ops (markdown format mismatch) |
| JS-bundle | N/A (:8001 is JSON API; :8000 Gradio bundle not extracted) |

---

## Impact

Any anonymous internet client can:
1. Monitor active meeting transcriptions in real-time via WebSocket or polling
2. Disrupt meetings by clobbering the session (Primitive 3) or terminating it (Primitive 4)
3. Learn internal server paths (`/app/transcripts/<id>.txt`)
4. Push audio to the transcription engine via `POST /audio` or `WS /ws/audio`
5. Upload arbitrary audio to the Whisper Playground for transcription/translation at the operator's compute cost

The exposed system is Pantaflow's own production product, not a test instance.

---

## Toolchain Provenance

Discovery: Survey 17 Voice/Audio AI Shodan harvest → masscan tier-2  
Fingerprint: manual (custom platform, no aimap fingerprint)  
Chain: aimap → recongraph → VisorGraph (pantaflowai.com) → VisorLog → BARE → VisorCorpus  
