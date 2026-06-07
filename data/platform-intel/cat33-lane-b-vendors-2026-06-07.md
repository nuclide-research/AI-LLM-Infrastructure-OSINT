# Cat-33 Lane B: API Gateway / Bearer-token Guardrails

_Phase 3B Lane B platoon return, 2026-06-07. Companion to [`33-ai-email-guardrails-deep-brief-2026-06-06.md`](../../categories/33-ai-email-guardrails-deep-brief-2026-06-06.md) and [`33-ai-email-guardrails.md`](../../shodan/queries/33-ai-email-guardrails.md). Lane B sits between an AI agent and an LLM provider over HTTPS with a bearer token. Customer integrates an SDK or curls the JSON contract._

## Vendors covered

| Vendor | Apex | Tome JSON | Marker probe | Result |
|---|---|---|---|---|
| Lakera Guard | lakera.ai | `~/tome/platforms/lakera-guard.json` | POST /v1/guard | 400 body cites docs.lakera.ai/docs/api |
| Prompt Security | prompt.security | `~/tome/platforms/prompt-security.json` | GET /v1/protect | 400 JSON `{"status":false,"error":"No api key provided"}` |
| AegisAI | aegisai.ai | `~/tome/platforms/aegisai.json` | GET console.aegisai.ai/ | 200 HTML title "Aegis AI Console" |
| Sluice (B-mode) | sluice.email | already in `~/tome/platforms/sluice.json` (Lane A owns) | n/a | pointer only |
| Salus | salus-ai.com (REFUTED) | not written | n/a | apex mismatch: salus-ai.com is Italian medication-management product, not YC W2026 vendor |

## DNS posture (Insight #80 input)

| Vendor | MX | DMARC | Notes |
|---|---|---|---|
| Lakera | Outlook (lakera-ai.mail.protection.outlook.com) | `p=reject` + easydmarc + cloudflare aggregation | enterprise-grade |
| Prompt Security | Google Workspace | `p=reject` self-hosted rua | mid-stage cloud-native |
| AegisAI | Google Workspace | `p=reject` rua=ryan@aegisai.ai | founder-personal inbox |
| Salus (apex collision) | Outlook | none | unrelated entity |

## Subdomain populations (hackertarget hostsearch 2026-06-07)

- Lakera: 49 hosts, multi-region `*.api.lakera.ai`, internal-AWS DNS leaks (`-internal` -> RFC1918), LiteLLM in path (`litellm-eu`, `litellm-us`), separate Gandalf challenge product, customer dashboard at `platform.lakera.ai`.
- Prompt Security: 50+ hosts, 8 region splits, BYOS deployment scaffold (`byos-example`, `byos-<customer>.prompt.security`), dev cluster reveals named engineers via DNS (operator OSINT), admin-Kibana + ArgoCD on private 10.x.
- AegisAI: 14 hosts, smaller surface, Langfuse + internal phishhook on staging, GCP IAP gating on demo.
- Salus apex: 3 hosts, vercel-fronted (76.76.21.x), unrelated product.

## Marker fingerprint observation

Both Lakera (`POST /v1/guard`) and Prompt Security (`GET /v1/protect`) deliberately return a distinctive vendor-branded error body at HTTP 400 without authentication, for customer integration debugging. The error string IS the cheap-fingerprint banner for the entire API-gateway guardrail lane. AegisAI ships a branded console SPA title instead. Hypothesis: the API-gateway guardrail lane has a STRUCTURAL banner-by-design pattern. Confirm against a third independent vendor (Cascade, Galini, Lakera v2) to elevate to numbered Insight.

## Public auth posture

| Vendor | Scheme | Default | Bearer-token surface |
|---|---|---|---|
| Lakera Guard | `Authorization: Bearer lak_<token>` | auth-on-default | API key per workspace; SDK + REST |
| Prompt Security | `APP-ID` header + API key | auth-on-default | per-app key; regional endpoints route by header or hostname |
| AegisAI | Workspace-OAuth side, no public API surface found | n/a | inbound; OAuth scope is the threat surface (Cat-33 Lane C discipline) |

