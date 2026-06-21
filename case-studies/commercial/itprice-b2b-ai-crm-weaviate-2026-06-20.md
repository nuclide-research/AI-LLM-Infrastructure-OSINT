---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "Router-switch.com B2B AI Sales CRM: Unauthenticated Read, Write, and Delete on an Exposed Weaviate Store"
summary: "An exposed Weaviate vector store at api.itprice.yejian.tech ran with no authentication on port 8080. We confirmed unauthenticated read, write, and delete against 839 AI sales-coaching conversation records tied to Router-switch.com, a Chinese B2B reseller of Huawei and Cisco network equipment. The store holds live operational CRM data, not test fixtures."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - b2b-crm-pii
  - network-equipment-reseller
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "Router-switch.com (api.itprice.yejian.tech)"
      - k: Sector
        v: "B2B Network Equipment Reseller / E-commerce"
      - k: Location
        v: "Alibaba Cloud (inferred, .yejian.tech)"
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

# Router-switch.com B2B AI Sales CRM: Unauthenticated Read, Write, and Delete on an Exposed Weaviate Store

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A Weaviate vector store at `api.itprice.yejian.tech` (47.238.237.94, port 8080) ran with no authentication. Anyone with a port scan could read, change, or delete the entire knowledge base behind an AI sales-coaching tool.

The operator is Router-switch.com, a Chinese B2B reseller of Huawei and Cisco network equipment. The store holds 839 AI coaching conversation logs. Each log is a live B2B sales session covering customer identities, deal values, order numbers, multi-year payment histories, and competitor analysis. This is operational CRM data, not test fixtures.

We confirmed full read, write, and delete. We reversed every change we made.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate v1.28.4 | AI sales-coaching vector store, 839-record conversation corpus | None |

The host responds to the Weaviate REST API with no token, no API key, and no network ACL in front of it.

---

## What We Confirmed

**Read:** Pulled the `Cmf_ai_data_message_history` class without credentials. 839 objects returned, HTTP 200.

**Write:** Inserted a marked canary object (UUID `a86e334e-277f-4b9b-a17f-bf5bc3cb542b`, history field `NUCLIDE-CANARY-2026-06-20`) via `POST /v1/objects`. Object created, HTTP 200.

**Delete:** Removed the canary via `DELETE /v1/objects/Cmf_ai_data_message_history/<uuid>`. HTTP 204. Re-queried the same UUID and got HTTP 404, confirming the object was gone.

Every test artifact we created we removed. No production record was touched.

---

## Data Exposed

The store held one class.

| Class | Objects | Content |
|-------|---------|---------|
| `Cmf_ai_data_message_history` | 839 | AI sales-coaching conversation logs |

Schema fields:

| Field | Type | Notes |
|-------|------|-------|
| `conversation_id` | integer | Links a session to a CRM customer record |
| `text` | string | Null in most records |
| `history` | string | Full Q&A between a salesperson and the AI coach |

The data classes present in the corpus include customer identities, active order numbers, deal status, multi-year per-customer payment summaries, and AI-generated deal-recovery scripts. An internal order-number convention is visible in the corpus. Records are in Chinese and represent live operational CRM activity, not staging or test data.

Names, classes, and counts are the finding. No personal records, customer rows, or financial values are reproduced here.

---

## Impact

**Confidentiality:** All 839 AI coaching sessions are readable without authentication. This is the operator's complete sales-coaching conversation corpus, including customer identities, deal values, order numbers, multi-year payment histories, and competitor analysis. Competitors, former employees, or any party running a port scan can read it.

**Integrity:** Write access allows injecting false coaching advice into the vector store. A salesperson querying the AI coach could be served instructions to offer unauthorized discounts, cite wrong product specifications, or route customer contacts to attacker-controlled channels. The AI retrieves from this store. Poisoned records become poisoned recommendations.

**Availability:** Delete access with no auth gate means the entire 839-object knowledge base can be wiped in a single loop. No backup mechanism is visible from the external surface. Loss of this store breaks the AI sales-coaching tool.

**Business intelligence:** The internal order-number convention, combined with customer IDs and deal context, is enough to support targeted social engineering against Router-switch.com customers and sales staff.

---

## Remediation

**Immediate:** Firewall port 8080 to the internal network only. No code change required.

**Short-term:** Enable Weaviate's API-key or OIDC authentication. Add audit logging on object writes and deletes.

**Medium-term:** Plant canary records in the production store to detect unauthorized writes. Run periodic retrieval-distribution monitoring to catch ranking anomalies from injected content.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
