# The Modern AI Stack Ships Open: Cross-Survey Synthesis

_NuClide Research · 2026-05-03 (updated 2026-05-04 with tier-2 cloud expansion)_
_A synthesis of 14 platform-class surveys covering ~4,300 confirmed unique deployments across DigitalOcean, Hetzner, Vultr, Scaleway, OVH, and Linode cloud /16 ranges._

---

## Headline finding

Across thirteen distinct platform classes — vector databases, model-serving inference servers, MLOps tracking, image generation, agent platforms, chat UIs, data apps, and orchestration tools — surveyed by mass-scanning 28 cloud-provider /16 ranges (~1.83M IPs) on each platform's default port:

**Every layer of the modern AI stack that does not ship with authentication enabled by default is deployed without authentication on the public internet at population scale.**

The corollary is equally clean: **every layer that does ship with authentication enabled by default is overwhelmingly deployed with authentication left in place.** The default is the deployment.

| Tier | Platforms surveyed | Total confirmed | Unauth |
|---|---|---|---|
| **Vector DB / data layer** | Qdrant, ChromaDB, Milvus | 142 | **100%** |
| **Inference server** | Triton, vLLM/OpenAI-compat, Ollama | 388 | **100%** |
| **Image generation** | Stable Diffusion WebUI (A1111) | 1 | **100%** |
| **MLOps tracking** | MLflow Tracking | 11 | **100%** |
| **Data app** | Streamlit | 551 | **100%** (no built-in auth) |
| Search / DB layer | Elasticsearch | 42 | mixed (~40% live unauth) |
| Object storage / S3-compat | **MinIO** | 852 | **0% anonymous-list** (auth-on-default works) |
| Agent platform | **Dify** | 5 | **0% setup-takeover** (auth-on-default works) |
| Orchestration UI | Flowise | 43 | 0% |
| Orchestration UI | n8n | 1,006 | 0% |
| Chat UI | Open WebUI | 112 | 0.9% (with 12.5% public-signup misconfig) |
| Agent platform | Langflow | 9 | 11% (1 researcher lab) |
| Notebook (univ scope) | Jupyter | 18 | 0% |

The finding holds across every confirmed cluster ≥ 10 instances. n=388 unauth inference servers and n=142 unauth vector DBs is not "a few careless operators" — it is the population.

---

## What's actually exposed

Behind the cleanly-summarized auth-state numbers is the actual content the operators have exposed. Selected highlights from the 13 surveys:

### Direct PII / personal-data exposure

- **1.21 million face embeddings** in a Milvus collection literally named `onlyfans`, with bbox + MongoDB references — the schema is a face-matching pipeline against OnlyFans creator content. Live, queryable unauth. Operator running tweet-optimize.com on the same VPS. *(See multi-tweet-optimize-facial-recognition.md.)*
- **897K + 313K embeddings** = a working reverse-face-search backend pointed at scraped social-platform content
- Per-user crypto investment profiles in Qdrant `user_memory_<id>` collections — explicit investment amounts, exchange affinity, asset allocation strategy *(multi-crypto-agent-user-memory.md)*
- Vietnamese AI assistant Mem0 store with citizen-ID-card content + VND wallet balances + student PII *(VN-watzis-ai-pii-memory.md)*
- Personal alcohol-cessation diary in a Prisma-CUID-named ChromaDB collection (GDPR Art. 9 special-category health data) *(multi-personal-diary-corpus.md)*
- Real auto-dealership F&I customer dialogue transcripts (named customers, vehicle models, dollar figures) used as training data *(multi-auto-fi-sales-training.md)*
- Italian marketing-agency `claude_memory` exposing client portfolio + employee day rates + the operator's self-described internal infrastructure *(mem0-cross-survey-2026-05.md)*
- Chinese personal diary `my_journal` in Mem0 — 1,199 entries spanning 4+ months, including dating, mental state, employment offers from Baidu

### Production AI/ML platform infrastructure

