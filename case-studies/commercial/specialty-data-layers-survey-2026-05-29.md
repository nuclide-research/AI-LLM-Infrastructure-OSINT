# Specialty Data Layers survey, 2026-05-30

_Survey type: category survey of specialty data layers behind AI stacks: columnar
stores, feature stores, compute-history servers. Pre-survey intel:
data/platform-intel/specialty-data-layers-osint-2026-05-27.md._

## Summary

Three of five sampled Spark History Servers exposed their job inventories with no
authentication, and two of them are machine-learning pipelines. The job names are
the finding. They map the feature-engineering, training, and prediction stages of
an ML workflow on Google Cloud. ClickHouse returned 5,208 hosts on the empty-
password port, but confirming the unauthenticated-query finding requires executing
SQL against production databases, which the scope discipline did not permit. The
population is real; the unauth claim is unverified, and this writeup says so.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.title:"ClickHouse" port:8123` | 5,208 | huge, empty-password default class |
| `http.title:"History Server" port:18080` | 33 | Spark History Servers |
| `port:6566 "feature_names"` (Feast) | 0 | JSON-dark |

ClickHouse is the large population, 5,208 on the HTTP port, heavily the United
States, Germany, and China. Spark History Server returned 33, Google Cloud
dominated. Feast returned zero because it serves JSON and its strings are not in
the crawled HTML, the Insight #67 pattern.

## Stage 2, Verify

**Spark History Server, three of five open, two of them ML pipelines.**
`GET /api/v1/applications` is a REST job-list endpoint, the same class of marker
probe as a policy list, not a query. Three hosts answered with their application
inventory and no authentication:

- 34.145.73.130 on Google Cloud held 47 applications: `gen-traintable-job`,
  `gen-predtable-job`, `trainingjob-*`, `test_graph_gcs`. The names map a feature-
  table generation, training, and prediction pipeline.
- 35.247.60.56 held 9: `gen-traintable-job`, `livy-session`, batch job IDs.
- 20.22.162.38 held 4, all `SparkLoggingTestV2`, a test instance.

The job names are the finding. They disclose the structure of the ML workflow.
Spark History Server's per-application environment page can contain
`spark.hadoop.fs.s3a.access.key`, the AWS credential the operator passed to the
job. That page was not pulled. The job inventory confirms the unauthenticated
exposure and the AWS-key surface without reading the keys.

**ClickHouse, the line the survey did not cross.** ClickHouse ships with an empty
password for the default user, and the reputation of the 5,208-host population is
open SQL. Confirming that requires sending a query, `GET /?query=SELECT+1`, to a
production database the survey selected from Shodan. That is a different class of
action from reading a status endpoint, and `system.environment`, the table that
holds the operator's secrets, is the documented escalation. The scope discipline
gated it. `GET /ping` returned `Ok.` on all six sampled, confirming live
ClickHouse. The unauthenticated-query finding is unverified, and the population is
reported as exactly that, a population, not a count of open instances. A 200 from
a health check is not an auth state, which is Insight #16.

## Stage 3 through 7, the arsenal

aimap v1.9.40 fingerprinted all six Spark hosts as Apache Spark UI at high
severity, the fingerprint already in the catalog. menlohunt swept the 47-job ML
pipeline host and found it isolated, no stacked services, the host firewalled to
the one port. Two unauthenticated Spark hosts and the ClickHouse population landed
in nuclide.db.

## Impact

- **ML pipeline disclosure.** Two unauthenticated Spark History Servers expose the
  job structure of a machine-learning pipeline: feature-table generation,
  training, and prediction. The names map the workflow.
- **AWS credential surface.** Spark History Server's environment page holds the
  S3 access key the operator passed to the job. It is reachable without auth on
  these hosts. It was not pulled.
- **ClickHouse population.** 5,208 hosts on the empty-password port. The open
  subset is unmeasured here because the survey did not query production databases.

## Remediation

- Put Spark History Server behind authentication or a reverse proxy. It ships
  open, and the environment page leaks cloud credentials.
- Pass S3 credentials to Spark through an IAM role or a secret manager, never as a
  job property visible in the History Server environment.
- Set a ClickHouse password and restrict `listen_host`. The empty-password default
  is the documented exposure.

## What the method could not see

The ClickHouse open-subset count needs a query the survey would not run. Feast,
Cassandra, and the native-protocol data stores are not HTTP-probeable and need
protocol handshakes. Redis and MinIO were heavily covered in prior surveys. The
Spark sample was five of 33.

## Note on scope and footprint

Mullvad was down and the verification ran off-VPN with operator authorization. The
ClickHouse SQL verification was declined: executing queries against production
databases selected from Shodan is outside what a generic directive authorizes, and
the auto-mode gate enforced that line. Recorded for an honest account of both the
footprint and the restraint.

## Toolchain provenance

```
JAXEN        Playwright; 3 dorks (ClickHouse 5208, Spark 33, Feast 0)
aimap        v1.9.40; 6/6 Spark hosts -> Apache Spark UI (high), fingerprint in catalog
aimap-profile N/A this run
VisorGraph   bare cloud IPs, 0 nodes
VisorBishop  menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    34.145.73.130 IP-shadow: isolated, 0 findings
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only
VisorPlus    components individual
VisorLog     2 Spark unauth (high) + 1 ClickHouse (info) -> nuclide.db
VisorScuba   Spark-unauth / ClickHouse not mapped to a control (gap)
BARE         data-layer authz first-party class
VisorCorpus  N/A no inference surface
VisorAgent   controlled-target only; not fired at survey hosts
VisorRAG     N/A
VisorHollow  N/A Windows-only
cortex       codify-stage
JS-bundle    N/A Spark UI / ClickHouse, no secret bundle
```
