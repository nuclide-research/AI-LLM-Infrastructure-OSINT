# Session Analysis: Voice/Audio AI re-run (Category 17)

## 1. Overview

### Objective
Re-run Category 17 (voice/audio AI) under the manual-to-productize-to-re-run
discipline. The category was first surveyed 2026-05-08. Since then aimap shipped
ten voice fingerprints from the 2026-05-27/28 platoon intel. The goal: drive the
new fingerprints against a fresh harvest, chase the RCE (GPT-SoVITS, RVC) and
voice-clone (Chatterbox) surfaces the platoon flagged, and confirm or break the
auth-on-default thesis for this category.

### Scope and Constraints
Commercial tier-2 cloud (Contabo, OVH, Hurricane Electric, DigitalOcean,
ByteDance). Shodan via Playwright web UI only, both API keys dead. All active
probing through Mullvad (us-lax-wg-007). Metadata-only marker probes; no payload
execution, no voice-clone uploads, no Redis keyspace access, no RCE attempts.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. Shodan harvest by browser automation. aimap and the recon
tools run as bounded background commands. Verification probes via curl and a
python socket through Mullvad.

### Tools Used
Full 19-tool arsenal. Run with material output: JAXEN (Playwright), aimap,
aimap-profile, VisorGraph, VisorBishop, menlohunt, recongraph, nu-recon,
VisorLog, VisorScuba, BARE, VisorCorpus, cortex, JS-bundle check. Documented
non-runs: VisorSD/VisorPlus/VisorRAG (Shodan or embedding-key blocked),
VisorGoose (gov/edu scope), VisorHollow (Windows-only), VisorAgent (controlled
target only, internal-agent blocked on API key).

### Notable Configuration
aimap v1.9.39. nuclide.db at ~/visorlog/nuclide.db. Workspace
~/recon/voice-audio-rerun-2026-05-29/.

## 3. Methodology

### Enumeration approach
Fifteen Shodan dorks, prioritizing the platoon's near-zero-FP probes and the
RCE/voice-clone brand strings. Port-anchored and title-anchored dorks preferred
over html-keyword.

### Candidate identification
28 unique candidate IPs across the productive dorks. aimap fingerprinted them on
the seventeen observed ports.

### Validation checks
Primary-source marker probes on every confirmed and every disputed candidate.
Chatterbox via /health + /config. Kokoro via /debug/system or /v1/audio/voices.
MinIO via anonymous LIST. RVC candidates via /openapi.json. Redis via PING +
INFO server. Two tools (menlohunt, VisorBishop) cross-confirmed the Redis.

### Safeguards
Mullvad verified before probing and re-checked mid-run. No payloads. The
voice-clone upload endpoint, the Redis keyspace, and the GPT-SoVITS RCE chain
were left untouched. Read only what confirms severity.

## 4. Execution Trace

```
1. Read METHODOLOGY.md, SESSION.md, voice-audio platform intel, query catalog
2. Verified 19 arsenal binaries present + executable; aimap v1.9.39
3. Shodan key probe -> 401 (both keys dead) -> switched to Playwright web UI
4. Playwright: confirmed live Shodan session (dashboard, no login redirect)
5. 15 dork searches via browser; extracted Total + port facet + result cards per dork
6. Logged all 15 dorks to shodan/query-log.md with hit counts
7. Built 28-IP candidate list; aimap -scan-all-fingerprints x 25 ports -> TIMEOUT (900s cap)
8. Lean re-run: aimap 30 hosts x 17 observed ports, DefaultPorts match, 4s timeout -> 8 services
9. Primary-source verify: 3 Chatterbox unauth, 3 Kokoro unauth, 2 MinIO 403-locked
10. RVC candidates: /openapi.json -> Beijing OpenAI relay (FP, not RVC) -> killed RCE claim
11. aimap-profile x5 -> no honeypot, commercial, no ethics flags
12. VisorGraph passive x2 -> 0 nodes/edges (bare IPs); active run hung -> killed
13. menlohunt scan -ip 195.179.226.37 -> unauth Redis:6379 (IP-shadow)
14. Primary-source Redis: PING +PONG, INFO server (7.4.8, Linux 6.8, 23d uptime)
15. VisorBishop -ip-shadow-all -> corroborated Redis+MinIO; :8000 chromadb = FP (verified FastAPI 404)
16. recongraph 0 nodes; nu-recon simulated mode
17. VisorLog: 25 aimap events + 1 Redis -> nuclide.db (after fixing stray-cwd-DB bug)
18. VisorScuba: 5 hosts passing/0 violations -> false-compliant (no voice control)
19. BARE: 3 classes, all no-MSF-coverage (top 0.45-0.52)
20. VisorCorpus: built 136-case focused+protocol corpus
21. VisorAgent: vector catalog listed; internal-agent blocked (no API key); ethical-stop honored
22. JS-bundle: Kokoro /web = built-in static UI, no vendor bundle
23. Wrote insight-67, case study, findings-breakdown, query-file FP traps, this analysis
```

