---
type: operational
---

# Operator Remediation Guide

_NuClide Research · 2026-05-04_
_If your IP appears in any of the [`case-studies/commercial/`](.) survey papers, this is your fix-it page._

---

## TL;DR

If you operate one of the platforms surveyed in 2026-05, **most exposures resolve to a single configuration change** to enable authentication. The most-effective hardening goes one step further and binds the service to localhost, so it's never reachable from the public internet at all. Both fixes together take ~10 minutes and require no application-code changes.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, S7068, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5868
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

**Most operators surveyed do not need to migrate, redesign, or buy a different product.** The platform you chose is fine; the configuration default is what's exposing you.

---

## By platform

### Qdrant (port 6333)

**Symptom:** Anyone on the internet can `GET /collections` against your IP and read your vector data.

**Fix in `config.yaml`:**
```yaml
service:
  api_key: <generate a strong random key, e.g. `openssl rand -hex 32`>
  read_only_api_key: <optional separate read-only key for read-only clients>
```

Restart Qdrant; set the same `api_key` in your application's Qdrant client (e.g. `QdrantClient(url=..., api_key=...)`).

**Better:** also bind Qdrant to localhost:

```yaml
service:
  host: 127.0.0.1
  http_port: 6333
  grpc_port: 6334
```

Access only from same-host clients or via private-network reverse proxy. Production Qdrant should not be on the public internet.

**If you have pre-created snapshots** (`/collections/<name>/snapshots`), they remain bulk-downloadable until you set `api_key`. The snapshot endpoint inherits the API auth state, once `api_key` is set, both live data and snapshot files require auth.

---

### ChromaDB (port 8000)

**Symptom:** Anyone on the internet can `GET /api/v2/heartbeat` and `GET /api/v2/tenants/.../collections` and read your collections.

**Fix:** Set environment variables before starting Chroma:

```bash
export CHROMA_SERVER_AUTHN_PROVIDER="chromadb.auth.token_authn.TokenAuthenticationServerProvider"
export CHROMA_SERVER_AUTHN_CREDENTIALS="<your strong random token>"
export CHROMA_SERVER_AUTHZ_PROVIDER="chromadb.auth.simple_rbac_authz.SimpleRBACAuthorizationProvider"
export CHROMA_SERVER_AUTHZ_CONFIG_FILE="/path/to/authz.yaml"
```

For client requests, send `Authorization: Bearer <token>` header.

**Better:** bind Chroma to localhost via `chroma run --host 127.0.0.1 --port 8000`.

---

### Milvus (port 19530, REST + gRPC)

**Symptom:** Anyone on the internet can `POST /v2/vectordb/collections/list` and read your collection schemas.

**Fix:** Enable Milvus RBAC in `milvus.yaml`:

```yaml
common:
  security:
    authorizationEnabled: true
    superUsers:
      - root
```

Set the `root` user's password and create per-application users. Configure all clients to use these credentials.

**Better:** bind Milvus's proxy to localhost in your Docker Compose / k8s deployment, and access only via same-host or VPN.

---

### Ollama (port 11434)

**Symptom:** Ollama has no built-in authentication. Anyone on the internet can `GET /api/tags`, list your models, and `POST /api/generate` to use your hardware.

**Fix at the network layer** (Ollama itself cannot enforce auth):

1. Set `OLLAMA_HOST=127.0.0.1` before starting Ollama, so it binds to localhost only.
2. If you need network access, run Ollama behind a reverse proxy (Caddy, nginx, Traefik) with HTTP basic auth or OAuth. The reverse proxy adds the auth layer Ollama lacks.
3. Add a firewall rule to drop port 11434 traffic from outside your private network.

**`:cloud` model exposure note:** If your operator has `:cloud`-suffix models registered (e.g., `minimax-m2.7:cloud`, `deepseek-v4-pro:cloud`), every external prompt against those models bills the operator's Ollama Cloud subscription. Until you fix the network exposure, attackers can drain your Ollama Cloud credits at no cost to themselves. **Rotate your Ollama Cloud API key immediately if your instance has been exposed.**

---

### MLflow Tracking Server (port 5000)

**Symptom:** Anyone on the internet can `GET /api/2.0/mlflow/experiments/search` and read your experiment history. **Plus** if you're running MLflow ≤ 2.11.x, **CVE-2023-1177 path traversal is actively exploited in the wild**, attackers inject experiments with `artifact_location` like `http:///#/../../../../../../../../../../../../../../etc/` to read your filesystem.

**Fix immediately:**

1. **Upgrade MLflow to ≥ 2.12.0** to patch CVE-2023-1177.
2. Enable basic auth: launch MLflow with `mlflow server --app-name basic-auth` and set `MLFLOW_AUTH_CONFIG_PATH` pointing to a config with admin credentials.
3. Bind to localhost: `mlflow server --host 127.0.0.1`.

**If you see attacker-injected experiments** with names like `3BT8ncOzBWAH4GyIGz0EXsSwj7f` and `artifact_location` containing `..` path-traversal segments, **assume root compromise.** Rotate SSH keys, rebuild the host from a clean image, and audit any data the MLflow process had filesystem access to.

