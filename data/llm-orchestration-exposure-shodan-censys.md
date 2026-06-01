# Defending LLM Orchestration Against Internet Scanners
### Shodan / Censys / FOFA Exposure Management — A Companion Guide (2026)

> Companion to the hardening checklist. This doc is about the step *before* exploitation: **discovery**. Scanners index every internet-facing service continuously; attackers query them, match a fingerprint to a known CVE, and fire a public PoC — often within days. The goal here is to make your orchestrator **undiscoverable**, because the most reliable defense against mass exploitation is simply not being in the search results.

---

## The reality: discovery is automated, fast, and auth often doesn't save you

The Langflow `CVE-2025-3248` campaign is the textbook example of the full kill chain:

- **Discovery:** attackers first gathered IPs and ports of publicly exposed Langflow servers **using Shodan or FOFA**, then ran a public GitHub PoC to get a remote shell, then deployed the **Flodrix botnet** (DDoS + data exfiltration, with self-deletion and string obfuscation for stealth).
- **Scale of exposure:** Shodan showed ~1,050 exposed instances early on (later 1,600+); Censys counted ~466–470. The exposure was global — US, Germany, Singapore, India, China leading.
- **Speed:** SANS honeypots began seeing scans for the flaw **two days after the PoC was published**, some attempting to grab a password file. GreyNoise observed **361 malicious IPs** attempting exploitation. CISA added it to KEV with a federal patch deadline.
- **The brutal lesson:** researchers noted **most internet-exposed Langflow instances had authentication enabled — and it didn't help**, because the vulnerable endpoint sat *in front of* auth. Logging in is irrelevant when the bug is pre-auth.

Takeaways that drive everything below: **(1)** exposure alone is the risk, independent of how well you think the app is locked down; **(2)** time-to-exploit after disclosure is measured in days, not weeks; **(3)** "we have a login page" is not an exposure control.

---

## 1. How scanners actually find your orchestrator (the fingerprint vectors)

Shodan, Censys, FOFA, ZoomEye, and BinaryEdge continuously scan the whole IPv4 space and index far more than open ports. Each of these is a way you leak:

| Vector | What leaks | Attacker dork (illustrative) |
|---|---|---|
| **Open port + banner** | Service identity from the response banner/headers | `port:7860`, `port:3000`, `port:11434` (Ollama) |
| **HTTP title** | The product name in `<title>` | `title:"Langflow"`, `http.title:"Flowise"` |
| **Response body** | Unique strings, JS, tracking IDs, API paths in the page | `body:"langflow"`, `html:"/api/v1/validate/code"` |
| **Favicon hash** | A product's icon is a near-unique fingerprint across *all* its instances | `http.favicon.hash:<mmh3>` (Shodan/ZoomEye = MurmurHash3; Censys = MD5) |
| **TLS/SSL certificate** | Hostnames in CN/SAN, issuer, org — Censys specializes here | `cert:"yourcompany.com"`, search by SAN |
| **Certificate Transparency logs** | *Every* public-CA cert is published — leaks hostnames before any scan | `crt.sh`, Censys cert search |
| **DNS records** | Predictable subdomains (`langflow.company.com`) | passive DNS, Subfinder, DNSDumpster |

Two of these deserve emphasis because teams consistently overlook them:

**Favicon hashing.** If you serve the product's default favicon, your instance matches a *known* hash that maps directly to the product (and often a CVE). A single `http.favicon.hash` query returns every instance of that product on the internet — including ones hidden behind CDNs or on odd ports. The hash is computed from the favicon bytes (base64 → MurmurHash3 for Shodan), so anyone can generate it from a single known-good instance and find all the rest.

