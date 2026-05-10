---
title: AI observability tier — cross-platform synthesis (Phase 1)
date: 2026-05-10
class: substrate
category: cross-platform-synthesis
status: research-complete-phase-1
methodology: cross-platform Shodan sweep + source-level auth audits + IP-direct-shadow methodology
---

# AI observability tier — cross-platform synthesis · 2026-05-10

NuClide Research · 2026-05-10

## TL;DR

Seven AI observability platforms surveyed at population scale on 2026-05-10. Combined population: **~1,800 self-hosted instances** across Phoenix, Langfuse, Helicone, LangSmith, Lunary, OpenLIT, and Pezzo.

**Phoenix accounts for 100% of the unauthenticated instances in the cohort.** 94 unauth Phoenix hosts; 0 unauth across the other six platforms combined.

The 25% unauth rate at the Phoenix population (94 of 377) is **not** a property of "AI observability is hard to deploy securely" — it's a property of **Phoenix specifically shipping with `PHOENIX_ENABLE_AUTH=False` as the documented default in current `main` branch source**. Every other platform in the same product category ships with mandatory auth and operators run them that way.

This is decisive evidence that **shipping defaults are load-bearing for security posture at population scale** — large enough to register as Methodology Insight #13 (see [insight-13-shipping-defaults-load-bearing.md](../../methodology/insight-13-shipping-defaults-load-bearing.md)).

## Population scale across the seven platforms

| Platform | Population | Confirmed | Unauth | Unauth rate | Auth-by-default? |
|---|--:|--:|--:|--:|---|
| **Arize AI Phoenix** | **377** | 357 | **94** | **25%** | **NO** |
| **Langfuse** | 1,333 | 381 | 0 | 0% | YES |
| **LangSmith** | 96 | 27 | 0 | 0% | YES |
| **OpenLIT** | 23 | 23 | 0 | 0% | YES |
| **Helicone** | 21 | ~16 | 0 | 0% | YES |
| **Lunary** | 6 | 1 | 0 | 0% | YES |
| **Pezzo** | 3 | 1 | 0 | 0% | YES |
| **TOTAL** | **1,859** | **806** | **94** | **5.1%** | — |

Without Phoenix in the corpus, the unauth rate drops to **0%** (0/482 confirmed instances). Phoenix singlehandedly drives the entire population-scale unauthenticated exposure of the AI observability tier.

## What's on the line per platform

The data class flowing through each of these platforms is the same: every prompt, every model response, every chain step, every tool call, every customer query, every system prompt the operator has built. The Phoenix survey found:

- **Lillia** (lilliacare.ai) — Vertex AI patient-health platform, 40,000+ patients across GCC + India, two ADA-published clinical studies. Persistent `user_id` (`DRB_110008755478` format) tied to weight, sleep, blood-pressure logs.
- **MCM biodefense agent** — GPT-4o + LlamaIndex agent reasoning over a SQL pathogen-and-countermeasure database. Three Azure regions.
- **Kapture CRM** — three regions of customer-service trace data, ~1.06B cumulative tokens.
- **Chinese brand-monitor SaaS** — AWS Singapore active-active pair, ~2.17B tokens.
- **reputacion.digital** — single-host multi-surface exposure (Phoenix + NFS exports of Postgres data files + Prometheus + MailCatcher).

The Langfuse survey surfaced **identical operator classes** (UK AI Safety Institute, Amazon internal beta deployments, healthcare, fintech) — but every one of them was properly auth-fronted because Langfuse forces them to be.

The threat model isn't that Phoenix attracts worse operators. **The Langfuse population includes Amazon's own internal AI beta deployments and the UK government's AI Safety Institute.** Auth-by-default works at any operator sophistication tier; auth-by-environment-variable does not.

## Source-level findings per platform

### Phoenix — `PHOENIX_ENABLE_AUTH` default + two-tier admin model

`src/phoenix/config.py:1136`:
```python
def get_env_enable_auth() -> bool:
    return _bool_val(ENV_PHOENIX_ENABLE_AUTH, False)
```

Default is `False`. Operators who follow the quickstart get a publicly-readable trace store.

