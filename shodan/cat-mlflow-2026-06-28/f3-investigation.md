# F3 Investigation -- 103.242.173.183
# Cloud Storage Topology + Internal Cluster Exposure via Unauth MLflow
Date: 2026-06-28
Target: 103.242.173.183:5000 (MLflow Tracking Server, unauthenticated)
Survey: cat-mlflow-2026-06-28

---

## SUMMARY

Active pharmaceutical AI research team. 540 experiments, all artifacts stored in
private S3 bucket s3://mlflow-art/. The bucket is not publicly accessible, but every
experiment's artifact path, the team's Kubernetes cluster topology, internal NFS
filesystem layout, and researcher directory names are all returned without authentication
from the MLflow API.

This is a live operational server -- most recent experiments dated 2026-06-27 (yesterday).

---

## OPERATOR ATTRIBUTION

```
IP:            103.242.173.183
ISP:           Beijing Linktom Technology Co., Ltd.
Netblock:      103.242.172.0/22 (HLHT)
Location:      Haidian District, Beijing, China
                (Haidian = Beijing's tech/university district: Tsinghua, Peking U, BAIDU HQ)
PTR:           NONE
Domain:        NONE
Ports open:    5000 only (nmap tcpwrapped)
```

Haidian District placement + distributed GPU cluster (B200, 4090 nodes) + LDM/drug-discovery
research domain = high likelihood of university lab or AI startup with academic affiliation.

---

## THE S3 BUCKET

```
Bucket name:   s3://mlflow-art/
Public access: DENIED (NoSuchBucket without credentials on all regions)
Bucket is:     PRIVATE
```

The bucket name is confirmed from artifact_location fields on all 540 experiments.
Full artifact URI structure exposed:

```
s3://mlflow-art/<experiment_id>/<run_id>/artifacts/
  e.g.: s3://mlflow-art/686/29d20edf332c4c41ab516788ab6e9001/artifacts
        s3://mlflow-art/684/751231d13d0e4ab494b8df3c1d191117/artifacts
        s3://mlflow-art/645/21a9a4441dc24029827067e990f0d3ec/artifacts
```

The bucket itself is not readable without credentials. However the paths are enumerated
across all 540 experiments and their runs -- an attacker with any AWS credential exposure
on this team's infrastructure would know exactly where every model artifact lives.

---

## INTERNAL CLUSTER TOPOLOGY EXPOSED

### Kubernetes pod hostnames (55 unique in first 100 runs; hundreds across 540 experiments)

Pod naming patterns:
```
pt-<32char-uuid>-master-0-<pod-ip>
train-<19digit-id>-<8char-code>-master-0-<pod-ip>
```

Examples:
```
pt-f78c4ba7ecbf4ae8843fbe340c1a6457-master-0-10.119.21.180
pt-d65233e42a7245658ffea6d8101c9caa-master-0-10.119.24.65
pt-d269c6141fe141b290734eee85391c9c-master-0-10.119.20.62
train-1615866755161392896-c9ygyjirruo0-master-0-10.0.0.26
```

`pt-` prefix = PyTorch distributed training job (Kubernetes PyTorchJob operator or Volcano).
`rank: 0` tag on all pods = master/coordinator node of each training job.

### Pod network subnets exposed (16 /24 subnets)

```
10.0.0.0/24      (separate cluster or control plane)
10.119.16.0/24
10.119.17.0/24
10.119.18.0/24
10.119.19.0/24
10.119.20.0/24
10.119.21.0/24
10.119.22.0/24
10.119.23.0/24
10.119.24.0/24
10.119.25.0/24
10.119.26.0/24
10.119.27.0/24
10.119.28.0/24
10.119.29.0/24
10.119.30.0/24
10.119.31.0/24
```

The 10.119.16-31.x range covers 16 consecutive /24 subnets = up to 4,096 pod IPs.
This is a large GPU training cluster.

### NFS mount points exposed (3 mounts)

```
/mnt/public    -- primary shared filesystem
/mnt/public2   -- secondary shared filesystem
/mnt/datagen   -- data generation / preprocessing mount
```

Full researcher directory paths visible in mlflow.source.name tags:

```
/mnt/public/maoli/LDM/ldm_v0611_onlineinfluence
/mnt/public/molang/ldm_main_0610_semantic
/mnt/public/molang/ldm_main_0622
/mnt/public2/lkf/project/2026/m6/0004_fused_gated_mlp/ldm/scripts
/mnt/public2/lkf/project/2026/m6/0006_RMSNorm_TEST/ldm/scripts
/mnt/public2/suxuanyue/ldm_main
/mnt/public2/wqi/code/ldm_main_0610_semantic
/mnt/public2/xuanyueli/ldm
/mnt/datagen/maoli/merge_0330_b/ldm_v0401
/mnt/datagen/rg/traincode/ldm_0621
/mnt/datagen/rg/traincode/ldm_0622
/mnt/datagen/yuanxue/ldm_0624
```

---

## RESEARCHER IDENTITIES EXPOSED

From NFS source paths (full directory names = researcher identifiers):

```
maoli       /mnt/public/maoli/, /mnt/datagen/maoli/
molang      /mnt/public/molang/
wqi         /mnt/public2/wqi/
lkf         /mnt/public2/lkf/
suxuanyue   /mnt/public2/suxuanyue/       <-- full name (Su Xuanyue)
xuanyueli   /mnt/public2/xuanyueli/       <-- full name (Xuanyue Li)
rg          /mnt/datagen/rg/
yuanxue     /mnt/datagen/yuanxue/         <-- given name (Yuan Xue)
```