**Certificate Transparency.** The moment you request a public TLS cert (e.g., Let's Encrypt) for `langflow-internal.company.com`, that hostname is permanently published to CT logs and queryable via `crt.sh` or Censys — **even if you never created a public DNS record and never exposed the service to a port scan**. CT log mining of certificate SANs is a primary subdomain-enumeration technique (export SANs from your primary cert, grep for `dev`/`staging`/`internal`/`admin`).

---

## 2. The hierarchy of defenses (most → least effective)

Apply top-down. Tier 0 is the only thing that *defeats* scanners; everything below merely reduces or obscures.

### Tier 0 — Don't be on the public internet (the only real fix)
- [ ] **Put the orchestrator and all builder UIs behind a VPN or zero-trust access layer** (WireGuard/Tailscale, Cloudflare Access / Access-style identity-aware proxy, AWS PrivateLink, an SSH/bastion). No public listener = nothing for scanners to index.
- [ ] If it must be reachable, expose **only a hardened reverse proxy** with auth, never the app's native port.
- [ ] **Bind the app to `127.0.0.1` / private subnet, not `0.0.0.0`.** (Langflow's FastAPI/Gradio default binds to `0.0.0.0` on `7860`/`8501`; Flowise to `3000` — these are exactly the ports scanners enumerate.)
- [ ] Default-deny inbound at the security group / firewall; allowlist source IPs where the audience is fixed (offices, VPN egress).

### Tier 1 — Network-layer access control (if some public reach is unavoidable)
- [ ] IP allowlisting / geo-fencing at the WAF or load balancer.
- [ ] mTLS or client-cert auth at the proxy so even a discovered endpoint can't be probed without a client cert.
- [ ] Rate-limit and challenge (e.g., interactive challenge) unauthenticated probes; drop known-scanner traffic at the edge (note: scanner IP ranges rotate, so this thins noise but isn't a control).

### Tier 2 — Fingerprint reduction (shrink your signal once reachable)
- [ ] **Strip/anonymize server banners and headers** (`Server`, `X-Powered-By`, framework version strings) at the reverse proxy.
- [ ] **Change or remove the HTML `<title>`** so `title:"Langflow"`-style dorks miss you.
- [ ] **Replace or remove the default favicon** so your `http.favicon.hash` no longer matches the product's well-known hash. (Obscurity only — it breaks the favicon dork, not the exploit.)
- [ ] **Certificate hygiene:** prefer **wildcard certs** (`*.company.com`) so the specific internal hostname is not published to CT logs; keep purely internal services on a **private CA / internal PKI** so no public CT entry exists; never put descriptive internal hostnames (`admin`, `langflow`, `mcp`) in a public cert's SAN.
- [ ] **DNS hygiene:** no public DNS records for internal services; avoid predictable, product-revealing names.
- [ ] Move off default ports — `7860`/`3000`/`11434` etc. (cuts opportunistic, port-keyed scanning; trivially bypassed by full scans, so treat as noise-reduction only).
- [ ] Remove verbose error pages / stack traces / `/docs` Swagger UIs that confirm the framework and version.

### Tier 3 — Continuous self-monitoring & alerting (assume you'll slip)
- [ ] **Run the attacker's queries against your own footprint** on a schedule (see §4). Search by your **IP ranges, ASN, org name, certificate, and favicon hash**.
- [ ] Stand up **Shodan Monitor** and/or a **Censys ASM/Exposure-Management** watch on your IP ranges and domains; alert on any *new* exposed service or newly-opened port.
- [ ] Subscribe to CISA KEV and the relevant framework advisories (LangChain core, Langflow, Flowise, MCP) so you can correlate "new CVE" against "do we have an exposed instance" in minutes.
- [ ] Deploy honeypots/canaries on adjacent IPs to detect scanning/recon aimed at your space.

---

## 3. Common misconceptions (each one has burned somebody)

1. **"`robots.txt` will keep us out of Shodan/Censys."** It won't — internet scanners do not honor `robots.txt`. That file is for well-behaved search-engine crawlers, not port scanners.
2. **"We have a login page, so exposure is fine."** The Langflow campaign exploited a **pre-auth** endpoint while most instances *had* auth on. Auth doesn't protect a vulnerable unauthenticated route.
3. **"We're on a non-standard port, so nobody will find us."** Scanners sweep the full port range and fingerprint by banner/title/favicon regardless of port. Port-changing reduces opportunistic noise only.
4. **"It's an internal hostname with no public DNS, so it's hidden."** A public TLS cert publishes that hostname to CT logs the moment it's issued — independent of DNS and port scans.
5. **"Behind Cloudflare/a CDN = invisible."** A reused favicon hash, a leaked origin IP in DNS history, or a cert SAN frequently reveals the origin behind the CDN.
6. **"We patched, so exposure no longer matters."** Exposure is a standing liability — the *next* CVE drops against your already-indexed, already-known instance. Shrink the surface regardless of patch state.

---

## 4. Self-audit: find your own footprint before attackers do

Run these against **your own** assets only — this is exposure self-assessment, not targeting.

**Shodan (web UI or CLI):**
```
# Everything Shodan knows about your ranges / org
net:"203.0.113.0/24"
org:"Your Company, Inc."
ssl.cert.subject.cn:"company.com"

# Product fingerprints you should NOT see pointing at your IPs
http.title:"Langflow"   http.title:"Flowise"
product:"Ollama"   port:11434
http.favicon.hash:<your-instance-hash>
```

**Censys:**
```
ip: 203.0.113.0/24
services.tls.certificates.leaf_data.subject.common_name: "company.com"
services.http.response.html_title: "Langflow"
# Pull cert SANs and grep for dev/staging/internal/admin/mcp
```

**Certificate Transparency (passive, finds leaked hostnames):**
```
crt.sh  ->  %.company.com    (review every SAN; flag internal-looking names)
```

**Generate your own favicon hash** (to confirm whether the default product icon is exposing you), then search for that hash across Shodan/Censys/FOFA. If your hosts appear under the *product's* default hash, replace the favicon.

Action on findings: anything appearing that you didn't intend to expose goes to Tier 0 (pull it behind VPN/zero-trust) immediately, then rotate any credentials that endpoint could have leaked.

---

## 5. Exposure-management checklist (condensed)

- [ ] No orchestrator/builder UI on a public listener; VPN or zero-trust in front
- [ ] App bound to `127.0.0.1`/private, never `0.0.0.0`; default-deny firewall; source-IP allowlist where feasible
- [ ] Only a hardened reverse proxy is internet-facing (never the native app port)
- [ ] Server banners/headers/version strings stripped; HTML title changed; default favicon replaced/removed
- [ ] Wildcard certs (or private CA for internal); no descriptive internal hostnames in public cert SANs; CT logs reviewed
- [ ] No public DNS for internal services; no product-revealing subdomain names
- [ ] Swagger/`/docs`, verbose errors, and stack traces disabled in prod
- [ ] Scheduled self-scan (Shodan/Censys/CT) of IP ranges, ASN, org, cert, favicon
- [ ] Shodan Monitor / Censys ASM alerting on new exposures and open ports
- [ ] CISA KEV + framework advisory feeds wired to an "do we have an exposed instance?" triage path
- [ ] Honeypots/canaries on adjacent IPs for recon detection

---

## Appendix — Detection & monitoring (the angle from the hardening doc)

Pair exposure management with runtime detection so a discovered-and-probed instance trips an alarm. High-signal things to alert on, mapped to attack class:

- **Recon/scanning:** bursts of unauthenticated requests to framework-specific paths (`/api/v1/validate/code`, `/api/v1/build_public_tmp/*`, `mcpServerConfig` params, `/docs`); requests from known scanner ASNs; attempts to fetch credential/`.env` files.
- **Exploitation (RCE):** the code-validation/build endpoints receiving POSTs with Python/JS payloads; child-process spawns from the app user; new outbound connections from the orchestrator host to unfamiliar IPs (botnet C2, e.g., Flodrix-style TCP beacons); unexpected downloaders (`curl`/`wget`/`npx` spawning shells).
- **Prompt-injection / agent abuse:** tool calls that don't match the task; egress attempts to `169.254.169.254` or RFC1918; serialization/deserialization of model-output fields (`additional_kwargs`, `response_metadata`) in streaming/logging paths; sudden privilege or scope changes mid-session.
- **Exfiltration:** outbound volume spikes; secrets/PII patterns in responses or logs; DNS-tunneling-shaped queries.
- **Cost/DoS:** per-key token or spend anomalies; agent loops hitting iteration caps; latency-stacked failover retries.

Feed all of it to OTel → a tamper-resistant store, and treat **any** tool call without an attributable identity as an incident.

*Compiled June 2026. Exposure counts and CVE timelines cited reflect reporting at disclosure; re-check live scanner data and advisories before relying on them.*
