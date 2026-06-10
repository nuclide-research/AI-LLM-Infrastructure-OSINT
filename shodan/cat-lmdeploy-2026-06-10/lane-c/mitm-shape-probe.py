#!/usr/bin/env python3
"""
Sandbox-MITM gate (Insight #96). Before any L7 conclusion in Lane C, hash response
shapes from 5 unrelated public HTTPS endpoints. If the digests collapse to ≤ 2
distinct values, the observation position is COMPROMISED (an intercepting
sandbox is rewriting bodies). Otherwise the wire is CLEAN and Lane C verifies.
"""
import hashlib
import ssl
import urllib.request
import urllib.error
import socket
import json
import datetime

TARGETS = [
    ("https://api.github.com/", "api.github.com"),
    ("https://www.cloudflare.com/", "www.cloudflare.com"),
    ("https://www.google.com/", "www.google.com"),
    ("https://www.amazon.com/", "www.amazon.com"),
    ("https://example.org/", "example.org"),
]

def shape_digest(url):
    """Return (status, body_len, sha256-of-first-2048, content_type) for the response."""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"User-Agent": "nuclide-mitm-probe/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as r:
            body = r.read(2048)
            return {
                "status": r.status,
                "content_type": r.headers.get("Content-Type", ""),
                "body_len_partial": len(body),
                "body_sha256_partial": hashlib.sha256(body).hexdigest(),
            }
    except urllib.error.HTTPError as e:
        body = (e.read(2048) if e.fp else b"")
        return {
            "status": e.code,
            "content_type": (e.headers.get("Content-Type", "") if e.headers else ""),
            "body_len_partial": len(body),
            "body_sha256_partial": hashlib.sha256(body).hexdigest(),
        }
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError) as e:
        return {"status": None, "err": str(e)}

def main():
    out = {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "targets": [],
        "verdict": None,
    }
    digests = []
    for url, host in TARGETS:
        r = shape_digest(url)
        r["target"] = host
        out["targets"].append(r)
        if r.get("body_sha256_partial"):
            digests.append(r["body_sha256_partial"])
        print(f"[mitm] {host}: status={r.get('status')} ct={r.get('content_type','')[:40]} len={r.get('body_len_partial')} sha256={(r.get('body_sha256_partial') or '')[:16]}")

    distinct = len(set(digests))
    print(f"\n[mitm] distinct response-shape digests: {distinct} of {len(TARGETS)}")
    if distinct <= 2 and len(digests) >= 3:
        out["verdict"] = "COMPROMISED — observation position rewriting bodies"
    elif distinct >= 4:
        out["verdict"] = "CLEAN — wire shape is distinct across 4+ unrelated endpoints"
    else:
        out["verdict"] = f"INCONCLUSIVE — only {distinct} distinct digests from {len(digests)} successful probes"
    out["distinct_digests"] = distinct
    out["successful_probes"] = len(digests)

    print(f"\n=== SANDBOX-MITM VERDICT: {out['verdict']} ===")
    with open("mitm-shape-probe.json", "w") as f:
        json.dump(out, f, indent=2)
    return out

if __name__ == "__main__":
    main()
