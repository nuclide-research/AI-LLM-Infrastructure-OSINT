---
type: methodology
insight_number: 37
title: Asymmetric auth gating, dashboard requires login but the API does not; observability platforms accept unauthenticated trace ingestion even when the UI is locked
---

# Insight #37. Asymmetric auth gating: dashboard locked, API open

_Source: AI cost / billing / usage analytics survey, 2026-05-19. 95 of 95 verified Arize Phoenix self-hosted instances had the signin page rendering on the dashboard (port 6006), but the `/v1/traces` HTTP OTLP ingestion endpoint on the same port returned 200 to unauthenticated POSTs and the `/metrics` Prometheus endpoint returned 200 unauthenticated. Same pattern observed across the LLM Gateways tier (2026-05-04) and the LangSmith tier in past observations._

## The rule

Many AI observability + telemetry platforms ship with **two distinct authentication surfaces** on the same port:

- The **dashboard / UI** requires login (auth-on by default in modern frameworks)
- The **ingestion / API surface** (telemetry write, OTLP traces, Prometheus metrics, webhook receivers) accepts unauthenticated requests by default

Operators configure auth for the dashboard (the visible surface; the one the operator looks at every day) and forget that the same port also serves an ingestion API that needs separate gating. The dashboard-auth verification gives the operator the warm feeling that the deployment is "secured," while the API surface remains a write-vector for any unauthenticated attacker.

**The consequence is asymmetric**: the operator cannot READ from the platform without auth (good), but an attacker can WRITE to it without auth (bad). The write-vector enables:

- **Data poisoning**: inject fake traces to corrupt cost analytics, eval scores, and historical baselines
- **Metric flooding**: write to Prometheus-class ingestion endpoints to spike costs (storage, alerting bandwidth)
- **Detection evasion**: write fake "all clear" status events to confuse SIEM rules
- **Denial of analytics**: overwhelm the ingestion path with junk to make the operator's data unusable

## Empirical basis

### Arize Phoenix (this survey, 2026-05-19)

95 verified Phoenix instances. Per-host probe matrix:

| Surface | Auth state | Count of 95 |
|---|---|---|
| Dashboard signin page on `/login` | rendered (auth required for read) | 95 |
| OTLP HTTP ingestion at `/v1/traces` | returns 200 to unauthenticated POST | 95 |
| Prometheus metrics at `/metrics` | returns 200 unauthenticated | 95 |

**100% asymmetric**. Every Phoenix instance with a locked dashboard had an open ingestion API on the same port.

### LLM Gateways (2026-05-04 survey)

1,857 of 1,899 LLM-gateway hosts (97.8%) accepted unauthenticated `/v1/chat/completions` POSTs while their admin UIs at `/ui` or `/admin` required login. The operator gated the admin path, not the inference path.

### LiteLLM (2026-05-19 same-day survey)

42-66% of LiteLLM hosts accepted unauthenticated inference while many of those same hosts had `master_key` configured for the `/admin` path. Same asymmetric pattern.

## Diagnostic signals

A host shows asymmetric auth gating when:

1. **GET on the dashboard root or `/login` returns the framework's signin page** (auth required for the human-facing surface)
2. **GET / POST on a known ingestion path** (`/v1/traces`, `/api/v1/events`, `/metrics`, `/api/log/request`, `/v1/chat/completions`) **returns 200 OK with a non-error response body** (auth not required for the machine-facing surface)
3. **Same port serves both** (the surfaces are not running on different ports with different auth configs)

## Procedural rules this insight generates

1. **Probe both surfaces, not just one.** A survey that probes only the dashboard misses the API exposure entirely. A survey that probes only the API misses the framework attribution. Both are needed for a correct severity classification.

2. **Severity tiering for asymmetric findings**:
   - Read-only dashboard auth + open ingestion = MEDIUM-HIGH (data-poisoning class, no exfiltration)
   - Read-only dashboard auth + open ingestion + open `/metrics` = HIGH (data-poisoning + operator-internal metrics exposure)
   - Open dashboard + open ingestion = CRITICAL (full read + write, traditional auth-off class)

3. **Disclosure message framing**: explain to the operator that login on the dashboard does NOT protect the API. Reference the specific endpoint they need to gate (e.g., Phoenix `/v1/traces` requires `PHOENIX_ENABLE_AUTH=true` AND a separate API-key configuration; the dashboard auth env-var alone does not gate ingestion).

4. **Framework / vendor education**: a framework that ships dashboard-auth and ingestion-no-auth as separate config dimensions should require BOTH to be set explicitly at first startup, with a UI warning if one is enabled and the other is not.

5. **Cross-survey pattern recognition**: this asymmetry is not Phoenix-specific. Re-survey LangSmith self-hosted, LiteLLM, Helicone self-hosted, and any other platform where dashboard + ingestion share a port, looking for the same pattern.

## Relationship to prior insights

- **Insight #8 (auth-bypass-via-misconfiguration redirects)**: same family. #8 documents how an `auth_role_public=admin` misconfiguration turns a login-gated app into an open-app at the application layer. #37 documents how a per-endpoint auth-gating gap leaves an open-API alongside a closed-dashboard.
- **Insight #2 (single-template auth-off propagates)**: the underlying framework default is the load-bearing variable. The Phoenix population shows the framework's API surface is auth-off by default; operators do not flip the default because the dashboard auth is the visible signal of "secured."
- **Insight #16 (status code is not identity, not auth state)**: a 200 OK on `/v1/traces` is the literal auth-state signal here. A reader who only sees the 401 on the dashboard would conclude the host is auth-gated; the 200 on the ingestion path is the actual ground truth.

## Open questions

- **What fraction of observability / telemetry platforms ship asymmetric by default?** A targeted survey across Phoenix, LangSmith, OpenLLMetry collectors, Datadog APM self-hosted, Honeycomb, Grafana Tempo would map the population.
- **Is the asymmetry intentional?** Some platforms intentionally ship open ingestion (for SDK-side telemetry to "just work" without provisioning API keys). The trade-off is documented but not surfaced to the operator at deployment time.
- **What does the operator need to do to fix it?** Per Phoenix: set `PHOENIX_ENABLE_AUTH=true` AND configure `PHOENIX_API_KEY_*` for ingestion. The two-env-var requirement is non-obvious; many operators set one and assume the other follows.

## See also

- `case-studies/commercial/cost-billing-analytics-survey-2026-05-19.md`: source survey (Phoenix 95-host cohort)
- `case-studies/commercial/llm-gateways-cloud-survey-2026-05.md`: same asymmetry at the gateway tier
- `case-studies/commercial/safety-guardrail-population-survey-2026-05-19.md`: LiteLLM 42% functional unauth on inference path while many operators have admin auth configured
- `insight-08-auth-bypass-via-misconfiguration-redirects.md`: same auth-gate-gap family at the application layer
- `insight-16-status-code-is-identity-not-auth-state.md`: the status-code rule that confirms asymmetric findings
