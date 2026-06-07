# ML Governance / Data Catalog survey, 2026-05-29

_Survey type: new-category population survey. Data catalogs, ML metadata stores,
lineage trackers. Pre-survey intel: data/platform-intel/ml-governance-osint-2026-05-27.md._

## Summary

Nine dorks. Six platforms. The category is well-secured at population scale, and
that is the finding. The auth-on platforms run patched versions. The auth-off
platforms are either Shodan-dark or empty demos. One unauthenticated Marquez
server confirmed, and it held no production data.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003, K942

<!-- ksat-tag:auto-generated:end -->

This is the auth-on-default thesis confirmed by its secure branch. Voice-AI
(cat-17, same day) shipped auth-off and bled. ML governance ships auth-on at the
catalog tier, operators patch, and the population holds. The shipping default is
load-bearing in both directions.

## Stage 0, Discover

| Platform | Dork | Total | Verdict |
|----------|------|------:|---------|
| OpenMetadata | `http.title:"OpenMetadata" port:8585` | 56 | clean, all real |
| DataHub | `http.title:"DataHub" port:9002` | 27 | clean frontends |
| Apache Atlas | `port:21000 http.title:"Atlas"` + 2 variants | 0 | Shodan-dark |
| CKAN | `http.html:"ckan" port:5000` | 53 | gov open-data, reads open by design |
| Marquez | `http.title:"Marquez"` | 50 | ~50% real, surname collisions |

Atlas returned zero across three variants (title, `api/atlas/v2` path, `"Apache
Atlas"`). Atlas lives in Cloudera and Hortonworks deployments on internal
networks, not public tier-2 cloud. The variant space is exhausted. This is a
category-tenancy negative, the same shape as NVIDIA Clara on the medical-edge
survey.

CKAN's `ckan_version` JSON-field dork returned zero because the field lives in
the `/api/3/action/status_show` JSON body, not the crawled HTML. The HTML dork
found 53 government open-data portals (Turkish and Indonesian municipalities).
CKAN reads are open by design for public data portals, so an open dataset list
is not a finding.

## Stage 2, Verify

The verification was version-bucketing, and it inverted the headline.

**OpenMetadata, the CVSS 9.8 that was not there.** CVE-2024-28255 is an
auth-bypass scored 9.8, exploited in the wild against Kubernetes clusters for
cryptomining. It affects versions below 1.3.1. The dork found 56 OpenMetadata
hosts. A survey that stopped at the dork would report 56 exposed catalogs with a
9.8 auth bypass.

The version endpoint settled it. `GET /api/v1/system/version` is unauthenticated
by design and returns the version string. Ten of ten sampled hosts ran 1.10.5
through 1.12.6. Every one is years past 1.3.1. None carry the bypass. The catalog
data endpoint confirmed the lock: `GET /api/v1/tables` returned 401 on every host
tested. The version string leaks, which is information disclosure at the INFO
tier. The data estate behind it is closed.

**DataHub, the backend that was not exposed.** DataHub's GMS service on port
8080 is authentication-off by default and is the high-value surface. Ten of ten
sampled hosts refused the connection on 8080. Only the frontend on 9002 faces
the internet, behind its login. The auth-off surface exists in the software and
was not deployed to the public internet on any sampled host. One host,
3.30.235.161, sits on AWS us-gov-west-1, frontend only.

**Marquez, the one open door, empty.** Marquez is authentication-off by default.
One host, 136.114.205.74 on Google Cloud, served `/api/v1/namespaces` with no
credentials. The namespaces were `default` and `metalake_demo`. The default
namespace held zero jobs and zero datasets. `metalake_demo` is the namespace
name from the Marquez tutorial. This is a demo deployment, open as the software
ships, holding no production lineage. A second Marquez host, 48.217.48.173,
returned HTTP 500 with a PostgreSQL connection error. The server is up and the
database is down, so it serves no lineage. The remaining sampled hosts did not
answer on the API ports.

## Stage 1 through 7, the arsenal

aimap confirmed the picture: twelve services, one unauthenticated. It flagged the
ten OpenMetadata hosts at fingerprint-default `critical` but its enumerator
correctly downgraded each to MEDIUM "unauthenticated version disclosure", the
same hardcoded-default-severity pattern aimap shows on MLflow and Flowise. Trust
the enumerator verdict, not the fingerprint default. It found the Marquez
unauthenticated namespaces and a Grafana on the same host as one OpenMetadata
instance, login-gated.

menlohunt swept the unauthenticated Marquez host for adjacent services and found
only SSH and the Marquez port. No stacked Redis, no exposed Postgres, zero attack
chains. Unlike the voice-AI stacked host the same day, this operator isolated the
service. VisorGraph and VisorBishop returned nothing: bare cloud IPs with no
certificate SAN to pivot and no adjacent unauthenticated surface. BARE found no
Metasploit coverage for either finding class. VisorScuba scored every host as
passing, which is correct for the version-disclosure INFO tier and a gap for the
Marquez unauthenticated API, which maps to no control.

## Impact

The category-level result is low risk and high confidence. The data catalog is a
reconnaissance goldmine when open: one exposed OpenMetadata or DataHub reveals
every database, schema, PII tag, and connection string in an organization. None
of the sampled production catalogs were open. The one open Marquez held no data.

The reconnaissance value of an exposed catalog is the reason to keep checking
this category as it grows. An open OpenMetadata below 1.3.1, or a DataHub with
GMS on a public 8080, would be a map to an entire data estate. The population did
not contain one today.

## Remediation

- OpenMetadata operators below 1.3.1 must upgrade now. CVE-2024-28255 is
  exploited in the wild.
- DataHub operators must keep GMS on 8080 off the public internet and change the
  datahub/datahub frontend default.
- Marquez and Amundsen ship authentication-off. Operators must put them behind a
  reverse proxy with auth or bind them to localhost.

## What the method could not see

Apache Atlas is Shodan-dark on public cloud and was not enumerated. A Cloudera or
Hortonworks census needs internal-network access, not Shodan. CKAN's open-by-
design reads mask the real finding classes for that platform: API tokens leaked
in resource descriptions and the path-traversal RCE CVE-2023-32321, neither
pursued here. The OpenMetadata and Marquez samples were page-one of the result
sets, not the full populations.

## Toolchain provenance

```
JAXEN        Playwright web UI; 9 dorks, 6 platforms (Cloudflare paced)
aimap        v1.9.39 lean 25 hosts x 11 ports; 12 services, 1 unauth
aimap-profile Marquez + gov-adjacent DataHub: unclassified/commercial, no honeypot
VisorGraph   0 nodes/edges (bare cloud IP, no cert SAN)
VisorBishop  3 hosts severity=none, no ip-shadow findings
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    Marquez host: SSH + Marquez only, 0 chains (isolated)
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only without live key
VisorPlus    components run individually
VisorLog     25 events via aimap adapter -> nuclide.db
VisorScuba   25 hosts passing (version-disclosure INFO; Marquez-unauth unmapped, gap)
BARE         no MSF coverage (0.547/0.427) first-party/novel
VisorCorpus  N/A no LLM-adjacent surface (catalogs, not inference)
VisorAgent   N/A controlled-target only; not fired at survey hosts
VisorRAG     N/A no RAG surface
VisorHollow  N/A Windows-only
cortex       run at codify on analysis
JS-bundle    N/A catalogs serve own UI, no CDN-SPA secret bundle
```
