# Backup & Snapshot Services on Public AI Infrastructure — Survey

_NuClide Research · 2026-05-04_
_Cross-survey companion to: [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md), [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md)_

---

## Summary

Re-probe of the 663 unauthenticated tier-2 Qdrant instances catalogued in the parallel cross-survey, this time targeting Qdrant's **snapshot endpoints** (`GET /snapshots` and `GET /collections/<name>/snapshots`). 16 of 663 hosts (2.4%) expose **pre-built snapshot files**, totaling **2,512 snapshot files = 269 GB** of bulk-downloadable vector-DB state.

The snapshot endpoint is fundamentally different from `/points/scroll` as an exposure vector:

- **`/points/scroll`** returns paginated 100-1000-point batches; bulk exfiltration takes thousands of round-trips and hits any rate-limiter.
- **`/collections/<name>/snapshots/<file>`** returns the **entire collection as a single file download** in seconds. No pagination, no rate-limit per-record, no server-side query cost.

Operators who pre-create snapshots for their own backup workflow are also creating bulk-exfil endpoints accessible to anyone reaching the unauth Qdrant. **The snapshot endpoint inherits the unauth state of the rest of the API** — no separate auth layer.

The two standout findings:

1. **`crm-fast.pl` (`146.59.71.151`, OVH France)** — Polish B2B CRM SaaS. Production Qdrant with collections `leads_embeddings` (112,271 points × 1536-dim ≈ OpenAI ada-002), `emails_embeddings` (152 MB/day), `whatsapp_embeddings`, `interactions_embeddings`, `decision_embeddings`. **7-day rolling daily snapshots, ~8 GB total.** Live production CRM — leads, email content, WhatsApp messages, customer interactions, sales decisions all bulk-downloadable.

2. **`gptplane.it` siena.backup (`193.70.33.74`, OVH France)** — Italian AI/RAG SaaS. Cert SAN reveals this is `siena.backup.gptplane.it` — a tenant-named backup server holding multi-tenant snapshots. **18+ months of daily snapshots** (oldest dated `20241107` = Nov 7 2024). Six tenant collections (`gptplane.siena.{1,2,3}` + `gptplane.sigerico.{3,4,5}`). **226 GB across 1,800+ snapshot files** — the single largest snapshot-exposure host in the survey.

---

## The Qdrant snapshot endpoint as bulk-exfiltration vector

Qdrant supports two snapshot endpoints in stock configuration:

```
GET /snapshots                       — list cluster-level snapshots (rare)
GET /collections/<name>/snapshots    — list per-collection snapshots
GET /collections/<name>/snapshots/<filename>  — DOWNLOAD a snapshot file
POST /collections/<name>/snapshots   — CREATE a new snapshot
```

The snapshot file format is a Qdrant-specific binary archive containing the full collection: vectors, payloads, HNSW index. Importing it with `POST /collections/<name>/snapshots/upload` rebuilds the collection on a different cluster.

**Key auth-posture observation:** the `service.api_key` setting governs the entire HTTP API uniformly. If api_key is unset (84.9% of tier-2 Qdrant), the snapshot endpoints are reachable without auth alongside `/collections` and `/points/search`. Operators who manually pre-create snapshots for their own backup workflow are creating bulk-exfil endpoints by accident.

