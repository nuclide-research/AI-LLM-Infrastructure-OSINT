# NCKU Edge Host: a Kubernetes Control Plane Behind a MikroTik Gateway

**Target:** 140.116.247.125
**Operator:** National Cheng Kung University (NCKU), Tainan, Taiwan
**Network:** TANet, AS1659 ERX-TANET-ASN1 (Taiwan Academic Network)
**Sector:** university / academic research
**Date:** 2026-05-31
**Classification:** Internal / Research Use Only

---

## Summary

A single handed-over IP resolved into an NCKU lab's internet edge: a MikroTik
RouterOS gateway DNAT-forwarding to an internal network, with eighteen services
reachable through it. The headline exposure is not an AI service. It is a
KubeSphere v3.1.0 Kubernetes management console, branded "ECPaaS," reachable on
tcp/23180, leaking its version, its unchanged default JWT secret, and its preset
usernames in the page source. Alongside it sits a Django app running with
DEBUG=True in production. The assessment is a clean example of a curated AI-port
scanner reporting "no AI service" on a host that is, in fact, badly exposed.

## Discovery

aimap fingerprinted the IP across its 51 AI-intent ports. It found three open:
80, 443, and 8000. Both 80 and 443 returned the verbatim string
`404 page not found` as `text/plain` with `X-Content-Type-Options: nosniff` and
no Server header. That is the default response of a Go `net/http` mux, and in
this case the Traefik default backend. aimap's verdict: no AI/ML service
identified. A scanner tuned for Ollama, Qdrant, and MLflow has no reason to
probe tcp/23180 or tcp/2000, so it could not see what mattered.

VisorGraph confirmed the proxy. A direct-IP TLS probe with no SNI returned
`TRAEFIK DEFAULT CERT` with the SAN `*.traefik.default`. Traefik only presents a
real certificate and routes to a backend when the request carries a matching
SNI or Host header. The cert told us the architecture (a containerized ingress)
but withheld the operator domain.

The picture opened when Censys was brought in as the passive data source (the
Shodan API key was invalid this session). Censys saw eighteen services where
aimap's curated set saw three:

```
80/HTTP  443/HTTP  2000/MIKROTIK_BW  5422/SSH  6349/HTTP  8000/HTTP
8002/HTTP  9722/SSH  11122/SSH  12722/SSH  16822/SSH  16922/SSH
19022/SSH  19422/SSH  22722/SSH  23180/HTTP  23222/SSH  23322/SSH
```

The `2000/MIKROTIK_BW` service is a RouterOS bandwidth-test server. With eleven
SSH services on scattered high ports, the shape is unmistakable: a MikroTik edge
gateway with DNAT rules, each high SSH port mapping to a different internal
host's sshd.

## The control plane

Censys captured the HTML title `ECPaaS` on tcp/23180. The page is a KubeSphere
single-page app, and its inline `window.globals` config blob is a gift:

- `version: { kubesphere: "v3.1.0", kubernetes: "v1.22.9", openpitrix: "v3.1.0" }`
- `encryptKey: "kubesphere"` (the unchanged default)
- `presetUsers: ["admin", "sonarqube"]`
- `disableAuthorization: false`
- the full nav tree: clusters, access control, users, roles, workspaces,
  DevOps pipelines, credentials, secrets, configmaps

