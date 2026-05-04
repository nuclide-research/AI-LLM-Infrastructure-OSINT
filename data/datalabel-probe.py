#!/usr/bin/env python3
"""
datalabel-probe.py — Probe a candidate host for exposed data-labeling / annotation servers.

Platforms detected (order tried per (ip, port)):
  - Argilla       — GET /api/_info  (port 6900 default)
  - LabelStudio   — GET /version    (port 8080 default)
  - Prodigy       — GET /           (port 8080) — HTML title check
  - doccano       — GET /v1/health  (port 8000 default)
  - CVAT          — GET /api/server/about (port 8080 default)

Each platform has a distinct response signature; the probe matches on those rather
than relying on port alone (8080/8000 collide heavily with other AI platforms).

Output JSONL per confirmed host:
  {ip, port, platform, version, project_count, auth_required, raw_signature}

Usage:
  echo -e "1.2.3.4:6900\\n5.6.7.8:8080" | python3 datalabel-probe.py
  python3 datalabel-probe.py --in ips.txt --out confirmed.jsonl --threads 200
"""
import argparse
import concurrent.futures
import json
import re
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_PORTS = [6900, 8000, 8080]
TIMEOUT_S = 5.0
MAX_BYTES = 32768


def parse_target(s: str) -> tuple[str, int]:
    s = s.strip()
    if ":" in s:
        ip, port_s = s.rsplit(":", 1)
        return ip, int(port_s)
    return s, 0


def http_get(url: str, timeout: float = TIMEOUT_S, accept: str = "application/json,text/html") -> tuple[int, dict, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-datalabel-probe/0.1 (research; security@nuclide-research.com)",
            "Accept": accept,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read(MAX_BYTES)
    except urllib.error.HTTPError as e:
        try:
            body = e.read()[:MAX_BYTES]
        except Exception:
            body = b""
        return e.code, dict(e.headers or {}), body
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError):
        return 0, {}, b""


def try_argilla(ip: str, port: int) -> Optional[dict]:
    url = f"http://{ip}:{port}/api/_info"
    status, _, body = http_get(url)
    if status == 0 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    # Argilla /api/_info returns {"version": "...", "elasticsearch": {...}, ...}
    if not isinstance(data, dict):
        return None
    if "version" not in data or "elasticsearch" not in data:
        return None
    # Try /api/me to check auth posture
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/me")
    auth_required = (s2 == 401 or s2 == 403)
    # Try /api/v1/workspaces to count
    s3, _, b3 = http_get(f"http://{ip}:{port}/api/v1/workspaces")
    workspace_count = None
    if s3 == 200:
        try:
            d3 = json.loads(b3)
            if isinstance(d3, dict) and isinstance(d3.get("items"), list):
                workspace_count = len(d3["items"])
            elif isinstance(d3, list):
                workspace_count = len(d3)
        except Exception:
            pass
    return {
        "platform": "Argilla",
        "version": data.get("version", ""),
        "auth_required": auth_required,
        "project_count": workspace_count,
        "raw_signature": "elasticsearch+version in /api/_info",
    }


def try_labelstudio(ip: str, port: int) -> Optional[dict]:
    url = f"http://{ip}:{port}/version"
    status, _, body = http_get(url)
    if status == 0 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    # LabelStudio returns {"release": "X.Y.Z", "label-studio-os-package": {...},
    #                       "label-studio-os-backend": {...}, "label-studio-frontend": {...}}
    if not isinstance(data, dict):
        return None
    if "release" not in data and "label-studio-os-package" not in data:
        return None
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/projects")
    project_count = None
    auth_required = (s2 == 401 or s2 == 403)
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            if isinstance(d2, dict) and isinstance(d2.get("results"), list):
                project_count = d2.get("count", len(d2["results"]))
            elif isinstance(d2, list):
                project_count = len(d2)
        except Exception:
            pass
    return {
        "platform": "LabelStudio",
        "version": data.get("release", ""),
        "auth_required": auth_required,
        "project_count": project_count,
        "raw_signature": "release+label-studio-os-* in /version",
    }


