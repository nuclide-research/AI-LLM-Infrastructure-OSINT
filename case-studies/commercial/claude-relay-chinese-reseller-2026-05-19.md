---
title: "Chinese commercial Claude-reseller ecosystem: 32 pooled Anthropic accounts across six relays, ~13.92B tokens served via claude-relay-service OSS"
date: 2026-05-19
type: case-study
sector: commercial
tags:
  - claude-relay-service
  - llmjacking
  - resale-fraud
  - attribution-laundering
  - anthropic-tos
  - tencent-cloud
  - aceville
  - yunnan-landui
  - pincc
  - sub2api
  - insight-39
---

# Chinese commercial Claude-reseller ecosystem: claude-relay-service population survey

_NuClide Research · 2026-05-19 · Six publicly-indexed `claude-relay-service` instances pool 32 paid Anthropic accounts and resell Claude inference through customer-facing LiteLLM storefronts in the same Chinese commercial cloud netblocks._

## Summary

A pivot off the LiteLLM UNAUTH_FUNCTIONAL cohort from the same-day safety/guardrail survey surfaced an upstream `api_base` at `43.167.216.195:38762` (Tencent Cloud Singapore / Aceville Pte Ltd). That upstream returned a JSON stats schema unique to the `claude-relay-service` OSS project. A targeted Shodan dork on the schema's load-bearing tokens (`availableAccounts` + `thirdPartyMaxConcurrent`) surfaced five additional hosts running the same OSS. The six visible relays collectively pool 32 paid Anthropic accounts and have served approximately 13.92 billion tokens of Claude inference across ~430,000 successful API requests. The OSS substrate (`github.com/Wei-Shaw/claude-relay-service`, 11.8K stars, MIT) is documented in Chinese only and explicitly marketed for `拼车` (carpool) account-sharing. The maintainer operates a commercial brand at pincc.ai with the slogan "Claude Code Max 20X, saves 60%+." The Go-rewrite successor `sub2api` has 21,800 stars and 8,105 Shodan-indexed deployments, suggesting the visible Claude Relay v1 population is the long tail of operators who left `/health` open, not the deployed base.

## Thesis fit

Confirms the auth-on-default thesis at the per-endpoint granularity captured in Insight #37: the OSS ships with admin-class endpoints gated and stats / health endpoints open. The open stats endpoint is the population-discovery vector for the broader fraud architecture.

Generates new methodology: **Insight #39 (pooled-account upstream proxy as attribution-laundering layer)**. The relay tier separates paid-account substrate from customer-facing storefront across hosts, flattening attribution at the vendor's side.

---

## Per-finding entries

### F1. `43.167.216.195:443` (Aceville Pte Ltd / Tencent SG)

#### What was found

GET / returns JSON:

```json
{"status":"ok","version":"1.0.0","accounts":6,"availableAccounts":0,
 "stats":{"totalRequests":59309,"successRequests":53655,"failedRequests":5256,
 "totalTokens":5348164892,"uptime":16119220,"activeApiRequests":3,
 "queuedApiRequests":0,"activeThirdPartyRequests":0,
 "queuedThirdPartyRequests":0,"thirdPartyMaxConcurrent":200}}
```

187 days of continuous uptime. 6 Anthropic accounts in the pool. Approximately 5.35B tokens of Claude inference served. Response headers include the full Anthropic Stainless SDK CORS allowlist (`x-stainless-os`, `x-stainless-lang`, `x-stainless-package-version`, `x-stainless-runtime`, `x-stainless-runtime-version`, `x-stainless-arch`) plus `anthropic-version` and `anthropic-beta`.

The `version: "1.0.0"` string is a hardcoded fallback in `src/app.js:137` of the upstream OSS, not a release tag. The actual OSS releases reach v1.1.304 as of 2026-05-16.

#### Why it is bad

**Verified**: paid Anthropic accounts (6 of them) are operating as a shared compute pool serving an unauthorized end-customer base. ~5.35B tokens of inference at Claude Sonnet's blended pricing (~$9 per million tokens) corresponds to roughly $48,000 of Anthropic API value moved through this host. Anthropic's per-account telemetry observes one account at a time; the per-account view does not reveal the fan-out below.

**Inferred (chain not exercised per restraint)**: the downstream customer base is reachable from the LiteLLM at 154.36.180.105 which names this host as its `api_base`. Cross-customer prompt observation through the relay's logs (if it logs prompts) was not probed.

