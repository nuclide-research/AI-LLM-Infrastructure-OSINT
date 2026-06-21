---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Brazilian Electrical Retail AI Platform: Unauthenticated Read, Write, and Delete on 86K Product Records"
summary: "A multi-tenant Weaviate instance serving AI product search for 11 Brazilian electrical supply retailers ran with no authentication. Read, write, and delete were all confirmed across 13 classes holding roughly 86,012 product records with live retail pricing. The write path allows price manipulation that feeds the AI recommender, and a schema delete wipes a retailer's entire catalog."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - retail-pricing
  - retail
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Brazilian electrical retail AI platform (multi-tenant)"
      - k: Sector
        v: "Retail / Electrical Supply"
      - k: Location
        v: "São Paulo, BR (Google Cloud Platform)"
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

# Brazilian Electrical Retail AI Platform: Unauthenticated Read, Write, and Delete on 86K Product Records

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A Weaviate instance on Google Cloud in São Paulo, Brazil, served AI product search and recommendations for Brazilian electrical supply and hardware retailers. It ran with no authentication. Each retail client had a dedicated Weaviate class holding their full product catalog with retail pricing.

Anyone on the internet could read every SKU and price across all clients, overwrite any record, or delete a retailer's entire catalog. We confirmed read, write, and delete. We reversed the one record we wrote.

The write path is the sharp edge. Records carry an AI recommendation score that drives what the platform surfaces to shoppers. An attacker who can rewrite prices and scores controls what the recommender promotes.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.33.2 | Multi-tenant vector store, 13 classes, ~86,012 records | None |
| 50051 | gRPC | Weaviate gRPC, nmap open, weavscan inconclusive | None observed |

Host: 34.39.219.41. RDNS 41.219.39.34.bc.googleusercontent.com. Google Cloud Platform, São Paulo. The server loaded 37 AI provider integration modules. API keys are client-supplied per request, not stored in the server environment.

---

## What We Confirmed

**Read:** Pulled full catalogs without credentials. HTTP 200. The GraphQL `Get` interface returned every record with pricing, category, and brand for every class.

**Write:** Unauthenticated PUT to `/v1/objects/{class}/{uuid}` overwrote a record. HTTP 200, STATUS SUCCESS.

**Delete:** Removed the test object. HTTP 204.

Canary: `1869c010-be1e-4280-a705-c62e4de967a0` was written to Inventory9, confirmed present, deleted with HTTP 204, and verify returned 404. The single artifact we created we removed.

Schema delete (`DELETE /v1/schema/{class}`) was documented as the destructive primitive but was not exercised against client data. The read, write, and delete primitives were proven on a single canary object only.

---

## Data Exposed

Thirteen Weaviate classes (Inventory1 through Inventory14, with no Inventory2). Eleven held active retailer catalogs. Two were provisioned but empty.

| Class | Client ID | Records |
|-------|-----------|---------|
| Inventory1 | 1 | 7,201 |
| Inventory3 | 3 | 7,200 |
| Inventory4 | 4 | 7,201 |
| Inventory5 | 5 | 7,200 |
| Inventory6 | 6 | 0 (empty) |
| Inventory7 | 7 | 0 (empty) |
| Inventory8 | 8 | 4,704 |
| Inventory9 | 9 | 16,904 |
| Inventory10 | 10 | 7,200 |
| Inventory11 | 11 | 7,200 |
| Inventory12 | 12 | 7,200 |
| Inventory13 | 13 | 7,001 |
| Inventory14 | 14 | 7,001 |

Total active clients: 11. Total records: roughly 86,012.

Per-record schema, by field name: internal product ID, SKU code, full product name in Portuguese, normalized search name, brand, category, unit of measure, retail price in BRL, alternative search names, an AI recommendation score, an inventory batch number, the client store name, and the client ID.

The data class is commercial retail catalog and live pricing. Each class names its owning retailer and ID. No personal data, no credentials, and no biometric data were present in the schema. The sensitivity is competitive: every SKU, price, and category for 11 named retailers is readable by any competitor with no account.

---

## Impact

**Read, competitor pricing intelligence.** About 86,012 products with live retail prices across 11 Brazilian electrical supply stores. A competitor can pull every SKU, price, and category from every client on the platform in minutes. Real-time pricing intelligence with no account and no trace beyond a read.

**Write, price and recommender manipulation.** Unauthenticated PUT overwrites any record. An attacker can set competitor prices to near zero so their products surface as cheapest in semantic search, push high-margin products out of recommendations by driving the AI score negative, or inject phantom SKUs with attacker-controlled names. The recommendation score directly shapes what shoppers see, so manipulation maps straight to retail sales outcomes.

**Delete, platform disruption.** A schema delete destroys a retailer's entire AI search catalog. For Inventory9 at 16,904 products, a shopper searching for a circuit breaker or an LED fixture gets zero results until the platform re-indexes from source. The inventory batch field suggests re-ingestion is manual or scheduled, so recovery time is unknown.

---

## Remediation

**Immediate:** Firewall ports 8080 and 50051 to the internal network or the application backend only. No public exposure.

**Short-term:** Enable Weaviate's API-key or OIDC authentication and require it on the REST and GraphQL interfaces and on gRPC. Treat write and schema endpoints as privileged.

**Medium-term:** Add canary records and periodic schema-and-count monitoring to detect unauthorized writes or deletes. Log object mutations. Per-tenant isolation so one client's compromise does not expose the whole platform.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
