# Session Analyses

_Required closing artifact for every NuClide Research assessment run. Written at session end alongside the SESSION.md update. Covers the full session arc: objective, tooling, methodology, execution trace, findings, risk assessment, recommendations, limitations, and PoC illustrations._

These are distinct from [case studies](../case-studies/) (which are per-target) and [methodology insights](../methodology/) (which are generalizable lessons). A case study covers one target. An analysis covers one session — which may touch multiple targets, dispatch parallel sessions, ship tool fixes, and produce no new findings. All of that is worth documenting.

**To write a new analysis:** copy [`_TEMPLATE.md`](_TEMPLATE.md) to `session-analysis-YYYY-MM-DD.md`, fill in all 9 sections, add a row to the table below, commit + push.

---

| Date | File | Targets | Key Findings |
|---|---|---|---|
| 2026-05-22 | [session-analysis-2026-05-22](session-analysis-2026-05-22.md) | Evidently ML Monitoring (fingerprint); Agenta (carry-forward); Langfuse :5432 / Opik / PromptLayer (dispatched) | Evidently Tier-A no-auth default confirmed via Docker probe; aimap v1.9.24 shipped; Agenta open-signup verified across 6/6 hosts |
| 2026-05-22 | [session-analysis-2026-05-22-langfuse-cert-pivot](session-analysis-2026-05-22-langfuse-cert-pivot.md) | Langfuse :5432 Postgres cert-pivot corpus (11 hosts) | 11/11 Postgres auth-enforced (SCRAM-SHA-256); cert pivot on 34.0.11.208 → agenthub.cygnusalpha.one (signup-open, prod + dev); production S3 bucket names in dev CSP; 2× HIGH; `fe_sendauth` ≠ open Postgres (Insight #16 extended to protocol layer) |
