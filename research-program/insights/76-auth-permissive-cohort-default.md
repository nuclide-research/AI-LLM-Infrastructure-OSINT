# Insight #76 — Auth-permissive defaults are the cohort norm for new-gen OSS AI/LLM infrastructure

**Status:** Candidate. 3 same-day data points (2026-06-06).
**Falsifiability:** Direct. Find a same-cohort platform that ships auth-closed by default AND has comparable OSS lineage and adoption curve.

## Statement

The default deployment posture of new-generation open-source AI/LLM infrastructure platforms (LLM observability, RAG knowledge-base engines, agent orchestrators, workflow builders, model gateways) is **auth-permissive**: either public registration is enabled by default, or the data layer is exposed without authentication entirely. This holds across:

- Multiple upstream maintainers (Langfuse / Berlin, InfiniFlow / Shanghai, Arize / US, Flowise / Denmark)
- Multiple functional categories (observability, RAG, workflow builder)
- Multiple major versions (Langfuse v2.x → v3.x, RAGFlow stable, Phoenix v6.x)

The rate is **cohort-dependent**, not version-dependent. The same maintainer's recent v3.x release ships the same default as the v2.x release from 18+ months earlier.

The rate **can be moved** by public population surveys combined with upstream-maintainer disclosure within 2–3 minor-version cycles. Open WebUI is the existing precedent: their `ENABLE_SIGNUP` default changed to `false` after public surveys exposed the previous rate. Their resulting rate (11.8% as of 2026-06-06) is an order of magnitude lower than the unaddressed-cohort rate.

Without the survey+disclosure pressure, **the default holds across major-version transitions in the absence of pressure.**

## Evidence (2026-06-06 same-day baseline)

| Platform | Upstream maintainer | Class | Rate (OPEN of reachable) |
|---|---|---|---|
| Langfuse | Langfuse GmbH, Berlin | Observability | 88.9% SIGNUP_OPEN |
| RAGFlow | InfiniFlow, Shanghai | RAG engine | 87.2% REGISTER_OPEN |
| Flowise | (FlowiseAI, Denmark) | Workflow builder | 68.7% CHATFLOWS_OPEN |
| Arize Phoenix | Arize AI, US | Observability | 74.5% PROJECTS_UNAUTH / 61.8% USERS_UNAUTH |
| **LibreChat** | **danny-avila (community)** | **Chat UI** | **26.3% overall / 10.3% v0.8.x ← correcting** |

### Counterexamples (same-day)