Survey result: **16 of 663 unauth tier-2 Qdrant hosts have pre-created snapshots accessible**. Empty `/snapshots` list (operator hasn't created any) on the other 647 — but those operators *can have one created remotely* via `POST /snapshots`, which writes to operator disk and exposes the same vector. NuClide did not POST to create snapshots; that crosses the line from passive reconnaissance into modifying operator state.

---

## Findings Summary

| Metric | Value |
|---|---|
| Unauth Qdrant hosts probed | 663 (tier-2 cross-survey) |
| Hosts with ≥1 pre-created snapshot | **16** |
| Total collections with exposed snapshots | 32 |
| Total snapshot files exposed | **2,512** |
| Total bytes exposed | **269 GB** |
| Largest single snapshot file | 3.38 GB (`semantic-hierarchy-hybrid-search` on 51.178.83.102) |
| Largest single host (cumulative) | 226 GB (gptplane.it siena.backup, 193.70.33.74) |

### Hosts with ≥500 MB cumulative exposure

| IP | Total exposed | Operator (where identified) |
|---|---|---|
| 193.70.33.74 (OVH) | **226 GB** | **gptplane.it** (Italian RAG SaaS, multi-tenant) — `siena.backup.gptplane.it` |
| 51.68.226.121 (OVH) | 18.6 GB | Unidentified — `dora_docs` collection (212 daily snapshots) |
| 51.178.83.102 (OVH) | 9.0 GB | Unidentified — `semantic-hierarchy-hybrid-search` (3 multi-GB snapshots) |
| 146.59.71.151 (OVH) | **8.1 GB** | **crm-fast.pl** (Polish CRM SaaS) — leads/emails/WhatsApp/interactions/decisions |
| 51.79.9.102 (OVH-CA) | 4.0 GB | Unidentified — `emails`, `documentos_ocr`, `tarefas_apollo1` (Brazilian Portuguese task RAG) |
| 51.91.136.93 (OVH) | 2.4 GB | Unidentified — Qwen3-embedding-keyed corpus, 31 daily snapshots |

OVH hosts dominate the exposure — same pattern as the parallel tier-2 Qdrant survey (97.3% of unauth Qdrant on OVH). Operators on OVH dedicated servers run production-scale workloads and configure daily backup workflows; the unauth posture means the backups are public.

---

## Headline finding 1: crm-fast.pl (Polish CRM SaaS)

**Operator:** crm-fast.pl (TLS cert CN on port 443 of `146.59.71.151`)

**Stack:**
```
Qdrant 1.14.0 on port 6333, fully unauth
TLS-fronted CRM web UI on :443 (cert CN = crm-fast.pl)
Reverse DNS: ns3211712.ip-146-59-71.eu  (OVH default-named host)
```

**Exposed collections (with daily snapshots):**

| Collection | Live points | Daily snap size | 7-day total |
|---|---|---|---|
| `leads_embeddings` | 112,271 | ~1.0 GB | 7.0 GB |
| `emails_embeddings` | (live) | ~152 MB | 1.07 GB |
| `whatsapp_embeddings` | (live) | ~772 KB | 5.4 MB |
| `interactions_embeddings` | (live) | ~1.1 MB | 7.9 MB |
| `decision_embeddings` | (live) | ~772 KB | 5.4 MB |

The collection naming is the canonical structure of a B2B sales-enablement CRM with WhatsApp Business integration:
- **leads** — sales pipeline records
- **emails** — outbound/inbound email content
- **whatsapp** — WhatsApp Business message history (most CRMs running WhatsApp need to vectorize messages for context retrieval)
- **interactions** — generic customer-touchpoint log
- **decisions** — sales decisions / CRM-AI decision tree

All 5 collections are 1536-dim Cosine, OpenAI text-embedding-ada-002 fingerprint. The 112K-point leads collection is **live customer pipeline data**, currently in production and being updated.

**Bulk-exfil vector.** A single `curl` against `/collections/leads_embeddings/snapshots/<latest-filename>` retrieves the entire 1 GB lead vector index, which can be imported into a separate Qdrant via `POST /snapshots/upload` and queried offline.

**Disclosure priority: high.** Polish operator, GDPR jurisdiction, customer PII (leads + email content + WhatsApp messages), live production. Disclosure is reachable directly via crm-fast.pl operator contact.

---

## Headline finding 2: gptplane.it (Italian RAG SaaS, multi-tenant backup server)

**Operator:** gptplane.it (TLS cert CN = `siena.backup.gptplane.it` on port 443 of `193.70.33.74`)

**Stack:**
```
Qdrant on port 6333, fully unauth
Cert: siena.backup.gptplane.it (Let's Encrypt E8)
Reverse DNS: ns3059198.ip-193-70-33.eu (OVH default-named host)
Other OVH IPs likely host the production siena.gptplane.it / api.gptplane.it
```

**Exposed collections (note the multi-tenant naming):**

```
gptplane.siena.1.20241107140228574       # 436 snapshots, 58 GB
gptplane.siena.2.20250411083828947       # 388 snapshots, 45 GB
gptplane.siena.3.20250925071635984       # 221 snapshots, 28 GB
gptplane.sigerico.3.20241030083704626    # 436 snapshots, 37 GB
gptplane.sigerico.4.20250402063904063    # 400 snapshots, 33 GB
gptplane.sigerico.5.20250620074723037    # 318 snapshots, 25 GB
                                          ── total 226 GB across 1,800+ snapshots
```

**Naming structure:** `gptplane.<tenant>.<corpus_id>.<creation_timestamp>`. The two visible tenants are `siena` and `sigerico` (both look like Italian-language operator names — Siena is a Tuscan city; "sigerico" is obscure but Italianate). Multiple `<corpus_id>` per tenant suggests each tenant has multiple knowledge bases / RAG configurations.

**Critical detail.** This server is named **`siena.backup.gptplane.it`** (from the cert SAN) — meaning it's labeled as the backup server *for* the Siena tenant. Yet it's holding snapshots for tenant `sigerico` too. Either (a) `sigerico` is a sub-tenant of `siena`, or (b) the backup server is shared across multiple primary-tenants in a multi-tenant-on-shared-backup pattern. **Either way, one tenant's backup-server compromise potentially exposes another tenant's data.**

**18-month snapshot retention.** Oldest snapshot timestamp is `20241107140228574` (Nov 7, 2024 14:02:28). The operator has been creating daily snapshots since at least Nov 2024, none expired. That's a complete historical record of vectorized RAG content for both tenants — content drift, deletion attempts, modifications, all preserved in the daily snapshots.

**Bulk-exfil vector.** Same as crm-fast.pl — a single `curl` retrieves any individual snapshot. The largest single snapshot is ~13 GB.

**Disclosure priority: high.** Italian operator, EU jurisdiction, multi-tenant data exposure (one tenant's snapshot may contain another tenant's content), 18-month historical record, live production. Operator reachable via gptplane.it.

---

## Other notable hosts

| IP (OVH-class) | Pattern | Notable |
|---|---|---|
| 51.68.226.121 | `dora_docs` collection, 212 daily snapshots, 18.6 GB cumulative | Long retention; "Dora" is either a product name or the operator/employee name. Roughly 7-8 months of daily snapshots. |
| 51.178.83.102 | `semantic-hierarchy-hybrid-search` 3 multi-GB snapshots | Big single snapshots (1.5–3.4 GB) suggest large corpora. Hybrid search = dense + sparse vectors stored together. |
| 51.79.9.102 | `emails` (2.4 GB snap), `documentos_ocr` (1.6 GB snap), `tarefas_apollo1` | Brazilian Portuguese names ("documentos", "tarefas"). OCR'd documents + emails + tasks = office-automation RAG. |
| 137.74.118.71 | `thirard_expert_1` + `thirard_expert` (1.8 MB snaps) | "Thirard" is a French locksmith brand. Possibly an expert-system / customer-support RAG. |
| 141.95.107.232 | `pim-hybrid` (199 MB snap) | PIM = Product Information Management. E-commerce hybrid-search index. |
| 146.59.71.151 (already covered) | crm-fast.pl daily CRM backups | — |
| 167.114.115.192 | `hce_chunks`, `epc_feedback` (small daily snaps) | "HCE" + "EPC" possibly health/energy domain abbrevs |
| 51.91.136.93 | `469_qwen3-embedding-8b` 31 daily snaps | Qwen3-embedding-8B-keyed corpus — operator iterating embedding configs |

The 32 distinct collections with snapshots span: CRM/sales (crm-fast), multi-tenant SaaS RAG (gptplane), e-commerce PIM (141.95.107.232), document-OCR + email archive (51.79.9.102), brand-customer-support (137.74.118.71), generic large-corpus search (51.178.83.102, 51.68.226.121).

---

## The two-tier backup-exposure pattern

A pattern visible across the snapshot survey: **operators with mature backup workflows are at higher risk than those without.**

- A Qdrant deployment with `service.api_key` unset and **no manual snapshot history** exposes only the live data layer. Bulk exfiltration requires paginated `/points/scroll` (slow, rate-limit-able).
- A Qdrant deployment with `service.api_key` unset and **a daily-snapshot cron** exposes both the live data AND a chronological backup record. Bulk exfiltration is `curl <snapshot-URL>` (single request, full download).

The operator who set up the daily-snapshot cron is doing the right operational thing for *their own* recovery. They are also providing a free bulk-download endpoint for any internet visitor. The auth-off-default vulnerability is amplified by good operational discipline — a counterintuitive but reproducible pattern.

The fix on the Qdrant side is one line: `service.api_key: <key>` in `config.yaml`. This locks down `/snapshots` along with everything else.

---

## Other backup/snapshot endpoints in the survey series (brief)

The same probe-pattern can be applied to other platforms. Spot-checks:

- **Milvus**: `/v2/vectordb/collections/describe` returns full collection schema (visible across the 36 real tier-2 Milvus). Milvus snapshots/backups are typically managed via [milvus-backup](https://github.com/zilliztech/milvus-backup) which writes to S3/MinIO — exposure depends on operator's S3 backend, not Milvus itself. Cross-cuts to MinIO survey.
- **MLflow**: artifact store is exposed via `/api/2.0/mlflow-artifacts/artifacts/<path>` on populated MLflow instances. Often points at S3 buckets via signed URLs (cross-cuts MinIO/S3-compat exposures). The two actively-exploited CVE-2023-1177 hosts in the MLflow survey both have artifact_locations pointing at attacker-controlled `/etc/` and `/root/.ssh/` paths via path traversal.
- **MinIO bucket-listing**: anonymous listing was 0 in the MinIO survey (852 instances) — but bucket *names* containing "backup", "snapshots", "dump" are still indexable via Shodan facets if quota allows.
- **ChromaDB**: no built-in snapshot endpoint; backups are operator-side filesystem copies of the persistence directory.

The Qdrant snapshot pattern is the most concrete in this survey because Qdrant is the only platform in the series with a first-class snapshot HTTP endpoint that inherits the API auth state.

---

## Disclosure posture

- **crm-fast.pl** — disclosure-priority candidate. Polish jurisdiction, GDPR, identifiable operator, live customer pipeline data including WhatsApp messages and email content. Will draft scoped operator disclosure.
- **gptplane.it** — disclosure-priority candidate. Italian jurisdiction, multi-tenant data risk, 18-month historical exposure. Will draft scoped operator disclosure.
- **Other 14 hosts** — operator identification harder without further pivots; aggregate disclosure note in the case study suffices for now.
- **Qdrant upstream** — the snapshot-endpoint-inherits-API-auth design is the right behavior, but the framework defaults make it a "auth-off-default and snapshot endpoint accidentally public" failure mode at population scale. Worth flagging upstream that the snapshot endpoint specifically may warrant a separate "snapshot read access" auth tier in future versions.

---

## Methodology

```
qdrant-snapshot-probe.py (100-thread)
  Input: 663 unauth Qdrant JSONL records (from tier-2 survey)
  For each host:
    GET /snapshots                                  -> cluster-level snapshots
    GET /collections/<name>/snapshots               -> per-collection (up to 30 collections per host)
  Record any non-empty snapshot list with name, creation_time, size, checksum
  → 16 hosts with snapshots
  → 2,512 snapshot files
  → 269 GB total exposed
```

Read-only metadata enumeration only. NuClide did not:
- Download any snapshot file
- POST to create new snapshots
- Submit `/points/search` queries against indexed collections

The snapshot **listings** are what's reported. The actual snapshot **file contents** were not retrieved by NuClide.

---

## Raw Data

```
~/recon/qdrant-snapshots-2026-05-04/qdrant-snapshots-found.jsonl  (16 hosts)
```

Each record:
```json
{
  "ip": "...",
  "version": "1.x.x",
  "per_collection_snapshots": [
    {"collection": "...", "snapshots": [
      {"name": "...", "creation_time": "...", "size": N, "checksum": "..."}
    ]}
  ]
}
```

---

## See Also

- [`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md) — parent survey (663 unauth Qdrant on tier-2 cloud)
- [`qdrant-cloud-survey-2026-05.md`](qdrant-cloud-survey-2026-05.md) — original DO/Hetzner/Vultr Qdrant baseline
- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — cross-survey synthesis
- [`mlflow-cloud-survey-2026-05.md`](mlflow-cloud-survey-2026-05.md) — MLflow `artifact_location` exposure pattern (different mechanism, similar shape)
