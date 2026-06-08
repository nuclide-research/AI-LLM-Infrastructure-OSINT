#!/usr/bin/env python3
"""
Argilla population verifier — Cat-51.

Restraint posture:
  - GET requests only.
  - Read NAMES (dataset names, workspace names) NOT RECORDS.
  - Never call /api/v1/datasets/{id}/records — would dump labeled training data.
  - Never call /api/v1/records — same.
  - Workspace name + dataset name + counts only.

Per-host flow:
  1. GET /api/_info   (Argilla version banner; old releases also expose /api/version)
  2. GET /api/v1/me   -> 401 = auth-gated; 200 + user = unauth
  3. (only if /me returned 200) GET /api/v1/workspaces -> workspace names
  4. (only if /me returned 200) GET /api/v1/datasets -> dataset names + counts
  5. (only on the auth-gated set) default-api-key probe:
       X-Api-Key: argilla.apikey  then  X-Api-Key: owner.apikey
       against /api/v1/me to test the well-known default credential.

Verdict buckets:
  unauth_argilla_confirmed   — /api/v1/me returned 200 with user JSON
  default_creds_argilla      — only the X-Api-Key default unlocked /me
  auth_argilla_confirmed     — /api/_info or /api/v1/me confirmed Argilla shape AND 401/403 returned
  fp_not_argilla             — endpoints returned non-Argilla shape (Shodan title FP)
  dead                       — no response or non-decodable on any probe
"""
import json
import sys
import urllib3
import concurrent.futures as cf
from pathlib import Path

import requests

urllib3.disable_warnings()

PAIRS = Path(__file__).parent / "pairs.txt"
OUT = Path(__file__).parent / "verify-results.json"

TIMEOUT = 6
THREADS = 50
UA = "NuClide-Survey/1.0 (Argilla population survey 2026-06-08, contact: nicholas@nuclide-research.com)"
HEADERS = {"User-Agent": UA, "Accept": "application/json"}

DEFAULT_KEYS = ["argilla.apikey", "owner.apikey"]


def schemes(pair):
    ip, port = pair.split(":")
    if port == "443":
        return [f"https://{ip}"]
    if port == "80":
        return [f"http://{ip}"]
    # ambiguous port — try https first then http
    return [f"https://{ip}:{port}", f"http://{ip}:{port}"]


def safe_get(url, headers=None):
    try:
        return requests.get(
            url,
            headers=headers or HEADERS,
            timeout=TIMEOUT,
            verify=False,
            allow_redirects=True,
        )
    except Exception:
        return None


def probe_info(base):
    """Return (version, looks_like_argilla, raw_status)."""
    for path in ("/api/_info", "/api/version", "/api/info"):
        r = safe_get(base + path)
        if r is None:
            continue
        if r.status_code != 200:
            continue
        body = r.text.strip()
        # strip <pre>...</pre> wrapper if present (lesson from Cat-49)
        if body.startswith("<pre>") and body.endswith("</pre>"):
            body = body[5:-6].strip()
        try:
            j = r.json()
        except Exception:
            try:
                j = json.loads(body)
            except Exception:
                continue
        if isinstance(j, dict):
            # Argilla /api/_info returns {"version": "...", "argilla": {...}}
            v = j.get("version") or (j.get("argilla", {}) or {}).get("version") or j.get("release")
            if v and ("argilla" in json.dumps(j).lower() or path == "/api/_info"):
                return v, True, 200
            # fallback: any version field with the right path that returned 200
            if v:
                return v, True, 200
    return None, False, 0


def probe_me(base, headers=None):
    """Return (status, json_or_none, path_used).

    Try modern /api/v1/me first, then pre-v1 /api/me.
    Strict: a 200 only counts if Content-Type is JSON-ish. The Argilla Nuxt SPA
    returns the SPA index HTML on any /api/v1/* path that the backend has not
    mounted (very common on old or partially-deployed instances), which would
    otherwise be misread as "unauth user".
    """
    for path in ("/api/v1/me", "/api/me"):
        r = safe_get(base + path, headers=headers)
        if r is None:
            continue
        ct = (r.headers.get("content-type") or "").lower()
        # 401/403 with JSON detail body — auth-gated Argilla shape (any path)
        if r.status_code in (401, 403):
            try:
                j = r.json()
            except Exception:
                j = None
            return r.status_code, j, path
        if r.status_code == 200:
            # Must be JSON to count as an unauth user response
            if "application/json" not in ct and "json" not in ct:
                continue  # SPA HTML catch-all; try next path
            try:
                j = r.json()
            except Exception:
                continue
            if not isinstance(j, dict):
                continue
            return 200, j, path
        # other status (404 / 500 etc) — try next path
    return 0, None, None


def probe_workspaces(base, headers=None):
    """Workspace NAMES only. Returns list of names or None.

    Tries v1 then pre-v1. Requires JSON content-type (HTML catch-all guard).
    """
    for path in ("/api/v1/workspaces", "/api/workspaces"):
        r = safe_get(base + path, headers=headers)
        if r is None or r.status_code != 200:
            continue
        ct = (r.headers.get("content-type") or "").lower()
        if "json" not in ct:
            continue
        try:
            j = r.json()
        except Exception:
            continue
        items = j.get("items") if isinstance(j, dict) else j
        if not isinstance(items, list):
            continue
        return [x.get("name") for x in items if isinstance(x, dict)]
    return None


