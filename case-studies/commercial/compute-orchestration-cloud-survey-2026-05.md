---
type: survey
title: Compute Orchestration / Training tier, cloud survey 2026-05
date: 2026-05-06
class: substrate
category: compute-orchestration
status: surveyed
methodology: shodan-driven
---

# Compute Orchestration / Training: cloud survey 2026-05-06

NuClide Research

## Summary

A Shodan-seeded survey of the **Compute Orchestration / Training** tier of the
[category taxonomy](../../reference/category-taxonomy.md#compute-orchestration--training) confirmed
**118 unauthenticated exposures** across three platforms, Apache Spark (85),
Apache Airflow (29), Ray Dashboard (4), out of 203 candidate hosts surfaced
by three Shodan dorks.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7067, T5854, T5868, T5882, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K942, S7065

<!-- ksat-tag:auto-generated:end -->

Population-tier severity breakdown:

| Severity | Count | Composition |
|---|---|---|
| **Critical** | 12 | 8 Airflow unauth-dashboard (DAG enumeration WITHOUT auth via `/home`) + 4 Ray Dashboard unauth (CVE-2023-48022 ShadowRay surface) |
| **High** | 79 | Apache Spark, Master + Worker + Application UI exposed; cluster topology + driver Environment-tab credential leak surface |
| **Medium** | 25 | Apache Airflow login pages (version disclosure but auth-gated dashboard); 6 Spark Worker-only |
| **Low** | 2 | Apache Airflow `/api/v1/version` + `/health` only (component visibility, not admin) |

Single-day end-to-end execution: Shodan dork → fast-probe fingerprint → VisorGraph
cert-pivot → aimap-profile classification → nuclide-contact disclosure resolution
→ VisorLog ledger ingest → VisorScuba compliance scoring → BARE Metasploit-module
ranking → VisorCorpus adversarial corpus.

## Headline findings

### 1. The Airflow `/home` bypass: 8 unauth dashboards

Apache Airflow's web UI redirects `/` to `/home` when the user is logged in.
Operators who enable the `AnonymousUser` public role (commonly added during
testing and forgotten in production) reach the same `/home` *unauthenticated*
the redirect short-circuits to a fully populated DAGs listing, scheduler state,
and last-run history. The login page at `/login/` is still served, but the
dashboard is reachable around it.

This is **not an authentication bypass exploit**, it's the documented behavior
of `AUTH_ROLE_PUBLIC = "Admin"` (or `"Op"`) plus `WEB_SERVER_AUTH_TYPE = "AUTH_DB"`
with a public role that has full read access. Operator misconfiguration is the
attack path. Eight of 36 confirmed-Airflow hosts in this sample have the
configuration shipped open.

| IP | Operator | Provider | Severity |
|---|---|---|---|
| `81.200.154.252` | (Timeweb customer `cx90974`) | Timeweb (Russia/Kazakhstan) | Critical |
| `167.71.184.30` | (DigitalOcean customer) | DigitalOcean | Critical |
| `159.223.47.220` | (DigitalOcean customer) | DigitalOcean | Critical |
| `34.107.199.191` | (GCP customer) | Google Cloud | Critical |
| `34.120.202.253` | (GCP customer) | Google Cloud | Critical |
| `34.209.146.250` | (AWS customer, us-west-2) | AWS | Critical |
| `35.184.10.196` | (GCP customer) | Google Cloud | Critical |
| `52.2.224.249` | (AWS customer, us-east-1) | AWS | Critical |

Methodology lesson: a probe that only checks `/` will miss this category
entirely. The `/`-route returns an HTTP 302 to `/home`, and following the
redirect lands on the dashboard if the public role is configured. A naked
`/login/` check will catch the version-disclosure surface but report
"login-gated" when the dashboard is in fact open.

### 2. Ray Dashboard: 4 confirmed CVE-2023-48022 ShadowRay surface

Out of 26 Ray-dorked candidates, 4 hosts return the Ray Dashboard at root
without authentication. Ray's
[CVE-2023-48022 (ShadowRay)](https://nvd.nist.gov/vuln/detail/CVE-2023-48022)
is an unauthenticated job-submission RCE that has been actively exploited
since disclosure. The fix requires operator action (set `RAY_HEAD_NODE_ENABLE_AUTH=1`);
the framework default remains auth-off.

| IP | Operator | Provider |
|---|---|---|
| `100.48.41.65` | (AWS customer) | AWS EC2 |
| `34.193.202.61` | (AWS customer, us-east-1) | AWS EC2 |
| `44.216.229.38` | (AWS customer) | AWS EC2 |
| `94.124.160.20` | (Shock Hosting customer) | Shock Hosting |

The remaining 16 of the 26 Shodan hits had ports open but my fingerprint did
not match the Ray Dashboard root content shape, these are likely Ray Serve
deployments with custom basePath, or Ray instances behind a reverse proxy.
Worth follow-up probing on `/-/routes` and `/-/healthz` for Ray Serve
fingerprints.

### 3. Apache Spark: 85 hosts, three deployment shapes

Spark Master returns the cluster dashboard at `/` on port 8080 (or worker UI on
8081, application UI on 4040) with no authentication framework, Spark UI is
Tier-A "no-auth concept" by default. The dashboard discloses:

- Cluster topology (Master + Worker IPs + memory + cores)
- Currently-running applications + their driver IPs
- Recently-completed applications + their final state
- Per-application Environment tab (port 4040) which routinely leaks credentials
  embedded in `spark.hadoop.fs.s3a.access.key`,
  `spark.cassandra.connection.host`, `spark.streaming.kafka.bootstrap.servers`,
  and similar runtime config

**Geographic distribution** (post-dedup of repeated Korea host
`3.38.161.105`):

| Country | Confirmed |
|---|---|
| United States | 21 |
| China | 23 |
| Germany | 17 |
| France | 17 |
| Korea | 4 |
| (other / mixed) | 3 |

Spark's exposure rate is consistent with the auth-on-default-vs-off thesis:
the framework ships open by design (Spark UI assumes trusted-network
deployment) and operators who expose it on the public internet have not
bolted authentication on top via reverse proxy or k8s ingress.

## Methodology

**Scope:** the [Compute Orchestration / Training](../../reference/category-taxonomy.md#compute-orchestration--training)
tier as defined in the category taxonomy, Apache Spark, Apache Airflow, Ray
(Dashboard + Serve), Dask, Prefect, Temporal, Kubeflow / KServe, BentoML.
This survey covered Spark + Airflow + Ray; the remaining six platforms are
deferred to a follow-up sweep.

**Discovery:** three Shodan dorks (`http.html:"ray dashboard" country:"US"`,
`http.html:"apache airflow"`, `http.title:"Spark Master"`) executed manually
in the Shodan web UI (no API credits available). Top-5 country pages per
dork; dedupe + honeypot-list cross-reference produced 203 unique candidate
hosts; zero AS63949 honeypot overlap.

**Fingerprint and confirmation:** `aimap` (canonical fingerprinter)
encountered slow throughput in the multi-port + deep-enumerator path under
the active Mullvad VPN egress, so a 50-thread Python `fast-probe`
(`fast-probe.py`) ran in parallel and produced the canonical fingerprint
output. Each hit carries the platform's distinctive content token at HTTP 200
on the platform's documented port:

- Ray Dashboard: `<title>Ray Dashboard</title>` or `favicon.ico` reference + Ray-specific React bundle paths
- Apache Airflow: `<title>Airflow - Login</title>` (login-gated) or `<title>DAGs - Airflow</title>` (unauth admin via `/home`) plus `is_scheduler_running` meta tag
- Apache Spark: `Spark Master at` / `Spark Worker at` / `Spark Jobs` title
  pattern plus `<meta name="application-name" content="Spark">` and standard
  Spark UI HTML scaffold

**Auth-posture validation (Airflow):** a secondary `/home` re-probe
distinguished login-gated Airflow (the bulk) from `AnonymousUser`-public
Airflow (the 8 critical). The methodology lesson is captured under
`case-studies/commercial/SYNTHESIS-2026-05.md` (Methodology Insight #8, see
below).

**Attribution:** `visorgraph` cert-pivot per host produced operator-side
attribution where TLS was on; `aimap-profile --mode fast` provided
classification. `nuclide-contact` chained WHOIS abuse + DNS SOA + security.txt
+ pattern-guess+MX for disclosure recipient resolution per critical host.

**Severity scoring:** classify-and-ingest.py produces NDJSON in VisorLog ECS
shape; severity rules:

- Ray Dashboard reachable → **critical** (CVE-2023-48022 ShadowRay surface)
- Airflow with DAGs/admin reachable via `/home` → **critical** (anonymous
  public role enabled, full read+sometimes write)
- Airflow `/api/v1/version` + `/health` only → **low** (component visibility,
  not admin)
- Airflow login-gated → **medium** (version-disclosure surface only)
- Spark Master + Application UI → **high** (cluster topology + driver env
  credential leak)
- Spark Master OR Application UI alone → **high**
- Spark Worker only → **medium**

**Ledger ingest:** 118 findings written to `data/nuclide.db` via
`visorlog ingest --format ndjson`.

**Compliance scoring:** `visorscuba assess --db data/nuclide.db` evaluated
all 742 ledger nodes; our 118 produced 236 violations (118 × `AI.C1`
"AI services must not be publicly accessible without authentication" + 118
× `AI.H1`). Note: VisorScuba's policy templates are Ollama-tuned, the
violation message names "Unauthenticated Ollama" even for our Spark/Ray/Airflow
findings. Policy needs platform-aware text; tracked as policy-coverage gap.

**Exploit ranking:** BARE returned consistent rank-1 matches across all 91
critical/high findings:

| Platform | BARE rank-1 module | Coverage |
|---|---|---|
| Apache Spark | `exploits_linux_http_spark_unauth_rce` | 79/79 |
| Apache Spark (alt) | `exploits_linux_http_apache_spark_rce_cve_2022_33891` | 79/79 |
| Ray Dashboard | `exploits_linux_http_ray_agent_job_rce` | 4/4 |
| Apache Airflow | `exploits_linux_http_apache_airflow_dag_rce` | 8/8 |

Every critical/high finding maps to a documented Metasploit commodity-CVE
module, these are not first-party authz bugs. The unauth dashboards are
known-CVE attack surface.

**Adversarial corpus:** `visorcorpus build -profile strict -type baseline
-max 200` produced a 137-case corpus
(`visorcorpus-compute-orch.json`) for downstream LLM/RAG validation by
operators consuming this disclosure.

## Disclosure routing: 12 critical hosts

| Critical host | WHOIS org | Primary recipient |
|---|---|---|
| `100.48.41.65` (Ray) | Amazon.com, Inc. | `aws-security@amazon.com` |
| `34.193.202.61` (Ray) | Amazon Technologies Inc. | `aws-security@amazon.com` |
| `44.216.229.38` (Ray) | Amazon.com, Inc. | `aws-security@amazon.com` |
| `94.124.160.20` (Ray) | Shock Hosting LLC | `abuse@shockhosting.com` |
| `159.223.47.220` (Airflow) | DigitalOcean, LLC | `abuse@digitalocean.com` |
| `167.71.184.30` (Airflow) | DigitalOcean, LLC | `abuse@digitalocean.com` |
| `34.107.199.191` (Airflow) | Google LLC | `google-cloud-compliance@google.com` |
| `34.120.202.253` (Airflow) | Google LLC | `google-cloud-compliance@google.com` |
| `34.209.146.250` (Airflow) | Amazon Technologies Inc. | `aws-security@amazon.com` |
| `35.184.10.196` (Airflow) | Google LLC | `google-cloud-compliance@google.com` |
| `52.2.224.249` (Airflow) | Amazon Technologies Inc. | `aws-security@amazon.com` |
| `81.200.154.252` (Airflow) | Timeweb, LLP (RU/KZ) | `abuse@timewebcloud.kz` |

Cloud-provider abuse channels forward to the customer; for Timeweb the
customer routing path is less established and a duplicate notification to
the operator-direct channel (where derivable from cert/reverse-DNS pivot)
is recommended.

## Methodology Insight #8: the Airflow `/home` bypass

A naked `/`-fetch reports Airflow as login-gated when its public role is
enabled. The dashboard reachability check must follow `/` → `/home` (302
target) and inspect for the `is_scheduler_running` meta tag plus DAG
listing. A login-gated instance returns the login template; a public-role
instance returns the same template the authenticated dashboard renders.

This pattern parallels Methodology Insight #6 (substring-FP at scale) and
#7 (Shodan-facet substring-FP) in [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md):
**a fingerprint that only inspects the entry-point response shape misses
auth-bypass-via-misconfiguration findings whose entry-point looks identical
to the login-required case.** Future surveys against application-tier
platforms (RAG framework, LLM orchestration, BI/Dashboard) should bake in
post-redirect auth-posture validation, not just landing-page fingerprinting.

## Cross-tier auth-posture observation

The compute-orchestration tier extends the auth-posture pattern documented
in [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md):

| Platform | Tier | Auth posture in default config | Confirmed exposure rate |
|---|---|---|---|
| **Apache Spark** | Infrastructure-for-engineers | "no auth concept" | 85 / 120 candidates → ~71% exposure |
| **Ray Dashboard** | Infrastructure-for-engineers | auth-off-default | 4 / 26 candidates confirmed unauth |
| **Apache Airflow** | Application-tier (auth available) | login required by default | 36 / 57 candidates → ~63% had Airflow + 8 (~14%) had public-role-enabled |

Apache Spark behaves like the [Vector Databases](../../reference/category-taxonomy.md#vector-databases)
tier, framework default is no-auth, exposure rate is high. Apache Airflow
behaves like the [LLM Orchestration](../../reference/category-taxonomy.md#llm-orchestration)
tier, framework default is auth-on, exposure is the ~10-15% misconfig
slice. Ray Dashboard sits between the two but skews infrastructure-side.

This empirically validates the cross-tier framing: **the framework default
IS the deployment.**

## Toolchain provenance

```
Shodan (manual web UI)        →  3 dorks
fast-probe.py                 →  126 confirmed unauth
visorgraph (per host)         →  attribution graphs
aimap-profile --mode fast     →  ethics + classification
classify-and-ingest.py        →  ECS NDJSON, 118 ledger events
visorlog ingest               →  data/nuclide.db updated
visorscuba assess             →  236 violations
nuclide-contact (per critical)→  disclosure recipients (12)
bare --top 3                  →  3 rank-1 Metasploit modules
visorcorpus build             →  137-case adversarial corpus
```

All artifacts at `~/recon/compute-orch-2026-05-06/` (NDJSON, JSONs, contact
files). Per-host attribution at `~/recon/compute-orch-2026-05-06/attribution/`.

## Future work

1. Re-probe the 16 Ray ports-open-no-match hosts on Ray Serve endpoints
   (`/-/routes`, `/-/healthz`), likely Ray Serve, not Ray Dashboard
2. Sweep the remaining six Compute Orchestration platforms, Dask, Prefect,
   Temporal, Kubeflow, KServe, BentoML, using the same Shodan-then-probe
   pattern documented above
3. Coordinated disclosure batch send to the 12 critical via the
   `disclosures/send_drafts_api.py` Gmail-API pipeline
4. Add platform-aware text to VisorScuba policies, current `AI.C1`
   violation hardcodes "Unauthenticated Ollama"
5. Fold confirmed findings into [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md)
   cross-tier table

## References

- Category taxonomy entry, [`reference/category-taxonomy.md#compute-orchestration--training`](../../reference/category-taxonomy.md#compute-orchestration--training)
- Future-surveys roadmap, [`FUTURE-SURVEYS.md#compute-orchestration--training-tier`](FUTURE-SURVEYS.md#compute-orchestration--training-tier)
- Cross-survey synthesis, [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md)
- CVE-2023-48022 (Ray ShadowRay), https://nvd.nist.gov/vuln/detail/CVE-2023-48022
- CVE-2022-33891 (Apache Spark unauth RCE), https://nvd.nist.gov/vuln/detail/CVE-2022-33891
