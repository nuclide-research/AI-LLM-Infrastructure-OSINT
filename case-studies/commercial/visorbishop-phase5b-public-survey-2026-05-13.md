---
type: tool-dev-log
title: "VisorBishop Phase 5b: bucket-accessibility pass against 49 MLflow artifact stores (public)"
date: 2026-05-13
class: tool
category: cross-platform-tool-validation
status: research-complete
methodology: anonymous read-only list-bucket probes against the cloud-provider artifact URIs surfaced in Phase 5
visibility: public
---

# VisorBishop Phase 5b · 2026-05-13

NuClide Research · 2026-05-13

## Summary

Phase 5 extracted 58 unique artifact buckets from the 120-host
critical-MLflow inventory. The open question: how many of those
buckets are actually reachable anonymously? Do operators who expose
their MLflow tracker also expose the artifact tier behind it, or do
they tighten down at the storage layer?

This pass probes the 49 cloud-provider buckets (21 S3 + 20 GCS +
8 Azure-blob; the 9 local-fs / databricks-dbfs / http-non-cloud
rows were excluded) with anonymous list-bucket requests. No
credentials sent, no destructive operations, no GET-by-key beyond
what the listing surfaces.

**Result: 1 of 49 cloud buckets exposed an anonymous-list ACL, and
that container was empty at probe time.** The Phase 1–2 observation
that MLflow operators have decent bucket hygiene survives empirical
contact.

The Phase 5 "second-order disclosure" framing turns out to be
conservative on the upside. The class behavior at the storage tier
is *better* than the class behavior at the tracker tier. Operators
who don't bother authenticating their MLflow UI do, in 48 cases out
of 49, lock down the artifact backend.

This finding is the empirical basis for
[Methodology Insight #18](/methodology/insight-18-storage-tier-hygiene-exceeds-tracker-tier/).

## Methodology

Source corpus: the cloud-bucket inventory extracted in Phase 5 from
the artifact_uri field of every critically-exposed MLflow tracker.
Filter to cloud-provider rows only (`aws-s3`, `gcs`, `azure-blob`).

Per-provider probes (read-only, anonymous):

| Provider | Probe URL pattern | Discriminator |
|---|---|---|
| aws-s3 | `https://<bucket>.s3.amazonaws.com/?list-type=2&max-keys=10` (virtual-host) then path-style; follow region-redirect | 200 → `public-list`; 403 `AccessDenied` → `exists-private`; 404 `NoSuchBucket` → `not-found` |
| gcs | `https://storage.googleapis.com/storage/v1/b/<bucket>/o?maxResults=10` (JSON) + XML fallback | 200 → `public-list`; 401/403 → `exists-private`; 404 on both → `not-found` |
| azure-blob | `https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&maxresults=10` | 200 → `public-list`; 401/403 → `exists-private`; **409 `PublicAccessNotPermitted` → `account-locked`** (stronger); 404 → `not-found`; DNS NXDOMAIN → `not-found` |

Each probe issued sequentially with 0.4s pacing, 6-second timeout,
6KB response cap, identifying User-Agent
(`NuClide-VisorBishop-Phase5b/1.0 (research; read-only)`).

Tooling: `probe.py`, stdlib only, ~300 lines.

## Results

### Verdict distribution

| Verdict | Count | Meaning |
|---|--:|---|
| **`exists-private`** | **40** | Bucket present, anonymous denied. Best-case operator posture. |
| `not-found` | 6 | Bucket renamed/deleted, or MLflow tracker references a stale URI. |
| `account-locked` | 2 | Azure storage account globally disables anonymous (strongest posture). |
| **`public-list`** | **1** | Container had anonymous-list ACL; empty at probe time. |
| **Total** | **49** | |

### By provider × verdict

| Provider | Public-list | Account-locked | Exists-private | Not-found |
|---|--:|--:|--:|--:|
| aws-s3 (21) | 0 | (n/a) | 18 | 3 |
| gcs (20) | 0 | (n/a) | 20 | 0 |
| azure-blob (8) | **1** | 2 | 2 | 3 |

S3 and GCS: 0 hits across 41 buckets. Azure-blob: 1 hit out of 8 =
12.5%. That elevation isn't statistically meaningful at n=8, but
it does match the broader pattern that Azure permits per-container
ACLs operators can mis-set, while accounts with the
`AllowBlobPublicAccess=false` flag (the 2 `account-locked` cases)
block the whole class.

## The one public-list hit

Anonymous list-blobs ACL was permitted on a single Azure container
backing one of the surveyed MLflow trackers. The container was
empty at probe time. Listing returned a valid `EnumerationResults`
XML document with `<Blobs />` empty. Per-experiment prefix probes
were also empty.

The MLflow tracker that references this container is real and
returns experiments and runs whose `artifact_uri` points at the
container, so the wiring is intact. The operator either purged
artifacts recently, or writes via a SAS-token path that doesn't
materialize visible blobs to anonymous list.

The finding is "configuration confirmed, no current artifacts." A
real ACL misconfiguration that would leak any future artifact
upload, but no current data exposure. Per coordinated-disclosure
practice, the operator-specific detail is held until the disclosure
window closes.

## Why `exists-private` is a finding worth keeping

Of the 40 `exists-private` results, every bucket returned a
discriminating error:

- **403 `AccessDenied`** for S3
- **403 `Forbidden`** for GCS JSON API
- **401 / 403** for Azure container-level

That confirms:

- The bucket name resolves to a real account/project. Operator
  attribution is preserved (bucket-name → tenant identity).
- The bucket has explicit deny configured (not just absence of
  allow): a stronger posture than the default.
- The artifact URI in the MLflow tracker is wired to the right
  backend (vs. a placeholder or stale reference).

For the 6 `not-found` cases the MLflow tracker is leaking a *dead*
URI. Either renamed buckets, deleted projects, or copy-paste
configuration from documentation. These have no immediate impact
but are interesting as operator-profile signals: the team has
rotated buckets without updating the tracker pin.

## Reproducibility

Evidence pack: `evidence/2026-05-13-bucket-accessibility/`

- `probe.py` (tri-cloud prober, stdlib only)
- `probe-targets.tsv` (49 cloud buckets fed to the prober)
- `results.json` (raw probe records)
- `results-classified.json` (with 409 → `account-locked` and DNS
  NXDOMAIN → `not-found` post-classifications applied)
- `results.tsv` (tab-separated summary)
- `run.log` (stderr capture from the actual sweep)

Reproduce against the original bucket corpus:

```bash
python3 probe.py 2>&1 | tee run.log
```

Probes are stateless and idempotent. Re-running against the same
target set produces a near-identical verdict distribution on any
given day; verdicts only change if an operator actively modifies a
bucket ACL or deletes an account between runs.

## Cross-references

- [VisorBishop Phase 5 (three primitives)](/research/visorbishop-phase5-primitives-2026-05-11/). Origin of the 58-bucket corpus.
- [VisorBishop iter-7 (MLflow + W&B case study)](/research/visorbishop-iter7-survey-2026-05-11/). Origin of the 120-host critical-MLflow inventory.
- [Methodology Insight #13: shipping defaults are load-bearing](/methodology/insight-13-shipping-defaults-load-bearing/). Frames why the tracker tier is exposed.
- [Methodology Insight #18: storage-tier hygiene exceeds tracker-tier hygiene](/methodology/insight-18-storage-tier-hygiene-exceeds-tracker-tier/). Primary insight surfaced by this pass.
- [AI observability Phase 2 synthesis](/research/SYNTHESIS-ai-observability-phase2-2026-05-12/). Broader observability-tier characterization.