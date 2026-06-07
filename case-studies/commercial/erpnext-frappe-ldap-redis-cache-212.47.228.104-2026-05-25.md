---
type: case-study
title: "CloudCentric / BizCentric — ERPNext/Frappe Multi-Tenant Redis Cache: LDAP Settings Keys Exposed, 27 Tenants"
date: 2026-05-25
updated: 2026-05-26
severity: HIGH
sector: commercial
tags: [Redis-Stack, ERPNext, Frappe, LDAP, credentials, document-cache, helpdesk, multi-tenant, cloudcentric, bizcentric, Scaleway, UAE, SaaS]
summary: "CloudCentric runs a shared Redis Stack instance at 212.47.228.104 (Scaleway, Paris) as the document cache for a multi-tenant ERPNext/Frappe deployment. No authentication. DBSIZE 2,716. Two LDAP Settings document cache keys are present with TTL -1 (persistent). The LDAP Settings doctype in Frappe stores the bind DN, bind password, and LDAP server URL. Key names are readable without auth. Values were not read per restraint ethic. 27 tenant subdomains identified from Redis job queue keys."
---

# CloudCentric / BizCentric — ERPNext/Frappe Multi-Tenant Redis Cache: LDAP Settings Keys Exposed

**Date:** 2026-05-25 | **Updated:** 2026-05-26  
**Target:** 212.47.228.104  
**PTR:** 104-228-47-212.instances.scw.cloud  
**ASN:** AS12876, Scaleway, Paris, France  
**Operators:** CloudCentric (cloudcentric.me, SaaS provider) + BizCentric (bizcentric.me, ERP vendor, Dubai/UAE)  
**Severity:** HIGH

---

## Findings

### F1 — Redis Stack Open Without Authentication, LDAP Settings Keys Present (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Port 6379 answers without credentials:

```
TCP -> RESP PING -> +PONG (no AUTH)
```

DBSIZE: 2,716. Redis 7.4.7 on Linux 5.15.0-179-generic. Uptime 2 days. Running from `/opt/redis-stack/etc/redis-stack.conf`. The path confirms Redis Stack. RediSearch is confirmed active via FT._LIST. RedisJSON ships with Redis Stack and is expected loaded.

Two LDAP Settings document cache keys present:

```
_10f50ffff591b288|document_cache::LDAP Settings::LDAP Settings
_43c0afbe28adca55|document_cache::LDAP Settings::LDAP Settings
```

Both confirmed:

```
EXISTS -> :1
TYPE   -> +string
TTL    -> :-1   (no expiry — persistent)
```

The key name pattern is canonical Frappe. The format is `{site_hash}|document_cache::{doctype}::{docname}`. Two site hashes map to two Frappe site instances. Each caches its own LDAP Settings document. Both are persistent and will not expire.

The Frappe LDAP Settings doctype stores LDAP server URL, bind DN, bind password, user search base, user name attribute, and group search parameters. That is the full credential set for the organization's LDAP/AD directory.

Values were not read. The finding is the key presence, the cache type, and the zero-expiry TTL. The exposure is structural. Any client that reaches port 6379 can read the bind DN and password.

### F2 — Multi-Tenant Deployment: 27 Tenant Sites Identified (INFO)

The Redis job queue (`rq:job:*` and `rq:results:*` keys) encodes the Frappe site name in every key. Scanning these produces the full tenant list:

**cloudcentric.me tenants:**

| Subdomain | Notes |
|---|---|
| adham.cloudcentric.me | Customer tenant |
| cc-demo.cloudcentric.me | Demo — ecommerce integration (Unicommerce) |
| client-portal | Internal label |
| demo-15.cloudcentric.me | Demo tenant — email + Google Calendar sync |
| demo-2.cloudcentric.me | Demo tenant — pulse events, Google Calendar |
| demo.cloudcentric.me | Demo tenant |
| demo2-backup.cloudcentric.me | Backup/staging — M365 messaging integration |
| digitaloasis.cloudcentric.me | Customer tenant |
| ess-15.local | Internal / local instance |
| evadclone.cloudcentric.me | Customer tenant — EVAD |
| evadtesting.cloudcentric.me | Testing — ERPNext GL/SLE ops |
| fmc.cloudcentric.me | Customer tenant — FMC |
| fmsipoc.cloudcentric.me | Customer tenant — FMSIPOC (POC deployment) |
| ino-backup.cloudcentric.me | Customer backup tenant |
| kjglobal-backup.cloudcentric.me | Customer backup tenant — KJ Global |
| learning.cloudcentric.me | Learning/training tenant |
| mazaya.cloudcentric.me | Customer tenant |
| messaging.cloudcentric.me | Messaging integration node |
| ms365.cloudcentric.me | M365 integration tenant |
| poc.cloudcentric.me | POC tenant — ERPNext + Google Calendar |
| recieva-demo.cloudcentric.me | Demo — Recieva |
| retail.cloudcentric.me | Customer tenant — retail, frappe_assistant_core |
| retaildemo.cloudcentric.me | Retail demo |
| sales.cloudcentric.me | Sales tenant |
| smacenter-demo.cloudcentric.me | Demo — SMA Center |
| testing-demo-data.cloudcentric.me | Test data tenant — M365 contact sync |

