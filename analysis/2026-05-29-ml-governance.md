# Session Analysis: ML Governance / Data Catalog survey

## 1. Overview

### Objective
First population survey of the ML governance category: data catalogs, ML metadata
stores, lineage trackers. Test the auth-on-default thesis on a class where the
flagship platforms (OpenMetadata, DataHub) ship auth-on and the lineage tools
(Marquez, Amundsen) ship auth-off. Pre-survey intel:
data/platform-intel/ml-governance-osint-2026-05-27.md.

### Scope and Constraints
Commercial tier-2 and hyperscale cloud (GCP, AWS, Azure, OVH, Contabo, Huawei,
Aliyun). Shodan via Playwright web UI, both API keys dead. All probing through
Mullvad (us-lax-wg-007). Metadata-only marker probes; no default-credential
attempts, no payloads, no data reads beyond namespace/version metadata.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. Shodan harvest by browser automation, paced after a
Cloudflare rate-limit. aimap and recon tools as bounded background commands.
Verification by curl through Mullvad.

### Tools Used
Full 19-tool arsenal. Material output: JAXEN, aimap, aimap-profile, VisorGraph,
VisorBishop, menlohunt, VisorLog, VisorScuba, BARE, cortex. Documented non-runs:
VisorSD/recongraph/nu-recon/VisorPlus (Shodan-key blocked), VisorGoose (gov/edu
scope), VisorCorpus/VisorAgent/VisorRAG (no LLM-adjacent surface; ethical-stop),
VisorHollow (Windows-only), JS-bundle (catalogs serve own UI).

### Notable Configuration
aimap v1.9.39. nuclide.db at ~/visorlog/nuclide.db (visorlog ingest --db
explicit, lesson carried from cat-17). Workspace ~/recon/ml-governance-2026-05-29/.

## 3. Methodology

### Enumeration approach
Nine dorks across six platforms, title-anchored and port-anchored. OpenMetadata
and DataHub have platform-specific ports (8585, 9002) with low FP.

### Candidate identification
56 OpenMetadata, 27 DataHub, 53 CKAN, 50 Marquez (~50% real). Atlas zero.

### Validation checks
OpenMetadata: version-bucketing via /api/v1/system/version, then /api/v1/tables
for auth state. DataHub: GMS /config on 8080. Marquez: /api/v1/namespaces.
Restraint: no default creds, no data reads beyond metadata.

### Safeguards
Mullvad verified before and during. No DataHub datahub/datahub login attempt (the
frontend gate is the control; trying creds is active auth beyond marker scope).
No CKAN write operations. Marquez read namespace names only.

## 4. Execution Trace

```
1. Read ml-governance platform intel + methodology
2. Mullvad verified (us-lax-wg-007)
3. Playwright: OpenMetadata dork -> 56; DataHub -> 27
4. Atlas: 3 variants (title, api-path, "Apache Atlas") all 0 -> Shodan-dark
5. Cloudflare rate-limit hit on CKAN dork; paced (no reload), recovered
6. CKAN: ckan_version 0 (JSON-dark), html:"ckan" -> 53 gov portals
7. Marquez: marquezproject 0, title:"Marquez" -> 50 (~50% real)
8. OpenMetadata verify: 10/10 /api/v1/system/version 1.10-1.12 (CVE-2024-28255 patched)
9. OpenMetadata /api/v1/tables -> 401 (catalog gated) on 3 sampled
10. DataHub GMS :8080 -> 000 on 10/10 (not exposed; secure)
11. Marquez verify: 136.114.205.74:3000 unauth (default+metalake_demo, 0 jobs/datasets);
    48.217.48.173 -> 500 PSQLException (DB down)
12. aimap lean 25 hosts x 11 ports -> 12 services, 1 unauth (Marquez)
13. aimap-profile: unclassified/commercial, no honeypot, no ethics flags
14. menlohunt IP-shadow on Marquez host -> SSH + Marquez only, 0 chains (isolated)
15. VisorGraph 0 nodes; VisorBishop severity=none, no ip-shadow
16. VisorLog: 25 events via aimap adapter -> nuclide.db
17. VisorScuba: 25 passing/0 violations; BARE: no MSF coverage
18. Wrote case study, query file 28-ml-governance.md, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 Marquez 136.114.205.74 (GCP): unauthenticated lineage API, demo
MEDIUM. /api/v1/namespaces unauth: default + metalake_demo, 0 jobs, 0 datasets.
Auth-off-default confirmed; no production data.

### 5.2 OpenMetadata x10: unauthenticated version disclosure, patched
INFO. /api/v1/system/version unauth (by-design), versions 1.10-1.12. CVE-2024-28255
needs <1.3.1; none vulnerable. Catalog 401-gated.

### 5.3 DataHub GMS: not exposed (secure)
0/10 expose :8080. Frontend-only. 3.30.235.161 = AWS us-gov-west-1.

### 5.4 Apache Atlas: Shodan-dark
0 across 3 variants. Cloudera/HDP internal-network. Category-tenancy negative.

### 5.5 CKAN x53: open by design
Government open-data portals; reads unauth by design. Not a finding.

## 6. Risk Assessment

### Overall Posture
Well-secured at population scale. The auth-on-default thesis holds by its secure
branch: OpenMetadata ships auth-on, operators patch, the population is closed.
Marquez ships auth-off and the one reachable instance is open, but empty.

### Confidentiality
A data catalog is the map to the data estate. None of the sampled production
catalogs leaked it. The version string disclosure is INFO.

### Integrity
DataHub GMS JWT non-verification would let an attacker forge any user, but GMS
was not reachable on any sampled host.

### Availability
No availability findings.

### Systemic Patterns
- Version-bucketing is the discriminator (extends Insight #16: a 200 from a
  version endpoint is identity, not auth state, and the version decides exploitability).
- Shipping default is load-bearing both ways (cat-17 auth-off bled; ML-gov auth-on holds).
- Category-tenancy negative for Atlas (internal-network product, cf. NVIDIA Clara).

## 7. Recommendations

### R1: Upgrade OpenMetadata below 1.3.1
CVE-2024-28255 is exploited in the wild. None sampled were vulnerable; the rule
stands for the unsampled tail.

### R2: Keep DataHub GMS off public 8080
And change the datahub/datahub frontend default.

### R3: Auth in front of Marquez/Amundsen
They ship auth-off. Reverse proxy or localhost bind.

```
# Marquez: do not expose the API unauthenticated
# front with nginx + auth_basic, or bind the container to 127.0.0.1
```

## 8. Limitations

Atlas Shodan-dark, not enumerated (needs internal-network access). CKAN open-by-
design reads masked the real CKAN finding classes (token leak, CVE-2023-32321),
not pursued. Samples were page-one, not full populations. DataHub frontend
default creds not tested (active auth beyond marker scope).

## 9. PoC Illustrations

```
# OpenMetadata: version unauth (INFO), catalog gated
$ curl -s http://34.128.90.229:8585/api/v1/system/version
{"version":"1.11.6","revision":"f5e54333...","timestamp":1768994525447}
$ curl -s -o /dev/null -w '%{http_code}' http://34.128.90.229:8585/api/v1/tables
401

# Marquez: unauth namespaces, demo (metalake_demo = tutorial)
$ curl -s http://136.114.205.74:3000/api/v1/namespaces | jq '.namespaces[].name'
"default"
"metalake_demo"

# DataHub GMS: not exposed (secure)
$ curl -s -o /dev/null -w '%{http_code}' http://3.30.235.161:8080/config
000
```
