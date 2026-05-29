# LLM Guards / AI Firewalls: Adopter Map (public-disclosure OSINT)

_Date: 2026-05-29. Method: passive, public sources only (vendor case studies, customer-logo walls, press, GitHub dependents, job postings, conference talks, federal contract records). Every adopter cited. No active probing. Companion to the `LLM Guards / AI Firewalls` taxonomy category._

**Reading the confidence column:** 0.9+ = named by both parties or primary contract record. 0.7-0.85 = vendor-published or solid press, single strong source. 0.4-0.65 = single secondary source, pilot, or component-attribution uncertain. Below 0.4 = excluded (see dead space).

**One distinction does all the work here:** *end-user adopter* (an org running the guard on its own traffic) vs *integration-partner* (a product that wraps or supports the guard). Conflating the two is the dominant false-positive trap; it is called out per vendor.

---

## Named end-user adopters

| Guard | Adopter | Sector | Conf | Evidence |
|---|---|---|---|---|
| **Lakera** (Check Point) | **Dropbox** | tech | 0.98 | Dual-confirmed: Lakera case study + Dropbox's own eng blog "How we use Lakera Guard to secure our LLMs" (Docker RPC service, prompt-injection/jailbreak screen). Also investor (Dropbox Ventures). |
| **Lakera** | **Cohere** | AI | 0.85 | Joint "Set the Bar for Enterprise LLM Security" announcement; Cohere Head of AI Safety quoted on Lakera customers page. |
| **Protect AI** (Palo Alto) | **Hugging Face** | AI | 0.97 | Guardian integrated to scan all Hub models (4.47M model versions). Both parties' blogs. Distribution partnership more than private enterprise win. |
| **LLM Guard** (OSS) | **Microsoft** (KAITO) | tech | 0.55 | Listed in llm-guard dependents graph (AKS add-on). Import not code-confirmed. |
| **LLM Guard** (OSS) | **IBM Research** (BeeAI) | tech | 0.55 | Dependents graph (agent framework, now Linux Foundation). Import not code-confirmed. |
| **NeMo Guardrails** (NVIDIA) | **Amdocs** | telecom sw | 0.9 | NVIDIA blog: integrated into amAIz platform. |
| **NeMo Guardrails** | **Cerence AI** | automotive | 0.9 | NVIDIA blog: in-car assistant filtering. |
| **NeMo Guardrails** | **Lowe's** | retail | 0.88 | NVIDIA blog: store-associate knowledge tools. |
| **NeMo Guardrails** | AT&T | telecom | 0.45 | NeMo *platform* customer (Customizer/Evaluator); Guardrails-specific use not confirmed by primary source. |
| **LlamaFirewall** (Meta) | **Meta** | tech | 0.9 | Self-attributed: "utilized in production at Meta" (arXiv 2505.03574). |
| **LlamaFirewall** | Trendyol | e-commerce | 0.4 | *Evaluated and red-teamed* it (found bypasses). Not confirmed production. |
| **Robust Intelligence** (Cisco) | **Expedia** | travel | 0.85 | First paying AI Firewall customer (2020), model QA. Sequoia spotlight. |
| **Robust Intelligence** | Deloitte | prof services | 0.7 | Sequoia spotlight customer list. Single secondary source. |
| **Robust Intelligence** | Intuit | fintech | 0.7 | Sequoia spotlight. Single secondary source. |
| **Robust Intelligence** | JPMorgan Chase | finance | 0.55 | 2019 pilot per Sequoia narrative; not confirmed standing customer. |
| **Robust Intelligence** | BMW | automotive | 0.5 | Post-Cisco engagement ("i Vision Dee"), single soft source. |
| **CalypsoAI** (F5) | **Palantir** | data/gov | 0.9 | CalypsoAI press (now on f5.com): integrated into Palantir AIP. FedStart partner announcement. |
| **CalypsoAI** | **SGK** | marketing | 0.8 | F5 acquisition PR: "Trusted by Palantir and SGK." |
| **HiddenLayer** | **US Missile Defense Agency** | defense | 0.85 | MDA SHIELD IDIQ awardee (Dec 2025, Golden Dome). PRNewswire + trade press. |
| **HiddenLayer** | **US Dept of the Air Force** | defense | 0.75 | STTR Phase II (~$1.8M), AI detection & response. |
| **Arthur** (Shield) | **Humana** | healthcare | 0.85 | Flagship enterprise customer, multiple press. (ML-monitoring era; Shield-specific not all confirmed.) |
| **Arthur** | **John Deere** | manufacturing | 0.8 | Fast Company coverage. |
| **Arthur** | **Axios** | media | 0.75 | Fast Company. |
| **Arthur** | **US DoD / US Air Force** | defense | 0.7-0.75 | VentureBeat + Fast Company. |
| **Arthur** | **Truebill** (Rocket Money) | fintech | 0.7 | Arthur PRNewswire. |
| **WhyLabs** | **Glassdoor** | tech/HR | 0.8 | AWS-collaboration BusinessWire release; observability across AI/LLM portfolio. |
| **WhyLabs** | **Snappt** | proptech | 0.8 | Same release; fraud-detection model health. |
| **NeuralTrust** | **ABANCA** | banking | 0.6 | NeuralTrust states it stress-tested ABANCA's "SOFia" GenAI chatbot; vendor-asserted role, ABANCA deployment independently documented. |
| **Guardrails AI** | **Robinhood** | fintech | 0.85 | Seed-funding PR + Zetta VP article; quote from Robinhood technical advisor. |
| **Guardrails AI** | **Masterclass** | edtech | 0.8 | Zetta article + reused on guardrailsai.com; quote from AI eng lead. |
| **PromptArmor** | (none named) | - | - | Testimonials role-attributed only; named companies on site are research targets, not customers. |
| **Rebuff** | (no named end-users) | - | - | Owned by Protect AI -> Palo Alto; archived May 2025. |

