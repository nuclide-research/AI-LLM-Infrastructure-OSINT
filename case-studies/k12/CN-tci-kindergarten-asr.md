# 117.50.80.181 — TCI Kindergarten ASR / Speech-Assessment Platform

**Date:** 2026-05-22
**Survey:** 17 — Voice/Audio AI
**Severity:** CRITICAL
**Operator:** TCI — CUHK-SZ / Nanshan-linked K12 speech-assessment platform (China)
**Host:** 117.50.80.181 (China)
**Ports:** 80 (nginx), 8000 (TCI Assessment System v1.0.0), 8001 (TCI ASR Service v3.0.0), 9000 (MinIO)

_NuClide Research · 2026-05-22 · Survey 17 companion to the [Pantaflow](../commercial/pantaflow-live-transcription-2026-05-22.md) finding — the second voice/audio host where the exposed system is the operator's own production product._

---

## Summary

`117.50.80.181:8001` runs the "TCI ASR Service" v3.0.0, a Chinese kindergarten classroom speech-assessment platform. The processing tier has no authentication. An unauthenticated internet caller can submit audio to the platform's automatic-speech-recognition, speaker-diarization, and voiceprint-registration pipeline. The same endpoints carry an arbitrary-path file-existence oracle through an unsanitised `ffmpeg -i` call. The platform's data class is kindergarten-age children's classroom audio and the voiceprint biometrics of children and teachers.

The auth posture is split. The transcript-export route is gated at HTTP 401. The audio-ingest, speaker-resolution, and speaker-registration routes are not gated. The operator gated the visible read path and left the processing tier — which holds both the path-injection bug and the biometric-enrollment endpoint — open.

No child audio file was retrieved. No voiceprint prototype was read. No transcript was exported. The exposure was enumerated to set severity and stopped there. On a minors-data target the restraint ethic is the entire posture: the finding is the open door, not anything behind it.

## Thesis fit

