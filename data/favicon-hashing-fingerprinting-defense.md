# Favicon Hashing: Fingerprinting, Exposure & Defense
### A Standalone Technical Guide (2026)

> What favicon hashing is, exactly how Shodan/Censys/FOFA compute it, why it's one of the most powerful and overlooked ways your infrastructure is discovered, and how to defend against it — including the common "fix" that makes things worse. Examples are defensive; run the queries against your own assets only.

---

## TL;DR

A favicon is the little icon in a browser tab. Internet scanners hash it and index the hash, so a service can be found by its icon alone. Because a favicon is **static and shared across every instance of a product or across all of an organization's assets**, one hash → one search → every matching host on the internet, including instances on odd ports, behind CDNs, or that you forgot you exposed. For self-hosted AI tools (Langflow, Flowise, Ollama dashboards, etc.) that ship a default favicon, this means a single dork can enumerate every exposed instance of the product — the reconnaissance step that precedes mass exploitation. The clean defense is to **remove the favicon**, not to add a custom one (which is double-edged — see §6). Ultimately it's obscurity, not security: the real control is not being internet-exposed.

---

## 1. What it is

Favicon hashing fingerprints a web service by computing a hash of the favicon it serves (historically `/favicon.ico`, but it can live anywhere the HTML `<link rel="icon">` points). Shodan pioneered the technique roughly a decade ago for two purposes: spotting **phishing sites** that reuse a brand's icon, and **identifying assets** that belong together. Scanners store the hash and expose a search filter, turning "what does this icon look like?" into "show me everyone on the internet using this exact icon."

The favicon is a near-perfect fingerprint precisely because almost nobody changes it: it's static, it's reused across subdomains and deployments, and product vendors ship the same default icon to every user.

---

## 2. How the hash is computed (precisely)

Different engines use different algorithms — getting this exactly right matters if you reproduce it:

| Engine | Algorithm | Input | Search filter |
|---|---|---|---|
| **Shodan** | MurmurHash3 (32-bit, **signed**) | favicon bytes, **base64-encoded (RFC 2045)** | `http.favicon.hash:<int>` |
| **ZoomEye** | MurmurHash3 | same as Shodan | `iconhash:"<int>"` |
| **FOFA** | MurmurHash3 | same | `icon_hash="<int>"` |
| **Censys** | **MD5** | raw favicon bytes | favicon/cert search operator |

**The Shodan pipeline, step by step:**
1. Download the favicon bytes.
2. **Base64-encode them per RFC 2045** — meaning a newline (`\n`) inserted every 76 characters, plus a trailing newline.
3. Compute **MurmurHash3** of that base64 string.
4. The result is a 32-bit **signed** integer (it can be negative, e.g. `-335242539`).

Reproducing it in Python (this matches Shodan exactly):

```python
import mmh3, requests, codecs
r = requests.get("https://app.example.com/favicon.ico")
favicon = codecs.encode(r.content, "base64")   # RFC 2045: \n every 76 chars + trailing \n
print(mmh3.hash(favicon))
# Verified reference: Wikipedia's favicon -> 857403617
```

One-liner:
```bash
python3 -c "import mmh3,requests,codecs,sys; print(mmh3.hash(codecs.encode(requests.get(sys.argv[1]).content,'base64')))" "https://example.com/favicon.ico"
```

> **Note:** to use Shodan's favicon filter you must be logged in (a membership feature).

---

## 3. The cross-language gotcha (why people get the wrong hash)

In Python, `codecs.encode(data, 'base64')` and `base64.encodebytes()` **insert the RFC-2045 newlines automatically**, so they match Shodan. But `base64.b64encode()` does **not** add newlines — and most languages' default base64 does the same. If you skip the line breaks, MurmurHash3 returns a completely different value and your searches silently miss.

To match Shodan in any language, base64-encode, then insert `\n` every 76 characters and append a trailing `\n`, before hashing:

```python
import base64, re, mmh3
with open("favicon.ico", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
    # REQUIRED to match Shodan: newline every 76 chars (and at the end)
    rfc2045 = re.sub("(.{76}|$)", "\\1\n", b64, 0, re.DOTALL)
    print(mmh3.hash(rfc2045))
```

Censys is simpler: it's just the MD5 of the raw favicon bytes (no base64, no newlines).

---

## 4. Why it's so powerful (the threat model)

A single favicon hash unlocks several recon moves:

- **Product fingerprinting → CVE matching.** Default vendor favicons map to a product (and often a known vulnerability). Public databases — a "Favicon Map," the OWASP Favicon Database, FavFreak's known-hash list — translate a hash into "this is product X." Searching that hash yields every exposed instance, which an attacker cross-references against current CVEs.
- **CDN / origin de-anonymization.** Favicon dorks reveal other servers using the same icon — frequently the **origin server behind Cloudflare** or another CDN. Some of those origins aren't protected, so the icon leaks the real IP that the CDN was meant to hide.
- **Organization-wide asset correlation.** Because companies reuse one icon across assets, its hash becomes a signature that stitches together subdomains, IPs, and shadow IT into a single inventory — including services you didn't know were exposed.
- **C2 / phishing infrastructure tracking.** Offensive tooling (Cobalt Strike, Metasploit, phishing kits) ships default favicons, so their hashes expose reused panels and cloned-brand phishing pages — the same property defenders use to hunt them.

The unifying point: **the favicon clusters things that belong together**, whether that's "all instances of a vulnerable product" or "all of one org's infrastructure."

---

## 5. The specific risk to self-hosted AI orchestration tools

Self-hosted LLM tooling is a textbook target because the defaults line up perfectly for favicon discovery:

- Visual builders and dashboards (Langflow, Flowise, and similar) ship a recognizable default favicon.
- They commonly bind to `0.0.0.0` on well-known ports.
- Several have had **unauthenticated, actively-exploited RCE** vulnerabilities.

So an attacker doesn't even need to port-scan broadly: one `http.favicon.hash:<product_hash>` query returns the global population of exposed instances of that product, which they then probe for the vulnerable version/endpoint. Favicon hashing is the cheap, automated front end of the mass-exploitation pipeline that hit tools like Langflow.

---

## 6. Defending against it — ranked, with the trap called out

**The trap:** the obvious move — "replace the default favicon with our own custom logo" — is **double-edged**. A unique custom favicon *does* break the "find all of product X" dork. But because you'd reuse that same custom icon across your estate, it becomes a **unique organization-wide fingerprint**: now a single hash maps your *entire* footprint and de-anonymizes your origins. For stealth, that's worse than the default.

Ranked by how much they actually reduce your signal:

1. **Remove the favicon entirely.** Return `204`/`404`, or don't serve one. If a host has no favicon, scanners record no favicon hash for it, so it cannot be found via this vector at all. Cleanest option when the goal is to not be discovered.
   ```nginx
   # at the internet-facing reverse proxy
   location = /favicon.ico { return 204; }
   ```
2. **Per-host variation.** Serve a slightly different icon per instance (browsers ignore trailing bytes, so appending random bytes changes the hash) so your instances don't cluster under one hash. Defeats correlation; more to manage.
3. **Do not deploy a single unique custom favicon across the estate** unless your goal is brand/phishing protection (where being findable by your icon is *desirable*) rather than stealth.

Supporting controls (favicon defense is only one layer):
- Strip server banners/headers and the HTML `<title>` too, or attackers just pivot to `http.title:` / `body:` / cert dorks.
- Keep internal hostnames out of public certificates (wildcard or private CA), since cert SANs are an equally strong correlation vector.
- **Tier 0 remains the real fix:** put the service behind a VPN / zero-trust proxy with no public listener. Favicon hygiene removes you from the cheap automated dragnet; it does not stop a determined, targeted attacker.

> **Bottom line:** favicon hygiene is *obscurity, not security*. It defeats mass, favicon-keyed sweeps that hit product defaults — a meaningful reduction in opportunistic risk — but a determined adversary still finds you by other fingerprints. Treat it as defense-in-depth, never as the control.

---

## 7. Use it on yourself (defensive self-audit & brand protection)

The same technique is a strong blue-team tool:

- **Find your own exposed assets / shadow IT.** Compute the hash of your custom (or default) favicon and search it across Shodan, Censys, ZoomEye, and FOFA to surface forgotten instances and unmanaged services tied to your icon.
- **De-anonymize your own CDN gaps.** Searching your favicon hash will reveal any origin servers leaking behind your CDN — fix those before an attacker maps them.
- **Phishing / brand protection.** Searching your brand's favicon surfaces cloned phishing pages reusing it (the original Shodan use case). Triage by domain similarity, registration date, and hosting geography.

Self-audit queries (run against **your own** assets only):
```bash
# Compute your favicon hash (Shodan-compatible)
python3 -c "import mmh3,requests,codecs; print(mmh3.hash(codecs.encode(requests.get('https://app.example.com/favicon.ico').content,'base64')))"

# Search it
#   Shodan:   http.favicon.hash:<int>
#   ZoomEye:  iconhash:"<int>"
#   FOFA:     icon_hash="<int>"
#   Censys:   (MD5-based favicon/cert operator)

# Combine with other filters to find login panels / admin UIs you exposed
#   http.favicon.hash:<int> http.title:"admin"
#   http.favicon.hash:<int> 200
```

Tooling that automates the whole loop:
- **FavFreak** — extracts favicons, computes MurmurHash3 (Shodan/ZoomEye) *and* MD5 (Censys), and emits ready-to-run dorks across engines; multithreaded.
- **httpx** (`-favicon`) — probes hosts and grabs/hashes favicons at scale.
- **nuclei** favicon templates — match favicon hashes against a fingerprint database to flag known products/issues.

---

## 8. Common mistakes

1. **Replacing the default favicon with one unique custom icon for stealth** — creates an org-wide fingerprint; worse than the default for hiding.
2. **Assuming a CDN hides you** — a reused favicon hash frequently exposes the origin behind Cloudflare et al.
3. **Reproducing the hash without the RFC-2045 base64 newlines** (`b64encode` instead of `encodebytes`) — wrong hash, silent misses.
4. **Treating favicon removal as sufficient** — title/body/cert/port fingerprints still find you; it's one layer.
5. **Never auditing your own footprint** — attackers run your favicon hash; you should too.
6. **Forgetting the favicon can live anywhere** — a non-root `<link rel="icon">` path still gets fetched, hashed, and indexed.

---

## Quick reference

| Want to… | Do this |
|---|---|
| Not be found by favicon | Remove the favicon (`return 204`); don't serve one |
| Avoid org-wide correlation | No single unique custom icon across assets; per-host variation |
| Match Shodan's hash exactly | base64 with `\n` every 76 chars (`codecs.encode(...,'base64')`), then MurmurHash3 (signed 32-bit) |
| Match Censys | MD5 of raw favicon bytes |
| Audit your exposure | Compute your hash → search Shodan/ZoomEye/FOFA/Censys; use FavFreak/httpx |
| Actually be secure | Tier 0 — VPN/zero-trust, no public listener (favicon hygiene is obscurity only) |

*Compiled June 2026. The hashing algorithms are stable; tooling and fingerprint databases evolve — verify current behavior before relying on it.*
