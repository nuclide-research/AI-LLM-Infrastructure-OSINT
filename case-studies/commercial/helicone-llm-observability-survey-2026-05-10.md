---
type: survey
title: Helicone LLM-observability population survey (21-host self-hosted population)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + source-level auth audit + IP-direct-shadow check
---

# Helicone LLM-observability survey · 2026-05-10

NuClide Research · 2026-05-10

## Summary

Third platform in the AI-observability cross-platform sweep, after [Phoenix](phoenix-llm-observability-survey-2026-05-10.md) (25% unauth) and [Langfuse](langfuse-llm-observability-survey-2026-05-10.md) (0% unauth). Helicone is a YC-backed LLM observability + AI gateway product, SOC 2 + GDPR compliant, primarily SaaS but offers a Docker-based self-host path.

**Population finding: 21 self-hosted Helicone instances total.** Almost an order of magnitude smaller than Phoenix or Langfuse — a SaaS-first product. Of those:
- 5 are Helicone's own AWS infrastructure (`api.helicone.ai`, `jawn.helicone.ai`, `eu.api.helicone.ai`)
- ~16 are self-hosted operator instances
- **0 unauthenticated** (auth model is mandatory via BetterAuth or Supabase; no master "auth off" toggle)
- 2 secondary-surface IP-shadow finds (1 MailHog empty, 1 Cockpit login-required)

The cross-platform pattern continues: Helicone is closer to Langfuse than Phoenix. Mandatory-auth by design. The 25% Phoenix rate remains a Phoenix-specific phenomenon.

> **Reproduce with VisorBishop:** `visorbishop -i helicone-hosts.txt -ip-shadow`
> See VisorBishop or `visorplus bishop`.

## Discovery dorks

| Dork | Hits |
|---|--:|
| `http.title:"Helicone"` | 6 |
| `http.html:"helicone"` | 11 |
| `ssl.cert.subject.cn:"helicone"` | 10 |
| `http.html:"helicone.ai"` | 6 |
| `http.html:"_next/static" "helicone"` | 0 |

Combining dorks 2+3 and deduplicating: **21 unique hosts**.

The order-of-magnitude smaller population than Phoenix (377) or Langfuse (1,333) reflects Helicone's product strategy: they push customers to the cloud SaaS by default. The Docker self-host path exists (documented at `docs/getting-started/self-host/docker.mdx`) but is rarely exercised at population scale.

## Population

| Metric | Value |
|---|---|
| Total unique hosts (port+IP combinations) | 21 |
| Helicone's own AWS infrastructure | 5 (`api.helicone.ai` ×3, `eu.api.helicone.ai` ×2 across AWS regions) |
| Self-hosted operator instances | ~16 |
| Properly auth-protected on every probe | All — 0 unauthenticated |
| Hosts where /api/health returns Helicone-shape | 0 (all returned 404 or Next.js SPA HTML) |

**Self-hosted operator identifications visible in hostnames:**

| Hostname | IP | Org |
|---|---|---|
| `helicone.eclypsium.io` | 34.168.167.203 | Google LLC (US) — Eclypsium is firmware/supply-chain security |
| `helicone.lhapps.net` | 34.36.125.39 | Google LLC (US) |
| `helicone.boy01-vir.usa.egrx.us` | 20.55.49.156 | Microsoft (US) |
| `helicone.yahyah.fun` | 47.251.252.141 | Alibaba Cloud US |
| `api-helicone.dev.bridge-mt.net` | 88.99.171.64 | Hetzner DE |
| `stg-promptproof.hatchandco.cloud` | 34.149.150.86 | Google LLC (US) — PromptProof, an LLM prompt-testing product built on Helicone |
| `agoont.com` | 107.191.51.227 | Vultr — "agoont - AI Gateway Benchmarks" |
| `ai.daf-yomi.com` | 5.100.255.188 | O.M.C. Computers & Communications (Israel) — Hebrew Daf Yomi study portal using Helicone backend |
| `q7core.com` | 74.208.17.59 | IONOS (US) |
| `benchmarkit.solutions` | 137.184.217.47 | DigitalOcean (US) |

