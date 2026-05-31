# Network Perimeter / Service Mesh — Query Catalog

_Generated: 2026-05-31 from Stage −1 OSINT pass (4 platforms)._
_See: data/platform-intel/service-mesh-perimeter-osint-2026-05-31.md for full intel._

**Threat model:** These planes describe the cluster's internal traffic by design. A reachable control/observability plane = cluster-wide recon API (service graph, pod IPs, mesh identities, mTLS certs, L7 metadata). Most ship no-auth-by-default and rely on network placement as the only control.

**Source routing.** High/odd ports (15000, 15014, 4191, 4245, 9962-9965, 20001, 8084) are Shodan-undersampled → **Censys-preferred** (full-range coverage). Shodan brand-dorks will undercount this category. Censys discovery search = web UI / Playwright (cencli search 403 on free); cencli view = per-asset verify, 1 credit. Identity-probe column is the aimap/grpcurl verification probe, not a dork.

---

## Istio / Envoy

**Auth default:** Envoy admin (15000) no-auth, loopback-bound (reachable via co-tenant / nodePort). istiod debug (15014/15010) unauth pre-1.30. Kiali `anonymous` strategy = full cluster read.
**Exposure class:** `/config_dump` = full mesh topology + cert material; istiod `/debug/registryz` = full service registry; Kiali anon = cluster-wide read via Kiali SA.

| Label | Query | Source | Rationale | FP Risk |
|-------|-------|--------|-----------|---------|
| envoy-admin | `port:15000 http.html:"config_dump"` | Censys/Shodan | Envoy admin landing page links the admin endpoints | Med |
| istiod-metrics | `port:15014 "pilot_xds"` | Censys | `pilot_xds*` metric prefix is Istio-exclusive | Low |
| kiali-panel | `http.title:"Kiali"` | Shodan | Exact UI title | Low |
| spiffe-san | `ssl:"spiffe://cluster.local"` | Shodan/Censys | Workload URI SAN; custom trust domain attributes operator | Low |
| jaeger-codeploy | `http.title:"Jaeger UI"` | Shodan | Co-deployed trace UI, no-auth default | Low |
| identity-probe | `GET :15000/server_info` → json `state=LIVE` + `node.user_agent_name=envoy` + body `sidecar~` | — | Confirms Istio-managed Envoy vs standalone | — |
| identity-probe | `GET :15014/debug/endpointz` → `"serviceAccount"`+`"namespace"`+`.svc.cluster.local` | — | istiod registry, gated 401 on 1.30+ | — |

## Linkerd

**Auth default:** proxy admin (4191) no-auth on 0.0.0.0; viz dashboard (8084) no auth layer (Host-header guard only).
**Exposure class:** 4191 `/env.json` = proxy env (creds if env-injected); `/metrics` = workload graph; viz = full topology; tap = live cross-pod request headers (auth material).

| Label | Query | Source | Rationale | FP Risk |
|-------|-------|--------|-----------|---------|
| viz-panel | `http.html:"data-controller-namespace=\"linkerd"` | Shodan | Dashboard namespace attr (matches verified nuclei) | Low |
| viz-title | `http.title:"Linkerd"` | Shodan | UI title; pair with namespace attr | Med |
| proxy-admin | `port:4191 "proxy_build_info"` | Censys | Proxy metric, not in generic exporters | Low |
| identity-issuer | `ssl.cert.subject.cn:"identity.linkerd.cluster.local"` | Shodan/Censys | High-precision operator-attribution pivot | Low |
| trust-anchor | `ssl:"root.linkerd.cluster.local"` | Shodan/Censys | Linkerd trust anchor CN | Low |
| identity-probe | `GET :4191/metrics` → `proxy_build_info`+`inbound_http_authz_allow_total`; `GET :4191/env.json` → `LINKERD2_PROXY_` | — | Presence + unauth env confirmation | — |

## Cilium / Hubble

**Auth default:** Hubble Relay (4245) external listener plaintext gRPC, no auth by default. Hubble UI no auth. Metrics/health no auth.
**Exposure class:** `GetFlows` on 4245 = cluster-wide live flow tap (pods, identities, L7 HTTP/DNS/Kafka, policy verdicts). The category's crown jewel.

| Label | Query | Source | Rationale | FP Risk |
|-------|-------|--------|-----------|---------|
| hubble-ui | `http.title:"Hubble UI"` | Shodan | Unique product title | V.Low |
| hubble-metrics | `port:9965 "hubble_flows_processed_total"` | Censys | Zero-FP Hubble metric | V.Low |
| cilium-metrics | `"cilium_drop_count_total"` | Censys | Cilium-exclusive metric namespace | V.Low |
| operator-metrics | `port:9963 "cilium_operator"` | Censys | Operator metrics, default-on all-iface | Low |
| hubble-grpc-san | `ssl:"hubble-grpc.cilium.io"` | Shodan/Censys | Relay/server cert SAN; leaks cluster name | V.Low |
| relay-grpc | `port:4245` (full-range) → grpcurl reflect | Censys/masscan | gRPC, Shodan-dark; aimap gap, grpcurl manual | — |
| identity-probe | `grpcurl -plaintext :4245 list` → `observer.Observer`; `observer.Observer/ServerStatus` → `num_flows`,`version` | — | Identity + unauth confirmation in one call | — |

## Pomerium

**Auth default:** Pomerium IS the auth layer. Presence trivial; finding is behavioral (public route → open relay).
**Exposure class:** misconfigured route fronting internal tooling (Grafana/Kibana/Jupyter/Argo CD/Vault UI); pprof/metrics on public iface (split mode, <0.17.1); databroker JWT (<0.27.1).

| Label | Query | Source | Rationale | FP Risk |
|-------|-------|--------|-----------|---------|
| pomerium-cookie | `http.headers.set_cookie:"_pomerium"` | Shodan | Distinctive session cookie name | Low |
| pomerium-html | `http.html:"pomerium"` | Shodan | Catches login/error pages — also docs | Med |
| authenticate-san | `ssl.cert.subject.an:"authenticate."` | Censys/Shodan | authenticate.<domain> subdomain; real operator SANs | Med |
| identity-probe | `GET /.well-known/pomerium/jwks.json` → json `keys.0.use=sig`+`kty=EC` | — | Deterministic unauth presence (NOT generic /.well-known/jwks.json) | — |
| misconfig-probe | route `/` returns 200 upstream content, no OIDC redirect to authenticate.<domain>, no `pomerium.com` in body | — | Behavioral open-relay state; **not a finding until manually verified** | — |

---

## FP traps documented (do not re-run blind)

- `http.html:"pomerium"` and `http.title:"Linkerd"` are single-token — pair with a second conjunct (cookie / namespace attr) per Insight #7.
- nuclei `linkerd-ssrf*.yaml` target Linkerd **1.x** l5d-dtab — silent-miss on 2.x; do not treat a null as "not vulnerable".
- `ssl:"spiffe://cluster.local"` / `*.default.hubble-grpc.cilium.io` with default names are noisy across many clusters; the *custom* trust-domain / cluster-name variants are the attribution-grade signals.
- 200 on Envoy admin / Hubble UI / Linkerd viz = identity, not auth-state (Insight #16) — confirm with the data-layer identity-probe before counting unauth.
