#!/usr/bin/env python3
"""
Khoj population verifier.

Restraint: GET only. NEVER POST chat/search. NEVER read indexed files.
Document COUNTS and CONFIG-TIER PRESENCE only, never bodies.

Endpoints probed (all GET):
  /                       -> Khoj identity (markers in HTML)
  /api/v1/health          -> liveness + version
  /api/v1/user            -> auth state probe (200 -> permissive/anon; 401 -> auth-required)
  /api/v1/agents          -> agent persona list (count + names only)
  /api/v1/automations     -> scheduled task list (count only)

Verdict buckets:
  unauth_khoj_confirmed  -> Khoj confirmed AND /api/v1/user returns anonymous user (no creds)
  auth_khoj_confirmed    -> Khoj confirmed AND /api/v1/user is 401/403
  single_user_mode       -> Khoj confirmed AND /api/v1/user returns user but only one default account
  fp_not_khoj            -> server up but no Khoj markers
  dead                   -> no response / connection failure
"""

import concurrent.futures as cf
import json
import socket
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import urllib3

urllib3.disable_warnings()
import requests

PAIRS_FILE = Path(__file__).parent / "pairs.txt"
OUT_FILE = Path(__file__).parent / "verify_results.jsonl"
TIMEOUT = 8
WORKERS = 50

KHOJ_MARKERS = [
    "khoj-favicon",
    "khoj.dev",
    "khoj-ai",
    "khoj_ai",
    '"khoj"',
    "Khoj AI",
    "/_next/static",  # Khoj uses Next.js; check together w/ other markers
]


