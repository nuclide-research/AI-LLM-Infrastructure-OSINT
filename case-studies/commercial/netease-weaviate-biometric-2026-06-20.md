---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "NetEase Weaviate: Unauthenticated Read, Write, and Delete on a 20,298-Record Facial Recognition Store"
summary: "A NetEase facial recognition vector store ran on a public Weaviate instance with no authentication. The store held 20,298 real-person face image records across two production game lines, each carrying inline face image blobs and cross-product identity keys. We confirmed full read, write, and delete with a reversed canary."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - biometric
  - gaming
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "NetEase (netease.com)"
      - k: Sector
        v: "Gaming / Entertainment"
      - k: Location
        v: "OVH Canada (51.222.138.139)"
      - k: Severity
        v: CRITICAL
  - kind: see-also
    label: Classification
    kv:
      - k: Primary
        v: "CWE-306 Missing Authentication for Critical Function"
      - k: Secondary
        v: "CWE-284 Improper Access Control"
      - k: OWASP
        v: "LLM04 Data and Model Poisoning"
---

# NetEase Weaviate: Unauthenticated Read, Write, and Delete on a 20,298-Record Facial Recognition Store

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

A NetEase facial recognition backend ran on a public Weaviate instance with no authentication on any operation. Anyone on the internet could read, change, or erase the entire store that powers a cross-product face recognition pipeline.

The store held 20,298 real-person face image records. Each record carries a full face image blob, two internal identifiers that link the same face across two NetEase product lines, and a live CDN URL to the source image on NetEase infrastructure. Face images are biometric identifiers and are treated as a special data category under GDPR Article 9, CCPA, and PIPL.

We confirmed full read, write, and delete. The write and delete tests used a marked canary record in an empty class, and we reversed every change in the same session. No production records were modified.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.30.0 | Vector store, img2vec-neural facial recognition pipeline | None |
| 50051 | gRPC | Weaviate gRPC surface | Closed |
| 2112 | Metrics | Weaviate metrics endpoint | Not probed |

Single node, status HEALTHY, version 1.30.0. The REST API on port 8080 gave complete access. No authentication was required for any operation and no rate limiting was observed.

---

## What We Confirmed

**Read:** Pulled records without credentials. `GET /v1/objects?class=WWMFacesRecogProd&limit=100` returned full records including image blobs and the `text` field. Schema enumeration confirmed the three biometric classes. Cursor pagination scrolled across both populated classes.

**Write:** `POST /v1/batch/objects` returned `STATUS=SUCCESS` with no authentication. The canary was written to the empty class `WWMFacesRecog`, affecting zero production records. Canary UUID `a3d18705-263c-43e9-a785-5fe1689dbf59`.

**Delete (object):** `DELETE /v1/objects/WWMFacesRecog/<uuid>` on the canary returned 204. A follow-up GET on the same UUID returned 404, confirming removal. Canary created and deleted within the same test session.

**Delete (schema):** `DELETE /v1/schema/<ClassName>` was not tested. The surface is present and unauthenticated, but the destructive class-level operation was not exercised.

Every test artifact we created we removed. No production records were modified.

---

## Data Exposed

The store held three classes, two of them populated.

| Class | Records | Vectorizer | Role |
|-------|---------|-----------|------|
| WWMFacesRecogProd | 14,178 | img2vec-neural | Production inference set |
| WWMFaces | 6,120 | img2vec-neural | Base / training set |
| WWMFacesRecog | 0 | none | Empty class |
| **Total** | **20,298** | | |

Each populated record carries:

- A base64-encoded PNG face image blob, roughly 2.8MB each, stored inline.
- Two internal identifiers in the `text` field. One uses the `wwm_facedata_R37_` namespace, the other the `yysls_facedata_R37_` namespace. These cross-link the same face across two distinct NetEase product lines.
- A live CDN URL to the source image on NetEase infrastructure (`fp.ps.netease.com` and the `easebar.com` subsidiary CDN).

The `R37` batch identifier in every record suggests prior batches, so the full corpus across all hosts may be larger than what is stored on this instance.

This is a biometric data class. Face images are biometric identifiers, legally distinct from general PII in most jurisdictions. No actual face images, identifiers, or record values are reproduced here. The class names, record counts, vectorizer, and cross-product identity structure are the finding.

---

## Operator Attribution

The CDN URLs in the `text` field of every record point to NetEase infrastructure: `h72.fp.ps.netease.com` and `h72sg.fp.ps.easebar.com`. The `easebar.com` domain is a NetEase subsidiary and product CDN. The `fp.ps` path segment matches a face-photo photo-service naming convention consistent with a facial recognition pipeline.

The two internal ID namespaces (`wwm_facedata` and `yysls_facedata`) map to two NetEase product lines sharing one face recognition backend.

---

## Impact

**Biometric exposure at scale.** 20,298 real-person face images are readable with no credentials. The CDN URLs resolve to live NetEase servers, confirming these are real persons rather than synthetic data. Image blobs are stored inline, so no secondary CDN fetch is required for bulk read. With no rate limiting, the entire corpus is reachable via cursor pagination.

**Cross-product identity mapping.** Each record carries both a `wwm_facedata` ID and a `yysls_facedata` ID, linking one face across two product lines through a shared biometric key. This enables re-identification across systems that were likely intended to remain separate.

**Pipeline architecture exposure.** The img2vec-neural module and the two internal ID namespaces reveal the structure of NetEase's cross-product facial recognition system.

**Write enables corpus poisoning.** Unauthenticated POST to `/v1/batch/objects` allows injection of arbitrary face image records into any class. Adversarial inputs into the production class corrupt the production embedding space, which can degrade identity matching and weaken face-based anti-fraud.

**Delete enables pipeline destruction.** Unauthenticated DELETE on individual objects was confirmed. The schema-level DELETE surface is present but was not exercised. Bulk deletion of the production class would destroy the facial recognition pipeline and require full re-ingestion from the CDN source and re-vectorization.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 to internal network only. The instance should not be reachable from the public internet.

**Short-term:** Enable Weaviate's API-key or OIDC authentication and require it on all REST and gRPC operations. Move biometric image blobs out of the inline `text` and `image_blob` fields and behind an access-controlled object store.

**Medium-term:** Add canary records to detect unauthorized writes. Monitor for unexpected scroll or batch traffic. Audit the `R37` batch lineage and any sibling hosts that may hold prior batches under the same naming scheme.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
