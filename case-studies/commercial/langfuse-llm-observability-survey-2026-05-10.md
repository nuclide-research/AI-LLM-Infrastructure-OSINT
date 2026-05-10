---
title: Langfuse LLM-observability population survey (1,333-host population, 0% unauth)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + source-level auth audit + IP-direct-shadow check
---

# Langfuse LLM-observability survey · 2026-05-10

NuClide Research · 2026-05-10

## Summary

Langfuse is the second platform in the AI-observability tier we're surveying after Arize AI's Phoenix. Same product class, same target market, same self-hostable OSS model. The survey is a hypothesis test: does Langfuse share Phoenix's default-no-auth shipping pattern?

**Answer: no.** Of 1,333 Langfuse hosts identified via Shodan, **0 are unauthenticated** at the population level. Every reachable instance enforces auth on the `/api/public/projects` endpoint. The 25% Phoenix unauth rate doesn't transfer.

This is a meaningful negative result for the cross-platform thesis. The pattern Phoenix exposes is **not** universal to LLM-observability platforms — it's a vendor-specific design choice. Langfuse's architecture forecloses the failure mode at design time; Phoenix's permits it via a default-False env var.

## Discovery dorks

Three candidates tested:

| Dork | Hits | Signal |
|---|--:|---|
| `http.title:"Langfuse"` | 3 | Title doesn't reach Shodan because Langfuse is a SPA |
| `http.html:"langfuse"` | 3,426 | Wide; catches tutorials, GitHub copies, marketing pages |
| `ssl.cert.subject.cn:"langfuse"` | **1,454** | Clean signal; matches operators who put a `langfuse` subdomain in their TLS cert |
| `http.html:"_next/static" "langfuse"` | 3,244 | Catches Langfuse + generic Next.js with Langfuse mention |

Going with `ssl.cert.subject.cn:"langfuse"` for the population probe. 1,333 unique URLs after Shodan dedup.

## Population

| Metric | Value |
|---|---|
| Total hosts (cert-CN matched) | 1,333 |
| Reachable as Langfuse via direct IP probe | 245 (18%) |
| Reachable as Langfuse via hostname probe | 381 (29%) — includes the 245 plus 136 hostname-only |
| Properly auth-protected (401/403 on `/api/public/projects`) | **381 (100% of reachable)** |
| **Unauthenticated** | **0** |
| Not reachable (LB frontend without backend route on test path) | 950 |

**Geographic distribution:** US 883, JP 73, IE 70, DE 60, SG 43, GB 32, IN 26, NL 26, CA 22, AU 22.
**Hosting:** Heavy AWS+GCP+Azure. Google 309, Amazon Technologies 263, Amazon.com 183, Amazon Data Services NoVa 155, Microsoft 71, Amazon JP 56, Amazon IE 36, Hetzner 34. **A100 ROW GmbH at 34** — interesting; Hetzner sub-brand.

**Versions in the reachable subset** (extracted from `/api/public/health`):

Most-deployed: `3.137.0` (27), `3.172.1` (26), `3.169.0` (20), `3.162.0` (18), `3.150.0` (18), `3.155.1` (16). Latest at survey time: `3.173.0` per Langfuse's GitHub.

The version distribution skews recent — operators update Langfuse much more aggressively than they do Phoenix. The Phoenix population spanned 4.x → 15.x with a long legacy tail; Langfuse's tail tops out at `2.95.11` and most deployments are 3.x within ~30 versions of head.

## Source-level auth audit

`web/src/features/public-api/server/createAuthedProjectAPIRoute.ts` wraps every public-API endpoint with `ApiAuthService.verifyAuthHeaderAndReturnScope`. Walking `web/src/pages/api/public/` (73 handler files):

- **All 73 handlers** are wrapped by `createAuthedProjectAPIRoute` or `withMiddlewares`
- The only intentionally unauthenticated endpoints are `/api/public/health` and `/api/public/ready` (operational liveness checks)
- **No `AUTH_DISABLE_ALL` or equivalent master switch exists.** The env vars `AUTH_DISABLE_SIGNUP` and `AUTH_DISABLE_USERNAME_PASSWORD` disable *credential providers*, not auth itself. Operators can run with only SSO/OAuth login enabled, but they cannot run without auth.

This is the **structural difference** from Phoenix:

