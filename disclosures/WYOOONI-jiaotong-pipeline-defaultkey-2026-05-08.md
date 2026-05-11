---
to: admin@wyoooni.net
cc: domain@oray.com
severity: CRITICAL
ip: 139.196.198.169
institution: "wyoooni.net (睿尚ERP, Guangdong CN) — OpenWebUI Pipelines service on 139.196.198.169:8081 accepts the factory-default API key 0p3n-w3bu!, granting full pipeline admin access to LangGraph Agent 交大-销售助手; n8n workflow automation at agent.wyoooni.net authenticated via same domain"
status: SENT
outcome: sent
date: 2026-05-08
---

**To:** admin@wyoooni.net
**Cc:** domain@oray.com (Oray/花生壳 registrar abuse)
**Subject:** wyoooni.net (139.196.198.169) — CRITICAL: LangGraph pipeline service using factory-default API key — full pipeline admin access exposed

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
2026-05-08

This is an unsolicited good-faith coordinated-disclosure notification. I was unable to find a security contact for wyoooni.net, so I am reaching admin@wyoooni.net. Please forward to your system administrator immediately.

---

## Executive Summary / 摘要

The LangGraph pipeline service running on `139.196.198.169:8081` is accepting the **factory-default API key `0p3n-w3bu!`** for full administrative access. This is a known default credential shipped by the OpenWebUI Pipelines project — any attacker who knows this default (it is publicly documented) can:

- Enumerate all pipelines, including the 交大-销售助手 (Jiaotong Sales Assistant) agent
- Read and modify pipeline valve parameters (temperature, max_tokens, debug mode)
- Upload new pipelines or replace the existing LangGraph agent with a malicious one
- Intercept or manipulate all queries routed through the sales assistant

---

## Technical Finding

**Service:** LangGraph Pipelines Service v1.0.0
**Host:** `139.196.198.169:8081` (Alibaba Cloud, CN)
**Domain:** `wyoooni.net` / `agent.wyoooni.net`

**Proof (default key still accepted as of 2026-05-08 05:11 UTC):**

```
$ curl -s http://139.196.198.169:8081/
{"service":"LangGraph Pipelines Service","version":"1.0.0","pipeline_id":"交大-销售助手"}
date: Fri, 08 May 2026 01:04:10 GMT

$ curl -s -H "Authorization: Bearer 0p3n-w3bu!" \
    http://139.196.198.169:8081/pipelines
{"pipelines":[{
  "id":"交大-销售助手",
  "name":"LangGraph Agent",
  "type":"pipe",
  "description":"LangGraph Agent - 集成三个模块的智能路由系统"
}]}

$ curl -s -H "Authorization: Bearer 0p3n-w3bu!" \
    http://139.196.198.169:8081/交大-销售助手/valves
{"max_tokens":2048,"temperature":0.7,"debug":false}
```

The `0p3n-w3bu!` key is the well-known default credential for the OpenWebUI Pipelines project and is documented publicly. It is not a secret NuClide discovered — it is a factory default that was never rotated.

**n8n workflow automation:** `agent.wyoooni.net` serves an n8n instance (nginx reverse proxy). The `/rest/settings` endpoint is publicly accessible (no auth required) and confirms the SSO OIDC configuration. n8n workflow execution appears to require authentication; however the public settings endpoint leaks the OIDC login URL and authentication configuration details.

---

## Impact

**Pipeline hijacking:** An attacker can call `/交大-销售助手/valves/update` with the default key to change pipeline parameters (or upload a replacement pipeline via the `/pipelines/upload` endpoint if implemented). This allows injecting malicious system prompts or rerouting queries to an attacker-controlled LLM — a direct supply-chain attack on every conversation handled by the sales assistant.

**Query interception:** If the pipeline proxies user queries to an LLM, any party with the default key can observe or modify those queries and responses in real time.

**Reconnaissance:** The publicly accessible `/v1/models` endpoint enumerates the internal pipeline IDs and model configuration, aiding further targeting.

---

## Recommendation

**Immediate (within hours):**
1. **Change the API key.** Replace `0p3n-w3bu!` in the pipeline server configuration with a randomly generated secret (e.g., `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`). This is the only action needed to close the primary attack vector.
2. **Firewall port 8081 from the public internet.** The pipeline service is an internal component and should only be reachable from the OpenWebUI frontend or localhost. A firewall rule restricting `:8081` to `127.0.0.1` or the OpenWebUI host IP eliminates the attack surface entirely.

**Within a few days:**
3. **Review n8n public settings exposure.** Restrict `/rest/settings` to authenticated users or firewall the n8n port similarly.
4. **Audit pipeline logs** for any unexpected API calls using the default key during the exposure window.

---

## Evidence Preservation

Evidence bundle preserved locally with SHA-256 manifest, server-asserted `Date:` headers from every HTTP capture, and OpenTimestamps receipt. Bundle available on request; not published pending your remediation.

---

## IOCs

| Type | Value |
|---|---|
| Affected host | `139.196.198.169` (Alibaba Cloud CN) |
| Domain | `wyoooni.net`, `agent.wyoooni.net` |
| Exposed port | `8081` (LangGraph Pipelines Service) |
| Default credential | `Authorization: Bearer 0p3n-w3bu!` |
| Pipeline ID | `交大-销售助手` |
| Confirmed live | Fri, 08 May 2026 05:11:16 GMT |

---

## Reference

- OpenWebUI Pipelines default API key issue: <https://github.com/open-webui/pipelines>
- OpenWebUI security configuration: <https://docs.openwebui.com/getting-started/advanced-topics/env-configuration>

---

Regards,
Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
https://nuclide-research.com
AI-LLM-Infrastructure-OSINT
