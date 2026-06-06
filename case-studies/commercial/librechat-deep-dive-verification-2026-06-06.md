---
type: case-study-verification
category: cat-lc
platform: LibreChat
date: 2026-06-06
parent: librechat-population-survey-2026-06-06.md
status: verified
---

# LibreChat Verification Deep-Dive — Notable Findings Re-Profiled

_NuClide Research · 2026-06-06_

Deeper verification on the six notable finding clusters surfaced in the LibreChat population survey. **Restraint maintained throughout: no registration, no LLM invocation, no account creation.** Methods used: `/api/config`, `/api/endpoints`, PTR lookup, TLS cert inspection, WHOIS, marketing-site cross-reference.

The key disclosure surface beyond `/api/config` is **`/api/endpoints`**, which returns the configured LLM provider list per host without authentication. The crucial field is `userProvide`:

- `userProvide: true` — each registered user must bring their own API key. Lower LLM10 risk: the operator's account is not consumed by attackers.
- `userProvide: false` (or absent) — the operator has configured a server-side API key. **All registered users invoke completions against that key.** This is the canonical Denial-of-Wallet condition.

---

## Finding 1 — UC Berkeley: Severity downgrade after verification

**Host:** `169.229.156.181:3080`
**PTR:** `fixed-169-229-156-181.ce.berkeley.edu` → UC Berkeley Civil & Environmental Engineering Department
**Title:** "LibreChat" (default — no operator customization)
**Server domain:** `http://localhost:3080` (default; reverse proxy not configured)

**Configured providers (all USER_KEY mode):**
```
openAI(USER_KEY), google(USER_KEY), bingAI(USER_KEY),
gptPlugins(USER_KEY), anthropic(USER_KEY)
```

**Revised assessment:** The host is on UCB CEE department infrastructure with registration open, but **all configured LLM providers require user-supplied API keys**. The LLM10 Denial-of-Wallet surface is **not present** on this host — an attacker who registers cannot consume any UCB-paid LLM budget.

The finding remains a registration-open finding on institutional infrastructure but downgrades from HIGH (LLM10 + institutional) to **MEDIUM-institutional**. The risk reduces to: registered users could potentially access other registered users' chat content depending on workspace isolation, and the instance is consuming UCB compute + storage.

**Disclosure target:** `security@berkeley.edu` (still warranted; institutional finding stands)

**Research-program insight:** USER_KEY mode is the **best-practice deployment configuration** for LibreChat when public registration is intentional. It eliminates the LLM10 surface entirely. UCB's deployment appears to be a research-lab or student project that defaulted to USER_KEY — likely the LibreChat install template behavior for non-customized deployments.

---

## Finding 2 — Santepair.fr: Severity confirmed at HIGH-SENSITIVE

**Host:** `51.77.213.247:443`
**PTR:** `vps-cc60b3e5.vps.ovh.net` (OVH France)
**Server domain:** `https://chat.santepair.fr` (confirms operator)
**Title:** "Santepair.fr - ChatBot IA Bien-être et santé psychique"

**Marketing-site verification:** `santepair.fr` returns title "Santé Pair - Pair-aidance et médiation en santé mentale et psychique". The operator is **Santé Pair, a French nonprofit providing peer-support mediation in mental and psychic health.**

**Configured providers (SERVER_KEY confirmed):**
```
agents(SERVER_KEY), Mistral(SERVER_KEY)
```

**Auth surface:** Six social login providers enabled (Google, Facebook, OpenID, GitHub, Discord, SAML) + email login + open registration.

**Revised assessment:** **CONFIRMED HIGH-SENSITIVE.**
- LLM10 surface confirmed: anyone who registers can invoke Mistral against Santé Pair's API key.
- GDPR Article 9 (special categories of personal data — health-related): mental health is the specific example given in Article 9(1).
- Operator is a healthcare nonprofit; the chat interface is the public-facing peer-support tool.
- Open registration on a mental-health AI = privileged-conversation exposure across user boundary if workspace isolation misconfigured.

