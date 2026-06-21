---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "B2Finance BeATrix: Unauthenticated Read, Write, and Delete on the SAP B1 Client Document RAG"
summary: "B2Finance's internal AI document intelligence platform, BeATrix, backed its RAG agent with a Weaviate store left open to the internet. We confirmed unauthenticated read, write, and delete on roughly 3,141 records, including 129 confidential SAP Business One integration specifications for around 40 Brazilian client companies."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - confidential-business-data
  - sap-consulting
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "B2Finance (b2finance.com.br)"
      - k: Sector
        v: "SAP Business One Consulting / BPO"
      - k: Location
        v: "Santa Clara, CA (DigitalOcean)"
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
        v: "LLM02 Sensitive Information Disclosure"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# B2Finance BeATrix: Unauthenticated Read, Write, and Delete on the SAP B1 Client Document RAG

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

B2Finance is a Brazilian SAP Business One consulting and BPO firm. Their internal AI platform, BeATrix, ingests client SAP B1 implementation specifications from SharePoint, embeds them in a Weaviate vector store, and serves a RAG agent that consultants query about client integrations.

The Django app at port 8000 requires authentication on every endpoint. The Weaviate store at port 8080 required none. Anyone on the internet could read, change, or erase the entire knowledge base behind that RAG agent.

We confirmed full read, write, and delete. We reversed the one record we wrote and the one we deleted.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.27.4 | RAG vector store, roughly 3,141 records | None |
| 8000 | BeATrix Django app (Gunicorn) | RAG agent and document API | Required |
| 5432 | PostgreSQL | Django state | Required |

Port 8080 held the data. Port 8000 read that data and answered consultant queries. Only port 8080 failed to ask who was calling.

---

## What We Confirmed

**Read:** Pulled the schema and listed all document records without credentials. Two classes, roughly 3,141 records total.

**Write:** Inserted one marked canary record into the Document class. The Weaviate batch endpoint returned STATUS=SUCCESS.

**Delete:** Removed the canary object. The store returned HTTP 204.

Canary ID `21bf39a6-c754-43d4-a1a3-6fa567ec3e59` was written to the Document class, confirmed present, then deleted. Schema-level deletion was not tested. Topology reported `operationalMode: ReadWrite` and `lastSnapshotIndex: 0`, meaning no internal recovery point.

---

## Data Exposed

The store held two classes.

| Class | Records | Content |
|-------|---------|---------|
| Document | 348 | Client SAP B1 project specification documents, 129 unique files |
| Sapb1dbdocs | 2,793 | SAP Business One SDK 10.0 database table reference |

The Document class chunks 129 internal SAP B1 integration specifications for around 40 B2Finance client companies. Each chunk carries the source filename, disk path, full document text, an LLM-extracted keyword array, and document and chunk identifiers.

The data class is confidential business data. The specifications contain custom API endpoint schemas and field mappings, webhook URLs and integration credentials, CNPJ Brazilian business registration numbers, personnel names and project responsibilities, and internal process automation logic used in production integrations. Documents date from 2023 to 2025, with some 2026 material. The content is current production specification, not archived material.

Client document names reference major Brazilian and multinational firms across private equity, banking, pharmaceuticals, and medical devices. The Sapb1dbdocs class is generic SAP documentation and not client specific.

Per NuClide restraint practice, individual client records, named personnel, CNPJ values, and credentials are not reproduced here. The class names, file counts, record counts, and data classes are the finding.

---

## Impact

**Read:** 129 internal SAP B1 integration specifications for around 40 client companies are readable by anyone on the internet. They expose custom field configurations, integration credentials, webhook endpoints, and business registration data tied to live production systems.

**Write:** BeATrix serves a RAG agent at `/api/agent/query/` that consultants use to answer questions about client integrations. Weaviate is the knowledge base behind it. Writing a poisoned record into Weaviate causes the RAG agent to return attacker-controlled answers to authenticated consultants. No BeATrix credentials and no BeATrix auth bypass are required. The attacker writes to the open store and waits for a consultant to query. The result is wrong SAP field mappings or attacker-directed steps delivered to a consultant working a live client implementation.

**Delete:** With no recovery snapshot, a schema-level delete would destroy the class definition, all Document chunks, and all vector embeddings in one call. The RAG agent would return empty or wrong answers until the corpus was re-ingested from the SharePoint source.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. No code change required.

**Short-term:** Enable Weaviate's built-in API key or OIDC authentication so the store rejects anonymous calls the way the Django app already does.

**Medium-term:** Add canary records to the production store to detect unauthorized writes. Monitor retrieval distribution to catch ranking anomalies that signal poisoning. Configure snapshots so a delete is recoverable.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
