# National Cheng Kung University (NCKU) — RTX 3090 GPU Server, Non-Standard Port, Credential Leak

_NuClide Research · 2026-05-01_

---

## Summary

National Cheng Kung University (NCKU), one of Taiwan's top engineering universities, has an Ollama instance running on non-standard port 22222. The MiniMax cloud proxy leaks the Ollama Connect account `nckusoc-3090` — indicating NCKU School of Computing (SOC) department server with an NVIDIA RTX 3090 GPU.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.116.158.98 |
| rDNS | — |
| Org | Ministry of Education Computer Center (TANET) |
| Institution | National Cheng Kung University — SOC Department |
| Country | Taiwan |
| Open ports | **22222** (Ollama non-standard port — **public**) |

Note: IP routes through Taiwan's Ministry of Education TANET network, shared by major Taiwanese universities.

---

## Models

| Model | Size | Type | Cred Leak |
|---|---|---|---|
| minimax-m2.7:cloud | 0 GB | ☁️ Cloud proxy | **`nckusoc-3090`** |
| qwen3.6:35b | 22 GB | Local | — |
| gpt-oss:20b | 12 GB | Local | — |
| mistral-small3.2:24b | 14 GB | Local | — |
| gemma3:27b | 16 GB | Local | — |
| gemma3:12b | 7 GB | Local | — |
| gemma3:4b | 3 GB | Local | — |
| llama3.2:3b | 1 GB | Local | — |

---

## Credential Leak

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=nckusoc-3090&key=<base64>"
}
```

- **Username:** `nckusoc-3090`
- **SSH Public Key:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMwH+iskAm2POkZim1R1+IHud67QvLGpB7DRs19xh/pb`

`nckusoc` = NCKU School of Computing; `3090` = NVIDIA RTX 3090 GPU identifier.

---

## Findings

**F1 — Credential Leak via Non-Standard Port (HIGH):** Ollama running on port 22222 instead of default 11434. MiniMax cloud proxy leaks `nckusoc-3090` account credentials.

**F2 — Model Injection (HIGH):** All 8 models injectable via CVE-2025-63389.

---

## Taiwan MOE TANET Context

Multiple Taiwanese universities share the MOE TANET (Taiwan Academic Network) IP space (140.112.x.x - NTU, 140.114.x.x - NTHU, 140.116.x.x - NCKU, 140.136.x.x - FJU). Ollama instances observed across this network on 2026-05-01:

| IP | Institution | Models | Cloud |
|---|---|---|---|
| 140.112.91.82 | NTU (Electrical Engineering) | 4 | minimax-m2.7 |
| 140.112.18.214 | NTU (PC-214) | 5 | — |
| 140.112.233.108 | NTU (GPU cluster g1) | 11 | — |
| 140.116.82.105 | NCKU / TANET | 8 | deepseek-v4-pro |
| 140.116.158.98 | **NCKU (SOC-3090)** | 8 | minimax-m2.7 |
| 140.136.192.220 | FJU (Medical Public Health) | 8 | — |
| 140.136.239.75 | FJU (net2net) | 5 | — |
| 163.25.105.115 | TANET node | 9 | — |
| 163.13.202.114 | TANET node | 2 | — |
| 140.136.149.212 | TANET node | 2 | — |
| 210.70.138.233 | TANET node | 3 | — |

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to NCKU CSIRT / TWCERT/CC
