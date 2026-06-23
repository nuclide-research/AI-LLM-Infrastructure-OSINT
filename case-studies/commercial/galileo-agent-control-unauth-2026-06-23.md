---
category: cat-33-ai-email-guardrails
date: 2026-06-23
host: 13.68.189.140
port: 8000
service: Galileo agent-control
version: "0.1.0"
severity: high
cloud: Azure East US (AS8075)
verification: "inner-B / outer-1"
deployed: "~2026-06-20 (3 days old at discovery)"
---

# Galileo agent-control: Unauthenticated Runtime Guardrails API + Policy Bypass Recipe

**Discovery:** Shodan dork `port:8000 http.html:"agentcontrol"` (1 result)  
**Date:** 2026-06-23  
**Host:** 13.68.189.140:8000 (Microsoft Azure East US, ephemeral IP)  
**Deployed:** approximately 2026-06-20 (3 days old at time of discovery)  
**Verification status:** inner-B / outer-1 (exercised against live host, single in-scope instance)

---

## Condition

Galileo agent-control v0.1.0 deployed on a public Azure IP with zero authentication on all API endpoints. The service is a runtime guardrail/policy engine for AI agents -- its stated purpose is to intercept agent actions and enforce policy rules before execution. The operator deployed a dev build to a public IP without auth and left it running.

The service hosts a real e-commerce customer-support agent. The exposed policy configuration is production-grade business logic, not test data.

---

## Evidence

### Health check (service confirmation)

```
GET http://13.68.189.140:8000/health
{"status":"healthy","version":"0.1.0"}
```

### Auth config (confirmed auth-off)

```
GET http://13.68.189.140:8000/api/config
{"requires_api_key": false, "auth_mode": "none", "has_active_session": false}
```

### Agent registration (full read access)

```
GET http://13.68.189.140:8000/api/v1/agents/customer-support-agent
{
  "agent": {
    "agent_name": "customer-support-agent",
    "agent_description": "Customer support agent with Agent Control runtime guardrails",
    "agent_created_at": "2026-06-20T05:00:50.463931+00:00",
    "active_controls_count": 0
  }
}
```

Agent created 2026-06-20 -- 3 days old at discovery. Description claims guardrails are active. All 5 controls are disabled.

### Agent tool registry (4 tools, full read access)

```
GET http://13.68.189.140:8000/api/v1/agents/customer-support-agent
  steps:
    get_order_status        -- order lookup by ID
    lookup_customer         -- customer lookup by email (PII surface, SSN exposure -- see block-pii below)
    get_order_internal      -- internal order detail: cost_of_goods, profit_margin, internal_notes, fraud flags
    process_refund          -- refund execution, capped at $200 by disabled rule
    _invoke_llm             -- controlled LLM call gate (pre/post eval points)
```

### Controls -- ALL 5 DISABLED (GET /api/v1/controls)

```
Control 1: block-prompt-injection  enabled: false  stage: pre  step: llm_call
  regex: ([Ii]gnore previous instructions|[Ss]ystem prompt|[Yy]ou are now|[Ff]orget everything|[Dd]isregard all)
  -- bypass recipe: any phrase NOT in this list passes. Pattern is now public.

Control 2: block-internal-data  enabled: false  stage: post  step: get_order_internal
  regex: (internal_notes|cost_of_goods|profit_margin|[Ee]scalation risk|[Ff]riendly fraud)
  -- financial internals (margins, COGS, fraud flags) blocked in policy but rule disabled.
     get_order_internal returns these fields unguarded.

Control 3: block-pii  enabled: false  stage: post  steps: lookup_customer, llm_call
  regex: \d{3}-\d{2}-\d{4}
  -- SSN pattern. lookup_customer output blocked for SSN format -- rule is disabled.
     SSN in customer records is unguarded.

Control 4: block-competitor-discuss  enabled: false  stage: pre  step: llm_call
  regex: ([Cc]ompare.*([Aa]mazon|[Ss]hopify)|[Ss]witch to ([Aa]mazon|[Ss]hopify)|[Bb]etter than ([Aa]mazon|[Ss]hopify))
  -- business logic rule, minor impact.

Control 5: max-refund-amount  enabled: false  stage: post  step: process_refund
  json_field_constraint: refund_amount.max = 200
  -- $200 refund cap defined but not enforced.
```

