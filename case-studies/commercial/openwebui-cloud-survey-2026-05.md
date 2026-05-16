---
type: survey
---

# Open WebUI on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Reused the 20,581 port-3000 hits from the prior Flowise sweep and re-fingerprinted them for **Open WebUI** (the popular Ollama / OpenAI-compatible chat frontend) via `GET /api/version` body match (`{"version":"0.x.x"}`) plus `/api/config` for auth-state + branding. **112 confirmed Open WebUI instances** across DO/Hetzner/Vultr.

In contrast to the vector-DB and inference-server tier, **Open WebUI ships auth-on by default** and operators have largely left it that way: **111 of 112 instances enforce authentication.** This matches the earlier finding for Flowise (43 instances, 0% unauth) and n8n (1006 instances, 0% unauth), orchestration / chat-UI tier is closed-by-default.

The new finding shape is **operator-policy misconfiguration** rather than auth-disabled: **14 of 112 instances have `enable_signup: true`** at the application layer. Authentication is required, but anyone can register an account from the public internet and use the operator's Ollama/OpenAI-compatible backend. Five of those are branded deploys with operator-attributable names ("Aera IA", "TopicalBase AiChat", "Lexa", "Tuuci AI", "CloudU3 AI Platform"), meaning the operator ID is visible in the `/api/config` response.

A side benefit of the survey: branded deployments reveal previously-unmapped commercial AI-chat products that can be cross-referenced for further investigation.

---

## Methodology

```
Reused IPs from prior Flowise port-3000 masscan: 20,581 hosts

openwebui-probe.py (200-thread fingerprint)
  GET /api/version → {"version":"x.y.z"} (Open WebUI shape)
  GET /api/config  → features (auth, signup, ldap, api_keys), name, default_models
  GET /api/models  → model list (gated in newer versions)
  → 201 raw matches → 112 confirmed Open WebUI (via /api/config name + features shape)
```

The 89 raw matches that weren't Open WebUI are other apps with `/api/version` that happen to return JSON with a "version" key, generic Node.js dashboards, custom apps using arbitrary version strings (Unix timestamps, CalVer-style numbers, etc.). Distinguishing was via `/api/config` returning the Open WebUI `features` shape (`auth`, `enable_signup`, `enable_login_form`, `enable_websocket`, etc.).

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 (DO/Hetzner/Vultr) |
| Masscan hits on :3000 | 20,581 |
| Open WebUI confirmed | **112** |
| Authentication required | **111 (99.1%)** |
| Public signup enabled (`enable_signup: true`) | **14** |
| Branded deployments (custom name) | 5 |

### Version distribution (top 10)

| Version | Count |
|---|---|
| 0.8.12 | 22 |
| 0.9.2 | 19 |
| 0.8.10 | 8 |
| 0.7.2 | 8 |
| 0.8.8 | 7 |
| 0.9.1 | 6 |
| 0.6.18 | 5 |
| 0.6.36 | 4 |
| 0.7.1 | 3 |
| 0.6.41 | 3 |

The bulk of the surveyed population is on 0.7.x – 0.9.x, with a long tail going back to 0.3.x. Open WebUI's release cadence is rapid; a meaningful fraction of operators are 6+ minor versions behind, exposing them to whatever security fixes have shipped in the interim.

---

## Class A: Public-Signup Instances (HIGH: anyone-can-register)

`enable_signup: true` in `/api/config` means the chat UI's login page exposes a "Sign up" button that creates a new user account from a public form. Combined with `enable_login_form: true` (also set on these), the registration flow is fully open to the internet. New accounts default to `pending` or `user` role depending on the version + operator config.

If the operator is paying for backend Ollama GPU compute or for OpenAI/Anthropic API quota that the chat UI proxies, every new external account drains that compute/quota.

| Host | Brand name | Version | Hoster |
|---|---|---|---|
| `116.202.111.2` | **Aera IA (Open WebUI)** | 0.8.12 | Hetzner |
| `116.203.143.206` | **TopicalBase AiChat (Open WebUI)** | 0.6.15 | Hetzner |
| `138.68.163.246` | **Lexa** | 3.0 (custom versioning) | DigitalOcean |
| `138.68.45.153` | Open WebUI | 0.9.2 | DigitalOcean |
| `157.90.24.114` | Open WebUI | 0.3.32 | Hetzner |
| `157.90.92.48` | Open WebUI | 0.9.1 | Hetzner |
| `167.71.115.173` | Open WebUI | 0.7.1 | DigitalOcean |
| `168.119.33.246` | Open WebUI | 0.8.11 | Hetzner |
| `206.189.62.253` | Open WebUI | 0.6.18 | DigitalOcean |
| `45.32.169.146` | **Tuuci AI** | 0.9.2 | Vultr |
| `45.76.115.244` | **CloudU3 AI Platform** | 0.3.32 | Vultr |
| `45.76.28.106` | Open WebUI | 0.6.5 | Vultr |
| `65.109.131.165` | Open WebUI | 0.9.2 | Hetzner |
| `65.109.162.107` | Open WebUI | 0.5.7 | Hetzner |

