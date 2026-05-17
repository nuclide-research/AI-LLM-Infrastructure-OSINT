---
type: synthesis
---

# LLM gateway / proxy population survey, 2026-05-17

_NuClide Research, 2026-05-17 (night pass)_
_Survey #21 in the AI infrastructure series._

---

## Summary

We surveyed the public-facing LLM gateway / API-proxy population: LiteLLM, Helicone, Portkey, OneAPI, NewAPI, OpenRouter self-host. A LLM gateway sits between an application and one or more upstream LLM providers — it brokers requests, holds the operator's OpenAI / Anthropic / DeepSeek API keys, logs every prompt and response, and meters usage.

When an LLM gateway is exposed without authentication, the operator has handed an attacker every prompt their organization has run, every API key the gateway brokers, and (on the OneAPI / NewAPI family) the underlying user account list with quotas.

The population is large and Chinese-operator-dominant.

**Headline numbers:**

- **202 unique OneAPI** instances confirmed.
- **22 unique NewAPI** instances confirmed.
- Every confirmed instance leaks the full deployment-config object at `/api/status` without authentication, including auth-provider flags (OIDC, GitHub OAuth, Lark, email verification), version, and admin-panel URL.
- Most deployments rely on basic password auth (default credential `root / 123456` is documented in the One-API GitHub README; no broad credential testing performed in this survey per restraint).

---

## Hosting and geographic distribution (202 OneAPI / NewAPI hosts)

| ASN | Operator | Hosts |
|---|---|---:|
| AS37963 | Alibaba Cloud (Hangzhou) | 30 |
| AS45102 | Alibaba Cloud (US Technology) | 22 |
| AS20473 | Vultr | 18 |
| AS45090 | Tencent Cloud (CN) | 17 |
| AS132203 | Tencent Cloud (CN, alternate range) | 17 |
| AS22552 | eSited Solutions | 11 |
| AS31898 | Oracle BMC | 9 |
| AS25820 | IT7 Networks (Canada) | 5 |
| AS979 | NetLab Global | 4 |
| AS63949 | Akamai-Linode | 4 |

| Country (WHOIS-resolved) | Hosts |
|---|---:|
| US | 82 |
| CN | 37 |
| AU | 28 |
| SG | 13 |
| HK | 9 |
| CA | 9 |
| NL | 6 |
| MU | 4 |

The US-resolved hosts are mostly Chinese-operator deployments on US-side Alibaba and Vultr — Chinese operators front-running LLM proxy as a commercial service for downstream resellers. A typical operator chain: domestic user pays a Chinese reseller for OpenAI access → the reseller's OneAPI server brokers the user's request to an OpenAI key the reseller pays for → the reseller logs the prompt, charges in credits or RMB.

---

## What `/api/status` leaks

The fingerprint discriminator is also the disclosure surface. `GET /api/status` returns a 200 + JSON for every OneAPI / NewAPI host, without authentication, containing the full deployment config:

```json
{
  "data": {
    "version": "v0.6.11-preview.7",
    "start_time": "1747...",
    "email_verification": false,
    "github_oauth": false,
    "oidc": false,
    "oidc_authorization_endpoint": "",
    "oidc_client_id": "",
    "lark_client_id": "",
    "footer_html": "",
    "logo": "",
    "chat_link": "",
    "display_in_currency": true,
    ...
  }
}
```

This is the unauthenticated-config leak that bridges the survey from "I see a OneAPI server" to "I know the auth posture without trying to log in." It reveals:

- **Version**: feed into CVE tracking. OneAPI < v0.6.x has had multiple disclosed issues; v0.6.11-preview was the current pre-release pin at time of survey.
- **Email verification disabled**: signup is open-by-default unless OAuth is configured (and we see most are not).
- **OIDC + GitHub + Lark all disabled**: deployment relies on basic password auth. The default admin credential is `root / 123456` per upstream docs.
- **Currency display preference**: tells us which operator-region the proxy targets.
- **Start time**: lets a follower-up survey measure uptime tempo.

---

## Threat shape: why an exposed LLM gateway is critical

A typical OneAPI deployment holds:

1. **Upstream API keys** (the operator's paid OpenAI / Anthropic / Gemini / DeepSeek keys). An attacker who gains admin can extract these keys and drain quota.
2. **User accounts** + per-user **API tokens**. The operator's customers each have a key that routes through the proxy; an attacker who reads the user table inherits all of them.
3. **Prompt-and-response logs** for every request the proxy has ever brokered. The proxy's purpose is to log this for billing; once breached, every customer prompt is enumerable.
4. **Quota balances**, which translate directly to fiat-currency theft potential.

Severity ranking: **critical**. Per the auth-on-default thesis ([Insight #13](../../methodology/insight-13-shipping-defaults-load-bearing.md)), an LLM gateway that ships with `root/123456` default and no email-verification requirement guarantees population-scale exposure.

---

## Restraint

We did not attempt password authentication on any OneAPI / NewAPI host. The `/api/status` endpoint is intended to be readable by the browser UI before login; reading it is consistent with the restraint ethic. The version string and auth-config flags are the finding.

We also did not query `/v1/chat/completions` or any other inference endpoint. Inference-routing testing would prove RCE-class quota theft but is outside the survey's metadata-only scope.

---

## Other LLM-gateway products surveyed

| Service | Confirmed hosts | Notes |
|---|---:|---|
| OneAPI | 202 | The dominant population; Chinese-operator-built proxy |
| NewAPI | 22 | Fork of OneAPI; same threat shape; some hosts match both fingerprints |
| Open WebUI | 7 | Coincident matches in this corpus (not a gateway, but ranks AI infra) |
| Langfuse | 5 | Mostly auth-gated; not a disclosure target |
| Dify | 4 | LLM-app platform; ships its own gateway layer |
| Coqui XTTS | 4 | Voice synthesis; coincident match |
| n8n | 3 | Workflow automation; some n8n instances embed LLM keys |
| Grafana | 3 | Coincident |
| dcm4che / dcm4chee-arc | 73 | Insight #22 catchall false positive; honeypot-style baits |
| Docker Registry | 7 | Honeypot bait, same FP class |

LiteLLM, Helicone, Portkey, and OpenRouter all had very small (<10 each) hit counts. Most are deployed behind reverse proxies with auth fronts (Cloudflare Access, oauth2-proxy) and don't expose the underlying service to Shodan-class discovery. The OneAPI / NewAPI corpus dominates because its deployment model is "stick the docker container on a VPS and forward the port directly" — the auth-on-default failure mode lives entirely in operator-deployment hygiene.

---

## Insight reuse

- **Insight #11** (source code is authoritative): the `/api/status` endpoint is a documented upstream feature, not an undisclosed admin path. Reading it requires no exploitation.
- **Insight #13** (shipping defaults are load-bearing): the upstream OneAPI repository ships with `root/123456` default admin login and email-verification-disabled. Every operator who deploys without changing those defaults exposes the same surface.
- **Insight #30** (multi-port honeypot filter): aimap matched OneAPI on 234 (host, port) combinations, but only 202 unique IPs. No host responded as OneAPI on 4+ ports — the corpus is not honeypot-poisoned. This validates Insight #30 working both ways: it confirms honeypots and confirms real services.

---

## Disclosure approach

Per-host disclosure is not viable at this scale. The most useful disclosure here is:

1. **Upstream maintainer (songquanpeng / Calcium-Ion)** with a documentation patch request: ship deployments with email-verification ON by default; require password change on first login; warn admin in the README that `/api/status` is unauthenticated-by-design and operators must put the cluster behind a reverse proxy with auth.
2. **Hosting-provider abuse contacts** (Alibaba, Tencent, Vultr) with batch reports listing the IP cohorts. These can issue per-customer notices internally.

A custom disclosure batch for 200+ individual hosts is not the right tool. Upstream policy + provider-level forwarding is.

---

## Toolchain provenance

```
JAXEN           [x] Shodan harvest across 8 protocol-strict dorks (565 candidates)
aimap v1.9.11   [x] new One API + NewAPI fingerprints; 391 service hits in 1h08m
classifier      [x] Insight #30 multi-port honeypot filter: 0 OneAPI honeypots
visorgraph      [ ] queued — cert-pivot the highest-traffic 20 for operator IDs
visorlog        [ ] queued ingest
nuclide-contact [ ] not run — population-scale disclosure goes upstream, not per-host
```

---

## See also

- [`mcp-server-survey-2026-05-17.md`](mcp-server-survey-2026-05-17.md) — sibling survey, established Insight #30
- [`training-observability-survey-2026-05-17.md`](training-observability-survey-2026-05-17.md) — sibling Adya AI WandB-proxy finding shares the embedded-credential threat shape
- [`../../methodology/insight-13-shipping-defaults-load-bearing.md`](../../methodology/insight-13-shipping-defaults-load-bearing.md)
- [`../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md`](../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md)
