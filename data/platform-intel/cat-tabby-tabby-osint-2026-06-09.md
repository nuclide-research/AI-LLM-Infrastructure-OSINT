# Tabby (TabbyML/tabby) — Cat-Tabby Platform Intelligence Brief

**Date:** 2026-06-09
**Researcher:** NuClide OSINT Platoon, Squad 1 of 4
**Stage:** -1 (intelligence gathering, no probing)
**Status:** CANDIDATE — doc-grounded, host-unverified
**Latest release at brief time:** v0.32.0 (2026-01-25)

## 1. One-line identity

Open-source self-hosted AI code-completion server (alternative to GitHub Copilot). Rust core, Axum HTTP, llama.cpp subprocess for local inference, optional enterprise webserver layer (GraphQL, auth, team management, RAG answer engine).

## 2. Auth modes & deploy posture

### Auth modes supported (full list)

| Mode | Build | Notes |
|------|-------|-------|
| None (token unset) | OSS + EE | Default for `serve --no-webserver`. Bearer header absent in client; server accepts. |
| Bearer token | OSS + EE | Optional on `/v1/completions`, `/v1/chat/completions`, `/v1beta/chat/completions`, `/v1/events`. Set via webserver admin UI → "Generate API token." |
| JWT session | EE (`--webserver` default ≥ v0.11.0) | Webserver creates admin on first visit; `TABBY_WEBSERVER_JWT_TOKEN_SECRET` env. Argon2id password hash. |
| LDAP | EE ≥ v0.24.0 (2025-01-23) | Directory bind. |
| OIDC | EE | Generic OIDC SSO provider. |
| OAuth (GitHub, Google, GitLab) | EE | SSO with email-domain self-signup eligibility check. |
| Self-hosted GitHub / GitLab | EE | Org-instance SSO. |

### Auth posture history (load-bearing)

- **≤ v0.6.x (pre-Dec-2023):** no built-in auth. `serve` exposes API on `:8080` open. `/v1beta/...` was the live namespace.
- **v0.7.0 (2023-12-15):** `--webserver` flag introduced — opt-in secure team mode requiring IDE tokens.
- **v0.11.0 (2024-05-10):** `--webserver` made **default**. Operators must pass `--no-webserver` to get the legacy open-API behavior. Same release moved `/v1beta/chat/completions` → `/v1/chat/completions` (legacy alias kept).
- **v0.12.0:** HTTP API leaves experimental status.
- **v0.24.0 (2025-01-23):** LDAP integration.
- **v0.27.0 (2025-03-29):** option to hide password-login form in frontend (URL-param reveal).
- **v0.29.0 (2025-05-20):** REST API documentation integrated (Swagger UI).

### What "auth-on-default" looks like today (≥ v0.11.0)

The docker quickstart at `tabby.tabbyml.com/docs/quick-start/installation/docker/` does NOT walk through admin-account creation or JWT secret — it just runs `serve`. The webserver layer activates by default; first HTTP visit is funnelled into admin-account creation. **But:**

- `/v1/health`, `/v1beta/models`, `/v1beta/server_setting` are **always unauthenticated** in OSS builds. In EE builds `/v1beta/server_setting` is unauthenticated only when webserver is disabled — i.e. `--no-webserver` mode re-exposes it. (Source: DeepWiki server-implementation page.)
- `/v1/completions` and `/v1/chat/completions` take an **optional** bearer. If the operator never set a token (or runs `--no-webserver`), these endpoints accept any caller.
- The `TABBY_OWNER_IMPERSONATE_OVERRIDE` env var exists as a maintainer testing backdoor — its presence in a process env would be a finding.
- `--no-webserver` mode strips the entire JWT/admin/team layer and is the operational equivalent of pre-v0.11 open mode.

### Security-conscious deployment vs operator-default

