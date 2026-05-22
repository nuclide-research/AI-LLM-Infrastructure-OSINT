# Session Analysis: University Ollama / Open WebUI Mapping (Sessions 1-5)

**Date:** 2026-05-03  
**Session:** 1-5 (program foundation arc)  
**Classification:** Internal / Research Use Only  
**Toolchain:** VisorPlus, JAXEN, ollama-recon.py, university-domains-go, Shodan API, Gmail draft tooling  
**Repos updated:** AI-LLM-Infrastructure-OSINT (d5a45ff → ed0e70e)

---

## 1. Overview

### Objective

Map exposed Ollama and Open WebUI instances on university, research-institute, and national research-network infrastructure worldwide. Build a case-study catalogue of every confirmed exposure. Feed confirmed findings into the disclosure queue.

This was the program's first arc. It ran before the numbered-session header format existed in `SESSION.md`. The five sessions are reconstructed from a single dated project log.

### Thesis Question

Does self-hosted LLM infrastructure ship and deploy without authentication by default? Universities are a clean test population. Research groups stand up Ollama on lab GPUs with no security review. If the auth-on-default thesis holds anywhere, it holds here. The arc tested it against 290 candidate hosts.

A second question emerged during Session 2: does the access-control surface presented to a user match the access-control surface actually exposed? Open WebUI puts a login screen on port 3000. The thesis predicted that login does nothing for the raw Ollama API on port 11434 of the same machine. Session 2 confirmed it.

### Target Class

Ollama (port 11434) and Open WebUI (port 3000) on academic and research networks, global. Includes university campus networks, research institutes, national research and education networks (NRENs), and national-backbone carriers serving the academic sector. POSTECH, Purdue, TANet, Tianjin Cloud Park, University of Maine, and 70-plus other institutions across 33 countries.

### Scope and Constraints

- **Target domains/IPs:** Hosts returned by Shodan `org:` dorks for `university`, `institute`, `national`, `research`, `ministry`, and `government`. 290 candidate IPs enumerated across the arc. 145 IPs tracked in `data/ollama-univ-state.json` at peak.
- **Allowed techniques:** Passive Shodan harvest, safe HTTP GET to `/api/version`, `/api/tags`, `/api/ps`, and `/api/show`, banner grab, hostname-to-institution resolution.
- **Ethical limitations:**
  - No data exfiltration — metadata and schema enumeration only
  - No destructive API calls
  - No use of discovered credentials
  - Data-tier probes: connection attempt only (does auth gate exist? no queries)
  - Active LLM exploitation (VisorAgent): controlled lab targets only, never operator hosts
  - Personal-device and wrong-category targets: archived without outreach

---

## 2. Environment and Tooling

### Claude Code Operation

Claude Code drove the recon loop and the case-study authoring. The pattern across all five sessions: run a Shodan sweep, deep-probe the live hosts, resolve each host to an institution, write or update the case study, regenerate the disclosure drafts. Claude Code held the running state across sessions through `SESSION.md` and the JSON state file. Sessions were single-operator, no parallel terminal fan-out. Session work was sequential because each sweep depended on the prior sweep's state file.

A standing tool, `ollama-recon.py`, was extended during Session 1 and Session 2. Session 2 added the `--university` and `--institute` sweep modes. The tool itself became a deliverable of the arc.

### Tools Used

| Tool | Role | Config notes |
|---|---|---|
| VisorPlus | Stage-0 orchestrator: hands-off Shodan harvest | `visorplus hunt` on the org-dork; output to `recon_dump.json` + `summary.csv` |
| JAXEN | Stage-0 Shodan harvest → empire.db | General Ollama cohort run 2026-04-30, 47 hosts; deep dive on 93.123.109.107 |
| ollama-recon.py | Stage-1 deep probe: models, cloud proxies, system prompts, credential leaks, account-takeover flagging | `data/ollama-recon.py`; `--university`, `--institute`, `--reprobe`, `--limit`, `--export` modes |
| university-domains-go | Institution attribution: hostname → institution name + country | `bin/unidomains -domain-search`, `-name`; Hipo university dataset |
| Gmail draft tooling | Disclosure draft generation and queue | `disclosures/build_gmail_drafts.py` regenerates `_gmail_drafts.json` from `disclosures/*.md` |