def try_doccano(ip: str, port: int) -> Optional[dict]:
    url = f"http://{ip}:{port}/v1/health"
    status, _, body = http_get(url)
    if status == 0 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    # doccano returns {"status": "green"} (or similar) — generic; check for distinctive pattern
    # Better: GET / returns "doccano" in HTML, OR /v1/projects returns paginated project list
    s2, _, b2 = http_get(f"http://{ip}:{port}/v1/projects")
    auth_required = (s2 == 401 or s2 == 403)
    project_count = None
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            if isinstance(d2, dict) and "count" in d2 and "results" in d2:
                project_count = d2["count"]
        except Exception:
            return None
    elif s2 != 401 and s2 != 403:
        return None
    # Verify distinctively doccano via static asset check
    s3, _, b3 = http_get(f"http://{ip}:{port}/")
    if s3 != 200 or b"doccano" not in b3.lower():
        # Health endpoint matched but no doccano marker — could be FP
        if not auth_required and project_count is None:
            return None
    return {
        "platform": "doccano",
        "version": "",
        "auth_required": auth_required,
        "project_count": project_count,
        "raw_signature": "v1/projects pagination + 'doccano' marker",
    }


def try_cvat(ip: str, port: int) -> Optional[dict]:
    url = f"http://{ip}:{port}/api/server/about"
    status, _, body = http_get(url)
    if status == 0 or not body:
        return None
    try:
        data = json.loads(body)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    name = (data.get("name") or "").lower()
    if "computer vision annotation" not in name and "cvat" not in name:
        return None
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/projects")
    auth_required = (s2 == 401 or s2 == 403)
    project_count = None
    if s2 == 200:
        try:
            d2 = json.loads(b2)
            if isinstance(d2, dict):
                project_count = d2.get("count")
        except Exception:
            pass
    return {
        "platform": "CVAT",
        "version": data.get("version", ""),
        "auth_required": auth_required,
        "project_count": project_count,
        "raw_signature": "name='Computer Vision Annotation Tool' in /api/server/about",
    }


def try_prodigy(ip: str, port: int) -> Optional[dict]:
    url = f"http://{ip}:{port}/"
    status, _, body = http_get(url)
    if status == 0 or not body:
        return None
    text = body.decode("utf-8", errors="ignore").lower()
    # Prodigy ships a SPA — title and asset paths reference "prodigy"
    if "prodigy" not in text:
        return None
    if not (
        "<title>prodigy" in text
        or 'class="prodigy' in text
        or "prodigy.js" in text
    ):
        return None
    version = ""
    m = re.search(r'prodigy[^\d]*([\d]+\.[\d]+(?:\.[\d]+)?)', text)
    if m:
        version = m.group(1)
    return {
        "platform": "Prodigy",
        "version": version,
        "auth_required": None,  # Prodigy has no built-in auth; reverse-proxy tier
        "project_count": None,
        "raw_signature": "'prodigy' marker in HTML root",
    }


PLATFORM_HANDLERS = {
    6900: [try_argilla],
    8000: [try_doccano, try_argilla, try_labelstudio, try_cvat],
    8080: [try_labelstudio, try_cvat, try_prodigy, try_argilla, try_doccano],
}


def probe_target(target: str, ports: list[int]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        handlers = PLATFORM_HANDLERS.get(p, [])
        if not handlers:
            handlers = [try_argilla, try_labelstudio, try_doccano, try_cvat, try_prodigy]
        for h in handlers:
            t0 = time.monotonic()
            try:
                res = h(ip, p)
            except Exception:
                res = None
            if res:
                res["ip"] = ip
                res["port"] = p
                res["url"] = f"http://{ip}:{p}"
                res["elapsed_ms"] = int((time.monotonic() - t0) * 1000)
                return res
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?")
    ap.add_argument("--in", dest="infile")
    ap.add_argument("--out", dest="outfile")
    ap.add_argument("--threads", type=int, default=100)
    ap.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS))
    args = ap.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    targets: list[str] = []
    if args.target:
        targets.append(args.target)
    if args.infile:
        with open(args.infile) as f:
            targets.extend(line.strip() for line in f if line.strip())
    if not targets and not args.target:
        targets.extend(line.strip() for line in sys.stdin if line.strip())

    if not targets:
        ap.print_help()
        sys.exit(1)

    out = open(args.outfile, "w") if args.outfile else sys.stdout
    confirmed = 0
    by_platform = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(probe_target, t, ports): t for t in targets}
        for fut in concurrent.futures.as_completed(futures):
            try:
                res = fut.result()
            except Exception:
                continue
            if res:
                out.write(json.dumps(res) + "\n")
                out.flush()
                confirmed += 1
                p = res.get("platform", "?")
                by_platform[p] = by_platform.get(p, 0) + 1

    if args.outfile:
        out.close()
    print(f"# probed: {len(targets)} hosts, confirmed: {confirmed}", file=sys.stderr)
    for plat, n in sorted(by_platform.items(), key=lambda kv: -kv[1]):
        print(f"#   {plat}: {n}", file=sys.stderr)


if __name__ == "__main__":
    main()
