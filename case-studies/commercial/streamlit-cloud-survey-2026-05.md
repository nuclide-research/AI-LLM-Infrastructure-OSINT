---
type: survey
---

# Streamlit Data Apps on Public Cloud: Auth Posture Survey

_NuClide Research · 2026-05-03_

---

## Summary

Mass-scan of port 8501 (Streamlit's default) across 28 cloud-provider /16 ranges (DO/Hetzner/Vultr) returned 1,389 hits → fingerprinted via `/_stcore/host-config` → **551 confirmed Streamlit apps**, all **unauthenticated** (`useExternalAuthToken: false`). A 100-app Playwright-rendered sample revealed **84 unique app titles** = operator-attributable products, spanning trading bots, OSINT tools, business admin portals, dashboards, and a long tail of internal AI demos.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5904
- **733 (AI Risk & Ethics Specialist):** K7040, S7067, T5854, T5868, T5893, T5904
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003, K7024, K7048, K942, S7065

<!-- ksat-tag:auto-generated:end -->

Streamlit ships without built-in authentication, the framework expects operators to put a reverse proxy in front of it. The 100% unauth result here is therefore expected: any Streamlit found on the public internet on its default port has no auth in front. The novel finding shape is **what people are running on top of Streamlit unauth**, production trading dashboards, dark-web OSINT tools, admin portals, etc., often with embedded API keys, LLM access, file-upload PII pipelines, and internal data exposed to every visitor.

This is the largest "long-tail" sample in the NuClide commercial-AI series and the broadest cross-section of how AI/data tooling actually gets deployed in 2026.

---

## Methodology

```
masscan -iL <28 cloud /16 CIDRs> -p 8501 --rate 10000
  → 1,389 port-8501 hits

streamlit-probe.py (200-thread fingerprint)
  GET /_stcore/host-config → JSON {"useExternalAuthToken":false, "allowedOrigins":[...]}
  GET /_stcore/health      → "ok"
  GET /                    → HTML (title only, set client-side via JS)
  → 551 confirmed Streamlit apps

streamlit-render-probe.py (Playwright sample, 100 random instances)
  Render each app with a real browser; wait for JS hydration; extract
  document.title and first 5 lines of body text.
  → 98 successfully rendered, 84 unique custom titles
```

NuClide deliberately did not interact with the Streamlit apps (no form input, no file upload, no button clicks). Title + first-render snapshot only.

---

## Findings Summary

| Metric | Value |
|---|---|
| Cloud /16 ranges scanned | 28 |
| Masscan hits on :8501 | 1,389 |
| Streamlit confirmed | **551** |
| Unauthenticated | **551 (100%)** |
| Sampled with Playwright (rendered) | 100 |
| Successful renders | 98 |
| Custom-titled apps | ~85% (extrapolating from sample) |
| Default-titled ("Streamlit"/"main"/"app") | ~15% |

---

## Threat Classes Observed in the 100-App Sample

### Class A: Trading bots / crypto / finance dashboards (highest concentration)

The single largest cluster. ~20% of titled apps are trading-related:

| App title | IP | Notes |
|---|---|---|
| Trading Desk | 165.227.127.162 | Generic trading dashboard |
| Trading Dashboard | 45.32.35.83 | Generic |
| Trading Bot Dashboard | 178.62.87.181 | Generic |
| 交易历史 - Binance Bot | 149.28.141.122 | Chinese-language Binance trading-history dashboard |
| Crypto Bot Dashboard | 138.197.87.106 | Generic |
| Hyperliquid Dashboard | 45.76.92.38 | Hyperliquid (perpetuals DEX) trading view |
| Polymarket Smart Money | 159.69.23.69 | Polymarket whale-tracking |
| Daytrade bot, dashboard | 116.203.227.71 | Generic |
| Bot Dashboard | 116.203.192.203 | Generic |
| PBGUI - Welcome | 65.109.134.92 | PassivBot UI (popular open-source crypto bot frontend) |
| Pre-Volatility Dashboard | (sampled) | Generic |
| Systematic Portfolio Dashboard | 138.197.223.108 | Generic |
| Kalshi Weather Desk | 104.131.190.28 | Kalshi prediction-market weather contracts |
| Finance Tracker | 159.203.67.30 | Generic |
| 帝國矩陣指揮部 \| Institutional Grade | (sampled) | Chinese, "Empire Matrix Command Center" |
| 台股基本面系統化分析 | (sampled) | Chinese, Taiwan stock fundamental analysis |
| Heights Insights | 159.203.64.214 | Likely finance |

**Risk class:** strategy disclosure (the dashboard reveals which signals/positions the operator runs), API-key exposure (Binance/Hyperliquid/Polymarket account credentials often hard-coded in Streamlit `st.secrets`), live position visibility, and the standard "free LLM/inference" exposure if the bot uses an embedded API key.

This matches the prior `94.183.187.228` (retail trading bot) finding from the earlier session, which was a single example of this pattern. The cloud sweep shows the pattern at population scale: **trading bots on Streamlit are the dominant exposed AI workload type**.

### Class B: Operator-attributable admin portals (CRITICAL by class)

Apps named with administrative or operational language:

| App title | IP | Notes |
|---|---|---|
| Fair Skies Admin Portal 👤 | 138.197.225.245 | Customer admin UI |
| Quetzality Admin | 138.197.33.66 | Operator-branded admin |
| Heritage Lens Agent | 45.63.100.169 | Internal agent tool |
| Lynchburg Carbon Intelligence | 104.236.8.2 | Carbon-emission intelligence (operator: Lynchburg) |
| Peaqock Tenders | 167.71.47.246 | Peaqock tender-management |
| Yguazu - Pedidos de Combustible | 149.28.107.69 | Spanish, fuel-order management |
| AMZ Bid Manager Level 3 | 46.101.215.72 | Amazon advertising bid manager |
| Управление данными о селлерах OZON | 65.109.88.77 | Russian, OZON e-commerce sellers data management |
| AFI Tools, Data Cleanse | 206.189.190.107 | Data-cleansing internal tool |
| Observability Utility Tool | 206.189.132.132 | Internal ops tool |
| WG Device Manager | 45.63.53.47 | WireGuard or similar device manager |
| MITEC Live | 108.61.185.244 | "MITEC", Mexican government IT-secretariat naming pattern |
| Alarm Rationalization Platform | 138.197.80.150 | Industrial / SCADA-adjacent |
| FORGE, Milos | 138.197.19.120 | Custom platform |
| Sentinel Core | 116.202.97.178 | Custom platform |
| Shinbu Command Center | 45.76.122.49 | Custom platform |
| Ayuda-Foreclosure Manager | 138.197.93.163 | Foreclosure case management |

**Risk class:** these are internal operations tooling exposed to the public internet. Each one likely contains the operator's customer data, ticket queue, or business-process state.

### Class C: AI / OSINT / agent tools (HIGH: operator IP + capability)

| App title | IP | Notes |
|---|---|---|
| **Robin: AI-Powered Dark Web OSINT Tool** | (sampled) | Literal name |
| Polygraph Terminal | 167.71.166.118 | Investigative/intel tool |
| Evidence Engine | 116.203.134.204 | Investigative |
| Fourby Newsroom | 167.172.119.126 | News/research |
| AI Visibility OS (Personal Edition) | 45.55.91.146 | LLM-app monitoring |
| PolyGraph Terminal | 167.71.166.118 | Same as above |
| MySQL Chatbot | 167.71.226.163 | Free unauth-DB chatbot |
| NHL Agent Chat | 167.172.26.116 | Sports agent / scout chatbot |
| BANG Companion App | 65.109.225.156 | Unknown |
| Smart Dustbin Dashboard | 206.189.155.51 | IoT |
| Project Planner | 167.172.182.229 | Internal |
| MERMAID Data Analysis Toolkit | 45.76.173.245 | Marine science (MERMAID = Marine Ecological Research and Monitoring) |
| VisionCup Questions | 149.28.138.130 | Sports |
| Telco Churn Predictor | 165.227.67.180 | Telecom analytics |
| Water Flow Rate Prediction | 167.71.210.165 | Utility |

### Class D: Cross-correlation with the MLflow survey

**`GC Breeders Evaluation`** appears twice in the 100-app sample (port 8501), and `GC_BREEDER_*` was the dominant experiment-name pattern on the MLflow at `188.166.132.129/.104` (port 5000). Same operator runs:

- MLflow Tracking Server with 10 `GC_BREEDER_*` experiments → see [mlflow-cloud-survey-2026-05.md](mlflow-cloud-survey-2026-05.md)
- Streamlit dashboards titled "GC Breeders Evaluation" for browsing the model results
- Multi-host deployment (DigitalOcean)

This is a **complete MLOps stack exposure** for one operator: training (MLflow) + dashboarding (Streamlit), both unauth.

---

## What Was NOT Done

- No form fills, no button clicks, no file uploads to any Streamlit app
- No interaction with `/_stcore/stream` (the WebSocket data plane), would let an attacker watch the operator's live dashboard updates
- No probing of `st.secrets`-style endpoints
- No identification of embedded API keys (would require deeper interaction)

The Playwright render captured the public-facing first-screen state only. Many apps likely have richer surfaces behind the home page, login screens, admin tabs, file-upload forms, that NuClide did not exercise.

---

## Cross-Survey Pattern (updated)

| Tier | Platform | Sample | Unauth |
|---|---|---|---|
| Vector DB | Qdrant / ChromaDB / Milvus | 142 | 100% |
| Inference | Triton / vLLM | 46 | 100% |
| Image-gen | A1111 | 1 | 100% |
| MLOps | MLflow Tracking | 11 | 100% |
| **Data App** | **Streamlit** | **551** | **100%** |
| Orchestration UI | Flowise / n8n / Open WebUI / Langflow | 1170 | 0% (small misconfig %) |

Streamlit confirms the broader pattern: **anything in the AI/ML stack that doesn't ship with auth-on-default is overwhelmingly deployed without auth in front of it.** Operators who would never deploy a public-internet Postgres or Redis will happily expose their Streamlit dashboard with the same access semantics as that database.

---

## Remediation

```bash
# Streamlit has NO built-in auth. Recommended:

# 1. Reverse-proxy with HTTP Basic / OAuth2 forward auth
#    (Caddy / Nginx / Traefik with oauth2-proxy)

# 2. streamlit-authenticator package (community, recommended)
#    pip install streamlit-authenticator

# 3. Streamlit Community Cloud SSO (managed, only works for public-cloud-hosted)

# 4. Bind to localhost only and front with a tunnel
streamlit run app.py --server.address=127.0.0.1
```

---

## Disclosure Posture

NuClide is not opening 551 individual disclosure threads. The ~85% custom-titled fraction means several hundred operator-attributable apps. Disclosure priorities by class:

- **Trading bots / finance dashboards**, operator-specific where the brand is identifiable. PBGUI and similar open-source bots = community awareness only. Branded Trading Bot Dashboards = direct operator contact.
- **Admin portals (Fair Skies, Quetzality, MITEC, OZON)**, operator-attributable; direct disclosure to brand contact.
- **GC Breeders multi-stack operator**, coordinated disclosure with the MLflow finding (same operator, same VPS family).
- **Robin Dark Web OSINT Tool**, given the data class implied (dark-web scrape data), worth contacting the operator directly via brand.

---

## NuClide Pipeline Artifacts

| Stage | Notes |
|---|---|
| Discovery | masscan port 8501 → 1,389 IPs |
| Fingerprint | `streamlit-probe.py`, `/_stcore/host-config` shape match |
| Render sample | `streamlit-render-probe.py`, Playwright on 100 random instances; 98 successful |
| Findings ledger | Top-titled instances ingested into `data/nuclide.db` |
| What was NOT done | No app interaction, no file uploads, no form fills, no probing of internal pages |

---

## References

- Streamlit security model: https://docs.streamlit.io/develop/concepts/connections/secrets-management
- streamlit-authenticator: https://github.com/mkhorasani/Streamlit-Authenticator
- Cross-survey index: [index.md](index.md)
