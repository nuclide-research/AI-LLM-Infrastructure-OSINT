---
type: case-study
category: 07
platform: RAG Framework Servers (multi-platform)
survey_date: 2026-05-31
status: complete
findings: 33 unauthenticated confirmed (AnythingLLM 20, Perplexica 11, DocsGPT 1, Ragapp 1)
verification_rung: inner-B / outer-2 (AnythingLLM auth-state read from the API itself across a fingerprinted population sample); restraint held at metadata
---

# RAG Framework Servers Population Survey — Cat-07 (2026-05-31)

_NuClide Research · 2026-05-31_

---

## Scope

First population survey of the RAG-framework-server category. 16 platforms in the 2026-05-27 pre-assessment intel (`data/platform-intel/rag-frameworks-osint-2026-05-27.md`); 15 dorks run this session. The category spans private document-QA workspaces, RAG pipelines, agentic-RAG, and self-hosted AI search — platforms whose value is the *document corpus and connected LLM API keys*, not just compute.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, S7076, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7052, S7056, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, K7041, T5896

<!-- ksat-tag:auto-generated:end -->

aimap v1.9.41 shipped 13 new fingerprints for this survey (LightRAG, PrivateGPT, txtai, Cognita, R2R, Kotaemon, Quivr, Danswer/Onyx, Verba, DocsGPT, Ragapp, Perplexica, RAGFlow); AnythingLLM/Flowise/Dify already shipped.

---

## Discovery (15 dorks, query-log with hit + harvested counts)

| Platform | Dork | Shodan hits | Harvested | Auth default |
|---|---|---|---|---|
| RAGFlow | `http.html:"ragflow"` | 1,674 | 17 | default-creds |
| AnythingLLM | `http.title:"AnythingLLM" port:3001` | 154 | 30 | off (single-user) |
| Onyx | `http.title:"Onyx" port:3000` | 71 | 30 | configurable |
| Perplexica | `http.title:"Perplexica"` | 64 | 20 | off |
| Kotaemon | `http.html:"kotaemon"` | 17 | 16 | default-creds |
| DocsGPT | `http.html:"DocsGPT"` | 14 | 13 | off |
| PrivateGPT | `http.html:"privateGPT"` | 8 | 8 | off |
| Quivr | `http.html:"quivr"` | 8 | 8 | on |
| Ragapp | `http.html:"ragapp"` | 4 | 4 | off (by design) |
| txtai | `http.html:"txtai"` | 3 | 2 | off |
| Danswer | `http.title:"Danswer" port:3000` | 0 | 0 | rebranded → Onyx |
| LightRAG | `port:9621 http.html:"LightRAG"` | 0 | 0 | Shodan-dark SPA |
| Cognita | `http.html:"cognita"+"truefoundry"` | 0 | 0 | Shodan-dark SPA |
| R2R | `port:7272 http.html:"r2r"` | 0 | 0 | Shodan-dark JSON API |
| Verba | `http.html:"goldenverba"` | 0 | 0 | Shodan-dark SPA |

**148 unique IPs harvested.** Two dork-design lessons:
- **Variant-rescue:** PrivateGPT's `port:8001` lock returned 0; dropping the port to `http.html:"privateGPT"` returned 8. The port assumption was wrong, not the platform.
- **RAGFlow favicon hash was stale** (`-1467534538` → 0); the `http.html:"ragflow"` string returned 1,674.

