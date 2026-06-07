---
type: multi-host
---

# HolaModa + Delta701: Multi-Tenant Fashion Retail RAG with Dev/Prod Co-Located on Unauth ChromaDB

_NuClide Research · 2026-05-03_

---

## Summary

A ChromaDB instance on a DigitalOcean VPS holds 1.53M embedded documents across seven collections, spanning two tenants (HolaModa and Delta701) and mixing development with production environments on the same database. All readable without authentication on port 8000. The collection naming pattern (`chroma_hmdev_*`, `chroma_delta701dev_*`, `holamoda_google_multi_002`) discloses environment separation that exists in the application layer but has been collapsed at the database layer, a textbook multi-tenant SaaS isolation gap.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854
- **overlap (Common AI KSATs (all 5 roles)):** K1157, K1158, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 46.101.118.246 |
| Hosting | DigitalOcean |
| Port | 8000 (HTTP, no auth) |
| ChromaDB version | 0.6.3 (v2 API) |
| Tenant / DB | `default_tenant` / `default_database` (single ChromaDB tenant, multi-app) |
| Discovery date | 2026-05-03 |
| Embedding model | Google Cloud Vertex AI `text-embedding-gecko` (per collection naming) |

---

## Collections

| Collection | Docs | Inferred role |
|---|---|---|
| `holamoda_google_multi_002` | 736,711 | HolaModa primary catalog (multi-language?) |
| `holamoda_google` | 652,435 | HolaModa primary catalog (legacy) |
| `chroma_delta701_textembedding-gecko` | 65,324 | Delta701 production |
| `chroma_delta701dev_textembedding-gecko` | 64,658 | Delta701 development |
| `chroma_hmdev_textembedding-gecko` | 9,500 | HolaModa development |
| `chroma_demorep_textembedding-gecko` | 2,217 | "Demo rep", possibly a third tenant or a shared demo |
| `holamoda_google_005` | 2,250 | HolaModa variant (perhaps a chunking experiment) |

Aggregate: **1,533,095** documents.

---

## Findings

### F1: Two Tenants Co-Located on One ChromaDB (CRITICAL)

The `holamoda_*` and `chroma_delta701*` namespace prefixes identify **two distinct tenants** sharing the same ChromaDB instance. ChromaDB has only one database tenant boundary, `default_tenant/default_database`. Application-layer logic must restrict each tenant's queries to their own collection prefix; if any query path accepts a collection name from user input or has an IDOR/prompt-injection bypass, both tenants' data are exposed in a single query.

This pattern is the ChromaDB-equivalent of running multiple paying customers in one PostgreSQL database with no row-level security, an established anti-pattern in SaaS isolation.

### F2: Dev and Production Co-Located (CRITICAL)

`chroma_hmdev_textembedding-gecko` (HolaModa dev, 9,500 docs) shares the database with `holamoda_google` (HolaModa prod, 652,435 docs). `chroma_delta701dev_textembedding-gecko` (Delta701 dev, 64,658 docs) shares the database with `chroma_delta701_textembedding-gecko` (Delta701 prod, 65,324 docs).

Implications:

1. **Prod credentials in dev.** A developer testing against `*dev` collections may inadvertently embed real customer-facing copy that includes API keys, partner credentials, internal price lists, or pre-launch campaign copy.
2. **No environmental promotion gate.** Promoting from dev to prod usually involves a controlled deploy step that catches PII leaks; here a stray document written to `*dev` is, from an attacker's perspective, indistinguishable in posture from one written to prod, both are equally exposed.
3. **Test data with real user identifiers.** Common dev practice is "use anonymized prod data for testing", but that anonymization step is exactly what gets skipped under deadline pressure.

### F3: Aggregate Volume Is Operationally Significant (HIGH)

1.5M+ embeddings across seven collections, with the largest collection at 736K docs, indicates an active production workload at retail-product-catalog scale. For an apparel/fashion ecommerce operator, the embedded content typically includes:

- Product titles, descriptions, attributes
- Customer review content (potential PII)
- Image alt-text and SEO copy
- Internal product ontology / category tree
- Seller-facing listings (if marketplace), possibly seller PII

Without sample-document extraction past the first record per collection, the precise content distribution is not characterized, but the document counts force the conclusion that this is production-scale data.

### F4: Embedding Model Disclosed (LOW informational)

The `_textembedding-gecko` suffix names Google Cloud Vertex AI as the embedding provider. This is mostly informational, but it tells an attacker: (a) the operator is paying for Vertex AI API quotas, so quota-drain attacks (running query embeddings to force the operator to pay for compute) become economically meaningful, and (b) any leaked internal document showing a `GOOGLE_APPLICATION_CREDENTIALS` path is the next pivot to GCP-side compromise.

### F5: Root Cause: Default-Off Auth (CRITICAL)

ChromaDB 0.6.3 unauthenticated, port 8000 on the public internet, no firewall. Collection list, count, and document fetch all return 200 with no credentials.

---

## Remediation

### Immediate

```bash
chroma run --host 0.0.0.0 --port 8000 \
  --auth-provider chromadb.auth.token \
  --auth-credentials <strong-token>
```

Firewall port 8000 to the application backend only.

### Architectural

1. **Separate ChromaDB instances per tenant.** Two physical instances, two tokens. Application-layer routing selects which one a request hits based on authenticated tenant context.
2. **Separate dev from prod.** Two more instances: dev-isolated, prod-isolated. Dev credentials never in prod environment, and vice versa.
3. **Re-evaluate the `default_tenant/default_database` posture.** ChromaDB v2 supports application-defined tenants and databases; this instance has not used them, defeating the database's own multi-tenant primitive.

### Notification

If either operator (HolaModa, Delta701) determines that customer PII or seller-facing data was exposed, jurisdictional breach assessment applies. The HolaModa operator name appears Spanish-language; if either is a Mexican operator, LFPDPPP applies (Mexican federal data protection law); if Spanish, LOPDGDD/GDPR Article 33 (72-hour notification window).

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending, HolaModa appears to be a real operator brand; attribution + outreach warranted
- **Note:** Two-tenant exposure means coordinated disclosure to both operators and the platform vendor (DigitalOcean) for hosting context