Confirms the auth-on-default thesis and extends [Insight #16](../../methodology/insight-16-status-code-is-identity-not-auth-state.md). A custom platform shipped with no auth concept on its processing endpoints. Per-route auth checking — not a single front-door probe — surfaced the split: `/api/export/transcript/*` returns 401, the processing routes do not. A single homepage 200 would have read as "platform alive" and missed the posture entirely.

---

## Stack

| Port | Service | Auth | Notes |
|------|---------|------|-------|
| 80 | nginx | — | default page |
| 8000 | TCI Assessment System v1.0.0 | not deep-probed | banner-read only |
| 8001 | TCI ASR Service v3.0.0 (uvicorn / FastAPI) | **split** | processing endpoints unauth; transcript export 401-gated |
| 9000 | MinIO S3 API | required | HTTP 403 on `/` |

**Backends** — declared by the `:8001` `GET /` features object, no keyword guessing required:

| Role | Backend |
|------|---------|
| `zh_asr_backend` | `speech_paraformer-large_asr_nat-zh-cn-16k-common` (Alibaba DAMO Paraformer) |
| `en_asr_backend` | `faster-whisper` |
| `speaker_backend` | `speech_eres2netv2_sv_zh-cn` (ERes2NetV2 speaker verification — voiceprint) |
| `diarization_backend` | `pyannote/speaker-diarization-community-1` |
| `speaker_registration` | `true` |

---

## F1. Unauthenticated ASR + speaker-registration pipeline (CRITICAL)

#### What was found

`POST /api/transcribe`, `POST /api/resolve-speakers`, and `POST /api/register-speaker` accept unauthenticated requests and process them. A probe to `/api/transcribe` with no token returned `{"status":"failed","transcripts":[],"task_id":"9661c9dd-2f55-414b-b326-fd21787d8c12","duration":null,...}`. The server assigned a task ID, invoked `ffmpeg`, and ran the pipeline. No HTTP 401. The endpoints are open. **Verified.**

The platform's own `GET /` banner declares `speaker_registration:true`, a `speech_eres2netv2_sv` speaker-verification backend, and a `pyannote` diarization backend. An unauthenticated caller reaches an ASR + speaker-diarization + voiceprint-enrollment pipeline.

#### Why it is bad

The platform processes kindergarten classroom audio. ASR produces transcripts of what was said in the room. Diarization attributes each utterance to a speaker. The `eres2netv2_sv` speaker-verification model and the `register-speaker` endpoint enroll and match voiceprint biometrics. The processing tier sits behind no auth gate.

A malicious caller can submit audio for transcription and diarization at the operator's compute cost, and can reach the `register-speaker` endpoint that writes biometric prototypes into the speaker registry. The voiceprints in that registry belong to children and teachers. **Verified** that the endpoints process unauthenticated requests; **Inferred** that the registry is writable end-to-end — the registration call was issued with a probe path, returned `status:failed` on the ffmpeg step, and was not driven to a completed enrollment.

#### Who it affects

Kindergarten-age children and teachers whose classroom audio and voiceprints the platform processes. The operator is a Shenzhen K12 speech-assessment deployment (see Operator attribution). Hosting is a bare China IP.

#### How it got exposed

The platform shipped with no auth concept on its processing routes. The operator added an auth gate to `/api/export/transcript/*` — the route that returns stored data, the one a casual review would check — and left ingest, resolution, and registration ungated. This is the partial-auth failure mode seen on the alpha-miner host: the operator believes the platform is protected because the route they checked returns 401. Per-route verification is the only way to see it.

---

## F2. Arbitrary-path file-existence oracle via `ffmpeg` path injection (HIGH)

#### What was found

`/api/transcribe` and `/api/resolve-speakers` accept a server-side `path` parameter and pass it unsanitised into `ffmpeg -y -i <path> -ar 16000 -ac 1 <out>.wav`. The JSON `error` field returns the raw ffmpeg result. The response is a boolean file-existence oracle:

- Path does not exist → `{"error":"Audio file not found: <path>"}`
- Path exists, is not audio → `{"error":"外部命令失败: ffmpeg -y -i <path> ..."}` (`外部命令失败` = "external command failed" — ffmpeg ran, the path was real)

The two responses differ. An unauthenticated caller distinguishes them and maps the server filesystem. **Verified.** Confirmed present via the oracle, read-only against structural and system paths:

```
/data/tci_system/asr-service/workdir/{cache,segments,output,logs,tmp,audio,speakers,models}
/share/models/ASR/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
/share/models/ASR/speech_eres2netv2_sv_zh-cn_16k-common
/data/tci_system/.env          /etc/environment          /app/config.json
/proc/1/environ  /proc/1/cmdline  /proc/self/environ  /proc/net/tcp  /proc/version
```

#### Why it is bad

The oracle confirms the existence of any file the service user can read. That includes the platform's own secret files — `/data/tci_system/.env`, `/etc/environment`, `/app/config.json` were all confirmed present — and `/proc/1/environ`, which on an un-hardened container holds the init process environment. It also confirms the existence of individual child audio files under `workdir/cache`.

**Verified:** the existence oracle works against arbitrary absolute paths. **Inferred, not exercised:** the oracle can confirm any specific child audio file by path; it was not pointed at one. **Not achieved:** file *content* extraction. The probe attempted to surface `/proc/1/environ` and `.env` contents through the ffmpeg error string. ffmpeg's stderr truncates at its own version banner before any file content. No environment variable and no `.env` value was recovered. ffmpeg 4.4.2 here is compiled with a wide protocol and demuxer set, which makes the path-injection a candidate SSRF and file-read primitive through ffmpeg's protocol demuxers — that escalation was not exercised.

#### How it got exposed

The endpoints treat a caller-supplied string as a trusted local path and hand it to a subprocess. There is no allowlist, no confinement to the upload directory, no rejection of `/proc` or absolute paths outside the workdir. The error string — ffmpeg's verbatim stderr — is returned to the caller, which converts a failed decode into an information-disclosure oracle.

---

## F3. Split-auth posture (root cause)

#### What was found

`/api/export/transcript/{1..30}` — 30 sequential probes, all HTTP 401. The transcript-export route is auth-gated. **Verified.** The processing routes in F1 are not. The account layer is otherwise reasonably built: `POST /api/auth/password-reset/request` returns HTTP 200 with `{"message":"如果邮箱存在，重置邮件已发送"}` ("if the email exists, a reset mail has been sent") — the non-enumerating response; `verify-email` with guessed tokens returns HTTP 400; `login/json` returns 401.

#### Why it is bad

The operator gated one route and shipped the rest open. The gated route is the safe one — it only reads stored transcripts. The open routes are the dangerous ones — audio ingest, the path-injection oracle, and biometric enrollment. The split produces false confidence: the route an operator checks first returns 401, so the platform reads as protected.

#### Who it affects

The same children and teachers as F1. The split is the structural reason F1 and F2 are reachable.

#### How it got exposed

Auth was added per-route rather than as middleware across the API surface. Whoever added the `/api/export/*` gate did not carry it to the processing routes. Middleware-level enforcement — auth checked once, before routing — would have closed all of it.

---

## Children's-data framing

The sensitive class on this host is kindergarten-age children's classroom audio and the voiceprint biometrics of children and teachers. This assessment enumerated the exposure to set a severity tier. It did not exercise any pathway against real data:

- The ffmpeg path oracle was driven against system and structural paths only. It was not pointed at any child audio file.
- The speaker-registry scopes — `kindergarten`, `teacher`, `nanshan`, `school`, `org1`, `org2`, `org4` — were probed for directory existence only. Every probe returned `NO_DIR` or a failure status. No biometric prototype was retrieved.
- The 30 `/api/export/transcript/{id}` probes were a yes/no auth check. Each returned 401 and the loop stopped. No transcript content was requested.
- MinIO `:9000` returned HTTP 403 on `/`. The connection confirmed an auth gate exists. No bucket was listed, no object was fetched.

The finding is the open door. The finding is not anything behind it.

---

## Operator attribution

Attribution is **Inferred**, banner-and-context only. "TCI" is taken from the `:8001` ("TCI ASR Service") and `:8000` ("TCI Assessment System") service banners. The speaker-registry scope names probed include `nanshan` — Nanshan is the Shenzhen administrative district that hosts the Chinese University of Hong Kong, Shenzhen and a large public kindergarten network. The scope names `kindergarten`, `teacher`, and `school` plus the `:8000` "Assessment System" banner identify a K12 / kindergarten speech-assessment deployment. There is no TLS on `:8001`, so no VisorGraph cert pivot was possible. The host is a bare China IP with no rDNS. Attribution does not resolve below "Shenzhen K12 speech-assessment platform, TCI-branded."

---

## Arsenal chain

| Tool | Result |
|------|--------|
| JAXEN | In corpus — Survey 17 tier-2 (216-host masscan set) |
| aimap | `:9000` MinIO auth-required (medium); `:8001` TCI ASR Service not fingerprinted (custom platform) — gap logged |
| aimap-profile | China, education sector; minors-data flag raised; ethics posture set to children's-data restraint |
| VisorGraph | No TLS on `:8001` — no cert pivot; attribution from banner strings |
| VisorBishop | Adjacent-port sweep — `:80` nginx default, `:8000` / `:8001` / `:9000` mapped |
| VisorSD | Shodan credits exhausted |
| VisorGoose | 0 Ollama co-located (dedicated ASR stack) |
| menlohunt | 0 GCP surface (China host) |
| recongraph | Ran — bare-IP seed |
| nu-recon | Ran |
| VisorLog | Ingested — CRITICAL, children's-data class flagged |
| VisorScuba | Rego field-mapping gap — scoring deferred |
| BARE | No packaged Metasploit module for the ffmpeg-path-oracle traversal class — first-party bug class |
| VisorCorpus | Focused corpus built |
| VisorAgent | [ethical-stop] — not fired at the operator host |
| VisorRAG | N/A |
| VisorHollow | [—] Windows-only |
| cortex | Auth-context split documented manually (markdown format mismatch) |
| JS-bundle | N/A — JSON API, no SPA |

---

## Impact

An anonymous internet client can:

1. Submit audio into the kindergarten ASR, diarization, and voiceprint pipeline at the operator's compute cost.
2. Reach `/api/register-speaker`, the endpoint that enrolls voiceprint biometric prototypes.
3. Map the server filesystem through the ffmpeg path oracle.
4. Confirm the presence of the platform's secret files — `/data/tci_system/.env`, `/etc/environment`, `/app/config.json` — and of `/proc/1/environ`.
5. Confirm the existence of individual child audio files by path under `workdir/cache`.

The transcript-export route is the one surface the operator gated. Everything that produces or enrolls the sensitive data is open.

---

## Honest negative space

- No file *content* was extracted. The ffmpeg oracle confirms existence only; ffmpeg's stderr truncates before any file content. `/proc/1/environ` and `.env` were probed for contents and yielded nothing.
- `:8000` "TCI Assessment System" was banner-read only, not deep-probed. Its auth posture and routes are not characterized.
- The speaker registry was probed by scope name for directory existence. Every probe returned `NO_DIR`. The registry's true scope structure and enrolled-record count are not mapped.
- The account-layer routes (`register`, `verify-email`, `password-reset`) are live and accept requests. A completed registration yielding a working account was not exercised. Open self-service signup is not verified — only that the routes respond.
- No TLS on `:8001` — no cert pivot. Operator attribution is banner-and-context only and does not resolve to a named legal entity.
- aimap v1.9.24 has no fingerprint for the TCI ASR Service. The platform was identified by manual banner read. Logged as a fingerprint gap, alongside the same gap on Pantaflow's `:8001`.

---

## Methodology — what this case study adds

The `ffmpeg -i <attacker-path>` pattern is a fingerprint-able bug class. Any ASR or audio platform that returns the ffmpeg error string to the caller and accepts a path parameter has the same oracle. The discriminator is the two-response split — `Audio file not found` versus `外部命令失败` (or the English `external command failed`). A candidate aimap deep-enumerator: post a known-nonexistent path and a known-existent system path (`/etc/hostname`), and flag the platform if the two responses differ. Carry-forward to the Survey 17 fingerprint set.

This is also a second data point for the per-route auth-checking discipline behind Insight #16. Both Survey 17 voice hosts — Pantaflow and TCI — passed a homepage probe and failed per-route. On TCI specifically the split was internal to one API: gated export, ungated processing.

## See also

- [Pantaflow Live Transcription Server](../commercial/pantaflow-live-transcription-2026-05-22.md) — Survey 17 companion, same date, same "the exposed system is the product" pattern
- [Session analysis 2026-05-22 — Voice/Audio AI follow-up](../../analysis/2026-05-22-voice-audio-pantaflow-tci.md)
- [Insight #16 — a status code is identity, not auth state](../../methodology/insight-16-status-code-is-identity-not-auth-state.md)
- `shodan/queries/17-voice-audio-ai.md` — Survey 17 query catalog

---

## Toolchain provenance

```
Discovery:    Survey 17 Voice/Audio AI Shodan harvest → masscan tier-2 (216-host set)
Fingerprint:  manual banner read — GET / on :8001 self-describes (custom platform, no aimap fingerprint)
Verify:       per-route probe — :8001 processing routes unauth, /api/export/transcript/* 401;
              ffmpeg path oracle confirmed against system/structural paths only
Chain:        JAXEN → aimap → aimap-profile → VisorBishop → recongraph → VisorLog → BARE → VisorCorpus
Restraint:    children's-data target — no child audio, no voiceprint, no transcript retrieved
```
