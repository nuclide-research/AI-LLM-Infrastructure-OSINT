# Qdrant Snapshot/Unauth — Disclosure Ledger

_NuClide Research · started 2026-05-04_
_Companion to: [`backup-snapshot-services-survey-2026-05.md`](../backup-snapshot-services-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](../qdrant-tier2-cloud-survey-2026-05.md)_

---

## Purpose

This ledger tracks coordinated-disclosure status for the operators identified in the Qdrant tier-2 + Backup-Snapshot surveys. **Operator identities are redacted** until either (a) the 30-day disclosure window elapses without remediation, or (b) the operator confirms remediation and consents to public attribution.

The redaction is the same coordinated-disclosure courtesy NuClide extends in every disclosure: name the IP and the role/sector, never the operator, until the window is complete.

---

## Disclosure pipeline (2026-05-04 batch)

| # | IP | Role / sector | Severity | Disclosure draft staged | Sent | Acknowledged | Remediated |
|---|---|---|---|---|---|---|---|
| 1 | 51.79.9.102 (OVH-CA) | Brazilian-Portuguese citizenship-application SaaS — passport/certidão OCR archive (125,651 docs), email archive (238,765), tasks (287,401) | **CRITICAL** | yes | _pending_ | _pending_ | _pending_ |
| 2 | 146.59.71.151 (OVH-FR) | EU CRM SaaS — leads (112K) + WhatsApp + emails + interactions + decisions; 7-day rolling daily snapshots | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 3 | 193.70.33.74 (OVH-FR) | EU multi-tenant RAG SaaS backup server — 226 GB, 1,800+ snapshots, 18-month retention, cross-tenant exposure | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 4 | 51.79.54.120 (OVH-CA) | Brazilian B2B distributor CRM (dual-brand) — 70K customer records + product/vendor catalogs | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 5 | 51.83.116.239 (OVH-FR) | Colombian academic-library AI chatbot SaaS dev env — multi-university tenants (UniAndes, UniMagdalena, ECCI, others) | **MEDIUM** | yes | _pending_ | _pending_ | _pending_ |
| 6 | 51.68.226.121 (OVH-FR) | EU resilience-monitoring SaaS — `dora_docs` knowledge base, 212 daily snapshots = 18.6 GB | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 7 | 51.178.83.102 (OVH-FR) | Pharma data platform — 784K-point hybrid-search index, 9 GB cumulative snapshots | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 8 | 51.75.255.241 + 51.75.252.52 (OVH-FR) | Multi-tenant chat-AI SaaS (Russian-language) — 45 production + 10 dev customer-company collections | **HIGH** | yes | _pending_ | _pending_ | _pending_ |
| 9 | 51.91.136.93 (OVH-FR) | RAG-as-a-service operator — 6 customer/job-numbered Qwen3-embedding corpora, 458K total points | **MEDIUM** | yes | _pending_ | _pending_ | _pending_ |
| 10 | 172.236.144.25 (Linode/Akamai-SG) | Vietnamese AI/Notion-tooling — `fpt_*` corporate-policy + speaker-identity collections | **MEDIUM** | yes | _pending_ | _pending_ | _pending_ |
| 11 | 195.154.82.157 (Scaleway) | Operator hidden behind Traefik default cert | LOW (operator unidentifiable) | n/a | n/a | n/a | n/a |

### Unidentified operators (no TLS on :443, OVH default rDNS only)

These hosts are part of the same survey but cannot be operator-attributed without further pivots. Listed for completeness:

| IP | Snapshot exposure observed |
|---|---|
| 137.74.118.71 | `thirard_expert` collections (~1.8 MB snapshots) — Thirard appears to be a French locksmith brand; operator unconfirmed |
| 141.95.107.232 | `pim-hybrid` (199 MB snap) — Product Information Management RAG |
| 151.80.234.120 | (no snapshot exposure observed) |
| 167.114.115.192 | `hce_chunks`, `epc_feedback` (small daily snaps) |
| 172.104.46.174 | (no snapshot exposure observed) |
| 51.75.26.136 | (no snapshot exposure observed) |

---

## Disclosure procedure

For each identified operator above:

1. **Email draft prepared** at `~/recon/<operator-slug>-disclosure-2026-05-04/` (private, off-repo)
2. **30-day coordinated-disclosure window** opens at the date the email is sent
3. **Re-probe schedule** during the window:
   - First 24h: every 6h (verify operator received + initial response)
   - 24h – 72h: every 12h
   - 72h – 7d: daily
   - 7d – 30d: weekly
4. **Re-probe leading indicators** for each host:
   ```bash
   curl http://<ip>:6333/collections
   # → 401 Unauthorized = remediated (api_key set)
   # → 200 OK with collections list = unfixed, attack continuing
   # → connection refused = bound to localhost or firewalled (also remediated)
   ```
5. **At day 30** if unremediated: lift the operator-identity redaction in the public case study; update this ledger with the operator's name and full technical detail.
6. **At remediation confirmation**: update this ledger ("Remediated: <date>"); do NOT lift redaction without operator's explicit consent. Some operators prefer to remain redacted even after fixing.

---

## Aggregate metrics (informational)

- **663 unauth Qdrant instances** identified across the tier-2 cloud survey
- **16 of 663** have pre-built snapshot files = direct bulk-exfiltration vectors
- **All 663** are vulnerable to remote-snapshot-creation-and-download via `POST /snapshots` (NuClide did not exercise this, but the surface exists)
- **10 of 16** snapshot-exposing operators identified via TLS cert pivots
- **2 of 663** broader Qdrant-only operators identified opportunistically during disclosure-pipeline buildup (aglets, metabiblioteca)

---

## Update log

_(reverse chronological — most recent on top)_

### 2026-05-04 — Pipeline initialized

- All 10 identifiable snapshot-exposing operators have disclosure drafts staged
- 2 additional Qdrant-only operators (aglets, metabiblioteca) added to the pipeline
- Public ledger established at this file
- Operator identities redacted in [`backup-snapshot-services-survey-2026-05.md`](../backup-snapshot-services-survey-2026-05.md) until disclosure windows complete
- _Nothing sent yet._ Send order priority: 1, 4, 7, 8, 6, 2, 3, 9, 5, 10
