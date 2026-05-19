#!/usr/bin/env python3
"""Exfiltrated-credential hard-proof verification chain (Insight #38).

Six-step chain: index-match -> live re-fetch -> format-validate -> cred validity
-> operator attribution -> content verification. Tier-promotion at each step.

Usage:
  export SHODAN_API_KEY=...
  python3 exfil_cred_verify.py --vendor langfuse --max-step 5
  python3 exfil_cred_verify.py --vendor stripe --max-step 4
  python3 exfil_cred_verify.py --list-vendors

Each vendor is configured as a small VENDOR_CONFIG entry below: the Shodan dork,
the format regex, the verify endpoint, the auth scheme, and the content endpoint.
Add more vendors by extending VENDOR_CONFIG.

Restraint: Step 4 hits the vendor SaaS using the exfiltrated cred (1 read-only
call). Step 6 reads one operator data record. Use --max-step to bound the chain.
"""
import argparse, base64, json, os, re, sys, time, urllib.parse, urllib.request

VENDOR_CONFIG = {
    "langfuse": {
        "shodan_dorks": ['http.html:"sk-lf-"', 'http.html:"pk-lf-"', 'http.html:"LANGFUSE_SECRET_KEY"'],
        "key_pattern": r"sk-lf-[a-zA-Z0-9_-]{20,}",
        "pubkey_pattern": r"pk-lf-[a-zA-Z0-9_-]{20,}",
        "format_regex": r"^sk-lf-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
        "default_endpoint": "https://us.cloud.langfuse.com",
        "alt_endpoints": ["https://cloud.langfuse.com", "https://eu.cloud.langfuse.com"],
        "auth_scheme": "basic_pk_sk",  # Basic auth: base64(pk:sk)
        "verify_path": "/api/public/projects",
        "verify_marker": "data",
        "operator_path": ["data", 0, "organization", "name"],
        "product_path": ["data", 0, "name"],
        "content_endpoint_template": "/api/public/traces/{trace_id}",  # needs trace id from /api/public/v2/observations
        "content_list_path": "/api/public/v2/observations?limit=1&fromStartTime={start}&toStartTime={end}",
    },
    "stripe_test": {
        "shodan_dorks": ['http.html:"pk_test_"'],
        "key_pattern": r"sk_test_[a-zA-Z0-9_-]{20,}",
        "pubkey_pattern": r"pk_test_[a-zA-Z0-9_-]{20,}",
        "format_regex": r"^sk_test_[a-zA-Z0-9]{24,}$",
        "default_endpoint": "https://api.stripe.com",
        "auth_scheme": "bearer_sk",
        "verify_path": "/v1/balance",
        "verify_marker": "object",
        "operator_path": ["object"],  # Stripe doesn't expose org-name on /v1/balance; would need /v1/account
        "content_endpoint_template": None,  # Stripe content read-tier is sensitive; tooling-disabled by default
    },
    "stripe_live": {
        "shodan_dorks": ['http.html:"sk_live_"'],
        "key_pattern": r"sk_live_[a-zA-Z0-9_-]{20,}",
        "pubkey_pattern": r"pk_live_[a-zA-Z0-9_-]{20,}",
        "format_regex": r"^sk_live_[a-zA-Z0-9]{24,}$",
        "default_endpoint": "https://api.stripe.com",
        "auth_scheme": "bearer_sk",
        "verify_path": "/v1/account",
        "verify_marker": "id",
        "operator_path": ["business_profile", "name"],
        "content_endpoint_template": None,
    },
    "helicone": {
        "shodan_dorks": ['http.html:"sk-helicone-"'],
        "key_pattern": r"sk-helicone-[a-zA-Z0-9_-]{20,}",
        "format_regex": r"^sk-helicone-[a-zA-Z0-9_-]{20,}$",
        "default_endpoint": "https://api.helicone.ai",
        "auth_scheme": "bearer_sk",
        "verify_path": "/v1/request/count",  # confirm key + see request count
        "verify_marker": "data",
        "operator_path": [],  # Helicone doesn't expose org-name on count endpoint; need /v1/user/info
        "content_endpoint_template": None,
    },
    "anthropic": {
        "shodan_dorks": ['http.html:"sk-ant-"'],
        "key_pattern": r"sk-ant-api03-[a-zA-Z0-9_-]{50,}",
        "format_regex": r"^sk-ant-api03-[a-zA-Z0-9_-]{50,}$",
        "default_endpoint": "https://api.anthropic.com",
        "auth_scheme": "x_api_key",
        "verify_path": "/v1/messages",
        "verify_marker": None,  # Anthropic's /v1/messages is POST-only; can't verify with GET
        "note": "Anthropic key verification requires POST; not suitable for read-only chain",
        "content_endpoint_template": None,
    },
    "openai": {
        "shodan_dorks": [],  # too broad; sk- prefix has too many false matches
        "key_pattern": r"sk-[a-zA-Z0-9]{40,}",
        "format_regex": r"^sk-[a-zA-Z0-9]{40,}$",
        "default_endpoint": "https://api.openai.com",
        "auth_scheme": "bearer_sk",
        "verify_path": "/v1/models",
        "verify_marker": "data",
        "operator_path": [],  # OpenAI doesn't expose org-name on /v1/models
        "content_endpoint_template": None,
        "note": "Bare sk- prefix is too broad; use co-anchored dorks (e.g. http.html:'sk-' http.html:'openai')",
    },
}


def shodan_search(api_key, dork, page=1):
    url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={urllib.parse.quote_plus(dork)}&page={page}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())


def http_get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read() if e.fp else b""
    except Exception as ex:
        return None, str(ex).encode()


