---
type: survey
---

# Weaviate on Public Cloud: Auth Posture and Enterprise Tenant Exposure Survey

_NuClide Research · 2026-05-09_

---

## Summary

Shodan pull of `http.html:"weaviate" port:8080` → 852 unique IPs → asyncio probe of `/v1/meta`, `/v1/schema`, `/v1/nodes` → **694 confirmed reachable Weaviate instances**. Of these, **435 are fully open** (no authentication), **344 contain at least one populated class** (vector collection), **201 have the OpenAI module active** (meaning an OpenAI API key is configured server-side and callable by any unauthenticated client). The auth-off-by-default thesis reproduces cleanly: Weaviate's anonymous access is opt-out, not opt-in.

The notable findings are not the auth posture itself (well-documented) but the **enterprise multi-tenant SaaS pattern** appearing at scale: AI integrators have built chatbot platforms on top of Weaviate and exposed the entire client-portfolio knowledge base without access controls. Named enterprise tenants confirmed across luxury retail, public transport infrastructure, national-level financial regulatory, government, and cybersecurity sectors.

---

## Methodology

```
shodan download --limit 1000 weaviate-8080.json.gz 'http.html:"weaviate" port:8080'
  → 852 unique IPs

weaviate-probe.py (asyncio, 80 concurrent, 2s connect / 4s read / 8s host deadline)
  GET /v1/meta     → version, module list (OpenAI/Cohere/Anthropic/etc)
  GET /v1/schema   → class names (collection names)
  GET /v1/nodes    → object count, shard count, node health
  GET /v1/objects?limit=1 → confirm data access (no content read)
  → 694 confirmed (12 seconds wall time)
```

---

## Findings Summary

| Metric | Value |
|---|---|
| Shodan hits (`http.html:"weaviate" port:8080`) | 858 (852 downloadable) |
| Confirmed reachable | **694** |
| Auth-gated (HTTP 401) | 259 |
| **Fully open (no auth)** | **435** |
| Populated (≥1 class) | **344** |
| Populated + OpenAI module | **169** |
| OpenAI module active (any) | 201 |
| Cohere module active | 135 |
| Both OpenAI + Cohere | 134 |

### Version distribution (top 10)

| Version series | Count |
|---|---|
| v1.24.x | 55 |
| v1.27.x | 54 |
| v1.28.x | 39 |
| v1.30.x | 31 |
| v1.25.x | 29 |
| v1.32.x | 27 |
| v1.23.x | 26 |
| v1.31.x | 25 |
| v1.35.x | 22 |
| (no meta response) | 262 |

The 262 "unknown version" hosts responded on /v1/schema or /v1/nodes but not /v1/meta. Likely older Weaviate versions or non-standard deployments that nonetheless serve the schema API.

---

## Notable Findings

### F1: MyAi Corporation multi-tenant platform (HIGH)

**Hosts:** `188.245.173.135:8080` (Hetzner DE, `www.myaicorp.com`), `91.98.226.57:8080` (Hetzner DE)  
**Operator:** MyAi Corporation (`myaicorp.com`). Spanish AI integrator, TLS cert `*.myaicorp.com` (Sectigo DV)  
**Severity:** HIGH. Enterprise multi-tenant SaaS platform with no access controls; named clients' vectorized knowledge bases publicly readable

Both instances share the same schema with 200–203 classes, running Weaviate v1.28.4 with `text2vec-openai` and `backup-filesystem` modules. The instances appear to be production and staging (or load-balanced pair) for MyAi Corporation's chatbot/RAG platform. The schema enumerates the complete client portfolio.

Named clients confirmed in the class namespace (selection):

| Sector | Clients |
|---|---|
| **Luxury / beauty** | Dior, Chanel, YSL, Armani, Charlotte Tilbury, Tom Ford, Louboutin, Lancôme, Hermès, Byredo, Paco Rabanne, Guerlain, Nars, Revlon |
| **Industrial equipment** | Wittmann (injection molding robots — 10 model-specific classes), IKA (lab equipment), Salicru (UPS/power), Yaskawa (industrial robots), VaccuBrand, Plasmac |
| **Public transport** | Renfe (Spanish national rail), TMB (Barcelona metro), Metro Madrid, Moventis, FGC (Ferrocarrils de la Generalitat de Catalunya), Turkish Cargo |
| **Government** | Gencat / Generalitat de Catalunya (Catalan government), Qatar University, Riyadh Municipality, Roshn (Saudi NEOM-era mega-city developer) |
| **Finance / payments** | Astropay, Monri (Balkan payment gateway), Signifyd |
| **Cybersecurity** | CrowdStrike, Kaspersky, Orange (Cyberdefense) |
| **Pharma / health** | Probiotical, URIAGE (French dermo-cosmetic) |

The `Dataseekers`-prefixed classes (`DataseekersFragranceArtisan`, `DataseekersFragranceLouboutin`, `DataseekersMakeUpChanel`, etc.) indicate Dataseekers is either a sub-brand or an integrator project name within the MyAi Corporation platform.

**Reproduction (operator-self-test):**
```bash
curl http://188.245.173.135:8080/v1/schema | python3 -m json.tool | grep '"class"'
```

