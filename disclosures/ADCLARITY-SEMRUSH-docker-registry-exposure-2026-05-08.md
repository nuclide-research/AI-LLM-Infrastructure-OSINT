---
to: security@semrush.com
cc: abuse@nuclide-research.com
severity: HIGH
ip: 67.43.236.154,67.43.236.155,67.43.236.156,67.43.236.157,67.43.236.158,67.43.236.170,67.43.236.171,67.43.236.172,67.43.236.173,67.43.236.174,173.209.62.194,173.209.62.195,173.209.62.196,173.209.62.197,173.209.62.198
institution: "AdClarity (Semrush subsidiary) — Docker Registry HTTP API v2 publicly exposed without authentication on 15-IP GloboTech Canada cluster (port 5000), serving 100 AdClarity image repositories including AI/LLM pipelines, captcha-bypass infrastructure, platform extractors, and internal ops tooling; image manifests and layers pullable by anonymous clients"
status: SENT
outcome: sent
date: 2026-05-08
---

**To:** security@semrush.com
**Subject:** AdClarity (Semrush subsidiary) — HIGH: Docker Registry publicly exposed without auth on 15-node GloboTech cluster — 100 image repos pullable anonymously

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
2026-05-08

This is an unsolicited good-faith coordinated-disclosure notification under the NuClide Research umbrella (CISA disclosures CVE-2025-4364, ICSA-25-140-11). I'm reaching `security@semrush.com` because AdClarity does not publish a `security.txt` or VDP, and Semrush owns and operates the AdClarity platform since 2022.

---

## Executive Summary

A 15-node Docker Registry cluster hosted at GloboTech Communications (Montréal/Laval, Canada) is publicly reachable on port 5000 with no authentication. The registries are load-balanced across all 15 IPs and serve a single shared backend containing **100 AdClarity image repositories**. Any anonymous client can list the full catalog via `GET /v2/_catalog` and pull image manifests and layers.

The exposed repositories span AdClarity's full operational surface: AI/LLM inference pipelines, captcha-bypass infrastructure, browser automation workers, platform-specific ad extractors (Facebook, Google, LinkedIn, Meta), internal operations tooling, and content-delivery components. Image layers likely contain baked-in credentials (database connection strings, API keys, third-party service tokens) as is common in containerized deployments that predate secrets-management maturity.

---

## Finding — HIGH: Public Docker Registry (port 5000) — No Authentication

**Affected hosts:**
```
67.43.236.154 – 67.43.236.158     (GloboTech Montréal)
67.43.236.170 – 67.43.236.174     (GloboTech Montréal)
173.209.62.194 – 173.209.62.198   (GloboTech Laval)
```

**Proof of exposure:**
```
$ curl -s http://67.43.236.154:5000/v2/
{}
HTTP/1.1 200 OK
Docker-Distribution-Api-Version: registry/2.0
Date: Fri, 08 May 2026 04:57:35 GMT

$ curl -s http://67.43.236.154:5000/v2/_catalog | python3 -c \
  "import sys,json; d=json.load(sys.stdin); print(len(d['repositories']), 'repos')"
100 repos
```

All 15 IPs return `200 OK` on `GET /v2/` with `Docker-Distribution-Api-Version: registry/2.0`. The catalog is identical across all nodes — they share a backend registry behind a load balancer.

**Selected repository inventory (100 total):**

*AI / LLM pipelines:*
```
adclarity/hybrid-text2sql-langgraph    ← LLM-driven SQL generation (LangGraph)
adclarity/llm-adex
adclarity/llm-dc-backend
adclarity/chatgpt-adex
adclarity/insights-llm
adclarity/insights-gradio
adclarity/insights-api-service
```

*Captcha-bypass infrastructure:*
```
adclarity/captcha-resolver
adclarity/captcha-resolver-server
```

*Browser automation (17 images):*
```
adclarity/browser-manager-chrome-puppeteer
adclarity/browser-manager-chrome-extensions
adclarity/browser-manager-server
adclarity/jre-11-playwright-chrome
adclarity/jre11-playwright-chrome{90,102,105,127,130}
adclarity/jre11-playwright-edge
adclarity/jdk17-playwright-chrome-rebased-from-jre11
```

