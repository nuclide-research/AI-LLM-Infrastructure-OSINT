# LLM08:2025 — Vector and Embedding Weaknesses

**OWASP rank 2025:** #8 (**NEW in 2025**)

Added to the 2025 list because of "the rise of RAG architectures creating new attack vectors." The 2023 list predated mass RAG adoption; the 2025 update brings the vector-store layer into scope as a first-class attack surface.

## Description

Vulnerabilities specific to the vector + embedding layer of RAG and agent-memory systems:

1. **Vector database manipulation** — direct write access to the vector store (Pinecone, Weaviate, Qdrant, Milvus, Chroma) when authentication is misconfigured
2. **Embedding inversion attacks** — recovering original text content from embedding vectors
3. **Retrieval poisoning** — inserting documents that will be retrieved for chosen queries (overlaps LLM04)
4. **Context injection through knowledge bases** — manipulating the retrieved-context window through the RAG corpus
5. **Embedding model attacks** — adversarial examples in embedding space that retrieve attacker-chosen content for benign-looking queries

## Academic citations

The 2026-06-06 cs* corpora cover embedding-space adversarial work:

- **Mikolov word embeddings + BERT lectures** (CS 307, CS 442) — foundational embedding semantics
- **Adversarial examples** literature lineage — FGSM (`1412.6572`), C&W (`1608.04644`), Madry PGD (`1706.06083`) all in CS 562 / CS 598 — the conceptual base for "adversarial perturbation in embedding space" extends naturally from "adversarial perturbation in pixel space"
- **GCN** (Kipf & Welling, `1609.02907`) — graph convolutions; graph-embedding adversarial work (Zugner et al. Nettack `1804.00308`) in CS 562 / CS 598 covers structural attacks on embeddings
- **CycleGAN** (`1703.10593`) and related — semantic embedding manipulation

The graph-AdvML cluster in CS 598 Fall 2021 (~6 papers) is the closest direct ancestor to embedding-space adversarial attacks.

## Current survey instances

NuClide's prior Cat-02 Vector Database survey (2026-06-04) covered the vector-store layer extensively: 148 verified-unauth Vector DB hosts across Qdrant, Weaviate, Milvus, Chroma, Pinecone-self-hosted. Current 2026-06-06 surveys extend this:

- **Flowise FDAPineconeIndexing** (`146.190.128.73:3000`) — `pineconeIndex: "flowise"` discoverable from the open chatflow config; the operator's Pinecone API key (in Flowise credential store) gives anyone with chatflow-API access the ability to read or write to the Pinecone index. **The vector store is reachable via the chatflow proxy.**
- **RAGFlow** (`surveys/2026-06-06-ragflow.md`) — 87.2% REGISTER_OPEN. A registered tenant can write to the vector store (RAGFlow's internal Infinity/Elasticsearch backend). Multi-tenant isolation determines whether one tenant's writes affect another's retrieval.
- **Earlier surveys**: Weaviate 13,631 PII records publicly accessible (aimable.ai case, 2026-05-15); Qdrant 4 collections including 18,828 vectors on University of Queensland UQConnect cluster (Cat-05 finding F-006).

## Why LLM08 is structurally connected to the NuClide research program

NuClide's tooling (aimap with Qdrant/Weaviate/Milvus/Chroma fingerprints; herald's LLM-platform configs) was built specifically to surface this attack class. The 2025 addition of LLM08 to OWASP validates the program's focus area: the field has caught up to what the NuClide methodology has been finding for 12+ months.

## Defensive controls

- Auth-gate vector database endpoints (Qdrant `--api-key`, Weaviate auth, Pinecone API key rotation)
- Network segmentation between LLM gateway and vector store (vector store not internet-facing)
- Multi-tenant isolation at the vector-namespace level (Pinecone namespaces, Qdrant collections per tenant)
- Retrieval provenance display (user sees the source document for each answer)
- Embedding model versioning and signature verification

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — surfaces vector-store exposures
- **421 Database Administrator** — operator-side counterpart; the role with primary responsibility for vector-DB auth configuration
- **661 R&D Specialist** — builds the vector-store-specific fingerprints in aimap

## Insight #76 connection

The auth-permissive-default cohort that enables LLM02 disclosure also enables LLM08: every Flowise/RAGFlow/LangChain/LlamaIndex deployment shipped with an attached vector store inherits the auth-permissive default of the orchestration layer. The vector store is downstream; if the orchestration layer is unauthenticated, the vector store is reachable through it.
