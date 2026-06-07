# PromptLayer — Marker-Build Assessment

**Date:** 2026-05-22
**Target:** PromptLayer (LLM request-logging / prompt-management SaaS, Magniv Inc)
**Mode:** Marker-build. First standalone treatment of the PromptLayer platform class.
**Scope run:** Single host `34.95.65.63` + the production `dashboard.promptlayer.com` SPA.
**Population survey:** deferred (see Negative Space).

---

## 1. Summary

PromptLayer was queued for its first population survey: `http.title:"PromptLayer"`
(6 hits) and `ssl.cert.subject.cn:promptlayer` (10 hits). The discovery stage
could not run — both Shodan API keys on `rooster` return `401 Unauthorized`, and
the ledger holds zero pre-harvested PromptLayer hosts, so there was no fallback
corpus. JAXEN, VisorSD, VisorGoose and VisorPlus's `hunt` path are all
Shodan-gated and were blocked at the same point.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, K7054, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7051, S7056, S7067, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K108, K1158, K1159, K22, K6311, K6900, K6935, K7003, K942, T5896

<!-- ksat-tag:auto-generated:end -->

The assessment proceeded in marker-build mode: derive the PromptLayer identity
marker from the one host already in hand (`34.95.65.63`, captured 2026-04-20),
then run the full arsenal against that single host so the population survey can
be executed cheaply and correctly the moment Shodan access is restored.

**What stands:**

- The prior finding holds and is re-verified. Three hardcoded Make.com webhook
  URLs are embedded in the production `dashboard.promptlayer.com` SPA bundle,
  callable unauthenticated by any visitor. This is a frontend secret-leak class
  (Insight #19 family), not a backend auth failure.
- The PromptLayer backend API has hardened. `api.promptlayer.com/workspaces`
  returned `422` in April 2026 and returns `401` now — auth-on-default,
  consistent with Insight #40 (the thesis strengthens rightward over time under
  disclosure pressure).
- An identity marker for the population survey is defined and validated against
  the bundle (Section 3).
- One tool gap codified: VisorScuba misclassifies any unauthenticated non-Ollama
  node as "Unauthenticated Ollama" (Section 6).

---

## 2. Architecture

PromptLayer is a three-surface deployment:

| Surface | Host | Role | Hosting |
|---|---|---|---|
| Marketing | `www.promptlayer.com` | Static marketing site | Vercel (`server: Vercel`, `x-vercel-id`) |
| Dashboard SPA | `dashboard.promptlayer.com` | Vite-built single-page app | Google Cloud Storage (`server: UploadServer`) |
| Backend API | `api.promptlayer.com` | Headless REST API | Auth-gated (`401` unauth) |

`34.95.65.63` is a Google Cloud Storage edge serving the dashboard SPA. The
`UploadServer` response header is the GCS static-hosting signature. The SPA
bundle fetched from this IP is byte-identical to the one served from the
canonical `dashboard.promptlayer.com` hostname:

```
863f07e6a97b7c2d064139f2545971ac7eda8b9998bc3f7dcec265c04a557ead  (GCS edge 34.95.65.63)
863f07e6a97b7c2d064139f2545971ac7eda8b9998bc3f7dcec265c04a557ead  (dashboard.promptlayer.com)
```

The exposure is the production SPA, not a stray edge node.

Ancillary surfaces seen in the SPA network capture, all benign:
`colonial.promptlayer.com` is a PostHog reverse-proxy; the `phc_*` key it carries
is a PostHog publishable key (public by design). `tag.clearbitscripts.com/v1/pk_278599...`
is a Clearbit publishable tag key (public by design). Neither is a finding.
Intercom uses `user_hash` HMAC verification — correct.

---

## 3. The identity marker

Per Insight #15, a raw `http.title:"PromptLayer"` dork runs ~50% false positives
— marketing-page reflections, reverse proxies passing the title through, clones.
A population survey needs a marker that confirms a host is *running* PromptLayer,
not merely *mentioning* it.

PromptLayer's dashboard API contract carries endpoint names that are unique to
the product and would not appear in a coincidental title match or a passthrough
proxy's served JavaScript:

```
/api/dashboard/v2/organizations-with-workspace-and-invites
/expand-prompt-blueprint
/branch-prompt-template-version
/duplicate-prompt-template-to-workspace
/add-request-log-to-dataset
/get-shared-request
```

**Chosen marker:** the string `organizations-with-workspace-and-invites`. It is
a single, distinctive, product-specific API path fragment. It appears once in
the production bundle and is not a generic framework or library term.

**Marker probe (for the deferred population survey):**

1. Fetch `/` from the candidate host, parse the SPA entry HTML for the
   `/assets/index-*.js` bundle reference.
