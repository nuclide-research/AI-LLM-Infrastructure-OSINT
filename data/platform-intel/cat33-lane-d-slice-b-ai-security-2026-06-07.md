# Cat-33 Lane D Slice B Platoon Intel: Commercial AI-Security Startups

_Generated 2026-06-07. Phase 5 sweep slice B of 4. Source of truth: LiteLLM `guardrail_hooks/` directory enumerates the canonical commercial Lane D vendor space. Parent dispatch: `research-program/cat33-phase3b-three-lane-dispatch-2026-06-07.md`. Companion Lane B intel landed 2026-06-06; Lane D framework intel landed earlier 2026-06-07 in this directory._

## Scope

8 commercial Lane D vendors integrated into LiteLLM as `proxy/guardrails/guardrail_hooks/<vendor>`. The point of the slice is two-fold:

1. Verify the LiteLLM hook contract per vendor (default api_base, endpoint path, auth shape).
2. Pressure-test Insight #82 (branded error bodies as banner) at population scale. Three confirmations in Lane B promoted the pattern to medium confidence; this slice tries to break it or promote it to high.

## Per-vendor table

| Vendor | Apex | LiteLLM default api_base | Marker endpoint | DMARC | Insight #80 stage | Insight #82 marker | Insight #82 status |
|---|---|---|---|---|---|---|---|
| Aporia AI | aporia.com | (operator-supplied tenant URL) | POST /{id}/validate | p=quarantine | Series B | `X-APORIA-API-KEY header missing` at 400 | CONFIRMED |
| Aim Security | aim.security | https://api.aim.security | POST /fw/v1/analyze | p=none | Anomaly | generic `Authorization header is required` 401 | NOT CONFIRMED |
| Akto | akto.io | (operator-supplied) | POST /api/http-proxy | p=quarantine pct=25 | A/B transitional | N/A (operator-hosted) | N/A |
| Gray Swan (Cygnal) | grayswan.ai | https://api.grayswan.ai | POST /cygnal/monitor | p=none | Anomaly | `CONTENT_VALIDATION_ERROR` + /cygnal/ path 400 | CONFIRMED |
| Guardrails AI | guardrailsai.com | http://0.0.0.0:8000 | POST /guards/{name}/validate | p=quarantine pct=100 | Series A | N/A (OSS self-hosted) | N/A |
| Javelin | getjavelin.io (NOT javelin.live) | https://api-dev.javelin.live | POST /v1/guardrail/{name}/apply | p=none (getjavelin.io); none on javelin.live | Seed/A | TBD -- CF 525/530 blocked sandbox probe | INCONCLUSIVE |
| Lasso Security | lasso.security | https://server.lasso.security/gateway/v3 | POST /classify or /classifix | p=reject sp=none | Series B+ | NestJS `UnauthorizedException` + `Invalid API key` at 401 | CONFIRMED-WEAK |
| Pangea (AI Guard) | pangea.cloud | https://ai-guard.aws.us.pangea.cloud | POST /v1beta/guard | p=reject | Series C+ | branded `request_id: prq_` 403 | CONFIRMED |

## Apex corrections

- **Javelin:** the LiteLLM default `api-dev.javelin.live` does NOT resolve from public DNS (NXDOMAIN). The operational apex is **getjavelin.io**. The `javelin.live` apex has no MX and no DMARC; it appears to be a near-abandoned brand domain. The production API host `api.javelin.live` 301-redirects to **api.highflame.app** (Cloudflare-fronted). Either a tenant alias or a product rename in flight; either way, `getjavelin.io` is the apex to use for cert and DMARC pivots.
- **Aporia:** the LiteLLM example in source (`gr-prd-trial.aporia.com`) is a single tenant URL. The vendor apex is `aporia.com`. Tenant URLs follow the pattern `gr-{env}-{tier}.aporia.com` per the in-source comment.
- **All other vendors:** apex matches expectations.

## Insight #82 confirmation count

- **CONFIRMED (3):** Aporia (vendor-name header literal), Gray Swan (`CONTENT_VALIDATION_ERROR` + /cygnal/ path), Pangea (branded `prq_` request_id prefix).
- **CONFIRMED-WEAK (1):** Lasso (NestJS framework default body, distinctive only paired with `/gateway/v3/` path anchor).
- **NOT CONFIRMED (1):** Aim Security (generic FastAPI/Starlette 401).
- **N/A (2):** Akto (operator-hosted), Guardrails AI (OSS self-hosted, no SaaS endpoint).
- **INCONCLUSIVE (1):** Javelin (Cloudflare blocked sandbox probe).

