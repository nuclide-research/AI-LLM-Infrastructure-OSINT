# Case study — Chinese LLM-jacking productized ecosystem

**Date:** 2026-06-09
**Lift-off:** syllabus wandb-sweep follow-up → 137.184.42.189 (Grok2API + Sub2API) → cohort expansion
**Outcome:** scale shifted from single-host to **12,000+ host productized ecosystem with 5+ cousin platforms and 9+ credential-pool MySQL backing stores reachable on the public internet.**

## Population scale

| Shodan dork | Hits | Class |
|---|---|---|
| `http.html:"Sub2API"` | **10,675** | Sub2API frontend ecosystem |
| `http.title:"Sub2API - AI API Gateway"` | **10,380** | Sub2API title-confirmed |
| `http.html:"Grok2API"` | **1,902** | Grok2API backend ecosystem |
| `"Sub2API"` (strict body) | 435 | High-confidence Sub2API |
| `http.html:"feishu/webhook"` | 28 | Feishu-integrated FastAPI (mostly OpenClaw) |
| `"Grok2API"` (strict body) | 2 | High-confidence Grok2API |

This is a **productized open-source ecosystem at internet scale**, not a one-off operator. The methodology gap noted in the Talent Library V2 case study (no academic population study of LLM infrastructure auth posture) extends here too — LLM-jacking proxies have never been measured at population scale academically.

## Upstream identification (CONFIRMED)

Both upstream OSS projects identified, both Chinese-developer GitHub, both highly active:

- **`chenyme/grok2api`** — 5,195 stars, FastAPI MIT, Python. Chinese description: "基于 FastAPI 构建的 Grok 网关...转换为 OpenAI 兼容 API". Multi-account round-robin, streaming, image/video generation, voice. **Pushed today (2026-06-09).** OpenAPI advertises `info.title="Grok2API"`, version `0.1.0` (FastAPI default — codebase tracks `2.0.4.rc4` in pyproject).
- **`Wei-Shaw/sub2api`** — **26,714 stars**, Go + Vue3, LGPL-3.0. Self-description: "open-source relay platform that unifies Claude, OpenAI, Gemini, and Antigravity subscriptions into a single endpoint. Supports account sharing and cost-sharing." Official site `sub2api.org`, demo `demo.sub2api.org`. Image `weishaw/sub2api:latest`.

Both bundle WeChat + LinuxDo OAuth scaffolding. Both ship with `payment_enabled=false` + `registration_enabled=false` defaults (private/closed-pool defaults for the canonical host).

## Cousin platforms in the same ecosystem (newly identified)

Active-banner scan of 124 cohort IPs surfaced sibling platforms beyond Grok2API and Sub2API:

| Platform | Evidence | Function |
|---|---|---|
| **OpenClaw** | `114.132.156.122:80` "OpenClaw Feishu Webhook Server"; titles "OpenClaw 一键部署 - 30秒开始使用" | One-click deploy LLM-jacking proxy, Feishu webhook intake |
| **QClaw Agent** | `137.175.121.65:8081` title "QClaw Agent" | Agent framework in the same family |
| **Spider2Table Studio** | banner title hit | Scraper-as-a-service co-located with proxy infra |
| **Outlook 注册管理面板** | banner title hit | Microsoft account registration management panel (credential seeding) |

The ecosystem is the full vertical stack from Lane B's GitHub-recon: **registration-bots → credential-pool → MySQL backing → OpenAPI-compat relay UI → Sub2API frontend → payment gateway → reseller dashboard.**

## Credential-pool backing stores (the data-layer layer)

9 of 124 cohort IPs have MySQL port 3306 exposed to the public internet:

| IP | Version | TCP handshake | Auth method |
|---|---|---|---|
| 137.175.121.65 | MySQL 8.0.43 | open | mysql_native_password |
| 150.136.160.62 | MySQL 8.4.7 | open | caching_sha2_password |
| 154.44.10.117 | MariaDB | **IP-allowlist** | rejecting Shodan crawler IP 136.37.103.3 |
| 104.168.83.222 | MySQL | **IP-allowlist** | rejecting Shodan crawler IP |
| 120.55.44.20 | MySQL 8.0.46 Ubuntu | open | caching_sha2_password |
| 116.62.18.176 | MySQL 8.0.36 | open | mysql_native_password |
| 123.57.85.94 | MySQL 9.7.0 | open | caching_sha2_password |
| 47.243.233.185 | MySQL | **IP-allowlist** | rejecting Shodan crawler IP |
| 45.76.102.229 | **MySQL 5.7.40 EOL** | open | mysql_native_password |

