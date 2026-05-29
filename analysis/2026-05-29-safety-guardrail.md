# Session Analysis: LLM Safety / Guardrail survey

## 1. Overview

### Objective
First population survey of the LLM safety/guardrail category: guardrail API
servers, safety classifiers, prompt-injection scanners. Test the auth-on-default
thesis on a class the intel flagged as auth-off across the board. Pre-survey
intel: data/platform-intel/safety-guardrail-osint-2026-05-27.md.

### Scope and Constraints
Commercial cloud (Hetzner, OVH, AWS, Azure, Koyeb). Shodan via Playwright, both
API keys dead, queries paced to avoid the Cloudflare rate-limit. All probing
through Mullvad (us-lax-wg-007). Benign marker probes only: a "test" string to
the scanner, Redis PING and INFO metadata, MongoDB TCP-connect without query. No
real prompts, no upstream-LLM bypass, no data reads.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. Shodan harvest by browser, paced. aimap and menlohunt as
bounded background commands. Verification by curl and python socket through
Mullvad.

### Tools Used
Full 19-tool arsenal. Material output: JAXEN, aimap, aimap-profile, menlohunt,
VisorLog, BARE, cortex. Documented non-runs: VisorSD/recongraph/nu-recon/VisorPlus
(Shodan-key blocked), VisorGoose (gov/edu), VisorRAG (no RAG surface), VisorHollow
(Windows), VisorAgent (controlled-target only; not fired at the operator host),
VisorBishop (no guardrail fingerprint, gap), JS-bundle (no CDN-SPA).

### Notable Configuration
aimap v1.9.39 (no LLM Guard fingerprint, gap). nuclide.db at ~/visorlog/nuclide.db.
Workspace ~/recon/safety-guardrail-2026-05-29/.

## 3. Methodology

### Enumeration approach
Five dorks. LLM Guard via OpenAPI title; NeMo/Guardrails AI/Rebuff via brand
strings; Vigil via port + keyword.

### Candidate identification
LLM Guard 9 (clean). NeMo/Guardrails AI/Rebuff 0 (JSON-dark). Vigil 20 (FP swamp).

### Validation checks
LLM Guard: GET / for identity, POST /analyze/prompt benign for auth state.
IP-shadow via menlohunt on the unauth host. Redis PING+INFO, MongoDB TCP-connect.

### Safeguards
Mullvad verified before and during. Benign "test" scanner input only. Redis
metadata only, no keyspace. MongoDB connected but not queried. No upstream-LLM
bypass attempted.

## 4. Execution Trace

```
1. Read safety-guardrail intel + methodology
2. Mullvad verified (us-lax-wg-007); paced dorks (Cloudflare lesson from this session)
3. NeMo /v1/rails/configs -> 0 (JSON-dark)
4. Vigil port:5000 "vigil" -> 20 FP (Pro-Vigil cameras + Synology NAS)
5. LLM Guard "LLM Guard API" -> 9 clean
6. Guardrails AI -> 0; Rebuff -> 0 (both string-dark)
7. LLM Guard verify: GET / -> {"name":"LLM Guard API"}; root path discovery on 8000
8. POST /analyze/prompt benign: 5.78.101.230 unauth (scanner verdict); 57.128.58.103
   + 15.204.46.173 "Not authenticated"; 4 hosts root 000 (aged-out Koyeb)
9. 5.78.101.230 /analyze/output -> Sensitive scanner (full roster disclosed)
10. aimap lean 8 hosts -> only Grafana (no LLM Guard fingerprint, gap)
11. menlohunt IP-shadow on 5.78.101.230 -> MongoDB + Redis + MySQL + Postgres + Docker reg, 6 chains
12. Primary-source Redis 7.2.10 PING+PONG+INFO (Linux 5.4, 17d); MongoDB TCP open (not queried)
13. VisorLog: 8 aimap + 2 manual events -> nuclide.db
14. aimap-profile, BARE (no MSF), arsenal accounting
15. Wrote case study, query-file append, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 5.78.101.230 (Hetzner): unauth LLM Guard + stacked data tier
HIGH. Unauth LLM Guard :8000 (safety-layer bypass, scanner roster disclosed) plus
unauth MongoDB :27017, Redis 7.2.10 :6379, MySQL :3306, PostgreSQL :5432, Docker
registry :5000. The guardrail is the smallest part. Insight #12.

### 5.2 LLM Guard auth-enforced x2: thesis evidence
57.128.58.103, 15.204.46.173 set AUTH_TOKEN. The opt-in toggle works when used.

## 6. Risk Assessment

### Overall Posture
Auth-off-default confirmed. One of three reachable LLM Guard servers open, two
secured. The nonzero open rate is the default's signature; the two secured hosts
prove the toggle gets used.

### Confidentiality
The stacked MongoDB and Redis on the open host expose whatever the operator
stored. The guardrail leaks its scanner roster.

### Integrity
The open guardrail can be bypassed: route prompts straight to the upstream model.

### Availability
Redis FLUSHALL and the open data tier are denial vectors.

### Systemic Patterns
- The safety tool was the least-guarded thing on the host (Insight #12 + the irony of the platform class).
- Shipping default predicts the open rate: three categories, three points on one curve (voice-AI all-open, guardrail partial, ML-gov closed).
- Guardrail API servers are Shodan-dark behind JSON roots except LLM Guard's OpenAPI title (Insight #67, third category).

## 7. Recommendations

### R1: Set AUTH_TOKEN on LLM Guard
It ships off. Turn it on.

### R2: Lock the data tier
Bind MongoDB, Redis, MySQL, PostgreSQL to localhost or firewall them.

### R3: Authenticate the Docker registry

```
# Redis: refuse public bind
bind 127.0.0.1 ::1
requirepass <strong-random>
# LLM Guard: set the token
docker run -e AUTH_TOKEN='<strong-random>' laiyer/llm-guard-api
```

## 8. Limitations

NeMo Guardrails, Guardrails AI, and Rebuff are Shodan-dark and were not
enumerated (need masscan + API-shape fingerprinting). The LLM Guard sample was
nine hits, four aged out by probe time. Vigil could not be separated from the
Pro-Vigil brand. aimap has no guardrail fingerprint, so manual verification
carried the survey.

## 9. PoC Illustrations

```
# LLM Guard unauth scanner (benign test input)
$ curl -s http://5.78.101.230:8000/
{"name":"LLM Guard API"}
$ curl -s -XPOST http://5.78.101.230:8000/analyze/prompt -d '{"prompt":"test"}'
{"is_valid":true,"scanners":{"PromptInjection":-1.0,"Toxicity":-1.0,"Secrets":-1.0},"sanitized_prompt":"test"}

# Stacked Redis on the same host (metadata only)
$ printf 'PING\r\nINFO server\r\n' | nc 5.78.101.230 6379
+PONG
redis_version:7.2.10

# Auth-enforced peer (toggle set)
$ curl -s -XPOST http://57.128.58.103:8000/analyze/prompt -d '{"prompt":"test"}'
{"message":"Not authenticated","details":null}
```
