# Disclosure log — tweet-optimize.com / 65.108.107.240

_NuClide Research · finding: 1.21M facial embeddings unauth on Milvus_
_Case study: [`../multi-tweet-optimize-facial-recognition.md`](../multi-tweet-optimize-facial-recognition.md)_
_Evidence pack: [`../../../evidence/tweet-optimize-2026-05-03/`](../../../evidence/tweet-optimize-2026-05-03/)_

---

## Disclosure timeline

### 2026-05-03 — Initial disclosures sent

Four parallel channels:

| Channel | Recipient | Sent | Acknowledged | Action observed |
|---|---|---|---|---|
| Operator direct | tweet-optimize.com `/contact` form | 2026-05-03 | _pending_ | _pending_ |
| Platform — privacy | privacy@onlyfans.com (Cc fenix.eurep@dapr.pl) | 2026-05-03 | _pending_ | _pending_ |
| Hosting — abuse | abuse@hetzner.com | 2026-05-03 | _pending_ | _pending_ |
| Regulator — DPA | tietosuoja@om.fi (Finnish DPA) | 2026-05-03 | _pending_ | _pending_ |

Disclosure email drafts archived locally only (not in this public repo) at `~/recon/tweet-optimize-disclosure/email-{onlyfans,hetzner,finnish-dpa,operator}.md` until acknowledged or until publication is appropriate.

### 2026-05-03 19:48 UTC — Post-disclosure exposure check

Re-probed the target immediately after disclosure was sent. **Exposure still live**, counts unchanged:

```
GET  /healthz                              → "OK"
POST /v2/vectordb/collections/list         → ["psos","onlyfans"]
POST /entities/query (onlyfans count)      → 897111
POST /entities/query (psos count)          → 313066
```

Raw capture: [`../../../evidence/tweet-optimize-2026-05-03/raw/60-post-disclosure-check.txt`](../../../evidence/tweet-optimize-2026-05-03/raw/60-post-disclosure-check.txt)

This documents that the operator had not pre-emptively closed the exposure prior to receiving the disclosure. Whether they close it on receipt — and how quickly — is the next data point.

---

## What we're tracking

For each channel, three observable states from this side:

1. **Acknowledged** — recipient sent any reply (auto-responder or human)
2. **Action by operator** — the Milvus auth state changes (port closed, RBAC enforced, instance taken down)
3. **External update** — Hetzner internal ticket #, OnlyFans takedown, Finnish DPA case #, regulator notice

The Milvus auth state is the leading indicator. Periodic re-probes (one curl, count + healthz) will show change immediately:

```bash
curl -sS http://65.108.107.240:9091/healthz
curl -sS -X POST http://65.108.107.240:19530/v2/vectordb/collections/list \
  -H 'Content-Type: application/json' -d '{"dbName":"default"}'
```

Three observable change states:
- **No change** — endpoints still return `OK` + collection list → operator inaction
- **Closed at network** — connection refused / timeout → operator firewalled the port
- **Closed at app** — endpoints return 401/403 / require auth header → operator enabled RBAC

---

## Re-probe schedule

| Window | Cadence | Rationale |
|---|---|---|
| First 24h | every 6h | typical operator-receipt-and-fix window |
| 24h-72h | every 12h | regulatory 72h breach-notification window |
| 72h-7d | daily | extended operator-no-response watch |
| 7d-30d | weekly | regulator response window |
| 30d+ | monthly | long-tail audit |

Each re-probe captured to `evidence/tweet-optimize-2026-05-03/raw/6X-recheck-<date>.txt`.

---

## Subsequent log entries

_(reverse chronological — most recent on top once entries accumulate)_

_— pending —_
