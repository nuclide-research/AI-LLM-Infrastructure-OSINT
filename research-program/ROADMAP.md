# Roadmap

Decision log + survey queue. Append-only at the top; never rewrite past entries.

## 2026-06-07

### Done today

- [x] PAT secret set; auto-rebuild workflow operational (`nuclide-research.com` repo)
- [x] Mitnick-lens reframe: cert-pivot on disclosure-queue seeds → 3 sharpened findings + Insight #86 (disclosure pipeline as attack surface)
- [x] Disclosure-cohort response analysis (n=104, 7.4% closed-loop rate; institutional/academic carries the responsiveness)
- [x] Disclosure `outcome:` controlled vocabulary (`disclosures/SCHEMA.md`) + migration (7 files normalized)
- [x] d+30 follow-up worklist (82 silent cases sorted by age)
- [x] Longitudinal re-survey: Langfuse + RAGFlow + Phoenix (Day-1 baseline-comparison — falsification test requires longer pressure window)

### Queue deferrals (2026-06-07)

Honest scope: the survey queue items below each need a focused half-day session for full-arsenal discipline. Documenting what each one needs to start so the next session can pick one up cold.

- [ ] **Streamlit** — needs WebSocket probe class in herald (currently HTTP-only). Tool-build prerequisite: extend herald to speak WS handshake + a per-platform probe verb that does WS upgrade + initial-frame match. Population: ~24,500 indexed; the high-leverage start.
- [ ] **Helicone** — needs herald YAML config + Shodan dork validation. Population unknown (tier-2 LLM observability). Pre-work: ~30 min OSINT pass to identify a body fingerprint.
- [ ] **Opik** (Comet ML) — needs herald YAML + dork. CometML hosts a SaaS, so the indexed pop is the self-hosted tail; expect small-n.
- [ ] **PromptLayer** — same shape as Helicone/Opik. All three tier-2 platforms could be done in one batched session.
- [ ] **Mem0** — agent-memory layer. Prior survey notes exist; this is a re-survey + tome update.
- [ ] **FastGPT** — Chinese RAG. Larger pop expected. Cohort-cultural test: does the auth-default thesis hold in Chinese-jurisdiction maintainer space the way it does for Langfuse/RAGFlow? (RAGFlow itself is the existing Chinese data point; FastGPT is the second.)

### Queue cleared (resolved this session)

- [x] Insight #76 longitudinal re-survey — Langfuse / RAGFlow / Phoenix done at Day-1; see `research-program/longitudinal-resurvey-2026-06-07.md`. The 2-3 minor-version disclosure-pressure window is the actual test condition; Day-1 just nails the baseline.

## 2026-06-06

### Done today

- [x] Cat-LC LibreChat (3,153 indexed; 412/1,565 REGISTRATION_OPEN; 26.3% rate; v0.8.x = 10.3% cohort-corrected) — herald
- [x] Cat-OW Open WebUI (5,097 indexed; 603 findings; 11.8% rate) — Python probe
- [x] Cat-FW Flowise (841 indexed; 578 chatflow exposures; 68.7% rate; + CVE-2024-36420 PoC lab analysis) — Python probe
- [x] Cat-DF Dify (1,600 swept; 9 SIGNUP_OPEN + 939 CONFIG_DISC) — herald (1st survey)
- [x] AnythingLLM (232 swept; 0% open — population hardened or rotated) — herald
- [x] Cat-LF Langfuse (1,140 swept; 816 SIGNUP_OPEN; 88.9% rate) — herald
- [x] Cat-RF RAGFlow (1,905 swept; 618 REGISTER_OPEN; 87.2% rate) — herald + numeric coercion fix
- [x] Cat-PX Arize Phoenix (89 swept; 41/34 PROJECTS/USERS_UNAUTH) — herald
- [x] herald v0.1.1 public at github.com/nuclide-research/herald
- [x] Research-program directory scaffolded

### In progress

- [ ] Populate `roles/` from the 4 explicitly-stepped NICE pathways (422, 541, 631, 661)
- [ ] Populate `literature/threat-classes/` with OWASP LLM Top 10 (2025) categories
- [ ] Index all 41 NICE pathway PDFs (mechanical extraction)
- [ ] Index 355 aisecure papers (large effort, fan-out)
- [ ] State `disclosures/INDEX.md` with today's institutional findings

### Queued (next sessions)

- [ ] Streamlit (24,500 indexed) — needs WebSocket probe (not HTTP body parse)
- [ ] Helicone (LLM observability tier-2)
- [ ] Opik (Comet ML LLM observability)
- [ ] PromptLayer (LLM observability)
- [ ] Mem0 (agent memory) — small population, prior survey noted
- [ ] OpenHands (autonomous agent) — prior survey noted 61 verified
- [ ] LangGraph (agent framework) — prior survey #38
- [ ] Bisheng (Chinese LLM workflow builder — DataElem)
- [ ] FastGPT (Chinese RAG platform)
- [ ] Continue Insight #76 longitudinal — re-survey Langfuse + RAGFlow at v3.176 / v0.21+

### Decision log

- **2026-06-06**: chose `~/AI-LLM-Infrastructure-OSINT/research-program/` over standalone directory or private repo. Rationale: existing public repo, existing redaction discipline, single source of truth.
- **2026-06-06**: chose herald (declarative YAML) over per-survey Python scripts. Rationale: 8 platform configs already prove the abstraction; numeric type coercion bug found and fixed within hours of first cross-platform use.
- **2026-06-06**: chose "all three layered" indexing (research thread + NICE role + disclosure state). Rationale: maximum leverage; the work was already happening across all three; just needed the index.

## Earlier roadmap entries

Pre-2026-06-06 roadmap was tracked in `SESSION.md` and ad-hoc notes. See `~/AI-LLM-Infrastructure-OSINT/SESSION.md` for the prior session-by-session work log.
