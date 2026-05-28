---
type: methodology
title: Tool-to-stage mapping — which arsenal tool runs at which pipeline stage, and why
date: 2026-05-28
---

# Tool-to-Stage Mapping

The arsenal is documented in three places that each organize it differently:
the website `/tools` (by Visor-vs-adjacent), `data/visor-chain-runner.sh` (by
execution order), and `METHODOLOGY.md` (by 8-stage pipeline phase). This doc
reconciles all three into one view, so "where does tool X belong" is answerable
without re-deriving it from three sources every session.

The pipeline (from `METHODOLOGY.md`):

**Discover → Fingerprint → Verify → Attribute → Classify → Ledger → Score → Codify**

Verify is the load-bearing stage. Everything before it produces *candidates*;
Verify is where a candidate becomes a finding.

---

## 1. The 8-stage map

| Stage | Tools | Role at this stage | Governing insights |
|-------|-------|--------------------|--------------------|
| **0 Discover** | **JAXEN** (Shodan harvest → empire.db), **VisorSD** (Shodan/ASN-org dork sweep), **VisorGoose** (gov-TLD via CT logs + Shodan + DNS), **menlohunt** (GCP EASM), **recongraph** (seed-polymorphic graph) | Produce candidate hosts. JAXEN is the spine; the rest are disjoint discovery channels. Also: the `nuclide.db` ledger itself is a discovery substrate. | #23 (coverage is multiplicative), #9 (ledger as discovery substrate), #65 (cert-dork selection bias) |
| **1 Fingerprint** | **aimap** (69 services / 36 deep enumerators), **VisorBishop** (12-platform observability meta-fingerprinter) | "What AI/ML service is on this port?" — identity ONLY, not auth state. | #16 (a 200 is identity, not auth state), #66 (DefaultPorts survey-driven), #6 (conjunctive matchers) |
| **2 Verify** ⭐ | **aimap** deep enumerators, **VisorBishop** IP-direct-shadow probe, **nu-recon** (single-host passive deep-read), **Cortex** (authz-context analyzer, via VisorRAG), **JS-bundle** extraction, **category probes** (`data/*-probe.py` incl. `kubecost-opencost-probe.py`) | Candidate → finding. Speak the protocol; read the data layer; probe both UI and API surfaces. | #51/#52/#53 (per-stage precision: port 1.4%, HTTP-200-path 0%, label≠identity), #37 (asymmetric auth), #8 (auth-bypass paths), #12 (IP-direct shadow) |
| **3 Attribute** | **VisorGraph** (cert-pivot → CT-log SAN enumeration → operator), **recongraph** (provenance graph), **nuclide-contact** (WHOIS → disclosure recipient) | Anonymous IP → named operator. | #4 (WHOIS authoritative), #17 (operators are mono-platform), #65 |
| **4 Classify** | **aimap-profile** (HIPAA/clinical/commercial/research/honeypot + ethics flags), **osint-platoon** (HIGH+/CRITICAL deep-dive orchestration — see §3) | Sector, sensitivity, ethics gate, honeypot discrimination. | #1/#22/#30 (honeypot discrimination), #4 (disclosure routing) |
| **5 Ledger** | **VisorLog** (`nuclide.db`, append-only, ECS-normalized, lifecycle-tracked) | The record of work. Not a terminal print — every confirmed finding lands here. | #9 (the ledger is also Stage-0 substrate) |
| **6 Score / Rank / Corpus** | **VisorScuba** (OPA/Rego compliance, 0–10, extends CISA ScubaGear), **BARE** (offline semantic exploit→module ranking), **VisorCorpus** (adversarial corpus for LLM-adjacent surface) | Severity scoring, commodity-vs-first-party exploit mapping, red-team payload generation. | — |
| **7 Codify** | case study + numbered **Insight**; **AI-LLM-OSINT** is the published catalog | Extract the class of mistake. A survey with no insight under-delivered. | #5 (disclosure efficacy), #52 (ship insights as executable winnow signatures, not prose) |

---

## 2. The executable order (`data/visor-chain-runner.sh <slug>`)

The runner does NOT execute in clean pipeline order — it interleaves for
efficiency. The actual step sequence:

