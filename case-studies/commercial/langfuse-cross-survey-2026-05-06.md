---
type: survey
title: Langfuse cross-survey-correlation single-host case study (2026-05-06)
date: 2026-05-06
class: substrate
category: llm-observability
status: surveyed-partial
methodology: cross-survey-correlation
---

# Langfuse: cross-survey-correlation single-host case study

NuClide Research · 2026-05-06

## Summary

Single confirmed Langfuse exposure surfaced via a **cross-survey-correlation methodology** when Shodan API access was unavailable. The exposed instance is part of a **stacked four-platform AI catastrophe** at one Greek startup-hub operator (`pharos.unistarthubs.gr`, Hetzner DE, IP `135.181.252.66`):

1. **Langfuse v3.73.1** on port 3001, `signUpDisabled:false` (open public registration), credentials-only auth
2. **Mem0 / Milvus** on port 19530, fully unauthenticated, agent-memory collections (`experience_memory`, `mem0migrations`, `all`, `all_v3`)
3. **Attu** Milvus admin GUI on port 3000, loads without auth, can connect to local Milvus
4. **Pharos** AI Assistant SPA on port 8080, branded React webapp with **`CLIENT_SECRET` literally hardcoded in `/env.js`**

The four exposures chain to give an attacker complete operational visibility into the operator's AI product:

- **Sign up to Langfuse → read every logged LLM interaction** (system prompts, user inputs, model outputs, tool-call invocations) for the operator's Pharos app
- **Direct unauth read of Mem0 agent memory** via Milvus, every persisted user-conversation memory
- **Use the leaked `CLIENT_SECRET` from `env.js`** to authenticate against the Pharos backend (chat WebSocket endpoint surfaced at `/api/query/ws/chat/query`)
- **Combine** to reconstruct full multi-turn agent interactions, customer identities (where logged in traces), and the operator's prompt-engineering IP

**Severity:** CRITICAL.

## Discovery methodology: when Shodan dies

This case study was produced under an unusual constraint: the Shodan API key tied to NuClide's research account had expired before the survey began. The canonical Shodan-driven discovery (`visorplus full <dork>`, `jaxen hunt`, `visorsd`) was unavailable. CT logs (`crt.sh`, `certspotter`) returned mostly Northflank PaaS addon backends (`langfuse-pg--<id>.addon.code.run`) but very few operator-deployed Langfuse webapp frontends, operators rarely include "langfuse" in subdomain names of self-hosted instances.

The fallback methodology applied: **probe the IPs already in the NuClide ledger from prior surveys**. The hypothesis: operators who already expose a Tier-A platform (Ollama, Qdrant, Milvus, MLflow, ChromaDB, vLLM, Streamlit, MinIO, Open WebUI, Specialty Data Layers) may also expose Langfuse on the standard port 3000, same operator, same auth-off pattern, adjacent platform.

### Probe sweep: methodology insight #9

Methodology Insight #9 (added to [SYNTHESIS-2026-05.md](SYNTHESIS-2026-05.md)): **cross-survey-correlation as a Shodan-free discovery vector**.

Two sweeps over 723 unique IPs from prior cloud surveys:

| Probe | Targets | Ports | Hits | Hit rate |
|---|---|---|---|---|
| Pass 1, strict default port | 723 | 3000 (HTTP/HTTPS) | 0 | 0% |
| Pass 2, alt ports | 723 | 3001, 8080, 443, 80 (HTTP/HTTPS where applicable) | **1** | 0.14% |

Strict matcher: HTTP 200 + `Content-Type: application/json` + JSON body with `status == "OK"` + `version` field present. The conjunctive matcher per Methodology Insight #6 ruled out FPs; the single hit was confirmed by additional probes against `/api/public/projects` (returns 401, confirms Langfuse auth-side surface).

The 0/723 result on the default port and 1/723 on the alt ports is itself **a cross-tier finding worth noting**:

- The operator population that exposes Tier-A platforms (vector DBs, inference servers) is **not** the same population that exposes Langfuse on default ports
- Either: (a) Langfuse operators are a different security-aware stratum, (b) Langfuse is typically deployed behind reverse proxies that terminate `/api/public/health` differently, or (c) operators colocate with another :3000 service and shift Langfuse to alt ports. The single hit on port 3001 is consistent with hypothesis (c), `pharos.unistarthubs.gr` runs Attu admin GUI on :3000 (default for Attu), so Langfuse necessarily moved to :3001.