This is the JS-bundle-extraction move handed to us in plain page source: version,
secret, and user enumeration before a single authenticated request. KubeSphere
3.1.0 dates to 2021 and Kubernetes 1.22 is end of life. The unchanged
`encryptKey` is the operator-never-hardened-past-quickstart tell, the
shipping-defaults-are-load-bearing corollary (Insight #13) playing out on a
control plane instead of a model server.

BARE ranked the finding against the Metasploit corpus: 0.532 to
`exploit/multi/kubernetes/exec`, 0.580 to a Rancher authenticated-API
credential-exposure auxiliary. The semantic verdict is that this is a commodity
Kubernetes-exposure class, not a bespoke authz bug. If the console yields
kubectl-equivalent access, the exec module is the packaged path. We did not test
it. Login was not attempted (restraint ethic; this is a live research system).

## The Django app

tcp/8000, behind gunicorn, served a live Django debug 404. The page declares
`DEBUG = True`, names the URLconf `education.urls`, and lists the routes `api/`
and `students/`. Debug mode in production discloses settings, environment, and
stack traces, and a stack trace on any unhandled exception can leak the
`SECRET_KEY`. This finding is live-confirmed: the debug page itself is the
artifact (inner rung B, outer rung 1).

## Re-verification caught a stale claim

Censys also showed tcp/6349 serving an Apache + PHP login portal for a
dairy-cattle activity-sensing and feeding-management research system, with a
`register.php` that offers administrator self-registration. That is an
effective-unauth candidate worth flagging. A live re-check found tcp/6349
**closed**. The finding was downgraded to Censys-observed, not current, and was
not exercised. Logging it as a present exposure off the cached snapshot alone
would have been a confident, reproducible, wrong finding. Re-run the probe
before propagating prior data (Insight #11, generalized).

## Censys cross-population sweep

A sweep for the distinctive console title (`host.services.endpoints.http.html_title="ECPaaS"`)
returned exactly one host: 140.116.247.125 itself. The KubeSphere console is not
a campus-wide fleet by that signal. This is an isolated single-lab exposure, not
a TANet rollout, which shifts the risk framing from systemic to local. The same
result card resolved tcp/8002 as `Encode Uvicorn` (a FastAPI/Starlette ASGI
API), distinct from the Django/gunicorn app on 8000, so the host runs two
separate Python web apps behind the proxy. The Censys snapshot timestamp
(2026-05-31T08:10Z) matched the session, corroborating the live re-checks.

The scripted `data/censys-sweep.py` was not used: its Censys v2 API path is gated
on the free plan. The sweep ran through the authenticated web UI, the same
convention used for Shodan.

## Findings

| # | Severity | Finding | Rung | Live |
|---|---|---|---|---|
| 1 | HIGH | KubeSphere v3.1.0 console exposed, default JWT secret, K8s 1.22 EOL (tcp/23180) | A / 1 | yes |
| 2 | HIGH | Django DEBUG=True in production, education.urls leak (tcp/8000) | B / 1 | yes |
| 3 | MED | MikroTik gateway, 11 SSH services DNAT-forwarded | B / 1 | yes |
| 4 | LOW | PHP portal with open admin self-registration (tcp/6349) | A / 1 | no, downgraded on re-check |

No active exploitation. No credentials used. No disclosure prepared (out of
scope for this run). ML workloads, if any, run inside the cluster and were not
observed from outside.

## Remediation

- **KubeSphere:** put the console behind the campus VPN or an authenticating
  reverse proxy; rotate `jwtSecret` off the `kubesphere` default; upgrade off
  3.1.0 / K8s 1.22. The default secret lets an attacker forge valid console
  tokens.
- **Django:** set `DEBUG = False` and configure `ALLOWED_HOSTS`. Rotate
  `SECRET_KEY` if any debug page was ever public.
- **MikroTik:** drop the bandwidth-test server on tcp/2000 from the WAN; review
  whether eleven internal sshd surfaces need direct internet DNAT; key-only auth
  and source allowlists on each.

## Toolchain provenance

```
0   JAXEN         Shodan API key invalid -> harvest inert; Censys substituted
0b  Censys        platform.censys.io host record -> 18 services, KubeSphere config blob
1   aimap 1.9.41  -target ... and -ports 6349,8002,23180 ; 3 AI-ports, 0 AI fingerprints (honest negative)
2   VisorGraph    -ip ... -sandbox-check ; TRAEFIK DEFAULT CERT, no operator-domain pivot
3   aimap-profile --mode fast ; unclassified (Shodan-degraded) -> manual sector=university
4   JS-bundle     KubeSphere window.globals -> version + default encryptKey + preset users
5   VisorLog      add x4 -> nuclide.db #36158-36161
6   VisorScuba    assess --org NCKU ; 0/0 vacuous pass (no K8s-control-plane control)
7   BARE          KubeSphere -> multi/kubernetes/exec 0.532 ; Django/MikroTik below coverage
+   VisorBishop   4 URLs + IP-shadow ; no AI platform confirmed, no new shadow ports
+   recongraph    empty graph (passive-source-degraded)
+   nu-recon      simulated output, discarded (no key)
```

*Prepared by NuClide Research (Nicholas Kloster + Claude) · 2026-05-31*