### Write surface (unauth policy modification)

```
POST http://13.68.189.140:8000/api/policy
Content-Type: application/json
{"rules": [...]}   -- no credentials required
```

Upstream write surface also available at PUT/DELETE /api/v1/controls/{id} (auth=none).

---

## Impact chain

```
  [AUTH OFF]             [ALL CONTROLS DISABLED]       [POLICY SURFACE EXPOSED]
  GET /api/config    ->  requires_api_key: false    ->  GET /api/v1/controls/*
  auth_mode: none         active_controls_count: 0       all 5 controls returned
  any caller                                             enabled: false on each
          |
          v
  [BYPASS RECIPE PUBLIC] [SSN SURFACE CONFIRMED]       [FINANCIAL DATA EXPOSED]
  block-prompt-injection  block-pii regex: SSN pattern  block-internal-data:
  regex handed to         \d{3}-\d{2}-\d{4} -- signals  cost_of_goods, profit_margin
  any reader              customer records have SSNs     internal_notes, fraud flags
  (rule disabled)         (rule disabled)                get_order_internal tool
          |
          v
  [WRITE SURFACE]        [ELEVATE REFUND CAP]          [CHAIN TO FULL COMPROMISE]
  POST /api/policy    -> raise from $200 to unlimited -> process_refund executes
  no auth, no token      or delete max-refund-amount     unlimited refunds
  DELETE /api/v1/        rule entirely                   
  controls/{id}
```

**Impact points by severity:**

1. **All guardrails disabled -- agent is completely unguarded.** All 5 controls are `enabled: false`. The system is installed but not enforcing any policy. The agent description says "with Agent Control runtime guardrails" -- this is false. The operator configured guardrails and then disabled all of them. Not a misconfiguration in the classical sense -- it is a specific state: control plane deployed, enforcement off.

2. **SSN exposure surface.** `block-pii` uses regex `\d{3}-\d{2}-\d{4}` -- Social Security Number format. The rule exists precisely because `lookup_customer` can return SSNs. With the rule disabled, SSNs are returned unfiltered. Neither confirmed exfiltration via the tool nor denied -- data-class signal is the finding.

3. **Financial internals unguarded.** `get_order_internal` returns fields including `internal_notes`, `cost_of_goods`, `profit_margin`, `escalation risk`, `friendly fraud` flags. The `block-internal-data` rule (disabled) was the only guard on this tool. Business-sensitive financial data on every order is reachable via unauth API call.

4. **Bypass recipe for injection filter is public.** The 5-phrase injection regex is enumerable via GET /api/v1/controls/1/data. Any input not matching these exact phrases passes the filter -- even if the rule were re-enabled. The evasion surface is fully documented.

5. **Refund cap not enforced, modifiable.** `process_refund` capped at $200 by `max-refund-amount` (control 5, disabled). Unauth write to /api/policy or DELETE /api/v1/controls/5 removes the cap entirely. Agent executes unlimited refunds.

6. **3-day-old deployment, active context.** Agent created 2026-06-20T05:00:50 UTC. Not a forgotten stale instance -- active development. Operator almost certainly does not know policy state is public.

Severity: HIGH. Unauth read of complete policy state + SSN data-class signal in disabled PII control + unguarded financial internals + write surface on all 5 controls. Not CRITICAL: no confirmed tool execution, no confirmed data pull from lookup_customer or get_order_internal (restraint ethic).

---

## Verification status

- Inner axis: **B** -- request exercised against live artifact. All endpoints confirmed 200-with-data.
- Outer axis: **1** -- single in-scope host. Population sweep of 74 "Agent Control" title IPs found 1 Galileo instance. No population rate calculable.

---

## Attribution

### Infrastructure (Bravo squad)

| Signal | Value |
|--------|-------|
| ASN | AS8075 Microsoft Corporation |
| Region | Azure East US, Boydton VA 23917 |
| PTR | NXDOMAIN (entire /28 unconfigured) |
| Cert transparency | 0 results for IP; /24 yields only sslip.io for unrelated host |
| SSH fingerprint | ED25519 `IGWPWWPxFoFofmJJ5gb1w7d77DPNBKTPW1BXbhiQLySy` (no indexed reuse) |
| Static bundle timestamp | Last-Modified: Thu, 12 Mar 2026 07:43:11 GMT (Galileo release day) |
| VisorGraph | 0 nodes, 0 edges (plain HTTP, no TLS, no PDNS) |

