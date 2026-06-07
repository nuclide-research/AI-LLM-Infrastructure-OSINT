---
type: case-study
title: "EPOLCA — RedisInsight Credential Leak on Industrial Simulation Demo Server"
date: 2026-05-26
severity: MEDIUM
sector: commercial
tags: [redis-stack, redisinsight, chain-b, credential-leak, industrial, MES, demo-data, production-planning]
summary: "RedisInsight exposed the Redis password for an ePolca production planning demo server on Hetzner DE; AUTH succeeded and revealed six keys covering factory simulation results, KPI states, and production orders — all scoped to the EPOLCA_DEMOS namespace."
---

# EPOLCA — RedisInsight Credential Leak on Industrial Simulation Demo Server

**Date:** 2026-05-26
**Target:** 116.203.208.124
**Hostname:** static.124.208.203.116.clients.your-server.de (Hetzner generic rDNS)
**ASN:** AS24940, Hetzner Online GmbH, DE
**Severity:** MEDIUM
**visorlog:** #68

---

## What Was Found

**F1 — RedisInsight unauth on port 8001.** No login required. The stored Redis credential was readable from the GUI.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5854
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

**F2 — AUTH succeeded.** The 60-character generated password worked against Redis 6.2.12 (Redis Stack). OS: Linux 5.15.0-164-generic x86_64. Uptime: 146 days. The server has been running without rotation for nearly five months.

**F3 — EPOLCA_DEMOS namespace exposed.** DBSIZE: 6 keys. Three with TTL. All keys share the `EPOLCA_DEMOS:*` prefix. Key names:

- `EPOLCA_DEMOS:upgrade_text`
- `EPOLCA_DEMOS:history_data_at`
- `EPOLCA_DEMOS:finished_simulation_orders:4:with_incoming`
- `EPOLCA_DEMOS:finished_simulation_orders:4:only_production`
- `EPOLCA_DEMOS:simulation_results_factory_4`
- `EPOLCA_DEMOS:kpi_states`

No full-text search indexes (FT._LIST returns empty). No user records. No PII in key names.

**F4 — Additional surface: port 5000 open, silent.** TCP connection accepted. No HTTP response returned. Port 80 returns nginx 503. No TLS certificate served on the IP directly.

---

## Attribution

ePolca is production planning and sequencing software built by InnovaIT and QRM Institute Spain. It connects to factory ERP/MES systems and sequences manufacturing orders in real time. The algorithm is based on POLCA (Paired-cell Overlapping Loops of Cards with Authorization), a Quick Response Manufacturing technique for regulating flow in complex factory environments.

The product is Spanish. Website: epolca.com. LinkedIn: linkedin.com/company/epolca.

The key namespace `EPOLCA_DEMOS` is unambiguous. This server runs a demo environment for the ePolca platform. The key names map directly to documented product modules: `kpi_states` matches the WIP/KPI dashboard; `simulation_results_factory_4` and `finished_simulation_orders` match the Sequencer module's simulation output; `history_data_at` matches the Orders module's historical data feed.

crt.sh history for epolca.com shows three customer subdomains from 2018: `justorm.epolca.com`, `systa.epolca.com`, `systanl.epolca.com`. The current server hosts demo data only.

---

## Chain

```
RedisInsight :8001 open (no auth required)
  → stored credential readable from GUI
    → AUTH '<60-char generated password>' → +OK
      → DBSIZE: 6 (3 with TTL)
        → FT._LIST → empty (no search indexes)
          → KEYS EPOLCA_DEMOS:* → 6 keys
            → data class: industrial simulation / production planning demo data
              → no PII fields in key names
                → severity: MEDIUM
```

---

## Impact

The credential is live. Any actor who visited port 8001 could read and write all six keys. The `EPOLCA_DEMOS` namespace contains simulation-generated data: factory 4 production orders, KPI states, simulation results. No evidence of real customer data, user records, or PII in the key schema.

The write surface matters here. An attacker could modify `kpi_states` or `simulation_results_factory_4` before a sales demo. Corrupted demo data could affect a prospect's evaluation. For a small SaaS vendor, a failed demo has direct revenue impact.

Port 5000 accepts connections but returns nothing on HTTP. Its role is unknown. It may be the ePolca application backend. If it is, and if it trusts the local Redis without re-authentication, then write access to Redis carries application-layer reach.

Data class remains demo-only based on available evidence. The namespace prefix `DEMOS` is explicit. No key names suggest real customer factories or production environments are on this host.

---

## Pivot Avenues

1. **Port 5000 protocol identification** — the service accepts TCP but ignores HTTP. Try WebSocket upgrade or raw protocol sniffing to identify the application layer (ePolca backend, Flask, Node, or similar)
2. **crt.sh subdomain pivot** — `justorm.epolca.com`, `systa.epolca.com`, `systanl.epolca.com` are 2018-era customer hostnames; resolve them and check if any still point to live infrastructure
3. **Shodan pivot on Redis Stack banner** — search for other hosts sharing the same Redis Stack version (6.2.12) on Hetzner to find additional ePolca deployment nodes
4. **epolca.com JavaScript bundle** — the SPA will contain API endpoint paths and may reference additional server addresses for live customer instances
5. **InnovaIT infrastructure search** — innovait.cat is the developer; their IP space may host additional ePolca demo or staging environments
6. **TTL key analysis** — three of six keys have TTLs, suggesting active simulation activity; TTL values could confirm whether the demo server is in use during a live sales cycle

---

## Remediation

1. Restrict port 8001 to the local network or a private VPN interface; remove public access
2. Enable RedisInsight authentication (Settings → Security)
3. Bind Redis to localhost or a non-public interface
4. Rotate the exposed 60-character credential
5. Audit whether the demo server is network-adjacent to any production ePolca instances; if so, segment them

---

*NuClide Research — Chain B RedisInsight survey, 2026-05-26*
