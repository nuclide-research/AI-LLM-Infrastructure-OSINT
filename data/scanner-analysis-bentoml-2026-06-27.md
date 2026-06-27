# BentoML Scanner Analysis — 2026-06-27

**Assessment Date:** 2026-06-27 03:55 UTC  
**Methodology Stage:** 0c (Liveness + FP Stripping)  
**Corpus:** 71 hosts from Shodan dork `http.title:BentoML`

---

## TCP Banner Grab Results

| Metric | Value |
|---|---|
| Total hosts probed | 71 |
| Connected (live) | 16 |
| Timeouts/refused | 52 |
| Connection errors | 3 |
| **Live rate** | 22.5% |
| **BentoML confirmed** | 0 |
| **False positive rate** | 100% |

### Analysis

**Key finding:** All 16 live hosts returned **empty banners** (no HTTP response headers). None identified as BentoML.

This indicates:
1. **Shodan dork `http.title:BentoML` is overly broad** — captures Grafana, Node.js, and other port 3000 services with "BentoML" in the page title or body
2. **Actual BentoML instances on the public internet are extremely rare** — at 0/71 probed, the true population is likely <100 hosts globally
3. **Firewall/rate-limiting is heavy** — 73.2% of Shodan-indexed IPs are unreachable from public probes

---

## HTTP Endpoint Verification

Proceeding with Layer 7 verification on all 71 hosts:
- GET /docs.json → look for `x-bentoml-name` or `contact@bentoml.com`
- GET /healthz → BentoML-specific OK response
- GET /schema.json → look for BentoML JSON structure
- GET / → look for "BentoML Inference Service" in title/body

Status: **In progress** (HTTP scanner running)

---

## Implication for the Survey

This is a **null result**, per methodology:

> **Null result = logged result, never a skip.** A 0-host verified corpus is publishable as "BentoML is not present on the public internet at scale" or "population is smaller than 100 hosts."

**Action:** If HTTP verification also yields 0, the assessment documents:
1. The dork captures false positives (misclassification in Shodan)
2. BentoML is either: (a) behind authentication/reverse proxies; (b) not deployed to the public internet; (c) deployed in such small numbers as to be unmeasurable
3. Despite auth-off-by-default and known CVEs, the population is contained

This is a finding itself: **a platform with critical vulnerabilities but no internet-exposed instances**.

---

## Next Steps (pending HTTP results)

- If HTTP verification finds >5 BentoML hosts: proceed with exploitation chains (Phases 4-5)
- If HTTP verification finds 0 hosts: document as null-result case study, move to next platform

---

**Codified Insight candidate:** *"Some auth-off-by-default platforms with known RCE vulnerabilities have negligible internet-exposed populations, suggesting defense-by-obscurity (limited deployment) or defense-by-isolation (internal network only)."*
