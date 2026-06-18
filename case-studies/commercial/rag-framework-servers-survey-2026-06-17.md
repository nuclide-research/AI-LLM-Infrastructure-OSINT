---
type: survey
category: rag-framework-servers
date: 2026-06-17
---

# RAG Framework Servers: First Population Survey (LlamaIndex / Haystack / LightRAG / Microsoft GraphRAG)

_NuClide Research · 2026-06-17 · Cat-RAG-Framework-Servers_

## Result

The auth-on-default thesis holds on a fourth platform class. Three of the four frameworks in this tier ship auth-off or auth-absent by default, and the population matches the default.

- **LightRAG**. Tier-A* (auth exists, ships disabled). At population, 12 of 13 reachable instances confirmed currently unauthenticated; roughly 29 percent of the 62 instances exposing `/health` self-report `auth_mode=disabled`. Thesis confirmed.
- **LlamaIndex**. Tier-A (no auth concept; CORS `*`). Confirmed unauthenticated LLM-chat inference on a named commercial operator. Thesis confirmed.
- **Microsoft GraphRAG accelerator**. Tier-B as designed (auth pushed to an APIM gateway). Zero direct exposure on the accelerator path. The negative is the thesis: gateway-auth-default produces a near-zero direct-unauth population, the contrapositive of the LightRAG result.
- **Haystack / hayhooks**. Shodan-dark on every brand string. Not a posture finding; an indexability gap. The framework serves a JSON root with no HTML title, so brand dorks return genuine zero and the population is reachable only by active banner-grab on 1416/1417 or Censys (blocked this run).

Seven findings confirmed (F1 through F7). Two leads refuted at the verification stage (R1, R2), including the lead ranked highest going in. The refutations are the discipline story: the scan produced candidates, verification produced the findings, and the two strongest-looking candidates did not survive a 200-with-data re-probe.

## Headline findings

- **F7 · Mobee (mobee.com)**. An OJK-regulated, ISO 27001 Indonesian crypto/digital-asset exchange running a populated production unauthenticated LightRAG corpus (roughly 600 documents) on its own Cloudflare-Origin-CA origin box. Regulated-financial operator class. Headline by data sensitivity.
- **F1 · Hanssen Agency (hanssen.agency)**. A German creative agency's self-hosted Nextcloud document corpus, vectorized into an unauthenticated Qdrant collection named `nextcloud-docs` (531 document embeddings). Private third-party agency and client material, GDPR-DE data subjects.

Both are names-only. No document content was read. `data_accessed=false` everywhere.

## Population

| Stage | Count |
|---|---|
| Shodan candidates | 549 |
| Live (scanner banner) | 223 |
| Clean live (tarpit-stripped) | 175 |
| Tarpit / honeypot fleet | 48 |
| AI services (aimap-confirmed) | 87 |
| LightRAG confirmed | 67 (50 unique IP) |
| Qdrant | 2 |
| Ollama | 1 |
| Neo4j | 8 |
| MCP servers | 4 |

The 48-host tarpit fleet (open 8 or more ports; 21 hosts open all 25 probed) was stripped before aimap, in line with scanner Step 0c. Names and counts are the finding; no honeypot was engaged.

## Reconnaissance

Stage -1 OSINT framed the tier before a single probe. The RAG framework layer sits above the vector databases of Cat-02 and the RAG builders of Cat-34. Each framework leaks system prompts, retrieval logic, ingested documents, and embedded provider keys even when the underlying vector store is locked. Four parallel research lanes produced the posture table that the survey then tested:

| Platform | Default posture | Verification primitive |
|---|---|---|
| LlamaIndex | Tier-A (no auth, CORS `*`) | `GET :4501/status` -> `max_deployments` + `deployments[]` |
| Haystack / hayhooks | Tier-A* (no auth primitive ships) | `GET /status` -> `{"status":"Up!","pipelines":[...]}` |
| LightRAG | Tier-A* (auth exists, off default) | `GET :9621/health` -> `auth_mode:"disabled"` |
| Microsoft GraphRAG | Tier-B designed / Tier-C misdeploy | `GET /manpage/openapi.json` -> `info.title=="GraphRAG"` |

Shodan harvest ran through the in-page `fetch()` technique inside an authenticated Playwright session, zero API credits, every dork logged with hit count. Three findings emerged at the dork stage:

1. **Three Shodan-dark JSON-root tiers.** LlamaIndex `:4501`, hayhooks JSON, and the LightRAG `/health` field all return JSON with no HTML title. Brand dorks for these route to near-zero on the Shodan web UI by design. Zero is a logged result, not absence. LightRAG was still discoverable through `http.title:"LightRAG"` (92 hits) and `port:9621` (274, FP-heavy superset).

2. **GraphRAG namespace collision.** `http.title:"GraphRAG"` returned 46 hosts, every one of them non-Microsoft: Youtu-GraphRAG (Tencent) x5, ProtonX, ManGAI, a Purdue GraphRAG chatbot, a GraphRAG Agentique instance on OVH, and 39 custom builds. This is the third independent platform-class confirmation of the dork-stage schema-anchor pattern, promoting Insight #102 from candidate to numbered.

3. **Haystack genuinely Shodan-dark.** Every hayhooks and deepset brand string returned a verified zero. The only port signal (1416/1417) is FP-heavy and overlaps MCP. The population is real but invisible to brand discovery. A routing finding rather than a posture finding.

## Verification

Verification was the load-bearing stage, and it both confirmed and refuted.

**LightRAG population (F4, rung A/2).** The `/health` endpoint self-reports `auth_mode`. At scan, 18 instances reported disabled, 44 enabled, 5 unknown, roughly 29 percent unauthenticated. The 3v re-probe found 12 of 13 candidates still live and unauthenticated; only 98.81.157.172 went genuinely down. Two hosts (3.142.219.65, 34.172.75.32) returned `/documents` 403 despite `auth_mode=disabled`, which produced a codified insight: `auth_mode=disabled` does not mean all endpoints are open. Endpoint-level gating is independent of the global flag. Verify the endpoint, not the flag.

**Vhost undercount correction.** The bare-IP probe systematically undercounted the unauthenticated population because vhost-routed AI services reject bare-IP requests with 400/404/timeout. Re-probing with a Host header recovered from rDNS or cert SAN brought back three more confirmed-unauth LightRAG instances, including the F7 Mobee corpus, which was invisible to the bare-IP method. This extends Insight #69 to the probe-technique layer: re-probe vhosted services with a Host header before declaring them down.

**Restraint held throughout.** Every confirmed finding sits at rung A/1 or A/2: depth A (logic-confirmed) by host or by population, breadth 1 (single host) or 2 (population). No finding required reading a document. Where severity needed confirmation, a single metadata read settled it (collection point counts, document status buckets, model lists). Names and counts are the finding.

## Findings

### F1 · Qdrant unauth, `nextcloud-docs` corpus · 82.165.133.93:6333 (rung A/1, HIGH)

Unauthenticated Qdrant. `GET /collections` returned 200 with no auth; the `nextcloud-docs` collection holds 531 document embeddings (plus two test collections). The collection name matches the operator's own Nextcloud front at cloud.hanssen.agency. Private agency and client document vectors are retrievable without authentication. Data not read; sensitivity inferred from operator class and collection name. High-PII/PHI.

- DCWF: T5854 / K7040 (733 Risk/Ethics: PII surface in ingested corpus, names-only).

### F2 · Qdrant unauth, 71,037 points · 31.57.224.107:6333 (rung A/1, HIGH surface / LOW data)

Unauthenticated Qdrant; full collection-management surface open. `GET /collections` returned 200; total `points_count` 71,037 (a Quran ayah/tafsir corpus). High exposure surface, low data sensitivity; the corpus is public religious text. Same IP carries an adjacent Postgres:5432 and a Neo4j instance (authenticated). The surface is the finding; the data class is benign.

- DCWF: T5919 / K7044 (672 T&E: adversarial test of the exposure surface).

### F3 · Ollama unauth, 4 models · 54.37.225.10:11434 (rung A/1, MEDIUM)

