# 9. AI Code Assistants

_v2 catalog rebuilt + population-verified: 2026-05-14_

Self-hosted code assistants index proprietary source code to produce completions, or run autonomous agents against a repo. Exposure of the assistant backend leaks the indexed codebase, the agent's workspace, or provider credentials wired into the tool config.

**Verification methodology:** every query below was run on the Shodan Freelance tier and the hit banners sampled. `http.html:"<word>"` matches are noise-prone when the word is common (person names, marketing copy) — those were dropped. `http.title:` and exact-product-string matches that survived banner inspection are marked **verified**. Counts are 2026-05-14 snapshots.

---

## Verified — real populations

| Shodan Query | Count | Ports | Notes |
|---|---|---|---|
| `http.title:"OpenHands"` | 215 | 3000 (dom.), 3001, 443 | All Hands AI autonomous coding-agent backend (ex-OpenDevin). `uvicorn` server. Autonomous agent + Docker workspace → sandbox-escape tier |
| `http.html:"openhands"` | 241 | 3000, 3001 | Broader body match, confirms title set |
| `http.html:"OpenDevin"` | 5 | 80, 3000, 8080 | Legacy OpenDevin installs still live; `uvicorn`; same product family as OpenHands |
| `http.title:"OpenDevin"` | 3 | — | Title-only subset of the above |
| `ssl.cert.subject.cn:"tabnine"` | 31 | 443 | Tabnine self-hosted — TLS cert CN reads **"Tabnine Context Engine"** (literal product name). Indexes private repos for completion |
| `http.title:"Sourcegraph"` | 31 | 80, 81, 443 | Self-hosted Sourcegraph — banner "Sign in - Sourcegraph", `Caddy` server. Code-search + Cody backend. **Use this, not `http.html:"Sourcegraph"` (288 = mostly marketing pages)** |
| `http.html:"sourcebot"` | 25 | 8080, 3000, 443 | Sourcebot self-hosted code-search — `Caddy`. "sourcebot" is not a common word, body match is clean |
| `http.title:"Sourcebot"` | 25 | — | Title-only, same population |
| `http.html:"sweepai"` | 22 | 80, 443 | Sweep AI — banner "Sweep AI", `uvicorn`. Autonomous PR/issue-fixing agent |
| `("bolt.diy" OR "bolt.new")` | 24 | 443, 3001, 8081, 9000 | bolt.diy self-hosted app-builder agent — blank banners on odd ports = self-host pattern (not StackBlitz marketing). ⚠️ confirm at probe time |
| `http.title:"CodeGeeX"` | 2 | 80, 443 | THUDM CodeGeeX self-hosted — small but banner-verified |
| `http.title:"Refact"` | 2 | 443 | Refact.ai self-hosted — banner "Refact Server Login". `"Refact" port:8081` returns 12 (blank banners, probe-verify) |

---

## Probe-time verification required

These returned a plausible population but blank/ambiguous banners — can't confirm from Shodan facets alone, need an aimap body probe to separate real from noise:

| Shodan Query | Count | Why uncertain |
|---|---|---|
| `"Refact" port:8081` | 12 | Blank title + server; 8081 is Refact's documented port but also generic |
| `"gpt-engineer" "/api"` | 7 | Blank banners on 8081/8083/3001; could be gpt-engineer server mode or unrelated |
| `("bolt.diy" OR "bolt.new")` | 24 | (also listed above) odd-port blank banners need API-shape confirmation |

---

## Dead / Shodan-dark — documented, not surveyable

| Product | Status | Evidence |
|---|---|---|
| **TabbyML** | **Shodan-dark** | `"TabbyML"`, `http.html:"tabbyml"`, `"tabby-webserver"`, `"Server: Tabby"`, `"/v1beta/health"` all → 0 or false-positive. `http.title:"Tabby"` (108) is **Tabby Terminal** ("a terminal for a more modern age", Electron app — unrelated). TabbyML's web UI returns JSON-only roots Shodan can't crawl. **Needs masscan-seeded discovery on port 8080**, like the embeddings survey |
| **FauxPilot** | **Extinct** | `"fauxpilot"`, `"copilot_proxy"`, `"v1/engines/codegen"`, `"codegen-16B"`/`-6B`/`-2B` (the models it served) all → 0. Abandonware, no live population |
| **Continue.dev** | **No server footprint** | Continue is a VS Code/JetBrains extension; its server/hub mode has no distinct Shodan signature. `port:65432` (its old default) = 80,710 unrelated hits. `http.html:"Continue" "autocomplete"` (4) = noise (camping-gear shop) |

