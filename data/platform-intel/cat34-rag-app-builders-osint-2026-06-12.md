# Cat-34 — Self-Hosted LLM-App / RAG Builders

Category slug: `rag-app-builders` | Date: 2026-06-12 | Platforms: 27

## Category Thesis

This class is the composition layer of the AI stack. Each platform sits between three high-value asset pools at once. It holds the operator's upstream LLM provider keys (OpenAI, Anthropic, Azure, Bedrock, and a dozen more) wired into model-provider config. It holds the ingested RAG corpus, the org's own documents, frequently PII, PHI, contracts, and internal source material. And it holds the business-logic flows, the prompts, tool wiring, agent definitions, and data-source bindings that describe how the org runs.

A single foothold on one of these collapses all three. An exposed admin claims the LLM keys (LLMjacking, direct cost), reads the corpus (data breach), and reads the flows (business intelligence). The composition layer is worse than the sum of its parts because the parts are co-located by design. Most of these ship as multi-container Docker Compose stacks where the vector store, the object store, and the relational DB ride along on the same host with default credentials, so the app's auth gate is only the front door of a house with the windows open.

The version dimension matters. Auth-on-default strengthens across OSS generations under disclosure pressure (Insight #40). Flowise moved from open-by-default (pre-3.0.1, the 12,000-host fleet behind CVE-2025-8943) to a forced org-setup wall in 3.0.1+. Langflow added API-key enforcement at 1.5. The exposed population is dominated by old builds, not current ones.

## Per-Platform Table

| Platform | Ports | Auth Default | Conf | Top Sensitive Asset |
|---|---|---|---|---|
| Dify | 80, 443, 5003 | auth-on-default | HIGH | Per-workspace upstream LLM keys; claimable-admin race via empty INIT_PASSWORD first-run window |
| Langflow | 7860 | open-by-default | HIGH | Global Variable LLM keys in flow JSON; superuser UI = arbitrary Python = RCE |
| Flowise | 3000 | auth-on-default | HIGH | Encrypted creds decryptable with on-disk key; pre-3.0.1 fully unauth fleet |
| RAGFlow | 80, 443, 9380-9384 | auth-on-default | HIGH | Ingested docs in MinIO/ES (default `infini_rag_flow`); admin server ON with admin@ragflow.io/admin |
| AnythingLLM | 3001 | configurable-default-off | HIGH | Upstream LLM keys readable when AUTH_TOKEN unset (quickstart default) |
| Quivr | 3000, 5050, 5555, 6379 | configurable-default-on | HIGH | Forgeable HS256 tokens (public Supabase demo secret shipped); brains/chats |
| PrivateGPT | 8001, 8080 | configurable-default-off | HIGH | Ingested corpus via unauth /v1/chunks; auth.py installs always-true gate |
| Verba | 8000, 8080, 3000 | ui-gated-api-open | HIGH | RAG corpus via WebSocket (zero auth); paired Weaviate anon access |
| Cognita | 5001, 8000, 6333-6334, 7997, 9500, 11434, 5432 | open-by-default | HIGH | LLM keys via zero-click RCE chain (CVE-2025-27519 + CVE-2025-27518) |
| R2R | 7272-7274 | configurable-default-off | HIGH | LLM keys via /v3/system/settings config_toml dump (anonymous-superuser) |
| Khoj | 42110 | open-by-default | HIGH | Personal knowledge base (PII); shipped --anonymous-mode = unauth premium user |
| LibreChat | 3080, 8000, 7700, 27017, 5432 | configurable-default-on | HIGH | Repo-default JWT/CREDS keys decrypt stored provider keys; first-user-admin race |
| Lobe Chat | 3210 | configurable-default-off | HIGH | LLM keys via forgeable X-lobe-chat-auth (XOR, not signed); unauth /webapi/proxy SSRF |
| BionicGPT | 3000, 7703, 7700 | configurable-default-off | HIGH | Quickstart bakes DANGER_JWT_OVERRIDE = every visitor is admin John Doe |
| Hayhooks | 1416, 1417 | open-by-default | HIGH | Unauth /deploy_files Python upload = RCE; pipeline definitions |
| Open WebUI | 3000, 8080 | auth-on-default | HIGH | RAG docs + chats; first-registrant-admin race; SSRF to cloud metadata |
| FastGPT | 3000, 3003, 3005, 9000, 9001 | auth-on-default | HIGH | root/1234 shipped default (reset every restart); unauth SSRF proxy |
| MaxKB | 8080 | auth-on-default | HIGH | Global default admin/MaxKB@123.. baked into image; LLM keys + corpus |
| QAnything | 8777, 9210, 19540, 3316, 9200, 19530, 3306, 9001 | open-by-default | HIGH | Unauth get_file_base64 returns raw ingested files; user_id is free-text |
| Kotaemon | 7860 | auth-on-default | HIGH | admin/admin shipped default; path traversal reads .env (CVE-2025-53358) |
| h2oGPT | 7860, 5000 | open-by-default | HIGH | Private doc corpus; unauth OpenAI proxy on 5000 = LLMjacking |
| RAGapp | 8000, 6333, 11434 | open-by-default | HIGH | Unauth /api/management config+files+agents by vendor design |
| Morphik | 8000, 3003, 5432, 6379, 11434, 6000 | configurable-default-off | HIGH | bypass_auth_mode=true shipped; installer defaults to skip-password |
| Casibase | 14000, 3306 | ui-gated-api-open | HIGH | Anonymous Casbin policy grants read+write on chats/stores; /chat/completions authz bypass |
| LocalGPT | 3000, 8000, 8001, 11434 | open-by-default | HIGH | Bare BaseHTTPRequestHandler, no auth table exists (CVE-2026-5000) |
| Chatbot UI | 3000, 54321-54324 | configurable-default-off | HIGH | Hardcoded Supabase demo service_role JWT in migration; open self-signup |
| Vanna | 8084, 5000 | open-by-default | HIGH | Unauth /api/v0/run_sql against connected production DB; NoAuth() default |

## Class-Level Auth-on-Default Verdict

Of 27 platforms, the posture splits:

- **open-by-default: 10** — Langflow, Cognita, Khoj, Hayhooks, QAnything, h2oGPT, RAGapp, LocalGPT, Vanna. (Counting the dominant deployed reality, not the marketing claim.)
- **ui-gated-api-open: 2** — Verba, Casibase.
- **auth-on-default: 7** — Dify, Flowise, RAGFlow, Open WebUI, FastGPT, MaxKB, Kotaemon.
- **configurable-default-off: 6** — AnythingLLM, PrivateGPT, Lobe Chat, BionicGPT, Morphik, Chatbot UI.
- **configurable-default-on: 2** — Quivr, LibreChat.

The verdict for the class: **auth-on-default is the minority, and even within it the gate is frequently hollow.** 10 of 27 ship open. 6 more ship auth code that is OFF by default, so the documented quickstart produces an open instance unless the operator takes an extra step the install prompt does not force (Morphik's installer literally defaults to "press Enter to skip"). That is 16 of 27 where the documented happy path yields an unauthenticated UI and API.

The 7 true auth-on-default platforms are not clean either. Four ship a globally-identical default credential that degrades the gate to near-open: FastGPT root/1234, MaxKB admin/MaxKB@123.., Kotaemon admin/admin, RAGFlow admin@ragflow.io/admin (on the admin server that is ON by default). Three rely on a first-user-becomes-admin race (Dify, Open WebUI, Flowise org-setup) where an attacker who reaches the port before the operator registers claims admin with no credential at all.

The two ui-gated-api-open cases are the cleanest illustration of the failure mode: the browser UI shows a login, the JSON API does not enforce it. Verba's WebSocket RAG endpoints bypass the same-origin middleware entirely. Casibase's Casbin policy explicitly whitelists the anonymous role for read AND write on chats and stores, and short-circuits authz on /chat/completions.

**Evidence quality: HIGH across all 27.** Every auth verdict is anchored to a named primary source: the shipped .env.example or docker-compose, the specific auth-handler source file with the gating logic quoted, and the vendor's own quickstart docs. This is not framing-level attribution. It is source-level. The auth-on-default thesis is falsifiable here and the data largely refutes it for this category: the composition layer does not ship secure.

## Restraint Posture

The exposed knowledge base is the dangerous primitive in this category, and not only because of what reading it leaks. The read primitive sits one URL away from the poison-write primitive. On most of these platforms the same unauthenticated surface that lists ingested documents also accepts new ones: Hayhooks /deploy_files, RAGapp /api/management/files, Verba /ws/import_files, Casibase anonymous /api/add-message, Vanna /api/v0/train, LocalGPT /indexes/{id}/upload. RAG-poisoning research (corpus injection of adversarial documents that the retriever later surfaces as grounded fact) means a write to an exposed knowledge base is a persistent injection into every downstream answer the org trusts. The read endpoint and the poison endpoint are siblings on the same router.

So the discipline is hard. We enumerate, we do not exfiltrate. We read document names, collection names, schema, version banners, and config flags. Those are the finding. The presence of `{"step":"not_started"}` on a Dify host is the finding without claiming the admin. The `registrationEnabled:true` in LibreChat /api/config is the finding without registering. We sample a payload minimally only to confirm severity (one chunk to confirm the corpus is PII-bearing, not the corpus). We never POST to a write or train or deploy route on a third-party host. We never run /api/v0/run_sql. We never forge the HS256 token even when the secret is public. Blocked or gated access is logged as "surface open, access not exercised," never inflated to a confirmed read. The claimable-admin window is detected, not claimed. Names are the finding.

## Misconfiguration Class Summary

The recurring class across all 27: the operator runs the documented quickstart, exposes the port, and inherits an insecure default the vendor either chose (Khoj --anonymous-mode, RAGapp "auth is your gateway's job," Vanna NoAuth()) or buried (Morphik bypass_auth_mode=true, Chatbot UI open Supabase signup). The fix is uniform and real-world: a fronting reverse proxy with auth, network isolation of the backing stores, rotation of every shipped secret, and a version bump past the unauth-RCE fix line. None of these require the vendor to change anything. All require the operator to not trust the default.