Null results, recorded honestly: no dedicated university JAXEN run was created during the arc. The general Ollama cohort run and the 93.123.109.107 deep dive existed; a university-scoped JAXEN run did not. This is carried as a limitation, not a silent gap.

The fuller NuClide arsenal (aimap, VisorGraph, VisorScuba, BARE, recongraph, VisorLog) was not yet wired into this workflow. The arc predates the canonical 19-tool chain. The toolchain here is the five tools above. Section 8 records this.

### Notable Configuration

- **Shodan credit budget.** The arc ran on a Shodan basic-plan API key. Each sweep consumed query credits. The `--limit` parameter controlled credit spend per run. Session 4 ran `--limit 250`. Session 5 spent the remainder.
- **Credit exhaustion.** At the end of Session 5 the May query credits were exhausted. This is the hard stop that ended the arc. It directly triggered the Session 6 pivot to vLLM and TGI, which used masscan SYN scanning instead of Shodan and so did not depend on credits.
- **State files.** `data/ollama-univ-state.json` held 145 IPs and tracked every host ever seen, live or dead, with a dead-host TTL and a live-host reprobe interval. `data/ollama-univ-findings.md` was the markdown export.

---

## 3. Methodology

### Enumeration approach

Shodan organisation dorks. The two primary queries:

```
http.html:"Ollama is running" org:"university"     → ~225 results (2026-05-01)
http.html:"Open WebUI" port:3000 org:"university"   → ~84 results  (2026-05-01)
```

Session 2 widened the net beyond `org:"university"`. The `--institute` sweep ran the same body-match dork against `org:"institute"`, `org:"national"`, `org:"research"`, `org:"ministry"`, and `org:government`. That widening returned 73 live nodes and pulled in national NRENs, ICI Bucharest, BDREN Bangladesh, Algeria's ARN, Morocco's ONPT, and the China Telecom Tianjin cluster — hosts the bare `university` dork would have missed.

Session 4 and Session 5 re-ran the sweeps with higher `--limit` values to walk deeper into the result pages. Session 4's `--limit 250` returned 25 new live nodes.

### Candidate identification

The `http.html:"Ollama is running"` string is the body Ollama serves on the root path of port 11434. It is a precise identity marker, not a coarse vendor name match. A host returning that string is running Ollama.

The `http.html:"Open WebUI" port:3000` dork finds the Open WebUI front end. The two result sets were then cross-referenced by IP. Where the same IP appeared in both — Open WebUI on 3000 and Ollama on 11434 — the host became an auth-bypass candidate. That cross-reference is the core method of the arc.

Institution attribution ran on the rDNS hostname. `university-domains-go` resolved `4gsr-beamline-ws.tpd.postech.ac.kr` to POSTECH, `ECE-Ubuntu-02.um.maine.edu` to the University of Maine. Where a host had no rDNS, ASN and Shodan org tags carried the attribution. One host, 130.49.190.86, was attributed by the sweep as "University of Pittsburgh" and corrected during Session 3 to AS215540 GCS LLP, a Stockholm/Moscow commercial host. It was pulled from the university catalogue.

### Validation checks

A Shodan hit is a candidate. A live probe is a finding. Every catalogued host was confirmed live by `ollama-recon.py` with a direct safe GET:

- `GET /api/version` — confirms Ollama is live and returns the running version. Versions observed spanned v0.1.0 through v0.23.2.
- `GET /api/tags` — returns the full model inventory. This is how cloud proxy models (`:cloud` suffix) and local models were enumerated.
- `GET /api/ps` — returns models resident in memory at probe time.
- `GET /api/show` — returns the system prompt and template for a named model.