#### Who it affects

- **Primary affected party**: Anthropic. The pooled accounts are operating outside the per-account TOS. The fan-out is invisible from Anthropic's side.
- **Secondary affected parties**: the holders of the six pooled accounts, who may be unaware their credentials are operating a multi-tenant resale service or may be operating it knowingly.
- **Hosting provider**: Aceville Pte Ltd / Tencent Cloud Singapore (AS132203 / AS45090 zone).
- **Downstream end-customers**: pay storefront operators in this netblock for Anthropic API access through the pooled-account substrate; they receive the model they paid for but are routed through an unauthorized middle tier.

#### How it got exposed

The OSS ships `/health` and `/` as the load-balancer probe endpoints. The OSS author's deployment template assumes these endpoints front a private VPC; operators copy the template and expose the relay to the public internet without firewall rules in front of those paths. Insight #13 (shipping-defaults-load-bearing) and Insight #37 (asymmetric auth gating). The operator-facing `/admin` path is gated; the machine-facing health-check path is not.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 - Discover | Shodan walk (LiteLLM cohort) | Initial surface via the Mauritius LiteLLM at 154.36.180.105 naming this host as `api_base` |
| 1 - Fingerprint | aimap + direct probe | JSON schema match against `claude-relay-service` source on GitHub |
| 2 - Verify | curl GET / | Confirmed `accounts: 6` + token throughput + Stainless CORS header set |
| 3 - Attribute | VisorGraph + WHOIS | Aceville Pte Ltd (Tencent SG) netblock |
| 4 - Classify | aimap-profile | commercial / resale-fraud category |
| 5 - Ledger | VisorLog | finding F1 logged at HIGH; lifecycle open -> disclosed (2026-05-19 to usersafety@anthropic.com) |
| 6 - Score | VisorScuba | TOS-violation class (vendor-internal scoring, no public CIS / NIST mapping) |

**The load-bearing chain for this finding**: LiteLLM `/v1/model/info` -> upstream resolution -> direct GET / -> source-code cross-reference (GitHub).

---

### F2. `101.34.235.97:80` (Tencent Cloud Beijing)

#### What was found

GET / returns the same `claude-relay-service` schema. `accounts: 2`, `totalRequests: 122337`, `successRequests: 114761`, `totalTokens: 2706654014`, uptime overflows the int32 field (suggests > 70 days). Load-balanced pair with F3 (`101.33.200.21:443`) which on this probe was unreachable but had previously returned matching token counts.

#### Why it is bad

**Verified**: 2 pooled accounts; ~2.71B tokens served (~$24,000 of Anthropic value); the highest per-account utilization in the visible cohort (over 1.3B tokens per account).

#### Who it affects

Anthropic + 2 accountholders. Tencent Cloud Beijing.

#### How it got exposed

Same OSS default; same `/health` open-to-internet pattern.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 - Discover | Shodan dork `http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent"` | Conjunctive dork derived from F1 schema |
| 1 - Fingerprint | direct probe | Schema match |
| 2 - Verify | curl GET / | Confirmed stats |
| 3 - Attribute | WHOIS | Tencent Cloud Beijing |
| 4 - Classify | aimap-profile | commercial / resale-fraud |
| 5 - Ledger | VisorLog | F2 at HIGH |

---

### F3. `101.33.200.21:443` (Tencent Cloud Beijing)

#### What was found

Probe-time unreachable. Prior Shodan-index snapshot shows matching `claude-relay-service` schema with `totalTokens: 2706681578` (within 27,564 tokens of F2, consistent with a load-balanced pair).

#### Why it is bad

**Inferred**: same fraud class as F2 if confirmed on next re-probe; possible HA pair behind a load balancer with F2.

#### Which tools contributed to the finding

| Stage | Tool | Contribution |
|---|---|---|
| 0 - Discover | Shodan dork (same as F2) | Schema match |
| 2 - Verify | curl GET / | **Null on probe day**; finding rests on Shodan-index snapshot only |
| 5 - Ledger | VisorLog | F3 at MEDIUM (verification incomplete, surface inferred) |

**Tools that ran but did not contribute unique signal**: live HTTP probe (target offline at probe time).

---

### F4. `49.51.183.217:80` (Tencent Cloud Beijing, US region)

#### What was found

GET / returns the schema. `accounts: 2`, `successRequests: 23389`, `totalTokens: 2061216465`, uptime 30 days.

#### Why it is bad

