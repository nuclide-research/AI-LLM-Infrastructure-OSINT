---
type: survey
title: "Langfuse deep-dive: Phase 2 (source audit + latent primitives + extended IP-shadow)"
date: 2026-05-10
class: substrate
category: platform-deep-dive
status: research-active
methodology: source-level audit + cross-version posture + extended IP-direct-shadow
---

# Langfuse deep-dive · 2026-05-10 (Phase 2)

NuClide Research · 2026-05-10

## Summary

Phase 2 of the cross-platform observability sweep. Phoenix got its deep-dive on 2026-05-10 morning (admin-gate audit, mutation-surface triage, cross-version posture). Langfuse, the highest-population auth-by-default platform, now gets the same treatment.

The Phase 1 finding stands: **0 of 381 reachable Langfuse instances are unauthenticated.** Phase 2 looks inside that "0% unauth" headline for latent primitives, cross-version weaknesses, and operator-side hardening misses that don't appear in a simple auth-posture probe.

**Key findings:**

1. **Critical default-secret pattern in `.env.prod.example`:** `NEXTAUTH_SECRET="secret"`, `SALT="salt"`, `ENCRYPTION_KEY="0"*64`. Operators who copy the prod example without rotating these three values get forgeable session JWTs, predictable API-key hashes, and reversible LLM-provider credential encryption.
2. **Wider IP-shadow surface than Phase 1's quick check showed:** Postgres exposed on 5 operator hosts (publicly reachable on port 5432). ClickHouse, Redis, and Postgres co-located on `langfuse.revdot.ai`. One operator (`navgen.ai`) appears to have deliberately published `db.navgen.ai`, `redis.navgen.ai`, `langfuse.navgen.ai` as separate hostnames on the same host.
3. **`user.admin === true` is a cross-project bypass** in `protectedProjectProcedure`. Legitimate when the operator sets it; combined with weak `NEXTAUTH_SECRET="secret"` it becomes a full takeover primitive (forge JWT with `admin: true`, get every project).
4. **Cross-version posture is diverse:** 80+ unique versions across 381 hosts, range `2.65.0` → `3.173.0`. 22 instances still on v2.x. Auth posture is identical across versions.

Langfuse's auth posture is genuinely strong as a system; the failure modes are operator-side (weak secrets) and infrastructure-side (DB exposure) rather than platform vulnerabilities.

> **Reproduce with VisorBishop:** `visorbishop -i langfuse-confirmed-ips.txt -ip-shadow-all`
> See VisorBishop or `visorplus bishop`.

## Source-level admin-gate audit

`web/src/server/api/trpc.ts` defines five procedure types:

| Procedure | Auth state required |
|---|---|
| `publicProcedure` | No auth (but session readable if present) |
| `authenticatedProcedure` | Any logged-in user |
| `protectedProjectProcedure` | Logged-in user who is a member of the project (or has `admin: true`) |
| `protectedOrganizationProcedure` | Logged-in user member of the org (or `admin: true`) |
| `adminProcedure` | The instance super-admin (`user.admin === true`) |

**The `admin` bypass:** `protectedProjectProcedure` short-circuits the project-membership check when `ctx.session.user.admin === true`:

```ts
// from trpc.ts:280-310
if (!sessionProject) {
  if (ctx.session.user.admin === true) {
    // fetch org as it is not available in the session for admins
    const dbProject = await ctx.prisma.project.findFirst({
      where: { id: projectId, deletedAt: null },
    });
    // sendAdminAccessWebhook fires for audit logging
    return next({
      ctx: {
        session: {
          ...ctx.session,
          orgId: dbProject.orgId,
          orgRole: Role.OWNER,
          projectId,
          projectRole: Role.OWNER,
        },
      },
    });
  }
  // not a member
  throw new TRPCError({ code: "UNAUTHORIZED", message: "User is not a member of this project" });
}
```

When the user has `admin === true`, they get `Role.OWNER` on any project they touch. A webhook fires to notify the operator (`sendAdminAccessWebhook`), so this is legitimate behavior an operator opts into for instance-wide support access. But the webhook only logs; it doesn't prevent.

`web/src/features/rbac/utils/checkProjectAccess.ts` reinforces the bypass:

```ts
export function hasProjectAccess(p: HasProjectAccessParams): boolean {
  const isAdmin = hasOwnRole(p) ? p.admin : p.session?.user?.admin;
  if (isAdmin) return true;  // <-- bypass
  // ... normal role check
}
```