2. Fetch the bundle.
3. Confirm `organizations-with-workspace-and-invites` is present.
4. Only hosts passing step 3 count toward the PromptLayer population. Quote both
   the raw dork count and the marker-confirmed count (Insight #15).

This marker should be added to aimap as a PromptLayer fingerprint: a conjunctive
matcher of `http.title:"PromptLayer"` + bundle-contains
`organizations-with-workspace-and-invites` — three conjuncts in the Insight #6
sense (title + structured SPA asset path + anchored product-unique keyword).

---

## 4. Finding — hardcoded Make.com webhooks in the public client bundle

### 4.1 What

Three Make.com webhook URLs are embedded directly in the dashboard SPA bundle
`index-DRh7GgeC.js`. The bundle loads unconditionally for every unauthenticated
visitor to `dashboard.promptlayer.com` on initial page render.

| Offset | Webhook token | Function | Timeout |
|---|---|---|---|
| 7,045,111 | `yeqk2o9ehl7u7588upfcn5du3togu8ue` | "AI dataset assistant" | 35 s |
| 7,051,448 | `ns5g45k7f52qixmhdexk848m5o7cydbn` | "Generate Dataset" | — |
| 7,264,382 | `9teowog7bslthsy30xju8rynk4v8s53c` | "AI prompt assistant" | 45 s |

Reconstructed call site (webhook 3, "AI prompt assistant"):

```js
const r = new AbortController,
  s = setTimeout(() => { r.abort(), Ke("Oh no! The AI prompt assistant is taking too long to respond. Please try again.") }, 45e3);
try {
  const o = await (await fetch("https://hook.us1.make.com/9teowog7bslthsy30xju8rynk4v8s53c", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt_blueprint: JSON.stringify(n), customer_prompt: JSON.stringify(t) }),
    signal: r.signal
  })).json();
```

All three are bare `POST` calls with `Content-Type: application/json` and no
authentication header, no signature, no nonce.

### 4.2 Why it matters

A Make.com webhook URL *is* the credential. Make webhook scenarios authenticate
the caller solely by possession of the unguessable URL path token. Once that
token is in a public JS bundle, anyone who reads the bundle holds the credential.

These three scenarios each invoke an LLM behind PromptLayer's Make account
(prompt generation, dataset generation). An attacker who scripts `POST`s to the
three URLs drains the operator's Make.com operations quota and any LLM provider
quota the scenarios consume — classic **LLMjacking / quota-drain**. No PromptLayer
login is required; the bundle is served to anonymous visitors.

### 4.3 Chain context

This is the same class as the PromptLayer prior finding's framing and the
SmartShop AI `api.amazonrec.space` case (Insight #19): a CDN/cloud-fronted SPA
that ships a hardcoded upstream credential in its largest JS asset. The
distinguishing trait of the class — and why it is not caught by port-and-banner
fingerprinting — is that the vulnerable surface is *static client code*, not a
listening service. aimap correctly found "no AI service" on `34.95.65.63`; the
exposure lives in a file the host serves, not in a port it answers on. JS-bundle
extraction is the only stage of the chain that surfaces it.

BARE scored this finding at 0.443 against the 3,904-module Metasploit corpus —
below the 0.55 coverage threshold. There is no commodity exploit module for
"hardcoded webhook in client bundle"; it is a first-party design fault, not a
CVE chain. That null result is itself the classification.

### 4.4 Remediation

Move the three webhook invocations server-side. The SPA should call a
PromptLayer backend endpoint (authenticated by the user's existing session); the
backend holds the Make.com webhook URLs as server-side secrets and proxies the
request. The webhook tokens currently in the bundle must be rotated in Make.com
— they are compromised by virtue of having been public, independent of whether
abuse has occurred yet.

### 4.5 Restraint

None of the three webhooks were invoked. The finding rests entirely on passive
bundle retrieval and static code inspection. Evidence does not depend on a live
trigger and remediation urgency does not either.

---

## 5. Negative space — what this assessment could not see

- **The population survey did not run.** Both Shodan keys on `rooster` return
  `401`. JAXEN, VisorSD, VisorGoose and VisorPlus `hunt` are Shodan-gated and
  were blocked. The "6 title hits / 10 cert-CN hits" counts in the briefing came
  from a Shodan session with working access; they are unverified here.
- **The ledger held no fallback corpus.** `nuclide.db` had zero PromptLayer or
  `34.95.65.63` rows before this run, so the Insight #9 ledger-substrate
  discovery move had nothing to work with.
- **`recongraph` returned 0 nodes / 0 edges.** Its passive sources yielded
  nothing for a bare GCP IP without a Shodan host record to seed from.
- **`VisorRAG` could not run.** The local embedding service returns `401`; RAG
  ingest of the playbooks failed. Same infrastructure gap recorded in Session 30.
- **`VisorAgent` was not fired.** Ethical-stop boundary — it is never pointed at
  a real operator endpoint. The controlled-target run also could not execute: no
  local LLM endpoint is available on `rooster` (same infra gap as VisorRAG).
- The cert-CN population (`ssl.cert.subject.cn:promptlayer`, 10 hits) is, per
  Insight #47, attribution-only and most likely reverse-proxy-fronted with auth
  on. It is not platform confirmation and must be run through the marker probe
  like any other corpus.

---

## 6. Tool gap — VisorScuba misclassifies non-Ollama unauthenticated nodes

`visorscuba assess` was run against the ledger node for this finding. It returned:

```json
{"score":0,"max_score":0,"compliance_pct":0,"passing":false,
 "violations":[{"criticality":"Critical","id":"AI.C1",
   "details":"Unauthenticated Ollama at 34.95.65.63 (dashboard.promptlayer.com)"}]}
```

The node is a PromptLayer SPA edge. It is not Ollama. Two defects compound:

1. `visorlog add` populates the VisorScuba node schema with `port_11434_public:true`
   by default when no Ollama-specific fields are supplied — a non-Ollama finding
   has no honest representation in the schema.
2. VisorScuba's `AI.C1` rule hardcodes the word "Ollama" into the violation
   message, so any node with `authenticated:false` is reported as an
   "Unauthenticated Ollama" regardless of what it actually is.

This is the mirror image of the Session 30 VisorScuba gap (AI.C1 *only* firing
on ollama-class nodes). The schema cannot represent the actual finding class —
a frontend webhook leak — and the score (0/10) is computed on a false premise.

**Proposed fix:** add a `finding_class` enum to the VisorScuba node schema
(`ollama` | `webhook_leak` | `setup_token` | `datasource` | `unauth_api` | ...),
make `AI.C1`'s message template read from it, and add the rules already proposed
in Session 30 (`AI.C8 setup_token_exposed`, `AI.H7 vllm_unauth_api`, etc.). A
`webhook_leak` class scoring under a new `AI.C10` (hardcoded upstream credential
in client-delivered code) would let this finding score honestly.

---

## 7. Toolchain provenance

```
[~] JAXEN          deferred — both Shodan keys 401; no live harvest possible
[x] aimap          2 open ports (80/443), no AI service on host (correct — SPA edge, not inference)
[x] aimap-profile  GCP / Google LLC; title-confirmed PromptLayer; no security.txt, no bounty program
[x] VisorGraph     server=UploadServer (GCS), exposure=public_intended; 6 nodes / 2 edges; cert issued_for 2 SANs
[x] VisorBishop    3 targets, severity distribution: none — no listening platform service (consistent with aimap)
[~] VisorSD        dry-run only — Shodan-gated; printed scoped query catalog, no live hits possible
[x] VisorGoose     n/a result — gov/edu Ollama/WebUI discovery tool; PromptLayer is commercial; 0 expected
[x] menlohunt      GCP EASM scan: 4 findings (M:1 I:3), 0 attack chains; MEDIUM = WireGuard UDP 51820 open|filtered (FP — UDP ambiguity, no WireGuard on a GCS edge)
[x] recongraph     0 nodes / 0 edges — no passive seed without Shodan host record
[x] nu-recon       simulated mode (no Shodan); overall_risk low; reported port 22 "exposed" — contradicted by direct TCP probe (22 closed); trust the probe
[~] VisorPlus      orchestrator — components run by hand (methodology §5 permits); hunt path Shodan-blocked
[x] VisorLog       finding #35925 ingested into nuclide.db (high, tags WEBHOOK-LEAK,LLMJACKING,SPA,GCS)
[x] VisorScuba     ran — AI.C1 fired as FALSE POSITIVE (see Section 6); tool gap codified
[x] BARE           PL-1 webhook leak 0.443 < 0.55 → no msf coverage (first-party design fault, not a CVE chain)
[x] VisorCorpus    adversarial corpus built (baseline variant) for the LLM-adjacent surface
[—] VisorAgent     ethical-stop — not fired at survey set; controlled-target run also blocked (no local LLM on rooster)
[~] VisorRAG       failed — local embedding API 401; playbook ingest could not run
[—] VisorHollow    not applicable — Windows-only process-injection benchmark
[x] cortex         run against this analysis document (auth-context validation)
[x] JS-bundle      3 Make.com webhooks confirmed; pk_/phc_ keys identified as publishable-class (not leaks); identity marker derived
```

---

## 8. Next actions

1. **Restore Shodan access**, then run the deferred population survey:
   `jaxen hunt 'http.title:"PromptLayer"'` and `jaxen hunt 'ssl.cert.subject.cn:promptlayer'`,
   apply the Section 3 marker probe, quote raw vs marker-confirmed counts.
2. **Add the PromptLayer fingerprint to aimap** — conjunctive matcher per Section 3.
3. **Patch VisorScuba** — `finding_class` enum + non-Ollama AI.C1 message + the
   Session 30 rule additions. Section 6.
4. **Candidate Insight** — "the vulnerable surface is static client code, not a
   listening service": port-and-banner fingerprinting structurally cannot see a
   hardcoded-credential-in-bundle finding; JS-bundle extraction is mandatory and
   non-substitutable for any CDN/cloud-fronted SPA platform class. Extends
   Insight #19 from "a tell to look for" to "a stage that cannot be skipped."
```
