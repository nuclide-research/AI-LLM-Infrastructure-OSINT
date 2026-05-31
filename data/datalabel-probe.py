#!/usr/bin/env python3
"""datalabel-probe.py — verify exposed data-labeling / annotation servers.

Identity + auth-state per platform (Argilla, Label Studio, doccano, CVAT, Prodigy).
Each platform has a distinct response signature; the probe matches on those rather
than port alone (8080/8000 collide heavily with other AI platforms).

v0.2 (2026-05-31, data-labeling survey): added https support (managed-cloud :443),
Label Studio open-signup detection (the headline LS misconfig), project-NAME capture
(names are the finding), and --from-aimap to verify hosts an aimap report identified.

RESTRAINT: enumerates auth-state, project COUNT, and up to 3 project NAMES only.
Never reads labeled records / imagery / annotations. Never registers or authenticates
(open-signup and default-credential states are reported as reachable, not exercised).

Output JSONL per confirmed host:
  {ip, port, url, platform, version, auth_required, project_count, project_names,
   signup_open?, raw_signature}

Usage:
  echo -e "1.2.3.4:6900\\n5.6.7.8:443" | python3 datalabel-probe.py
  python3 datalabel-probe.py --in ips.txt --out confirmed.jsonl --threads 200
  python3 datalabel-probe.py --from-aimap aimap-report.json --out confirmed.jsonl
"""
import argparse
import concurrent.futures
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

TIMEOUT_S = 6.0
MAX_BYTES = 65536
DEFAULT_PORTS = [6900, 8000, 8080, 80, 443, 8085, 8081]
_SSL = ssl._create_unverified_context()


def parse_target(s: str):
    s = s.strip()
    if "://" in s:  # full base url (e.g. from --from-aimap)
        return s, None
    if s.count(":") == 1 and not s.startswith("["):
        ip, port_s = s.rsplit(":", 1)
        if port_s.isdigit():
            return ip, int(port_s)
    return s, None


def bases_for(ip: str, port: Optional[int]):
    if port:
        sch = ["https", "http"] if port in (443, 8443) else ["http", "https"]
        return [f"{s}://{ip}:{port}" for s in sch]
    out = []
    for p in DEFAULT_PORTS:
        sch = ["https", "http"] if p in (443, 8443) else ["http", "https"]
        out += [f"{s}://{ip}:{p}" for s in sch]
    return out


def http_get(url: str, timeout: float = TIMEOUT_S, accept: str = "application/json,text/html"):
    req = urllib.request.Request(url, headers={
        "User-Agent": "nuclide-datalabel-probe/0.2 (research; security@nuclide-research.com)",
        "Accept": accept,
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL) as resp:
            return resp.status, dict(resp.headers), resp.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()[:MAX_BYTES]
        except Exception:
            body = b""
        return e.code, dict(e.headers or {}), body
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError, ValueError):
        return 0, {}, b""


def _names(d, keys=("title", "name")):
    """Up to 3 project NAMES (the finding) — never the labeled data inside them."""
    out = []
    results = d.get("results") if isinstance(d, dict) else (d if isinstance(d, list) else [])
    if isinstance(results, list):
        for it in results[:3]:
            if isinstance(it, dict):
                for k in keys:
                    if it.get(k):
                        out.append(str(it[k])[:60])
                        break
    return out


def try_argilla(base: str) -> Optional[dict]:
    for path in ("/api/v1/version", "/api/_info"):
        st, _, body = http_get(base + path)
        if st != 200 or not body:
            continue
        try:
            data = json.loads(body)
        except Exception:
            continue
        if not isinstance(data, dict) or "version" not in data:
            continue
        s2, _, _ = http_get(base + "/api/v1/me")
        return {"platform": "Argilla", "version": data.get("version", ""),
                "auth_required": s2 in (401, 403), "project_count": None,
                "project_names": [], "raw_signature": path}
    return None


def try_labelstudio(base: str) -> Optional[dict]:
    st, _, body = http_get(base + "/api/version")
    if st != 200 or not body:
        st, _, body = http_get(base + "/version")
    if st != 200 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    if not isinstance(data, dict) or ("release" not in data and "label-studio-os-package" not in data):
        return None
    s2, _, b2 = http_get(base + "/api/projects")
    auth = s2 in (401, 403)
    cnt, names = None, []
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            cnt = d2.get("count") if isinstance(d2, dict) else (len(d2) if isinstance(d2, list) else None)
            names = _names(d2)
        except Exception:
            pass
    # open-signup misconfig: reachable signup form = effective-unauth (inner-A, NOT exercised)
    s3, _, b3 = http_get(base + "/user/signup")
    low = b3.lower()
    signup_open = s3 == 200 and (b"create account" in low or b"sign up" in low or b"signup" in low) and b"label" in low
    return {"platform": "LabelStudio", "version": data.get("release", ""),
            "auth_required": auth, "project_count": cnt, "project_names": names,
            "signup_open": signup_open, "raw_signature": "release/label-studio-os-package"}


def try_doccano(base: str) -> Optional[dict]:
    st, _, body = http_get(base + "/v1/health")
    if st != 200 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    if not isinstance(data, dict) or "status" not in data:
        return None
    s2, _, b2 = http_get(base + "/v1/projects")
    auth = s2 in (401, 403)
    cnt, names = None, []
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            if isinstance(d2, dict) and "count" in d2 and "results" in d2:
                cnt = d2["count"]
                names = _names(d2)
            else:
                return None  # health matched but projects not doccano-shaped = FP guard
        except Exception:
            return None
    else:
        s3, _, b3 = http_get(base + "/")
        if not (s3 == 200 and b"doccano" in b3.lower()) and not auth:
            return None
    return {"platform": "doccano", "version": "", "auth_required": auth,
            "project_count": cnt, "project_names": names,
            "raw_signature": "v1/health+v1/projects"}


