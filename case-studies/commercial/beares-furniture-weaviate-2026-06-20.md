---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Bears Furniture: Unauthenticated Read, Write, and Delete on a Retail AI Search Index"
summary: "Bears Online, a South African furniture and bedding chain, ran the Weaviate vector store behind its AI product search wide open. Anyone could read the full ~986-object catalog and blog corpus, inject fake product records into the live search index, or delete the store. Each record also carried a BigQuery ID, a pivot toward the GCP data warehouse behind the retail operation."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - retail-catalog
  - rag-poisoning
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Bears Online (bearesonline.co.za)"
      - k: Sector
        v: "Furniture and Bedding Retail"
      - k: Location
        v: "Google Cloud Platform (us-central1)"
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

# Bears Furniture: Unauthenticated Read, Write, and Delete on a Retail AI Search Index

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

Bears Online is a South African furniture and bedding retailer trading as Bears and Real Beds. The Weaviate vector database that powers its AI product search ran on the public internet with no authentication. Anyone could read the full product catalog and blog corpus, write fake records straight into the live search index, or delete the store.

Each product and blog record also carried a BigQuery record ID. That field is a thread back to the GCP data warehouse behind the retail operation.

We confirmed read, write, and delete. We wrote one marked canary and removed it.

---

## Attack Surface

One host. One open port. No authentication.

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.30.0 | Vector store behind the AI product search and recommendation system | None |

The host is 35.224.252.183 on Google Cloud Platform, us-central1.

---

## Data Exposed

Three classes, roughly 986 objects.

| Class | Records | Content |
|-------|---------|---------|
| Product | ~700 | Furniture and bedding SKUs: name, brand, SKU, inventory quantity, price, descriptions, FAQ, product-page URL |
| BlogPost | ~200 | Editorial articles with full body text and SEO metadata |
| BlogAttribute | ~80 | Product attributes linked by product ID |

Operator attribution comes from the data itself. Product brand fields read Bears and Real Beds. Product URLs point to bearesonline.co.za. Every Product and BlogPost record carries a `bq_id` field, a BigQuery record identifier consistent with the GCP hosting.

We read the schema and confirmed record counts. We did not exfiltrate the catalog.

---

## What We Confirmed

**Read:** Schema and all three classes returned over plain HTTP. Roughly 700 products, 200 blog posts, 80 attributes, all reachable without credentials.

**Write:** A marked canary record was accepted into the Product class and returned 200.

**Delete:** The canary was removed with a 204 and confirmed gone with a 404 on re-fetch.

Canary UUID `b887ad5a-4e9e-473d-b99e-1ed0876ecc31`. Written, confirmed, deleted, verified. Every change reversed.

---

## Impact

**Catalog exfiltration:** The full product catalog with SKU, brand, inventory state, and direct product URLs is readable by any competitor. The complete blog and content corpus, the operator's full SEO and content strategy, comes with it.

**AI search poisoning:** Write access injects arbitrary records into the live Weaviate index. The AI search and recommendation system serving bearesonline.co.za shoppers would surface poisoned records: false pricing, fabricated specifications, fake FAQ content, served directly to retail customers with no authentication required.

**BigQuery pivot:** Each record carries a `bq_id` linking to a GCP BigQuery warehouse. If that identifier exposes the GCP project and the dataset IAM is misconfigured for public read, the vector exposure becomes a path into the full data warehouse behind the retail operation.

**Destruction:** A single delete call removes records from the search index with no recovery point observed.

---

## Remediation

**Immediate (no code change):** Firewall port 8080 to the internal network only.

**Short-term:** Enable Weaviate API-key authentication. Add request logging.

**Medium-term:** Audit the BigQuery dataset IAM referenced by `bq_id` for public access. Add canary records and retrieval-distribution monitoring to detect unauthorized writes.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
