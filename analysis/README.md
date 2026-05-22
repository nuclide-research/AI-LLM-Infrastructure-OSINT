# Session Analyses

_Required closing artifact for every NuClide Research assessment run. Written at session end alongside the SESSION.md update. Covers the full session arc: objective, tooling, methodology, execution trace, findings, risk assessment, recommendations, limitations, and PoC illustrations._

These are distinct from [case studies](../case-studies/) (which are per-target) and [methodology insights](../methodology/) (which are generalizable lessons). A case study covers one target. An analysis covers one session — which may touch multiple targets, dispatch parallel sessions, ship tool fixes, and produce no new findings. All of that is worth documenting.

**To write a new analysis:** copy [`_TEMPLATE.md`](_TEMPLATE.md) to `YYYY-MM-DD-sNN-slug.md` (e.g. `2026-05-22-s31-langfuse-cert-pivot.md`), fill in all 9 sections, add a row to the table below, commit + push.

---

| Date | File | Targets | Key Findings |
|---|---|---|---|
| 2026-05-22 | [2026-05-22-s31-llmops-observability](2026-05-22-s31-llmops-observability.md) | Evidently ML Monitoring (fingerprint); Agenta (carry-forward); Langfuse :5432 / Opik / PromptLayer (dispatched) | Evidently Tier-A no-auth default confirmed via Docker probe; aimap v1.9.24 shipped; Agenta open-signup verified across 6/6 hosts |
| 2026-05-22 | [2026-05-22-s31-langfuse-cert-pivot](2026-05-22-s31-langfuse-cert-pivot.md) | Langfuse :5432 Postgres cert-pivot corpus (11 hosts) | 11/11 Postgres auth-enforced (SCRAM-SHA-256); cert pivot on 34.0.11.208 → agenthub.cygnusalpha.one (signup-open, prod + dev); production S3 bucket names in dev CSP; 2× HIGH; `fe_sendauth` ≠ open Postgres (Insight #16 extended to protocol layer) |
| 2026-05-22 | [2026-05-22-s32-climategpt-opik-vllm](2026-05-22-s32-climategpt-opik-vllm.md) | 80.79.202.18 -- Opik v1.10.13 + vLLM + Streamlit (DTN Amsterdam, NL) | 4-surface stacked unauth: vLLM CRITICAL (climategpt_8b_latest, 34789 reqs, 92M tokens); Opik HIGH (7 projects, write-open); Prometheus HIGH; Streamlit HIGH; BARE 0/3 coverage (novel class); 2 aimap gaps filed |
| 2026-05-22 | [2026-05-22-s31-promptlayer-marker-build](2026-05-22-s31-promptlayer-marker-build.md) | PromptLayer 34.95.65.63 / dashboard.promptlayer.com (Magniv Inc, GCS-backed SPA) | 3 hardcoded Make.com webhooks in production SPA bundle (HIGH, LLMjacking); backend 401 auth-on-default confirmed; identity marker defined; VisorScuba AI.C1 FP codified |
