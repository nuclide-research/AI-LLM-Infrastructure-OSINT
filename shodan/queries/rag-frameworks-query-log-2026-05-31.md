# Cat-07 RAG Frameworks — Shodan Query Log (2026-05-31)
Playwright web UI, VPN: Mullvad US. Zero = result. "Harvested" = unique IPs pulled into the corpus.

| Platform | Dork | Shodan hits | Harvested | Notes |
|---|---|---|---|---|
| RAGFlow | `http.html:"ragflow"` (favicon dork stale=0) | 1,674 | 17 | default-creds admin@ragflow.io/admin + CVE-2024-12433 RCE; ~50% FP expected (Insight #15); sampled for chain |
| AnythingLLM | `http.title:"AnythingLLM" port:3001` | 154 | 30 | auth-off-default (single-user); sampled |
| Onyx | `http.title:"Onyx" port:3000` | 71 | 30 | configurable auth (AUTH_TYPE=disabled possible); sampled |
| Perplexica | `http.title:"Perplexica"` | 64 | 20 | no-auth-by-default; LLM API keys in config.toml; sampled |
| Kotaemon | `http.html:"kotaemon"` | 17 | 16 | default-creds admin/admin; full |
| DocsGPT | `http.html:"DocsGPT"` | 14 | 13 | auth-off-default; CVE-2025-0868 pre-auth RCE; full |
| PrivateGPT | `http.html:"privateGPT"` (`:8001` lock=0) | 8 | 8 | auth-off-default; variant rescued the dork; full |
| Quivr | `http.html:"quivr"` | 8 | 8 | auth-on-default (Supabase JWT); identity-only; full |
| Ragapp | `http.html:"ragapp"` | 4 | 4 | no-auth-by-design; /admin + /api/management/config; full |
| txtai | `http.html:"txtai"` | 3 | 2 | auth-off-default; full |
| Danswer | `http.title:"Danswer" port:3000` | 0 | 0 | fully rebranded to Onyx |
| LightRAG | `port:9621 http.html:"LightRAG"` | 0 | 0 | Shodan-dark: SPA does not render name; port 9621 bare=519 but Chinese-cloud/WAF noise. Needs masscan + /health probe (Insight #21). |
| Cognita | `http.html:"cognita"+"truefoundry"` (+truefoundry alone) | 0 | 0 | Shodan-dark SPA |
| R2R | `port:7272 http.html:"r2r"` | 0 | 0 | Shodan-dark: JSON API, no HTML to index. Needs masscan 7272 + /v3/health probe. |
| Verba | `http.html:"goldenverba"` | 0 | 0 | Shodan-dark Next.js SPA |

**Totals:** 15 dorks run · 10 platforms returned hits · 5 returned 0 (1 rebrand-dead, 4 Shodan-dark SPA/JSON-API) · **148 unique IPs harvested** for the chain.

**Population note:** RAGFlow's 1,674 dominates but is HTML-renderer-biased and ~50% FP per Insight #15. The auth-off-default SPA tier (LightRAG, Cognita, R2R, Verba) is Shodan-dark — the same HTML-renderer-vs-SPA split seen in Cat-29 and Insight #21. True population for those requires masscan + port-probe.

## Censys Platform queries (manual web UI, Free tier, 2026-05-31)
Logged by the same standing rule. "Confirmed/Unauth" = after our verification probe.

| Query (CenQL) | Censys hits | Harvested | Result |
|---|---|---|---|
| `host.services.banner: "LightRAG"` | gated | 0 | banner field Starter-gated on Free tier |
| `host.services.port=9621` | ~1.2K | — | faceted: uvicorn 331; vs Shodan's undifferentiated 519 noise |
| `host.services.port=9621 and host.services.software.product="uvicorn"` | 185 | 100 | LightRAG candidates → 81 confirmed, **36 UNAUTH** |

**Censys recovered the Shodan-dark LightRAG tier:** Shodan HTML dork = 0; Censys = 185 candidates, 36 unauth confirmed. First NuClide finding sourced entirely from Censys. R2R (7272) and Cognita/Verba (8000) reachable the same way next.
