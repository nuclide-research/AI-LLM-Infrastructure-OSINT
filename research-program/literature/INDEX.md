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

## Course corpora — INDEXED

| Course | Detail file | PDFs | Topic concentration |
|---|---|---:|---|
| CS 307 (UIUC, intro ML) | [cs307-index.md](cs307-index.md) | 13 | ML foundations; lecture decks only, no AI security depth |
| CS 442 (UIUC, AML) | [cs442-index.md](cs442-index.md) | 23 | Adversarial ML + certified robustness; Bo Li-author-heavy |
| CS 562 (UIUC, secure ML) | [cs562-index.md](cs562-index.md) | 83 | Privacy + adversarial + poisoning; broadest coverage |
| CS 598 Fall 2020 (UIUC, AML) | [cs598-fall2020-index.md](cs598-fall2020-index.md) | 108 | Graduate AML — older syllabus |
| CS 598 Fall 2021 (UIUC, AML) | [cs598-fall2021-index.md](cs598-fall2021-index.md) | 126 | Updated grad AML; 2021 backdoor + watermark + extraction additions |

**Total corpus: 353 PDFs across 5 course-years.** All indexed 2026-06-06 via parallel agent extraction (1 corpus per agent).

**Course instructor:** Bo Li (UIUC). The aisecure.github.io domain hosts the course materials. The arXiv numbered PDFs are the canonical AI security literature (FGSM `1412.6572`, Carlini-Wagner `1608.04644`, Madry PGD `1706.06083`, BadNets `1708.06733`, DP-SGD `1607.00133`, PATE `1610.05755`, randomized smoothing `1902.02918`, et al.).

## Cross-corpus reading-list overlap

Several canonical papers appear in multiple course corpora. Detection of overlap and the "must-cite" anchor papers:

- **FGSM (Goodfellow et al., `1412.6572`)** — in CS 442, CS 562, CS 598 Fall 2020, CS 598 Fall 2021. The single most-cited adversarial-ML paper.
- **C&W attack (`1608.04644`)** — in CS 562, CS 598 Fall 2020, CS 598 Fall 2021.
- **DP-SGD (Abadi et al., `1607.00133`)** — in CS 442, CS 562, CS 598 Fall 2020, CS 598 Fall 2021.
- **PATE (`1610.05755`)** — in CS 562, CS 598 Fall 2020.
- **Randomized smoothing (Cohen et al., `1902.02918`)** — in CS 442, CS 562, CS 598 Fall 2020/2021.
- **Membership inference (Shokri et al., `1610.05820`)** — in CS 562, CS 598 Fall 2020/2021.
- **Backdoor / BadNets (Gu et al., `1708.06733`)** — referenced across multiple courses.
- **CRFL (`2106.08283`)** — in CS 562 + CS 598 Fall 2021 (Bo Li-coauthored; relevant to federated-learning surveys).

## Bo Li authorship across corpora

Across the 5 corpora, papers where Bo Li or her students appear as authors include: FGSM-derivative attacks, AdvGAN, stAdv, 3D adversarial mesh (`1801.02612`), DBA (Distributed Backdoor Attacks on FL), LID detection, CRFL, Feature Cross-Substitution (2014 early work). The reading lists are explicitly built around her own research lineage. This is the canonical academic AI/ML security corpus from one of the field's most-cited authors.

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
