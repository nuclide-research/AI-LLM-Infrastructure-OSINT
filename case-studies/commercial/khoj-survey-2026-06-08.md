# Khoj — Personal RAG Population Survey

**Date:** 2026-06-08
**Category:** Cat-52 — Personal RAG / Self-Hosted AI Assistants
**Surveyor:** NuClide Research
**Methodology:** Shodan harvest -> verifier (GET only) -> verdict bucket -> codify

---

## Target

[Khoj](https://github.com/khoj-ai/khoj) is a self-hostable personal AI assistant
that builds a RAG index over a user's documents (Notion, Obsidian, GitHub,
PDF, Markdown, local filesystem) and exposes a chat UI for asking
questions against that index. It runs as a single Docker container,
exposes port 42110 by default, and is most commonly deployed as a
personal sidecar to an Obsidian or note-taking workflow. The hosted
version runs on Fly.io under khoj.dev; the self-hosted population is what
this survey targets.

The Khoj security model is documented as "single-user by default" — if
auth is not explicitly configured, the entire instance is owned by an
anonymous user with the canonical email `default@example.com`. Khoj's
own docs flag this and instruct production deployments to set
`KHOJ_DEBUG=False`, disable anonymous mode, and configure either Google
OAuth or Magic Link auth. Operators who skip these steps expose their
personal RAG index to the public internet.

---

## Population

| Dork | Count | Notes |
|---|---|---|
| `"khoj"` (body) | 242 | Noisy — matches Khoja, Khojpost, Khojaly Khojawiki, etc. |
| `http.title:"Khoj"` | 7 | Strong but small; includes 2 name-collision FPs |
| `http.html:"khoj"` | 24 | Wider than title, still has substring noise |
| `port:42110` | 411 | Khoj's canonical port; also widely used by Hikvision, snmp, Aliyun WAF, and ~33 flyio.net hosts |

After de-dup against IP:PORT pair: **412 unique candidates**.

The right dork for Khoj is `http.title:"Khoj AI"` — the body substring
"khoj" matches too many unrelated South Asian brand names. Port 42110
catches a substantial flyio population that is almost entirely
firewalled-but-still-Shodan-cached; the live Khoj instances we observed
on the internet were all behind reverse proxies on 80/443/3000, never
exposing 42110 directly.

---

## Verifier

Restraint-first design: GET only. No POST chat messages. No
`/api/content/file/*` document reads. No `/api/chat/history` reads.

Probed endpoints, all read-only:

```
GET /                       -> Khoj identity (HTML markers)
GET /api/health             -> liveness + anonymous-mode marker
GET /api/agents             -> count + key list (no persona text)
GET /api/automations        -> count
GET /api/chat/sessions      -> count + first-row keys (no titles)
GET /api/content/types      -> label list (no document bodies)
```

Verdict buckets:
- `unauth_khoj_confirmed` — `/api/health` returns `{"email":"default@example.com"}` AND content listings reachable
- `auth_khoj_confirmed` — `/api/health` returns `{"detail":"OK"}` OR privileged endpoints return 401/403
- `single_user_mode` — health exposes a non-default email but sessions reachable
- `multitenant_public_agents` — `/api/agents` lists public community personas; user data still locked
- `fp_not_khoj` — alive HTTP service, no Khoj API surface
- `dead` — TCP/TLS failure

---

## Results

Of 412 candidates:

| Verdict | Count |
|---|---|
| dead | 350 |
| fp_not_khoj | 55 |
| auth_khoj_confirmed | 6 |
| unauth_khoj_confirmed | **1** |

**7 confirmed Khoj instances. 1 in anonymous mode.**

| Host | Port | ASN | Country | Verdict |
|---|---|---|---|---|
| 192.9.190.118 (obsidian.the-judsons.com) | 443 | Oracle Cloud | US | **unauth_khoj_confirmed** |
| 101.200.195.180 (bitxiong.com) | 443 | Aliyun | CN | auth + multitenant_public_agents (24 agents) |
| 101.200.195.180 (bitxiong.com) | 3000 | Aliyun | CN | auth (alt port) |
| 121.196.236.20 (qmwai.com) | 443 | Aliyun | CN | auth |
| 47.111.150.4 (qmwai.com) | 443 | Aliyun | CN | auth (alt instance) |
| 13.232.31.32 | 80 | AWS Mumbai | IN | auth (re-probe dead) |

Two Shodan-titled "Khoj" hosts (`20.235.79.57` Khoj-by-Axiomaera and
`34.144.216.8` Khoj-Varaha-Science-Pipeline) use Khoj as a product name
but do NOT run khoj-server. No `/api/health`, no `/api/chat/options`,
no `/static/khoj-favicon`. Categorized FP.

---

## The Headline Finding

**192.9.190.118 / obsidian.the-judsons.com** — Khoj instance running on
Oracle Cloud (US), fronted by nginx on 443, in canonical anonymous mode.

Observed metadata (counts + keys only, no bodies):

```
GET /                       -> 200, title "Khoj AI - Ask Anything"
GET /api/health             -> 200, {"email": "default@example.com"}
GET /api/chat/sessions      -> 200, 5 active conversations
                                keys: conversation_id, slug, agent_name,
                                      agent_icon, agent_color,
                                      agent_is_hidden, created, updated
GET /api/content/types      -> 200, ["all"]
GET /api/agents             -> 200, 0 agents (default install)
```

