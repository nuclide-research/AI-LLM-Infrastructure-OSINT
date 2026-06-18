---
type: methodology
insight_number: 105
title: "A health/liveness endpoint on a no-auth skip-list is a platform config-disclosure anti-pattern: it leaks LLM provider/model and operator filesystem paths on every instance, including authed ones"
status: candidate
codified: 2026-06-17
source_survey: Cat-RAG-Framework-Servers 2026-06-17
falsifiability_tier: high
falsified_by: a platform with a no-auth health endpoint whose body carries only liveness state and exposes no provider, model, or filesystem-path configuration on authed instances
related_insights: [3, 16, 41, 56, 64]
---

# Insight #105 - A health endpoint on a no-auth skip-list is a platform config-disclosure anti-pattern

## The pattern

Web frameworks routinely exempt a liveness probe from authentication so an
orchestrator (Kubernetes, a load balancer) can poll it without credentials. The
endpoint goes on a no-auth skip-list, before the auth middleware runs. That is
sound for a body that returns only `{"status":"healthy"}`.

The anti-pattern: the platform expands that same no-auth health body to carry
**configuration**, and now an endpoint that is unauthenticated BY DESIGN, on every
instance, leaks operator config to anyone. Because the disclosure rides the
skip-list, enabling auth does NOT close it. A fully hardened, auth-on instance
leaks exactly as much as an auth-off one. The exposure is a property of the
PLATFORM (where the skip-list and the config-bearing body were both decided
upstream), not of the operator's auth choice.

Two disclosure classes are typical, both present in the founding case:

1. **Backend/provider identity** - which LLM and embedding provider the operator
   wired up (provider name plus model name). This is supply-chain and cost-model
   intel: it names the operator's paid upstream and the exact model, useful for
   LLMjacking target selection and for inferring spend.
2. **Filesystem paths** - a `working_directory` or data-root path that embeds the
   OS username and the project name (`/home/<user>/<project>-rag/`). This is
   operator-attribution and host-layout intel handed over with no auth.

## Empirical founding case - LightRAG (Cat-RAG-Framework-Servers 2026-06-17)

LightRAG's `/health` is on the no-auth skip-list and returns a configuration
object on ALL 67 confirmed instances, the auth-on ones included. The body
discloses:

- `configuration.llm_binding` + `llm_model` - observed across the population:
  `anthropic:claude-haiku-4-5`, `azure_openai:gpt-5.5`, `aws_bedrock`,
  `openai:gpt-4o-mini`, `ollama:qwen2.5`, `openrouter:...`. The operator's paid
  LLM upstream and exact model, by name, unauth.
- `configuration.embedding_model` - the embedding provider/model.
- `working_directory` - operator filesystem paths naming users and projects:
  `/home/azureuser/`, `/usr/local/eagletalent/robot-graphrag/`,
  `/home/ubuntu/elitra-light-rag/`, `aidsmo-chatbot`.

This is the survey's F5: a finding logged against the PLATFORM, not the operators.
It is independent of the `auth_mode` posture (Insight #104), the auth-on
instances disclose the same config because the leak is on the skip-list, in front
of the gate. One upstream fix (drop config from the unauth health body, or move
config behind the gate) protects the entire population at once, which is exactly
why it is a platform finding and not 67 operator findings.

The data was never read beyond the health body itself (rung A/2, breadth =
population). The provider names, model names, and paths ARE the finding; no
documents, queries, or graphs were touched.

## Why this is a distinct anti-pattern, not a config-leak restatement

Insight #3 (capabilities-object schema leak) and #56 (self-identifying JSON
fingerprint) cover platforms that disclose their SHAPE in a metadata response.
#105 is sharper on two axes:

1. **The skip-list makes it auth-invariant.** The leak survives the operator's
   single most important hardening action (turning auth on). That is what makes it
   a platform anti-pattern: the operator cannot fix it by configuration, only the
   vendor can, by moving config off the skip-listed route.
2. **The body carries OPERATOR config, not platform identity.** A self-identifying
   fingerprint discloses "I am LightRAG vN." A config-bearing health body
   discloses "this operator pays Anthropic for claude-haiku-4-5 and runs out of
   /home/azureuser/eagletalent." The first is the platform talking about itself;
   the second is the platform talking about its operator, for free, with no auth,
   on every instance.

So this is the liveness-probe analogue of Insight #41 (admin-endpoint field-name
enumeration as a restraint primitive): the same "the metadata IS the finding"
discipline, applied to a route the platform deliberately left unauthenticated.

## How to apply

1. On any platform with an unauth liveness/health/ready endpoint, read the body
   and classify it: liveness-only (sound) vs config-bearing (anti-pattern).
2. If config-bearing, log a PLATFORM finding, not a per-operator finding. The
   count of affected instances is the breadth (rung A/2), and it includes authed
   instances by construction.
3. Specifically enumerate (do not read past the health body): provider+model
   bindings, embedding model, and any path/working-directory field. The provider
   binding is LLMjacking and cost-model intel; the path is operator attribution.
4. Treat this as auth-INVARIANT: do NOT exclude authed hosts from the affected
   count. The whole point is that auth does not close it.
5. Cross-check sibling platforms for the same shape (Langfuse, other RAG servers,
   any FastAPI/Flask service with a config-rich `/health` or `/info`). The
   anti-pattern is portable across any framework that puts config on the
   skip-listed liveness route.

## Population consequence

Where a normal unauth finding scales with the operators who left auth off, a
skip-list config-disclosure scales with EVERY instance the platform ships,
hardened or not. It is the rare finding whose affected count is the full install
base, and whose remediation is a single upstream change. For the survey ledger,
that means the affected-instance count is a platform-population number (all 67),
not an auth-off-subset number (the ~29% that ran `auth_mode=disabled`).

## Related insights

- Insight #3 - Capabilities-object schema leak (the metadata-disclosure parent;
  #105 is the auth-invariant, operator-config-bearing case)
- Insight #16 - A 200 is identity, not auth state (the health 200 is identity AND,
  here, an unintended config read)
- Insight #41 - Admin-endpoint field-name enumeration as a restraint primitive
  (same "names ARE the finding" discipline on a deliberately-unauth route)
- Insight #56 - Self-identifying JSON fingerprint (platform identity in metadata;
  #105 is operator config in metadata)
- Insight #64 - Agent-manifest pre-run disclosure (config disclosed before any
  authenticated action; #105 is config disclosed with no authentication at all)

## Promotion criteria

Confirmed at 1 platform (LightRAG `/health`, full 67-instance population including
authed). Promotion to numbered Insight requires a second platform whose
skip-listed health/liveness endpoint leaks provider/model or filesystem-path
config on authed instances. Immediate next checks: Langfuse `/api/public/health`,
other RAG-server `/health` bodies, any agent-platform `/info` on a no-auth route.
