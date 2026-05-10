---
title: "Hostname-routed SSO doesn't protect the IP-direct shadow"
insight_number: 12
date: 2026-05-10
tags:
  - methodology
  - sso-misconfiguration
  - reverse-proxy-bypass
  - kubernetes
  - prometheus
  - phoenix
  - mailhog
  - kibana
  - nfs
related_research:
  - case-studies/commercial/AR-reputacion-digital-multi-surface-2026-05-10.md
  - case-studies/commercial/phoenix-llm-observability-survey-2026-05-10.md
source: case-studies/commercial/phoenix-llm-observability-survey-2026-05-10.md
---

# Methodology Insight #12: Hostname-routed SSO doesn't protect the IP-direct shadow

## Statement

When an operator deploys SSO at the application layer (authentik, OAuth proxy, Keycloak, oauth2-proxy, Traefik forward-auth, etc.) and binds it via the reverse proxy's hostname routing, every service that listens on the underlying host's IP — at any port — answers requests by IP and bypasses the SSO front-end. The operator's mental model of "everything is auth-fronted" is wrong by exactly the count of services that don't have their own auth in addition to the reverse-proxy auth.

The class signal at population scale: **of 92 internet-exposed unauth Phoenix hosts surveyed in the 2026-05-10 sweep, 25 (27%) had at least one secondary attack surface exposed on the same IP that was not protected by the operator's SSO front-end.** Five of those secondary surfaces had real, exploitable primitives:

| Host | Phoenix project | Secondary surface | Severity |
|---|---|---|---|
| 190.210.105.193 (reputacion.digital) | GPU_REPORTS, 1.21B tokens | NFS exports incl. /postgres + Prometheus + MailCatcher | CRITICAL |
| 173.208.247.17 (wiratek.id, PLN Indonesia) | stt-dr-assistant | Prometheus on GPU compute (dcgm-exporter) | HIGH |
| 173.214.172.254 (dsb-kairo.de, German School Cairo) | Phoenix unauth | Prometheus scraping FastAPI backend | HIGH |
| 47.251.246.12 (Alibaba Cloud US, "deepagents") | deepagents-monitor-verify | Kibana 7.17.20 fully unauthenticated | HIGH |
| 51.15.207.110 (Teetsh, French edu SaaS) | default (empty) | MailHog with 139 captured emails | HIGH |

## How the failure mode arises

The reverse-proxy-only SSO pattern is structurally the same across implementations:

1. Operator runs services in containers / pods, each bound to a high port on the host (`:6006`, `:9090`, `:8025`, `:2049`, etc.)
2. Operator deploys a reverse proxy (Traefik, nginx, Caddy, oauth2-proxy outpost) listening on `:443`
3. Operator configures the reverse proxy to require SSO before forwarding to any backend
4. Operator binds public DNS records: `phoenix.example.com → reverse-proxy:443`, `grafana.example.com → reverse-proxy:443`, etc.
5. **Operator forgets to firewall the underlying high ports off the public internet**

Result: requests to `https://phoenix.example.com/` hit the reverse proxy and get bounced to SSO. Requests to `http://<host-IP>:6006/` hit Phoenix directly, no auth in the path. Same backing service, two routes, only one of them auth-fronted.

The mental model gap is the load-bearing piece. Operators who deploy SSO at the application layer typically believe "all my services are behind SSO." They're correct *for traffic that arrives via the configured hostnames*. They're wrong for any other route to the same backend.

## Why operators get this wrong consistently

Three reinforcing factors:

- **Default service binding is `0.0.0.0`, not `127.0.0.1`.** Most container images and pip/cargo/npm-installed services default to listening on all interfaces. The operator would have to explicitly opt into loopback-only binding (or a private CNI interface) to avoid the public surface.
- **Cloud-provider firewalls are off by default for most ports.** AWS Security Groups, GCP firewalls, DigitalOcean droplet firewalls — all start permissive. Restricting requires explicit action.
- **Testing path is hostname-routed.** When the operator opens their browser and goes to `https://phoenix.example.com/`, they get the SSO login. Confirms the auth works. They never test `http://<host-IP>:6006/` directly because that's not the path they use.

