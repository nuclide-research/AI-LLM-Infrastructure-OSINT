# Network Perimeter / Service Mesh — Pre-Assessment OSINT

_Generated: 2026-05-31 from Stage −1 agentic OSINT pass (4 platforms, 4 parallel lanes, all WebSearch+WebFetch live-verified)._
_Category: Network Perimeter / Service Mesh. Cold category — no prior intel doc, no query file, ~0 meaningful ledger hits._
_Companion query catalog: `shodan/queries/service-mesh-queries.md`._

---

## Category thesis

Service meshes and identity-aware proxies are **introspection-rich by design**. Every platform here ships a control plane and/or an observability plane whose explicit job is to describe the cluster's internal traffic: who talks to whom, on which ports, with which identities, carrying which L7 metadata. When that plane is reachable, the finding is not "one unauthenticated service" — it is **cluster-wide reconnaissance delivered as an API**: the full internal service graph, pod IPs, SPIFFE/mesh identities, mTLS cert material, routing tables, and (where L7 policy is applied) live HTTP/DNS/Kafka metadata.

**Auth-on-default mapping.** The category mostly *confirms* the thesis by a specific mechanism: these planes are **no-auth-by-default and rely on network placement, not authentication** ("don't expose it" — loopback bind, ClusterIP-only, NetworkPolicy) as the entire control. That is a defense that fails the moment a NodePort / LoadBalancer / hostPort / container-escape changes the network position. Linkerd's viz dashboard, Cilium's Hubble Relay, and Istio's istiod debug all ship with zero authentication and a documentation note that says "do not expose." Pomerium is the deliberate inverse (below).

**The Pomerium inversion (candidate Insight).** For Istio/Linkerd/Cilium, "exposed" means the introspection plane is reachable. For Pomerium — an identity-aware *proxy*, i.e. the auth layer itself — presence is trivial to fingerprint (public JWKS) but the *finding* is behavioral: a route configured `allow_public_unauthenticated_access: true` (renamed `public_access` in ≥v0.23) turns the zero-trust gateway into an **open relay to whatever internal service it fronts**. There is no static signal distinguishing a correctly-protected Pomerium from an open-relay Pomerium; only behavioral per-route probing (does the route serve upstream content without an OIDC redirect?) reveals it. This is Insight #10 (effective-unauth beyond literal no-auth) applied to an auth product's own misconfiguration.

**Censys leverage: HIGH (confirmed).** Every high-value surface here lives on a high/odd port Shodan undersamples: Envoy admin 15000, istiod 15010/15014, Linkerd proxy-admin 4191 / viz 8084-8085, Hubble Relay 4245, Cilium metrics 9962/9963/9965, Kiali 20001. This is the LightRAG `port + software.product` pattern's natural habitat. Censys full-range port coverage + the data-tier/auth-state decoders are the right discovery primitive; Shodan brand-dorks will undercount.

---

## aimap TOOL GAP — gRPC surface is unmeasured (honest negative space)

The single highest-value surface in the category is **gRPC-only and plaintext**: Cilium Hubble Relay on 4245 (`observer.Observer` service; `GetFlows` = cluster-wide live flow tap, no auth on the default insecure listener). Istio xDS (15010/15012) and Pomerium inter-service (5443) are also gRPC. **aimap's probe model is HTTP-only** — a GET to 4245 returns gRPC framing aimap cannot parse. aimap therefore *cannot currently fingerprint the most security-relevant surface in this category.*

- **Decision point for Nick (see end).** Either (a) add a gRPC-reflection probe type to aimap before the sweep, or (b) run HTTP-only this pass and cover the gRPC tier with `grpcurl` (present in loadout) as a documented manual lane, logging Hubble-Relay 4245 as honest negative space until aimap is extended.
- Proposed aimap capability: `Type: "grpc_service_list"` (reflection → match service name e.g. `observer.Observer`) and `Type: "grpc_call"` (invoke `observer.Observer/ServerStatus`, match JSON fields `num_flows`/`version`). Definitive zero-FP identification + unauth confirmation in one call.

