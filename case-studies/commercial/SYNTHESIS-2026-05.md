# The Modern AI Stack Ships Open: Cross-Survey Synthesis

_NuClide Research · 2026-05-03_
_A synthesis of 13 platform-class surveys covering ~3,300 confirmed unique deployments across DigitalOcean, Hetzner, and Vultr cloud /16 ranges._

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

Total ingested into `data/nuclide.db`: **548 open findings** across all severity tiers, all with VisorScuba compliance scoring.

---

## References

- VisorLog findings ledger: https://github.com/Nicholas-Kloster/VisorLog
- VisorScuba compliance scoring: https://github.com/Nicholas-Kloster/VisorScuba
- VisorCorpus adversarial corpus generator: https://github.com/Nicholas-Kloster/VisorCorpus
- aimap AI/LLM service fingerprinter: https://github.com/Nicholas-Kloster/aimap
- Cross-survey index: [index.md](index.md)