Three operators selectively IP-allowlist their backing store (block Shodan's crawl IP `136.37.103.3` but allow their own tooling). Six expose handshake-reachable databases — auth still gated by root password, but the database surface is internet-public. One runs MySQL 5.7 (EOL 2023, no security patches).

**Co-location pattern:** `137.175.121.65` runs both `QClaw Agent` on :8081 AND MySQL on :3306. One operator, one VPS, relay UI on top of credential-pool DB. Same as the `137.184.42.189` colocation of Grok2API + Sub2API. This is the small-operator productized pattern.

## Cohort scan summary

- **121 of 124 IPs alive** (97% liveness).
- 103 SSH (:22), 82 :80, 63 :443, 63 :8080, 39 :8000, 9 :8081, 9 :3306, 7 :9000, 1 :8123 (ClickHouse?), 1 :5984 (CouchDB).
- Geographic spread: heavy CN/Aliyun (43.x, 47.x, 8.x, 123.x, 60.x), CN/Tencent (43.x ranges), US (38.x, 70.x, 144.x, 154.x, 162.x, 192.x, 207.x, 216.x — typical DO/Vultr/cheap-VPS clusters), some EU.
- Title diversity: 20 `404 Not Found`, 17 `301 Moved Permanently`, 7 `400 HTTP-to-HTTPS-port`, 5 `没有找到站点` ("site not found"), 5 nginx defaults — many hosts answer only on specific paths, not root.

## Insight #39 cohort — scale-revised

Original Insight #39 framing (pooled-account proxy = attribution laundering) was codified from individual-host observations. The actual cohort scale is **~12,000+ hosts globally** running productized Chinese OSS LLM-jacking proxies (Sub2API + Grok2API + OpenClaw + QClaw Agent + Spider2Table). Attribution laundering at this scale is no longer a per-instance concern — it is a structural feature of the global LLM-jacking shadow market.

The supply chain documented by Lane B agent (registration bots like `ReinerBRO/grok-register`, `cnitlrt/AutoTeam`, `wenfxl/openai-cpa` feeding credential pools; dashboards like `qixing-jk/all-api-hub` aggregating relays) is real and matches what scanner banners showed across the cohort. The classes A/B/C/D taxonomy:

- **Class A** OSS-relay + open registration — observed pattern via `payment_enabled=false` + `registration_enabled=true` (need full SPA config check per host)
- **Class B** OSS-relay + paid subscription — `137.184.42.189` candidate (Stripe + Cloudflare Turnstile present but `payment_enabled=false`; likely B-shell with closed pool)
- **Class C** Pool-of-pools brokerage — `all-api-hub` aggregator class; not directly observed in this 124-IP sample but exists per Lane B GitHub recon
- **Class D** Operator-personal — many of the 5.7.40-EOL-MySQL low-effort VPSes likely fit

## Academic anchor

**Malla: Demystifying Real-world LLM-Integrated Malicious Services** — Lin Zilong et al., USENIX Security 2024. *"the Malla ecosystem: pooled stolen keys, jailbreak-as-a-service, OpenAI-compat reseller storefronts."* This finding is the empirical population data Malla's framework anticipated. Citation handle for future writeup.

## What we didn't do (restraint discipline)

- Zero POSTs to any cohort host.
- Zero `/v1/chat/completions` calls.
- Zero MySQL handshake completions (just TCP banner read).
- Zero attempts to enumerate root-password defaults on the 6 open-handshake MySQL hosts.
- Zero login attempts on Sub2API frontends.
- 121-host enum stayed strictly at banner-grade.

Per `feedback_no_disclosure_recommendations`: zero disclosure recommendations on cohort operators. Attribution direction (whose credentials populate the pool) is the actionable angle, not relay-operator identification.

## Open ends

1. **Per-class population breakdown** (A/B/C/D) would require Sub2API frontend SPA config check on a 50-100 host sample
2. **Cert-CN attribution** sweep via VisorGraph would surface naming conventions
3. **MySQL exposed-backing-store survey** as its own category — co-located DB + LLM-jacking proxy is a recurring infrastructure pattern worth a Cat-NN
4. **All 12,000+ Sub2API host enumeration** is impractical via Shodan UI pagination — needs Censys cross-check
5. **Outlook registration management panel** discovery is a separate finding — Microsoft credential harvesting infrastructure within the same ecosystem, worth its own sub-survey

## Files

- `~/syllabus/cohort-harvest-2026-06-09.json` — Shodan harvest (50 Grok2API + 48 Sub2API + 26 Feishu)
- `~/syllabus/cohort-targets.txt` — 124 unique IPs
- `~/syllabus/cohort-scan.jsonl` — 377 banner records
- `~/syllabus/137.184.42.189-deepen.md` — Lane A architecture deep
- `~/tome/platforms/grok2api.json` + `sub2api.json` — CANDIDATE platform entries
- `~/syllabus/case-study-syllabus-wandb-sweep.md` — master case