## Source-level auth audit

Helicone supports two auth backends, both mandatory:

1. **Supabase** (default for the cloud product; available for self-hosters via `web/.env.example`) — uses Postgres + Supabase Auth's row-level security. JWT-based session tokens issued by Supabase.
2. **BetterAuth** (introduced for the Docker self-host path; `web/.env.hosted.example` and `web/.env.example.better-auth`) — Next.js-native auth using cookie-based sessions signed with `BETTER_AUTH_SECRET`.

The `.env.example` files include a literal default secret:

```
BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"
```

This identical string appears in three .env.example files (`web/`, `valhalla/jawn/`, `docker/`). Operators who copy any of those verbatim and don't rotate the secret have predictable session-cookie signatures — a forgery primitive for anyone with the value. The official `docker.mdx` documentation **does** explicitly call out using `openssl rand -base64 32` for production deployments, but the Quick Start docker-run command in the same doc omits `BETTER_AUTH_SECRET` entirely, defaulting to `change-me-in-production` per the documented env-table.

The MinIO bundled with Helicone's `helicone-all-in-one` Docker image defaults to:

```
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
```

If an operator exposes the bundled S3 to the public internet (port 9080 in the documented setup), these defaults stand. The MinIO API would accept these credentials and grant full read/write to the `request-response-storage` bucket — which is where Helicone stores the bodies of every captured LLM request and response.

**Latent-primitive summary:**

| Primitive | Source-level confirmation | Population probing |
|---|---|---|
| Predictable `BETTER_AUTH_SECRET=MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi` | Yes — literal in 3 `.env.example` files | Not probed (would require credential testing) |
| `change-me-in-production` `BETTER_AUTH_SECRET` default | Yes — documented in env-table | Not probed |
| `minioadmin:minioadmin` for bundled S3 | Yes — documented default | Not probed (no S3 port exposure surfaced in IP-shadow sweep) |

Probing for these primitives against the live operator population would constitute credential testing on third-party infrastructure — outside the read-only scope of this survey. Documented for the threat-model writeup.

## Auth-posture probe across the 21 hosts

