---
title: "Insight #67: Voice/audio AI API servers are Shodan-dark behind JSON-only roots; only the demo UI indexes"
date: 2026-05-29
survey: voice-audio-rerun-2026-05-29
thesis_touch: auth-on-default (confirms by contrapositive for the indexable subset)
extends: ["insight-21-port-first-discovery-for-low-footprint-platforms", "insight-15-dork-hits-vs-platform-instances"]
---

# Insight #67: Voice/audio AI API servers are Shodan-dark behind JSON-only roots

## The lesson

For the entire voice/audio AI category, the **highest-severity surfaces are the
ones Shodan cannot see.** The OpenAI-compatible TTS/ASR API servers
(GPT-SoVITS, Orpheus, Kokoro's API path, Deepgram on-prem, WhisperLive) return
a **JSON-only root or a non-root JSON status endpoint** that the Shodan crawler
does not index as HTML. Their brand and port dorks return 0 even when live
instances exist. Only the **demo / Swagger / built-in web UI** pages get
indexed, in tiny counts.

This is Insight #21 (port-first beats brand-dork) generalized from one platform
(AutoGen Studio's unrendered Gatsby `<meta>`) to a **whole category**, and it is
the dominant structural fact of voice-AI discovery.

## The evidence (2026-05-29 re-run, 15 dorks)

| Dork | Total | What it means |
|------|------:|---------------|
| `http.html:"GPT-SoVITS" port:9880` | **0** | The RCE-vulnerable API (5x critical CVE) is JSON-only at `/`; Shodan-dark |
| `port:8899 http.html:"Orpheus"` | **0** | Orpheus API JSON-only |
| `http.title:"Orpheus TTS"` | **0** | variant space exhausted, Orpheus fully dark |
| `port:8880 http.html:"/dev/captioned_speech"` | **0** | Kokoro's unique path not in indexed HTML |
| `http.html:"system_health" http.html:"active_batch_requests"` | **0** | Deepgram `/v1/status` JSON not crawled |
| `port:9090 "WhisperLive"` | **0** | WebSocket JSONL handshake not indexed; port 9090 = Prometheus-dominated |
| `port:8880 http.html:"Kokoro"` | 2 | only the Swagger/demo HTML pages index |
| `http.title:"Chatterbox TTS"` | 18 | only the built-in web UI title indexes |
| `http.html:"/v1/audio/speech" -openai` | 12 | highest-yield: catches servers that echo the path in an HTML doc |

The severity inversion is the point: the **0-result dorks are the RCE and
live-audio-PII surfaces**; the small-count dorks are the lower-severity
demo-UI-exposing deployments.

## Corollaries proven the same session

1. **Title-anchored beats html-keyword** (extends Insight #15). `http.html:"chatterbox"`
   = 96 hits, a false-positive swamp (custom photo-wall-art `chatterboxwalls.com`,
   the `entermediadb` DAM product, LexisNexis). `http.title:"Chatterbox TTS"` = 18,
   all real. The single keyword collides; the product-title string does not.

2. **The RCE brand-dork is a false-positive generator.** `http.html:"rvc-webui"`
   returned 4 hits, all on one ByteDance (Beijing Volcano Engine) ASN. Primary
   source killed all four: `:8000/openapi.json` title = `北京open ai relay 服务器`
   (Beijing OpenAI **relay server**), an LLM proxy, not RVC voice cloning. The
   `rvc-webui` string was incidental HTML. **aimap's RVC fingerprint has naked
   single-word `body_contains` alternates (`GPT-SoVITS`, `Applio`) that would
   have confirmed these as RCE targets**, the methodology's own
   never-a-naked-single-word rule (Insight #6) caught a live FP.

## What this means for method

- **The vulnerable voice-AI population is masscan-territory, not Shodan-territory.**
  To survey GPT-SoVITS/RVC RCE at population scale, masscan ports 9880/7865/7860
  across tier-2 cloud and fingerprint by JSON API shape. Shodan only ever shows
  the demo-UI minority.
- **Quote the 0 as a finding.** "GPT-SoVITS RCE surface is Shodan-dark" is a
  publishable negative; it tells the next surveyor the discovery mode is wrong,
  not that the platform is absent.
- **Verify every voice brand-dork hit against the API shape**, never the HTML
  keyword. The `-openai`-negated `/v1/audio/speech` dork is the one cross-platform
  query that selects on the actual API contract.

## Source
`case-studies/commercial/voice-audio-ai-rerun-2026-05-29.md`,
`recon/voice-audio-rerun-2026-05-29/`.
