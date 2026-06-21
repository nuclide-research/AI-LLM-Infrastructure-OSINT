---
type: case-study
severity: HIGH
date: 2026-06-20
title: "Nalu Services: Unauthenticated Read on the AI Support Chatbot Knowledge Base (Weaviate)"
summary: "Nalu Services ran the Weaviate vector store behind ai-support.naluservices.com with no authentication. The full chatbot knowledge base, 10 classes and roughly 767 objects, was readable over unauthenticated GraphQL. Read access was confirmed. Write and delete were not exercised."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - commercial-content
  - it-services
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Nalu Services (naluservices.com)"
      - k: Sector
        v: "IT Services / Digital Marketing"
      - k: Location
        v: "Vultr"
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
        v: "LLM02 Sensitive Information Disclosure"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# Nalu Services: Unauthenticated Read on the AI Support Chatbot Knowledge Base (Weaviate)

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Nalu Services runs a customer-facing AI support chatbot at ai-support.naluservices.com. The Weaviate vector store behind that chatbot was reachable on the public internet with no authentication. Anyone could read the full indexed corpus that powers the chatbot over unauthenticated GraphQL.

The store held 10 classes and roughly 767 objects. Two classes carry the Nalu brand directly: NalumomentsAI and Naluendorse. The other eight have randomized 5-character names. Name randomization is not access control. All 10 classes read without credentials.

We confirmed read only. Write and delete were not exercised.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.28.4 | RAG vector database for the AI support chatbot | None |

The host is 149.28.54.81, hosted on Vultr. The domain ai-support.naluservices.com resolves to this IP. Weaviate exposed `/v1/meta`, `/v1/schema`, and the `/v1/graphql` query endpoint with no token on any of them.

---

## What We Confirmed

**Read:** Pulled the schema and class objects without credentials.

- `GET /v1/meta` returned 200 with version info (Weaviate 1.28.4).
- `GET /v1/schema` returned 200 with all 10 class schemas.
- `POST /v1/graphql` returned 200 with records for NalumomentsAI, Naluendorse, ZDUXL, and the other classes queried.

**Write:** Not exercised. The `POST /v1/objects` endpoint carries no authentication layer, so write access is highly probable, but we did not exercise it. No canary UUID was injected. This is a restraint posture: access was not exercised past read.

**Delete:** Not exercised. `DELETE /v1/objects/{uuid}` was not called.

---

## Data Exposed

The store held 10 classes and roughly 767 total objects. Eight of the 10 class names are randomized 5-character strings. The two named classes reference the Nalu brand.

| Class | Properties | Content class |
|-------|-----------|---------------|
| NalumomentsAI | source, text, url, blobType, title | Scraped naluservices.com pages powering the AI chatbot |
| Naluendorse | source, text | Nalu Endorse product FAQ |
| XTCGS | fileName, text | Unknown source document(s) |
| FLJEC | fileName, text | Unknown source document(s) |
| ZDUXL | source, blobType, title, url, text, loc_lines_from, loc_lines_to | Web-scraped content with line-range location metadata |
| AEDII | title, url, text | Web content |
| IJRBB | title, url, text | Web content |
| JXQAQ | title, url, text | Web content |
| FPRRG | title, url, text | Web content |
| XUSIE | fileName, text | Document source(s) |

NalumomentsAI holds scraped service pages, an accessibility widget script, contact information, Facebook Pixel code, and third-party tracking scripts. If any of that scraped JS inlines API keys or pixel IDs, those values are accessible through the exposed corpus.

Naluendorse holds the product FAQ for the Nalu Endorse business listing service, covering endorsement link creation, business card generation, subscription upgrades, and listing claiming.

ZDUXL carries loc_lines_from and loc_lines_to fields. Line-level location metadata suggests it may index source code or structured documents rather than plain web pages. The full content of the eight obfuscated classes was not scrolled.

The data class is commercial content: chatbot knowledge base, product documentation, and scraped web content. No personal records were enumerated. No individual data was pulled.

---

## Impact

**Chatbot knowledge base exfiltration.** Everything that powers ai-support.naluservices.com is readable. Any actor can pull the full indexed corpus, service descriptions, product documentation, and internal FAQ content, without authentication. The eight obfuscated class names suggest the operator tried to obscure the structure. The names do not restrict access.

**Product IP.** The full Nalu Endorse FAQ is indexed and readable. A competitor can extract product documentation and feature language with a single query.

**Analytics credential risk.** NalumomentsAI records include scraped JS containing Facebook Pixel code and third-party tracking scripts. If any of those scripts inline API keys or pixel IDs, those credentials sit in the exposed corpus.

**Chatbot poisoning.** The store shows no write authentication. An actor who exercises write access can inject false records into NalumomentsAI. Poisoned records would surface as AI chatbot responses to Nalu's customers. The operator's own support interface would deliver misinformation, phishing links, or social engineering content. Write was not exercised in this assessment.

---

## Remediation

**Immediate:** Firewall port 8080 to internal network only. Do not expose Weaviate to the public internet.

**Short-term:** Enable Weaviate's built-in API key or OIDC authentication. Disable anonymous access. Do not rely on randomized class names for access control. Rotate any analytics or tracking credentials that may be present in scraped JS records.

**Medium-term:** Add canary records to the production vector store to detect unauthorized writes. Monitor retrieval distribution for ranking anomalies that would signal poisoned records.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
