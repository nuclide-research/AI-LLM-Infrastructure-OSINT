---
type: survey
---

# Voice-Cloning Population Survey: Shodan-Reachable Slice (2026-05-15)

_NuClide Research · 2026-05-15 (late evening, third survey of the day)_
_Closes: Survey 17 batch 2 (voice-cloning leg)_
_Companion to: [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md), [`llamacpp-population-survey-2026-05-15.md`](llamacpp-population-survey-2026-05-15.md)_

---

## Summary

Survey of the Shodan-reachable voice-cloning surface (RVC / GPT-SoVITS / Applio / OpenVoice / ChatTTS / F5-TTS) and adjacent voice-TTS platforms. The aimap fingerprints for these platforms were shipped 2026-05-08 (`shodan/queries/17-voice-audio-ai.md`); this is the population-survey leg that closes Survey 17 batch 2.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

**The survey's primary contribution is a methodological one.** The Shodan dorks for these platforms produced 49 candidate IPs, and **37 of those 49 (76%) are false positives** where the brand string matched unrelated content (Rockville Centre restaurant, R. Van Coevorden M.D., RVC Paint, RVC Volunteer Center, RVC Synology NAS named "RVC", etc.). Of the **12 real voice-related hosts** surfaced, only ~6 are true voice-cloning instances (commercial services); 5 are Coqui TTS demo servers; 1 is a defensive Deepfake Awareness Portal.

This re-confirms **Insight #15 (single-token Shodan-dork FP class)** at a near-90% FP rate when the brand string is a common acronym like "RVC". The actionable methodology lesson: **voice-cloning's Gradio-based platforms are Shodan-dark, the brand strings live in JS bundles Shodan doesn't index**, so a population-scale survey requires masscan-tier-2 on Gradio default ports (7860/7865/7897/8000), not Shodan-walk.

---

## What was actually found

### Real voice-cloning instances (6 hosts)

| Host | Title | Operator profile |
|---|---|---|
| `103.141.140.192:8081` | **Magicvoice Studio - Clone & Generate** | Vietnamese commercial voice-clone SaaS, React/Vite SPA |
| `204.168.212.143:8181` | **VoxAI - KimDeo AI** | Commercial voice-AI service |
| `8.141.9.1:80` | **变声极客 · RVC AI 硬件变声盒子** | Chinese **commercial hardware** voice-changer product page (RVC-algorithm based, real-time low-latency) |
| `154.201.65.75:8090` | **AI实时变声伴侣 - RVC算法增强优化的变声软件** | Chinese commercial real-time voice-changer software |
| `164.70.188.19:18045` | **RVC API** | Bare RVC API endpoint — direct framework exposure |
| `43.138.74.248:443` | **五月rvc后台管理** | Chinese "May RVC admin panel" — operator backend |

### Coqui TTS cluster (5 hosts)

| Host | Voice model | Language |
|---|---|---|
| `147.135.137.14:5006` | tacotron2-DDC | French |
| `178.170.43.107:8880` | vits | French |
| `47.116.69.40:9002` | (model query 404) | unknown |
| `5.180.174.202:5006` | vits | German |
| `5.39.216.147:5006` | vits | German |

These are Mozilla-TTS / Coqui-TTS demo servers (`<meta description="🐸Coqui AI TTS demo server.">`). Endpoints exposed: `/`, `/details`, `/voices`, `/api/tts` (POST text + speaker_id = synthesized speech). The two `vits-de` hosts likely belong to the same operator (identical loadout, different cloud regions). **Compute-theft surface, not voice-clone fraud. These models can't clone arbitrary voices, only the published model speakers.**

### Defensive / counter-target (1 host)

| Host | Title | Notes |
|---|---|---|
| `152.53.254.147:3001` | **Deepfake Awareness Portal** | Almost certainly defensive/educational, not offensive. Worth confirming before any disclosure-class action. |

### Shodan-FP class (37 hosts, 76% of harvest)

The dork `http.title:"RVC"` matched the literal substring "RVC" in `<title>` and surfaced:

- Restaurants in Rockville Centre, NY (`104.237.151.28` Red Rooster House)
- Doctor Reinier Van Coevorden's medical practice (`35.165.207.193`)
- Lithuanian companies (`135.181.209.23` UAB "RVC Lobis")
- Russian volunteer centers (`195.178.106.106` Волонтерский Центр)
- Spanish-language sales contact pages (`164.92.67.52`)
- Paint companies (`178.128.20.253/45` "RVC Paint - Login")
- Synology NAS hardware (`182.93.32.188:5000` RVC-NAS)
- Learning portals (`40.85.91.121` / `52.169.24.150` "RVC LEARN")
- Project management tools, government registries, IT-automation portals

None of these are voice-cloning.

---

## Methodology: Shodan-walk vs the Gradio JS-bundle problem

Voice-cloning's primary platforms (RVC / GPT-SoVITS / Applio / OpenVoice / ChatTTS / F5-TTS) are all Gradio-based webapps. Gradio's default landing page is a thin HTML shell + JS bundle; the platform-identifying strings (`Retrieval-based-Voice-Conversion`, `IAHispano/Applio`, etc.) live inside the JS bundle, not in the HTML body Shodan crawls. Shodan's response-text index therefore sees only the generic Gradio shell on these hosts.