`user.admin` is sourced from the Prisma `users.admin` column at session-creation time (`web/src/server/auth.ts:780`). Operators promote a user to admin by direct DB write. There's no UI for it. This is intentional: admin is a "break glass" role.

**Combined with NEXTAUTH_SECRET="secret":** if an attacker can forge a JWT containing `user.admin=true`, they automatically pass `protectedProjectProcedure` and `hasProjectAccess` on every project. They get `Role.OWNER` on the entire instance.

## Latent primitive: `.env.prod.example` default secrets

`/tmp/langfuse-src/.env.prod.example` ships with three load-bearing defaults:

```bash
# For each of these, you can generate a new secret on the command line with:
# openssl rand -base64 32
NEXTAUTH_SECRET="secret" # https://next-auth.js.org/configuration/options#secret
SALT="salt" # salt used to hash api keys

# API level encryption for sensitive data
# Must be 256 bits, 64 string characters in hex format, generate via: openssl rand -hex 32
ENCRYPTION_KEY="0000000000000000000000000000000000000000000000000000000000000000"
```

The comments explicitly tell operators to generate new values, but the literal defaults are:

| Variable | Default | Impact if not rotated |
|---|---|---|
| `NEXTAUTH_SECRET` | `"secret"` | All NextAuth.js JWTs signed with literal `"secret"`. Attacker can forge any session including `user.admin = true`. Full instance takeover. |
| `SALT` | `"salt"` | API keys hashed with predictable salt. If DB or backup leaks, attacker computes hashes for guessed keys at zero cost. Rainbow-table-able. |
| `ENCRYPTION_KEY` | `"0"*64` (32 zero bytes) | All stored LLM provider API keys (OpenAI, Anthropic, Bedrock, Vertex, Azure) decryptable. If DB or backup leaks, attacker reads every operator's LLM provider creds in plaintext. |

This is materially worse than the analogous Helicone finding (`BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"` literal in `.env.example` files). Langfuse's `.env.prod.example`, explicitly the production template, uses `"secret"` and `"0"*64`, which are easier to detect, more memorable, and faster to fall into "wait, that looks like a placeholder" failure mode when reviewing.

The defensive comments help, but the population-scale prevalence is unknown. Operators who run through Langfuse's quickstart, copy the prod example, and skip the "generate secrets" step end up with all three defaults at once.

**We did not probe this latent primitive against live operators.** That requires active forgery testing (crafting a JWT signed with `"secret"`, sending it as a session cookie, observing whether the server accepts it). The probe shape would be unambiguous: send a `next-auth.session-token` cookie with a JWT signed with `"secret"` containing `email: attacker@example.com, admin: true, sub: <random>` and look for the server treating the request as authenticated. We're documenting at source level and stopping.

## LLM provider credential storage: strong vs. Phoenix's weakness

Where Phoenix's `Secret.value` GraphQL field returns the decrypted secret to anyone the `IsAdminIfAuthEnabled` check lets through (which is **everyone** when auth is off), Langfuse's `LlmApiKeys` Prisma model is defended at multiple layers:

1. **Schema-level secret separation**: the model has both `secretKey` (encrypted) and `displaySecretKey` (masked redacted preview like `...sk-XX`). Public endpoints only return `displaySecretKey`.
2. **Explicit SELECT exclusion**: `web/src/pages/api/public/llm-connections/index.ts` has an explicit Prisma `select` that omits `secretKey` and `extraHeaders`. The comment in the source: `// Explicitly exclude: secretKey, extraHeaders`.
3. **Encryption uses AES-256-GCM with random IV per encryption**: `packages/shared/src/encryption/encryption.ts`. Authenticated encryption; no malleability.
4. **`ENCRYPTION_KEY` env var required at startup**: if not set, `encrypt()` and `decrypt()` throw. No default value in the code (only in `.env.prod.example`).

The defensive pattern works. The remaining attack surface is the `.env.prod.example` `ENCRYPTION_KEY=0...0` default, but even that requires the attacker to have already obtained the encrypted blobs (via DB compromise or backup access). Not directly equivalent to Phoenix's "GraphQL field returns plaintext."

## tRPC mutation surface (~60 routers, hundreds of procedures)

Per `web/src/server/api/root.ts`, the appRouter pulls in 38+ sub-routers covering:

- Trace data: `traces`, `sessions`, `generations`, `events`, `scores`, `observations`
- Dataset management: `datasets`, `experiments`, `evals`
- Project / org: `projects`, `organizations`, `members`, `projectApiKeys`, `organizationApiKeys`
- User: `users`, `userAccount`, `credentials`, `notificationPreferences`
- Eval / quality: `scoreAnalytics`, `scoreConfigs`, `annotationQueues`, `comments`
- LLM connections: `llmApiKeys`, `llmSchemas`, `llmTools`, `defaultEvalModel`
- Integrations: `posthogIntegration`, `mixpanelIntegration`, `blobStorageIntegration`, `slack`
- EE: `cloudBilling`, `spendAlert`, `verifiedDomain`, `ssoConfig`, `uiCustomization`
- Ops: `backgroundMigrations`, `auditLogs`, `batchExport`, `automations`
- Misc: `dashboard`, `dashboardWidgets`, `tableViewPresets`, `media`, `naturalLanguageFilter`

Every procedure (other than `publicProcedure`) requires auth. The mutation surface is bigger than Phoenix's 40-mutation set, but unlike Phoenix's, **none of them are reachable on the default-no-auth state** because there is no default-no-auth state.

The single shared-secret risk: **`adminProcedure` is the most powerful**, it requires `user.admin === true`, gates org/project creation, membership management, ingestion replay, BullMQ admin, and `/api/admin/*` REST routes. A forged JWT with `admin: true` opens this entire surface.

## Cross-version posture (full 381-host distribution)

Extracted from `/api/public/health` response on every confirmed-reachable instance:

| Major.minor | Hosts |
|---|--:|
| 3.172.x | 32 |
| 3.137.x | 27 |
| 3.169.x | 20 |
| 2.95.x (legacy) | 18 |
| 3.150.x | 18 |
| 3.155.x | 18 |
| 3.162.x | 18 |
| 3.163.x | 14 |
| 3.152.x | 13 |
| 3.171.x | 12 |
| 3.75.x | 12 |
| 3.100.x | 10 |
| 3.160.x | 10 |
| (others) | 156 |

Range: `2.65.0` → `3.173.0` (latest at survey time). **22 instances on v2.x**, the rest on 3.x. All return 401 on `/api/public/projects`. Auth posture is consistent across versions. Langfuse has never shipped with a default-no-auth state across either major version.

The distribution is much more diverse than Phoenix's bimodal `13.15.0` + `15.2.0` pattern. Langfuse operators update sporadically but consistently.

## Extended IP-direct-shadow sweep (381 confirmed IPs, 18 ports)

Phase 1 swept 245 IP-direct-reachable Langfuse hosts on 11 ports. Phase 2 sweeps all 381 confirmed IPs (including the 136 hostname-only ones, whose backing IPs are still reachable for non-Langfuse co-located services) on **18 ports**, adding: 5432 (Postgres), 6379 (Redis), 8123 (ClickHouse), 8080 (nginx/alt-web), 8125 (statsd), 27017 (MongoDB), 3306 (MySQL).

| Port | Open hosts | Most likely service |
|---|--:|---|
| 3000 | 48 | Langfuse itself on alt port |
| 9090 | 27 | mostly non-Prometheus auth-protected; 1 unauth Prometheus (already characterized) |
| 5432 | **5** | **Postgres directly exposed** |
| 8080 | 3 | nginx / alt-web |
| 9100 | 1 | node_exporter |
| 8123 | **1** | **ClickHouse on `langfuse.revdot.ai`** (auth-protected) |
| 6379 | **1** | **Redis on `langfuse.revdot.ai`** (auth-protected) |

### Critical IP-shadow findings

#### `157.180.74.91` (`langfuse.revdot.ai`, Hetzner Finland): full data-plane on the public internet

| Port | Service | Auth |
|---|---|---|
| 3000 | Langfuse | ✓ auth |
| 5432 | Postgres | TCP open; password unknown |
| 6379 | Redis | `-NOAUTH Authentication required` ✓ |
| 8123 | **ClickHouse 25.6.13.41 (HTTP interface)** | **401 on SELECT** — `default` user has a password ✓ |
| 9090 | unknown (403) | ? |

This operator runs every piece of Langfuse's backing infrastructure on public IPs. The auth on each layer is properly configured. ClickHouse rejects `default` user without password, Redis requires AUTH. But the **exposure surface is what an attacker would feast on if any of those passwords leak via any side-channel**.

#### Five Langfuse operators expose Postgres on port 5432

