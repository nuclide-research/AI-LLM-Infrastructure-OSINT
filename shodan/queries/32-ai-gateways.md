# Cat-32: AI Gateways
_NuClide Research · survey initiated 2026-06-01_

Platforms: Portkey, Kong AI Gateway, Bifrost (maximhq), one-api, new-api, sub2api, TensorZero, Helicone, Envoy AI Gateway

Threat model: gateway tier aggregates all upstream provider API keys + logs all traffic. Unauth access = master-key compromise across the operator's entire LLM portfolio.

Reference intel: `data/platform-intel/ai-gateways-osint-2026-06-01.md`
Favicon hashes: `shodan/favicon-hashes.md` (AI Gateways section)
CT catalog: `shodan/ct-log-catalog.md` (AI Gateways section)

---

## Dork Catalog

| # | Dork | Platform | Signal type | Est. pop | Run date | Hit count | Status |
|---|---|---|---|---|---|---|---|
| 1 | `"AI Gateway says hey"` | Portkey | Body string (health endpoint) | Low | 2026-06-01 | 0 | ✓ zero -- pure API proxy, not publicly indexed |
| 2 | `"Welcome to kong" port:8001` | Kong Admin API | Title/body | High | 2026-06-01 | 0 | ✓ zero -- body string mismatch; try `product:kong port:8001` |
| 3 | `http.html:"available_on_server" http.html:"ai-proxy" port:8001` | Kong AI plugin | Body (AI plugin enabled) | High | 2026-06-01 | 277 | ✓ 100 IPs harvested |
| 4 | `http.title:"Bifrost AI Gateway"` | Bifrost | Title | Medium | 2026-06-01 | 0 | ✓ zero -- title differs in deployments; use dork 5+6 |
| 5 | `http.html:"getbifrost.ai" port:8080` | Bifrost | Body (footer/link) | Medium | 2026-06-01 | 82 | ✓ 82 IPs harvested |
| 6 | `http.favicon.hash:1651823509` | Bifrost | Favicon | Medium | 2026-06-01 | 237 | ✓ 97 IPs harvested |
| 7 | `http.title:"One API" port:3000` | one-api | Title + port | High | 2026-06-01 | 2,449 | ✓ 100 IPs harvested (page 1/25) |
| 8 | `http.title:"New API" port:3000` | new-api | Title + port | **CRITICAL** | 2026-06-01 | 13,456 | ✓ 114 IPs harvested (page 1/135) -- LARGEST POP |
| 9 | `http.favicon.hash:1318451613` | one-api | Favicon | High | 2026-06-01 | 274 | ✓ 95 IPs harvested |
| 10 | `http.favicon.hash:-1643864359` | new-api | Favicon | High | 2026-06-01 | 251 | ✓ 99 IPs harvested |
| 11 | `port:8585 http.html:"helicone"` | Helicone (worker) | Port + body | Low | 2026-06-01 | 0 | ✓ zero -- tool in maintenance mode |
| 12 | `http.favicon.hash:-794809853` | Helicone (web UI) | Favicon | Low | 2026-06-01 | 2 | ✓ 2 IPs harvested |
| 13 | `port:9901 http.html:"config_dump"` | Envoy AI GW admin | Port + body | High | 2026-06-01 | 89 | ✓ 87 IPs harvested -- HIGH PRIORITY |
| 14 | `http.title:"TensorZero"` | TensorZero | Title | Low | 2026-06-01 | 1 | ✓ 1 IP harvested |
| 15 | `http.favicon.hash:-112038367` | Kong Manager | Favicon (UI) | High | 2026-06-01 | 268 | ✓ 97 IPs harvested |

---

## Execution Notes

**JAXEN run order:** fire all 15 via Playwright/Shodan. Log hit count in Hit count column above. Zero = result (log in query-log.md).

**FP mitigation:**
- Dorks 7+8 (title + port) reduce FP vs title-only (port 3000 narrows to expected deployment port)
- Dorks 2+3 are complementary: dork 2 catches all Kong, dork 3 specifically confirms AI plugin is active
- Dorks 6+4+5 are triple-redundant for Bifrost (favicon OR title OR footer link)