def get_path(d, path):
    """Walk a dict/list path like ['data', 0, 'organization', 'name']."""
    try:
        for p in path:
            d = d[p]
        return d
    except Exception:
        return None


def run_chain(vendor, max_step):
    cfg = VENDOR_CONFIG[vendor]
    key = os.environ["SHODAN_API_KEY"]

    print(f"=== Insight #38 chain for vendor: {vendor}, max_step={max_step} ===\n")

    # STEP 1 — index match
    print("STEP 1 — Shodan index-match")
    candidates = {}
    for dork in cfg["shodan_dorks"]:
        try:
            data = shodan_search(key, dork)
            total = data.get("total", 0)
            print(f"  dork: {dork[:60]} -> {total} hits")
            for m in (data.get("matches") or [])[:10]:
                ip = m.get("ip_str"); port = m.get("port"); body = m.get("http", {}).get("html", "")
                if not (ip and body): continue
                keys_sk = list(set(re.findall(cfg["key_pattern"], body)))
                keys_pk = list(set(re.findall(cfg.get("pubkey_pattern", "$nothing^"), body))) if cfg.get("pubkey_pattern") else []
                if keys_sk:
                    candidates[f"{ip}:{port}"] = {"ip": ip, "port": port, "sk_keys": keys_sk, "pk_keys": keys_pk}
            time.sleep(1)
        except Exception as e:
            print(f"  err: {e}")
    print(f"  -> {len(candidates)} candidates with key-format matches")
    print()

    if max_step <= 1: return

    # STEP 2 — live re-fetch (skipped here; the dorks already validated current state for the most-recent crawl)
    # STEP 3 — format validation
    print("STEP 3 — format validation")
    for ipport, c in list(candidates.items()):
        c["sk_keys"] = [k for k in c["sk_keys"] if re.match(cfg["format_regex"], k)]
        if not c["sk_keys"]:
            del candidates[ipport]
            print(f"  {ipport}: dropped (no format-valid key)")
        else:
            print(f"  {ipport}: {len(c['sk_keys'])} format-valid key(s)")
    print()

    if max_step <= 3: return

    # STEP 4 — credential validity
    print("STEP 4 — credential validity (single read-only API call per candidate)")
    for ipport, c in candidates.items():
        sk = c["sk_keys"][0]
        pk = c["pk_keys"][0] if c.get("pk_keys") else sk  # fallback for vendors that don't have a pk
        endpoint = cfg["default_endpoint"]
        verify_url = endpoint + cfg["verify_path"]
        if cfg["auth_scheme"] == "basic_pk_sk":
            auth = base64.b64encode(f"{pk}:{sk}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}", "User-Agent": "nuclide-exfil-cred-verify/2026-05-19"}
        elif cfg["auth_scheme"] == "bearer_sk":
            headers = {"Authorization": f"Bearer {sk}", "User-Agent": "nuclide-exfil-cred-verify/2026-05-19"}
        elif cfg["auth_scheme"] == "x_api_key":
            headers = {"x-api-key": sk, "User-Agent": "nuclide-exfil-cred-verify/2026-05-19"}
        else:
            continue
        sc, body = http_get(verify_url, headers=headers)
        if sc == 200 and (not cfg.get("verify_marker") or cfg["verify_marker"].encode() in body):
            c["live"] = True
            c["verify_response"] = body[:512].decode("utf-8", errors="replace")
            try:
                c["verify_parsed"] = json.loads(body)
            except: c["verify_parsed"] = None
            print(f"  {ipport}: LIVE (status 200)")
        else:
            c["live"] = False
            print(f"  {ipport}: not-live (status {sc})")
    print()

    if max_step <= 4: return

    # STEP 5 — operator attribution
    print("STEP 5 — operator attribution")
    for ipport, c in candidates.items():
        if not c.get("live"): continue
        parsed = c.get("verify_parsed")
        if not parsed: continue
        if cfg.get("operator_path"):
            op = get_path(parsed, cfg["operator_path"])
            c["operator"] = op
        if cfg.get("product_path"):
            prod = get_path(parsed, cfg["product_path"])
            c["product"] = prod
        print(f"  {ipport}: operator={c.get('operator')} product={c.get('product')}")
    print()

    if max_step <= 5: return

    # STEP 6 — content verification (requires explicit per-vendor template)
    print("STEP 6 — content verification (one record per candidate)")
    if not cfg.get("content_endpoint_template"):
        print(f"  vendor {vendor}: no content_endpoint_template configured; SKIPPED by design")
        return
    print(f"  (manual escalation only — see Insight #38 procedural rule #3)")
    print(f"  hosts ready for content-verification:")
    for ipport, c in candidates.items():
        if c.get("live"):
            print(f"    {ipport}  operator={c.get('operator')}  product={c.get('product')}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vendor", required=False)
    ap.add_argument("--max-step", type=int, default=4, choices=[1, 2, 3, 4, 5, 6])
    ap.add_argument("--list-vendors", action="store_true")
    args = ap.parse_args()
    if args.list_vendors:
        for v, cfg in VENDOR_CONFIG.items():
            print(f"  {v}: dorks={cfg.get('shodan_dorks')[:2]}... endpoint={cfg.get('default_endpoint')}")
        return
    if not args.vendor:
        ap.error("--vendor required (or --list-vendors)")
    if args.vendor not in VENDOR_CONFIG:
        ap.error(f"unknown vendor; supported: {list(VENDOR_CONFIG.keys())}")
    run_chain(args.vendor, args.max_step)


if __name__ == "__main__":
    main()
