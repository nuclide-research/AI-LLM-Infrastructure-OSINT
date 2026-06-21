---
type: case-study
severity: CRITICAL
date: 2026-06-20
title: "NamedSource: Unauthenticated Read, Write, and Delete on the Weaviate Store Behind a Fact-Checking Platform"
summary: "NamedSource ran two Weaviate stores, stage and live, both open on port 8080 with no authentication. We confirmed read, write, and delete on both, with a reversed canary on stage. The store holds the platform's FakeIndex, the curated registry of URLs flagged as fake. Write access lets an attacker whitewash known disinformation or flag accurate reporting as fake."
tags:
  - weaviate
  - vector-database
  - unauth
  - cwe-306
  - fact-checking-data
  - media
sidenotes:
  - kind: host
    label: Target
    kv:
      - k: Operator
        v: "NamedSource (namedsource.com)"
      - k: Sector
        v: "Media / Fact-Checking"
      - k: Location
        v: "Hetzner"
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

# NamedSource: Unauthenticated Read, Write, and Delete on the Weaviate Store Behind a Fact-Checking Platform

_NuClide Research -- Nicholas Kloster -- 2026-06-20_

---

## Summary

NamedSource is a content reliability and fact-checking platform. It tracks URL attribution and flags misleading or fake content. The platform runs two Weaviate vector stores, a stage environment and a live environment. Both are open on port 8080. Neither asks for authentication.

We confirmed read, write, and delete on both stores. On stage we wrote a marked canary record, deleted it, and verified it was gone. The store holds the FakeIndex, the platform's curated registry of URLs flagged as fake or misleading. That registry is the platform's core trust product. Anyone on the internet can change it.

Stage carries more data than live and is the leading deployment environment. Both are open at the same time.

---

## Attack Surface

| Port | Software | Role | Auth |
|------|----------|------|------|
| 8080 | Weaviate 1.36.5 (stage, 5.78.177.119) | Vector store, ~81 objects, node `ns_weaviate` | None |
| 8080 | Weaviate 1.37.0-rc.1 (live, 5.78.189.252) | Vector store, ~43 objects, node `ns_weaviate` | None |

Both hosts run on Hetzner. Both share the node name `ns_weaviate`. Live runs a release candidate, `1.37.0-rc.1`, which may carry unfixed bugs not yet addressed in a stable release.

---

## What We Confirmed

**Read:** Pulled the schema and objects from both stores without credentials. HTTP 200 on both.

**Write:** Inserted a marked canary record into the FakeIndex class on stage. Write returned HTTP 200. Confirmed write succeeds on live as well, HTTP 200.

**Delete:** Removed the stage canary. Delete returned HTTP 204. Re-queried the canary ID and got HTTP 404, confirming the record was gone. Confirmed delete succeeds on live as well, HTTP 204.

The stage canary UUID was `66db8bac-3d70-4c13-b076-9741bbaedd53`, written to the FakeIndex class. Write 200, delete 204, verify 404. Every test artifact we created we removed.

---

## Data Exposed

Both stores carry an identical schema across four classes.

| Class | Fields | Content |
|-------|--------|---------|
| Documents | document_id, chunk_id, metadata, preview, chunk_text | Full document corpus used to support fact-check claims |
| DocumentURLIndex | document_id, url, maps_to | URL-to-document mapping table |
| RedAlerts | document_id, chunk_id, metadata, preview, chunk_text | High-severity flagged content, same schema as Documents |
| FakeIndex | url, maps_to (array of UUIDs), explanation | Curated list of fake or misleading URLs, the platform's core trust product |

Stage holds about 81 objects. Live holds about 43. Stage is ahead of live and is the leading environment, likely used for testing new content before promotion.

The data class is fact-checking and content reliability editorial data. FakeIndex records reference namedsource.com post paths and carry short editorial explanations of why a URL is flagged. RedAlerts contains high-severity flagged content. If embargo procedures exist for fact-check publishing, contents in RedAlerts may be pre-publication material. Documents and DocumentURLIndex expose the entire evidence base used to support fact-check claims. We enumerated class names, field names, and counts only. We did not exfiltrate the corpus.

---

## Impact

**FakeIndex tampering, the core trust product.** The FakeIndex is NamedSource's editorial output, a curated registry of URLs flagged as fake or misleading. Write access allows two attacks. Whitewashing: delete legitimate fake-URL entries to remove known disinformation sources from the index, so the platform's output silently becomes incomplete. Weaponized censorship: insert accurate URLs as fake, so the platform flags real reporting as disinformation. Neither attack requires authentication. Both are silent and leave no application-layer audit trail.

**Dual-environment exposure.** Stage and live are both open. A remediation that closes one leaves the other exposed. Stage carries more data and is the leading environment.

**Full content corpus read.** Documents and DocumentURLIndex expose the source documents and the URL-to-document mapping behind every fact-check claim. Read access is sufficient to copy the full research corpus.

**Version risk.** Live runs a release candidate, `1.37.0-rc.1`. RC builds may carry unfixed bugs.

---

## Remediation

**Immediate (no code change required):** Firewall port 8080 on both 5.78.177.119 and 5.78.189.252 to the internal network only.

**Short-term:** Enable Weaviate's API-key or OIDC authentication on both environments. Treat stage with the same controls as live, since stage carries more data.

**Medium-term:** Add canary records to both stores to detect unauthorized writes. Add audit logging for write and delete operations. Monitor for changes to the FakeIndex class outside the editorial workflow.

---

## Disclosure

Finding documented 2026-06-20 under NuClide Research responsible-disclosure practice. Prior coordinated disclosures from this researcher include CVE-2025-4364 and ICSA-25-140-11, both through CISA.
