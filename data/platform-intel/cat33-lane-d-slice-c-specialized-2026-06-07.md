# Cat-33 Lane D Slice C -- newer/specialized vendors (long tail)

Date: 2026-06-07
Slice: C of 4 (specialized / newer / smaller vendors of the LiteLLM canonical Lane D catalog)
Discipline: source code on GitHub (no clone), DMARC + MX dig only, no active probing, source-of-truth = LiteLLM guardrail_hooks subtree.

## Headline numbers

- **Vendors covered:** 10
- **Real commercial entities:** 8
- **Stubs / OSS-wrappers:** 2 (`semantic_guard`, `vigil_guard`)
- **DMARC distribution (8 real-vendor apexes):**
  - p=reject: 3 (noma.security, onyx.security, qohash.com)
  - p=quarantine: 3 (dynamo.ai, promptguard.co, qualifire.ai)
  - p=none: 1 (enkryptai.com) -- AI-SECURITY vendor running monitoring-only DMARC
  - no DMARC at all: 1 (cycraft.ai -- product subsidiary domain; parent cycraft.com.tw is the protected name)

The cohort is roughly what the dispatch predicted: heavy early-stage, founder-attributable, with one obvious own-house finding (enkryptai p=none) and one structural surprise (cycraft.ai bare).

## Per-vendor table

| Slug | Apex | Real / Stub | API base | DMARC | MX provider | Notable risk surface | Founder / origin |
|---|---|---|---|---|---|---|---|
| dynamoai | dynamo.ai | REAL | api.dynamo.ai | p=quarantine | Google Workspace | API key leak; standard SaaS guardrail vendor | Vinod Iyengar (ex-H2O.ai); Boston |
| enkryptai | enkryptai.com | REAL | api.enkryptai.com | **p=none** | Microsoft 365 + HubSpot SPF | DMARC monitoring-only on an AI-SECURITY apex; spoofable | Yash Datta; Boston/SF; founded 2023 |
| noma | noma.security | REAL | api.noma.security | p=reject | Google + Salesforce + HubSpot | Mature ops; AIDR endpoint; default_application_id=`litellm` makes operator detection trivial on Noma's side | Niv Braun; Tel Aviv/NYC; founded 2023; $32M Series A 2024 |
| onyx | onyx.security | REAL (early) | ai-guard.onyx.security | p=reject | Google Workspace | **API key in URL path** (`/guard/evaluate/v1/{api_key}/litellm`) -- credentials leak to any path-logging intermediary; OWASP A02:2021 anti-pattern | Early-stage; minimal LiteLLM hook (141 lines) suggests pre-seed/seed |
| promptguard | promptguard.co | REAL (solo founder) | api.promptguard.co | p=quarantine | Google + Postmark | API key leak; .co TLD + 221-line hook = early-stage solo vendor | **Abhijoy Sarkar** (per DMARC ruf address) |
| qohash | qohash.com | REAL (mature) | self-hosted nexus:8800 | p=reject | Google + HubSpot + Greenhouse | On-prem Qostodian Nexus appliance; default scheme is plaintext http://; in-cluster trust assumption; LoadBalancer/NodePort drift exposes appliance | Qohash; Quebec City; founded 2018; pivoted DLP -> AI-DLP |
| qualifire | qualifire.ai | REAL | api.qualifire.ai + proxy.qualifire.ai | p=quarantine (adkim=s aspf=s strict) | Google + HubSpot + Amplemarket | Reverse-proxy mode means vendor sees every prompt/completion in cleartext by design; concentration risk operators may underweight | Tel Aviv; founded 2024 |
| semantic-guard | **N/A** | **STUB** | in-process embedding | N/A | N/A | LiteLLM-shipped feature wrapping aurelio-labs/semantic-router; no commercial entity, no network surface | (none) |
| vigil-guard | **N/A** | **STUB** | operator-supplied (BYO) | N/A | N/A | Almost certainly wraps deadbits/vigil-llm OSS; operator self-deploy; route shape `/v1/guard/analyze` + decision enum ALLOWED/SANITIZED/BLOCKED matches vigil-llm | Adam Swanda (deadbits) for upstream OSS |
| xecguard | cycraft.ai | REAL | api-xecguard.cycraft.ai (AWS CloudFront US edge) | **NONE (and no SPF)** | (parent cycraft.com.tw on Google) | **cycraft.ai product domain has zero email auth** -- spoofable; uncommon for an AI-security vendor | **CyCraft Technology** (Benson Wu / Jeremy Chiu); Taipei, Taiwan; founded 2017; **foreign-origin tool, disclose** |

## Real-vs-stub split

Real commercial vendors (8):
dynamoai, enkryptai, noma, onyx, promptguard, qohash, qualifire, xecguard.

