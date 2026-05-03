# Qdrant on Public Cloud — Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Sweep of 1.83M IPs across 28 cloud-provider /16 ranges (DigitalOcean, Hetzner, Vultr) on port 6333 → 9,462 live hosts (partial scan, killed at ~40% coverage) → 151 masscan hits → **61 confirmed Qdrant instances** via `/collections` → `{"result":{...}}` fingerprint. **All 61 unauthenticated.** 48 of 61 contain actual vector collections with payload data.

This is the inverse of the Flowise result: Qdrant ships with auth disabled by default and the default has not changed meaningfully across the operator population sampled here.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 6333 --rate 6000 (partial, ~40% coverage)
  → 151 masscan hits on :6333

/home/cowboy/go/bin/httpx -p 6333 -path /collections -mc 200 -ms '"result"'
  → 61 confirmed Qdrant instances

aiapp-probe.py (deep enumeration)
  → collections list, per-collection scroll (2 points with_payload)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Masscan hits on :6333 | 151 |
| Confirmed Qdrant (httpx) | 61 |
| Unauthenticated | **61 (100%)** |
| With collections (non-empty) | 48 |
| Empty / fresh installs | 13 |

---

## Notable Exposures

### 1. Pingu — Crypto Trading AI + Nova Drug Discovery Agent

**Host:** `45.76.20.46:6333` (Vultr)

**Collections (25 total):**
`system_learnings`, `findings`, `mol_batch_results`, `pingu_setups`, `pingu_master`, `pingu_rules`, `pingu_sol`, `pingu_btc`, `pingu_eth`, `trade_outcomes`, `strategy_decisions`, `account_moves`, `nova_status_checks`, `mol_decisions`, `mol_scores`, `account_insights`, `mem0_memories`, ...

**What's exposed:**

The operator is running two parallel AI agent systems:

**Crypto trading agent ("Pingu"):**
- `trade_outcomes` — live BTC/ETH/SOL/DOGE trade records. Example: `{"asset": "BTC", "direction": "long", "outcome": "hit_tp1", "pnl_pct": 0.648, "reasoning": "long BTC at 77100.0", "timestamp": "2026-04-17T14:27:11"}`
- `strategy_decisions` — full AI reasoning traces for each trade: RSI values, funding rates, multi-factor analysis, `"direction": "wait"` / `"long"` decisions
- `system_learnings` — 7-day performance summaries: `"7-day performance: 62% accuracy (10/16), avg PnL -6.0%"`
- `pingu_btc`, `pingu_eth`, `pingu_sol` — per-asset strategy state

**Molecular optimization agent (Nova competition):**
- `mol_batch_results` — batch molecular screening results
- `findings` / `strategy_leaderboard` — competition leaderboard: `"aldehyde_170060_exploit"` strategy ranked #1 with score 0.1115
- `nova_status_checks` — epoch-by-epoch competitive standing: `"our_best_ranks": {"21553": 26, "21554": 20}` vs winning VBS scores
- `mol_reactant_profiles`, `mol_analysis`, `mol_constraints`, `mol_decisions` — full molecular design pipeline memory

**Severity:** HIGH — active financial trading system with live position data and strategy IP exposed. Competition entries with unreleased research results.

---

### 2. Watzis — Vietnamese AI Assistant (PII in Memory)

**Host:** `149.28.77.155:6333` (Vultr)

**Collections:** `watzis_longterm_memory`, `hybrid_watzis_longterm_memory`, `file_context`, `watzis_file_context`, `working_memory`, `longterm_memory`, `mem0migrations`

**What's exposed:**

