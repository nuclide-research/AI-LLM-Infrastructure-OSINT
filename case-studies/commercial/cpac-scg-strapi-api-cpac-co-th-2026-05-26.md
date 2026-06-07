# CPAC Strapi CMS — Production API Surface Enumeration

**Target:** api.cpac.co.th  
**Date:** 2026-05-26  
**Severity:** LOW (this node) / see chain context for full picture  
**Category:** CMS Admin Panel / Unauth Content API / Infrastructure Mapping  
**Tags:** strapi, cms, cpac, scg, thailand, construction, content-api, subdomain-enumeration, aws-ap-southeast-7

---

## Context

Second node in the CPAC chain. The primary finding is in `cpacredis-redisinsight-chain-b-178.128.84.65-2026-05-26.md`. The Redis credential prefix `cpacredis` pivoted to `cpac.co.th`, which resolved to a Strapi CMS instance serving the CPAC website backend. This document covers the Strapi surface.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

**CPAC** (The Concrete Products and Aggregate Co., Ltd.) is Thailand's largest ready-mix concrete producer. Parent: Siam Cement Group (SCG), SET-listed, Thai state-linked conglomerate.

---

## Infrastructure

| Property | Value |
|---|---|
| Hostname | api.cpac.co.th |
| IPs | 43.210.181.122, 43.209.69.59 |
| Provider | AWS ap-southeast-7 (Bangkok region) |
| Load balancer | AWS ELB (both IPs redirect to cpac.co.th on direct IP access) |
| CMS | Strapi v4 (confirmed via `X-Powered-By: Strapi <strapi.io>`) |
| TLS | DigiCert wildcard `*.cpac.co.th` — O=The Concrete Products and Aggregate Co., Ltd. |
| Admin UUID | `37347594-b2ee-4199-bc69-362534c04454` |
| Admin logo | `/uploads/logo_4a82d785cd.png` (custom CPAC wordmark uploaded) |
| S3 bucket | `prd-cpac-website` in `s3.ap-southeast-7.amazonaws.com` (from CSP header) |

The two IPs sit behind an AWS ELB. Both IPs return HTTP 301 to `https://cpac.co.th:443/` on direct access. All application routing goes through the named host. The `awselb/2.0` server header confirms the load balancer tier.

---

## Admin Panel State

`/admin` returns HTTP 200 with the full Strapi Admin SPA. No authentication gate at the network layer. Credentials are required before the UI yields content, but the panel is publicly reachable.

`/admin/init` response:

```json
{
  "data": {
    "uuid": "37347594-b2ee-4199-bc69-362534c04454",
    "hasAdmin": true,
    "menuLogo": "/uploads/logo_4a82d785cd.png",
    "authLogo": "/uploads/logo_69318bd702.png"
  }
}
```

`hasAdmin: true` means at least one super-admin account exists. The instance is not in the first-run provisioning state. Admin registration flow is closed.

`/admin/users/me` returns `401 UnauthorizedError` — admin endpoints require a valid JWT. No credential bypass, no session fixation surface probed.

`/content-manager/content-types` returns `401` — content type introspection requires admin auth.

**Admin auth state: login required. Panel UI publicly accessible. Admin account provisioned.**

---

## Public Content API

Strapi v4 exposes content types via `/api/<collection>`. Permission for each route is configured per-role; the `Public` role gets read access on whatever the operator explicitly enables. Three endpoints returned 200 without credentials:

### /api/tags

46 records. Marketing taxonomy tags for the CPAC website. Titles in Thai:

- GreenFleet, CPACGREENSOLUTION, LovetheSea, GreenConstruction, LowCarbon (English sustainability brand names)
- บ้านปะการัง, คนรักษ์ทะเล (Thai: "Coral House", "Sea Lovers") — environmental campaign names
- เอสซีจี (SCG brand tag)
- CPAC#DinBKKDW2024 (Bangkok Design Week 2024 campaign tag)

All records carry `documentId`, `createdAt`, `updatedAt`, `publishedAt`, and `locale: "th"`. No PII. Content is editorial metadata.

### /api/project-references

14 records. Thai-language project names referencing Bangkok infrastructure and commercial properties:

- อาคารออลซีซั่น (All Seasons Place tower)
- สะพานพระราม 9 (Rama IX Bridge)
- โรงแรมดุสิตธานี (Dusit Thani Hotel)
- ถนนวงแหวนอุตสาหกรรม (Industrial Ring Road)
- รถไฟฟ้า BTS (BTS Skytrain)
- ดอนเมืองโทลเวย์ (Don Mueang Tollway)
- ธนาคารไทยพาณิชย์สำนักงานใหญ่ (SCB HQ)

