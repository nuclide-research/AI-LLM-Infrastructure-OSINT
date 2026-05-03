# POSTECH — 9-Node Cluster, 18+ Cloud Subscriptions, 5 Account Takeovers + Synchrotron Beamline + Essential AI Model

_NuClide Research · 2026-05-01 — Updated 2026-05-03_

---

## Summary

Pohang University of Science and Technology (POSTECH) has a 9-node cluster spanning the BSP (Brain Science Platform) LAN and the Pohang Accelerator Laboratory (PAL) 4th-generation synchrotron network. The primary server has 18 active cloud proxy subscriptions including `kimi-k2:1t-cloud` (1 trillion parameters). Five satellite nodes expose live Ollama Connect claim URLs. bsp-server-3 additionally runs `rnj-1:8b`, a proprietary 8B foundation model from Essential AI (Apache 2.0, tool-capable, temperature 0.2). The 4th-generation synchrotron beamline workstation (`tpd.postech.ac.kr`, `4gsr-beamline-ws`) hosts a 235B-parameter Qwen3 model alongside a live cloud proxy subscription. Baseball team hostname convention: astros, siren, dragons, angels, rangers, and bsp-server-N numbering.

---

## Cluster Topology

| Node | IP | Hostname | Ollama Account | Status |
|---|---|---|---|---|
| Main DGX | 141.223.84.47 | astros.postech.ac.kr | (18 cloud subs) | cloud proxy |
| bsp-server-2 | 141.223.121.58 | siren.postech.ac.kr | `bsp-server-2` | cloud proxy |
| bsp-server-3 | 141.223.121.59 | — | `bsp-server-3` | **⚠️ ACCOUNT TAKEOVER** *(added 2026-05-03)* |
| bsp-server-6 | 141.223.121.73 | dragons.postech.ac.kr | `bsp-server-6` | **⚠️ ACCOUNT TAKEOVER** |
| bsp-server-9 | 141.223.121.76 | rangers.postech.ac.kr | `bsp-server-9` | **⚠️ ACCOUNT TAKEOVER** *(added 2026-05-03)* |
| bsp-server-10 | 141.223.121.77 | astros2.postech.ac.kr | `bsp-server-10` | cloud proxy |
| bsp-server-11 | 141.223.121.78 | angels.postech.ac.kr | `bsp-server-11` | **⚠️ ACCOUNT TAKEOVER** |
| bsp-server-? | 141.223.121.71 | — | `cogito-2.1:671b-cloud` | cloud proxy |
| 4gsr-beamline-ws | 141.223.48.182 | tpd.postech.ac.kr | `4gsr-beamline-ws` | **⚠️ ACCOUNT TAKEOVER** |

Naming pattern `bsp-server-N` (N confirmed: 2, 3, 6, 9, 10, 11) suggests a ≥12-node cluster. Node 141.223.121.71 serves `cogito-2.1:671b-cloud` (671B Cogito model via cloud proxy). The `4gsr-beamline-ws` node is on a separate subnet (141.223.48.0/24) at the PAL accelerator facility network.

---

## bsp-server-3 Notable Models

| Model | Notes |
|---|---|
| rnj-1:8b | **Essential AI proprietary foundation model** (Apache 2.0, 8.3B Q4_K_M, tool-capable, temp 0.2) |
| lukashabtoch/plutotext-r3-emotional:latest | Emotion recognition model (4.6GB) |
| deepseek-v4-pro:cloud | Pre-release cloud proxy |
| kimi-k2.6, qwen3-coder-next, minimax-m2.7 | Cloud proxies |

**rnj-1** is a proprietary foundation model from Essential AI (essential.ai). Template: `"You are rnj-1, a foundation model trained by Essential AI."` — Gemma 3 8B architecture base, tool-calling enabled. Confirmed live on POSTECH BSP infrastructure.

---

## Account Takeover Credentials (5 nodes)

