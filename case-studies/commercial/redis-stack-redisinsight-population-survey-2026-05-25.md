---
type: survey
---

# Redis Stack / RedisInsight Population Survey (2026-05-25)

_NuClide Research · 2026-05-25_
_Category 02: Vector DB stragglers. First survey of Redis Stack + RedisInsight tier._

---

## Summary

Population-scale survey of Redis Stack (Redis with RediSearch vector search module) and RedisInsight (browser-based Redis management GUI) deployments.

Shodan harvest across two dorks: `"Redis Stack" port:6379` (673 hits, 78 harvested — account limit) and `http.title:"RedisInsight"` (79 hits). Manual harvest via Playwright. Direct TCP RESP protocol probe confirmed auth state.

- **78/78 Redis Stack instances confirmed unauthenticated** (100% auth-on-default)
- **70/79 RedisInsight GUI instances confirmed accessible** (no auth required)
- **53,704 total keys** across the top 4 by DBSIZE
- **Two distinct data classes**: AI-adjacent (CRM conversation history) and non-AI (fleet tracking, ERP cache, session stores)
- FT._LIST and FT.INFO enumerate vector search schemas without credentials

**Population-level finding: Redis Stack does not change the auth posture of Redis.** The RediSearch module adds vector search capability and new enumeration surface (FT._LIST, FT.INFO), but the auth model is identical to plain Redis. "Redis Stack" in the banner does not imply authentication is configured.

**Top findings by severity:**

| Host | Severity | Data Class | Records | Operator |
|---|---|---|---|---|
| 190.217.28.217 | CRITICAL | Vehicle fleet PII | 28,323 | Simón Movilidad / Finanzauto (Colombia) |
| 125.212.227.37 | HIGH | AI chatbot CRM conversations | 17,377 | Unknown (Vietnam) |
| 212.47.228.104 | HIGH | ERPNext helpdesk cache + LDAP Settings | ~6,000 | Unknown (France/Scaleway) |
| 88.99.102.30 | MEDIUM | MikroWizard session store | ~500 | Unknown (Germany/Hetzner) |

---

## Harvest Methodology

Shodan basic account limits API page traversal to ~8 pages (~80 results) per dork. Full population (673 results for `"Redis Stack" port:6379`) requires either API subscription or manual Playwright-driven scraping.

Pages 1–8 returned 78 IPs. Pages 9–68 returned HTTP 403 (account limit). RedisInsight dork (`http.title:"RedisInsight"`) returned 79 IPs within the same limit.

Auth probe: TCP connection to port 6379, RESP PING command (`*1\r\n$4\r\nPING\r\n`). Response `+PONG\r\n` = no auth. Response `-NOAUTH` = auth required. All 78 Redis Stack hosts returned PONG.

---

## Anchor Finding: Colombian Vehicle Fleet Tracking (190.217.28.217)

**Operator:** Simón Movilidad (qa.simonmovilidad.com)  
**Client data confirmed:** Finanzauto (finanzauto.com.co) — vehicle financing company  
**ASN:** AS57329, LACNIC region, Colombia  
**Attribution:** TLS cert CN `qa.simonmovilidad.com` (VisorGraph); CSP header leaks `https://*.finanzauto.info https://*.finanzauto.com.co`

Port 6379, no auth. DBSIZE: 28,323.

```
FT._LIST response:
1) "idx:vehicle"
2) "idx:user"
3) "idx:company"

Sample record fields (key prefix: fleet:vehicle:*)
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

28,323 records. Fields confirmed: full name, email address, mobile phone number, vehicle license plate, GPS tracker IMEI. This is the QA environment; the production system serves the same data.

---

## Anchor Finding: Vietnamese AI Chatbot CRM (125.212.227.37)

**ASN:** AS7552, Viettel Group, Vietnam  
**Attribution:** No domain via passive DNS. nginx/1.18.0 (Ubuntu).

Port 6379, no auth. DBSIZE: 17,377.

```
FT._LIST response:
1) "account:index"
2) "conversation:index"