These are CPAC concrete delivery references, landmark Bangkok projects where CPAC supplied ready-mix. No PII. No contact data. Editorial content.

### /api/about-us

1 record. Single-type content: Thai-language "About Us" page content. `title: "เกี่ยวกับเรา"`. Editorial.

**Public API data class: editorial/marketing content only. No PII. No user data. No operational data.**

---

## Endpoints That Returned Non-404

| Endpoint | Status | Notes |
|---|---|---|
| `/admin/` | 200 | Full Strapi Admin SPA — publicly reachable |
| `/admin/init` | 200 | UUID + logo paths disclosed |
| `/api/tags` | 200 | 46 editorial tags, no auth |
| `/api/about-us` | 200 | 1 single-type record, no auth |
| `/api/project-references` | 200 | 14 project references, no auth |
| `/api/users` | 500 | Internal server error (not 403 — see note below) |
| `/upload/files` | 401 | Exists, auth required |
| `/i18n/locales` | 401 | Exists, auth required |
| `/users-permissions/roles` | 401 | Exists, auth required |
| `/admin/users/me` | 401 | Admin auth required |
| `/content-manager/content-types` | 401 | Admin auth required |
| `/graphql` | 405 | Method Not Allowed — GraphQL plugin absent or POST not accepted |

### /api/users — 500 Note

`/api/users` returns HTTP 500 (InternalServerError) rather than 401 or 403. In Strapi v4, this endpoint maps to `plugin::users-permissions.user`. A 500 instead of a clean auth error means the route is misconfigured: either the `find` permission is improperly set on the Users & Permissions plugin, or the plugin has a bug in the public role handler. No data exposed at present. If the misconfiguration resolves toward "public find enabled" rather than "401", the user table becomes unauthenticated-readable.

---

## CPAC Infrastructure Map

### Confirmed Subdomains (cpac.co.th)

Enumerated via subfinder + DNS brute force. crt.sh returned 502 at time of scan; DNS-based enumeration produced the following:

| Subdomain | IP(s) | Service |
|---|---|---|
| api.cpac.co.th | 43.210.181.122, 43.209.69.59 | Strapi v4 (production) |
| staging-api.cpac.co.th | 43.210.181.122, 43.209.69.59 | Strapi v4 (same instance, same UUID) |
| staging.cpac.co.th | 43.210.181.122, 43.209.69.59 | Next.js frontend (staging) |
| www.cpac.co.th | 43.210.181.122, 43.209.69.59 | Next.js frontend (production) |
| web.cpac.co.th | 43.210.181.122, 43.209.69.59 | (same cluster) |
| cdn.cpac.co.th | CloudFront IPs | CDN layer |
| staging-cdn.cpac.co.th | CloudFront IPs | CDN layer (staging) |
| uate-learning.cpac.co.th | LiteSpeed (Dot Enterprise Co., Ltd. hosting) | LMS — Eudica template |
| test-web.cpac.co.th | (no response within timeout) | unknown |

### staging-api Confirmation

`staging-api.cpac.co.th/admin/init` returns the identical UUID `37347594-b2ee-4199-bc69-362534c04454`. Production and staging API subdomains hit the same Strapi instance behind the ALB. No separate staging deployment. The same database serves both hostnames.

### Parallel Brand: cpacsolution.com

The CSP header on `www.cpac.co.th` discloses a parallel domain cluster: `api.cpacsolution.com`, `staging-api.cpacsolution.com`, `tapi.cpacsolution.com`, `tstaging-api.cpacsolution.com`, `web.cpacsolution.com`. All `cpacsolution.com` API subdomains returned empty responses (no HTTP headers within timeout). Decommissioned or internal-only deployment. The CSP header lists it as an allowed `connect-src` and `img-src` origin, pointing to it as the prior API domain before migration to `api.cpac.co.th`.

### Learning Management System

`uate-learning.cpac.co.th` serves an LMS built on the Eudica template (Bootstrap 4, `Spruko Technologies Private Limited` as template author). Hosted on LiteSpeed via Dot Enterprise Co., Ltd. (Thai ISP/hosting provider). Session cookies set with `secure; HttpOnly`. The 404 page on `/admin/init` confirms it is not a Strapi deployment. No further probe. Out of scope for this pass.

