# 33. AI Email Guardrails (outbound LLM-generated email safety)

_Section created: 2026-06-06. Companion to [§24](24-llm-safety-guardrail-policy.md) (general guardrails / policy engines). This section covers the **outbound-mail-layer** AI safety class: products that sit between an AI agent and the recipient inbox, scanning every LLM-drafted email for PII, prompt-injection-echo, hallucinations, tone, policy violations, and rate-limit / loop pathologies before delivery._

The category is distinct from classic AI-for-email-security (Abnormal, Sublime, Material, Avanan, Proofpoint+Tessian, Cloudflare Email Security/Area 1) which is **inbound** phishing detection at the inbox. This category is **outbound** LLM-output guardrails at the MTA or REST API layer, addressed at agentic-mail use cases.

| Subclass | Examples | Deployment mode | Shodan visibility |
|---|---|---|---|
| **MTA-layer relay guardrails** | Sluice (Haraka relay + REST API) | Hosted SaaS, customer SMTP-points-here | Direct on the relay node (port 587/465) + cert SAN |
| **API-layer agent guardrails** | AegisAI, Prompt Security email connectors | SaaS API | Indirect (caller-side dorks against apps) |
| **Agent-side safety bouncers** | BeeSafe AI (YC), Salus (YC W2026) | SaaS / sidecar | Indirect |
| **General LLM guardrails repurposed for email** | Lakera Guard, Guardrails AI, NeMo Guardrails | Mixed | See §24 |

**Methodology lesson (carried from §24):** brand-name single-word body matching is noisy. "Sluice" alone matches sluice gates, sluice boxes, hydraulic engineering content. Conjunctive matching required: brand + tagline + endpoint signature.

**Survey status:** **first platform CONFIRMED 2026-06-06 (Sluice).** Three sibling candidates queued. This file logs every dork executed against the category with hit count and date; zero-result dorks are kept.

---

## 1. Sluice (sluice.email)

CONFIRMED 2026-06-06. Single canonical hosted instance on `204.168.138.213` (Hetzner Helsinki, Haraka MTA in Docker Compose). Operator: sluice.email, registered 2026-03-11 via Ascio DK. See [`platforms/sluice.json`](../../../tome/platforms/sluice.json) and case study `case-studies/commercial/sluice-ai-email-guardrails-2026-06-06.md` (pending).

| Shodan Query | Notes |
|---|---|
| `ssl.cert.subject.cn:"sluice.email"` | Cert-SAN anchor (highest specificity). |
| `ssl.cert.subject.cn:"app.sluice.email"` | App-cert anchor. |
| `ssl.cert.subject.cn:"smtp.sluice.email"` | SMTP-cert anchor (smtp subdomain is NOT Cloudflare-proxied, so directly visible). |
| `http.html:"AI email safety layer"` | Tagline meta-description match. |
| `http.html:"AI email safety layer" http.title:"Sluice"` | Conjunctive brand + tagline. |
| `http.favicon.hash:-2070047203` | Favicon mmh3 of the Sluice app icon. |
| `port:587 "Nice to meet you" "sluice"` | Haraka greeting + brand string on submission port. |
| `"sluice-nginx-1.sluice_default"` | Docker Compose service+network leak in EHLO greeting. |
| `port:465 "You talk too soon"` | Haraka `early_talker` plugin signature; combine with brand. |

Operator hardening posture: Cloudflare front on web, HSTS preload, locked CSP, current OpenSSH 9.6p1, Let's Encrypt E7 fresh. **No probing past banner-grab.**

---

## 2. AegisAI (aegisai.ai)

Sibling candidate. CONFIRMED public footprint, **not yet enumerated.** "Agentic AI email security platform": closest naming/positioning to Sluice.

| Shodan Query | Notes (run-pending) |
|---|---|
| `ssl.cert.subject.cn:"aegisai.ai"` | Cert anchor. |
| `ssl.cert.subject.cn:"app.aegisai.ai"` | App-cert anchor. |
| `http.html:"AegisAI" http.html:"email"` | Brand + topic. |

---

## 3. Prompt Security (prompt.security)

Broader GenAI runtime platform; **email connectors are part of the surface.** Inbound-policy SaaS, not MTA relay. Sibling-adjacent. Not yet enumerated.

| Shodan Query | Notes (run-pending) |
|---|---|
| `ssl.cert.subject.cn:"prompt.security"` | Cert anchor. |
| `http.html:"prompt.security"` | Body reference. |