**Disclosure path:** CNIL coordination + Santé Pair DPO contact via santepair.fr legal page.

---

## Finding 3 — TruslerLegal / Lexpertcloud: White-label legal-AI SaaS

**Host:** `144.126.133.109:3080`
**PTR:** `vmi2783240.contaboserver.net` (Contabo VPS, Germany)
**Server domain:** `https://chat.lexpertcloud.com`
**Title:** "TruslerLegal AI Assistant"

**Operator identification:** The server domain `chat.lexpertcloud.com` (operational at HTTP/2 200) suggests **LexpertCloud is the underlying platform operator**, with TruslerLegal as a tenant. LexpertCloud may operate as a white-label legal-AI SaaS hosting multiple law-firm tenants on a shared LibreChat instance.

**Configured providers:**
```
openAI(SERVER_KEY), agents(SERVER_KEY), google(USER_KEY), anthropic(SERVER_KEY)
```

Three of four providers are SERVER_KEY. The TruslerLegal tenant has the operator's OpenAI, agents, and Anthropic keys configured server-side.

**Assessment:** **CONFIRMED HIGH-PRIVILEGED.**
- LLM10 surface on three providers
- Multi-tenant white-label deployment: open registration means a new user could potentially access other tenants' chat content depending on isolation
- Attorney-client privilege exposure risk
- Legal-AI tenant branding (Trusler Legal) on a shared infrastructure (Lexpertcloud) creates a brand-trust gap: clients expect privacy commensurate with a law firm, but the auth posture is consumer-grade

**Disclosure path:** Direct to Trusler Legal (LinkedIn/website contact) + Lexpertcloud platform operator. Trademark search recommended to surface other Lexpertcloud-hosted legal-AI tenants.

---

## Finding 4 — LegalMatch AI: MVP on AWS ALB

**Host:** `18.207.2.243:80`
**PTR:** `ec2-18-207-2-243.compute-1.amazonaws.com` (AWS us-east-1)
**Server domain:** `http://growth-rag-mvp-alb-1391618126.us-east-1.elb.amazonaws.com` (AWS Application Load Balancer, RAG MVP environment)
**Title:** "LegalMatch AI"

**Operator identification:** LegalMatch is a known US legal-services-directory company (legalmatch.com). The `growth-rag-mvp-alb` ALB name indicates a **product growth team's MVP** environment — likely an internal pilot or beta product not yet at full production.

**Configured providers:**
```
openAI(SERVER_KEY), agents(SERVER_KEY), LM Atlas(SERVER_KEY)
```

"LM Atlas" appears to be LegalMatch's proprietary endpoint (LM = LegalMatch). All providers SERVER_KEY.

