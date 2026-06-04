# Analysis — Cat-01 LLM Orchestration virgin re-birth + Censys onboarding

**Date:** 2026-06-04
**Arc:** one session: Stage -1 agentic intel → Shodan deep-pull → 11 new aimap fingerprints →
verification sweep → Censys Platform onboarding + credit-cache tooling → ledger.

## 1. Overview
Cat-01 was treated as a **virgin category** (Nick directive): no prior Stage -1 intel doc existed;
the 05-15/05-19 runs jumped to harvest on inherited dorks. This session built the category from
primary sources and, mid-stream, onboarded a newly-purchased Censys Platform account into the methodology.

## 2. Tooling
- **OSINT Platoon** (6 parallel Sonnet research squads) — 25 platforms, 6 research lanes each.
- **Shodan** (Freelance) — `shodan download` deep-pull; `shodan stats` facet triage. CLI repaired (setuptools<81).
- **aimap v1.9.46** — 11 NEW fingerprints added (Langflow, LibreChat, LobeChat, big-AGI, FastGPT, Coze,
  BISHENG, Chainlit, Cheshire Cat, Khoj, h2oGPT); grouped-by-known-open-port sweep (timeout-avoidance).
- **agent-logging-system** — FP monitor (Chainlit 100% FP flagged).
- **Censys Platform** — onboarded; reference at `data/censys-platform-reference.md`; new tool
  `censys-cache` (github.com/nuclide-research/censys-cache, PRIVATE) dedups searches.
- **VisorLog** — 2,254 events ingested. VisorScuba — scoring.

## 3. Methodology notes
- **Grouped-by-known-open-port sweep**: scanning only the ports Shodan reported open per host
  eliminated the dead-port timeout storm (a blind 21-port sweep extrapolated to ~6h; grouped ≈ minutes).
  New reusable pattern; respects the home-uplink constraint.
- **Censys credit model MEASURED**: search=5cr flat (any pages), aggregate=5cr, view=1cr, cache-hit=0.
  Earlier "CLI cheaper / aggregate cheap" assumptions were WRONG and corrected. Policy: Shodan-first,
  Censys only when structurally blind, prefer view(1cr), cache everything.
- **Bandwidth discipline**: killed the 443/80 aimap groups mid-run (Nick flagged uplink saturation);
  reverse-proxied tier reassigned to Censys (zero-uplink). Saved [[feedback-throttle-scans-home-internet]].

## 4. Findings (evidence-gated) — see recon findings-breakdown.txt
- **CRITICAL**: 13 Flowise unauth credential-endpoint hosts (3 with stored creds); 98 critical events total.
  Censys-enriched: 4/13 expose shadow MySQL; named operators via free cert-pivot; 2 hosts cross-correlated
  to one operator (amvader.net); stacked control-planes (Coolify+Portainer, Dify+Ollama).
- **MEDIUM headline / verification win**: OpenClaw 598 Control UIs exposed but **token-gated** — REFUTES
  the web-sourced "92% unauth" claim. False-critical avoided (Insight #16).
- **NEGATIVES (publishable)**: Cheshire Cat 0/292, Khoj 0/490 (noisy-port dorks, 0 FPs from new fingerprints);
  Langflow title-farm (96k titled, ~0 real); Jan unmappable on Shodan.

## 5. Risk assessment
The category's auth-on-default thesis holds hard: builder/chat-UI/local-runtime tier is auth-off or
claimable by default; only architecturally-DB-backed platforms (Chatbot UI, LobeChat Mode-B) resist.
Real critical risk concentrates in Flowise (unauth credential store + CVE) and the stacked-host chains,
not the large populations (OpenClaw/LibreChat are medium). Population size and severity were inversely correlated.

## 6. Limitations / negative space
- Reverse-proxied 443/80 tier and the 7860 (Langflow/h2oGPT) tier NOT actively swept — Censys-deferred.
- LibreChat auth-state unread (enumerator gap). Coze fingerprint marker wrong (`@coze-studio/app`).
- 2026-dated CVEs from squads are unverified leads, not asserted facts.
- Censys host history on Starter = 1 week (staleness bound on view data).

## 7. Round-2 (every survey runs twice)
VisorCAS signatures: Chainlit-MCP-collision, (Coze-marker). Fingerprint fixes: Coze `@coze-studio/app`,
LibreChat auth-read. Censys sweep of 443/80 + 7860 tiers. tiptoe shadow on any non-Censys-covered confirmed host.

## 8. Candidate Insights
- **#71** — unauth config endpoint collapses identity-vs-auth-state for the chat-UI tier.
- **Verification-refutes-framing** — OpenClaw 92%-unauth web claim refuted by live probe.
- **Censys dual-primitive at 1 credit** — view = shadow-port map + cert-pivot + data-tier auth, zero uplink.

## Toolchain provenance
OSINT Platoon (Agent x6) → shodan download/stats → aimap (11 new FPs) grouped sweep →
agent-logging-system monitor → Censys view enrichment (censys-cache) → aimap-to-findings → visorlog ingest →
visorscuba. Recon dir: ~/recon/01-llm-orchestration-2026-06-04/.
