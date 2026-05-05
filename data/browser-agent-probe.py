#!/usr/bin/env python3
"""
browser-agent-probe.py — Probe for exposed browser-automation backends used by AI agents.

Platforms detected:
  - Browserless                — port 3000, 8000; /json/version returns CDP info
  - Playwright server          — port 3000, 4444; /json/protocol returns CDP
  - Puppeteer remote (CDP)     — port 9222 (default Chrome DevTools Protocol port)
  - Selenium Grid              — port 4444; /wd/hub/status returns Selenium status
  - Skyvern                    — port 8000; /api/v1/health + Skyvern-specific routes

Output JSONL per confirmed host:
  {ip, port, platform, version, browser_version, raw_signature}
"""
import argparse
import concurrent.futures
import json
import socket
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_PORTS = [3000, 4444, 8000, 9222]
TIMEOUT_S = 5.0
MAX_BYTES = 32768


def parse_target(s: str) -> tuple[str, int]:
    s = s.strip()
    if ":" in s:
        ip, port_s = s.rsplit(":", 1)
        return ip, int(port_s)
    return s, 0


def http_get(url: str, timeout: float = TIMEOUT_S) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-browser-agent-probe/0.1 (research; security@nuclide-research.com)",
            "Accept": "application/json,text/html",
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


def try_cdp(ip: str, port: int) -> Optional[dict]:
    """Chrome DevTools Protocol fingerprint — Browserless, Playwright server, Puppeteer remote."""
    s, _, b = http_get(f"http://{ip}:{port}/json/version")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    if "Browser" not in data and "User-Agent" not in data and "webSocketDebuggerUrl" not in data:
        return None
    browser_version = data.get("Browser", "") or data.get("V8-Version", "")
    # Distinguish Browserless / Playwright / raw Chromium
    s2, _, b2 = http_get(f"http://{ip}:{port}/")
    text = b2.decode("utf-8", errors="ignore").lower() if b2 else ""
    plat = "Chrome DevTools Protocol (raw Chromium)"
    if "browserless" in text:
        plat = "Browserless"
    elif "playwright" in text or "playwright" in browser_version.lower():
        plat = "Playwright server"
    return {
        "platform": plat,
        "version": data.get("Browser", "") or "",
        "browser_version": browser_version,
        "auth_required": None,
        "raw_signature": "/json/version returns CDP shape",
    }


def try_selenium(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/wd/hub/status")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    val = data.get("value", {})
    if not isinstance(val, dict):
        return None
    if "ready" not in val and "build" not in val:
        return None
    build = val.get("build", {})
    version = build.get("version", "") if isinstance(build, dict) else ""
    return {
        "platform": "Selenium Grid",
        "version": version,
        "browser_version": "",
        "auth_required": None,
        "raw_signature": "/wd/hub/status returns Selenium 'value.ready' shape",
    }


def try_skyvern(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/api/v1/health")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    s2, _, b2 = http_get(f"http://{ip}:{port}/")
    is_skyvern = b2 and (b"skyvern" in b2.lower())
    if not is_skyvern:
        return None
    return {
        "platform": "Skyvern",
        "version": "",
        "browser_version": "",
        "auth_required": None,
        "raw_signature": "/api/v1/health + skyvern marker",
    }


PLATFORM_HANDLERS = {
    3000: [try_cdp, try_skyvern],
    4444: [try_selenium, try_cdp],
    8000: [try_skyvern, try_cdp],
    9222: [try_cdp],
}


def probe_target(target: str, ports: list[int]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        handlers = PLATFORM_HANDLERS.get(p) or [try_cdp, try_selenium, try_skyvern]
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
