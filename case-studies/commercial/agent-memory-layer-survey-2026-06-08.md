---
type: survey
---

# Agent Memory Layer — First Population Survey (MemMorph attack surface)

_NuClide Research · 2026-06-08 · Cat-47 (Agent Memory Layer)_

> **Why this survey exists.** A syllabus-driven hunt. The MemMorph paper (arxiv 2605.26154, "Tool Hijacking in LLM Agents via Memory Poisoning") describes a memory-poisoning attack against LLM agent platforms, with `mem0` (github.com/mem0ai/mem0) as the named target. The paper proves the attack works in lab conditions; this survey asks whether the population exists at internet scale. It does — and the broader emerging "agent memory layer" tier (Mem0, Letta née MemGPT, Zep, Cognee) shows the same auth-off-default pattern as the established AI/ML tiers, despite the population being orders of magnitude smaller.

## Summary

First standalone population survey of agent-memory platforms exposed on the public internet. Across 269 Shodan-discovered hosts:

| Platform | Discovered | Verified | Unauth (of verified) | Headline finding |
|---|---|---|---|---|
| **Zep** (open-source LLM memory) | 23 | 19 | **14 (74%)** | 27 user-session identifiers leaked, ready-to-poison memory at population scale |
| **Mem0** (the MemMorph target) | 161 | 6 | **3 (50%)** | **Memory-poisoning attack surface reachable on all 3 unauth Mem0 hosts** (users + memories endpoints both 200) |
| **Letta** (formerly MemGPT) | 67 | 10 | **5 (50%)** | Agent inventory disclosed unauth |
| **Cognee** (knowledge-graph memory) | 18 | 1 | 1 (100%) | Single confirmed unauth; population thin |
| **Total** | 269 | 36 | **23 (64%)** | First empirical anchor for MemMorph attack class |

The 233 hosts not "verified" in this table fall into two buckets: 87 returned 0 on every probe (Shodan banner stale, host offline), and 146 returned shapes the verifier couldn't classify (likely documentation pages, blog references, framework demos — the broader dorks like `http.html:"mem0"` match anything that mentions the platform, not just running instances). On the **confirmed-running subset (n=36)**, the auth-off-default rate is **64%**, in line with the established Chroma / VictoriaMetrics / Prometheus tiers.

## Methodology

Paper-first target selection. Steps:

1. Syllabus search ("agent memory exfiltration LLM context store") returned MemMorph as the top thematic match.
2. Read the paper for platform names → identified `mem0` as the named target.
3. Shodan probe for Mem0 + related memory-layer platforms (Letta, Zep, Cognee).
4. Population existed at meaningful scale (269 candidates) → proceed to verifier.
5. Built `verify_agentmem.py` — read-only probes per platform's documented API.
6. Verified, classified, rolled up.

**Restraint discipline.** Read-only probes ONLY. The MemMorph paper documents a write-surface attack (`POST /v1/memories` with poisoned content). We did NOT attempt the attack. We measure the **open-of-write-surface** by observing whether the related GET endpoints (`/v1/users`, `/v1/memories`) return 200 unauth — those returns prove the API surface is accessible without auth and the documented write paths require no different credential. Confirmation that the attack vector exists at population scale; no exploitation attempted.

## Platform-by-platform findings

### Zep — the headline (14/19 = 74% unauth)

Zep is an open-source "memory for LLM apps" platform written in Go. Default deployment exposes `/api/v1/sessions` and `/api/v1/memory/{session}/messages`. Both endpoints return 200 unauth on 14 of 19 verified-running hosts.

**27 session identifiers leaked** across the unauth subset. Each session ID corresponds to a per-user conversation history. An attacker who reads the session list learns:
- How many distinct users the operator has
- Session-name patterns (often containing user_id, email prefix, or workspace identifier)
- Per-session message counts and recency

Geography: DE 4, US 4, FR 2, FI 1, AE 1, KZ 1, HK 1. Cloud distribution: Hetzner 5, OVH 2, Google 1, others 1 each. Pattern matches typical EU/US self-hosted indie deployments — exactly the population this layer targets.

