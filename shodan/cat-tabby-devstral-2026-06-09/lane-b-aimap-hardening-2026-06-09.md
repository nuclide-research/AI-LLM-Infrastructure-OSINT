# Lane-B aimap Tabby Fingerprint Hardening — 2026-06-09

**Operator:** Lane-B DCWF 623 AI/ML Specialist
**Outfit:** `cat-tabby-lane-b-engineering`
**Atoms exercised:** T0064 (data-mining R&D), K0177 (kill chain), K0001 (networking concepts), K0009 (application vulnerabilities), A0123 (CIA to ML ops), S0001 (vuln scan)
**Tool:** `aimap` v1.9.53 (rebuilt clean, version preserved)
**File:** `~/ai-recon/aimap/fingerprints.go` — Tabby (TabbyML) block (lines 2685-2728)

---

## FP Class: `tabby-honeypot-vpn-mimicry`

The Cat-Tabby + Devstral survey on 2026-06-09 surfaced 66 false-positive Tabby identifications. Root cause: a VPN-exit / response-rewriting layer in the network path between scanner and target hosts was injecting a 22-byte stub body — literally `<title>Tabby - Sign In` — into `/auth/signin` responses of unrelated hosts (Elasticsearch, MCP credential-theft honeypots, generic SaaS landing pages). The injection bypassed the conjunctive structure because both pre-hardening matchers fired:

- `status_code 200` — satisfied (the rewriting layer returns 200)
- `body_contains "<title>Tabby"` — satisfied (literally what was injected)

This is the classic "naked single-token `body_contains` proves too permissive" failure (Insight #6). The marker carried no structural anchor.

## Original Probe Weakness

```go
{Path: "/auth/signin", Matches: []MatchCond{
    {Type: "status_code", Value: "200"},
    {Type: "body_contains", Value: "<title>Tabby"},
}},
```

Two-condition conjunctive, but the second condition is a 14-byte literal that any MITM can mint. There is no structural witness that the response is actually rendered by a Tabby Next.js SPA.

## Hardened Probe

```go
{Path: "/auth/signin", Matches: []MatchCond{
    {Type: "status_code", Value: "200"},
    {Type: "body_contains", Value: "<title>Tabby"},
    {Type: "body_contains", Value: "/_next/static/chunks/webpack-"},
    {Type: "body_contains", Value: "app/auth/signin/page-"},
}},
```

Two new conjunctive markers:

1. **`/_next/static/chunks/webpack-`** — the Next.js webpack runtime chunk path. Emitted by every Next.js build (real Tabby is v0.11.0+ Next.js SPA). Confirmed present on the real-Tabby reference response at `5.78.203.59:8080` as `/_next/static/chunks/webpack-3ca055e18387de13.js`.
2. **`app/auth/signin/page-`** — the Tabby-application-route Next.js page chunk path (App Router file-system convention). Even more specific: it names the signin route. Confirmed present on the same reference as `app/auth/signin/page-61459fca9bffa87c.js`.

The honeypot/MITM stub bodies are 22 bytes — no script tags, no chunk paths, no HTML scaffolding. They cannot satisfy either new marker without producing a fully-rendered Next.js SPA shell, at which point they are no longer mimicking — they are reproducing.

**CIA impact (A0123):** Confidentiality preserved (no new data read). Integrity strengthened (FP class refuted). Availability: theoretically a real Tabby v0.10.x build without the webpack chunks could miss; in practice the webpack chunk path has been stable since Tabby switched to Next.js. The pre-existing `/v1/health` probe (probe 1) remains as the version-tolerant identity anchor for any host that lacks the SPA bundle.

## Regression Test Results

| Host                  | Port | Pre-hardening | Post-hardening | Verdict |
|-----------------------|------|---------------|----------------|---------|
| `5.78.203.59` (real)  | 8080 | Tabby fires   | Tabby fires    | TP preserved |
| `3.137.167.45`        | 9090 | Tabby FP      | NO Tabby match | FP refuted; correctly reclassifies as unauth MCP credential-theft honeypot |
| `18.145.83.168`       | 9090 | Tabby FP      | NO Tabby match | FP refuted; same MCP honeypot pattern |
| `13.206.73.237`       | 9090 | Tabby FP      | NO Tabby match | FP refuted; same MCP honeypot pattern |

Real Tabby continues to identify. All three sampled FPs from the contaminated cohort no longer fire as Tabby. Bonus: the hardened scan correctly surfaces what those hosts actually are — unauthenticated MCP servers exposing dangerous tool surfaces (`get_aws_admin_credentials`, `schedule_commands`, etc.) — a finding the Tabby FP was masking.

## VisorCAS Signature Draft

```yaml
signature_id: tabby-honeypot-vpn-mimicry
class: false_positive_refutation
target_tool: aimap
target_fingerprint: "Tabby (TabbyML)"
introduced: 2026-06-09
introduced_by: lane-b-cat-tabby-devstral-survey
shape:
  - probe_path: /auth/signin
    must_be_present:
      - body_contains: "<title>Tabby"
      - status_code: 200
    must_be_absent:
      - body_contains: "/_next/static/chunks/webpack-"
  evidence_hint: |
    Body length typically <= 64 bytes; no <html>/<head>/<script> tags;
    VPN-exit or MITM response-rewriting layer injecting the <title> tag
    into unrelated services' /auth/signin responses.
disposition: confirmed_fp_class
sample_hosts:
  - 3.137.167.45:9090
  - 18.145.83.168:9090
  - 13.206.73.237:9090
cross_corpus: pending_second_confirmation
notes: |
  The MITM injects exactly the 22-byte stub "<title>Tabby - Sign In".
  Real Tabby always emits the Next.js webpack chunk path. The absence
  of the chunk path with presence of the title is the FP fingerprint.
```

The signature is the inverse of the hardened probe: where the aimap matcher now requires `webpack-` PRESENT, VisorCAS records the FP class as `webpack-` ABSENT alongside title PRESENT. Second-corpus confirmation will promote it from `pending_second_confirmation` to standing signature.

## Justification (one line)

Conjunctive marker discipline (Insight #6): a `<title>Tabby` literal can be MITM-injected for free; a full Next.js webpack chunk path cannot, so anchoring the keyword to the SPA's structural artifact converts a 14-byte spoofable token into a build-artifact witness.
