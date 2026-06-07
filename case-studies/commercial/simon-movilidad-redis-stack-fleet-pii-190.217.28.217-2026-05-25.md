---
type: case-study
title: "Simón Movilidad / Finanzauto — Full Picture: Traccar 6.12.2, 28,323 Open GPS Records, CAS Default Config"
date: 2026-05-25
updated: 2026-05-26
severity: CRITICAL
sector: commercial
tags: [Redis-Stack, RediSearch, Traccar, fleet-tracking, PII, Colombia, LACNIC, CAS-SSO, Finanzauto, Alfresco]
summary: "Simón Movilidad runs Traccar 6.12.2 (GPS fleet tracking) with Redis Stack as the live device state store. The Redis instance at qa.simonmovilidad.com is open without auth: 28,323 GPS device records, keyed by IMEI, each containing plate, name, phone, email. Tenant: Finanzauto S.A. BIC (Colombian vehicle financing). Finanzauto's admision subdomain runs Apereo CAS SSO with the default-config HTML comment in production."
---

# Simón Movilidad / Finanzauto — Full Picture

**Date:** 2026-05-25 | **Updated:** 2026-05-26  
**Target:** 190.217.28.217 (qa.simonmovilidad.com)  
**ASN:** LACNIC region, Colombia  
**Operator:** Quantum Data Processing de Colombia S.A.S. (trade name: Simón Movilidad) — simonmovilidad.com  
**Data owner / tenant:** Finanzauto S.A. BIC — finanzauto.com.co  
**Severity:** CRITICAL

---

## Findings

### F1 — Redis Stack Open Without Authentication (CRITICAL)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5882, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Port 6379 answers without credentials:

```
TCP → RESP PING → +PONG (no AUTH)
```

DBSIZE: 28,323. Redis 7.4.1, Linux 5.15.0-179-generic. Uptime 4 days. db0 only — single database, 1 key with TTL (avg 7.8 days), rest persistent.

Keys are raw IMEI strings. Type: ReJSON-RL (Redis JSON module). FT indexes confirm Redis Stack vector search layer, not plain cache.

### F2 — 28,323 GPS Device Records With PII (CRITICAL)

Each key is a GPS tracker IMEI. Each value is a JSON document:

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

Fields confirmed: full name, email, phone, license plate, GPS tracker IMEI, vehicle manufacturer. The company field reads Finanzauto.

The IMEI is the GPS tracker's hardware identifier. Plate, IMEI, name, phone, and email are in the same record. 28,323 records. This is the complete live device state cache for the QA environment.

### F3 — Traccar 6.12.2 Stack Trace via /health (LOW)

GET /health on port 443 returns a full Java stack trace:

```
org.traccar.web.WebServer.lambda$initClientProxy$0
org.eclipse.jetty.ee10.servlet.FilterHolder.doFilter
```

Application is **Traccar 6.12.2** — open-source GPS tracking platform. Jetty embedded server. Google Guice DI. Jersey JAX-RS.

### F4 — Traccar /api/server Public Endpoint (LOW)

```json
{
  "version": "6.12.2",
  "registration": false,
  "readonly": false,
  "deviceReadonly": false,
  "geocoderEnabled": true,
  "openIdEnabled": false
}
```

No auth. Returns version, feature flags, and map config. `/api/devices`, `/api/positions`, `/api/users` all return 401 — Traccar API layer enforces auth. The Redis instance does not.

### F5 — Finanzauto CAS SSO Default-Config Comment in Production (HIGH — ADJACENT)

`admision.finanzauto.com.co` (8.242.212.102) runs Apereo CAS. The login page HTML contains:

```html
<!-- - Felicidades por iniciar CAS correctamente! El método de autentifiación
     por defecto es el nombre de usuario igual a la contraseña : adelante, pruébelo. -->
```

"Congratulations on starting CAS correctly! The default authentication method is username equals password: go ahead, try it."

