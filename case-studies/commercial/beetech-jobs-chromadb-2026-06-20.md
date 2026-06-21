---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Bee Tech Job Matching SaaS: Unauthenticated Read, Write, and Delete on a Multi-Tenant ChromaDB"
summary: "Bee Tech's AI job-matching platform exposed a single ChromaDB instance holding candidate CVs and job listings for 16 named client tenants, with no authentication. We confirmed unauthenticated read, write, and delete across all tenants. Names, emails, and phone numbers for roughly 2,500 job seekers were readable by anyone on the internet."
tags:
  - chromadb
  - vector-database
  - unauth
  - cwe-306
  - pii
  - recruitment
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Bee Tech (Vietnam)"
      - k: Sector
        v: "Recruitment / Job Matching SaaS"
      - k: Location
        v: "DigitalOcean"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
---

# Bee Tech Job Matching SaaS: Unauthenticated Read, Write, and Delete on a Multi-Tenant ChromaDB

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Bee Tech runs an AI-powered job-matching platform for clients in Vietnam. The platform stores candidate CVs and job listings in a single ChromaDB instance. That instance was reachable on the public internet with no authentication.

Anyone could list every collection, read candidate records across every tenant, and add or remove records. The data was not partitioned by access control. One request reads any tenant's candidate pool. We confirmed read, write, and delete, and we reversed the canary record we wrote.

The exposure covers 16 named client tenants. Roughly 2,500 candidate records carry real names, email addresses, and phone numbers.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8000 | ChromaDB 1.0.0 (v2 multi-tenant API) | RAG vector store: candidate CVs and job listings for 16 tenants | None |

The host is 188.166.247.146 on DigitalOcean. The v2 API exposes the default tenant and database path with no token check.

---

## What We Confirmed

**Read:** Listed all 35 collections. Pulled candidate records with name, email, phone, and summary fields, and job listings with title, company, department, industry, and description. Cross-tenant read confirmed: every tenant's collection is reachable regardless of tenant label.

**Write:** Inserted a marked canary record (`nuclide-canary-2026`) into the probe collection `probe-base-1780358607019010200` with a three-dimension zero vector. The add returned HTTP 201. The probe collection has no fixed dimension and accepts any vector, so the operator's embedding model is not required to inject.

**Delete:** Removed the canary. The delete returned `{"deleted": null}`. This is a ChromaDB 1.0.0 quirk. It returns null on a successful delete before the record flushes from the write-ahead log. A follow-up get for the canary ID returned an empty `ids` list. The record was gone.

Every test artifact we created we removed.

---

## Data Exposed

The store held 35 collections, roughly 4,236 records total. 22 of the 35 collections were PII-positive, with email addresses and personal names present.

| Collection Pattern | Collections | Records (est.) | Content Class |
|--------------------|-------------|----------------|---------------|
| candidate_embeddings_{tenant} | 16 | ~2,500 | Candidate CV data: name, title, email, phone, summary |
| job_embeddings_{tenant} | 17 | ~1,700 | Job listings: title, company, department, industry, description |
| probe-* | 3 | 0 | Internal test/probe collections |

The two largest collections were `candidate_embeddings_admin-beetechdev` at roughly 1,290 records and `candidate_embeddings_admin-ite` at roughly 785.

The collection naming convention exposed 16 client tenant identifiers directly. Two candidate collections held nursing-role matches. The client roster includes an insurance company and a biotech company. That adds healthcare-sector exposure to the candidate pool.

The records themselves are candidate CVs for real job seekers in Vietnam. We enumerated the schema, collection names, tenant identifiers, and counts. We did not exfiltrate the candidate dataset. The names and classes are the finding.

---

## Impact

Real name, email, phone, and professional-summary data is exposed for job seekers across 16 named client tenants. Anyone who submitted a CV through a Bee Tech client platform is affected. The data has no access control, so a single unauthenticated request reads any tenant's candidate pool. A breach at one client is a breach at all 16.

The platform places all tenant data in one ChromaDB instance with zero isolation. Collection names carry tenant identifiers, enumerable without authentication. The isolation failure is at the SaaS architecture level. It is not one misconfigured collection.

Write access to any `job_embeddings` collection allows injection of fraudulent job listings. A poisoned listing can redirect real job seekers to fake employers or harvest further PII through fraudulent application flows. Write access to `candidate_embeddings` allows injection of false CVs, which corrupts match quality for paying clients.

---

## Remediation

**Immediate (no code change required):** Firewall port 8000 to the internal network only.

**Short-term:** Enable ChromaDB's built-in token authentication. Add per-tenant access control so a request scoped to one tenant cannot read another's collections.

**Medium-term:** Add audit logging on writes and deletes. Place canary records in production collections to detect unauthorized writes. Run periodic monitoring for collection-count and record-count anomalies.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
