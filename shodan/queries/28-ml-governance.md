# 28. ML Governance / Data Catalog / Lineage

_Section created: 2026-05-29 (survey ml-governance-2026-05-29)_

Data catalogs, ML metadata stores, lineage trackers, governance platforms. An
exposed data catalog is a reconnaissance goldmine: one API call reveals every
database, schema, PII tag, and connection string in an organization. The map to
the data estate.

**Category verdict (2026-05-29):** well-secured at population scale. Auth-on
platforms (OpenMetadata) run patched versions; auth-off platforms (DataHub GMS,
Marquez) are either Shodan-dark, not-deployed-to-public, or empty demos. Thesis
confirmed by the secure branch.

## Verified dorks

| Dork | Total | Yield |
|------|------:|-------|
| `http.title:"OpenMetadata" port:8585` | 56 | CLEAN, all real OpenMetadata. Port 8585 is OpenMetadata-specific, low FP. |
| `http.title:"DataHub" port:9002` | 27 | CLEAN DataHub frontends. The GMS backend on :8080 is the auth-off-default surface (was not exposed on any sampled host). |
| `http.html:"ckan" port:5000` | 53 | Real CKAN open-data portals (gov). Reads open by design. |
| `http.title:"Marquez"` | 50 | ~50% real Marquez (OpenLineage). Surname collisions are the other half. |

## Verification probes

| Platform | Probe | Confirms |
|----------|-------|----------|
| OpenMetadata | `GET /api/v1/system/version` (unauth, INFO) then `GET /api/v1/tables` (401 = gated) | version for CVE-2024-28255 bucketing (bypass needs <1.3.1); catalog auth state |
| DataHub GMS | `GET :8080/config` -> JSON `noCode` field | GMS auth-off (high-value); :8080 refused = secure deploy |
| Marquez | `GET /api/v1/namespaces` (often on :3000 UI port) | unauth lineage; `metalake_demo` namespace = tutorial/demo |
| CKAN | `GET /api/3/action/status_show` -> `ckan_version` | identity (open by design) |

## FP traps (do NOT re-run / filter)

| Dork | Total | Trap |
|------|------:|------|
| `port:21000 http.title:"Atlas"` | 0 | Atlas UI title not literally "Atlas". Atlas is Shodan-dark on tier-2 cloud anyway (Cloudera/HDP internal-network). |
| `http.html:"api/atlas/v2"` | 0 | Atlas API path not in crawled HTML. |
| `http.html:"ckan_version"` | 0 | `ckan_version` is in the `/api/3/action/status_show` JSON body, NOT crawled HTML. Use `http.html:"ckan"`. |
| `http.html:"marquezproject"` | 0 | Marquez serves JSON/React; string not in crawled HTML. Use `http.title:"Marquez"` and filter surnames. |

## CVE watch

- **CVE-2024-28255 (OpenMetadata, CVSS 9.8)**, auth bypass via JwtFilter path-param injection, affects < 1.3.1, exploited in wild (Microsoft TI, April 2024). 2026-05-29 sample: 10/10 hosts ran 1.10-1.12, none vulnerable. Version-bucket every OpenMetadata hit before claiming this CVE.
- **CVE-2024-28253/28254 (OpenMetadata)**, authenticated SpEL RCE. Requires auth, so chains off the bypass on unpatched hosts.
- **CVE-2023-32321 (CKAN)**, path traversal + RCE via crafted resource IDs.
- **DataHub GMS**, JWT signatures not cryptographically verified (GitHub Security Lab); forge any user when GMS reachable. No CVE assigned.

## Apache Atlas, DataHub GMS, Marquez are auth-off-by-design

The auth-off surfaces in this category are real in the software but were not
deployed open at population scale on 2026-05-29. DataHub GMS bound internal,
Marquez instances empty or DB-down, Atlas off public cloud entirely. Recheck as
the category grows: an OpenMetadata < 1.3.1 or a public DataHub GMS :8080 is a
full data-estate map.
