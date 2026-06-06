---
type: case-study
category: cat-px
platform: Arize Phoenix
date: 2026-06-06
findings: 41 projects-unauth, 34 users-unauth (of 55 reachable)
status: verified
toolchain: herald v0.1.1
---

# Arize Phoenix Population Survey — 41/55 Unauthenticated Project Disclosure

_NuClide Research · 2026-06-06_

---

## Executive Summary

Arize Phoenix (github.com/Arize-ai/phoenix) is an open-source LLM observability and tracing platform — span ingestion, project organization, dataset versioning, prompt management for production AI applications. 94 Shodan-indexed instances on `"Phoenix" port:6006`. 89 unique endpoints downloaded; 55 responded.

**Of 55 reachable instances, 41 (74.5%) expose `/v1/projects` without authentication, and 34 (61.8%) expose `/v1/users` without authentication.** The user list endpoint returns account records including creation timestamps and account IDs — a PII disclosure at population scale.

This is a smaller population than Langfuse or RAGFlow, but the auth surface is more severe: where Langfuse and RAGFlow expose only a signup flag, Phoenix exposes the data layer (projects, users) directly. The finding class is **LLM02:2025 Sensitive Information Disclosure** (current OWASP Top 10 for LLM Applications #2).

Notable institutional findings: Northeastern University (Boston, USA), SENAI (Brazil — Serviço Nacional de Aprendizagem Industrial, the Brazilian national vocational education service).

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `"Phoenix" port:6006` | shodan CLI (89 records) |
| Stage 0c | TCP/HTTP liveness via `/healthz` | herald |
| Stage 1b | Auth-posture probe `/v1/projects` and `/v1/users` (array_nonempty match) | herald phoenix platform config |
| Stage 3v | Endpoint semantics validated against Phoenix v6.x source (`src/phoenix/server/api/routers/v1/`) | manual review |
| Stage 12b | Dataset enrichment with country/org from Shodan record | Python + Shodan join |

The probes use `array_nonempty` matching: if the response contains a non-empty `data` array, the finding fires. Phoenix returns `{"data": [], "next_cursor": null}` when authenticated routes are queried without credentials in instances where auth is configured — so a non-empty `data` array is the unauth signal.

NuClide restraint: account count is the only `/v1/users` field consumed by herald. Schema/PII details were not extracted, per the restraint ethic — names ARE the finding.

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 94 | — |
| Unique endpoints downloaded | 89 | — |
| Reachable (HEALTH_OPEN) | 55 | 61.8% of indexed |
| `/v1/projects` unauth (PROJECTS_UNAUTH) | 41 | 74.5% of reachable |
| `/v1/users` unauth (USERS_UNAUTH) | 34 | 61.8% of reachable |

The PROJECTS_UNAUTH > USERS_UNAUTH gap (41 vs 34) is consistent: about a third of Phoenix instances have configured user accounts (so `/v1/users` returns data), and the remainder have no users at all (a fresh install with no auth requirement — even more permissive).

---

## Notable Findings

### Northeastern University — `129.10.224.226:6006` (HIGH)

Northeastern University (Boston, USA, AS161). Phoenix instance with two projects: `Essaybot` and `default`. The `Essaybot` project name suggests a student essay-grading or writing-assistant LLM application — potentially handling student work products, which is FERPA-relevant data under US education privacy law.

Project names accessible unauthenticated. User records (count = 2) accessible. Span/trace data not exercised (restraint).

Disclosure recipient: `oirc@northeastern.edu` (Northeastern Office of Information Security)

### SENAI Brazil — `200.9.65.187:6006` (HIGH)

Serviço Nacional de Aprendizagem Industrial (SENAI) is Brazil's national industrial apprenticeship service — vocational education for ~3 million students annually, operated by the Brazilian National Confederation of Industry (CNI). Phoenix instance on SENAI infrastructure with 2 projects exposed and 2 users disclosed.

Vocational education context: Brazilian LGPD applies. Disclosure recipient: CERT.br for coordination, with SENAI national IT direct contact.

### `37.27.248.144:6006` Hetzner Helsinki — 21 Projects Disclosed (HIGH)

Single Phoenix instance on Hetzner Helsinki (AS24940) exposing 21 distinct project names unauthenticated. The largest project-count disclosure in the population. Operator not identified from the Shodan record (no TLS cert, no PTR).

Operator profiling: 21 projects suggests a sophisticated production deployment — either a multi-tenant SaaS offering Phoenix-as-a-service to downstream customers, or a single large engineering org with many parallel LLM applications. Either case elevates concern.

### Scaleway Paris Cluster — 7 Instances (MEDIUM-PATTERN)

7 Phoenix instances on Scaleway France (`163.172.x`, `51.15.x`, `51.158.x`, `51.159.x`), all PROJECTS_UNAUTH, most also USERS_UNAUTH. The IP clustering suggests either a single Scaleway customer running a fleet or a Scaleway tenant pattern. Worth follow-up profiling to determine if this is a single operator.

### Google Cloud US Cluster — 7 Instances (MEDIUM-PATTERN)

7 Phoenix instances on Google LLC (`34.x`, `35.x`), all PROJECTS_UNAUTH. Same pattern observation. One instance (`34.133.205.22`) discloses 8 projects.

---

## Geographic Distribution (Findings)

| Country | PROJECTS_UNAUTH hosts |
|---|---:|
| United States | 12 |
| France (Scaleway) | 8 |
| Germany (Hetzner / Contabo / IONOS) | 7 |
| Finland (Hetzner) | 1 |
| Brazil (SENAI) | 1 |
| Sweden | 1 |
| Poland | 1 |
| China (Aliyun, UCloud) | 2 |
| Vietnam | 1 |
| India | 1 |
| Indonesia | 1 |
| Canada | 1 |
| Other | 5 |

Unlike Langfuse and RAGFlow (CN-dominant and CN-second respectively), Phoenix's population is US-Western-Europe dominated. This reflects Arize's commercial customer base — primarily US enterprise AI teams using the open-source Phoenix for self-hosted observability alongside Arize's paid product.

---

## Comparison: Auth Surface Severity

| Platform | Auth signal | Data exposed |
|---|---|---|
| Langfuse | `signUpDisabled: false` flag | Registration possible; trace data behind workspace auth |
| RAGFlow | `registerEnabled: 1` flag | Registration possible; knowledge base behind tenant auth |
| Open WebUI | `features.auth: false` | Full chat interface, model inference |
| Dify | `is_allow_register: true` | Registration possible; apps behind workspace auth |
| **Phoenix** | `/v1/projects`, `/v1/users` return data | **Direct project + user enumeration; spans potentially accessible** |

Phoenix's exposure model is the most severe: while the other platforms gate the *data layer* even when registration is open, Phoenix exposes project names and user account metadata unauthenticated, requiring no account creation step at all.

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| Northeastern University | HIGH (FERPA-class) | oirc@northeastern.edu |
| SENAI Brazil | HIGH (LGPD-class) | CERT.br + SENAI IT |
| `37.27.248.144` (21 projects) | HIGH (operator unknown) | Vendor mediated via Arize |
| Scaleway Paris cluster (7) | MEDIUM | Profiling first, then per-tenant |
| Google Cloud cluster (7) | MEDIUM | Profiling first |
| 41 total PROJECTS_UNAUTH | UPSTREAM | Arize: change default to auth-required for `/v1/projects` and `/v1/users` |

The upstream remediation is the highest-leverage. Arize Phoenix currently ships with `PHOENIX_ENABLE_AUTH` defaulting to false. A one-line config change protects the entire population.

---

## Remediation (per-operator)

```bash
# Phoenix environment:
PHOENIX_ENABLE_AUTH=true
PHOENIX_SECRET=<strong-random-secret>
```

Verify:
```bash
curl http://IP:6006/v1/projects
# Expected: 401 or 403, NOT a populated data array
```

---

## Toolchain Provenance

```
Step 0:    shodan download '"Phoenix" port:6006' (89 records)
Step 0c:   IP extraction → ip-port.txt (89 unique)
Step 1b:   herald -platform phoenix < ip-port.txt
           - probe id projects_unauth: /v1/projects array_nonempty
           - probe id users_unauth: /v1/users array_nonempty
           - probe id health_open: /healthz body_contains "OK"
Step 3v:   Endpoint semantics verified against Arize/phoenix v6.x source
Step 12b:  This document
```

Tool: **herald** v0.1.1 (`github.com/nuclide-research/herald`). Phoenix config added with three probes covering the LLM02-class disclosure surface.

---

## Research Contribution

Phoenix is the third same-day platform survey (after Langfuse and RAGFlow). Unlike the registration-flag findings, Phoenix surfaces a **direct data-layer disclosure**: the platform's default deployment exposes the actual data model (projects, users) without any auth step. This maps cleanly to OWASP LLM Top 10 (2025) entry **LLM02 Sensitive Information Disclosure**, which jumped from #6 to #2 in the 2025 revision specifically because of incidents like this — enterprise AI deployments leaking observability data publicly.

The Phoenix population is also the smallest of the three (89 vs 1,140 vs 1,905), suggesting either a more sophisticated user base who hardens by default, or a less mature deployment cycle where many operators still run development instances unauthenticated. The 74.5% PROJECTS_UNAUTH rate suggests the latter.

The three-platform same-day corpus (Langfuse 88.9%, RAGFlow 87.2%, Phoenix 74.5%) is a strong empirical baseline for the auth-permissive-default cohort hypothesis (Candidate Insight #76).