Stubs / OSS-wrappers (2):
- **semantic_guard** -- LiteLLM-built-in. Pure Python in-process embedding match using the open-source `semantic-router` (Aurelio Labs). No vendor. Treat as a LiteLLM feature, not a third party.
- **vigil_guard** -- BYO endpoint. `VIGIL_GUARD_URL` required; no default; integration raises `VigilGuardMissingConfig` without it. Route shape and decision enum match the open-source `deadbits/vigil-llm`. No hosted vendor.

The stub-rate (20%) is in line with the dispatch hypothesis that Lane D's long tail would include OSS-wrapper integrations LiteLLM ships for completeness.

## Notable own-house findings (vendor's own infrastructure)

These are the per-apex findings that surface from a DMARC/MX-only dig pass -- no active probing, names-as-finding discipline.

1. **enkryptai.com runs DMARC p=none.** An AI security vendor whose customers depend on it for runtime safety is operating its own email at the weakest enforcement tier. Spoofable; phishing-amplifying. Either an oversight or a transition state that has lingered.

2. **cycraft.ai has no DMARC and no SPF.** The product subsidiary domain for XecGuard is unprotected. The corporate parent `cycraft.com.tw` is the email-active domain. Customers receiving outbound from a `*.cycraft.ai` address have no DMARC verifiability.

3. **Onyx API key in URL path.** Not a DMARC finding -- structural API design -- but it surfaces directly from the LiteLLM source. `/guard/evaluate/v1/{api_key}/litellm` puts credentials into every path-logging intermediary the operator runs (CDN access log, WAF, reverse proxy, browser Referer for any operator UI that renders a link). OWASP A02:2021 anti-pattern. Onyx has p=reject on email but a credential-design issue in product.

4. **Qohash default scheme is plaintext.** `QOSTODIAN_NEXUS_API_BASE` default is `http://nexus:8800`. The integration assumes in-cluster trust (Kubernetes service DNS). Operators who run the appliance outside that boundary, or with cross-namespace egress monitoring, see guardrail decisions in cleartext.

5. **Noma `default_application_id="litellm"`.** Cosmetic, but: operators using Noma + LiteLLM without overriding the application_id are labeling themselves as LiteLLM operators on Noma's side. Useful for Noma's customer-shape analytics; mildly fingerprinting from an operator-privacy lens.

6. **Qualifire proxy mode = vendor sees everything.** `proxy.qualifire.ai` is a transparent reverse proxy. Vendor sees prompt and completion in cleartext by design. Not a defect -- it is the product -- but worth flagging in the per-vendor risk surface.

## Side findings (cohort-level)

- **Founder-attributable from DMARC.** PromptGuard's `ruf=mailto:abhijoysarkar@promptguard.co` puts the founder's full name on a passive query. Notable because it confirms the solo-founder pattern at this scale.

- **Marketing-stack provenance.** HubSpot SPF appears in 4 of 8 (enkryptai, noma, qohash, qualifire). Amplemarket outbound on qualifire signals active outbound sales. Greenhouse on qohash signals active hiring. These are go-to-market maturity signals, not vulnerabilities, but they help cohort the population.

- **TLD distribution.** 4 of 8 real-vendor apexes are non-`.com`: dynamo.ai, qualifire.ai, onyx.security, noma.security, plus promptguard.co. The `.security` TLD is over-represented (noma + onyx), a 2023-2024 launch tell.

- **CyCraft on AWS CloudFront US edge.** api-xecguard.cycraft.ai resolves to 18.173.121.0/24 (AWS CloudFront US). A Taiwanese vendor fronting its AI-guardrails API on US infrastructure is a sovereignty-relevant deployment shape.

## Files written

- 10 tome platform JSONs at `/home/cowboy/tome/platforms/{dynamoai,enkryptai,noma,onyx,promptguard,qohash,qualifire,semantic-guard,vigil-guard,xecguard}.json`
- Dorks appended at `/home/cowboy/AI-LLM-Infrastructure-OSINT/shodan/queries/33-ai-email-guardrails.md` under heading `## Lane D Slice C newer/specialized`
- This summary at `/home/cowboy/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-d-slice-c-specialized-2026-06-07.md`

## Method discipline (logged)

- LiteLLM source read via `gh api` (no clone), one file per vendor.
- DNS via `dig +short` only (TXT _dmarc, MX, SPF on apex).
- No active probing. No HTTP requests to vendor APIs.
- Names are the finding; the dorks are the next-stage probe, not exercised here.

## Codified Insight candidate -- Lane D Slice C, the long-tail stub-rate

For LiteLLM's guardrail catalog, the long-tail slice (vendors with single-author or recent additions) contains roughly 20% stubs: BYO-endpoint integrations or in-process OSS wrappers with no commercial entity behind them. These should not be counted as platforms in any vendor-population census; they are LiteLLM features that happen to share the guardrail_hooks subtree shape. The discriminator at the source-code level is the absence of a default api_base URL pointing at a vendor-controlled host. Tested on N=10 vendors in this slice; 2 stubs found; both lacked a vendor default URL. Confidence: medium.
