# AI Gateway & Infrastructure Fingerprinting — Technical Reference (2026)

> Scope: assets you own or are authorized to test; append a scope clause (`net:` / `org:` / `asn:` / `ssl.cert.subject.cn:`) to every query.

---

## 1. Response signatures (the reliable identifiers)

Port is the weakest signal; the **headers, root/title, and unauthenticated JSON endpoints** are what confirm a product. Defaults below are the documented ones — match on ≥2 vectors to kill false positives.

### LLM gateways

| Product | Default port(s) | `Server`/headers | Root / title | Unauth endpoints + sample response |
|---|---|---|---|---|
| **Kong** | 8000/8443 proxy, **8001/8444 admin**, 8002 Manager | `Server: kong/<ver>`, `X-Kong-*` | Manager title `Kong Manager` | Admin `GET /` → `{"tagline":"Welcome to Kong","version":"x.y.z","plugins":{...},"configuration":{...}}` (full config + version) |
| **LiteLLM** | **4000** | FastAPI/uvicorn | Swagger at `/`; admin UI `/ui` | `/health` (needs key) → `{"healthy_endpoints":[{"api_base":"...","model":"..."}],"healthy_count":N}`; `/health/liveliness`, `/health/readiness` (unauth); `/v1/models` → `{"data":[...]}` |
| **Portkey** | 8787 (OSS gateway) | `x-portkey-*` | root → `AI Gateway says hey` | `/v1/*` OpenAI-compatible |
| **Bifrost** | (verify) | — | title `Bifrost AI Gateway` | — |
| **Helicone** | 8585 + others | `Helicone-*` | body `helicone`; backend `Jawn` | — |

Hosted-only (**OpenRouter**, **Cloudflare AI Gateway**): no instance to fingerprint — exposure is leaked keys, not a host.

### Model servers (usually unauthenticated)

| Product | Port | `Server` | Root | Unauth endpoints + response |
|---|---|---|---|---|
| **Ollama** | **11434** | — (body is the tell) | `Ollama is running` | `GET /api/tags` → `{"models":[{"name":"llama3.1:latest","size":...,"digest":...}]}`; `/api/version` → `{"version":"0.x.y"}`; OpenAI-compat `/v1/models`, `/v1/chat/completions`. Exposed when `OLLAMA_HOST=0.0.0.0` |
| **vLLM** | **8000** | `uvicorn` | FastAPI `/docs` | `/health` → 200; `/v1/models` → `{"object":"list","data":[{"id":"<model>","owned_by":"vllm"}]}`; `/metrics` (Prometheus) |
| **Open WebUI** | 8080 | — | title `Open WebUI` | `/health`, `/api/config` |
| **LocalAI** | 8080 | — | body `LocalAI` | `/readyz`, `/v1/models` |

### Builders / control planes

| Product | Port | Title | Endpoints |
|---|---|---|---|
| **Langflow** | 7860 / 8501 | `Langflow` | `/health` → `{"status":"ok"}`; `/api/v1/*` (incl. the historic RCE routes `/validate/code`, `/build_public_tmp`) |
| **Flowise** | 3000 | `Flowise` | `/api/v1/*`; CustomMCP node config |
| **Dify** | 3000/5001 | `Dify` | `/console/api/*`, `/v1/*` |
| **n8n** | **5678** | `n8n` | `/healthz` → `{"status":"ok"}`; `/rest/*` |
| **Langfuse** | 3000 | `Langfuse` | `/api/public/health` |
| **MCP Inspector** | client 6274, proxy 6277 (verify) | — | dev tool; unauth RCE = CVE-2025-49596 |

---

## 2. Dorks (multi-vector, Shodan syntax — add a scope clause)

```text
# Kong
"Server: kong"                                            # any port, most durable
port:8001 http.html:"\"tagline\":\"Welcome to Kong\""     # admin API root JSON
http.title:"Kong Manager"                                 # GUI

# LiteLLM
port:4000 http.html:"litellm"
http.title:"LiteLLM"
http.html:"healthy_endpoints"                             # /health body leaked

# Portkey / Bifrost / Helicone
http.html:"AI Gateway says hey"
http.title:"Bifrost AI Gateway"
http.html:"helicone"

# Ollama  (high-yield, usually no auth)
port:11434 "Ollama is running"
http.html:"\"models\":[" port:11434                       # /api/tags response

# vLLM
http.html:"\"owned_by\":\"vllm\""
port:8000 http.html:"/v1/models"

# Builders
http.title:"Langflow"      |  port:7860 http.html:"langflow"
http.title:"Flowise"       |  http.title:"n8n"  port:5678
http.title:"Open WebUI"    |  http.title:"Langfuse"
```