This is the Apereo CAS quickstart/overlay demo comment. Its presence confirms the instance was stood up from the default template. Whether the default credential handler is still active is unconfirmed — that would require a credential test against a Finanzauto production system, which is out of scope here.

Additional signal: jsessionid appears in the URL path (`/cas/login;jsessionid=60AE926FF84EAC736F3106CDFF31CFA7`). URL-embedded session IDs are a separate misconfiguration — susceptible to session fixation and logged in browser history, proxy logs, and referrer headers.

Title: "ATC – Autenticación Única." This is Finanzauto's single sign-on for their internal systems, including admissions/loan intake.

---

## Attribution

**Operator: Quantum Data Processing de Colombia S.A.S.**  
NIT: 900237820 | Carrera 106 15A-25, Bogotá | qdatacolombia.com  
Trade name: Simón Movilidad | simonmovilidad.com  
DNS: Google Cloud, GoDaddy registrar, Google Workspace MX, Masiv SMS

**Data owner: Finanzauto S.A. BIC**  
NIT: 860028601 | Founded 1970 | Grupo SEISSA  
Colombia's largest non-banking vehicle financing entity. 572 employees. 150 service points. IDB Invest + US DFC backed. Supervised by Superintendencia Financiera de Colombia.

**Relationship:** The Android package for the Simón Movilidad app is `ve.org.finanzauto` — Finanzauto is the commissioning entity. Both share Google Cloud DNS and Masiv transactional email infrastructure.

VisorGraph cert pivot: `qa.simonmovilidad.com` Let's Encrypt cert. CSP leaks `*.finanzauto.info`, `*.finanzauto.com.co`, `wss://localhost:3000/scada/`.

**Subdomains confirmed:**

| Subdomain | IP | Notes |
|---|---|---|
| qa.simonmovilidad.com | 190.217.28.217 | This host. Redis open. |
| dev.simonmovilidad.com | 190.217.28.218 | Sequential IP. Redis AUTH required. |
| www.simonmovilidad.com | 54.166.83.247 | AWS EC2. Production web. |
| visor.finanzauto.com.co | 8.242.215.220 | Alfresco document search SPA. Self-signed cert. |
| admision.finanzauto.com.co | 8.242.212.102 | CAS SSO (F5 above). Sectigo wildcard. |
| uno.finanzauto.com.co | 66.22.63.111 | Google Sites / OAuth |

**Disclosure contacts:**
- Platform operator: servicioalcliente@simonmovilidad.com (no security@ published)
- Data owner DPO: oficialprotecciondatos@finanzauto.com.co (verified from Finanzauto's own data protection policy PDF)
- Finanzauto DPO phone: 749 9000 ext. 338

---

## Stack Map

| Host | Port | Service | Version | Auth |
|---|---|---|---|---|
| 190.217.28.217 | 443 | nginx → Traccar | 6.12.2 | Auth required (Traccar API) |
| 190.217.28.217 | 6379 | Redis Stack | 7.4.1 | **NONE** |
| 190.217.28.218 | 6379 | Redis Stack | unknown | Auth required |
| 8.242.212.102 | 443 | Apereo CAS SSO | unknown | Default-config comment present |
| 8.242.215.220 | 443 | Alfresco SPA | unknown | TLS (surface only) |

---

## Thesis Placement

Traccar stores live device states in Redis Stack. The application layer (Traccar API) enforces auth on all user-facing endpoints. The data layer (Redis) does not. This is the pattern: a mature application with working auth, sitting on top of an unauthenticated data store. The data store is the exposure.

The dev node (190.217.28.218) has Redis gated. QA was left open. Both are adjacent IPs in the same /24. One deployment step separates a protected instance from an open one.

**See also:** [Redis Stack / RedisInsight Population Survey (2026-05-25)](redis-stack-redisinsight-population-survey-2026-05-25.md) · [Insight #60 — Redis Stack FT._LIST as Vector-Tier Enumeration Primitive](../../methodology/insight-60-redis-stack-ft-list-vector-tier-enumeration.md)
