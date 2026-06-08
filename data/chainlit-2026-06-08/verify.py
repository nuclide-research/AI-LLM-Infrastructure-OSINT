#!/usr/bin/env python3
"""
Chainlit population verifier — NuClide Cat-50 survey (2026-06-08).

RESTRAINT POSTURE (LOAD-BEARING):
- GET requests ONLY.
- DO NOT POST to /message or any chat endpoint.
- DO NOT read chat history or user messages.
- Names + counts + version strings only.

Pipeline per host:
  1. GET /            -> Chainlit identity (og:url chainlit/chainlit, og:image
                        chainlit-cloud S3, /assets/index-*.js bundle, uvicorn header)
  2. GET /auth/config -> auth: providers, requireLogin (modern Chainlit endpoint)
  3. GET /user        -> 200 user-obj == open, 401/403 == auth-required
  4. GET /project/translations -> Chainlit secondary identity marker

Verdict buckets:
  - unauth_chainlit_confirmed : Chainlit identity + auth_config.requireLogin == false
  - auth_chainlit_confirmed   : Chainlit identity + auth_config.requireLogin == true
  - fp_not_chainlit           : reachable but no Chainlit markers
  - dead                      : connect/timeout/TLS failure
"""

import json
import re
import sys
import time
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HEADERS = {
    "User-Agent": "NuClide-survey/1.0 (chainlit-cat50; nicholas@nuclide-research.com)",
    "Accept": "*/*",
}
TIMEOUT = 10

# Chainlit identity markers (modern v1.x+ — body marker set; any one is sufficient)
CHAINLIT_MARKERS = [
    b"github.com/chainlit/chainlit",       # og:url canonical
    b"chainlit-cloud.s3",                  # og:image canonical
    b"chainlit_banner.png",
    b'/assets/index-',                     # vite bundle prefix (high-prob but not unique alone)
    b"built with chainlit",
    b'name="chainlit"',
]


def scheme_for(port: int) -> str:
    return "https" if port in (443, 8443, 9000) else "http"


def fetch(url: str):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=False, allow_redirects=True)
        return r
    except Exception as e:
        return e


def is_chainlit_body(body: bytes) -> bool:
    lc = body.lower()
    # Require at least one HIGH-confidence marker (rules out the lone vite-bundle
    # false-positive that any vite SPA would trip).
    high_conf = (
        b"github.com/chainlit/chainlit" in lc
        or b"chainlit-cloud.s3" in lc
        or b"chainlit_banner.png" in lc
        or b"built with chainlit" in lc
        or b'name="chainlit"' in lc
    )
    return high_conf


