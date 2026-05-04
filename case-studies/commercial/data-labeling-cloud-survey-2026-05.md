# Data Labeling / Annotation Servers — Cross-Cloud Survey (2026-05)

_NuClide Research · 2026-05-04 (in progress)_

> **Status:** Methodology + scaffolding complete. Discovery scan queued behind the MCP preview pass. Synthesis section will fill as data lands.

---

## Premise

Data-labeling and annotation servers (Argilla, LabelStudio, Prodigy, doccano, CVAT) sit at the **input boundary of every supervised-learning ML pipeline**. They host the raw data being labeled — frequently real customer PII, internal documents, facial imagery, medical scans, support-ticket transcripts, financial filings — and the labeling-team workforce metadata.

Operators stand them up quickly to crowd-source annotation, then forget to lock them down before walking away from the project. The auth posture varies sharply by platform:

- **Argilla** ships with auth on by default since v1.x — but anonymous workspaces and `default-public` settings are common in tutorial deployments.
- **LabelStudio** ships with mandatory auth out-of-the-box — but operator-deployed-without-RBAC instances expose `/api/projects` reads.
- **Prodigy** has **no built-in auth** — operators are expected to bolt on a reverse proxy. They often don't.
- **doccano** has auth but its `/v1/projects` endpoint can be made public for collaborative annotation.
- **CVAT** has auth on by default — but `/api/server/about` and project listing are sometimes left readable.

The auth-on-default thesis predicts: **Prodigy will be 100% unauth at population scale (no auth concept). The others will trend lower.** This survey tests that prediction.

---

## Methodology

### Discovery

Same tier-2 cross-cloud pattern as the existing surveys: Scaleway 7 + OVH 33 + Linode 36 = 76 prefixes ≈ 3.55M IPs.

Ports scanned: **6900** (Argilla default), **8000** (doccano default), **8080** (LabelStudio / CVAT / Prodigy reverse-proxy default).

Note: ports 8000 and 8080 collide with **dozens** of other AI platforms (vLLM, OpenAI-compat servers, MCP HTTP+SSE, Airflow, Spark UI, Weaviate, etc.). Platform identification therefore relies on **response signatures**, not port alone.

### Probe

`data/datalabel-probe.py` is a multi-platform fingerprint prober. For each (ip, port), it tries each platform's distinctive endpoint in turn:

| Platform | Probe endpoint | Match signature |
|---|---|---|
| **Argilla** | `GET /api/_info` | JSON with `version` + `elasticsearch` keys |
| **LabelStudio** | `GET /version` | JSON with `release` and `label-studio-os-*` keys |
| **doccano** | `GET /v1/health` + `GET /v1/projects` | health responds; `/v1/projects` returns paginated `{count, results}` |
| **CVAT** | `GET /api/server/about` | JSON with `name` containing "Computer Vision Annotation Tool" |
| **Prodigy** | `GET /` | HTML body containing `prodigy` markers |

For each confirmed instance, capture: platform, version, project/workspace count (if reachable unauth), auth posture (401/403 or 200 on `/api/projects`), raw match signature.

### Filters

- **AS63949 honeypot fleet** — apply standard filter (393-host Akamai/Linode honeypot list at `~/recon/ollama-tier2-2026-05-04/as63949-honeypot-fleet.txt`).
- **Common port-8080 false positives** — anything that returns Spark/Airflow/Weaviate signatures is excluded by the probe's signature-matching (those don't return Argilla/LabelStudio/CVAT JSON shapes).
- **Auth-on-default instances** — record presence (`auth_required: true`) but exclude from the "exposed projects/data" enumeration.

### Tools-classification taxonomy

For each confirmed unauth instance, classify by what kind of data the project metadata reveals:

| Class | Examples | Risk |
|---|---|---|
| **Healthcare / clinical** | radiology images, EHR text, drug-trial transcripts | HIPAA / GDPR Art. 9 |
| **Financial / KYC** | identity documents, transaction logs, AML-flagged content | PCI / regional financial-data laws |
| **Government / law-enforcement** | police body-cam, surveillance footage, immigration docs | jurisdiction-dependent |
| **Personal / consumer** | user-generated content, customer support transcripts, social-media DMs | GDPR / CCPA |
| **Facial / biometric** | face recognition training, age-detection, emotion-tagging | GDPR Art. 9 (biometric special-category) |
| **NLP corpus** | document classification, NER, sentiment | mostly low risk unless internal docs |
| **Computer vision (non-faces)** | object detection, segmentation, retail | low to medium |
| **Internal-business** | invoices, contracts, ID cards from operator's own org | confidentiality + sometimes PII |

---

## Discovery results

_(populated as the masscan + probe pipeline completes)_

| Source | Hits | Confirmed | Auth-on | Auth-off |
|---|---|---|---|---|
| Scaleway tier-2 (7 prefixes) | TBD | TBD | TBD | TBD |
| OVH tier-2 (33 prefixes) | TBD | TBD | TBD | TBD |
| Linode tier-2 (36 prefixes) | TBD | TBD | TBD | TBD |
| **Total unique** | TBD | TBD | TBD | TBD |

### By platform

| Platform | Confirmed | Auth-off | Median version | Notes |
|---|---|---|---|---|
| Argilla | TBD | TBD | TBD | TBD |
| LabelStudio | TBD | TBD | TBD | TBD |
| Prodigy | TBD | TBD | TBD | TBD |
| doccano | TBD | TBD | TBD | TBD |
| CVAT | TBD | TBD | TBD | TBD |

---

## Project-content classification

_(populated)_

| Class | Hosts | Notable examples |
|---|---|---|
| Healthcare / clinical | TBD | TBD |
| Financial / KYC | TBD | TBD |
| Government / law-enforcement | TBD | TBD |
| Personal / consumer | TBD | TBD |
| Facial / biometric | TBD | TBD |
| NLP corpus | TBD | TBD |
| Computer vision (non-faces) | TBD | TBD |
| Internal-business | TBD | TBD |

---

## Notable findings

_(populated)_

---

## Threat classes

1. **Direct dataset exfil** — when `/api/projects` is unauth, the project list discloses operator identity, business domain, and (often) the actual labeled records.
2. **PII leak via raw labeling content** — annotation projects routinely contain customer support transcripts with names + emails + phones, medical records, identity documents.
3. **Biometric data exposure** (GDPR Art. 9) — facial-recognition labeling projects expose face crops + identifiers; same regulatory class as the tweet-optimize.com Milvus finding.
4. **Annotator credential leak** — some platforms expose user lists, sometimes with email + role.
5. **Model fingerprinting** — Argilla integrates with HuggingFace models; the project schema reveals which models the operator is fine-tuning.
6. **Operational intel** — the "label classes" defined in a project disclose the operator's classification taxonomy (often proprietary business logic).

---

## Honest negative space

- **Authenticated platforms with read-only public projects** — some operators intentionally publish public-domain corpora via Argilla/doccano. Manual review needed to distinguish "intentional public" from "misconfigured."
- **Reverse-proxied Prodigy** — Prodigy's no-auth-by-design is mitigated when operators correctly add nginx + basic-auth in front. Those return 401 at the network edge and are out of scope (but the proxy + Prodigy combination is the recommended deployment path; population data on whether operators actually do it is the survey's value-add).
- **CVAT enterprise / SaaS deployments** — the SaaS-hosted version (cvat.ai) is auth-on by design; this survey targets self-hosted instances only.

---

## Disclosure plan

For each unauthenticated instance with high-risk content classes (healthcare, financial, biometric, government), draft coordinated-disclosure email per the standard NuClide template, routed via WHOIS-derived institution identification (per the contact-resolver rule from the Buffalo State misroute lesson).

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — companion cross-survey synthesis
- [`FUTURE-SURVEYS.md`](FUTURE-SURVEYS.md) — broader unsurveyed roadmap
- [`data/datalabel-probe.py`](../../data/datalabel-probe.py) — multi-platform fingerprint prober used for this survey