**Risk class:** quota exhaustion / unauthorized usage. An attacker registers, uses the chat UI to query the operator's models freely. For operator-attributed deploys (Aera IA, TopicalBase, Tuuci AI, CloudU3) the operator's brand is also visible to the registering user, likely they think their tooling is more closed than it actually is.

---

## Class B: Branded Deployments (HIGH informational: operator attribution)

Six instances expose a custom brand name in `/api/config.name`, identifying the operator's commercial AI product even where the underlying tech is generic Open WebUI:

| Host | Brand | Notes |
|---|---|---|
| `116.202.111.2` | Aera IA | Hetzner; signup open |
| `116.203.143.206` | TopicalBase AiChat | Hetzner; signup open |
| `168.119.156.118` | ParticulateAI | Hetzner; signup closed |
| `168.119.96.100` | Chatty AI | Hetzner; v4.0.1 (custom versioning, not Open WebUI native) |
| `45.32.184.85` | OdionChat | Vultr; v0.8.7 |
| `135.181.96.47` | Marine AI Knowledgebase | Hetzner; v0.6.2 |
| `108.61.213.116` | DJ AI | Vultr; v0.5.18 |
| `188.166.188.175` + `188.166.235.217` | InsightERA CorpGPT (2 instances) | DO; v1.2.1 (likely fork) |
| `45.32.169.146` | Tuuci AI | Vultr; signup open |
| `45.76.115.244` | CloudU3 AI Platform | Vultr; signup open |
| `138.68.163.246` | Lexa | DO; v3.0 (likely fork) |

The custom-named deploys with non-Open-WebUI version numbers (Lexa v3.0, Chatty AI v4.0.1, InsightERA CorpGPT v1.2.1) are likely **forks of Open WebUI** that have rebased the version string. Whoever maintains those forks may have re-pointed the security defaults too, worth tracking as separate operator entities.

---

## Cross-Survey Pattern (updated)

| Tier | Platform | Sample | Unauth | Default |
|---|---|---|---|---|
| Vector DB | Qdrant | 61 | 100% | auth-off |
| Vector DB | ChromaDB | 48 | 100% | auth-off |
| Vector DB | Milvus | 33 | 100% | RBAC-off |
| Inference | Triton | 2 | 100% | auth-off |
| Inference | vLLM / OpenAI-compat | 44 | 100% | auth-off |
| Orchestration | Flowise | 43 | 0% | auth-on (since CVE-2024-36420) |
| Orchestration | n8n | 1,006 | 0% | auth-on (since v0.166.0) |
| Orchestration | Jupyter | 18 (univ) | 0% | PAM/LDAP standard |
| **Chat UI** | **Open WebUI** | **112** | **0.9% no-auth, 12.5% open-signup** | **auth-on** |

The pattern crystallizes: **the data and inference tiers ship unauthenticated and operators don't fix it; the orchestration and chat-UI tiers ship authenticated and operators leave that default in place.** The shift between layers is sharp. Open WebUI fits the orchestration/UI pattern, auth defaults are respected, but introduces a *new* failure mode (open-signup misconfiguration) that doesn't exist for headless backend services.

---

## Remediation

For Open WebUI operators with public signup unintentionally enabled:

```yaml
# docker-compose.yml - environment variables to set
environment:
  - ENABLE_SIGNUP=False              # disable public registration
  - DEFAULT_USER_ROLE=pending        # new users require admin approval
  - WEBUI_AUTH=True                  # ensure auth is on (default)
  # optional: restrict signup by allowed-domain
  - WEBUI_SIGNUP_ALLOWED_DOMAINS=yourcompany.com
```

For operators on old Open WebUI versions (0.3.x – 0.6.x): upgrade to current 0.9.x. The release notes from 0.6 → 0.9 include several auth/permission improvements.

Branded-fork operators (Lexa, Chatty AI, InsightERA CorpGPT): cross-check that fork upstream has merged Open WebUI's recent auth-related fixes.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | Reused 20,581 port-3000 IPs from flowise-cloud-survey-2026-05 |
| Fingerprint | `openwebui-probe.py`, `/api/version` shape + `/api/config` features |
| Findings ledger | To be ingested into `data/nuclide.db` |
| What was NOT done | No account registration attempted; no `/api/v1/auths/signup` POSTs; no usage of operator's Ollama/OpenAI-compat backend |

---

## Cross-Referenced Survey: Marqo (port 8882): Zero Confirmed

A parallel masscan of port 8882 (Marqo's default) across the same 28 cloud /16 ranges produced 2,952 hits, but `/indexes` probes against those hits returned zero confirmed Marqo instances. Sample-host inspection of the surface revealed:

- ~80% of hits time out on TCP HTTP probes (TCP-open at masscan layer but RST/drop on actual HTTP)
- Detected honeypot signatures on at least one (`Server: 360 web server`, TELDAT, A10WS, characteristic T-Pot vector-DB-honeypot fake)

Marqo as a self-hosted product is **rare on cheap cloud VPSes**, the vast majority of Marqo deployments are either Marqo Cloud (managed) or behind reverse proxies that hide port 8882 from the public internet. No Marqo findings to report.

---

## References

- Open WebUI auth configuration: https://docs.openwebui.com/getting-started/env-configuration#authentication
- Open WebUI release notes: https://github.com/open-webui/open-webui/releases
- Cross-survey index: [index.md](index.md)
