# DCWF Custom Outfits (Wardrobe-built)

Custom DCWF outfits assembled from `~/wardrobe` (1,281 NICE Cybersecurity Workforce
Framework atoms across 39 work-role pathways). Each outfit hand-picks atoms
across roles to produce a lean operating posture for a specific NuClide lane.

Each `.json` is a wardrobe outfit definition (try-on into wardrobe to use, render
as LLM prompt). Each `.md` is the pre-rendered LLM system prompt suitable for
agent dispatch.

## LJP-OSS Cohort Investigation (2026-06-09)

| Outfit | DCWF base roles | Lane |
|---|---|---|
| `config-attribution-audit-612` | 612 SCA | OAuth, email-whitelist, cookie SSO attribution |
| `endpoint-enumeration-541` | 541 VAA | CSP, security.txt, /api/system/config enum |
| `idp-branding-attribution-221` | 221 CCI + 212 Forensics | OIDC discovery + Open Graph meta attribution |
| `jsbundle-ws-deep-analysis-661` | 661 R&D + 511 CDA | JS source maps + WebSocket endpoint mining |
| `discovery-scale-up-422` | 422 Data Analyst | Multi-source enumeration (favicon, CT, GitHub, HackerTarget) |
| `per-ip-investigation-harness-621-671` | 621 SW Dev + 671 T&E | Build cohort-harness.py + run aimap/herald per host |
| `threat-scoring-synthesis-511-612` | 511 CDA + 612 SCA | Final per-IP threat score + cohort synthesis |

## Re-use pattern

```bash
# Load any outfit into wardrobe to inspect, edit, or render
wardrobe load discovery-scale-up-422
wardrobe outfit
wardrobe render --as prompt > /tmp/agent-prompt.md

# Or feed the pre-rendered .md directly to an agent dispatch
```

## Provenance

Outfits built 2026-06-09 by Nick + Claude during the Chinese LLM-Jacking
Productized OSS Proxy cohort investigation (Cat-XX, Insight #79). Reusable for
any future cohort investigation that needs the same lane assignments.
