---
type: survey
title: "Helicone deep-dive: Phase 2 (default ClickHouse exposure on benchmarkit.solutions)"
date: 2026-05-10
class: substrate
category: platform-deep-dive
status: research-active
methodology: source audit + extended IP-shadow + confirmed actualized primitive
---

# Helicone deep-dive · 2026-05-10 (Phase 2)

NuClide Research · 2026-05-10

## Summary

Phase 2 of the Helicone survey. The Phase 1 finding was 21 hosts total with **0% unauth** on the platform's own auth surfaces (BetterAuth/Supabase enforce auth correctly). Phase 2 looks beyond the platform's auth layer at:

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K7003, K942

<!-- ksat-tag:auto-generated:end -->

1. The latent `BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"` literal default in `.env.example` (documented in Phase 1, not probed)
2. The Docker Compose default port bindings
3. Co-located service exposure on the same 19 Helicone IPs

**Key finding: One operator (`benchmarkit.solutions` / `137.184.217.47` / DigitalOcean US) exposes ClickHouse 23.4.2.11 on port 8123 with no authentication. Full read access to the Helicone trace store including `request_response_rmt` (every captured LLM request/response body).**

Root cause: Helicone's `docker/docker-compose.yml` binds ClickHouse port 8123 to host port 18123 on `0.0.0.0` (not `127.0.0.1`), and ships with `CLICKHOUSE_USER: default` and no `CLICKHOUSE_PASSWORD`. Operators running the standard Helicone Docker setup on a host without firewall rules end up with ClickHouse on the public internet with the no-password `default` user.

This is **shipping-defaults adjacent**: not an `*_ENABLE_AUTH=False` switch like Phoenix, but a default port-binding pattern in the official docker-compose that produces a similar population-scale risk for operators who don't add a layered firewall.

> **Reproduce with VisorBishop:** `visorbishop -t https://137.184.217.47:443 -ip-shadow`
> See VisorBishop or `visorplus bishop`.

## Critical actualized find: `benchmarkit.solutions` (`137.184.217.47`). Unauth ClickHouse

| Aspect | Value |
|---|---|
| URL | `http://137.184.217.47:8123/` |
| Operator | `benchmarkit.solutions` (DigitalOcean US) |
| ClickHouse version | **23.4.2.11** (July 2023 release; multiple CVEs since) |
| Databases visible | `INFORMATION_SCHEMA`, `default`, `information_schema`, `system` |
| Tables in `default` | **14** including `request_response_rmt`, `request_response_log`, `request_response_versioned`, `response_copy_v1/v2/v3`, `properties_v3`, `rate_limit_log` |
| Auth on `default` user | **None** — `GET /?query=SELECT+1` returns `1` HTTP 200 |
| Auth on `/ping` | Open (`Ok.`) |

Confirmed via:
```
$ curl -sk "http://137.184.217.47:8123/?query=SELECT+1"
1
$ curl -sk "http://137.184.217.47:8123/?query=SHOW+DATABASES"
INFORMATION_SCHEMA
default
information_schema
system
$ curl -sk "http://137.184.217.47:8123/?query=SELECT+version()"
23.4.2.11
```

The `request_response_rmt` table is Helicone's main trace store. Per `clickhouse/migrations/schema_31_request_response_versioned_merge_tree_m1.sql` and follow-ups, it holds:
- Full LLM request body (every prompt)
- Full LLM response body (every completion)
- Token counts, cost, latency
- Provider, model name
- User/session/organization metadata
- Country codes (for routing analytics)
- Cache state

This is the same data class that the Phoenix population leaks via unauthenticated GraphQL, but the leak vector is different (Phoenix: GraphQL on port 6006 unauth; Helicone: ClickHouse on port 8123 unauth via the Docker default).

**We confirmed structure and version but did not query row contents.** Counting rows or selecting bodies would constitute exfiltration. The exposure is fully documented at structure level.

## Root cause: Helicone docker-compose.yml port binding

`docker/docker-compose.yml`:

```yaml
  clickhouse:
    image: clickhouse/clickhouse-server:24.3.13.40
    container_name: helicone-clickhouse
    ports:
      - "18123:8123" # HTTP interface
      - "19000:9000" # Native interface
    volumes:
      - clickhouse_data:/var/lib/clickhouse
```

The `"18123:8123"` syntax (no IP prefix) binds the host port to `0.0.0.0:18123`, exposing ClickHouse to every interface the host listens on. The correct syntax for localhost-only would be `"127.0.0.1:18123:8123"`.

Combined with `CLICKHOUSE_USER: default` and no `CLICKHOUSE_PASSWORD` in the same compose file:

```yaml
    environment:
      CLICKHOUSE_HOST: http://clickhouse:8123
      CLICKHOUSE_USER: default
```