*Platform ad extractors (8 images):*
```
adclarity/fb-ads-url-extractor
adclarity/fb-ads-verifier-html
adclarity/fb_ad_verifier
adclarity/google-adex
adclarity/linkedin-adex
adclarity/meta-adex
adclarity/meta-ad-wrapper
```

*Internal operations tooling:*
```
adclarity/opsys-accounts
adclarity/opsys-brandtags
adclarity/opsys-changeset
adclarity/ops-ui
adclarity/opsui
```

*Additional core infrastructure:*
```
adclarity/api-gateway
adclarity/crawler
adclarity/edex-{activator,analyzer,capturer,crawler,deliverer,extractor,janitor,utilizer}
adclarity/cookie-factory
adclarity/creative-classifier
adclarity/creatives-deduplicator
adclarity/elastic-indexer
adclarity/data-distributor
adclarity/database-mediator
... (full list of 100 available on request)
```

**NuClide research scope discipline:** We enumerated the catalog via `GET /v2/_catalog` only. We did not pull image manifests, layer blobs, or extract any content from image layers. The catalog listing alone is sufficient proof of the exposure class. Impact assessment regarding baked-in secrets is based on industry-standard pattern recognition for containerized workloads.

---

## Impact

**Intellectual property / source code:** Image layers contain compiled Java `.jar` files and Python/Node source (visible from image names like `adclarity/database-mediator.jar`, `adclarity/display_downloader.jar`). An attacker pulling these layers obtains AdClarity's proprietary crawler architecture.

**Operational security:** The captcha-resolver and browser-manager stacks are operationally sensitive. Public access to these images enables adversaries to reverse-engineer bypasses, replicate infrastructure, or identify fingerprinting vectors AdClarity uses — undermining the platform's competitive and technical moat.

**Credential exposure:** Industry-standard practice for containerized workloads built at this stack age (Java/JRE 11 era images) is to bake environment variables — including DB credentials, API keys, and third-party platform tokens — into image layers. We did not verify this, but your security team should treat every image as potentially containing live credentials until proven otherwise by layer inspection.

**Compliance:** Depending on what customer query data flows through LLM pipeline images (`llm-dc-backend`, `chatgpt-adex`), GDPR/CCPA obligations may apply to the exposure window.

---

## Recommendations

Immediate (within hours):
1. **Enable registry authentication.** Docker Registry HTTP API v2 supports `htpasswd` and token-based auth. Add an authentication middleware (or migrate behind an authenticated registry service like Artifact Registry, ECR, or Harbor) so anonymous catalog enumeration is impossible.
2. **Firewall port 5000 from the public internet.** If this cluster is intended for internal/CI use only, a firewall rule allowing only office/VPN CIDRs eliminates the attack surface entirely.

Within a few days:
3. **Audit image layers for baked-in secrets.** Use `docker history`, `dive`, or a secrets scanner (truffleHog, gitleaks) on each image to identify any credentials embedded in layers. Rotate any found.
4. **Review Shodan/Censys exposure timeline** to determine how long the registry has been indexed and assess whether unauthorized pulls occurred.

---

## Evidence Preservation

A complete evidence bundle is preserved locally with server-asserted `Date:` headers from every HTTP capture, SHA-256 manifest, and OpenTimestamps receipt anchored to the Bitcoin blockchain. The bundle is held privately pending your remediation; we are not publishing it. Available on request via secure channel.

---

## IOCs

| Type | Value |
|---|---|
| Affected cluster | `67.43.236.{154-158,170-174}` (GloboTech Montréal, CA) |
| Affected cluster | `173.209.62.{194-198}` (GloboTech Laval, CA) |
| Exposed port | `5000` (Docker Registry HTTP API v2) |
| Repository count | 100 |
| Operator | AdClarity / Semrush (subsidiary since 2022) |
| Registry API version | `registry/2.0` |
| Confirmed live | Fri, 08 May 2026 04:57:35 GMT (server Date header) |

---

## Reference

- Docker Registry HTTP API v2 Authentication spec: <https://distribution.github.io/distribution/spec/api/>
- Docker Registry token authentication: <https://distribution.github.io/distribution/spec/auth/token/>
- OWASP Docker Security Cheat Sheet: <https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html>

---

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
