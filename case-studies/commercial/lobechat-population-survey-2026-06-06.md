---
type: case-study
category: cat-lh
platform: LobeChat
date: 2026-06-06
findings: 10 AUTH_OFF / 12 reachable (83.3%); 636 indexed
status: verified
toolchain: herald v0.1.3
---

# LobeChat Population Survey — 10/12 Fully Open (83.3%, small population)

_NuClide Research · 2026-06-06_

---

## Executive Summary

LobeChat (`github.com/lobehub/lobe-chat`) is an open-source ChatGPT-alternative chat interface from Lobehub, a China-origin OSS community. Direct functional parallel to LibreChat. 641 Shodan-indexed; 636 downloaded; **only 12 of 636 (1.9%) responded to live HTTP probing**. Of the 12 reachable: **10 are in fully-open mode (`enabledAccessCode: false` AND `enabledOAuthSSO: false`)**, 2 are ACCESS_CODE_GATED, 1 of the open instances also has OAuth SSO available alongside no-access-code.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7070, S7075, T5858, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, S7067, T5854, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935, K7003, K7048

<!-- ksat-tag:auto-generated:end -->

The 1.9% reachability rate is the lowest observed in any 2026-06-06 survey. Most indexed LobeChat hosts are either stale (Shodan cache aging out), behind reverse proxies that intercept the SSR HTML, or deployed on extremely transient infrastructure. The small reachable subset is correspondingly less statistically robust than the same-day LibreChat / Langfuse / RAGFlow surveys.

**Among the reachable subset, the 83.3% AUTH_OFF rate matches the auth-permissive-default cohort norm.** The LibreChat counter-example (v0.8.x correcting to 10.3%) does not appear to extend to LobeChat — though the small N means this is best read as suggestive rather than confirmed.

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `http.title:"LobeChat"` | shodan CLI (636 records) |
| Stage 0c | HTTP liveness via root GET | herald |
| Stage 1b | Auth state via SSR HTML body markers | herald lobechat platform config |
| Stage 3v | Source verification: `enabledAccessCode` and `enabledOAuthSSO` are LobeChat client config fields embedded in Next.js SSR streams (`self.__next_f.push`) | manual review of LobeChat source |

**Probe semantics calibration**: LobeChat's server-side rendered HTML embeds the client config as JSON-escaped strings inside Next.js streams. The exact markers used:

- `\"enabledAccessCode\":false` → no access-code prompt: anyone can use the chat
- `\"enabledAccessCode\":true` → access-code prompt on first visit: gated
- `\"enabledOAuthSSO\":true` → OAuth SSO available

**Auth modes** (from LobeChat source):
- Both false → fully open, no auth at all
- `enabledAccessCode: true` → simple shared-password gate
- `enabledOAuthSSO: true` → full identity provider flow (Auth0, Casdoor, Logto, etc.)

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 641 | — |
| Downloaded | 636 | — |
| Reachable | 12 | 1.9% of indexed |
| AUTH_OFF (fully open, no access code) | 10 | 83.3% of reachable |
| ACCESS_CODE_GATED | 2 | 16.7% of reachable |
| OAUTH_SSO_ENABLED | 1 | (one of the AUTH_OFF hosts also has OAuth) |

---

## AUTH_OFF Hosts (full list — small N)

| IP:Port | Country | Provider |
|---|---|---|
| `129.146.5.44:8036` | United States | Oracle Cloud |
| `111.231.14.199:32101` | China | Tencent Cloud |
| `101.37.145.198:30002` | China | Alibaba Cloud |
| `139.129.111.70:3020` | China | Alibaba Cloud |
| `140.245.51.103:8036` | Singapore | Oracle Cloud |
| `156.229.163.187:8036` | United States | Akile LTD |
| `152.70.238.77:8036` | Korea | Oracle Cloud |
| `192.3.131.11:80` | United States | RackNerd LLC |
| `47.239.236.83:3000` | Hong Kong | Alibaba Cloud |
| `8.154.30.249:18006` | China | Alibaba Cloud |

**Notable pattern**: 4 of 10 AUTH_OFF hosts are on Oracle Cloud port `8036` across 3 regions (USA, Singapore, Korea). This consistent port + provider combination suggests a Lobehub deployment template — possibly the one-click deploy guide that defaults to no access code for ease-of-demo.

---

## Geographic split

| Country | AUTH_OFF |
|---|---|
| China + Hong Kong + Singapore + Korea | 6 (60%) |
| United States | 3 (30%) |
| Singapore | 1 (10%) |

The reachable + AUTH_OFF population is **60% APAC-concentrated**, consistent with LobeChat's China-origin OSS community. This is the inverse of LibreChat's geographic distribution (US-dominant, 34% US).

---

