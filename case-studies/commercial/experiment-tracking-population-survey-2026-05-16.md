---
type: survey
---

# Experiment-Tracking Population Survey (2026-05-16)

_NuClide Research · 2026-05-16 (Survey 10 of the day's 10-category batch)_
_Closes: category 04 (training-experiments) registry-half — W&B self-hosted / ClearML / Aim Stack / Comet ML_

---

## Summary

Closes the experiment-tracking half of category 04 (the compute-orchestration half was surveyed 2026-05-06 with Spark / Airflow / Ray). MLflow was surveyed earlier in the series (Insight #18 buckets-locked finding). This survey covers the MLflow siblings: Weights & Biases self-hosted, ClearML, Aim Stack, Comet ML.

- 1,096 unique candidates harvested across ClearML / W&B / Aim / Comet dorks
- Probed via `fast_enum_exp_tracking.py` (threads=80, ~4 min)
- **2 confirmed unauth Aim instances** (both `project=My awesome project` — placeholder demo names; likely abandoned dev deployments)
- 8 auth-gated, 64 shell-only, 240 dead, 285 unrelated FPs, 497 unknown
- 0 confirmed unauth ClearML / W&B self-hosted / Comet ML at the data layer

**Result:** experiment-tracking tier is mostly Tier-C (auth-on-default) at population scale. The 2 Aim hits are demo/abandoned hosts, not production. The framework's auth-on-default pattern holds.

---

## Per-platform observations

### ClearML — 200 candidates, 0 unauth confirmed at data layer

ClearML's REST API at `/api/v2.X/projects.get_all` requires `Authorization: Bearer <token>` by default. Of ~200 candidates, those that returned 200 on root either:
- Returned the ClearML HTML shell (frontend reachable, API gated)
- Were shell-only matches (HTML mentions "ClearML" but isn't actually ClearML)

ClearML ships with auth on by default. Confirms Tier-C at population scale.

### W&B self-hosted — 84 candidates, 0 unauth

`GET /api/viewer` returns the GraphQL viewer; without a valid session/key it returns `null` (W&B's documented anonymous-user shape — exactly the same pattern documented in [[insight-16-status-code-is-not-auth]] from the 2026-05-04 observability survey). The "viewer:null" response is **NOT unauth** — it's W&B's auth-required-but-returns-200 pattern. None of the 84 candidates returned a non-null viewer.

Confirms Tier-C at population scale.

### Aim — 880 candidates, 2 confirmed unauth (both demo deployments)

```
34.28.105.134:80   project="My awesome project"
34.67.83.75:80     project="My awesome project"
```

Both hosts return `GET /api/projects` unauth with the default placeholder project name `"My awesome project"` (Aim's default `aim init` project). These are **demo / abandoned dev** deployments, not production. The 2 hits do NOT contradict Aim's framework default — Aim defaults to no auth on its REST API, but the framework documentation strongly recommends running behind a reverse proxy with auth (Tier-A* pattern).

The 880 `http.title:"Aim"` candidates are dominated by FPs — "Aim" is a generic word that matches many unrelated HTML titles (`http.title:"Aim High"`, `http.title:"Aim Solar"`, `http.title:"AimZap"`, etc.). Probably ~10-20 real Aim instances in the 880-candidate pool.

### Comet ML self-hosted — 1 title hit

Effectively no Shodan footprint. Comet ML is primarily SaaS (comet.com); self-hosted Comet is rare. No real instances observed.

---

## Methodology placement

Adds ClearML + W&B self-hosted to Tier-C confirmed. Aim is Tier-A* (auth optional, off-by-default but documentation recommends reverse-proxy auth). Comet ML self-hosted has too small a footprint to characterize.

Confirms the auth-on-default thesis on a high-value modality (experiment-tracking platforms store hyperparameters, model metrics, sometimes model weights and training data references). The 0/200 ClearML unauth rate + 0/84 W&B unauth rate is consistent with the platforms' Tier-C framework defaults.

---

## Cross-survey colocation

| Pair | Overlap |
|---|---|
| Exp-tracking ∩ MLflow (from 2026-05 cross-survey) | TBD — MLflow is its own platform, treated separately |
| Exp-tracking ∩ ClickHouse (same-day Survey 7) | TBD — some ClearML deployments use ClickHouse as backend |

Methodologically: experiment-tracking is a "platform with multiple backend services" pattern — operators who run W&B/ClearML/Aim almost always run a database (Postgres/MySQL) + object store (MinIO/S3) + sometimes ClickHouse for metrics. The IP-direct-shadow on confirmed experiment-tracking hosts is worth a follow-up.

---

## Toolchain Provenance

```
0. shodan search × 6 dorks → 1,096 unique candidates
1. fast_enum_exp_tracking.py (threads=80) → 2 Aim unauth + 0 others
2. (queued) IP-direct-shadow on the 2 confirmed hosts → 15-port adjacent sweep for DB / object-store leakage
3. (queued) visorlog ingest → 2 events
```

---

## Honest negative space

- **`http.title:"Aim"` dork is dominated by FPs.** Per [[insight-26-shodan-facet-fp-rate-escalates-with-token-commonality]], "Aim" is a common-word dork; real-rate is probably <2%. A second-conjunct anchor (`http.title:"Aim" "experiment"` or `http.title:"Aim" "tracking"`) would tighten the candidate set.
- **W&B viewer:null is NOT a finding.** Documented in Insight #16 from the prior observability survey; re-confirmed at population scale here.
- **ClearML SaaS deployments not surveyed.** ClearML offers a hosted version (app.clear.ml); the customer's data lives in ClearML's cloud and our survey doesn't reach it.
- **Aim Stack v3 may have introduced auth.** The 2 hits we found ran older Aim versions without auth; newer Aim may differ.
- **No backend-stack probing.** Each experiment-tracking platform has a backend (Postgres / Mongo / MinIO / ClickHouse) where the actual experiment data lives. IP-direct-shadow on the 2 confirmed Aim hosts would reveal whether the operator left the backend public too.

---

## Disclosure posture

- The 2 Aim hosts at `34.28.105.134` and `34.67.83.75` (both default placeholder project names, both port :80 on GCE/AWS IPs) are most likely abandoned dev deployments. Per-host disclosure is low-priority unless the IPs map to a recognized operator via WHOIS/PTR.

---

## See also

- [[insight-16-status-code-is-not-auth]] — W&B viewer:null pattern was the original codification
- [[insight-25-falsification-confirmation-tier-c-platforms]] — ClearML + W&B add to the Tier-C confirmation list
- [[insight-26-shodan-facet-fp-rate-escalates-with-token-commonality]] — `http.title:"Aim"` is a textbook common-word dork pathology
- [[insight-18-storage-vs-tracker-tier]] — MLflow buckets-locked finding applies here too: ClearML/W&B backed by S3 buckets are likely separately gated
- [`clickhouse-population-survey-2026-05-16.md`](clickhouse-population-survey-2026-05-16.md) — same day; ClearML can use ClickHouse as backend, the overlap is methodologically interesting
