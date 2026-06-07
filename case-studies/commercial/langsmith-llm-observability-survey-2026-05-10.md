---
type: survey
title: LangSmith LLM-observability population survey (27-host self-hosted population)
date: 2026-05-10
class: substrate
category: cross-cloud-survey
status: research-active
methodology: shodan-driven + auth-posture probe + IP-direct-shadow check
---

# LangSmith LLM-observability survey · 2026-05-10

NuClide Research · 2026-05-10

## Summary

Fourth platform in the AI-observability cross-platform sweep. LangSmith is the closed-source SaaS+self-host observability product from LangChain (the same team behind the LangChain framework). Cloud is at `smith.langchain.com`; the self-hosted version is distributed as private Docker images.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, K7051, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

**Population finding: 27 self-hosted LangSmith instances confirmed (of 96 Shodan hits), 100% auth-fronted.** No source-code audit possible. Closed-source. Auth posture confirmed via live probing of `/api/v1/sessions` and `/api/v1/tenants` endpoints, all 27 returned 401 or 403.

The cross-platform pattern after four surveys:

| Platform | Population | Unauth | Unauth rate |
|---|--:|--:|--:|
| **Phoenix** | 377 | 94 | **25%** |
| **Langfuse** | 1,333 | 0 | **0%** |
| **Helicone** | 21 | 0 | **0%** |
| **LangSmith** | 27 | 0 | **0%** |

Phoenix remains the outlier. The 25% unauth rate is a Phoenix-specific shipping behavior, not a class pattern of AI observability platforms.

> **Reproduce with VisorBishop:** `visorbishop -i langsmith-hosts.txt`
> See VisorBishop or `visorplus bishop`.

## Discovery dorks

| Dork | Hits | Used? |
|---|--:|---|
| `http.title:"LangSmith"` | 67 | partial — title only present when fully rendered |
| `http.html:"langsmith"` | **96** | ✓ primary dork |
| `http.html:"\"LangSmith\""` | 96 | duplicate of above |
| `ssl.cert.subject.cn:"langsmith"` | 52 | subset |
| `http.html:"smith.langchain.com"` | 0 | |

Confirmation rate: **96 Shodan hits → 27 actual LangSmith instances (28%).** The other 69 hits are unrelated apps that mention "langsmith" in their HTML (typically as a backend integration: "Welcome to Banking AI API with LangSmith Tracing", "langsmith_configured: true" health endpoints, etc.).

## Population

| Metric | Value |
|---|---|
| Total unique Shodan hits | 96 |
| **Confirmed LangSmith instances** (returned `/api/v1/info` with version+git_sha) | **27** |
| Confirmation rate | 28% |
| Unique IPs (some hosts have HTTP+HTTPS dual-listen) | 24 |
| Unauthenticated on `/api/v1/sessions` | 0 |
| Unauthenticated on `/api/v1/tenants` | 0 |
| Properly auth-fronted | **100% (27/27)** |
| IP-direct-shadow finds | **0** |

**Country distribution:** US 72, DE 7, SG 4, NL 3, GB 3, JP 2, CN 2, FR 1, FI 1, BE 1.

## Information disclosure: `/api/v1/info` unauthenticated by design

LangSmith ships with an unauthenticated `/api/v1/info` endpoint that returns:

```json
{
  "version": "0.13.40",
  "git_sha": "7ed913b583e68d2684b0d7af1c72b5b2ad054639",
  "license_expiration_time": "...",
  ...
}
```

This is not a vulnerability. It's a standard practice for self-hosted enterprise products to expose version info for support diagnostics. But it does enable:

- **Version-targeted vulnerability research**: once a LangSmith CVE is published, attackers can identify affected operators in minutes via this endpoint at population scale.
- **License-expiration-window targeting**: if the response includes license expiry timestamps, attackers can preferentially target instances close to expiry (operator distraction window).
- **Git-SHA correlation**: the git_sha tells attackers the exact build, which maps to specific CI artifacts and dependency versions.

Comparable behavior in this cohort:
- Phoenix: SPA `Config.platformVersion` exposed in inline `<script>` block on the root HTML; same effect.
- Langfuse: `/api/public/health` returns `{status:"OK", version:"3.137.0"}`. Same shape, also unauthenticated.
- Helicone: SPA shadowing makes version probing harder; no documented unauth version endpoint.

LangSmith is the most explicit of the four; version+SHA+license fields are full first-class JSON in a documented endpoint.

## Version distribution (27 confirmed instances)

| Version | Hosts |
|---|--:|
| 0.10.91 | 6 |
| 0.14.4 | 3 |
| 0.12.21 | 3 |
| 0.14.8 | 2 |
| 0.13.40 | 2 |
| 0.12.48 | 2 |
| 0.13.44, 0.13.31, 0.13.28, 0.13.14, 0.12.57, 0.12.35, 0.11.20, 0.10.124, 0.10.116 | 1 each |

Version spread from `0.10.91` (likely Q3 2025) to `0.14.8` (recent). The bimodal distribution at `0.10.91` (6 hosts) and `0.14.x` (5 hosts) suggests two operator cohorts: legacy deployers stuck on 0.10 and recent deployers on the head. The mid-range (0.11-0.13) is widely scattered, consistent with operators updating sporadically.

## Auth posture verification