---

## 3. Cross-engine syntax

| Field | Shodan | Censys | FOFA | ZoomEye |
|---|---|---|---|---|
| Title | `http.title:"X"` | `services.http.response.html_title:"X"` | `title="X"` | `title:"X"` |
| Body | `http.html:"X"` | `services.http.response.body:"X"` | `body="X"` | (body) |
| Header | `"Server: X"` | `services.http.response.headers.server:"X"` | `header="Server: X"` | (header) |
| Port | `port:N` | `services.port:N` | `port="N"` | `port:N` |
| Favicon | `http.favicon.hash:N` | favicon op (MD5) | `icon_hash="N"` | `iconhash:"N"` |
| TLS JARM | `ssl.jarm:H` | `services.tls.ja3s` / fingerprints | `jarm="H"` | — |
| Cert CN | `ssl.cert.subject.cn:"X"` | `services.tls.certificates.leaf_data.subject.common_name:"X"` | `cert="X"` | `ssl:"X"` |
| Scope | `net: / org: / asn:` | `ip: / autonomous_system.asn:` | `org= / cidr=` | `cidr: / org:` |

---

## 4. Advanced vectors (when banners are stripped)

- **Favicon hash.** Shodan = `mmh3(base64(bytes))` (signed 32-bit), Censys = MD5. Default product favicons map to a single hash → one query enumerates all instances. Filter `http.favicon.hash:`.
- **TLS / JARM.** JARM is an active server-side TLS fingerprint (10 Client Hellos → 62-char hash of the responses) identifying the TLS stack + config. It clusters hosts with identical TLS settings (same proxy/app build) **even after you strip `Server`/title**. Shodan indexes it: `ssl.jarm:<hash>`. JA4+ (JA4S server hash) is the newer suite.
- **ALPN / HTTP version.** Advertised `h2` vs `http/1.1` and the cert chain narrow the stack.
- **Header set + ordering.** Vendor headers (`X-Kong-*`, `x-portkey-*`, `Helicone-*`) and header ordering fingerprint the framework even with `Server` blanked.
- **Tech-detect tooling.** `httpx -title -tech-detect -favicon -json`; `nuclei -t http/technologies/ -t http/exposures/`; Wappalyzer fingerprint DB. Nuclei's favicon templates map a hash → product/CVE automatically.

---

## 5. Harvest workflow (derive exact signatures from your own instance)

```bash
T="https://svc.example.com"
curl -sI "$T"                                   # Server / X-* / ALPN via -v
curl -s  "$T" | grep -iE '<title>|portkey|kong|litellm|helicone|langflow|flowise|ollama|vllm|langfuse'
for p in / /health /healthz /readyz /api/tags /api/version /v1/models /metrics /ui /docs; do
  printf '== %s ==\n' "$p"; curl -s -m5 "$T$p" | head -c 300; echo
done
# Favicon hash (Shodan-matching)
python3 -c "import mmh3,requests,codecs;print(mmh3.hash(codecs.encode(requests.get('$T/favicon.ico').content,'base64')))"
# JARM
pip install jarm && python3 -m jarm.scanner.jarm svc.example.com -p 443
```
Assemble scoped dorks from the output:
```
"Server: kong" port:8001 net:"203.0.113.0/24"
port:11434 "Ollama is running" org:"ACME"
http.favicon.hash:<hash> ssl.cert.subject.cn:"acme.com"
ssl.jarm:<hash> asn:AS#####
```

---

## 6. Remediation reference

| Finding | Action |
|---|---|
| Any gateway/builder/model server reachable | Bind app to `127.0.0.1`; front with reverse proxy + auth; or VPN/zero-trust (no public listener) |
| Kong `8001`/`8444`, LiteLLM `/ui`, any admin API | Never internet-facing; bind to private/loopback; firewall |
| Open Ollama/vLLM (`/api/tags`, `/v1/models` unauth) | Add auth proxy; restrict egress; `OLLAMA_HOST` to private bind |
| Exposed gateway | Rotate all upstream provider keys; move secrets to vault (out of env/prompts) |
| Langflow/Flowise exposed | Confirm patched (Langflow ≥1.8.x, Flowise ≥3.0.6); check logs for `/validate/code`, `/build_public_tmp`, CustomMCP |
| MCP Inspector exposed | Upgrade ≥0.14.1; never expose; not bound to `0.0.0.0` |
| Fingerprint reduction (defense-in-depth) | `server_tokens off`, strip `X-*`, blank title, neutralize favicon, wildcard certs |

---

*June 2026. Cross-engine syntax, JARM, and the Kong/Ollama/vLLM signatures are stable; product ports/strings change across versions — confirm with §5 against a known-good instance.*
