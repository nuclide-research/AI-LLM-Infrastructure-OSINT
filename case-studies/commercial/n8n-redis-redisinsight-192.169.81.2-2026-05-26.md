---
type: case-study
title: "Evolution API WhatsApp Broker — RedisInsight Open, 117 Keys Including WhatsApp Session State and Lead Phone Numbers"
date: 2026-05-26
severity: HIGH
sector: commercial
tags: [evolution-api, whatsapp, redis, redisinsight, n8n, workflow-automation, brazil, bmaconnect, phone-PII, session-state, queue-store]
summary: "Brazilian WhatsApp automation SaaS bmaconnect.com.br runs RedisInsight 2.42.0 with no authentication on port 8001, exposing full read/write access to Redis 7.4.7 (n8n-redis-1). 117 keys confirmed: 7 Evolution API WhatsApp session hashes (208KB to 1.16MB), 108 Brazilian phone number conversation queues across 5 named operator clients, and an n8n scheduling key with unresolved lead-number expression. Evolution API 2.3.7 on port 8080 enforces auth on instance management. n8n 1.122.5 (development mode) proxied via ia.bmaconnect.com.br. Second server at 179.190.63.39 for api./zion-teste. subdomains. 90 unique Brazilian phone numbers exposed in key names."
---

# Evolution API WhatsApp Broker — RedisInsight Open, 117 Keys Including WhatsApp Session State and Lead Phone Numbers