---

## 4. BeeSafe AI (YC) / Salus (YC W2026)

Frontier social-engineering / agent-side safety. Possibly relevant. Footprint sparse. Not yet enumerated.

---

## Discovery dorks (open-ended, for finding NEW platforms in this class)

| Query | Rationale |
|---|---|
| `port:587 "Nice to meet you"` | All Haraka MTAs (broad, ~thousands). Filter against `dnsbl`, `relay`, `email-safety`, `guardrails` in nearby fields. |
| `port:587 "Nice to meet you" "_default"` | Haraka behind docker-compose (project_default network leak in EHLO). |
| `ssl:"AI email safety"` | Cert subject containing the phrase. |
| `http.html:"guardrails for AI-generated email"` | Sluice tagline; would also catch any clone. |
| `http.html:"safety layer for"` `http.html:"agent"` `http.html:"email"` | Conjunctive thematic search for similar pitches. |
| `product:"Haraka"` `port:587` | Haraka MTAs at scale; useful seed list. Cross-reference with TLS cert org field. |

---

## Population estimate

| Class | Estimated public instances | Source |
|---|---|---|
| MTA-layer outbound guardrails (Sluice-class) | **1 confirmed** (Sluice); category is emerging | this survey |
| API-layer outbound guardrails | unknown; SaaS, indirect | category-adjacent §24 |
| General Haraka MTAs (broad seed) | several thousand | Shodan `product:"Haraka"` |

The category is **net-new as of 2026-06-06** for NuClide. Sluice is platform 1.

---

## Codified Insight Candidate

