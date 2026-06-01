# Favicon Hash Catalog

_NuClide Research · Shodan-compatible MurmurHash3 (32-bit signed) of RFC-2045 base64-encoded favicon bytes._

Algorithm: `mmh3.hash(codecs.encode(favicon_bytes, 'base64'))` — newline every 76 chars + trailing newline. Negative values are valid.
Censys uses MD5 of raw bytes (no base64).

Compute new hashes:
```bash
python3 -c "
import urllib.request, codecs, struct, sys

def murmur3(data):
    if isinstance(data, str): data = data.encode()
    n, h = len(data)//4, 0
    c1, c2 = 0xcc9e2d51, 0x1b873593
    for i in range(n):
        k = struct.unpack_from('<I', data, i*4)[0]
        k = ((k*c1)&0xFFFFFFFF); k = ((k<<15)|(k>>17))&0xFFFFFFFF; k = (k*c2)&0xFFFFFFFF
        h ^= k; h = ((h<<13)|(h>>19))&0xFFFFFFFF; h = (h*5+0xe6546b64)&0xFFFFFFFF
    t = data[n*4:]; k = 0
    if len(t)>=3: k^=t[2]<<16
    if len(t)>=2: k^=t[1]<<8
    if len(t)>=1: k^=t[0]; k=(k*c1)&0xFFFFFFFF; k=((k<<15)|(k>>17))&0xFFFFFFFF; k=(k*c2)&0xFFFFFFFF; h^=k
    h^=len(data); h^=h>>16; h=(h*0x85ebca6b)&0xFFFFFFFF; h^=h>>13; h=(h*0xc2b2ae35)&0xFFFFFFFF; h^=h>>16
    return h-2**32 if h>=2**31 else h
url=sys.argv[1]; d=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})).read()
print(murmur3(codecs.encode(d,'base64')))
" <favicon_url>
```

---

## AI Gateways (surveyed 2026-06-01)

| Platform | Hash | Port | Dork | Source | Notes |
|---|---|---|---|---|---|
| Bifrost (maximhq/bifrost) | `1651823509` | 8080 | `http.favicon.hash:1651823509` | `ui/public/favicon.ico` | 163,670 bytes (multi-res ICO bundle) |
| one-api (songquanpeng/one-api) | `1318451613` | 3000 | `http.favicon.hash:1318451613` | `web/default/public/favicon.ico` | 4,286 bytes |
| new-api (QuantumNous/new-api) | `-1643864359` | 3000 | `http.favicon.hash:-1643864359` | `web/default/public/favicon.ico` | 15,406 bytes; distinct from one-api |
| Kong Manager | `-112038367` | 8002 | `http.favicon.hash:-112038367` | `public/favicon.ico` (kong-manager repo) | Admin UI at :8002; not the Admin API at :8001 |
| Helicone (self-hosted) | `-794809853` | 8585/3000 | `http.favicon.hash:-794809853` | `web/public/favicon.ico` | 187,078 bytes; maintenance mode but instances persist |
| Portkey | N/A | 8787 | N/A | No favicon in repo | Pure API proxy, no web UI; fingerprint via `"AI Gateway says hey"` body |
| TensorZero | `1457979471` (⚠) | 3000 | unreliable | SVG only (`favicon.svg`); Shodan crawls `.ico` → 404 | Don't use |

---

## LLM Orchestration / Dashboards

| Platform | Hash | Port | Dork | Source | Notes |
|---|---|---|---|---|---|
| _Add as discovered_ | | | | | |

---

## Vector Databases

| Platform | Hash | Port | Dork | Source | Notes |
|---|---|---|---|---|---|
| _Add as discovered_ | | | | | |

---

## Model Serving / Inference

| Platform | Hash | Port | Dork | Source | Notes |
|---|---|---|---|---|---|
| _Add as discovered_ | | | | | |

---

## Notes

- **Hash collision check:** one-api and new-api hashes are distinct — no FP risk between forks.
- **Negative hashes are valid** Shodan values (`-1643864359` is correct syntax in the filter).
- **Org-wide fingerprinting risk:** a custom favicon reused across all assets becomes a unique org fingerprint — worse than a default for stealth. Per-host variation or no favicon (`return 204`) is the clean defense.
- **CDN de-anonymization:** favicon hash dorks frequently expose origin IPs behind Cloudflare.
- **FOFA equivalent:** `icon_hash="<int>"` — same MurmurHash3 value.
- **ZoomEye equivalent:** `iconhash:"<int>"`.
- **Censys:** MD5 of raw bytes (no base64 step) — different values, different filter.
