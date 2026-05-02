# "No. 18 Institute of Jingdong HQ" — 26-Node Cluster, China Unicom

_NuClide Research · 2026-05-02_

---

## Summary

A 26-node Ollama cluster on China Unicom's 111.228.0.0/16 range, all registered to org `eleven street,No. 18 Institute of Jingdong headquarters`. The org name reads as a Chinese physical address (Jingdong district, No. 18 compound), suggesting a large research institute or corporate campus. All nodes run Ollama v0.5.10 — a 2023-era version — indicating a static, long-running deployment. Primary models across the cluster: deepseek-r1:1.5b (17 nodes), llama3.2:3b (15 nodes), nomic-embed-text (11 nodes, RAG pipeline). The uniform version and model distribution suggests centralized administration with individual researcher nodes.

---

## Cluster Infrastructure

| Field | Value |
|---|---|
| Org | eleven street,No. 18 Institute of Jingdong headquarters |
| IP range | 111.228.0.0/16 (China Unicom) |
| Country | China |
| Nodes | 26 live |
| Ollama version | v0.5.10 (all nodes) |
| Open port | 11434 (public on all nodes) |

---

## Model Distribution (cluster-wide)

| Model | Nodes |
|---|---|
| deepseek-r1:1.5b | 17 |
| llama3.2:3b | 15 |
| nomic-embed-text:latest | 11 |
| smollm2:135m | 5 |
| qwen2.5:1.5b | 1 |
| qwen2.5:7b | 1 |
| qwen2.5:3b | 1 |
| codeqwen:7b | 1 |
| freehuntx/qwen3-coder:14b | 1 |
| aliafshar/gemma3-it-qat-tools:27b | 1 |
| bge-m3:latest | 1 |
| mxbai-embed-large:latest | 1 |

---

## Notable Nodes

| IP | Version | Models | System Prompt |
|---|---|---|---|
| 111.228.47.1 | 0.5.10 | 7 | Qwen: "You are Qwen, created by Alibaba Cloud." |
| 111.228.44.72 | 0.15.2 | 2 | Qwen2.5-3b: default |
| 111.228.59.44 | 0.5.10 | 2 | codeqwen: "You are a helpful assistant." |
| 111.228.47.196 | 0.17.7 | 2 | — |

---

## Findings

### F1 — 26-Node Cluster, All Public on 0.0.0.0:11434 (CRITICAL)

All 26 nodes expose Ollama on the public internet without authentication. The cluster spans a /16 subnet, suggesting a large campus or research compound with many individual researcher workstations or assigned VMs.

### F2 — Stale Version Across Entire Cluster (HIGH)

Every node runs v0.5.10 — a November 2023 release. No node has been updated in over 18 months. The uniform version across 26 nodes indicates either: centralized deployment that was never patched, or a managed image used for researcher VMs. All known Ollama CVEs (CVE-2025-63389, SSRF via /api/pull) apply.

### F3 — RAG Pipeline Signal (11 nomic-embed-text nodes) (MEDIUM)

11 nodes have `nomic-embed-text:latest` alongside generative models — standard RAG pipeline configuration. Whatever these nodes are processing, vector embeddings are being generated locally.

### F4 — Model Injection on All Nodes (CRITICAL)

CVE-2025-63389 applies. Single `/api/create` call injects a persistent system prompt across any of the 26 nodes.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-02
- **Status:** Institution identity unconfirmed — pending further OSINT
