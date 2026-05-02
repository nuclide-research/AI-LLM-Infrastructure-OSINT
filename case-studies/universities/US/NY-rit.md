# Rochester Institute of Technology — 4-Node Cluster, DGX with 18 Cloud Subscriptions, Student Machine with Abliterated Models

_NuClide Research · 2026-05-01_

---

## Summary

Rochester Institute of Technology (RIT) has four externally-accessible Ollama nodes on campus, including an NVIDIA DGX research server with 18 cloud proxy subscriptions (same subscription portfolio as POSTECH/Shiv Nadar/Hanoi) and a student machine with two abliterated QwQ-32B models alongside an embedding model for a RAG pipeline. All nodes injectable via CVE-2025-63389.

---

## Infrastructure

| Hostname | IP | Models | Cloud | Notes |
|----------|-----|--------|-------|-------|
| disco-dgx-spark.wireless.rit.edu | 129.21.25.95 | 25 | **18** | NVIDIA DGX GPU server |
| ragdepc.student.rit.edu | 129.21.149.97 | 4 | 0 | **Student machine — abliterated models + RAG** |
| 8N610008D0.ad.rit.edu | 129.21.220.95 | 10 | 1 (deepseek) | AD-joined workstation |
| cl5.wireless.rit.edu | 129.21.146.150 | 19 | 0 | Wireless client — llama2-uncensored |

---

## Node: 8N610008D0.ad.rit.edu (AD Workstation — Cloud Proxy + Account Takeover)

| Field | Value |
|-------|-------|
| IP | 129.21.220.95 |
| Hostname | 8N610008D0.ad.rit.edu |
| Models | 10 (1 cloud proxy: deepseek) |

Cloud proxy 401 leaks Ollama Connect credentials:

```json
{
  "error": "unauthorized",
  "signin_url": "https://ollama.com/connect?name=72e95ec7e5f4&key=<base64>"
}
```

- **Username:** `72e95ec7e5f4`
- **SSH pubkey:** `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMq7cpKDactDR6mE3QWowO3fcW+GaM4HcOSjhbxRtsCN`

Username `72e95ec7e5f4` is a MAC address — matches the AD hostname pattern (8N610008D0), AD-joined Windows machine running Ollama.

---

## Node: disco-dgx-spark (DGX GPU Server — 18 cloud subscriptions)

Same 18-model cloud portfolio as POSTECH, Shiv Nadar, and Hanoi University:  
DeepSeek (v4-pro, v4-flash, v3.2), MiniMax (m2, m2.1, m2.5, m2.7), Kimi (k2.5, k2.6, k2-thinking), GLM (4.6, 4.7, 5, 5.1), Qwen (3.5, coder-next), Gemini (flash-preview), Nemotron.

Local models: qwen3.6:35b (22GB), qwen3.5:27b (16GB), qwen3-coder-next:latest (48GB), llama3.2:3b, smollm2:135m.

All 25 models injectable via CVE-2025-63389. 18 cloud subscriptions accessible through unauthenticated port.

---

## Node: ragdepc.student.rit.edu (STUDENT Machine — Abliterated + RAG)

| Model | Size | Notes |
|---|---|---|
| qwq:latest | 14 GB | QwQ-32B reasoning model |
| qwq-uncensored:latest | 14 GB | **Abliterated QwQ — safety removed** |
| huihui_ai/qwq-abliterated:32b-Q3_K_M | 14 GB | **Abliterated QwQ — safety removed** |
| nomic-embed-text:latest | 0 GB | **Embedding — RAG pipeline** |

- Hostname prefix `ragdepc` suggests "RAG deep PC" — student building a RAG system with abliterated reasoning models
- Two variants of abliterated QwQ-32B publicly accessible on student hardware
- Model injection via CVE-2025-63389 affects any RAG pipeline using these models

---

## Node: cl5.wireless.rit.edu (Wireless Client — uncensored model)

19 models including:
- `llama2-uncensored:7b` — uncensored Llama 2
- `gpt-oss:latest` (12GB), `glm-4.7-flash` (17GB), `lfm2.5-thinking`, `ShreyanGondaliya/s5:latest`
- Multiple qwen3.5 variants, deepseek-coder

---

## Findings

### F1 — DGX GPU Server: 18 Cloud Subscriptions Exposed (CRITICAL)

Research-grade NVIDIA DGX server running Ollama with 18 cloud proxy subscriptions, publicly accessible without authentication.

### F2 — Student Machine: Dual Abliterated Reasoning Models + RAG (HIGH)

Student's machine running two variants of QwQ-32B with safety fine-tuning removed, alongside an embedding model confirming a RAG pipeline. Both abliterated models and the RAG pipeline are publicly accessible without credentials.

### F3 — Third Node: llama2-uncensored on Wireless Client (MEDIUM)

Wireless-connected laptop running `llama2-uncensored:7b` exposed on port 11434.

---

## Pattern Note

The DGX server's 18-model cloud proxy portfolio (DeepSeek + MiniMax + Kimi + GLM + Qwen + Gemini + Nemotron) appears identically at POSTECH (Korea), Shiv Nadar (India), Hanoi University (Vietnam), and now RIT. This suggests a **shared Ollama Connect subscription, demonstration account, or institutional license** distributed across multiple universities.

---

## Remediation

```bash
# All nodes
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Network perimeter: block TCP 11434 outbound at campus edge.

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to RIT IT Security: security@rit.edu