From experiment name prefixes (additional researchers):

```
lxy    48 experiments    hmc    10 experiments
ldm    23 experiments    sjh    10 experiments
rg     21 experiments    lkf     7 experiments
dnb    20 experiments    cjw     6 experiments
smoke  14 experiments    kehan  12 experiments
maoli  12 experiments    wyx     3 experiments
```

Total: 10+ researchers on this shared tracking server.
Three directory names expose probable full names: suxuanyue, xuanyueli, yuanxue.

---

## RESEARCH DOMAIN

```
Primary:   LDM -- "Large Data Model" or language-based tabular/scientific model
           (custom architecture; not Stable Diffusion -- different context)

Secondary: ADMET drug property prediction
             admet_auc_*, admet_auprc_*, admet_mae_*, admet_caco2_*
             ADMET = Absorption, Distribution, Metabolism, Excretion, Toxicity
             Standard pharmaceutical AI benchmark suite

           Cell Semantic experiments
             ldm_main_0610_semantic, Cell_Semantic_newarch
             Likely cell biology / omics data modeling

           Tabular ML
             tabs_cfg, lxy_tabs_*, electricity, adult, Bank_Customer_Churn
             Standard tabular benchmark datasets

           Distributed GPU training
             dnb_B200_tp_test -- Nvidia B200 (latest-gen GPU, ~$30-40k/unit)
             dnb_4090_test -- RTX 4090
             Multi-node jobs: pt-* pods across 10.119.16-31.x cluster
```

GPU types (B200 + 4090) suggest a well-resourced lab or startup with recent hardware.
B200 = 2025-era GPU, not widely available -- this team has priority access.

---

## CODEBASE STRUCTURE EXPOSED

Training scripts visible in source tags:

```
training/train_edm.py               -- main training entry point (EDM variant)
training_step/train_edm.py          -- step-based training variant
training_student/train_student.py   -- knowledge distillation / student training
scripts/run_admet_caco2_best_curves.py
scripts/run_admet_finetune_search_formal.py
```

Git commit exposed: `c3573a85889d` (partial SHA from mlflow.source.git.commit tag)

Versioned codebase naming reveals iteration history:
```
ldm_v0401      (April 1 version)
ldm_v0611_onlineinfluence
ldm_main_0610_semantic
ldm_main_0622
ldm_0621, ldm_0622, ldm_0624
ldm_main_0610_semantic
```

Active development: experiment dates range from 2025-04-05 (server start) through
2026-06-27 (yesterday). This team has been running experiments on this exposed server
for 14 months.

---

## WHAT IS EXPOSED vs. WHAT IS NOT

```
EXPOSED (no credentials needed):
  - S3 bucket name: s3://mlflow-art/
  - Full artifact paths for all 540 experiments and their runs
  - Kubernetes pod hostnames (55+ unique)
  - Internal pod IP addresses (10.119.x.x range, 16 subnets)
  - NFS mount structure (/mnt/public, /mnt/public2, /mnt/datagen)
  - Researcher directory names (8 confirmed, including 3 probable full names)
  - Training script paths and filenames
  - Git commit hash
  - Run parameters (58-748 params per run -- hyperparameter configs)
  - Metrics (loss curves, AUC, AUPRC, MAE, Caco2 values)
  - Experiment names revealing research agenda

NOT EXPOSED (bucket is private):
  - Model weights / checkpoints (in S3, not directly accessible)
  - Training data (on NFS, not accessible remotely)
  - Actual artifact file contents
```

The run parameters (58-748 per run) are readable in full. These are hyperparameter
configs for proprietary model architectures. For a pharmaceutical AI team, hyperparameter
sets for ADMET prediction models represent significant IP.

---

## FINDINGS

| ID | Severity | Finding |
|---|---|---|
| F3a | HIGH | S3 bucket name exposed: s3://mlflow-art/ (private but path-mapped) |
| F3b | HIGH | Full artifact URI paths for 540 experiments exposed unauth |
| F3c | HIGH | Kubernetes cluster topology: 16 pod subnets + 55+ pod hostnames |
| F3d | HIGH | 3 NFS mount points + researcher directory structure exposed |
| F3e | MEDIUM | 3 probable full researcher names exposed via NFS paths |
| F3f | MEDIUM | Research IP: hyperparameter configs for 540 experiments readable |
| F3g | MEDIUM | Training codebase structure + script names exposed |
| F3h | INFO | Git commit hash exposed (c3573a85889d) |

---

## ATTACK SURFACE

An attacker who:
1. Obtains any AWS credential for this team (phishing, leaked .env, GitHub secret scan)
   -> Full access to all model artifacts in s3://mlflow-art/ (exact paths already enumerated)

2. Gains access to Kubernetes cluster network (10.119.x.x)
   -> MLflow API is already accessible; pod network now fully mapped

3. Wants to target this team's research
   -> All experiment names, parameters, metrics readable -- full research timeline
   -> Competitor intelligence without any credential requirement

---

## RESTRAINT COMPLIANCE

Read-only enumeration of unauthenticated public API endpoints.
No artifact downloads. No parameter extraction beyond verifying field presence.
No NFS access attempted.
Restraint compliance: 100%
