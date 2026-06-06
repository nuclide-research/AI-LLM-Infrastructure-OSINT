# The Research Program

## What we are studying

The auth-on-default posture of the AI/LLM infrastructure deployment landscape.

A new generation of open-source AI/LLM infrastructure tools (vector databases, RAG knowledge-base engines, agent orchestrators, observability platforms, model gateways, LLM workflow builders) has shipped over the past 24 months. Many ship with **auth-permissive defaults** — registration open, no authentication required for the data layer, configuration disclosure on public endpoints. These instances are then deployed into production environments — including universities, hospitals, national research institutes, and Fortune 500 enterprises — without the operator re-configuring the defaults.

The research program is:

1. **Map** the population of internet-facing instances per platform.
2. **Measure** the rate at which each platform's default auth posture is preserved into production.
3. **Discover** the systemic mistakes that bridge from "OSS default" to "production deployment exposed."
4. **Codify** the recurring patterns as numbered insights.
5. **Disclose** institutional findings to operators and CERTs; disclose population-level findings to upstream maintainers.
6. **Test** whether public surveys + upstream disclosure measurably shift the auth-permissive-default rate within 2–3 minor-version cycles.

## The central thesis

> **Candidate Insight #76 (working title):** Auth-permissive defaults are the cohort norm for new-generation OSS AI/LLM infrastructure platforms. The rate is platform-cohort dependent, not version-cohort dependent. Public surveys with upstream disclosure measurably move the rate within 2–3 minor-version cycles. Without that pressure, the default holds across major-version transitions.

This is **falsifiable**. Each survey either confirms the cohort pattern or breaks it. Negative results (AnythingLLM 0% open) are publishable. The cohort hypothesis can be broken by finding a platform that ships auth-closed by default AND has the same OSS lineage as the others.

## Empirical baseline (as of 2026-06-06)

| Platform | Rate | Class | Citation |
|---|---|---|---|
| Langfuse | 88.9% SIGNUP_OPEN | observability | `surveys/2026-06-06-langfuse.md` |
| RAGFlow | 87.2% REGISTER_OPEN | RAG engine | `surveys/2026-06-06-ragflow.md` |
| Arize Phoenix | 74.5% PROJECTS_UNAUTH | observability | `surveys/2026-06-06-phoenix.md` |
| Flowise | 68.7% CHATFLOWS_OPEN | workflow builder | `surveys/2026-06-06-flowise.md` |
| Open WebUI | 11.8% AUTH_OFF + SIGNUP_OPEN | chat UI | `surveys/2026-06-06-open-webui.md` |
| Dify | 0.9% SIGNUP_OPEN | LLM app platform | `surveys/2026-06-06-dify.md` |
| AnythingLLM | 0% NO_AUTH | doc chat | `surveys/2026-06-06-anythingllm.md` |
| LiteLLM | 0.81% NO_MASTER_KEY (18 CRIT) | model gateway | `surveys/2026-06-06-litellm.md` |

Three observability/RAG platforms surveyed same day at 74.5–88.9%. Two chat/app platforms surveyed at 0.9–11.8%. The cohort difference is real and statistically supports the platform-cohort hypothesis.

## The methodology in one paragraph

Discover → Fingerprint → **Verify** → Attribute → Classify → Ledger → Score → Codify. The verification stage is load-bearing: 18 of 21 codified insights are verification-stage failures. A scanner produces *candidates*; verification produces *findings*. At population scale, skipped verification fails systematically — confident, reproducible, wrong numbers. The restraint ethic governs every survey: enumerate metadata, do not exfiltrate; names ARE the finding; sample payloads minimally only to confirm severity.

Full methodology in `~/.claude/nuclide-internal/METHODOLOGY.md`. Numbered insights in `insights/INDEX.md`.

## Tooling stack

The 19-tool arsenal is documented in `~/.claude/CLAUDE.md`. Tool design notes that *belong to this research program* (not the general methodology) live in `tools/`. As of 2026-06-06:

- **herald** (built today) — declarative HTTP auth-probe tool. 8 platforms, public at `github.com/nuclide-research/herald`. Validated against same-day Python probe baselines.
- aimap, scanner, VisorLog, VisorCAS, VisorGraph, VisorBishop, VisorSD, et al. — full inventory in `tools/INDEX.md`.

## Disclosure pipeline

State-tracked in `disclosures/INDEX.md`. Disclosures are **never** sent autonomously; they are queued here and proceed only on Nicholas Kloster's explicit instruction. Per NuClide protocol: disclosure preparation is not a recommendation; the analyst surfaces findings and the researcher decides what to do with them.

## Research-program identity

The research program operates under the NICE Framework composite role: **541 Vulnerability Assessment Analyst** + **661 Research and Development Specialist** + **631 Information Systems Security Developer** + **422 Data Analyst**. Role-task mapping in `roles/INDEX.md`. Other roles (731 Legal Advisor, 731 Privacy Officer, 532 etc.) are referenced as supporting roles for specific work (legal review of disclosures, etc.).
