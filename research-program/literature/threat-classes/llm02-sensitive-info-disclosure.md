# LLM02:2025 — Sensitive Information Disclosure

**OWASP rank 2025:** #2 (**PROMOTED from #6 in 2023**)
**OWASP rank 2023:** LLM06 #6

The 2025 promotion from #6 to #2 was driven by Samsung's source-code leak via ChatGPT (2023), several healthcare-AI data breaches, and concrete cross-session data leakage incidents. Model theft (`LLM10:2023`) was also absorbed into this category — model weights are treated as sensitive information.

## Description

An LLM-integrated system leaks sensitive information through:

1. **Training-data extraction** — the model returns memorized training data verbatim (Carlini's "Extracting Training Data from Large Language Models" line of work).
2. **Membership inference** — an attacker determines whether a specific record was in the training set.
3. **Model extraction / theft** — model weights, fine-tuning datasets, or distilled approximations are stolen via query API.
4. **Configuration / metadata disclosure** — the *infrastructure* leaks credentials, project names, user records, API endpoints, model identifiers. **This is the NuClide-discovered class.**
5. **Cross-session leakage** — multi-tenant deployments leak one user's data to another.

## Academic citations

From the NuClide aisecure literature corpora:

- **Shokri et al. "Membership Inference Attacks Against Machine Learning Models" (`arxiv_1610.05820`)** — the foundational paper on inferring training-set membership. In CS 562, CS 598 Fall 2020/2021.
- **Carlini et al. "The Secret Sharer" (`arxiv_1802.08232`)** — measures unintended memorization in generative sequence models. In CS 562, CS 598 Fall 2020/2021.
- **Tramèr et al. "Stealing Machine Learning Models via Prediction APIs" (USENIX 2016)** — model extraction via API queries.
- **Abadi et al. "Deep Learning with Differential Privacy (DP-SGD)" (`arxiv_1607.00133`)** — the canonical defense against the above. In CS 442, CS 562, CS 598 Fall 2020/2021.
- **Papernot et al. "PATE" (`arxiv_1610.05755`)** — alternative DP training. In CS 562, CS 598 Fall 2020.

## Current survey instances — the NuClide-discovered class

This is the **most common finding class in the 2026-06-06 surveys**. NuClide finds infrastructure-side configuration/metadata disclosure, not training-data extraction.

- **Arize Phoenix** (`surveys/2026-06-06-phoenix.md`) — 41/55 hosts expose `/v1/projects` without auth (project names, IDs); 34/55 expose `/v1/users` (account records, timestamps). **The single cleanest LLM02 finding in the day's work.**
  - Notable: Northeastern University (Essaybot project — FERPA-class), SENAI Brazil (LGPD-class), `37.27.248.144` Hetzner with 21 projects exposed.
- **LiteLLM** (`surveys/2026-06-06-litellm.md`) — 18 instances expose `/model/info` `litellm_params` including Azure resource names (`uksdoai673aif02.openai.azure.com`), GCP project IDs (`inquinion-code`, `tdsipex`), Databricks workspace IDs (`adb-4870463909224736.16.azuredatabricks.net`). Configuration disclosure across cloud-provider tenant identifiers.
- **Open WebUI** (`surveys/2026-06-06-open-webui.md`) — AUTH_OFF instances expose `/api/config` revealing version, deployment name, branding (`PLLuM dla Edukacji`, `SwiftRef Assistant`, `Dartmouth Offshore Wind Lab AI`) — operator profiling at population scale.

## Disclosure pathway implications

LLM02 findings on US enterprise infrastructure trigger:
- **FERPA** if student records are involved (Northeastern Essaybot)
- **HIPAA** if PHI is involved (Strategion kardiointerakt medical AI)
- **PCI DSS** if payment data is in scope (none confirmed today)
- **LGPD** for Brazilian PII (SENAI)
- **GDPR** for EU PII (multiple EU institutions found)

The 732 Privacy Officer / Privacy Compliance Manager role (see `roles/732-privacy-officer-privacy-compliance-manager.md`) is the canonical disclosure recipient for these findings.

## Why LLM02 jumped #6 → #2 in 2025

Per AI-Native LLM Security (Packt, December 2025) Appendix A: the promotion reflects "documented incidents and broader deployment of LLM systems" — specifically Samsung 2023 (employees pasting proprietary code into ChatGPT), healthcare app breaches, and cross-session data leakage in multi-tenant LLM services. The NuClide research-program data point — 34/55 Phoenix instances exposing user records publicly — is consistent with the OWASP committee's empirical observation that this class is widespread.

## Related NICE roles

- **541 Vulnerability Assessment Analyst** — discovers the exposure
- **732 Privacy Officer / Privacy Compliance Manager** — receives the disclosure
- **612 Security Control Assessor** — runs the inside-the-boundary equivalent assessment
- **731 Cyber Legal Advisor** — handles cross-jurisdictional disclosure (LGPD, GDPR, FERPA)

## Insight #76 connection

The cohort-default for new-gen OSS AI/LLM infrastructure (88.9% Langfuse, 87.2% RAGFlow, 74.5% Phoenix) is the **enabling condition for LLM02:2025 at population scale**. The OWASP committee's rank promotion and the NuClide same-day three-platform survey corpus are pointing at the same phenomenon from different sides.
