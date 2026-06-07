# RAG framework stragglers, 2026-05-29

_Survey type: category survey of RAG-framework stragglers (AnythingLLM, RAGFlow,
LightRAG, R2R, Kotaemon, Ragapp). Pre-survey intel:
data/platform-intel/rag-frameworks-osint-2026-05-27.md._

## Summary

AnythingLLM ships single-user mode with no password, and two of five sampled
hosts had the web UI open to any browser visitor. The verification narrowed the
finding: the open UI is browser-reachable, but the developer REST API still
demands a key even in no-auth mode. RAGFlow returned 1,705 hosts, a large
pre-auth-RCE-class population, but the RCE lives on an internal RPC port and the
vulnerable version cannot be confirmed from outside, so the survey confirms
identity and stops there. LightRAG is Shodan-dark behind its JSON API.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7070, S7075, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6900, K6935, K7003

<!-- ksat-tag:auto-generated:end -->

Two tool outputs were false positives that verification killed: an aimap "MCP
Server" that served only 404s, an aimap "dcm4che" that was a RuoYi admin
framework, and a menlohunt "public GCS bucket" that was global-namespace guessing
with no link to the host.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.title:"AnythingLLM" port:3001` | 152 | clean, all real AnythingLLM |
| `http.html:"ragflow"` | 1,705 | clean, real RAGFlow at population scale |
| `port:9621 http.html:"LightRAG"` | 0 | JSON-dark |
| `http.favicon.hash:-1467534538` | 0 | RAGFlow favicon hash stale |

AnythingLLM's `<title>` renders to Shodan, so the title dork returned 152 clean
hits, heavily China and Germany on Contabo. RAGFlow's nginx frontend serves the
"RAGFlow" string in HTML, so it returned 1,705, Alibaba and Tencent and Linode
dominated. LightRAG serves a FastAPI JSON API and returned zero, the Insight #67
pattern. The documented RAGFlow favicon hash no longer matches current builds.

## Stage 2, Verify

**AnythingLLM exposes its own auth posture.** `GET /api/setup-complete` is
unauthenticated and returns `RequiresAuth`. Two of five sampled hosts returned
`RequiresAuth:false`: 213.239.218.83 on Contabo and 143.244.209.125 on
DigitalOcean. The other three returned `RequiresAuth:true`.

The verification narrowed the severity. `RequiresAuth:false` means the web UI is
open to any browser visitor, who can use the chat, see the workspaces, and spend
the connected LLM key. But the developer REST API tells a different story:
`GET /api/v1/workspaces` returned `{"error":"No valid api key found."}` even on
the no-auth hosts. The programmatic API is key-gated regardless of the UI auth
mode. So this is a MEDIUM browser-UI exposure, not a fully-open API. The browser
was not driven to read workspace data.

**RAGFlow is a large population with an applicable RCE class.** 1,705 hosts
confirmed by the "RAGFlow" title. CVE-2024-12433 is a pre-auth RCE through pickle
deserialization and a hardcoded RPC AuthKey, fixed in 0.14.0. The exploit path is
the internal RPC service on port 9380, not the web frontend, and the version is
not visible from the SPA root. The survey confirms 1,705 RAGFlow instances and
names the applicable RCE class. It does not confirm a vulnerable version per host
and does not touch the internal RPC. The honest tier is identity at scale, RCE as
applicable class.

**The adjacent surface and the false positives.** menlohunt's IP-shadow on the
browser-unauth 213.239.218.83 found MySQL open on 3306, a real host-attributed
adjacent port (auth state not exercised). It also reported a "public GCS bucket"
named `static-dev`, but that was the tool guessing common bucket names against
the global storage.googleapis.com namespace, with no link to this host's
operator. Per the hard-proof rule, the bucket is not recorded as this operator's
exposure. aimap, which has no AnythingLLM or RAGFlow fingerprint, reported an
"MCP Server" on 85.190.246.13 that served only 404s, and a "dcm4che" on
118.253.158.3 that was a RuoYi-Vue-Plus admin framework returning a generic
catchall, the documented aimap dcm4chee false positive. Three tool over-claims,
three killed at verification.

## Impact

- **Browser-UI exposure.** Two AnythingLLM hosts let any visitor open the UI and
  use the operator's configured LLM, see the workspaces, and read the chat
  history. The dev API key gates the programmatic path.
- **RAGFlow RCE class at scale.** 1,705 RAGFlow instances carry the
  CVE-2024-12433 class if they run a version below 0.14.0. Confirming the
  vulnerable subset needs the internal RPC port, out of scope here.

## Remediation

- Enable multi-user mode on AnythingLLM and set a password. Single-user mode
  ships with the UI open.
- Upgrade RAGFlow to 0.14.0 or later and keep the internal RPC port off the
  public internet.
- Bind MySQL to localhost or firewall it.

## What the method could not see

LightRAG, R2R, Kotaemon, and Ragapp are Shodan-dark behind JSON APIs. The RAGFlow
vulnerable-version subset needs internal-RPC probing the survey did not perform.
The AnythingLLM sample was five of 152.

## Note on footprint

The harvest and the AnythingLLM and RAGFlow verification ran through Mullvad
(us-lax-wg-007). The VPN dropped before the later arsenal steps, and the aimap
re-run, the menlohunt sweep, and the two false-positive confirmation probes ran
off-VPN with operator authorization. Recorded for an honest footprint.

## Toolchain provenance

```
JAXEN        Playwright; 4 dorks (AnythingLLM 152, RAGFlow 1705, LightRAG 0, favicon 0)
aimap        no AnythingLLM/RAGFlow fingerprint; 2 incidental services, both FP (MCP-404, RuoYi-not-dcm4che)
aimap-profile run on browser-unauth host
VisorGraph   bare cloud IPs, 0 nodes
VisorBishop  menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    213.239.218.83 IP-shadow: MySQL :3306 open (real); GCS "buckets" = global-namespace FP (not attributed)
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only
VisorPlus    components individual
VisorLog     2 AnythingLLM browser-unauth events -> nuclide.db
VisorScuba   AnythingLLM browser-unauth not mapped to a control (gap)
BARE         RAG authz first-party class
VisorCorpus  N/A no inference surface confirmed unauth
VisorAgent   controlled-target only; not fired at survey hosts
VisorRAG     N/A
VisorHollow  N/A Windows-only
cortex       codify-stage
JS-bundle    N/A AnythingLLM React UI, RAGFlow nginx SPA, no secret bundle
```
