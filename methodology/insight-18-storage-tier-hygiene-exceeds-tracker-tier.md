---
title: "Storage-tier hygiene exceeds tracker-tier hygiene at population scale"
insight_number: 18
date: 2026-05-13
tags:
  - methodology
  - mlflow
  - cloud-storage
  - operator-attribution
  - second-order-disclosure
related_research:
  - case-studies/commercial/visorbishop-phase5b-bucket-accessibility-2026-05-13.md
  - case-studies/commercial/visorbishop-phase5-primitives-2026-05-11.md
  - case-studies/commercial/visorbishop-iter7-survey-2026-05-11.md
source: case-studies/commercial/visorbishop-phase5b-bucket-accessibility-2026-05-13.md
---

# Methodology Insight #18: Storage-tier hygiene exceeds tracker-tier hygiene at population scale

## The insight

Across 49 cloud-provider buckets extracted from the artifact URIs of 120
critically-exposed unauthenticated MLflow trackers, **48 buckets (97.96%) are
locked at the storage tier**. One container has an anonymous-list ACL, and it
was empty at probe time.

Operators who don't authenticate their MLflow UI overwhelmingly do
authenticate their bucket. The mistake that exposes the tracker (the
`MLFLOW_TRACKING_AUTH` default-off shipping posture) does not propagate to
the cloud-storage backend the tracker writes to.

## What this rules out

Several attractive readings of Phase 5's bucket inventory are foreclosed by
this data:

1. **"The tracker exposure implies a bucket exposure."** No. The bucket-tier
   ACL is configured in an independent IAM workflow the operator did engage
   with.
2. **"Naming the bucket in the tracker is itself a data leak."** Mostly no.
   It's a *metadata* leak (operator name, project taxonomy, cloud-provider
   mix) but not an *artifact* leak at this population.
3. **"Storage-tier remediation is the high-impact move."** No. 48 of 49 are
   already remediated. The tracker tier is where every additional fix lives.

## What this enables

The Phase 5 "second-order disclosure surface" framing reframes from
*data exfil* to *metadata disclosure*. That changes the disclosure-recipient
math: the operator's customer data is not behind the exposed tracker, but
the operator's identity, project taxonomy, and cloud-provider attribution
are.

The 40 confirmed `exists-private` buckets are also high-value as a
**positive operator-attribution feed**. Each bucket name resolves to a real
account/project, validating the operator's identity for disclosure routing
without needing to probe further.

## How to apply

For any future survey of a tier-A platform with tier-B storage backends:

1. Extract the per-host backend URIs from the tier-A metadata API (MLflow
   artifact_uri, Phoenix exports, Helicone log sinks, etc.).
2. Categorize by provider (`aws-s3 / gcs / azure-blob / databricks-dbfs /
   local-fs / http / unknown`).
3. Probe each cloud-provider bucket anonymously, single-shot per probe:
   - S3: `GET https://<bucket>.s3.amazonaws.com/?list-type=2&max-keys=10`
   - GCS: `GET https://storage.googleapis.com/storage/v1/b/<bucket>/o?maxResults=10`
   - Azure: `GET https://<account>.blob.core.windows.net/<container>?restype=container&comp=list&maxresults=10`
4. Classify into `public-list | account-locked | exists-private | not-found`.

Expect the population-scale ratio to land near 40+ private : 1 public-list
for MLflow at least. Re-verify on each new platform class; the ratio is
class-dependent.

## Verdict semantics matter

Three classifications carry forensic value beyond the headline:

- **`exists-private`**: bucket present and explicitly denied. Confirms the
  operator's attribution and IAM posture. The strongest individual-operator
  signal in the corpus.
- **`account-locked`** (Azure-specific: HTTP 409 `PublicAccessNotPermitted`).
  The storage account globally disables anonymous access, a stronger
  posture than per-container ACL. Worth tracking separately.
- **`not-found`**: bucket name leaked by the tracker no longer resolves.
  Indicates a stale tracker configuration; useful as an operator-profile
  signal (the team has rotated buckets but didn't update the tracker pin).

`public-list` empty-at-probe-time is a real finding. The standing surface
will leak any future artifact upload, but it doesn't actualize the
"second-order disclosure" claim into current data exfil.

## When this could break

The mono-tier-hygiene hypothesis should be re-verified when surveying:

- **Tier-A platforms with tighter IAM coupling**, e.g. Databricks
  managed-DBFS, AWS SageMaker MLflow apps. These bind storage credentials to the
  platform-managed identity. Storage tier exposure may track tracker tier
  exposure 1:1 when IAM is bundled.
- **Self-hosted on-cluster storage**, e.g. MinIO, Ceph, plain HTTP file
  servers. The cloud-IAM workflow that protected the 48 doesn't exist; the
  operator who left the tracker open may also leave the local store open.
- **Newer cloud defaults**, e.g. GCS uniform bucket-level access, AWS S3
  Block Public Access, Azure `AllowBlobPublicAccess=false`. As these defaults
  spread, the public-list rate trends to zero independent of operator skill.
  Don't conflate platform-default improvement with operator-behavior
  improvement.

## Discovery context

Phase 5 of the VisorBishop arc derived three primitives from the
cumulative-MLflow corpus. The bucket-URI primitive surfaced 58 unique
buckets across 120 hosts. Phase 5's writeup framed this as a "second-order
disclosure surface": what would become accessible if the buckets were
also exposed.

Phase 5b answered that question empirically. The answer was less catastrophic
than the framing implied, and the data warranted a methodological
re-anchoring: this is a metadata surface, not an artifact surface, and the
operator population's storage-tier discipline is the load-bearing reason.

The reframing matters for disclosure prioritization. The 492 critical MLflow
operators in the Phase 5 cumulative inventory are reachable by tracker-tier
disclosure first; storage-tier follow-up is a separate, much smaller queue.