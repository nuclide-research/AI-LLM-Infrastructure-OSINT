# Cat-33 Lane D Slice A: Enterprise Security Vendor Guardrails

_Generated 2026-06-07 as the Slice A return of the 4-slice Phase 5 sweep over the LiteLLM canonical Lane D vendor catalog (`litellm/proxy/guardrails/guardrail_hooks/`). Parent: `categories/33-ai-email-guardrails-deep-brief-2026-06-06.md`. Dispatch spec: `research-program/cat33-phase3b-three-lane-dispatch-2026-06-07.md`. Lane D parent intel: `cat33-lane-d-vendors-2026-06-07.md` (same directory)._

## Scope

8 enterprise-security vendors with confirmed LiteLLM guardrail integrations. All are commercial; 7 SaaS, 1 OSS-self-hosted with a hyperscaler commercial wrapper (IBM watsonx.governance / FMS Guardrails). Source-of-truth for the API contract: the LiteLLM `guardrail_hooks/` subdirectory per vendor, read off `raw.githubusercontent.com` (NOT a local clone).

## Vendor coverage

| Vendor | LiteLLM dir | Integration status | Apex | DMARC | MX provider | Parent |
|---|---|---|---|---|---|---|
| HiddenLayer | `hiddenlayer/` | REAL (OAuth2 client_credentials, /detection/v1/interactions) | hiddenlayer.com (corp) + hiddenlayer.ai (product) | corp=p=quarantine, product=p=none | corp=Google Workspace, product=no MX | HiddenLayer Inc, M12-led Series B |
| CrowdStrike AIDR | `crowdstrike_aidr/` | REAL (Bearer CS_AIDR_TOKEN, /v1/guard_chat_completions; api_base operator-set per Falcon region) | crowdstrike.com | p=reject | Proofpoint | CrowdStrike Holdings (CRWD) |
| Zscaler AI Guard | `zscaler_ai_guard/` | REAL (Bearer ZSCALER_AI_GUARD_API_KEY, /v1/detection/execute-policy at api.us1.zseclipse.net) | zscaler.com (corp) + zseclipse.net (product) | corp=p=reject, product=no DMARC | corp=Google Workspace, product=no MX | Zscaler Inc (ZS) |
| Microsoft Purview | `microsoft_purview/` | REAL (OAuth2 client_credentials via login.microsoftonline.com, calls graph.microsoft.com/v1.0; user-id resolution chain is documented impersonation surface) | microsoft.com | p=reject pct=100 | Microsoft EOP | Microsoft |
| IBM Guardrails | `ibm_guardrails/` | REAL (Bearer IBM_GUARDRAILS_AUTH_TOKEN, dual-mode: detector-server /api/v1/text/contents or orchestrator /api/v2/text/detection/content; base_url operator-supplied) | ibm.com (commercial); foundation-model-stack on GitHub (OSS upstream) | p=reject sp=none | Proofpoint | IBM Corporation |
| PANW Prisma AIRS | `panw_prisma_airs/` | REAL (x-pan-token vendor header, /v1/scan/sync/request at service.api.aisecurity.paloaltonetworks.com; LARGEST guardrail hook in the catalog at 84KB, with /v1/messages and /v1/responses streaming support) | paloaltonetworks.com (corp) + aisecurity.paloaltonetworks.com (product) | p=reject | Proofpoint | Palo Alto Networks (PANW) |
| Cato Networks | `cato_networks/` | REAL (Bearer CATO_API_KEY, /fw/v1/analyze at api.aisec.catonetworks.com; WSS streaming variant) | catonetworks.com (corp) + aisec.catonetworks.com (product) | p=quarantine | Microsoft EOP | Cato Networks (SASE) |
| Rubrik | `rubrik/` | REAL but split: hook dir is initializer stub; real implementation at `litellm/integrations/rubrik.py` (605 lines). Webhook-style: post-completion tool blocking + batch logging. Webhook URL operator-supplied. | rubrik.com | p=reject pct=100 (multi-RUA including self mailsecurity@rubrik.com) | Google Workspace | Rubrik Inc (RBRK) |

