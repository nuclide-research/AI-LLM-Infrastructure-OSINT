# LLM Safety / Guardrail survey, 2026-05-29

_Survey type: new-category population survey. LLM guardrails, safety classifiers,
prompt-injection scanners. Pre-survey intel:
data/platform-intel/safety-guardrail-osint-2026-05-27.md._

## Summary

Five dorks. One confirmed unauthenticated guardrail server, and the guardrail was
the least exposed thing on the box. The same host left MongoDB, Redis, MySQL,
PostgreSQL, and a Docker registry open with no authentication. The safety tool
meant to inspect untrusted input was sitting on an unlocked data tier.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** S7056, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K22, K6311, K6900, K6935, K7003, T5896

<!-- ksat-tag:auto-generated:end -->

The category ships auth-off by default and the population shows it, but with a
toggle that some operators set. Of three reachable LLM Guard servers, one was
open and two required the AUTH_TOKEN. Most guardrail servers do not index on
Shodan at all because they serve JSON, not HTML. That is Insight #67 again, now
on a third category.

## Stage 0, Discover

| Dork | Total | Verdict |
|------|------:|---------|
| `http.html:"LLM Guard API"` | 9 | clean, real LLM Guard scanner servers |
| `http.html:"/v1/rails/configs"` (NeMo) | 0 | JSON-dark |
| `port:5000 http.html:"vigil"` | 20 | false-positive swamp |
| `http.html:"guardrails-ai" port:8000` | 0 | Swagger-dark |
| `http.html:"rebuff" port:3000` | 0 | archived, string not in HTML |

LLM Guard was the one platform that indexed, because its OpenAPI title string
"LLM Guard API" appears in the served HTML. Nine hits across AWS, OVH, Hetzner,
Azure, and Koyeb. NeMo Guardrails, Guardrails AI, and Rebuff returned zero: they
serve JSON APIs, and the marker strings live in the JSON body or the `/docs`
route, not the crawled root HTML.

Vigil was the trap. `port:5000 http.html:"vigil"` returned 20, every one a
Pro-Vigil video-surveillance box or a Synology NAS named nas-vigil, on
residential ISP ranges. Not one was the deadbits prompt-injection scanner. The
word "vigil" belongs to a security-camera brand. Single-keyword collision, the
Garak lesson again.

## Stage 2, Verify

LLM Guard's identity is `GET /` returning `{"name":"LLM Guard API"}`, no auth.
The auth state is the scan endpoint. `POST /analyze/prompt` with a benign test
input runs the scanners and returns the verdict, or returns
`{"message":"Not authenticated"}` when AUTH_TOKEN is set.

**5.78.101.230 on Hetzner ran the scanners with no token.** `POST /analyze/prompt`
returned `{"is_valid":true,"scanners":{"PromptInjection":-1.0,"Toxicity":-1.0,
"Secrets":-1.0},"sanitized_prompt":"test"}`. `POST /analyze/output` returned the
Sensitive scanner. The full scanner roster is disclosed, and the safety layer is
bypassable: an attacker sends straight to the upstream LLM. The test input was
benign and no upstream bypass was exercised.

**Two hosts were locked.** 57.128.58.103 and 15.204.46.173 returned
`{"message":"Not authenticated"}`. Their operators set the AUTH_TOKEN. The other
four hits had aged out of the Shodan banner: the Koyeb fctl.app hosts cycle, and
all four returned connection-refused on re-probe.

One open of three reachable. The auth-off default produces a nonzero open rate.
The toggle exists and two of three operators used it.

## Stage 3 through 5, the IP shadow, where the real finding was

The unauthenticated guardrail was the headline until menlohunt swept the host.