### S3 Bucket

`prd-cpac-website` in `s3.ap-southeast-7.amazonaws.com` — disclosed in Strapi's Content Security Policy header. Bucket listing returns `AccessDenied`. Direct access blocked. The bucket name and region confirm production asset storage in AWS Bangkok.

### aimap-profile Output

- Resolved: 43.210.181.122 (primary), 43.209.69.59 (secondary)
- ASN: AMAZON-AS-AP
- Adjacent PTR sweep: ec2-43-210-181-{120..127}.ap-southeast-7.compute.amazonaws.com — standard AWS /29 block
- Web surface probe on 43.210.181.122 confirms Thai-language CPAC website title
- No honeypot signals
- Classification: unclassified (not an AI/ML service; expected)
- Disclosure: no security.txt, no bounty program found

---

## Findings

**F5 — Strapi Admin UI publicly reachable** (LOW)

`/admin` returns 200 without credentials. The admin panel SPA loads from the public internet. `hasAdmin: true` confirms an active admin account. Admin login is required to access any data, but the panel surface is exposed and the UUID is disclosed. Strapi recommends restricting admin URL access to internal networks or VPN in production.

**F6 — Strapi /admin/init discloses instance UUID and asset paths** (INFO)

The `uuid` field (`37347594-b2ee-4199-bc69-362534c04454`) uniquely identifies this Strapi instance. Combined with the custom logo upload paths, this confirms the instance as a CPAC production deployment. The UUID has no direct exploit path but is useful for fingerprinting and correlation.

**F7 — /api/users returns 500 rather than 401** (LOW)

The Users & Permissions plugin `find` endpoint for the public role is misconfigured. It errors instead of denying. If the error direction resolves toward "allow," the user table becomes unauthenticated-readable. No data exposed at present. The misconfiguration is in an unstable state.

**F8 — staging-api.cpac.co.th shares the production Strapi instance** (LOW)

Both production and staging API hostnames resolve to the same ALB and return the same Strapi UUID. Any vulnerability in the staging entry point affects production data. The staging surface is an additional attack vector against the same backend.

**F9 — MinIO CVE-2023-28432 unprobed** (UNRATED — pending authorization)

The fleet telematics node (178.128.84.65:9000) runs MinIO RELEASE.2020-05-16, which predates the fix for CVE-2023-28432 by three years. This vulnerability discloses `MINIO_ROOT_PASSWORD` in plaintext via a single unauthenticated POST to `/minio/health/cluster?verify`. The probe is one HTTP request, no auth, no destructive action. Unrated pending Cowboy authorization.

---

## Chain Context

This node is the attribution layer of the CPAC chain. The Redis exposure (F1–F4 in the primary case study) is CRITICAL. The Strapi surface adds infrastructure context and secondary attack surface:

- Strapi manages editorial content (tags, project references, about-us page) for cpac.co.th.
- Production and staging API subdomains share the same ALB and Strapi instance. A staging entry point is an attack vector against production data.
- `cpacsolution.com` in the CSP header is a decommissioned predecessor API domain. Orphaned endpoints may remain.
- `uate-learning.cpac.co.th` is a separate attack surface on a different hosting provider.

The Redis node (178.128.84.65, DigitalOcean Singapore) and the Strapi node (43.210.181.122, AWS Bangkok) are on separate cloud providers. The shared credential naming convention (`cpacredis`) points to one ops team managing both.

---

## Tool Chain

- curl: admin state check, API enumeration, CSP analysis
- aimap v1.9.23: port scan (443 only open in target set), X-Powered-By disclosure
- aimap-profile: AWS attribution, PTR sweep, web surface probe
- subfinder + DNS brute: subdomain enumeration (8 subdomains confirmed)
- dig: DNS resolution, NS/MX infrastructure mapping

**Ledger entry:** CPAC chain — F5-F8 appended (LOW). F9 pending.

---

## Remediation

1. Restrict `/admin` to internal network or VPN. Strapi's middleware config supports IP allowlisting on the admin prefix.
2. Fix the `/api/users` 500 — explicitly disable the public `find` permission on the Users & Permissions plugin, confirm the endpoint returns 403 cleanly.
3. Separate staging and production Strapi instances. Shared-backend staging creates a common point of failure.
4. Probe CVE-2023-28432 on MinIO 2020-05-16 (178.128.84.65:9000) and patch if confirmed.
5. Review `cpacsolution.com` API subdomains — decommission or firewall any orphaned endpoints.