## Comparison with LibreChat (same-day, same-category)

| Dimension | LibreChat | LobeChat |
|---|---|---|
| Shodan indexed | 3,153 | 641 |
| Reachable | 1,565 (78.3%) | 12 (1.9%) |
| Open rate (of reachable) | 26.3% REG_OPEN | 83.3% AUTH_OFF |
| Within-platform correction | v0.8.x = 10.3% (corrected) | Not detected at this sample size |
| Geographic dominance | US (34%) | China/APAC (60%) |
| Origin community | US-led OSS (danny-avila) | China-led OSS (Lobehub) |

The two platforms are **direct functional substitutes** for self-hosted ChatGPT-alternative deployment. They diverge sharply on auth-default trajectory:
- LibreChat: explicitly tightened in tagged releases (v0.8.x = 10.3% — Open-WebUI-equivalent)
- LobeChat: among reachable population, the cohort-default auth-permissive rate (83.3%) persists

**Caveat for cohort comparison**: the LobeChat reachable N=12 is too small to conclude the absence of correction. The hypothesis space remains: (a) LobeChat ships auth-permissive default still, (b) operators of LobeChat skew toward demo / public-facing deployment intent, (c) reverse proxies in Chinese cloud regions intercept the SSR HTML and Shodan cached the proxy not the LobeChat backend.

The cleanest test of the cohort hypothesis would require either:
- A larger LobeChat reachable population (different dorks; Censys cross-reference)
- A direct source-code review of LobeChat's current default `ACCESS_CODE` env var behavior

---

## LLM10 surface

LobeChat's AUTH_OFF mode means **anyone visiting the URL invokes completions against whatever LLM providers the operator has configured**. The provider list is embedded in the SSR HTML as `languageModel: {provider: {enabled: bool}}` — enumerable per host with no auth.

LobeChat supports broad provider coverage including:
- OpenAI, Anthropic, Azure, Google, AWS Bedrock (Western frontier)
- DeepSeek, Moonshot, Qwen, MiniMax, Zhipu/GLM, Baichuan, Spark/Wenxin/Tongyi (Chinese frontier)
- Ollama, custom OpenAI-compatible (self-hosted)

A single fully-open LobeChat instance with SERVER-side configured API keys for any of the above is a direct LLM10 Denial-of-Wallet target. Among the 10 AUTH_OFF hosts surveyed, provider enumeration was not exhaustively performed at this sample (provider-name regex requires JSON-escape-aware match; deferred to next round).

---

## Toolchain Provenance

```
Step 0:    shodan download 'http.title:"LobeChat"' (636 records)
Step 0c:   IP extraction → ip-port.txt (636 unique)
Step 1b:   herald -platform lobechat < ip-port.txt
           - probe id fully_open: / body_contains '\"enabledAccessCode\":false'
           - probe id access_code_set: / body_contains '\"enabledAccessCode\":true'
           - probe id oauth_sso: / body_contains '\"enabledOAuthSSO\":true'
Step 3v:   Probe semantics verified against LobeChat source (Next.js SSR
           __next_f stream embedding `enabledAccessCode` and `enabledOAuthSSO`
           in client config)
Step 12b:  This document
```

**Tool note (herald v0.1.3):** the LobeChat config exposed a `body_contains` matching issue around JSON-escaped quote sequences. Initial probe used literal `"enabledAccessCode":false` and matched zero hosts. The actual SSR HTML contains the JSON-escaped form `\"enabledAccessCode\":false` (the page is a JSON-stringified Next.js stream rendered inside HTML script tags). Updated to escaped form; sweep then succeeded. **This is a generalizable lesson: Next.js / Remix / SSR-streamed framework HTML embeds config data as JSON-stringified strings with escaped quotes. body_contains probes against SPAs need to account for the escape level.**

---

## Research-Program Contribution

LobeChat fills the **Chinese-origin OSS chat-UI cohort slot** in the 2026-06-06 survey corpus. Same category as LibreChat (US-origin OSS); same functional class; different origin community.

The 83.3% AUTH_OFF rate (small N caveat) is **directionally consistent with the uncorrected-cohort norm** of Insight #76. Combined with LibreChat's clear within-platform correction in v0.8.x, the dataset begins to support a sub-hypothesis: **Western OSS chat-UI maintainers have begun correcting; Chinese OSS chat-UI maintainers may not yet have**.

This is testable against further Chinese-origin OSS AI/LLM platforms surveyed under similar conditions. Bisheng (DataElem), FastGPT (Sealos), and Open Interpreter all candidates for the next-round comparison.

The herald `body_contains` escape-level limitation surfaced during this survey is documented as a known issue and warrants a v0.2 enhancement: optional regex or fuzzy-match mode for SPA-embedded JSON.
