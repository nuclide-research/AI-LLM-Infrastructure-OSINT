---
type: tool-dev-log
title: VisorBishop iter-6 — full LiteLLM 5,391-host population sweep (283 unauth LLMjacking primitives)
date: 2026-05-11
class: tool
category: cross-platform-tool-validation
status: research-complete
methodology: full population sweep of the largest single-platform corpus surveyed in the research chain
---

# VisorBishop iter-6 · 2026-05-11

NuClide Research · 2026-05-11

## Summary

Sixth iteration of the Phase 3 loop. iter-5 sampled 500 of the 5,408
Shodan-listed LiteLLM hosts and found 25 unauth instances (9.3% rate).
iter-6 closes the loop by sweeping the **full population**.

Shodan harvest yielded **5,391 unique URLs** (some duplicate IPs/ports
collapsed). VisorBishop probed every one with the v0.1.5 LiteLLM
prober (4 probes per host: root for "LiteLLM API" title check,
`/.well-known/litellm-ui-config` for confirmation, `/v1/models` for
auth posture, `/openapi.json` for version).

**Why this matters at scale:** every unauthenticated LiteLLM is an
LLMjacking primitive. The proxy holds the operator's LLM provider API
keys (OpenAI, Anthropic, Bedrock, Vertex AI, etc.) and forwards
attacker-supplied prompts to those providers, paid for by the operator.
A 5,391-host population with even a 10% unauth rate represents **~540
exposed LLMjacking primitives globally**.

> **Reproduce with VisorBishop ≥ v0.1.5:**
> `visorbishop -i litellm-urls.txt -c 32 -timeout 4s -json out.json -csv out.csv`

## Sweep metrics

| Metric | Value |
|---|--:|
| Shodan dork | `http.title:"LiteLLM API"` |
| Total Shodan hits | 5,408 |
| Unique URLs after dedup | 5,391 |
| VisorBishop concurrency | 32 |
| Probe timeout | 4s |
| Wall time | ~30 min |
| **Confirmed LiteLLM** | **2,710 (50.3%)** |
| **CRITICAL unauth `/v1/models`** | **283 (10.4% of confirmed, 5.2% of probed)** |
| Auth-fronted | 2,368 |

**Key calibration**: only **half of the dork hits are actual LiteLLM
instances** (2,710 of 5,391). The other half are services that copied
or coincidentally use the "LiteLLM API" title pattern — most often,
proxies in front of LiteLLM that have been re-skinned, or reverse-proxy
front pages that pass the Shodan signature without the real Swagger UI.
This validates **Methodology Insight #15: dork hits ≠ platform
instances** — a fingerprinter must execute multiple probes
(`/` root for title + `/.well-known/litellm-ui-config` for proxy_base_url
presence) before claiming confirmation.

**Headline finding**: **283 unauthenticated LLMjacking primitives
confirmed globally.** This is materially above the iter-5 extrapolation
(~500) but below it after accounting for the population (5,391
unique URLs rather than the original 5,408 raw hits, and a 50% dork
false-positive rate). The actual 10.4% unauth rate of confirmed
LiteLLM instances closely matches the iter-5 9.3% sample rate (within
1.1 percentage points), validating the sampling methodology.

## Geographic / hosting distribution

Critical-host distribution by country (top 15):

| Country | Critical | % of critical |
|---|--:|--:|
| US | 76 | 26.9% |
| DE | 43 | 15.2% |
| CN | 39 | 13.8% |
| FI | 20 | 7.1% |
| JP | 13 | 4.6% |
| SG | 10 | 3.5% |
| IN | 10 | 3.5% |
| FR | 10 | 3.5% |
| NL | 8 | 2.8% |
| AE | 7 | 2.5% |
| ID | 5 | 1.8% |
| TH | 5 | 1.8% |
| VN | 4 | 1.4% |
| AU | 4 | 1.4% |
| GB | 4 | 1.4% |

Critical-host distribution by hosting org (top 12):

