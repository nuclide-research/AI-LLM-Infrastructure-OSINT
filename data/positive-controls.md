# Positive Controls — Auth-Enforced Platform Inventory

_Last updated: 2026-05-28_

Platforms found correctly secured across NuClide surveys. Evidence for the auth-on-default thesis: what works vs what fails.

---

## Platform Class Summary

### Well-Secured (94–100% auth enforcement)

| Platform | Auth Rate | Mechanism | Evidence |
|----------|-----------|-----------|----------|
| JupyterHub (institutional) | 94–98% | Campus LDAP/SSO backends | 1,964 auth-enforced instances across global university survey; 378/399 verified |
| Argo Workflows | 100% | Bearer token | 0/84 unauthenticated instances; all return 401 on /api/v1/* |
| sub2api v2 (Go) | 96.1% | x-api-key / JWT bearer | 5,848/6,083 verified hosts auth-enforced; zero POOL_LEAK (v1 pattern did not generalize) |
| PostgreSQL (production) | 100% | SCRAM-SHA-256 + pg_hba.conf | 11/11 Langfuse-associated instances secured |
| Agenta (LLMOps) | 100% | HTTP 401 at API layer | All sampled cloud instances return 401 on /api/apps, /api/v1/* |
| Mem0 (agent memory) | 100% | MEMO_API_KEY mandatory | 70/70 instances enforced at data layer |

### Inconsistently Secured

| Platform | Auth Rate | Notes |
|----------|-----------|-------|
| Open WebUI | 99.1% | Login required by default; 14/112 sampled instances have enable_signup:true (uncontrolled registration risk) |
| PromptLayer | 100% backend / open frontend | Backend API returns 401; frontend allows self-registration (HIGH finding separately) |

### Poorly Secured (0% auth enforcement — thesis inversions)

| Platform | Auth Rate | Why |
|----------|-----------|-----|
| Ollama | ~0% | Port 11434 ships with no authentication; operator opt-in required; 16,473+ unauth confirmed |
| Rasa | 0% | Platform ships no-auth by default; webhook endpoints unauthenticated by design; 196-host survey: 0 auth-gated |

---

## Specific Positive Control Instances

### JupyterHub — University of Southern Maine
- **Hosts:** wasp, earwig, locust, mosquito, ant, beetle, turing, pascal (cs.usm.maine.edu)
- **Auth:** LDAP/institutional SSO; 403 on /hub/api/info across all 8 hosts
- **Source:** `case-studies/universities/US/ME-southern-maine.md`

### JupyterHub — University of South Florida Marine Lab
- **Hosts:** ocgmod1.marine.usf.edu, manglillo.marine.usf.edu
- **Auth:** Campus SSO; login form accessible, credentials required; no anonymous API access
- **Source:** `case-studies/universities/US/FL-usf.md`

### Argo Workflows — Global Population (84 instances)
- **Auth:** Bearer token; gRPC error "token not valid for running mode" on all tested hosts
- **Source:** `case-studies/commercial/argo-workflows-survey-2026-05-27.md`

### sub2api v2 — 7,720 host population
- **Auth:** x-api-key or JWT bearer; endpoints return 401 with API_KEY_REQUIRED envelope
- **Source:** `case-studies/commercial/sub2api-population-2026-05-19.md`
- **Note:** v1 (Node.js) showed POOL_LEAK; v2 (Go rewrite) hardened — generational improvement via disclosure feedback

### Agenta — Cloud Deployments (DO/Hetzner/Vultr/AWS)
- **Auth:** 401 on /api/apps, /api/v1/configs, /api/v1/evaluators, /api/v1/workspaces
- **Source:** `case-studies/commercial/agenta-llmops-observability-survey-2026-05-22.md`

### Mem0 — 70 Cloud Instances
- **Auth:** MEMO_API_KEY enforced at data layer by framework design
- **Source:** `case-studies/commercial/agent-memory-population-survey-2026-05-16.md`

### Open WebUI — Institutional Deployments
- **Hosts:** genai.arizona.edu (OIDC), kahan.ee.cooper.edu (LDAP), datalab02.rrcc.edu
- **Auth:** enable_signup:false + institutional OIDC/LDAP federation
- **Source:** `case-studies/universities/US/AZ-arizona.md` and university index

### PostgreSQL — Langfuse LLMOps Infrastructure (11 instances)
- **Auth:** SCRAM-SHA-256; 11/11 production instances secured
- **Source:** `analysis/2026-05-22-s31-llmops-observability.md`

### PromptLayer — Backend API
- **Auth:** HTTP 401 on unauthenticated requests; tightened from 422 (April) to 401 (May 2026) post-disclosure
- **Source:** `analysis/2026-05-22-s31-promptlayer-marker-build.md`

---

## Key Findings

**What works:** Platforms with mandatory API key configuration (Mem0), institutional SSO integration (JupyterHub), or framework-enforced bearer tokens (Argo) achieve 94–100% auth enforcement in practice. The mechanism matters — opt-in auth fails; mandatory-on-first-run auth succeeds.

**Generational hardening:** sub2api v2 demonstrates that disclosure pressure causes measurable improvement. The v1 POOL_LEAK finding did not generalize to v2 — the platform hardened its successor. PromptLayer tightened error responses within the disclosure feedback window (422→401, April→May 2026).

**Database vs application layer:** PostgreSQL data tiers show 100% enforcement (11/11). Application-layer infrastructure (Ollama, Rasa) shows 0%. Data-tier operators have more security discipline or the stakes are more obvious.

**Thesis inversions:** Ollama and Rasa completely invert the auth-on-default thesis. Both ship no-auth-by-default and fail across all surveys. These are not exceptions — they are platform-design choices that propagate to every deployment.
