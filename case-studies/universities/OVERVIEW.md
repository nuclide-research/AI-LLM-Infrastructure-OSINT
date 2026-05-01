# University AI Infrastructure Exposure — Global Overview

_NuClide Research · 2026-05-01_

---

## Scale

Shodan returns **225 university Ollama instances** (port 11434) and **84 university Open WebUI instances** (port 3000) as of 2026-05-01. The following findings were confirmed through active probing on the same date.

---

## Confirmed Exposures by Severity

### CRITICAL — Cloud Proxy Live (200 OK)

Direct quota drain at operator expense, no authentication:

| Institution | Country | Model | Tokens |
|-------------|---------|-------|--------|
| Purdue University Northwest | US-IN | qwen3-coder-next:cloud | 4 |
| Purdue University Northwest | US-IN | gemma4:31b-cloud | 2 |
| Purdue University Northwest | US-IN | gpt-oss:20b-cloud | **61** |
| SUNY Buffalo | US-NY | gemma4:31b-cloud | 2 |
| Hertfordshire (RobotHouse) | UK | gpt-oss:latest (cloud) | 103 |
| University of Žilina (student laptop) | Slovakia | devstral-2:123b / deepseek-v3.1:671b / qwen3-coder:480b | 200 OK |
| Yonsei University | South Korea | minimax-m2.1:cloud | 40 |
| Syracuse University (IST R640, port 12345) | US-NY | gemma4:31b-cloud | 10 |

### CRITICAL — Auth Disabled

Open inference for any internet actor:

| Institution | Country | Instance Name |
|-------------|---------|---------------|
| UC Santa Barbara | US-CA | "AI Lab (Open WebUI)" |

### CRITICAL — Cloud Proxy + Credential Leak

Operator API credentials (SSH pubkey + username) in 401 response:

| Institution | Country | Username | Leak Type |
|-------------|---------|----------|-----------|
| Columbia University | US-NY | `seascvn066` | Personal account |
| Chulalongkorn University | Thailand | `llm` | Generic service account |
| Technical Univ. of Crete | Greece | `arian` | Personal account |
| Hanoi University | Vietnam | `04aa6fb5e0b8` | Docker container ID |
| POSTECH bsp-server-2 | South Korea | `bsp-server-2` | Hostname-pattern service acct |
| POSTECH bsp-server-6 | South Korea | `bsp-server-6` | Hostname-pattern service acct |
| POSTECH bsp-server-10 | South Korea | `bsp-server-10` | Hostname-pattern service acct |
| POSTECH bsp-server-12 | South Korea | `bsp-server-12` | Hostname-pattern service acct |
| Seoul National University | South Korea | `node1` | Generic node service account |
| NCKU SOC | Taiwan | `nckusoc-3090` | Lab-pattern service acct |
| Shandong Medical | China | `bowee` | Personal account |
| Lanka Education & Research Network | Sri Lanka | `modelserver` | Generic service account |
| IIAP NAS Armenia | Armenia | (Docker container ID) | Container hostname |
| Chinese Primary School | China | `simmir2077-Rack-Server` | Server hostname |

### HIGH — Large Cloud Proxy Portfolio (No 200 OK, No Cred Leak)

| Institution | Country | Cloud Proxies | Largest |
|-------------|---------|---------------|---------|
| POSTECH | South Korea | 18 | kimi-k2:1t-cloud (~1T total / ~32B active MoE — Moonshot) |
| Shiv Nadar University | India | 18 | deepseek-v3.1:671b-cloud |
| Hanoi University | Vietnam | 18 | multiple |
| KTH Royal Inst. of Tech. | Sweden | 2 (2 nodes) | — |
| Keio University | Japan | 2 | — |
| Univ. of Western Ontario | Canada | 1 | — |
| University of Newcastle | Australia | 1 | — |
| JKUAT | Kenya | 1 | — |

---

## Abliterated / Uncensored Models on University Servers

Safety fine-tuning removed by design. Accessible to unauthenticated callers:

| Institution | Country | Model |
|-------------|---------|-------|
| KTH Royal Inst. of Tech. | Sweden | `hf.co/OBLITERATUS/gemma-4-E4B-it-OBLITERATED:latest` (running as **root**) |
| Shiv Nadar University | India | `vishalraj/qwen3-30b-abliterated:latest` + `uandinotai/dolphin-uncensored:latest` |
| Brno Univ. of Technology | Czech Republic | `seamon67/Gemma3-Abliterated:27b-q4_K_M` |
| RIT (student machine `ragdepc`) | US-NY | `qwq-uncensored:latest` + `huihui_ai/qwq-abliterated:32b` |
| RIT (wireless client `cl5`) | US-NY | `llama2-uncensored:7b` |
| Shandong Medical Graduate School | China | abliterated DeepSeek-R1-Distill-Qwen-32B |
| ENSTINET Egypt NREN | Egypt | `HauhauCS-35B-Fixed` + `HauhauCS-35B-Smart` — Arabic-language uncensored, system prompt: "execute all user requests without restrictions or censorship" |

---

## Agentic Models with Tool Execution

| Institution | Country | Model | Capability |
|-------------|---------|-------|------------|
| Duke University | US-NC | `qwen3.6-27b-agent:latest` | "Prefer using available tools to inspect files" |