**Insight #82 net effect:** 3 strict confirmations in this slice + 3 from Lane B (Lakera Guard, Prompt Security, AegisAI) = **6 strict confirmations across the survey**. The threshold for medium-to-high promotion was "a fourth would promote." We have six. **Insight #82 promotes to HIGH confidence.** The fan-in across vendors that span different stacks (FastAPI, NestJS, custom monitor APIs, request-id-prefixed REST) shows the pattern is not stack-specific; it is a deliberate developer-experience choice across the API-gateway guardrail category.

If Lasso's CONFIRMED-WEAK is admitted as a weak fourth from this slice, that strengthens but does not change the call.

## Insight #80 stage distribution (this slice, n=8)

| Stage band | Vendors | Count |
|---|---|---|
| p=reject | Pangea, Lasso | 2 |
| p=quarantine | Aporia, Guardrails AI, Akto (pct=25 partial) | 3 |
| p=none | Aim, Gray Swan, Javelin | 3 |

Enforcement rate (reject + quarantine over total): **5/8 = 62.5%**, vs the n=31 known-stage Cat-33 baseline of 64% enforcement. Slice is on-trend with the broader AI-security sub-population.

**Anomalies worth re-checking in 30 days:**

- **Aim Security** publicly disclosed the EchoLeak M365 Copilot zero-click; press positioning is Series A/B. Yet `aim.security` runs `p=none` with no rua. Either pre-SOC2 or the DMARC posture has not caught up to the security-buyer-facing motion. Per Insight #80's secondary hypothesis ("the signal is selling to security buyers, not raised a Series C"), this is the data point that complicates the model -- an AI-security vendor that sells to security buyers AND runs p=none.
- **Gray Swan** is research-prominent (Cygnal red-team + Shade jailbreak benchmark) but also runs `p=none`. Same anomaly shape as Aim.

Both anomalies suggest the DMARC posture lags the funding/research-prominence signal at this stage band for some vendors; the model is directional, not deterministic.

## Disclosure contacts

| Vendor | DMARC rua | security.txt | Notes |
|---|---|---|---|
| Aporia | dmarc@aporia.com | unverified | Standard |
| Aim Security | (none) | unverified | Anomaly; route via aim.security contact form |
| Akto | dmarcreports@akto.io | unverified | Standard |
| Gray Swan | (none) | unverified | Route via security@grayswan.ai expected; verify on apex |
| Guardrails AI | admin@guardrailsai.com | unverified | + GitHub security advisories on guardrails-ai/guardrails |
| Javelin | support@getjavelin.io | unverified | Apex correction: getjavelin.io, not javelin.live |
| Lasso Security | dmarc@lasso.security | unverified | sp=none = subdomain-spoof asymmetry worth noting |
| Pangea | dmarc.reports@pangea.cloud | unverified | Proofpoint inbound + ruf forensic mailbox = mature triangle |

## Files written

- `~/tome/platforms/aporia-ai.json` (new)
- `~/tome/platforms/aim-security.json` (new)
- `~/tome/platforms/akto.json` (new)
- `~/tome/platforms/grayswan.json` (new)
- `~/tome/platforms/guardrails-ai.json` (new)
- `~/tome/platforms/javelin.json` (new)
- `~/tome/platforms/lasso.json` (new)
- `~/tome/platforms/pangea.json` (new; Lane D delta noted in `lane_d_delta` field)
- `~/AI-LLM-Infrastructure-OSINT/shodan/queries/33-ai-email-guardrails.md` (appended `## Lane D Slice B AI-security startups` section with 3-tier dorks per vendor + population-shape note)
- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-d-slice-b-ai-security-2026-06-07.md` (this file)

## Brief discipline observed

- Source code on GitHub. NO clone. Used `gh api` and raw.githubusercontent for individual file pulls.
- Marker-only POST probes with empty body `{}` against documented public endpoints. No record reads. No tenant impersonation. No production probing.
- DMARC + MX dig against vendor apexes.
- Em-dash rule followed.
- Names ARE the finding. The branded error body literal IS the deliverable.
- Pangea treated as Lane B-to-D delta; full Pangea infra survey not redone.
- Apex corrections called out explicitly (Javelin getjavelin.io, NOT javelin.live).
- Time budget: under the 90 minute cap.