All 21 hosts tested with `POST /v1/oai/chat/completions` (Helicone's OpenAI-compatible proxy endpoint) without auth headers. Results:

| Response shape | Count | Interpretation |
|---|--:|---|
| Next.js SPA HTML returned (200, but doesn't reach the backend) | 9 | Marketing-page shadow over the API; backend isn't actually receiving the request |
| 404 from backend or LB | 7 | Endpoint not exposed externally |
| Empty response / timeout | 3 | LB or instance unreachable |
| 307 redirect to auth | 2 | Properly auth-gated |
| 200 actually proxying to LLM | **0** | No LLMjacking primitive found |

The SPA-HTML-on-POST pattern is the same shadowing behavior we identified on Phoenix port 6006 — the Next.js router returns the marketing page for any route the React app doesn't explicitly handle, which makes external probing harder than a clean "404 from FastAPI" response would. False-positive 200s during initial probing.

## IP-direct-shadow sweep

Applying [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md). 11-port nmap sweep against the 19 unique IPs in the Helicone population (excluding two AWS LB-only addresses):

| Port | Hits | Verified service |
|---|--:|---|
| 3000 | 4 | Helicone web UI on alt port (its default port — not a shadow finding) |
| 111 | 1 | rpcbind on `137.184.217.47` |
| 8025 | 1 | **MailHog** on `188.34.196.197` (currently empty store) |
| 9090 | 1 | **Cockpit** (Linux server admin UI) on `62.171.190.103`, login-required |

### Finding: MailHog at `188.34.196.197:8025` (api-helicone.dev.bridge-mt.net likely)

The Hetzner DE host running Helicone also has MailHog running on port 8025 — the same pattern we found on the Teetsh operator in the Phoenix sweep. Currently `GET /api/v2/messages?limit=0` returns `{"total":0}` — the store is empty. The exposure is latent: any time the application sends mail (password resets, account verification, notifications), captured messages become publicly readable until the operator clears the store.

### Finding: Cockpit at `62.171.190.103:9090` (vmi3071145.contaboserver.net, Contabo DE)

Cockpit is the Red Hat web-based Linux server admin UI. Login-required at `/login`. Not unauth-exploitable directly, but binding Cockpit to `0.0.0.0:9090` instead of `127.0.0.1:9090` (or putting it behind a VPN) is a hardening miss. Default Cockpit auth uses system credentials; weak SSH passwords on the host become Cockpit login attempts at scale.

Neither finding is a Helicone vulnerability. Both are co-located operator services exposed alongside Helicone — the same IP-direct-shadow class pattern we documented in the Phoenix case study.

## Cross-platform synthesis (preliminary, 3 platforms in)

| Platform | Population | Reachable | Unauth | Unauth rate | IP-shadow finds |
|---|--:|--:|--:|--:|---|
| **Phoenix** | 377 | 357 | 94 | **25%** | 5 critical (NFS, MailHog with 139 emails, Kibana, 2× Prometheus) |
| **Langfuse** | 1,333 | 381 | 0 | **0%** | 1 minor (localhost-scoped Prometheus) |
| **Helicone** | 21 | ~16 | 0 | **0%** | 2 minor (empty MailHog, login-required Cockpit) |

The pattern across three platforms:

- **Phoenix is the outlier.** Its default-no-auth shipping behavior is unique among the three observed so far.
- **Helicone has the smallest population by far** — SaaS-first product strategy.
- **Both Langfuse and Helicone enforce auth by design.** Operators cannot turn auth off, only configure which credential providers are accepted.
- **The IP-shadow methodology surfaces operator-side misconfigurations** regardless of the platform's auth strength. Operators who deploy ANY of these platforms on a Linux host tend to expose other services on that same host.

Latent primitives in Helicone are different in kind from Phoenix's:

| Primitive class | Phoenix | Helicone |
|---|---|---|
| Default auth state | Auth-off (configurable on) | Auth-on (always) |
| Default secret | `PHOENIX_SECRET` must be set if auth enabled | `BETTER_AUTH_SECRET=MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi` literally in `.env.example` |
| Default service credentials | None | `minioadmin:minioadmin` for bundled S3 |
| Latent exploitation | Stored-secret extraction via GraphQL field | Session-token forgery if default `BETTER_AUTH_SECRET` not rotated |

Helicone's latent primitives require either (a) credential testing or (b) cryptographic forgery — both materially harder than Phoenix's "the GraphQL schema is reachable unauthenticated" finding. Different threat models.

## Next steps (research, not disclosure-yet)

1. ~~Shodan harvest~~ ✓ 21 hosts total
2. ~~Source-level auth audit~~ ✓ BetterAuth + Supabase, mandatory; default-secret pattern documented
3. ~~Auth-posture probe across 21 hosts~~ ✓ 0 unauth findings
4. ~~IP-direct-shadow sweep~~ ✓ 2 minor finds (MailHog empty, Cockpit login-required)
5. **Default-secret prevalence probe** (deferred) — would require active forgery testing
6. **LangSmith population survey** — next platform in the cross-platform sweep
7. **Cross-platform synthesis document** — after LangSmith + 2-3 more land

## Evidence pack

`~/recon/2026-05-10-llm-sweep/helicone/`
- `helicone-hosts.tsv` — deduplicated Shodan hit list (21 unique URL/hostname pairs)
- `helicone-ips.txt` — 19 unique IPs
- `helicone-probe-results.tsv` — per-host auth-posture probe results
- `helicone-ip-shadow.{nmap,gnmap,xml}` — IP-shadow port sweep

Cross-references:
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md) (25% unauth)
- [langfuse-llm-observability-survey-2026-05-10.md](langfuse-llm-observability-survey-2026-05-10.md) (0% unauth)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
