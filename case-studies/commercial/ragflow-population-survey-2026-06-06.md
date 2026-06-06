---
type: case-study
category: cat-rf
platform: RAGFlow
date: 2026-06-06
findings: 618 register-open of 709 reachable (87.2%)
status: verified
toolchain: herald v0.1.1
---

# RAGFlow Population Survey — 618/709 Open Registration (87.2%)

_NuClide Research · 2026-06-06_

---

## Executive Summary

RAGFlow (github.com/infiniflow/ragflow) is an open-source RAG knowledge-base engine — document ingestion, vector retrieval, LLM-backed Q&A over enterprise knowledge bases. 1,915 Shodan-indexed instances on `http.title:"RAGFlow"`. 709 responded to live probing. **618 (87.2% of live, 32.3% of indexed) expose `registerEnabled: 1` to the public internet.**

`registerEnabled: 1` is RAGFlow's default deployment posture, exposed unauthenticated via `GET /v1/system/config`. The response also confirms RAGFlow's identity and configuration model:

```json
{"code": 0, "data": {"registerEnabled": 1}, "message": "success"}
```

Anyone with an internet connection can register an account on these instances. Once registered, the user can create a tenant workspace and ingest documents into a vector store — but more significantly, in RAGFlow's tenant model, an authenticated user can enumerate tenant structure, knowledge base names, and assistant configurations of other tenants depending on workspace isolation configuration.

The 87.2% rate sits between Langfuse (88.9%) and Flowise (68.7%) and is the second-highest auth-permissive default measured in the 2026 NuClide survey program. Combined with the prior survey note that the **CVE-2024-12433 pre-auth RCE class applies to RAGFlow <0.14.0** and the version is not externally confirmable from the unauth surface, this is a high-priority population for upstream disclosure.

Notable institutional findings: Hong Kong University of Science and Technology, Brno University of Technology, Indiana University, Taiwan Ministry of Education Computer Center (two instances).

---

## Methodology

| Stage | Action | Tool |
|---|---|---|
| Stage 0 | Shodan harvest `http.title:"RAGFlow"` | shodan CLI (1,905 records) |
| Stage 0c | TCP/HTTP liveness | herald (built-in client) |
| Stage 1b | Auth-posture probe `/v1/system/config` field `data.registerEnabled == 1` | herald ragflow platform config |
| Stage 3v | Source-code verification: the field is set from RAGFlow's `service_conf.yaml` `register_enabled` key; default `True` in upstream | manual review of `api/apps/system_app.py` |
| Stage 12b | Dataset enrichment with country + ASN from Shodan record | Python + Shodan record join |

The probe was validated against `1.13.185.6:8888` (TencentCloud), which returned `registerEnabled: 1`. RAGFlow's API pattern returns HTTP 200 with an inner `code` field — `code: 0` means success, `code: 401` means unauthorized. The probe matches against the inner code, not the HTTP status, because all RAGFlow responses are wrapped HTTP 200.

---

## Population Results

| Metric | Count | Rate |
|---|---|---|
| Shodan-indexed | 1,915 | — |
| Downloaded for sweep | 1,905 | — |
| Reachable with valid RAGFlow response | 709 | 37.2% of indexed |
| `registerEnabled: 1` (REGISTER_OPEN) | 618 | 87.2% of reachable |
| Config disclosure (any RAGFlow response) | 708 | — |

The 37.2% reachability rate is lower than Langfuse (80.5%) — RAGFlow installations are more frequently behind reverse proxies that intercept the API path, or have churned off Shodan's cache.

---

## Geographic Distribution

| Country | REGISTER_OPEN hosts |
|---|---:|
| China | 429 |
| United States | 45 |
| Germany | 36 |
| Singapore | 23 |
| Hong Kong | 17 |
| Vietnam | 10 |
| Taiwan | 7 |
| India | 7 |
| Japan | 5 |
| UAE | 5 |

RAGFlow's user base concentration is dramatically Chinese: 429 of 618 (69.4%) of open-registration instances are in China. RAGFlow originates from InfiniFlow (Shanghai). This is a different operator demographic than Langfuse (CN/US roughly even at 200 each).

---

## Verified Institutional Findings

### Hong Kong University of Science and Technology — `143.89.8.80:8080` (HIGH)

HKUST campus network (AS9405). RAGFlow instance with `registerEnabled: 1`. HKUST is one of Asia's leading research universities.

Disclosure recipient: `cscsec@ust.hk` (HKUST Computing Services Security)

### Brno University of Technology — `147.229.83.184:81` (HIGH)

Brno University of Technology (VUT Brno), Czechia (AS197451). RAGFlow instance on the university's allocation.

Disclosure recipient: `csirt@vutbr.cz`

### Indiana University — `149.165.150.184:80` and `:443` (HIGH)

Indiana University allocation (AS87 / AS19782). Single host exposing RAGFlow on both HTTP and HTTPS ports, both with `registerEnabled: 1`.

Disclosure recipient: `it-incident@iu.edu` (IU University Information Security)

### Taiwan Ministry of Education Computer Center — `140.128.122.64:443` and `163.15.166.54:80` (CRITICAL)

Two RAGFlow instances on Taiwan national education infrastructure with open registration. The same MoE Computer Center allocation hit on the Langfuse survey (`140.115.59.61:3000`) — this is the third confirmed exposure on Taiwan national edu infrastructure in a single day, all platforms with public registration enabled.

