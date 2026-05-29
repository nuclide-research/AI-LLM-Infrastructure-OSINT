# Experiment Tracking, registry and RCE half, 2026-05-29

_Survey type: category survey, registry and RCE half. The compute-orchestration
half (ClearML, Prefect, Dask, BentoML) ran 2026-05-26. This leg covers the
high-severity trackers the intel flagged: Ray ShadowRay, MLflow registry,
Determined.ai admin:blank, Aim. Pre-survey intel:
data/platform-intel/experiment-tracking-osint-2026-05-27.md._

## Summary

MLflow ships with no authentication, and the population shows it: eight of eight
sampled servers returned the full experiment list with no credentials. One held
379 experiments and leaked a Google Cloud Storage bucket name. The other
high-severity targets did not deliver. Determined.ai was authenticated on every
reachable host, including two on AWS GovCloud, so the admin:blank default did not
appear. Ray and Aim are Shodan-dark behind React single-page apps.

One category, both ends of the auth-on-default curve. MLflow ships auth-off and
bleeds. Determined ships with a credential and holds.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.title:"MLflow" port:5000` | 370 | clean, the big unauth population |
| `http.title:"Determined" port:8080` | 6 | 4 real plus 2 "could not be determined" error pages |
| `port:8265 http.title:"Ray"` | 1 | one host, crawl date weeks stale |
| `http.html:"ray dashboard" port:8265` | 0 | React SPA, string not in HTML |
| `port:43800 http.html:"aim"` | 0 | React SPA, JSON-dark |

MLflow was the population. 370 hits across the United States, Germany, China,
India, and the Netherlands, on GCP, E2E Networks, Scaleway, netcup, and Azure.
Ray's literal "ray dashboard" string returned zero because the dashboard is a
React app; the title "Ray Dashboard" returned one host, weeks old. Aim on port
43800 returned zero for the same reason. The ShadowRay-exposed Ray population and
the Aim population are real but Shodan-dark, the Insight #67 pattern again.

## Stage 2, Verify

**MLflow, eight of eight open.** Every sampled host answered
`GET /api/2.0/mlflow/experiments/search` with no token. Experiment counts ran
from 4 to 379. Restraint held: experiment names and artifact locations only, no
run parameters, no metrics, no artifacts.

The headline is 34.139.85.153 on Google Cloud. It served 379 experiments
unauthenticated and its artifact locations pointed at
`gs://aircheck-mlflow-tracking`. The bucket name is the finding. "aircheck" maps
to a drug-discovery machine-learning effort, and the bucket name attributes the
operator and names the storage backend without touching it (Insight #18). The
bucket itself was not probed.

aimap confirmed all eight as MLflow and flagged each critical, because its
enumerator appends CVE-2024-37052 through 37060, the model-deserialization RCE
class, on service identity alone. That is a known aimap behavior: the CVE is
applicable-class, not version-confirmed. The tier label here is HIGH for
confirmed unauthenticated catalog access, not CRITICAL, because the version was
not checked against the vulnerable range. The registry model-poisoning surface is
present: an unauthenticated write can register a backdoored model and set its
stage to Production. It was not exercised.

**Determined.ai, authenticated everywhere.** Four real hits, two of them on AWS
us-gov-west-1. All four returned 401 or 501 to `GET /api/v1/me` with no token.
The admin:blank default the intel flagged did not appear on the live sample.
Operators set credentials. No finding.

## Stage 3 through 7, the arsenal

menlohunt swept the 379-experiment host for adjacent services and found only SSH,
the MLflow port, and an 8080 HTTP-alt. No stacked Redis, no MongoDB, zero chains.
This operator isolated the host, unlike the voice-AI and guardrail stacked hosts
the same day. The exposure is the MLflow and the bucket reference, nothing more.

BARE found no Metasploit coverage for the MLflow finding class. aimap-profile
returned commercial and no honeypot. Twelve events landed in nuclide.db.

## Impact

- **Full experiment inventory, eight hosts.** An unauthenticated MLflow exposes
  every experiment, run, parameter, metric, and artifact path. The 379-experiment
  host exposes a production drug-discovery pipeline's tracking data.
- **Cloud storage attribution.** The leaked `gs://aircheck-mlflow-tracking` bucket
  names the operator's storage backend.
- **Model poisoning.** Unauthenticated registry write lets an attacker promote a
  backdoored model to Production. The surface is present on all eight.

## Remediation

- Put MLflow behind authentication or a reverse proxy with auth. It ships with
  none and binds to 0.0.0.0 when exposed.
- Lock the artifact storage bucket independent of the tracking server.
- Pin MLflow to a version past the CVE-2024-37052 deserialization fixes and
  disable model loading from untrusted sources.

## What the method could not see

Ray and Aim are Shodan-dark behind their React apps. The ShadowRay population
(CVE-2023-48022, architecturally auth-off, SSRF to cloud metadata) needs a
masscan pass on port 8265, not Shodan. The MLflow sample was eight of 370. The
ShadowRay RCE and the MLflow model-poisoning write were both left unexercised by
the restraint ethic.

## Toolchain provenance

```
JAXEN        Playwright; 5 dorks (MLflow 370, Determined 6, Ray 1, Aim 0)
aimap        lean 13 hosts; 8/8 MLflow unauth; enumMLflow CVE-2024-37052+ (applicable-class, hardcoded)
aimap-profile 34.139.85.153 commercial, no honeypot
VisorGraph   bare cloud IPs, 0 nodes
VisorBishop  menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    34.139.85.153 IP-shadow: SSH + MLflow + 8080 only, 0 chains (isolated)
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only
VisorPlus    components individual
VisorLog     12 events via aimap adapter -> nuclide.db
VisorScuba   MLflow unauth maps to AI.C1
BARE         no MSF coverage (0.522) first-party/novel
VisorCorpus  N/A tracking servers not LLM-inference
VisorAgent   controlled-target only; not fired at survey hosts
VisorRAG     N/A no RAG surface
VisorHollow  N/A Windows-only
cortex       codify-stage
JS-bundle    N/A MLflow React UI + JSON API, no secret bundle
```