No nuclei templates exist for Cilium/Hubble. Istio/Envoy and Linkerd/Pomerium templates exist but are partial/narrow (see per-platform notes).

---

## Per-platform intel

### Istio / Envoy

**Auth posture.** Envoy sidecar admin (15000) binds loopback in-pod, no auth — reachable from any co-tenant container or an exposed nodePort. mTLS defaults to **PERMISSIVE** (accepts plaintext) until STRICT is set. istiod debug (15014) + plaintext xDS (15010) were structurally **unauthenticated pre-1.30**; `ENABLE_DEBUG_ENDPOINT_AUTH=true` is the default only from **1.30.0**. Kiali (20001) defaults to `token` now but `anonymous` strategy (full cluster-wide read via Kiali SA) was the common sample-install default pre-~1.7.

**Highest-density unauth leak.** `GET :15000/config_dump` — full mesh topology + all TLS cert material this proxy holds + routing + filter chains. `/certs` yields every mTLS peer's SPIFFE identity. `POST /quitquitquit` = sidecar DoS.

**istiod debug (15014, pre-1.30).** `/debug/registryz` `/debug/configz` `/debug/endpointz` = full service registry, all pod IPs/SAs/namespaces — a read-only projection of everything istiod's ClusterRole can see (get/list/watch pods, services, endpoints, secrets).

**Key CVEs.** CVE-2026-31838 (cross-namespace debug, 15010/15014 missing namespace auth; fixed 1.27.8/1.28.5/1.29.1) — confirms pre-1.30 debug was unauth. CVE-2026-31837 (JWKS fallback → JWT forgery, CVSS 8.7). CVE-2022-39388 (localhost→full-mesh identity impersonation, <1.15.3). Auth-policy-bypass is a recurring class (CVE-2024-23324, -26308, -2026-39350). No KEV entries.

**TLS attribution.** Workload URI SAN `spiffe://<trust-domain>/ns/<ns>/sa/<sa>` (default trust domain `cluster.local`); operator-customized trust domains attribute directly. istiod serving cert CN `istiod.istio-system.svc`.

---

### Linkerd

**Auth posture.** Proxy admin (4191) binds **0.0.0.0**, no auth, no TLS — `/metrics`, `/env.json`, `/shutdown`, `/proxy-log-level`. Only control is opt-in NetworkPolicy. linkerd-viz dashboard (8084) has **no auth layer by design** (docs say protect externally); the only built-in guard is a Host-header regexp (DNS-rebind fix, ~2020) which `enforcedHostRegexp: .*` disables. The `linkerd-web`→`linkerd-viz` repackaging did **not** add auth — zero-auth dashboard remains the 2026 default.

