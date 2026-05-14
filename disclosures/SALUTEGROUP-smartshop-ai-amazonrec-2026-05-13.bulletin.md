---
to: info@salutegroup.com.tr
cc: abuse@pendc.com
severity: CRITICAL
target: api.amazonrec.space  ·  78.135.66.61
issued_date: 2026-05-13
kind: Coordinated vulnerability disclosure  ·  no click required
slug: SALUTEGROUP-smartshop-ai-amazonrec-2026-05-13
---

## Subject
Security advisory — unauthenticated production API and ML pipeline on api.amazonrec.space (78.135.66.61)

## Who we are
NuClide Research studies how AI and machine-learning infrastructure gets left exposed on the public internet. When we find a host at risk, we send the owner a free advisory. This is one of those. We are not selling anything, we do not run a bug-bounty program, and we do not take payment from the people we contact. We hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11.

## What we found
The host at `api.amazonrec.space` (`78.135.66.61`) is exposing a full AI/ML stack to the public internet: a model API branded "SmartShop AI", an experiment tracker, an in-memory store, a workflow scheduler, and a database. The inference and experiment-tracking layers accept anonymous calls. Right now, anyone on the internet can call the recommendation API and read the experiment metadata without a password.

The reason we are contacting Salute Group: this host runs the mail server for your brand Nadorawear (`mail.nadorawear.com` resolves to `78.135.66.61`), the `nadorawear.com` domain WHOIS lists `domain@salutegroup.com.tr`, and the SmartShop AI deployment shares the same hosting and DNS posture. If SmartShop AI is a Salute Group product or a Salute Group client's project, you are best placed to forward this report to the right team. If it is not, please let us know and we will route it elsewhere.

You weren't targeted. We don't pick specific companies; our tooling watches the public internet for AI infrastructure that has been accidentally left open, and this host turned up in a routine review. Nothing here costs anything. This is a heads-up.

## How we found it
We scan the public internet (the same kind of survey that powers Shodan and Censys) for hosts whose visible services look like an AI or machine-learning system. When a host carries those services and also exposes things that should never be reachable from the open internet, like a passwordless experiment tracker or a database with no firewall in front of it, we flag it for a human to look at.

Our probes are read-only. We look at the public banner information each service hands out to anyone who connects, the same thing your own admin would see. We did not access, copy, or store any of the data those services hold. This host was reviewed by hand on 2026-05-13. Nothing in this bulletin came from authenticated access.

## Infrastructure
| Field | Value |
|---|---|
| IP | 78.135.66.61 |
| rDNS | 78.135.66.61.pendns.net |
| ASN | AS48678  ·  PENTECH BILISIM TEKNOLOJILERI SANAYI VE TICARET LIMITED SIRKETI |
| Network | geo: TR (Istanbul)  ·  hosting provider: PENTECH BILISIM |
| Hostnames | api.amazonrec.space\nmlflow.amazonrec.space\nairflow.amazonrec.space\nmail.nadorawear.com |
| Frontend | amazonrec.space — Vercel-hosted SPA, "SmartShop AI MLOps Console" |

## Findings
| Port | Service | Severity | Issue | Verify |
|---|---|---|---|---|
| 443 | FastAPI (api.amazonrec.space) | CRITICAL | 13 endpoints publicly callable with zero authentication; OpenAPI schema and /docs reachable anonymously; components.securitySchemes is empty | https://api.amazonrec.space/docs |
| 5000 | MLflow tracking | CRITICAL | Anonymous experiment, run, and artifact disclosure; artifact URIs point to wasbs:// Azure storage | http://78.135.66.61:5000/ |
| 6379 | Redis | CRITICAL | Internet-exposed; banner tagged database and eol-product by Shodan | $ redis-cli -h 78.135.66.61 PING |
| 8080 | Apache Airflow | HIGH | Sign-in page reachable from the public internet; running release matches 11 outstanding CVEs (CVE-2024-25142 cluster) | http://78.135.66.61:8080/ |
| 5432 | PostgreSQL | HIGH | Datastore directly internet-reachable; backing store for the SmartShop AI API and the MLflow tracker | $ nc -zv 78.135.66.61 5432 |
| 25/465/587 | Postfix mail | MEDIUM | Banner tagged eol-product; also serves mail.nadorawear.com on the same host | $ nc -zv 78.135.66.61 25 |

## Findings note
The first three rows say that anyone on the internet can call your recommendation model, read your experiment metadata, and reach your in-memory cache, without a password. The next two say your job scheduler and your database are reachable on the same path; the network layer that would normally sit in front of them is missing. The sixth row is a hygiene issue: an outdated mail daemon on the same host.

## Evidence
A single unauthenticated GET request:

$ curl -s https://api.amazonrec.space/api/v1/session/init
{"success":true,"user_id":"AH2IJABKXWIZIO2FYJXNFEXNRR6A","interaction_count":19,
 "top_categories":["Buy a Kindle","Books","Toys & Games"],"assigned_at":"2026-05-13T16:56:31Z"}

$ curl -s https://api.amazonrec.space/openapi.json | jq '.paths | keys | length'
13

$ curl -s https://api.amazonrec.space/api/v1/interactions/stats
{"total_logged":15139,"db_writes":6374,"s3_writes":15139}

$ curl -sI http://78.135.66.61:5000/ | head -1
HTTP/1.1 200 OK   # MLflow UI, no auth

[ probes were read-only; no writes, no enumeration beyond the first page of each listing ]

## Verify it yourself
You shouldn't have to take our word for any of this. Every URL in the Findings and Evidence sections is a live link to a piece of your own infrastructure. Click one and it will open the exposed dashboard or status page in your browser, with no login prompt. The two findings that aren't reachable in a browser, Redis and PostgreSQL, carry a one-line terminal command you can paste into any machine. None of those checks send anything back to us.

You are also welcome, and we would actively encourage it, to forward this bulletin to an internal security engineer or to an outside firm. Nothing in it depends on NuClide Research being involved going forward. We will publish a redacted technical writeup on 2026-05-27 per standard coordinated-disclosure practice; the published version will redact specific user IDs and any operator-customer data.

## Recommended fix
1. Put api.amazonrec.space behind a login. Your FastAPI spec already declares a global security scope; flipping that to require an actual scheme (API key header, OAuth, or Cloudflare Access) is a small change in the app initialization.
2. Lock down MLflow. Turn on authentication and TLS, keep model-artifact storage off any internet-routable path, and rotate any tokens that have lived in plaintext on the tracker.
3. Lock down Redis. Set requirepass, define ACLs, leave protected-mode on, and upgrade off the end-of-life branch to a currently-supported release.
4. Lock down PostgreSQL. Restrict pg_hba.conf to internal CIDR ranges only, and audit any accounts created during the exposure window.
5. Upgrade Airflow. Move to a currently-supported release and apply the eleven outstanding advisories that map to the observed version.
6. Decide on Postfix. Decommission the mail daemon if outbound mail is not in active use on this host, or restrict it to internal submission only. This also affects mail.nadorawear.com.