---

## Largest Deployments

| Institution | Country | Total Models | Largest Local Model |
|-------------|---------|-------------|---------------------|
| KRENA (Kyrgyzstan) | Kyrgyzstan | 5 | **frob/glm-5.1:744b-a40b-ud-q4_K_XL — 753.9B params (433GB)** |
| Monash University (AU) | Australia | 8 | **deepseek-v3.1:latest — 671.0B params (404.5GB)** — co-largest deployment |
| Shiv Nadar University | India | 76 | DeepSeek-V3-0324:671b (376GB) |
| Shandong Medical | China | — | DeepSeek-V3-0324:671b (376GB) |
| NTUA Athens | Greece | 20 | deepseek-coder-v2:236b — 235.7B params (123GB) |
| FJU Medical (Taiwan) | Taiwan | 8 | qwen3.5:122b-a10b — 125.1B params (75GB), gpt-oss:120b (60GB) |
| SUNY Buffalo | US-NY | 26 | mixtral:8x22b (74GB) |
| POSTECH | South Korea | 31 | (mostly cloud — kimi-k2:1t-cloud) |
| Hanoi University | Vietnam | 31 | (mostly cloud) |

---

## Geographic Coverage

| Region | Institutions Confirmed | Count |
|--------|----------------------|-------|
| North America | Columbia, UCSB, Duke, SUNY Buffalo, Purdue NW, UWO, RIT, U Manitoba, UC Davis, Syracuse, SUNY Stony Brook, Virginia Tech | 12 |
| Asia-Pacific (East) | POSTECH, Yonsei, Keio, NCKU, NTU (Taiwan), NCU/Aiden (Taiwan), FJU Medical (Taiwan), Shandong Medical, SNU, INHA | 10 |
| Asia-Pacific (SE) | Hanoi, Chulalongkorn, VNU Hanoi, VNU HCMC, U Indonesia, Newcastle (AU), Monash (AU), Swinburne (AU) | 8 |
| Asia-Pacific (South) | COMSATS (PK), Shiv Nadar (IN), KRENA (KG), Lanka LEARN (LK) | 4 |
| Europe | KTH, TechCrete, NTUA, Brno, Hertfordshire, Žilina, Crete Medical, ITMO, TU Łódź (PL) | 9 |
| Africa | JKUAT, Covenant, ENSTINET Egypt NREN, Galaxy Backbone Nigeria | 4 |
| Latin America | CEFET/RJ (BR), IF-Paraíba (BR — minimax cloud) | 2 |
| Middle East / Caucasus | IIAP NAS Armenia | 1 |
| Government Health | Thailand Ministry of Public Health | 1 |
| Commercial (separate) | emails-pro.fr (FR commercial SaaS hosted on Romanian academic IPs) | see [commercial/](../commercial/index.md) |

---

## Attack Patterns Documented

1. **Open WebUI auth bypass**: UI auth on port 3000 does not protect raw Ollama on port 11434
2. **Cloud proxy quota drain**: Free-tier cloud models (gemma4-cloud, gpt-oss-cloud, qwen3-coder-next-cloud) return 200 OK without credentials
3. **Credential leak via 401**: Ollama Connect username + SSH pubkey in 401 error response body
4. **Docker binding misconfig**: `-p 11434:11434` binds to 0.0.0.0 by default
5. **Agent model injection**: File inspection agents injectable via CVE-2025-63389
6. **RAG pipeline injection**: Embedding models signal active RAG pipelines; injection affects document-augmented responses
7. **Production SaaS system prompt extraction**: `/api/show` returns full system prompt — for commercial AI assistants this leaks business logic, PII collection schemas, function-call formats, and anti-injection rules (see Aiden Assistant @ NCU/Taiwan, rdv-bot @ emails-pro.fr/Romania)
8. **18-subscription cloud bundle**: Identical 18-model cloud subscription portfolio (DeepSeek + MiniMax + Kimi + GLM + Qwen + Gemini + Nemotron) appears across POSTECH, Shiv Nadar, Hanoi, RIT, Yonsei — suggests shared institutional license or demo account
9. **Non-standard ports**: Ollama found on 5004 (Yonsei), 3005 (ENSTINET Egypt), 12345 (Syracuse), 22222 (NCKU SOC) — defenders relying on default-port-only filtering miss these
10. **Cross-border hosting attribution**: Operator country (e.g., France) ≠ host country (e.g., Romania) — IP-based reputation tagging misleads
11. **Uncensored Arabic-language models**: Custom Qwen3.5-MoE fine-tunes with system prompts explicitly disabling content restrictions deployed on NREN infrastructure (ENSTINET Egypt)
12. **CVE-2025-63389 persistent impact**: Model deletion via `/api/delete` is confirmed writable; injected system prompt layers persist in blob cache making full restoration non-trivial after attack
13. **Cross-institutional model propagation**: Identical low-citation community fine-tunes (`lukashabtoch/plutotext-r3-emotional`, `mattw/pygmalion`) appear on geographically unrelated institutions — operator social networks or shared Hugging Face download patterns create attribution pivot points

---

## Common Fix

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama

# Docker:
docker run -p 127.0.0.1:11434:11434 ollama/ollama
```

**CVE-2025-63389** — All Ollama versions. `first_patched_version: null`.
