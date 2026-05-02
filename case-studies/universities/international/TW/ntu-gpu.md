# National Taiwan University — GPU Cluster g1pc2n108, Multimodal Vision Stack

_NuClide Research · 2026-05-01_

---

## Summary

NTU's GPU cluster node `g1pc2n108.g1.ntu.edu.tw` (140.112.233.108) has Ollama exposed on port 11434 with 11 models skewed heavily toward vision and multimodal tasks — including GLM-OCR, GLM-4.7-Flash, MiniCPM-V, LLaVA, and llama3.2-vision.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 140.112.233.108 |
| Hostname | g1pc2n108.g1.ntu.edu.tw |
| Organization | National Taiwan University — GPU Cluster 1, Node 108 |
| Network | Taiwan MOE TANet (140.112.0.0/16) |
| Country | Taiwan |
| Open ports | 11434 (Ollama — public) |

---

## Model Inventory

| Model | Size | Category |
|---|---|---|
| `glm-4.7-flash:latest` | 17GB | ZhipuAI GLM-4.7 vision-language |
| `glm-ocr:latest` | 2GB | ZhipuAI OCR model (1.1B params) |
| `llama3.2-vision:latest` | 7GB | Meta vision-language |
| `minicpm-v:latest` | 5GB | MiniCPM-V multimodal |
| `llava:7b` | 4GB | LLaVA vision-language |
| `moondream:latest` | 1GB | Lightweight vision model |
| `qwen3.5:latest` | 6GB | Text LLM |
| `llama3.2:3b` | 1GB | Small LLM |
| `llama3.2:latest` | 1GB | — |
| `llama3:latest` | 4GB | — |
| `qwen:latest` | 2GB | — |

---

## Findings

### F1 — Unauthenticated Inference on University GPU Cluster (HIGH)

All 11 models are publicly accessible without authentication. The heavy multimodal/vision focus — GLM-4.7-Flash, GLM-OCR, LLaVA, MiniCPM-V, moondream, llama3.2-vision — indicates this node serves active vision research or document processing workflows.

**GLM-OCR** (glm-ocr:latest) is a specialized optical character recognition model. Any documents being processed through this pipeline are accessible to unauthenticated callers.

### F2 — CVE-2025-63389 Injectable (HIGH)

All 11 models injectable via unauthenticated `/api/create`.

---

## NTU Footprint

Multiple NTU nodes have been identified across different departments:

| Node | IP | Hostname | Notes |
|---|---|---|---|
| EE Dept | 140.112.91.82 | — | Engineering department node |
| PC-214 | 140.112.18.214 | — | Workstation/lab |
| GPU Cluster 1 Node 108 | 140.112.233.108 | g1pc2n108.g1.ntu.edu.tw | Vision stack |

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-01
- **Status:** Pending outreach to NTU CERT (140.112.0.0/16 — csirt@ntu.edu.tw)
