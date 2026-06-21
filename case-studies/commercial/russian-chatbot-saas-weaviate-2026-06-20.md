---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Russian Chatbot SaaS: Unauthenticated Read, Write, and Delete Across a Multi-Tenant Weaviate Fleet"
summary: "A multi-tenant AI chatbot platform serving Russian Apple device resellers ran five Weaviate nodes with no authentication. Every customer's knowledge base was readable, writable, and deletable by anyone on the internet. Confirmed read, write, and delete with a reversed canary across the fleet."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - customer-chatbot-pii
  - retail-saas
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Unknown Russian chatbot SaaS platform"
      - k: Sector
        v: "Retail SaaS / AI Customer Chatbot"
      - k: Location
        v: "Russia (Moscow-area resellers)"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# Russian Chatbot SaaS: Unauthenticated Read, Write, and Delete Across a Multi-Tenant Weaviate Fleet

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A multi-tenant AI chatbot SaaS platform ran five Weaviate nodes with no authentication on any of them. The platform serves Russian consumer retail, specifically Apple device resellers operating on the Avito marketplace. Every node exposed every customer's chatbot knowledge base to anyone on the internet.

The platform's entire knowledge base storage is open, not one customer's chatbot. Tenant IDs, knowledge base IDs, and all stored Q&A content are readable without credentials. One endpoint exposes all customers at once.

We confirmed read, write, and delete. We wrote a marked canary, deleted it, and verified the deletion. Every test artifact we created we removed.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.30.0 / 1.37.2 | Multi-tenant chatbot knowledge base store | None |

Five nodes total. Four nodes ran Weaviate 1.30.0; one node (185.252.232.86) ran 1.37.2. All five answered on port 8080 with no authentication.

```
Cluster A (replicated -- same class IDs and record counts):
  132.243.117.114  Weaviate 1.30.0  82 records
  88.218.123.199   Weaviate 1.30.0  82 records
  185.252.232.86   Weaviate 1.37.2  82 records  (newest version)
  89.150.34.22     Weaviate 1.30.0  82 records

Cluster B (separate tenant set -- earlier CUID timestamps):
  95.81.96.54      Weaviate 1.30.0  61 records
```

---

## What We Confirmed

**Read (all five nodes):** Pulled every class and every object on all five nodes without credentials. HTTP 200.

**Write (132.243.117.114):** Inserted a marked canary object into class `KB_cmo47hc5y00b7pe57jtx86osk`. Batch write returned STATUS=SUCCESS, HTTP 200.

**Delete (132.243.117.114):** Removed the canary object. HTTP 204.

**Verify:** Re-queried the deleted object ID. HTTP 404, confirming the delete took effect.

Canary ID: `06447648-58ee-426a-8120-47a2a48cf93b`, written to `KB_cmo47hc5y00b7pe57jtx86osk` on 132.243.117.114, deleted 204, verify 404.

Read was exercised across all five nodes. Write and delete were exercised on one node (132.243.117.114) and reversed.

---

## Data Exposed

The data class is customer chatbot knowledge base content: Russian-language Q&A pairs that train and ground each reseller's support chatbot, plus per-tenant identifiers. The records describe iPhone resale operations on Avito, Moscow delivery and self-pickup, installment financing, and device verification.

The schema across all `KB_` classes:

```
text              text     -- chatbot Q&A pair (Russian)
tenantId          text     -- SaaS customer identifier (CUID)
knowledgeBaseId   text     -- knowledge base identifier (CUID)
chunkIndex        int      -- chunk position
metadata          text     -- JSON: charCount, wordCount, semanticUnit, positions
```

CUID-format IDs (cmm.../cmo...) point to a Node.js/Prisma ORM generation pattern. Multiple distinct tenant IDs across the nodes confirm a SaaS serving multiple separate Russian small businesses.

### Cluster A -- 4 nodes, 82 records, 4 tenant knowledge bases

| Class | Records |
|-------|---------|
| KB_cmo47hc5y00b7pe57jtx86osk | 42 |
| KB_cmnehab4y00suvz57jp31cizc | 16 |
| KB_cmol9i34t0ofdkv571f0rzntu | 15 |
| KB_cmnoljvi01s3qfj575jfp1jwu | 9 |

### Cluster B -- 1 node, 61 records, 3 active tenant knowledge bases

| Class | Records |
|-------|---------|
| KB_cmmdmg9i606akz6p1kw2okbdb | 44 |
| KB_cmmer3yrj0ah6z6p177gvqo7n | 16 |
| KB_cmm9kjeyw0007z6p1xdmlh5b6 | 1 |
| KB_cmmn442oo07g6k4p1bt5c3ux7 | 0 (empty) |

Counts, class names, and tenant identifiers are the finding. No customer record content is reproduced here.

---

## Impact

**Cross-tenant data exposure.** The entire platform's knowledge base storage is unprotected. Every customer's chatbot training data is readable by anyone. Tenant IDs, knowledge base IDs, and all Q&A content are accessible without credentials. One Weaviate endpoint exposes all customers simultaneously.

**Customer chatbot poisoning.** Write access to any class poisons the chatbot for that tenant's customers. A poisoned chatbot can redirect customers in that market. It can hand out fraudulent payment instructions, false return or warranty procedures, or attacker-controlled contact details. That exploits the retailer's own customer relationships.

**Platform-wide wipe.** Delete access across both clusters means all customers can lose their chatbot knowledge bases at once. Recovery requires the SaaS operator to re-ingest all customer content.

---

## Remediation

**Immediate:** Firewall port 8080 on all five nodes to the internal network only. No public client needs direct database access.

**Short-term:** Enable Weaviate's API-key or OIDC authentication and enforce it on every node. Verify that replicated Cluster A nodes share one hardened config so a single node is not left open.

**Medium-term:** Add per-write audit logging. Plant canary objects in production classes to detect unauthorized writes. Monitor retrieval and write patterns for cross-tenant anomalies.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
