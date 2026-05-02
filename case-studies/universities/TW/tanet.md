# Taiwan Academic Network (TANet) — 18-Node Cluster, 1 Account Takeover, Multi-Institution

_NuClide Research · 2026-05-02_

---

## Summary

The Taiwan Ministry of Education Computer Center operates TANet (Taiwan Academic Network), the national IP allocation backbone for all Taiwan universities. The institute sweep found 18 live Ollama nodes across the TANet IP space, spanning at least six institutions: National Taiwan University (NTU), National Chengchi University (NCCU), National Tsing Hua University (NTHU), Fu Jen Catholic University (FJU), National Cheng Kung University (NCKU), and an unidentified host. One node has a live account takeover URL (`name=ollama`). Multiple nodes run cloud proxy subscriptions. Versions span 0.11.6 to 0.22.1 — this deployment has been running for years.

---

## Cluster Topology

| IP | Hostname | Institution | Version | Models | Tags |
|---|---|---|---|---|---|
| 120.126.16.144 | — | TANet | 0.20.3 | 7 | — |
| 140.112.18.214 | pc214.ee.ntu.edu.tw | NTU EE | 0.17.7 | 5 | sys: 5G security |
| 140.112.91.82 | — | NTU | 0.18.0 | 4 | CLOUD |
| 140.112.183.119 | — | NTU | 0.22.1 | 6 | CLOUD |
| 140.112.233.108 | g1pc2n108.g1.ntu.edu.tw | NTU GPU cluster | 0.19.0 | 11 | — |
| 140.114.197.130 | sd197130.shin34.ab.nthu.edu.tw | NTHU | 0.22.0 | 2 | — |
| 140.115.54.35 | — | TANet | 0.15.4 | 1 | — |
| 140.116.82.105 | — | TANet | 0.20.7 | 8 | CLOUD |
| 140.119.163.219 | V100x4.cs.nccu.edu.tw | NCCU CS V100 | 0.11.6 | 15 | — |
| 140.125.180.91 | — | TANet | 0.14.3 | 5 | CLOUD + **⚠️ ACCOUNT TAKEOVER** |
| 140.136.147.26 | 740-26.ee.fju.edu.tw | FJU EE | 0.20.2 | 1 | — |
| 140.136.149.212 | — | TANet | 0.21.0 | 2 | — |
| 140.136.178.236 | user236.phy.fju.edu.tw | FJU Physics | 0.21.0 | 4 | — |
| 140.136.192.220 | user220.medph.fju.edu.tw | FJU MedPH | 0.21.2 | 8 | — |
| 140.136.239.75 | net2net.net.fju.edu.tw | FJU | 0.18.2 | 5 | — |
| 163.13.202.114 | — | TANet | 0.21.0 | 2 | — |
| 163.25.105.115 | — | NCKU | 0.22.0 | 9 | — |
| 210.70.138.233 | — | TANet | 0.21.0 | 3 | — |

---

## Infrastructure

| Field | Value |
|---|---|
| Network | Taiwan Academic Network (TANet) |
| Registrant | Ministry of Education Computer Center |
| Country | Taiwan |
| IP ranges | 120.126.x, 140.112.x–140.136.x, 163.x, 210.70.x |
| Open port | 11434 (Ollama — public on all nodes) |

---

## Findings

### F1 — Account Takeover via Live Ollama Connect Claim URL (CRITICAL)

`140.125.180.91` returns a live Ollama Connect claim URL. The account name `ollama` (not a container ID, not a hostname) indicates someone ran `ollama serve` on this box with zero configuration — no custom name, no custom key. Account takeover grants full model management and cloud subscription control.

```json
{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=ollama&key=c3NoLWVkMjU1MT..."}
// SSH: ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIGdI/XYFCAqJaH2k+MfvjFRJ2i4GYKPN3rvGAEF8Niey
```

Cloud proxy models on this node: `deepseek-v4-pro:cloud`, `minimax-m2.7:cloud`.

### F2 — Multi-University Cloud Proxy Exposure (CRITICAL)

Four nodes have active cloud proxy subscriptions:

| IP | Cloud models |
|---|---|
| 140.125.180.91 | deepseek-v4-pro:cloud, minimax-m2.7:cloud |
| 140.112.91.82 | minimax-m2.7:cloud |
| 140.112.183.119 | minimax-m2.7:cloud |
| 140.116.82.105 | deepseek-v4-pro:cloud |

Any internet actor can drain these operator API quotas through the unauthenticated endpoints.

### F3 — 5G Network Security Expert System Prompt Leaked (HIGH)

`140.112.18.214` (NTU EE, `pc214.ee.ntu.edu.tw`) runs a qwen3.5 model with system prompt:

```
You are a 5G network security expert. Respond directly without internal reasoning. /no_think
```

The deployment is on the EE department at NTU — active research tooling for 5G security analysis, fully injectable via CVE-2025-63389.

### F4 — NCCU V100 Cluster Exposed Since v0.11.6 (HIGH)

`140.119.163.219` (`V100x4.cs.nccu.edu.tw`) runs Ollama v0.11.6 with 15 models — the oldest version in this cluster, indicating exposure since early 2024. NCCU Computer Science V100 GPU cluster, unauthenticated.

### F5 — NTU GPU Cluster g1pc2n108 (HIGH)

`140.112.233.108` (`g1pc2n108.g1.ntu.edu.tw`) — NTU's GPU compute cluster node g1pc2n108, 11 models. Previously documented independently in `TW/ntu-gpu.md`; confirmed again in TANet sweep.

### F6 — Model Injection on All Nodes (CRITICAL)

CVE-2025-63389 applies to all 18 nodes. Researchers across six Taiwan institutions receive model outputs under attacker-controlled system prompts after a single `/api/create` call.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Pending outreach to TANet / MoE Computer Center
- **Contact:** noc@tanet.edu.tw