## Detection methodology (for surveys)

Given a population of unauth-on-port-X hosts (e.g., 94 unauth Phoenix instances), the IP-direct-shadow check adds two passes:

1. **Phase 1 — TCP SYN sweep on high-signal ports.** Run nmap against the IPs on a curated list of "things operators commonly expose by accident":
   - `2049` — NFS
   - `111` — rpcbind / portmapper (announces NFS)
   - `1080` — MailCatcher / SOCKS proxy
   - `8025` — MailHog
   - `9090` — Prometheus
   - `9093` — AlertManager
   - `9100` — node_exporter
   - `5601` — Kibana
   - `9200` — Elasticsearch
   - `3000` — Grafana (default, also collides with many Next.js dev servers — verify)

2. **Phase 2 — per-port auth-posture probe.** For each open port, fingerprint the actual service (port number alone is unreliable — port 9090 also gets used by random Python web apps) and test whether the API is auth-fronted:
   - Prometheus: `GET /api/v1/query?query=up` should return `{"status":"success",...}` if unauth
   - Grafana: `GET /api/datasources` should return 401 if auth-protected, 200+JSON if not
   - Kibana: `GET /api/spaces/space` should return 401 if auth-protected, 200+JSON if not
   - MailHog: `GET /api/v2/messages?limit=0` should return `{"total": N, ...}` always (no auth in MailHog by design)
   - NFS: `showmount -e <ip>` returns export list if open, error otherwise

3. **Phase 3 — same-host correlation.** A single host with Phoenix unauth + Prometheus unauth + NFS open is a multiplicatively-worse exposure than any of those alone. Prioritize hosts where ≥3 secondary surfaces stack.

## Implications for cross-survey methodology

The IP-direct-shadow check should be added to the standard 9-step OSINT chain as a phase between operator attribution (step 7) and span sampling (step 8). It surfaces:

- **New operators not visible in the primary survey** (the Teetsh + Brutus + Wiratek + dsb-kairo finds in the Phoenix sweep were all picked up via shadow ports, not Phoenix project names)
- **Multi-product operator attribution** (the same Scaleway French IPs running Phoenix + MailHog + Brutus legal-assistant + Teetsh educational tools all tied to one operator — the shadow ports were the disambiguator)
- **Severity multipliers** (a single host with a stacked exposure has a much sharper threat model than a host with one exposed service)

It also adds **fewer false positives than naive port scanning** because the seed population (Phoenix unauth hosts) is already known to have at least one default-no-auth service. Operators who fail at Phoenix tend to fail at other co-located services in the same cluster, and the population-level signal of "27% have another exposed surface" is significant.

## Implications for operator-side defense

Three layered fixes the operator can apply:

1. **Bind services to loopback or private interfaces only.** Configure each containerized service to listen on `127.0.0.1:6006` instead of `0.0.0.0:6006`, or use a private CNI bridge. Then traffic only reaches the service through the reverse proxy.
2. **Firewall the high ports.** Explicit cloud-provider firewall rules dropping inbound traffic to `:6006`, `:9090`, `:2049`, etc. — only allow `:443` and `:80` from the public internet.
3. **Add a second auth layer per service where the service supports it.** Phoenix, Grafana, Prometheus all support native auth. Don't rely solely on the reverse-proxy SSO; defense in depth.

The first option is the cheapest and most robust. The second is what most operators reach for first because it doesn't require touching any service config. The third is the rigorous defense-in-depth path.

## Related primitives

- **Insight #02** (single-template auth-off propagates): the reason these stacks share the auth-off pattern across many ports is because the operator's deployment template ships them all that way.
- **Insight #08** (auth bypass via misconfiguration redirects): different mechanism, same outcome — auth checks that don't fire.
- **Insight #10** (vendor-template default-no-auth): the upstream cause of the secondary surfaces being unauth in the first place.
