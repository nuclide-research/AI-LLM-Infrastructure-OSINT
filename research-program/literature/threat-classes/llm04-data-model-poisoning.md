# LLM04:2025 — Data and Model Poisoning

**OWASP rank 2025:** #4 (expanded from LLM03:2023 Training Data Poisoning)
**OWASP rank 2023:** LLM03 #3

The 2025 expansion now covers:
- Training-data poisoning (the original 2023 scope)
- **RAG knowledge-base poisoning** (new — directly relevant to NuClide RAG surveys)
- Fine-tuning data manipulation
- Model backdoor insertion
- Embedding manipulation (links to LLM08:2025)

## Description

An attacker introduces malicious content into:

1. **Pre-training corpus** — large-scale web scraping is hard to defend; canonical poisoning literature
2. **Fine-tuning dataset** — smaller, attacker-accessible; common in domain-specific LLMs
3. **RAG knowledge base** — the data the model retrieves at inference time; **the NuClide-relevant new class**
4. **Embedding model weights** — through compromised model upload (overlaps LLM03)
5. **Reward model in RLHF** — the most subtle; trained-in misaligned reward

Causes the model to (a) emit attacker-chosen output on trigger inputs (backdoor), (b) drift toward attacker preferences over many queries (slow poisoning), or (c) leak training-set content (memorization manipulation).

## Academic citations

Strong coverage in the NuClide aisecure corpora:

- **Biggio et al. "Poisoning Attacks against Support Vector Machines" (`arxiv_1206.6389`)** — foundational ML poisoning paper. Indexed in CS 562, CS 598 Fall 2020/2021.
- **Gu et al. "BadNets" (`arxiv_1708.06733`)** — canonical neural backdoor.
- **Chen et al. "Targeted Backdoor Attacks on Deep Learning Systems Using Data Poisoning" (`arxiv_1712.05526`)** — in CS 442.
- **Shafahi et al. "Poison Frogs!" (`arxiv_1804.00792`)** — clean-label poisoning.
- **Saha et al. "Hidden Trigger Backdoor Attacks"** — in CS 598 Fall 2020/2021.
- **DBA: Distributed Backdoor Attacks against Federated Learning** (Bo Li-coauthored; `arxiv_2004.04986`) — in CS 562, CS 598 Fall 2021.
- **Neural Cleanse** — backdoor detection — in CS 598 Fall 2021.
- **Trojaning Attack on Neural Networks** (Liu et al., NDSS 2018) — in CS 598 Fall 2021.

## Current survey instances

The NuClide 2026-06-06 surveys **enable** LLM04 findings on RAG platforms without exercising them:

- **RAGFlow** (`surveys/2026-06-06-ragflow.md`) — 618/709 hosts allow public registration. A registered tenant can create knowledge bases. **If multi-tenancy isolation is misconfigured**, an attacker tenant can poison the shared knowledge base read by all tenants. NuClide does not exercise this — the survey establishes the enabling condition only.
- **Flowise FDAPineconeIndexing** (`146.190.128.73:3000`) — Pinecone vector index "flowise" connected to Flowise. With the Flowise chatflow API open, an attacker could potentially write to the Pinecone index, poisoning future retrievals. Not exercised.

## Why RAG poisoning is the most actionable LLM04 class for NuClide

Pre-training data poisoning requires scale (hundreds of gigabytes of crawled web data). Fine-tuning data poisoning requires access to the operator's labeled dataset. **RAG knowledge-base poisoning requires only registration on an open-signup RAG platform.** Given the 87.2% REGISTER_OPEN rate for RAGFlow alone, the enabling-condition population is in the high hundreds.

The OWASP 2025 revision specifically added RAG poisoning to LLM04 because of exactly this scaling property.

## Defensive controls

- Multi-tenant isolation hardening (RAGFlow's tenant model, Pinecone's namespace separation)
- Content-source signing for RAG corpora
- Retrieval-time provenance display (so the user sees which document the answer came from)
- Periodic backdoor detection (Neural Cleanse-class techniques applied at production scale)
- Federated-learning certified defenses (CRFL, where Bo Li's group has the canonical work)

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — finds the open-registration enabling condition
- **661 R&D Specialist** — researches poison-detection techniques for production deployment
- **632 Systems Developer** — implements multi-tenant isolation correctly
- **A0044 KSA: Ability to apply programming language structures (e.g., source code review)** — code review of the multi-tenant isolation logic in RAGFlow / Flowise / Phoenix