Integration confirmation totals: **8 / 8 REAL** (none are stub, none are experimental). One structural split (Rubrik) where the hook directory under `guardrail_hooks/` only ships `__init__.py` but the logger lives at `litellm/integrations/rubrik.py`.

## Apex correction count

**0 corrections to the Slice prompt vendor names**, but **2 product-vs-corporate apex distinctions** worth flagging downstream:

- HiddenLayer: `hiddenlayer.com` is corporate / email infra; `hiddenlayer.ai` is product / API. DMARC posture differs (`p=quarantine` vs `p=none`).
- Zscaler AI Guard: `zscaler.com` is corporate; `zseclipse.net` is product. Product apex has neither DMARC nor MX (product-only domain).
- Cato Networks: `catonetworks.com` corp, `aisec.catonetworks.com` product subdomain (not split apex).
- PANW: `paloaltonetworks.com` corp, `aisecurity.paloaltonetworks.com` product subdomain (not split apex).

The HiddenLayer and Zscaler product-apex splits are the cohort's exposure pattern: vendor uses a different TLD or domain for the product, and the security posture is uneven across the split.

## Notable findings

### Strongest DMARC posture

CrowdStrike: `p=reject; fo=1; ri=3600; rua=` to both Proofpoint and Agari, ruf the same. Hourly forensic interval (ri=3600), full-failure reporting (fo=1), dual aggregator. This is the highest-discipline DMARC config in the cohort.

### Weakest DMARC posture (and the irony of it)

HiddenLayer's product apex `hiddenlayer.ai` has `p=none`. The corporate apex `hiddenlayer.com` has `p=quarantine`. A security vendor with a product apex at `p=none` is a structural finding: the OSINT signature of "treat product domain as marketing-only, ignore email security on it" is present at an AI-security vendor whose entire product class is supposed to catch this.

### Auth-scheme heterogeneity

The 8 vendors use 5 distinct auth schemes:

1. **Bearer token (standard)**: CrowdStrike, Zscaler, IBM, Cato, Rubrik (5 of 8).
2. **OAuth2 client_credentials -> JWT bearer**: HiddenLayer, Microsoft Purview (2 of 8).
3. **Vendor-specific header (NOT Authorization)**: PANW with `x-pan-token` (1 of 8).

For population enumeration: `http.headers:"x-pan-token"` is a Shodan dork that selects PANW-protected traffic specifically, but Shodan's HTML-only body matching may 0-result on this; route to Censys for header-layer signal. Insight candidate: vendor-specific auth headers (`x-pan-token`, `x-cs-token`, etc) are a richer fingerprint than `Authorization: Bearer` because they collide with no other vendor.

### IBM is the only OSS-self-hosted entry in the cohort

The other 7 vendors run the policy engine in their own cloud. IBM ships the detector server and orchestrator as foundation-model-stack OSS, expecting operators to deploy. This means:

- IBM is the only vendor in this slice that inherits the dork-population-substitution risk pattern from Lane D parent.
- The other 7 vendors' Shodan-visible population is **the vendor's own edge**, NOT customer adoption. Customer attribution requires cert-pivot.
- IBM's threat surface lives in customer-side deployments; the others' threat surface lives in vendor-side API gateways.

### Rubrik's header proxying

The Rubrik guardrail explicitly proxies inbound Authorization, Cookie, and x-api-key headers from the original client-to-LiteLLM call through to the configured webhook URL. This is documented behavior in the source (`litellm/integrations/rubrik.py` line 346 area). Operators who configure Rubrik AI Detection may not realize that client tokens flow to Rubrik's logging plane. A misconfigured `RUBRIK_WEBHOOK_URL` (typo, DNS hijack on the operator's chosen URL) exfiltrates every agent call including these inbound headers.

### PANW hook is by far the heaviest