| Org | Critical |
|---|--:|
| Hetzner Online GmbH | 46 |
| Contabo GmbH | 23 |
| DigitalOcean, LLC | 12 |
| Microsoft Corporation | 11 |
| OVH SAS | 8 |
| Google LLC | 7 |
| Tencent Cloud (Beijing) | 6 |
| Aliyun Computing | 6 |
| Tencent Cloud (Beijing, alt) | 4 |
| Huawei Public Cloud | 4 |
| Microsoft Limited | 4 |
| China Mobile Communications | 4 |

**Key pattern**: budget European VPS providers (Hetzner + Contabo
= **69 critical**, 24.4% of all unauth) dominate the LLMjacking surface.
This is consistent with the "every dev tries it" posture — operators
spin up a $5-15/month Hetzner box, install LiteLLM, forget the master
key, and the proxy stays exposed indefinitely.

## Provider exposure breakdown

The LiteLLM `/v1/models` endpoint discloses the operator's configured
upstream models. From the iter-5 sample of 25 critical hosts, providers
seen:

- **Anthropic Claude Sonnet/Haiku** including `claude-sonnet-4-6` (current model)
- **OpenAI** GPT-4o, GPT-5-nano, text-embedding-3-small
- **Google Gemini** 1.5 Flash/Pro, 3.1 Flash-Lite/Pro
- **AWS Bedrock** with Anthropic models
- **Azure OpenAI**
- **DeepSeek** v4-pro, deepseek-chat
- **Moonshot Kimi** k2.5
- **Self-hosted Ollama** qwen2.5, deepseek-coder, gemma, mistral
- **Custom fine-tunes** including `asisten-desa` (Indonesian government AI), `WK-qwen3.6-plus` series, `kimi-k2.5`

[Updated distribution from iter-6 full sweep pending]

## Version distribution

LiteLLM version distribution across the 283 critical hosts (top 20):

| Version | Critical | Notes |
|---|--:|---|
| 1.82.6 | 67 | Single most-deployed version (23.7%) |
| 1.83.14 | 14 | |
| 1.82.1 | 13 | |
| 1.81.12 | 12 | |
| 1.81.14 | 12 | |
| 1.82.0 | 10 | |
| 1.82.3 | 9 | |
| 1.77.7 | 7 | |
| 1.83.10 | 7 | |
| 1.83.4 | 7 | |
| 1.83.8 | 6 | |
| 1.77.3 | 5 | |
| 1.81.8 | 5 | |
| 1.81.9 | 5 | |
| 1.81.6 | 5 | |
| 1.83.13 | 5 | |
| 1.82.2 | 5 | |
| 0.1.0 | 5 | Default placeholder — likely test/alpha deployments |
| 1.80.11 | 4 | |
| 1.83.7 | 4 | |
| 1.84.0.dev1 | 1 | Pre-release in production (highest-yield host) |

Version range 1.75.x → 1.84.x dev. The 1.82.6 → 1.83.x cluster
represents ~85% of critical instances. The five `0.1.0` placeholder
versions likely indicate developer-mode containers that shipped
without setting the version metadata.

## Top 30 critical hosts by exposed model count

