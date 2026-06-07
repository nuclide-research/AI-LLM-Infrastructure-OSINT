---
type: case-study
title: "ORES CRM (CloudWorks/ows.vn) — Redis Stack Open, 17,337 Chatbot Conversation Records, Multi-Channel Social PII"
date: 2026-05-26
severity: HIGH
sector: commercial
tags: [Redis-Stack, RediSearch, chatbot-crm, Zalo, Facebook-Page, Zalo-OA, Pancake, PII, Vietnam, Viettel, ores.vn, CloudWorks]
summary: "ORES, a Vietnamese AI-chatbot CRM SaaS built by CloudWorks (ows.vn), runs Redis Stack at 125.212.227.37 without authentication. Two RediSearch indexes expose 34 channel accounts and 17,337 conversation records. Key names confirm multi-channel routing across Zalo, Facebook Page, Zalo OA, and Pancake. The account:index schema stores a token field: OAuth credentials for each connected social channel. The host is the backend for my.ores.vn, proxied through ssl-proxy2.ows.vn at the adjacent IP 125.212.227.40. ASN: AS7552 Viettel Group, Vietnam."
---

# ORES CRM (CloudWorks/ows.vn) — Redis Stack Open, 17,337 Chatbot Conversation Records

**Date:** 2026-05-26  
**Target:** 125.212.227.37  
**ASN:** AS7552 Viettel Group, Vietnam  
**Operator:** CloudWorks — ows.vn / ores.vn  
**Product:** ORES CRM (ORES_Ultimate, ORES_Center, ORES_Telesale, ORES_Social_Hub)  
**Severity:** HIGH

---

## Findings

### F1 — Redis Stack Open Without Authentication (HIGH)

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

Port 6379 accepts RESP commands without credentials:

```
TCP → RESP PING → +PONG (no AUTH required)
```

DBSIZE: 17,377. Two RediSearch indexes registered: `account:index` and `conversation:index`. JSON key type confirmed (ReJSON-RL). This is a RediSearch full-text index tier in production, not a throwaway cache.

### F2 — account:index: 34 Channel Accounts, Token Field in Schema (HIGH)

FT.INFO on `account:index`:

```
prefix:   account:
key_type: JSON
num_docs: 34
```

Schema fields:

| Field | Type | Notes |
|---|---|---|
| id | NUMERIC | internal account ID |
| type | TAG | channel type (zalo, facebook_page, zalo_oa, pancake) |
| name | TAG | channel/page display name |
| avatar | TAG | avatar URL |
| sns_account_id | TAG | platform-assigned account ID |
| app_id | NUMERIC | Facebook/Zalo app ID |
| token | TAG | **platform access token** |
| is_hide_comment | TAG | moderation flag |

The `token` field is indexed. Each token is an OAuth or app-level credential ORES uses to send and receive messages on behalf of a connected channel. The schema shows 34 accounts across Zalo, Facebook Page, Zalo OA, and Pancake.

### F3 — conversation:index: 17,337 User Conversation Records (HIGH)

FT.INFO on `conversation:index`:

```
prefix:   conversation:
key_type: JSON
num_docs: 17,337
```

Schema fields:

| Field | Type | Notes |
|---|---|---|
| id | NUMERIC | internal conversation ID |
| type | TAG | channel (zalo, facebook_page, zalo_oa) |
| sns_account_id | TAG | operator's channel account ID |
| sns_friend_id | TAG | end-user's platform ID |
| app_id | NUMERIC | Facebook/Zalo app ID |
| count | NUMERIC | message count in thread |

Key naming pattern confirmed from SCAN:

```
conversation:conversation_1212182856091035_110882_zalo
conversation:conversation_1212182856091035_2214141_facebook_page
conversation:conversation_1212182856091035_2215420_facebook_page
conversation:conversation_1212488833004529_111235_zalo_oa
conversation:conversation_1212135788288636_2214303_facebook_page
```

The `sns_friend_id` is the end-user's Zalo UID or Facebook UID. It is a persistent platform handle. 17,337 records. 17,337 users. Their conversation history with these chatbot channels is in this store.

### F4 — Web Front End: ORES CRM SPA (LOW)

Port 80 serves an nginx/1.18.0 (Ubuntu) front end:

```
GET / → 200 OK
Title: Ores
nginx/1.18.0 (Ubuntu)
```

The SPA bundle (`/assets/index-6c074757.js`) confirms product identity. Hardcoded API origins:

```
https://my.ores.vn
https://api-sales.ores.vn
https://ores.reseller.dev.ows.vn
```

Product SKUs visible in bundle: `ORES_Ultimate`, `ORES_Pos`, `ORES_Telesale`, `ORES_Center`, `ORES_Social_Hub`. Support routed to `support.cloudworks.vn`. Store at `store.ores.vn`. Docs at `docs.ores.vn`.

---

## Attribution

**Operator: CloudWorks Vietnam**  
Domain: ows.vn / cloudworks.vn  
Product brand: ORES (ores.vn)  
Registration: DNS via Google Workspace MX (aspmx.l.google.com), Mailgun secondary  
Infrastructure: Viettel AS7552, /24 125.212.227.0/24

**SSL proxy layer:** `my.ores.vn` and `api-sales.ores.vn` are CNAMEd to `ssl-proxy2.ows.vn`. That resolves to `125.212.227.40`, three addresses away in the same /24. The Redis backend at `.37` has no PTR record and sits outside the proxy layer.

**Adjacent IPs in same /24 (PTR sweep):**

| IP | PTR |
|---|---|
| 125.212.227.32 | 32.0-24.227.212.125.in-addr.arpa. (no hostname) |
| 125.212.227.37 | No PTR — **this host** |
| 125.212.227.40 | ssl-proxy2.ows.vn (ores.vn / api-sales.ows.vn proxy) |

**Product architecture (from schema and bundle):**

ORES is a multi-channel AI chatbot CRM. Operators connect social media channels via OAuth tokens stored in `account:index`. The schema suggests each inbound message creates or updates a `conversation:` record keyed by app ID, conversation ID, and channel type. The `count` field tracks messages per thread. Message content sits in the JSON document body, not in the indexed fields.

---

## Stack Map

| Host | Port | Service | Version | Auth |
|---|---|---|---|---|
| 125.212.227.37 | 80 | nginx + ORES CRM SPA | nginx/1.18.0 | None (front end) |
| 125.212.227.37 | 6379 | Redis Stack (RediSearch + ReJSON) | unknown | **NONE** |
| 125.212.227.40 | 443 | nginx ssl-proxy2.ows.vn | unknown | TLS (proxy layer) |
| my.ores.vn | 443 | ORES CRM (via ssl-proxy2) | — | Auth required (app) |
| api-sales.ores.vn | 443 | ORES Sales API (via ssl-proxy2) | — | Auth required (app) |

---

## Thesis Placement

ORES enforces application-layer auth at the nginx proxy. The chatbot workers write to Redis from the Zalo and Facebook webhook handlers. They require no Redis auth. The application boundary is protected. The data layer is not.

Platform access tokens bound to live Facebook Pages and Zalo OA channels are indexed and exposed. Reading those fields gives direct API access to each connected channel. The schema links 17,337 Vietnamese users' Zalo UIDs and Facebook UIDs to their message history.

This is the standard Redis-as-hot-cache pattern. The application team added auth to every user-facing surface and left the backing store open.

**See also:** [Redis Stack / RedisInsight Population Survey (2026-05-25)](redis-stack-redisinsight-population-survey-2026-05-25.md)