def probe_datasets(base, headers=None):
    """Dataset NAMES + workspace_id only — no records. Returns list of dicts or None."""
    for path in ("/api/v1/datasets", "/api/datasets"):
        r = safe_get(base + path, headers=headers)
        if r is None or r.status_code != 200:
            continue
        ct = (r.headers.get("content-type") or "").lower()
        if "json" not in ct:
            continue
        try:
            j = r.json()
        except Exception:
            continue
        items = j.get("items") if isinstance(j, dict) else j
        if not isinstance(items, list):
            continue
        return [
            {
                "name": x.get("name"),
                "workspace_id": x.get("workspace_id") or x.get("workspace"),
                "task": x.get("task"),
            }
            for x in items if isinstance(x, dict)
        ]
    return None


def is_user_shape(j):
    """A valid Argilla /me 200 must look like a user record."""
    return (
        isinstance(j, dict)
        and (
            "username" in j
            or ("id" in j and ("role" in j or "first_name" in j or "api_key" in j))
        )
    )


def is_argilla_auth_error(j):
    """401/403 JSON body shape match for Argilla."""
    if not isinstance(j, dict):
        return False
    d = j.get("detail")
    if isinstance(d, str) and ("credentials" in d.lower() or "not authenticated" in d.lower()):
        return True
    if isinstance(d, dict):
        code = d.get("code", "")
        if isinstance(code, str) and "argilla" in code.lower():
            return True
        params = d.get("params", {})
        if isinstance(params, dict) and "credentials" in str(params).lower():
            return True
    return False


def verify_one(pair):
    result = {"pair": pair, "verdict": "dead", "base": None, "version": None,
              "me_status": None, "me_path": None, "workspaces": None, "datasets_count": None,
              "datasets_sample": None, "default_key_unlock": None, "notes": []}
    for base in schemes(pair):
        version, looks_argilla, _ = probe_info(base)
        me_status, me_json, me_path = probe_me(base)
        if me_status == 0 and not looks_argilla:
            continue  # try next scheme
        result["base"] = base
        result["version"] = version
        result["me_status"] = me_status
        result["me_path"] = me_path

        # Shape gate — must be Argilla via /api/_info OR via /me shape match
        is_argilla_shape = looks_argilla
        if me_status == 200 and is_user_shape(me_json):
            is_argilla_shape = True
        if me_status in (401, 403) and is_argilla_auth_error(me_json):
            is_argilla_shape = True

        if not is_argilla_shape:
            result["verdict"] = "fp_not_argilla"
            result["notes"].append(f"info={looks_argilla} me={me_status} path={me_path}")
            return result

        if me_status == 200 and is_user_shape(me_json):
            # UNAUTH confirmed — enumerate NAMES only
            result["verdict"] = "unauth_argilla_confirmed"
            ws = probe_workspaces(base)
            result["workspaces"] = ws
            ds = probe_datasets(base)
            if ds is not None:
                result["datasets_count"] = len(ds)
                result["datasets_sample"] = ds[:10]
            return result

        # auth-gated path — try default keys
        if me_status in (401, 403) or (looks_argilla and me_status not in (200,)):
            unlocked = None
            for k in DEFAULT_KEYS:
                hs = dict(HEADERS); hs["X-Api-Key"] = k
                st, j, p = probe_me(base, headers=hs)
                if st == 200 and is_user_shape(j):
                    unlocked = k
                    result["default_key_unlock"] = k
                    ws = probe_workspaces(base, headers=hs)
                    result["workspaces"] = ws
                    ds = probe_datasets(base, headers=hs)
                    if ds is not None:
                        result["datasets_count"] = len(ds)
                        result["datasets_sample"] = ds[:10]
                    break
            if unlocked:
                result["verdict"] = "default_creds_argilla"
            else:
                result["verdict"] = "auth_argilla_confirmed"
            return result

        # If we get here Argilla shape was confirmed via /api/_info but /me path
        # behaves oddly. Default-key probe still worth trying.
        unlocked = None
        for k in DEFAULT_KEYS:
            hs = dict(HEADERS); hs["X-Api-Key"] = k
            st, j, _ = probe_me(base, headers=hs)
            if st == 200 and is_user_shape(j):
                unlocked = k
                result["default_key_unlock"] = k
                ws = probe_workspaces(base, headers=hs)
                result["workspaces"] = ws
                ds = probe_datasets(base, headers=hs)
                if ds is not None:
                    result["datasets_count"] = len(ds)
                    result["datasets_sample"] = ds[:10]
                break
        result["verdict"] = "default_creds_argilla" if unlocked else "auth_argilla_confirmed"
        return result

    return result


def main():
    pairs = [p.strip() for p in PAIRS.read_text().splitlines() if p.strip()]
    print(f"[+] verifying {len(pairs)} pairs", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=THREADS) as ex:
        futs = {ex.submit(verify_one, p): p for p in pairs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            r = f.result()
            results.append(r)
            print(f"[{i}/{len(pairs)}] {r['pair']:30s} -> {r['verdict']}", file=sys.stderr)
    OUT.write_text(json.dumps(results, indent=2))
    print(f"[+] wrote {OUT}", file=sys.stderr)
    # tally
    from collections import Counter
    c = Counter(r["verdict"] for r in results)
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print(f"  {k:30s} {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
