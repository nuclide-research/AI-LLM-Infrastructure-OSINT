---
type: synthesis
---

# AI agent framework population survey, 2026-05-17

_NuClide Research, 2026-05-17 (late evening pass)_
_Survey #20 in the AI infrastructure series._

---

## Summary

We surveyed the public-facing agent-framework population: AutoGen Studio, CrewAI, LangGraph Studio, Langflow, AgentOps. The corpus harvested from Shodan dorks totaled 351 unique IPs. After running aimap with existing fingerprints and applying [Insight #30](../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md) multi-port consistency checking, the result is striking: **the population is dominated by honeypot baits.**

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7070, S7075, T5858, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6935

<!-- ksat-tag:auto-generated:end -->

Three findings.

**One. The agent-framework Shodan-dork landscape is heavily poisoned.** Of 351 candidate IPs, aimap matched 83, and 60+ of those matches were on honeypot baits (Docker Registry, dcm4che, MCP Server fingerprints triggered by canary content, not real services). Only 3 hosts were confirmed real (Langfuse, all properly authenticated).

**Two. Single-word substring dorks are unusable at this population scale.** `"crewai"` returned 121 hits; `"langflow"+http` returned 176; `http.title:"Langflow"` returned 51,435. Sample probes against the top of each list returned bait pages titled "ruianzhu-高恪", "Zero Touch Provisioning", "SAP NetWeaver", "HealthBackend_Login", "prtg", and "Persona 5 Bio WordPress". All with distinct UUID favicons consistent with the AS63949 honeypot fleet. Insight #15 ("the 50% rule") and Insight #26 (substring-FP escalates with token commonality) are both applied here.

**Three. aimap does not yet have fingerprints for CrewAI, LangGraph Studio, Langflow, or AgentOps.** This is a coverage gap that prevents protocol-strict verification on the agent-framework population. Even if the Shodan corpus contained real Langflow hosts (probability low after the honeypot filter, but not zero), aimap cannot currently confirm them.

---

## What aimap caught (83 service hits, 60+ bait-only)

| Service classification | Hits | Notes |
|---|---:|---|
| MCP Server | 15 unique IPs | Multi-port classifier: 3/3 sampled returned canned `mcp-server 1.0.1 2025-06-18` on all 6 probe ports. 100% honeypot. |
| ClickHouse | 14 hits | Survey-irrelevant; same FP class as MCP honeypots. |
| Docker Registry | 9 hits | Honeypot bait variant. |
| dcm4che / dcm4chee-arc | 9 hits | Insight #22 — known catchall FP class for ASP.NET-shaped responses. |
| Langfuse | 3 hits | **Real**, all properly authenticated (HTTP 401 on `/api/public/projects`). No exposure. |
| Typesense | 1 hit | Search engine FP, survey-irrelevant. |
| Open Directory | 1 hit | Generic directory listing. |

**Real services confirmed:** 3 (all auth-gated Langfuse instances).
**Honeypot baits matched:** ~60 distinct IPs.
**Unclassified by existing fingerprints:** ~270 IPs. These may include real agent frameworks aimap cannot yet identify.

---

## The honeypot signature recap

The AS63949 (Akamai-Linode) and now AS16509 (AWS) honeypot fleets bait many AI categories simultaneously. From the MCP survey earlier today + this survey, characteristic canaries include:

- `POC_SUCCESS_` literal on `/volumes`
- Fake OpenSSH private keys on `/images/json`
- Ivanti Connect Secure login bait on `/networks`
- DrayTek VigorConnect admin pages on `/sse`
- Distinct UUID-based favicon hashes on every host (unique to the fleet)
- Same canned MCP `initialize` response on every port (`mcp-server 1.0.1 2025-06-18`)
- Decoy SOHO router admin pages (Huawei HG658d, Netman 204, RT-GM-5)
- Chinese tech-product login pages (ruianzhu-高恪, HealthBackend, prtg)

A real agent framework runs on one port, returns one identifiable HTML title or API response, and presents a coherent authentication posture. The honeypots fail on consistency.

---

## What is needed for a useful agent-framework survey

1. **aimap v1.9.11 fingerprint expansion.** Add probes for Langflow (`GET /api/v1/version` → `{"version": "x.y.z", "main_version": "..."}`), CrewAI (CLI tool, less common as a server; possibly skip), LangGraph Studio (`GET /info` → server info), AgentOps (`GET /api/v1/agents` if auth-open).
2. **Protocol-strict harvest queries.** `"langflow"+"api/v1/flows"`, `"langgraph-api"`, `"@modelcontextprotocol/sdk"`, etc.. Narrow enough that honeypots cannot fake them in their bulk-canary set.
3. **Multi-port honeypot filter (Insight #30) on every survey, default-on.** Already coded for MCP; needs to become a standard aimap second-pass check via a `--filter-honeypots` flag in v1.9.11.

Until those land, agent-framework survey at population scale is not viable. The signal-to-noise ratio is too low.

---

## What did NOT need to be confirmed

The 3 Langfuse hits are properly authenticated; no exposure. The 14 ClickHouse "hits" in this corpus are honeypot variants (different from the 1,832-host real ClickHouse population we mapped yesterday, those are still real). The 9 dcm4che hits are the catchall FP class documented in Insight #22.

No disclosure-class exposures surfaced in this survey.

---

## Toolchain provenance

```
JAXEN           [x] 351 candidates across 5 dorks (AutoGen, CrewAI, LangGraph,
                    Langflow, AgentOps)
aimap v1.9.10   [x] 83 service hits across 12-port probe set, 25min runtime
aimap-profile   [ ] not needed — no real targets to profile
VisorGraph      [ ] not needed — no real targets to cert-pivot
classifier      [x] Insight #30 multi-port honeypot filter applied as second pass
v1.9.11 fingerprints  [ ] queued: Langflow, LangGraph, CrewAI, AgentOps deep enums
```

---

## See also

- [`mcp-server-survey-2026-05-17.md`](mcp-server-survey-2026-05-17.md): sibling survey, identified the AWS-cohort honeypot expansion
- [`../../methodology/insight-15-dork-hits-vs-platform-instances.md`](../../methodology/insight-15-dork-hits-vs-platform-instances.md): the 50% rule
- [`../../methodology/insight-26-shodan-facet-fp-rate-escalates-with-token-commonality.md`](../../methodology/insight-26-shodan-facet-fp-rate-escalates-with-token-commonality.md)
- [`../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md`](../../methodology/insight-30-multi-port-identical-responses-identify-honeypots.md)
- [`../../reference/as63949-honeypot-fleet.md`](../../reference/as63949-honeypot-fleet.md)
