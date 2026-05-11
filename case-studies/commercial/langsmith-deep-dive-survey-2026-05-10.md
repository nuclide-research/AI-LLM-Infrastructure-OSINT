---
title: LangSmith deep-dive — Phase 2 (customer identity disclosure on 19 enterprise operators)
date: 2026-05-10
class: substrate
category: platform-deep-dive
status: research-active
methodology: probe-based audit (closed-source) + extended IP-shadow
---

# LangSmith deep-dive · 2026-05-10 (Phase 2)

NuClide Research · 2026-05-10

## Summary

Phase 2 of LangSmith. Closed-source platform (Docker-images-only distribution from LangChain), so no source-level audit. Phase 1 found 27 confirmed self-hosted instances, all auth-fronted on `/api/v1/sessions` and `/api/v1/tenants`.

Phase 2 dug into the unauthenticated `/api/v1/info` endpoint that we flagged as "information disclosure by design" in Phase 1. **It discloses materially more than expected.**

**Key finding: `/api/v1/info` returns the operator's full enterprise customer identity** — `customer_name`, `customer_id` (UUID), `license_expiration_time`, and the complete `instance_flags` configuration. **19 of 27 instances disclose recognizable enterprise customer names**, including Grammarly, ByteDance, Generali, Rakuten, National Bank of Greece, University of Michigan, RealPage, Pigment (5 instances), and Lockton.

This is the highest-impact information disclosure surfaced across the entire observability tier cohort. It's not a data leak — but it's a **customer-identity leak** that turns the 27-host LangSmith population into a public roster of enterprise AI deployments.

> **Reproduce with VisorBishop:** `visorbishop -i langsmith-confirmed-ips.txt -ip-shadow`
> See VisorBishop or `visorplus bishop`.

## The `/api/v1/info` finding

Every LangSmith self-hosted instance exposes `/api/v1/info` without authentication. Sample response from `http://98.90.221.236:80`:

```json
{
  "version": "0.13.40",
  "git_sha": "7ed913b583e68d2684b0d7af1c72b5b2ad054639",
  "license_expiration_time": "2026-11-27T00:00:00Z",
  "customer_info": {
    "customer_id": "0e8ff24b-1ac1-4a5c-b976-49d0658b81a6",
    "customer_name": "Grammarly"
  },
  "instance_flags": {
    "playground_auth_bypass_enabled": true,
    "self_hosted_jit_provisioning_enabled": true,
    "phone_home_enabled": true,
    ...
  },
  "batch_ingest_config": { ... }
}
```

The `customer_info` block was unexpected in Phase 1 (Phase 1 read only `version` + `git_sha` + `license_expiration_time`). Phase 2 confirms it's present on the majority of instances.

## Enterprise customers disclosed across the 27 confirmed instances

| Customer | Instances | Sector | Geo |
|---|--:|---|---|
| **Pigment** | 5 | FinTech / corporate financial planning | EU/US |
| **Generali** | 3 | Insurance (Fortune Global 500) | IT/EU |
| **Grammarly** | 2 | Tech / AI writing | US |
| **Weber Shandwick** | 1 | Marketing / PR | US |
| **Turing — applied AI** | 1 | AI/ML | US |
| **ByteDance** | 1 | Tech (TikTok parent) | CN/global |
| **University of Michigan** | 1 | Academia | US |
| **Lockton** | 1 | Insurance brokerage | US |
| **Rakuten** | 1 | E-commerce | JP/global |
| **RealPage Inc** | 1 | Real estate software | US |
| **National Bank of Greece** | 1 | Banking | GR |
| **P-1.ai** | 1 | AI | (unknown) |
| (no customer_info) | 8 | — | — |

**Total: 19 identifiable enterprise customers across 27 instances.**

The 8 instances without `customer_info` are mostly on v0.10.91 — an older LangSmith version that may not have included the field. The 8 with no name use license_expiration_time `2026-12-31` (suggesting a default trial/eval license).

License expiration windows are visible too — they cluster around quarter-ends, suggesting renewal cycles. Pigment's 5 instances all renew 2026-08-27; Generali's 3 all renew 2026-09-15.

## Threat model: customer-identity disclosure

Why this matters:

1. **Targeted attacks become trivial to scope.** A LangSmith CVE published tomorrow can be matched to "Grammarly, ByteDance, NBG, University of Michigan" within minutes. Threat actors targeting any of these orgs can pivot to their LangSmith infrastructure first.
2. **Vendor-target chain disclosure.** Knowing Grammarly runs LangSmith means a LangSmith breach is material to Grammarly. Vice versa: a Grammarly compromise can pivot through LangSmith to other customers if shared infrastructure exists.
3. **License-expiration targeting.** Operators close to license renewal often have less rigorous monitoring during transition periods. License expiration data is visible per-customer.
4. **Cross-correlation with leaked breach datasets.** If any of these enterprises appears in a future breach lookup, the LangSmith trace store becomes a high-value follow-on target.
5. **Competitive intelligence.** Pigment running 5 LangSmith instances is visible business intelligence about their AI deployment scale.

This is **not** a Phoenix-class data leak — no LLM traces or prompts leak. But the customer-identity disclosure has unique compounding effects: **the very fact that an enterprise has a public-internet-reachable LangSmith self-host is operational intelligence about that enterprise's AI program.**

## What we didn't probe

The `instance_flags` block surfaces several intriguing properties that we did **not** active-probe:

- **`playground_auth_bypass_enabled: true`** on 27/27 instances. Probing `/playground`, `/api/v1/runs/playground`, `/auth/playground` returned 401 / Next.js SPA HTML / 404. Without source access, the actual bypass behavior isn't clear. Could be a UI-only feature (the LangSmith playground page calls its own backend with a service-account token), or could be a way for unauthed users to send traces under a "playground" session ID.
- **`self_hosted_jit_provisioning_enabled: true`** on 18/27. JIT (just-in-time) user provisioning — operators use SSO-based account creation. Not directly exploitable; signals operator config.
- **`phone_home_enabled: true`** on 9/27. The self-hosted instance reports telemetry to LangChain's central servers. Worth noting for operators with strict data-residency requirements: even self-hosted LangSmith calls home on some configurations.

These probes are non-destructive metadata reads, not exploitation attempts. The `playground_auth_bypass` warrants source-level inspection if LangSmith opens up; closed-source today.

## Cross-version posture

Version distribution from Phase 1 (re-stated):

| Version | Instances |
|---|--:|
| 0.10.91 | 6 |
| 0.14.4 | 3 |
| 0.12.21 | 3 |
| 0.14.8 | 2 |
| 0.13.40 | 2 |
| 0.12.48 | 2 |
| (10 versions × 1 each) | 9 |

Range: `0.10.91` (Q3 2025) to `0.14.8` (recent). Auth posture is consistent across versions. The customer_info disclosure appears in v0.11+; v0.10.x instances (7 of 8 "no customer_info" hosts) don't include the field, suggesting it was added in v0.11.

The 6 instances on v0.10.91 are all stale — they've been running unupdated since at least late 2025. Pre-CVE-window risk: if a critical LangSmith CVE drops in 2026, v0.10.91 operators are months behind.

## Extended IP-direct-shadow sweep

17-port nmap sweep across the 24 unique LangSmith IPs (NFS, rpcbind, MailHog, MailCatcher, Prometheus, AlertManager, node_exporter, Kibana, Elasticsearch, Grafana, Postgres, Redis, ClickHouse, MongoDB, MySQL, statsd, alt-web).

**Result: 0 hosts with any of the surveyed ports open.**

This is the cleanest IP-shadow result across all platforms surveyed. Even with the extended port set (databases + caches), LangSmith operators show 0 co-located services exposed.

Interpretation: LangSmith is sold and deployed by enterprise infrastructure teams. Network firewalls, LB-fronted ingress, and tight egress are standard. The customer roster matches: Grammarly, ByteDance, Generali, National Bank of Greece — these are organizations with mature security operations. Their LangSmith deployments reflect that.

| Platform | IPs probed | IP-shadow finds | Critical |
|---|--:|--:|--:|
| Phoenix | 92 | 25 | 5 |
| Langfuse | 381 | ~18 | 2 (5 Postgres, 1 unauth Prom) |
| Helicone | 19 | 4 | 1 (unauth ClickHouse) |
| **LangSmith** | **24** | **0** | **0** |
| Lunary + OpenLIT + Pezzo | 30 | 1 | 1 (unauth node_exporter) |