A full Langfuse population survey via Shodan dorks (`"Langfuse" port:3000`, `http.title:"Langfuse"`) is **deferred** until Shodan API access is restored. The query catalogue at [`shodan/queries/05-gateways-monitoring.md`](../../shodan/queries/05-gateways-monitoring.md) cites ~1,131 hits for `"Langfuse" port:3000` as of last harvest, the population is non-trivial.

## Per-host detail: `135.181.252.66` (Hetzner DE)

### Identification

- **IP:** `135.181.252.66`
- **rDNS:** `pharos.unistarthubs.gr`
- **TLS cert SANs (via VisorGraph cert pivot):** `unistarthubs.gr`, `*.unistarthubs.gr` (Google Trust Services R1, expires 2026-08-01)
- **Hosting:** Hetzner Online GmbH, Germany
- **Operator:** Unistart Hubs (Greek startup hub / accelerator, domain `unistarthubs.gr`, Cloudflare-fronted)
- **Adjacent IPs:** `.70` resolves to `backend.zapier.hu` (Zapier integration backend, separate operator), `.68/.69/.71` are Hetzner static-pool generic
- **Sector:** Commercial / startup-tech

### Port surface

| Port | Service | Auth | Severity | Notes |
|---|---|---|---|---|
| 80/tcp | nginx 1.27.5 | n/a | low | Static placeholder page |
| 3000/tcp | **Attu** (Milvus admin GUI) | none on the GUI itself | medium | UI loads anonymously; can connect to the local Milvus on `127.0.0.1:19530` (which has no auth) |
| 3001/tcp | **Langfuse v3.73.1** | password-only, **signup-open** | **critical** | `signUpDisabled:false`, `authProviders.credentials:true` (only) |
| 8080/tcp | **Pharos** AI Assistant SPA | `env.js` leaks `CLIENT_SECRET` | **critical** | React app titled "Pharos, Your AI Assistant"; bundle exposes Langfuse public-API integration paths and a Pharos-internal `/api/query/ws/chat/query` chat WebSocket |
| 19530/tcp | **Milvus** REST/HTTP | **none** | high | Already in NuClide ledger as event #220 (Mem0-on-Milvus deployment); collections `experience_memory`, `mem0migrations`, `all`, `all_v3` |
| 9091/tcp | (Milvus metrics, port closed at probe time) |, |, |, |
| 443/tcp | (closed; main `unistarthubs.gr` is Cloudflare-fronted) |, |, |, |

### Langfuse exposure detail

`/api/public/health` returns:

```json
{"status":"OK","version":"3.73.1"}
```

`/api/public/projects` returns `HTTP 401 Unauthorized` (auth required for the API surface). However the SSR-rendered `__NEXT_DATA__` blob on `/auth/sign-in` carries the runtime auth config:

```json
"authProviders": {
  "google": false, "github": false, "githubEnterprise": false,
  "gitlab": false, "okta": false, "credentials": true,
  "azureAd": false, "auth0": false, "cognito": false,
  "keycloak": false, "workos": false, "custom": false, "sso": false
},
"signUpDisabled": false,
"runningOnHuggingFaceSpaces": false
```