**Deduplication:** one-api and new-api are forks with distinct favicon hashes; if an IP hits both dork 9 and dork 10, investigate whether both are deployed or it's a hash collision (unlikely -- verified distinct in favicon-hashes.md).

**Verification priority after harvest:**
1. Kong :8001 (CVE-2020-11710, CVSS 9.8 -- highest severity)
2. one-api / new-api (default creds; active exploitation documented)
3. Envoy :9901 (config_dump = plaintext credential exposure)
4. Bifrost (root path bypass)
5. Portkey (SSRF only if version < v1.14.0)

---

## Verification Primitives (post-harvest, passive-first)

```bash
# Kong Admin API -- read-only version check
curl -s http://<IP>:8001/ | jq '{version:.version,tagline:.tagline}'
# Confirmed unauth if: tagline = "Welcome to kong"
# STOP here -- do not POST, do not create resources

# one-api / new-api -- title fingerprint only (no login attempt)
curl -s http://<IP>:3000/ | grep -o '<title>[^<]*'
# Confirmed if: "One API" or "New API"
# Default cred check: log as "default cred state unverified" unless explicitly tasked

# Envoy admin -- config dump (read-only, but contains credentials)
curl -s http://<IP>:9901/config_dump | python3 -c "
import sys, json
cfg = json.load(sys.stdin)
# grep for auth patterns -- enumerate metadata, do not exfiltrate
print('config_dump accessible: YES')
print('clusters:', len(cfg.get('configs',[])))
"
# Log: "config_dump accessible, N clusters enumerated" -- do not log credential values

# Bifrost -- root bypass check
curl -s -o /dev/null -w "%{http_code}" http://<IP>:8080/
# Confirmed bypass if: 200 (not 401/403)

# Portkey -- health check
curl -s http://<IP>:8787/ | grep -c "AI Gateway says hey"
# Confirmed if: 1
```

---

## aimap Fingerprints Needed

New fingerprints to add before Stage 1 scan:

| Platform | Port | Fingerprint signal | Status |
|---|---|---|---|
| Portkey | 8787 | Body: `"AI Gateway says hey"` | Needs aimap spec |
| Kong Admin API | 8001 | Body: `"Welcome to kong"` + JSON version field | Needs aimap spec |
| Bifrost | 8080 | Title: `"Bifrost AI Gateway"` OR favicon hash `1651823509` | Needs aimap spec |
| one-api | 3000 | Title: `"One API"` (distinguish from new-api via favicon) | Needs aimap spec |
| new-api | 3000 | Title: `"New API"` + favicon hash `-1643864359` | Needs aimap spec |
| Envoy AI GW | 9901 | Path: `/config_dump` accessible + JSON response | Needs aimap spec |

---

## Query Log Reference

All executed dorks logged to: `shodan/query-log.md` (format: date, dork, hit count)

## Dorks Added Post-Reference-Doc Review (2026-06-01)

| # | Dork | Platform | Signal type | Count | Run date | IPs | Status |
|---|---|---|---|---|---|---|---|
| 16 | `"Server: kong"` | Kong (all) | Server header | 70,924 | 2026-06-01 | pending harvest | ✓ most durable Kong signal; entire install base |
| 17 | `port:8001 http.html:"Welcome to Kong"` | Kong Admin API | Body (capital K) | 600 | 2026-06-01 | pending harvest | ✓ FIXED from dork 2 (lowercase k bug) |
| 18 | `http.title:"LiteLLM"` | LiteLLM | Title | 65,976 | 2026-06-01 | pending harvest | ✓ MISSED PLATFORM -- added from reference doc |
| 19 | `port:4000 http.html:"litellm"` | LiteLLM | Port + body | 2,290 | 2026-06-01 | pending harvest | ✓ subset of dork 18 |

**LiteLLM scope note:** LiteLLM is an LLM gateway/proxy (proxy for 100+ LLMs, admin UI, virtual keys). Auth enforced on newer versions but older deployments expose `/v1/models`, `/health`, and admin UI unauthenticated. 65,976 is a large population -- needs aimap fingerprint + verification pass.
