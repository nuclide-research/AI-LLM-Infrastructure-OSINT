# OSINT Platoon SALUTE -- 13.68.189.140:8000 (Galileo agent-control)
# Cat-33 AI Agent Guardrails | 2026-06-23

---

## S -- SIZE

Single instance. 13.68.189.140:8000. One agent registered (customer-support-agent). 5 controls configured, 0 active. 4 tools exposed. Agent created 2026-06-20T05:00:50 UTC. v0.1.0 first release build.

---

## A -- ACTIVITY

Service live and serving requests. Shodan-indexed. Next.js SPA frontend loading. API responding on /api/config, /api/v1/agents, /api/v1/controls, /api/v1/controls/{1-5}/data. Static bundle Last-Modified 2026-03-12 (initial release, no updates deployed). No active sessions (has_active_session: false). No authentication active.

---

## L -- LOCATION

Microsoft Azure East US. Boydton, Virginia 23917. AS8075. NET-13-64-0-0-1. IP ephemeral Azure allocation. No PTR for entire /28. No domain associated. Bare IP deployment.

---

## U -- UNIT (operator attribution)

Software: Galileo AI / agentcontrol/agent-control (Apache 2.0, launched 2026-03-11, 267 stars). Docker image: galileoai/agent-control-server:latest. PostgreSQL default creds in docker-compose.

Operator: Unknown external developer. Tool set matches AWS AgentCore customer-support blueprint (awslabs/agentcore-samples) more closely than Galileo's own stock template. Operator raised process_refund cap from $100 (AWS example) to $200, deployed on Azure instead of AWS, and disabled all 5 policy controls.

Galileo principals for disclosure: Yash Sheth (CTO), Vikram Chatterji (CEO), Lev Neiman (staff engineer, agent-control lead). Post-acquisition by Cisco (2026-04-09), routes to Cisco/Splunk Observability security.

---

## T -- TIME

Agent deployed: 2026-06-20T05:00:50 UTC. Shodan first-seen: ~2026-06-20 (3 days before discovery). Static build timestamp: 2026-03-12 (same day as Galileo's initial release -- operator pulled the release build directly, no updates since). Product announced: 2026-03-11. Cisco acquisition announced: 2026-04-09.

---

## E -- EQUIPMENT / FINDINGS

### Finding 1 (HIGH) -- All guardrails disabled, control plane fully exposed

  Auth:    NONE (requires_api_key: false, auth_mode: "none")
  Surface: /api/config, /api/v1/agents, /api/v1/controls, /api/v1/controls/{1-5}/data
  Write:   POST /api/policy, DELETE /api/v1/controls/{id} -- unauthenticated

  5 controls, all enabled: false:
    block-prompt-injection -- injection regex exposed (bypass recipe public)
    block-internal-data    -- financial internals (margins, COGS, fraud flags) unguarded
    block-pii              -- SSN pattern (\d{3}-\d{2}-\d{4}); lookup_customer returns SSNs
    block-competitor-discuss -- minor business policy, disabled
    max-refund-amount      -- $200 cap on process_refund, not enforced

  4 tools: get_order_status, lookup_customer (SSN surface), get_order_internal (financial internals), process_refund

  Agent description: "Customer support agent with Agent Control runtime guardrails" -- INACCURATE. No guardrails enforced.

### Key secondary (infra) -- attribution ceiling is application layer only

  No domain, no TLS, no PTR. SSH key not reused. Attribution stops at Galileo software + Azure East US region.

---

## INTELLIGENCE GAPS

- Operator identity: not attributable via IP/cert/DNS. Could be Galileo internal test, third-party evaluator, or customer pilot.
- Contents of lookup_customer response: not pulled (restraint ethic). SSN presence inferred from block-pii regex pattern, not confirmed.
- Contents of get_order_internal response: not pulled. Financial field names inferred from block-internal-data regex pattern.
- Whether controls are disabled by configuration (operator intent) or default behavior (product default): both. AGENT_CONTROL_API_KEY_ENABLED=false is the product default. Control enabled: false is likely set during agent registration workflow.

---

## OSINT Platoon squad status

  [x] Alpha (web OSINT)   -- Galileo Technologies attribution, Cisco acquisition, auth-off documented
  [x] Bravo (infra/cert)  -- Azure East US confirmed, /28 no PTR, SSH key, cert CT = 0
  [x] Charlie (social)    -- Principal identities, operator template analysis, AWS AgentCore blueprint match
  [x] Weapons (docs/code) -- Full upstream API surface, Docker creds, default PostgreSQL creds