**Highest-density unauth leaks.** `/env.json` on 4191 (proxy env vars — credential exposure if secrets are env-injected; reachable cross-cluster on multicluster gateway pods per issue #9145). `/metrics` on 4191 (full workload graph via `dst_*` labels, cert-expiry timing, version). **tap** (8088/8089, RBAC-gated) streams live request *headers* cross-pod — Authorization/cookie/JWT material — explicitly excludes bodies (discussion #8353), but headers are the crown jewel; an over-privileged tap-admin binding = cluster-wide passive wiretap.

**Key CVEs.** CVE-2024-40632 (no-auth `/shutdown` → SSRF-chained sidecar DoS, low). CVE-2025-43915 (proxy metrics resource exhaustion, 6.5). DNS-rebind dashboard issue (P0, no CVE, fixed ~2020). 2024 7ASecurity/OSTIF audit found no RCE/auth-bypass. No KEV.

**TLS attribution.** Trust anchor CN `root.linkerd.cluster.local`, identity issuer CN `identity.linkerd.cluster.local` — high-precision, rarely on non-Linkerd clusters. Workload SAN `<pod>.<ns>.serviceaccount.identity.linkerd.cluster.local`.

**nuclei.** `linkerd-panel.yaml` correct (conjunctive title + namespace attr). `linkerd-ssrf*.yaml` target Linkerd **1.x** l5d-dtab routing — do **not** apply to 2.x (silent miss). No 4191/8085 template.

---

### Cilium / Hubble

**Auth posture.** Hubble per-node server (4244) is mTLS-default-on (Helm 1.16+, cert CN `*.<cluster>.hubble-grpc.cilium.io`). **Hubble Relay (4245) external listener is plaintext gRPC by default** (`insecureServer: true`, `serverTLSConfig: null`) — the aggregation point that sees the *whole cluster's* flows is unauthenticated toward callers unless `hubble.relay.tls.server.enabled=true` is set manually. Hubble UI: no auth, no login (assumes port-forward-only). Metrics (9962/9963/9965) + agent health (9879): no auth.

**Highest-density unauth leak.** `observer.Observer/GetFlows` on 4245 — streaming, cluster-wide: src/dst pod+ns+labels+IP+port, K8s security identities, L7 HTTP (method/path/status/headers), L7 DNS (query names → PII), L7 Kafka topics, policy verdicts (FORWARDED/DROPPED + which rule), node names. **Critical** — passive cluster-wide network tap with app-layer visibility, one `grpcurl` away. `ServerStatus` (node count + version), `GetNamespaces`, `GetNodes` all unauth.

**Key CVEs.** CVE-2025-23047 (Hubble UI insecure-default CORS leaks node/workload metadata cross-origin, 6.5). CVE-2026-41520 (cilium sysdump bundles WireGuard private key, 7.9). CVE-2026-33726 (L7 proxy bypasses NetworkPolicy on EKS/GKE per-endpoint-routing, auto-enabled — 5.4). No KEV. No public ITW research on Relay direct-access — **this category may be genuinely under-researched** (publishability signal).

**TLS attribution.** `*.<cluster-name>.hubble-grpc.cilium.io` — zero-FP, leaks operator cluster name when non-default.

---

### Pomerium (identity-aware proxy)

**Framing.** Pomerium *is* the auth layer; the interesting state is a *misconfigured protector*. Modes: all-in-one (gRPC on loopback 5443 — low surface) vs split (gRPC `grpc_address` must not be internet-exposed — CVE-2022-24797 / CVE-2024-47616 vector).

**Presence fingerprint (trivial, unauth, deterministic).** `GET /.well-known/pomerium/jwks.json` → `{"keys":[{"use":"sig","kty":"EC","alg":"ES256",...}]}`. The `/.well-known/pomerium/` path prefix distinguishes from generic OIDC `/.well-known/jwks.json`. Corroborate with `/.well-known/pomerium` (`authentication_callback_endpoint` field) and `Set-Cookie: _pomerium=`.

**The finding (behavioral, not static).** A route with `allow_public_unauthenticated_access: true` / `public_access: true` fronting an internal service (Grafana, Kibana, JupyterHub, Argo CD, Vault UI, k8s dashboard) = open relay. Detect by behavior: a protected route always 3xx-redirects to `authenticate.<domain>` or returns the Pomerium login JS bundle; a public/misconfigured route returns upstream app content directly. `pass_identity_headers` + an upstream that trusts `X-Pomerium-Jwt-Assertion` without verifying the signature = identity spoof via direct upstream hit.

**Key CVEs.** CVE-2023-33189 (**9.8 critical** — incorrect authorization / policy bypass, no-auth; <0.17.4/0.21.4/0.22.2). CVE-2024-47616 (databroker incomplete JWT validation → session spoof if gRPC port reachable, 6.8). CVE-2022-24797 (pprof/metrics on public iface in split mode <0.17.1). No KEV.

**TLS attribution — strong.** Pomerium hosts carry the operator's **real domain SANs** (it fronts real tooling); `authenticate.<domain>` subdomain confirms the service; `/.well-known/pomerium`'s `authentication_callback_endpoint` reveals the authenticate FQDN directly. Excellent VisorGraph cert-pivot feed.

**nuclei.** `pomerium-detect.yaml` probes `/.pomerium/index.js` for bundle strings — too narrow (only fires post-redirect, misses API routes / customized login). JWKS probe above is the correct anchor.

---

## Proposed aimap fingerprints (none exist today)

All conjunctive + marker-anchored per Insight #6. HTTP-probeable set below; gRPC tier (Hubble Relay, Istio xDS) blocked on the tool gap above.

| Name | Ports | Anchor probe | Key conjuncts |
|------|-------|--------------|---------------|
| Istio-Envoy-Admin | 15000 | `/server_info` | json `state=LIVE` + `node.user_agent_name=envoy` + body `sidecar~` + (`/config_dump` body `.svc.cluster.local` + `envoy.admin.v3`) |
| Istio-istiod-Debug | 15014, 8080 | `/debug/endpointz` | body `"serviceAccount"` + `"namespace"` + `.svc.cluster.local`; `/metrics` `pilot_xds` |
| Kiali | 20001 | `/api/health` | json `status=healthy` + ct `application/json`; `/api/namespaces` json_array + `"name"` (anon→critical, 401→medium) |
| Linkerd-Proxy-Admin | 4191 | `/metrics` | body `proxy_build_info` + `inbound_http_authz_allow_total`; `/env.json` body `LINKERD2_PROXY_` |
| Linkerd-Viz | 8084 | `/namespaces` | body `<title>Linkerd</title>` + `data-controller-namespace="linkerd` + ct text/html |
| Hubble-UI | 12000, 8080, 80 | `/` | body `<title>Hubble UI</title>` + `id="app"`; opt `/api/v1/namespaces` json_array |
| Cilium-Metrics | 9962, 9963, 9965 | `/metrics` | body `cilium_drop_count_total` (9965: `hubble_flows_processed_total`) |
| Cilium-Agent-Health | 9879 | `/healthz` | status 200 + json_field `status` (med FP; pair with 9962) |
| Pomerium | 443, 80 | `/.well-known/pomerium/jwks.json` | json `keys.0.use=sig` + `keys.0.kty=EC`; corroborate `/.well-known/pomerium` `authentication_callback_endpoint` |
| Hubble-Relay (gRPC) | 4245 | `observer.Observer/ServerStatus` | **BLOCKED — needs aimap gRPC capability**; grpcurl manual lane meanwhile |

Per the productize-and-re-run discipline: build these into aimap, then re-run the corpus (every survey runs twice).

## Shadow-sweep port priorities (IP-direct shadow on every confirmed host)

K8s api-server 6443/8443, kubelet 10250/10255, etcd 2379/2380, Prometheus 9090, Grafana 3000 (anon common), Jaeger 16686, kube-state-metrics 8080/8443, node-exporter 9100, CoreDNS 9153. Operators who ship one mesh plane auth-off ship these auth-off too (Insight #12).

## Candidate insights to test this survey

- **The "network-placement-as-auth" failure class** — the category's planes substitute loopback/ClusterIP/NetworkPolicy for authentication; measure what fraction of *exposed* instances therefore have a fully-unauth plane (prediction: very high, because exposure already means placement failed).
- **The Pomerium inversion** — presence is static, the finding is behavioral; an auth product's own misconfig is the effective-unauth state (#10 extension).
- **gRPC as a systematic blind spot** — HTTP-only fingerprinting structurally misses the highest-value surface (Hubble Relay); quantify how much of the category is gRPC-gated.

## Limitations / honest negative space

- Hubble Relay 4245 (highest-value surface) is unmeasurable by aimap until the gRPC gap is closed; `grpcurl` covers it manually but does not scale through the chain.
- Favicon hashes for Kiali / Hubble UI not recovered — add as conjuncts once observed live.
- Linkerd metrics-api `/api/v1/stat` JSON schema (`ok` field) inferred, not live-verified.
- Population sizes unknown until Stage 0 (Censys web-UI + Shodan-Playwright).

---
_Provenance: 4 parallel general-purpose(sonnet) Stage −1 lanes, 2026-05-31. Sources: istio.io security bulletins, envoyproxy docs, linkerd.io docs + GH advisories, cilium.io/hubble docs + GH advisories, pomerium.com docs + GH advisories, NVD, GitHub Security Advisories, projectdiscovery/nuclei-templates._