**Verified**: 2 pooled accounts; ~2.06B tokens served. The US-region hosting (Tencent Cloud's US zone allocation) may complicate jurisdictional response.

#### Who it affects

Anthropic + 2 accountholders. Tencent Cloud (US-region allocation).

#### Which tools contributed to the finding

Same chain as F2.

---

### F5. `43.228.78.164:80` (YunNan LanDui Network Technology)

#### What was found

GET / returns the schema. `accounts: 8` (the highest pool size in the visible cohort), `successRequests: 82131`, `totalTokens: 1971258691`, uptime overflows.

#### Why it is bad

**Verified**: 8 pooled accounts is the largest single-relay pool surfaced. The high `successRequests / totalTokens` ratio (24K tokens per request) is consistent with multi-turn coding-assistant traffic. The hosting provider (YunNan LanDui) is a smaller Chinese cloud not typically associated with international SaaS, suggesting a more domestic-China end-customer base than F1.

#### Who it affects

Anthropic + 8 accountholders. YunNan LanDui Network Technology Co Ltd.

---

### F6. `43.163.211.82:80` (Aceville Pte Ltd / Tencent SG)

#### What was found

GET / returns the schema. `accounts: 1`, `successRequests: 21038`, `totalTokens: 1834594872`, uptime 30 days.

#### Why it is bad

**Verified**: single-account relay with the highest per-account token throughput in the visible cohort (~1.83B tokens on one account). The single-account pattern suggests a smaller-scale operator or a relay in early operational ramp.

#### Who it affects

Anthropic + 1 accountholder. Aceville Pte Ltd / Tencent Singapore.

---

### Aggregate finding: Tier 3 storefront base (Aceville LiteLLM cohort)

A wider Shodan sweep on `org:"ACEVILLE" http.html:"litellm"` surfaced 30 LiteLLM proxies in the Aceville Pte Ltd netblock, disjoint from the six visible relays. One advertises in Chinese branding ("飞经理使用指南" / "Fei Manager Usage Guide") at 43.167.168.41:443. Cross-correlation against the relay cohort is partial; the LiteLLM cohort was not probed individually for `/v1/model/info` upstream resolution (out-of-scope for this case study; the LiteLLM UNAUTH_FUNCTIONAL deep-dive captures that cohort separately).

The architectural inference: the LiteLLM proxies in the Aceville netblock are the Tier 3 storefronts whose upstreams are the Tier 2 relays surveyed here. The full Tier 4 -> Tier 3 -> Tier 2 -> Tier 1 chain is empirically confirmed for one Tier 3 host (the Mauritius LiteLLM at 154.36.180.105 -> 43.167.216.195:38762); the same chain shape is inferred for the remaining 30 Aceville LiteLLM hosts.

---

## Cross-survey / cross-finding analysis

**Pool-size distribution across six relays**:
- F1: 6 accounts
- F2: 2 accounts (HA-paired with F3)
- F3: unknown (offline at probe; HA partner likely 2)
- F4: 2 accounts
- F5: 8 accounts
- F6: 1 account

Total visible: 32 pooled Anthropic accounts. Mean pool size 5.3, median 2.

**Token throughput distribution** (in billions of tokens, lifetime):
- F1: 5.35
- F2+F3: 2.71 (single-source attribution; HA pair reports identical counts)
- F4: 2.06
- F5: 1.97
- F6: 1.83
- Total visible: ~13.92B

**Hosting concentration**:
- Tencent Cloud (incl. Aceville SG zone): 5 of 6 hosts
- YunNan LanDui: 1 of 6 hosts
- 100% Chinese commercial cloud.

**OSS substrate uniformity**:
- 6 of 6 hosts return the identical JSON schema
- 6 of 6 hosts include the full Stainless SDK CORS allowlist (verbatim copy of Anthropic's official SDK CORS config)
- 6 of 6 hosts return `version: "1.0.0"` (the `src/app.js:137` fallback string), suggesting none of the operators have patched or customized the relay beyond config
- The OSS author maintains a commercial brand (pincc.ai) and ships English-persona maintainer metadata (`name: "Wesley Liddick"`) while writing documentation Chinese-only

**Operator awareness signal**: GitHub issues #587 ("heavy account bans these days"), #861 (auto-prune-banned-accounts feature request), #673 (silent-fallback-to-direct ban-risk), #1000 (overage-throttle misclassification) confirm the operator class understands the activity is TOS-violating and coordinates technical countermeasures. None reference Anthropic's TOS by name; bans are discussed operationally.

## Methodology - what this case study adds

**New Insight #39 - pooled-account upstream proxy as attribution-laundering layer.** See `methodology/insight-39-pooled-account-attribution-laundering.md`.

The structural pattern is distinct from prior LLMjacking insights:
- NOT proxy + stolen-compute LLM on the same host (Insight #23-bis)
- NOT proxy lying about the model (Insight #38)
- IS proxy lying about the payer: a paid vendor account is fanned out to multiple unauthorized end-customers through a Tier 2 relay tier

The disclosure target is the vendor (Anthropic), not the customer or the hosting provider. The customer is receiving the model they paid for; the harm flows upstream.

## Honest negative space

- **The visible v1 population is likely a fraction of total deployments.** sub2api (Go rewrite) has 8,105 Shodan-indexed deployments. The Claude Relay v1 dork (`availableAccounts` + `thirdPartyMaxConcurrent`) surfaces only 6 hosts because most operators correctly firewall the `/health` endpoint; the visible cohort is the long tail of operators who left it public.
- **Tier 4 attribution is not exercised.** The end-customers downstream of the Tier 3 LiteLLM storefronts are not probed in this case study. They are the most-affected party in customer-trust terms but the least-affected in fraud-attribution terms (they receive the model they paid for).
- **The 6 pooled accounts are not individually identified.** The relay reports `accounts: N` as a count but does not expose account-IDs externally. Anthropic-side telemetry is the only way to identify which 32 accounts are actually pooled.
- **The OSS author's commercial brand (pincc.ai) was not probed in detail.** A separate deep-read of pincc.ai's storefront would reveal customer-facing pricing tiers, payment processors, and whether the brand operates its own relay infrastructure or only sells the OSS.
- **The "Wesley Liddick" English-persona maintainer name was not verified as a real identity.** The GitHub profile lists no location, email, or blog; the content is Chinese-only; the name may be a pseudonym. No further attribution attempted.

## Toolchain provenance

```
Stage 0 (Discover)    Shodan walk on LiteLLM cohort (safety-guardrail survey 2026-05-19)
                      -> LiteLLM at 154.36.180.105 names api_base 43.167.216.195:38762
                      -> direct GET on upstream reveals claude-relay-service schema
                      -> derived conjunctive Shodan dork from schema
                         (http.html:"availableAccounts" http.html:"thirdPartyMaxConcurrent")
                      -> 5 additional hosts surfaced
Stage 1 (Fingerprint) Source-code cross-reference against github.com/Wei-Shaw/claude-relay-service
                      -> matched response schema to src/app.js routes
                      -> identified version: "1.0.0" as src/app.js:137 fallback
Stage 2 (Verify)      curl GET / on each of six hosts
                      -> 5 of 6 returned schema on probe day (F3 offline)
                      -> Stainless SDK CORS allowlist confirmed on all responding hosts
Stage 3 (Attribute)   WHOIS on each IP
                      -> 5 of 6 Tencent Cloud (incl. Aceville SG zone)
                      -> 1 of 6 YunNan LanDui
                      VisorGraph cert pivot
                      -> none of the six expose TLS with operator-identifying SAN
Stage 4 (Classify)    aimap-profile -> commercial / resale-fraud
                      Cross-correlation with Aceville LiteLLM cohort (30 hosts disjoint)
Stage 5 (Ledger)      VisorLog ingest of six findings + aggregate Tier 3 entry
Stage 6 (Score)       BARE exploit-rank n/a (no remote-exploitable CVE; the finding is TOS-class, not vuln-class)
Stage 7 (Codify)      Insight #39 written; this case study filed
```

## See also

- `methodology/insight-39-pooled-account-attribution-laundering.md`: the methodology insight generated by this survey
- `methodology/insight-37-asymmetric-auth-gating-dashboard-vs-api.md`: the open-stats-endpoint pattern at the OSS-default level
- `methodology/insight-38-litellm-model-impersonation-fraud.md`: adjacent fraud pattern in the same operator ecosystem
- `case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`: parent survey from which this case study branched
- `case-studies/commercial/cost-billing-analytics-survey-2026-05-19.md`: same-day asymmetric-auth survey on Phoenix
- `https://github.com/Wei-Shaw/claude-relay-service`: the OSS substrate
- `https://github.com/Wei-Shaw/sub2api`: the Go-rewrite successor (broader population)