| Step | Tool | Pipeline stage | Notes |
|------|------|----------------|-------|
| 0 | JAXEN | Discover | `jaxen import --no-lookup` → empire.db → `ips.txt` |
| 1a | VisorPlus | (orchestrates 1–2) | `visorplus assess <ip>` per host, 6-phase passive |
| 1b | aimap | Fingerprint | `aimap -list ips.txt -ports <AIMAP_PORTS> -threads 30` |
| 2 | VisorGraph | Attribute | `visorgraph -ip <ip>` per host (cert pivot) |
| 3 | aimap-profile | Classify | `--mode fast` per host |
| 3b | **osint-platoon** | Classify→deep-dive | **CONDITIONAL** — fires only on HIGH+/CRITICAL hosts (see §3) |
| 4 | JS-bundle | Verify | **SKIPPED in batch** — deferred to case-study-time manual extraction |
| 5 | nuclide-contact | Attribute | WHOIS → recipient (disclosure routing) |
| 6 | VisorLog | Ledger | aimap → NDJSON → `visorlog ingest` |
| 7 | VisorScuba | Score | `visorscuba assess --db <DB>` |
| 8 | BARE | Rank | `bare --top 3` from findings.ndjson |
| 9 | VisorCorpus | Corpus | adversarial baseline for LLM-adjacent surface |
| 10 | VisorRAG | Verify (agentic) | `visorrag recall --target <ip>` (no LLM call in chain) |
| 11 | VisorAgent | (deep, controlled) | **INTENTIONALLY DEFERRED** — ethical-stop (see §4) |

