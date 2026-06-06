# Surveys

Every NuClide AI/LLM infrastructure survey. Append-only at the top.

Entries link to case studies in `../../case-studies/`. One-line summary per survey: date, platform, dork population, finding count, rate, insight tag.

## 2026-06-06

- [Phoenix (Arize)](../../case-studies/commercial/phoenix-population-survey-2026-06-06.md) — 89 indexed, 41/55 PROJECTS_UNAUTH (74.5%), 34/55 USERS_UNAUTH. LLM02-class direct data-layer disclosure. Northeastern, SENAI flagged. #76
- [RAGFlow](../../case-studies/commercial/ragflow-population-survey-2026-06-06.md) — 1,915 indexed, 618/709 REGISTER_OPEN (87.2%). HKUST, Brno U, Indiana U, TW MoE x2, Shenzhen MS flagged. CVE-2024-12433 latent class. #76
- [Langfuse](../../case-studies/commercial/langfuse-population-survey-2026-06-06.md) — 1,141 indexed, 816/918 SIGNUP_OPEN (88.9%). Harvard, ASU, UCSB, TW MoE, KNTU Tehran flagged. Highest rate measured. #76
- [Arize Phoenix v0.7](#) — see above (same survey)
- [AnythingLLM](#) — 232 swept, 0/27 reachable open (NEGATIVE result; population hardened or rotated). #40-reverse
- [Dify](../../case-studies/commercial/dify-population-survey-2026-06-06.md) — 2,289 indexed, 9 SIGNUP_OPEN + 939 CONFIG_DISC. ByteDance Volcano enterprise cluster. SSO+register conflict on Alibaba host.
- [Flowise](../../case-studies/commercial/flowise-population-survey-2026-06-06.md) — 841 indexed, 578/841 chatflow API open (68.7%). CVE-2024-36420 PoC lab at 146.190.128.73 (43 chatflows). Prototype-pollution RCE second vector identified.
- [Open WebUI](../../case-studies/commercial/openwebui-population-survey-2026-06-06.md) — 5,097 indexed, 39 AUTH_OFF + 564 SIGNUP_OPEN (11.8%). PLLuM/NASK, SwiftRef, Dartmouth flagged.
- [LiteLLM](../../case-studies/commercial/litellm-gateway-survey-cat05-2026-06-06.md) — 2,209 indexed, 18 CRIT NO_MASTER_KEY (0.81%). Anthropic/Bedrock/Azure/Vertex/Databricks/Moonshot providers leaked.

## Earlier

Surveys before 2026-06-06 are tracked in case-studies index + SESSION.md history. See `~/AI-LLM-Infrastructure-OSINT/case-studies/` for the full archive (Cat-01 through Cat-32 plus campaign-specific case studies).
