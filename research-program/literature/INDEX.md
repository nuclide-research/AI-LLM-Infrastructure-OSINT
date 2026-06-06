# Literature

Academic + standards corpus grounding the research program. PDFs in `~/Documents/cs*-aisecure/` (academic) and `~/Documents/dod-cyber-pathways/` (NICE Framework).

## Threat-class taxonomy

The taxonomy of finding classes is built around the **OWASP Top 10 for LLM Applications (2025)** as the canonical reference. Each threat class has its own file in `threat-classes/` linking the OWASP category, the academic citations that established it, and the surveys that found instances.

| OWASP LLM Top 10 (2025) | Detail file | First evidence in our surveys |
|---|---|---|
| LLM01:2025 Prompt Injection | `threat-classes/llm01-prompt-injection.md` | Flowise deepseek_admin prompt injection canary |
| LLM02:2025 Sensitive Information Disclosure | `threat-classes/llm02-sensitive-info-disclosure.md` | Phoenix `/v1/users` (PROMOTED #6→#2 in 2025) |
| LLM03:2025 Supply Chain | `threat-classes/llm03-supply-chain.md` | (queued: aimap-profile findings) |
| LLM04:2025 Data and Model Poisoning | `threat-classes/llm04-data-model-poisoning.md` | (RAG knowledge-base poisoning vector — RAGFlow exposure surface enables) |
| LLM05:2025 Improper Output Handling | `threat-classes/llm05-output-handling.md` | (queued) |
| LLM06:2025 Excessive Agency | `threat-classes/llm06-excessive-agency.md` | Flowise Custom Tool RCE (CVE-2024-36420) merged plugin+agency class |
| LLM07:2025 System Prompt Leakage | `threat-classes/llm07-system-prompt-leakage.md` | Flowise deepseek_admin context injection canary |
| LLM08:2025 Vector and Embedding Weaknesses | `threat-classes/llm08-vector-embedding-weaknesses.md` | RAG architecture attack surface (new in 2025) |
| LLM09:2025 Misinformation | `threat-classes/llm09-misinformation.md` | — |
| LLM10:2025 Unbounded Consumption | `threat-classes/llm10-unbounded-consumption.md` | LiteLLM open proxy → Denial of Wallet on operator's Anthropic/Bedrock key |

## Course corpora

| Course | Path | PDFs | Topic |
|---|---|---:|---|
| CS 307 (UIUC, intro ML) | `~/Documents/cs307-aisecure/` | 15 | ML foundations: linear/logistic, NN, RandomForest, embeddings, VAE, RL |
| CS 442 (UIUC, AML) | `~/Documents/cs442-aisecure/` | 23 | Adversarial ML focused: FGSM, physical attacks, backdoors, certified defenses |
| CS 562 (UIUC, secure ML) | `~/Documents/cs562-aisecure/` | 83 | Privacy + adversarial ML: differential privacy, federated, attacks on training |
| CS 598 Fall 2020 (UIUC, AML) | `~/Documents/cs598-fall2020-aisecure/` | 108 | Graduate AML — older syllabus |
| CS 598 Fall 2021 (UIUC, AML) | `~/Documents/cs598-aisecure/` | 126 | Updated graduate AML; includes 2021 backdoor + watermark + extraction papers |

**Course instructor:** Bo Li (UIUC; bio at aisecure.github.io). The aisecure.github.io domain hosts the course materials. The arXiv numbered PDFs are the canonical AI security literature (FGSM `1412.6572`, Carlini-Wagner `1608.04644`, BadNets `1708.06733`, et al.).

Per-paper summaries indexed in `paper-index.md` (to be built; mechanical per-PDF extraction).

## Standards corpus

| Document | Purpose | Path |
|---|---|---|
| OWASP LLM Top 10 (2025) | Threat-class taxonomy | (online — saved as `owasp-llm-top10-2025.md` in this dir) |
| NICE Cybersecurity Workforce Framework | Role/task definitions | `~/Documents/dod-cyber-pathways/` |
| NIST SP 800-53 | Security control catalog | (referenced; not in corpus yet) |
| NIST AI Risk Management Framework (AI RMF) | AI-specific risk taxonomy | (referenced; not in corpus yet) |
| ISO/IEC 23894 AI Risk Management | International AI risk standard | (referenced; not in corpus yet) |
| MITRE ATLAS | Adversarial Threat Landscape for AI Systems | (referenced; not in corpus yet) |

## Reading queue

`reading-queue.md` tracks unread / next-priority papers from the academic corpus.

## Indexing approach

The 355-paper academic corpus is being indexed via parallel mechanical extraction. Each paper gets:

- Title + author + arXiv ID (or course slug)
- One-paragraph summary
- Threat-class tag (LLM01–LLM10 or "foundations" or "defense")
- Direct citation: which survey, insight, or tool design references it

The full per-paper index lives in `paper-index.md`. Build status: pending.
