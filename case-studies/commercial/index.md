# Commercial AI Infrastructure Exposures

_NuClide Research — ongoing · Updated 2026-05-03_

Commercial / SaaS Ollama and AI infrastructure exposures discovered during OSINT sweeps. These differ from university and research-network exposures in that the operators are commercial entities with paying customers and PII pipelines.

> **2026-05 cross-survey synthesis:** [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) — pulls together all 13 platform surveys (~3,300 confirmed deployments) into one analysis: tier-by-tier auth-posture comparison, root-cause taxonomy, threat-class taxonomy, cross-survey operator correlations.

---

## Confirmed Findings

| File | Operator | Country | Severity | Key Finding |
|------|----------|---------|----------|-------------|
| [FR-emails-pro-rdv-bot.md](FR-emails-pro-rdv-bot.md) | emails-pro.fr (hosted on Romanian ICI IP space) | France / Romania | CRITICAL | Production French commercial appointment-booking SaaS — full system prompt + PII collection schema + function-call format exposed |
| [TR-sanctionscanner-aml-kyc.md](TR-sanctionscanner-aml-kyc.md) | sanctionscanner.com (168.119.90.62, Hetzner DE) | Turkey / Germany | CRITICAL | AML/KYC compliance SaaS — 79M KYB records + 6.2M individual sanctions list entries unauth; active ransom compromise; disclosed 2026-05-03 |
| [VN-watzis-ai-pii-memory.md](VN-watzis-ai-pii-memory.md) | Watzis / Calmio AI assistant (149.28.77.155, Vultr) | Vietnam | HIGH | Vietnamese AI assistant — Mem0 long-term memory store unauth; citizen ID card + VND wallet + student PII in plaintext; multiple users confirmed |
| [multi-pingu-trading-ai.md](multi-pingu-trading-ai.md) | Unknown operator (45.76.20.46, Vultr) | Unknown | HIGH | Pingu crypto trading AI + Nova molecular optimization — 25 Qdrant collections unauth; live trade PnL, full LLM reasoning traces, competition leaderboard |
| [multi-legal-compliance-investigation.md](multi-legal-compliance-investigation.md) | Unknown operator (167.172.120.218, DigitalOcean) | Unknown | CRITICAL (if populated) | Legal/compliance investigation platform schema exposed unauth — investigation_data, case_drafts, attachments collections; empty at probe time; flagged for re-probe |
| [multi-auto-fi-sales-training.md](multi-auto-fi-sales-training.md) | Unknown operator (104.131.60.234, DigitalOcean) | Unknown (Sean McNally methodology) | HIGH | Auto F&I sales training RAG — real customer dialogues with names + vehicles + dollar figures, Sean McNally methodology IP, 1,608 docs unauth ChromaDB |
| [multi-crypto-agent-user-memory.md](multi-crypto-agent-user-memory.md) | Unknown operator (159.203.117.193, DigitalOcean) | Spanish-language LatAm/Spain | HIGH | Crypto investment agent — per-user financial profiles ($50K targets, exchange affinity, asset allocation) in user_memory_<id> collections; 12 collections, 15.9K docs unauth |
| [multi-holamoda-multitenant.md](multi-holamoda-multitenant.md) | HolaModa + Delta701 (46.101.118.246, DigitalOcean) | Unknown (Mexican/Spanish?) | CRITICAL | Multi-tenant fashion retail RAG — 2 tenants + dev/prod co-located on one ChromaDB; 1.53M docs across 7 collections unauth; Vertex AI text-embedding-gecko |
| [multi-personal-diary-corpus.md](multi-personal-diary-corpus.md) | Unknown Prisma SaaS (188.166.71.44, DigitalOcean) | Belgium/France inferred | HIGH | Multi-tenant document SaaS — Prisma CUID per-user collections expose personal alcohol-cessation diary (GDPR Art. 9), theater scripts with author emails + Belgian phones, public-domain texts |
| [multi-tweet-optimize-facial-recognition.md](multi-tweet-optimize-facial-recognition.md) | tweet-optimize.com (65.108.107.240, Hetzner FI) | Finland (Hetzner DC) | CRITICAL | **1.21M face embeddings unauth on Milvus** — onlyfans (897K) + psos (313K) collections with bbox + mongo_id refs. Worst-case interpretation: a doxing-as-a-service backend exposed on the public internet via unauth `/entities/search` |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | sanctionscanner.com (168.119.90.62, Hetzner DE) | Turkey / Germany | CRITICAL | AML/KYC compliance SaaS — 79M KYB records + 6.2M individual sanctions list entries unauth; active ransom compromise; disclosed 2026-05-03 |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Multiple operators | Various | HIGH | 61/61 Qdrant instances unauth across DO/Hetzner/Vultr — crypto trading AI, Vietnamese PII in agent memory, internal SOPs, legal compliance platform |

