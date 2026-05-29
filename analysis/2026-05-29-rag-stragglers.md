# Session Analysis: RAG framework stragglers

## 1. Overview

### Objective
Survey RAG-framework stragglers (AnythingLLM, RAGFlow, LightRAG, R2R, Kotaemon,
Ragapp) for unauthenticated exposure and the pre-auth RCE classes the intel
flagged (RAGFlow CVE-2024-12433). Intel:
data/platform-intel/rag-frameworks-osint-2026-05-27.md.

### Scope and Constraints
Commercial cloud (Contabo, DigitalOcean, Alibaba, Tencent, Linode). Shodan via
Playwright. Harvest and the AnythingLLM/RAGFlow verification ran through Mullvad
(us-lax-wg-007). The VPN dropped mid-survey; the later arsenal steps ran off-VPN
with operator authorization. Restraint: AnythingLLM auth-posture marker only, no
browser-driven workspace read, no RAGFlow internal-RPC probe, no MySQL auth
attempt.

## 2. Environment and Tooling

### Claude Code Operation
Orchestrator-direct. Shodan harvest paced after an extended Cloudflare cooldown.
aimap and menlohunt as bounded background commands. The Bash safety classifier
and the VPN were both intermittently down; work continued via file tools and
operator-authorized off-VPN probing.

### Tools Used
Full 19-tool arsenal. Material: JAXEN, aimap, aimap-profile, menlohunt, VisorLog.
Non-runs: VisorSD/recongraph/nu-recon/VisorPlus (Shodan-blocked), VisorGoose
(gov/edu), VisorCorpus/VisorAgent/VisorRAG (ethical-stop), VisorHollow (Windows),
VisorBishop (menlohunt covered shadow), JS-bundle (React/SPA, no bundle).

### Notable Configuration
aimap v1.9.39 (no AnythingLLM/RAGFlow fingerprint, gap). nuclide.db at
~/visorlog/nuclide.db. Workspace ~/recon/rag-stragglers-2026-05-29/.

## 3. Methodology

### Enumeration approach
Four dorks. AnythingLLM and RAGFlow by HTML/title; LightRAG by port plus string;
RAGFlow favicon hash.

### Candidate identification
AnythingLLM 152, RAGFlow 1,705, LightRAG 0, favicon 0.

### Validation checks
AnythingLLM: /api/setup-complete for auth posture, /api/v1/workspaces for dev-API
state. RAGFlow: /api/v1/datasets. menlohunt IP-shadow on a browser-unauth host.

### Safeguards
Mullvad for harvest and primary verification. Marker-only. No browser-driven read,
no internal-RPC probe, no MySQL auth. Tool over-claims verified against primary
source before recording.

## 4. Execution Trace

```
1. Read RAG intel; Mullvad verified (us-lax-wg-007); Cloudflare cooldown waited out
2. AnythingLLM title 3001 -> 152
3. LightRAG 9621 -> 0; RAGFlow favicon -> 0; RAGFlow html -> 1705
4. AnythingLLM verify (on-VPN): /api/setup-complete -> 2/5 RequiresAuth:false
   (213.239.218.83, 143.244.209.125); /api/v1/workspaces -> key-gated even in no-auth
5. RAGFlow verify (on-VPN): /api/v1/datasets -> SPA HTML (API proxied/internal)
6. [VPN dropped] aimap re-run -> 2 services, both FP on primary-source check
   (85.190.246.13 MCP=404; 118.253.158.3 dcm4che=RuoYi admin)
7. menlohunt IP-shadow 213.239.218.83 -> MySQL :3306 open (real); GCS "buckets" = namespace-guess FP
8. VisorLog: 2 AnythingLLM browser-unauth events
9. Wrote case study, findings-breakdown, this analysis
```

## 5. Findings

### 5.1 AnythingLLM browser-UI-unauth x2: MEDIUM
213.239.218.83, 143.244.209.125 return RequiresAuth:false. Web UI open to any
browser; dev REST API key-gated (verification-refined). Single-user default.

### 5.2 213.239.218.83 MySQL :3306 open: adjacent
Host-attributed open port. Auth state not exercised.

### 5.3 RAGFlow 1,705: identity, RCE applicable-class
Population confirmed; CVE-2024-12433 class applies to <0.14.0; version not
externally confirmable; internal RPC not probed.

### 5.4 Three tool false positives, killed
menlohunt GCS namespace-guess; aimap MCP-on-404; aimap dcm4che-as-RuoYi.

## 6. Risk Assessment

### Overall Posture
AnythingLLM single-user default produces a browser-open minority (2/5). RAGFlow is
a large RCE-class population the survey can only confirm by identity. The thesis
gradient holds: the shipping default predicts the open rate.

### Confidentiality
The browser-open AnythingLLM hosts expose chat, workspaces, and connected-LLM use
to any visitor. The dev API gates the programmatic path.

### Integrity
RAGFlow's CVE-2024-12433 class is a pre-auth RCE on the internal RPC, not
exercised.

### Availability
The open MySQL on the AnythingLLM host is a denial vector if unauthenticated, not
tested.

### Systemic Patterns
- Verification refines severity: browser-UI-open is not API-open (Insight #16).
- Three tool over-claims killed by primary source (aimap MCP/dcm4che, menlohunt GCS namespace-guess).
- Insight #67: LightRAG and the other JSON-API RAG servers Shodan-dark.
- 6th thesis data point: AnythingLLM single-user default -> 2/5 browser-open.

## 7. Recommendations

### R1: Enable AnythingLLM multi-user mode with a password
Single-user mode ships the UI open.

### R2: Upgrade RAGFlow past 0.14.0 and firewall the internal RPC port

### R3: Bind MySQL to localhost

```
# AnythingLLM: enable password / multi-user in settings; do not run single-user on a public IP
```

## 8. Limitations

The VPN dropped mid-survey; later arsenal steps ran off-VPN (operator-authorized,
footprint recorded). LightRAG/R2R/Kotaemon/Ragapp are Shodan-dark and were not
enumerated past LightRAG. RAGFlow's vulnerable-version subset needs internal-RPC
probing not performed. AnythingLLM sample was 5 of 152.

## 9. PoC Illustrations

```
# AnythingLLM auth posture, unauth (browser-UI-open)
$ curl -s http://213.239.218.83:3001/api/setup-complete
{"results":{"RequiresAuth":false,"AuthToken":false,"JWTSecret":false,...}}
# dev API still key-gated even in no-auth mode
$ curl -s http://213.239.218.83:3001/api/v1/workspaces
{"error":"No valid api key found."}

# Tool FP killed by primary source
$ curl -s http://118.253.158.3:8080/   # aimap said dcm4che
欢迎使用RuoYi-Vue-Plus后台管理框架   # = RuoYi admin framework, not DICOM
```
