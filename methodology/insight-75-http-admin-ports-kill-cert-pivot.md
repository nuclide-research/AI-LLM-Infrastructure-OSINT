# Insight #75 — HTTP-only admin ports are a dead-end for cert-pivot; attribution requires secondary port pivot

_Sourced to: Cat-32 AI Gateways survey, VisorGraph Stage 3, 2026-06-01._

## The lesson

Cert-pivot (VisorGraph / crt.sh) only works on HTTPS endpoints -- there is no
TLS handshake to intercept and no certificate to extract from a plaintext HTTP
port. AI gateway admin APIs run HTTP-only by design:

- Kong Admin API: `:8001` HTTP, `:8444` HTTPS (rarely deployed with TLS)
- Envoy Admin: `:9901` HTTP only (TLS on admin explicitly not recommended in docs)
- Bifrost: `:8080` HTTP
- one-api / new-api: `:3000` HTTP

A VisorGraph passive run seeded with 187 of these admin-port IPs produced **0
graph nodes and 0 edges** because the passive cert probes (TLS ClientHello,
crt.sh lookup) found nothing to pivot from. The tool worked correctly; the seed
set was structurally incompatible with cert-pivot.

**The fix:** pivot to HTTPS ports on the same IP before running cert-pivot. In the
Cat-32 survey, the `api.host()` dossier for three attributed hosts revealed that
each IP ran additional HTTPS services alongside the HTTP admin port:

| IP | Admin port (HTTP) | HTTPS pivot port | TLS cert finding |
|---|---|---|---|
| 203.154.187.226 (NIEMS TH) | Kong :8001 | :443 Kong proxy | Default self-signed (CN=localhost, O=Kong -- never rotated) |
| 128.211.143.207 (Purdue) | Envoy :9901 | :6443 k3s API | CN=k3s; SANs: cms-h006.rcac.purdue.edu, kubernetes, 10.43.0.1 |
| 193.233.134.97 (WAIcore) | Envoy :9901 | :443 Envoy proxy | CN=khotlenko.ru (operator domain, full attribution) |

The HTTPS port on the same IP carries the operator's actual TLS identity. This
is where cert-pivot produces results.

## Why it generalizes

This gap applies to any survey category where the primary dork surfaces an admin
or management interface on an HTTP port:

- Kubernetes API server dorks (:8080 insecure-port, before it was deprecated)
- etcd client port (:2379, HTTP)
- Consul HTTP API (:8500)
- Nomad HTTP API (:4646)
- Prometheus (:9090)
- Any admin panel exposed on a non-TLS port

In all these cases, a cert-pivot run seeded only with the admin-port IP will
produce 0 nodes. The session records "VisorGraph: 0 findings" -- which looks
like "no relationship chains found" when the real meaning is "wrong port class
for cert-pivot."

## How to apply

1. **Before seeding VisorGraph with admin-port IPs, resolve the HTTPS ports on
   those IPs first.** Use `shodan.host()` or a secondary Shodan search filtered
   to `ip:<x> port:443` to find the co-located HTTPS service. Seed VisorGraph
   with the HTTPS IP:port, not the HTTP admin port.
2. **Add an HTTPS-port pre-pivot step to the chain runner.** In
   `visor-chain-runner.sh`, after extracting admin-port IPs, run a Shodan
   host-dossier pull on the top N IPs to extract their HTTPS port set, then
   feed those ports into VisorGraph.
3. **HTTP admin port → cert pivot is a two-step, not one-step, attribution.**
   Step 1: identify the HTTPS port on the same IP. Step 2: cert-pivot on that
   port. The admin port is the finding; the HTTPS port is the attribution surface.
4. **VisorGraph `-max-iter` cap.** The installed binary capped at 50 iterations
   (hardcoded). `nuclide-research/VisorGraph` commit 18ea9cb exposes `-max-iter`
   as a CLI flag. For 187 seeds use `-max-iter 500`; the default remains 50 for
   single-host runs.

## Default self-signed cert as a signal

The NIEMS Thailand Kong instance had a TLS cert that was still the Kong install
default: `CN=localhost, L=San Francisco, O=Kong, OU=IT Department`. This is a
secondary finding class: **default TLS certificate = no TLS lifecycle management
= operator is not actively maintaining security posture**. A default cert is a
stronger signal than a self-signed cert, because it specifically identifies that
the operator accepted every Kong install default including the TLS configuration.
Shodan tags this as `self-signed`; a filter for `http.component:"Kong"
ssl.cert.subject.o:"Kong"` would surface instances with the install-default cert
in place.

## Relationships

- Pairs with **#73** (header-versioned APIs evade headerless fingerprinters): both
  are cases where the probe model is structurally incompatible with the target's
  design. There it was request headers; here it is TLS vs plaintext.
- The WAIcore attribution case (`khotlenko.ru` cert on `:443`) is the positive
  example: Envoy proxies the operator's own domain on HTTPS while the admin port
  is plaintext -- pivot the HTTPS cert, not the admin port.