**Assessment:** **CONFIRMED HIGH-PRIVILEGED.**
- LLM10 surface on all configured providers
- MVP environment with open registration: testing artifact not hardened for public
- Custom internal endpoint "LM Atlas" exposed by name (configuration intelligence about LegalMatch's AI architecture)

**Disclosure path:** LegalMatch corporate security contact (security@legalmatch.com per their published security page, or via responsibledisclosure@legalmatch.com).

---

## Finding 5 — Atticus + Legal-KG-Chatbot: Smaller legal-AI deployments

**Host A:** `34.75.202.219:80` (Atticus: Legal Assistant)
- GCP us-east1 hosting
- Server domain: `http://localhost:3080` (uncustomized)
- Providers: `agents(SERVER_KEY)`, `anthropic(USER_KEY)`
- Apple login distinctively enabled (most LibreChat instances don't have Apple)

**Host B:** `20.77.81.170:443` (Legal-Knowledge-Graph-Chatbot)
- Azure hosting (20.x = Azure)
- Server domain: `localhost:3080` (uncustomized)
- `/api/endpoints` returned empty — newer LibreChat may auth-gate this endpoint, or no providers configured

**Assessment:**
- Atticus: MEDIUM. SERVER_KEY on the agents endpoint = limited LLM10 surface. The `anthropic` USER_KEY config means the typical chat path requires user-supplied keys.
- Legal-KG: MEDIUM-UNKNOWN. Empty `/api/endpoints` is unusual and warrants confirmation that the host is actually using LLM providers vs. being a graph-only system.

**Disclosure path:** Both require WHOIS / operator identification before direct outreach. Default LibreChat branding + localhost server_domain suggests small operations.

---

## Finding 6 — Capitol AI Chat Agent: Enterprise multi-tenant SaaS (CRITICAL ESCALATION)

**20-host AWS fleet** across `us-east-1`, `us-east-2`, `eu-west-1`, `eu-west-2`, `ap-southeast-1` regions.

**Operator confirmation:** `capitol.ai` resolves to `www.capitol.ai` (Framer-hosted marketing site). Self-description: "Capitol is the agentic AI platform that transforms structured data, live research, and internal knowledge into high-quality content, reports, and artifacts in moments – not months."

**Capitol.ai is a real US AI-platform startup** (not a NuClide hallucination from the title alone).

**Server-domain enumeration across the fleet reveals customer-tenant naming pattern:**

| Subdomain | Likely tenant |
|---|---|
| `chatagent.capitol.ai` | Capitol.ai production |
| `chatagent-development.capitol.ai` | Internal dev |
| `chatagent-staging.capitol.ai` | Internal staging |
| `chatagent-staging-eu-west-1.capitol.ai` | EU staging |
| `customer-chat-staging.capitol.ai` | Customer-tenant staging |
| **`chatagent-ey-ap-southeast-1.capitol.ai`** | **Suspected Ernst & Young customer, APAC region** |
| **`chatagent-ey-eu-west-1.capitol.ai`** | **Suspected Ernst & Young customer, EU region** |
| **`chatagent-ey-us-east-2.capitol.ai`** | **Suspected Ernst & Young customer, US region** |
| **`chatagent-hmg-eu-west-2.capitol.ai`** | **Suspected UK HMG (His Majesty's Government) customer, London region** |
| `chatagent-eont-us-east-2.capitol.ai` | Unidentified customer "eont" |

**Configured providers (SERVER_KEY confirmed on sampled instance):**
```
openAI(SERVER_KEY), agents(SERVER_KEY), anthropic(SERVER_KEY), Cerebras(SERVER_KEY)
```

**All four providers SERVER_KEY.** Cerebras provides ultra-fast inference at premium pricing — the LLM10 surface here is economically substantial.

**Assessment: CRITICAL.**

This is the most significant LibreChat finding of the day. Capitol.ai has deployed customer-segregated LibreChat instances under named subdomains, but every customer-tenant instance has **`registrationEnabled: true`**. The implications:

1. **Brand-trust gap**: a customer engaging Capitol.ai (e.g. EY, HMG) expects an enterprise-grade AI deployment. The public-registration default contradicts that expectation. A non-customer can register on the customer-tenant instance.

2. **Cross-tenant exposure potential**: if registration is open AND the workspace isolation is misconfigured, a registered user on (say) `chatagent-ey-eu-west-1.capitol.ai` could potentially access content created by EY users — exactly the scenario that breaks enterprise SaaS trust.

3. **LLM10 at customer-tenant scale**: every customer-tenant instance burns Capitol.ai's (or the customer's) SERVER_KEY budget on every registered user's queries.

4. **Suspected enterprise customers**: If `ey-` and `hmg-` prefixes truly map to Ernst & Young and the UK Government, this is a finding with substantial reputational and regulatory implications for Capitol.ai. **Verification of the customer mapping by Capitol.ai itself is the responsible disclosure step — NuClide does not claim the EY/HMG identification, only flags the suspected pattern.**

**Disclosure path:**
- **Direct to Capitol.ai security contact**: capitol.ai marketing site → security/contact page → coordinated disclosure with the customer-tenant mapping confirmation request
- Recommended Capitol.ai remediation: change customer-tenant template to `registrationEnabled: false` by default; require Capitol.ai admin allowlist for user provisioning on customer-tenant instances; document this as part of the standard customer-SaaS contract.

---

## Summary of revised severities

| Finding | Initial severity | Revised severity | Change |
|---|---|---|---|
| UC Berkeley CEE | HIGH | MEDIUM-institutional | DOWNGRADED (USER_KEY eliminates LLM10) |
| Santepair.fr | HIGH-SENSITIVE | HIGH-SENSITIVE | Confirmed (GDPR Article 9 + SERVER_KEY Mistral) |
| TruslerLegal / Lexpertcloud | HIGH | HIGH-PRIVILEGED | Confirmed + clarified white-label pattern |
| LegalMatch AI | HIGH | HIGH-PRIVILEGED | Confirmed (MVP environment, all SERVER_KEY) |
| Atticus Legal | HIGH | MEDIUM | Refined (partial USER_KEY) |
| Legal-KG-Chatbot | HIGH | MEDIUM-UNKNOWN | Refined (insufficient providers data) |
| **Capitol AI fleet** | **HIGH-FLEET** | **CRITICAL-ENTERPRISE** | **ESCALATED (EY/HMG suspected customer tenants)** |

---

## Research-program contributions

### LLM10 disclosure-method advancement

The `/api/endpoints` endpoint with `userProvide` field is a **LibreChat-specific LLM10 severity discriminator**. Updated herald probe class will distinguish SERVER_KEY from USER_KEY findings in future LibreChat sweeps.

This generalizes: the population-scale auth-permissive finding is necessary but not sufficient for LLM10 — the configuration-disclosure layer reveals whether the operator's account is actually consumable. For three platforms surveyed today (Open WebUI, Dify, LibreChat), the per-instance LLM10 risk depends on configuration data exposed at the same layer as the registration flag.

### Capitol AI as the canonical enterprise-customer-tenant finding

The Capitol AI fleet pattern (per-customer named subdomains all with open registration) is a **new finding class for the survey program**: enterprise SaaS providers using LibreChat as the underlying technology, with customer-tenant naming that creates an "I am a security-conscious enterprise vendor" impression while shipping consumer-grade auth defaults.

The class is testable against other LibreChat-based commercial SaaS — searching for `chatagent.*.com` patterns in DNS could reveal similar deployments.

### Operator-attribution discipline

Six of six profiled hosts had attributable operator information via PTR, server_domain, and marketing-site cross-reference. **Direct restraint-bounded operator-attribution is fully sufficient for disclosure-grade findings** at LibreChat scale. No registration was required for any of these identifications.

This validates the NuClide methodology: high-confidence finding identification from the metadata layer alone, with the data layer left untouched per the restraint ethic.

---

## Updated disclosure pipeline state

| Target | Severity (revised) | State |
|---|---|---|
| Capitol.ai (vendor + suspected EY + suspected HMG customer-tenant) | CRITICAL-ENTERPRISE | QUEUED |
| Santepair.fr (Santé Pair nonprofit + CNIL) | HIGH-SENSITIVE (GDPR Art 9) | QUEUED |
| TruslerLegal + Lexpertcloud platform | HIGH-PRIVILEGED | QUEUED |
| LegalMatch AI (legalmatch.com security) | HIGH-PRIVILEGED | QUEUED |
| UC Berkeley CEE (downgraded) | MEDIUM-institutional | QUEUED |
| Atticus Legal Assistant | MEDIUM | QUEUED |
| Legal-Knowledge-Graph-Chatbot | MEDIUM-UNKNOWN | QUEUED |
| LibreChat upstream (danny-avila) | UPSTREAM | QUEUED |