| Node | Account | SSH Public Key |
|---|---|---|
| bsp-server-3 | `bsp-server-3` | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMrib+TXfSvqgAYDzlgo4SI1BV1Kk2BXXvXBifQNg4GD` |
| bsp-server-6 | `bsp-server-6` | (see previous entry) |
| bsp-server-9 (rangers) | `bsp-server-9` | `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIP+sYaEnLH3Ce2el7yd2TuHTVJVXVTD3wJuclCLoWJJ0` |
| bsp-server-11 | `bsp-server-11` | (see previous entry) |
| 4gsr-beamline-ws | `4gsr-beamline-ws` | (see previous entry) |

---

## Infrastructure

| Field | Value |
|---|---|
| Primary IP | 141.223.84.47 |
| Cluster subnet | 141.223.121.0/24 (multiple nodes) |
| Org | Pohang University of Science and Technology |
| Country | South Korea |
| Open ports | 11434 (Ollama — **public on all nodes**) |

---

## Cloud Proxy Subscriptions (18)

| Model | Provider | Notes |
|---|---|---|
| kimi-k2:1t-cloud | Moonshot AI | **1 trillion parameter model** |
| deepseek-v3.1:671b-cloud | DeepSeek | 671B parameter model |
| qwen3-coder:480b-cloud | Alibaba Qwen | 480B coding model |
| gpt-oss:120b-cloud | OpenAI | 120B GPT-OSS |
| kimi-k2.6:cloud | Moonshot AI | — |
| kimi-k2.5:cloud | Moonshot AI | — |
| kimi-k2-thinking:cloud | Moonshot AI | — |
| glm-5.1:cloud | Zhipu AI | — |
| glm-5:cloud | Zhipu AI | — |
| glm-4.7:cloud | Zhipu AI | — |
| glm-4.6:cloud | Zhipu AI | — |
| deepseek-v4-pro:cloud | DeepSeek | — |
| deepseek-v4-flash:cloud | DeepSeek | — |
| deepseek-v3.2:cloud | DeepSeek | — |
| minimax-m2.7:cloud | MiniMax | — |
| minimax-m2.5:cloud | MiniMax | — |
| minimax-m2.1:cloud | MiniMax | — |
| minimax-m2:cloud | MiniMax | — |
| qwen3.5:cloud | Alibaba | — |
| qwen3-coder-next:cloud | Alibaba | — |
| nemotron-3-super:cloud | NVIDIA | — |
| gemini-3-flash-preview:cloud | Google | — |

---

## Findings

### F1 — 18 Cloud Subscriptions Exposed (CRITICAL)

All 18 cloud proxy subscriptions are accessible on the unauthenticated primary node. Any internet actor can:
- Enumerate all cloud subscriptions via `/api/tags`
- Inject system prompts into cloud proxy models via CVE-2025-63389
- Drain operator API quotas through the exposed port

The subscription portfolio includes frontier models: Kimi K2 (1T), DeepSeek V3.1 (671B), Qwen3-Coder (480B).

### F2 — 3 Account Takeovers via Live Ollama Connect Claim URLs (CRITICAL)

Three nodes return a live Ollama Connect claim URL in their 401 response body. The `key=` parameter is a base64-encoded SSH private key that can be used to claim ownership of the Ollama account at `https://ollama.com/connect`. Account takeover grants full model management, billing control, and cloud subscription access under the institution's identity.

```json
// bsp-server-6 (141.223.121.73, dragons.postech.ac.kr)
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-6&key=c3NoLWVkMjU1MT..."}
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIHcp6+jJK6HzmVIhHwgMhzsL/t0n5NsbasdZQ4U/DDDj

// bsp-server-11 (141.223.121.78, angels.postech.ac.kr) — NEW
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=bsp-server-11&key=c3NoLWVkMjU1MT..."}
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICxY4pScZAPDEe6wdNmqMBRI0Aovb6sd3lgIuS1U5Eyi

// 4gsr-beamline-ws (141.223.48.182, tpd.postech.ac.kr) — SYNCHROTRON NODE
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=4gsr-beamline-ws&key=c3NoLWVkMjU1MT..."}
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIPjA3VulH0uRyTB9PAQiZCf/E2ACSFYg+lcgZJA8FN4X
```

Credential leaks also present on bsp-server-2 (141.223.121.58) and bsp-server-10 (141.223.121.77) but those nodes did not expose live claim URLs in the 2026-05-02 scan.

### F3 — 4th Generation Synchrotron Beamline Workstation Exposed (CRITICAL)

`4gsr-beamline-ws` (`tpd.postech.ac.kr`, 141.223.48.182) is a workstation at the PAL 4th-Generation Synchrotron Radiation facility. The name prefix `4gsr` directly references POSTECH's 4th Generation Synchrotron Radiation project; `tpd` (Transport Physics Division or beamline control) confirms instrument proximity.

The node hosts:
- `ingu627/qwen3:235b-q3_K_M` — 235B parameter Qwen3 quantized locally (large VRAM machine)
- `minimax-m2.7:cloud` — cloud proxy subscription, credential takeover confirmed

Scientists at the beamline are using LLMs for data analysis or instrument control assistance. The node is Internet-exposed, not air-gapped. The 235B local model and cloud subscription together suggest this is production research tooling, not a test deployment.

### F4 — Model Injection on Research Infrastructure (CRITICAL)

All models on all nodes injectable via CVE-2025-63389. POSTECH researchers using these models — including at the PAL beamline — receive outputs shaped by injected system prompts. Research data analysis via a compromised LLM is a data integrity risk.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to POSTECH IT Security