`signUpDisabled:false` is the load-bearing line. Any internet visitor can navigate to `/auth/sign-up`, register an account (the operator's PostgreSQL persists a user record), and then call the authenticated Langfuse API endpoints (`/api/public/projects`, `/api/public/traces`, `/api/public/observations`, `/api/public/scores`, `/api/public/datasets`, `/api/public/dataset-items`) on their own behalf. The aimap deep enumerator (`enumLangfuse` at `enumerators.go:710`) flags this as the highest-severity finding for any Langfuse instance.

The lack of SSO/OIDC providers (only `credentials:true`) compounds the risk, there's no identity-provider brute-force ceiling and no centralized MFA. A registered attacker has the same access as a legitimate operator-authenticated user, except they are not in the operator's identity directory.

### Pharos `CLIENT_SECRET` leak

`http://135.181.252.66:8080/env.js` returns:

```js
window.APP_CONFIG = {
    CLIENT_SECRET: '<32-char alphanumeric secret value redacted from public case study;
                     transmitted privately to the operator + Hetzner abuse>'
};
```

> **Why redacted here:** the secret is already published by the operator's misconfiguration, but republishing it in NuClide's case study amplifies discoverability beyond the stray JS bundle. The full value is held out-of-git at `~/recon/pharos-langfuse-2026-05-06/env-js-secret.txt` and was included in the disclosure email to `abuse@hetzner.com` + `security@unistarthubs.gr` (sent separately, not included in the disclosure draft committed to this repo). Once the operator confirms remediation (rotation), the case study can be updated to include a hash or partial fingerprint as historical evidence.

The secret is loaded into the page as `window.APP_CONFIG.CLIENT_SECRET` and would be referenced by the bundled JS (likely the Pharos chat WebSocket initialization). It is published to every visitor of port 8080 in plain text. Whatever auth surface this secret unlocks (the Pharos backend chat WebSocket, an OAuth integration, or a custom session-issuer flow), an unauthenticated attacker has the secret in hand without any prior credential.

The Pharos main JS bundle (`/static/js/main.bf027797.js`, 1.1 MB) references the following API paths (extracted via `grep`):

```
/api/public/dataset-items       (Langfuse)
/api/public/dataset-items/      (Langfuse)
/api/public/dataset-run-items   (Langfuse)
/api/public/datasets            (Langfuse)
/api/public/datasets/           (Langfuse)
/api/public/ingestion           (Langfuse - trace/event ingest)
/api/public/v2/prompts          (Langfuse - managed prompt templates)
/api/public/v2/prompts/         (Langfuse)
/api/query/ws                   (Pharos backend, WebSocket)
/api/query/ws/chat/query        (Pharos backend, chat WebSocket)
```

The Pharos app is a Langfuse-instrumented LLM application, it sends traces, manages prompt templates, and uses Langfuse datasets, all via the Langfuse SDK pointed at `http://135.181.252.66:3001`.

### Mem0 / Milvus exposure (existing finding)

Already documented in [`milvus-cloud-survey-2026-05.md`](milvus-cloud-survey-2026-05.md), collections `experience_memory`, `mem0migrations`, `all`, `all_v3`. The Mem0 framework writes an embedding for every persistent piece of user-conversation memory; with unauth read access to the Milvus collection, an attacker can dump the full agent-memory store.

Combined with the Langfuse trace exfil, an attacker has both the **operational logs** (what the agent did, when, and what the user said) and the **persistent memory** (what the agent learned about the user across sessions).

### Attu admin GUI exposure (new)

Attu is the official Milvus web admin GUI. The Attu container is configured to connect to the local Milvus instance (`127.0.0.1:19530`) by default. Anyone navigating to `http://135.181.252.66:3000/` can interact with Attu's UI to:

- Browse all collections
- Inspect schema and field types
- Execute search queries (read embeddings + payload metadata)
- Drop / create collections (write surface)

Attu inherits Milvus's auth posture, since the Milvus instance has no auth, Attu has full read+write authority over it.

## Toolchain provenance

```
Pass 1: cross-probe.py port 3000        →   0 confirmed Langfuse from 723 ledger IPs
Pass 2: altports-probe.py 3001/8080/443/80 →   1 confirmed → 135.181.252.66:3001
visorgraph -domain unistarthubs.gr      →   cert pivot (4 nodes / 1 edge), confirmed cert SANs
aimap-profile --target 135.181.252.66 --mode fast →  full passive recon: rDNS, MX, neighbors, web surface
nuclide-contact --ip 135.181.252.66     →   rDNS pivot pharos.unistarthubs.gr; recipient pattern resolved
JS extraction (curl + grep)             →   Pharos env.js CLIENT_SECRET leak; Langfuse SDK integration paths
visorlog add (event #862)               →   ledger entry, severity critical
visorscuba assess                       →   2 violations (AI.C1 + AI.H1); score 0/0
bare /tmp/bare-input-langfuse.json --top 5 →  no commodity Metasploit module (top score 0.45 - first-party authz class, not commodity CVE)
visorcorpus build (kb_exfil + system_prompt + config_secrets) →  46-case adversarial corpus saved at /tmp/visorcorpus-langfuse-trace-exfil.json
```

## Methodology Insight #9: cross-survey-correlation as Shodan-free fallback

When Shodan API access is unavailable, the next-best discovery vector for an additional platform-class survey is the **set of IPs already confirmed exposed in prior NuClide surveys**. This vector has three properties:

1. **Free**, no API credits, no rate limits.
2. **Pre-validated targets**, every IP in the ledger is a known operator who has already shipped at least one auth-off platform; the priors for them shipping a second auth-off platform are higher than population baseline.
3. **Cross-platform-correlation finding bonus**, when the survey hits, the result is automatically a *stacked exposure on a single operator*, which is more impactful for disclosure than a single-platform finding.

The cost: low yield. 1 hit in 723 IPs is a 0.14% hit rate, two orders of magnitude below the per-platform rates observed in dedicated tier-2 cloud surveys (Ollama tier-2: ~24% confirmed-AS-real Ollama on candidate IPs). For a population finding, Shodan-driven discovery is necessary. For a single-host case study + a methodology demonstration, cross-survey-correlation is sufficient.

The 1 hit also validates the **alt-port hypothesis**, operators who colocate two web services on adjacent ports often shift the second service off its default. Future cross-survey probes should sweep ports 3000+3001+3002, 8080+8081+8082, 5000+5001 rather than the canonical default alone.

This insight is folded into [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) as Methodology Insight #9.

## Severity classification

| Component | Severity | Rationale |
|---|---|---|
| Langfuse signup-open | **critical** | Anyone can register → read all stored LLM traces (system prompts, user inputs, model outputs). Persistent attacker presence after first signup |
| Pharos `CLIENT_SECRET` leak | **critical** | App secret in plain `env.js`. Unlock surface unknown but guaranteed non-zero, would not be set as `CLIENT_SECRET` if it were inert |
| Mem0/Milvus unauth | high | Already in ledger; attacker reads persistent agent-memory store |
| Attu admin GUI exposure | medium | UI front-end to the unauth Milvus; expands operational surface for the same data |

Combined: **CRITICAL operator catastrophe**, full LLM application observability + agent memory + app secret all reachable to a single anonymous internet caller in <5 minutes.

## Disclosure routing

Two-channel notification recommended:

- **Hosting provider:** `abuse@hetzner.com` (the IP block is RIPE-allocated to Hetzner Online GmbH; Hetzner abuse handles customer notification per their AUP)
- **Operator-direct:** `security@unistarthubs.gr` (pattern-guess + MX-validated; `unistarthubs.gr` MX is `mail.unistarthubs.gr`, accepts mail)

A third channel, Greek national CSIRT (`info@csirt.gr` for ENISA-coordinated disclosure of GDPR-relevant findings), should be considered if the operator does not respond within 14 days. The agent-memory store likely contains personally-identifiable user data, putting the finding within GDPR Article 33 breach-notification scope.

## Future work

1. **Shodan-driven full Langfuse population survey**, deferred until API key restored. The query `"Langfuse" port:3000` returned ~1,131 hits as of last harvest; aimap's `enumLangfuse` deep enumerator is ready to fire on the cohort with no per-survey bespoke probe needed (per Methodology Insight #6).
2. **Cross-survey-correlation on alt-port grid**, apply the methodology to other expected-default-3000 platforms (Open WebUI on 3000+3001+3002, n8n likewise, Flowise likewise) to find operator-shifted instances missed by default-port-only probes.
3. **Pharos `CLIENT_SECRET` impact assessment**, without using the secret to authenticate (which would cross from PoC into active exploitation), enumerate which OAuth or API surface this secret is bound to. The `/api/query/ws/chat/query` WebSocket is the most likely binding.
4. **Mem0-on-Milvus collection content audit**, already covered in `milvus-cloud-survey-2026-05.md`; the `experience_memory` collection should be inspected for PII shape (count + sample without exfil) to size the GDPR exposure.

## References

- VisorLog event #862, `data/nuclide.db`, source `nuclide-langfuse-cross-probe-2026-05-06`
- VisorScuba violations, AI.C1 (auth-required default), AI.H1 (cloud-proxy paid-quota exposure)
- VisorCorpus adversarial corpus, `/tmp/visorcorpus-langfuse-trace-exfil.json` (46 cases, kb_exfiltration + system_prompt + config_secrets categories)
- aimap fingerprint, `fingerprints.go:291` Langfuse entry
- aimap deep enumerator, `enumerators.go:710` `enumLangfuse` (signup-disabled / SSO / public-projects checks)
- Cross-survey synthesis, [`SYNTHESIS-2026-05.md`](SYNTHESIS-2026-05.md) Methodology Insight #9
