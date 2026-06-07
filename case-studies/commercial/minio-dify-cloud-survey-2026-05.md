---
type: survey
---

# MinIO + Dify on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Two parallel sweeps:

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5868, T5882, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K7024

<!-- ksat-tag:auto-generated:end -->

- **MinIO (port 9000):** masscan → 9,513 hits → **852 confirmed MinIO instances**, every one on the public internet. Of these, 747 are Console-on-port-9000 (admin UI exposed for brute-force), 75 are plain MinIO API, 4 are MinIO AIStor (commercial). **27 instances expose version strings (older-than-2021 releases) → all CVE-2023-28432 / CVE-2024-24747 vulnerable.** No anonymous-list-buckets observed (operators DID configure auth), the threat is credential brute-force + version-CVE exploitation, not direct anonymous read.
- **Dify (port 5001):** masscan → 8,162 hits → **only 5 confirmed Dify instances**, all with `setup_step: finished` (no setup-wizard takeover possible). Dify is typically deployed behind nginx on 80/443; port 5001 is the internal API and rarely exposed directly.

The MinIO finding is the larger of the two, and complements the prior MLflow survey, several MLflow instances reference `s3://` paths that are likely served from instances in this MinIO surface.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 9000 --rate 10000  (MinIO)
  → 9,513 port-9000 hits

masscan -iL <28 cloud /16 CIDRs> -p 5001 --rate 10000  (Dify)
  → 8,162 port-5001 hits

minio-probe.py
  GET /                       → match `Server: MinIO` header
  GET /minio/health/live      → confirm health
  GET /                       → parse S3 XML for anonymous bucket list (if present)
  GET /login                  → check for "MinIO Console" HTML
  → 852 confirmed MinIO

dify-probe.py
  GET /console/api/setup           → {"step":"finished"|"not_initialized"}
  GET /console/api/system-features → auth/branding config
  GET /console/api/version         → version
  → 5 confirmed Dify (all initialized)
```

NuClide did not attempt MinIO default credentials, did not POST to the Dify setup wizard, and did not interact with any operator's data.

---

## MinIO Findings (852 instances)

### Auth posture

| Server header | Count | Posture |
|---|---|---|
| `MinIO Console` (admin UI on :9000) | 747 | Brute-force / default-cred surface |
| `MinIO` (S3 API, no version disclosed) | 75 | Auth-required, API exposed |
| `MinIO AIStor` | 4 | Commercial offering, auth-required |
| `MinIO/RELEASE.<date>` (versioned, older) | 27 | CVE-vulnerable |
| Anonymous `/` returns S3 ListAllMyBucketsResult | **0** | (none observed, operators do enforce auth) |
| Anonymous `/` returns AccessDenied (proper auth) | 4 | Confirmed auth in place |

The 0 anonymous-bucket-list result is the interesting negative finding. Earlier expectations (based on the public reputation of MinIO default-creds problems) suggested significant anonymous-bucket-listable surface. None observed in this 852-instance cloud sample. The exposure mode here is the next layer in: **credential brute-force on the Console UI** and **version-CVE exploitation on older releases**.

### Version-disclosed older MinIO (CRITICAL)

27 instances expose old MinIO Server headers, all are vulnerable to one or more of:

- **CVE-2023-28432** (info disclosure of admin secrets via `/minio/bootstrap/v1/verify`), affects everything < `RELEASE.2023-03-20T20-25-46Z`
- **CVE-2024-24747** (auth bypass on certain admin endpoints)
- **CVE-2024-29892** (SSRF)

| Release | Count | Notes |
|---|---|---|
| `RELEASE.2019-08-07T01-59-21Z` | **9** | Same exact release on 9 distinct IPs, Docker-image template propagation pattern |
| `RELEASE.2020-10-03T02-19-42Z` | 2 | |
| 16 other 2019-2020 releases | 1 each | Long tail of frozen-version operators |

The cluster of 9 instances on the identical 2019-08-07 release is the most distinctive finding. Six years out of date, identical hash, distributed widely, likely a third-party hosting-provider template (e.g., a "1-click MinIO on DigitalOcean" image from 2019 that got installed by 9+ users and never updated).

### Console-on-port-9000 (HIGH)

747 instances expose `MinIO Console` HTML on port 9000 (newer single-port deployments default to this; older deployments split Console to 9001). The login page itself is not an exploit surface, but:

1. **Default credentials**: `minioadmin:minioadmin` is the canonical MinIO default. Operators who haven't changed it are exposed to direct login.
2. **Brute-force**: 747 login forms means substantial attacker dictionary surface. MinIO does have built-in rate limiting but it's per-IP and bypassable with a moderately-distributed source pool.
3. **Information disclosure on login error pages**: some MinIO Console versions return distinguishable error messages for "user-doesn't-exist" vs "bad-password", which leaks valid usernames.

NuClide did not attempt credentials.

### Cross-correlation with MLflow survey

The prior [mlflow-cloud-survey-2026-05.md](mlflow-cloud-survey-2026-05.md) showed several MLflow Tracking Server instances pointing to S3 buckets:

| MLflow instance | S3 bucket reference | Possibly served by MinIO? |
|---|---|---|
| `138.197.152.103` | `s3://aipod-crop/` | Likely external S3 (AWS) given the bucket name |
| `188.166.132.129/.104` | `s3://flow-bucket/` | Possibly an adjacent MinIO host |
| `159.69.35.23` | `s3://mlflow/` | Likely on a co-located MinIO |
| `168.119.201.8/.89` | `s3://mlflow/` | Likely co-located |

