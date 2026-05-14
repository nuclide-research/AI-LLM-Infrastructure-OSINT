---
to: info@salutegroup.com.tr
cc: abuse@pendc.com
severity: CRITICAL
ip: 78.135.66.61
institution: Salute Group, SmartShop AI / amazonrec.space full MLOps pipeline exposed on PENTECH BILISIM host
status: DRAFT
date: 2026-05-13
---

**To:** info@salutegroup.com.tr
**Cc:** abuse@pendc.com
**Subject:** Security advisory — unauthenticated production API + ML pipeline on api.amazonrec.space / 78.135.66.61

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-13

**Re:** SmartShop AI / amazonrec.space — full MLOps pipeline exposed without authentication on a PENTECH BILISIM host
**IP:** 78.135.66.61
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification. No engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

On 2026-05-13 my external research identified that a host at 78.135.66.61 (PENTECH BILISIM, Turkey) exposes a recommendation-system product branded "SmartShop AI" at api.amazonrec.space, plus the full MLOps pipeline behind it, to the public Internet without any authentication.

The reason I'm contacting Salute Group: the host runs your brand Nadorawear's mail server (mail.nadorawear.com resolves to 78.135.66.61), the nadorawear.com domain WHOIS lists domain@salutegroup.com.tr, and the SmartShop AI deployment shares the same hosting and DNS posture. If SmartShop AI is a Salute Group product or a Salute Group client's project, you are best placed to forward this report to the right team. If it isn't, please let me know and I'll route it elsewhere.

## Infrastructure

| Field | Value |
|---|---|
| IP | 78.135.66.61 |
| rDNS | 78.135.66.61.pendns.net |
| ASN | AS48678 |
| Network | PENTECH BILISIM TEKNOLOJILERI (Istanbul, TR) |
| Hostnames | api.amazonrec.space, mlflow.amazonrec.space, airflow.amazonrec.space, mail.nadorawear.com |
| Frontend | amazonrec.space (Vercel-hosted SPA, "SmartShop AI MLOps Console") |

## Findings

| Port | Service | Severity | Issue |
|---|---|---|---|
| 443 | FastAPI (api.amazonrec.space) | CRITICAL | 13 endpoints publicly callable with zero authentication. OpenAPI spec at /docs and /openapi.json show components.securitySchemes is empty. /api/v1/session/init returns Amazon-dataset user IDs and category histories anonymously. /api/v1/interactions/stats reports 15,139 logged interactions, 6,374 Postgres writes, 15,139 S3 writes. |
| 5000 | MLflow tracking | CRITICAL | Unauthenticated tracker exposes experiment list, run parameters, artifact URIs (wasbs:// to Azure storage). |
| 6379 | Redis | CRITICAL | Internet-exposed, no auth, tagged "database" and "eol-product" by Shodan. |
| 8080 | Apache Airflow | HIGH | Sign-in page publicly reachable. Host carries 11 Airflow CVE references in Shodan (CVE-2024-25142 cluster, including DAG-permission bypass). |
| 5432 | PostgreSQL | HIGH | Internet-exposed. Backing store for both the SmartShop AI API and the MLflow tracker. |
| 25/465/587 | Postfix SMTP | MEDIUM | "eol-product" tag in Shodan. Also affects mail.nadorawear.com on the same host. |

## Evidence

A single unauthenticated GET request:

```
GET https://api.amazonrec.space/api/v1/session/init

{"success":true,
 "user_id":"AH2IJABKXWIZIO2FYJXNFEXNRR6A",
 "interaction_count":19,
 "top_categories":["Buy a Kindle","Books","Toys & Games"],
 "assigned_at":"2026-05-13T16:56:31.269772"}
```

The user_id format and the category strings match the public Amazon Reviews research dataset, so this likely isn't real customer PII, it's the public research corpus. However, serving that corpus from an unauthenticated production API still creates concrete operational and reputational risk.

## Why this matters

Even with synthetic-looking user IDs, the unauthenticated API enables three concrete harms: free unlimited model-behaviour scraping by competitors, model-feedback poisoning via POST to /api/v1/interactions (writes succeed and the total_logged counter increments), and unbounded data egress through the operator's S3 backend (15,139 events written so far). The MLflow tracker on the same host additionally exposes training-pipeline IP, every experiment, every hyperparameter, every artifact location, to anyone on the public Internet.

## Recommended fix

1. Put api.amazonrec.space behind an authentication wall: API key header, OAuth, or Cloudflare Access. Your FastAPI spec already declares a "global" security scope; flipping that to require a scheme is a one-line change in the FastAPI app initialization.
2. Bind Postgres (5432), Redis (6379), MLflow (5000), and Airflow (8080) to localhost or a private subnet. These should not be reachable from the public Internet.
3. Patch the Airflow tree to a current release to clear the CVE-2024-25142 cluster.
4. Upgrade the Postfix install (Shodan tags it as eol-product). This also affects mail.nadorawear.com on the same host.
5. Disable Swagger UI at /docs in production, or gate it behind auth. Public OpenAPI specs make endpoint enumeration trivial.
6. Audit Vercel deployment hooks on amazonrec.space to ensure the frontend doesn't leak production API tokens in build environment variables.

## Disclosure timeline

I will publish a redacted technical writeup on 2026-05-27 per standard coordinated-disclosure practice (14 days). The published version will redact specific user IDs and any operator-customer data. If you'd prefer a different timeline or want to coordinate the disclosure language, I'm happy to discuss.

Full technical detail and remediation notes are in the public research repository:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md

Reply-to for any clarifying questions or coordination: nicholas@nuclide-research.com.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