---

## Cross-Provider Surveys

Aggregate auth-posture studies across cloud-hosting providers (DigitalOcean, Hetzner, Vultr, etc.) for specific platform classes.

| File | Platform | Sample | Result |
|------|----------|--------|--------|
| [flowise-cloud-survey-2026-05.md](flowise-cloud-survey-2026-05.md) | Flowise | 43 instances across DO/Hetzner/Vultr | 0 unauthenticated — operator hygiene post-CVE-2024-36420 has improved on cloud platforms |
| [n8n-cloud-survey-2026-05.md](n8n-cloud-survey-2026-05.md) | n8n | 1,006 instances across DO/Hetzner/Vultr | 0 unauthenticated — mandatory auth since v0.166.0 fully adopted on cloud platforms |
| [jupyter-survey-2026-05.md](jupyter-survey-2026-05.md) | Jupyter / JupyterHub | 18 confirmed university instances (Berkeley, ETH, Cambridge, NTU, INHA, NCCU) | 0 unauthenticated — JupyterHub PAM/LDAP auth standard across all surveyed institutions |
| [qdrant-cloud-survey-2026-05.md](qdrant-cloud-survey-2026-05.md) | Qdrant | 61 instances across DO/Hetzner/Vultr | 100% unauthenticated — ships auth-off by default; 48/61 contain live data |
| [chromadb-cloud-survey-2026-05.md](chromadb-cloud-survey-2026-05.md) | ChromaDB | 48 instances across DO/Hetzner/Vultr | 100% unauthenticated — ships auth-off by default; 22/48 populated; **2.67M documents** total exposed |
| [milvus-cloud-survey-2026-05.md](milvus-cloud-survey-2026-05.md) | Milvus | 33 instances across DO/Hetzner/Vultr | 100% unauthenticated — RBAC opt-in; 27/33 populated; multi-tenant Everos AI agent platform, Saudi legal RAG, Midea KB, image+facial pipelines |
| [triton-cloud-survey-2026-05.md](triton-cloud-survey-2026-05.md) | NVIDIA Triton Inference Server | 2 instances on DO | 100% unauthenticated — chat-safety pipeline w/ 127M-inference minor-detection classifier (159.203.42.211), workplace-surveillance YOLOv8 pipeline (178.62.225.198) |
| [vllm-cloud-survey-2026-05.md](vllm-cloud-survey-2026-05.md) | vLLM / OpenAI-compatible LLM servers | 44 instances across DO/Hetzner/Vultr | 100% unauthenticated — 19 vLLM + 25 generic; **10 commercial-API reseller proxies** (Grok2API, Kiro-Go, AgentBar) burning operator credits on every external prompt; sipgate + Infomaniak proprietary fine-tunes attributable; Llama-3.3-70B-AMD, gpt-oss-120b, Qwen3-235B + Kimi-K2.6 clusters, Pixtral-12B all exposed |
| [openwebui-cloud-survey-2026-05.md](openwebui-cloud-survey-2026-05.md) | Open WebUI (Ollama/OpenAI-compat chat UI) | 112 instances across DO/Hetzner/Vultr | 99.1% auth-enforced (different finding shape) — but **14 instances with `enable_signup: true` (anyone can register)**, 5 branded deploys identifiable (Aera IA, TopicalBase, Tuuci AI, CloudU3, Lexa fork) |
| [gradio-port-7860-survey-2026-05.md](gradio-port-7860-survey-2026-05.md) | Gradio / A1111 / Langflow on port 7860 | 16 instances (9 Langflow + 1 A1111 + 6 Gradio) | A1111 (167.172.175.48) fully open w/ dreamshaper + 3 models; 1 unauth Langflow is a CVE-research lab (excluded from disclosure); 6 branded Gradio LLMs incl. ByteDance Ark commercial-API tester |
| [mlflow-cloud-survey-2026-05.md](mlflow-cloud-survey-2026-05.md) | MLflow Tracking Server | 11 instances across DO/Hetzner/Vultr | 100% unauth — **2 already actively exploited via CVE-2023-1177** by external attackers (visible attacker-injected experiments targeting /etc/ + /root/.ssh/, same actor across hosts); production workloads exposed: SPX hedging trading models, pediatric medical XGBoost classifiers, horse-racing/livestock breeders, manufacturing homogeneity, dental AI, AI safety probes |
| [streamlit-cloud-survey-2026-05.md](streamlit-cloud-survey-2026-05.md) | Streamlit data apps | 551 instances across DO/Hetzner/Vultr | 100% unauth (no built-in auth); 100-app Playwright sample → 84 unique custom titles. Dominant cluster: trading bots / crypto dashboards (Binance, Hyperliquid, Polymarket, Kalshi). Also: Dark-Web OSINT tool ("Robin"), Russian OZON sellers admin, MITEC Live, GC Breeders Evaluation (cross-correlates with MLflow finding — same operator) |
| [ollama-cloud-survey-2026-05.md](ollama-cloud-survey-2026-05.md) | Ollama | 342 instances across DO/Hetzner/Vultr | 100% unauth (Ollama has no auth concept); **172 instances loading `:cloud` models = direct Ollama Cloud quota theft** (minimax-m2.7, deepseek-v4-pro, kimi-k2.6, deepseek-v3.1:671b, devstral-2:123b); **22+ abliterated/uncensored** safety-rail-removed models (huihui_ai family, Llama-3.1-8B-Lexi-Uncensored, Qwen3.5-9B-Claude-Opus-Uncensored-Distilled) |
| [minio-dify-cloud-survey-2026-05.md](minio-dify-cloud-survey-2026-05.md) | MinIO + Dify | 852 MinIO + 5 Dify | MinIO: **0% anonymous-list** (operators DID enable auth) but 27 version-disclosed older releases CVE-2023-28432 vulnerable, 747 Console-exposed for credential brute-force, 9-instance cluster on identical 6-year-old release. Dify: 5 confirmed all `setup_step:finished` — no setup-wizard takeover. Negative finding for both: **auth-on-default upstream + clear docs = ~zero unauth at population scale** |
| [mem0-cross-survey-2026-05.md](mem0-cross-survey-2026-05.md) | Mem0 (cross-DB framework) | 8 instances (6 Qdrant + 2 ChromaDB) | Content fingerprint cross-ref; 4 new identifiable-individual exposures: "Friday" assistant (8,984 pts), Italian marketing agency claude_memory (424), Chinese personal diary (1,199), openclaw_memories (empty) |
| [elasticsearch-cloud-survey-2026-05.md](elasticsearch-cloud-survey-2026-05.md) | Elasticsearch / OpenSearch | 42 instances across DO/Hetzner/Vultr | Mixed — ~18 ransomed/wiped, ~16 live production data; ES 7.x default-no-auth still common |

---

## Why Separate from Universities

Commercial exposures carry distinct risk profiles:
- **Paying customers** — direct financial / contractual liability when PII is exposed
- **Live PII pipelines** — system prompts often reveal the exact data-collection schema
- **Competitive intel** — proprietary business logic in plain text
- **Cross-border attribution** — host country (e.g., Romania) often differs from operator country (e.g., France), complicating regulatory disclosure
