---
type: case-study
severity: HIGH
date: 2026-06-20
title: "Ikigai: Unauthenticated Read, No-Vector Write, and Delete on a German Job-Platform RAG Store"
summary: "Ikigai, a German AI job-search and employer-branding platform, exposed a Weaviate vector store with no authentication. We confirmed full read of 9,513 records across three classes, including 27 named ZEISS employee profiles, plus no-vector write and class delete. Vectorized writes and semantic search were blocked by a client-supplied OpenAI key."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - pii
  - employment
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Ikigai (German AI job platform)"
      - k: Sector
        v: "Recruitment / Employer Branding"
      - k: Location
        v: "Netherlands (Google Cloud Platform)"
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

# Ikigai: Unauthenticated Read, No-Vector Write, and Delete on a German Job-Platform RAG Store

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Ikigai is a German AI-powered job-search and employer-branding platform. Its Weaviate vector store sat on a public Google Cloud host with no authentication on any endpoint.

Anyone on the internet could read the full job corpus, the named-employee career-story records, and the schema. We confirmed read of 9,513 records across three classes, no-vector write into the live store, and class-level delete. Vectorized writes and semantic nearText search were the only blocked operations, and only because the OpenAI key is supplied per request by the client application rather than stored on the server.

The records include 27 EmployerBranding stories that name real Carl Zeiss AG employees by first name with role and biography. That is GDPR-relevant personal data exposed through an unauthenticated endpoint.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.31.9 | RAG vector store -- 9,513-record job and employer-branding corpus | None |

Host: 34.1.233.6, RDNS 6.233.1.34.bc.googleusercontent.com, Google Cloud Platform, Netherlands. The vectorizer module is `text2vec-openai` configured in the client-key pattern. The OpenAI key is not in the server environment (`OPENAI_APIKEY` unset), so the server itself cannot vectorize.

---

## What We Confirmed

**Read:** Full. All 9,513 records across all three classes were accessible with no credentials, every field readable. No rate limiting observed.

**Write, vectorized:** Blocked. Requires an `X-OpenAI-Api-Key` header. Server error: `API Key: no api key found neither in request header: X-Openai-Api-Key nor in environment variable under OPENAI_APIKEY`.

**Write, no vector:** Confirmed. An object written without the key is created and persists in the database, unindexed. It does not appear in semantic search but does appear in BM25 keyword search.

**Delete:** Confirmed. Object delete returned 204. Two canary objects were created, confirmed present, then deleted with a 204, and the delete was verified by re-query returning 404.

**Semantic search (nearText):** Blocked. Same client-key requirement as vectorized write.

Topology at time of test: `node: main_node`, `status=HEALTHY`, version 1.31.9, `operationalMode: ReadWrite`, `lastSnapshotIndex: 0`. No snapshot means no recovery point.

Every test artifact we created we removed.

---

## Data Exposed

Three classes, roughly 9,513 records.

| Class | Records | Content class |
|-------|---------|---------------|
| Job | 9,361 | German job listings: title, full description, location, geolocation, company identifier |
| JobAzure | 125 | Azure-sourced job listings |
| EmployerBranding | 27 | Named-employee career stories, all under customer_id zeiss |

**Job class.** German job listings carrying full descriptions, location strings, ISO country codes, latitude and longitude, a remote-work flag, and LLM-generated normalized titles and task summaries. Client company identifiers (customer_id) tie listings to named employers. Sampled client identifiers include an aggregator feed, ams-OSRAM, Carl Zeiss AG, MediaMarkt, Cosmo Consult, and the Schwarz Group.

**JobAzure class.** 125 Azure-sourced listings under three Munich-based client identifiers that remain unattributed.

**EmployerBranding class.** 27 records, all under customer_id zeiss. These are career stories that identify real Carl Zeiss AG employees by first name, with role title, project detail, and full biographical narrative. Name plus employment role plus employer identifies a natural person, which makes this GDPR-relevant personal data. Operator attribution is supported by an Azure OpenAI resource name in the module config and by the ZEISS-tagged customer_id values.

Per the NuClide restraint ethic, no personal record values, employee identities beyond the class description, or biographical contents are published here. The class names, record counts, and data classes are the finding.

---

## Impact

**Read, job corpus.** 9,361 German job listings with full descriptions, geolocation, and company attribution are exfiltrable in bulk with no rate limiting. That is competitor intelligence: which companies are hiring, for which roles, in which locations.

**Read, named employee profiles.** 27 EmployerBranding stories expose identifiable Carl Zeiss AG employees through an unauthenticated endpoint. This is GDPR-relevant personal data that the operator and the named employer have not authorized for public, unauthenticated exposure.

**Write, phantom job injection.** A no-vector write appears in BM25 keyword search but not semantic search. An attacker can inject fake listings under a legitimate customer_id such as zeiss to phish candidates toward attacker-controlled contact channels. Injected objects persist until deleted.

**Delete, platform wipe.** Three schema deletes destroy the entire data layer. With `lastSnapshotIndex: 0` there is no recovery point, so the corpus would have to be re-indexed from source.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. The store should not be reachable from the public internet.

**Short-term:** Enable Weaviate authentication (API-key or OIDC) and set authorization so that read, write, and delete all require a credential. Restrict schema-delete to an admin role.

**Medium-term:** Configure snapshot backups so a recovery point exists. Add canary records to detect unauthorized writes, and monitor for unexpected schema or object deletion.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