Attribution ceiling: application layer only. HTML canonical link + Docker image name (`galileoai/agent-control-server`) attribute the software to Galileo AI / agentcontrol org. The specific operator who deployed this instance is not attributable.

### Operator analysis (Charlie squad)

**Software origin:** Galileo AI's `agentcontrol/agent-control` (Apache 2.0, launched 2026-03-11). Under Cisco/Splunk Observability following 2026-04-09 acquisition.

**Tool set does not match Galileo's stock example.** Galileo's customer-support template uses `lookup_customer`, `search_knowledge_base`, `create_ticket`. This deployment has `get_order_status`, `lookup_customer`, `get_order_internal`, `process_refund` -- closest match is the AWS AgentCore Samples blueprint which caps `process_refund` at $100. This operator raised the cap to $200 and deployed on Azure.

Operator profile: an external developer who adapted the AWS AgentCore customer-support blueprint to use agent-control, raised the refund cap, deployed on Azure, and disabled all 5 policy controls. Not Galileo running their own demo.

**Galileo principals (for disclosure routing -- not the operator):**

| Person | Role | Contact |
|--------|------|---------|
| Yash Sheth | Co-founder / CTO | linkedin.com/in/yash-sheth-/ |
| Vikram Chatterji | Co-founder / CEO | linkedin.com/in/vikram-chatterji |
| Lev Neiman | Staff Engineer (agent-control lead) | linkedin.com/in/levneiman/ |

Post-acquisition: disclosure routes through Cisco/Splunk security channels.

---

## Remediation

1. Bind to localhost (`host: 127.0.0.1`) for all dev deployments
2. Enable AGENT_CONTROL_API_KEY_ENABLED=true and set a key before any internet-facing deployment
3. The README warning ("no authentication required for development") should become a startup-time check that refuses to bind to 0.0.0.0 without explicit `--allow-public` flag
4. Enable all controls before connecting real agent tools -- deployed-but-disabled is not a valid security posture
5. Rotate policy configuration after any public exposure -- regex bypass recipes are now in Shodan cache

---

## PLATFORMS SURVEYED (Stage -1 + Stage 0)

| Platform | Domain | Shodan surface | Auth default | Finding |
|---|---|---|---|---|
| Sluice | sluice.email | 204.168.138.213:587 | ON (hardened) | Done 2026-06-06 |
| Clawvisor | clawvisor.com | vendor IAP only | ON (IAP + JWT) | Vendor infra only |
| Alter | alterauth.com | 0 | SaaS-only | Shodan-dark |
| Salus | usesalus.ai | 0 | SaaS-only | Shodan-dark |
| Invariant GW | invariantlabs.ai | 0 | port 8005 | Dark tier |
| OpenGuardrails | openguardrails.com | 0 | SaaS-only | Dark tier |
| LlamaFirewall | Meta OSS | 0 | library | No surface |
| agent-control | agentcontrol.dev | 13.68.189.140:8000 | **OFF** | **FINDING #1 HIGH** |
| Galini | galini.ai | 0 | SaaS API key | Shodan-dark |
| Pipelock | pipelock (gh) | 0 | open core | Too new (May 2026) |
| AgenticMail | agenticmail (gh) | 0 | Bearer token | Auth-on-default |

---

## Full dork log (43 dorks, 2026-06-23)

