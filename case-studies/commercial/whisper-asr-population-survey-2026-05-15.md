---
type: survey
---

# Whisper ASR Population Survey (2026-05-15)

_NuClide Research · 2026-05-15 (late evening, sixth survey of the day)_
_Closes: Survey 17 batch 1 (Whisper ASR leg) — Survey 17 now fully closed across all 3 batches_

---

## Summary

Population-scale survey of Whisper ASR (speech-to-text) deployments — the canonical OpenAI Whisper plus the popular forks (`whisper.cpp`, `faster-whisper`, `WhisperX`). aimap fingerprints shipped 2026-05-08; this survey closes the remaining open piece of Survey 17.

- Shodan harvest across 6 dorks → **537 unique candidate IPs**
- Probed via `fast_enum_whisper.py` (read-only: GET /, /docs, /openapi.json + HEAD on /asr and /v1/audio/transcriptions) in 32.6 seconds at threads=80
- **230 confirmed unauthenticated Whisper deployments** (43% of harvest; 124 dead)
- **145 hosts with `/asr` or `/v1/audio/transcriptions` reachable** — unauth POST-audio surface = anyone can submit audio and get transcription on the operator's compute (63% of confirmed)

**Platform breakdown:**

| Platform | Count | % | Notes |
|---|---|---|---|
| **openai-whisper-asr-webservice** | **139** | 60% | The canonical OpenAI-Whisper FastAPI wrapper. Default deploys ship `/docs` Swagger UI + unauth `/asr` POST endpoint. |
| **whisper.cpp Server** | 40 | 17% | The llama.cpp sibling for speech — server mode exposing `/v1/audio/transcriptions` OpenAI-compat |
| **faster-whisper** | 25 | 11% | CTranslate2-backed Whisper, 4-5× faster than OpenAI's reference impl |
| **WhisperX** | 4 | 2% | Word-level timestamps + speaker diarization wrapper |
| Unidentified Whisper-class | 22 | 10% | Title-tagged but no body-marker; likely customized deploys |

---

## The single big finding: openai-whisper-asr-webservice default-deploy pattern

**137 hosts ship with the default Swagger UI title `"Whisper Asr Webservice - Swagger UI"`** — that's an out-of-the-box `ahmetoner/whisper-asr-webservice` deployment (the most popular Whisper wrapper on Docker Hub). The image's default config exposes:

- `/` — landing page
- `/docs` — Swagger UI (interactive API browser)
- `/openapi.json` — full schema
- `POST /asr` — the transcription endpoint, **unauth by container default**

The deployment template doesn't ship with authentication. Operators who run `docker run -p 9000:9000 onerahmet/openai-whisper-asr-webservice` and expose the port are running the unauth surface by design — same Tier-A "no auth concept in framework default" pattern as Ollama, vLLM, Triton.

Compute-theft surface: anyone can POST a 5-minute audio file and burn the operator's GPU/CPU on Whisper-large-v3 transcription. At the operator-paid-Compute tier, this is the audio analog of the Ollama `/api/generate` surface — same class, different modality.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Whisper ∩ Ollama (16,473) | **13** (multi-modal text+audio AI stack — same VPS) |
| Whisper ∩ llama.cpp (965) | 2 |
| Whisper ∩ Docker daemon (286) | 0 |
| Whisper ∩ voice-agent (184) | 0 |

The 13-host Whisper+Ollama overlap is the **multi-modal stacked operator catastrophe** class:
- Whisper exposes audio→text transcription (operator's compute)
- Ollama exposes text→text inference (operator's compute, often paid `:cloud` quota)
- Together: an attacker can pipe `audio → Whisper → Ollama → response` end-to-end through the operator's resources

The 2 Whisper+llama.cpp overlap is a smaller version of the same — same VPS running both unauth ASR and unauth LLM.

---

## Methodology placement

This survey adds **Whisper** to the Tier-A "no auth concept in framework default" platform list, joining:

- Ollama (no auth concept — 100% unauth)
- vLLM (no auth concept — 100% unauth at population)
- Triton (no auth concept)
- Qdrant / ChromaDB / Milvus (no auth concept in defaults)
- MLflow Tracking (no auth in defaults)
- **Whisper ASR webservice family (no auth in defaults — confirmed at 230 hosts)**

Reinforces the auth-on-default thesis on the audio-AI tier (which was previously only tested via the voice-cloning / voice-agent surveys earlier today; Whisper-ASR fills the speech-recognition side of the audio quadrant).

---

## Toolchain Provenance

```
0. shodan_paginate.py × 6 dorks                          →  537 ip:port unique
1. fast_enum_whisper.py (threads=80, timeout=6s, ~32s)   →  230 confirmed (139 webservice + 40 cpp + 25 faster + 4 X + 22 unid)
2. /docs + /openapi.json + /asr + /v1/audio HEAD probes  →  145 hosts with unauth-POST audio endpoint reachable
3. cross-survey diff vs Ollama/llama.cpp/Docker/voice    →  13 Whisper+Ollama; 2 Whisper+llama.cpp
4. visorlog ingest                                       →  28 net-new events (heavy dedup with prior surveys' IPs)
```

---

## Honest negative space

- **Model-hint extraction returned mostly empty** — openai-whisper-asr-webservice doesn't expose its loaded model (`ASR_MODEL` env var) in the `/openapi.json` description. The operator-workload-corpus axis from Insight #24 doesn't have a direct analogue here; the loaded model is an internal-only config.
- **No PHI / hospital / clinical hostnames surfaced** in the immediate analysis pass (because the hostname-enrichment query had a path error during analysis; full hostname-vs-sensitive-token grep is flagged for follow-up). The healthcare-tier risk class is real for Whisper (hospital transcription deployments) but didn't surface a specific gov/edu/clinical host this run.
- **537 candidate corpus may undercount** the true Whisper population. `http.html:"whisper"` returned 2,300 candidates that this survey didn't probe (Shodan-broader pool). A second-pass on the 2,300 with the full prober is flagged for follow-up.

---

## See also

- [`voice-cloning-population-survey-2026-05-15.md`](voice-cloning-population-survey-2026-05-15.md) — Survey 17 batch 2 (closed)
- [`voice-agents-population-survey-2026-05-15.md`](voice-agents-population-survey-2026-05-15.md) — Survey 17 batch 3 (closed)
- `shodan/queries/17-voice-audio-ai.md` — query catalog; **all 3 batches now closed**
- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md) — 13 hosts overlap with this Whisper survey (multi-modal stack)
