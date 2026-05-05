#!/usr/bin/env python3
"""
aisafety-probe.py — DEPRECATED 2026-05-05. DO NOT USE.

This probe used naked single-word substring matching (`b"garak" in body`,
`b"confident" in body`) and produced 6 false positives + 0 true positives
at population scale. Concrete trace: it matched a personal video clip
browser as "Garak" because an anime filename `Garakuta no Kamisama`
contained "garak" as a substring.

Superseded by aimap (https://github.com/Nicholas-Kloster/aimap), which
implements the same coverage with conjunctive structured fingerprints
(status_code + json_field + anchored body_contains, all required to fire).

See `case-studies/commercial/ai-safety-eval-cloud-survey-2026-05.md`
"Methodology correction" for the full FP analysis. Kept on disk as a
historical artifact for the methodology-correction record only.

To re-survey the AI safety eval category, use:
    aimap -list <ip-list> -ports 1984,5000,7575,8000,8080,15500

aimap covers: Promptfoo, NeMo Guardrails, DeepEval Server, LangSmith
Self-Hosted, Inspect AI, Garak REST, Lakera Guard Self-Hosted.

ORIGINAL DOCSTRING (do not rely on):
  Platforms detected:
    - Promptfoo evaluators — port 15500; /api/health + promptfoo-specific endpoints
    - Garak (NVIDIA adversarial harness) — varies; some web UIs expose /api
    - DeepEval / Confident AI — varies; /api/health
    - LangSmith self-hosted — port 1984; /api/info
  Output JSONL per confirmed host:
    {ip, port, platform, version, eval_count, auth_required, raw_signature}
"""
import sys
print("DEPRECATED: use aimap. See header docstring.", file=sys.stderr)
sys.exit(2)
# Original implementation preserved below for historical record only.
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

DEFAULT_PORTS = [1984, 5000, 8000, 15500]
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
            "User-Agent": "nuclide-aisafety-probe/0.1 (research; security@nuclide-research.com)",
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


def try_promptfoo(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/api/health")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    # Promptfoo-distinctive: /api/eval/list or /api/results
    s2, _, b2 = http_get(f"http://{ip}:{port}/api/results")
    is_pf = False
    if s2 == 200 and b2 and b"promptfoo" in b2.lower():
        is_pf = True
    if not is_pf:
        s3, _, b3 = http_get(f"http://{ip}:{port}/")
        if s3 == 200 and b3 and (b"promptfoo" in b3.lower() or b"PromptFoo" in b3):
            is_pf = True
    if not is_pf:
        return None
    return {
        "platform": "Promptfoo",
        "version": data.get("version", "") if isinstance(data.get("version"), str) else "",
        "auth_required": None,
        "raw_signature": "/api/health + promptfoo marker",
    }


def try_langsmith(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/api/info")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    text = json.dumps(data).lower()
    if "langsmith" not in text and "langchain" not in text:
        return None
    return {
        "platform": "LangSmith self-hosted",
        "version": data.get("version", "") if isinstance(data.get("version"), str) else "",
        "auth_required": None,
        "raw_signature": "/api/info with langsmith/langchain marker",
    }


def try_deepeval(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/api/health")
    if s != 200 or not b:
        return None
    text = b.decode("utf-8", errors="ignore").lower()
    if "deepeval" not in text and "confident" not in text:
        return None
    return {
        "platform": "DeepEval / Confident AI",
        "version": "",
        "auth_required": None,
        "raw_signature": "/api/health with deepeval marker",
    }


def try_garak_web(ip: str, port: int) -> Optional[dict]:
    s, _, b = http_get(f"http://{ip}:{port}/")
    if s != 200 or not b:
        return None
    text = b.decode("utf-8", errors="ignore").lower()
    if "garak" not in text:
        return None
    return {
        "platform": "Garak (NVIDIA)",
        "version": "",
        "auth_required": None,
        "raw_signature": "garak marker in HTML root",
    }


PLATFORM_HANDLERS = {
    1984: [try_langsmith],
    5000: [try_promptfoo, try_garak_web, try_deepeval],
    8000: [try_promptfoo, try_deepeval, try_langsmith, try_garak_web],
    15500: [try_promptfoo],
}


def probe_target(target: str, ports: list[int]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        handlers = PLATFORM_HANDLERS.get(p) or [
            try_promptfoo, try_langsmith, try_deepeval, try_garak_web,
        ]
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