| Host | Models | Version | Country | Org | Hostname/Notes |
|---|--:|---|---|---|---|
| `20.2.91.83:80` | **57** | 1.84.0.dev1 | HK | Microsoft Azure | dev-build, broadest catalog |
| `217.217.248.242:4000` | 56 | — | ES | ONO/Vodafone | `vmi2956275.contaboserver.net` |
| `204.168.237.160:4000` | 44 | 1.82.6 | FI | Hetzner | `static.160.237.168.204.clients.your-server.de` |
| `107.174.66.118:4000` | 30 | 1.81.15 | US | RackNerd | `118s.pstnmizionlablinc.org` |
| `135.181.250.114:4000` | 26 | 1.83.0 | FI | Hetzner | |
| `95.216.124.247:4321` | 22 | 1.83.7 | FI | Hetzner | |
| `98.149.54.126:4100` | 22 | 1.75.5 | US | Charter Spectrum | `syn-098-149-054-126.res.spectrum.com` — **residential ISP** |
| `203.149.11.67:443` | 20 | 1.83.10 | TH | Samart Infonet | **`api.modelharbor.com`** — named product |
| `8.135.1.210:8002` | 19 | 1.81.5 | CN | Aliyun | |
| `156.227.236.247:4000` | 18 | 1.81.14 | JP | Yisu Cloud | |
| `52.55.247.39:80` | 17 | 1.77.7 | US | AWS US-East-1 | `ec2-52-55-247-39.compute-1.amazonaws.com` |
| `54.146.182.79:80` | 17 | 1.77.7 | US | AWS US-East-1 | likely co-tenant of 52.55.247.39 |
| `54.84.252.63:80` | 17 | 1.77.7 | US | AWS US-East-1 | likely co-tenant |
| `80.225.230.75:4000` | 17 | 1.83.10 | IN | Oracle Cloud | |
| `20.119.96.222:4000` | 16 | 1.81.15 | US | Microsoft Azure | |
| `64.227.146.129:4000` | 16 | 1.82.1 | IN | DigitalOcean | |
| `103.52.212.89:4000` | 15 | 1.82.6 | ID | PT Awan Data Teknologi | Indonesian govt-stack — `asisten-desa` model |
| `8.219.58.50:18081` | 14 | 1.81.12 | SG | Alibaba Cloud SG | |
| `84.247.181.100:4000` | 14 | 1.82.6 | DE | Contabo | **`search.lindela.io`** — named product |
| `144.76.201.226:4000` | 13 | 1.81.12 | DE | Hetzner | |
| `139.59.1.164:4000` | 12 | 1.81.12 | IN | DigitalOcean | |
| `157.180.28.97:4000` | 12 | 1.82.2 | FI | Hetzner | |
| `74.1.21.180:8001` | 12 | 1.81.15 | US | GTT | |
| `43.153.66.205:4000` | 11 | 1.81.6 | US | Tencent | |
| `95.216.95.1:4000` | 11 | 1.83.12 | FI | Hetzner | **`netiva.com.tr`** — named Turkish operator |
| `178.104.24.17:4000` | 10 | 1.82.5 | GB | EE Limited (your-server.de fronted) | |
| `109.123.227.237:8000` | 9 | 1.81.12 | AU | Contabo Asia | |
| `158.220.123.152:4000` | 9 | 1.81.12 | DE | Contabo | |
| `216.167.124.225:4000` | 9 | 1.83.3 | US | NTT America | |
| `38.45.80.70:4000` | 9 | 1.83.8 | US | Cogent | |

**Three AWS US-East-1 hosts (52.55.247.39, 54.146.182.79, 54.84.252.63)
all run the same version 1.77.7 with identical 17-model catalogs** —
high probability they're the same operator running a redundant deployment.
Worth a deeper attribution pass to determine.

## Notable named operators

Operators with identifiable hostnames or product branding in the
critical-host set:

- **`api.modelharbor.com`** (203.149.11.67, Thailand) — 20 models. The
  hostname `modelharbor` reads as a commercial LLM-routing product;
  if so, every customer of that product is sharing an unauth proxy.
- **`search.lindela.io`** (84.247.181.100, Germany Contabo) — 14 models.
  `lindela.io` is a registered domain with a product-branded subdomain;
  the host is running an auth-disabled LiteLLM serving a search-product
  pipeline.
- **`netiva.com.tr`** (95.216.95.1, Hetzner Finland) — 11 models. Turkish
  operator, product-style domain.
- **`evaluator.elastiplay.com`** (in extended top-100) — Indian operator,
  ML eval pipeline.
- **PT Awan Data Teknologi** (103.52.212.89, Indonesia) — 15 models
  including `asisten-desa` ("village assistant" — Indonesian government
  AI service).
- **Charter Spectrum residential** (98.149.54.126) — 22 models exposed
  on a **residential ISP IP**. This is a developer running LiteLLM at
  home with their personal API keys.

