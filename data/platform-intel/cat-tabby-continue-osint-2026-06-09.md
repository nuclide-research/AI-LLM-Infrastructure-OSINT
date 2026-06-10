# Continue.dev — Cat-Tabby Stage -1 Intelligence Brief

Researcher: NuClide research squad 2 of 4
Date: 2026-06-09
Status: CANDIDATE (doc-grounded, host-unverified)
Scope: Continue.dev self-hosted server surface (Continue Hub, workspace server, proxy/agent components)

---

## Verdict (read first)

**Continue.dev is CLIENT-SIDE ONLY. No first-party self-hosted server surface to probe.**

What ships in the `continuedev/continue` repository:

- IDE extensions (VS Code, JetBrains)
- `cn` — Continue CLI (interactive + headless, stdio only)
- `core/` — TypeScript core that runs in-process inside the extension or CLI host; talks to the IDE webview via a local JSON-RPC channel (CVE-2026-8770 surface)

What is NOT in the open-source repo:

- No first-party self-hosted server
- No HTTP/REST daemon
- No web UI bound to a network interface
- No agent-as-a-service deployment (cn does not have a `--port` / `--listen` / server mode)
- No on-prem Continue Hub. hub.continue.dev / Mission Control is SaaS only

Repo positioning as of 2026-06: archived/read-only state, repositioned to "Source-controlled AI checks, enforceable in CI. Powered by the open-source Continue CLI." Product pivot from IDE-companion to CI-quality-checks. No server endpoint emerges from the pivot.

**Scope answer for Cat-Tabby:** the platform is OUT OF SCOPE for active Shodan-population probing as a Continue-branded surface. The exposed surface that operators actually run alongside Continue (Ollama, LiteLLM, vLLM, TGI) is in scope under those platforms' existing tome entries, not under "Continue."

This matches the Insight #21 / agno-survey pattern: agent platforms that turn out to be CLI/library-only with no operator-side endpoints. The finding for Continue is the verdict.

---

## Lane 1 — Auth modes & deploy config

| Component | Lives where | Listens on network? | Auth default |
|---|---|---|---|
| VS Code / JetBrains extension | User's IDE process | No | n/a (in-process) |
| `cn` CLI | User's terminal | No (stdio only) | n/a |
| Core JSON-RPC | Local IPC (extension webview <-> core) | **Localhost only** | None (local trust boundary) |
| Continue Hub | hub.continue.dev SaaS | n/a (not self-hostable) | SaaS account login |
| Upstream LLM gateway | Operator-chosen (Ollama, LiteLLM, vLLM, TGI) | **Yes** (these are the real surface) | Per-product default; Ollama=none, LiteLLM=master-key |

`config.yaml` is the canonical config format (`config.json` deprecated; `config.ts` removed). Auth toward upstream models = bearer token in `apiKey` field, or `requestOptions.headers` for custom auth. There is no Continue-side auth to misconfigure because there is no Continue-side server.

Sources:
- https://docs.continue.dev/customize/overview
- https://docs.continue.dev/guides/cli
- https://docs.continue.dev/guides/understanding-configs
- https://docs.continue.dev/guides/how-to-self-host-a-model

---

## Lane 2 — Shodan fingerprint & population

No first-party Continue server = no first-party Shodan fingerprint. The only Continue-related strings that could appear in banners are operator-side artifacts:

- TLS cert CN containing `continue.dev` or `hub.continue.dev` on a reverse-proxied LiteLLM/Ollama gateway (rare, operator-attribution surface)
- HTTP `Referer` / CORS allow-list entries naming `continue.dev` in front of a self-hosted gateway (not directly Shodan-indexable)

**Best Shodan probe = NONE for Continue itself.** Route the population question to the upstream-gateway platforms already in tome:

- `ollama` (port 11434, http.title:"Ollama")
- `litellm` (port 4000, OpenAI-compatible `/v1/models` w/ master-key gate)
- `vllm` (port 8000, OpenAI-compatible)
- `tgi` (HuggingFace Text Generation Inference, port 80/3000)

aimap fingerprint check: `/home/cowboy/go/pkg/mod/github.com/nuclide-research/aimap@v1.9.39/fingerprints.go` — only `continue` matches in source are Go `continue` keywords. No "Continue.dev" fingerprint exists. Correct outcome — there is no server to fingerprint.

nuclei templates: no `continuedev` / `continue.dev` templates found in projectdiscovery/nuclei-templates index search.

---

## Lane 3 — API surface & data exposure

The only Continue HTTP/RPC surface is the **local JSON-RPC channel** between the IDE webview and the core process. Bound to localhost. Documented endpoint names include the `lsTool` handler (CVE-2026-8770: path traversal via unvalidated `dirPath`). This is a *local* attack vector — exploitable only by code running in the same user session that can reach the local RPC channel.

| Endpoint class | Network exposure | Severity if remote |
|---|---|---|
| Local JSON-RPC (lsTool, others) | localhost only | n/a — not remote |
| Mission Control / Hub API | hub.continue.dev SaaS | Out of scope |
| Outbound model traffic | Operator's chosen upstream | Severity = upstream platform's |

