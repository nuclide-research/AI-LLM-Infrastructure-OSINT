# Lane C — Sandbox-MITM Verdict — Cat-Tabby + Devstral 2026-06-09

**Operator:** DCWF 672 AI Test & Evaluation Specialist
**Outfit:** `cat-tabby-lane-c-te` (T0247, T0188, S0081, K0009, K0005, K0006)
**Date:** 2026-06-09
**Routing observed:** Mullvad WireGuard `us-mia-wg-102`, public exit `146.70.187.101` (M247, Miami FL)
**Script:** `mitm-shape-probe.py`
**Raw results:** `mitm-shape-probe-results.json`

---

## (a) Sandbox-MITM shape table — 5 unrelated public controls

Probe = `GET <path> HTTP/1.1` with `Host:` matching the SNI. Shape digest = first 16 hex of SHA256 over `status || sorted-header-keys || body_len/64 || first-32-body-bytes`.

### Probe 1: `GET /`

| Control       | Status | Hdr keys | Body len | Shape digest        |
|---------------|--------|----------|----------|---------------------|
| google-dns    | 200    | 8        | 1393     | `ab4d4da731f6ddb3`  |
| cloudflare    | 200    | 8        | 56614    | `100c671d3aed7793`  |
| aws-s3        | 307    | 7        | 0        | `12572f494449a48a`  |
| github-api    | 200    | 8        | 2262     | `be28dae60ad4deb8`  |
| example-org   | 200    | 8        | 571      | `bc16c363c68e92e8`  |

**Unique shapes: 5 / 5.**

### Probe 2: `GET /api/tags` (the contaminated endpoint)

| Control       | Status | Hdr keys | Body len | Shape digest        |
|---------------|--------|----------|----------|---------------------|
| google-dns    | 404    | 8        | 1569     | `d498881c767dc576`  |
| cloudflare    | 404    | 8        | 1285     | `30b81467d969513b`  |
| aws-s3        | 301    | 8        | 465      | `82288c6985944958`  |
| github-api    | 404    | 8        | 106      | `d2a310cba255ff57`  |
| example-org   | 404    | 8        | 571      | `8697ec1faef1d8fa`  |

**Unique shapes: 5 / 5.** Even though four hosts agree on status `404`, the body sizes and first-32-byte payloads diverge as authentic per-origin error pages would. No collapse.

---

## (b) Decision rule outcome

Threshold per recongraph / VisorGraph: collapse to ≤2 distinct digests across 5 unrelated controls = COMPROMISED observation position. We observe **5 / 5 distinct on `/`** and **5 / 5 distinct on `/api/tags`**.

**Verdict: CLEAN.** The current routing (Mullvad us-mia-wg-102) is not rewriting HTTP responses end-to-end. L7 conclusions taken through this exit are not being shape-collapsed by a transparent interceptor.

Note: a clean MITM check rules out *shape-rewriting* contamination on the wire. It does not rule out per-host upstream weirdness (caching, load balancer differences, Shodan-cache lag, or the suspect cohort being a coordinated honeypot fleet that happens to return Ollama-shaped JSON). Those are out of scope for this probe and live in Lane A / Lane B follow-ups.

---

## (c) Suspect-host instability test — `3.137.167.45:11434/api/tags` × 3, 15 s gaps

| Probe | Status | Body len | Shape digest        | First 32 bytes               |
|-------|--------|----------|---------------------|------------------------------|
| 0     | 200    | 1327     | `8feae3db493e5dba`  | `{"models": [{"name": "qwen2.5:1.` |
| 1     | 200    | 1327     | `8feae3db493e5dba`  | `{"models": [{"name": "qwen2.5:1.` |
| 2     | 200    | 1327     | `8feae3db493e5dba`  | `{"models": [{"name": "qwen2.5:1.` |

**Unique shapes: 1 / 3.** Byte-for-byte stable across 30 s. No cache layer / LB jitter detected at this specific host. Body starts with `{"models": [{"name": "qwen2.5:1.` — this is not Cat-Tabby and not Devstral. The host is a real Ollama serving qwen2.5, and it consistently returns the same payload.

---

## (d) Trust recommendation for Lane A's paired-probe corpus

**Trustable, with the following caveats:**

1. **Wire-level integrity confirmed.** No transparent MITM is collapsing response shapes through the Mullvad exit. Lane A's HTTP status, body length, and JSON content captured through this same routing can be treated as authentic origin responses.
2. **The Stage 0 contamination class is NOT exit-rewriting.** The original "1,217 code-loaded / 66 honeypot" anomaly therefore needs a different root cause — most likely (a) Shodan cache staleness, (b) a coordinated honeypot fleet returning Ollama-shaped JSON with planted model names (`codellama:13b` etc.), or (c) an upstream CDN/WAF in front of a real-host subset returning identity responses. None of those require us to downgrade Lane A's *direct* re-probe data.
3. **Lane A's filtered cohort can move to verification.** Per methodology §1, treat each suspect-host re-probe as a fresh candidate, not a finding. The 200-with-data rule still applies. Shape-stability over a 30 s window is a necessary but not sufficient condition for "real host"; it must be paired with model-list semantic plausibility and aimap deep-enum corroboration before promotion.
4. **Recommended downgrades:** Any Stage 0 conclusion that was *only* a Shodan banner read (no direct fetch from this T&E session) stays at `OPAQUE` until re-probed live. The MITM check clears the wire; it does not retroactively bless cached banners.

---

## (e) Verification rung pair for Lane A's eventual filtered cohort

Per Insight #68 (Depth A/B × Breadth 0/1/2) — apply once Lane A's filtered cohort lands:

- **Inner (Depth):** **A** — direct fetch of `/api/tags` from this T&E station with shape-stable response over a 30 s pair-probe window AND a semantically valid Ollama model list (no fabricated names, no shape-collapse against the honeypot signature). Optional escalation to **B** (model-completion smoke) is OUT OF SCOPE for restraint reasons — names are the finding.
- **Outer (Breadth):** **1** — per-host claim, never population-wide. Each surviving IP carries its own evidence; no cohort-level "all 1,217 are real" claim is permitted. **0** (single anchor) is too thin for a public artifact; **2** (cross-corpus replication) is the right escalation only if a second collection (Censys CT-log cross-pop, or a non-Mullvad routing snapshot) confirms the host independently.

**Final rung pair for Lane A's promoted findings: A / 1.**
NuClide restraint stance preserved: high-depth, narrow-breadth, by choice.

---

## Audit trail (T0188)

- VPN state at probe time: Mullvad WireGuard active, exit `us-mia-wg-102`, public IP `146.70.187.101`.
- VPN-off comparison run: NOT performed. Rationale: VPN-on shapes already passed the 5-distinct threshold, so the decision rule terminates CLEAN without needing the differential. A VPN-off differential is the *escalation* path when VPN-on collapses to ≤2 shapes; it is unnecessary when VPN-on is already clean. Logged as a deliberate non-run, not a skip.
- Restraint preserved: no POST, no auth attempts, no completions; all probes were `GET` against public control endpoints and a single read-only `/api/tags` against the suspect host already in the OSINT corpus.

— Lane C / DCWF 672 T&E, 2026-06-09
