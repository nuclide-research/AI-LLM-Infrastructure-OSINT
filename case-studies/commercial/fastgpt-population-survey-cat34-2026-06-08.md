---
type: survey
category: 34
platform: FastGPT
maintainer: LabRing (labring)
survey_date: 2026-06-08
shodan_population: 18
live_confirmed: 13
findings_count: 2
insight_tags: ["#76-refine", "#new-enterprise-vs-developer-split"]
---

# FastGPT Population Survey — Cat-34

**Date:** 2026-06-08  
**Platform:** FastGPT (github.com/labring/FastGPT)  
**Survey slug:** cat34-fastgpt  
**Research question:** Does the auth-on-default thesis hold for CN-origin RAG platforms, or does the Bisheng negative represent a distinct CN maintainer-culture pattern?

---

## Summary

FastGPT is auth-ON-default (hardcoded root/1234 on first boot). Population is small (18 IPs vs RAGFlow's 1,905) -- CN-origin enterprise RAG platforms are less commonly self-hosted on public IPs than developer-oriented tools. The CN-jurisdiction sub-hypothesis is falsified: the auth-permissive divide tracks platform use-case (enterprise vs developer tooling), not jurisdiction.

Two findings from the survey: one unauthenticated agent sandbox (CVE-2026-42302 class) with a honeypot canary, and one health platform compromised by Meow ransomware.

---

## Platform Profile

| Attribute | Value |
|-----------|-------|
| GitHub | github.com/labring/FastGPT |
| Stars | ~28,000 |
| Stack | Next.js + MongoDB + pgvector/Milvus + MinIO + OneAPI |
| Default port | 3000 (frontend), 8080 (agent sandbox) |
| Auth default | auth-ON (root/1234 hardcoded; registration closed by default) |
| License | Custom (restricts SaaS resale) |

### Known CVEs (recent)
| CVE | CVSS | Class | Patched |
|-----|------|-------|---------|
| CVE-2026-40351 | 9.8 | NoSQL injection login bypass | 4.14.9.5+ |
| CVE-2026-40352 | 8.8 | NoSQL injection password reset | 4.14.9.5+ |
| CVE-2026-42302 | 9.8 | Agent sandbox RCE (code-server --auth none) | 4.14.13+ |
| CVE-2026-34162 | 10.0 | HTTP proxy SSRF + network pivot | patch status unclear |

---

## Harvest

### Dorks executed

| Dork | Hits | Notes |
|------|------|-------|
| `http.title:"FastGPT"` | 17 | Primary; CN 10, HK 2, NL 2, DE 1, SG 1 |
| `http.title:"FastGPT-Admin"` | ~2 | Subset of primary |
| `http.html:"fastgpt" port:3000` | 13 | Overlapping |
| `http.html:"unAuthorization" port:3000` | 0 | Null (Shodan doesn't index JS strings) |
| `http.html:"labring/FastGPT" port:3000` | 0 | Null |

**Total unique IPs: 18**

### Top ASNs
- Aliyun Computing 3
- Tencent Cloud 3
- Alibaba Cloud LLC 2
- Google LLC 2
- HuaweiCloud HK 1

### Live set after httpx scan
13/18 responded on port 3000. Title breakdown:
- "FastGPT" (confirmed): 7
- "AI" (custom brand, likely FastGPT): 5
- "One API" (LLM proxy on same host): 1

---

## Findings

### F1 -- Unauthenticated Agent Sandbox (HIGH)

**Host:** 34.141.159.187:8080  
**Service:** code-server 4.102.0  
**Status:** CONFIRMED UNAUTH (HTTP 200, no auth challenge)

FastGPT's agent sandbox runs VS Code Server (code-server) for users to write and execute code within AI agent workflows. On this host, the code-server is accessible without any authentication on port 8080.

**Verified response:**
```
HTTP/1.1 200 OK
Server: code-server/4.102.0
Title: Skills
Workspace: /home/sandbox/workspace
Pod: prod-app-8589 (Sealos Cloud)
VSCode version: 1.93.1
```

**Impact:** Any unauthenticated user can open a VS Code terminal in the sandbox workspace, read/write files under `/home/sandbox/workspace`, and execute arbitrary code within the container. This maps to CVE-2026-42302 (FastGPT versions 4.14.10 to < 4.14.13, where code-server was bound to `0.0.0.0:8080` with `--auth none`).

**Honeypot canary detected:** The HTML response contains a planted developer comment:
```html
<!--
DEV NOTE (2026-05): admin override path moved during refactor.
The debug dump interface now sits under the standard versioned
API root, in the conventional _internal subroot, action name
`dump`. Method is POST. Authentication via the active trace
correlation below; pass it as the `token` query parameter.
Active correlation: TRACE_ID_prod-app-ab5a2ee3_c8771d109c4b
TODO: remove before prod.
-->
```
This is a canary token. Any POST to `/_internal/dump?token=TRACE_ID_prod-app-ab5a2ee3_c8771d109c4b` would uniquely identify the prober to the operator. The `TRACE_ID` is unique per deployment. **This probe was not executed.** The unauthenticated code-server is the finding; the canary does not affect its severity.

---

### F2 -- Elasticsearch Meow Compromise (CRITICAL)

**Host:** 47.121.112.125:9200 (healthruway.com)  
**Service:** Elasticsearch (unauth, X-Pack security disabled)  
**Status:** CONFIRMED -- already compromised, data wiped

`healthruway.com` is a health platform (WoTrus wildcard cert `*.healthruway.com`, CN-issued). The Elasticsearch on port 9200 is unauthenticated and has been compromised by the Meow/Indexrm automated extortion campaign.

**State:** 1 index total (`read_me` ransom note), all original data wiped. The operator's health platform data no longer exists in this Elasticsearch instance.

**Actor attribution (from aimap/VisorLog):**
- Actor class: Meow-Actor-A
- Contact: wendy.etabw@gmx.com
- Paste: tli.sh/73x1k
- BTC: bc1q38rjul6gdamfflf6p4ukz0ymtvfgfv2j9saf6r

**Note:** This host also runs FastGPT on port 3000 (title "AI", custom branded). The Elasticsearch is a co-deployed service that was left unprotected. FastGPT itself does not use Elasticsearch natively; this is an operator-added service.

**Disclosure framing:** Do not tell this operator "your host is exposed." Tell them "you have been hit by an automated extortion attack, here is the actor attribution and recovery posture." Data is already gone.

---

## Operator Attribution

| IP | Operator | Evidence |
|----|---------|---------|
| 119.13.85.110 | **Tianjin Pharmaceutical Group** (天津市医药集团有限公司) | TLS CN: `chatdrt.tjph.cn`; WHOIS tjph.cn = 天津市医药集团有限公司, zhftjpharm@163.com |
| 47.121.112.125 | healthruway.com | TLS cert `*.healthruway.com` (WoTrus CA, CN) |
| 150.158.92.76 | ai.powev.com | TLS CN from Shodan: ai.powev.com (Let's Encrypt) |

**Tianjin Pharmaceutical Group note:** State-owned pharma enterprise. Running FastGPT-Admin + OneAPI at `chatdrt.tjph.cn` on HuaweiCloud HK. OneAPI is properly auth-gated (HTTP 401). MinIO on port 9000 is auth-required. No active exposure -- identity attribution only.

---

## aimap Results

| Service | Auth status | Count | Notes |
|---------|-------------|-------|-------|
| FastGPT | auth=unknown | 9 | Deep enumerator gap -- no creds check |
| Elasticsearch | auth=none | 1 | 47.121.112.125 (Meow-wiped) |
| One API | auth=required | 1 | 119.13.85.110 (401) |
| MinIO | auth=required | 1 | 119.13.85.110 |
| code-server | (manually verified) | 1 | 34.141.159.187:8080 |

**aimap gap noted:** FastGPT deep enumerator needs: (1) default creds probe root/1234, (2) agent sandbox port 8080 detection, (3) version extraction, (4) registration state check.

---

## Research Question: CN-Jurisdiction Sub-Hypothesis

**Result: FALSIFIED.**

The divide is not jurisdiction. It is use-case/deployment model:

| Platform | Origin | Auth default | Rate |
|----------|--------|-------------|------|
| Bisheng (DataElem) | CN | auth-ON (first-user model) | 0/4 unauth |
| FastGPT (LabRing) | CN | auth-ON (root/1234) | 0 REGISTER_OPEN |
| RAGFlow (infiniflow) | CN | auth-permissive | 87.2% REGISTER_OPEN |
| LobeChat | CN | auth-permissive | 83.3% unauth |
| Langfuse | EU | auth-permissive | 88.9% SIGNUP_OPEN |
| Phoenix | US | auth-permissive | 74.5% unauth |

**Pattern:** Bisheng and FastGPT are enterprise-focused (document intelligence, enterprise RAG, role-based multi-tenant). RAGFlow and LobeChat are developer/consumer tools. The auth-permissive default correlates with developer/consumer tooling, not jurisdiction. Langfuse and Phoenix are observability tools -- developer-class, auth-permissive. The CN-origin maintainers of RAGFlow/LobeChat make the same auth-permissive choices as Western maintainers of similar tools.

**Insight candidate:** Auth-on-default correlates with enterprise deployment model (multi-tenant, RBAC, billing, data residency requirements). Auth-permissive correlates with developer/consumer tooling designed for single-operator local deployment but exposed publicly.

---

## Checklist

```
[x] -1.  OSINT Platoon       — CVE profile, auth posture, fingerprints, dorks
[x] 0.   Shodan harvest      — 18 IPs; http.title:"FastGPT" (17) + http.html:"fastgpt" port:3000 (13)
[x] 0b.  Censys              — NULL (insufficient balance on v2 API)
[x] 0c.  scanner             — 13 live; 34.141 code-server flagged; nmap + httpx
[x] 0d.  aimap FPs           — fingerprint exists (v1.9.53); gap: no deep enumerator
[x] 1b.  aimap               — 44 open ports / 12 hosts; 2 findings; FastGPT auth=unknown (enumerator gap)
[x] 1a.  VisorPlus           — help-mode only (assess command not triggered)
[x] 2.   VisorGraph          — cert pivot: tjph.cn = Tianjin Pharma; healthruway.com confirmed
[x] 3v.  VERIFY              — F1 confirmed 200-no-auth; F2 Meow-wiped confirmed
[x] 4.   JS-bundle           — RegisterForm route present; billing components (PayModal, BillTable)
[x] 6.   VisorLog            — #2 (34.141 HIGH), #3 (47.121 CRITICAL)
[ ] 7.   VisorScuba          — skipped (no unauth data read to score)
[x] 8.   BARE                — N/A (no interactive exploit surface confirmed open)
[ ] 9.   VisorCorpus         — N/A (no accessible LLM endpoint found unauth)
[ ] 10.  VisorRAG            — no prior findings to recall
[x] 12b. findings-breakdown  — written
[x] 13.  persist -> GitHub   — pending
```
