---
title: AI observability tier — small platforms population sweep (Lunary, OpenLIT, Pezzo)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + per-platform auth probe + IP-direct-shadow check
---

# AI observability tier — small platforms sweep · 2026-05-10

NuClide Research · 2026-05-10

## Summary

Phase 1 finishing pass — three smaller AI-observability platforms surveyed in a single batch:

| Platform | Hits | Confirmed | Unauth | Unauth rate |
|---|--:|--:|--:|--:|
| **Lunary** | 6 | 1 | 0 | 0% |
| **OpenLIT** | 23 | 23 | 0 | 0% |
| **Pezzo** | 3 (title) / 65 (html) | 1 | 0 | 0% |
| Traceloop / OpenLLMetry | 0 | — | — | — |
| HoneyHive | 0 | — | — | — |

None of these platforms have a single unauthenticated instance in the public-internet population. The cross-platform synthesis is now decisive: **Phoenix is the sole observability platform shipping with default-no-auth.**

> **Reproduce with VisorBishop:** `visorbishop -i hosts.txt -ip-shadow`
> See [VisorBishop](https://github.com/Nicholas-Kloster/VisorBishop) or `visorplus bishop`.

## Lunary

`lunary.ai` — open-source LLM observability + prompt management. YC-backed.

**Population: 6 Shodan hits, 1 confirmed Lunary instance.**

| URL | Hostname | Status |
|---|---|---|
| `https://100.26.119.0:443` | `genesysappliedresearch.com` | **Confirmed Lunary** — `/api/v1/health` → `{"status":"OK"}`, `/v1/runs` → 401, `/v1/apps` → 401, `/v1/projects` → 401 |
| `https://164.152.34.46:443` | `panel.lunary.com.br` | Different product also called "Lunary Panel"; not the observability platform |
| `https://115.68.224.204:443` | `studio-lunary.com` | "Studio Lunary" — unrelated to observability Lunary |
| `100.26.119.0`, `54.151.225.117`, `52.77.135.119`, `13.228.107.89` | various ec2-amazonaws | non-Lunary or empty |

**Auth posture on the one confirmed instance:** all sensitive endpoints return 401 `{"message":"Invalid access token"}`. The publicly-exposed instance at `genesysappliedresearch.com` enforces auth on every protected route.

**Default secret in source?** Looked at the `lunary-ai/lunary` repo `.env.example` — no static literal secrets in committed examples; operators get `JWT_SECRET=changeme` placeholder values that won't function until rotated. Better than Helicone's literal `BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"` pattern.

## OpenLIT

`openlit.io` — open-source LLM/GenAI observability with built-in eval/playground/prompt-management.

**Population: 23 Shodan hits, 23 confirmed OpenLIT instances. 100% auth-fronted.**

All 23 hosts return identical behavior:

| Endpoint | Response |
|---|---|
| `/` | 307 redirect to `/login` (or 200 with the SPA HTML) |
| `/api/db/checkConnection` | **307 redirect to `/login?callbackUrl=...`** |
| `/api/ping` | **307 redirect to `/login?callbackUrl=...`** |
| `/api/prompt-hub` | **307 redirect to `/login?callbackUrl=...`** |

NextAuth.js cookie-based session middleware. Every API endpoint is wrapped in the auth middleware that redirects unauthenticated requests to the login flow. **0 unauthenticated finds.**

**Hosting distribution:** 11 AWS / 4 Azure / 2 GCP / 2 Oracle / 1 Huawei / 1 OVH / 1 DigitalOcean / 1 BT.

### IP-shadow find: `124.71.61.247` (Huawei Cloud China)

The Huawei Cloud China OpenLIT instance also exposes **`node_exporter` on port 9100 unauthenticated**. Standard Prometheus exporter, dumps full host metrics:
- CPU/memory/disk/network usage
- Process list (with `process_*` metrics)
- Go runtime stats (GC, goroutines)
- File handles, network connections

Not a credential leak directly but enables follow-on targeting: attacker learns the host's load patterns, disk usage trends, and process count without authenticating. Combined with the public-facing OpenLIT (which itself is auth-protected), this gives an attacker the operator's deployment fingerprint at no cost.

This is the same IP-direct-shadow class pattern as the Phoenix population's reputacion.digital host: the platform itself is properly configured, but co-located services on the same IP escape the platform's auth layer because they're separate services bound to the public interface.

## Pezzo

`pezzo.ai` — open-source LLMOps platform (prompt management, observability, dataset versioning). Originally TypeScript/Nest.js.

**Population: 3 hits via `http.title:"Pezzo"`, 1 confirmed Pezzo instance.**

The 65-hit `http.html:"pezzo"` dork is mostly noise (people named Pezzo, products with "Pezzo" as a substring, etc.). Only 3 hits with a literal `<title>Pezzo</title>`:

| URL | Hostname | Status |
|---|---|---|
| `http://101.34.81.6:4200` | (Tencent Cloud CN) | **Confirmed Pezzo** — frontend on 4200, Nest.js backend on 3000 |
| `https://167.234.237.175:443` | `gabrielpezzo.dev` | Personal site, unrelated |
| `http://167.71.37.226:7000` | (DigitalOcean) | Returns 404, no Pezzo |

The single Pezzo instance has the **same Next.js SPA-shadowing pattern** as Phoenix and Helicone — every endpoint returns the SPA HTML regardless of path. Probing the actual backend at port 3000 returned a 405 (Method Not Allowed) on GraphQL, indicating the API is reachable but requires the right method (POST). Without an API key the requests will fail.

Not exploitable from outside. Auth is enforced at the GraphQL layer; the SPA-shadow is a hardening problem (it makes it harder for legitimate users to debug their connection, not easier for attackers).

## Traceloop / OpenLLMetry and HoneyHive

Both returned 0 Shodan hits with the natural dorks. These platforms either:
- Run primarily as exporter libraries (the Traceloop OpenLLMetry SDK sends to their cloud)
- Use proprietary protocols that don't surface in HTTP fingerprints
- Have very small self-hosted populations

Not enough signal to survey at population scale.

## IP-direct-shadow sweep (30 unique IPs across the 3 platforms)

Same 11-port nmap sweep as the Phoenix/Langfuse/Helicone/LangSmith surveys.

**Findings:** 1 critical, 0 noteworthy elsewhere.

| IP | Platform | Find |
|---|---|---|
| 124.71.61.247 | OpenLIT (Huawei Cloud CN) | unauth node_exporter on 9100 |

Compare to prior platforms:

| Platform | Hosts with ANY secondary port | Critical IP-shadow finds |
|---|--:|--:|
| Phoenix | 25/92 (27%) | 5 (NFS+/postgres, MailHog with 139 emails, Kibana, 2× Prometheus) |
| Langfuse | ~15/245 (6%) | 1 (localhost-only Prometheus) |
| Helicone | 2/19 (11%) | 0 (empty MailHog, login-required Cockpit) |
| LangSmith | 0/24 (0%) | 0 |
| **Small platforms combined** | **1/30 (3%)** | **1** (the OpenLIT node_exporter find) |

The pattern: Phoenix operators have a 27% rate of co-located unauth services. Every other observability platform's operator population is at single-digit percentages.

## Cross-platform synthesis (Phase 1 essentially complete)

After 7 platforms surveyed (Phoenix + Langfuse + Helicone + LangSmith + Lunary + OpenLIT + Pezzo), the picture stabilizes:

| Platform | Population | Unauth rate | Auth model | Latent primitives |
|---|--:|--:|---|---|
| **Arize AI Phoenix** | 377 | **25%** | `PHOENIX_ENABLE_AUTH=False` default | `IsAdminIfAuthEnabled` insecure-fail (Secret.value), bulk-export at `POST /v1/spans` |
| Langfuse | 1,333 | 0% | Mandatory via NextAuth.js | `ADMIN_API_KEY` if weak |
| Helicone | 21 | 0% | Mandatory via BetterAuth or Supabase | `BETTER_AUTH_SECRET` literal in `.env.example`, `minioadmin:minioadmin` defaults |
| LangSmith | 27 | 0% | Mandatory (closed-source) | `/api/v1/info` discloses version+git_sha+license (info disclosure by design) |
| Lunary | 1 | 0% | Mandatory via JWT | No static secrets in committed examples |
| OpenLIT | 23 | 0% | Mandatory via NextAuth.js | None observed; node_exporter co-located (operator issue, not OpenLIT) |
| Pezzo | 1 | 0% | Mandatory via Nest.js JWT | None observed |

**The class-level finding is decisive:** Phoenix is the only observability platform in this cohort that ships with default-no-auth. The 25% Phoenix unauth rate at population scale is **not** a "this is hard to deploy securely" problem — it's a "Phoenix specifically ships with auth off" problem. Every other vendor in the same product category has made the opposite design choice.

The cross-platform synthesis will document this as **Methodology Insight #13: Shipping defaults are load-bearing for population-scale security posture.** Phoenix's `PHOENIX_ENABLE_AUTH=False` default produces 94 publicly-readable trace stores including patient health data (Lillia), biodefense MCM agent prompts, and ~5.5B tokens of customer LLM traffic. The same product class shipped with auth-required defaults produces 0 unauthenticated instances at 4-5× the population size.

## Next steps

1. ~~Lunary survey~~ ✓
2. ~~OpenLIT survey~~ ✓
3. ~~Pezzo survey~~ ✓
4. ~~Traceloop / HoneyHive scoping~~ ✓ (insufficient Shodan signal)
5. **Cross-platform SYNTHESIS document** — pull all seven platform surveys into one cross-cuts analysis
6. **Phase 2 — depth+breadth deep-dives** per the [phase plan](../../../recon/2026-05-10-llm-sweep/PHASE-PLAN.md)
7. **Phase 3 — meta-fingerprinter tool**

## Evidence pack

`~/recon/2026-05-10-llm-sweep/{lunary,openlit,pezzo}/`
- Per-platform host lists, probe results, IP-shadow nmap output
- `small-platforms-ip-shadow.{nmap,gnmap,xml}` — combined IP-shadow sweep across 30 unique IPs

Cross-references:
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md) — the outlier
- [langfuse-llm-observability-survey-2026-05-10.md](langfuse-llm-observability-survey-2026-05-10.md)
- [helicone-llm-observability-survey-2026-05-10.md](helicone-llm-observability-survey-2026-05-10.md)
- [langsmith-llm-observability-survey-2026-05-10.md](langsmith-llm-observability-survey-2026-05-10.md)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
