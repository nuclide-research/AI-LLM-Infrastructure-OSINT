# Session Analysis: Censys x OSINT-repo Cross-Reference

**Date:** 2026-05-31
**Type:** Cross-reference pass (Stage 0b feeding the existing corpus), not a fresh survey.
**Operator:** Nuclide (Nick + Claude)
**Credits:** 17 of 24 Free-tier weekly (24 -> 7, resets 2026-06-08)

## 1. Overview

Nick directive: "using censys, cross reference our llm osint repo research." Censys is the
newly-codified chain step 0b. The deliverable per methodology is the DELTA Censys adds over
our Shodan-sourced surveys: ports, certs, and auth-state our surveys could not see. The pass
targeted the repo's own flagged Shodan-dark gaps (where the delta is guaranteed non-empty)
and a confirmed-unauth RAG sample. All reads passive; no host was connected to.

## 2. Tooling

- cencli (Censys Platform CLI, Go, ~/go/bin) `view` and `credits`. 1 credit per host view.
- nuclide.db `events` ledger (25,810 events) for the confirmed corpus.
- jq for record parsing. No bespoke probe loops written (none needed; cencli covers it).
- Non-runs: cencli `search` (403 on Free, needs paid org-id) -> population lane deferred to
  web-UI/Playwright. VisorAgent (controlled-target only). VisorHollow (Windows).

## 3. Methodology

Sample-then-scale on credits: validated per-view cost (exactly 1) and output shape on one
known-rich host before batching. Primary source over notes: re-ran `cencli credits` rather
than trusting SESSION.md ("no PAT") or METHODOLOGY ("token configured"); the live probe
settled it (authenticated, 24 credits). Banner-verified every Censys software label against
the HTTP/protocol decode in the same record before believing it.

## 4. Execution trace

1. Read METHODOLOGY.md, SESSION.md, MEMORY index. Posted arsenal checklist.
2. Verified cencli auth state: `config print` (no visible token) then `credits` (200 OK, 24).
   Confirmed Free-tier split: view works, search 403.
3. Cost calibration: `view 100.23.189.139` (Argo cert host) -> 1 credit, no services (quiet).
4. Services-on-Free test: `view 152.53.91.184` (LightRAG) -> 7 services returned. Confirmed
   Free returns full services.
5. Argo 2746 dark tier: `view --input-file` x5 then x3 cross-provider -> 0/8 show :2746.
6. RAG shadow: `view --input-file` x7 -> full-port shadow parsed; auth-decoders read.
7. Wrote findings-breakdown, this analysis. SESSION.md and memory updated.

## 5. Findings (evidence-gated)

- **INFO / negative (inner-B, outer-1):** Argo Cat-29 port-2746 dark tier is invisible to
  Censys too (0/8 hosts show 2746, cross-provider Alibaba+Tencent). Closes the "Censys
  cross-check skipped" gap. Evidence: 8 cencli view records, service_count and port arrays.
- **LOW / enrichment (inner-B, outer-1):** 148.113.183.4 (Perplexica) exposes 10 services;
  Censys decoders show Postgres (demands creds), Redis (NOAUTH required), Coolify (login-gated)
  are all AUTH-ENFORCED. No new unauth finding. Evidence: postgres.startup_error,
  redis.ping_response in the saved record.
- **LOW / enrichment:** 152.53.91.184 (LightRAG) runs >= 2 AI apps on one IP (LightRAG :9621,
  RefChecker :8000) + OTLP + TensorBoard + ssh. Censys :8000 "neo4j" label is a FP (banner =
  RefChecker SPA). Second-app unauth NOT verified (200 SPA = identity).
- **LOW / attribution:** 60.205.196.161 :443 serves a branded Xiaohui AI customer-service
  frontend (operator identity the bare-port AnythingLLM probe missed).
- **RE-VERIFY FLAG:** 82.156.224.203 tagged "docsgpt" #36145, but Censys shows Home Assistant
  + CUPS, no DocsGPT. Possible survey FP or host repurposed.

## 6. Risk assessment

No new exposed-data finding was created by this pass. Its value is corrective and
expansionary: it disqualified an apparent multi-DB catastrophe (148.x) down to a single
app-tier exposure, surfaced a likely survey misclassification (82.x DocsGPT), and confirmed
a dark tier is genuinely unreachable rather than merely Shodan-blind. The model risk it
controls is the population-scale overclaim: a Censys port list read without the decoders
would have inflated the unauth count.

## 7. Recommendations / next

1. Population-delta lane via web UI (free, Playwright): R2R 7272, Cognita/Verba 8000, RAGFlow
   1674, then cross-category. This is the half of the cross-reference cencli Free cannot do.
2. Codify candidate Insight #70 (Censys dual primitive: full-range ports + auth-decoders;
   label is identity, decoder is auth-state).
3. Ledger updates (proposed, await go): append cross-ref notes to the relevant events;
   re-verify #36145 (DocsGPT -> Home Assistant) before it propagates.

## 8. Limitations

- Free tier gates some advanced-protocol fields; `search` blocked (org-id). Population delta
  not measured this session.
- Per-host credit budget (24/week) caps breadth. This pass was 16 hosts; deliberately narrow.
- Argo 2746 sample is the dark tier by definition (Alibaba/Tencent), so not provider-general
  beyond that tier.

## 9. PoC illustrations

- Redis auth-state without connecting: `redis.ping_response = "NOAUTH Authentication required"`
  in the Censys view of 148.113.183.4:6379. The host was never contacted by us.
- Full-port delta: survey logged 1 port on 148.113.183.4; Censys view returned 10.