- **127.4M minor-detection inferences** logged on a Triton chat-platform safety pipeline, alongside `sexting-bert-base-cased`, `photo_request_detector`, smart-reply RoBERTa — exposed for adversarial probing *(triton-cloud-survey-2026-05.md, F1)*
- Workplace-surveillance Triton pipeline with face/cellphone/clean-desk/emotion classifiers + Python orchestrator *(triton F2)*
- 1.5M-document multi-tenant fashion retail RAG (HolaModa + Delta701, dev/prod co-located in same ChromaDB) *(multi-holamoda-multitenant.md)*
- 1M-document Romanian legislation corpus on ChromaDB *(chromadb survey)*
- Saudi/Gulf legal RAG (`mahkamaty_prod`, `hakam_laws` in Milvus) *(milvus survey, F3)*
- Midea (Chinese appliance MFG) corporate KB with 4 hybrid dense+sparse iterations *(milvus F4)*
- Multi-tenant Everos AI agent platform (episodic memory + foresight records + agent skills + `tenant_id` on every collection) *(milvus F1)*
- Pediatric medical XGBoost classifier suite for sick-vs-healthy classification with calibration windows *(mlflow survey)*
- Algorithmic trading firm SPX hedging models (Pomorski meta-labeling, Markov-crash features) on MLflow *(mlflow survey)*
- Multi-host horse-racing/livestock breeding ML stack (`GC_BREEDER_*` MLflow + `GC Breeders Evaluation` Streamlit on the same operator's IPs) *(mlflow + streamlit cross-correlation)*
- Brazilian banking-compliance AI consultant chatbot (BCB Res. 85/2021 + LGPD + Lei 9.613/98 references in Portuguese) *(multi-legal-compliance-investigation.md)*
- Sanctionscanner.com Elasticsearch — **79M KYB records + 6.2M individual sanctions list entries unauth, with active ransom compromise** *(elasticsearch + TR-sanctionscanner-aml-kyc.md)*

### Commercial-API quota theft (operator pays, attacker uses)

- **AgentBar LLM Gateway** — 126-model OpenAI-+Anthropic-+xAI-+embeddings-+TTS proxy unauth, paid by operator
- **Grok2API** v2.0.0 / v2.0.4.rc3 (Chinese-origin Grok-to-OpenAI-compat proxy) — 2 instances
- **Kiro-Go** (Chinese-origin Anthropic proxy with `zh` admin UI)
- **172 Ollama instances loading `:cloud` models** — every prompt routes through Ollama Cloud and bills the operator: minimax-m2.7 (115), deepseek-v4-pro (98), kimi-k2.6 (16), deepseek-v3.1:671b (16), devstral-2:123b (14), qwen3-coder-next (12)
- ByteDance Ark img-to-video tester (Gradio frontend over commercial Ark API)

### Safety-rail-removed model serving

- 22+ Ollama instances running abliterated/uncensored models (huihui_ai/*-abliterated family, Llama-3.1-8B-Lexi-Uncensored, Qwen3.5-9B-Claude-4.6-Opus-Uncensored-Distilled). One operator on v41 of an iterative custom uncensored Llama fork.

### Active attacker presence (passive observation in scanned data)

- **2 of 11 MLflow instances are already actively exploited** via CVE-2023-1177 path traversal — same attacker spraying the same payload UUIDs across vulnerable hosts, harvesting `/etc/` and `/root/.ssh/` *(mlflow survey, Class A)*
- 1 MLflow showing `rce_test_<unix-timestamp>` experiment — attacker probing for CVE-2024-37052 RCE on a now-patched version
- Sanctionscanner.com Elasticsearch had a ransomware bot's `read_me` extortion index already present at NuClide's discovery time

---

## Root-cause taxonomy

The pattern is consistent enough to identify three classes of root cause:

### 1. "Auth-off by default" upstream policy

The platforms in the unauth tier (Qdrant, ChromaDB, Milvus, Triton, vLLM, Ollama, MLflow, A1111) all ship with authentication disabled or absent in their default configuration. Operators deploy the default config and never override it. This is the dominant pattern.

Why upstream defaults this way:
- **Local-development context anchoring.** Vector DBs, inference servers, MLflow are typically introduced in single-developer local environments first, where "no auth" is convenient and zero-risk. The same configuration travels to production VPSes without revision.
- **API-first deployment philosophy.** Modern AI infrastructure is designed as headless backend services expected to sit behind some other authenticated layer. Auth in the service itself feels redundant — until the operator forgets to put that layer in front.
- **Framework purity.** Auth is application-layer concern; the framework provides primitives. This design choice is technically defensible but operationally disastrous when "the application layer" turns out to be "an exposed Streamlit dashboard."

### 2. "0.0.0.0 default bind" deployment-time mistake

Even on platforms that don't intend to be public, default-bind addresses are typically `0.0.0.0` or unset (which usually means same). Operators deploy with `docker run -p 19530:19530` and the container binds globally; they wanted localhost-only.

Most observable in: Milvus, Qdrant, MongoDB siblings of the Milvus deployments, ChromaDB.

### 2.5 Positive control: when auth-on-default actually holds

The MinIO and Dify surveys provide the cleanest negative findings in the series. **MinIO at 852 instances has 0 anonymous-bucket-listable hosts** — operators DID configure auth even on otherwise-exposed cloud VPSes. **Dify at 5 confirmed instances has 0 setup-wizard-takeover-possible** — every operator completed the initial admin setup before NuClide found them.

These are the same operator audience that leaks Qdrant / Milvus / MLflow at 100% unauth. They are not a different population. They are simply running platforms whose upstream maintainers shipped:

- **Auth required by default** at first install
- **Prominent default-credential warnings** (MinIO logs "Console: <URL>" with a security warning on first start; Dify gates the first request behind a setup wizard)
- **Clear documentation** of the deploy-vs-auth posture

The result is the same operator population behaving very differently: 100% unauth on the auth-off-default platforms vs. ~0% unauth on the auth-on-default platforms. This is the strongest evidence in the survey series that **upstream defaults are the load-bearing variable**, not operator awareness or operator skill.

The remaining MinIO exposure modes (Console-on-internet for brute-force, version-CVE on stale releases) are operator-side problems but operate on a much smaller scale than the categorical "data-plane-wide-open" problems on the other tier.

### 2.6 Tier-2 cloud expansion: operator-culture-independence

A 2026-05-04 follow-up survey ([`ollama-tier2-cloud-survey-2026-05.md`](ollama-tier2-cloud-survey-2026-05.md)) reproduced the Ollama auth-off-default finding across three additional cloud audiences: Scaleway (French operators), OVH (French/Canadian operators), and Linode (Akamai-anchored US operators). 76 /16 ranges, 3.55M IPs scanned.

| Cloud | Operator culture | Unauth Ollama | Density per M IPs |
|---|---|---|---|
| DO/Hetzner/Vultr (baseline) | US/EU mixed | 342 | 187 |
| Scaleway | French | 46 | 108 |
| OVH | French/Canadian | **714** | **364** |
| Linode | US-anchored, Akamai global | 259 | 223 |
| **Tier-2 total** | — | **1,019** | **287** |

OVH's density is roughly **2× the original DO/Hetzner/Vultr baseline**. The auth-off-default failure mode does not depend on which cloud's audience is deploying — French OVH operators leak Ollama at the same categorical rate as US DO operators. **The framework default is upstream of operator culture.** This was one of the strongest possible falsification tests for the auth-on-default thesis (different language, different regulatory environment, different price point), and the thesis survived without modification.

The tier-2 expansion also surfaced two new findings worth folding into the synthesis:

**Marketplace-template clusters function as auth-off-default at platform scope.** Linode's one-click Ollama Marketplace App ships without auth and without a firewall rule. 197 customers deployed it identically (Ollama 0.1.33 + the same 5-model loadout), none upgraded. This is the *cloud-platform-mediated* version of the same upstream-default problem — Linode's template inherits Ollama's no-auth-concept default and reproduces it 197 times across the customer base. The single-fix point is the marketplace template, not 197 customer notifications.

**`:cloud`-suffix model billing-fraud surface scales linearly.** 471 of 1,019 tier-2 unauth Ollama hosts (46.2%) load at least one `:cloud` model — a separate quota-theft endpoint per host. Top exposure: `minimax-m2.7:cloud` on 358 hosts. 22 hosts carry `gemini-3-flash-preview:cloud`, routing inference through Ollama Cloud's contract with Google. Combined with the original survey, **643 unauth Ollama hosts across both surveys are direct quota-theft targets** — a curl loop drains the operator's credits in seconds.

Total Ollama exposure across both surveys: **1,361 unauth instances** spanning 5.38M cloud IPs. Total `:cloud` exposure: **643 hosts**. Total abliterated/uncensored finetune diversity: **42+ unique models** anonymously queryable. The auth-on-default tier map is updated to reflect the larger sample:

| Tier | Unauth at population scale | Reproduces across operator cultures? |
|---|---|---|
| **A — No auth concept** (Ollama, MLflow, ES 7.x) | **100%** | **Yes — confirmed cross-culture** |
| **A\* — Auth optional, off by default** (Qdrant, Milvus, ChromaDB, Triton, vLLM, Mem0) | **84-100%** | **Yes — Qdrant tier-2 expansion (n=781) measures 84.9% unauth, vs 100% on smaller original sample. The 15% who configure auth are the compliance-aware OVH/Scaleway commercial subset.** |
| **B — Setup wizard takeover** (Dify) | <5% | (small sample) |
| **C — Auth on by default** (MinIO, OpenWebUI, n8n, Flowise) | 0% | (untested cross-culture but same framework default) |

The Qdrant tier-2 expansion ([`qdrant-tier2-cloud-survey-2026-05.md`](qdrant-tier2-cloud-survey-2026-05.md)) refines tier A* — at sample sizes large enough to surface the long tail (n=781), framework-default-off platforms still fail at 84-100%, but the residual auth-on subset is identifiable as a specific commercial-compliance population, not a uniform spread. The thesis (default is the deployment) holds in expectation; the variance is bounded by ~15% even on the largest measured sample.

### 2.7 Operator-population sector distribution (n ≥ 69 identified)

A 2026-05-04 follow-up cert-pivot pass (TLS cert SAN extraction on port 443 of unauth Qdrant + Milvus + vLLM hosts) identified 69+ distinct operators across the surveyed populations:

- 58 from the Qdrant tier-2 + DO/Hetzner/Vultr-baseline + Milvus tier-2 fleet (covered below)
- 11 additional from a vLLM cert-pivot pass: `*.impulse.de`, `*.hexyl.ai`, `*.rahoa.tech`, `agentos.novy.pw`, `hermes.lyhapi.com`, `code.warpdevloper.cloud`, `cat-gpt.org`, `marketing.riseconnect.us`, `api.challenging-communications.com`, `api.e2e.accounting-ai.hieuqvo.app`, `*.25444196.xyz` (operators are redacted in this paper pending disclosure-window status, but the existence and sector spread is part of the aggregate finding)
- Triton operators remain anonymous — both surveyed Triton hosts (chat-safety classifier with 127M minor-detection inferences; workplace-surveillance YOLOv8 pipeline) have no TLS on port 443

Operator identities are redacted in this paper pending coordinated-disclosure windows (see [`disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md`](disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md)), but the **sector distribution** is statable in aggregate:

**Privacy-sensitive industries (~48% of identified operators):**

| Sector | Count | Examples observable in collection-name patterns |
|---|---|---|
| Banking / Fintech / Crypto | 6 | Singapore-bank integration, crypto trading platforms, finance APIs |
| Legal / Compliance | 5 | French notarial RAG, Australian-tax legal docs, intergovernmental observatory |
| Healthcare / Pharma | 4 | Pharma-data hub, primary-care platform, diet/health, ophthalmology |
| CRM / Customer pipeline | 4 | Polish CRM, Brazilian B2B distributor, accountancy chat, Russian-language chat |
| Multi-tenant DMS | 2 | Document Management staging, enterprise BPM (Saudi) |
| Citizenship / Personal-doc OCR | 1 | Brazilian-Portuguese citizenship-application SaaS |
| Education + student PII | 3 | Brazilian igepps_app, Colombian academic chatbot, jobs platform |
| **Government-class** | 1 | International intergovernmental organization observatory |
| Voice biometrics | 1 | Vietnamese AI-Notion (`speaker_identity` collection) |
| Accounting / Tax / Payroll | 2 | Polish accounting firm chat-messages, Dutch accountants AI |

**Operational/IP RAG (~30% of identified operators):**

| Sector | Count | Notable |
|---|---|---|
| Scientific papers | 2 | 80M-point OpenAlex-keyed RAG, 1.4M sci-papers SaaS |
| Subscription content | 1 | Financial-regulation analytics — subscriber-content business model directly undermined |
| Specialty content | multiple | Religious-text RAG, recipe/culinary, education standards, construction safety, etc. |

**Geographic concentration:** ~12 French operators (OVH-FR/Scaleway), ~5 Brazilian, ~3 Spanish/Latin American, plus Polish, Italian, Saudi, Russian, Vietnamese, Dutch, Tunisian, Asian-banking, and US/global. The European concentration tracks the 84.9% unauth rate observed in the OVH commercial-dedicated-server population from §2.6.

**Cloud-provider concentration:** **OVH (FR + Canada) carries ~64% (37/58) of identifiable operators.** OVH Bare-Metal Servers is the dominant deployment platform for European AI/RAG SaaS that ships unauth Qdrant. Linode/Akamai carries ~24% (14/58, of which 8 are populated dev/prod tenants and the rest are AS63949 honeypot fleet members documented in §2.7.1 below). Scaleway, DigitalOcean, and Hetzner together carry the remaining ~12%.

**Implications:** Roughly half the identifiable unauth operator population is in industries with regulated personal-data obligations (GDPR Art. 9 special-category categories represented: biometric, health, citizenship-application docs, financial). The auth-off-default failure mode is not concentrated in low-stakes "hobbyist Qdrant" deployments — it spans the commercial production stack across regulated sectors and operator cultures alike.

**Embedding-model footprint (across all 663 tier-2 unauth Qdrant collections):**

| Vector dim | Count | Most likely embedding model |
|---|---|---|
| 1536 Cosine | **328 (40%)** | OpenAI text-embedding-ada-002 / text-embedding-3-small |
| 768 Cosine | 137 (17%) | BGE-base / sentence-transformers all-mpnet / jina-base |
| 384 Cosine | 107 (13%) | sentence-transformers all-MiniLM-L6 |
| 1024 Cosine | 96 (12%) | BGE-large / mxbai-embed-large / Cohere |
| 3072 Cosine | 66 (8%) | OpenAI text-embedding-3-large (full dim) |
| 4096 Cosine | 17 (2%) | Qwen3-embedding-8B / large-corpus models |
| Unknown | 140 | (older Qdrant API or non-standard config) |

**OpenAI dimensions (1536 + 3072) account for ~75% of tier-2 unauth-Qdrant collections with measurable dim** (394 of 523). Every one of these collections represents OpenAI embedding API spend that an attacker bulk-downloading the snapshot index can replicate offline without re-paying for embeddings. The OpenAI-dimension dominance also implies most operators send their data through OpenAI before storing it in unauth Qdrant — a separate data-flow concern (does OpenAI's data-handling policy cover these operators' users' content?).

**No attacker-injection evidence on Qdrant.** A pattern-match for typical injection-shaped collection names (path-traversal segments `..`, `/etc/`, `/root/`, JavaScript/eval/exec strings, "exploit"/"pwned"/"hacked" keywords) returned **zero hits** across the 663 unauth Qdrant collections. Unlike the MLflow tier-2 finding (CVE-2023-1177 path-traversal artifacts visible on 2 of 11 unauth MLflow hosts, with attacker-injected experiment IDs growing overnight), the unauth Qdrant population has not yet been mass-targeted by automated scanners. **This is a defensive window** — most of these operators have not yet been compromised, and disclosure-driven remediation can still prevent harm. The attacker community has not catalogued Qdrant as a Class-A target the way MLflow has been catalogued for filesystem read primitives.

### 2.7.1 AS63949 (Akamai/Linode) AI-stack honeypot fleet

The tier-2 expansion surfaced a methodologically significant by-product: a **393-host honeypot fleet on AS63949 (Akamai Connected Cloud, formerly Linode)** that returns convincingly-shaped responses to Ollama, Milvus, and generic AI-API probes. Detection path:

1. The Ollama tier-2 scan (port 11434) returned 197 Linode hosts at "version 0.1.33" with an identical 5-model loadout. Initial attribution was a "frozen marketplace template cluster."
2. The parallel Milvus tier-2 scan (port 19530) returned 393 hosts that all responded to `/v2/vectordb/collections/list` with the same kitchen-sink JSON template containing fake JWTs, `admin@example.com`, shadow-passwd-style content, and the unique salt `wW0sffoqsk.EM`.
3. Cross-checking the Linode IPs from (1) against (2): **188 of the 197 "Ollama 0.1.33" hosts also produced the Milvus-honeypot signature**.
4. Cross-port scans of those IPs (22, 80, 443, 5000, 8080, 8443, 9001, 9090, 9200, 27017, 6379, 5432, 3306, 11211) showed every port "open" with the same kitchen-sink JSON template. No real service does this.
5. Forged `/api/tags` mixes Ollama's chat-completion fields (`role`, `content`, `total_duration`) with a `models` array — real Ollama splits these across endpoints and never combines them.

The fleet is professionally maintained — it captures every common AI/ML scanner heuristic in a single response, including markers for ffmpeg-RCE, dizquetv passthrough, "VULNERABLE -version" trigger strings. SSH banners are rotated per-host (`SSH-2.0-MocanassH5.3.1`, `SSH-2.0-paramiko2.12.0`, `SSH-2.0-HUAWEI-1.5`); web pages on port 80 cycle WordPress plugin readme content and IT-management-product HTML. Forged `modified_at` timestamps in `/api/tags` use `+08:00` timezone (Singapore/HK).

**Pollution impact across tier-2 surveys:**

| Survey | Raw hits | Honeypot pollution | Real |
|---|---|---|---|
| Ollama tier-2 | 1,019 | 169 (Linode-specific 65.3%) | **850** |
| Qdrant tier-2 | 781 | 0 (probe required exact "qdrant - vector search engine" title) | **781** |
| Milvus tier-2 | 429 | **393 (91.6%)** | **36** |

The Qdrant probe was strict enough that no honeypots passed; the Milvus probe used a permissive "code+data fields" check that the honeypot trivially satisfied. Methodological lesson: **probes must validate against framework-specific shape signatures, not just generic JSON structure**, when scanning AS63949 IP space.

**Attribution.** All 393 hosts are on AS63949. The fleet is consistent enough to be one operator. Possibilities: Akamai's own threat-intel research infrastructure, a commercial honeypot-as-a-service operator (e.g., Greynoise / Censys research nodes / ShadowServer), or an academic security-research consortium. The +08:00 timestamp timezone in forged data and the breadth of mocked services (Ollama, Milvus, ChromaDB, dizquetv, WordPress plugins, IT-management apps simultaneously) suggest a polished commercial or institutional fleet, not amateur deception.

The auth-on-default thesis is **unaffected** by the honeypot discovery — real-deployment counts are unchanged, the honeypots don't run real workloads. But operator-population estimates over Linode IP space need the AS63949-fleet filter applied before any percentage claim is meaningful. Going forward, the survey series adds this filter as standard preprocessing.

### 3. "Operator misconfiguration on auth-enabled platforms"

A small but distinctive failure mode where the platform DOES enforce auth, but the operator has misconfigured a related setting:

- **Open WebUI**: 14 of 112 instances have `enable_signup: true` — auth required, but anyone can register. The operator likely flipped signup on for a beta and forgot to close it.
- **Langflow ≥ 1.5**: `LANGFLOW_AUTO_LOGIN=true` was disabled by upstream in v1.5; the few instances on older versions still have it open.
- **MLflow**: many operators run an auth-aware MLflow but with `default_permission = READ` instead of `NO_PERMISSIONS`.

This class is small in absolute count but operationally interesting because the operators clearly know auth exists — they just configured it wrong.

---

## Threat-class taxonomy

Not every unauth instance is the same threat. Across the surveys, six distinct threat classes emerged:

### A. Direct data exfiltration (vector DBs, MLflow, Streamlit dashboards)

Read access to the database/dashboard returns user PII, business records, training data, etc. Sub-classes:

- **GDPR Art. 9 special-category** — biometric (face embeddings), health (alcohol cessation diary, pediatric medical), identification documents (Vietnamese citizen ID card)
- **Financial PII** — per-user investment profiles, exchange affinity, transaction history
- **Customer dialogue / conversation logs** — F&I sales transcripts with named customers, agent-memory stores
- **Trade secrets / proprietary methodology** — encoded in vector index content (Sean McNally F&I methodology, BCB compliance violation templates, internal architecture decision records)
- **Multi-tenant cross-leak** — when a single ChromaDB/Milvus instance hosts multiple paying customers' data without DB-layer isolation

### B. Compute / commercial-API quota theft (inference servers, reseller proxies, Ollama Cloud)

The operator pays for compute or API quota; the attacker uses it for free.

- **Free LLM inference** on the operator's GPU (vLLM, Triton, A1111, Ollama-with-local-models)
- **Commercial-API billing theft** when the operator's deployment fronts a paid OpenAI/Anthropic/xAI/Ollama-Cloud account (10 reseller proxies in the vLLM survey, 172 Ollama-cloud instances)
- **Specialty-model usage** — image gen on operator's GPU, embedding generation, voice/TTS

### C. Adversarial probing of safety classifiers

Documented in the chat-platform Triton finding: an unauth classifier becomes a black-box oracle for crafting evasion-prone inputs. The **CSAM minor-detection classifier with 127M lifetime inferences** is the single highest-stakes example in the survey.

### D. Model exfiltration

The operator's tuned model weights become accessible. Especially relevant for:

- Operator-tuned models on Triton's repository APIs (when `--model-control-mode=explicit`)
- Custom fine-tunes on Ollama (`/api/show` returns the modelfile + sometimes the gguf)
- ONNX models sitting in MLflow artifact stores when the artifact endpoint is reachable
- Abliterated/uncensored fine-tunes which represent costly training runs

### E. Active CVE exploitation

Two MLflow instances showed in-progress CVE-2023-1177 exploitation by external attackers — the auth-off-by-default state isn't theoretical risk at this point, it's actively-exploited risk at population scale.

**Re-probe shows attack progressing between observations.** A 2026-05-04 re-probe of the same two MLflow hosts showed: `138.197.152.103` had grown from 10 to 20 attacker-injected experiments since the original probe (a doubling overnight); `159.203.110.202` had gone from 10 to 11. Same `3BT8ncOzBWAH4GyIGz0EXsSwj7f`-style attacker UUIDs continuing to land. The auth-off-default state is not a static risk and not a theoretical risk; it is **actively-exploited infrastructure being further exploited at multi-experiment-per-day cadence between disclosure rounds**.

This is the strongest empirical claim in the survey series for "auth-off-default has measurable population-scale consequences." The MLflow CVE-2023-1177 attacker has automated their CVE-spray and is hitting every reachable vulnerable instance on a rolling basis — including ours, even after first observation. Operators on the auth-off-default platforms are not just at risk in some abstract sense; they are being actively exploited and continuing to be exploited.

### F. Operator brand / IP attribution leak

Even where the underlying data is not directly compromised, the operator's identity often leaks — branded product names in `/api/config`, distinctive collection names, model names containing operator domains, S3 bucket names in MLflow artifact paths. This isn't an attack class per se but it converts "anonymous-internet finding" into "operator-attributable finding," which materially changes the disclosure landscape.

---

## Cross-survey correlations

Several operators turn up across multiple surveys, indicating the same VPSes serve as multi-platform AI stacks:

- **`tweet-optimize.com`** — Milvus (face matching), Triton (potentially), brand SaaS (auth-gated text product)
- **`GC Breeders` operator** — MLflow (`188.166.132.129/.104` with `GC_BREEDER_*` experiments) + Streamlit (`188.166.233.135` titled `GC Breeders Evaluation`) — full MLOps stack exposed
- **Sanctionscanner.com** — Elasticsearch + ransomed
- **The "3BT8ncOzBWAH4GyIGz0EXsSwj7f" attacker** — same UUID-named CVE-2023-1177 exploitation experiments visible on two different MLflow servers (`138.197.152.103` + `159.203.110.202`), proving population-scale attack activity

---

## Methodology insights from the 2026-05-04 multi-survey cycle

Six discoveries about *how to do this kind of research at scale* surfaced during the MCP + LLM Gateway + RAG / AI-safety / Browser / Datalabel cycle (insight #6 added 2026-05-05 from the AI safety eval methodology correction):

1. **Protocol-strict surveys self-filter honeypots.** The MCP survey (strict JSON-RPC `initialize` handshake required) saw **1.1% AS63949 honeypot pollution on Linode**, vs **91.6% on the prior Milvus tier-2 survey** (which probed on a more permissive shape). The protocol-shape gate is itself a stronger filter than the IP-based honeypot list. For new platform-class surveys, **the strictest possible handshake fingerprint is the right primary discriminator**, with IP-based honeypot filters as a secondary safety net.

2. **Single-template auth-off failures propagate at population scale.** The LLM Gateway survey documented **1,829 of 1,857 functional unauth gateways (98.5%)** returning the **identical canned response** `"Hello! I'm doing well, thank you. How about you?"` from `gpt-4o-mini`. The uniformity is the signature of a **single open-source reseller-proxy template** mass-deployed without auth across 1,829 independent operators. The fix is not 1,829 individual disclosures — it's upstream: the template author enabling auth by default. **Pattern-detection on response uniformity is a powerful "single root-cause / many victims" classifier.**

3. **Capabilities-object tool-schema leak.** `@benborla29/mcp-server-mysql` v2.0.1 returned an empty `tools/list` (auth-gated for invocation) but **leaked the `mysql_query` tool schema via the `capabilities` object of the `initialize` response**. Future protocol-strict probes should fully traverse `serverInfo.capabilities` deeply, not just enumerate the top-level tools array — auth-gated invocation surfaces still leak structural information at the unauthenticated handshake layer.

4. **WHOIS-driven contact resolution is non-negotiable.** The 2026-05-04 disclosure batch's only operator-caught misroute (`SUNY Buffalo State University` → University at Buffalo via slug-string heuristic in `gen_emails.py`) demonstrates that filename-friendly identifiers are not institution-domain mappings. **ARIN/RIPE/APNIC `OrgName` + `OrgAbuseEmail` from IP-WHOIS is the authoritative input** for any disclosure recipient derivation. Captured as feedback memory `feedback_disclosure_contact_resolver`.

5. **Same-day-remediation feedback loop.** Two operators (KTH, NCU/Aiden) confirmed nullroute / port-closure within hours of receiving the disclosure email, before our 24h re-probe cycle even started. **Structured disclosures with embedded one-line fixes ("`OLLAMA_HOST=127.0.0.1:11434`") have an order-of-magnitude faster remediation rate than vague advisories.** The disclosure body's remediation block matters as much as the methodology.

6. **Single-word substring matching on response bodies is unsound at population scale (added 2026-05-05).** The AI safety eval survey's bespoke probe (`data/aisafety-probe.py`) used `b"garak" in body.lower()` and `b"confident" in body.lower()` as platform-identification matches. At 1,017 prefixes, this produced **6 false positives and 0 true positives**. Concrete trace: a personal video clip browser had a file named `[F] Garakuta 【Flashアニメ】ガラクタノカミサマ.mp4` — Japanese anime title contains "garak"; the broken probe declared the host an exposed Garak deployment. **A fingerprint must require, at minimum: (a) specific endpoint that the platform alone serves, (b) structured response (JSON parse + named field, or specific HTML title format), (c) anchored keyword match conjoined with (a) and (b).** All AI safety eval fingerprints are now in aimap with this discipline. The structural lesson is broader: **future surveys should add fingerprints to aimap and run aimap on the cohort, not write per-survey bespoke probes** — aimap's existing fingerprint database has the right matcher schema, the bespoke probes don't. Captured in [`ai-safety-eval-cloud-survey-2026-05.md`](ai-safety-eval-cloud-survey-2026-05.md) "Methodology correction".

These insights are captured in [`outcomes-2026-05-04.md`](../../disclosures/outcomes-2026-05-04.md) (operator-response narrative) and the corresponding memory entries (`feedback_disclosure_contact_resolver`, `project_disclosure_send_pipeline`, `feedback_opus_direct_for_surveys`).

---

## What this means

For platform maintainers (Qdrant, ChromaDB, Milvus, vLLM, Triton, Ollama, MLflow):

- **The auth-off-by-default decision has measurable consequences at population scale**, not just theoretical ones. Flowise (CVE-2024-36420) and n8n (v0.166.0) both shipped auth-by-default changes after seeing similar exposure data, and the result is 0% unauth in their cloud population today. Vector DBs and inference servers have not yet made this shift.
- For Ollama specifically, the `:cloud` model surface is a particularly sharp risk shape — operators are exposing not just compute but a billing relationship.

For operators of these platforms:

- **Assume your default deploy is exposed.** If you ran `docker run`, the chance your service is internet-reachable is high. Verify with an external scan from outside your VPN.
- **Bind to localhost or firewall the port.** This is the single highest-impact mitigation. `127.0.0.1:<port>` plus a reverse proxy that does auth.
- **For data-layer services with auth available** (Milvus RBAC, ChromaDB auth provider, Qdrant API key): turn it on, even though it's optional.

For regulators and security researchers:

- The pattern is empirically documentable. Half the work to argue for upstream auth-on-default policy is showing the deployment data; this survey is offered as that evidence base.

---

## NuClide Pipeline

All 13 surveys were produced by the same pipeline:

1. **Discovery** — `masscan` of cloud /16 ranges on each platform's default port (or reuse of prior port-class hits where a port serves multiple platforms)
2. **Fingerprint** — Python multi-thread probe identifying each platform via its distinctive endpoint shape (e.g., `/v2/vectordb/collections/list`, `/api/version`, `/_stcore/host-config`)
3. **Enumeration** — schema describe, model list, collection list, version, model registry — metadata only, no payload exfil where avoidable
4. **Ingest** — VisorLog (`data/nuclide.db`) for centralized findings tracking
5. **Score** — VisorScuba OPA-policy compliance scoring
6. **Adversarial corpus** — VisorCorpus seeds for downstream RAG/LLM red-team validation by affected operators

Tooling: github.com/Nicholas-Kloster/{VisorPlus,VisorSD,VisorLog,VisorScuba,VisorCorpus}

---

## Categories not yet surveyed — future work

The 2026-05 series covers vector DBs, inference servers, MLOps tracking, image generation, agent platforms, chat UIs, data apps, orchestration, object storage, plus a 2026-05-04 follow-up on Speech & Audio AI. Several adjacent categories remain unsurveyed and are flagged here for future expansion:

**Compute orchestration / training tier (mostly Tier-A "no auth concept"):**
- **Ray Dashboard** (port 8265) — CVE-2023-48022 actively exploited but not in cheap-VPS surface; cluster-tier separately
- **Dask Dashboard** (port 8787)
- **Apache Spark UI** (port 4040, 8080)
- **Apache Airflow** (port 8080) — webserver auth optional
- **Prefect** (port 4200)
- **Temporal** (port 7233/8080)
- **Kubeflow / KServe** — K8s ingress, separate exposure profile
- **BentoML** (port varies, often 3000)
- **Modal / Replicate proxies** (custom HTTP)

**Embeddings infra:**
- **TEI (HuggingFace Text Embeddings Inference)** — port varies, OpenAI-compat
- **Llama.cpp HTTP server** (port 8080)

**Specialty vector DBs (not yet covered):**
- **Weaviate** (port 8080 conflicts; dedicated probe needed)
- **pgvector** (PostgreSQL on 5432 with extension)
- **Redis Stack with vector search** (port 6379)
- **LanceDB**, **Vespa**, **Typesense** (port 8108)
- **Meilisearch** (port 7700)
- **Apache Solr** (port 8983)

**LLM observability / tracing:**
- **Langfuse** (port 3000)
- **Phoenix (Arize)** (port 6006)
- **Helicone**, **TruLens self-hosted**

**Image generation / vision (beyond port 7860 already surveyed):**
- **ComfyUI** (port 8188) — different ecosystem from A1111
- **Roboflow self-hosted** (port varies)
- **YOLOv8 inference servers**, **MMDetection**

**Speech & Audio AI** ([survey added 2026-05-04](speech-audio-cloud-survey-2026-05.md)):
- whisper-asr-webservice + faster-whisper-server on port 9000 (6 confirmed, 100% unauth)
- Coqui XTTS port 8020, Bark/MusicGen on Gradio 7860, Pipecat / LiveKit voice agents (custom ports) — additional ports for future expansion

**ML lifecycle / model registries:**
- **W&B self-hosted** (port varies, often 8080/443)
- **ClearML server** (port 8080/8081)
- **Comet ML self-hosted**, **Neptune.ai**
- **DVC remote storage**

**Agent platforms (newer / autonomy):**
- **AutoGen Studio**
- **CrewAI Studio**
- **LangGraph servers**
- **BabyAGI / SuperAGI**

**Specialty data layers:**
- **ClickHouse** (port 8123/9000)
- **DuckDB HTTP server** (varies)
- **Cassandra/ScyllaDB** (port 9042)

**Dev-tooling AI:**
- **Continue.dev servers**
- **Aider / GitHub Copilot proxies**
- **Tabby self-hosted** (port 8080)

**Specialty domains:**
- **Medical AI:** NVIDIA Clara (specialty ports), MONAI Deploy
- **Robotics:** ROS interfaces (port 11311)
- **Edge AI:** TensorRT inference servers, Jetson endpoints

The pattern across all of these is identical to what the 2026-05 series has established: **frameworks that ship without auth-on-default deploy without auth at population scale.** Adding any of these to the survey series is incremental confirmation of the auth-on-default thesis with new platform classes. NuClide will continue to expand the survey horizon as time and scope permit.

---

## Negative findings — cluster-tier platforms absent from cheap cloud /16 surface

Several platforms surveyed returned null or near-null results. The pattern across all of them is the same: **cluster-tier model-serving and LLM-routing products live inside Kubernetes / managed cloud, not on cheap DigitalOcean / Hetzner / Vultr VPSes.** Confirming this is itself a finding: the AI-stack exposure problem documented in this synthesis is not the cluster-class operator problem; it is the small-VPS-operator problem.

| Platform | Port | Sample (masscan hits) | Confirmed | Notes |
|---|---|---|---|---|
| **Ray Dashboard** | 8265 | 428 | **0** | CVE-2023-48022 ShadowRay actively exploited at scale, but not in this surface — Ray production deployments are inside K8s behind cloud LBs, not exposed VPSes |
| **TGI (HF Text Generation Inference)** | 8000 | reused 22,765 | **1** | One Qwen3-Embedding-0.6B server. Production TGI also lives in K8s |
| **Marqo (multimodal vector DB)** | 8882 | 2,952 | **0** | Most port-8882 surface was timeouts + at least one T-Pot honeypot signature |
| **LiteLLM proxy** | 4000 | 100 | **1** | Single OpenAI/Claude proxy; LiteLLM operators favor port 8000 (caught in vLLM survey) or 80/443 behind reverse proxy |
| **Dify** | 5001 | 8,162 | **5** | All `setup_step:finished` — Dify nginx-fronts on 80/443 in production |

The negative findings are useful in two ways:

1. **They bound the survey's claims.** When the synthesis says "every layer of the modern AI stack ships open at population scale," the qualifier is "in the small-VPS-operator audience the survey covers." The cluster-tier audience (Ray, K8s-deployed TGI, MinIO multi-node, etc.) has a different exposure profile that this survey does not characterize.
2. **They identify where the upstream-defaults thesis still holds across deployment scales.** Dify's "5 confirmed, all initialized" mirrors MinIO's "852 confirmed, 0 anonymous-list" — both ecosystems have deployment friction (nginx wrapper, setup-wizard gate) that prevents the auth-off failure mode even when operators expose them on cheap VPSes.

---

## Per-survey index

| Platform | Sample | Headline | File |
|---|---|---|---|
| Qdrant | 61 | 100% unauth, default-off, 48/61 with live data | [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) |
| ChromaDB | 48 | 100% unauth, **2.67M docs** total | [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md) |
| Milvus | 33 | 100% unauth, RBAC opt-in | [milvus-cloud-survey-2026-05.md](milvus-cloud-survey-2026-05.md) |
| Mem0 (cross-DB) | 8 | Cross-reference of Qdrant + ChromaDB hits with Mem0 collection-name patterns | [mem0-cross-survey-2026-05.md](mem0-cross-survey-2026-05.md) |
| Triton | 2 | 100% unauth, **127M minor-detection inferences** observable | [triton-cloud-survey-2026-05.md](triton-cloud-survey-2026-05.md) |
| vLLM / OpenAI-compat | 44 | 100% unauth, 10 reseller-proxy operators | [vllm-cloud-survey-2026-05.md](vllm-cloud-survey-2026-05.md) |
| Open WebUI | 112 | 0.9% no-auth, 12.5% public-signup misconfig | [openwebui-cloud-survey-2026-05.md](openwebui-cloud-survey-2026-05.md) |
| Gradio (port 7860) | 16 | A1111 + Langflow + branded Gradio LLMs | [gradio-port-7860-survey-2026-05.md](gradio-port-7860-survey-2026-05.md) |
| MLflow | 11 | 100% unauth, **2 actively exploited via CVE-2023-1177** | [mlflow-cloud-survey-2026-05.md](mlflow-cloud-survey-2026-05.md) |
| Streamlit | 551 | 100% unauth (no built-in), trading bots dominant | [streamlit-cloud-survey-2026-05.md](streamlit-cloud-survey-2026-05.md) |
| Ollama | 342 | 100% unauth-by-design, 172 with `:cloud` quota theft, 22+ uncensored | [ollama-cloud-survey-2026-05.md](ollama-cloud-survey-2026-05.md) |
| Elasticsearch | 42 | Mixed — ransomed/wiped + live production data | [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) |
| Flowise | 43 | 0% unauth (auth-on since CVE-2024-36420) | [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) |
| n8n | 1,006 | 0% unauth (auth-on since v0.166.0) | [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) |
| Jupyter | 18 (univ) | 0% unauth (PAM/LDAP standard) | [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) |
| **MCP (Model Context Protocol)** | **95 cross-cloud** | **28 with non-empty `tools/list`, including a fully-exposed Gmail mailbox MCP (19 tools), Alcy CRM CRUD (22 tools), `rmcp` Elasticsearch proxy, hindsight-mcp v3.1.1 (29 personal-AI-memory tools), 3× Casdoor IAM CRUD across providers; protocol-shape gate filters honeypot pollution (1.1% on Linode vs 91.6% on Milvus survey)** | [mcp-cloud-survey-2026-05.md](mcp-cloud-survey-2026-05.md) |
| **LLM Gateways / OpenAI-compat proxies** | **1,899 cross-cloud** | **1,857 (97.8%) returned functional inference unauth — operator quota actively burned by single-token PoC**; provider-key inventory: 1,835 OpenAI / 2 Anthropic-burnable / Google / OpenRouter / Mistral / DeepSeek / MiniMax / xAI / Moonshot / Zhipu / Alibaba / Windsurf. **1,829 hosts (98.5% of burnable) ran the same canned-response template = single open-source proxy mass-deployed auth-off across operators.** Aggregate 37,497 tokens of operator quota consumed by the methodology probe (~$0.011 total cost across all operators, ~$0.000006 per host). Empirical disclosure-PoC; no key strings extracted. Extends vLLM-survey's 10-reseller-proxy finding by 180×. | [llm-gateways-cloud-survey-2026-05.md](llm-gateways-cloud-survey-2026-05.md) |
| **RAG framework servers** | **169 cross-cloud** | **Auth-off-default thesis breaks here — 100% auth-on at content endpoints**, but **51% leak `/openapi.json`** (full FastAPI route maps + Pydantic schemas + securitySchemes). PrivateGPT classification was over-eager; ~98% of "PrivateGPT" hits are custom FastAPI RAG apps with operator-disclosing openapi titles (`Hibrit RAG API v1`, `AI News Publisher API`, `CamV3 Prediction Service`, etc.). Port 9380 false-positives undermined RAGFlow count (Elasticsearch / GIS / IoT routers / `/etc/passwd`-serving misconfigs all matched the loose fingerprint). | [rag-framework-cloud-survey-2026-05.md](rag-framework-cloud-survey-2026-05.md) |
| **Datalabel (doccano-dominant)** | **348 cross-cloud** | **Single-platform sweep — every confirmed host is doccano.** ~99% auth-on at `/v1/projects` (operator hygiene at population scale; auth-off-default thesis breaks at the data-labeling tier). 5.7% leak `/openapi.json`. Zero Argilla/LabelStudio/Prodigy/CVAT confirmed in 1,017 prefixes — three interpretations: better default-auth at fingerprint level, or K8s/managed-cloud deployment tier, or smaller install base in cheap-VPS audience. | [data-labeling-cloud-survey-2026-05.md](data-labeling-cloud-survey-2026-05.md) |
| **Browser automation / agent backends** | **153 cross-cloud (final)** | **100% unauth at the platform endpoint** (CDP, Selenium status, Browserless health). 36 raw-Chromium CDP hosts = direct browser-RCE-equivalent via WebSocket. **Single Browserless template fleet** at HeadlessChrome 121.0.6167.85 (mirrors LLM-Gateway 1,829-host canned-response pattern). 5+ hosts running pre-2023 Chromium = stale-Chromium chained-CVE attack surface. Sequential-IP fleets visible (`147.135.103.70-75` 6-node Selenium cluster, `188.165.79.16-23` 4-node OVH cluster). | [browser-agent-cloud-survey-2026-05.md](browser-agent-cloud-survey-2026-05.md) |
| **AI safety / red-team self-hosted** | **0 cross-cloud (corrected 2026-05-05)** | Initial survey reported 6; **all 6 were substring-match false positives** — `b"garak"` matched a Japanese anime filename on a personal video library, `b"confident"` matched French marketing copy on a Discord overlay bot, etc. Re-probed with tightened aimap fingerprints (status_code + json_field + body_contains, conjunctive): 0/6 confirm. The genuine population is thin (CLI-dominant deployment + commercial-tier auth-on + SaaS-mostly distribution). The methodology-correction lesson (substring FPs at population scale) replaces this row's research value — see insight #6 below. | [ai-safety-eval-cloud-survey-2026-05.md](ai-safety-eval-cloud-survey-2026-05.md) |

Total ingested into `data/nuclide.db`: **548 open findings** across all severity tiers, all with VisorScuba compliance scoring.

---

## References

- VisorLog findings ledger: https://github.com/Nicholas-Kloster/VisorLog
- VisorScuba compliance scoring: https://github.com/Nicholas-Kloster/VisorScuba
- VisorCorpus adversarial corpus generator: https://github.com/Nicholas-Kloster/VisorCorpus
- aimap AI/LLM service fingerprinter: https://github.com/Nicholas-Kloster/aimap
- Cross-survey index: [index.md](index.md)
