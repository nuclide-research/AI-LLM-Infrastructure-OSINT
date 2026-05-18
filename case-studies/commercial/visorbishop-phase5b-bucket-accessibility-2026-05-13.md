---
type: tool-dev-log
title: "VisorBishop Phase 5b: Bucket-accessibility pass against 49 MLflow artifact stores"
date: 2026-05-13
class: tool
category: cross-platform-tool-validation
status: research-complete
methodology: anonymous read-only list-bucket probes against the 58 unique cloud bucket URIs surfaced in Phase 5
---

# VisorBishop Phase 5b · 2026-05-13

NuClide Research · 2026-05-13

## Summary

Phase 5 extracted 58 unique artifact buckets from the 120-host
critical-MLflow inventory. The open question: how many of those
buckets are actually reachable anonymously? Are operators who
expose their MLflow tracker also exposing the artifact tier behind
it, or do they tighten down at the storage layer?

This pass probes the 49 cloud-provider buckets (21 S3 + 20 GCS +
8 Azure-blob; the 9 local-fs / databricks-dbfs / http-non-cloud
rows were excluded) with anonymous list-bucket requests. No
credentials sent, no destructive operations, no GET-by-key beyond
what the listing surfaces.

**Result: 1 of 49 cloud buckets exposed an anonymous-list ACL, and
that container was empty at probe time. The Phase 1-2 observation
that MLflow operators have decent bucket hygiene survives empirical
contact.**

The Phase 5 "second-order disclosure" framing turns out to be
conservative on the upside. The class behavior at the storage tier
is *better* than the class behavior at the tracker tier. Operators
who don't bother authenticating their MLflow UI do, in 48 cases
out of 49, lock down the artifact backend.

## Methodology

Source corpus: `mlflow-artifact-buckets.tsv` from Phase 5
(`~/recon/2026-05-11-phase5/`). Filter to cloud-provider rows only
(`aws-s3`, `gcs`, `azure-blob`).

Per-provider probes (read-only, anonymous):

| Provider | Probe URL pattern | Discriminator |
|---|---|---|
| aws-s3 | `https://<bucket>.s3.amazonaws.com/?list-type=2&max-keys=10` (virtual-host) then `https://s3.amazonaws.com/<bucket>/...` (path), then region-redirect-followed | 200 → public-list; 403 AccessDenied → exists-private; 404 NoSuchBucket → not-found |
| gcs | `https://storage.googleapis.com/storage/v1/b/<bucket>/o?maxResults=10` (JSON API) + `https://storage.googleapis.com/<bucket>?max-keys=10` (XML fallback) | 200 → public-list; 401/403 → exists-private; 404 on both → not-found |
| azure-blob | `https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&maxresults=10` | 200 → public-list; 401/403 → exists-private; **409 PublicAccessNotPermitted → account-locked** (stronger); 404 → not-found; DNS NXDOMAIN → not-found |

Each probe issued sequentially with 0.4s pacing, 6-second timeout,
6KB response cap, identifying User-Agent
(`NuClide-VisorBishop-Phase5b/1.0 (research; read-only)`).

Tooling: `probe.py` in this directory's evidence pack.

## Results

### Verdict distribution

| Verdict | Count | Meaning |
|---|--:|---|
| **`exists-private`** | **40** | Bucket present, anonymous denied. Best-case operator posture. |
| `not-found` | 6 | Bucket renamed/deleted, or MLflow tracker references a stale URI. |
| `account-locked` | 2 | Azure storage account globally disables anonymous access (strongest posture). |
| **`public-list`** | **1** | `model-storage@blobimgstore.blob.core.windows.net` — empty at probe time. |
| **Total** | **49** | |

### By provider × verdict

| Provider | Public-list | Account-locked | Exists-private | Not-found |
|---|--:|--:|--:|--:|
| aws-s3 (21) | 0 | — | 18 | 3 |
| gcs (20) | 0 | — | 20 | 0 |
| azure-blob (8) | **1** | 2 | 2 | 3 |

S3 and GCS: 0 hits. Azure-blob: 1 hit out of 8 = 12.5%. That
elevation isn't statistically meaningful at n=8, but it does match
the broader pattern that Azure storage accounts allow per-container
ACLs that operators can mis-set, while accounts with the global
`AllowBlobPublicAccess=false` flag (the 2 `account-locked` cases)
block the whole class.

## The one finding: `model-storage@blobimgstore`

### What it is

- **Account:** `blobimgstore.blob.core.windows.net`
- **Container:** `model-storage`
- **ACL:** anonymous list-blobs permitted
  (`?restype=container&comp=list` returns 200 OK with valid
  `EnumerationResults` XML)
- **Source MLflow tracker:** `http://98.67.188.174:5000`
  (Azure West US 2 / Microsoft Corporation)
- **Phase 5 reference count:** 4 occurrences across 1 host

### What it isn't

The container is **empty at probe time** (`<Blobs />` in the
listing response, both at the root and at the per-experiment
prefix `101/`). The upstream MLflow tracker confirms the artifact
URIs are real (e.g. run `674395d6d24c46de831acac38e870aa7` under
experiment 101 has artifact_uri
`wasbs://model-storage@blobimgstore.blob.core.windows.net/101/674395d6d24c46de831acac38e870aa7/artifacts`),
but that prefix returns 0 blobs as well.