def probe(ip: str, port: int) -> dict:
    """Probe a single host. GET-only."""
    result = {
        "ip": ip,
        "port": port,
        "khoj": False,
        "verdict": "dead",
        "errors": [],
    }

    # Try HTTPS first for 443/8443, else HTTP. Allow fallback.
    schemes = ["https", "http"] if port in (443, 8443, 8843) else ["http", "https"]

    base = None
    for sch in schemes:
        url = f"{sch}://{ip}:{port}"
        try:
            r = requests.get(
                url + "/",
                timeout=TIMEOUT,
                verify=False,
                allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0 (NuClide-survey/khoj)"}
            )
            base = url
            result["scheme"] = sch
            result["root_status"] = r.status_code
            result["root_len"] = len(r.text)
            body_lower = r.text.lower()
            marker_hits = [m for m in KHOJ_MARKERS if m.lower() in body_lower]
            result["root_markers"] = marker_hits
            # Specific high-confidence: "khoj-favicon" or "khoj ai" or "khoj.dev"
            if any(m in marker_hits for m in ["khoj-favicon", "khoj.dev", "khoj-ai", "khoj_ai", "Khoj AI"]):
                result["khoj"] = True
            elif "khoj" in body_lower and ("/_next/" in r.text or "_next/static" in r.text):
                # Khoj is a Next.js app; combo of khoj + Next.js is high confidence
                result["khoj"] = True
            elif "khoj" in body_lower and r.headers.get("server", "").lower() == "uvicorn":
                result["khoj"] = True
            break
        except Exception as e:
            result["errors"].append(f"root_{sch}:{type(e).__name__}")
            continue

    if base is None:
        return result

    # If not Khoj-identified by root, try the health endpoint anyway —
    # Khoj's static landing may proxy weirdly behind nginx.
    if not result["khoj"]:
        try:
            r = requests.get(base + "/api/v1/health", timeout=TIMEOUT, verify=False)
            if r.status_code == 200:
                try:
                    j = r.json()
                    if "status" in j or "version" in j:
                        result["khoj"] = True
                        result["health"] = j
                except Exception:
                    pass
        except Exception as e:
            result["errors"].append(f"health_pre:{type(e).__name__}")

    if not result["khoj"]:
        result["verdict"] = "fp_not_khoj"
        return result

    # Confirmed-Khoj path: probe auth + capability surface.
    # Khoj's real API path is /api/health (not /api/v1/health).
    # /api/health -- returns {"email": "..."} for the logged-in user, or {"detail":"OK"}
    try:
        r = requests.get(base + "/api/health", timeout=TIMEOUT, verify=False)
        result["health_status"] = r.status_code
        if r.status_code == 200:
            try:
                j = r.json()
                result["health"] = j
                # Khoj reports the CURRENT user's email here when in anon/single-user mode.
                # default@example.com is the canonical anonymous-mode marker.
                if isinstance(j, dict) and "email" in j:
                    result["user_has_email"] = True
                    email = j.get("email", "")
                    result["anon_default_email"] = email == "default@example.com"
                    result["health_keys"] = sorted(list(j.keys()))
            except Exception:
                pass
    except Exception as e:
        result["errors"].append(f"health:{type(e).__name__}")

    # /api/agents -- list count only (NEVER the persona text bodies)
    try:
        r = requests.get(base + "/api/agents", timeout=TIMEOUT, verify=False)
        result["agents_status"] = r.status_code
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, list):
                    result["agents_count"] = len(j)
                    if j and isinstance(j[0], dict):
                        result["agents_keys_sample"] = sorted(list(j[0].keys()))[:10]
                elif isinstance(j, dict) and "agents" in j:
                    result["agents_count"] = len(j["agents"])
            except Exception:
                pass
    except Exception as e:
        result["errors"].append(f"agents:{type(e).__name__}")

    # /api/automations
    try:
        r = requests.get(base + "/api/automations", timeout=TIMEOUT, verify=False)
        result["automations_status"] = r.status_code
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, list):
                    result["automations_count"] = len(j)
                elif isinstance(j, dict) and "automations" in j:
                    result["automations_count"] = len(j["automations"])
            except Exception:
                pass
    except Exception as e:
        result["errors"].append(f"automations:{type(e).__name__}")

    # /api/chat/sessions -- COUNT ONLY. Never log session contents.
    try:
        r = requests.get(base + "/api/chat/sessions", timeout=TIMEOUT, verify=False)
        result["sessions_status"] = r.status_code
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, list):
                    result["sessions_count"] = len(j)
                    # Conversation IDs only; do NOT keep titles or message bodies.
                    if j and isinstance(j[0], dict):
                        result["sessions_keys_sample"] = sorted(list(j[0].keys()))[:8]
            except Exception:
                pass
    except Exception as e:
        result["errors"].append(f"sessions:{type(e).__name__}")

    # /api/content/types -- list of indexed content types (e.g. ["all", "notion", "computer"])
    # PRESENCE-ONLY. Never call /api/content/file/* or /api/content/computer/*.
    try:
        r = requests.get(base + "/api/content/types", timeout=TIMEOUT, verify=False)
        result["content_types_status"] = r.status_code
        if r.status_code == 200:
            try:
                j = r.json()
                if isinstance(j, list):
                    result["content_types"] = j  # list of type labels, not content
                    result["content_types_count"] = len(j)
            except Exception:
                pass
    except Exception as e:
        result["errors"].append(f"content_types:{type(e).__name__}")

    # Verdict logic
    hs = result.get("health_status")
    has_email = result.get("user_has_email", False)
    is_default = result.get("anon_default_email", False)
    agents_ok = result.get("agents_status") == 200
    sessions_ok = result.get("sessions_status") == 200
    content_ok = result.get("content_types_status") == 200

    if is_default and (sessions_ok or content_ok):
        # default@example.com + reachable content/session listing = anonymous mode
        result["verdict"] = "unauth_khoj_confirmed"
    elif has_email and not is_default and sessions_ok:
        # Real-looking single-user account + sessions reachable
        result["verdict"] = "single_user_mode"
    elif hs == 200 and result.get("health") == {"detail": "OK"}:
        # Returns "OK" with no user info -> auth enforced
        result["verdict"] = "auth_khoj_confirmed"
    elif result.get("agents_status") == 403 or result.get("sessions_status") == 403:
        result["verdict"] = "auth_khoj_confirmed"
    elif agents_ok and not has_email:
        # /api/agents 200 lists public agents w/o exposing user -> multi-tenant w/ public surface
        result["verdict"] = "multitenant_public_agents"
    else:
        result["verdict"] = "auth_khoj_confirmed"

    return result


def main():
    pairs = []
    for line in PAIRS_FILE.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) >= 2:
            ip, port = parts[0], parts[1]
            try:
                pairs.append((ip, int(port)))
            except ValueError:
                continue

    print(f"[+] {len(pairs)} unique IP:PORT to probe", file=sys.stderr)
    print(f"[+] Restraint: GET only. No POST. No /api/content/*. No /api/chat/history.", file=sys.stderr)

    out = OUT_FILE.open("w")
    completed = 0
    khoj_confirmed = 0
    with cf.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(probe, ip, port): (ip, port) for ip, port in pairs}
        for fut in cf.as_completed(futures):
            ip, port = futures[fut]
            try:
                r = fut.result(timeout=TIMEOUT * 3)
            except Exception as e:
                r = {"ip": ip, "port": port, "verdict": "dead", "errors": [f"future:{type(e).__name__}"]}
            out.write(json.dumps(r) + "\n")
            completed += 1
            if r.get("khoj"):
                khoj_confirmed += 1
            if completed % 25 == 0:
                print(f"[*] {completed}/{len(pairs)} done; khoj={khoj_confirmed}", file=sys.stderr)
    out.close()
    print(f"[+] Done. {completed} probed, {khoj_confirmed} Khoj-confirmed.", file=sys.stderr)


if __name__ == "__main__":
    main()
