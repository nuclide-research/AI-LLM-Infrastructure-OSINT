# Elasticsearch / OpenSearch on Public Cloud — Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 9200 → 313 masscan hits → **42 confirmed unauthenticated Elasticsearch/OpenSearch instances** (38 ES, 4 OpenSearch). Roughly half are ransomed/wiped. Several contain production data including a compliance SaaS with 79 million KYB records.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 9200 --rate 6000 (partial, ~40% coverage)
  → 313 masscan hits on :9200

/home/cowboy/go/bin/httpx -p 9200 -path /_cat/indices -mc 200 (confirmed live)
  → 51 live → 42 confirmed ES/OpenSearch via /_cat/indices?format=json

curl /_cat/indices?format=json, /{index}/_search (per-instance enumeration)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Masscan hits on :9200 | 313 |
| Confirmed ES/OpenSearch (httpx) | 51 |
| Unauthenticated with data | **42** |
| Ransomed / wiped (`read_me` only) | ~18 |
| Hash-named tutorial indices only | ~8 |
| Production data | **~16** |
| AI/ML-specific indices | 3 |

---

## Notable Exposures

### 1. AML/KYC Compliance SaaS — 79M Records (CRITICAL)

**Host:** `168.119.90.62:9200` (Hetzner — `eu-cluster` node `es01`)

**Indices:**
| Index | Docs |
|---|---|
| `kyb_data_index_prod` | 79,067,927 |
| `allsearchindexv2prod` | 6,230,703 |
| `documentsearchindexprod` | 877,138 |
| `ongoing_monitoring_organization_2_queries` | 2 |

**What's exposed:**

This is a production multi-tenant AML/KYC compliance screening platform. The exposure is complete — the entire production database is unauthenticated.

**`kyb_data_index_prod`** — 79M company records. Sample:
```json
{"id": "O109062743", "companyName": "FUNDACIÓN MUJERES DE GLORIA", "companyNumber": "2279122",
 "cleanFullName": "FUNDACION MUJERES GLORIA", "status": "1",
 "establishmentDate": "2026-02-18T00:00:00", "listTypeId": "17", "matchRate": 0}
```
Colombian business registry entities cross-referenced against watchlists. `listTypeId` maps to specific sanctions/watchlist sources. `matchRate` indicates sanctions screening match score.

**`allsearchindexv2prod`** — 6.2M individual records from global sanctions and watchlists:
```json
{"id": "I26783920", "fullName": "Roger Edward Muse", "cleanFullName": "ROGER EDWARD MUSE",
 "nationalities": [], "listId": "3589", "typeId": 1, "isIndividual": true,
 "createdDate": "2021-04-08T22:15:34"}
```
`listId` references specific sanctions lists (OFAC SDN, EU Consolidated, UN, PEP databases, etc.). Thousands of distinct list IDs present.

**`documentsearchindexprod`** — 877K document number records (tax IDs, registration numbers) tied to entities in the watchlists.

**`ongoing_monitoring_organization_2_queries`** — Live monitoring queries:
```json
{"id": 20, "cleanQueryString": "ADEM YILMAZ", "listType": 1,
 "searchedType": 0, "organizationId": 2, "period": 1}
```
Active client (organizationId 2) is monitoring "ADEM YILMAZ" against sanctions lists. Multi-tenant platform confirmed.

**Impact:**
1. **Compliance data provider IP stolen** — the aggregated watchlist corpus is a proprietary product sold to banks/fintechs/exchanges. Full extraction is trivial.
2. **Sanctions evasion enablement** — adversaries can query whether they appear on watchlists before attempting financial transactions.
3. **Client exposure** — the `ongoing_monitoring_organization_2_queries` data reveals who the platform's clients are screening, which is protected information.
4. **GDPR Article 9 / FATF implications** — sanctions list data combined with identifiers constitutes special category data under GDPR; unprotected exposure in an EU-hosted cluster triggers notification obligations.

**Severity:** CRITICAL

---

### 2. Vietnamese AI Image Service — API Request Logs

**Host:** `65.108.32.173:9200` (Hetzner)

**Index:** `facex-logs-2026.05.03` (577 docs, live today)

**What's exposed:**

API request/response logs for a Vietnamese AI image service running at `+07:00`. Logs contain:
- User credentials: `{"user_id": "e5c1ed0b-...", "username": "service-account-eztech", "email": "eztech-client@gmail.com", "tenant_id": "eztech"}`
- Endpoint activity: `/service/api/v2/nsfw`, `/service/api/v2/art-changestyle`, `/service/api/upload/presigned-url`
- Image URLs being processed (Pinterest, uploads)
- Processing times, response codes

**Severity:** MEDIUM — production API logs with customer credentials (tenant IDs, user IDs, email addresses) written to unprotected Elasticsearch in real time.

---

### 3. Nepal Government Notices Database

**Host:** `206.189.133.202:9200` (DigitalOcean)

**Index:** `notices` (2,539 docs)

Nepali-language government tender and public notices. Sample: procurement notices from various ministries, staff appointment announcements, ayurvedic health center notifications. Ministry and category fields present; base64-encoded images embedded in description fields.

Source data appears to be public government notices, but this should be served through a frontend, not an exposed ES index.

**Severity:** LOW — public data, but infrastructure exposure.

---

### 4. Ransomed / Wiped Instances

Approximately 18 instances contained only a `read_me` index with the following ransom demand:

> "Your database has been deleted from your server, but all the information remains stored on our cluster. The instructions for recovery are as follows: You must send 0.0041 BTC to the following wallet: bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r. Then, you must send an email to wendy.etabw@gmx.com with code 0SH7HH1Q72JL..."

Standard automated ES ransom campaign. The same wallet/email/code across all instances. Data was pre-wiped before this scan; these operators have already been victimized.

---

## Version Distribution (where exposed)

| Version | Count |
|---|---|
| ES 7.17.x | Confirmed on 168.119.90.62 |
| ES 8.x | Several (version header present) |
| OpenSearch 2.x | 4 |
| Version not disclosed | Majority |

---

## Why This Matters

Elasticsearch ships with security disabled by default pre-8.0. The 7.x series (still in wide production use for 8+ year deployments) requires explicit `xpack.security.enabled: true` configuration. Most operators running fresh deployments on cloud VMs from tutorials do not add this. Elasticsearch 8.x enables security by default, but many installations disable it for "simplicity."

The consequence: the production database of an AML/KYC platform with 79 million records is accessible with a single unauthenticated GET.

---

## Probe Tooling

- `data/aiapp-probe.py` — Elasticsearch prober: `/_cat/indices?format=json`, `/{index}/_search?size=2` per non-system index
- httpx filter: `/home/cowboy/go/bin/httpx -p 9200 -path /_cat/indices -mc 200`

---

## Discoverer

NuClide Research — nicholas@nuclide-research.com

No data was modified or exfiltrated. Search queries used `size=2` to confirm data accessibility only.