**Impact:** Any unauthenticated caller can enumerate all client names, read schema structure for each client's knowledge base, and issue semantic search queries over any client's vectorized documents. The `text2vec-openai` module means OpenAI embeddings are computed using an API key baked into the server config, but credential extraction requires the `/v1/modules/text2vec-openai` config endpoint, which was not tested.

**Disclosure status:** Not yet disclosed. Routing via myaicorp.com contact surface (currently nginx default page, no public contact form or security email found at time of survey).

---

### F2: Indian regulatory/compliance RAG platform (HIGH)

**Hosts:** `34.56.31.138:8080` (GCP US-central1, Iowa), `104.154.128.27:8080` (GCP US-central1, Iowa)  
**Severity:** HIGH. 3,059-class and 197-class instances respectively; Indian government and financial regulatory corpus

Both GCP instances run Weaviate v1.31.3 with the full Weaviate Cloud module set (all generative providers: OpenAI, Anthropic, Cohere, Google, Mistral, etc.) and `hostname: http://[::]:8080`. The Weaviate Cloud Service embedded-module profile. These may be WCS-managed instances or self-hosted with the WCS module bundle.

**34.56.31.138 (3,059 classes):** Schema contains Indian regulatory documents across:
- **NPCI** (National Payments Corporation of India). UPI operational circulars
- **UIDAI** (Unique Identification Authority of India). Aadhaar-related notifications
- **MCA** (Ministry of Corporate Affairs). Companies Act GSR gazette amendments (largest class group: ~2,000+ GSR series)
- **SEBI**: securities regulation (smaller subset)
- **IBC** (Insolvency and Bankruptcy Code). Enforcement notifications
- **CCI** (Competition Commission of India)

**104.154.128.27 (197 classes):** SEBI-focused subset. Securities circulars, borrowing regulations, timeline extension notifications.

**Context:** This is an Indian corporate law / compliance AI assistant built over vectorized gazette notifications. The breadth of coverage (NPCI/UPI + UIDAI/Aadhaar + MCA + SEBI + IBC) suggests either a legal-tech product or an in-house compliance tool for a regulated entity. The data itself is public (gazette notifications are public domain), but the unauthorized searchable RAG interface over this corpus represents exposure of the operator's proprietary knowledge curation work, and `/v1/generate` queries (generative RAG) would consume the operator's API keys without authorization.

**Disclosure status:** Not yet disclosed. Operator identity not established from IP/module profile alone. WCS module bundle is consistent with Weaviate Cloud Service managed instances (disclosure would route via Weaviate Cloud abuse contact if confirmed).

---

### F3: Multi-tenant chatbot SaaS (MEDIUM)

**Host:** `85.190.246.164:8080` (Contabo DE, `vmi1891772.contaboserver.net`)  
**Severity:** MEDIUM. 50 classes, **136,243 vector objects** (highest object count in survey), Weaviate v1.23.5 with OpenAI + Cohere generative modules

Named tenants include UK brands: Harrogate Spring (mineral water), Heck (food), Imperial (tobacco/brands), Redline Specialist Cars, Odyssey, and multiple `001`-suffixed patterns indicating a tenant-per-class SaaS model. The `Dead01` and `Deadnorthern_001` classes suggest decommissioned tenants that weren't deleted.

136,243 objects is the largest corpus volume confirmed in this survey. Weaviate v1.23.5 predates the introduction of authentication as an easily-configurable default, making this a legacy deployment unlikely to be hardened.

**Disclosure status:** Not yet disclosed.

---

## Auth Posture Analysis

Weaviate ships with `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=true` by default. The operator must explicitly set `AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED=false` and configure an auth method (API key, OIDC, or both) to restrict access. This is the same opt-out posture as ChromaDB (pre-0.6) and early Qdrant deployments.

The 259 auth-gated instances (37%) represent operators who actively configured auth. A better ratio than ChromaDB (0% auth-gated in both NuClide surveys) but still a majority unauthenticated.

**OpenAI key exposure path:** Weaviate's `/v1/modules/text2vec-openai` endpoint returns module configuration including whether a key is configured (the key value itself is not returned in the config endpoint per Weaviate's design). However, any unauthenticated caller on a Weaviate with `text2vec-openai` active can issue embedding and generative queries that consume the operator's OpenAI API quota at their own cost. This is effectively LLM compute theft via the semantic search layer, not direct key extraction.

---

## Discovery Context

Survey conducted 2026-05-09 as part of NuClide Research vector database exposure series. Shodan pull on `http.html:"weaviate" port:8080`, asyncio probe with per-endpoint timeout enforcement (2s connect / 4s read / 8s host deadline, 80 concurrent). Total probe time: 12 seconds for 852 hosts.

Port 8080 is Weaviate's default through v1.x. Weaviate Cloud Service and newer managed deployments front on 443; the direct-8080 exposure set represents self-hosted instances, the majority of which are not behind a reverse proxy with auth.

Companion surveys: `chromadb-tier2-cloud-survey-2026-05.md`, `milvus-cloud-survey-2026-05.md`, `milvus-tier2-cloud-survey-2026-05.md`.