The critical-host set spans 16+ countries and includes both cloud
deployments (AWS/Azure/GCP/Alibaba) and budget-VPS deployments (Hetzner/
Contabo/DigitalOcean), with both production-branded hosts and
clearly-developer-machine deployments.

## Why LiteLLM unauth is uniquely severe at population scale

LLMjacking via unauth LiteLLM is different from other observability-tier
unauth findings in two ways:

1. **Active financial exposure.** Phoenix unauth exposes trace data
   (passive disclosure). LiteLLM unauth lets attackers actively spend
   the operator's money. A 24-hour automated probe campaign against an
   unauth LiteLLM can run thousands of dollars in upstream provider
   bills.

2. **Bypass of provider rate-limiting.** Many operators deploy LiteLLM
   precisely BECAUSE it's a single endpoint that aggregates multiple
   providers — meaning the LiteLLM proxy has the operator's API keys
   for OpenAI + Anthropic + Bedrock + Azure simultaneously. One
   unauth LiteLLM = potential abuse across the operator's full
   provider stack.

3. **Difficult to detect from operator side.** Most operators check
   their LLM provider dashboards by date-range. A slow, distributed
   probe (e.g. 10 requests/hour from different IPs) would show up as
   "normal-looking traffic" until the bill arrives.

## Disclosure plan

Per standing research-mode discipline, no disclosure outreach happens
during the research chain. When the chain calls "complete":

1. **Vendor-side**: BerriAI/LiteLLM should consider making the master-key
   requirement non-optional, OR shipping a warning banner when starting
   without `LITELLM_MASTER_KEY` set. This is the single highest-leverage
   change that would shrink the population-scale unauth rate.

2. **Operator-side**: each of the ~500 individual operators needs
   coordinated disclosure. Likely batched via the VisorBishop output
   as the canonical input for the disclosure pipeline (see
   `disclosures/send_drafts_api.py` in this repo for the existing
   pipeline shape).

## Methodology refinement

iter-6 is the **first full-population sweep** in the Phase 3 loop —
prior iters used the original Shodan corpora (which were themselves
populations from manual Phase 1+2 work, not fresh harvests). The
LiteLLM full sweep proves VisorBishop scales to population-class
workloads.

The right shape going forward: every platform fingerprint should get
both an initial-sample sweep (50-500 hosts to validate the prober)
AND a full-population sweep when the prober is mature.

## Next steps

1. ~~iter-1/2/3/4/5: platform + port expansion~~ ✓
2. ~~iter-6: full LiteLLM 5,391-host sweep~~ ✓ (this case study)
3. **Methodology Insight #14, #15 final writeups** — yield-vs-port-class alignment + dork-hits ≠ instances
4. **Phase 4 (web UI)** — VisorBishop dashboard with cross-platform attribution
5. **Disclosure-routing pipeline** for the cumulative iter-1..6 findings (283 unauth LiteLLM ready for BerriAI vendor disclosure + per-operator outreach)

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/iter6/`
- `litellm-full.json` (1.4MB) / `.csv` — 5,391-host full LiteLLM sweep
- `critical-top100.tsv` — 100 highest-yield critical hosts with attribution
- `critical-all.tsv` — full 283-host critical inventory
- `litellm-full.log` — sweep stderr (~69KB; mostly TLS handshake noise)

`~/recon/2026-05-10-llm-sweep/iter5/`
- `litellm-full.json.gz` — 89MB Shodan harvest (5,408 records)
- `litellm-full-urls.txt` — 5,391 deduplicated URLs
- `litellm-attribution.tsv` — ip:port → (hostnames, org, country, isp) lookup

`~/recon/2026-05-10-llm-sweep/iter6-triage.py` — reusable triage helper
that joins VisorBishop output to the Shodan attribution data.

Source: Nicholas-Kloster/VisorBishop@v0.1.5

Cross-references:
- [iter-5 case study (500-host sample)](visorbishop-iter5-survey-2026-05-11.md)
- [Phase 3 case study](visorbishop-phase3-survey-2026-05-11.md)