The default ClickHouse `default` user has no password (this is the upstream ClickHouse default; Helicone doesn't change it). An operator running the standard Helicone Docker Compose on a public IP with no host-level firewall has ClickHouse on the open internet with `default:no-password` auth.

The `clickhouse:24.3.13.40` image in the compose is newer than the 23.4.2.11 actually deployed at `benchmarkit.solutions`. This operator is running an older Helicone version, not the current docker-compose. The exposure has likely existed since their initial deployment.

## Source-level latent primitive (re-confirmed from Phase 1)

`.env.example`, `valhalla/jawn/.env.example`, `docker/.env.example` all contain:

```bash
BETTER_AUTH_SECRET="MKUcaeqyMD7UBkGeFYY5hwxKS1aB6Vsi"
```

The official `docs/getting-started/self-host/docker.mdx` documents using `openssl rand -base64 32` for production but the Quick Start command omits `BETTER_AUTH_SECRET` (defaults to `change-me-in-production` per the env-table). Both defaults are session-forgery primitives for operators who don't rotate.

We did not probe whether `benchmarkit.solutions` or any other Helicone host runs the default `BETTER_AUTH_SECRET`. The probe shape would be active forgery; out of scope for read-only research-mode.

## Other Helicone Phase 2 IP-shadow findings

Extended 17-port nmap sweep across the 19 Helicone IPs:

| Port | Open hosts | Service | Auth |
|---|--:|---|---|
| 3000 | 4 | Helicone on alt port | proper |
| 8080 | 2 | unknown alt-web | varies |
| **5432** | **2** | **Postgres on `benchmarkit.solutions` + `q7core.com`** | TCP only; password unknown |
| 9090 | 1 | Cockpit (already characterized) | login-required |
| **8123** | **1** | **ClickHouse on `benchmarkit.solutions`** | **NONE — unauth confirmed** |
| 8025 | 1 | MailHog (already characterized) | open but empty |
| 111 | 1 | rpcbind | metadata only |

### Postgres exposure on 2 Helicone operator hosts

- **`137.184.217.47` (benchmarkit.solutions / DigitalOcean US)**: same host as the unauth ClickHouse. Both Postgres AND ClickHouse on the public internet. Whether the Postgres has a default `postgres:postgres` we don't probe.
- **`74.208.17.59` (q7core.com / IONOS US)**: Postgres on port 5432 publicly reachable.

The Helicone Docker Compose binds Postgres port 5432 to host port 54388 (per the .env.example: `DATABASE_URL="postgresql://postgres:testpassword@localhost:54388/helicone_test"`). The `postgres:testpassword` is the documented dev default. Operators running the standard self-host on a public host without firewall rules expose Postgres with these defaults to anyone.

## Comparison to Phoenix and Langfuse

| Platform | Default ports | Default service creds | Outcome at population scale |
|---|---|---|---|
| Phoenix | 6006 web (auth-off-by-default) | n/a (auth off skips all auth) | 25% unauth (94/377) |
| Langfuse | 3000 web (auth required) | `NEXTAUTH_SECRET="secret"` in `.env.prod.example` | 0% unauth on web, 5 hosts expose Postgres |
| **Helicone** | 3000 web (auth required), 18123 ClickHouse (`0.0.0.0` bind, no password) | `BETTER_AUTH_SECRET=` literal + `minioadmin:minioadmin` + ClickHouse `default:no-password` | **1 confirmed unauth ClickHouse with full trace store, 2 hosts with Postgres exposed** |

Phoenix's shipping-defaults problem is **the auth toggle itself**. Helicone's is **the supporting-service port bindings**. Both produce real-world exposure; Helicone's is narrower because there are fewer Helicone self-hosters, but the per-instance impact (full trace-store readability) is comparable to Phoenix's GraphQL leak.

## Cross-version posture

The Phase 1 Shodan hits don't expose Helicone version on a uniform endpoint. The `benchmarkit.solutions` ClickHouse runs 23.4.2.11 (mid-2023). Significantly older than the Helicone docker-compose.yml's pinned `24.3.13.40`. This operator is running a vintage Helicone deployment that hasn't been updated since at least mid-2023.

Older Helicone versions had less strict defaults. The current Helicone `docker.mdx` does call out generating a `BETTER_AUTH_SECRET` for production. Older versions may not have had that documentation.

## What's NOT a finding

- The 4 Langfuse/Helicone-on-port-3000 hosts: all auth-fronted Helicone instances.
- The Cockpit on `62.171.190.103:9090`: login-required; documented in Phase 1 as an operator hardening miss but not a vulnerability.
- The MailHog on `188.34.196.197:8025`: empty store, documented in Phase 1.

## Next steps (research, not disclosure-yet)

1. ~~Phase 2 source-level audit (port bindings, default creds)~~ ✓
2. ~~Extended IP-direct-shadow with database ports~~ ✓
3. ~~Confirm actualized primitive on `benchmarkit.solutions`~~ ✓ ClickHouse unauth at structure level
4. **LangSmith Phase 2**, closed-source, focus on `/api/v1/info` disclosure surface + IP-shadow
5. **Phase 3 meta-fingerprinter**, incorporate the Helicone-docker-compose port-binding signal as a new fingerprint type

## Evidence pack

`~/recon/2026-05-10-llm-sweep/helicone/`
- All Phase 1 artifacts (host list, probe results, basic IP-shadow)
- `helicone-deep-shadow.{nmap,gnmap,xml}`: extended 17-port sweep across 19 IPs

Cross-references:
- [helicone-llm-observability-survey-2026-05-10.md](helicone-llm-observability-survey-2026-05-10.md) (Phase 1)
- [SYNTHESIS-ai-observability-2026-05-10.md](SYNTHESIS-ai-observability-2026-05-10.md)
- [langfuse-deep-dive-survey-2026-05-10.md](langfuse-deep-dive-survey-2026-05-10.md) (same Phase 2 pattern, different exposures)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
- [Methodology Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md): this finding extends the insight: shipping-defaults aren't limited to auth toggles; port-binding defaults in docker-compose have the same population-scale signature