The `default@example.com` email in `/api/health` is the unambiguous
Khoj anonymous-mode marker. Once that endpoint returns the default
user, every other Khoj API call runs as that user. There is no auth
challenge between the public internet and:

- The 5 active chat conversations
- The indexed-content namespace (already populated, type "all")
- The local-filesystem sync configuration
- The Notion / Obsidian / GitHub integration tokens (if configured)
- Any future search / chat / file-read API call

This survey stopped at the verification rung. We confirmed the unauth
surface is reachable. We did not exercise the reads (`/api/chat/history`,
`/api/content/file/*`) — those would dump message bodies and indexed
document contents, and the restraint posture forbids that.

Reverse DNS (`obsidian.the-judsons.com`) suggests this is a personal
Obsidian-vault Khoj instance — a household, not a vendor. The
unauth-mode failure here is a personal-privacy exposure, not a
multi-tenant SaaS breach.

---

## Insight Candidates

**(C1) The default port is not the observed port.** All 7 confirmed Khoj
instances ran behind a reverse proxy on 80/443/3000. None exposed port
42110 directly. The port-42110 dork (411 hits) returned essentially zero
real Khoj — the 33 flyio.net hosts were all firewalled, and the rest
was unrelated infrastructure (Hikvision cameras, Aliyun WAF, net-snmp).
Population-mapping tools that lean on default-port dorks will systematically
miss the Khoj population. **Title and HTML-body anchors on
"Khoj AI - Ask Anything" are the durable Khoj signal.**

**(C2) Conversation slugs leak intent without leaking bodies.** Khoj's
session list exposes a `slug` field per conversation, which is the
auto-generated short title of the first user question. Reading session
counts (the restraint-bound move) leaves slug strings on the table — a
follow-up survey could examine whether slugs themselves are sensitive
without ever touching `/api/chat/history`. This is the same intent-leak
class Insight #66 surfaced on OpenWebUI's chat-list page.

**(C3) Anonymous-mode rate consistent with prior generations.** Of the 5
unique Khoj hosts observed, 1 (20%) was in anonymous mode. Small-N
sample, but matches the same ~10-25% range Open-WebUI shows with
`WEBUI_AUTH=False` and LibreChat shows with `ALLOW_REGISTRATION=true`.
Three generations of personal-AI UIs share the same default-permissive
tradeoff. The fix pattern is also the same: ship the easy-mode
configuration as a debug toggle, require an explicit env-var flip
for production. Khoj is closer to compliant than its predecessors —
the docs say so explicitly — but population-level visibility shows
real users continue to ship the unsafe configuration.

---

## Substrate

| ASN | Org | Hosts |
|---|---|---|
| AS37963 | Aliyun (Alibaba Cloud, CN) | 3 unique (bitxiong x2 ports + qmwai x2 instances) |
| AS31898 | Oracle Cloud (US) | 1 (the anonymous host) |
| AS16509 | AWS Mumbai (IN) | 1 |

The Aliyun cluster is the multi-tenant Chinese deployment pattern
(bitxiong.com / qmwai.com) — these are Khoj instances re-packaged
behind a custom UI as a Chinese-language AI chatbot product. Auth is
enforced on user data even though public agent listings are exposed.
The Oracle US host is the personal-deployment failure mode.

---

## Restraint Ledger

GET-only verifier. Total HTTP calls per host: 6 (root, health, agents,
automations, chat/sessions, content/types). All probes returned counts,
status codes, and JSON key lists — never message text, never document
content, never user emails beyond the canonical
`default@example.com` marker.

Endpoints explicitly NOT probed on any host:
- `/api/chat/history` (message bodies)
- `/api/content/file/<path>` (indexed document content)
- `/api/content/computer/<path>` (local-filesystem sync)
- `/api/agents/<slug>` (persona text)
- `/api/notion/auth` (integration tokens)
- any POST/PUT/DELETE verb

---

## Disclosure Stance

The single anonymous-mode host is a personal Obsidian deployment, not
a vendor's product. Disclosure target: the operator directly via DNS
WHOIS or domain contact, if accessible. The Khoj project itself
correctly documents the production-deployment requirements; the gap
here is operator practice, not vendor default. Khoj's `KHOJ_DEBUG=False`
flow and Google OAuth / Magic Link options are documented and
enforceable — the project ships a hardened default for those who
follow the production docs.

We do not pitch disclosure routes from the survey output. Disclosure
decisions remain Nick's.

---

## Next

- Add Khoj fingerprint to aimap. Anchor: `/api/health` body matches
  `{"email": "default@example.com"}` for unauth bucket, or
  `{"detail":"OK"}` for auth bucket. Both are unique JSON shapes.
- Write Khoj platform JSON to tome corpus (Stage -1 codify step).
- Re-survey at +30d to see whether the 20% anonymous-mode rate
  trends down with disclosure pressure.
- Cross-reference flyio.net 42110 hosts in a future Censys pull —
  Shodan can't reach them but Censys CT-log scanning might.