Persistent long-term memory store for a multi-user AI assistant, likely built on [Mem0](https://mem0.ai). Users are Vietnamese-speaking, one confirmed student.

Sample payloads from `watzis_longterm_memory`:
- `"ví của tôi có 100000 VND"` — "my wallet has 100,000 VND" (financial data)
- `"số định danh cá nhân của tôi là gì"` — "what is my personal identification number?" (national ID query)
- `"Thông tin trên căn cước công dân"` — "information on citizen identification card" (citizen ID data discussion)
- `"Cần chuẩn bị các loại axit"` — "Need to prepare types of acid" (chemistry lab context)
- `"Lớp học hóa của tôi bắt đầu vào 7h tối"` — "My chemistry class starts at 7pm" (student identifying info)

All records include `user_id` (MongoDB ObjectID format), `session_id`, `run_id`, and creation timestamps. Multiple distinct users confirmed (`user_id` field varies).

**Severity:** HIGH — multi-user platform with Vietnamese user national ID discussions and financial data in unprotected persistent memory. PDPA/Vietnamese data protection obligations implicated.

---

### 3. Rubbl / Claude Code Deployment SaaS (Internal SOPs)

**Host:** `159.203.25.162:6333` (DigitalOcean)

**Collections:** `viral_content_rubbl`, `viral_content`, `user_memories`, `knowledge_base`, `sops_internal`

**What's exposed:**

Internal standard operating procedures for what appears to be a Claude Code deployment/automation service.

Sample `sops_internal` records:
- SOP CC-005: "Static Site Deployment via Caddy on DigitalOcean"
- SOP S-004: "Thread Resolution & Title Generation"
- Collection also contains `user_memories` (user interaction history) and `knowledge_base`

**Severity:** MEDIUM — proprietary operational documentation and user memory data exposed.

---

### 4. Legal Compliance Investigation Platform

**Host:** `167.172.120.218:6333` (DigitalOcean)

**Collections:** `investigation_data`, `messages`, `sessions`, `case_drafts`, `attachments`, `compliance_knowledge`

**What's exposed:** Collection names indicate a legal/compliance investigation workflow platform. The schema (`case_drafts`, `attachments`, `investigation_data`) suggests casework data. Collections returned empty during this probe — data may have been cleared or query rate-limited.

**Severity:** CRITICAL if populated — legal casework and compliance investigation data is highly sensitive.

---

### 5. Nomothesia — Greek Legal Database

**Host:** `138.68.18.121:6333` (DigitalOcean)

**Collections:** `nomothesia_laws`, `n4495_v6`, `nok_v1`, `n4495_primary_kodified_v4`, `nomothesia_laws_v2`, `n4495_primary_v4b`, `n4495_hybrid_v3`, `nomothesia`

Greek legal text vector database. [Nomothesia](https://www.nomothesia.gr) is a public Greek law portal — the underlying corpus is public, but the vector representations and retrieval infrastructure being exposed indicates this is a RAG service with potential system prompt and query log exposure through other attack surfaces.

**Severity:** LOW — source data is public, but infrastructure exposure indicates attack surface for the associated application.

---

## Version Distribution

Qdrant does not serve version info on an unauthenticated path in most configurations. All confirmed instances returned `null` version. The `/` root endpoint and `/version` path are not standardized across deployments.

---

## Why This Matters

Qdrant's `/collections` endpoint, when unauthenticated, exposes:
1. **What data the system holds** — collection names alone reveal the business (trading, legal, medical, financial)
2. **The actual document payloads** — via `/collections/{name}/points/scroll` with `with_payload: true`
3. **Full exfiltration path** — `scroll` with `next_page_offset` allows complete dataset extraction without authentication

Unlike Flowise (which stores API keys), Qdrant stores the **data that AI systems reason over** — often the most sensitive data the operator handles.

---

## Probe Tooling

- `data/aiapp-probe.py` — Qdrant prober uses `/collections` → enumerate → `/collections/{n}/points/scroll` with `with_payload: true` on first collection
- httpx filter: `/home/cowboy/go/bin/httpx -p 6333 -path /collections -mc 200 -ms '"result"'`

---

## Discoverer

NuClide Research — nicholas@nuclide-research.com

No data was modified or exfiltrated beyond minimal payload sampling (2 records per collection) to confirm severity. Scroll was used only to prove data accessibility.
