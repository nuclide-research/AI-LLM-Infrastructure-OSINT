---
type: case-study
severity: HIGH
date: 2026-06-20
title: "Salt at Amelia Island / Ritz-Carlton: Unauthenticated Read/Write/Delete on a Restaurant Chatbot RAG Store"
summary: "A Weaviate vector store backing a restaurant chatbot ran on a public Azure IP with no authentication. We confirmed unauthenticated read, write, and delete on the single class. The deployment is test/staging holding 7 records scraped from the public restaurant website, so no non-public data was exposed, but the open-by-default pattern carries directly to production."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - public-web-scrape
  - hospitality
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Salt at Amelia Island (The Ritz-Carlton, Amelia Island, FL)"
      - k: Sector
        v: "Hospitality / Restaurant"
      - k: Location
        v: "Microsoft Azure"
      - k: Severity
        v: HIGH
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

# Salt at Amelia Island / Ritz-Carlton: Unauthenticated Read/Write/Delete on a Restaurant Chatbot RAG Store

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A Weaviate vector store ran on a public Microsoft Azure IP with no authentication. Anyone on the internet could read, change, or erase the class that backs a restaurant chatbot RAG pipeline.

The deployment is a test or staging instance. It holds 7 records scraped from the public Salt at Amelia Island restaurant website, so no non-public data is exposed today. The significance is the pattern. The same open-by-default Weaviate deployment, on an Azure IP, is wired to a Ritz-Carlton hospitality property. If real reservation data, customer details, or private dining inquiries are ingested next, the same open store exposes them.

We confirmed full read, write, and delete on the class. We reversed every change we made.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.28.16 | RAG vector database backing a restaurant chatbot | None |

The store sits on Azure IP 20.51.140.169. It does not ask who is calling.

---

## What We Confirmed

**Read:** Pulled the class contents without credentials. HTTP 200.

**Write:** Inserted a marked canary object. It persisted and returned a UUID. HTTP 200.

**Delete:** Removed the canary object. HTTP 204.

The canary write returned a UUID and was immediately confirmed deleted. The access pattern is consistent with full read, write, and delete on the class. Every test artifact we created we removed.

---

## Data Exposed

One class, 7 records.

| Class | Records | Content |
|-------|---------|---------|
| DocumentContent | 7 | saltameliaisland.com web scrape, chunked |

The class schema describes a generic web-scrape ingestion: `blob_url`, `file_name`, `content_type`, `file_type`, `text`, `chunk_index`, `total_chunks`, `container_id`, `language`, `created_at`, `updated_at`, `uploaded_by`, `tags`, `page_number`.

Two fields mark this as a test deployment. `container_id` is `test`, and `uploaded_by` is empty, so no user attribution is recorded. The 7 records are a single URL scrape of the public restaurant site, chunked into positions 0 through 6.

The content classes are all public marketing material already on the restaurant website: menus, private dining package descriptions, chef bio, team, and OpenTable integration references. No personal data, no reservations, no customer rows. The operator attribution rests on the scraped source URL (`https://www.saltameliaisland.com/`) and on named public events in the content. The Azure hosting is consistent with Ritz-Carlton enterprise cloud infrastructure.

---

## Impact

Today the store holds only public restaurant content, so direct data exposure is limited. The finding is a pattern indicator. The Weaviate instance has no authentication, sits on a public Azure IP, and is connected to a hospitality property.

If the operator promotes this deployment to production with real reservation data, customer details, or private dining inquiries, the severity escalates to CRITICAL on the spot. The vulnerability is already present. The data sensitivity depends on what gets ingested next.

The `container_id: "test"` value implies a production container also exists. An OpenTable reservation integration feeding a concierge chatbot would put customer name, email, and dining preferences into a store with this same open posture.

Write and delete access also means the chatbot's knowledge base can be tampered with. An attacker can insert or remove records that the chatbot reads when answering a guest, which maps to OWASP LLM04 data poisoning.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. Remove the public Azure exposure.

**Short-term:** Enable Weaviate's API-key or OIDC authentication before any production data is ingested. Confirm the production container, if it exists, is not exposed the same way.

**Medium-term:** Add canary records to production vector stores to detect unauthorized writes. Monitor the retrieval pipeline for ranking anomalies that would signal a poisoned record.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
