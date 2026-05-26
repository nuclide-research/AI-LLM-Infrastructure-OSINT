---
type: case-study
title: "Simón Movilidad — 28,323 Vehicle Fleet Records in an Unauthenticated Redis Stack"
date: 2026-05-25
severity: CRITICAL
sector: commercial
tags: [Redis-Stack, RediSearch, fleet-tracking, PII, Colombia, LACNIC, vector-DB]
summary: "A Colombian vehicle fleet tracking platform runs Redis Stack in its QA environment with no authentication. 28,323 records contain full names, emails, phone numbers, vehicle license plates, and GPS tracker IMEI codes. The client is Finanzauto, a Colombian vehicle financing company."
---

# Simón Movilidad — 28,323 Vehicle Fleet Records in an Unauthenticated Redis Stack

**Date:** 2026-05-25  
**Target:** 190.217.28.217  
**ASN:** LACNIC region, Colombia  
**Operator:** Simón Movilidad — simonmovilidad.com  
**Severity:** CRITICAL

---

## What Was Found

### F1 — Redis Stack Open Without Authentication (CRITICAL)

Port 6379 answers without credentials:

```
TCP connect → RESP PING (*1\r\n$4\r\nPING\r\n) → +PONG\r\n
```

No `AUTH` command required. DBSIZE: 28,323.

FT._LIST returns three active RediSearch indexes:

```
1) "idx:vehicle"
2) "idx:user"
3) "idx:company"
```

All three respond without credentials. FT.INFO idx:vehicle returns the schema: `plate`, `imei`, `user`, `user_id`, `manufacturer`, `company`, `phone`, `email`.

### F2 — 28,323 Fleet Tracking Records With PII (CRITICAL)

Sample record from `fleet:vehicle:*` key namespace:

```json
{
  "plate": "OYL-123",
  "imei": "864...",
  "user": "Carlos [REDACTED]",
  "user_id": 4821,
  "manufacturer": "Hyundai",
  "company": "Finanzauto",
  "phone": "31[REDACTED]",
  "email": "[REDACTED]@gmail.com"
}
```

Fields confirmed: full name, email address, phone number, license plate, GPS tracker IMEI, and vehicle manufacturer. The company field reads Finanzauto.

The IMEI is the GPS tracker's globally unique hardware identifier. Plate, IMEI, name, phone, and email are in the same record.

---

## Attribution

VisorGraph cert-pivot on 190.217.28.217:

```
TLS cert CN: qa.simonmovilidad.com
Issuer: Let's Encrypt (R13)
SAN: [qa.simonmovilidad.com]
```

CSP header confirms two additional operators:

```
connect-src: https://*.finanzauto.info https://*.finanzauto.com.co
             https://www.simonmovilidad.com
             wss://localhost:3000/scada/
```

- **Simón Movilidad** (simonmovilidad.com) — vehicle fleet tracking SaaS. The `qa` subdomain is the QA environment.
- **Finanzauto** (finanzauto.com.co) — Colombian vehicle financing company. The company field in sampled records reads Finanzauto.

This is a QA environment. The data is live.

---

## Stack Map

| Port | Service | Auth |
|---|---|---|
| 443 | nginx/1.28.3 — Simon Movilidad web app (qa subdomain) | HTTPS (prod frontend) |
| 6379 | Redis Stack — fleet tracking database | NONE |

---

## Thesis Placement

This is a non-AI Redis Stack deployment. The operator adopted Redis Stack for its RediSearch vector capabilities. The data is GPS fleet tracking, not LLM context. The auth state is identical to plain Redis. The distribution ships with authentication off.

FT._LIST returned three active indexes. Redis Stack is the search layer, not a cache. Any actor can run `FT.SEARCH idx:vehicle * LIMIT 0 28323` and get all 28,323 records.

**See also:** [Redis Stack / RedisInsight Population Survey (2026-05-25)](redis-stack-redisinsight-population-survey-2026-05-25.md) · [Insight #60 — Redis Stack FT._LIST as Vector-Tier Enumeration Primitive](../../methodology/insight-60-redis-stack-ft-list-vector-tier-enumeration.md)