Unauthenticated Ollama. `GET /api/tags` returned 200 with four models loaded: glm-5.2:cloud, deepseek-v4-pro:cloud, llama3.2:3b, qwen2.5:14b. The two `:cloud` models indicate a passthrough to ollama.com, which makes an open `/api/generate` an attribution-laundering and cost-shifting surface against a paid upstream (Insight #39). Surface open, inference not exercised; `/api/generate` and `/api/pull` were deliberately not called. Operator unattributed (bare OVH VPS, Gravelines, no cert, no operator rDNS, no vhost).

- DCWF: T5854 / K7040 (733: cost-shift / attribution-laundering risk).

### F4 · LightRAG population unauth · port 9621 (rung A/2, HIGH)

Twelve of thirteen reachable candidates confirmed currently unauthenticated (`auth_mode=disabled` and reachable). At population scale, roughly 29 percent of the 62 instances exposing `/health` self-report disabled auth. The thesis result: a Tier-A* framework ships auth off, and operators inherit the default. Two hosts gate `/documents` with a 403 despite `auth_mode=disabled`, evidence that endpoint gating outranks the global flag.

- DCWF: T5919 / K7044 (672: V&V at population scale, verify primitive).

**Attribution note (Tokyo Swagger sub-fleet, 2026-06-18).** The four-host AWS ap-northeast-1 LightRAG Swagger sub-fleet decommissioned to one survivor under re-verification: `52.69.81.89` confirmed unauth, two timed out, and `35.78.152.204` resolved to a carrier finding. Its TLS cert (CN `console.ran-nssmf.sorp.docomo.ne.jp`, Amazon-issued) attributes it to NTT DoCoMo 5G RAN-NSSMF (RAN Network Slice Subnet Management Function) management infrastructure. The host is fronted by an AWS ALB (`server: awselb/2.0`) that returns 403 on every path regardless of Host header: surface-open, access not exercised. The attribution is the finding; given carrier 5G management infra, restraint stopped at identification. Names ARE the finding.

### F5 · LightRAG `/health` platform config-disclosure · all 67 instances (rung A/2, HIGH)

A finding against the platform, not the operators. The LightRAG `/health` endpoint sits on a no-auth skip-list and leaks `llm_binding` and `llm_model` (anthropic, azure_openai, aws_bedrock, openai, ollama, openrouter), the `embedding_model`, and `working_directory` paths that name operator usernames and project directories. This fires on every instance, including the authenticated ones. One upstream fix protects the whole population. A health endpoint on a no-auth skip-list is a platform config-disclosure anti-pattern.

- DCWF: T5919 / K7044 (672: V&V tooling; platform-class verification).

### F6 · Unauth LLM chat, framework unconfirmed · 108.132.72.10:443 (rung B/1, HIGH)

app.babbid.com serves unauthenticated LLM inference. `POST /api/chat` returned 200 with a live model reply and no auth gate; the session is stateful (UUID tracking) with no authentication. A single confirm probe established severity; no chat history, no context extraction, no file traversal.

Operator attribution (2026-06-18): the domain babbid.com was registered 2019-07-11 via IONOS SE, registrant country ES (Madrid), DNS on Cloudflare. `app.babbid.com` is Cloudflare-fronted (172.67.165.72 / 104.21.57.182); the origin is `108.132.72.10` on AWS eu-west-1 (Ireland), presenting a self-signed cert (CN == issuer == app.babbid.com) and reachable directly past Cloudflare on :443 (the chat surface has no WAF in front of it at the origin).

Verification corrected the platform label. aimap fingerprinted this as LlamaIndex on a loose `/api/chat/config` match, but the JS-bundle pass found a Laravel + Inertia.js + Vue 3 coworking application. The LLM/chat surface is server-side; the bundle leaks zero secrets, model names, or provider keys. The finding stands as unauthenticated LLM chat inference on a named commercial operator (Babbid Centros de Negocios, a Spanish coworking SME, six centers), but the underlying LLM framework is unconfirmed. Reclassified accordingly. The bundle did yield a complete pre-auth endpoint map (a public Vite `manifest.json` plus an inlined 241-route Ziggy table) and a server-side editable system prompt with version-restore, a prompt-injection-relevant surface, surface-open, not exercised. Low-public data class.

- DCWF: T5919 / K7044 (672: fingerprint V&V correction); T5854 / K7040 (733: unauth-inference cost-abuse surface).

### F7 · LightRAG unauth production corpus · 159.69.89.55:443 (rung A/1, HIGH) · HEADLINE

mobee.com runs an unauthenticated LightRAG instance with a populated production corpus. The `/health` endpoint reports `auth_mode=disabled`; `/documents` status buckets total roughly 600 documents (processed 426, failed 425, parsing 105, analyzing 9, pending 34). The instance is vhost-routed and was invisible to the bare-IP probe. It was recovered only by re-probing with the cert-SAN Host header.

Operator is Mobee, an OJK-regulated, ISO 27001 Indonesian crypto/digital-asset exchange (Jakarta, SCBD; 300-plus crypto assets and US stocks). The Cloudflare Origin CA cert with SAN `*.mobee.com` ties this Hetzner box to the operator's own Cloudflare account, an operator-owned origin host, not a squatter. The box sits outside the Cloudflare proxy, so no WAF fronts the RAG instance. mobee.com carries an `anthropic-domain-verification` TXT record (an active Anthropic/Claude customer). The corpus is most plausibly internal KB / support / KYC-AML / SOP material derived from or containing customer PII and financial data. High-PII/PHI by operator class. Documents not read; sensitivity inferred from operator class per scope.

- DCWF: T5854 / K7040 (733: regulated-financial PII/PHI surface, names-only); T5919 / K7044 (672: vhost re-probe verification primitive).

## Refuted

The verification discipline is the headline as much as the findings are. Two leads, including the one ranked highest going in, did not survive re-probing and would have been published falsehoods.

### R1 · Neo4j (8 hosts) · REFUTED

This was the top-ranked lead. The premise: LightRAG's graph backend (Neo4j) holds the extracted-entity corpus, the actual data tier above the RAG front, and stacked exposure would be catastrophic. Verification refuted it. All eight hosts demand auth at the data plane (`/db/data/` returns 401). The `:7474/` root leaks a version string only, info-level, useful for CVE scoping, not a data exposure. The graph backends are authenticated. The strongest lead was wrong.

### R2 · Flagship stacked host 206.189.153.160 · REFUTED as catastrophe

The narrative centerpiece going in: LightRAG (`:80`/`:443`/`:9621`) plus Neo4j:7474 plus Redis:6379 on one IP, the realized worst case of RAG front, extracted-entity graph store, and cache all exposed together. Verification reduced it to LOW metadata-disclosure. All three legs are auth-on (LightRAG `/documents` 401, Neo4j 401, Redis NOAUTH). The host leaks storage topology (Redis/Neo4j/Milvus), an OpenRouter model (gemini-3-flash-preview), and version strings via `/health` and `/auth-status`. Milvus 19530/9091 are open at the liveness layer only. Recon and CVE-scoping value, no unauthenticated record read. The catastrophe did not exist; the discipline of re-probing caught it before publication.

## Negatives (publishable)

- **Microsoft GraphRAG accelerator, 0 direct exposure.** The `/manpage/openapi.json` and accelerator routes returned zero. APIM-gated by default. This is thesis-confirming: a gateway-auth-default framework produces near-zero direct unauthenticated exposure, the contrapositive of the LightRAG result. The honest limit: a bypass-APIM misdeploy cannot be measured without host evidence, and none surfaced this run.
- **Haystack / hayhooks, Shodan-dark.** Every brand string returned a genuine zero (JSON root, no HTML title). The population is reachable only by active 1416/1417 banner-grab or Censys, which was blocked this run. A routing finding, not a posture finding.

## Impact

The two headline findings carry the population's risk. F7 puts a roughly-600-document production corpus on a regulated financial operator's origin box, unauthenticated, outside the operator's own WAF. For an OJK-regulated, ISO 27001 exchange, an internal KB / KYC-AML / support corpus exposed without auth is a regulatory and customer-data exposure regardless of which specific records it holds; the names and counts establish the class. F1 exposes a creative agency's private Nextcloud document corpus (contracts, proposals, client material) as recoverable semantic content, a GDPR-DE exposure of third-party data subjects on a single-VPS full-business stack.

At the platform level, F5 is the highest-leverage finding: a `/health` config-disclosure that fires on all 67 LightRAG instances, including the authenticated ones, leaking provider, model, and operator-directory paths. One upstream fix protects the entire population. F4 quantifies the structural risk: roughly 29 percent of the discoverable LightRAG population ships unauthenticated, the auth-on-default thesis realized on a fourth platform class.

The refuted leads bound the impact honestly. The catastrophe scenario (stacked RAG-plus-graph-plus-cache, unauth graph backends) did not materialize. Graph backends in this population are authenticated. The real exposure is at the RAG-front and vector-store layer, not the graph data tier.

## Remediation

- **LightRAG operators:** set `auth_mode` to enabled; do not rely on the disabled default. Note that endpoint-level gating is independent of the global flag, so gate `/documents`, `/query`, and `/graphs` explicitly.
- **LightRAG platform:** remove `/health` from the no-auth skip-list, or strip `llm_binding`, `llm_model`, `embedding_model`, and `working_directory` from the unauthenticated response. The skip-list disclosure is a platform anti-pattern.
- **Qdrant operators:** enable the API key; the collection-management surface is fully open without it.
- **Ollama operators:** bind to localhost or front with auth; cloud-passthrough deployments shift cost and laundering risk to the paid upstream.
- **Vhost-routed RAG operators:** an origin host outside the proxy (F7) removes the WAF. Keep the RAG instance behind the same edge as the apex, or gate it directly.
- **Front-end operators (F6 class):** the public Vite `manifest.json` and inlined route table give a complete pre-auth endpoint map; restrict the legacy manifest path and treat the server-side editable system prompt as a prompt-injection surface.

## Codified insights

- **Insight #102 promoted to numbered.** GraphRAG namespace collision (`title:"GraphRAG"` = 46, all non-Microsoft) is the third independent platform-class confirmation of the dork-stage schema-anchor pattern for OSS-name-collision platforms.
- **Vhost undercount (extends Insight #69).** Vhost-routed AI services reject bare-IP probes (400/404/timeout); re-probe with a Host header from rDNS or cert SAN before declaring a host down. Bare-IP probing systematically undercounts the vhosted unauthenticated population.
- **`auth_mode=disabled` is not all-endpoints-open.** Two LightRAG hosts gate `/documents` 403 despite a disabled global flag. Endpoint-level gating is independent of the auth flag. Verify the endpoint, not the flag.
- **Health-endpoint skip-list config-disclosure.** A `/health` on a no-auth skip-list that returns provider/model/path metadata is a platform config-disclosure anti-pattern (LightRAG; check whether Langfuse and others share it).
- **Insight #106 (candidate), a 422 is a format mismatch, not an access denial.** F6 returned 422 to the OpenAI-idiomatic `{"messages":[...]}` shape; reading the validation body gave the real schema (`{"message":"...","chatHistory":[]}`) and the probe returned 200. A single-shape verifier would have closed F6 on the 422. 422 (and 400-with-validation-body) is the request-side dual of Insight #16: reshape and re-probe before declaring a chat/inference host denied. Single-shape verifiers systematically undercount bespoke-schema (non-hyperscaler) operators.

## Toolchain provenance

| Stage | Tool / mechanism | Output |
|---|---|---|
| -1 | OSINT Platoon (4 parallel research lanes) | Stage -1 intel doc + posture table; aimap FP gap list |
| 0 | Shodan in-page `fetch()` via authenticated Playwright MCP session | 549 candidates, every dork logged with hit count, 0 API credits |
| 0c | scanner (TCP/TLS banner, tarpit-strip, version, dork-FP strip) | 223 live -> 175 clean live; 48-host tarpit fleet stripped |
| 1b | aimap v1.9.55 (fingerprint + deep-enum, grouped-by-open-port) | 87 AI services; 67 LightRAG, 2 Qdrant, 1 Ollama, 8 Neo4j, 4 MCP |
| 1cm | agent-logging-system (per-enumerator FP-candidate scan) | flagged the loose LlamaIndex `/api/chat/config` match (F6 correction) |
| 3v | verify workflow (adversarial re-probe; 200-with-data earns the label) | confirmed F1-F7; refuted R1, R2; vhost Host-header recovery of F7 |
| 2 | attribution workflow (WHOIS + cert CN/SAN + rDNS + CT pivot) | 5 operator attributions; Hanssen, Babbid, Mobee, Qdrant pair, OVH gap |
| 4 | JS-bundle pass | F6 framework correction (Laravel/Inertia/Vue, not LlamaIndex SPA) |
| 6 | ledger ingest (nuclide.db) | findings persisted |
| 7 | scuba (compliance scoring) | severity/data-class scored |
| 8 | BARE (semantic exploit-module ranking) | modules ranked against findings |

Restraint ethic held end to end: metadata enumerated, nothing exfiltrated. `data_accessed=false` on every finding. Names and counts are the finding.