def try_cvat(base: str) -> Optional[dict]:
    # CVAT uses DRF AcceptHeaderVersioning: /api/server/about needs the vendor
    # media type or it 404s/406s. A plain application/json probe (and aimap, which
    # sends no vendor media type) both missed CVAT in the 2026-05-31 survey.
    st, _, body = http_get(base + "/api/server/about", accept="application/vnd.cvat+json")
    if st != 200 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None  # anti-IAP: a non-JSON 200 (HTML catch-all) is not CVAT
    if not isinstance(data, dict) or "computer vision annotation" not in (data.get("name") or "").lower():
        return None
    s2, _, b2 = http_get(base + "/api/projects", accept="application/vnd.cvat+json")
    auth = s2 in (401, 403)
    cnt, names = None, []
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            cnt = d2.get("count") if isinstance(d2, dict) else None
            names = _names(d2)
        except Exception:
            pass
    return {"platform": "CVAT", "version": data.get("version", ""), "auth_required": auth,
            "project_count": cnt, "project_names": names,
            "raw_signature": "name=Computer Vision Annotation Tool"}


def try_prodigy(base: str) -> Optional[dict]:
    st, _, b = http_get(base + "/health")
    if st == 200 and b:
        try:
            d = json.loads(b)
            if isinstance(d, dict) and d.get("status") == "alive":
                s2, _, b2 = http_get(base + "/project")
                view = False
                if s2 == 200:
                    try:
                        view = "view_id" in json.loads(b2)
                    except Exception:
                        pass
                return {"platform": "Prodigy", "version": "", "auth_required": False,
                        "project_count": None, "project_names": [],
                        "raw_signature": "/health alive" + ("+view_id" if view else "")}
        except Exception:
            pass
    # fallback: prodigy.js bundle (anti-name-collision: never a bare title)
    st, _, body = http_get(base + "/")
    if st == 200 and b"prodigy.js" in body.lower():
        return {"platform": "Prodigy", "version": "", "auth_required": False,
                "project_count": None, "project_names": [], "raw_signature": "prodigy.js bundle"}
    return None


HANDLERS_BY_PORT = {
    6900: [try_argilla],
    8000: [try_doccano, try_argilla, try_labelstudio, try_cvat],
    8080: [try_labelstudio, try_cvat, try_prodigy, try_doccano],
    8085: [try_labelstudio],
    8081: [try_labelstudio, try_cvat],
    443: [try_labelstudio, try_cvat, try_doccano, try_argilla, try_prodigy],
    80: [try_labelstudio, try_cvat, try_doccano, try_prodigy],
}
ALL_HANDLERS = [try_argilla, try_labelstudio, try_doccano, try_cvat, try_prodigy]


def probe_base(base: str, handlers) -> Optional[dict]:
    for h in handlers:
        t0 = time.monotonic()
        try:
            res = h(base)
        except Exception:
            res = None
        if res:
            res["url"] = base
            res["elapsed_ms"] = int((time.monotonic() - t0) * 1000)
            return res
    return None


def probe_target(target: str, ports) -> Optional[dict]:
    raw, hint = parse_target(target)
    if "://" in raw:  # full base url (from --from-aimap)
        tail = raw.rsplit(":", 1)[1]
        port = int(tail) if tail.isdigit() else None
        res = probe_base(raw, HANDLERS_BY_PORT.get(port, ALL_HANDLERS))
        if res and "ip" not in res:
            res["ip"] = raw.split("://", 1)[1].rsplit(":", 1)[0]
            res["port"] = port
        return res
    ip = raw
    for p in ([hint] if hint else ports):
        for base in bases_for(ip, p):
            res = probe_base(base, HANDLERS_BY_PORT.get(p, ALL_HANDLERS))
            if res:
                res["ip"] = ip
                res["port"] = p
                return res
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--in", dest="infile")
    ap.add_argument("--from-aimap", dest="aimap", help="aimap report.json; verifies each service's base_url")
    ap.add_argument("--out", dest="outfile")
    ap.add_argument("--threads", type=int, default=100)
    ap.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS))
    args = ap.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    targets = []
    if args.target:
        targets.append(args.target)
    if args.infile:
        with open(args.infile) as f:
            targets.extend(line.strip() for line in f if line.strip())
    if args.aimap:
        rep = json.load(open(args.aimap))
        for s in rep.get("services", []):
            base = s.get("base_url")
            if base:
                targets.append(base)
    if not targets:
        targets.extend(line.strip() for line in sys.stdin if line.strip())
    if not targets:
        ap.print_help()
        sys.exit(1)

    # dedupe preserving order
    seen, uniq = set(), []
    for t in targets:
        if t not in seen:
            seen.add(t)
            uniq.append(t)

    out = open(args.outfile, "w") if args.outfile else sys.stdout
    confirmed, by_platform, unauth = 0, {}, 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(probe_target, t, ports): t for t in uniq}
        for fut in concurrent.futures.as_completed(futures):
            try:
                res = fut.result()
            except Exception:
                continue
            if res:
                out.write(json.dumps(res) + "\n")
                out.flush()
                confirmed += 1
                by_platform[res["platform"]] = by_platform.get(res["platform"], 0) + 1
                if res.get("auth_required") is False or res.get("signup_open"):
                    unauth += 1
    if args.outfile:
        out.close()
    print(f"# probed: {len(uniq)} hosts, confirmed: {confirmed}, effective-unauth: {unauth}", file=sys.stderr)
    for plat, n in sorted(by_platform.items(), key=lambda kv: -kv[1]):
        print(f"#   {plat}: {n}", file=sys.stderr)


if __name__ == "__main__":
    main()