LangSmith's IP-shadow is genuinely empty. The only LangSmith exposure surfaced in this entire research chain is the `/api/v1/info` customer-identity disclosure — which is platform behavior, not operator misconfiguration.

## Comparison vs Phoenix and Langfuse Phase 2

| Vector | Phoenix | Langfuse | LangSmith |
|---|---|---|---|
| Default auth state | `False` (94 unauth) | mandatory | mandatory |
| Default secrets in `.env.example` | n/a | `NEXTAUTH_SECRET="secret"` + `SALT="salt"` + `ENCRYPTION_KEY="0"*64` | (closed source) |
| Customer identity exposed pre-auth | no | no | **YES — 19/27 enterprises named** |
| IP-shadow secondary surfaces | 27% of unauth hosts | 6% | 0% |
| Database direct-exposure | 1 NFS+postgres | 5 Postgres | 0 |
| Operator class | mixed (research, SaaS, enterprise) | mixed (enterprise heavy) | enterprise only |

LangSmith's per-instance defensive posture is the strongest in the cohort. Its **platform-level information disclosure** (customer roster) is the worst. The threat models are different in kind: Phoenix's failure is "data leaks at population scale"; LangSmith's is "your customer list is public."

## Operator clustering

The `customer_info.customer_name` field is the per-instance attribution oracle. Cross-instance clustering by customer_name surfaces multi-host operators:

- **Pigment** runs 5 instances across versions 0.14.4 (×3) and 0.14.8 (×2). All license-expire 2026-08-27. Same license, same customer, multiple HA replicas or environment tiers.
- **Generali** runs 3 instances all v0.12.21 with same expiry. Likely HA cluster.
- **Grammarly** runs 2 instances both v0.13.40 with same expiry. Likely failover pair.

Phoenix's project-name clustering surfaced 4 multi-host operators; LangSmith's `customer_name` is a much more reliable signal (no naming ambiguity, no project-noise).

## What's NOT a finding

- **The `playground_auth_bypass_enabled` flag**: visible but doesn't translate to unauth access via probed paths. Closed-source means we can't fully verify, but standard endpoints reject playground-tagged unauth requests.
- **`phone_home_enabled=true` on 9 instances**: not a vulnerability — LangChain ships telemetry to their cloud, which is documented behavior.
- **The 8 instances without `customer_info`**: most are v0.10.91 where the field didn't exist yet. Not a hidden-customer pattern, just version skew.

## Next steps (research, not disclosure-yet)

1. ~~Phase 2 metadata probe~~ ✓ — `/api/v1/info` customer-identity disclosure documented
2. ~~Extended IP-direct-shadow~~ ✓ — 0 finds
3. ~~Cross-version posture~~ ✓
4. ~~Operator clustering via customer_name~~ ✓ — Pigment, Generali, Grammarly multi-instance
5. **Phase 3 meta-fingerprinter** — incorporate `/api/v1/info` customer-name detection as a fingerprint signal; enables one-call "is this an enterprise LangSmith deployment?" check
6. **Methodology Insight candidate**: "Unauthenticated info endpoints leak more than version strings — check for customer/license/feature-flag fields too."

## Evidence pack

`~/recon/2026-05-10-llm-sweep/langsmith/`
- All Phase 1 artifacts (host list, info-probe results, IP-shadow)
- `langsmith-info-detail.json` — full /api/v1/info dump from all 27 instances (customer names, license dates, instance flags, batch config)
- `langsmith-deep-shadow.{nmap,gnmap,xml}` — extended 17-port sweep across 24 IPs

Cross-references:
- [langsmith-llm-observability-survey-2026-05-10.md](langsmith-llm-observability-survey-2026-05-10.md) (Phase 1)
- [SYNTHESIS-ai-observability-2026-05-10.md](SYNTHESIS-ai-observability-2026-05-10.md)
- [langfuse-deep-dive-survey-2026-05-10.md](langfuse-deep-dive-survey-2026-05-10.md)
- [helicone-deep-dive-survey-2026-05-10.md](helicone-deep-dive-survey-2026-05-10.md)
