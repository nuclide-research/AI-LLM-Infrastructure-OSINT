# Insights

Numbered methodology insights codified during the research program. The full canonical list lives in `~/.claude/nuclide-internal/` (insight-*.md files); this directory holds research-program-specific insights and the index that ties them to surveys.

## Active candidate insights

| ID | Title | First evidence | Status |
|---|---|---|---|
| #86 | The disclosure pipeline is itself an attack surface | 2026-06-07 audit of `disclosures/` (142 sent) + `INDEX.md` (~30 QUEUED, 0 in any post-send state) | Candidate (1 program-wide data point); detail at `~/AI-LLM-Infrastructure-OSINT/methodology/insight-86-disclosure-pipeline-is-attack-surface.md` |
| #76 | Auth-permissive defaults are the cohort norm for new-gen OSS AI/LLM infrastructure | 2026-06-06 Langfuse + RAGFlow + Phoenix triple survey | Candidate (3 data points) |
| #77 | Banner identity != schema; vector-use confirmation stays aimap's job | Cat-02 VectorDB survey | Codified (CLAUDE.md ref) |
| #75 | Reporting-gap-not-probing-gap | Cat-02 VectorDB round-3 | Codified |
| #74 | TBD | Cat-02 VectorDB round-3 | Codified |
| #73 | TBD | Cat-02 VectorDB round-3 | Codified |
| #72 | TBD | Cat-02 VectorDB round-3 | Codified |
| #71 | Argo/RAG/Service Mesh class | 2026-05-26 | Codified |
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
| (further insights as they emerge) | |

## Anti-insights (claims tested and broken)

| Claim | Broken by | Date |
|---|---|---|
| "AnythingLLM browser-UI-unauth rate is durable" | Re-survey 2026-06-06: 0/27 reachable open | 2026-06-06 |
| (TBD) | | |