| Aspect | Operator-default quickstart | Hardened |
|--------|----------------------------|----------|
| Webserver | enabled (since v0.11) | enabled |
| Port 8080 | exposed direct | reverse-proxied (Caddy/Traefik/Nginx) with TLS |
| Admin creation | on first visit (anyone first) | created behind VPN/SSH tunnel, then exposed |
| JWT secret | auto-generated default | strong `TABBY_WEBSERVER_JWT_TOKEN_SECRET` env |
| Token gen | optional | API tokens required for IDE clients |
| LDAP/OIDC | off | on |

Sources: `tabby.tabbyml.com/docs/quick-start/installation/docker/`, `deepwiki.com/TabbyML/tabby/3.1-server-implementation-and-http-apis`, `ee/tabby-webserver/src/service/auth.rs`.

## 3. Shodan fingerprint & population

### Port surface

- **Canonical:** TCP 8080 (HTTP, all editions). Confirmed default in docker quickstart, hub.docker.com/r/tabbyml/tabby image, and `--port` flag default.
- **Alt:** none in upstream docs. Reverse-proxy fronted instances surface on :443/:80 with backend on 8080.
- **Subprocess (local-only):** llama-cpp-server child process; bound to loopback, not externally listening.

### Distinctive HTTP markers (best Shodan dorks)

The OSS code paths return Axum-default headers — no custom `Server: tabby-server` was found in source review. Identification comes from response **body** content, not headers.

| Dork tier | Query | Logic | FP risk |
|-----------|-------|-------|---------|
| basic | `http.html:"Tabby" http.html:"AI coding"` | Webserver SPA title/meta | mid (term collisions w/ Eugeny/tabby terminal — different product) |
| basic-port | `port:8080 "Tabby"` | catches OSS+EE direct | mid |
| strict-json | `http.html:"server_setting" http.html:"tabby"` or via `/v1beta/server_setting` JSON keys (`completion`, `chat`, `disable_client_side_telemetry`) | EE webserver | low |
| strict-health | banner contains `{"model":` and `"chat_model":` and `"webserver":` keys (HealthState JSON shape) | OSS `/v1/health` GET | low |
| strict-favicon | `http.favicon.hash:<favicon-of-website/static/img/favicon.ico>` | served by webserver SPA | low (compute and pin) |
| swagger | `http.html:"swagger-ui" http.html:"tabby"` ≥ v0.29 | Swagger embed | low |
| version | basic + `"tabby"` + body-version regex pulled via `/v1beta/server_setting` `version` field | OSS+EE | low |

**Indexed-string assumption (critical):** Shodan crawls HTML body and HTTP headers. The webserver SPA serves `<title>Tabby</title>` (single-word, high collision). The `/v1beta/server_setting` and `/v1/health` JSON responses are direct-fetched on probe — they appear in Shodan only when the index crawler hit those paths, which Shodan generally does NOT (it indexes `/`). So `port:8080 "Tabby"` over root HTML is the primary harvest path; JSON-content dorks route to Censys / scanner Step 0c full-handshake fetch.

### Favicon

Path: `/website/static/img/favicon.ico` (also served by webserver at `/favicon.ico`). MMH3 hash should be computed via `tome probe tabby` and pinned. Worth a Shodan facet sweep — favicon-pinned hits are FP-free.

### TLS cert signal