---

## Noise signatures — DROPPED (do not use)

Recorded so a future contributor doesn't re-run them. All returned high counts that banner-inspection proved were name collisions:

| Dropped Query | Count | What it actually matched |
|---|---|---|
| `http.title:"Tabby"` | 108 | Tabby **Terminal** (SSH/serial app), not TabbyML |
| `http.html:"cody"` | 673 | People named Cody, "On Dreams of Dixie" documentary |
| `http.title:"cody"` | 151 | "Cody Ingram", "Rimrock Tire \| Cody, WY" |
| `http.html:"aider"` | 4,391 | French auth portals ("aider votre entreprise") |
| `http.title:"Aider"` | 37 | French marketing copy, "AIDER 회원관리" |
| `http.html:"roo-code"` | 261 | Random low-banner boxes |
| `http.html:"bloop"` | 70 | "BLAP BLAP", "16 CH" |
| `http.title:"Devon"` | 256 | Cornwall/Devon UK businesses |
| `"codel"` | 398 | ARGUS devices |
| `"ChatDev"` | 48 | Chatwoot, Dynatrace error pages |
| `http.title:"twinny"` | 10 | "Twinny Development" (Polish property developer) |
| `"collama"` | 9 | SNMP (port 161) |
| `"privy" "code"` | 14 | "PetPocketbook Backups" |
| `"melty"` | 10 | SSH/FTP boxes |
| `"Pythagora"` | 67 | Random ports 53/465/9100 |
| `http.html:"devika"` | 21 | "TileDB Resources", "My Website" |
| `http.html:"zoekt"` | 484 | Dutch hosting landing pages |
| `http.title:"Hound"` | 102 | "Outward Hound" dog toys, "Basset Hound" kennels |
| `http.html:"cofounder"` | 109 | LinkedIn-style "Cofounder & CEO" bio pages |

**Lesson:** `http.html:"<common-word>"` is a false-positive trap. Code-assistant names that are also English words / common nouns / person names (Cody, Aider, Hound, Devon, Melty, Bloop) can only be matched via `http.title:` *and* banner verification, or by a unique conjoined token (`sourcebot`, `sweepai`, `openhands` survive because they're not words).

---

## Tooling gap — BLOCKS the assessment chain

**aimap v1.9.2 has ZERO code-assistant fingerprints.** Confirmed by source grep of `~/ai-recon/aimap/fingerprints.go` + `enumerators.go` — no Tabby, OpenHands, Sourcegraph, Refact, Tabnine, Sourcebot, or Sweep matchers exist.

Steps 1–8 of the assessment chain cannot run on this category until fingerprints + deep enumerators are built. Required before harvest → chain:
- Conjunctive-matcher fingerprints (status_code + json_field + body_contains, per the Insight #6 FP-correction convention) for: **OpenHands** (`/api/options/models`), **Sourcegraph** (`/.api/graphql`), **Refact** (`/v1/caps`), **Tabnine** (Context Engine API), **Sourcebot**, **Sweep AI**, **bolt.diy**.
- Deep enumerators for the high-risk surfaces: OpenHands workspace/conversation API (autonomous-agent control, sandbox state), Sourcegraph indexed-repo enumeration (private source-code exfil), Refact/Tabnine indexed-codebase + provider-key exposure.
- TabbyML fingerprint exists as a need but TabbyML is Shodan-dark — pair the fingerprint with a masscan-seeded port-8080 discovery pass.

---

## Phase 2 — provider-first discovery (planned, not yet run)

Name-first querying (this file) has a hard ceiling: it only finds products with a googleable signature. The genuinely obscure long-tail — self-rolled completion servers, internal forks, unnamed agent backends — won't have a name string but **will** sit on a port, on a tier-2 cloud provider, with a detectable API shape.

Planned: masscan the tier-2 cloud ranges (DigitalOcean / Hetzner / Vultr / Scaleway / OVH / Linode) on the code-assistant port set — **8080, 8081, 3000, 3001, 7080, 5000, 8000, 65433** — then fingerprint by API shape via aimap `-scan-all-fingerprints`. Same methodology that surfaced the AS63949 honeypot fleet. This phase depends on the aimap fingerprints above existing first.