Without explicit IP→bucket mapping, the cross-correlation is conjectural. Operators running MLflow + MinIO on adjacent IPs in our cloud /16 surface are likely paying for both exposures simultaneously.

---

## Dify Findings (5 instances)

Sparse result, Dify is typically fronted by nginx on 80/443 in production, with 5001 being the internal API container port. Direct exposure of 5001 is unusual and appears to be exclusively pre-production / dev-environment deployments.

| IP | Setup state | Email-password login | Email-code login | Notes |
|---|---|---|---|---|
| (5 instances) | All `finished` | 4 of 5 enabled | mixed | All initialized, no setup-wizard takeover possible |

The "setup-wizard takeover" attack class, where `setup_step: not_initialized` would allow any internet client to POST admin credentials and become superuser, was the headline threat we expected to find. **Zero observed.** Either:

1. Operators run Dify via the official Docker Compose, which ships nginx on 80/443 and the operator completes setup quickly.
2. Pre-prod Dify deployments behind firewalls don't appear in the cloud /16 surface.

This is a clean negative finding, the upstream Dify project's defaults plus operator behavior are working.

---

## Cross-Survey Pattern (updated)

| Tier | Platform | Sample | Unauth |
|---|---|---|---|
| Vector DB | Qdrant / ChromaDB / Milvus | 142 | 100% |
| Inference | Triton / vLLM / Ollama | 388 | 100% |
| Image-gen | A1111 | 1 | 100% |
| MLOps | MLflow Tracking | 11 | 100% |
| **Object storage / S3-compat** | **MinIO** | **852** | **0% anonymous-list, ~3% CVE-vulnerable, ~88% Console exposed** |
| Data app | Streamlit | 551 | 100% |
| Agent platform | Dify | 5 | 0% |
| Orchestration UI | Flowise / n8n / Open WebUI / Langflow | 1170 | 0% (small misconfig %) |

MinIO breaks the pattern. The MinIO ecosystem has done what the vector-DB ecosystem hasn't: ship with auth required by default (since 2018), make the default-credentials warning prominent, and document the public-internet exposure model clearly. The result is **zero anonymous-bucket-listable instances in 852 confirmed**. The remaining exposure modes are version-CVE (operator never updated) and brute-force-on-Console (operator never changed default creds), both of which are operator-side problems rather than upstream-defaults problems.

Dify behaves the same way. Its upstream Docker Compose makes "hit the setup wizard once and lock in" easy enough that nobody we found left it incomplete.

The lesson is consistent: **auth-on-default upstream policy + clear documentation = ~zero unauth exposure at population scale**, even on a platform whose audience is "people running model artifacts on cheap cloud VPSes" who otherwise leak Qdrant/Milvus/MLflow at 100%.

---

## Disclosure Posture

The 27 version-disclosed older MinIO instances are time-sensitive (CVE-2023-28432 is widely scanned + actively exploited). Coordinated disclosure to DigitalOcean / Hetzner / Vultr abuse channels for those 27 is warranted.

The 747 Console-exposed instances are an awareness-level finding, every one has a real exposure (default-creds-on-the-internet) but disclosing 747 individually is past triage capacity. This is upstream-MinIO territory: a "default credential warning that gates the first login" change would help, similar to MongoDB's auth-required-by-default shift in v3.6.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | masscan port 9000 → 9,513 IPs; masscan port 5001 → 8,162 IPs |
| Fingerprint | `minio-probe.py` (Server-header match), `dify-probe.py` (`/console/api/setup` shape) |
| What was NOT done | No default-credential attempts; no setup-wizard POSTs; no bucket reads |

---

## References

- MinIO security: https://min.io/docs/minio/linux/operations/security.html
- CVE-2023-28432: https://nvd.nist.gov/vuln/detail/CVE-2023-28432
- CVE-2024-24747: https://nvd.nist.gov/vuln/detail/CVE-2024-24747
- Dify deployment guide: https://docs.dify.ai/getting-started/install-self-hosted
- Cross-survey index: [index.md](index.md)
- 2026-05 cross-survey synthesis: [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md)
