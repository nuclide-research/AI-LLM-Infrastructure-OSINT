# Voice/Audio AI re-run: Category 17, 2026-05-29

_Survey type: manual-to-productize-to-re-run. Category 17 was first surveyed
2026-05-08. Since then aimap shipped 10 voice fingerprints (Kokoro, Chatterbox
x2, Orpheus, WhisperLive, Deepgram, RVC, Coqui XTTS, Piper, Whisper ASR) from
the 2026-05-27/28 platoon intel. This re-run drives the new fingerprints against
a fresh harvest and chases the RCE and voice-clone surfaces the platoon flagged._

## Summary

Fifteen dorks. Twenty-eight candidates. Six confirmed unauthenticated voice
services across five hosts. One four-service stacked host. Four false positives
killed at the verification stage, including a would-be remote-code-execution
finding that turned out to be an LLM relay server.

The headline is structural, not per-host: **the high-severity voice-AI servers
are Shodan-dark.** The remote-code-execution surfaces (GPT-SoVITS, RVC) and the
live-audio-PII surface (WhisperLive) return zero on their own brand and port
dorks. They serve JSON at the root, and Shodan indexes HTML. Only the demo UIs
show up, in small numbers. That finding is now Insight #67.

## Stage 0: Discover

Shodan harvest ran through the web UI under Playwright. Both API keys are dead,
so every query was a browser search, the result read off the page.

The brand dorks for the high-severity platforms came back empty:

- `http.html:"GPT-SoVITS" port:9880` returned 0. The GPT-SoVITS API server (five
  critical CVEs, CVE-2025-49837 through 49841) answers JSON at `/`. Shodan never
  indexes it.
- `port:8899 http.html:"Orpheus"` and `http.title:"Orpheus TTS"` both 0. Orpheus
  is fully dark across the variant space.
- `http.html:"system_health" http.html:"active_batch_requests"` (Deepgram
  on-prem) returned 0. The `/v1/status` JSON is not crawled.
- `port:9090 "WhisperLive"` returned 0. The WebSocket handshake is not indexed,
  and port 9090 is Prometheus territory anyway.

The dorks that did return hits selected for the demo UI, not the API:

- `port:8880 http.html:"Kokoro"` returned 2 (Hetzner and Chinanet demo pages).
- `http.title:"Chatterbox TTS"` returned 18, all real Chatterbox web UIs.
- `http.html:"/v1/audio/speech" -openai` returned 12, the highest yield, because
  it matches servers that echo the OpenAI-compatible path in an HTML doc.

One dork was a false-positive swamp. `http.html:"chatterbox"` returned 96, mostly
a custom photo-wall-art site, the entermediadb digital-asset-management product,
and LexisNexis. The single keyword collides. The product title does not. This is
the Garak and Whisper collision lesson again, and the reason the title-anchored
dork is the right one.

## Stage 1-2: Fingerprint and Verify

aimap v1.9.39 scanned the 28 candidates. The first pass used
`-scan-all-fingerprints` across 25 ports with a six-second timeout. It hit the
fifteen-minute cap before finishing. The dead-port timeouts dominated wall time,
exactly as Insight #44 predicts. The lean re-run dropped to the seventeen
observed ports, matched on DefaultPorts, and finished in four and a half minutes.

Eight services confirmed:

| Host | Service | Port | Note |
|------|---------|------|------|
| 65.19.175.20 | Chatterbox TTS API | 4123 | Hurricane Electric US; CUDA GPU; v2.1.0 |
| 195.179.226.37 | Chatterbox TTS API | 4123 | Contabo DE; v1.3.0; stacked host |
| 51.75.252.187 | Chatterbox TTS API | 4123 | OVH FR; v2.1.0; voice ref `/voices/elon.wav` |
| 195.179.226.37 | Kokoro-FastAPI | 8880 | Contabo DE; stacked host |
| 158.220.117.114 | Kokoro-FastAPI | 8880 | Contabo DE "Universal TTS" |
| 170.64.228.236 | Kokoro-FastAPI | 8880 | DigitalOcean AU |
| 195.179.226.37 | MinIO | 9000 | Contabo DE; auth-enforced |
| 5.189.184.239 | MinIO | 9000 | Contabo DE; auth-enforced |

Then primary-source verification, the load-bearing stage. Marker probes only,
through Mullvad, metadata not payloads.

**The three Chatterbox hosts confirmed unauthenticated.** `GET /health` returns
the model state, `GET /config` returns the full server config, no token. One of
them, 51.75.252.187, has already loaded a voice-clone reference at
`/voices/elon.wav`. The unauthenticated `/upload_reference` endpoint is the
voice-clone fraud surface. It was not exercised.

**The three Kokoro hosts confirmed unauthenticated.** `/debug/system` returns
host CPU and memory on two of them; the third answered `/v1/audio/voices` with
twenty-seven voice IDs. Compute theft.

**Both MinIO instances were downgraded to non-findings.** Anonymous LIST returned
`403 AccessDenied`. The buckets are locked. The storage tier did not inherit the
exposure, the same split as Insight #18. Both share a MinIO HostId, so they are
one operator or one template.

**Four candidates were killed as false positives.** The `rvc-webui` dork's four
hits, all on Beijing Volcano Engine, were not RVC. `GET :8000/openapi.json`
returned a title of `北京open ai relay 服务器`, a Beijing OpenAI relay server,
an LLM proxy. The `rvc-webui` string was incidental HTML. aimap's RVC
fingerprint carries naked single-word matches for `GPT-SoVITS` and `Applio`.
Those alternates would have confirmed these hosts as remote-code-execution
targets. The never-a-naked-keyword rule caught a live false positive. No RCE
was claimed.