| Aspect | Phoenix | Langfuse |
|---|---|---|
| Master "auth off" toggle | `PHOENIX_ENABLE_AUTH=False` (default) | None — auth is always required |
| Public-API auth wrapper | Some endpoints have it; some (incl. `POST /v1/spans`) explicitly skip | All public-API endpoints wrapped |
| Admin auth class | Two-tier with insecure-fail variant (`IsAdminIfAuthEnabled`) | Single-tier; admin operations require `ADMIN_API_KEY` env var (self-hosted only) |
| Default shipping state | Wide open | Closed |

## ADMIN_API_KEY — the latent equivalent of Phoenix's insecure-fail

Langfuse's self-hosted instances support an `ADMIN_API_KEY` env var. When set, the bearer key plus matching `x-langfuse-admin-api-key` header plus `x-langfuse-project-id` header grants admin access to any project on that instance. From `createAuthedProjectAPIRoute.ts`:

```ts
/**
 * Allow authentication via ADMIN_API_KEY for self-hosted instances only.
 * Admin API key authentication requires:
 * - Authorization: Bearer <ADMIN_API_KEY>
 * - x-langfuse-admin-api-key: <ADMIN_API_KEY> (must match exactly for redundancy)
 * - x-langfuse-project-id: <project-id> (target project)
 *
 * This authentication method is ONLY available when NEXT_PUBLIC_LANGFUSE_CLOUD_REGION
 * is not set (self-hosted).
 */
```

The threat model is similar to Phoenix's `IsAdminIfAuthEnabled`: if an operator sets a weak `ADMIN_API_KEY` (`admin`, `password`, `changeme`, etc.) the entire instance becomes accessible to anyone who guesses it. We did **not** probe this against the live population — that would be active credential testing on third-party infrastructure, which is outside the read-only scope of this survey.

The defensive properties Langfuse gets right here:

- The env var is **not set by default**; operators must explicitly opt in
- The auth method is **gated by `NEXT_PUBLIC_LANGFUSE_CLOUD_REGION`**; the Cloud-hosted Langfuse doesn't expose the path at all
- The two-header redundancy (`Authorization` + `x-langfuse-admin-api-key`) means accidental leakage of one header doesn't grant access

Worth flagging as a research follow-on: spec-confirmed primitive; population prevalence unknown.

## IP-direct-shadow sweep across 245 IP-direct-reachable Langfuse hosts

Applying [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md) — the SSO-bypass pattern we surfaced in the Phoenix survey. Same 11-port nmap sweep (NFS, rpcbind, MailCatcher, MailHog, Prometheus, AlertManager, node_exporter, Kibana, Elasticsearch, Grafana).

