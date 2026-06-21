---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "SheriaLens: Unauthenticated Read, Write, and Delete on a Kenyan Legal AI Corpus"
summary: "SheriaLens, a Kenyan legal AI platform, exposed its Weaviate vector store to the internet with no authentication. We confirmed read, write, and delete on the full 56,782-record corpus of Kenyan court judgments, parliamentary acts, bills, and Hansard records. The write primitive lets an attacker inject false legal precedent scored as a maximally reliable source, surfacing to anyone querying the legal assistant."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - legal-corpus
  - legal-tech
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "SheriaLens"
      - k: Sector
        v: "Legal AI / Legal Tech"
      - k: Location
        v: "Germany (Contabo VPS)"
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

# SheriaLens: Unauthenticated Read, Write, and Delete on a Kenyan Legal AI Corpus

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

SheriaLens is a Kenyan legal AI research and information platform. Its Weaviate vector store sat on the public internet with no authentication. Anyone could read, change, or erase the entire legal corpus that powers the assistant.

The store held 56,782 chunks of Kenyan legal material: court judgments, parliamentary acts, bills, Hansard debate records, and human rights documentation. Each chunk carries an operator-assigned reliability score. That score is the lever. A false ruling written with a top reliability score reads, to any retrieval pipeline, exactly like a real Kenya Law judgment.

We confirmed read, write, and delete. We reversed the canary we wrote.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.28.4 | Vector store -- 56,782-record Kenyan legal corpus | None |
| 50051 | gRPC | Weaviate gRPC endpoint | Closed |

Only port 8080 was open on this host. Weaviate was the sole external surface. No vectorizer module was loaded, and no public web frontend was found on the IP.

Host: 84.247.188.44, a Contabo VPS in Germany (vmi3153195.contaboserver.net). Node name `sl-data-weaviate`.

---

## What We Confirmed

**Read:** Pulled records from the `SheriaLensChunk` class with full chunk text and no credentials. HTTP 200.

**Write:** Inserted a marked canary object into `SheriaLensChunk`. The batch write returned STATUS=SUCCESS, HTTP 200. Canary ID `1626b5b6-2aea-4b17-b134-f21368be9d86`.

**Delete:** Removed the canary object. HTTP 204. Re-queried the ID, which returned 404.

Every test artifact we created we removed. Canary written, confirmed, deleted 204, verified 404.

---

## Data Exposed

One class, 56,782 records.

| Class | Records | Content |
|-------|---------|---------|
| SheriaLensChunk | 56,782 | Kenyan legal corpus, chunked |

The schema carries ten fields: `doc_id`, `source`, `doc_type`, `title`, `url`, `chunk_text`, `chunk_index`, `section_hint`, `published_date`, and `source_reliability`. The `source_reliability` field is an operator-assigned credibility score from 0.0 to 1.0. Kenya Law judgments carry 0.95.

Document-type breakdown from a sample of the first 500 records:

| doc_type | Count | Description |
|----------|-------|-------------|
| act | 260 | Kenyan parliamentary acts |
| hansard | 63 | Parliamentary debate records |
| humanitarian_dataset | 50 | Humanitarian and development data |
| bill | 50 | Parliamentary bills |
| judgment | 30 | Kenya Law court judgments |
| news_article | 29 | Kenyan news outlets |
| human_rights | 10 | Human rights documentation |
| health | 2 | Health-related documents |
| transparency | 2 | Transparency and governance documents |
| treasury | 1 | Treasury documents |
| telecom_statistics | 1 | Telecom data |
| policing_oversight | 1 | Police oversight records |
| constitution | 1 | Kenyan constitution |

The corpus is public legal material drawn from Kenya Law (new.kenyalaw.org), parliamentary sources, and Kenyan news outlets. It is not personal data, but it is a curated, reliability-scored dataset, and the integrity of that curation is the asset.

---

## Impact

**Read:** Full corpus exfiltration. 56,782 chunks of curated, reliability-scored Kenyan legal material, pullable in roughly 568 paginated requests with no account. A competitor gets the entire retrieval corpus for free.

**Write:** Legal guidance poisoning. The `source_reliability` field ranks credibility, and legitimate judgments score 0.95. An injected record written with `doc_type: judgment` and `source_reliability: 0.95` is indistinguishable from a real court ruling in any RAG retrieval pipeline. A legal AI assistant that surfaces false precedent to lawyers or to citizens researching their rights is a direct harm pathway.

**Delete:** Platform destruction. A single schema delete drops the `SheriaLensChunk` class and all 56,782 records along with the HNSW vectors. `lastSnapshotIndex: 0` means there is no internal recovery point. The operator would have to re-crawl and re-ingest every source.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. Weaviate is the sole external service on this host, so closing it removes the entire surface.

**Short-term:** Enable Weaviate authentication. Set `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false` and configure API-key or OIDC auth. Restrict write and schema-delete operations to service accounts.

**Medium-term:** Take and store Weaviate snapshots so a delete is recoverable. Place canary records in the corpus to detect unauthorized writes. Monitor retrieval-distribution and reliability-score changes to catch injected high-credibility records.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
