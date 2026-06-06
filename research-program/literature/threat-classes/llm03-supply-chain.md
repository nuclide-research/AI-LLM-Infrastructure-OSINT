# LLM03:2025 — Supply Chain

**OWASP rank 2025:** #3 (promoted from #5 in 2023)
**OWASP rank 2023:** LLM05 #5

## Description

LLM applications depend on a long supply chain: foundation model weights, fine-tuning datasets, embeddings models, vector database libraries, agent orchestration frameworks, plugin SDKs, MCP server packages. A compromise at any of these links propagates to every downstream user.

The 2025 promotion reflects "concrete incidents of poisoned foundation models" and "compromised third-party datasets causing disruptions." Examples include:
- Typosquatted PyPI packages mimicking popular AI/ML libraries (the 2023 `pytorchnightly` incident, `tensorfllow` and related)
- Compromised Hugging Face model uploads
- Poisoned LoRA adapters
- MCP-server supply-chain risk (the newest class — MCP launched late 2024, attack surface still emerging)

## Academic citations

The 2026-06-06 cs* literature corpora cover the precedent attacks on traditional ML supply chains:

- **Gu et al. "BadNets" (`arxiv_1708.06733`)** — the canonical paper on training-data backdoors. Indexed in CS 562, CS 598 Fall 2020/2021. The "outsourced training" threat model in BadNets is the direct ancestor of LLM03 supply-chain compromise: an attacker controls the training process at one step in the supply chain and the model behaves normally except under attacker-chosen triggers.
- **Chen et al. "Targeted Backdoor Attacks on Deep Learning Systems Using Data Poisoning" (`arxiv_1712.05526`)** — in CS 442.
- **Saha et al. "Hidden Trigger Backdoor Attacks"** — in CS 598 Fall 2020/2021.
- **Liu et al. "Trojaning Attack on Neural Networks"** (NDSS 2018) — in CS 598 Fall 2021.
- **CRFL (`arxiv_2106.08283`, Bo Li co-authored)** — certified robustness for federated learning, directly addressing the federated-learning supply-chain compromise scenario.

## Current survey instances

NuClide has not yet exercised LLM03 findings on the 2026-06-06 sweep set. The class is **enabled** by current findings but not directly probed:

- A Flowise instance with an open chatflow API and a Pinecone connection means the **upstream Pinecone index** is reachable with whatever credentials the operator embedded — supply-chain-adjacent. See `surveys/2026-06-06-flowise.md`.
- A LiteLLM instance proxying to Anthropic / Bedrock / Vertex with no master_key is the **distribution-stage** compromise — the operator's API key is the supply-chain link being abused. See `surveys/2026-06-06-litellm.md`.
- aimap-profile (NuClide tool) classifies hosts by their dependencies (Docker image tags, package manifests when exposed). This produces LLM03-aware findings when a host is running a flagged version of a known-compromised package.

## MCP supply-chain frontier

The Model Context Protocol (MCP) is mentioned in `~/.claude/CLAUDE.md` Assessment Protocol as a frontier sub-platform area. MCP server packages distributed via PyPI/npm/Docker Hub create a new supply-chain attack surface that the 2025 OWASP revision doesn't fully address yet (MCP launched late 2024). NuClide's MCP survey (prior session: 89 unauth findings) is the empirical baseline for this emerging class.

## Defensive controls

- Model card + dataset provenance verification (Hugging Face datasheets, model cards)
- Package supply-chain hardening (cryptographic signing, SBOM, vendor pinning)
- Dependency scanning for ML libraries (the NuClide `BARE` tool semantically ranks scanner findings against an embedded module corpus — see `tools/INDEX.md`)
- LoRA / adapter checksum verification at deploy time

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — finds the dependency exposure
- **622 Secure Software Assessor** — performs the upstream-code review
- **661 R&D Specialist** — builds the dependency-tracking tooling
- **K0126 KSA: Knowledge of Supply Chain Risk Management Practices (NIST SP 800-161)** — invoked across multiple NICE roles