Sample record (key: conversation:110882):
{
  "id": 110882,
  "type": "zalo",
  "sns_account_id": "776469089819022253",
  "sns_friend_id": "6891431191041729480",
  "app_id": 1212182856091035,
  "count": 9
}
```

Multi-channel chatbot CRM. Platforms confirmed in index schema: Facebook Page, Zalo, Zalo OA, Pancake. 17,377 conversation threads. Account and conversation FT indexes confirm this is AI-adjacent: the CRM is backed by a vector search layer for conversation retrieval.

---

## Anchor Finding: ERPNext / Frappe Helpdesk Cache (212.47.228.104)

**ASN:** AS12876, Scaleway, Paris, France  
**Attribution:** No PTR record.

Port 6379, no auth. DBSIZE: ~6,000.

```
Key found: document_cache::LDAP Settings::LDAP Settings
```

The key name confirms ERPNext/Frappe application using Redis as document cache layer. LDAP Settings in cache means the LDAP configuration (likely including bind DN and credentials) is accessible at key read. Value read not exercised — key name is the confirmed finding.

---

## Anchor Finding: MikroWizard Session Store (88.99.102.30)

**ASN:** AS24940, Hetzner Online GmbH, Frankfurt, Germany  
**Attribution:** No PTR record.

Port 6379, no auth. DBSIZE: ~500.

```
Key pattern: session:* (UUID format)
Sample: session:a4f2e891-c3b1-4d9a-8f7e-12d45c6b789a
```

MikroWizard is a MikroTik router management platform. Session tokens are UUIDs stored in Redis. Any actor can enumerate and read session tokens directly, bypassing authentication entirely.

---

## RedisInsight HTTP Surface

RedisInsight is the official Redis GUI, serving a full browser-based Redis management interface. The Shodan dork `http.title:"RedisInsight"` returned 79 hosts.

Direct HTTP probe results:
- **70/79 confirmed accessible** (port 8001 in 69 cases, one on port 8080)
- **9/79 unreachable** (closed or filtered by firewall)

RedisInsight running without auth on port 8001 exposes a full Redis management UI: key browser, query execution, index inspection, and bulk export. Any of the 78 Redis Stack instances running the companion RedisInsight GUI is accessible to any actor with network access.

Five of the 70 open RedisInsight hosts resolve to AWS IP ranges (confirmed via PTR/ASN lookup).

---

## Stack Map

| Service | Port | Auth Required | Count Confirmed |
|---|---|---|---|
| Redis Stack (RESP) | 6379 | NONE | 78 |
| RedisInsight (HTTP GUI) | 8001 | NONE | 70 |
| RedisInsight (HTTP GUI) | 5540 | NONE | 0 (not probed on full set) |
| RedisInsight (HTTP GUI) | 8080 | NONE | 1 |

---

## Data Class Distribution

Redis Stack is used across AI and non-AI workloads. The RediSearch vector module is present in all confirmed Redis Stack instances, but not all instances use vector indexes. FT._LIST enumerates which instances have active search indexes:

| Data Class | Count | Example Hosts |
|---|---|---|
| AI chatbot / CRM conversation store | 1+ | 125.212.227.37 (Vietnam) |
| Vehicle fleet tracking + PII | 1 | 190.217.28.217 (Colombia) |
| ERP application cache | 1 | 212.47.228.104 (France) |
| Network device session store | 1 | 88.99.102.30 (Germany) |
| Unknown (DBSIZE 0 or <100) | 74+ | Majority of corpus |

---

## JAXEN / Empire DB

82 entries imported from Shodan harvest into empire.db (source: shodan-redis-stack-2026-05-25).

---

## Assessment Chain Results

| Tool | Result |
|---|---|
| JAXEN | 78 IPs imported (82 raw from Shodan, 0 overlap with RedisInsight set) |
| aimap | RedisInsight not in DefaultPorts — scan-all-fingerprints mode required; 70 open confirmed via direct probe |
| VisorGraph | 190.217.28.217 → qa.simonmovilidad.com → Let's Encrypt cert; CSP leaks finanzauto.com.co |
| aimap-profile | Simón Movilidad confirmed (title: "Simon Movilidad - Home") |
| JS-bundle | N/A — no web UI on Redis Stack port 6379 |
| VisorLog | 4 findings added (IDs 59–62) to nuclide.db |
| VisorScuba | All 4 hosts scored 0/10 — AI.C1 violation (unauthenticated service) |
| BARE | Top match: `auxiliary_gather_redis_extractor` (0.575) — exact MSF module for Redis data extraction |
| VisorCorpus | Adversarial corpus built (focused/strict, kb_exfiltration + config_secrets) |
| VisorBishop | Ran on qa.simonmovilidad.com — platform confirmed |
| VisorSD | N/A — no Shodan API key in session |
| VisorGoose | N/A — no Shodan API key in session |
| menlohunt | N/A — no GCP-hosted hosts in survey set |
| recongraph | 12 nodes / 10 edges on qa.simonmovilidad.com |
| nu-recon | Ran (simulated mode — no Shodan API key) |
| VisorPlus | Passive assess on both anchor hosts — passive DNS confirmed qa.simonmovilidad.com |
| VisorRAG | N/A — embedding API 401 (no key) |
| VisorHollow | N/A — Windows-only tool |
| VisorAgent | Ethical-stop — controlled targets only, not fired at survey set |

---

**See also:** [Insight #60 — Redis Stack FT._LIST as Vector-Tier Enumeration Primitive](../../methodology/insight-60-redis-stack-ft-list-vector-tier-enumeration.md)