menlohunt's per-IP scan of 5.78.101.230 found MongoDB on 27017, Redis 7.2.10 on
6379, MySQL on 3306, PostgreSQL on 5432, and a Docker registry on 5000. Six
attack chains, three rated critical. Primary source confirmed the Redis: `PING`
returned `+PONG` with no AUTH, `INFO server` returned version 7.2.10 on Linux 5.4
with a 17-day uptime. The MongoDB port answered a TCP connect and was not
queried.

The operator who left the LLM guardrail open also left the entire data tier open.
The guardrail bypass is almost beside the point next to an unauthenticated
MongoDB and Redis on the same box. This is the IP-direct shadow paying off, the
same pattern as Insight #12: one service auth-off predicts more auth-off on the
same IP. The irony is the platform class. The tool was a safety scanner, and the
host around it was the least safe thing in the survey.

Six findings landed in nuclide.db via VisorLog.

## Stage 6 and 7, score, codify

aimap has no LLM Guard fingerprint and found only a Grafana on one host. The
guardrail category is a fingerprint gap in aimap and VisorBishop, so manual
verification carried the survey. That gap is logged as a candidate fingerprint:
`GET /` returning `{"name":"LLM Guard API"}` plus the `/analyze/prompt` scanner
response shape.

BARE found no Metasploit coverage for the guardrail finding class. VisorScuba has
no control that maps an unauthenticated guardrail or a safety-layer bypass, so it
did not score the finding. Both are the expected gaps for a category aimap has not
yet learned.

## Impact

- **Safety-layer bypass.** The open LLM Guard lets an attacker confirm which
  scanners run, then route prompts straight to the upstream model, defeating the
  control the operator deployed it to provide.
- **Stacked data-tier exposure.** The same host hands an unauthenticated attacker
  MongoDB, Redis, MySQL, and PostgreSQL. This is the operator-catastrophe class,
  and the guardrail exposure is the smallest part of it.

## Remediation

- Set AUTH_TOKEN on LLM Guard. It ships off; the operator must turn it on.
- Bind MongoDB, Redis, MySQL, and PostgreSQL to localhost or firewall them. A
  default-config data tier on a public IP is an open door.
- Put the Docker registry behind authentication.

## What the method could not see

NeMo Guardrails, Guardrails AI, and Rebuff are Shodan-dark behind their JSON
roots. A real census of those needs masscan on port 8000 and 3000 with API-shape
fingerprinting, not Shodan. The LLM Guard sample was nine hits, and four had aged
out by probe time. The Vigil prompt-injection scanner could not be separated from
the Pro-Vigil brand on a title or HTML dork and needs an `/analyze` path conjunct.

## Toolchain provenance

```
JAXEN        Playwright; 5 dorks (LLM Guard 9 clean, 3 JSON-dark 0, Vigil 20 FP)
aimap        lean 8 hosts x 7 ports; only Grafana found (no LLM Guard fingerprint, gap)
aimap-profile 5.78.101.230 unclassified/commercial, no honeypot
VisorGraph   0 nodes/edges (bare cloud IP)
VisorBishop  no LLM Guard fingerprint (same gap); menlohunt covered IP-shadow
VisorSD      N/A no Shodan key
VisorGoose   N/A gov/edu scope
menlohunt    HEADLINE: 5.78.101.230 -> MongoDB + Redis 7.2.10 + MySQL + Postgres + Docker registry, 6 chains 3 critical
recongraph   N/A Shodan-dependent
nu-recon     N/A simulated-only without live key
VisorPlus    components run individually
VisorLog     8 aimap + 2 manual events -> nuclide.db
VisorScuba   no control for guardrail-unauth (gap)
BARE         no MSF coverage (0.507/0.502) first-party/novel
VisorCorpus  136-case corpus reusable (guardrails are LLM-adjacent)
VisorAgent   controlled-target only; NOT fired at the operator host (ethical-stop)
VisorRAG     N/A no RAG surface
VisorHollow  N/A Windows-only
cortex       run at codify
JS-bundle    N/A LLM Guard serves JSON + minimal Swagger, no secret bundle
```