**bizcentric.me tenants:**

| Subdomain | Notes |
|---|---|
| portal.bizcentric.me | Customer/partner portal — BizCentric UAE |

Total: 27 tenant site names.

### F3 — Eight Frappe Helpdesk Full-Text Search Indexes Active (INFO)

`FT._LIST` returns 8 active RediSearch indexes, all named `helpdesk_idx`:

```
_d17607fc60be8531|helpdesk_idx
_03a71690f6b2465b|helpdesk_idx
_b3acc6253d287fca|helpdesk_idx
_ac10a527c39725f2|helpdesk_idx
_c0e97277a75767fe|helpdesk_idx
_32e3220278628335|helpdesk_idx
_555e77f0c38b8634|helpdesk_idx
_39c78b0774b894f7|helpdesk_idx
```

`FT.INFO` on one index confirms the indexed doctype is `HD Ticket`. Fields: `name`, `subject` (weight 6), `description` (weight 5), `headings` (weight 8), `team` (tag), `modified` (sortable), `creation` (sortable). This is the Frappe Helpdesk module. Each of the 8 indexes covers a separate site's support ticket corpus.

Search doc keys are visible in SCAN output (`search_doc:HD Ticket:152`, `search_doc:HD Ticket:143`, etc.). Active ticket data is indexed and searchable without auth.

### F4 — HTTP Surface: No Direct Web Response on Standard Ports (INFO)

HTTP probes on ports 80, 443, 8000, 8069, and 8080 returned nothing. The node is a shared backend Redis instance. The Frappe web layer sits elsewhere.

---

## Attribution

**Operator: CloudCentric**  
cloudcentric.me | "Your SaaS Provider"  
IP 20.74.216.59 (Azure) | MX: cloudcentric-me.mail.protection.outlook.com (Microsoft 365)  
WordPress site, Elementor. Describes itself as a SaaS hosting provider.  
Runs ERPNext/Frappe as the primary product offering.

**Operator / Partner: BizCentric**  
bizcentric.me | "Best HR and Payroll Software System in Dubai, UAE"  
IP 172.67.177.34 / 104.21.88.111 (Cloudflare CDN) | MX: bizcentric-me.mail.protection.outlook.com  
UAE-based ERP vendor. Products: ERPNext, Frappe Helpdesk, Accounting, CRM, HR and Payroll.  
One tenant (`portal.bizcentric.me`) shares this Redis backend. BizCentric runs on Frappe under CloudCentric infrastructure.

**Shared Redis backend:**  
The Redis instance at 212.47.228.104 serves both operators. Site-hash prefixes partition keys per tenant. The whole keyspace is flat and open to any client that connects. Frappe caches LDAP Settings in Redis as a performance optimization. It treats the document cache as an internal trust boundary. That boundary is missing here.

**Helpdesk modules in use:** `frappe_assistant_core` appears in job queue keys for retail.cloudcentric.me. At least one tenant runs an AI assistant layer on top of the helpdesk stack.

---

## Stack Map

| Component | Version | Auth | Notes |
|---|---|---|---|
| Redis Stack | 7.4.7 | **NONE** | Port 6379, bound to 0.0.0.0 |
| RediSearch | active | inherited | 8 helpdesk_idx indexes |
| Frappe / ERPNext | unknown | n/a | Application layer, not directly exposed |
| Frappe Helpdesk | active | n/a | HD Ticket doctype confirmed |
| LDAP integration | active | bind creds in cache | Two site instances |

---

## Chain Context

The Frappe document cache is write-through. When a user or background job loads an LDAP Settings document, Frappe serializes it into Redis as a string. The bind password is decrypted from MariaDB at load time. Frappe stores it encrypted at rest. The cache holds the decrypted runtime object. That is what Redis holds. Both keys have TTL -1. They were written once and will persist until flushed or overwritten.

BARE module ranking for this finding class:

```
auxiliary_scanner_redis_redis_login     score: 0.54
auxiliary_gather_redis_extractor        score: 0.48
```

Both are read-primitive modules.

---

## Thesis Placement

The application layer encrypts the bind password at rest. The cache layer holds the decrypted runtime object. The cache layer has no authentication. Security enforced at rest, missing in motion.

Any Frappe/ERPNext deployment that caches LDAP Settings and leaves Redis open has this exposure. One open Redis instance covers 27 sites. A single key read yields the bind DN and password for whichever site that key belongs to.

**See also:** [Redis Stack / RedisInsight Population Survey (2026-05-25)](../redis-stack-redisinsight-population-survey-2026-05-25.md)