def parse_json_safe(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None


def probe(pair: str) -> dict:
    ip, port = pair.split(":")
    port = int(port)
    base = f"{scheme_for(port)}://{ip}:{port}"
    out = {
        "pair": pair,
        "base": base,
        "verdict": "dead",
        "root_status": None,
        "root_title": None,
        "is_chainlit_root": False,
        "og_url_chainlit": False,
        "auth_config_status": None,
        "require_login": None,
        "auth_providers": [],
        "user_status": None,
        "user_identifier": None,
        "translations_status": None,
        "translations_is_chainlit": False,
        "project_name": None,
        "ui_name": None,
        "chat_profiles": [],
        "chainlit_version": None,
        "server_header": None,
        "x_powered_by": None,
        "js_bundle": None,
        "notes": [],
    }

    # Try both schemes for portability on common ports
    schemes = [scheme_for(port)]
    if port not in (80, 443, 8443):
        schemes = ["http", "https"]

    root_resp = None
    chosen_base = None
    for sch in schemes:
        b = f"{sch}://{ip}:{port}"
        r = fetch(f"{b}/")
        if isinstance(r, Exception):
            out["notes"].append(f"root {sch} err: {type(r).__name__}")
            continue
        root_resp = r
        chosen_base = b
        break

    if root_resp is None:
        return out

    out["base"] = chosen_base
    out["root_status"] = root_resp.status_code
    out["server_header"] = root_resp.headers.get("Server", "")
    out["x_powered_by"] = root_resp.headers.get("X-Powered-By", "")
    body = root_resp.content or b""

    # Title
    m = re.search(rb"<title[^>]*>([^<]+)</title>", body, re.IGNORECASE)
    if m:
        out["root_title"] = m.group(1).decode("utf-8", "replace").strip()[:120]

    # JS bundle hash (used for version cluster grouping)
    m = re.search(rb"/assets/(index-[A-Za-z0-9_-]+\.js)", body)
    if m:
        out["js_bundle"] = m.group(1).decode("ascii", "replace")

    # og:url to github.com/Chainlit/chainlit is canonical Chainlit signature
    if b"github.com/Chainlit/chainlit" in body or b"github.com/chainlit/chainlit" in body.lower():
        out["og_url_chainlit"] = True
    out["is_chainlit_root"] = is_chainlit_body(body)

    # /auth/config probe (modern Chainlit path)
    r = fetch(f"{chosen_base}/auth/config")
    if not isinstance(r, Exception):
        out["auth_config_status"] = r.status_code
        if r.status_code == 200:
            j = parse_json_safe(r.text)
            if j is not None and isinstance(j, dict):
                # Chainlit returns { requireLogin: bool, oauthProviders: [...], passwordAuth: bool, headerAuth: bool, ... }
                out["require_login"] = j.get("requireLogin")
                out["auth_providers"] = j.get("oauthProviders") or []
                # Presence of these keys in JSON form == Chainlit
                if any(k in j for k in ("requireLogin", "passwordAuth", "headerAuth", "oauthProviders", "cookieAuth")):
                    out["is_chainlit_root"] = True

    # /user probe — names + counts only, no content read
    r = fetch(f"{chosen_base}/user")
    if not isinstance(r, Exception):
        out["user_status"] = r.status_code
        if r.status_code == 200:
            j = parse_json_safe(r.text)
            if isinstance(j, dict):
                # ident only; do not log payload
                ident = j.get("identifier") or j.get("id") or "<set>"
                out["user_identifier"] = str(ident)[:80]
                if "identifier" in j or "metadata" in j:
                    out["is_chainlit_root"] = True

    # /project/translations — Chainlit-specific, useful as secondary identity
    r = fetch(f"{chosen_base}/project/translations")
    if not isinstance(r, Exception):
        out["translations_status"] = r.status_code
        if r.status_code == 200:
            j = parse_json_safe(r.text)
            if isinstance(j, dict) and ("translation" in j or "chat_messages" in j or "settings" in j):
                out["translations_is_chainlit"] = True
                out["is_chainlit_root"] = True
                # Don't extract payload; presence == confirmation

    # Verdict logic — three independent signals for restraint:
    #   identity:  og_url_chainlit OR auth/config JSON OR /project/translations JSON
    #   auth-on:   require_login==True  OR  /user==401/403
    #   auth-off:  require_login==False AND  /user==200 (no creds sent)
    identity = out["is_chainlit_root"] or out["og_url_chainlit"] or out["translations_is_chainlit"]

    if identity:
        if out["require_login"] is True:
            out["verdict"] = "auth_chainlit_confirmed"
        elif out["require_login"] is False:
            # Chainlit explicitly reports no-login-required.
            # /user == 200 here means anonymous session is accepted (open chat UI).
            if out["user_status"] in (200,):
                out["verdict"] = "unauth_chainlit_confirmed"
            elif out["user_status"] in (401, 403):
                # mismatch: requireLogin=false but /user blocked — count as auth posture
                out["verdict"] = "auth_chainlit_confirmed"
                out["notes"].append("requireLogin=false but /user blocked")
            else:
                out["verdict"] = "unauth_chainlit_confirmed"
                out["notes"].append("requireLogin=false; /user status non-200/401/403")
        else:
            # requireLogin not reported (older Chainlit or proxied) — fall back to /user
            if out["user_status"] in (401, 403):
                out["verdict"] = "auth_chainlit_confirmed"
                out["notes"].append("auth inferred from /user 401/403")
            elif out["user_status"] == 200:
                out["verdict"] = "unauth_chainlit_confirmed"
                out["notes"].append("auth inferred from /user 200")
            else:
                out["verdict"] = "chainlit_identity_only"
                out["notes"].append("identity confirmed; auth posture unknown")
    elif out["root_status"] is not None:
        out["verdict"] = "fp_not_chainlit"

    return out


def main():
    pairs_path = Path(__file__).parent / "pairs.txt"
    pairs = [ln.strip() for ln in pairs_path.read_text().splitlines() if ln.strip()]
    print(f"[+] Probing {len(pairs)} hosts (GET-only, no POST, no chat reads)", file=sys.stderr)

    results = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(probe, p): p for p in pairs}
        for f in as_completed(futs):
            res = f.result()
            results.append(res)
            print(f"  {res['pair']:25s}  {res['verdict']:30s}  title={res.get('root_title') or '-'}", file=sys.stderr)

    results.sort(key=lambda r: r["pair"])
    out_path = Path(__file__).parent / "verify-results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"[+] wrote {out_path}", file=sys.stderr)

    # Tally
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[ TALLY ]", file=sys.stderr)
    for k, v in sorted(tally.items()):
        print(f"  {k:35s}  {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
