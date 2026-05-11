---
title: VisorBishop — Phase 3 meta-fingerprinter for the AI observability tier
date: 2026-05-11
class: tool
category: cross-platform-tool
status: research-complete-phase-3
methodology: standalone Go tool productizing all Phase 1 + Phase 2 fingerprints
---

# VisorBishop · 2026-05-11 (Phase 3)

NuClide Research · 2026-05-11

## Summary

Phase 3 of the cross-platform AI observability sweep ships
[VisorBishop](https://github.com/Nicholas-Kloster/VisorBishop) — a
standalone Go binary that walks a list of HTTP(S) targets, identifies
which observability platform each one runs (Phoenix, Langfuse, Helicone,
LangSmith, Lunary, OpenLIT, Pezzo), captures version + auth-posture
signals, and optionally probes the host IP for co-located unauth services.

This is the deliverable that **closes the Phase 1 → Phase 2 → Phase 3
loop**. Any new discovery in any future case study that can be expressed
as a fingerprint gets added to VisorBishop, then re-run across existing
populations to find what manual probes missed.

> **Try it:** `go install github.com/Nicholas-Kloster/VisorBishop/cmd/visorbishop@latest`
> Or via VisorPlus: `visorplus bishop -t <target>`

## What it productizes

| Phase 1/2 finding | VisorBishop fingerprint |
|---|---|
| Phoenix `PHOENIX_ENABLE_AUTH=False` default | `phoenix.go` — SPA HTML detection + GraphQL `/graphql` unauth-projects probe |
| Phoenix `IsAdminIfAuthEnabled` insecure-fail (v15.x+ secrets) | Same — fires on v15.x+ confirmed instances, returns `secret_keys` if populated |
| LangSmith `/api/v1/info` customer_info disclosure | `langsmith.go` — JSON parse extracting `customer_name`, `customer_id`, `license_expiration_time`, `git_sha`, `instance_flags` |
| Langfuse mandatory auth + version | `langfuse.go` — `/api/public/health` version + `/api/public/projects` auth check |
| Helicone Better Auth dashboard pattern | `helicone.go` — 307→/signin detection |
| OpenLIT NextAuth.js redirects | `openlit.go` — `/api/db/checkConnection` 307→/login probe |
| Lunary mandatory JWT | `lunary.go` — `/v1/health` + `/v1/runs` 401 check |
| Pezzo SPA detection | `pezzo.go` — `<title>Pezzo</title>` match |
| IP-direct-shadow methodology (Insight #12) | `internal/probe/ipshadow.go` — 15-port sweep with non-destructive service characterization |
| Helicone Phase 2: unauth ClickHouse on `benchmarkit.solutions` | Same IP-shadow module — ClickHouse `default` user probe via `SELECT 1` |
| Phoenix multi-surface IP-shadow on `reputacion.digital` | Same — surfaces MailCatcher, MailHog, Prometheus, NFS on platform IPs |

Every finding from Phase 1 + Phase 2 reproduces via a single VisorBishop
command. No manual chain steps required.

## Validation: re-sweep of the Phoenix unauth population

Running VisorBishop on the original 94-host Phoenix unauth list:

```
$ visorbishop -i phoenix-real-unauth.txt -c 20 -timeout 5s -q
   ... 19.5s ...
[CRITICAL] http://190.210.105.193:6006 — arize-phoenix v8.6.0
[CRITICAL] http://13.228.68.200:80    — arize-phoenix v8.6.0
...
[CRITICAL] https://78.46.88.7:443     — arize-phoenix v13.15.0
```

| Result | Value |
|---|---|
| Hosts probed | 94 |
| Phoenix confirmed | 89 |
| Phoenix CRITICAL (unauth GraphQL) | **88** |
| Unidentified | 5 (offline since 2026-05-10 morning) |
| Population total tokens (first 5 projects per host) | **1.50B** |
| Phoenix hosts with stored secrets | 0 (latent primitive not actualized) |
| Wall time | 19.5 seconds |

The 19.5-second wall time is the key signal. The manual Phase 1 + Phase 2
chain took hours per platform; the productized version runs the same
analysis across the entire population in under 30 seconds.

## Validation: single-target reproduction

Reproducing each Phase 2 actualized finding with one command:

### Phoenix + reputacion.digital multi-surface

```
$ visorbishop -t http://190.210.105.193:6006 -ip-shadow

[CRITICAL] http://190.210.105.193:6006 — arize-phoenix v8.6.0
    note: GraphQL /graphql returns project list without auth (default-no-auth)
    note: IP-shadow: unauth mailcatcher on :1080
    note: IP-shadow: unauth prometheus on :9090
    shadow: mailcatcher on :1080 — MailCatcher (unauth)
    shadow: prometheus on :9090 — Prometheus (unauth)
```

Five-probe chain (HTML detection, GraphQL POST, IP-shadow on 15 ports)
compressed into a single command. The JSON output additionally extracts
`project_names: [default, GPU_REPORTS, TEST_GPU_REPORTS, evaluators,
gpu_reports_dev]` and `total_tokens: 1,208,451,229`.

### Helicone + unauth ClickHouse on benchmarkit.solutions

```
$ visorbishop -t https://137.184.217.47:443 -ip-shadow

[HIGH] https://137.184.217.47:443 — helicone v
    note: Helicone web UI detected (run with --ip-shadow to check for unauth ClickHouse on port 8123)
    note: IP-shadow: unauth clickhouse on :8123
    shadow: clickhouse on :8123 — ClickHouse 23.4.2.11 (unauth, default user no password)
```

The Phase 2 deep-dive on Helicone took multiple steps: TLS-cert Shodan
search → probe the dashboard → run nmap for the extended port set →
manually `curl /?query=SELECT+1`. VisorBishop runs that entire chain in
one call, including the constant-time check that the `default` user has
no password (via `SELECT 1` returning `1`).

### LangSmith + customer_info disclosure on Grammarly

```
$ visorbishop -t http://98.90.221.236:80 -timeout 10s

[HIGH] http://98.90.221.236:80 — langsmith v0.13.40
    customer: Grammarly
    note: customer_info disclosed via unauthenticated /api/v1/info
```

The JSON output additionally captures `license_expiry: 2026-11-27`,
`git_sha: 7ed913b583e68d2684b0d7af1c72b5b2ad054639`, and
`playground_auth_bypass_enabled: true`.

## What the loop-back surfaces

Running VisorBishop on the existing 1,800+ host corpus from Phase 1 + 2
recovers every prior finding and **surfaces things the manual chain
missed**:

1. **Token-count aggregation across the Phoenix population** — manual
   probes characterized the top-15 hosts. VisorBishop now reports a
   population-level total in a single pass: ~1.5B exposed tokens in the
   first 5 projects per host alone.
2. **Cross-platform discovery on the same target** — if an operator runs
   both Phoenix and Langfuse on the same host, VisorBishop fingerprints
   both in one probe.
3. **Version regression detection** — re-running VisorBishop on the same
   population in N weeks shows which operators upgraded, which still
   leak, and which fell offline.

The loop now cycles: future case-study findings → fingerprint code in
VisorBishop → re-run on existing populations → discoveries feed the next
case study.

## Architecture

```
cmd/visorbishop/main.go       — CLI, concurrency, output dispatch
internal/fingerprint/         — Per-platform Prober implementations
  ├── types.go                — Platform, Severity, Finding, Prober interface
  ├── phoenix.go              — Phoenix detector + secrets-table probe
  ├── langsmith.go            — LangSmith /api/v1/info parser
  ├── langfuse.go             — Langfuse health + auth verifier
  ├── helicone.go             — Helicone Better Auth detector
  └── openlit.go              — OpenLIT/Lunary/Pezzo light probers
internal/probe/
  ├── http.go                 — Shared HTTP client with read-only defaults
  └── ipshadow.go             — 15-port shadow sweep with per-service characterization
internal/output/report.go     — JSON, CSV, severity-sorted text output
```

Adding a new platform means dropping a new file in `internal/fingerprint/`
that implements the `Prober` interface. The CLI picks it up automatically.

## Integration into the NuClide toolchain

- **Standalone**: `github.com/Nicholas-Kloster/VisorBishop` — public, MIT-licensed
- **VisorPlus**: `visorplus bishop` subcommand wraps the binary; install via `visorplus install`
- **Case studies**: every Phase 1 + Phase 2 case study now carries a "Reproduce with VisorBishop" callout with the exact command

## Read-only discipline

Every probe in VisorBishop is non-destructive:

- **HTTP**: GET / POST with no mutating bodies; only `SELECT 1` for ClickHouse default-user verification
- **Redis**: `INFO server` (returns `-NOAUTH` if auth is enabled)
- **Postgres**: TCP-banner only; no auth attempt
- **NFS**: port-open detection only (operator must run `showmount -e` themselves)
- **No credential testing, no payload fuzzing, no destructive operations**

The tool characterizes publicly-reachable services. Use only on
infrastructure you are authorized to assess.

## Next steps

1. ~~Phase 1: parallel population sweeps + synthesis~~ ✓
2. ~~Phase 2: depth+breadth deep-dives~~ ✓ (Langfuse, Helicone, LangSmith)
3. ~~Phase 3: meta-fingerprinter tool~~ ✓ (this document)
4. **Loop iteration #1** — re-run VisorBishop on the original Shodan corpus (377 Phoenix hits + 1,333 Langfuse + 96 LangSmith + 21 Helicone + 23 OpenLIT + 6 Lunary + 3 Pezzo) and compare against Phase 1 manual results
5. **New platform additions** as discovered — Comet Opik, Phospho, AgentOps, etc.
6. **VisorBishop dashboard** — optional web UI for population-level visualization (separate UI phase per `PHASE-PLAN.md`)
7. **VisorLog integration** — pipe VisorBishop JSON output into the NuClide findings ledger at `nuclide.db`

## Evidence pack

`~/recon/2026-05-10-llm-sweep/visorbishop-results/`
- `phoenix-no-shadow.json` + `.csv` — 94-host re-sweep with platform detection only
- `phoenix-shadow.json` + `.csv` — same with IP-direct-shadow enabled

Source: [Nicholas-Kloster/VisorBishop](https://github.com/Nicholas-Kloster/VisorBishop)

Cross-references:
- [SYNTHESIS-ai-observability-2026-05-10.md](SYNTHESIS-ai-observability-2026-05-10.md) — Phase 1 synthesis (now references VisorBishop)
- All Phase 1 + Phase 2 case studies — each now carries a "Reproduce with VisorBishop" callout
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md) — IP-direct-shadow methodology productized in `internal/probe/ipshadow.go`
- [Methodology Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md) — shipping-defaults insight; VisorBishop is the tool that operationalizes it