`AIMAP_PORTS` (the survey-driven default set, #66): `80,443,1984,2379,3000,3001,4000,4040,4200,5000,5001,5678,6333,7575,7576,7860,8000,8001,8080,8081,8123,8233,8265,8443,8501,8787,8888,8889,9000,9090,9091,10000,11434,15500,18080,18789,19530,30000,51000,55000`

---

## 3. The orchestration layer

Three tools *run the chain* rather than occupying a single stage:

- **visor-chain-runner.sh** — the executable spine. Steps 0–11 over an IP list, one command.
- **VisorPlus** — the single-binary orchestrator; chains JAXEN → VisorSD → VisorCorpus → BARE → aimap hands-off, output landing in VisorLog.
- **osint-platoon** — a *multi-agent* orchestrator that runs inside Claude Code (not a standalone binary). Parallel `Agent` "squads" (Alpha/Bravo/Charlie/Weapons) under US Army **ATP 3-21.8** doctrine: each squad returns a SPOT report; the session synthesizes them into a SALUTE; `detailed` depth replans up to 3 iterations; `follow the pivot on X` re-tasks Bravo off a surfaced IP/domain/cert. It runs the **full arsenal per target**. In the chain-runner it is **step 3b, conditional** — parsed HIGH+/CRITICAL hosts get a deeper parallel dive. So osint-platoon is an *escalation orchestrator* at the Classify→deep-Verify boundary, not a single-stage tool. `cli.py --target <t> --dry-run` prints the METT-TC plan without firing squads.

The distinction: VisorPlus is linear single-host orchestration; osint-platoon is parallel multi-agent orchestration reserved for the high-value subset.

---

## 4. Off-linear and special-status tools

| Tool | Status | Where it actually fits |
|------|--------|------------------------|
| **VisorBishop** | On `/tools`, NOT a linear chain step | The productize-and-re-run tool (Fingerprint/Verify). Runs in iterative re-sweep loops over a corpus — "every survey runs twice"; iter-1 proved it doubles yield by checking 15 shadow ports vs 11 manual. |
| **VisorAgent** | Ethical-stop | Active LLM exploitation. Runs against **controlled/lab targets only**, never the survey set. Mark `[x] controlled target — not fired at survey set`. |
| **VisorHollow** | N/A on this platform | Windows process-injection detection benchmark. Cannot execute on a Linux/cloud OSINT corpus. Mark `[—] not applicable — Windows-only`. Not part of the OSINT pipeline at all; it is a separate defensive benchmark. |
| **Cortex** | Embedded | Authorization-context analyzer; reachable inside VisorRAG, not a standalone chain step. Verify stage. |
| **nu-recon** | The "19th" tool | Single-host passive deep-read. Documented in CLAUDE.md, absent from the website 18. Verify/Discover. |
| **JS-bundle extraction** | Skipped in batch | Verify-stage technique (CDN-SPA → largest JS asset → grep `api.<brand>` + `env.js` secrets, #19). Deferred to case-study-time, not run in the batch chain. |
| **`data/*-probe.py`** | Stopgap until aimap fingerprint exists | Category-specific Verify probes (`vllm-probe`, `mcp-probe`, `kubecost-opencost-probe`, …). The manual→productize→re-run loop: hand-walk to build the probe, then fold the fingerprint into aimap and re-run. A probe that survives is an aimap-fingerprint TODO. |

---

## 5. Why discovery is deliberately redundant

Stage 0 has five tools because they are **disjoint channels, not alternatives**
(#23, coverage is multiplicative). menlohunt only sees GCP; VisorGoose only
gov-TLD via CT logs; JAXEN walks Shodan; VisorSD sweeps ASN/org dorks;
recongraph expands a single seed polymorphically. Running one and skipping the
others undercounts the population in a way indistinguishable from a true
negative. #65 sharpens this: cert/Shodan-anchored discovery selects for the
auth-on managed class — pair it with direct masscan of cloud ranges to see the
auth-off class, and report both populations separately.

**Dual-stage tools.** VisorGraph and recongraph appear in both Discover and
Attribute: a cert-pivot is simultaneously a discovery vector (new SAN
subdomains → new seeds) and an attribution vector (cert O/CN → operator). That
dual role is the point of cert-anchored recon, not a classification error.

---

## 6. Quick tool catalog

| Tool | Lang | Stage(s) | One-liner |
|------|------|----------|-----------|
| JAXEN | Go | Discover | Stateful recon framework, deep TLS forensics; harvests → empire.db |
| VisorSD | Go | Discover | Shodan exposure scanner + ASN/org dork sweep + adversarial RAG |
| VisorGoose | Go | Discover | Gov-TLD AI discovery via CT logs + Shodan + DNS + Ollama fingerprint |
| menlohunt | Go | Discover | GCP External Attack Surface Management, chain detection |
| recongraph | Python | Discover/Attribute | Seed-polymorphic recon engine, environmental-contamination detection |
| aimap | Go | Fingerprint/Verify | "nmap for AI infra"; 69 fingerprints / 36 deep enumerators |
| aimap-profile | Python | Classify | Target classification (HIPAA/clinical/…/honeypot) + ethics + routing |
| VisorBishop | Go | Fingerprint/Verify | Cross-platform observability meta-fingerprinter, IP-direct-shadow; re-sweep loop |
| nu-recon | — | Verify | Single-host passive deep-read |
| Cortex | Go | Verify | Authorization-context analyzer (via VisorRAG) |
| VisorGraph | Go | Attribute/Discover | Infra mapping + cert-pivot operator attribution, gVisor sandbox |
| nuclide-contact | Python | Attribute | WHOIS → disclosure recipient |
| osint-platoon | Python/agentic | Classify/orchestration | ATP 3-21.8 multi-agent squad orchestrator; HIGH+/CRITICAL deep-dive |
| VisorLog | Go | Ledger | Append-only ECS-normalized findings ledger (nuclide.db), dashboard :8765 |
| VisorScuba | Go | Score | OPA/Rego AI-infra compliance (0–10), extends CISA ScubaGear |
| BARE | Rust | Rank | Air-gap-native semantic exploit→Metasploit-module mapping (offline) |
| VisorCorpus | Go | Corpus | Adversarial corpus generator (6 payload classes) for LLM/RAG |
| VisorRAG | Go | Verify (agentic) | RAG-grounded agentic recon CLI driving 6 live tools |
| VisorAgent | Go | deep (controlled) | Agentic LLM injection benchmark; ethical-stop, controlled targets only |
| VisorHollow | Go | N/A (Windows) | Process-injection detection benchmark + Sysmon validation |
| VisorPlus | Go | orchestration | Unified hunt/assess CLI orchestrating the suite |
| AI-LLM-OSINT | Markdown | Codify | Public OSINT catalog of exposure patterns (the published artifact) |

---

## See also
- `data/visor-chain-runner.sh` — the executable pipeline
- `~/.claude/nuclide-internal/METHODOLOGY.md` — the 8-stage methodology (note: summary only; 60 insight files are the full corpus)
- `methodology/insight-*.md` — the codified lessons cross-referenced above
- nuclide-research.com `/tools` (catalog) and `/stack` (per-class "How we test" restraint blocks)