**The HTML-renderer vs SPA/JSON split (Insight #21, category-wide):** platforms that server-render their name (AnythingLLM, Onyx, Perplexica, Kotaemon, DocsGPT, RAGFlow) are Shodan-visible; SPA/JSON-API platforms (LightRAG, Cognita, R2R, Verba) render nothing to the crawler and returned 0 on every HTML dork — they are Shodan-dark and need masscan + port-probe. This is the same split documented in Cat-29.

---

## Verification — THE load-bearing stage (33 unauth confirmed)

Per-platform distinctive-endpoint auth probe. Restraint: auth-state only — no documents read, no credentials tested, no config dumped.

| Platform | Reachable | UNAUTH | auth-enforced | Rate (reachable) |
|---|---|---|---|---|
| **AnythingLLM** | 28 | **20** | 8 | **71%** |
| **Perplexica** | 11 | **11** | 0 | 100% |
| **DocsGPT** | 1 | **1** | 0 | api-keys exposed |
| **Ragapp** | 1 | **1** | 0 | open admin |
| Onyx | 24 | 0 | 24 | 0% (auth-on holds) |
| Kotaemon | 11 | (gate) | — | default admin/admin documented, NOT tested |
| RAGFlow / Quivr / txtai / PrivateGPT | — | 0 | partial | mostly behind 443 proxy on non-probed ports |

**AnythingLLM is the strongest result and a clean inner-B signal:** `/api/setup-complete` returns `{"results":{"RequiresAuth":false,...}}` — the application's own API reports authentication disabled. This is not a "200 = unauth" inference (Insight #16); it is the auth state read from the data layer. 20 of 28 reachable hosts report `RequiresAuth:false`, exposing workspace documents, full chat history, and connected OpenAI/Anthropic API keys.

**Perplexica** ships no auth layer by design; all 11 reachable hosts serve the UI and expose `config.toml` LLM API keys. **DocsGPT** `82.156.224.203` exposed `/api/get_api_keys` unauthenticated (and the population sits in the CVE-2025-0868 pre-auth RCE window). **Ragapp** `13.60.85.230` serves `/admin` open by design.

**Onyx holds the auth-on line:** 24/24 reachable returned 401/403 on `/api/me`. The `AUTH_TYPE=disabled` deployment exists but none in this sample used it.

The no-response rows are reachability artifacts (apps behind a 443 reverse proxy on ports the probe did not hit), counted **inconclusive, not secure**.

**Thesis result:** auth-off-default platforms (AnythingLLM 71%, Perplexica 100%-reachable, Ragapp, DocsGPT) confirm the auth-on-default thesis at population scale. The one auth-on-default platform reached (Onyx) held at 0% unauth. Textbook contrapositive confirmation.

---

## Shadow finding — RAG hosts co-deploy a stack (Insight #12)

aimap fingerprinted **152 services across the 148 hosts** — more services than hosts. Beyond the RAG apps themselves, the IP-direct fingerprint surfaced co-located services on the same operators:

| Co-located service | Count | Significance |
|---|---|---|
| **MCP Server** | 39 | RAG operators wiring Model Context Protocol tool servers alongside — a second unauthenticated-RPC surface |
| Grafana | 15 | monitoring stack |
| Perplexica | 11 | (primary) |
| Coqui XTTS | 10 | voice TTS co-located (candidate — shared Gradio port 7860, verify before trusting) |
| Metabase | 9 | BI dashboard |
| Open WebUI | 5 | LLM chat UI |
| GPT Researcher | 2 | agentic research |

The 39 MCP servers are the highest-value shadow signal: operators who stand up an unauthenticated RAG app frequently co-deploy an MCP server (filesystem/shell/DB tools) on the same host. This is the Insight #12 pattern (operators who ship one service auth-off ship others auth-off) at the category level. The Coqui XTTS / port-7860 matches are flagged as candidates pending verification (shared Gradio port — possible FP, the Cat-29 lesson).

---

## Attribution (VisorGraph cert-pivot)

27 operator domains recovered from cert SANs / rDNS:
- `privategpt.com.br` — Brazilian PrivateGPT deployment
- `ragflow-pilot.germanywestcentral.cloudapp.azure.com` — RAGFlow pilot on Azure
- `crm.enersun.com.ua` — Ukrainian solar-energy company CRM running RAG
- `chat.dev.dodda.ai`, `chat.dev.api.dodda.ai` — AI startup dev
- `gather.switchboardcan.ai`, `companion.nikolairuh.online`, `escolarbot.lat`, `digitalux.mx`

Yandex Cloud Kafka/MDB broker hostnames appeared adjacent to several seeds — data infrastructure co-located with the RAG layer.

**Corpus composition: heavily Chinese cloud** (Alibaba/ALISOFT, Tencent) plus EU (OVH, Hetzner) and a long tail. A different operator population than Cat-29's GCP/AWS/IAP tier — and notably one with far weaker default auth posture.

---

## Toolchain Provenance (graded REAL / DEGRADED / NULL / BLOCKED)

```
Stage -1:      REAL     16-platform pre-assessment intel (2026-05-27), read not re-derived
aimap:         REAL     v1.9.41 +13 RAG fingerprints; 152 services/148 hosts; AnythingLLM 45,
                        MCP 39 (shadow), Grafana 15, Perplexica 11, Metabase 9, Kotaemon 6, RAGFlow 5
JAXEN:         REAL     15 dorks, 148 IPs, query log with hit+harvested counts
Verification:  REAL     per-platform auth probe → 33 unauth confirmed (THE result)
VisorGraph:    REAL     27 operator domains via cert-pivot
BARE:          REAL     6 findings → 0 MSF matches (all first-party app bugs; RAGFlow RCE closest 0.525)
VisorLog:      REAL     33 findings #36125-36157 (DocsGPT api-key host = critical)
VisorScuba:    DEGRADED whole-DB assess; survey nodes lack enrichment for a per-survey score
VisorCorpus:   REAL     137 adversarial prompts — KB-exfil + prompt-injection classes genuinely
                        apply to RAG (unlike Cat-29's non-LLM Argo target)
VisorAgent:    N/A-RUN  corpus-only (ethical-stop; not fired at operator hosts)
VisorGoose:    REAL     0 gov/edu nodes — correct, RAG corpus is commercial
menlohunt:     PARTIAL  only 3 GCP-range IPs in corpus (CN-cloud heavy); GCP-EASM minimal
aimap-profile: DEGRADED WHOIS only (no Shodan key for sector enrichment)
nu-recon:      NULL     simulated (no Shodan key)
VisorSD:       BLOCKED  Shodan API key required
recongraph:    folded into VisorGraph (Go engine)
VisorRAG:      THIN     not fired at operator hosts (restraint; verification probe sufficed)
VisorHollow:   [—]      Windows-only
cortex:        THIN     auth-context note; informational
JS-bundle:     N/A      AnythingLLM/Perplexica SPAs; auth confirmed via API, not bundle
```

Four tools carried the survey: aimap (identity + shadow), JAXEN (harvest), the verification probe (auth state), VisorGraph (attribution). VisorCorpus is genuinely applicable here because RAG is an LLM-adjacent surface.

---

## Honest Negative Space

- **SPA/JSON-API platforms are Shodan-dark.** LightRAG, Cognita, R2R, Verba returned 0 on every HTML dork; their true populations need masscan + port-probe (9621, 8000, 7272). The auth-off-default SPA tier is systematically undercounted by this methodology.
- **RAGFlow's 1,674 is HTML-renderer-biased and ~50% FP** per Insight #15; only 17 sampled, mostly behind proxy — its true unauth rate is unmeasured here.
- **Sampling:** AnythingLLM 30/154, Onyx 30/71, Perplexica 20/64, RAGFlow 17/1674. Rates are sample-based; noted, not population-complete.
- **No-response rows** (apps behind 443 proxies on non-probed internal ports) are inconclusive, not secure — the true unauth count is a floor, not a ceiling.
- **Kotaemon default admin/admin** is documented but was NOT tested (restraint — that crosses into credential use).
- aimap-profile/nu-recon/VisorSD degraded or blocked by the Playwright-only Shodan posture (no API key this session).

---

## Remediation (population reference)

1. **AnythingLLM:** enable multi-user mode or set the password toggle — single-user mode ships with `RequiresAuth:false`. Workspace documents and embedded LLM keys are otherwise world-readable.
2. **Perplexica / Ragapp / Verba:** never expose to the public internet — they ship no auth layer by design. Put behind an authenticating reverse proxy.
3. **DocsGPT:** upgrade past v0.12.0 (CVE-2025-0868 pre-auth RCE); `/api/get_api_keys` must not be reachable.
4. **RAGFlow:** change `admin@ragflow.io/admin`; upgrade ≥0.14.0 (CVE-2024-12433 pre-auth RCE).
5. **Co-located MCP servers:** audit the host — an exposed RAG app frequently means an exposed MCP tool server on the same IP.

---

## See Also
- Pre-assessment intel: `data/platform-intel/rag-frameworks-osint-2026-05-27.md`
- Query catalogs: `shodan/queries/rag-frameworks-queries.md`, `shodan/queries/07-rag-stacks.md`
- aimap v1.9.41 CHANGELOG (13 RAG fingerprints)

---

## Censys Dark-Tier Addendum — LightRAG recovered from the Shodan-dark tier (2026-05-31)

The Shodan HTML dorks returned **0** usable LightRAG (the SPA renders no name to the crawler; bare `port:9621` = 519 hosts of Chinese-cloud/WAF noise). Censys — full-handshake scanning + software fingerprinting — reached it.

**Censys Platform query** (`platform.censys.io`, Free tier, manual web UI, no API/PAT):
- `host.services.port=9621` → ~1.2K hosts (vs Shodan's undifferentiated 519), with a faceted software breakdown Shodan cannot produce.
- `host.services.port=9621 and host.services.software.product="uvicorn"` → **185 LightRAG candidates** (FastAPI/uvicorn on the LightRAG-exclusive port).

**Verification** (our probe, 100 candidates from page 1; restraint: `/health` + `/documents` existence only, no `/query` retrieval, no document reads):
- **81 confirmed LightRAG** (via `/health` `working_directory`/`core_version` signature)
- **36 UNAUTHENTICATED** — `/documents` readable without credentials, exposing the knowledge graph and ingested document chunks. Versions 1.3.9 → 1.4.16 captured per host for CVE-window mapping.
- ~45 api-key-set (auth enforced; `/health` open by design but `/documents` 401)
- 19 no-response

VisorLog #36164-36199. **This raises the Cat-07 confirmed-unauth total from 33 to 69** — the 36 LightRAG instances were completely invisible to the Shodan-based survey.

**Methodological proof:** this is the first NuClide finding sourced entirely from Censys reaching a population Shodan structurally cannot index. It validates Censys as a standing arsenal complement (Insight #69 + the dork-population-substitution lesson): for SPA/JSON-API platforms whose name never renders to a crawler, Shodan returns 0 and Censys returns the real population. The other Cat-07 Shodan-dark platforms (R2R 7272, Cognita/Verba 8000) are now reachable the same way — `host.services.port=<p> and host.services.software.product="uvicorn"` then verify.

**Censys account note:** Free tier (100 credits/mo); `host.services.banner` and advanced protocols are Starter-gated, but `port` + `software.product` + faceting are available and sufficient to isolate candidates. No PAT/API — manual web UI, same posture as Shodan.