---

### Streamlit (data apps, varies on port)

**Symptom:** Streamlit has no built-in authentication. Anyone hitting your Streamlit URL can use the app.

**Fix:** front Streamlit with a reverse proxy that enforces auth:
- Caddy + `basicauth`
- nginx + `auth_basic`
- Streamlit Community Cloud + Single Sign-On
- Cloudflare Access in front of the Streamlit IP

Or build OAuth into the Streamlit app via [streamlit-authenticator](https://github.com/mkhorasani/Streamlit-Authenticator) library.

---

### MinIO (object storage, port 9000 + 9001 console)

**MinIO ships auth-on by default** and our 852-instance survey found 0% anonymous-bucket-listable hosts. **You're probably OK on this one.**

If you want extra hardening:
- Make sure your `MINIO_ROOT_USER` is not the default `minioadmin`/`minioadmin`
- Don't expose port 9001 (Console) on the public internet, bind to private network or VPN-only
- If you're on a release older than `RELEASE.2023-07-21T21-12-44Z`, **upgrade now** to patch CVE-2023-28432 (information disclosure via env-var endpoint)

---

### Open WebUI (chat-UI, port 3000 / 8080)

**Open WebUI ships auth-on by default**, but two operator misconfigurations are common:

1. **`enable_signup: true`** lets any internet visitor register for a free account on your operator's instance. Set this to `false` in production. Run `WEBUI_AUTH=true && DISABLE_SIGNUP=true` env vars or set `enable_signup: false` in config.

2. **Backing Qdrant/Mem0 left unauth**, even if Open WebUI is auth-protected, the data tier (Qdrant on port 6333, ChromaDB on port 8000, Mem0 backing store) is reachable separately. Apply the per-platform fixes above to the data tier too.

---

### vLLM / OpenAI-compatible LLM servers (port 8000)

**vLLM has optional API-key auth** but ships off by default.

**Fix:** start vLLM with the `--api-key` flag:

```bash
python -m vllm.entrypoints.openai.api_server \
  --model <your-model> \
  --api-key "<your strong random key>"
```

Clients must then send `Authorization: Bearer <key>` header.

**Better:** front vLLM with a reverse proxy that adds auth + rate-limiting.

**Reseller-proxy note:** If you're running vLLM as a Grok2API / Kiro-Go / AgentBar reseller relay, **every external prompt burns your upstream operator's API credits**. Until you fix auth, attackers can drain your OpenAI/Anthropic/etc. account at no cost. Rotate your upstream API key after applying the fix.

---

## After remediation: what to verify

For any of the above, verification is the same shape:

```bash
# Before the fix, this returns 200 OK with data
curl http://<your-ip>:<port>/<endpoint>

# After the fix, this should return 401 / 403 / connection refused
curl http://<your-ip>:<port>/<endpoint>
```

Test from a network outside your private network (e.g., from a phone on cellular data) to confirm the fix is reachable from the public internet's perspective.

---

## What if my exposure has been catalogued in NuClide's published surveys?

The case studies in this folder reference operator IPs but redact operator-identifying details (TLS cert SAN, etc.) until coordinated-disclosure windows complete (typically 30 days from first contact). After remediation, operators may:

1. **Reply to NuClide's disclosure email** confirming the fix. NuClide will update its disclosure log + the case study to reflect remediation.
2. **Choose to remain redacted** even after remediation (some operators prefer not to be publicly named in connection with a prior exposure). NuClide honors this, only the redaction is lifted, never operator identity, without explicit operator consent.
3. **Accept attribution** if the operator wants to publicly model the remediation pattern for the broader community (rare but valuable; helps shift industry defaults).

Contact: `nicholas@nuclide-research.com`

---

## Upstream fix request

The aggregate finding across NuClide's 2026-05 survey series is:

> Every modern AI/ML data-tier platform that ships with authentication off by default is, at population scale, deployed without authentication on the public internet.

The most effective fix is **not per-operator remediation** (slow, never finishes, scales poorly). It's **upstream default change**: have the platform refuse to start (or auto-generate an admin credential and log it) without explicit operator opt-in to the auth-off mode.

NuClide is happy to support upstream-maintainer conversations on:

- Qdrant: change `service.api_key` from "unset" to "auto-generate + log to stderr on first start"
- ChromaDB: change `CHROMA_SERVER_AUTHN_PROVIDER` from "unset" to "token_authn with auto-generated token"
- Milvus: change `authorizationEnabled` default from `false` to `true` with auto-generated `root` password
- Ollama: ship with `OLLAMA_HOST=127.0.0.1` default, not `0.0.0.0`. Document the reverse-proxy auth pattern in the README.

The MinIO and Dify positive controls in the survey series demonstrate that auth-on-default platforms have ~0% unauth at population scale, even from the same operator audience that leaks Qdrant/Milvus/MLflow at 100%. **Default is the deployment.**

---

## See also

- [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md), cross-survey synthesis with the auth-on-default tier map
- Per-platform survey papers in this folder
- [`disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md`](disclosure/qdrant-snapshot-disclosure-ledger-2026-05.md), disclosure tracking