| Platform | Rate | Why it does not break #76 |
|---|---|---|
| Dify | 0.9% | Different cohort: LLM-app-building, mature SaaS-style product with stronger auth defaults |
| Open WebUI | 11.8% | Cohort partially corrected: ENABLE_SIGNUP default changed in v0.5+ after disclosure pressure (validates the second clause of #76) |
| AnythingLLM | 0% | Cohort-correcting: prior 2/5 sample (2026-05) → 0/27 today; population hardened |
| **LibreChat v0.8.x** | **10.3%** | **Cohort-correcting IN REAL TIME: maintainer tightened default in tagged release; full v0.8.x cohort at Open-WebUI-equivalent rate** |

### LibreChat as the in-progress correction case

LibreChat is the first 2026-06-06 survey to show **within-platform version-cohort correction at the time of measurement**:

| Cohort | Rate | Interpretation |
|---|---|---|
| LibreChat v0.8.x (tagged stable) | 10.3% | Corrected default in tagged release |
| LibreChat `main` (dev branch) | 32.7% | Older default still active in dev |
| LibreChat older / no buildInfo | 26.2% | Population-at-large baseline |
| LibreChat overall | 26.3% | Weighted by cohort distribution |

This is direct evidence for the **second clause of #76** — that the rate is movable — and adds a nuance: **the pressure can be internal-quality-driven rather than external-disclosure-driven**. The LibreChat maintainer (danny-avila) tightened the default in v0.8.x without (as far as known) external NuClide-class disclosure pressure. This suggests internal security review can produce the same correction we predicted would require external pressure.

The strong form of #76 ("auth-permissive defaults persist until external pressure") is broken by LibreChat. The weak form ("auth-permissive defaults are the cohort norm; the rate is movable") is supported.

### CN-cohort split refines #76 — maintainer-culture, not jurisdiction (added 2026-06-06)

The LobeChat result (83.3% AUTH_OFF, CN-origin) initially suggested **"CN-jurisdiction OSS trends auth-permissive."** Bisheng (DataElem Beijing) refuted that within hours: 4/4 confirmed Bisheng instances are auth-required.

The CN-origin matrix splits 2-2:

| Platform | Maintainer | City | Default | Open rate |
|---|---|---|---|---|
| LobeChat | Lobehub | Hangzhou | open | 83.3% |
| RAGFlow | InfiniFlow | Shanghai | reg-open | 87.2% |
| Bisheng | DataElem | Beijing | auth-required | 0% |
| Dify | Dify.AI | Shanghai | auth-required | 0.9% |

**Refined hypothesis:** the auth default is **platform-maintainer-specific**, reflecting whether the upstream team optimizes for:

- **"Clone, docker compose up, immediately demo"** → auth-permissive default
  Examples: Langfuse, RAGFlow, Phoenix, Flowise, LobeChat
- **"Self-host for our enterprise customers"** → auth-required default
  Examples: Bisheng, Dify, AnythingLLM, Open WebUI (post-correction)

The geographic-jurisdiction claim is **discarded**. The maintainer-culture claim is **the actively-supported form** of Insight #76 as of 2026-06-06.

### Scope-bounding refinement — platform class only (added 2026-06-07)

After MCP server and CrewAI negative-result surveys (`case-studies/commercial/mcp-crewai-negative-results-2026-06-07.md`), the hypothesis scope is now precisely bounded:

| Class | Examples | Survey methodology | #76 applies? |
|---|---|---|---|
| Platform — demo-first | Langfuse, RAGFlow, Phoenix, Flowise, LobeChat, OpenHands | Shodan dork + herald HTTP probe | YES (uncorrected default) |
| Platform — enterprise-first | Bisheng, Dify, AnythingLLM | Same | YES (auth-required default) |
| Platform — operator-misdeployment | LangGraph Studio | Same + ls-init decode | Boundary case (correct default abused) |
| Framework — library | CrewAI, AutoGen, LangChain, LlamaIndex | Per-deployment; operator-attribution-first | NO (no shared default) |
| Protocol — emerging | MCP servers | Port-scan + protocol-handshake (future tool) | NO (no canonical population yet) |

**Insight #76 final form (as of 2026-06-07):** Auth-permissive defaults are the cohort norm for **platform-class** new-generation OSS AI/LLM infrastructure where the upstream maintainer optimizes for demo-first deployment ergonomics. The rate is platform-maintainer-culture-specific, not jurisdiction-specific. The hypothesis does **not apply** to framework-class libraries (no shared deployment) or to maturing protocol-class ecosystems (no canonical population yet).

11 platform-class surveys 2026-06-06/07 fall within scope: Langfuse, RAGFlow, Phoenix, Flowise, LobeChat, OpenHands, Bisheng, Dify, AnythingLLM, Open WebUI, LibreChat, LangGraph Studio.

The counterexamples are consistent with the version-cohort-correction clause of the insight, not a refutation of it. They are the existence proof that **the cohort can be moved.**

## Version-distribution analysis (within-platform)

Langfuse breakdown:
- v1.x: 100% SIGNUP_OPEN (2/2)
- v2.x: 96.6% (115/119)
- v3.x: 87.7% (696/794)

The v3.x rate is *modestly* lower than v2.x — 9% improvement over ~18 months. This is *not* the order-of-magnitude correction seen in Open WebUI's v0.4→v0.5 transition. Hypothesis: Langfuse has had organic security-team improvement without external disclosure pressure; Open WebUI had direct pressure. The direct comparison is the test condition.

## Causal hypothesis (why auth-permissive is the default)

Plausible explanations to test:

1. **DX-first design philosophy.** OSS LLM-infrastructure projects optimize for "clone, docker compose up, immediately demo to your team" — closing auth by default adds friction to the demo path.
2. **Pre-LLM observability tradition.** Tools like Prometheus, Grafana, and pre-LLM tracing systems shipped open-by-default for similar DX reasons. Langfuse and Phoenix inherit this lineage.
3. **No security-team gate.** Many of these projects are < 3 years old. Some have not yet hired their first dedicated security engineer.
4. **Lack of public exposure data.** Without surveys like this one, maintainers do not see the population rate. The default looks safe until someone counts.

## Test condition

The test condition for this insight is:

1. **Disclose** the rates to Langfuse + InfiniFlow + Arize upstream maintainers (state: QUEUED in `disclosures/INDEX.md`)
2. **Wait** 2–3 minor-version cycles (likely 3–6 months for these projects)
3. **Re-survey** Langfuse v3.180+, RAGFlow v0.21+, Phoenix v7+
4. **Measure** the rate change. Predicted: order-of-magnitude correction following the Open WebUI precedent.

If the rate does not move within 6 months, the second clause of #76 (surveys+disclosure shifts the rate) is broken, and the insight downgrades to "auth-permissive defaults are the cohort norm; correcting them requires more than disclosure."

If the rate moves dramatically, #76 graduates from candidate to codified insight.

## Related insights

- **#40** — Auth-on-default strengthens across OSS generations under disclosure pressure (the precedent that motivated #76)
- **#8** — signUpDisabled:false = anyone registers (the specific Langfuse pattern that started this thread)
- **#12** — Stacked-catastrophe pattern (operator who ships one service auth-off ships others auth-off) — relevant when an OPEN-platform host also exposes Ollama/Qdrant/Redis
- **#39** — Pooled-account proxy = attribution-laundering (a downstream consequence of open-registration platforms)
- **#71** — Argo/RAG/Service Mesh class (architectural-tier auth gap related to the platform-tier #76)

## Surveys that contribute evidence

| Date | Survey | Contribution |
|---|---|---|
| 2026-06-06 | Langfuse | 88.9% rate baseline |
| 2026-06-06 | RAGFlow | 87.2% rate, different maintainer + jurisdiction |
| 2026-06-06 | Phoenix | 74.5%/61.8%, third maintainer + data-layer-direct exposure model |
| 2026-06-06 | Flowise (revisit) | 68.7%, fourth maintainer, workflow-builder class |
| 2026-06-06 | Dify | 0.9% counterexample (LLM-app-builder cohort) |
| 2026-06-06 | Open WebUI | 11.8% — validates correction-via-pressure clause |
| 2026-06-06 | AnythingLLM | 0% — validates correction-via-pressure clause |

The 7-survey same-day corpus is the empirical baseline. Re-survey of the same 7 platforms post-disclosure is the falsifiability test.