★ **Insight (candidate, pending number):** Docker Compose project leak via Haraka default EHLO greeting. Haraka's stock greeting is "Nice to meet you, $HELO". When the operator's `HELO` is left at the container hostname, EHLO leaks `<service-name>-1.<compose-project>_<network>`: exposing both the Compose project name (operator's internal product name) and the service name. Useful for cert-pivot and operator attribution. Mitigation: set Haraka `host_list` or `outbound.local_hostname` to a public-facing identity. The same class of leak likely exists for Postfix `mydestination` defaults and Exim banner default.

---

## See also

- Platform JSON: [`tome/platforms/sluice.json`](../../../tome/platforms/sluice.json)
- aimap fingerprint: `~/ai-recon/aimap/fingerprints.go` ("Sluice" entry, added 2026-06-06 v1.9.53-pending)
- Adjacent category: [§24 LLM Safety / Guardrails / Policy](24-llm-safety-guardrail-policy.md)
- Inbound counterpart: classic AI-for-email-security (Abnormal, Sublime, Material): not in NuClide scope, all SaaS-only


---

## Lane B platoon additions (2026-06-07)

Three-lane Phase 3B dispatch. Lane B covers API-gateway / bearer-token guardrails. New platform JSONs written to `~/tome/`: lakera-guard, prompt-security, aegisai. Sluice already owned by Lane A; not duplicated. Salus YC W2026 vendor unreachable: salus-ai.com resolves to an unrelated Italian medication-management product (Salus AI by Designed for Life), MX = Outlook. Lane C/D platoons should not assume salus-ai.com is the YC vendor apex; the correct apex is not yet identified.

### Lakera Guard

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl:"lakera.ai"` | Cert-based vendor-surface enumeration. |
| strict | `ssl.cert.subject.cn:"api.lakera.ai"` | Production API edge only. |
| version | `http.html:"Lakera Guard"` | Marketing-string detection on platform pages. |

Marker probe: `POST https://api.lakera.ai/v1/guard` with empty JSON returns HTTP 400 with body containing `docs.lakera.ai/docs/api`. That literal IS the fingerprint anchor. Population pivots: 4-region API edge (eu-west-1, us-east-1, us-west-2, ap-southeast-1), each with `-internal` AWS-private siblings; LiteLLM in path at litellm-eu / litellm-us.

### Prompt Security

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl:"prompt.security"` | Cert-based vendor surface (BYOS deployments included). |
| strict | `ssl.cert.subject.cn:"prompt.security"` | Tighter to vendor-issued certs. |
| version | `http.html:"prompt.security" http.html:"protect"` | Marketing + endpoint co-occurrence. |

Marker probe: `GET https://eu.prompt.security/v1/protect` returns HTTP 400 with body `{"status":false,"error":"No api key provided"}`. JSON shape + literal error string IS the fingerprint anchor. Pivot population: 8 region subdomains (eu, eunorth, us-east, apac, apnortheast, apsouth, amxuseast, global) plus BYOS-pattern `byos-<customer>.prompt.security`. Dev cluster surfaces named engineers (yoav-ps.dev, ofek-ps.dev) on 10.66.x.x private space via public DNS: operator OSINT only.

### AegisAI

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl:"aegisai.ai"` | Cert-based surface (CF-fronted SaaS). |
| strict | `http.title:"Aegis AI Console"` | Branded console page literal. |
| version | `http.html:"aegisai" http.html:"Aegis"` | Marketing-string co-occurrence. |

Marker probe: `GET https://console.aegisai.ai/` returns HTML with `<title>Aegis AI Console</title>`. Vendor self-labels as outbound AI-email security; primary-source DNS posture (Google Workspace MX, console-first product surface) refutes: AegisAI is INBOUND. Re-classify in Cat-33 lane taxonomy as misclassified. demo.aegisai.ai gated by GCP IAP (302 `Invalid IAP credentials: empty token`). Staging subdomains expose Langfuse + an internal "phishhook" product.

### Cross-lane dedup notes

- Sluice: Lane A owns the platform JSON. Lane B mode (same API, MTA underneath) does not produce a separate JSON. Pointer in `~/tome/platforms/sluice.json`.
- Salus: Lane B + Lane C overlap. Apex unresolved on this lane. Hand to Lane C platoon: do not assume salus-ai.com is correct; query YC W2026 directory or Crunchbase to resolve the actual product apex before any probe.

### Marker probe insight candidate

The Lakera Guard `POST /v1/guard` and Prompt Security `GET /v1/protect` both return a distinctive error message at HTTP 400 without authentication. This is a deliberate vendor design choice: the API leaks its own identity to support customer integration debugging, while denying any oracle behavior. The error-string-as-banner is the cheap-fingerprint surface for the entire API-gateway guardrail lane. Hypothesis to confirm against a third vendor: the lane has a structural fingerprint pattern, not just per-vendor markers. Pending confirmation as Insight candidate (next number) after a third lane-B vendor probe lands.

---

## Lane D platoon additions (2026-06-07): SDK / Wrapper guardrails (OSS-heavy)

Lane D targets are mostly OSS frameworks. The dorks below select the DEPLOYMENT side (operators running the OSS publicly), not the FRAMEWORK adoption (operators using it in-process). Population-substitution risk is high; noted per target. Names ARE the finding -- no record reads. Tome platform JSONs written: `~/tome/platforms/llamafirewall.json`, `openguardrails.json`, `invariant-gateway.json`. LiteLLM JSON pre-existed; Lane D mode is a delta noted in the summary, not a re-survey of Cat-05.

### LlamaFirewall (Meta OSS)

Framework, not service. No native network port. Only deployment-mode dorks are useful.

| Tier | Shodan Query | Hit count (2026-06-07) | Notes |
|---|---|---|---|
| basic | `http.html:"LlamaFirewall"` | pending | Catches any wrapper UI / docs mirror; high false-positive (any page citing the paper) |
| strict | `http.html:"LlamaFirewall" "PromptGuard"` | pending | Conjunctive; selects deployments that surface scanner names |
| version | `http.html:"llamafirewall" http.html:"AlignmentCheck" http.html:"CodeShield"` | pending | All three scanner names present -> high-confidence deployment |

Population substitution: operators self-select. The framework is a Python import; visible deployments are a thin-wrapper minority that already invested in shipping it as a service.

### OpenGuardrails

Framework AND deployment (docker-compose ships a public-facing platform with admin UI). Distinctive ports.

| Tier | Shodan Query | Hit count (2026-06-07) | Notes |
|---|---|---|---|
| basic | `http.html:"OpenGuardrails"` | pending | Brand string in landing/admin UI |
| strict | `http.html:"Zero Trust Firewall for AI Agents"` | pending | Tagline; high specificity |
| version | `http.html:"openguardrails-platform" port:54321 product:"PostgreSQL"` | pending | Compose default Postgres host-mapping leaks |
| pivot | `tcp.port:58002 "vllm"` | pending | vLLM serving OpenGuardrails-Text-2510 |

Population substitution HIGH. Brand dork selects operators who exposed the frontend; port-54321 dork selects operators who left compose defaults. Different subsets that overlap but are not the same.

### Invariant Gateway

Self-hosted exposes 8005:8000. SaaS variant (explorer.invariantlabs.ai) is cert-pivot-only.

| Tier | Shodan Query | Hit count (2026-06-07) | Notes |
|---|---|---|---|
| basic | `http.html:"Invariant Gateway"` | pending | Brand string |
| strict | `port:8005 http.html:"invariant"` | pending | Self-hosted compose port |
| version | `http.html:"/api/v1/gateway/"` | pending | Distinctive URL prefix |
| pivot-cert | `ssl.cert.subject.cn:"explorer.invariantlabs.ai"` | pending | SaaS users via cert SAN |

Population substitution MEDIUM-HIGH. Self-hosted operators self-select for data-residency rigor; not representative of SaaS-users.

### LiteLLM (policy-mode delta, NOT a re-survey)

Covered as Cat-05 inference gateway. Tome at `~/tome/platforms/litellm.json`. **Lane D delta:** the same proxy, when configured with `guardrails:` in `config.yaml` or via `/guardrails/*` endpoints (registry at `litellm/proxy/guardrails/guardrail_hooks/`), becomes a Lane D wrapper. The Shodan fingerprint does NOT change (still :4000 + `/health/liveliness` + `litellm_version`). What changes is which `guardrail_hooks` are loaded -- invisible to passive enumeration. The hooks directory itself maps the entire Lane D vendor ecosystem in one place: aim, akto, aporia_ai, azure, bedrock, cato_networks, crowdstrike_aidr, custom_code, dynamoai, enkryptai, grayswan, guardrails_ai, hiddenlayer, ibm_guardrails, javelin, lakera_ai (v1+v2), lasso, llm_as_a_judge, mcp_jwt_signer, mcp_security, microsoft_purview, model_armor, noma, onyx, pangea, panw_prisma_airs, pillar, presidio, prompt_security, promptguard, qohash, qualifire, rubrik, semantic_guard, vigil_guard, xecguard, zscaler_ai_guard.

| Tier | Shodan Query (Lane D refinement) | Hit count (2026-06-07) | Notes |
|---|---|---|---|
| pivot | `port:4000 "litellm_version"` cross-reference active `/guardrails/list` | pending | Active probe required to distinguish gateway-mode from guardrail-wrapper-mode |
| CVE | CVE-2026-40217 affects `/guardrails/tests` endpoint -- custom-code sandbox-escape | n/a | The guardrail USER is the attacker; affects 1.74.x to 2026-04-08 |

Population substitution: LiteLLM dork measures gateway population. Lane D subpopulation (guardrail-mode operators) is invisible without active `/guardrails/list` probe.

### Cascade and Galini (skipped per brief)

- **Cascade (cascade.dev)** -- domain returns an unrelated AmazonS3-hosted 1.2KB landing page (verified 2026-06-07 HTTP 200, content-length 1263, x-amz-server-side-encryption set). No relation to a YC W2026 guardrails-and-testing company. Stealth or pivoted. **Skipped.**
- **Galini (galini.ai)** -- parent brief line 286 reclassifies as a **consulting firm**, not a product. Removed. **Skipped.**

### Codified observation -- Lane D dork-population-substitution pattern (Insight candidate)

All four covered frameworks share a structural property: **the dork that selects the framework name selects only the operators who chose to make their deployment publicly visible**. Operators using the same framework as an in-process library are invisible. This is the dork-population-substitution risk (reference-dork-population-substitution) applied to the OSS-framework class. Conclusions about adoption based on dork counts are biased by deployment-style self-selection. Treat hit counts as "publicly-visible-wrapper operators," not "framework users." Insight candidate: the OSS-framework dork population is structurally a different population than the OSS-framework user population, by a self-selection mechanism that biases toward operators who already invested in shipping it as a service.

---

## 5. Lane C platoon -- Inbox Agent / Workspace addon middleware (2026-06-07)

Targets: Clawvisor (clawvisor.com, YC 2026 OSS), Alter (alterauth.com / alterai.dev marketing, YC W2026), Salus (usesalus.ai, YC W2026 -- apex correction). Lane C vendor summary: `data/platform-intel/cat33-lane-c-vendors-2026-06-07.md`. Tome JSONs: `tome/platforms/clawvisor.json`, `tome/platforms/alter.json`, `tome/platforms/salus.json`.

### Clawvisor

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl.cert.subject.cn:"clawvisor.com"` | Cert-SAN anchor. |
| strict | `ssl.cert.subject.cn:"clawvisor.com" http.html:"AI Agent Gatekeeper"` | Conjunctive brand + tagline. |
| version | `http.html:"AI Agent Gatekeeper" http.html:"Policy-based access control"` | Tagline-only (any CN). |
| self-host | `port:25297 http.title:"Clawvisor"` | OSS self-host default port (server.port=25297 per config.example.yaml). Matches the operator-warning case -- agents and the gateway sharing a host, internet-exposed. |
| favicon | TBD (pivot pending) | Logo at clawvisor.com web/public/favicon.svg. |

### Alter

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl.cert.subject.cn:"alterauth.com"` | Real product apex. |
| alt | `ssl.cert.subject.cn:"alterai.dev"` | Marketing apex. |
| strict | `ssl.cert.subject.cn:"alterauth.com" http.html:"Alter Vault"` | Conjunctive cert + brand. |
| version | `http.html:"Alter Vault" http.html:"Authorization Layer for AI Agents"` | Tagline anchor. |

### Salus (Lane C absent -- listed for completeness)

| Tier | Dork | Notes |
|---|---|---|
| basic | `ssl.cert.subject.cn:"usesalus.ai"` | Cert-SAN anchor. Apex corrected from salus-ai.com (Italian medication product, refuted by Lane B). |
| strict | `ssl.cert.subject.cn:"usesalus.ai" http.html:"A runtime for agents"` | Conjunctive cert + brand. |
| version | `http.html:"identity.ambiguous_caller" http.html:"Vol. XXI"` | Newspaper-style typography + policy-tag string anchor (the brand "Salus" alone is generic). |

### Lane C population-shape note

None of the three vendors publish a Google Workspace Marketplace or Microsoft AppSource listing detectable via passive scrape (Marketplace SPA hydrates client-side). The Lane C integration shape in this cohort is **per-operator OAuth client registration**, not Marketplace addon. The Workspace-Marketplace dork population is therefore **empty** for this lane -- the right population is cert-SAN + tagline on the vendor's own apex.

### Lane C OAuth scope manifest summary (the actual finding for this lane)

Discipline: scope manifests READ, not exercised. Names ARE the finding.

| Vendor | Gmail scopes requested | MS Graph scopes requested |
|---|---|---|
| Clawvisor | gmail.readonly, gmail.send, gmail.modify, userinfo.email, userinfo.profile | Mail.Read, Mail.Send, Calendars.ReadWrite, Files.ReadWrite, offline_access |
| Alter | gmail.readonly, gmail.send, gmail.compose, gmail.modify (catalog; operator-selectable) | Mail.Read, Mail.Send, Calendars.Read/ReadWrite, Files.Read/ReadWrite, offline_access (catalog) |
| Salus | n/a (no Workspace integration; product is tool-call proxy) | n/a |

**Restricted-scope finding:** Both Clawvisor and Alter request `gmail.modify`, a Google-classified RESTRICTED scope requiring CASA (Cloud Application Security Assessment) for production. Self-hosted Clawvisor deployments push CASA onto the operator's own GCP project; hosted Clawvisor and Alter carry CASA themselves.

**Microsoft scope finding:** Both expose `Mail.Send + Calendars.ReadWrite + Files.ReadWrite + offline_access` together under a single consent. `offline_access` enables long-lived refresh tokens; if the vendor's credential vault is compromised, refresh tokens permit attacker re-authentication until tenant admin revokes.

### Codified Insight #79 candidate -- Lane C-Cat-33 architecture: per-operator OAuth client, not Marketplace addon

For the AI-agent-authorization-gateway product class in 2026, the operative integration shape is **per-operator OAuth client registration in the customer's own GCP / Azure AD tenant**, not a Workspace Marketplace / AppSource addon. The Lane C platoon found zero detectable Marketplace listings across three target vendors (Clawvisor, Alter, Salus). Verifying this pattern requires:

1. The vendor publishes a docs page titled "Google OAuth Setup" / "Azure AD Setup" walking the operator through their own Cloud Console -- which is exactly what Clawvisor (docs/GOOGLE_OAUTH_SETUP.md) and Alter (reference/oauth-providers/google.mdx) ship.
2. The vendor exposes a scope **catalog** that operators select from per integration, not a fixed addon scope set. Clawvisor ships scope sets per adapter; Alter ships a selectable scope set per provider.

Implication for OSINT: the right Lane C dork is cert-SAN on the vendor apex, not Marketplace search. The threat-model surface is the **published scope catalog**, not a Marketplace install count. Confidence: medium (N=3 vendors); track against the next Lane C cohort that emerges.

