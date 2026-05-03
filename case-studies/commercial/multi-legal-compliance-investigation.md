# Unknown Operator — Legal / Compliance Investigation Platform — Unauthenticated Qdrant with Sensitive Schema

_NuClide Research · 2026-05-03_

---

## Summary

A Qdrant instance on a DigitalOcean VPS exposes an unauthenticated endpoint with a collection schema consistent with a RAG-backed legal casework or compliance investigation platform. Collections include `investigation_data`, `case_drafts`, `messages`, `attachments`, `sessions`, and `compliance_knowledge`. All collections returned empty at time of probe — the instance may be pre-production, freshly cleared, or rate-limited. The schema alone is sufficient to classify the risk: if populated, this endpoint exposes among the highest-sensitivity data classes (active legal investigations, case drafts, compliance findings, case attachments). Flagged for re-probe.

---

## Infrastructure

| Field | Value |
|---|---|
| IP | 167.172.120.218 |
| Hosting | DigitalOcean |
| Open port | 6333 (Qdrant — public, unauthenticated) |
| Likely function | RAG-based legal/compliance investigation tool |
| Discovery date | 2026-05-03 |
| Disclosure status | Pending |

---

## Collections

| Collection | Inferred Purpose |
|---|---|
| `investigation_data` | Primary case investigation records |
| `case_drafts` | In-progress legal or compliance case documents |
| `messages` | Communication records (internal or case-related) |
| `attachments` | Document attachments associated with cases |
| `sessions` | User/agent session state |
| `compliance_knowledge` | RAG knowledge base — compliance regulations, policies |

---

## Findings

### F1 — Unauthenticated Qdrant Endpoint on Legal Casework Infrastructure (CRITICAL — if populated)

The Qdrant REST API at `http://167.172.120.218:6333` requires no credentials. Collections are enumerable and scrollable without authentication. The collection schema maps directly to a legal case management workflow:

- `investigation_data` + `case_drafts` → active casework content
- `attachments` → supporting documents (contracts, evidence, filings)
- `messages` → communications tied to cases
- `compliance_knowledge` → embedded regulatory corpus used for RAG retrieval
- `sessions` → session-scoped state, potentially including user identity

All collections returned empty vectors during initial probe. Empty state does not reduce severity — the access control gap persists regardless of data load. Any future write to these collections is immediately accessible to unauthenticated clients.

### F2 — Schema Confirms High-Sensitivity Data Classification (HIGH)

The collection naming is not generic. `case_drafts` and `investigation_data` indicate a workflow where legal strategy, evidence summaries, or compliance violation findings are being embedded and stored. If this platform is used by law firms, compliance officers, or enterprise legal teams, the exposed data would typically carry:

- Attorney-client privilege
- Work-product doctrine protection
- Regulatory confidentiality obligations (GDPR Art. 9, sector-specific rules)
- Trade secret status for compliance findings prior to remediation

The risk is asymmetric: the schema reveals exactly what will be present if the instance is populated, allowing targeted re-probe.

### F3 — No Tenant Isolation Visible at Schema Level (MEDIUM)

No per-tenant namespacing is evident in the collection names. A single-tenant deployment (one organization, one instance) would still be fully exposed. A multi-tenant deployment — multiple organizations' cases in one Qdrant instance — would be catastrophic: all tenants' investigation data accessible to any single probe.

---

## Remediation

Enable Qdrant authentication before loading any case data:

```yaml
# config.yaml
service:
  api_key: <strong-random-key>
```

Restrict port 6333 to the application subnet via firewall. Do not expose vector database endpoints to the public internet. If this is a multi-tenant deployment, enforce collection-level or namespace-level isolation at the application layer in addition to database-level auth.

---

## Disclosure

- **Discovered:** 2026-05-03
- **Status:** Pending — operator not identified; collections empty at time of probe
- **Action:** Re-probe warranted. If populated on follow-up, escalate immediately — legal casework data constitutes among the highest-impact breach classes in enterprise AI deployments.
