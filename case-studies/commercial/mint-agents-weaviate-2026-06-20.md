---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Mint Agents: Unauthenticated Read, Write, and Delete on a Vietnamese Legal AI Knowledge Base"
summary: "Mint Agents, a Vietnamese-language legal RAG chatbot, ran its Weaviate vector store with no authentication. We confirmed anonymous read, write, and delete on the full legal corpus, then reversed every change. The store holds about 1,432 records of active Vietnamese legislation that the chatbot serves to citizens as legal guidance."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - legal-rag
  - government-legal
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Mint Agents"
      - k: Sector
        v: "Legal AI / Vietnamese Legislation RAG"
      - k: Location
        v: "Vietnam (no RDNS)"
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

# Mint Agents: Unauthenticated Read, Write, and Delete on a Vietnamese Legal AI Knowledge Base

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Mint Agents runs a Vietnamese-language legal RAG chatbot. A user asks a question about Vietnamese law, the backend retrieves matching text from a Weaviate vector store, and the chatbot answers. The Weaviate store has no authentication. Anyone on the internet can read, change, or delete the legal corpus that the chatbot answers from.

We confirmed full read, write, and delete against the store. We reversed every change we made.

The corpus is active Vietnamese legislation, including the Land Law (31/2024/QH15) and the Public Asset Management Law (15/2017/QH14), both issued by the Office of the National Assembly. A user querying the chatbot has no way to tell tampered legal text from real text.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.30.3 | RAG vector database -- legal knowledge base | None |
| 80 | Chainlit frontend | Mint Agents chatbot UI ("giao dien Chainlit native-first") | -- |
| 8000 | uvicorn backend | RAG backend, 404 on root | -- |

Port 8080 stored the legal corpus and asked nothing of the caller. The Chainlit frontend on port 80 reads that corpus and serves answers to citizens.

---

## What We Confirmed

**Read:** Pulled the full legal corpus without credentials. HTTP 200 across all classes.

**Write:** Inserted a marked canary into `LegalChunkV2` via the batch objects endpoint. The server returned STATUS=SUCCESS with HTTP 200.

**Delete:** Removed the canary object. The server returned HTTP 204. Re-querying the ID returned 404.

Canary ID `5e47e536-37ba-487f-bed6-f455c5e36550` was written, confirmed, deleted (204), and verified gone (404). Every test artifact we created we removed.

The node reported `status=HEALTHY`, `version=1.30.3`, `lastSnapshotIndex: 0`. There is no recovery point.

---

## Data Exposed

The store holds five classes, about 1,432 records total.

| Class | Records | Content |
|-------|---------|---------|
| LegalChunk | 431 | Vietnamese law article chunks, 67-property schema |
| LegalUnit | 566 | Vietnamese law unit nodes, 59 properties |
| LegalChunkV2 | 432 | Simplified chunk format, 20 properties |
| LegalDocument | 3 | Document metadata records |
| Legal | 0 | Empty |

Two laws are indexed:

| Document ID | Title | Number | Issued |
|-------------|-------|--------|--------|
| luat-31-2024-qh15 | LUAT DAT DAI (Land Law) | 31/2024/QH15 | 2024-01-18 (eff. 2024-08-01) |
| luat-15-2017-qh14 | Public Asset Management Law | 15/2017/QH14 | 2017-06-21 |

Both laws are issued by Van phong Quoc hoi, the Office of the National Assembly of Vietnam.

The `LegalChunk` schema carries 67 properties: document identifier, title, official number, document type and status, issuer, issued date, article and section identifiers, full article content, formal citations, hierarchical breadcrumbs, chapter and section metadata, a JSON navigation path, and a JSON relations field for cross-references to other laws. The data class is curated, structured public legislation with full text and complete structural metadata. No personal or private records were present.

---

## Impact

**Read:** Full text of indexed Vietnamese legislation with complete structural metadata, including chapter, section, and article hierarchy, cross-references, and official citations. The operator built a curated, structured legal corpus that anyone can read.

**Write:** The Chainlit frontend on port 80 is a direct interface for citizens asking about Vietnamese law. Injecting false articles into the Weaviate corpus makes the chatbot return attacker-controlled text as authoritative legal guidance. The Land Law (31/2024/QH15) affects millions of landowners. A user asking about land transfer obligations could receive poisoned output that reads as official law.

**Delete:** A five-class schema wipe destroys all 1,432 records and the vector indexes. The chatbot then returns empty answers on every legal query. With `lastSnapshotIndex: 0`, recovery requires a full re-ingest from source.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 to the internal network only. The Weaviate store has no reason to be internet-reachable.

**Short-term:** Enable Weaviate's built-in API-key or OIDC authentication. Add audit logging on writes and schema changes.

**Medium-term:** Take and store regular Weaviate snapshots so a recovery point exists. Place canary records in the production store to detect unauthorized writes, and monitor retrieval distributions for ranking anomalies that signal corpus tampering.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
