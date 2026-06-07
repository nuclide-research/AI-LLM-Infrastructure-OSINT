# Disclosure log: tweet-optimize.com / 65.108.107.240

_NuClide Research · finding: 1.21M facial embeddings unauth on Milvus_
_Case study: [`../multi-tweet-optimize-facial-recognition.md`](../multi-tweet-optimize-facial-recognition.md)_
_Evidence pack: [`../../../evidence/tweet-optimize-2026-05-03/`](../../../evidence/tweet-optimize-2026-05-03/)_

---

## Disclosure timeline

### 2026-05-03: Initial disclosures sent

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868, T5882, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K7003, K942

<!-- ksat-tag:auto-generated:end -->

Four parallel channels:

| Channel | Recipient | Sent | Acknowledged | Action observed |
|---|---|---|---|---|
| Operator direct | tweet-optimize.com `/contact` form | 2026-05-03 | _pending_ | _pending_ |
| Platform, privacy | privacy@onlyfans.com (Cc fenix.eurep@dapr.pl) | 2026-05-03 | _pending_ | _pending_ |
| Hosting, abuse | abuse@hetzner.com | 2026-05-03 | _pending_ | _pending_ |
| Regulator, DPA | tietosuoja@om.fi (Finnish DPA) | 2026-05-03 | _pending_ | _pending_ |

Disclosure email drafts archived locally only (not in this public repo) at `~/recon/tweet-optimize-disclosure/email-{onlyfans,hetzner,finnish-dpa,operator}.md` until acknowledged or until publication is appropriate.

### 2026-05-03 19:48 UTC: Post-disclosure exposure check

Re-probed the target immediately after disclosure was sent. **Exposure still live**, counts unchanged:

```
GET  /healthz                              → "OK"
POST /v2/vectordb/collections/list         → ["psos","onlyfans"]
POST /entities/query (onlyfans count)      → 897111
POST /entities/query (psos count)          → 313066
```

Raw capture: [`../../../evidence/tweet-optimize-2026-05-03/raw/60-post-disclosure-check.txt`](../../../evidence/tweet-optimize-2026-05-03/raw/60-post-disclosure-check.txt)

This documents that the operator had not pre-emptively closed the exposure prior to receiving the disclosure. Whether they close it on receipt, and how quickly, is the next data point.

---

## What we're tracking

For each channel, three observable states from this side:

1. **Acknowledged**, recipient sent any reply (auto-responder or human)
2. **Action by operator**, the Milvus auth state changes (port closed, RBAC enforced, instance taken down)
3. **External update**, Hetzner internal ticket #, OnlyFans takedown, Finnish DPA case #, regulator notice

The Milvus auth state is the leading indicator. Periodic re-probes (one curl, count + healthz) will show change immediately:

```bash
curl -sS http://65.108.107.240:9091/healthz
curl -sS -X POST http://65.108.107.240:19530/v2/vectordb/collections/list \
  -H 'Content-Type: application/json' -d '{"dbName":"default"}'
```

Three observable change states:
- **No change**, endpoints still return `OK` + collection list → operator inaction
- **Closed at network**, connection refused / timeout → operator firewalled the port
- **Closed at app**, endpoints return 401/403 / require auth header → operator enabled RBAC

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

_(reverse chronological, most recent on top once entries accumulate)_

### 2026-05-04 ~20:50 UTC: Elastic security team responded; out-of-scope per their own VDP

Elastic Information Security (`Help-At-Elastic <elasticprod@service-now.com>`) opened ticket **SEC0006144** in their internal queue and redirected to their HackerOne program at `hackerone.com/elastic`. Likely triaged from the public X thread on May 3 that tagged `@OnlyFans` and `@Hetzner_Online`.

Per Elastic's own published VDP:

> "Security issues in third party systems, domains, services and components fall outside this policy and are not eligible for a bounty."

The exposure is operator misconfiguration on **Milvus** (Zilliz, not an Elastic product), so a HackerOne resubmission would close N/A regardless. Independently, HackerOne gates higher-tier programs by **Signal** (researcher reputation), fresh accounts cannot submit to Elastic's program until reputation is built on lower-tier programs first.

**Net:** Disclosure to Elastic's security channel was non-substantive (auto-routing only, no engagement on the finding itself). No further follow-up planned via Elastic; the operator / Hetzner / Finnish DPA channels remain the meaningful tracks.

This is a recurring pattern worth flagging across the broader survey series: vendor security teams auto-redirect operator-misconfig reports to bounty-platform queues even when the finding is explicitly out of their VDP scope, and bounty-platform Signal-gating then locks new researchers out of submitting to those same queues. The friction has structural implications for outside-disclosure of vendor-shipped-but-customer-misconfigured infrastructure exposures.

---

### 2026-05-04 ~13:00 UTC: Re-probe #3 (~24 hours post-disclosure)

**Exposure remains live.** `/v2/vectordb/collections/list` still returns `["psos","onlyfans"]` without auth. The `onlyfans` collection schema confirmed unchanged: `id, mongo_id, image_id, embedding, bbox1-4`, face-bounding-box pipeline still in production state.

24 hours post-disclosure-send. **No remediation observed from the operator side. No public acknowledgment from any of the four channels** (operator, Fenix/OnlyFans, Hetzner abuse, Finnish DPA). Within normal response window for Hetzner abuse (typically 48-72h) and Finnish DPA (typically 7+d). Operator and OnlyFans/Fenix windows are both open but not yet bounded by industry norms.

### 2026-05-03 ~late evening UTC: Re-probe #2

**Exposure remains live.** Counts unchanged at 897,111 onlyfans + 313,066 psos; `/healthz: OK`; `/v2/vectordb/collections/list` returns `["psos","onlyfans"]` without auth header.

Several hours post-disclosure-send. No state change observed from the operator side. No acknowledgment from any of the four channels (operator, Fenix/OnlyFans, Hetzner abuse, Finnish DPA) yet, within normal response windows for all four.

Captured to: `evidence/tweet-optimize-2026-05-03/raw/61-post-disclosure-recheck-2.txt`