**Date:** 2026-05-26
**Target:** 192.169.81.2
**Hostname:** gestao.esamg.org.br (PTR)
**Operator Domain:** bmaconnect.com.br (TLS cert, Let's Encrypt, valid through Jul 2026)
**ASN:** Limestone Networks, Inc., 192.169.80.0/20
**Severity:** HIGH

---

## What Was Found

### F1 — RedisInsight 2.42.0 Open, No Authentication (HIGH)

There was no authentication. RedisInsight ran on port 8001. The `/api/databases` endpoint returned a pre-configured connection to an internal Redis instance:

```
GET http://192.169.81.2:8001/api/databases
→ HTTP 200
{
  "name": "n8n-redis-1:6379",
  "host": "n8n-redis-1",
  "port": 6379,
  "connectionType": "STANDALONE",
  "version": "7.4.7",
  "lastConnection": "2026-02-27T15:17:07.207Z"
}
```

RedisInsight version: 2.42.0. Build type: `DOCKER_ON_PREMISE`. Installed 2025-09-23.

The database name is `n8n-redis-1`. Redis 6379 is not externally reachable. It sits on the Docker internal network. RedisInsight is the proxy. The `/api/databases/:id/keys` endpoint accepts POST requests with SCAN parameters and returns key names, types, TTLs, and sizes. No token required.

Redis itself is firewalled. No port-level exploit was needed. RedisInsight handed over the keyspace via its REST API.

### F2 — 117 Redis Keys: WhatsApp Session State, Lead Phone Numbers, n8n Templates (HIGH)

Full SCAN of the keyspace returned 117 keys. All persistent (TTL -1). Four classes:

**Class A: Evolution API session hashes — 7 keys**

```
evolution:instance:2008475a-f5a1-4af7-9738-ac877b3e2f70  hash  1,168,552 bytes
evolution:instance:aeb884b7-1137-4f32-bcf0-379237e7b2fd  hash    846,032 bytes
evolution:instance:f3628223-66c1-4f79-91d7-c05067efee95  hash    416,144 bytes
evolution:instance:03cd08ef-87d7-41c8-bb04-a1cf09d4fafc  hash    433,744 bytes
evolution:instance:2d3c8150-1b99-428b-8f28-12fb3e6e01dc  hash    308,216 bytes
evolution:instance:b87ba01f-b2a7-4cab-a2f3-57d37cd7ac2c  hash    228,040 bytes
evolution:instance:6e332598-a0e5-4ea5-972d-17d79e38f87c  hash    208,648 bytes
```

Seven Evolution API WhatsApp instances. Each hash holds one connected WhatsApp Business session. Sizes range from 208KB to 1.16MB per instance. Based on the Evolution API codebase, these hashes store full session state: HMAC signing material, Noise Protocol keys, WhatsApp Web encryption keys, registration IDs, and message history references. Hash contents were not read. The key names alone confirm active sessions are present. Reading any hash gives the full cryptographic material to re-register that WhatsApp identity on separate infrastructure.

**Class B: Phone number conversation queues — 108 keys (lists)**

Key pattern: `<instanceName>-<recipientNumber>-<senderNumber>[-<sequenceID>]`

Examples:
```
BuffetPaoli1330-5511993786464-5511966192279    list   8,280 bytes
CPSEVA-1616-5511993786464-5511986973980        list  25,056 bytes
5511993786464                                  list  72,136 bytes
5511987241050                                  list   8,248 bytes
558182291159                                   list   6,200 bytes
```

All numbers carry the Brazil country code (+55). Instance names include `BuffetPaoli`, `CPSEVA`, and bare phone numbers. The list on key `5511993786464` is 72KB. One key carries `???????????????` as the sender segment, a masked or unresolved identifier. Values were not read. Key names alone expose every recipient phone number the system has contacted.

**Class C: n8n scheduling template key — 1 key (hash)**

```
scheduling:{{ $('Variaveis').item.json.lead_numero }}:calendar_data  hash  1,760 bytes
```

An n8n expression template was written to Redis before evaluation. The expression `$('Variaveis').item.json.lead_numero` references an n8n node named "Variaveis" and pulls a field called `lead_numero`. When n8n evaluates correctly, the key becomes `scheduling:5511993786464:calendar_data`. The literal key is a workflow bug: the expression ran without context. The key name reveals the data schema. This is a CRM or sales automation pipeline keying scheduling state by lead phone number.

**Class D: minha_chave — 1 key (string, 72 bytes)**

"My key" in Portuguese. A test or setup artifact. Value not read.

### F3 — Evolution API 2.3.7 Running Alongside RedisInsight (MEDIUM)

Evolution API is the open-source WhatsApp Business API. It ran on port 8080:

```
GET http://192.169.81.2:8080/
→ HTTP 200
{
  "message": "Welcome to the Evolution API, it is working!",
  "version": "2.3.7",
  "clientName": "evolution_exchange",
  "manager": "http://192.169.81.2:8080/manager",
  "documentation": "https://doc.evolution-api.com",
  "whatsappWebVersion": "2.3000.1040115662"
}
```

The welcome endpoint requires no credentials. The instance management API (`/instance/fetchInstances`) returned 401. Evolution API's global API key is enforced there. The Evolution Manager UI at `/manager/` loaded as a browser app.

Port 443 served a custom WhatsApp Bot HTML frontend. Page title: "WhatsApp Bot HTML". Language: `pt-br`. The TLS certificate was issued for `bmaconnect.com.br` by Let's Encrypt. Port 3000 served the same application. Port 80 returned an Apache Ubuntu default page.

n8n is present via the Redis key name (`n8n-redis-1`) and the scheduling template key with n8n expression syntax. Port 5678 is firewalled from the external network. The n8n instance is externally accessible via reverse proxy at `ia.bmaconnect.com.br` (Apache on the same host). The n8n `/rest/settings` endpoint returns without authentication:

```
GET https://ia.bmaconnect.com.br/rest/settings
→ HTTP 200
{
  "version": "1.122.5",
  "environment": "development",
  "release": "n8n@1.122.5",
  "instanceId": "e5dd9729a270e9e49963763db2ee689de760db4ce2f6b6f4eafb99c6924ade6e",
  "authenticationMethod": "email",
  "settingsMode": "public"
}
```

n8n version 1.122.5, environment `development`. The `/rest/workflows` endpoint returns `401 Unauthorized`. The settings endpoint is intentionally public in n8n; it leaks version and instance ID without credentials.

---

## Stack and Operator Attribution

| Layer | Service | Version | Port / Host | Auth |
|---|---|---|---|---|
| Workflow automation | n8n | 1.122.5 | 5678 firewalled / ia.bmaconnect.com.br proxy | email (login required for workflows) |
| WhatsApp broker | Evolution API | 2.3.7 | 8080 / evolutionapi.bmaconnect.com.br | API key (401 on instance list) |
| WhatsApp frontend | Custom bot UI (pt-br) | — | 443, 3000 | open |
| Redis GUI | RedisInsight | 2.42.0 | 8001 | **none** |
| Redis store | Redis | 7.4.7 | 6379 (Docker-internal) | unknown |
| Web server | Apache 2.4.52 Ubuntu | — | 80 / 443 | open |
| SSH | OpenSSH | 8.9p1 Ubuntu | 22 | key/password |

Operator: `bmaconnect.com.br` (BMA Connect). The Redis key namespace includes `BuffetPaoli`, a catering business name. The n8n scheduling workflow with `lead_numero` points to sales follow-up automation via WhatsApp: booking confirmations, appointment reminders, or lead outreach. `CPSEVA` is a second operator client; the four-digit suffixes (`1616`, `1211`, `1252`) appear to be campaign or channel IDs.

Host: Limestone Networks (US). PTR record `gestao.esamg.org.br` resolves to this IP. Every other host in the /20 carries a static `lstn.net` PTR. This entry is operator-attributed.

---

## The Job-Queue Risk

n8n in queue mode uses Redis as its job broker. Each Bull.js job payload carries the full execution context for a workflow step: trigger data, credential references, and intermediate node outputs. n8n resolves credentials at runtime and writes them into the payload for that step.

No Bull.js `bull:*` keys appeared in this SCAN. n8n may not be running in queue mode, may not have active jobs, or may write to a different db index. What is confirmed: the Redis instance is named `n8n-redis-1` and carries an n8n expression key. The queue integration is present. If queue-mode jobs run, their payloads carry third-party API credentials in cleartext through this same Redis instance, under the same open RedisInsight interface.

The session state and conversation queues for seven WhatsApp Business accounts are readable now. The Evolution API instance hashes carry the cryptographic material for each connected number. Reading any hash is enough to move a session to different infrastructure.

---

## Severity Basis

HIGH. Confirmed:
- RedisInsight 2.42.0 with no authentication (port 8001)
- Seven Evolution API session hashes present (208KB to 1.16MB each), key names confirmed
- 108 Brazilian phone numbers exposed as list key names
- n8n workflow data schema exposed via literal template key
- Evolution API 2.3.7, version and clientName confirmed unauthenticated

Hash contents inferred from Evolution API architecture. Values not read. The key name class alone establishes active session presence.

---

## Infrastructure Map

```
192.169.81.2  (Limestone Networks AS, 192.169.80.0/20)
│
├── PTR: gestao.esamg.org.br
│         esamg.org.br — no public web presence (DNS resolves, HTTP returns empty)
│         likely a client tenant or named deployment context, not BMA Connect itself
│
├── TLS cert: bmaconnect.com.br (Let's Encrypt, valid Jul 2026)
│
├── DNS: bmaconnect.com.br → 192.169.81.2
│         evolutionapi.bmaconnect.com.br → 192.169.81.2
│         ia.bmaconnect.com.br → 192.169.81.2  (n8n reverse proxy)
│
├── DNS: api.bmaconnect.com.br → 179.190.63.39  (Apache placeholder page)
│         www.zion-teste.bmaconnect.com.br → 179.190.63.39  (Apache placeholder page)
│         179.190.63.39 — second server, likely test/staging infrastructure
│
├── :22    OpenSSH 8.9p1 Ubuntu
├── :80    Apache 2.4.52 Ubuntu (default page)
├── :443   Apache 2.4.52 Ubuntu + TLS (WhatsApp Bot HTML, pt-br, "Conectar WhatsApp")
├── :3000  Node.js Express — WhatsApp Bot HTML (same app as :443)
│           Endpoints: /status?token=, /messages?token=, /send?token=
│           token=default → {"connected":true,"qr":null}  (session live)
├── :5678  n8n 1.122.5 — firewalled externally, proxied via ia.bmaconnect.com.br
│           /rest/settings → public (version, instanceId, authMethod=email)
│           /rest/workflows → 401
├── :6379  Redis 7.4.7 — Docker-internal only (n8n-redis-1 container)
├── :8001  RedisInsight 2.42.0 — NO AUTH
│           /api/databases → pre-configured n8n-redis-1:6379 connection
│           /api/databases/:id/keys (POST) → full keyspace scan, no token required
└── :8080  Evolution API 2.3.7 (clientName: evolution_exchange)
            /  → 200 (version info, no auth)
            /instance/fetchInstances → 401 (API key enforced)
            /manager → Evolution Manager UI (browser app, no auth check at HTML layer)
```

**Redis keyspace summary (117 keys, all TTL -1):**

| Class | Count | Key pattern | Data |
|---|---|---|---|
| Evolution API session hashes | 7 | `evolution:instance:<uuid>` | WhatsApp session crypto state, 208KB–1.16MB each |
| Conversation queues | 108 | `<operator>-<recipient>-<sender>[-<seq>]` | Message history lists |
| n8n scheduling template | 1 | `scheduling:{{ $('Variaveis')... }}:calendar_data` | Calendar integration data, unevaluated expression |
| Test/setup artifact | 1 | `minha_chave` (string, 72 bytes) | Unknown value, not read |

**Operator clients identified from key prefixes:**

| Client prefix | Keys | Notes |
|---|---|---|
| CPSEVA-1616 | 32 | Largest single client; central sender +5511986973980 |
| BuffetPaoli | 16 | Catering business; sender +5511966192279 |
| BuffetPaoli1330 | 5 | Variant instance (campaign 1330) |
| CPSEVA-1211 | 4 | Second CPSEVA channel |
| CPSEVA-1252 | 2 | Third CPSEVA channel |
| Bare phone numbers | 49 | Direct queues, no named instance prefix |

**90 unique Brazilian phone numbers appear in key names** spanning area codes 11 (São Paulo), 21 (Rio de Janeiro), 17–19 (São Paulo interior), 21–22 (Rio/ES), 31–55 (other BR states).

---

## Pivot Avenues

1. **cert pivot on `bmaconnect.com.br`** — crt.sh sweep returned: `api.bmaconnect.com.br`, `evolutionapi.bmaconnect.com.br`, `ia.bmaconnect.com.br`, `www.zion-teste.bmaconnect.com.br`. The `api.` and `zion-teste.` subdomains resolve to a second IP (179.190.63.39) currently serving placeholder pages. Staging or future deployments.
2. **Evolution API clientName `evolution_exchange`** — Shodan/Censys dork on this string to find other operators using the same named deployment
3. **`5511986973980` sender number** — the most frequent sender across CPSEVA and direct list keys; appears in 40+ key names; this is a central WhatsApp Business number in the fleet
4. **`5511966192279` sender number** — second most frequent sender; appears across all BuffetPaoli keys
5. **Adjacent IPs in 192.169.80.0/20** — all but this host resolve to `lstn.net` static PTR; any custom PTR in the /20 is another operator-attributed host on the same block
6. **esamg.org.br** — DNS resolves (no PTR elsewhere in /20), HTTP returns empty. No crt.sh history found. Could be a school or association using BMA Connect as a WhatsApp CRM tenant. Reverse-lookup `gestao.esamg.org.br` may surface sister domains.
7. **Port 3000 bot token surface** — the WhatsApp Bot HTML app uses a `?token=` parameter to select sessions. `token=default` confirmed live. Other token values could address other session slots.

---

## Remediation

RedisInsight requires a username and password. Enable this in Settings. Set `RI_ENCRYPTION_KEY` on the Docker deployment and bind RedisInsight to `127.0.0.1` or an internal interface. The management port has no business on a public IP, regardless of auth state. Redis is correctly isolated on the Docker network. The daemon is not the problem. RedisInsight is.

---

*NuClide Research — 2026-05-26*
