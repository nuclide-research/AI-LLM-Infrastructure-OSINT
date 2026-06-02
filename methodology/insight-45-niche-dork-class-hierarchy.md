---
type: methodology
insight_number: 45
title: "Niche Shodan dork yield follows a stable class hierarchy: Server-header > frontend-bundle-ID body > route-slug body. Route-slug dorks fail because Shodan crawls root HTML, not JS bundle source."
---

# Insight #45. Niche-dork class hierarchy in Shodan

_Source: LLM orchestration category-01 re-run, 2026-05-19. Of 52 niche dorks written for the re-run, 71% (37/52) returned zero hits. The 15 that succeeded sorted cleanly into three performance tiers._

## The rule

Shodan dork yield for AI/LLM infrastructure follows a stable three-tier class hierarchy:

```
Server-header dorks        ← highest yield, most reliable
  └─ "Server: llama.cpp"     → 1,638 hits
  └─ "Server: ollama"        → 593 hits (AS14061 alone)

Frontend bundle-ID body    ← medium yield, platform-dependent
  └─ http.html:"n8n-editor-ui"          → 66,802 hits
  └─ http.html:"\"chainlit\":{"         → 1,029 hits
  └─ ssl.cert.subject.cn:openai         → 965 hits

Route-slug body dorks      ← consistently zero
  └─ http.html:"/api/v1/chatflows"      → 0 hits
  └─ http.html:"/api/v1/prediction"     → 0 hits
  └─ [35 other route-slug variants]     → 0 hits
```

Route-slug dorks fail because Shodan's crawler indexes the root HTML response — not the JS bundle source. In modern SPA frameworks (React, Vue, Nuxt, Gatsby), route paths live exclusively in the JS bundle, which is fetched client-side after the root HTML loads. Shodan never executes the JS, so `/api/v1/chatflows` (a Flowise route) only appears in the bundle, not in any crawled HTML.

## Empirical basis (LLM orchestration re-run, 2026-05-19)

52 niche dorks written; 15 returned hits (29% success rate):

| Dork class | Hit rate | Best performer | Hits |
|---|---|---|---|
| Server-header | ~80% of written | `"Server: llama.cpp"` | 1,638 |
| Frontend bundle-ID body | ~40% of written | `http.html:"n8n-editor-ui"` | 66,802 |
| CN / cert field | ~60% of written | `ssl.cert.subject.cn:openai` | 965 |
| Route-slug body | **~3% of written** | (none succeeded reliably) | ~0 |
| Page-title only | ~50% of written | varies | low |

The 780/1,000 (78%) llama.cpp live-confirmation rate via `"Server: llama.cpp"` dork in the same session confirms that Server-header hits are not just indexed noise — they are the highest-precision, highest-yield class.

## Procedural rules this insight generates

1. **Write Server-header dorks first.** If the platform sets a recognizable `Server:` header (llama.cpp, Ollama, Triton, uvicorn with a recognizable suffix), that dork is the primary. It beats HTML body matching on both precision and yield.

2. **Frontend bundle-ID body is viable for platforms with distinctive static strings.** `n8n-editor-ui`, `chainlit`, `flowise`, `open-webui` all appear in root HTML (not just JS bundles) if the platform serves a recognizable page-level identifier in the initial HTTP response. Test one with a direct Shodan query before committing to it.

3. **Route-slug dorks are wasted query credits.** Do not write dorks of the form `http.html:"/api/v1/<endpoint>"` for modern SPAs. The endpoint path is never in Shodan's crawled index. The exception: platforms that serve non-SPA JSON APIs at root (e.g. llama.cpp's `/health` returns `{"status":"ok"}` as the root response) — but that is a JSON-field dork, not a route-slug dork.

4. **71% zero-hit rate is the expected budget.** In a new-category dork-writing session, expect most dorks to fail. Write 10-15 candidates; the 3-5 that land become the authoritative dork set. Do not interpret zero hits as "this platform is not deployed" without cross-validating against the Server-header and CT-log discovery channels.

5. **CT-log and port-first beats zero-yield Shodan dorks.** When all written dorks return zero, the platform is Shodan-dark for that dork class (see Insight #67 for voice/audio servers). Fall back to Censys CT-log sweep (Step 0b) and port-first discovery on the tier-2 cloud ranges.

## Relationship to prior insights

- **Insight #21 (port-first discovery for low-footprint platforms)**: the structural recommendation when dork-class hierarchy fails entirely. Port-first is the fallback when even Server-header dorks return zero.
- **Insight #67 (voice/audio AI API servers are Shodan-dark)**: the class of platforms where even tier-1 Server-header dorks fail because the platform returns JSON-only roots that Shodan cannot index as HTML.
- **Insight #7 (Shodan facet FP class)**: the inverse problem. This insight is about yield (too few hits); Insight #7 is about precision (too many false positives from over-broad dorks).

## See also

- `case-studies/commercial/llm-orchestration-rerun-2026-05-19.md` §11 (Codify, Candidate Insight #45)
- `methodology/insight-21-port-first-discovery-for-low-footprint-platforms.md`
- `methodology/insight-67-voice-api-servers-shodan-dark-json-root.md`
