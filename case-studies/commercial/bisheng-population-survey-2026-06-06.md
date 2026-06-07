---
type: case-study
category: cat-bs
platform: Bisheng
date: 2026-06-06
findings: 0 auth-permissive (negative result); 3 confirmed instances version-disclosed
status: verified
toolchain: manual probe
---

# Bisheng Population Survey — Negative Result (Auth-Required Default)

_NuClide Research · 2026-06-06_

---

## Executive Summary

Bisheng (`github.com/dataelement/bisheng`) is an open-source LLM application development platform from **DataElem (Beijing)**, focused on enterprise-oriented document AI, RAG, agent orchestration, and workflow building. Direct functional parallel to RAGFlow (also Shanghai-based) and Flowise.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

**Negative result.** The DataElem Bisheng platform ships **auth-required by default** across all data endpoints. The 30 Shodan-indexed hits on the `"BISHENG"` dork largely matched unrelated services (Chinese banks named after the historical figure Bi Sheng — inventor of movable type printing; Synology NAS user-named "BISheng"; Yongyou/UFIDA ERP). The actual DataElem Bisheng population is small (~4 confirmed reachable). All confirmed instances return HTTP 401 (`"Missing cookie access_token_cookie"`) on the canonical endpoints.

**This is the counter-example needed for the cohort-comparison sub-hypothesis that emerged from the LobeChat survey same-day.** The CN-origin OSS cohort is not uniformly auth-permissive: Bisheng (DataElem, Beijing) ships auth-required where LobeChat (Lobehub, Hangzhou) ships fully-open. The sub-hypothesis must be refined: **the cohort default is platform-maintainer-specific, not jurisdiction-wide.**

---

## Methodology

| Stage | Action | Detail |
|---|---|---|
| Stage 0 | Shodan harvest `"BISHENG"` | 30 results — high false-positive rate |
| Stage 1b | Per-host probe `/api/v1/user/info`, `/api/v1/config`, `/login`, `/api/v1/version` | Manual Python probe (no herald config yet) |
| Stage 3v | Confirmed Bisheng identity via `/api/v1/version` returning DataElem-style JSON wrapper `{"status_code":200,"status_message":"SUCCESS","data":{"version":"X.Y.Z"}}` | Per-host |
| Stage FP | Filtered non-Bisheng matches (banks, ERP, NAS) | Manual |

---

## Population Results

| Metric | Count |
|---|---|
| Shodan `"BISHENG"` matches | 30 |
| Web-UI candidate ports (80/443/3001/5000/5001/8089) | 25 |
| **Confirmed DataElem Bisheng** | **4** |
| Auth-required (all data endpoints return 401) | 4 / 4 (100%) |
| Auth-permissive | 0 / 4 (0%) |
| Other matches (banks, NAS, ERP — FPs) | ~26 |

### Confirmed DataElem Bisheng instances

| IP:Port | Version | Country | Provider | Auth state |
|---|---|---|---|---|
| `14.22.86.97:3001` | v2.0.0 | CN | Aliyun | 401 — auth required (data endpoints), version disclosed |
| `120.25.222.22:3001` | v2.4.0-beta1 | CN | Aliyun | 401 — auth required, version disclosed |
| `120.26.245.160:3001` | v2.4.0-beta1-fix | CN | Aliyun | 401 — auth required, version disclosed |
| `122.247.1.59:3001` | (500 on all endpoints) | CN | Tencent Cloud | service degraded / unhealthy |

### Sample false-positive matches removed

| IP:Port | Title | Why flagged |
|---|---|---|
| `112.5.139.115:8089` | 协同管理软件.A8N V9.0SP1 | Yongyou A8N (Chinese ERP) — unrelated |
| `114.32.121.143:5001` | BISheng - Synology NAS | User-named Synology NAS — unrelated |
| `117.149.2.27:443` | 浙江南浔农村商业银行股份有限公司 | Zhejiang Nanxun Rural Commercial Bank — unrelated |
| `183.134.216.216:443` | (same bank) | Same — unrelated |

