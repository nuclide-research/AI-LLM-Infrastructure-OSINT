# China Telecom Tianjin — 46-Node Multi-Tenant Ollama Cluster

_NuClide Research · 2026-05-03_

---

## Summary

China Telecom's Beijing-Tianjin-Hebei Big Data Industry Park (Tianjin, AS141679) hosts at least 46 cloud VM instances running Ollama on port 11434 without authentication. All discovered through a Shodan `org:"institute"` sweep, suggesting the tenants include research institutes (likely Chinese state/defense-adjacent research entities — "No. 18 Institute" naming convention found in scan data). Unlike the Jingdong cluster (AS9929, 26 uniform nodes), this is a multi-tenant environment with per-tenant model diversity. Uniformly Ollama v0.5.10 (majority) with some nodes on v0.15.2, no rDNS on any node.

---

## Infrastructure

| Field | Value |
|---|---|
| ASN | AS141679 |
| Org | China Telecom Beijing Tianjin Hebei Big Data Industry Park Branch |
| City | Tianjin, China |
| IP Range | 111.228.0.0/16 (subnet sample) |
| Nodes found | 46 (live ~25 at time of probe) |
| Ollama version | 0.5.10 (majority), 0.15.2 (some) |
| rDNS | None on any node |

---

## Model Diversity (sampled)

| IP | Models | Notes |
|---|---|---|
| 111.228.60.102 | aliafshar/gemma3-it-qat-tools:27b, smollm2:135m, deepseek-r1:1.5b | Tool-use Gemma 27B QAT |
| 111.228.39.48 | llama3.2:3b, nomic-embed-text, deepseek-r1:1.5b | RAG pipeline |
| 111.228.27.94 | deepseek-r1:1.5b, nomic-embed-text | RAG pipeline |
| 111.228.59.238 | freehuntx/qwen3-coder:14b, smollm2:135m, nomic-embed-text, deepseek-r1:1.5b | Code + RAG |
| 111.228.59.44 | codeqwen:7b, llama3.2:3b | Code-focused |
| 111.228.44.72 | llama3.2:3b, qwen2.5:3b | General (v0.15.2) |
| 111.228.56.186 | llama3.2:3b | Minimal |
| 111.228.1.223, .11.157 | (empty — provisioned, no models loaded) | — |

**Common pattern:** `deepseek-r1:1.5b` + `nomic-embed-text` = low-cost RAG pipeline on cloud VMs.

---

## Findings

### F1 — 46-Node Mass Exposure on Research Datacenter (HIGH)

46 cloud VMs on China Telecom's big data infrastructure park expose Ollama without authentication. The Shodan "institute" attribution suggests research institute tenants. No node has rDNS, consistent with cloud VM allocation. Any actor can run inference, inject system prompts, or enumerate what research pipelines are running on each node.

### F2 — RAG Pipeline Enumeration (MEDIUM)

At least 6 nodes run `nomic-embed-text` alongside small LLMs — a RAG pipeline footprint. Enumerating these nodes reveals which VMs are running document-retrieval pipelines and what data they may be ingesting, even without extracting the actual vector store contents.

### F3 — CVE-2025-63389 Applicable Across All Live Nodes (CRITICAL)

All live nodes run v0.5.10 (or v0.15.2), both affected. Unauthenticated `/api/create` allows system prompt injection on any loaded model. RAG pipelines are particularly vulnerable: injecting into the LLM layer can redirect generated answers independent of retrieval results.

---

## Context: Comparison to Jingdong Cluster

| Attribute | Jingdong (CN/jingdong.md) | Tianjin Cloud Park |
|---|---|---|
| ASN | AS9929 (China Unicom) | AS141679 (China Telecom) |
| Nodes | 26 | 46 |
| Version | v0.5.10 (uniform) | v0.5.10 majority |
| Models | deepseek-r1:1.5b dominant, uniform | Mixed — per-tenant diversity |
| Pattern | Single-org deployment | Multi-tenant cloud |
| rDNS | None | None |

Both clusters are on major Chinese carrier infrastructure, both uniformly v0.5.10, both without authentication. The Tianjin cluster is larger and more diverse, suggesting a shared cloud environment rather than a coordinated deployment.

---

## Remediation

Per-tenant fix (each VM operator):
```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

Cloud park operator: implement network-level ACL blocking public access to port 11434 across the 111.228.0.0/16 tenant subnet.
