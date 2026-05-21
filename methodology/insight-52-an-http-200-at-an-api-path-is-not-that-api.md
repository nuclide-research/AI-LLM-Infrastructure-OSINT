---
type: methodology
insight_number: 52
title: "An HTTP 200 at an API path is not that API"
---

# Insight #52 — An HTTP 200 at an API path is not that API

**Codified:** 2026-05-21 (global university LLM-exposure map, per-host arsenal triage)
**Family:** Insight #16 (no status code is identity), Insight #51 (a port number names a candidate). This is the layer-7 analogue of #51: where #51 is a TCP connect mistaken for a service, #52 is an HTTP 200 mistaken for an API.
**Falsifiability tier:** high. A counter-sweep where API-path 200s verify as the named API at a materially higher rate breaks it.

---

## The pattern

A scanner that confirms an API by requesting its path and accepting the HTTP 200 produces confident, reproducible, wrong CRITICALs. A web server answers 200 for paths it does not implement. The 200 proves the request was handled. It does not prove the named API is what handled it.

Stated empirically, with the source case:

`menlohunt`'s phase-4 `gcp_metadata` check requested four GCP metadata paths against the target's own IP, for example `http://<ip>/computeMetadata/v1/?recursive=true`. It set the `Metadata-Flavor: Google` request header and emitted a finding on `resp.StatusCode == 200 && len(body) > 0`. Any 200 with a body became "GCP Metadata API — full instance metadata", severity CRITICAL.

Across the university per-host survey the check fired **147 `gcp_metadata` findings on 37 hosts** — 73 CRITICAL, 37 HIGH, 37 MEDIUM. Every one of the 147 carried an HTML document as its evidence body. Not one carried metadata.

| Evidence body | Count | A finding? |
|---|---|---|
| HTML document (`<!DOCTYPE html>` ...) | **147** | no, the target's own web page |
| metadata-API output (plaintext / JSON) | 0 | — |

The precision of an HTTP-200-at-an-API-path label for "this API is exposed" on this sample is **0%**. 147 of 147 were the target's ordinary web server answering for a path it does not serve.

## Mechanism

The GCP metadata API lives at the link-local address `169.254.169.254` (`metadata.google.internal`). It is reachable only from inside a Google Compute instance. It is gated by the `Metadata-Flavor: Google` request header, Google's own confused-deputy guard, and returns plaintext or JSON. It is not reachable by an external scan and it never serves an HTML document.

A scan that requests `http://<public-ip>/computeMetadata/v1/...` never reaches that service. It reaches the target's own web server. The web server, asked for a path it does not implement, returns what web servers return: a homepage, a framework 404, a catch-all landing page. All of it HTML, all of it answered 200 or rendered as 200.

The check conflated two statements. "A request to this path returned 200" is a fact about the target's web server. "The GCP metadata API is exposed here" is a claim about a specific service. The check printed the first as the second. It was wrong on every host, and not randomly wrong. It was systematically wrong, because the same logic produces the same inflated label on every web server alive.

Identity is emitted, not inferred. A service identifies itself by returning something only that service returns. The metadata API identifies itself with the `Metadata-Flavor: Google` *response* header and a `Server: Metadata Server for VM` header. A status code is not that signal. Neither is the fact that the path you asked for came back 200.

## What this insight is NOT

- NOT "the gcp_metadata check is useless." A genuine SSRF or a misconfigured forwarding proxy can expose the metadata API, and that is CRITICAL when it happens. The error was the confirmation logic, not the existence of the check.
- NOT specific to GCP metadata. Any check that confirms an API by status code has this failure mode. AWS (`/latest/meta-data/`) and Azure (`/metadata/instance`) metadata probes fail the same way. So does any `*_api` path probe.
- NOT specific to menlohunt. menlohunt is simply the scanner whose output was measured and then fixed.
- NOT a claim that no scanned host runs GCP. It is a claim that none of the 147 findings verified as the metadata API, because none of them were.

## Falsification conditions

The insight is wrong if:

1. A sweep of API-path 200 candidates on a comparable population verifies as the named API at a materially higher rate, say above 10%.
2. The HTML-body class turns out to be an artifact of university web hosting and does not appear in a commercial-host population.

## The scanner-design corollary, and the fix

The fix is structural. An API-confirmation check must require the API's own identifying signal, not the status code.

Codified into menlohunt, commit `b335dea` (2026-05-21):

- The `gcp_metadata` finding now fires only when the response carries the `Metadata-Flavor: Google` header and the body is not an HTML document.
- A `looksLikeHTML` guard rejects any response that opens as an HTML document.
- Verified: a fresh scan of a previously-affected host, `120.96.125.59`, dropped from 4 `gcp_metadata` findings to 0.

The lesson also ships as code, the same day it was codified, in the verification tool `winnow`. Its `gcp-metadata-html` signature refutes any `gcp_metadata` finding whose evidence is an HTML body. menlohunt stops generating the false positive at the source; winnow catches it downstream, and catches the AWS and Azure variants, and catches it in any other scanner's output. The scanner fix and the screening signature are not redundant. One closes the source, one is the standing net.

## Methodology impact

- This is the layer-7 companion to Insight #51. #51: a TCP connect is not a service. #52: an HTTP 200 is not an API. Together they bound the methodology's load-bearing claim from both transport and application layers. A cheap signal short of a protocol-level discriminator is a candidate, never a finding.
- It is the first insight to ship as an executable signature in `winnow` on the day it was codified. An Insight that stays prose protects nothing. An Insight carried as a signature screens every scan from then on. This is the intended end state for the codified-Insight body.
- API confirmation must anchor on a service-unique response signal: a required response header, a protocol banner, a structured body whose shape only that service produces. The request path and the status code are not signals. They are what the scanner chose, echoed back.

## Cross-references

- **Insight #51** a port number names a candidate. Same failure, layer 4. The 1.4% precision there and the 0% here are the same measurement at two layers.
- **Insight #16** no status code is identity. #52 is the direct application: a 200 is a status code, and a status code is not identity.
- **METHODOLOGY.md** verification is the load-bearing stage. #52 is another verification-stage failure measured at population scale, and the first one fixed in both the scanner and the screening layer at once.

## Source data

- Survey: global university LLM-exposure map, per-host arsenal run, slug `univ-llm-2026-05-hosts`
- Finding set: 147 `gcp_metadata` findings across 37 hosts in `~/recon/global-university-llm-map/results/univ-llm-2026-05-hosts/*/menlohunt.json`, evidence body HTML on all 147
- menlohunt fix: commit `b335dea`, github.com/Nicholas-Kloster/menlohunt
- Screening signature: `gcp-metadata-html` in `winnow`, github.com/Nicholas-Kloster/winnow

---

*Codified by Nuclide Research (Nicholas Kloster + Claude) 2026-05-21 from the global university LLM-exposure map per-host arsenal triage. Methodology per `~/.claude/nuclide-internal/METHODOLOGY.md`.*