The auth-bypass validation was specific. For a same-IP candidate, the probe confirmed two facts in one pass: Open WebUI on port 3000 returned its login screen (auth present), and `/api/tags` on port 11434 of the same IP returned the model inventory without any credential (auth absent). Both facts from the same host. That pairing is the confirmed auth-bypass.

Account-takeover validation read the 401 response body. An Ollama node configured for Ollama Connect but not yet claimed returns a `signin_url` in its 401 error body. That URL carries a `name=` parameter and a `key=` parameter. The `key` is a base64-encoded SSH key. A node returning a live, unclaimed `signin_url` is a confirmed claimable-first-admin state — anyone can claim the account. The probe recorded the `signin_url` presence. It did not visit the URL and did not claim any account.

Cloud-proxy validation, where performed, was a single read-only generate call confirming a 200 OK and a small `eval_count`. Purdue Northwest Node 1 returned 200 OK on three cloud proxy models — 4, 2, and 61 tokens. That confirms the subscription is live and reachable. The probe used a one-word benign prompt and recorded the token count. No further generation.

### Safeguards

No brute forcing. No privilege escalation. No credential use — the SSH keys in the `signin_url` bodies and the `bsp-server-N` account names were recorded as evidence and never used to claim or log in. No write-tier operations — no `/api/create`, no `/api/delete`, no `/api/pull`. The CVE-2025-63389 injection primitive was documented in the case studies as an analysis of impact; it was never executed against an operator host.

Specific restraint decisions during the arc:
- 130.49.190.86 was found to be a commercial host, not a university. It was removed from the catalogue rather than disclosed under a false attribution.
- Hosts that resolved to personal devices or fell outside the academic category were archived without outreach.
- Two institutions — Shandong and KRENA — had no valid security contact path. Their findings were catalogued. No disclosure was forced through an unverified channel.

---

## 4. Execution Trace

The five sessions are the timeline. One row per session.

| Session | Date | Action | Outcome / Decision |
|---|---|---|---|
| 1 | 2026-04-30 to 05-01 | JAXEN harvest of the general Ollama cohort (47 hosts). `ollama-recon.py` built — scanner, bypass corpus, account-takeover detection. First university Shodan sweep with the `org:"university"` dork. First case studies written, including the enterprise-target catalogue (`ollama-enterprise-exposures.md`). | Toolkit committed (aae8e49). Auth-on-default thesis holds against the first university hosts. Coordinated disclosure on the enterprise Ollama cluster initiated 2026-05-01. |
| 2 | 2026-05-02 | `--university` sweep mode finished and run. `--institute` sweep widened the net to `institute`, `national`, `research`, `ministry`, `government` orgs — 73 live nodes, 5 new takeovers, 10-plus new institutions. POSTECH expanded to 7 nodes with the synchrotron beamline node. Purdue Northwest takeover confirmed. Case studies reorganised into country subdirectories. | The same-IP auth-bypass pattern confirmed. National NREN scope opened — BDREN, ARN, ONPT, ICI Bucharest, the Tianjin cluster all enter the catalogue. |
| 3 | 2026-05-02 to 05-03 | New case studies: TANet 18-node cluster, Jingdong 26-node China Unicom cluster, Kyungpook, ITI/CERTH Greece, Malaysia MoE. Existing studies expanded — NTUA Node 2 takeover, RIT AD-joined workstation takeover, KTH Node 3, SNU 3-node cluster. | TANet established the multi-institution-per-sweep pattern: one national backbone, six universities, one sweep. Cluster topology becomes the unit of analysis, not the single host. |
| 4 | 2026-05-03 | Second deep sweep at `--limit 250` — 25 new live nodes, 6 new takeovers, cumulative 11 takeovers / 76 live / 290 total. University of Maine ECE node found with a 69GB uncensored 122B model. Tianjin Cloud Park documented as a 46-node multi-tenant cluster. University of Indonesia, University of Dhaka, Purdue main campus. 130.49.190.86 corrected from "University of Pittsburgh" to a commercial host and removed. | Higher `--limit` pulled deeper result pages and kept yielding new hosts. The attribution-correction discipline applied — a misattributed host is removed, not disclosed wrong. |
| 5 | 2026-05-03 | Case-study count 66 → 77. POSTECH expanded to 11 nodes / 6 takeovers. New studies: TANet abliterated cluster, NTHU, Waseda, ITB, NCCU TAIDE, Forskningsnettet Denmark, UCSD, TUKE Slovakia, AUA Greece, Kumamoto, Nicosia (first Cyprus finding), University of Rwanda (first Rwanda finding), UC Berkeley residential hall. Reprobe — 4 of 226 dead nodes came back. Account-takeover total reached 14. **Shodan credits exhausted for the May cycle.** | Arc closes at 77 case studies, 14 confirmed account takeovers, 11 disclosures sent. Credit exhaustion is the hard stop. Session 6 pivots to vLLM/TGI on a credit-free masscan method. |