The `panw_prisma_airs.py` file is 84KB (1700+ lines) versus 5-30KB for every other hook in the catalog. It alone implements Anthropic `/v1/messages` SSE handling, OpenAI `/v1/responses` streaming, and the requester_metadata deep-copy for trace-id correlation. The implementation surface is meaningfully larger than its peers; CVE history for this hook will be worth watching.

### Microsoft Purview's user-id resolution surface

The source's `purview_base.py` explicitly documents 3 fallback paths to resolve the user a request is attributed to: `user_api_key_dict.user_id`, `end_user_id`, then `metadata["user_api_key_user_id"]`. The first two are caller-influenceable; only the third is proxy-trusted. The source explicitly calls out that LiteLLM operators must enable trusted-id mode (which strips caller-supplied `user_api_key_*` keys from metadata) to avoid impersonation. Default behavior is the looser resolution chain. This is an operator-misconfiguration surface, not a vendor bug.

## Disclosure contacts

| Vendor | Channel |
|---|---|
| HiddenLayer | `https://hiddenlayer.com/.well-known/security.txt` (verify) |
| CrowdStrike | `psirt@crowdstrike.com`, `https://www.crowdstrike.com/.well-known/security.txt` |
| Zscaler | `https://www.zscaler.com/.well-known/security.txt` (verify) |
| Microsoft | MSRC `https://msrc.microsoft.com` |
| IBM | `psirt@us.ibm.com` |
| PANW | `psirt@paloaltonetworks.com` |
| Cato Networks | `https://www.catonetworks.com/.well-known/security.txt` (verify) |
| Rubrik | `mailsecurity@rubrik.com` (observed in DMARC RUA list) |

## DMARC distribution

| Policy | Count | Vendors |
|---|---|---|
| `p=reject` | 6 | CrowdStrike, Microsoft, IBM, PANW, Rubrik, Zscaler (corp) |
| `p=quarantine` | 2 | Cato Networks (corp), HiddenLayer (corp) |
| `p=none` | 1 | HiddenLayer (product apex .ai) |
| no DMARC | 1 | Zscaler product apex zseclipse.net |

MX provider distribution: Proofpoint 3 (CrowdStrike, IBM, PANW), Google Workspace 3 (HiddenLayer corp, Zscaler corp, Rubrik), Microsoft EOP 2 (Microsoft, Cato Networks). All 8 use a third-party DMARC aggregator (Proofpoint, Dmarcian, vali.email, everest.email, mxtoolbox); none roll their own.

## Files written

- `~/tome/platforms/hiddenlayer.json`
- `~/tome/platforms/crowdstrike-aidr.json`
- `~/tome/platforms/zscaler-ai-guard.json`
- `~/tome/platforms/microsoft-purview.json`
- `~/tome/platforms/ibm-guardrails.json`
- `~/tome/platforms/panw-prisma-airs.json`
- `~/tome/platforms/cato-networks.json`
- `~/tome/platforms/rubrik-ai-detection.json`
- `~/AI-LLM-Infrastructure-OSINT/shodan/queries/33-ai-email-guardrails.md` (Lane D Slice A enterprise section appended; 3-tier dork block per vendor + cohort discipline + DMARC posture note)
- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-d-slice-a-enterprise-2026-06-07.md` (this file)

## Brief discipline observed

- Read LiteLLM source from raw.githubusercontent.com; no local clone.
- DMARC + MX dig only; zero active scanning of vendor production infrastructure.
- No em-dashes.
- Names ARE the finding; no record reads.
- Apex-split vs subdomain-split distinction recorded where it matters (HiddenLayer, Zscaler split apex; Cato, PANW use product subdomains).
- LiteLLM `default_branch` quirk (`litellm_internal_staging`) noted in parent Lane D file; not re-stated here.
- Population-substitution risk per vendor: 7 of 8 SaaS edges measure vendor-side infra, not customer adoption. IBM alone measures operator deployments and inherits the framework-vs-deployment confound.