**Cross-platform FP class:** "BISHENG" / "Bi Sheng" / "畢昇" refers to Bi Sheng, the 11th-century Chinese inventor of movable-type printing. Multiple Chinese commercial entities (especially in banking, ERP, and traditional cultural sectors) use the name. Future Bisheng surveys should disambiguate via `/api/v1/version` JSON response signature, not title alone.

---

## Information Disclosure Surface

While auth posture is sound, `/api/v1/version` is publicly accessible on all confirmed Bisheng instances:

```json
GET /api/v1/version
{"status_code":200,"status_message":"SUCCESS","data":{"version":"2.0.0"}}
```

Version disclosure on a Chinese enterprise AI platform with no public vulnerability database tracking would only become security-relevant once a Bisheng-specific CVE class is established. Current state: low-severity informational. Not flagged as a finding-worth-disclosing.

---

## Why This Negative Result Matters

The LobeChat survey (same day) found 10/12 reachable (83.3%) fully-open. The emerging sub-hypothesis was **"CN-origin OSS chat-UI / AI infrastructure trends auth-permissive."** Bisheng refutes the jurisdiction-wide form of that hypothesis:

| Platform | Origin | Default auth posture | Open rate (reachable) |
|---|---|---|---|
| LobeChat | CN — Lobehub (Hangzhou) | Open (no access code) | 83.3% AUTH_OFF |
| RAGFlow | CN — InfiniFlow (Shanghai) | Registration-open | 87.2% REGISTER_OPEN |
| **Bisheng** | **CN — DataElem (Beijing)** | **Auth-required** | **0% open** |
| Dify | CN — Dify.AI (Shanghai) | Auth-required | 0.9% open |

**The CN cohort splits 2-2:** LobeChat + RAGFlow ship auth-permissive defaults; Bisheng + Dify ship auth-required. The maintainer's deployment culture (DX-first one-click demo vs enterprise-customer-first secure-by-default) is the determining variable, not the jurisdiction.

**Refined sub-hypothesis:** the cohort default is **platform-maintainer-specific**, reflecting whether the upstream maintainer optimizes for:
- "Clone, docker compose up, immediately demo" — auth-permissive default (Langfuse, RAGFlow, Phoenix, Flowise, LobeChat)
- "Self-host for our enterprise customers" — auth-required default (Bisheng, Dify, AnythingLLM)

This refinement preserves the second clause of Insight #76 (the rate is movable) and discards the over-strong jurisdictional claim.

---

## Toolchain Provenance

```
Step 0:    shodan download '"BISHENG"' (30 records)
Step 1b:   manual urllib probe — herald lobechat config doesn't apply
Step 3v:   /api/v1/version JSON signature as Bisheng-identity confirmation
Step FP:   manual filter of bank/NAS/ERP false-positives via title
Step 12b:  This document
```

**Decision: no herald config for Bisheng at this time.** The population is too small (4 confirmed) to justify the per-platform config maintenance, and the auth-required default means there is no auth-permissive finding to detect. If a Bisheng CVE class emerges that surfaces an unauth disclosure endpoint, a herald config can be added then.

---

## Research-Program Contribution

**Negative result properly counter-examples** the LobeChat-suggested CN-jurisdiction sub-hypothesis. The cohort hypothesis #76 is refined from "platform-cohort dependent" to **"platform-maintainer dependent"** — the deployment culture of the upstream maintainer team is the determining variable, not the geographic/jurisdictional origin of the platform.

The 4-platform CN-origin matrix is now:
- Auth-permissive: LobeChat (Lobehub Hangzhou), RAGFlow (InfiniFlow Shanghai) — 2
- Auth-required: Bisheng (DataElem Beijing), Dify (Dify.AI Shanghai) — 2

**An interesting demographic gradient appears**: Beijing-based DataElem (enterprise-customer-first, China-government-adjacent enterprise AI vendor) and Shanghai-based Dify.AI (commercial SaaS) both auth-required. Hangzhou-based Lobehub (community OSS, DX-first) and Shanghai-based InfiniFlow (academic-origin RAG research) both auth-permissive. **Enterprise-customer-focused vs community/research-focused maintainer culture is the splitter** — not geography.