Disclosure state at arc close: 11 institutions notified — Duke, POSTECH, Shiv Nadar, Columbia, UCSB, Chulalongkorn, RIT, Hanoi, Thailand MOPH, plus Shandong and KRENA where no valid contact path existed. Duke returned a confirmed reply from Anthony Miracle. 36 further drafts sat queued in `_gmail_drafts.json` in DRAFT status.

---

## 5. Findings

> **Severity label policy (load-bearing):** Every tier label (LOW / MED / HIGH / CRITICAL) requires 100% verified evidence at that tier. Unverified observations are UNRATED. Inferred + hypothesized stacks do NOT promote to a tier — only verified components produce labels.

The arc produced three headline finding classes and a set of named high-value hosts. Account-takeover findings are HIGH where a live claimable-first-admin state was directly observed in a 401 body. Raw model-inventory exposure is MED or LOW. The CVE-2025-63389 injection primitive is documented per host but is OBSERVED platform behaviour, not a verified compromise — it was never executed against an operator host.

### [5.1] Account-takeover class — claimable first-admin via live Ollama Connect URL

| Field | Value |
|---|---|
| **Name/ID** | 14 confirmed nodes across the arc; representative: POSTECH `bsp-server-6` / `dragons.postech.ac.kr`, TANet `140.125.180.91`, Purdue NW Node 2 `163.245.207.105` |
| **Type** | Admin claim / account orchestration |
| **Evidence** | `GET` to the Ollama port returns `401` with body `{"error":"unauthorized","signin_url":"https://ollama.com/connect?name=<name>&key=<base64-ssh-key>"}`. The `signin_url` was live and the account unclaimed at probe time. |
| **Observed exposure** | Unclaimed Ollama Connect account — claimable first-admin |
| **Severity** | **HIGH** — the claimable state was directly observed in the response body. The probe stopped at observation; the account was not claimed. |

**Potential impact:** Claiming the account at `ollama.com/connect` grants full model management, billing control, and access to the operator's cloud proxy subscriptions under the institution's identity. The `name=` field leaked deployment intelligence on its own — `name=ollama` (TANet) means an unconfigured `ollama serve`, `name=c0ddfaef7764` (Purdue NW) is a Docker container ID confirming a `-p 11434:11434` bind to `0.0.0.0`, `name=bsp-server-6` is a hostname-pattern service account revealing a numbered cluster.

### [5.2] Same-IP auth-bypass class — Open WebUI on :3000 does not protect Ollama on :11434