Sweep covered the 245 hosts that respond to Langfuse on the direct IP (excluding the 136 hostname-only ones, which by definition don't expose anything on the bare IP).

| Port | Service | Hits | Notes |
|---|---|--:|---|
| 3000 | Often Langfuse-on-3000 itself | 43 | 40 are Langfuse on alt port (all returned 401 on `/api/public/projects`); 0 Grafana found |
| 9090 | Prometheus | 24 | **1 unauth** (`46.105.53.84` / `langfuse.astusse.dev`, OVH France) scraping only `localhost:9100`. 23 are non-Prometheus (auth-fronted or unrelated apps) |
| 9100 | node_exporter | 1 | Same host as the unauth Prometheus |

**Compared to Phoenix's IP-shadow result:** Phoenix had 5 hosts with real primitives (NFS+/postgres exposure, MailHog with 139 captured emails, unauth Kibana, two unauth Prometheus instances). Langfuse has effectively **0 critical IP-shadow primitives** — the one unauth Prometheus only scrapes its own local node and has no internal-network leakage.

The IP-shadow methodology produces signal proportional to **whether the platform's operators tend to co-locate their AI stack on the same host with weak auth on other services**. Phoenix's operators do; Langfuse's don't. That's a function of who deploys each platform, not the platform itself.

## Operator footprint (no exposure, but notable for cross-platform pattern)

Even without unauth findings, the hostname enumeration surfaces who's running Langfuse internally. A non-noise subset of operator hostnames:

| Operator class | Examples |
|---|---|
| **AI labs / enterprise AI** | `cloud.langfuse.com`, `core-langfuse.dev.i.ai.gov.uk` (UK AI Safety Institute), `langfuse.parakeethealth.io`, `langfuse.cynthia.africa`, `langfuse.kodosumi.io`, `langfuse.superme.ai`, `langfuse.api.auralis.ai`, `langfuse.mangrovesai.com` |
| **Amazon internal beta** | `langfuse-beta.csevalfuse.cs.amazon.dev`, `beta-langfuse.selection-agent.selling-partners.amazon.dev`, `beta-langfuse.transparency.ai.amazon.dev`, `beta.langfuse.aidp.dex.amazon.dev`, `beta.langfuse.cls.amazon.dev`, `beta.langfuse.ring.amazon.dev`, `danhn-bay.dev.duenna-langfuse.spx.amazon.dev` |
| **Enterprise customers** | `agent-eval-langfuse.dev.enterprisedb.com`, `langfuse.regology.com`, `morningstar.com` Langfuse, `consensys.net` Langfuse, `presidio.com` Langfuse, `capco-ch-ai-lab-langfuse-v3-gateway.unique.configuration.azure-api.net` |
| **Health / regulated** | `langfuse.parakeethealth.io` |
| **Government** | `core-langfuse.dev.i.ai.gov.uk` (UK AI Safety Institute) |
| **Crypto / fintech** | `langfuse.xbanker.ai`, `langfuse.deckster.app.presidio.com` |

This list is **not** an exposure list — every one of these hosts is properly auth-fronted on the public API. It's a market-share signal: Langfuse has deeply penetrated regulated enterprise AI deployments where Phoenix's default-no-auth would be unacceptable. The hypothesis worth flagging: **operators who care about auth picked Langfuse; operators who don't picked Phoenix.** That's not necessarily true, but it would explain the population-level auth-rate delta.

## Cross-platform synthesis (preliminary)

| Platform | Total hosts | Reachable | Unauth | Unauth rate |
|---|--:|--:|--:|--:|
| **Phoenix** | 377 | 357 | 94 | **25%** |
| **Langfuse** | 1,333 | 381 | 0 | **0%** |

The two platforms occupy opposite ends of the auth-by-default spectrum. Possible explanations (testable against further platforms):

1. **Vendor design choice** (most likely): Langfuse ships auth-on; Phoenix ships auth-off. Operators inherit the default.
2. **Market segmentation**: Langfuse attracts auth-conscious operators (enterprise, regulated). Phoenix attracts experimentation-first operators (research, prototyping). Both reasonable to hypothesize.
3. **Deployment friction**: Langfuse's auth is easier to set up (NextAuth.js handles all the OAuth providers out of the box). Phoenix's auth requires additional `PHOENIX_SECRET` + DB setup, so operators skip it.

The **synthesis-document deliverable** at the end of Phase 1 of the cross-platform sweep will revisit these once we have Helicone, LangSmith, Lunary, and others in the corpus.

## Next steps (research, not disclosure-yet)

1. ~~Shodan harvest~~ ✓ 1,333 hosts via `ssl.cert.subject.cn:"langfuse"`
2. ~~Auth-posture probe~~ ✓ 0% unauth
3. ~~Source-level audit (auth wrapper, default settings, ADMIN_API_KEY)~~ ✓
4. ~~IP-direct-shadow sweep~~ ✓ 1 unauth Prometheus, no critical primitives
5. ~~Operator hostname enumeration~~ ✓ surfaced UK AI Safety Institute, Amazon internal betas, enterprise customers — all properly auth-fronted
6. **Latent ADMIN_API_KEY probe** (deferred) — would require active credential testing; not in current scope
7. **Helicone population survey** — next platform in the cross-platform sweep
8. **Cross-platform synthesis document** — after Helicone + LangSmith + 2-3 more land

## Evidence pack

`~/recon/2026-05-10-llm-sweep/langfuse/`
- `langfuse-tls.json.gz` — 1,333-host Shodan harvest (TLS-cert-CN dork)
- `langfuse-urls.tsv` — deduplicated URL list
- `langfuse-probe-results.json` — full per-host probe results (health + projects endpoint × direct-IP + hostname)
- `ip-direct-ips.txt` — 245 IPs that respond to Langfuse on direct IP path
- `ip-shadow/phase1-syn-sweep.{nmap,gnmap,xml}` — IP-shadow port sweep on the 245 IPs
- `ip-shadow/p3000-results.tsv` — per-port-3000 service identification
- `ip-shadow/prom-results.tsv` — per-port-9090 Prometheus auth check
- `port3000-langfuse-auth.tsv` — auth-posture verification on 40 Langfuse-on-port-3000 hosts
- `probe.py` — concurrent probe script (Python stdlib, 20 workers)

Cross-references:
- Phoenix counterpart: [`phoenix-llm-observability-survey-2026-05-10.md`](phoenix-llm-observability-survey-2026-05-10.md)
- Methodology: [`Insight #12 (IP-direct-shadow)`](../../methodology/insight-12-ip-direct-shadow.md)
