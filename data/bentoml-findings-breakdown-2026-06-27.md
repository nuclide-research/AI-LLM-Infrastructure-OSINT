# BentoML Survey — Findings Breakdown

**Survey Date:** 2026-06-27  
**Population Target:** Internet-exposed BentoML model serving instances  
**Shodan Harvest:** 71 hosts (dork: `http.title:BentoML`)

---

## Findings Summary

| Finding | Count | Severity | Type |
|---|---|---|---|
| **Auth-off-by-default (confirmed)** | 0* | CRITICAL | Design |
| **Path traversal CVE-2024-42468** | 0* | HIGH (8.2) | CVE |
| **SSRF CVE-2024-36473** | 0* | HIGH (6.5) | CVE |
| **Yatai admin exposure** | 0* | CRITICAL | Misconfig |
| **Internet-exposed instances** | 0-16† | N/A | Population |

\* Pending HTTP verification results  
† TCP banner: 0 confirmed; HTTP verification in progress

---

## Classification

**Verdict (pending HTTP results):**
- **If 0 verified hosts:** Null result (population < 100 hosts or absent)
- **If 1-16 verified hosts:** Critical but low-population (niche deployment, internal-only)
- **If >16 verified hosts:** Population-scale attack surface (proceed to exploitation)

---

## Discoverable Assets (if population exists)

**Primary attack surfaces identified in Stage -1 OSINT:**
1. `/docs.json` — Unauthenticated OpenAPI schema (all versions)
2. `/metrics` — Prometheus endpoint, topology + cloud metadata leak (all versions)
3. `/predict`, `/summarize`, other inference endpoints — unauthenticated model inference (all versions)
4. `/healthz`, `/livez`, `/readyz` — Health endpoints, version fingerprinting
5. CVE-2024-2912 / 2024-9070 — Pickle RCE in runner server (< 1.3.4post1)
6. CVE-2025-27520 / 2025-32375 — Model loading RCE (< 1.4.8)
7. CVE-2026-44345 / 2026-44346 — Malicious package RCE (< 1.4.39 = current)

---

## Assessment Chain Status

```
✓ Phase 0:   Platform Intel              COMPLETE (bentoml-osint-2026-06-27.md)
✓ Phase 1:   Shodan Harvest              COMPLETE (71 hosts, 13 dorks)
✓ Phase 2:   aimap Config                COMPLETE (bentoml.yaml)
✓ Phase 3:   herald Config               COMPLETE (bentoml.yaml)
⧖ Phase 4a:  TCP Banner Scan             COMPLETE (0 BentoML confirmed, 16 FPs)
⧖ Phase 4b:  HTTP Verification           IN PROGRESS (payload: /docs.json, /healthz, /schema.json)
[ ] Phase 4c: Population Metrics          BLOCKED (pending Phase 4b)
[ ] Phase 5:  Exploitation Chains         BLOCKED (pending verified corpus > 0)
[ ] Phase 6:  Ledger Ingest               DEFERRED
[ ] Phase 7:  Compliance Scoring          DEFERRED
[ ] Phase 8:  BARE Module Ranking         DEFERRED
```

---

## Methodology Notes

**Null result protocol:** Per METHODOLOGY.md, a 0-host verified corpus is:
1. Logged as a distinct finding
2. Not treated as a failure
3. Publishable as "BentoML population is negligible" or "contained to internal networks"
4. Useful for the hypothesis: *"Auth-off-by-default prevalence varies by platform adoption and deployment context"*

**Shodan dork quality:** The `http.title:BentoML` dork is **overly broad** — it captures Grafana, Node.js, and other services with "BentoML" in the page. True BentoML may require a more specific signal (e.g., X-BentoML header in response, specific JSON structure in /docs.json, Yatai admin on 8080).

---

## Provisional Recommendation (pending results)

- **If HTTP confirms 0 hosts:** Document as null case study, pivot to next platform (FastGPT, Helicone, etc.)
- **If HTTP confirms 1-10 hosts:** Exploit all 3 chains on each host (detailed case study)
- **If HTTP confirms >10 hosts:** Full population assessment with spot-check exploitation

---

**Last updated:** 2026-06-27 04:05 UTC (HTTP verification pending)
