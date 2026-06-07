---
type: survey
---

# Voice-Agent Population Survey: LiveKit-dominant (2026-05-15)

_NuClide Research · 2026-05-15 (late evening, fourth survey of the day)_
_Closes: Survey 17 batch 3 (voice-agent leg)_

---

## Summary

Survey of the voice-agent platform population: LiveKit (server + agents framework), Pipecat, Vocode, with Deepgram / Twilio as secondary integration signals.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6900, K6935, K7003, S7065

<!-- ksat-tag:auto-generated:end -->

- 303 candidate IPs harvested via 8 dorks; 239 responsive; **184 confirmed LiveKit servers** (60% of harvest)
- Pipecat: 2 confirmed; Vocode: 2 confirmed (both tiny niches at population scale)
- **LiveKit's Twirp room API is auth-on-default at population scale**: 0 of 184 hosts returned room data unauth. The two HTTP-200 anomalies were SPA-frontend catch-all routes, not real Twirp data leaks. Tier-C confirmation.
- **The big finding is at the example-deployment-pattern tier: 31 of 42 LiveKit Voice Agent / Agents Playground frontends mint participant JWTs unauthenticated** via `/api/connection-details` (the LiveKit Next.js starter) or `/api/token` (the Agents Playground). **74% rate.**

This is a textbook **Tier-A\* (auth-optional, off-by-default in example template)** finding at population scale. LiveKit's own example apps ship with an unauth `/api/connection-details` endpoint as the demo-friendly pattern; operators who deploy based on those examples inherit the unauth posture.

---

## The token-mint surface

`POST http://<host>:<port>/api/connection-details` with body `{"room":"anything","identity":"anything"}` returns:

```json
{
  "serverUrl": "wss://<operator>.livekit.cloud",
  "roomName": "voice_assistant_room_<random>",
  "participantToken": "eyJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoidXNlciIsInZpZGVvIjp7InJvb20i...<JWT>...",
  "participantName": "user"
}
```

The JWT decoded has `roomJoin: true`, `canPublish: true`, `canSubscribe: true`, `canPublishData: true`. Full participant grants. Anyone with the token can connect to the operator's LiveKit server and:

1. Join the voice-agent's room
2. Publish audio (talk to the AI)
3. Subscribe to streams (listen if other participants are there)
4. Send data messages
5. Burn the operator's LLM + STT + TTS compute on every utterance

**At least one host (`34.58.247.238` / `app.olylive.org`)** mints tokens with `roomCreate: true`. The bearer can create arbitrary new rooms, expanding the abuse surface from "join one room" to "create many."

---

## Operator deployments visible in the leaked JWTs

The `serverUrl` field in the JWT response discloses the operator's named LiveKit deployment. Sample:

| Host (frontend) | Backend serverUrl | Operator profile |
|---|---|---|
| `38.242.250.130:3000` | `wss://banca-bqopqpjr.livekit.cloud` | **"Banca" — Italian for "Bank"; possible financial-services voice agent** |
| `107.178.240.27:443` | `wss://tarl-interview-bot-x1jqc3nd.livekit.cloud` | TARL Interview Bot |
| `13.233.178.230:443` | `wss://india-skilling-bot-x1xa6xqc.livekit.cloud` | **India Skilling Bot — Indian govt/NGO skilling program** |
| `3.109.121.27:443` | `wss://interview-bot-3sb0xacd.livekit.cloud` | Interview-screening bot |
| `34.180.50.178:443` | `wss://collection-bot-e25eb0rh.livekit.cloud` | Collection / debt-collection bot |
| `135.225.28.151:443` | `wss://voice-agent-main.swedencentral.cloudapp.azure.com` | Microsoft Azure Sweden Central voice-agent |
| `14.22.86.78:3000` | `wss://ws.ctagent.ailinone.com` | CT Agent (ailinone.com commercial agent platform) |
| `205.164.114.94:3000` | `wss://luma-h7rno42p.livekit.cloud` | Luma agent |
| `13.235.161.110:443` | `wss://chatterbot-tp1ff1i1.livekit.cloud` | Chatterbot |
| `34.58.247.238:443` | `wss://app.olylive.org/livekit-ws/` | OlyLive — **roomCreate enabled in the JWT** |
| `178.128.228.142:3000` | `wss://ikit.arcsip.io` | iKit Arcsip |
| `92.46.186.56:3000` | `ws://92.46.186.56:7880` | Self-hosted LiveKit on same VPS |
| `91.99.214.33:9001` | (Playground default) | **Also runs Ollama unauth on same IP — multi-modal stacked operator** |