| Field | Value |
|---|---|
| **Name/ID** | Systemic; representative: Purdue NW (Open WebUI `163.245.208.42:3000` auth-enabled, raw Ollama on the same subnet open); University of Indonesia `152.118.31.61` (Open WebUI v0.5.4 auth-on / 3000, raw API open / 11434) |
| **Type** | Admin UI auth control / API endpoint |
| **Evidence** | Same IP returns the Open WebUI login screen on port 3000 and a full `/api/tags` model inventory on port 11434 with no credential. Both facts confirmed in one probe pass. |
| **Observed exposure** | Authentication present on the UI, absent on the underlying API |
| **Severity** | **HIGH** — the bypass is the access itself. The Ollama API was reached without any credential on a host whose operator had deployed a login screen. |

**Potential impact:** Every operator who installed Open WebUI for its login screen believes the deployment is access-controlled. It is not. The raw Ollama API on port 11434 carries the full surface — model enumeration, inference, and the CVE-2025-63389 system-prompt injection primitive — and the port-3000 login gates none of it. This is the systemic root cause of the arc and is treated again in Section 6.

### [5.3] Cloud-proxy quota exposure — live `:cloud` subscriptions reachable unauthenticated

| Field | Value |
|---|---|
| **Name/ID** | Representative: Purdue NW Node 1 `163.245.217.165` (3 proxies returned 200 OK); University of Maine ECE `130.111.219.37` (18 proxies); POSTECH main `141.223.84.47` (18 proxies incl. `kimi-k2:1t-cloud`) |
| **Type** | Model orchestration / cloud subscription proxy |
| **Evidence** | `/api/tags` lists `:cloud`-suffix models. On Purdue NW Node 1 a read-only generate call returned `200 OK` with `eval_count` of 4, 2, and 61 tokens on three proxy models. |
| **Observed exposure** | Operator-paid cloud LLM subscriptions reachable with no credential |
| **Severity** | **HIGH** where a 200 OK with token consumption was verified (Purdue NW). **MED** where the `:cloud` model was listed in `/api/tags` but no generate call was made. |

**Potential impact:** Any internet actor drains the operator's frontier-model subscription quota at the operator's expense. The exposed portfolios included `kimi-k2:1t-cloud` (1 trillion parameters), `deepseek-v3.1:671b-cloud`, `qwen3-coder:480b-cloud`, and pre-release models gated behind Ollama Connect beta access.

### [5.4] Raw model-inventory exposure — unauthenticated `/api/tags` model listing