| IP | Operator hostname | Country |
|---|---|---|
| 194.87.115.10 | `ai-langfuse.cynthia.africa` | NL (TimeWeb) |
| 207.38.87.133 | `langfuse.navgen.ai` (also `db.navgen.ai`, `redis.navgen.ai`) | US (Velia) |
| 3.239.231.128 | `langfuse-us.genloop.ai` | US (AWS) |
| 5.187.0.135 | `langfuse.claw.vallettasoftware.com` | DE (Fornex) |
| 157.180.74.91 | `langfuse.revdot.ai` | FI (Hetzner) |

The `navgen.ai` operator is the most striking. Separate public DNS records for `db.*`, `redis.*`, and `langfuse.*` on the same host suggest a deliberate decision to publish the database. Whether that's intentional cross-region replication or a misconfiguration is unclear. We don't probe credentials.

### Comparison vs Phase 1's IP-shadow

Phase 1 surfaced 1 unauth Prometheus (localhost-only). Phase 2 with extended port set surfaces:

- 5 hosts exposing Postgres
- 1 host exposing ClickHouse (auth-protected)
- 1 host exposing Redis (auth-protected)

The exposures exist, but they're properly auth-fronted. **Compared to Phoenix's 5 critical IP-shadow finds (NFS+postgres data files, MailHog with 139 emails, unauth Kibana, 2× Prometheus), Langfuse's IP-shadow is much cleaner even at higher resolution.**

## Per-host operator clustering (Phase 2 extension)

Phoenix's Phase 1 operator clustering surfaced Lillia, Kapture CRM, the Chinese brand-monitor pair, and the MCM biodefense agent. Via Jaccard similarity on Phoenix project names visible to unauth callers. **Langfuse can't be clustered the same way** because no project names are visible without auth.

Alternative attribution path: hostname patterns in the 381-host CT-log-derived list. The Phase 1 enumeration already surfaced UK AI Safety Institute, Amazon internal beta deployments, enterprisedb.com, morningstar.com, consensys.net, presidio.com, parakeethealth.io, etc. Phase 2 doesn't add new operators. The hostname signal saturates at Phase 1's resolution.

The five Postgres-exposed operators above are the actionable Phase 2 outputs from operator clustering.

## What's NOT a finding

Two things worth flagging as **non-findings** so future-me doesn't re-research them:

- **The 22 v2.x hosts** are not a legacy-auth-weakness pattern. v2.x Langfuse enforces auth identically to v3.x. The version diversity reflects operator update cadence, not a security delta.
- **The 27 port-9090 hosts** are mostly not Prometheus. 26 of 27 return auth-protected responses or empty/blocked. Only the `46.105.53.84` (OVH France) Prometheus is unauth, and it scrapes only localhost. Phoenix's reputacion.digital pattern (58-target Prometheus + DoS endpoints) does not exist on the Langfuse population.

## Next steps (research, not disclosure-yet)

1. ~~Phase 2 source-level admin-gate audit~~ ✓
2. ~~Latent-primitive enumeration (default secrets in `.env.prod.example`)~~ ✓
3. ~~Cross-version posture sweep~~ ✓
4. ~~Mutation-surface triage~~ ✓
5. ~~Extended IP-direct-shadow sweep (18 ports, 381 hosts)~~ ✓
6. **Phase 2 deep-dive on Helicone**, verify whether the `BETTER_AUTH_SECRET` literal default is actualized in the wild (signaling test, not credential test)
7. **Phase 2 deep-dive on LangSmith**, closed-source, limited source-audit; focus on the `/api/v1/info` disclosure vector
8. **Phase 3 meta-fingerprinter**, productize per-platform fingerprints

## Evidence pack

`~/recon/2026-05-10-llm-sweep/langfuse/`
- All Phase 1 artifacts (host list, probe results, 245-IP shadow sweep)
- `all-confirmed-ips.txt`: 381 unique IPs from confirmed Langfuse instances
- `ip-shadow/phase2-deepdive.{nmap,gnmap,xml}`: extended 18-port sweep across 381 IPs

Cross-references:
- [langfuse-llm-observability-survey-2026-05-10.md](langfuse-llm-observability-survey-2026-05-10.md) (Phase 1)
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md) (compare: 25% unauth, IsAdminIfAuthEnabled insecure-fail)
- [SYNTHESIS-ai-observability-2026-05-10.md](SYNTHESIS-ai-observability-2026-05-10.md) (Phase 1 synthesis)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
- [Methodology Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md)
