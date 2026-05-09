# 19. Streamlit Data Apps

_Section created: 2026-05-09_

Streamlit ships with **no built-in authentication**. The framework expects operators to front it with a reverse proxy; when deployed directly on default port 8501, every visitor has full app access. Port 8501 is near-unique to Streamlit in Shodan, making it the highest-precision single-port signal in this catalogue — comparable to Qdrant's 6333.

**Survey result (2026-05-03):** 1,389 port-8501 hits across 28 cloud /16 ranges → **551 confirmed Streamlit apps, 100% unauthenticated**. Playwright-rendered sample of 100 found 84 unique operator-attributable titles including trading bots, admin portals, dark-web OSINT tools, financial dashboards, and LLM applications with embedded API keys.

**Auth posture:** T1 — no auth concept in the framework. `/_stcore/host-config` returns `{"useExternalAuthToken":false}` confirming no external auth proxy is wired. `/_stcore/health` returns `"ok"`.

**CVE watch:**
- No framework-level CVEs. Risk is entirely in the application layer: embedded API keys in `st.secrets`, file-upload PII pipelines accessible to any visitor, live database connections, internal LLM access.

---

**Shodan indexing note:** `"_stcore/host-config"` and `"_stcore/health"` return 0 — Shodan does not index the raw HTTP path strings from Streamlit's internal endpoints. Use `http.html:` prefix for reliable results. `port:8501` alone returns 107,747 (very noisy); `port:8501 http.html:"streamlit"` (4,766) is the precision signal.

## Core fingerprints

| Shodan Query | Verified hits | Notes |
|---|---|---|
| `port:8501 http.html:"streamlit"` | **4,766** | Best precision signal; HTML-scoped on default port |
| `port:8501` | 107,747 | Broadest; ~90%+ Streamlit but high noise from other port-8501 services |
| `port:8501 http.html:"streamlit-app"` | — | App container identifier |
| `port:8501 http.html:"useExternalAuthToken"` | — | Auth-config key in page source; confirms no-auth state |
| `port:8501 http.status:200` | — | Live + responding |
| `http.html:"streamlit" port:8501` | 4,766 | HTML lowercase on default port (same as top query) |
| `http.html:"st-app" port:8501` | — | Streamlit app class in DOM |
| `http.favicon.hash:-543900504` | — | Streamlit default favicon hash |
| `http.favicon.hash:-543900504 port:8501` | — | Favicon + default port |
| `http.favicon.hash:-543900504 -port:443` | — | Favicon, non-HTTPS |

---

## Reverse-proxied (80/443)

| Shodan Query | Notes |
|---|---|
| `http.html:"_stcore" port:80` | Streamlit behind HTTP proxy |
| `http.html:"_stcore" port:443` | Streamlit behind HTTPS proxy |
| `http.html:"streamlit" port:80` | HTML-scoped on port 80 |
| `http.html:"streamlit" port:443` | HTML-scoped on port 443 |
| `http.html:"_stcore/host-config"` | Config endpoint path in any indexed source |
| `ssl.cert.subject.cn:"streamlit"` | TLS cert CN contains "streamlit" |
| `hostname:"streamlit"` | rDNS pattern |
| `hostname:"streamlit" port:8501` | rDNS + default port |
| `http.title:"Streamlit"` | Default-titled apps (no custom title set) |
| `http.title:"Streamlit" port:8501` | Default title on default port |

---

## Cloud-provider scoped

| Shodan Query | Notes |
|---|---|
| `port:8501 org:"digitalocean"` | DigitalOcean (primary survey provider) |
| `port:8501 org:"hetzner"` | Hetzner |
| `port:8501 org:"vultr"` | Vultr |
| `port:8501 org:"amazon"` | AWS |
| `port:8501 org:"google"` | GCP |
| `port:8501 org:"microsoft"` | Azure |
| `port:8501 org:"ovh"` | OVH |
| `port:8501 org:"linode"` | Linode/Akamai |
| `port:8501 org:"scaleway"` | Scaleway |
| `port:8501 country:US` | US-scoped |
| `port:8501 country:CN` | China (high deployment density) |
| `port:8501 country:DE` | Germany |
| `port:8501 country:IN` | India |
| `port:8501 country:BR` | Brazil |

---

## Application-class targeting

| Shodan Query | Notes |
|---|---|
| `port:8501 http.html:"trading"` | Trading-bot apps (largest class in survey: ~20% of titled apps) |
| `port:8501 http.html:"dashboard"` | Dashboard apps |
| `port:8501 http.html:"admin"` | Admin portal apps (CRITICAL class in survey) |
| `port:8501 http.html:"api_key"` | Embedded API key references in page source |
| `port:8501 http.html:"openai"` | OpenAI-integrated apps |
| `port:8501 http.html:"llm"` | LLM-integrated apps |
| `port:8501 http.html:"chatbot"` | Chatbot apps |
| `port:8501 http.html:"upload"` | File-upload apps (PII pipeline risk) |
| `port:8501 http.html:"database"` | Database-connected apps |
| `port:8501 http.html:"osint"` | OSINT tools (class C in survey) |
| `port:8501 http.html:"crypto"` | Crypto/trading apps |
| `port:8501 http.html:"binance"` | Binance-integrated trading apps |