`src/phoenix/server/api/auth.py:78`:
```python
class IsAdminIfAuthEnabled(Authorization):
    def has_permission(self, source, info, **kwargs):
        if not info.context.auth_enabled:
            return True   # insecure-fail: ALLOW all when auth is off
        return isinstance(user := info.context.user, PhoenixUser) and user.is_admin
```

The `Secret.value` field that returns decrypted LLM provider API keys is decorated with `IsAdminIfAuthEnabled` — which **allows** unauthenticated callers through when `auth_enabled=False`. Latent stored-secret-extraction primitive on every Phoenix v15.x+ instance running auth-off (currently 0 actualized because operators haven't started storing API keys in Phoenix's secret manager yet).

### Langfuse — mandatory auth via NextAuth.js, all 73 public-API handlers wrapped

`web/src/features/public-api/server/createAuthedProjectAPIRoute.ts` wraps every public-API endpoint with `ApiAuthService.verifyAuthHeaderAndReturnScope`. The only intentionally unauthenticated endpoints are `/api/public/health` and `/api/public/ready`. There is **no env var that disables auth wholesale.** `AUTH_DISABLE_SIGNUP` and `AUTH_DISABLE_USERNAME_PASSWORD` disable specific credential providers; auth itself stays required.

Latent primitive: `ADMIN_API_KEY` for self-hosted instances. If operators set a weak value (`admin`, `password`), entire instance becomes accessible. Not probed against operators.

### Helicone — mandatory via BetterAuth or Supabase

Two auth backends, both required. No master toggle. Latent primitive: `BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"` literal value in three `.env.example` files. Operators who copy verbatim without rotating have predictable session signatures. Docker image documents using `openssl rand -base64 32` for production but the Quick Start docker-run command omits the secret entirely. Bundled MinIO defaults to `minioadmin:minioadmin`.

### LangSmith — closed-source, mandatory auth observed at endpoint level

All 27 confirmed instances return 401 on `/api/v1/sessions` and 401/403 on `/api/v1/tenants`. The unauthenticated `/api/v1/info` discloses `version` + `git_sha` + `license_expiration_time`. Standard practice for self-hosted enterprise products; enables population-scale version-targeted exploitation when CVEs land.

### Lunary, OpenLIT, Pezzo — mandatory auth, small populations

All three enforce auth at every API endpoint. NextAuth.js (OpenLIT), JWT (Lunary), or Nest.js JWT (Pezzo). Total population of ~25 confirmed instances combined; 0 unauthenticated.

## IP-direct-shadow as cross-platform methodology

Applied [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md) to all seven platforms. Per-platform results:

| Platform | IPs probed | Hosts with secondary port | Critical IP-shadow finds |
|---|--:|--:|--:|
| Phoenix | 92 | 25 (27%) | 5 — NFS+/postgres, MailHog with 139 emails, unauth Kibana, 2× Prometheus |
| Langfuse | 245 | ~15 (6%) | 1 — localhost-only Prometheus |
| LangSmith | 24 | 0 (0%) | 0 |
| Helicone | 19 | 2 (11%) | 0 — empty MailHog, login-required Cockpit |
| Lunary | 6 | 0 (0%) | 0 |
| OpenLIT | 20 | 1 (5%) | 1 — unauth node_exporter on Huawei Cloud China host |
| Pezzo | 1 | 0 (0%) | 0 |

**The Phoenix operator population has the highest co-location rate of secondary-surface exposures by an order of magnitude.** 27% of Phoenix-unauth hosts also expose NFS, MailHog, Kibana, or unauth Prometheus on the same IP. The next-closest is Helicone at 11%, and those are operator-side hardening misses (Cockpit binding, MailHog co-location) not platform issues.

This reinforces the hypothesis that Phoenix attracts a different operator population: people who deploy quickly with defaults across the board. The same operators who don't set `PHOENIX_ENABLE_AUTH=true` also don't firewall NFS, also don't move Prometheus to loopback, also leave MailHog running after they stop using it in dev. **The auth-off default is a marker for a broader hardening pattern.**

But Langfuse and LangSmith get **comparable enterprise customers** — Amazon, UK government, Morningstar, Consensys, enterprise databases — and the IP-shadow rate on those populations is 0-6%. So the operator-population delta is real but smaller than the auth-default delta. Both effects compound.

## Disclosure ladder (Phase 1 → Phase 2 → Phase 3)

