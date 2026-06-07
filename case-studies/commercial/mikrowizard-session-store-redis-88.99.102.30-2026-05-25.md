---
type: case-study
title: "MikroWizard — Unauthenticated Redis Session Store, 2,940 Active MikroTik Router Management Sessions"
date: 2026-05-25
updated: 2026-05-26
severity: MEDIUM
sector: commercial
tags: [Redis-Stack, MikroWizard, MikroTik, session-store, session-fixation, router-management, Hetzner, DE, AS24940]
summary: "MikroWizard router management platform at 88.99.102.30 (Hetzner Frankfurt) runs Redis 7.4.7 on port 6379 with no authentication. DBSIZE: 2,940 keys, all named mikrowizard::UUID. Session TTL: 29 days. Any actor with network access can read all active session identifiers directly from the data layer. The application layer at port 80 serves the MikroWizard Angular UI."
---

# MikroWizard — Unauthenticated Redis Session Store

**Date:** 2026-05-25 | **Updated:** 2026-05-26  
**Target:** 88.99.102.30  
**PTR:** static.30.102.99.88.clients.your-server.de  
**ASN:** AS24940 Hetzner Online GmbH, FSN1-DC13, Frankfurt, Germany  
**Severity:** MEDIUM

---

## Findings

### F1 — Redis Stack Open Without Authentication (MEDIUM)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K7003

<!-- ksat-tag:auto-generated:end -->

Port 6379 answers without credentials:

```
TCP → RESP PING → +PONG (no AUTH)
```

DBSIZE: 2,940. Redis 7.4.7, Linux 5.15.0-119-generic. Uptime 189 days. No FT indexes (FT._LIST returns empty array). Plain string keys only.

All 2,940 keys follow one pattern:

```
mikrowizard::<UUID>
```

Example: `mikrowizard::bfb91d99-9682-4391-aded-8d861d2ad0cd`

Key type: `string`. TTL on sampled key: 2,505,700 seconds (29 days). This is the MikroWizard session store. Each key is a live, authenticated session token for a MikroTik router management user.

The survey seed counted ~500 keys. Current measurement is 2,940. The count difference reflects measurement at different points in time — the store is live and active.

### F2 — MikroWizard Web UI Surface (LOW)

Port 80 serves the MikroWizard Angular application:

```
Server: nginx/1.27.0
Title: MikroWizard | Router Managment
Meta description: MikroWizard | Mange Your mikrotik routers
Meta keywords: mikrowizard,mikrotik,router
Angular: 16.2 (CoreUI v4.5.27)
Last-Modified: Thu, 02 Jan 2025 20:53:04 GMT
```

The web UI is the management front-end for MikroTik routers. No version string for MikroWizard itself disclosed in response headers or visible HTML. Port 443 did not respond (connection refused).

---

## Impact

A session identifier in `mikrowizard::UUID` format is the complete credential to impersonate an authenticated MikroWizard session. MikroWizard manages MikroTik routers — network devices used in ISPs, enterprises, and large campus networks. With a valid session token, an actor can:

1. Read session tokens directly from Redis without any credential
2. Present the token to the web application layer
3. Operate as the authenticated user — viewing managed routers, running commands, or modifying configurations

The 29-day TTL means tokens stay live. 2,940 active sessions represents a persistent, high-value target surface.

This is the same structural pattern seen across the survey population: application-layer auth is intact; the data layer behind it is open. The Redis instance and the web UI are co-located on the same host. The boundary between them is one unauthenticated TCP port.

No PII class was confirmed in this investigation. Session token values were not read. The data class of session content is unknown — it may be an opaque token or it may encode user identity fields. That determination is left for the operator.

---

## Attribution

**PTR record:** `static.30.102.99.88.clients.your-server.de` — generic Hetzner reverse DNS. No hostname configured.

**Netname:** HETZNER-fsn1-dc13 (Hetzner Falkenstein datacenter, Frankfurt region)

**Adjacent hosts:**
- 88.99.102.25 → mail.splinfra.com (shared /24, separate operator)
- 88.99.102.31 → backbone0.1bad0.net (adjacent IP, separate operator)

No domain name is associated with this host. No cert history found via crt.sh. The deployment uses a bare IP address for the web UI and Redis.

MikroWizard is a commercially available MikroTik router management platform. The operator deploying it on this infrastructure is not identified from passive signals alone.

---

## Stack Map

| Host | Port | Service | Version | Auth |
|---|---|---|---|---|
| 88.99.102.30 | 80 | nginx → MikroWizard UI | nginx/1.27.0, Angular 16.2 | Login required (web layer) |
| 88.99.102.30 | 443 | — | — | Connection refused |
| 88.99.102.30 | 6379 | Redis Stack | 7.4.7 | **NONE** |
| 88.99.102.30 | 22 | OpenSSH | — | Auth required |

---

## Thesis Placement

The MikroWizard web application enforces authentication at the UI layer. The Redis session store backing it does not. An actor who can reach port 6379 — which is publicly reachable — can read every active session identifier without presenting a password. The attack does not require a vulnerability in MikroWizard itself. It requires the ability to open a TCP connection.

The 189-day uptime confirms this has been the configuration since at least November 2025.

**See also:** [Redis Stack / RedisInsight Population Survey (2026-05-25)](redis-stack-redisinsight-population-survey-2026-05-25.md)
