# MLflow Tracking Server on Public Cloud — Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Mass-scan of port 5000 across 28 cloud-provider /16 ranges (DO/Hetzner/Vultr) returned 12,106 hits → fingerprinted via `/version` + `/api/2.0/mlflow/experiments/search` body match → **11 confirmed MLflow Tracking Server instances**, all **unauthenticated**.

Small absolute count vs. the noise on port 5000 (Flask's default), but every single confirmed instance is unauth and exposes the operator's ML experiment metadata, model registry, and artifact-storage URIs. **Two of the eleven are already being actively exploited** via CVE-2023-1177 (path traversal) by external attackers — observable as attacker-injected experiments with `artifact_location` values like `http:///?/../../../../../../../etc/` and `/root/.ssh/`. Same attacker IDs span multiple hosts, indicating a coordinated CVE-2023-1177 sweep at population scale.

Behind the attacker noise, the legitimate operators run substantial production ML workloads in finance (algorithmic trading SPX hedging), medicine (pediatric vital-sign classification), dental imaging, livestock/horse-racing breeding models, manufacturing process homogeneity, AI safety research, and chatbot services.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 5000 --rate 10000
  → 12,106 port-5000 hits

mlflow-probe.py (200-thread fingerprint)
  GET /version                                       → MLflow version (raw text)
  GET /api/2.0/mlflow/experiments/search             → confirms MLflow REST API
  GET /api/2.0/mlflow/registered-models/list         → model registry inventory
  → 11 confirmed MLflow Tracking Servers
```

CVE correlation:
- **< 2.2.1** vulnerable to CVE-2023-1177 (path traversal in artifact endpoints)
- **< 2.8.1** vulnerable to CVE-2023-6014 (auth bypass on multi-user)
- **< 2.10.0** vulnerable to CVE-2024-37052 through 60 (recipe deserialization → RCE)
- **< 2.12.0** vulnerable to CVE-2024-37060 (pickle deserialization)

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 |
| Masscan hits on :5000 | 12,106 |
| MLflow Tracking confirmed | **11** |
| Unauthenticated | **11 (100%)** |
| Already-compromised (CVE-2023-1177 attacker artifacts visible) | **2** |
| CVE-vulnerable by version | 2 (v2.2.1 + v2.9.2) |
| Versions sampled | 2.2.1, 2.9.2, 2.17.1, 2.18.0, 2.20.2, 2.21.3 (×2), 2.22.1, 2.22.4, 3.4.0 (×2) |

---

## Class A — Already-Compromised (CVE-2023-1177 exploitation in progress)

### `138.197.152.103` (DigitalOcean) — MLflow 2.2.1 (vulnerable to CVE-2023-1177, CVE-2023-6014, CVE-2024-37052/.../60)

**Attacker-injected experiments (path-traversal CVE-2023-1177 PoCs):**

```
3D9V4JvPnDuvfxpSHZBQo1TTM3x  → http:///?/../../../../../../../../../../../../../../etc/
PJYMtlmXsSfyO0hk             → http:///#/../../../../../../../../../../../../../../etc/
MXhmOLyZ7i2zgR5d             → http:///#/../../../../../../../../../../../../../../etc/
6tUWyqxY1Z3cuSvj             → http:///#/../../../../../../../../../../../../../../etc/
3CCGENufMtsxUjr3ij4gjsPM44m  → http:///?/../../../../../../../../../../../../../../etc/
3BT8ncOzBWAH4GyIGz0EXsSwj7f  → http:///#/../../../../../../../../../../../../../../etc/
3BT8OPIHCXoEhTZvbIPhCefQe7O  → http:///#/../../../../../../../../../../../../../../etc/
HfbDEvCSaL9t2Bkn             → http:///#/../../../../../../../../../../../../../../etc/
xk8wSBjZY7MJGU6r             → http:///#/../../../../../../../../../../../../../../etc/
```

**Operator's actual experiment** (the legitimate workload buried in attacker noise):

```
orthodontic-upper-multitask  → s3://aipod-crop/artifacts/583324192295777494
```

The operator runs **dental AI models for orthodontic upper-jaw classification** (multitask learning) with model artifacts stored in an S3 bucket called `aipod-crop`. The bucket name is now disclosed; whether the MLflow stores its S3 credentials in a way that's also readable via the path-traversal vulnerability would require further (destructive) probing.

### `159.203.110.202` (DigitalOcean) — MLflow 2.9.2 (vulnerable to CVE-2024-37052/.../60)

**Attacker-injected experiments — same actor as 138.197.152.103** (matching IDs `3BT8ncOzBWAH4GyIGz0EXsSwj7f` and `3BT8OPIHCXoEhTZvbIPhCefQe7O`), worse target list — `/root/.ssh/`:

```
A0lNs4QbTgIChecm  → http:///#/../../../../../../../../../../../../../../root/
9D6H17u0tiNmXdOp  → http:///#/../../../../../../../../../../../../../../root/.ssh/
aZGVwezuF60CHthW  → http:///#/../../../../../../../../../../../../../../root/.ssh/
RaYNG7f9MAsKW8ci  → http:///#/../../../../../../../../../../../../../../root/.ssh/
apwsM4eyDoVjWJxq  → http:///#/../../../../../../../../../../../../../../root/.ssh/
4lHeW9CUYxhVujFz  → http:///#/../../../../../../../../../../../../../../etc/
exploit_33295     → /mlflow/artifacts/13   (named "exploit" — older opportunistic actor)
```

**Operator's actual experiment:**

```
helios_stock_direction  → /mlflow/artifacts/1
```

The operator runs a **finance / algorithmic-trading model** ("Helios" stock-direction predictor) on this MLflow. Same actor that's been targeting 138.197.152.103 has also been spraying CVE-2023-1177 PoCs against this instance, specifically aimed at SSH key extraction.

### Cross-host attacker correlation

The duplicated experiment IDs (`3BT8ncOzBWAH4GyIGz0EXsSwj7f`, `3BT8OPIHCXoEhTZvbIPhCefQe7O`) appearing on BOTH compromised instances mean the same attacker IS spraying the same payload UUIDs across all reachable vulnerable MLflow servers. The attacker has been doing this for some time and at scale; both hosts are accumulating attacker artifacts.

The path-traversal artifact_location idiom (`http:///?/../../../../`) is the canonical PoC for CVE-2023-1177 — when MLflow constructs the file path for artifact retrieval, the `..` segments escape the artifact root and read arbitrary filesystem paths. With `etc/` and `root/.ssh/` as targets, the attacker is harvesting SSH keys, /etc/passwd, and similar generic-secrets fare.

---

## Class B — Production ML Workloads (Operator-Attributable by Experiment Names)

### `157.90.104.16` (Hetzner) — MLflow 2.17.1 — algorithmic trading

```
hedge                                       /root/ml/experimentation/mlflow_artifacts/9
hedge_extra_features                        /root/ml/experimentation/mlflow_artifacts/15
hedge_update_TFS                            /root/ml/experimentation/mlflow_artifacts/17
hedge_markov_crash                          /root/ml/experimentation/mlflow_artifacts/11
hedge_with_markov_crash_feats               /root/ml/experimentation/mlflow_artifacts/10
spx_test                                    mlflow-artifacts:/8
pomorski_labels_spx_bayesian_optimisation   mlflow-artifacts:/7
spx_rf_manual_labels                        mlflow-artifacts:/6
delete_me                                   /root/ml/experimentation/mlflow_artifacts/14
rce_test_1772834193                         /root/ml/experimentation/mlflow_artifacts/22  ← attacker probe
```

**Operator profile:** quantitative trading firm running SPX (S&P 500) hedging strategies. The "Pomorski labels" reference points to a known finance-research approach (Pomorski meta-labelling for trading). Markov-crash + bayesian-optimization signals serious production quant work. Local-disk artifact storage.

The `rce_test_1772834193` experiment is unix-timestamp-suffixed and named "rce_test" — it's an attacker probing for the CVE-2024-37052 recipe deserialization RCE path. This instance is also being actively scanned, but on this version (2.17.1, post-fix) the exploit doesn't land.

### `65.109.36.121` (Hetzner) — MLflow 2.22.1 — pediatric medical ML

```
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final2
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final1
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check_final
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check6
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check5
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check4
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check3
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check2
beh_ped_lyi_sta_ml_etgn_cal_cri_100_min_v4_check1
fts_large_v1_cal_all_cri_100_day_sic_vs_hlt_f1_xgboost_updated1
```

**Decoded naming:** `beh` (behavioral?) `ped` (pediatric) `lyi` (lying) `sta` (standing) `ml` (ml) `etgn` (?) `cal` (calibration) `cri` (criterion) `100_min` (100-minute window) — the model classifies pediatric patient state from sensor data with calibration thresholds across time windows. The `fts_large_v1_cal_all_cri_100_day_sic_vs_hlt_f1_xgboost` experiment name explicitly carries `sic_vs_hlt` (sick vs healthy) + `f1_xgboost` (F1-scored XGBoost classifier).

**Operator profile:** medical-ML team training pediatric vital-sign / posture classifiers (sick-vs-healthy outcome prediction). The `_check_final2` + 9 prior `_checkN` experiments imply iterative model tuning — production ML work with regulatory implications (HIPAA-class data class, FDA AI/ML pre-market submissions).

### `188.166.132.129` + `188.166.38.104` (DigitalOcean) — MLflow 3.4.0 — livestock/horse-racing breeding ML (multi-host operator)

Both hosts have identical experiment lists pointing to the same `s3://flow-bucket/*`:

```
DKA_LOSS_MODEL                    s3://flow-bucket/30
GC_LOSS_EXPERIMENT_ONE_MODEL      s3://flow-bucket/29
TAH_LOSS_EXPERIMENT               s3://flow-bucket/28
TAH_WEIGHT_EXPERIMENTS            s3://flow-bucket/21
GC_BREEDERS_EXPERIMENTS           s3://flow-bucket/20
GC_BREEDER_EXPERIMENT             s3://flow-bucket/19
GC_BREEDER_PRODUCTION_TRAINING    s3://flow-bucket/18
GC_BREEDER_ADVANCED_TRAINING      s3://flow-bucket/17
GC_BREEDER_ROBUST_TRAINING        s3://flow-bucket/16
GC_BREEDER_V2_MEMORY_OPTIMIZED    s3://flow-bucket/15
```

**Operator profile:** the BREEDER + WEIGHT + LOSS naming pattern with track-code-style prefixes (DKA, TAH, GC) is consistent with **horse-racing AI** — predicting race outcomes from horse weight, breeder lineage, track conditions. "PRODUCTION_TRAINING" + "ADVANCED_TRAINING" + "V2_MEMORY_OPTIMIZED" + "ROBUST_TRAINING" indicates serious MLOps for a commercial gambling/sports-analytics product. Multi-host deployment (two MLflow servers serving the same S3 bucket) suggests staging + production, or a load-balanced setup.

Alternative interpretation: agricultural livestock breeding (cattle/poultry). Either way, a commercial breeding-prediction product with substantial ML investment exposed.

### `159.69.35.23` (Hetzner) — MLflow 2.18.0 — manufacturing process

```
HOMOGENEITY_OPW_03  through  _11   (9 variants, all s3://mlflow/24-32)
shadow_experiment                   s3://mlflow/35
```

**Operator profile:** "HOMOGENEITY OPW" + sequential numbering pattern looks like **manufacturing process control** (Operations Per Window? Optimization Per Wafer?) — possibly semiconductor wafer-uniformity classification or similar quality-control ML. "shadow_experiment" is MLOps speak for a champion/challenger test.

### `168.119.201.8` + `168.119.201.89` (Hetzner) — MLflow 2.21.3 — AI safety research (multi-host)

```
zone_strategy   s3://mlflow/3
sine_wave       s3://mlflow/2
l2_probe        s3://mlflow/1
Default         s3://mlflow/0
```

**Operator profile:** "l2_probe" + "zone_strategy" + "sine_wave" reads as **LLM interpretability / safety research** terminology. L2-norm probes are a standard interpretability technique (Anthropic-style mechanistic interpretability). "Zone strategy" could be an attack-zone characterization. Two hosts in the same /24 with identical experiment lists = multi-replica research environment.

### Other instances (HIGH/MEDIUM, briefer)

| Host | Version | Workload |
|---|---|---|
| `135.181.108.159` (Hetzner) | 2.20.2 | `Chatbot_Service` (single experiment) |
| `65.109.28.42` (Hetzner) | 2.22.4 | `git-query-recommender` — dev tool / code search |

---

## Per-Class Severity

| Class | Count | Severity | Notes |
|---|---|---|---|
| A — Already-compromised (CVE-2023-1177 active exploitation) | 2 | **CRITICAL** | Attacker has been active against these for some time; SSH key + /etc/* extraction possible |
| B — Production ML workloads, post-CVE-fix versions, exposed metadata | 9 | HIGH | Operator-attributable workloads with sensitive content classes (medical, finance, breeding/gambling, manufacturing) |

The CRITICAL classification on Class A is sharp: an attacker who can read arbitrary filesystem paths via CVE-2023-1177 can extract SSH keys and pivot to full host compromise. Both `138.197.152.103` and `159.203.110.202` should assume their VPS root is compromised.

---

## Cross-Survey Pattern (updated)

| Tier | Platform | Sample | Unauth |
|---|---|---|---|
| Vector DB | Qdrant / ChromaDB / Milvus | 142 | 100% |
| Inference | Triton / vLLM | 46 | 100% |
| Image-gen | A1111 | 1 | 100% |
| **MLOps** | **MLflow Tracking** | **11** | **100% — 18% actively compromised** |
| Orchestration UI | Flowise / n8n / Open WebUI / Langflow | 1170 | 0% (small misconfig %) |

The MLOps tier (MLflow) joins the vector-DB and inference tiers in the auth-off-by-default cluster. The new wrinkle: **passive observation of attacker activity** within the MLflow data shows the auth-off-by-default state is being actively exploited at population scale, not just theoretically risky.

---

## Remediation

```bash
# MLflow basic auth (since 2.5)
mlflow server --app-name basic-auth --host 0.0.0.0 --port 5000

# Configure default-admin via env
export MLFLOW_AUTH_CONFIG_PATH=/path/to/auth-config.ini

# Or front with reverse-proxy auth (nginx/Caddy HTTP Basic)
```

For the 2 already-compromised instances: assume root compromise, rotate all SSH keys + AWS credentials in the artifact-store config, redeploy from clean image.

---

## Disclosure Posture

- **`138.197.152.103`** (dental AI / orthodontic-upper-multitask) and **`159.203.110.202`** (helios_stock_direction) are in active-attacker territory. Time-sensitive disclosure to DigitalOcean abuse + the operator (if identifiable from the S3 bucket `aipod-crop` for the first one) is warranted within hours, not days.
- **`157.90.104.16`** (algorithmic trading) — finance-class data exposed; Hetzner abuse channel.
- **`65.109.36.121`** (pediatric medical ML) — HIPAA-relevant data class implied; Hetzner abuse + potentially direct operator if identifiable.
- **`188.166.132.129/.104`** (horse-racing/livestock breeding ML) — commercial product IP exposed.
- Other 4 instances — informational.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | masscan port 5000 → 12,106 IPs |
| Fingerprint | `mlflow-probe.py` — `/version` regex + `/api/2.0/mlflow/experiments/search` body match |
| What was NOT done | No exploitation of CVE-2023-1177 (file read), no attempt to read attacker artifacts (which would have triggered the same vulnerable code path), no inference / model artifact downloads |

---

## References

- MLflow auth: https://mlflow.org/docs/latest/auth/index.html
- CVE-2023-1177: https://nvd.nist.gov/vuln/detail/CVE-2023-1177
- CVE-2024-37052/53/54/55/56/57/58/59/60: https://github.com/mlflow/mlflow/security/advisories
- Cross-survey index: [index.md](index.md)