Two probe endpoints tested, both auth-protected by spec:

| Endpoint | Expected | Observed |
|---|---|---|
| `GET /api/v1/sessions` | 401 if no auth | **27 of 27 returned 401** with body `{"detail":"Invalid token"}` |
| `GET /api/v1/tenants` | 401 or 403 | 13 returned 401, 14 returned 403 (RBAC variance) |

Zero hosts returned 200 on either endpoint. No unauthenticated session enumeration or tenant listing observed.

## IP-direct-shadow sweep

Applying [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md). 11-port nmap sweep against 24 unique LangSmith IPs (NFS, rpcbind, MailCatcher, MailHog, Prometheus, AlertManager, node_exporter, Kibana, Elasticsearch, Grafana, 3000).

**Result: 0 hosts with any of the surveyed ports open.**

This is the cleanest IP-shadow result of the four platforms surveyed. Comparison:

| Platform | IPs probed | Hosts with secondary surface | Critical finds |
|---|--:|--:|--:|
| Phoenix | 92 | 25 (27%) | 5 (NFS+/postgres, MailHog with 139 emails, Kibana, 2× Prometheus) |
| Langfuse | 245 | ~15 (6%) | 1 (localhost-only Prometheus) |
| Helicone | 19 | 2 (11%) | 0 (empty MailHog, login-required Cockpit) |
| **LangSmith** | **24** | **0 (0%)** | **0** |

Interpretation: LangSmith operators run their instances behind cloud load balancers with tight firewall rules. This is consistent with the platform's market positioning (enterprise self-hosted with formal SOC 2 compliance posture and tight LB-fronted networking patterns).

## Operator hints (visible in hostnames)

Most LangSmith IPs are bare cloud IPs (AWS, GCP, Azure) without informative reverse DNS. Notable exceptions:

| IP | Hostname hint | Country |
|---|---|---|
| 49.13.231.179 | `langchain-mcp.xyz` | Germany (Hetzner) |
| 5.11.83.110 | `edu.eval-ai.com` | Germany |
| 46.62.220.30 | `cv.meichin.com` | Germany |
| 188.239.57.162 | `ibizz-ai-core-service-uat.gentech-ai-site.com` | China (Huawei Cloud) |
| 8.137.192.133 | `www.double.ywdcn.com.cn` | China (Alibaba) |
| 88.99.140.96 | `api.talent.connaxis.com` | Germany |

The hostnames don't reveal sensitive operator information beyond confirming the deployment exists. Compare to Langfuse's hostname enumeration which surfaced UK AI Safety Institute, Amazon internal betas, etc.. The LangSmith population is smaller and less attribution-rich.

## Cross-platform synthesis (preliminary, 4 platforms in)

Pattern is stable after four surveys:

- **Phoenix is the only one with auth-off-by-default.** All three other platforms enforce auth as a design constraint.
- **Population size correlates inversely with auth strength.** Phoenix (large + leaky) > Langfuse (large + tight) > LangSmith ≈ Helicone (small + tight). Phoenix's loose default may itself be a population-growth driver: easier to spin up, more operators do, more end up exposed.
- **Information-disclosure endpoints exist in all four.** Version/git_sha/build info is universally available pre-auth across the cohort. This is standard for self-hosted enterprise software but enables population-scale version-targeted exploitation when CVEs land.
- **IP-shadow methodology surfaces operator-side misconfiguration, not platform vulnerabilities.** LangSmith's clean IP-shadow result reflects who deploys it (enterprise infra teams with tight firewalls), not anything LangSmith itself does.

The synthesis hypothesis emerging: **shipping defaults are load-bearing for security posture at population scale, but the operator population a platform attracts is also load-bearing.** Phoenix attracts experimentation-first developers; LangSmith attracts enterprise infra teams. Both effects compound.

## Next steps (research, not disclosure-yet)

1. ~~Shodan harvest~~ ✓ 96 hits, 27 confirmed LangSmith
2. ~~Auth-posture probe~~ ✓ 0 unauth, 100% auth-fronted
3. ~~Version + info-endpoint disclosure check~~ ✓ documented
4. ~~IP-direct-shadow sweep~~ ✓ 0 finds
5. **Lunary, OpenLIT, Pezzo population surveys**, next in the cross-platform sweep
6. **Cross-platform synthesis document**, after Lunary at minimum

## Evidence pack

`~/recon/2026-05-10-llm-sweep/langsmith/`
- `langsmith.json.gz`: Shodan harvest (96 hits)
- `langsmith-hosts.tsv`: deduplicated host list
- `langsmith-info.tsv`: per-host /api/v1/info + sessions + tenants probe results
- `langsmith-confirmed-ips.txt`: 24 unique LangSmith IPs
- `langsmith-ip-shadow.{nmap,gnmap,xml}`: IP-shadow port sweep

Cross-references:
- [phoenix-llm-observability-survey-2026-05-10.md](phoenix-llm-observability-survey-2026-05-10.md)
- [langfuse-llm-observability-survey-2026-05-10.md](langfuse-llm-observability-survey-2026-05-10.md)
- [helicone-llm-observability-survey-2026-05-10.md](helicone-llm-observability-survey-2026-05-10.md)
- [Methodology Insight #12](../../methodology/insight-12-ip-direct-shadow.md)
