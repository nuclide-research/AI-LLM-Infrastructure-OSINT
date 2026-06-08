# Insight #89 — Framework-Level Auth Bypass Propagates to Population Scale

_NuClide Research · 2026-06-08 · Origin: VictoriaMetrics survey + upstream issue #3060._

---

## Statement

When an auth mechanism does NOT cover a high-value endpoint at the framework level, every operator who configures auth still leaks that endpoint. The leak is unfixable at the deployment layer; it requires a framework patch. Population-scale evidence: VictoriaMetrics `-httpAuth.username/password` flags do not gate `/debug/pprof/`, and 91% of internet-exposed VM hosts (1,077 of 1,176) leave pprof open as a result — including hosts where the operator clearly DID configure auth on data endpoints.

## Derivation

Across the 1,176-host VictoriaMetrics corpus (numbers below reflect the post-publication DCWF 672 T&E audit correction):

- Originally 65 hosts labeled AUTH-ON; the DCWF 672 audit reclassified **10 of those as PARTIAL-AUTH-PPROF** (401 on data endpoints, 200 on both `/metrics` AND `/debug/pprof/`).
- **Fully gated population: 55 of 1,176 = 4.7%** (not 5.5% as originally published).
- The 10 partial-auth hosts are the strongest empirical evidence for this Insight: operators who explicitly configured `-httpAuth.username/password` STILL leak pprof. The framework's auth model is the only common factor.
- Across the full corpus, `/debug/pprof/` open rate: **1,077 / 1,176 = 91.5%** — unchanged after audit.

The upstream evidence is in `VictoriaMetrics/VictoriaMetrics` issue #3060 ("HTTP_AUTH doesn't work everywhere"), filed in 2022. The framework chose to leave `/debug/pprof/` outside the auth-middleware path. The choice has not been reversed in three years. Population data shows the choice is now load-bearing at scale.

## Why this is structural, not operator-side

Operator-side defaults can be fixed by operators. The Chroma auth-off-default is fixable per-deployment: set `CHROMA_SERVER_AUTH_CREDENTIALS_FILE` and the host stops leaking. Operators who don't set it, leak.

A framework-level bypass is different. The operator CANNOT fix it by configuration. They have to:
- Run a reverse proxy (vmauth) that gates pprof externally
- Restrict pprof at the network layer (firewall rule on `/debug/pprof*` paths)
- Patch the framework binary

None of those scale with operator hygiene. Configuration tutorials say "set `-httpAuth.username/password`" and operators do. Then pprof leaks anyway. The framework's auth model has a known gap and operators are not informed in-band.

## What pprof leaks

`/debug/pprof/` is Go's runtime profiling endpoint. With it accessible, anyone can:

- Pull goroutine stacks (`/debug/pprof/goroutine?debug=2`) which often contain in-flight HTTP request URLs, internal hostnames in DNS-lookup stacks, JWT-fragment-shaped strings if the runtime is mid-validation, etc.
- Pull CPU profiles (`/debug/pprof/profile`) which can leak request-routing internals and inferred QPS
- Pull heap profiles (`/debug/pprof/heap`) which leak object sizes / structures and indirectly cache contents
- Pull command-line args via `/debug/pprof/cmdline` — sometimes including auth flags as plain-text process arguments

For a binary with the framework-level auth model VictoriaMetrics has, pprof is the **out-of-band leak channel** that compromises in-band auth.

## Cross-platform check

This pattern applies to any Go framework that integrates `net/http/pprof` via `_ "net/http/pprof"` import (which auto-registers handlers on `http.DefaultServeMux`). When the application's auth middleware is registered on its own mux (not DefaultServeMux), pprof inherits a separate, unauthenticated routing tree.

Other potentially-affected populations:
- Kubernetes components (kube-apiserver pprof: gated by RBAC if configured, often is)
- etcd (etcd pprof: gated by client-cert auth, usually is)
- Consul (gated by ACL token)
- Prometheus (gated by `--web.enable-admin-api` separately, but pprof shares the surface)
- Nomad, Vault, Boulder, etc.

The category-wide research question: **for each major Go infrastructure service with a configurable auth model, does `/debug/pprof/` inherit auth or escape it?**

## Operator-action implication

The 91.5% pprof-open rate means the population-level remediation for unauth read on VictoriaMetrics is NOT "set `-httpAuth`". The remediation is:

1. Deploy `vmauth` reverse proxy as the only public entrypoint
2. Configure vmauth to deny `/debug/pprof/*` for unauth requests
3. Restrict network reachability of the raw vmsingle/vmagent port to known clients

A framework-level patch would be a strict subset of this surgery, applied once upstream.

## Research-program implication

This is the first Insight in the program that escalates a finding from operator-error to framework-error. Most NuClide findings live at the operator-deployment tier. This one is structural. It changes who the disclosure target is: not the operator (they cannot fix it), but the framework maintainer.

## Tooling

Single endpoint check per host: GET `/debug/pprof/`, classify 200-with-pprof-string as open. Trivial to add to any verifier. Worth adding to aimap as a per-Go-service post-finding check.