## Stage 3-5: Attribute, the stacked host, Ledger

Attribution came back thin. VisorGraph and recongraph both returned zero nodes
and zero edges. These are bare IPs on Contabo, OVH, Hurricane Electric, and
DigitalOcean with no TLS certificate SAN to pivot from. Plain-HTTP TTS servers
leave no cert-to-domain-to-operator chain. nu-recon fell back to simulated data
without a live Shodan key.

The IP-direct shadow paid off, as it usually does. menlohunt's per-IP sweep on
195.179.226.37 found an **unauthenticated Redis 7.4.8 on port 6379** that the
aimap port list had missed. Primary source confirmed it: `PING` returned
`+PONG` with no AUTH, `INFO server` returned the version, OS (Linux 6.8), run
id, and a 23-day uptime. Only server metadata was read, never the keyspace.
VisorBishop's productized IP-shadow independently confirmed the same Redis and
MinIO. Two tools agreeing is the verification.

That makes 195.179.226.37 a four-service stacked exposure: Chatterbox on 4123,
Kokoro on 8880, and Redis 7.4.8 on 6379, all unauthenticated, with MinIO on
9000 locked. One operator shipped three services auth-off on one box, which is
Insight #12 stated plainly.

Six findings landed in `nuclide.db` via VisorLog, the five aimap services
through the aimap adapter and the Redis through `visorlog add`.

## Stage 6-7: Score, map, codify

BARE found no Metasploit coverage for any of the three finding classes. Top
scores were 0.45 to 0.52, all under the 0.55 sentinel. These are first-party
authorization bugs and a novel CVE class, not a commodity chain. Even the
documented GPT-SoVITS RCE has no Metasploit module yet.

VisorScuba scored all five hosts as passing with zero violations. That is a
false-compliant result. Its Rego baseline has no control that maps to an
unauthenticated TTS or voice-clone service, a gap noted across roughly eight
prior sessions. The finding is real; the policy cannot see it.

## Impact

- **Voice-clone fraud.** Three unauthenticated Chatterbox servers expose
  zero-shot voice cloning. The OVH host already holds a celebrity-voice
  reference. Anyone can upload a reference and synthesize speech in that voice
  with no credential.
- **Compute theft.** Three Kokoro servers and the Chatterbox GPU host let anyone
  spend the operator's CPU and GPU on arbitrary text-to-speech.
- **Stacked data-tier exposure.** 195.179.226.37 hands an unauthenticated
  attacker a Redis instance alongside the AI services. Redis unauth is a known
  path to data theft and, with `CONFIG`, to code execution. It was not exercised.

## Remediation

- Put every TTS and ASR server behind authentication or a reverse proxy with
  auth. None of these projects ship auth by default, so the operator must add it.
- Bind Redis to localhost or set `requirepass`. A default-config Docker Redis on
  a public IP is an open door.
- Patch Starlette to 1.0.1 or later to close CVE-2026-48710 (BadHost), which
  bypasses path-based auth middleware on every FastAPI-wrapped server here.
- Operators running GPT-SoVITS or RVC must treat every exposed instance as a
  remote-code-execution target and pull it off the public internet now.

## What the method could not see

The remote-code-execution population is invisible to this method. GPT-SoVITS,
RVC, Orpheus, Deepgram, and WhisperLive are Shodan-dark behind JSON roots. A
real census of the RCE surface needs a masscan-seeded pass on ports
9880/7865/7860 across tier-2 cloud, fingerprinted by API shape. This survey
saw only the demo-UI minority. That is Insight #67.

## Toolchain provenance

```
JAXEN        Playwright web UI (Shodan API keys dead); 15 dorks, 28 candidates
aimap        v1.9.39; lean re-run 30 hosts x 17 ports; 8 services confirmed
aimap-profile no honeypot, unclassified/commercial, no ethics flags (5 hosts)
VisorGraph   passive; 0 nodes/0 edges (bare IPs, no cert SAN); active run killed (hung on crt.sh)
VisorBishop  platform=none (no fp), IP-shadow corroborated Redis+MinIO on stacked host; :8000 chromadb = FP
VisorSD      N/A, no Shodan API key
VisorGoose   N/A, gov/edu scope
menlohunt    surfaced unauth Redis:6379 on 195.179.226.37 (IP-shadow win)
recongraph   0 nodes/edges (Shodan-dependent)
nu-recon     simulated mode (no live key)
VisorPlus    component tools run individually (orchestrator Shodan-blocked)
VisorLog     25 events via aimap adapter + 1 Redis -> nuclide.db
VisorScuba   5 hosts passing/0 violations, false-compliant (no voice-AI control)
BARE         no MSF coverage (top 0.45-0.52 < 0.55), first-party/novel class
VisorCorpus  136-case focused+protocol adversarial corpus (87 HIGH)
VisorAgent   controlled-target only (ethical-stop); internal-agent blocked on API key; never fired at survey hosts
VisorRAG     embedding key not configured (carry-forward)
VisorHollow  N/A, Windows-only
cortex       run at codify on session analysis
JS-bundle    null, Kokoro /web is built-in static UI, no vendor bundle/secrets
```
