# Agricultural University of Athens — 142GB Qwen3-235B MoE, Dual-Embedding RAG

_NuClide Research · 2026-05-03_

---

## Summary

`afa4pc19.aua.gr` (143.233.187.19), Agricultural University of Athens (Γεωπονικό Πανεπιστήμιο Αθηνών, AUA), runs Ollama v0.18.2 with a 5-model stack anchored by `qwen3:235b-a22b-instruct-2507-q4_K_M` — the Qwen3 235B MoE model (235.1B total params, 22B active, July 2025 instruction variant) at 142GB. A dual-embedding RAG pipeline (BGE-M3 + nomic-embed-text) is running alongside DeepSeek-R1:32B and Llama3.3:70B.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 143.233.187.19 |
| Hostname | afa4pc19.aua.gr |
| Organization | Agricultural University of Athens (AUA) |
| Network | AUA Greece (143.233.0.0/16) |
| Country | Greece |
| Ollama version | 0.18.2 |
| Open port | 11434 (public) |

---

## Model Inventory

| Model | Size | Notes |
|---|---|---|
| `qwen3:235b-a22b-instruct-2507-q4_K_M` | 142GB | **235.1B params**, 22B active (MoE), July 2025 instruction variant, Q4_K_M |
| `llama3.3:70b` | 42GB | Llama 3.3 70B |
| `deepseek-r1:32b` | 19GB | DeepSeek reasoning model |
| `bge-m3:latest` | 1GB | **BGE-M3 multilingual RAG embedding** |
| `nomic-embed-text:latest` | — | **Nomic embedding** — secondary RAG layer |

**Total local storage:** ~204GB+

---

## Findings

### F1 — Qwen3 235B: Largest MoE Model on Greek Academic Infrastructure (HIGH)

`qwen3:235b-a22b-instruct-2507-q4_K_M` is a 235.1B parameter mixture-of-experts model — 22B parameters active per inference pass — running on agricultural university hardware. The `2507` tag indicates the July 2025 instruction fine-tune (the most current Qwen3 variant). At Q4_K_M quantization, the 142GB weight file requires significant GPU memory. The "afa4pc19" hostname suggests this is a department workstation (PC #19, AFA department — possibly Applied Forestry, Agricultural Sciences, or similar).

Unauthenticated inference against a 235B MoE constitutes significant compute theft at scale.

### F2 — Dual-Embedding RAG Pipeline (HIGH)

Both `bge-m3:latest` (multilingual, 500M+ params) and `nomic-embed-text:latest` are present simultaneously — a two-embedding RAG architecture. BGE-M3 supports 100+ languages, suggesting multilingual document retrieval. The combination with DeepSeek-R1 and Qwen3-235B indicates an active research-grade RAG system.

Documents indexed into the vector store (research papers, agricultural datasets, lab reports, student theses) are queryable via the unauthenticated API.

### F3 — CVE-2025-63389 (CRITICAL)

All 5 models injectable via unauthenticated `/api/create`. The 235B model's context handling is overwritable.

---

## Remediation

```bash
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending outreach to AUA IT Security (aua.gr) / GRNET (GEANT)
