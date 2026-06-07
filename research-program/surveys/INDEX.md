# Surveys

Every NuClide AI/LLM infrastructure survey. Append-only at the top.

Entries link to case studies in `../../case-studies/`. One-line summary per survey: date, platform, dork population, finding count, rate, insight tag.

## 2026-06-06

## 2026-06-07

- [LangGraph Studio](../../case-studies/commercial/langgraph-studio-population-survey-2026-06-07.md) — 20 indexed, 11 reachable, **10/11 misdeployed (desktop auth-type on public IPs, 90.9%)**, 1 properly auth-gated. **NEW FINDING CLASS: operator-misdeployment-of-correctly-defaulted dev-tool.** Class-distinct from maintainer-default-vulnerable surveys. Refines #76 with responsibility-model split.
- [OpenHands (autonomous coding agent)](../../case-studies/commercial/openhands-population-survey-2026-06-07.md) — 193 indexed, 75 reachable. **68/75 SETTINGS_EXPOSED (90.7%)** with LLM model + base URL leak. **25/75 CONVERSATIONS_EXPOSED (33.3%)** with task titles + repo names. **3 hosts under active `/proc/self/environ` attack visible in conversation titles.** Internal corporate HR pipeline ("xrxs" operator, Aliyun CN, 20 conversations). #76 maintainer-culture cohort confirmed; LLM06 Excessive Agency finding class.

## 2026-06-06

- [Bisheng (DataElem)](../../case-studies/commercial/bisheng-population-survey-2026-06-06.md) — 30 dork hits but high FP (banks/NAS/ERP); 4 confirmed Bisheng all auth-required. NEGATIVE result counter-examples CN-jurisdiction sub-hypothesis. Refines #76 to maintainer-culture, not jurisdiction.
- [LobeChat](../../case-studies/commercial/lobechat-population-survey-2026-06-06.md) — 641 indexed, only 12/636 reachable (1.9%), 10/12 AUTH_OFF (83.3%). Chinese-origin OSS chat-UI cohort. Sub-hypothesis emerging: Western chat-UI cohort correcting (LibreChat v0.8.x = 10.3%); CN cohort possibly not (small N caveat). #76
- [LibreChat (deep-dive verification)](../../case-studies/commercial/librechat-deep-dive-verification-2026-06-06.md) — Severity revisions: Capitol.ai ESCALATED to CRITICAL-ENTERPRISE (per-customer subdomains incl. suspected `ey-*` Ernst & Young + `hmg-*` UK government tenants, all SERVER_KEY); Santepair.fr CONFIRMED GDPR Article 9; UC Berkeley DOWNGRADED (USER_KEY mode eliminates LLM10); `/api/endpoints` userProvide field is the LLM10 discriminator.
- [LibreChat](../../case-studies/commercial/librechat-population-survey-2026-06-06.md) — 3,153 indexed, 412/1,565 REGISTRATION_OPEN (26.3%). Within-platform cohort correction: v0.8.x = 10.3% vs main = 32.7%. UC Berkeley, Santepair.fr mental health AI, 4 Legal AI deployments, Capitol AI Chat Agent 20-host AWS fleet. #40 + #76 nuance
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