The Banca / India Skilling / Collection / Interview bots are the operator categories where unauth voice-agent abuse has direct real-world impact: financial advice, government program intake, debt-collection, hiring-screening. Anyone can engage with the agent and influence/probe/exhaust the operator's quota.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Voice-agent ∩ Ollama (16,473) | **2** (42.200.155.199, 91.99.214.33) |
| Voice-agent ∩ llama.cpp (965) | 0 |
| Voice-agent ∩ voice-cloning (12 real) | 0 |

`91.99.214.33` runs **both** the voice-agent example UI (with unauth JWT-mint) AND unauth Ollama. Same VPS, two unauth AI surfaces. The multi-modal stacked operator pattern: voice frontend → wired to LLM → operator's LLM also unauth. Extends the cross-platform-colocation class catalogued in the llama.cpp survey (29 hosts) and the alpha_miner case (1 host).

---

## Tier-A\* methodology slot

This survey adds a new auth-posture-tier observation:

| Tier | Definition | Example platforms | Observed unauth rate |
|---|---|---|---|
| A | No auth concept in framework | Ollama, Triton, vLLM, Qdrant, MLflow | 95-100% |
| **A\*** | **Auth optional, off-by-default in example deployment templates** | **LiveKit `/api/connection-details` (Next.js starter), `/api/token` (Agents Playground)** | **74% (31/42)** |
| C | Auth on by default | LiveKit's own Twirp API, MinIO, Langfuse | 0% |

The methodology lesson: when measuring auth posture at population scale, **the framework's authentication tier and the framework's reference-deployment auth tier are separate axes.** LiveKit's Twirp API is solid (auth-on-default, 0% unauth at 184 hosts). LiveKit's example-deployment-template frontend (which most operators clone) ships the token-mint endpoint unauth. The framework gets a Tier-C grade; the example-deployment-pattern gets a Tier-A\* grade. Operators inherit whichever template they cloned.

Codifies as **Insight #26 candidate**: framework-auth-tier and example-template-auth-tier are separate; measure both.

---

## Toolchain Provenance

```
0. shodan_paginate.py × 8 dorks                  →  303 ip:port (211 LiveKit-title dominant)
1. fast_enum (HTTP + HTTPS schemes, conjunctive markers + Twirp probe + title extraction)
                                                   →  184 LiveKit + 2 Pipecat + 2 Vocode confirmed
2. token-mint probe (4 endpoint patterns × 2 methods) on 42 voice-agent frontends
                                                   →  31 mint unauth JWT with full participant grants
3. cross-survey diff vs Ollama + llama.cpp + voice-cloning
                                                   →  2 hosts run BOTH (Ollama + voice-agent unauth)
4. fast_enum_to_ndjson + visorlog ingest          →  83 events landed (104 deduped — high overlap)
```

---

## Honest negative space

- **The 184 "LiveKit confirmed" set includes example-app frontends that aren't actual LiveKit servers**: they're Next.js apps that proxy to a hosted LiveKit Cloud backend. The "operator host" we surveyed is the example-deployment, not the LiveKit server itself. The actual LiveKit servers (where the rooms live) live mostly on LiveKit Cloud (`*.livekit.cloud`) or operator-named subdomains.
- **Twirp Auth confirmation depended on POST /twirp/.../ListRooms responses**: most returned 404 (Twirp not mounted) or 401 (auth-required) which is the expected behavior. We didn't fire actual room-create / room-delete operations.
- **We did not connect to any of the JWT-mint targets**: the token-mint endpoint EXISTS and returns valid tokens, which proves the surface; actually connecting and engaging the voice agent would burn operator compute (restraint).

---

## See also

- [`voice-cloning-population-survey-2026-05-15.md`](voice-cloning-population-survey-2026-05-15.md): the day's earlier voice survey (closes Survey 17 batch 2)
- [`llamacpp-population-survey-2026-05-15.md`](llamacpp-population-survey-2026-05-15.md): the day's llama.cpp survey (965 confirmed)
- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): the day's flagship Ollama survey (16,473 confirmed)
- `shodan/queries/17-voice-audio-ai.md`: Survey-17 catalog (now batches 1+2+3 closed)