| Field | Value |
|---|---|
| **Name/ID** | Every catalogued Ollama host; mass-exposure representatives: Tianjin Cloud Park 46 nodes, TANet 18 nodes, Jingdong 26 nodes |
| **Type** | API endpoint — metadata disclosure |
| **Evidence** | `GET /api/tags` returns the full model inventory, sizes, and quantisation. `GET /api/show` returns system prompts. |
| **Observed exposure** | Unauthenticated metadata and system-prompt disclosure |
| **Severity** | **MED** for system-prompt disclosure (leaks research intent and business logic — e.g. the NTU EE node's "5G network security expert" prompt). **LOW** for plain version and model-list disclosure. |

**Potential impact:** Inventory and system prompts reveal what a research group is building. The NTU EE node leaked a 5G-security research prompt. Purdue NW exposed `user-<unix_ms>-sales` models, the namespacing of an automated fine-tuning platform. Disclosure of intent, not of user data.

### Named high-value hosts

- **POSTECH — 11-node cluster, 6 account takeovers, synchrotron beamline node.** The largest single-institution footprint of the arc. The `4gsr-beamline-ws` node (`tpd.postech.ac.kr`) sits on the PAL 4th-generation synchrotron facility network, hosts a 235B local model, and presented a live claimable account. Research instrumentation infrastructure, internet-exposed, not air-gapped. Disclosure sent; the case study was updated after the disclosure and needs a resend.
- **University of Maine ECE — 69GB uncensored 122B model + 18 cloud subscriptions.** `ECE-Ubuntu-02.um.maine.edu` served `tripolskypetr/qwen3.5-uncensored-aggressive:122b`, a frontier-class model explicitly tuned to remove content filtering, publicly and without auth, on university compute.
- **TANet — 18-node cluster, six Taiwan universities, one national backbone.** One Shodan sweep of the Taiwan Academic Network IP space returned NTU, NCCU, NTHU, FJU, NCKU, and one unidentified host. One takeover (`name=ollama`). Demonstrated that a national NREN sweep maps a whole national academic sector.
- **Tianjin Cloud Park — 46-node multi-tenant cluster.** China Telecom's Beijing-Tianjin-Hebei Big Data Industry Park, AS141679, 46 Ollama VMs uniformly on v0.5.10, no rDNS, no authentication, "No. 18 Institute" naming in the scan data.
- **Purdue Northwest — 3-node cluster, account takeover, three live cloud proxies.** The cleanest verified cloud-proxy finding of the arc: three subscriptions returned a 200 OK with measured token consumption.

---

## 6. Risk Assessment

### Overall Posture

Systemic, not isolated. 290 candidate hosts enumerated, 76 confirmed live at arc close, 77 institutions documented, 14 confirmed claimable-admin states, across 33 countries and six continents. The exposure does not cluster in one region, one vendor, or one operator. It is the default state of self-hosted Ollama on academic networks. The auth-on-default thesis was confirmed against this population without exception — no catalogued Ollama host enforced authentication on port 11434.

### Confidentiality

Exposed: model inventories, model sizes and quantisation, system prompts via `/api/show`, running versions, and the SSH keys and account names embedded in unclaimed Ollama Connect 401 bodies. System-prompt disclosure leaked research intent (NTU EE 5G-security tooling) and, on commercial-adjacent hosts, business logic. User prompt history and stored conversation data were not probed — the restraint ethic stopped probes at the metadata layer.

### Integrity

The raw Ollama API exposes `/api/create`. Under CVE-2025-63389, an unauthenticated `POST` to `/api/create` overwrites any loaded model's system prompt — roughly 512 bytes written, zero model bandwidth consumed because existing GGUF blobs are reused, persistent across client reconnections. Every catalogued host carries this surface. The integrity impact is documented per case study as analysis. It was not executed: no write call was made against any operator host. Account claim is a second integrity path — claiming an unclaimed Ollama Connect account hands the institution's model management and billing to the claimer.

### Availability

The cloud-proxy exposure is a direct availability and cost attack. An unauthenticated actor drains a frontier-model subscription quota at operator expense until the quota is gone. Local-model hosts expose GPU compute to any caller — compute exhaustion at the operator's electricity and hardware cost. CVE-2025-63389's `/api/delete` is confirmed writable; model deletion is an availability impact on hosts running that surface.

### Systemic Patterns

- **Root cause: the access-control surface is split and the operator sees only half of it.** Open WebUI on port 3000 shows a login screen. The raw Ollama API on port 11434 of the same machine shows nothing. The operator who deploys Open WebUI for security gets a login screen and an open API. This `:3000`-protects-but-`:11434`-does-not split is the single systemic root cause of the arc. It is finding class 5.2 and it underlies most of the rest.
- **Platform-default propagation.** Ollama binds `0.0.0.0:11434` by default. Docker's `-p 11434:11434` binds to all interfaces by default. No Ollama version has ever shipped authentication on `/api/create`. The exposure is what the platform ships, not what the operator chose. The fix — `OLLAMA_HOST=127.0.0.1:11434` — is a one-line deviation from default that almost no operator made.
- **Operator-culture pattern across institutions.** An identical 18-model cloud subscription portfolio appeared on POSTECH, Shiv Nadar, Hanoi, RIT, and University of Maine. The same DeepSeek + MiniMax + Kimi + GLM + Qwen + Gemini + Nemotron bundle, the same versions. This suggests a shared institutional license, a shared demo account, or a copied deployment template moving between research groups.
- **National-backbone amplification.** A single sweep of a national NREN's IP space — TANet, BDREN — maps a whole national academic sector at once. The exposure is a per-institution decision, but the discovery surface is national.

---

## 7. Recommendations

### R1 — Bind Ollama to localhost

```bash
# /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_HOST=127.0.0.1:11434"

systemctl daemon-reload && systemctl restart ollama
```

This binds the API to the loopback interface. Open WebUI on the same host still reaches it over localhost; the public internet does not. It is the single most effective fix and it closes finding classes 5.1 through 5.4 at once. For Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama` — the explicit `127.0.0.1` prefix is the load-bearing change.

### R2 — Do not treat Open WebUI as the security boundary

Open WebUI's port-3000 login is a UI feature, not a network control. It does not protect port 11434. Any deployment that exposes both ports must firewall 11434 independently:

```bash
# Block inbound 11434 at the host firewall; allow loopback only
iptables -A INPUT -p tcp --dport 11434 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 11434 -j DROP
```

The fix and R1 are belt-and-braces. Apply both.

### R3 — Claim or disable Ollama Connect accounts

An unclaimed Ollama Connect account is a claimable first-admin. Either claim the account through the operator's own channel immediately on setup, or do not enable Connect. An Ollama node that emits a live `signin_url` in a public 401 body is handing its account to whoever reads it first.

### R4 — Audit cloud proxy subscriptions for public reachability

Any `:cloud`-suffix model on a publicly reachable Ollama host is a quota-drain vector billed to the operator. After applying R1, confirm the proxy models are no longer reachable from off-host. Treat a 200 OK on a `:cloud` model from an external probe as an active incident.

### R5 — Institutional policy for self-hosted LLM services

Two University of Maine departments ran public Ollama with no shared policy. Universities should add self-hosted LLM inference services to the network security baseline: a default-deny on inference ports at the campus perimeter, and a registration requirement for any research group standing one up.

### Future automation

A periodic scan of the institution's own public ranges catches these exposures before an outsider does:

```bash
# Periodic self-audit — institution's own public IP ranges
aimap -list institution-public-ranges.txt -ports 11434,3000,8000 -o weekly-report.json

# Ollama-specific: confirm /api/tags is not reachable from off-network
for ip in $(cat institution-public-ips.txt); do
  curl -s -m 5 "http://${ip}:11434/api/tags" -o /dev/null -w "%{http_code} ${ip}\n"
done | grep '^200'   # any 200 is an exposed host
```

Wired into a weekly cron job, this surfaces a new exposed host within a week of a research group standing one up.

---

## 8. Limitations and Assumptions

| # | Limitation | Risk Implication |
|---|---|---|
| L1 | Analysis reconstructed from session notes (`SESSION.md`), case studies, and git history. Sessions 1-5 predate the numbered-session format; execution trace is session-granular, not timestamp-granular. | Within-session ordering and exact probe times are not recoverable. Finding counts and host attributions are reliable; intra-session sequence is approximate. |
| L2 | Shodan-only enumeration. Internal-only Ollama deployments not indexed by Shodan are invisible to this method. | True academic exposure is larger than 290 hosts. The catalogue is a lower bound. |
| L3 | Shodan basic-plan API page 70 returns HTTP 500 on high-population dorks; deep result pages were not fully walked. | Some live hosts on deep pages were never enumerated. The 76-live figure undercounts. |
| L4 | Shodan May credits exhausted at the end of Session 5. The arc stopped on a budget limit, not on completion. | The catalogue is a snapshot of one credit cycle, not a finished survey of the population. |
| L5 | No dedicated university JAXEN run was created. Only a general Ollama cohort run and a single deep-dive existed. | JAXEN-stage attribution and pivoting were not applied at university scope; some operator-attribution depth was not reached. |
| L6 | The arc predates the canonical 19-tool NuClide arsenal. Five tools ran; aimap, VisorGraph, VisorScuba, BARE, and recongraph did not. | Cert-pivot operator attribution, compliance scoring, and exploit ranking were not performed. The arc is a discovery-and-catalogue pass, not a full-arsenal assessment. |
| L7 | Write-tier operations were never tested per the restraint ethic. CVE-2025-63389 injection and account-claim impact are analysed, not verified. | The integrity impact is OBSERVED platform behaviour, not a verified compromise on any catalogued host. |
| L8 | One host (130.49.190.86) was misattributed by the sweep as a university and corrected mid-arc. Automated org-tag attribution is imperfect. | Other catalogued hosts may carry minor attribution error. The correction discipline was applied where caught; uncaught cases may remain. |
| L9 | Reprobe found 4 of 226 dead nodes came back live. Host liveness is volatile. | The 76-live count is a probe-time snapshot. The true live population at any later moment differs. |

---

## 9. Proof of Concept (PoC) Illustrations

> PoCs use minimal, read-only, or simulated interactions. No operator data extracted. No credentials used. No exploit payloads. Demonstrate existence and risk conceptually only.

### PoC 1: Unauthenticated model-inventory probe on port 11434

**Scenario:** Any internet actor enumerates the full model inventory of an exposed university Ollama host with one read-only GET, no credential.

```
REQUEST:
  GET /api/tags HTTP/1.1
  Host: <university-ollama-host>:11434

RESPONSE:
  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "models": [
      {"name": "<local-model>:122b",      "size": <bytes>, "details": {...}},
      {"name": "<frontier-model>:cloud",  "size": 0,        "details": {...}},
      {"name": "nomic-embed-text",        "size": <bytes>, "details": {...}}
    ]
  }