This reproduces the pattern documented in:
- [`rag-frameworks-population-survey-2026-05-15.md`](rag-frameworks-population-survey-2026-05-15.md): LlamaIndex and Haystack confirmed Shodan-dark; brand-dork yielded ≤2 hits each
- [`autogen-studio-survey-2026-05-14.md`](autogen-studio-survey-2026-05-14.md): drove [Insight #21 port-first-discovery-for-low-footprint-platforms](../../methodology/insight-21-port-first-discovery-for-low-footprint-platforms.md)

**The required follow-up methodology**: masscan tier-1 + tier-2 cloud (3.55M IPs) on Gradio default port 7860 (and RVC-specific 7865, Applio 7897, ChatTTS 9966, F5-TTS 7860, GPT-SoVITS 9880), then probe `/config` + `/info` + body for the platform-marker conjunct. The aimap fingerprints exist; the harvest channel is the bottleneck.

---

## Why this re-confirms Insight #15 sharply

| Survey | Dork | Total hits | Real positives | FP rate |
|---|---|---|---|---|
| LiteLLM (the original Insight #15 case) | `http.title:"LiteLLM API"` | 5,391 | 2,710 | **50%** |
| RVC voice-cloning (this survey) | `http.title:"RVC"` | 34 | ~6 | **~82%** |

The RVC case is harder than the LiteLLM case because "RVC" is a much more common acronym (4 distinct namespaces, restaurant locations, person initials, learning portals, voice-cloning) than "LiteLLM API." This survey provides the **upper-bound case** for the FP class: at acronym-tier specificity, single-token title dorks can be ~80-90% noise.

The methodology consequence: **single-token title dorks for common-acronym platforms are not just lossy. They're dominated by FPs.** Either anchor with a second conjunct (`http.title:"RVC" AND html:"retrieval-based"`) or skip the title dork entirely in favor of port-first masscan.

---

## Cross-survey colocation check

Diffed the 12 real voice-cloning IPs against the Ollama (16,473) and llama.cpp (965) confirmed sets. **Zero overlap.** Voice-cloning operators do not appear to colocate with text-LLM operators at population scale: separate operator demographics (commercial voice-SaaS, Chinese consumer-software vendors, TTS demo-server hosts) vs the text-LLM operator population (cloud-VPS / academic / SMB).

This is itself a finding: the cross-platform colocation class documented in [`alpha-miner-194-233-71-223-2026-05-15.md`](alpha-miner-194-233-71-223-2026-05-15.md) and at scale in the llama.cpp survey (29 cross-platform-host instances) does **not** extend to voice-cloning. Different operator demographics, different VPS patterns.

---

## Honest negative space

- **No operator-uploaded named voices surfaced via the public endpoints.** Coqui TTS hosts expose only base public-model speakers via `/voices`. Commercial voice-clone SaaS (Magicvoice, VoxAI, the Chinese RVC products) keep their voice models behind admin-auth not visible via the unauth landing page. The chat_template/SYSTEM-prompt-analogue discovery axis from Insights #24 + #25 does not have a clean equivalent for voice-cloning at this survey's reach.
- **Population is severely undercounted.** True voice-cloning population probably ~100-200× what this survey saw. Masscan-tier-2 follow-up needed.
- **`/api/tts` is the inference endpoint on Coqui TTS hosts.** Read-only restraint means we don't fire a synthesis request; we only enumerate `/voices` and `/details`. The unauth surface IS exploitable for compute-theft / synthesized-speech-on-operator-quota, but proving it crosses the restraint line.

---

## Tool-update Tracker

Adds the following to the methodology roadmap (already shipped in aimap v1.9.4-shipped fingerprints, just under-used by the Shodan-walk methodology):

- **aimap v1.9.5 candidate:** integrate Gradio `/config` and `/info` probing as a default for the voice-cloning fingerprints, since these endpoints expose platform identity that the initial HTML doesn't.

---

## Toolchain Provenance

```
0. shodan_paginate.py × 7 dorks                   →  49 ip:port unique
1. fast_enum_voicecloning.py (conjunctive markers) →  0 confirmed (Shodan-dark)
2. broad probe (title + voice-term regex)          →  12 real voice-related hosts, 37 FPs
3. /voices + /details enumeration on 5 Coqui      →  base TTS models only (tacotron2-DDC-fr, vits-fr, vits-de×2)
4. fast_enum_to_ndjson + visorlog ingest          →  11 events into nuclide.db (1 deduped)
5. cross-survey diff vs Ollama + llama.cpp        →  zero overlap (different operator demographics)
```

---

## See also

- [`ollama-population-survey-2026-05-15.md`](ollama-population-survey-2026-05-15.md): the day's largest survey (16,473 confirmed unauth Ollama)
- [`llamacpp-population-survey-2026-05-15.md`](llamacpp-population-survey-2026-05-15.md): the day's middle survey (965 confirmed llama.cpp)
- [`insight-15-dork-hits-vs-platform-instances`](../../methodology/insight-15-dork-hits-vs-platform-instances.md): the methodology Insight this survey re-confirms sharply
- [`insight-21-port-first-discovery-for-low-footprint-platforms`](../../methodology/insight-21-port-first-discovery-for-low-footprint-platforms.md): the port-first methodology the voice-cloning population needs
- `shodan/queries/17-voice-audio-ai.md`: the query catalog that drove the harvest (aimap fingerprints shipped 2026-05-08)
