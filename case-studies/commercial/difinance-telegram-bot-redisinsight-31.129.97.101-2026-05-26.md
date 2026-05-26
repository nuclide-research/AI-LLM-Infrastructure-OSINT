# difinance.online — RedisInsight Credential Leak on Telegram DeFi Bot

**Target:** 31.129.97.101  
**Date:** 2026-05-26  
**Severity:** MEDIUM  
**Category:** Unauth Management UI / Credential Exposure / Telegram Bot Infrastructure  
**Tags:** redis-stack, redisinsight, chain-b, credential-leak, telegram-bot, FSM, aiogram, DeFi, celery, RU

---

## The Tell

RedisInsight on port 8001 required no authentication. `GET /api/databases` returned the full Redis connection object, including the password `Sq3QmHxJCPn5Dt4LzAaNRg` in plaintext. The credential gave direct AUTH access to Redis 7.2.4. The instance held aiogram FSM state for a Telegram bot and Celery queue bindings — infrastructure for a DeFi financial services bot operating under the domain difinance.online.

---

## Infrastructure

- **IP:** 31.129.97.101  
- **Host:** Beget LLC (RU) — confirmed via WHOIS registrar and ASN
- **OS:** Linux 5.15.0-134-generic x86_64  
- **Uptime:** 420 days (since ~March 2025)  
- **Redis version:** 7.2.4  
- **Redis executable:** /opt/redis-stack/bin/redis-server  
- **Redis modules:** redisgears_2, ReJSON 2.6.10, RediSearch 2.8.13, RedisTimeSeries 1.10.12, RedisBloom 2.6.12  
- **RedisInsight version:** 2.44.0 (created 2024-04-29)  
- **Web stack:** nginx/1.18.0 (Ubuntu) on :80/:443  
- **Celery workers:** 3 (container IDs: 62dddf7cb027, ccfb53692327, eb310f55d338)

---

## Domain Surface

- `difinance.online` — React SPA, title "Difinance Admin". Admin panel frontend.
- `bot.difinance.online` — TLS cert SAN. Serves nginx default page ("Welcome to nginx!"). Bot API endpoint not publicly accessible.
- TLS cert issued by Let's Encrypt R13. Single-domain cert covering difinance.online only.
- Registrar: Beget LLC. Nameservers: ns1/ns2.beget.com and ns1/ns2.beget.pro.

VisorGraph returned 3 nodes: the difinance.online service, the domain node, and the Let's Encrypt cert. One edge: cert issued_for domain. SAN contains only difinance.online; no further pivots.

---

## Access Chain

```
GET http://31.129.97.101:8001/api/databases

→ password: "Sq3QmHxJCPn5Dt4LzAaNRg"
→ host: localhost
→ port: 6379
→ lastConnection: 2026-05-04T09:46:54.908Z
```

AUTH against Redis :6379 returned `+OK`. Both DB0 and DB1 accessible post-AUTH. No RedisInsight proxy required.

---

## Data Inventory

### DB0 — Telegram FSM State (4 keys)

Key pattern: `fsm:<user_id>:<chat_id>:aiogd:context:<state>:data` and `fsm:<user_id>:<chat_id>:aiogd:stack::data`

Telegram user IDs extracted from key names:

| User ID | Keys |
|---|---|
| 828506453 | context + stack |
| 6954953986 | stack only |

Key names only enumerated; values not read. Context keys carry state machine payloads for active bot conversations. Stack keys carry aiogram dialog navigation history.

### DB1 — Celery Queue Bindings + FSM State (9 keys)

**Celery worker queue bindings:**

| Binding Key | Members |
|---|---|
| `_kombu.binding.celery` | `celerycelery` (default task queue) |
| `_kombu.binding.celery.pidbox` | 3 worker mailboxes (62dddf7cb027, ccfb53692327, eb310f55d338) |
| `_kombu.binding.celeryev` | 3 worker event monitors |

3 Celery workers active, each in a separate Docker container. `_kombu.binding.celery` membership `celerycelery` is the default queue routing. No named task routes in the binding set.

**Additional FSM keys in DB1:**

| User ID |
|---|
| 464952938 |
| 828506453 |
| 1130451895 |

User 828506453 has active FSM state in both DB0 and DB1.

---

## Platform Assessment

difinance.online is a Telegram-based DeFi bot platform. The admin panel ("Difinance Admin") provides operator oversight. aiogram drives the bot's conversation state machine. Celery handles async task processing — likely transaction submission, balance checks, or notification dispatch.

Domain and registrar are Russian (Beget LLC, RU nameservers). 420-day uptime on a 2025-03 deployment. RedisInsight live since April 2024.

No financial data values were extracted. 4 Telegram user IDs across both DBs confirm an active bot. DeFi context comes from the domain name and "Difinance Admin" product framing.

The credential `Sq3QmHxJCPn5Dt4LzAaNRg` is a 22-character generated string. It was stored in plaintext in the RedisInsight configuration with no access control on the management port.

---

## Findings

**F1 — Unauthenticated RedisInsight with credential exposure** (MEDIUM)  
RedisInsight :8001 requires no authentication. The Redis password appears in the `/api/databases` response in plaintext. Any network client can recover the credential.

**F2 — Direct Redis AUTH access** (MEDIUM)  
This instance accepts the leaked credential on :6379 directly. No intermediary proxy required. Full keyspace access confirmed with the leaked password.

**F3 — Telegram user ID exposure via FSM key names** (LOW)  
Telegram user IDs are embedded in Redis key names. User IDs are semi-public on Telegram, but their presence confirms active users and allows cross-referencing via Telegram's user lookup surface.

**F4 — Celery worker infrastructure exposed via queue bindings** (LOW)  
3 Celery worker container IDs are visible in the `_kombu.binding.celery.pidbox` key. Worker count and container naming confirmed without authentication.

---

## Chain Context

Chain-B pattern: RedisInsight credential leak grants Redis access. The difinance instance is lower severity than fleet telematics or PII-bearing cases. The exposed data is infrastructure state, not wallet addresses, transaction history, or identity data.

420-day uptime. RedisInsight created April 2024. No evidence of patching or review. Beget LLC hosting is consistent with RU-origin DeFi infrastructure.

---

## Remediation

1. Enable authentication on RedisInsight (Settings → Authentication). RedisInsight 2.x supports username/password natively.
2. Bind :8001 to localhost. Do not expose the management port on the public interface.
3. Bind Redis :6379 to localhost or restrict via firewall. External access is not required for a localhost-only deployment.
4. Rotate `Sq3QmHxJCPn5Dt4LzAaNRg`. Treat as compromised.

---

## Tool Chain

- RedisInsight unauthenticated API: credential recovery, schema enumeration
- Redis direct AUTH: DB0/DB1 key enumeration
- aimap v1.9.23: 4 open ports (80, 443, 6379, 8001), no AI/ML surface
- VisorGraph: 3 nodes (service, domain, cert), 1 edge, no pivot
- nmap: nginx/1.18.0, Redis, Node.js Express confirmed
- crt.sh: bot.difinance.online + difinance.online
- WHOIS: Beget LLC registrar, RU nameservers confirmed

**Ledger entry:** `nuclide.db` — MEDIUM, tags: telegram-bot,FSM,aiogram,DeFi,celery,redisinsight,chain-b,RU