## Disclosure contacts

| Vendor | security.txt | DMARC rua | Direct |
|---|---|---|---|
| Lakera | 404 | dmarc@lakera.ai (easydmarc aggregation) | https://lakera.ai/contact |
| Prompt Security | 404 | dmarc@prompt.security | https://prompt.security |
| AegisAI | 404 | ryan@aegisai.ai (founder) | direct via DMARC rua |

No vendor in this lane published `/.well-known/security.txt` as of 2026-06-07. This is a Cat-33 lane finding: outbound-AI-email guardrails ship without canonical disclosure metadata, while preaching guardrails to others.

## Population estimate

| Lane B vendor | Public SaaS edge IPs | Self-hosted population | Source |
|---|---|---|---|
| Lakera Guard | 4 regions visible | self-hosted documented, dark to Shodan | DNS + product docs |
| Prompt Security | 8 region splits | BYOS scaffold visible | DNS |
| AegisAI | 1 production cluster | none surfaced | DNS |

## Blockers

- **Salus YC W2026 apex unresolved.** salus-ai.com is an Italian medication-management product (Salus AI Designed for Life), unrelated to the YC vendor. Lane C platoon should resolve via YC W2026 batch list or Crunchbase, not assume apex from name. Reported, not guessed.
- **crt.sh returning 502.** Subdomain enumeration ran through hackertarget instead. Coverage may be partial; re-run when crt.sh recovers.
- **No active Shodan facet sweep.** Per scope, Shodan = Playwright web UI from cowboy's authenticated session only. Documented dorks in 3 tiers for operator-led execution.

## Lane-empty determination

Lane B is NOT empty: 3 vendor JSONs written (Lakera, Prompt Security, AegisAI), with Sluice already in `~/tome/`. AegisAI re-classified as INBOUND per primary-source DNS posture, but kept in tome with category-lane-classification field documenting the misclassification. Lane B effective dedicated-vendor count = 2 (Lakera, Prompt Security) + 1 sibling (Sluice from Lane A) + 1 misclassified-tracked (AegisAI). Above the lane-empty threshold (>= 3).

## Cross-lane handoff

- **Salus**: hand to Lane C platoon with the apex blocker noted.
- **Sluice B-mode**: no work; Lane A canonical.
- **AegisAI re-classification**: surfaces in Cat-33 deep brief inbound-misclassified table; suggest updating brief to confirm the call after primary-source verification.

## Files written

- `~/tome/platforms/lakera-guard.json`
- `~/tome/platforms/prompt-security.json`
- `~/tome/platforms/aegisai.json`
- `~/AI-LLM-Infrastructure-OSINT/shodan/queries/33-ai-email-guardrails.md` (Lane B section appended)
- `~/AI-LLM-Infrastructure-OSINT/data/platform-intel/cat33-lane-b-vendors-2026-06-07.md` (this file)

## aimap fingerprint scaffold (review-only, not written to aimap)

```
// Lakera Guard
Name: "Lakera Guard"
Probe: POST /v1/guard with empty JSON body
Marker: body contains "docs.lakera.ai/docs/api" AND HTTP 400
False-positive guard: body must include the literal docs URL substring

// Prompt Security
Name: "Prompt Security"
Probe: GET /v1/protect
Marker: JSON body matches {status:false, error:"No api key provided"} AND HTTP 400
False-positive guard: response Content-Type starts with application/json

// AegisAI Console
Name: "AegisAI Console"
Probe: GET / on console.aegisai.ai (or any Aegis SPA)
Marker: HTML title literal "Aegis AI Console"
False-positive guard: title element EXACT match, no substring
```

Operator: review and add to `~/ai-recon/aimap/fingerprints.go` next aimap version bump.