## 5. Findings

### 5.1 195.179.226.37 (Contabo DE): 4-service stacked exposure
Chatterbox TTS :4123 (unauth), Kokoro :8880 (unauth), Redis 7.4.8 :6379 (unauth),
MinIO :9000 (locked). HIGH. The headline host. Insight #12 confirmed.

### 5.2 Chatterbox TTS: 3 hosts unauthenticated, voice-clone fraud
65.19.175.20 (CUDA GPU), 195.179.226.37, 51.75.252.187 (loaded /voices/elon.wav).
HIGH. /upload_reference unauth voice-clone surface, not exercised.

### 5.3 Kokoro-FastAPI: 3 hosts unauthenticated, compute theft
195.179.226.37, 158.220.117.114, 170.64.228.236. MEDIUM. /debug/system leaks host metrics.

### 5.4 ByteDance "rvc-webui": false positive, not RVC
4 hosts. Beijing OpenAI relay servers (LLM proxy). RCE claim killed at verification.

### 5.5 MinIO x2: downgraded, auth-enforced
195.179.226.37, 5.189.184.239. 403 AccessDenied on anon LIST. Non-findings.

## 6. Risk Assessment

### Overall Posture
Auth-on-default thesis holds by contrapositive: the Chatterbox and Kokoro
projects ship no auth, and their populations are unauthenticated at the demo-UI
tier. The high-severity tier (RCE servers) is Shodan-dark, so the passive census
undercounts the true exposure.

### Confidentiality
Live audio (WhisperLive) and call-center/medical ASR (Deepgram) are the PII
classes, both Shodan-dark. The confirmed Chatterbox/Kokoro hosts expose model
config and host metrics. The stacked Redis exposes whatever the operator stored.

### Integrity
Voice-clone servers let an attacker synthesize speech in a target voice. The
loaded elon.wav reference shows this is in active use.

### Availability
Compute theft on the GPU/CPU TTS servers. Redis is a denial vector via FLUSHALL.

### Systemic Patterns
- Insight #67: voice-AI API servers Shodan-dark behind JSON roots.
- Insight #12: one auth-off service predicts more on the same IP (4-service stack).
- Insight #6: aimap's naked-keyword RVC alternate caught a live FP.
- Insight #18: storage tier (MinIO) did not inherit the exposure.

## 7. Recommendations

### R1: Authentication on TTS/ASR servers
Every voice server here ships auth-off. Operators must add a reverse proxy with
auth or bind to localhost.

### R2: Lock the data tier
Bind Redis to localhost or set requirepass. Default-config Docker Redis on a
public IP is an open door.

### R3: Patch Starlette
Upgrade to 1.0.1+ for CVE-2026-48710 (BadHost) on every FastAPI-wrapped server.

```
# Redis: refuse public bind
# /etc/redis/redis.conf
bind 127.0.0.1 ::1
requirepass <strong-random>
```

## 8. Limitations

The RCE population (GPT-SoVITS, RVC) is invisible to Shodan and was not
enumerated. A masscan-seeded pass on ports 9880/7865/7860 is required for a real
census. Attribution was thin: bare IPs with no cert SAN gave VisorGraph and
recongraph nothing to pivot. nu-recon ran in simulated mode without a live
Shodan key. VisorScuba has no control for voice-AI and scored the findings as
compliant.

## 9. PoC Illustrations

```
# Chatterbox unauth identity (marker only)
$ curl -s http://65.19.175.20:4123/config | jq .api_info.name
"Chatterbox TTS API"

# Redis unauth (metadata only, no keyspace)
$ printf 'PING\r\nINFO server\r\n' | nc 195.179.226.37 6379
+PONG
redis_version:7.4.8
os:Linux 6.8.0-107-generic x86_64

# RVC false positive unmasked by primary source
$ curl -s http://101.126.150.82:8000/openapi.json | jq .info.title
"北京open ai relay 服务器"   # Beijing OpenAI relay, NOT RVC
```