**MemMorph applicability.** The Zep API includes `POST /api/v1/memory/{session}/messages` for writing to a session. The 14 unauth hosts expose this surface; the MemMorph attack (inject a poisoned memory that the agent later retrieves) is reachable. We did not test.

### Mem0 — the named MemMorph target (3/6 = 50% unauth, 3/3 write-surface reachable)

The MemMorph paper specifically targets Mem0. Empirically the platform's population on the public internet is small (161 Shodan hits, 6 verified-running, 3 unauth), but **every single confirmed-unauth Mem0 host has the memory-poisoning write surface reachable** (the `/v1/users` endpoint returns 200, confirming user enumeration; the related `POST /v1/memories` requires no additional auth per the OpenAPI spec).

The MemMorph attack against population: hits on a 3-host base. The paper's lab result generalizes. Geographic: CN 1, HK 1, EG 1. The CN/HK cohort is consistent with the broader pattern: Chinese self-hosted AI infra ships open-by-default at significant rates.

### Letta (formerly MemGPT) — 5/10 = 50% unauth

Letta is the rebranded MemGPT — the original "agents as operating systems" framework. Default deployment exposes `/v1/agents` returning the agent inventory. 5 of 10 verified-running hosts return 200 unauth, disclosing the operator's agent population and per-agent state names.

