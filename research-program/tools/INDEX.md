# Tools

NuClide tool family. Each tool has its own design-notes file in this directory linking to the source repo and documenting research-program-relevant design decisions.

The full 19-tool arsenal is canonical in `~/.claude/CLAUDE.md` Tool Inventory section. This index covers the subset relevant to the AI/LLM infrastructure research program, plus newly built tools.

## Core arsenal (research-program-active)

| Tool | Layer | Repo | Detail |
|---|---|---|---|
| **aimap** | L4 TCP/TLS fingerprinting + service deep enum | `github.com/Nicholas-Kloster/aimap` | [aimap.md](aimap.md) |
| **aimap-profile** | L7 target classification + ethics flags | `github.com/Nicholas-Kloster/aimap` (subpath) | [aimap-profile.md](aimap-profile.md) |
| **scanner** | L5 liveness + banner + version | (NuClide internal) | [scanner.md](scanner.md) |
| **herald** | L7 HTTP application-layer auth probe | `github.com/nuclide-research/herald` | [herald.md](herald.md) |
| **VisorLog** | Ledger ingest (nuclide.db) | (NuClide internal) | [visorlog.md](visorlog.md) |
| **VisorCAS** | False-positive ledger (CAS + bloom) | `~/visorcas/` | [visorcas.md](visorcas.md) |
| **VisorGraph** | Cert pivot + operator attribution | `~/go-engine/` | [visorgraph.md](visorgraph.md) |
| **BARE** | Semantic exploit module ranking | `github.com/Nicholas-Kloster/BARE` | [bare.md](bare.md) |
| **VisorPlus** | 6-phase passive recon per host | (NuClide internal) | (tbd) |
| **VisorRAG** | Prior findings recall per host | (NuClide internal) | (tbd) |
| **VisorCorpus** | Adversarial prompt corpus build | (NuClide internal) | (tbd) |
| **agent-logging-system** | Post-aimap per-enumerator FP-candidate scan | `~/agent-logging-system/` | (tbd) |

## Reference platforms (third-party, studied)

| Tool | Why studied | Path |
|---|---|---|
| **PentAGI** | Multi-agent pentest orchestrator architecture reference | `~/Tools/web-pentest/pentagi/` |
| **menlohunt** | GCP/AWS EASM tool — used in chain step | (NuClide-adjacent) |
| **recongraph** | Seed-polymorphic recon engine — typed provenance graphs | `~/Videos/jax/recongraph/` |

## Tool-family architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ Stage 0:   shodan / Censys harvest                               │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 0c:  scanner — TCP/TLS liveness + banner + version         │
│            (drops stale ~71% of Shodan candidates; gives clean   │
│             live subset to aimap)                                │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1b:  aimap — L4 fingerprint + service deep enum            │
│            (answers "what is this?")                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 1b': herald — L7 HTTP application-layer auth probe         │
│            (answers "is this open?")                             │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3:   aimap-profile — target classification + ethics flags  │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 3v:  manual verification (load-bearing)                    │
└──────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Stage 6:   VisorLog — ledger ingest                              │
│ Stage 7:   VisorScuba — compliance scoring                       │
│ Stage 8:   BARE — semantic exploit module ranking                │
│ Stage 12:  visor-report — drill-down HTML report from ledger     │
└──────────────────────────────────────────────────────────────────┘
```

Each tool's responsibility is distinct. herald, the newest, sits at L7 and asks the auth question — a slot that was previously filled by ad-hoc per-survey Python scripts.

## Tool development log (research-program-relevant)

| Date | Tool | Change | Driven by |
|---|---|---|---|
| 2026-06-06 | herald v0.1.0 | Initial public release with 6 platforms | Dify survey + cross-survey pattern |
| 2026-06-06 | herald v0.1.1 | Numeric type coercion fix (YAML int / JSON float64) | RAGFlow survey calibration found YAML int vs JSON float mismatch |
| 2026-06-06 | herald | Phoenix platform config added | LLM02-class disclosure pattern |
| (earlier) | aimap v1.9.52 | LLaMA-Factory FP fix (1MB body-read cap → `/gradio_api/info` probe) | Cat-04 training survey |
| (earlier) | aimap v1.9.53 | 5 FPs fixed (GPT Researcher, Lunary, h2oGPT, Coqui/Chatterbox TTS, KoboldCpp) | Cat-03 model serving survey |
| (earlier) | scanner | TCP/TLS Shodan-clone, aimap-integrated | Standing requirement after every Shodan/Censys harvest |