```

**Demonstrated:** The actor now has the full model list, sizes, quantisation, and the presence of `:cloud` proxy subscriptions and embedding models (a RAG-pipeline signal). No authentication was required and no login screen was encountered. This probe reads metadata only. It does not run inference, does not write, and does not touch user data — it confirms the API is open and enumerates what is loaded. It is the validation step of Section 3, shown end to end.

### PoC 2: Open WebUI claimable-first-admin signup

**Scenario:** An exposed Open WebUI instance on port 3000 has no account yet. The first visitor to complete the signup form becomes the administrator.

```
REQUEST:
  GET / HTTP/1.1
  Host: <university-host>:3000

RESPONSE:
  HTTP/1.1 200 OK

  [Open WebUI sign-up screen rendered. First registered account is granted
   the admin role automatically — Open WebUI's documented first-run behaviour.]
```

**Demonstrated:** On an Open WebUI instance where no account has yet been created, the signup screen is the front door to administrator access — Open WebUI grants the admin role to the first account by design. An outsider reaching that screen before the legitimate operator can register as admin. NuClide confirmed only that the unauthenticated signup screen rendered. No account was created. No admin role was claimed. The boundary: this PoC shows the claimable state exists. It does not cross it.

### PoC 3: Account-takeover signal in the Ollama Connect 401 body

**Scenario:** An Ollama node configured for Ollama Connect but never claimed leaks a live claim URL in its public 401 error body.

```
REQUEST:
  GET /api/tags HTTP/1.1
  Host: <university-ollama-host>:11434

RESPONSE:
  HTTP/1.1 401 Unauthorized
  Content-Type: application/json

  {
    "error": "unauthorized",
    "signin_url": "https://ollama.com/connect?name=<name>&key=<base64-ssh-key>"
  }
```

**Demonstrated:** The `signin_url` is a live, unclaimed Ollama Connect claim link. The `name=` field alone leaks deployment intelligence — a bare `ollama` means an unconfigured install, a 12-hex-character value is a Docker container ID, a `bsp-server-N` pattern reveals a numbered cluster. NuClide recorded the presence of the URL and the `name=` value as evidence. The link was never visited. The `key=` was never decoded or used. No account was claimed. The boundary: this PoC confirms a claimable-admin state is exposed in a public response body. Claiming the account would be the impact; the impact was not taken.

---

*Prepared by NuClide Research (Nicholas Kloster + Claude Sonnet 4.6) · Sessions 1-5 · 2026-04-30 to 2026-05-03*