| Dork | Hits | Notes |
|---|---|---|
| `ssl.cert.subject.cn:"clawvisor.com"` | 2 | vendor IAP only |
| `ssl.cert.subject.cn:"clawvisor.com" http.html:"AI Agent Gatekeeper"` | 0 | |
| `http.html:"AI Agent Gatekeeper" http.html:"Policy-based access control"` | 0 | |
| `port:25297 http.title:"Clawvisor"` | 0 | loopback-only default |
| `ssl.cert.subject.cn:"alterauth.com"` | 0 | |
| `ssl.cert.subject.cn:"alterai.dev"` | 0 | |
| `http.html:"Alter Vault" http.html:"Authorization Layer for AI Agents"` | 0 | |
| `ssl.cert.subject.cn:"usesalus.ai"` | 0 | |
| `http.html:"identity.ambiguous_caller" http.html:"Vol. XXI"` | 0 | |
| `http.html:"LlamaFirewall"` | 0 | library, no server |
| `http.html:"LlamaFirewall" "PromptGuard"` | 0 | |
| `http.html:"OpenGuardrails"` | 0 | |
| `http.html:"Zero Trust Firewall for AI Agents"` | 0 | |
| `http.html:"Invariant Gateway"` | 0 | |
| `port:8005 http.html:"invariant"` | 0 | |
| `http.html:"/api/v1/gateway/"` | 0 | |
| `ssl.cert.subject.cn:"explorer.invariantlabs.ai"` | 0 | |
| `http.html:"clawvisor"` | 0 | |
| `ssl:"clawvisor.com"` | 2 | same vendor hosts |
| `ssl.cert.subject.cn:"alter.dev"` | 1 | FP (altshina.com) |
| `http.html:"AlterAuth"` | 6 | FP (UN Oracle HCM) |
| `http.html:"usesalus"` | 0 | |
| `ssl:"usesalus.ai"` | 0 | |
| `ssl.cert.subject.cn:"invariantlabs.ai"` | 0 | |
| `ssl:"invariantlabs.ai"` | 0 | |
| `ssl.cert.subject.cn:"openguardrails.com"` | 0 | |
| `http.html:"email guardrail"` | 0 | |
| `http.html:"outbound email" http.html:"LLM"` | 0 | |
| `http.html:"email safety" http.html:"agent"` | 0 | |
| `product:"Haraka" port:587` | 0 | |
| `http.title:"Mailpit"` | 936 | dev email catchers, not guardrail |
| `http.html:"email" http.html:"policy" http.html:"swagger"` | 41 | FP class (GCP managed services) |
| `http.html:"email agent" http.html:"api_key"` | 2 | FP (dead hosts) |
| `port:8000 http.html:"Agent Control" http.html:"controls"` | 2 | FP (CHINANET dead) |
| `port:8000 http.html:"agentcontrol"` | 1 | **FINDING #1: 13.68.189.140 UNAUTH** |
| `port:8888 http.html:"pipelock"` | 0 | too new (May 2026) |
| `port:8888 "mediator-signed"` | 0 | |
| `port:3829 http.html:"agenticmail"` | 0 | |
| `ssl.cert.subject.cn:"galini.ai"` | 0 | SaaS-only |
| `port:8005 http.html:"/api/v1/gateway/"` | 0 | Invariant dark |
| `port:8005 "Invariant Gateway"` | 0 | |
| `ssl.cert.subject.cn:"clawvisor.com" -org:"Google LLC"` | 0 | no operators |
| `ssl.cert.subject.cn:"galileo.ai"` | 0 | |
| `http.title:"Agent Control"` | 84 | 74 unique IPs; 3 live; 1 Galileo; RETIRE |
| `port:8000 http.html:"Runtime Guardrails for AI Agents"` | 1 | canonical Galileo dork |
| `port:8000 http.html:"customer-support-agent"` | 1 | 34.57.26.77 dead at verify |

---

## aimap fingerprint

Added to `~/ai-recon/aimap/fingerprints.go` (AI agent platforms section):

```go
{
    Name:         "Galileo agent-control",
    DefaultPorts: []int{8000},
    Probes: []Probe{
        {Path: "/", Matches: []MatchCond{
            {Type: "status_code", Value: "200"},
            {Type: "body_contains", Value: "Runtime Guardrails for AI Agents"},
        }},
    },
    Severity: "high",
},
```

FP note: `/health` with `body_contains "status"` fires on ZenML and Chatterbox TTS. Root-path body anchor is the correct discriminator.

---

## BARE module matching

No corpus coverage. Top cosine similarity: 0.485 (below 0.55 threshold). No Metasploit modules for AI guardrail runtime services. Expected corpus gap for this novel service class.

---

## Survey context

Cat-33 AI Email/Agent Guardrails survey, 2026-06-23. 43 dorks executed. Category landscape: most Cat-33 vendors bind to loopback or are pure SaaS APIs. Shodan surface is structurally thin. This instance is a dev deployment mistake (auth-off by design in dev mode, accidentally bound to 0.0.0.0).