## Integration partners (wrap/support the guard, NOT end-users)

- **NeMo Guardrails:** Cisco (AI Defense), Palo Alto Networks (AI Runtime Security), Fiddler AI, Weights & Biases, ActiveFence, Hive, TaskUs, Tech Mahindra, Wipro.
- **Guardrails AI:** Databricks/MLflow (validators as GenAI scorers), LangChain.
- **Rebuff:** LangChain (official integration blog + notebook).

---

## Cross-vendor patterns

1. **Regulated verticals dominate every named set.** Banking (ABANCA, Chase, top-5 US banks, Robinhood), healthcare (Humana), defense (MDA, USAF, DoD), telecom (Amdocs, AT&T). Guardrail buyers self-select for compliance pressure; the named ones are large enough that the logo *is* the marketing.

2. **Defense/gov is the only publicly-named base for some vendors.** HiddenLayer's entire verifiable adopter list is US defense/IC, because federal contract awards are public record (PRNewswire, contract DBs) while commercial buyers stay behind NDA. Arthur leans the same way. Federal procurement transparency is itself an OSINT channel for this category.

3. **Vendor age predicts disclosure depth.** Arthur (founded 2018, ML-monitoring heritage) has the deepest named trail; the pure-play LLM-security startups (NeuralTrust, PromptArmor) disclose almost nothing and lean on aggregate social proof ("750+ companies", grey logo walls).

4. **OSS guard adoption is dark.** GitHub "Used by" is empty/near-empty for Guardrails AI, Rebuff, and thin for LLM Guard. These are PyPI/npm libs consumed without public org manifests, so the dependency channel does not reveal adopters. Signal lives in vendor testimonials and framework integrations, not code graphs. This matters for the taxonomy: you cannot enumerate OSS-guard adopters the way you enumerate exposed inference servers.

5. **The acquisition wave fragments evidence.** Lakera->Check Point, Protect AI->Palo Alto, Robust Intelligence->Cisco, CalypsoAI->F5 (calypsoai.com 301s to f5.com). Post-2025 named-customer marketing thins as standalone sites get absorbed.

6. **Three false-positive traps caught this pass** (logged so they do not recur):
   - **Investor != customer.** Citi appears via Citi Ventures (Lakera investor), not as a deployment. Excluded.
   - **Platform != component.** AT&T, BlackRock, Nasdaq, SAP are NeMo *platform* customers; primary sources do not tie them to the Guardrails component. Kept low or excluded.
   - **Research-target != customer.** PromptArmor's site names Anthropic/Google/Slack/Writer as prompt-injection *research subjects*. Akto and Aetion surfaced as dependents/blog matches but ship their own guardrail / use "guardrails" generically. All excluded.

---

## Tie-back to the taxonomy

The Lakera platoon run already showed the self-hosted guard ships auth-less by design. This adopter map adds the demand-side shape: the named buyers are regulated enterprises and defense, and OSS-guard adoption is invisible by org name. For a future survey of this category, the implication is that **population-scale enumeration will find self-hosted OSS instances (NeMo, LLM Guard, Guardrails Server on :8000) but will not easily attribute them to named orgs** the way a corporate-fronted inference server attributes via cert CN. Attribution for this category leans on the operator's *other* surfaces (cert SANs, adjacent hostnames), not the guard itself.
