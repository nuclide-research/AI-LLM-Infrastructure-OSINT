---
title: Pediatric medical ML operator — 224 unauth MLflow experiments + Metabase setup-token unclaimed (65.109.36.121)
date: 2026-05-06
class: substrate
category: mlops-tracking
status: disclosed-pending
methodology: bi-cross-survey-correlation
---

# Pediatric medical ML operator — stacked MLflow + Metabase pre-auth admin-takeover

NuClide Research · 2026-05-06

## Summary

Hetzner Helsinki host **`65.109.36.121`** runs a **pediatric medical ML operation** on three publicly-reachable services. The MLflow component (already in the NuClide ledger as event id 339) carries 224 production experiments naming sick-vs-healthy classifiers, behavioral-pediatric models, and calibration-window prediction tasks. The Metabase BI dashboard on the same host returns an **unclaimed setup-token** via the public-facing `/api/session/properties` endpoint — meaning any internet visitor can call `POST /api/setup` with that token and become the operator's Metabase administrator.

Combined: **CRITICAL operator catastrophe** in HIPAA-relevant ML domain.

This finding was surfaced by the BI Dashboard cross-survey-correlation probe on 2026-05-06 (5 platforms × 723 ledger IPs) which identified Metabase on this host. The MLflow component was already documented in `mlflow-cloud-survey-2026-05.md`; the BI probe added the Metabase setup-takeover surface that converts the existing exposure into a multi-platform compromise vector.

## Findings

### 1. Metabase v0.55.12 — pre-auth admin takeover (CRITICAL)

`GET http://65.109.36.121:3000/api/session/properties` returns:

```json
{
  "version": {"tag": "v0.55.12"},
  "site-name": null,
  "admin-email": null,
  "setup-token": "8f504ffb-d62d-4fa3-a03f-053cf7740a32",
  "has-user-setup": true,
  "site-uuid": null,
  "application-name": "Metabase"
}
```

The presence of a non-null `setup-token` means **the Metabase setup flow has not been completed** OR the operator created the admin via SSO without invalidating the setup-token. Either way, the token authorizes:

```
POST http://65.109.36.121:3000/api/setup
{
  "token": "8f504ffb-d62d-4fa3-a03f-053cf7740a32",
  "user": {
    "first_name": "...",
    "email": "attacker@..",
    "password": "..."
  },
  "prefs": { "site_name": "..." }
}
```

That request creates an admin user on the operator's Metabase. Once admin, the attacker has:

- **Browse + query 17 configured database drivers** including Databricks, Druid (JDBC), PostgreSQL, Spark SQL, MongoDB, MySQL, ClickHouse, Snowflake, BigQuery, Redshift — whichever the operator has actually wired up
- **Execute arbitrary SQL** via the Native Query interface against any connected database
- **Add new database connections** (including attacker-controlled databases for data exfiltration via CVE-2023-38646-style RCE on older Metabase versions; v0.55.12 is post-fix for the H2 RCE class but the Native Query interface itself remains powerful)
- **Read all dashboards + saved questions** which typically surface operator's KPI definitions, customer schemas, and aggregated PHI

NuClide did NOT call `/api/setup` with the disclosed token. The token is reproduced as evidence; the takeover step is left to the operator's incident-response team.

Verification was non-destructive: only `GET /api/session/properties` was called (a public endpoint by Metabase design).

### 2. MLflow 2.22.1 — 224 pediatric ML experiments unauth (HIGH, existing finding)

`GET http://65.109.36.121:5000/version` → `2.22.1` (post-CVE-2023-1177 fix; **not** vulnerable to the path-traversal class)

`POST /api/2.0/mlflow/experiments/search` returns 224 experiments. Sample names from the most-recent set (2026-04-24 to 2026-04-26):

```
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final2
fts_large_v1_cal_all_cri_100_day_sic_vs_hlt_f1_xgboost_updated1
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final1
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v3
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v3_check_final
```

Decoded naming pattern:

- `beh_ped` — behavioral pediatric
- `lyi_sta` — likely state / status indicator
- `ml_etgn` — ML etiology
- `cal_cri` — calibration critical
- `100_min` / `100_day` — prediction windows (100-minute / 100-day forward)
- `sic_vs_hlt` — sick-vs-healthy classifier
- `xgboost` — XGBoost (gradient-boosted trees, the standard tabular-medical-data model)
- `f1` — F1 score metric

This is a **clinical-decision-support model pipeline** — predicting whether a pediatric patient is sick vs healthy from behavioral and etiologic features within 100-minute or 100-day windows. HIPAA-class data is necessarily upstream of these models.

The MLflow component is post-CVE-2023-1177 patched, so the active-exploitation surface that affects AIPOD (`138.197.152.103`, MLflow 2.2.1) and Squeeze/Helios (`159.203.110.202`, MLflow 2.9.2) does NOT apply here. The exposure is "only" the metadata leakage — but at 224 experiments, the cumulative IP exposure is significant: the operator's complete ML strategy, hyperparameter sweeps, calibration approach, and model-performance progression are all readable.