Disclosure recipient: TWCERT/CC (consolidated escalation across the three findings).

### Shenzhen Middle School (深圳中学) — `202.96.165.227:10443` (HIGH)

Shenzhen Middle School allocation. RAGFlow instance on K-12 school infrastructure with open registration. Risk consideration: school IT infrastructure may store minor-student data; even if RAGFlow is segregated from the SIS, public registration on school-affiliated infrastructure is non-trivial.

Disclosure recipient: Coordinate through education sector channels in China; given the language and jurisdiction, a direct vendor disclosure to InfiniFlow with school identifying details is the safer path.

---

## CVE-2024-12433 Class Risk

The prior Cat-07 survey (2026-05-28) noted that **CVE-2024-12433 (RAGFlow pre-auth RCE, <0.14.0) is exploitable on the population class** but the specific version is not externally confirmable from the unauth surface — RAGFlow does not disclose its version in `/v1/system/config` or any other unauth endpoint.

Consequence: of the 618 REGISTER_OPEN hosts, an unknown subset is also vulnerable to CVE-2024-12433. The version cannot be enumerated remotely; it requires either source-code provenance (rare for self-hosted instances) or authenticated access. The recommended posture: treat the entire 618-host REGISTER_OPEN population as having an additional latent RCE risk weighted by the InfiniFlow release-version distribution at time of deployment.

NuClide restraint: no CVE-2024-12433 exploitation was attempted. The remote version check that would confirm vulnerability requires triggering the RCE primitive itself.

---

## Disclosure Pipeline

| Finding | Tier | Recommended action |
|---|---|---|
| Hong Kong U of Sci & Tech | HIGH | cscsec@ust.hk |
| Brno U of Technology | HIGH | csirt@vutbr.cz |
| Indiana University | HIGH | it-incident@iu.edu |
| Taiwan Ministry of Education (2 hosts) | CRITICAL | TWCERT/CC consolidated (with prior Langfuse finding) |
| Shenzhen Middle School | HIGH | InfiniFlow vendor disclosure |
| 618 commercial / cloud-tenant hosts | UPSTREAM | InfiniFlow: change `register_enabled` default from True to False |

The most efficient upstream remediation is a one-line change to `service_conf.yaml` template defaults. Combined with the version-disclosure gap, the upstream maintainer (InfiniFlow) is positioned to materially reduce both the registration-open population and the CVE-2024-12433 latent-risk population in a single release.

---

## Remediation (per-operator)

```yaml
# RAGFlow service_conf.yaml
register_enabled: 0    # Close public registration
```

Verify:
```bash
curl http://IP:PORT/v1/system/config | python3 -c "
import sys, json
print(json.load(sys.stdin).get('data', {}).get('registerEnabled'))
"
# Expected: 0
```

---

## Combined Insight: Langfuse + RAGFlow

Two independent surveys on the same day:

| Platform | Population | REGISTER/SIGNUP_OPEN | Rate |
|---|---:|---:|---:|
| Langfuse | 918 reachable | 816 | 88.9% |
| RAGFlow | 709 reachable | 618 | 87.2% |

Both upstream maintainers (Langfuse — Berlin; InfiniFlow — Shanghai) have shipped `signUpDisabled: false` / `register_enabled: 1` as the default for years across multiple major versions. Both are open-source observability/RAG platforms. Both have been deployed extensively into university research environments — and the same Taiwan MoE Computer Center allocation was found exposing both.

This is a robust empirical pattern: **the auth-permissive default is the rule for new-generation OSS AI/LLM infrastructure platforms, not the exception.** Open WebUI's case (where the default has corrected over versions) demonstrates that disclosure pressure can move the rate. Neither Langfuse nor RAGFlow has yet been subject to that pressure. The dual disclosure is the test condition.

---

## Toolchain Provenance

```
Step 0:    shodan download 'http.title:"RAGFlow"' (1,905 records)
Step 0c:   IP extraction → ip-port.txt (1,905 unique)
Step 1b:   herald -platform ragflow < ip-port.txt
           - probe id register_enabled: /v1/system/config field data.registerEnabled == 1
           - probe id config_disc: /v1/system/config field code == 0
Step 3v:   Source-code verification: InfiniFlow RAGFlow api/apps/system_app.py
           confirms data.registerEnabled is set from service_conf.yaml
Step 12b:  This document
Step 13:   Commit to OSINT repo + push to GitHub
```

Tool: **herald** v0.1.1 (`github.com/nuclide-research/herald`) — added numeric type coercion (YAML int / JSON float64 normalization) during this survey. RAGFlow platform config added.

---

## Insight Update

This survey adds the second data point supporting the cohort-default hypothesis from the Langfuse case study:

> **Candidate Insight #76 (strengthened):** auth-permissive defaults are the rule for new-generation OSS AI/LLM infrastructure platforms (Langfuse, RAGFlow, Flowise, Langfuse, Open WebUI v0.4.x). The rate can be moved by public surveys + upstream maintainer disclosure within 2-3 minor-version cycles, but the unaddressed default holds across major-version transitions in the absence of pressure.

The next survey-disclosure pair (Langfuse v3.176 + RAGFlow v0.21+ post-disclosure) is the test condition.