This synthesis is the deliverable that closes Phase 1 of the [phase plan](../../../recon/2026-05-10-llm-sweep/PHASE-PLAN.md). Disclosure framing is not yet active — per the standing research-mode discipline, no operator emails or vendor pings have gone out. The synthesis is for the public OSINT corpus only.

When Phase 2 (depth-and-breadth deep-dives) and Phase 3 (meta-fingerprinter tool) complete, the disclosure layer engages:

- **Arize AI** (vendor) — upstream disclosure on the `PHOENIX_ENABLE_AUTH=False` default + `IsAdminIfAuthEnabled` insecure-fail pattern + `POST /v1/spans` bulk-export primitive. This is the highest-leverage disclosure target.
- **Helicone** (vendor) — separate vendor ping on the `BETTER_AUTH_SECRET` literal in `.env.example` + `minioadmin:minioadmin` defaults. Lower priority because the population isn't actually exposing the primitive yet.
- **Per-operator** — each of the 94 unauth Phoenix operators gets a coordinated-disclosure ping. The reputacion.digital, Lillia, Kapture, brand-monitor, and MCM operators are highest-priority.

But none of this happens until Phase 2 + 3 land. The research chain extends; the disclosure phase comes after.

## Methodology Insight #13 (this synthesis)

**Shipping defaults are load-bearing for population-scale security posture.**

Two platforms in the same product class with similar enterprise customer overlap can have wildly different unauthenticated-exposure rates (0% vs 25%) based on a single env-var default value. The vendor's choice of `False` vs `True` for the `*_ENABLE_AUTH` env var, made years ago at platform inception, propagates through every operator's deployment template, every container image, every Helm chart, every devops tutorial — and shows up at population scale as the dominant signal in security posture.

The implications:

1. **For vendors building self-hostable AI infrastructure:** auth-by-default isn't just a CIS-Benchmark checkbox. It's the single highest-leverage security control at population scale. Change one env var default and your real-world security posture jumps by an order of magnitude.
2. **For operators:** the question "is this product secure by default?" is more important than "is this product secure?" Both Phoenix and Langfuse are secure when configured correctly. Only one is secure by default.
3. **For researchers:** when an entire product category shows the same failure pattern, look at the shipping default first. Don't assume operators are uniformly bad at security; assume vendors are uniformly setting the default state.

This insight gets its own methodology document at [insight-13-shipping-defaults-load-bearing.md](../../methodology/insight-13-shipping-defaults-load-bearing.md).

## Next steps

1. ~~Phase 1: parallel population sweeps + synthesis~~ ✓ (this document)
2. **Phase 2: depth-and-breadth deep-dives** — start with Langfuse (largest population, second-most operator attribution); apply the source-level admin-gate audit + cross-version posture + mutation-surface enumeration + span sampling that we did on Phoenix
3. **Phase 3: meta-fingerprinter tool** — productize the per-platform fingerprints into a single aimap enumerator or standalone `visor-observability-hunt` tool

## Evidence pack

`~/recon/2026-05-10-llm-sweep/`
- `phoenix/` — full Phoenix recon
- `langfuse/` — Langfuse recon + 245-host IP-shadow
- `helicone/` — Helicone recon
- `langsmith/` — LangSmith recon
- `lunary/` `openlit/` `pezzo/` — small platforms

Per-platform case studies in `case-studies/commercial/`:
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md)
- [langfuse-llm-observability-survey-2026-05-10.md](langfuse-llm-observability-survey-2026-05-10.md)
- [helicone-llm-observability-survey-2026-05-10.md](helicone-llm-observability-survey-2026-05-10.md)
- [langsmith-llm-observability-survey-2026-05-10.md](langsmith-llm-observability-survey-2026-05-10.md)
- [observability-tier-small-platforms-survey-2026-05-10.md](observability-tier-small-platforms-survey-2026-05-10.md)

Methodology insights surfaced or applied during Phase 1:
- [Insight #12: Hostname-routed SSO doesn't protect the IP-direct shadow](../../methodology/insight-12-ip-direct-shadow.md)
- [Insight #13: Shipping defaults are load-bearing for population-scale security posture](../../methodology/insight-13-shipping-defaults-load-bearing.md) (new)