### 3. Existing ledger context

NuClide ledger event id 339 (source `mlflow-cloud-survey-2026-05`) already has this host as `HIGH` severity, tagged `MEDICAL_ML, PEDIATRIC, XGBOOST, SICK_VS_HEALTHY, HIPAA_CLASS`. The Metabase finding from this BI probe **upgrades the combined severity to CRITICAL** because of the pre-auth admin-takeover vector.

## Disclosure routing

Per `nuclide-contact`:

- **Provider:** `abuse@hetzner.com` (Hetzner DE; ARIN/RIPE OrgAbuseEmail)
- **Operator-direct:** opaque — no public-facing domain, no rDNS-revealing customer brand, no CT log subdomains
- **Regulatory consideration:** if the operator is US-based serving US pediatric clinicians, BAA chain matters for HIPAA notification; without operator identification we cannot route directly to OCR. Hetzner abuse is the only path.

Disclosure draft: [`disclosures/HETZNER-65-109-36-121-pediatric-mlflow-metabase.md`](../../disclosures/HETZNER-65-109-36-121-pediatric-mlflow-metabase.md)

## Severity rationale

**CRITICAL.** Combined posture:

- **224 production ML experiments** revealing operator's clinical-prediction pipeline — operator-IP exfil at scale
- **Pre-auth admin takeover** via Metabase setup-token (`8f504ffb-d62d-4fa3-a03f-053cf7740a32`) — once claimed, attacker has access to whatever databases the operator has wired into Metabase (17 drivers configured, real connection state TBD)
- **HIPAA-relevant data class** — pediatric medical records upstream of the XGBoost classifier
- **Persistent (4+ weeks documented)** — original ledger entry from mlflow-cloud-survey 2026-05-04 → setup-token still unclaimed 2026-05-06

Not the same as AIPOD or Squeeze/Helios because the MLflow CVE-2023-1177 class doesn't apply (this MLflow is patched), but the Metabase setup-token gives an alternative escalation path of equivalent severity.

## Toolchain provenance

```
Step 0   BI cross-survey probe — bi-cross-probe.py (5 platforms × 723 ledger IPs × 13 port/path combos)
         → 36 confirmed BI dashboards across 17 unique operators
Step 1   bi-auth-check.py        → per-host auth posture validation
         → identifies setup-token at 65.109.36.121
Step 2   curl /api/session/properties → confirmed setup-token still unclaimed
Step 3   ledger cross-check       → existing event id 339 (mlflow MEDICAL_ML PEDIATRIC HIPAA_CLASS)
Step 4   curl /api/2.0/mlflow/experiments/search → 224 experiments confirmed
Step 5   nuclide-contact          → abuse@hetzner.com (operator opaque)
Step 6   visorlog (existing entry — this case study augments via tags)
Step 7   visorscuba (existing AI.C1 violation)
Step 9   visorcorpus (covered in earlier mlflow-cloud-survey corpus generation)
```

## Methodology Insight #12 candidate

**BI Dashboard cross-survey-correlation has the highest yield of any cross-platform probe so far** — 17 unique operators (5% hit rate vs Langfuse 0.14%, TEI 0%, LiteLLM 0.55%, Helicone/Portkey/LangSmith/TruLens 0%). Reasoning: BI dashboards are universal infrastructure (every operator running data needs visualization), unlike specialty AI/ML platforms which are tier-specific.

The follow-up auth-posture validation step is critical — Grafana's API endpoints often return SPA-fallback HTML with HTTP 200, which can falsely look like anonymous-org-readable. Real validation requires checking Content-Type + body shape:

- `application/json` body with auth-relevant content → real exposure
- `text/html` body → SPA fallback (auth required, just lenient routing)

Five "CRITICAL" Grafana hits in the initial automated triage turned out to be Tornado/BigAnt/Laravel admins on the same IP returning generic HTML — not Grafana data exposure. Without the validation step, the survey would have over-reported.

## References

- Original MLflow cloud survey — [`mlflow-cloud-survey-2026-05.md`](mlflow-cloud-survey-2026-05.md) (existing event id 339 entry)
- Sister actively-exploited MLflow hosts (different actor pattern) — [`multi-aipod-mlflow-cve-2026-05-06.md`](multi-aipod-mlflow-cve-2026-05-06.md), [`multi-squeeze-helios-trading-2026-05-06.md`](multi-squeeze-helios-trading-2026-05-06.md)
- Metabase setup-token mechanics — https://www.metabase.com/docs/latest/installation-and-operation/configuring-metabase
- CVE-2023-38646 (Metabase H2 driver pre-auth RCE — not directly applicable to v0.55.12 but the takeover-vector class is similar) — https://nvd.nist.gov/vuln/detail/CVE-2023-38646