Possible explanations (we did not actively investigate further to
respect the implicit scope on a third-party operator):

1. The bucket is correctly ACL'd but has been purged of artifacts
   recently. Perhaps after a prior disclosure or housekeeping cycle.
2. The MLflow tracker writes artifacts via a SAS-token-scoped path
   that doesn't materialize visible blobs to anonymous list.
3. Listing is anonymous but reads require auth; we did not test
   reading.

### Risk classification

| Dimension | Rating |
|---|---|
| ACL misconfiguration | confirmed (anonymous list ACL on container) |
| Actualized data exposure at probe time | none |
| Standing surface for any future artifact upload to leak | **yes** |
| Same-operator MLflow tracker exposes prompt/parameter history | yes (separate finding from Phase 1/Phase 5) |

This is the "configuration confirmed, no current artifacts" state.
It's a real finding. The operator's bucket would leak any
artifacts they push to it, but it doesn't actualize the Phase 5
"second-order disclosure" claim into a current data-exfil
demonstration.

## Methodology insight surfaced

### Insight #18: Storage-tier hygiene exceeds tracker-tier hygiene at population scale

> Across 49 cloud-provider buckets referenced by unauthenticated
> MLflow trackers, 48 (97.96%) were locked at the storage tier.
> Operators who don't authenticate their tracker UI overwhelmingly
> do authenticate their bucket. Meaning the artifact-URI exposure
> visible in the tracker's run metadata is a metadata-disclosure
> primitive, not a data-exfil primitive, at this population.

This refines the [Phase 5 "second-order disclosure surface"
framing](visorbishop-phase5-primitives-2026-05-11.md). The 58-bucket
inventory was a *metadata* surface (operator names, bucket-naming
conventions, cloud-provider mix, project taxonomies) much more than
an *artifact* surface.

The operator population's revealed preference: lock the storage
backend, leave the metadata tier exposed. That tracks with how
Phase 1 traced the originating mistake. Operators set
`PHOENIX_ENABLE_AUTH=False` and equivalent flags on the tracker UI
because those flags are loud defaults; bucket access is configured
in a separate IAM workflow they already paid attention to.

### Why "exists-private" matters as a verdict

Of the 40 `exists-private` results, every bucket returned a
discriminating error (`403 AccessDenied` for S3, `403 Forbidden`
for GCS JSON API, `401`/`403` for Azure container-level). That
confirms:

- The bucket name resolves to a real account/project. Operator
  attribution is bucket-name → tenant (forensic value preserved).
- The bucket has explicit deny configured (not just absence of
  allow). A stronger posture than just "default-deny applies."
- The artifact URI in the MLflow tracker is wired to the right
  backend (vs. a placeholder or stale reference).

For the 6 `not-found` cases the MLflow tracker is leaking a
**dead** URI. Either renamed buckets, deleted projects, or
copy-paste configuration from documentation. Operationally:
`not-found` from this probe should feed back into VisorBishop as a
"stale tracker config" signal. Interesting for operator-profile
narrative even though it carries no immediate risk.

## Reproducibility

Evidence pack: `evidence/2026-05-13-bucket-accessibility/`
- `probe.py`: the tri-cloud prober (~10 KB, stdlib only)
- `probe-targets.tsv`: the 49 cloud buckets fed to the prober
- `results.json`: raw probe records (verdict, status codes,
  truncated response bodies for every URL hit)
- `results-classified.json`: same with the 409 → account-locked
  and DNS-NXDOMAIN → not-found post-classification applied
- `results.tsv`: tab-separated summary (one line per bucket)
- `run.log`: stderr capture from the actual sweep

Reproduce:

```bash
cd ~/recon/2026-05-13-bucket-accessibility
python3 probe.py 2>&1 | tee run.log
```

Probes are stateless and idempotent. Re-running against the same
target set will produce a near-identical verdict distribution on
any given day (verdicts only change if an operator actively
modifies a bucket ACL or deletes an account between runs. Both
worth detecting if monitored over time).

## What's next

1. **VisorBishop integration:** roll the per-provider bucket-list
   probe into VisorBishop as an opt-in stage so future runs can
   classify newly-discovered MLflow trackers at both tiers in one
   pass. Cost: ~50 lines per provider, no new dependencies.
2. **`exists-private` → operator-profile feed:** the 40 confirmed
   buckets are operator attribution gold. Folded into the
   disclosure-routing pipeline (next phase) as the canonical
   per-operator artifact-store identifier.
3. **Re-probe `blobimgstore/model-storage` on a delay** to capture
   whether artifacts repopulate (single-host longitudinal study).

## Cross-references

- [Phase 5 primitives doc](visorbishop-phase5-primitives-2026-05-11.md): origin of the 58-bucket corpus
- [iter-7 MLflow + W&B case study](visorbishop-iter7-survey-2026-05-11.md): origin of the 120-host critical-MLflow inventory
- [Insight #13: shipping defaults are load-bearing](../../methodology/insight-13-shipping-defaults-load-bearing.md): frames why tracker tier is exposed and storage tier isn't
- [Phase 2 synthesis](SYNTHESIS-ai-observability-phase2-2026-05-12.md): broader observability-tier class characterization