**Do-not-call list for Continue:**

- The local JSON-RPC channel is not reachable across the network in any documented deployment, so there is no remote endpoint to put on a "do-not-call" list.
- If a survey ever finds a Continue JSON-RPC channel reachable across the network, that itself is the finding (misconfiguration class: localhost-IPC accidentally bound to 0.0.0.0). Do not enumerate further; report as a chained Cat-Tabby finding.

---

## Lane 4 — CVEs & prior research

**CVE-2026-8770** — Path traversal in `core/tools/implementations/lsTool.ts` (continuedev/continue <=1.2.22). lsTool handler accepts `dirPath` without normalization; supplying `..//` escapes the workspace root and enumerates arbitrary directories accessible to the IDE-running user. **Attack vector: local.** No vendor advisory or fix at publication. Vendor non-responsive.

Sources:
- https://www.sentinelone.com/vulnerability-database/cve-2026-8770/
- https://cve.threatint.eu/CVE/CVE-2026-8770

**GitHub Issue #9025** — community-reported privacy concern: extension allegedly sending code/telemetry to `api.github.com/copilot_internal/user` and `us.i.posthog.com` despite local-only configuration. Not a CVE; data-handling complaint. HIGH severity per reporter, no maintainer resolution visible.

CISA KEV: no entries.
HackerOne: continuedev does not run a public program; no public disclosures.

**Research gap:** no published research on operator misconfigurations (e.g., extension settings synced via Mission Control leaking into public repos as committed `config.yaml` with embedded API keys for upstream gateways). Worth a github-code-search pass under a separate engagement.

---

## Lane 5 — Deployment patterns

Continue is installed by the developer onto their workstation. The "self-hosted" articles users find are all about self-hosting the *upstream model gateway* that Continue points to, not Continue itself:

- "Self-Host Your AI Code Assistant With Continue.dev + Ollama" — Ollama is the server, Continue is the client
- "Complete Self-Hosted LLM Setup: Ollama + LiteLLM + Continue.dev" — Ollama + LiteLLM is the server stack
- "Deploy Continue.dev on RamNode VPS" — VPS hosts Ollama; Continue runs on the dev's IDE
- mojalab.com guide — typical chain is Ollama (11434) -> LiteLLM (4000) -> nginx (443) with only nginx public

Docker-compose searches surface stacks for Ollama+LiteLLM+nginx, never a Continue-server image. There isn't one.

CI mode (the new product positioning) runs as a GitHub Action calling the Continue CLI in headless mode — still no network listener.

---

## Lane 6 — Ecosystem co-deployment & adjacent surface

Operators self-hosting "Continue infra" almost universally run:

| Co-deployed | Default port | Already in tome? | Notes |
|---|---|---|---|
| Ollama | 11434 | (verify in tome) | The most common backend. Auth=none default. |
| LiteLLM | 4000 | yes (litellm.json) | OpenAI-compatible gateway. master-key gate. |
| vLLM | 8000 | (verify) | High-throughput OpenAI-compatible inference |
| TGI | 80/3000/8080 | (verify) | HuggingFace Text Generation Inference |
| nginx reverse proxy | 443/80 | n/a | Operator's TLS terminator |
| PostgreSQL (LiteLLM logs) | 5432 | n/a | Operator data layer |

Shadow-sweep priorities when a "Continue developer" operator is identified (e.g., from `config.yaml` leak or TLS-cert CN clue): scan 11434, 4000, 8000, 8080 on the same IP/ASN block. These are the actual surfaces.

---

## Insight candidate

**Codify candidate:** "Client-side-only platforms produce server-side findings via upstream-gateway exposure." Continue, agno, aider, and other CLI/extension coding agents do not contribute a Continue-branded Shodan population, but they *generate* operator-side LLM-gateway populations (Ollama, LiteLLM, vLLM) that *are* in scope. The platform's marketing footprint and the platform's attack surface live on different infrastructure.

Pair with Insight #21 (agno-survey pattern: CLI-only verdict is itself the finding).

---

## Sources

- https://github.com/continuedev/continue
- https://docs.continue.dev/customize/overview
- https://docs.continue.dev/guides/cli
- https://docs.continue.dev/guides/understanding-configs
- https://docs.continue.dev/guides/how-to-self-host-a-model
- https://deepwiki.com/continuedev/continue/3-core-components
- https://github.com/continuedev/continue/issues/9025
- https://www.sentinelone.com/vulnerability-database/cve-2026-8770/
- https://cve.threatint.eu/CVE/CVE-2026-8770
- https://changelog.continue.dev/
- https://mojalab.com/complete-self-hosted-llm-setup-ollama-litellm-continue-dev-integration-guide/
- https://dev.to/signal-weekly/self-host-your-ai-code-assistant-with-continuedev-ollama-vs-code-copilot-without-the-3ofe
