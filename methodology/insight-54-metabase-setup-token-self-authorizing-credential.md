---
type: methodology
insight_number: 54
title: "Metabase setup-token: a self-authorizing credential class"
---

# Insight #54 — Metabase setup-token: a self-authorizing credential class

**Codified:** 2026-05-21 (embedding-tier2-2026-05-21 session — masscan sweep of OVH/Scaleway tier-2 cloud ranges)
**Family:** Insight #39 (install-wizard-open / pooled-account attribution laundering), Insight #16 (no status code is identity), Insight #25 (auth-on-default thesis)
**Falsifiability tier:** low. The mechanism is Metabase's own documented setup flow. The structural claim is deterministic.

---

## The pattern

Six Metabase instances on OVH/Scaleway with live setup tokens. The token is exposed at unauthenticated GET `/api/session/properties` as the `setup-token` field. With that token, POST to `/api/setup` registers the caller as the first admin — full control over all connected databases, dashboards, and user accounts.

## Why "self-authorizing credential"

The Metabase setup token is structurally distinct from a leaked secret. A leaked secret is an authorization artifact that escaped its intended boundary — a `.env` file committed to GitHub, a DATABASE_URL in a container's environment dump. The token is a separated proof that still requires: network path to the database, credential validity check, and often port access through a firewall.

The Metabase setup token is intentionally exposed at an unauthenticated endpoint, by design, because the operator is supposed to claim it immediately and complete setup. The token's presence at GET `/api/session/properties` is itself proof it has not been claimed. The credential proves its own exploitability. This makes it self-authorizing: possession equals exploitability, and reachability equals possession.

The chain is two requests:

```
GET /api/session/properties
  -> {"setup-token": "<uuid>", ...}

POST /api/setup
  -> first-admin registration, full platform control
```

No credential guessing. No brute force. No lateral movement required. The platform hands it to any caller who arrives before the operator does.

Compare to a leaked DATABASE_URL: that credential's value is unknown until retrieved, requires a network path to the target database, requires credential validity (credentials rotate, expire, get revoked), and may still be blocked by firewall rules or IAM policy. The Metabase setup token has none of these friction points. GET → POST is the complete chain.

## Metasploit coverage gap

BARE max score across all six instances: **0.548** — below the 0.55 no-match threshold. No existing Metasploit module covers Metabase setup-token admin registration. The closest semantic matches BARE returns are tangential: Twonky auth-bypass, SysAid admin-account creation, APISIX default-token RCE. The signature of the class — unauthenticated API endpoint returns a token, same token POSTed to a registration endpoint claims admin — is absent from the corpus. A module covering the `/api/setup` POST with a scanned token fills this gap and would rank at the top of the semantic search for any future Metabase scan.

## Verification discipline

- **PASS**: GET `/api/session/properties` returns HTTP 200 with a non-empty, non-null `setup-token` field
- **CONFIRMED surface**: all six hosts; SETUP_OPEN label assigned
- **Ethical stop**: POST to `/api/setup` not performed; surface confirmed open, exploitation not executed
- **DO NOT label HIGH without the confirmed token**: if `/api/session/properties` returns 200 with an empty or null `setup-token`, setup is complete and the surface is closed. The presence check is mandatory; a 200 alone is not confirmation per Insight #16

## Severity basis

Six instances, all SETUP_OPEN confirmed by the token presence check:

- **Surface tier: HIGH** — unauthenticated admin registration is a single POST from confirmed token
- **Impact ceiling: CRITICAL** — admin credentials for all connected data sources (databases, BI dashboards) are available post-setup. Metabase operators typically connect production databases pre-setup; the token is a live path from anonymous internet to production database credentials
- **Assigned tier: HIGH** — exploitation was not performed; impact ceiling noted but not confirmed. Per Insight #100-percent-verified-tier-labels, the assigned tier tracks what is in hand

## Structural parallel to Insight #39 (install-wizard-open)

Sub2api SETUP_OPEN (Insight #39) and Metabase setup-token are the same class: a deployment-phase admin-claim primitive left live on the public internet. The operator set up the infrastructure and left before claiming the admin credential.

The difference is blast radius. Sub2api's wizard sets up an LLM proxy operator account; impact is API quota drain and attribution laundering. Metabase's wizard creates the admin for the analytics platform and inherits all connected data sources. An operator who connected production databases before completing setup left a live anonymous path to those database credentials. Metabase's blast radius is typically wider and more direct.

The shared failure mode: the platform is designed with the assumption that the operator completes setup in the same session as deployment. The deployment-to-claim gap is where the exposure lives. Any platform with this architecture — ship unauthenticated, claim-to-secure, assume immediate operator action — belongs to this insight family.

## Population and attribution

Six confirmed instances, OVH/Scaleway FR ranges. All bare cloud IPs; no custom domain attribution from cert pivot (VisorGraph run, zero cert-confirmed domains on any of the six). Shodan credits exhausted during the sweep — full population scan against the broader OVH/Scaleway prefix range deferred.

No clustering signal on these six: different /24s, no shared cert fingerprint, no banner correlation beyond Metabase version strings. Likely independent operator deployments, not a single managed cluster.

## Remediation

Complete the Metabase setup wizard. If setup cannot be completed immediately, block port 3000 at the firewall. There is no intermediate hardening step — the token is present until the setup wizard is run, and the wizard is accessible to anyone with network path to port 3000.

## What this insight is NOT

- NOT a claim that all six hosts contain sensitive data. Admin access to the platform does not confirm sensitive data in connected databases; that requires post-access enumeration that was not performed.
- NOT a Metabase-specific finding class. Any analytics or BI platform that ships a first-admin token at an unauthenticated endpoint belongs to this family. The mechanism is the design pattern, not the product.
- NOT confined to tier-2 cloud ranges. OVH/Scaleway was the survey scope; the class will appear on any cloud provider.

## Falsification conditions

The self-authorizing-credential framing is wrong if:

1. POST to `/api/setup` with a valid token is rejected without additional factors (email verification, network allowlisting, operator confirmation). Would make this HIGH-but-not-trivial rather than trivial.
2. Metabase rotates or expires the setup token on a short timer. Would make arrival-before-operator a race condition rather than an open window. Current empirical observation: tokens persist on all six hosts for the duration of the survey window (hours to days).

## Cross-references

- **Insight #39:** pooled-account attribution laundering / SETUP_OPEN class. Metabase setup-token is the BI-platform instance of the same deployment-gap failure mode
- **Insight #16:** no status code is identity. The HTTP 200 from `/api/session/properties` is not the confirmation — the non-null `setup-token` field value is
- **Insight #25:** auth-on-default thesis. Six of six Metabase instances without a completed setup wizard are auth-off-by-default for the entire platform

## Source data

- Survey: embedding-tier2-2026-05-21 session, masscan of OVH FR (91.121.0.0/16, 51.75.0.0/16) and Scaleway (51.15.0.0/16, 163.172.0.0/16) port 3000
- Token verification: `GET /api/session/properties` on each candidate, `setup-token` field null-check
- BARE scan: run against all six hosts, max score 0.548, no module match
- VisorGraph: run, zero cert-confirmed domain attributions
- Population: 6 confirmed SETUP_OPEN; full range scan deferred (Shodan credits exhausted)

---

*Codified by Nuclide Research (Nicholas Kloster + Claude) 2026-05-21 from the embedding-tier2-2026-05-21 OVH/Scaleway sweep. Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`.*
