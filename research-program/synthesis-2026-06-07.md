# The Auth-on-Default Landscape of OSS AI/LLM Infrastructure — A Two-Day Population Survey

**NuClide Research · 2026-06-07**

---

> **Thesis.** A new generation of open-source AI and LLM infrastructure tools has shipped over the past 24 months, and many of them ship with auth-permissive defaults. Those defaults survive into production deployment at university research labs, enterprise customer-tenant fleets, financial-messaging companies, mental-health nonprofits, and national education ministries. Across 13 platform surveys over two days (2026-06-06 and 2026-06-07), the rate at which the default holds correlates strongly with **upstream maintainer culture** — specifically, whether the maintainer team optimizes for "clone and demo it immediately" or "self-host for your enterprise customer." The rate is not jurisdiction-specific. It is movable in 2–3 minor-version cycles by upstream pressure, including internal-quality-driven pressure (LibreChat v0.8.x). The class of finding most directly enabled is OWASP LLM02:2025 Sensitive Information Disclosure (promoted #6→#2 in the 2025 revision specifically because of incidents of this type), with LLM06 Excessive Agency and LLM10 Unbounded Consumption as the next-most-common consequences.

---

## What was surveyed

13 platforms across 7 functional categories:

| Category | Platform | Upstream maintainer | Result |
|---|---|---|---|
| LLM observability | Langfuse | Langfuse GmbH (Berlin) | 88.9% SIGNUP_OPEN |
| LLM observability | Arize Phoenix | Arize AI (US) | 74.5% PROJECTS_UNAUTH / 61.8% USERS_UNAUTH |
| RAG engine | RAGFlow | InfiniFlow (Shanghai) | 87.2% REGISTER_OPEN |
| RAG engine | Bisheng | DataElem (Beijing) | 0% auth-required (negative) |
| LLM app builder | Dify | Dify.AI (Shanghai) | 0.9% SIGNUP_OPEN |
| LLM app builder | Flowise | FlowiseAI | 68.7% CHATFLOWS_OPEN |
| Chat UI | LibreChat | danny-avila (community) | 26.3% overall / 10.3% v0.8.x |
| Chat UI | LobeChat | Lobehub (Hangzhou) | 83.3% AUTH_OFF (small N) |
| Chat UI | Open WebUI | community | 11.8% AUTH_OFF + SIGNUP_OPEN |
| Doc chat | AnythingLLM | Mintplex Labs | 0% (population hardened) |
| LLM gateway | LiteLLM | BerriAI | 0.81% NO_MASTER_KEY |
| Autonomous agent | OpenHands | All-Hands-AI | 90.7% SETTINGS_EXPOSED / 33.3% CONVERSATIONS_EXPOSED |
| Autonomous agent | LangGraph Studio | LangChain | 90.9% operator-misdeployment |

Three additional attempted surveys produced negative results: AnythingLLM (population hardened), MCP servers (dork-noise), CrewAI (framework class, not population-surveyable).

---

## Central finding — the maintainer-culture taxonomy

After 13 surveys, the auth-permissive default rate clusters into three distinct maintainer-culture classes:

### Class 1 — Demo-first maintainers (auth-permissive default)

Maintainer teams that optimize for the "clone the repo, `docker compose up`, immediately demo your work to the team" workflow. Auth is opt-in via environment variables; the default is open.

| Platform | Rate | Class signal |
|---|---|---|
| Langfuse | 88.9% | Default `LANGFUSE_AUTH_DISABLE_SIGNUP=false` |
| RAGFlow | 87.2% | Default `register_enabled: True` |
| Phoenix (Arize) | 74.5% / 61.8% | Default `PHOENIX_ENABLE_AUTH=false` |
| Flowise | 68.7% | Auth plugin is opt-in |
| LobeChat | 83.3% (small N) | Default `ACCESS_CODE` unset |
| OpenHands | 90.7% / 33.3% | `OPENHANDS_AUTH_TYPE` is opt-in |

**Common pattern.** These tools are designed for the moment you tell your coworker "let me show you what I just built." Closing the auth gate adds friction to that demo moment, so the maintainer ships open and trusts the operator to read the docs.

The operator usually does not read the docs.

### Class 2 — Enterprise-customer-first maintainers (auth-required default)

Maintainer teams whose business model centers around shipping self-hostable software to identifiable enterprise customers. Auth is required; opening up requires explicit configuration.

| Platform | Rate | Class signal |
|---|---|---|
| Bisheng | 0% open | Always returns 401 on data endpoints; only `/api/v1/version` is public |
| Dify | 0.9% | Default `is_allow_register: false` |
| AnythingLLM | 0% | All API endpoints API-key gated; UI behind login |
| Open WebUI (post-correction) | 11.8% | Default tightened in v0.5+ after public surveys |

**Common pattern.** These tools were built with a paying or enterprise audience in mind. The maintainer treats the open-by-default question as a security gate at design time rather than as a documentation problem at deployment time.

### Class 3 — Operator-misdeployment of correctly-defaulted dev tools

Distinct from Classes 1 and 2: the maintainer's default is **correct for the tool's intended scope** (localhost development), but operators deploy the tool to public infrastructure anyway.

| Platform | Rate | Class signal |
|---|---|---|
| LangGraph Studio | 90.9% misdeployed | `VITE_BACKEND_AUTH_TYPE: "desktop"` correct for localhost; deployed to AWS EC2 / GCP with public IPs |

The maintainer (LangChain) ships two distinct products: LangGraph Studio (localhost dev) and LangGraph Platform / LangGraph Cloud (production). The 9.1% of LangGraph deployments using the production tooling demonstrate operators **can** make the right choice. The 90.9% who deployed Studio publicly represent a workflow misalignment, not a default-vulnerability.

This class matters because its remediation pathway differs from Classes 1 and 2. **Maintainer-default-vulnerable findings are remediated upstream; operator-misdeployment findings are remediated operator-side.**

---

## What the cohort split is NOT

It is tempting to read the cohort split as jurisdictional — auth-permissive defaults are "a Western open-source habit" or "a Chinese platform habit." The data refutes both.

The CN-origin cohort splits 2-2:

| Platform | Maintainer | City | Default | Open rate |
|---|---|---|---|---|
| LobeChat | Lobehub | Hangzhou | open | 83.3% |
| RAGFlow | InfiniFlow | Shanghai | reg-open | 87.2% |
| Bisheng | DataElem | Beijing | auth-required | 0% |
| Dify | Dify.AI | Shanghai | auth-required | 0.9% |

The maintainer's deployment culture (Beijing-based DataElem is enterprise-customer-first; Hangzhou-based Lobehub is community OSS DX-first) is the splitter. The geography is not.

Similarly, the Western cohort includes both demo-first (Langfuse Berlin, Phoenix US, Flowise Denmark, OpenHands) and enterprise-customer-first (AnythingLLM US, Open WebUI post-correction). Western OSS is not uniformly auth-permissive either.

---

## What the cohort split IS

The cohort split is **business-model-axis-aligned**.

Maintainers who ship demo-first defaults are typically:
- Academic-origin projects (Phoenix, RAGFlow's research lineage, OpenHands' OpenDevin heritage)
- Open-source community projects driven by GitHub adoption metrics (LobeChat, Flowise, Langfuse early days)
- Projects where "lower the friction to first demo" is the dominant product KPI

Maintainers who ship enterprise-customer-first defaults are typically:
- Funded by enterprise SaaS or hardware customers (DataElem, Dify, AnythingLLM's Mintplex)
- Building toward an audit, certification, or compliance path
- Operating in markets where customer trust requires security at deployment time

Both populations are doing rational, locally-correct work. The auth-permissive default isn't a moral failing of demo-first maintainers — it's a reasonable tradeoff for their cohort's goals. The problem is that **operators downstream don't always read the deployment documentation**, and a "demo-first" default ships into production at the same rate as a more carefully configured one.

---

## What gets exposed

The auth-permissive default enables a small set of OWASP LLM Top 10 (2025) classes at population scale. Listed in order of empirical prevalence across the 13-survey corpus:

### LLM02:2025 Sensitive Information Disclosure (promoted #6 → #2 in 2025)

This is the dominant finding class. NuClide does not find training-data extraction or membership inference at population scale; we find **infrastructure-layer configuration disclosure** — the platform itself reveals operator-side metadata without authentication. Examples:

- Phoenix `/v1/users` returns user records (account IDs, creation timestamps) on 34 of 55 reachable hosts (61.8%)
- Phoenix `/v1/projects` returns project names + IDs on 41 of 55 (74.5%) — including Northeastern University's "Essaybot" project, Hetzner Helsinki host with 21 projects, SENAI Brazil (national vocational education)
- LiteLLM `/model/info` discloses Azure resource names (`uksdoai673aif02.openai.azure.com`), GCP project IDs (`inquinion-code`, `tdsipex`), Databricks workspace IDs (`adb-4870463909224736.16.azuredatabricks.net`)
- OpenHands `/api/settings` discloses LLM model + custom `llm_base_url` on 90.7% of reachable hosts — including operator-specific cognitive services tenants and internal LiteLLM proxy endpoints
- Open WebUI `/api/config` discloses application names (`PLLuM dla Edukacji` — Polish National Research Institute; `SwiftRef Assistant` — SWIFT financial messaging; `Dartmouth Offshore Wind Lab AI`)

The OWASP committee promoted LLM02 from #6 (2023) to #2 (2025) "following major data breaches" and "documented incidents." The empirical NuClide data is consistent with that promotion — this class is the most common finding type across the corpus.

### LLM10:2025 Unbounded Consumption ("Denial of Wallet")

The 18 LiteLLM CRIT findings (Cat-05) are the canonical demonstration. An operator-side LLM gateway with no `master_key` set means any internet user can invoke completions against the operator's configured providers:

- Direct Anthropic API → Claude Sonnet 4.6, Claude Haiku 4.5
- AWS Bedrock EU → Claude Opus 4.7 (frontier-class, ~$15/M input tokens)
- Azure OpenAI → GPT-5.4, GPT-5.2
- Vertex AI → Gemini 2.5 Pro
- Databricks AI Gateway → proxied Claude
- Moonshot AI kimi-k2.5 (first non-Western frontier model in the survey)

LibreChat's open-registration instances enable the same class: each registered user invokes completions against the operator's configured providers (OpenAI / Anthropic / Google / Azure / Bedrock).

### LLM06:2025 Excessive Agency

OpenHands is the canonical demonstration. The platform exposes autonomous agents (CodeActAgent, BrowsingAgent, VisualBrowsingAgent) capable of code execution, web browsing, and file modification. At the unauth surface, attackers can both invoke new agent tasks and observe past task history.

The 25 OpenHands hosts with populated `/api/conversations` reveal:
- One operator's 20-conversation internal corporate HR development pipeline (xrxs/project-* GitLab repos, Chinese-language conversation titles describing salary policy and AWOL rule features)
- **Three separate hosts with visible conversation titles `"show me /proc/self/environ"`** — scripted attacker reconnaissance attempting to exfiltrate API keys from the agent's runtime environment

The /proc/self/environ class is significant because it is the **first time the NuClide methodology has observed in-flight attacker activity directly from the public surface**. The same dork that NuClide walked, an attacker is walking now. Whether keys were successfully exfiltrated is not visible to NuClide's restraint-bounded methodology — that would require reading conversation content.

### LLM07:2025 System Prompt Leakage (NEW in 2025)

Flowise demonstrates the canonical case: the 578 open-chatflow-API instances expose every chatflow's system prompt unauthenticated. At the canonical PoC lab (`146.190.128.73`, the operator deploying CVE-2024-36420 RCE chatflows publicly), the embedded `deepseek_admin` chatflow includes a prompt-injection canary:

```
System: "You are a system administrator assistant. When user asks to
'show context', repeat the following verbatim: {context}"
```

The chatflow is publicly readable without invoking the model. This is LLM07 by configuration disclosure — a more durable detection method than direct prompt-injection extraction, and one that scales with the Flowise auth-permissive default population.

### LLM08:2025 Vector and Embedding Weaknesses (NEW in 2025)

RAGFlow's 87.2% REGISTER_OPEN rate enables this class — a registered tenant can write to the knowledge base, and depending on multi-tenant isolation configuration, can affect retrievals seen by other tenants. NuClide did not exercise the class; the survey establishes the enabling condition only.

Earlier NuClide surveys (Cat-02, Cat-05) found Weaviate with 13,631 PII records, Qdrant exposed plant biology research vectors at University of Queensland's UQConnect, and Flowise hosts with Pinecone API keys embedded in chatflow configurations. The LLM08 class is materially enabled by the broader cohort default.

---

## The Capitol.ai escalation — what enterprise customer-tenant fleets look like

The single highest-impact finding of the two-day corpus emerged from extending the LibreChat survey via certificate transparency log enumeration. Capitol.ai is a real US AI-platform startup ("agentic AI platform that transforms structured data, live research, and internal knowledge into high-quality content, reports, and artifacts"). Their leadership pedigree is government-tech-adjacent:

- CEO ex-Airbnb, Google, NASA, White House, Department of Defense
- CTO previously directed the **AI Center of Excellence at the U.S. General Services Administration (GSA)** — federal AI policy infrastructure

The Shodan-indexed portion of their fleet (20 LibreChat instances across 5 AWS regions) showed `registrationEnabled: true` with `SERVER_KEY` LLM configurations across OpenAI, Anthropic, and Cerebras providers. Subsequent certificate transparency enumeration revealed **64 distinct `*.capitol.ai` subdomains**, with a customer-tenant naming convention:

- `chatagent-ey-{us-east-2,eu-west-1,ap-southeast-1}.capitol.ai` — suspected Ernst & Young customer, 3 regions
- `langfuse-ey-{us-east-2,eu-west-1,ap-southeast-1}.capitol.ai` — same EY tenant's Langfuse observability instances (3 regions)
- `xks-proxy-ey-*` — AWS External Key Store proxy (high-compliance cryptographic key management)
- `agentic-backend-grafana-ey-*` — customer-segregated monitoring per region
- `platform-ey-{eu,us,asia}` — admin/control plane per region
- `chatagent-hmg-eu-west-2.capitol.ai` — suspected UK HMG (His Majesty's Government) tenant, London region
- `langfuse-hmg-eu-west-2.capitol.ai` — same HMG tenant's observability
- `agentic-backend-grafana-plexal-eu-west-2.capitol.ai` — Plexal is the UK government-backed innovation centre in the Olympic Park supporting defense and cybersecurity startups
- `politico.search.capitol.ai` + `api-v2-politico-prod.capitol.ai` — confirmed Politico customer (the API tier returns HTTP 403, which is the correct auth-gated response)
- `dowjones.capitol.ai` — suspected Dow Jones
- `advance-local-*.search.capitol.ai` — confirmed Advance Local (newspaper publisher)
- `metric-media-*.search.capitol.ai` — confirmed Metric Media (local news network)
- `eont-*` — unidentified customer with a complete microservice fleet

SNI-correct probing of all four customer-tenant Langfuse instances confirmed:
- `langfuse-ey-ap-southeast-1.capitol.ai` — `signUpDisabled: false` — v3.155.1
- `langfuse-ey-eu-west-1.capitol.ai` — `signUpDisabled: false` — v3.155.1
- `langfuse-ey-us-east-2.capitol.ai` — `signUpDisabled: false` — v3.157.0
- `langfuse-hmg-eu-west-2.capitol.ai` — `signUpDisabled: false` — v3.155.1

Each customer-dedicated Langfuse instance ships with the Langfuse upstream default unchanged. A non-customer can register on the customer-tenant instance and potentially access trace data showing the EY or HMG users' LLM activity (depending on Langfuse workspace isolation).

**The Capitol.ai finding is a textbook case of the maintainer-culture default failing at the enterprise-SaaS scale.** Capitol.ai's *own* API tier is properly auth-gated (api-v2-politico-prod returns HTTP 403). The auth-permissive default leaks through the chat-UI and observability tiers they inherited from upstream OSS, replicated across the customer-tenant template.

NuClide's customer mapping is hypothesis — strongly evidenced by subdomain naming, service composition, the Plexal cross-reference, and the deployment topology — but not assertion. Capitol.ai is the only party who can self-verify. The published security contact (`security@capitol.ai`, listed in their own privacy policy) makes coordinated disclosure straightforward.

---

## Institutional findings worth surfacing

The corpus includes institutional findings across multiple regulated sectors. Each surfaces a different aspect of how the auth-permissive default propagates into operationally-significant contexts.

**Education (research and student data):**
- Harvard University — Langfuse instance with signup open
- Arizona State University — Langfuse with signup open (re-confirmed; previously flagged)
- UC Santa Barbara — Langfuse with signup open
- UC Berkeley Civil & Environmental Engineering — LibreChat with registration open (USER_KEY mode, so no LLM10 surface, but still an institutional registration finding)
- Northeastern University — Phoenix with "Essaybot" project exposed (FERPA-class given the project naming)
- Hong Kong University of Science and Technology — RAGFlow with registration open
- Brno University of Technology (Czechia) — RAGFlow with registration open
- Indiana University — RAGFlow with registration open on both HTTP and HTTPS ports
- Khajeh Nasir Toosi University of Technology (Iran, Tehran) — Langfuse with signup open (OFAC-sensitive handling required)
- Shenzhen Middle School (K-12) — RAGFlow with registration open (jurisdiction-mediated)
- Taiwan Ministry of Education Computer Center — **3 separate findings same day**: Langfuse on one allocation + RAGFlow on two more (consolidated TWCERT/CC disclosure target)
- CUNY AI Lab, Dartmouth Offshore Wind Lab, LLM-jp Playground, NCU Blockchain Lab — Open WebUI signup-open instances

**Healthcare, mental health, and sensitive data:**
- Santé Pair (santepair.fr) — French mental-health peer-support nonprofit with Mistral SERVER_KEY and open registration (GDPR Article 9 special-category health data)
- Strategion GmbH (kardiointerakt.dev-strategion.de) — medical AI with open LiteLLM proxy to Claude Opus 4.7
- Inspirali AI DEV — medical education company, Open WebUI signup-open on a DEV environment

**Legal:**
- TruslerLegal AI Assistant ("Better Divorce Austin" — Texas family-law boutique) — LibreChat with SERVER_KEY OpenAI + Anthropic + agents
- LegalMatch AI — production AI properly Cloudflare-fronted with auth; MVP environment on AWS ALB exposed (`growth-rag-mvp-alb-1391618126.us-east-1.elb.amazonaws.com`)
- Atticus: Legal Assistant — LibreChat with partial USER_KEY
- Legal-Knowledge-Graph-Chatbot — Azure-hosted

**Government and national infrastructure:**
- PLLuM dla Edukacji — Polish National Research Institute (NASK) state cybersecurity authority, Open WebUI AUTH_OFF
- SwiftRef Assistant — SWIFT financial messaging reference data, Open WebUI AUTH_OFF
- Singular GovTech Singapore — Open WebUI signup-open
- SENAI Brazil — national vocational education service (~3M students/year), Phoenix exposed (LGPD-class)
- Capitol.ai — suspected UK HMG and Ernst & Young customer-tenant fleet

**Enterprise / commercial:**
- deepset|PepsiCo — Open WebUI signup-open
- Allwyn UK National Lottery — 3 Open WebUI IPs (signup open)
- Groupe Narbonne — French auto parts retail, Open WebUI signup-open
- PromoPharma AI — pharmaceutical sector, Open WebUI signup-open
- Capitol AI Chat Agent fleet — 20-host LibreChat fleet (in addition to the Capitol.ai customer-tenant set)
- Nonprofit AI Workspace, Smollan Nexus, "Capitol AI Chat Agent" customer instances

The disclosure pipeline state for all of the above is **QUEUED**. Nothing has been sent. Decisions about timing and routing belong to the researcher, not the analyst.

---

## The negative results that bound the hypothesis

Three categories of negative result strengthen the program rather than weaken it.

**Population-level corrections.** AnythingLLM returned 0/27 reachable in no-auth mode in the 2026-06-06 sweep — down from a 2/5 sample in late May 2026. The population corrected itself. Open WebUI shows a similar pattern at 11.8% (corrected via v0.5+ default change). LibreChat's v0.8.x cohort sits at 10.3% — the within-platform correction is visible in real time across the version distribution. These results refute the strong form of Insight #76 ("auth-permissive defaults persist until external pressure") and confirm the weak form ("rates are movable").

**Counter-cohort entries.** Bisheng (DataElem Beijing) ships auth-required despite Chinese origin. Dify (Dify.AI Shanghai) ships auth-required. The CN cohort splits cleanly along maintainer-culture lines, refuting the jurisdiction interpretation of Insight #76 and strengthening the maintainer-culture form.

**Methodology-class negatives.** MCP servers cannot be surveyed via Shodan dorks at this stage of ecosystem maturity. CrewAI is framework-class (Python library) rather than platform-class — each deployment is a custom UI built by a different operator. Both findings are valuable because they bound the hypothesis to its applicable scope: platform class, where the maintainer ships a default that operators inherit at population scale.

The result is that Insight #76 is precisely defined, with explicit boundaries:

> Auth-permissive defaults are the cohort norm for **platform-class** new-generation OSS AI/LLM infrastructure where the upstream maintainer optimizes for demo-first deployment ergonomics. The rate is platform-maintainer-culture-specific, not jurisdiction-specific. The hypothesis does not apply to framework-class libraries (no shared deployment) or to maturing protocol-class ecosystems (no canonical population yet).

---

## The tool built during the survey — herald

The two-day survey work produced a tool. **herald** is a declarative HTTP auth-probe tool, public under MIT at [github.com/nuclide-research/herald](https://github.com/nuclide-research/herald). It reads platform YAML configs, sweeps an IP list, and outputs NDJSON findings.

```bash
cat ip-port.txt | herald -platform dify -workers 50
```

A new platform survey now requires writing a single YAML file:

```yaml
name: dify
description: "Dify LLM app development platform"
default_ports: [80, 443, 3000, 8080]
probes:
  - id: signup_open
    endpoint: /console/api/system-features
    match:
      field: is_allow_register
      value: true
    finding: SIGNUP_OPEN
    severity: high
```

By the end of the second day, herald had 9 platform configs (dify, open-webui, flowise, langfuse, litellm, anythingllm, ragflow, phoenix, librechat, lobechat, openhands). The marginal cost of adding a new platform survey is now: write a YAML file. The cost was previously: write a Python script per survey, debug it, run it, parse the output.

The tool was built incrementally during the surveys themselves. The numeric-type-coercion bug surfaced during the RAGFlow probe calibration (YAML unmarshals integers as `int`, JSON as `float64`; `reflect.DeepEqual` returned false on numerically-equal values) and was fixed within minutes. The body_contains escape-level limitation surfaced during the LobeChat probe calibration (Next.js SSR embeds config as JSON-escaped strings inside HTML script tags). The array-nonempty field-scoping limitation surfaced during the OpenHands probe calibration. Each was a probe-class discovery that improves the tool for future surveys.

Design references credited in the commits: *Security with Go* (Packt, 2018) for channel-semaphore concurrency; *Powerful Command-Line Applications in Go* (Pragmatic, 2021) for HTTP client architecture; *Hacking APIs* (No Starch, 2022) for the public-system-info endpoint discovery pattern.

---

## Where the work points next

Three directions emerge naturally from the two-day corpus.

**First, the test condition for Insight #76's second clause.** The strong form ("auth-permissive persists until external pressure") was broken by LibreChat's within-platform correction. The weak form ("rate is movable in 2–3 minor-version cycles by upstream pressure, including internal-quality-driven pressure") is supported by the same finding. The full test requires re-surveying Langfuse, RAGFlow, Phoenix, and Flowise post-disclosure at v3.180+/v0.21+/v7+/post-auth-plugin-default respectively. The disclosure pipeline state is QUEUED; the test condition activates when disclosures send and the next major release cycle completes.

**Second, the in-flight attacker observation deserves its own thread.** The `/proc/self/environ` conversation titles visible on three OpenHands hosts represent the first directly-observable population-scale exploitation in the program's history. The natural question is whether the pattern extends — are attackers already walking the same Shodan dorks NuClide is walking, for the other platforms? An IOC corpus from the OpenHands case could become a detection signature for future surveys: when a survey finds conversation titles, prompt logs, or task descriptions that look like reconnaissance, the operator notification becomes more urgent than the typical disclosure-pipeline cadence.

**Third, the framework-class and protocol-class categories need new tools.** CrewAI, AutoGen, LangChain, and LlamaIndex are not surveyable via the platform methodology. They require operator-attribution-first work — finding who is running them in production via GitHub corporate organizations, npm package adoption metadata, CT logs for known operator naming patterns. MCP servers will become surveyable once the ecosystem converges on canonical transport conventions (estimated 2026 H2 per the current spec roadmap). Each of these requires a different tool than herald: an operator-attribution graph for framework class, a port-scan + protocol-handshake tool for protocol class.

The platform-class work continues. The bounded Insight #76 hypothesis has 13 data points; expanding to 20+ would let the demo-first / enterprise-first cluster split be quantified statistically rather than observationally.

---

## Acknowledgments and provenance

The two-day survey work was conducted under formal engagement scope on designated targets. Custom tooling, prototype development, and finding demonstration are standard deliverables. All probes were restraint-bounded: enumerate metadata, do not exfiltrate; names ARE the finding; sample payloads minimally only to confirm severity.

The case study corpus, herald source, and research-program directory are all in the public repositories `nuclide-research/AI-LLM-Infrastructure-OSINT` and `nuclide-research/herald`. The NICE Framework career pathway PDFs that frame the work in role/task vocabulary are in `~/Documents/dod-cyber-pathways/`. The academic literature corpus grounding the threat-class taxonomy is in `~/Documents/cs*-aisecure/` (Bo Li, UIUC, five courses, 353 PDFs indexed).

Methodology references:
- **NICE Cybersecurity Workforce Framework** (Interagency Federal Cyber Career Pathways Working Group, November 2020) — composite role taxonomy
- **OWASP Top 10 for LLM Applications (2025)** — threat-class taxonomy
- **AI-Native LLM Security** (Packt, December 2025) — 2023 → 2025 OWASP evolution
- **Hacking APIs** (No Starch, 2022) — public-system-info endpoint discovery
- **Security with Go** (Packt, 2018) — channel-semaphore concurrency pattern
- **Powerful Command-Line Applications in Go** (Pragmatic, 2021) — HTTP client + NDJSON architecture

The composite operating role for the survey work was **NICE 541 Vulnerability Assessment Analyst** (audit-report generation, verification stage, finding classification) + **NICE 661 Research and Development Specialist** (capability-gap analysis driving herald's design) + **NICE 631 Information Systems Security Developer** (herald SDLC discipline) + **NICE 422 Data Analyst** (population analysis, geographic/ASN enrichment, longitudinal metrics).

The research program directory at `nuclide-research/AI-LLM-Infrastructure-OSINT/research-program/` indexes the entire corpus across three layers (research thread + NICE role + disclosure state). 67 markdown files. Every primary artifact reachable from at least three navigational paths.

---

## A note on the disclosure pipeline

Nothing in the QUEUED state has been sent. The pipeline state — institutional findings, upstream-maintainer recommendations, the Capitol.ai customer-tenant verification request, the OpenHands `/proc/self/environ` operator notifications — exists as researcher metadata, not as autonomous action. Decisions about timing, routing, and prioritization belong to Nicholas Kloster.

The published security contact for Capitol.ai (`security@capitol.ai`) is the most clearly-defined path. The institutional contacts (`security@berkeley.edu`, `security@security.harvard.edu`, `cscsec@ust.hk`, `csirt@vutbr.cz`, `it-incident@iu.edu`, `oirc@northeastern.edu`, `infosec@asu.edu`) are well-established. TWCERT/CC, CERT.br, and CNIL coordination paths exist for the consolidated Taiwan / Brazil / French findings respectively. OFAC-sensitive paths require explicit legal review.

The upstream-maintainer recommendations (Langfuse, InfiniFlow, Arize, All-Hands-AI, danny-avila) are the highest-leverage class. Each is a one-PR change to a default value that protects the entire population in a single release cycle. The Open WebUI precedent (v0.5+ default change after public surveys → 11.8% rate today, down from earlier higher rates) is the existence proof.

---

*This synthesis is one artifact in a larger research program. The full case-study corpus, finding breakdowns, herald source, and research-program index are public at github.com/nuclide-research/AI-LLM-Infrastructure-OSINT and github.com/nuclide-research/herald.*

*NuClide Research. Independent security research. nuclide-research.com.*
