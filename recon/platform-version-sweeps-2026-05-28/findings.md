# Platform Version Sweeps — n8n / Flowise / ChromaDB — 2026-05-28

Three concurrent CVE-targeted version surveys. Dork: Shodan `product:` filter for each platform.
Probe: async HTTP to version endpoints, 80-thread concurrency, 8s timeout.

---

## n8n — CVE-2025-68613 (CVSS 9.9, Expression Injection RCE)

**Affected:** v0.211.0 through v1.120.3  
**Fixed:** v1.120.4, v1.121.1, v1.122.0+  
**Exploitation:** Requires authenticated workflow creation/editing — no admin required

| Dork | Total |
|------|-------|
| `product:"n8n"` | 162,559 |

**Sample:** 95 hosts probed (first 20 Shodan pages)  
**Versioned:** 3 | **Unauth (settings endpoint):** 81

| Target | Version | CVE-2025-68613 | Auth |
|--------|---------|----------------|------|
| http://142.93.0.224:5678 | 0.228.2 | VULNERABLE | unauth |
| http://34.19.69.232:5678 | 1.59.4 | VULNERABLE | unauth |
| http://34.22.230.197:5678 | 1.109.2 | VULNERABLE | unauth |

All 3 versioned hosts fall within the 0.211.0–1.120.3 affected range.

**Note on auth state:** `unauth` here means `/rest/settings` returned data without a session cookie.
n8n instances with open registration or shared-team logins extend exploitation to any account holder.
162K exposed population; at 103K vulnerable per Censys (December 2025 scan), the unpatched tail
remains large.

---

## Flowise — CVE-2024-36420 (Auth Bypass < v1.8.2)

**Affected:** Flowise < v1.8.2  
**Fixed:** v1.8.2+

| Dork | Total |
|------|-------|
| `product:"Flowise"` | 512 |

**Probed:** 187 (Shodan pages 1–20, deduped)  
**Versioned:** 67 | **Vulnerable (<1.8.2):** 5 | **Patched (>=1.8.2):** 49 | **Unauth (any):** 108

### Vulnerable Hosts (5)

| Target | Version | Auth |
|--------|---------|------|
| http://132.220.245.91:3000 | 1.4.11 | unauth |
| http://146.190.128.73:3000 | 1.4.3 | unauth |
| http://167.71.251.208:3000 | 1.4.9 | unauth |
| http://209.145.54.1:3000 | 1.4.2 | unauth |
| http://39.105.152.205:3000 | 1.6.4 | unauth |

All 5 are unauthenticated AND vulnerable. CVE-2024-36420 is an auth bypass — on unauth instances
the auth layer is absent, so the bypass is moot and full API access is already granted.

**Version distribution (top):** v2.2.7-patch.1 (12), v2.2.5 (9), v2.2.4 (8) — majority patched.
Vulnerable hosts are legacy 1.4.x/1.6.x deployments left unattended.

---

## ChromaDB — Unauth Population Survey

**No CVE with a fixed version in scope.** ChromaDB lacks built-in auth in the 0.x series;
unauth access is the design default. All 35 versioned hosts have the DB fully open.

| Dork | Total |
|------|-------|
| `product:"Chroma"` | 1,766 |

**Probed:** 198 | **Versioned:** 35 | **Unauth:** 35 (100% of versioned)

**Version distribution:**

| Version | Count |
|---------|-------|
| 0.5.23 | 11 |
| 0.6.3 | 8 |
| 0.5.20 | 3 |
| 0.5.18 | 3 |
| 0.5.16 | 2 |
| 0.5.5 | 2 |
| 0.5.15 | 2 |
| 0.6.1 | 1 |
| 0.6.2 | 1 |
| 0.5.21 | 1 |
| 1.4.0 | 1 |

The 0.5.x population represents instances that predates ChromaDB's optional auth feature
(introduced in 0.6.x via `chroma_server_authn_provider`). Even in 0.6.x auth is opt-in;
none of these hosts have it configured.

One host runs v1.4.0 (`http://57.129.82.135:8001`) — the newest in the sample and
still unauthenticated.

Full host list: `chroma-versions.csv`

---

## Data Files

| File | Contents |
|------|----------|
| `n8n-versions.csv` | 95 hosts, version + auth state |
| `flowise-versions.csv` | 187 hosts, version + auth + CVE-2024-36420 classification |
| `chroma-versions.csv` | 198 hosts, version + auth state |
