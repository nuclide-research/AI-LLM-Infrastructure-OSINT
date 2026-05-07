---
to: abuse@digitalocean.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 138.197.152.103
institution: DigitalOcean — orthodontic-AI startup ("AIPOD") MLflow 2.2.1 actively exploited via CVE-2023-1177; 3-year persistent exposure
status: DRAFT
outcome: sent
date: 2026-05-06
---

**To:** abuse@digitalocean.com
**Cc:** abuse@nuclide-research.com
**Subject:** Actively-exploited MLflow 2.2.1 (CVE-2023-1177) on DigitalOcean droplet running orthodontic-AI R&D stack — 138.197.152.103

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** DigitalOcean customer host running outdated MLflow + Label Studio + persistent CVE-2023-1177 exploitation
**IP:** 138.197.152.103
**Severity:** HIGH

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

A DigitalOcean droplet at `138.197.152.103` is running an orthodontic-AI / dental-AI R&D stack with three publicly-reachable services in misconfigured states. The MLflow component is **actively being exploited** by an external attacker via **CVE-2023-1177** (path-traversal in MLflow's experiment artifact API).

| Port | Service | Auth | Issue |
|---|---|---|---|
| 5000/tcp | **MLflow 2.2.1** (released Feb 2023) | NONE | CVE-2023-1177 actively exploited — 18 attacker-injected experiments since 2026-03-26 |
| 8080/tcp | **Label Studio 1.5.0.post0** (Jul 2022 — 3 years stale) | Token required | CVE-2024-23633 LFR + CVE-2024-24566 SSRF apply to this version |
| s3://aipod-crop/ | AWS S3 (us-east-2) | Private (403) | Operator's artifact bucket; not directly exposed but the IP can be cred-pivoted to it via CVE-2023-1177 traversals to `/root/.aws/credentials` |
| 22/tcp | OpenSSH 8.9p1 (Ubuntu 22.04) | Key-only | Standard; not the exposure |

The operator (referred to here as **"AIPOD"** based on the S3 bucket name `aipod-crop`) appears to be a small dental-AI R&D team — no public-facing domain identified, opaque operator profile, only the bucket name and developer signatures from MLflow metadata.

## What's exposed (full operator-IP exfil from MLflow metadata)

`POST http://138.197.152.103:5000/api/2.0/mlflow/experiments/search` returns 24 experiments. Six are legitimate AIPOD work going back to **March 2023**:

| Year | Experiment | Domain |
|---|---|---|
| 2023 | `/demo-experiment` + `initial-model` + `real-exp` (~71 total runs) | Foundational image classifier on dental data |
| 2024 | `pan-segmentation` (13 runs) | Panoramic dental X-ray segmentation; datasets `pan_set_1, pan_set_2, pan_set_3` |
| 2025 | `ceph-keypoint` (14 runs) | Cephalometric (lateral skull X-ray) keypoint detection |
| 2026 | `orthodontic-upper-multitask` (19 runs, developer `gaurav`) | Multi-task upper-jaw arch + alignment classifier (R&D, ongoing) |

Developer roster extracted from `mlflow.user` + `mlflow.source.name`:
- `gaurav` (offshore developer; Mac, source path `/Users/gaurav/Documents/usa_work/ULClassification/`)
- `ubuntu` (production droplet user — the host itself)

Five `mlflow.source.git.commit` hashes are leaked: `34fb8541…`, `f32e5d52…`, `daa9915c…`, `dfe5665b…`, `0024a538…`. None match any public GitHub commits — the operator's repos are private.

Artifact storage is `s3://aipod-crop/artifacts/<exp_id>/<run_id>/artifacts/` for all runs. The bucket exists in us-east-2 (returns 403 to anonymous probes) but the access keys live somewhere on this droplet — most likely in `/root/.aws/credentials` or `/etc/environment`. CVE-2023-1177 path-traversal can reach those exact files.

## Active CVE-2023-1177 exploitation

24 total experiments on this host: 6 legitimate + **18 attacker-injected**. Each attacker experiment has the path-traversal pattern:

```
artifact_location: http:///#/../../../../../../../../../../../../../../etc/
artifact_location: http:///?/../../../../../../../../../../../../../../etc/
artifact_location: http:///#/../../../../../../../../../../../../../../root/.ssh/
```

Multiple distinct attacker campaign IDs are visible:

| Pattern | First seen | Targets |
|---|---|---|
| `3BT8ncOzBWAH4GyIGz0EXsSwj7f` (population-scale spray) | 2026-03-26 00:11 UTC | `/etc/` |
| `3CCGENufMtsxUjr3ij4gjsPM44m` | 2026-04-10 | `/etc/` |
| 16-char random-string campaigns (8 separate) | 2026-04-20 11:11 UTC (within ~30s burst) | `/root/.ssh/` (5 attempts) + `/etc/` (3 attempts) |
| `3D9V4JvPnDuvfxpSHZBQo1TTM3x` | 2026-05-01 22:54 | `/etc/` |
| `exp_103` (named) | 2026-05-05 08:37 | `/etc/` |
| `poc_exp` (named) | **2026-05-06 06:54 UTC** | `/etc/` |

The most recent injection landed **~16 hours before this disclosure**. The `/root/.ssh/` targeting on 2026-04-20 is particularly concerning — the attacker is hunting for SSH host keys / authorized_keys files, which would convert MLflow path-traversal into persistent root-shell access.

### Reproduction (non-destructive — list experiments, no data fetched)

```bash
$ curl -s 'http://138.197.152.103:5000/version'
2.2.1

$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"max_results":1000}' \
    'http://138.197.152.103:5000/api/2.0/mlflow/experiments/search' \
    | jq '.experiments[] | select(.artifact_location | contains("../"))| {name, artifact_location, creation_time}'
```

(Returns the 18 attacker-injected experiments with full artifact_location values.)

## Why this matters (for AIPOD)

- **Active root-shell pivot risk.** Attacker has been hunting `/root/.ssh/` for 17 days. If they exfil `id_rsa` or `authorized_keys` via the get-artifact step, they have persistent SSH access independent of the MLflow service.
- **AWS credential exfil → S3 bucket compromise.** The operator's `aipod-crop` S3 bucket holds 4 years of model artifacts (model weights, training-data references). CVE-2023-1177 traversal of `/root/.aws/credentials` would surface keys that unlock the bucket.
- **Patient-data exposure.** The `pan_set_1/2/3` references are panoramic dental X-ray training datasets — likely contain real patient imagery (dental AI training corpora are typically real-patient by necessity). No HIPAA / GDPR posture confirmed; if the operator is US-based serving US dentists, BAA chain matters.
- **Operator IP leakage.** 4 years of R&D progression (foundational classifier → panoramic seg → cephalometric keypoint → multi-task fusion) is documented in the experiment metadata. A competitor reading this has the operator's product roadmap.
- **3-year persistence.** First experiment created 2023-03-10. The droplet has been running this configuration for over 3 years — old enough that any successful compromise is likely already deep-rooted.

## Why this matters (for DigitalOcean)

The customer needs immediate notification. The fixes are operator-side and cheap (one-line config changes); the danger is that the operator may not be checking this droplet routinely (no `ubuntu` legit activity between 2024-05-04 and 2026-03-23 — 13 months of silence).

If DigitalOcean abuse can confirm whether the customer is responsive, that scopes the disclosure path. If unresponsive, escalation to AWS abuse (for the `aipod-crop` bucket, in case the keys have leaked) is warranted.

## Reproduction (continued — shows the persistent-exposure dimension)

```bash
$ # Three years of legit operator history visible:
$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"max_results":1000}' \
    'http://138.197.152.103:5000/api/2.0/mlflow/experiments/search' \
    | jq -r '.experiments[] | "\(.creation_time | tonumber / 1000 | strftime("%Y-%m-%d"))  \(.name)"' \
    | sort
2023-03-10  /demo-experiment
2023-03-17  initial-model
2023-03-20  real-exp
2024-03-26  pan-segmentation
2025-04-13  ceph-keypoint
2026-03-23  orthodontic-upper-multitask
[+ 18 attacker-injected experiments]
```

## Remediation (for the customer)

1. **Patch MLflow immediately** — upgrade to 2.10.0+ (CVE-2023-1177 patched in 2.3.1, multiple subsequent CVEs since). Bind to localhost or restrict via firewall:
   ```bash
   ufw deny 5000/tcp
   ufw allow from <admin-IP> to any port 5000
   ```
2. **Rotate AWS credentials** for the `aipod-crop` bucket — assume the keys on disk have been exfiltrated until proven otherwise; rotate now and audit S3 access logs.
3. **Audit `/root/.ssh/authorized_keys`** for unfamiliar entries. The 5 separate `/root/.ssh/` traversal attempts on 2026-04-20 represent attacker intent to install persistent SSH access. Compare current `authorized_keys` against the known-good baseline.
4. **Audit MLflow access logs** for `GET /get-artifact?path=` requests with the attacker run_ids listed in the table above. These would confirm whether the path-traversal exfil step (step 3 of the CVE-2023-1177 chain) actually executed.
5. **Upgrade Label Studio** from 1.5.0.post0 (3 years stale) to current 1.13+ — the 2024 LFR and SSRF CVEs (CVE-2024-23633, CVE-2024-24566) apply to 1.5.0.
6. **Delete the 18 attacker-injected experiments** after auditing them as evidence:
   ```bash
   for exp_id in 793104873966802295 561399937397099906 765385058040812500 \
                 432862210198838740 400948522244195620 254046331960495441 \
                 996456872754861465 809448534577103984 ... ; do
     curl -X POST 'http://localhost:5000/api/2.0/mlflow/experiments/delete' \
       -H 'Content-Type: application/json' \
       -d "{\"experiment_id\":\"$exp_id\"}"
   done
   ```

## Reference

Full case study (with operator timeline, developer roster, attack progression detail, and toolchain provenance):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-aipod-mlflow-cve-2026-05-06.md

CVE-2023-1177 advisory: https://nvd.nist.gov/vuln/detail/CVE-2023-1177

Original mlflow cloud survey (population-scale context for the actively-exploited finding):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mlflow-cloud-survey-2026-05.md

Happy to coordinate verification, or to extract the additional attacker UUIDs and timestamps needed for incident response.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