No upstream-supplied cert default. Cert issuer = whatever operator chose (Let's Encrypt majority for public exposures, self-signed for lab). Subject CN = the operator's domain (e.g. `tabby.<org>.com`, `code.<org>.com`). Useful for VisorGraph cert-pivot but not as a discovery filter.

### Existing aimap fingerprint

**None.** Grep of `/home/cowboy/aimap/` returns zero hits for "tabby" or "tabbyml". Step 0d will scaffold a new fingerprint from `tome probe tabby` once this brief is committed.

### Existing nuclei templates

**None.** `projectdiscovery/nuclei-templates` search returns 0 matches for "tabby" related to TabbyML. (Search hits return Eugeny/tabby terminal templates — different product.) This is a clean greenfield for NuClide tooling.

### Population estimate

No prior public Shodan/Censys count for Tabby exists. Docker Hub `tabbyml/tabby` has **100K+ pulls** as of brief time. Cross-referencing with comparable self-hosted-AI servers (Ollama at ~16K live, LocalAI at low-thousands), a ballpark live-direct-exposure estimate for Tabby is **150-600 instances**, dominated by:

- US, Germany, China universities and small dev shops
- DigitalOcean, OVH, Hetzner, Vultr, AWS lightsail
- Substantial portion will be `--no-webserver` lab installs and operators who set up tunneling but mis-configured firewall

Shodan harvest (Step 0) will narrow this in chain run.

## 4. API surface & data exposure

### Complete endpoint map

| Endpoint | Method | Auth | Data returned | NuClide severity if exposed |
|----------|--------|------|---------------|------------------------------|
| `/v1/health` | GET | none | `HealthState`: model id, chat_model id, device (cuda/cpu/rocm/metal), webserver enabled?, version | LOW — identity + version fingerprint |
| `/v1beta/models` | GET | none | model registry list from server config | LOW — model enumeration |
| `/v1beta/server_setting` | GET | none (OSS; EE only when `--no-webserver`) | `ServerSetting`: completion config, chat config, `disable_client_side_telemetry`, indexed repo list, allowed repo list | MEDIUM — config exposure + indexed repo URLs (potential internal source leak) |
| `/v1/completions` | POST | **optional bearer** | code completion (compute) — `CompletionResponse` with id, choices, debug_data | HIGH IF UNAUTH — **compute-exfil primitive** (LLM-jacking, prompt injection canvas, potential code-snippet leak via `segments.git_url`) |
| `/v1/chat/completions` | POST | **optional bearer** | SSE stream of OpenAI-compatible chat completion | HIGH IF UNAUTH — **compute-exfil primitive** |
| `/v1beta/chat/completions` | POST | optional bearer | legacy alias of above | HIGH IF UNAUTH |
| `/v1/events` | POST | optional bearer | logs LogEventRequest | LOW |
| `/swagger-ui/` | GET | none | OpenAPI spec UI (≥ v0.29) | INFO — confirms identity + version, lists endpoints |
| `/graphql` | POST | required (EE only) | full webserver schema (users, repos, threads, jobs) | CRITICAL IF UNAUTH (would be a finding) |
| `/` | GET | none | EE webserver SPA HTML; admin-creation funnel if uninitialized | MEDIUM if first-visit-claim is open (admin land-grab) |

### Restraint posture (THE DO-NOT-CALL LIST)

NuClide enumerates **identity / config / version** only. The following endpoints are **compute-exfil primitives** and are NOT to be called on operator hosts:

- `POST /v1/completions` — costs operator GPU-seconds, generates content, demonstrably LLM-jacking
- `POST /v1/chat/completions` — same
- `POST /v1beta/chat/completions` — legacy alias of above
- `POST /v1/events` — pollutes operator telemetry
- `POST /graphql` mutations — state-changing
- Admin-creation POST on `/` first-visit — claims the admin account (impact = host takeover)

**Allowed reads (NuClide standard for this platform):**

- `GET /v1/health`
- `GET /v1beta/models`
- `GET /v1beta/server_setting`
- `GET /swagger-ui/` (HTML only, no spec POST)
- `GET /favicon.ico`
- `GET /` HTML title + meta

The marker probe is `GET /v1/health` — Tabby-unique HealthState JSON shape (`{"model":..., "chat_model":..., "device":..., "webserver":...}`) is a high-confidence-low-FP identity. Pair with `GET /v1beta/server_setting` for config-class finding.

## 5. CVEs & prior research

### CVEs filed against TabbyML/tabby

**Zero.** As of 2026-06-09 there are no published CVEs and no published GitHub Security Advisories against `TabbyML/tabby`. The `github.com/TabbyML/tabby/security/advisories` page returns "There aren't any published security advisories."

### Disambiguation — DO NOT cross-attribute

- **CVE-2024-55950** (macOS privacy issue), **CVE-2024-48460** (`tabby-ssh` info exposure), **GHSA-m937-jm93-pfp6** (drag-and-drop RCE), **ZMODEM auto-confirm** RCE → all belong to **`Eugeny/tabby`**, a separate terminal-emulator product. **Not TabbyML.**
- **HackTheBox "Tabby" machine** (0xdf and inesmartins write-ups) → CTF box unrelated to either project.

### Prior research

- DeepWiki maintains generated documentation for the architecture; no security-research blog posts found on TabbyML's compute-exfil surface as of brief time.
- No HackerOne, Bugcrowd, or Intigriti programs found for TabbyML.
- No CISA KEV entry.
- No academic paper specifically on TabbyML attack surface.

### Research gaps NuClide can fill

1. **Population census + auth-posture distribution.** What fraction of public Tabby instances run `--no-webserver` mode? What fraction have an admin account claimed vs unclaimed (the first-visit land-grab condition)? Quantitative answer.
2. **OSS-builds-leak-server_setting characterization.** Document the indexed-repo and `git_url` leak surface visible via `/v1beta/server_setting` — internal source-control URLs are PII-adjacent.
3. **Compute-cost-of-exposure model.** What does an open `/v1/completions` actually cost the operator? Not exploited — modeled from token throughput and average GPU-hour pricing.
4. **Admin-land-grab survey.** Of Tabby instances reachable and showing first-visit admin-creation modal, what is the distribution? (Enumerate only; never claim.)
5. **Version-skew & auth-on-default thesis confirmation.** Compare `--webserver`-default-on (≥ v0.11) population vs pre-v0.11 stragglers. The thesis: disclosure pressure shifts default rightward (Insight #40).

## 6. Deployment patterns

### Canonical Docker quickstart

```bash
docker run -d \
  --name tabby \
  --gpus all \
  -p 8080:8080 \
  -v $HOME/.tabby:/data \
  registry.tabbyml.com/tabbyml/tabby \
    serve \
    --model StarCoder-1B \
    --chat-model Qwen2-1.5B-Instruct \
    --device cuda
```

Volume: `/data`. Data files: `~/.tabby/{config.toml, logs/, models/}`.

### docker-compose patterns (observed via search index)

Common service names: `tabby`, `tabbyml`, `tabby-server`, `ai-coding`. Common network names: `tabby_default`, `<project>_default`, `internal`. Volume: persistent `/data` binding. Many compose files chain Tabby to a reverse-proxy (Caddy or Traefik) on the same network — that's the operator-default exposure path.

### Reverse-proxy patterns

- **Caddy:** `tabby.<org>.com { reverse_proxy localhost:8080 }` — TLS auto. Common.
- **Traefik:** label-based; `traefik.http.routers.tabby.rule=Host(<domain>)`.
- **Nginx:** `proxy_pass http://localhost:8080;`.

NuClide IP-direct shadow probe: even when fronted by reverse-proxy on :443/:80, the backend often listens on :8080 reachable directly via IP without SNI — same exposure as the JAXEN Insight #12 shadow-sweep posture.

### Cloud-PaaS one-click

- **Railway:** template enables JWT auth by default + admin first-visit flow + persistent volume. Cleanest hardened pattern.
- **SkyPilot:** `sky launch` example deploys CUDA T4, exposes :8080 publicly by default — UNHARDENED.
- **RamNode VPS guide:** docker + Caddy + Let's Encrypt — hardened, public.
- **Hugging Face Spaces:** Docker SDK template; HF Spaces sandbox.
- **Clore.ai:** GPU rental + Tabby + reverse-proxy.

## 7. Ecosystem co-deployment & adjacent surface

### Co-deployed components

- **Local llama.cpp subprocess:** internal child process; bound to loopback. No external port.
- **No DBMS by default:** Tabby is self-contained per upstream README — uses SQLite at `~/.tabby/ee/db.sqlite` for EE state. Operators occasionally add Postgres for multi-node setups — not standard.
- **No external vector DB:** Tabby uses **Tantivy** (Rust full-text index) embedded. Sometimes operators front-load with Qdrant/Chroma in custom RAG setups — adjacent finding territory.
- **OpenAI-compatible upstream:** Tabby can call OpenAI, Anthropic, Mistral, vLLM, Ollama, LocalAI, llama.cpp-server, OpenRouter, etc. as `--chat-model` backend. Operator config file often has API keys in plaintext at `~/.tabby/config.toml`.

### Port map of full ecosystem (shadow-sweep priorities)

| Port | Likely service | Probe priority |
|------|---------------|----------------|
| 8080 | Tabby (canonical) | P0 |
| 11434 | Ollama backend on same host | P1 — likely co-host |
| 8000 | vLLM or LocalAI backend | P1 |
| 8001 | Triton / alt model server | P2 |
| 6333 | Qdrant (custom RAG) | P2 |
| 8000-8001 | LocalAI | P2 |
| 9090 | Prometheus | P3 (config leak) |
| 6379 | Redis (custom session) | P3 |
| 5432 | Postgres (multi-node EE) | P3 |
| 22 | SSH (always) | P3 |

Insight #12 shadow-sweep policy applies: when Tabby is fronted by reverse-proxy on 443, sweep 8080 + 11434 + 8000 + 6333 on the same IP for the most common backend leak path.

### TLS cert pivot (VisorGraph)

Cert subject-CN field on :443 of the Tabby host typically `tabby.<org>` or `code.<org>` or `ai.<org>`. Operator portfolio mapping via cert-pivot is high-yield: one cert CN often surfaces 3-10 related coding tools, Ollama, internal model gateway, etc.

## 8. Citations / sources read

- https://github.com/TabbyML/tabby (README, releases)
- https://github.com/TabbyML/tabby/security/advisories (empty, confirmed)
- https://github.com/TabbyML/tabby/issues/1159 (token discussion)
- https://raw.githubusercontent.com/TabbyML/tabby/main/README.md
- https://raw.githubusercontent.com/TabbyML/tabby/main/CHANGELOG.md
- https://raw.githubusercontent.com/TabbyML/tabby/main/MODEL_SPEC.md
- https://tabby.tabbyml.com/docs/welcome/
- https://tabby.tabbyml.com/docs/quick-start/installation/docker/
- https://tabby.tabbyml.com/api/chat-completions/
- https://hub.docker.com/r/tabbyml/tabby
- https://deepwiki.com/TabbyML/tabby
- https://deepwiki.com/TabbyML/tabby/3.1-server-implementation-and-http-apis
- https://github.com/TabbyML/tabby/blob/main/ee/tabby-webserver/src/service/auth.rs
- https://docs.skypilot.co/en/latest/examples/applications/tabby.html
- https://railway.com/deploy/tabby
- https://huggingface.co/docs/hub/spaces-sdks-docker-tabby
- https://ramnode.com/guides/tabby
- https://docs.clore.ai/guides/ai-coding-tools/tabby

## 9. NuClide chain next steps (out of brief scope)

- Stage 0: Shodan dork sweep via Playwright web UI (basic + strict-favicon + version tiers).
- Stage 0b: Censys body-content dork on `/v1beta/server_setting` JSON keys, `/v1/health` HealthState shape.
- Stage 0c: scanner liveness + version + dork-FP strip + 8080 + 11434 + 6333 shadow sweep.
- Stage 0d: build `aimap/fingerprints/tabby.json` from `tome probe tabby` scaffold; deep-enum `/v1/health`, `/v1beta/server_setting`, `/v1beta/models`, `/favicon.ico`, `/swagger-ui/`. **Never** `/v1/completions` or `/v1/chat/completions`.
- Stage 1c-favicon: jaxen favicon hash enrichment via the static favicon.
- Stage 3v: verify candidates; 200-with-data on `/v1/health` earns the identity, on `/v1beta/server_setting` earns the config-leak finding.

---

**Brief status:** CANDIDATE (doc-grounded, host-unverified). Promote to CONFIRMED after Stage 0-3v verification on a live host.
