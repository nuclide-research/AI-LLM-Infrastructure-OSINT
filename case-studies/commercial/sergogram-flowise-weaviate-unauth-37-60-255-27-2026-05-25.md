---
type: case-study
title: "SerGoGram Flowise + Weaviate: IT Credentials from German Blood Donation Organization in Open Vector Store"
date: 2026-05-25
severity: CRITICAL
sector: commercial
tags: [Flowise, Weaviate, vector-database, credentials-in-vector-store, healthcare-adjacent, multi-tenant, Contabo, nginx]
summary: "A Flowise instance at 37.60.255.27 exposes an unauthenticated Weaviate vector store containing internal IT documentation from a German blood donation organization. The corpus includes plaintext server credentials, internal IP addresses, server names, BitLocker PINs, and blood donation operational data. A second tenant's customer support documents occupy the same instance."
---

# SerGoGram Flowise + Weaviate: IT Credentials from German Blood Donation Organization in Open Vector Store

**Date:** 2026-05-25
**Host:** 37.60.255.27
**Subdomain:** gpt.sergogram.com
**Cloud:** Contabo GmbH, Nuremberg, Germany
**App:** Flowise (LLM app builder) + Weaviate 1.23.5
**Severity:** CRITICAL

---

## What Was Found

### F1 — Weaviate Unauthenticated: 1,171 Objects Including Plaintext Credentials (CRITICAL)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854, T5868, T5882
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Weaviate 1.23.5 at 37.60.255.27 holds internal IT documents from a German blood donation organization. No authentication. Any request returns them.

```
GET http://37.60.255.27:8080/v1/collections → 32 collections, no credentials required
```

Thirty-two collections. 1,171 objects. The vector store is the document backend for a Flowise LLM app builder. Collections are named `Test1` through `Test30`, `Test119`, and `Test120`. Flowise creates a new Weaviate collection for each vector store node. Numbers up to 120 with 32 remaining indicate at least 120 test iterations; the rest were deleted.

Object schema per collection:

```json
{
  "doc1": "<document chunk text>",
  "source": "blob",
  "blobType": "<type>",
  "loc_lines_from": <integer>,
  "loc_lines_to": <integer>
}
```

### F2 — Tenant 1: German Blood Donation Organization Internal IT Documents (CRITICAL)

Collections `Test3` through `Test118` contain internal IT documentation from an organization at `blutspende.net` (mail server `NoSpamProxy@blutspende`). Locations named in the corpus include Frankfurt/FFM, Karlsruhe/KAR, and Baden-Baden/BB.

Confirmed content from document chunks:

**Plaintext server credentials:**
```
IH-DBSERVER\operator  Pw: operator
```

**Internal server inventory:**
- `IH-DBSERVER`, `IH-DBBACKUP12`
- `KAR-IMPSRV-02`, `KAR-IMPSRV-03`
- `BAD-DA-02`, `BAD-DA-07`

**Internal IP addresses:**
- `172.23.111.65`, `172.23.111.70`
- `10.1.11.187`, `10.1.11.191`, `10.20.41.70`

**Operational data and runbook content:**
- BitLocker PIN convention: `1910FFMx` (site-coded)
- Domain join procedures for `Blutspende.net`
- Baramundi MDM configuration
- roXtra document management system references
- IH 1000 blood typing/cross-matching analyzers (Bio-Rad), vendor support contacts
- Blood donation unit numbering tables (Entnahmenummer ranges for MOB-DV series across Frankfurt and Baden-Baden donor locations)
- Email security policy (NoSpamProxy, confidentiality classification tiers)
- Network segmentation details (DMZ placement of lab devices)
- References to VNC passwords stored in a linked KB document

The corpus is internal IT runbooks, SOPs, and lab equipment procedures. The operator ingested this material as a knowledge base for an LLM chatbot. The Weaviate instance holding it has no authentication.

### F3 — Tenant 2: UK Toll Road Service Customer Support Documents (HIGH)

Collections `Test1` and `Test2` contain customer support FAQ documents for `emovis-tag.co.uk`, a UK electronic toll road tag subscription service. 250 objects in `Test1`, 289 in `Test2`. The two corpora have no relationship to each other. They share the same unauthenticated Weaviate instance.

### F4 — Flowise Unauthenticated on Ports 3000 and 443 (HIGH)

Flowise runs unauthenticated on port 3000 (direct) and port 443 (nginx reverse proxy). The full admin UI is open without credentials. Flowise stores API keys in its credentials store. `text2vec-openai` with `model: ada-002` is configured. An OpenAI API key is in the environment.

```
http://37.60.255.27:3000/     → Flowise admin UI, no auth
https://gpt.sergogram.com/    → same, via nginx
```

### F5 — Port and Version Disclosure (LOW)

Shodan confirms: ports 22, 80, 443, 3000.

- nginx/1.18.0 (Ubuntu 20.04 era)
- Weaviate 1.23.5 (version-disclosed unauthenticated via `/v1/meta`)
- OpenSSH 8.2p1
- Flowise build date: 2024-08-12 (Last-Modified header)

Shodan tags this host `eol-product` and lists CVE-2025-23419, CVE-2021-3618, CVE-2021-23017, CVE-2023-44487 against the nginx version.

---

## Stack

nginx (reverse proxy) → Flowise (LLM app builder) → Weaviate 1.23.5 (vector store). Contabo GmbH, Nuremberg, Germany. gpt.sergogram.com. Port 80: nginx default page (no vhost). Port 443: nginx → Flowise admin. Port 3000: Flowise direct. Port 8080: Weaviate, HTTP only, no TLS.

---

## Failure Mode

Flowise has no authentication enabled by default. The operator deployed it without enabling the `FLOWISE_USERNAME` and `FLOWISE_PASSWORD` environment variables. Weaviate's unauthenticated mode is its default. Both services ran open after deployment.

The operator ingested client documents as Flowise knowledge base vectors. The documents included internal IT runbooks. The plaintext credential was part of a runbook. The runbook was ingested as-is. Flowise chunked it and embedded it verbatim.

The Flowise binary carries a build date of 2024-08-12. The stack has run since at least August 2024.

---

## Operator Attribution

Main domain `sergogram.com` serves a WordPress coffee-shop demo template on 217.160.0.5 (IONOS SE, Germany). WHOIS privacy-protected. No registrant name or contact email exposed. WordPress locale is `de_DE`. The subdomain `gpt.sergogram.com` points to 37.60.255.27 (Contabo Nuremberg). Let's Encrypt cert issued August 2024. The WordPress locale is `de_DE` and both hosting providers are German. The multi-tenant corpus suggests a client-facing service. Operator identity is not confirmed.

No GitHub profile, no Telegram channel, no company name surfaced.
