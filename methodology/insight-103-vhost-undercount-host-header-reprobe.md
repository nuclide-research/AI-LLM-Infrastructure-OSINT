---
type: methodology
insight_number: 103
title: "Vhost-routed AI services reject bare-IP probes; re-probe with a Host header from rDNS or cert-SAN before declaring a host down (probe-technique extension of #69)"
status: candidate
codified: 2026-06-17
source_survey: Cat-RAG-Framework-Servers 2026-06-17
falsifiability_tier: high
falsified_by: a population where Host-header re-probing of bare-IP non-responders recovers no additional live AI services (the bare-IP method was complete)
related_insights: [12, 19, 46, 65, 69]
---

# Insight #103 - Vhost-routed AI services reject bare-IP probes; re-probe with a Host header before declaring down

## The pattern

When a scanner probes an AI service by bare IP and the response is 400, 404, or a
timeout, the natural reading is "down" or "not this platform." On a host that
front-ends the service with a name-based virtual host (nginx `server_name`,
Caddy/Traefik host routing, a Cloudflare origin keyed to a hostname), that
reading is wrong. The service is alive; the reverse proxy refused to route the
request because the bare-IP request carried no matching `Host` header.

The bare-IP probe is not measuring service liveness. It is measuring whether the
proxy has a default vhost that answers IP-addressed requests. Many do not, by
design, returning a 400 ("no Host header") or a 404 (default vhost is a stub) or
dropping the connection. The AI service behind the proxy is fully reachable the
moment the request carries the correct hostname.

The fix is a re-probe technique, not a new port or a new fingerprint:

1. On any bare-IP 400 / 404 / timeout from a host that is otherwise alive
   (TLS handshake completes, or the port answers), resolve a candidate hostname.
2. Sources for the hostname, in order of strength:
   - **TLS certificate SAN** (the cert the host already presented in the
     handshake; an exact-match origin name).
   - **rDNS / PTR** record for the IP.
   - The hostname implied by an `nginx`/`Cloudflare` default-vhost error body.
   - Operator-attribution names already in hand (Insight #46 cert-CN pivot).
3. Re-issue the probe with `Host:` (and SNI) set to that hostname.

A bare-IP 400 is a re-probe trigger, not a verdict.

## Empirical founding case - mobee.com (159.69.89.55)

Cat-RAG-Framework-Servers bare-IP probed 159.69.89.55 for LightRAG and got a
non-answer, so the host sat in the "unreachable / undercounted" bucket. The host
had presented a Cloudflare Origin CA certificate with SAN `*.mobee.com` during
the TLS handshake. Re-probing with the SAN-derived Host header recovered the
service:

```
GET /health  Host: static.55.89.69.159.clients.your-server.de   ->  auth_mode=disabled
GET /documents  (same vhost)  ->  status buckets:
    processed: 426, failed: 425, parsing: 105, analyzing: 9, pending: 34
```

A populated PRODUCTION unauthenticated LightRAG corpus of ~600+ documents,
invisible to the bare-IP probe, on the origin box of an OJK-regulated Indonesian
crypto exchange. It went from "unreachable" to a co-headline finding (F7) solely
on the Host-header re-do. The data was never read (rung A/1); the document-status
buckets are the metadata the platform itself reports.

The same survey showed the pattern is not a one-off. The L-01 LightRAG Tokyo
fleet had 35.78.152.204 returning HTTP 400 on bare IP while alive, the exact
"rejecting without Host header" signature, queued for an rDNS Host-header retry.

## Why this extends Insight #69 rather than restating it

Insight #69 is a **breadth** correction: a curated-port scan returning zero means
"widen the port set," because the host's exposure may live on ports the curated
scan never touches. #103 is a **probe-technique** correction at a port the scan
DID touch: the right port answered, the platform is there, and the probe still
read "down" because the request was malformed for a vhost-routed backend. #69
says do not conclude clean from a narrow port set. #103 says do not conclude down
from a bare-IP request shape. Both are species of "the negative is in the
instrument, not the host," #69 at the port layer, #103 at the request-construction
layer.

## Population consequence

Bare-IP probing systematically UNDER-counts the vhost-routed unauthenticated
population. The miss is not random: it correlates with operator sophistication.
Operators who put their AI service behind a named reverse proxy or a Cloudflare
origin are exactly the operators most likely to be running a real production
workload (mobee.com is regulated, ISO 27001, an active Anthropic customer), so the
bare-IP method preferentially drops the highest-value, most-populated targets and
keeps the bare unconfigured ones. A survey that does not Host-header-re-probe its
bare-IP non-responders publishes an unauth count biased low precisely where the
exposure matters most.

## How to apply

1. Capture the cert SAN during the Stage 0c TLS handshake; carry it into the
   re-probe stage as a candidate Host value (no extra request needed to learn it).
2. Treat bare-IP 400 / 404 / connection-drop on a TLS-alive host as a re-probe
   trigger, logged as "alive, rejecting without Host header," not as "down."
3. Re-probe with SAN-Host, then rDNS-Host, then default-vhost-implied-Host, in
   that order; first 200-with-platform-marker wins.
4. Only after the Host-header re-probe also fails may the host be declared down.
5. Restraint unchanged: the recovered surface is enumerated at the metadata layer
   (auth flag, document-status counts), not read.

## Related insights

- Insight #69 - Curated-scan negative is not a host negative (this is the
  probe-technique sibling at the request-construction layer)
- Insight #12 - IP-direct shadow (co-deploy on the same box; #103 is how you reach
  a vhosted member of that stack)
- Insight #19 - SPA/headless-API exposure tell (vhost routing is a common front)
- Insight #46 - TLS cert-CN operator-attribution surface (the SAN that supplies
  the Host value)
- Insight #65 - TLS cert dork selection bias (the same SAN data, used at the dork
  stage; here it is used at the probe stage)

## Promotion criteria

Confirmed at 1 platform/host class (LightRAG, founding host mobee.com, plus a
second rejecting host in the same fleet). Promotion to numbered Insight requires
the Host-header re-probe to recover live unauthenticated AI services on 2 more
platform classes whose bare-IP probe read "down" or "400/404." Candidates: any
vhost-routed LlamaIndex/Haystack behind nginx, any Cloudflare-origin vector DB.
