# Monash University — 3-Node Cluster, DeepSeek V3.1 671B, Cloud Proxies

_NuClide Research · 2026-05-01, updated 2026-05-03_

---

## Summary

Monash University (Melbourne, Australia) exposes three Ollama nodes on the `118.138.0.0/16` ERC subnet. The primary node (`vm-118-138-233-225.erc.monash.edu.au`) carries a full **DeepSeek V3.1 671B** (376.7GB) — largest local model in the sweep — alongside two cloud proxies and a qwen3-coder-next:latest (48.2GB). Two secondary nodes run smaller research stacks with active system prompts.

---

## Infrastructure

| Node | IP | Hostname | Version | Models | Cloud |
|---|---|---|---|---|---|
| Primary | 118.138.233.225 | vm-118-138-233-225.erc.monash.edu.au | 0.20.2 | 8 | 2 |
| Node 2 | 118.138.243.239 | vm-118-138-243-239.erc.monash.edu.au | 0.18.3 | 3 | 0 |
| Node 3 | 118.138.243.34 | vm-118-138-243-34.erc.monash.edu.au | 0.19.0 | 3 | 0 |

All on Monash ERC (Education and Research Cluster) subnet.

---

## Model Inventory — Primary Node (118.138.233.225)

| Model | Size | Notes |
|---|---|---|
| `deepseek-v3.1:latest` | **376.7 GB** | **671.0B params** — largest local model in sweep |
| `qwen3-coder-next:latest` | 48.2 GB | — |
| `nemotron-cascade-2:latest` | 24.3 GB | NVIDIA Nemotron Cascade 2 |
| `gpt-oss-safeguard:latest` | 13.8 GB | gpt-oss 20.9B — `safeguard` variant, system prompt empty |
| `kimi-k2.5:cloud` | 0 GB | ☁️ Cloud proxy |
| `minimax-m2.7:cloud` | 0 GB | ☁️ Cloud proxy |
| `gemma4:latest` | 9.6 GB | — |
| `qwen3.5:latest` | 6.6 GB | — |

**Note:** On probe, inference against `deepseek-v3.1:latest` returns `{"error":"model requires more system memory (373.8 GiB) than is available (18.9 GiB)"}`. Model is stored on disk but the current primary node lacks sufficient RAM to load it. The model file itself (376.7GB) represents the storage investment; inference would require the full cluster allocation.

---

## Model Inventory — Nodes 2 + 3 (118.138.243.239, 118.138.243.34)

Both nodes carry identical stacks:

| Model | Notes |
|---|---|
| `deepseek-r1:latest` | DeepSeek R1 reasoning |
| `qwen2.5:latest` | Qwen 2.5 — **default Alibaba system prompt active** |
| `llama3:latest` | Meta Llama 3 |

**System prompt on qwen2.5:** `"You are Qwen, created by Alibaba Cloud. You are a helpful assistant."` — default unmodified installation.

---

## Findings

### F1 — DeepSeek V3.1 671B Stored (HIGH)

`deepseek-v3.1:latest` (376.7GB, 671B params) is present on the primary node. Live inference is currently blocked by insufficient system RAM (18.9GB available vs 373.8GB required). However: (a) the model is accessible for download via API, (b) cloud proxies on the same node are fully drained, (c) future memory expansion would make inference live instantly.

### F2 — Cloud Proxy Portfolio (HIGH)

`kimi-k2.5:cloud` and `minimax-m2.7:cloud` on primary node. Both 401 without credential leak.

### F3 — gpt-oss-safeguard Unconfigured (MEDIUM)

`gpt-oss-safeguard:latest` (13.8GB) carries the name of a safety-filtered variant, but the system prompt is empty — the filtering was never configured.

### F4 — 3-Node Cluster, All Injectable (HIGH)

CVE-2025-63389 applies to all 14 models across all three nodes.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to Monash IT Security (monash.edu.au)