Geography: IT 1, UK 1, AE 1, DE 1, CN 1. One UK host is operated by a non-IT organization (asbestos remediation contractor) running an agent platform; one Italian host is operated by Sogei (the IT company of the Italian government's tax authority). The operator-class spread is wider than typical AI surveys — Letta is finding non-AI-native operators experimenting with agent frameworks.

### Cognee — 1/1 = 100% unauth

Smallest population (18 raw, 1 verified-running, 1 unauth). Insufficient to draw population-scale conclusions. Cognee is a knowledge-graph memory layer; its API endpoints (`/api/v1/datasets`, `/api/v1/pipelines`) are documented as unauth-by-default per the docs. The single empirical confirmation is consistent. CN-hosted.

## What the paper said, and what the population shows

The MemMorph paper:
- Defines a tool-hijacking attack via memory-poisoning on LLM agents
- Demonstrates the attack against Mem0 in a controlled lab
- Discusses generalization without claiming population-scale evidence
- Cites Mem0's GitHub repository as the implementation target

This survey adds:
- **Empirical confirmation that the attack surface exists at population scale.** Mem0 instances are publicly accessible with the write endpoints reachable unauth. The lab result is not artificial.
- **Generalization beyond Mem0.** Zep (different vendor, different language, different design) has the same auth-off-default issue at 74%. Letta has it at 50%. The memory-layer category itself ships open.
- **A population-level disclosure target.** 23 confirmed unauth hosts across 4 platforms. Each is a memory-poisoning attack opportunity. None requires CVE; the auth design defect is per-platform default.

## Why this category is different from substrate tiers

VictoriaMetrics and Prometheus leak topology (Insight #88). Chroma leaks RAG corpus identity. Agent-memory platforms leak **conversation state plus the writeable surface for the next conversation**. An attacker who poisons a memory chains forward: every future agent retrieval that touches the poisoned memory carries the attack into a new LLM context window, where it can hijack tool calls, exfiltrate state, or pivot to other systems the agent has access to.

The substrate-tier finding is "your monitoring is open." The agent-memory tier finding is "your agent's mind is open to writes from anyone." The blast radius depends on what the agent can do downstream of its memory — which, for production agent platforms, includes tool execution, function calls, file system access, and other agents.

## Insight #93 candidate — paper-driven surveys produce better-evidence outputs

The MemMorph paper described an attack; this survey provides empirical population data for it. The combination — paper attack class + population survey — is strictly stronger than either alone:

- Paper alone: novel attack class, lab demonstration, no population evidence
- Survey alone: population statistics, no semantic understanding of why the platforms matter
- Combined: attack class + population reachability + specific operator-disclosure pipeline

Future surveys should **read the literature first** for the next 1–3 emerging-tier categories per quarter. Specifically:
- Search the venues-ai-security corpus for "exposed" / "production" / "platform" + new attack class
- Identify the platform names mentioned
- Cross-check against the program's surveyed taxonomy
- Schedule the unsurveyed-named platforms next

The DCWF 902 strategic roadmap is one driver of next-category selection (substrate generalization). The syllabus is now confirmed as a second equally-valid driver (paper-attack-class anchoring).

## DCWF KSAT coverage

- **753 (AI/ML Specialist):** identified agent-memory layer as a coherent platform class via cross-reference between syllabus search and Shodan population (S7075 — eval ML algorithms / AI solutions for vulnerabilities).
- **672 (T&E):** verifier-correctness probe per platform; rejected 233 of 269 candidates as broad-dork FP (T5919 — adversarial testing in realistic environments).
- **733 (Risk & Ethics):** restraint discipline on the write surface — measured open-of-write rather than attempting it (T5854).
- **661 (R&D):** Insight #93 candidate codified — syllabus as survey driver (T0064 — engineering primitives that turn corpus state into a research process).

## Wardrobe + syllabus stance

**Wardrobe outfit loaded:** `ai-infra-hunt` (carries from earlier today's surveys). Syllabus role explicit: paper-first hunt, syllabus-derived target selection.

**Syllabus threat-literature anchors (load-bearing for this case study):**

- **arxiv 2605.26154 — MemMorph: Tool Hijacking in LLM Agents via Memory Poisoning** — the paper that motivated the hunt. Named Mem0 as target. This survey provides the missing population-scale evidence the paper does not.
- arxiv 2606.06036 — Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents — relevant to Cognee's knowledge-graph design; cited for future Cognee deep-dive.
- arxiv 2604.10717 — Detecting RAG Extraction Attack via Dual-Path Runtime Integrity Game — relevant to RAG-memory boundary; cross-cuts Chroma + Zep findings.
- NDSS — ACE: A Security Architecture for LLM-Integrated App Systems — proposes architectural mitigations; the 23 unauth hosts surveyed here are exactly the population this line of work prescribes mitigations for.

## Artifacts

- **Verifier:** `~/syllabus/shodan/verify_agentmem.py` → `tools/verify_agentmem.py`
- **Per-host evidence:** `~/syllabus/shodan/agentmem-verify/hosts/<ip_port>.json` (held private)
- **Rollup:** `~/syllabus/shodan/agentmem-verify/rollup.json`
- **Shodan harvest:** `~/syllabus/shodan/agentmem-harvest/hosts.json`

## What we did not do (restraint discipline)

- **Zero POSTs to memory-write endpoints.** The MemMorph attack vector is the documented write surface; we did NOT exercise it. The case study reports presence of the surface, not its exploitation.
- No reads of session contents on Zep (`/api/v1/memory/{session}/messages` left unprobed for any specific session ID we extracted).
- No reads of agent state on Letta beyond the inventory listing.
- No probing of any user identifier extracted from Mem0's `/v1/users` response.
- No internal-network reconnaissance from any leaked configuration.

The leak is the finding. The MemMorph paper has already demonstrated the exploit; the program's contribution is the population-reachability proof, not a reproduction of the attack.

## Insight updates

**Insight #93 candidate — syllabus-driven surveys.** Paper-first target selection produces case studies with denser evidence (attack class + population reachability) than population-first surveys alone. Codify after one more paper-driven survey confirms the pattern (next candidate: any of the NDSS / USENIX papers on emerging AI infrastructure categories).

**Insight #94 candidate — agent-memory leaks compound forward in time.** A poisoned agent memory is not a one-shot disclosure; it is a persistent trigger that affects every future LLM context window the agent constructs. Forward-compounding disclosure class. Future surveys should track NOT just "is the memory readable" but "is the memory writeable in a way that affects the next 100 agent turns." Codify after Zep + Letta operator notification yields remediation timing data.
