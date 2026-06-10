# Insights

Numbered methodology insights codified during the research program. The full canonical list lives in `~/.claude/nuclide-internal/` (insight-*.md files); this directory holds research-program-specific insights and the index that ties them to surveys.

## Active candidate insights

| ID | Title | First evidence | Status |
|---|---|---|---|
| #102 | Shodan favicon-hash dorks dominate HTML-body substring dorks (16,623 vs 10,675; 1.56x raw, ~10x per-query yield) | 2026-06-09 LJP-OSS Lane E discovery scale-up | Candidate (1 data point) |
| #101 | LJP-OSS client bundles do not leak customer-side identifiers at population scale (0/471 bundles, 0/403 source maps) | 2026-06-09 LJP-OSS Lane D | Candidate (1 data point) |
| #100 | Operator self-branding overwhelms tenant co-branding for LLM-relay SaaS (0/765 head blocks) | 2026-06-09 LJP-OSS Lane C | Candidate (1 data point) |
| #99 | OIDC discovery is not viable for LLM-relay customer attribution (0/2,455 probes returned parseable OIDC) | 2026-06-09 LJP-OSS Lane C | Candidate (1 data point) |
| #98 | Tool-hub itself is the supply-chain recon surface for pool-of-tools LLM agents | 2026-06-09 paper-mine of Li et al. (NDSS 2026, XTHP, 66 tools, 75% susceptible) | Candidate (1 academic data point + 6 attack-vector taxonomy); survey-category candidate POTAS |
| #97 | Doc-AI production microservices are a schema-leak class (Gateway / Inference / MLflow triad) | 2026-06-09 paper-mine of Fehlis et al. (Kungfu.AI, arXiv 2605.18818, 2026) | Candidate (1 reference architecture); survey-category candidate DAPMS |
| #96 | SSE field names are platform fingerprints for cloud LLM SaaS | 2026-06-09 paper-mine of Ablove et al. (NDSS 2026, 5 CN LLM services) | Candidate (1 academic data point, 5 named operators); survey-category candidate Cloud-LLM-SSE |
| #86 | The disclosure pipeline is itself an attack surface | 2026-06-07 audit of `disclosures/` (142 sent) + `INDEX.md` (~30 QUEUED, 0 in any post-send state) | Candidate (1 program-wide data point); detail at `~/AI-LLM-Infrastructure-OSINT/methodology/insight-86-disclosure-pipeline-is-attack-surface.md` |
| #76 | Auth-permissive defaults are the cohort norm for new-gen OSS AI/LLM infrastructure | 2026-06-06 Langfuse + RAGFlow + Phoenix triple survey | Candidate (3 data points) |
| #77 | Banner identity != schema; vector-use confirmation stays aimap's job | Cat-02 VectorDB survey | Codified (CLAUDE.md ref) |
| #75 | Reporting-gap-not-probing-gap | Cat-02 VectorDB round-3 | Codified |
| #74 | TBD | Cat-02 VectorDB round-3 | Codified |
| #73 | TBD | Cat-02 VectorDB round-3 | Codified |
| #72 | TBD | Cat-02 VectorDB round-3 | Codified |
| #71 | Argo/RAG/Service Mesh class | 2026-05-26 | Codified |
| #79 | LLM-Jacking Productized OSS Proxy Ecosystem (Cat-XX founding); 12,577-host population, 50% US-hosted, X.ai/OpenAI/Anthropic/Gemini upstream laundering | syllabus wandb sweep follow-up | Codified |
| #78 | Identity surface vs auth-bearing surface; classify access only on the surface the platform gates by design | Syllabus reverify + Cambridge near-miss | Codified (Candidate) |
| #70 | label=identity vs decoder=auth-state | Censys credit study | Codified |
| #68 | Findings = Depth(A/B) x Breadth(0/1/2) pair; NuClide restraint = high-depth/low-breadth by choice | Verification rung grid | Codified |
| #60–#76 | Various — see canonical insight files | 2026-05-12 to 2026-06-06 | Codified |
| #49 | 3 .edu shared Ollama Connect cloud portfolio | 2026-05-15 | Codified (Candidate) |
| #40 | Auth-on-default strengthens across OSS generations under disclosure pressure | Multi-survey | Codified |
| #39 | Pooled-account proxy = attribution-laundering; disclose to vendor | LLM-jacking proxy survey | Codified |
| #31 | App-builder tools brand the OUTPUT, not the AGENT; anchor verify on agent API contract | App-builder survey | Codified |
| #12 | Operator who ships one service auth-off ships others auth-off (stacked catastrophe) | Cat-05 UQConnect | Codified |
| #8 | signUpDisabled:false = anyone registers (effective unauth) | Langfuse survey precursor | Codified |

(Earlier insights #1–#76 are in `~/.claude/nuclide-internal/`. This index focuses on research-program-active ones.)

## Detail files in this directory

| File | Topic |
|---|---|
| `76-auth-permissive-cohort-default.md` | The central thesis being tested by the 2026-06-06 surveys |
| `78-identity-vs-auth-bearing-surface.md` | Identity surface vs auth-bearing surface |
| `79-llm-jacking-productized-ecosystem.md` | LJP-OSS founding (Cat-XX) |
| `96-sse-field-name-as-platform-fingerprint.md` | Cloud LLM SaaS SSE schema = operator fingerprint (paper-mined from Ablove NDSS 2026) |
| `97-doc-ai-microservice-as-schema-leak-class.md` | Doc-AI production stack (Gateway / Inference / MLflow) as a schema-leak survey category (paper-mined from Fehlis arXiv 2605.18818) |
| `99-oidc-discovery-not-viable-llm-relay-attribution.md` | OIDC discovery not viable for LLM-relay customer attribution (LJP-OSS Lane C) |
| `100-operator-self-branding-overwhelms-tenant-co-branding.md` | Operator self-branding overwhelms tenant co-branding (LJP-OSS Lane C) |
| `101-ljp-oss-client-bundles-do-not-leak-customer-identifiers.md` | JS bundles do not leak customer-side identifiers (LJP-OSS Lane D) |
| `102-favicon-hash-dominates-html-substring-for-discovery.md` | Shodan favicon-hash dorks dominate HTML-body substring (LJP-OSS Lane E) |
| `98-tool-hub-as-supply-chain-recon-surface.md` | Pool-of-tools agent tool-hubs as supply-chain recon surface (paper-mined from Li NDSS 2026) |
| (further insights as they emerge) | |

## Anti-insights (claims tested and broken)

| Claim | Broken by | Date |
|---|---|---|
| "AnythingLLM browser-UI-unauth rate is durable" | Re-survey 2026-06-06: 0/27 reachable open | 2026-06-06 |
| (TBD) | | |
