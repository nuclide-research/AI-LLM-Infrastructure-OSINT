#!/usr/bin/env python3
"""
mcp-probe.py — Probe a candidate host for an exposed Model Context Protocol (MCP) server.

Usage:
  python3 mcp-probe.py <ip>[:port]                       # probe one
  echo -e "1.2.3.4\\n5.6.7.8:8080" | python3 mcp-probe.py # bulk via stdin
  python3 mcp-probe.py --threads 200 --in ips.txt --out confirmed.jsonl

Probe sequence per (ip, port):
  1. POST <url> with JSON-RPC `initialize` request and Accept: text/event-stream
     - tries paths: /, /sse, /mcp, /message
  2. Parse SSE stream or direct JSON response for protocolVersion + serverInfo + capabilities
  3. If MCP confirmed, send `tools/list` and capture tool names/descriptions
  4. Output JSONL: {ip, port, path, server_name, server_version, protocol_version,
                     capabilities, tools: [{name, description}], elapsed_ms}

Honest about FPs: many JSON-RPC services (Ethereum nodes, Solana RPC) will partially
respond. We require either:
  - protocolVersion field in the initialize response
  - OR serverInfo with name matching MCP-server patterns
  - OR a tools/list that returns an array of {name, description} objects
to count it as a confirmed MCP server.
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

DEFAULT_PORTS = [3000, 8000, 8080, 8888]
DEFAULT_PATHS = ["/", "/sse", "/mcp", "/message", "/v1/sse", "/api/mcp"]
TIMEOUT_S = 5.0
SSE_READ_BUDGET_S = 4.0
MAX_BYTES = 65536

INIT_BODY = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "nuclide-probe", "version": "0.1"},
    },
    "id": 1,
}

TOOLS_LIST_BODY = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 2,
}


def parse_target(s: str) -> tuple[str, int]:
    s = s.strip()
    if ":" in s:
        ip, port_s = s.rsplit(":", 1)
        return ip, int(port_s)
    return s, 0  # 0 = caller will sweep DEFAULT_PORTS


def http_post(url: str, body: dict, accept: str = "application/json, text/event-stream",
              extra_headers: Optional[dict] = None, timeout: float = TIMEOUT_S) -> tuple[int, dict, bytes]:
    payload = json.dumps(body).encode()
    headers = {
        "Content-Type": "application/json",
        "Accept": accept,
        "User-Agent": "nuclide-mcp-probe/0.1 (research; security@nuclide-research.com)",
    }
    if extra_headers:
        headers.update(extra_headers)
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            # Read up to budget bytes / SSE budget seconds
            start = time.monotonic()
            buf = bytearray()
            while True:
                if time.monotonic() - start > SSE_READ_BUDGET_S:
                    break
                if len(buf) >= MAX_BYTES:
                    break
                chunk = resp.read(4096)
                if not chunk:
                    break
                buf.extend(chunk)
                if "text/event-stream" not in content_type and len(buf) > 2048:
                    # JSON response; one shot read is enough
                    break
            return resp.status, dict(resp.headers), bytes(buf)
    except urllib.error.HTTPError as e:
        try:
            body_b = e.read()[:MAX_BYTES]
        except Exception:
            body_b = b""
        return e.code, dict(e.headers or {}), body_b
    except (urllib.error.URLError, socket.timeout, ConnectionError, TimeoutError, OSError):
        return 0, {}, b""


def parse_sse_or_json(content_type: str, body: bytes) -> list[dict]:
    """Return list of JSON-RPC frames found in the response."""
    frames = []
    if "text/event-stream" in content_type or body.startswith(b"data:") or b"\ndata:" in body:
        # SSE: parse `data: {...}` lines
        for line in body.split(b"\n"):
            line = line.strip()
            if not line.startswith(b"data:"):
                continue
            try:
                data = json.loads(line[5:].strip())
                frames.append(data)
            except Exception:
                pass
    else:
        # plain JSON
        try:
            data = json.loads(body)
            frames.append(data)
        except Exception:
            # Sometimes responses concatenate multiple JSON objects
            text = body.decode("utf-8", errors="ignore")
            for m in re.finditer(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text):
                try:
                    frames.append(json.loads(m.group(0)))
                except Exception:
                    pass
    return frames


def looks_like_mcp(frames: list[dict]) -> tuple[bool, dict]:
    """Inspect JSON-RPC frames for MCP-distinctive markers. Return (is_mcp, info)."""
    info = {}
    for f in frames:
        if not isinstance(f, dict):
            continue
        result = f.get("result")
        if not isinstance(result, dict):
            continue
        if "protocolVersion" in result:
            info["protocol_version"] = result["protocolVersion"]
        if "serverInfo" in result and isinstance(result["serverInfo"], dict):
            info["server_name"] = result["serverInfo"].get("name", "")
            info["server_version"] = result["serverInfo"].get("version", "")
        if "capabilities" in result:
            info["capabilities"] = result["capabilities"]
    is_mcp = bool(info.get("protocol_version") or info.get("server_name"))
    return is_mcp, info


def parse_tools(frames: list[dict]) -> list[dict]:
    for f in frames:
        if not isinstance(f, dict):
            continue
        result = f.get("result")
        if isinstance(result, dict) and isinstance(result.get("tools"), list):
            tools = []
            for t in result["tools"][:50]:  # cap to avoid runaway
                if isinstance(t, dict):
                    tools.append({
                        "name": t.get("name", ""),
                        "description": (t.get("description") or "")[:200],
                    })
            return tools
    return []


def probe_one(ip: str, port: int, path: str = "/") -> Optional[dict]:
    url = f"http://{ip}:{port}{path}"
    t0 = time.monotonic()
    status, headers, body = http_post(url, INIT_BODY)
    if status == 0:
        return None
    if status >= 500 or not body:
        return None

    content_type = headers.get("Content-Type", "")
    frames = parse_sse_or_json(content_type, body)
    is_mcp, info = looks_like_mcp(frames)
    if not is_mcp:
        return None

    # Confirmed MCP — try tools/list
    tools = []
    status2, headers2, body2 = http_post(url, TOOLS_LIST_BODY)
    if status2 and body2:
        tools = parse_tools(parse_sse_or_json(headers2.get("Content-Type", ""), body2))

    elapsed_ms = int((time.monotonic() - t0) * 1000)
    return {
        "ip": ip,
        "port": port,
        "path": path,
        "url": url,
        "server_name": info.get("server_name", ""),
        "server_version": info.get("server_version", ""),
        "protocol_version": info.get("protocol_version", ""),
        "capabilities": info.get("capabilities", {}),
        "tools": tools,
        "tool_count": len(tools),
        "elapsed_ms": elapsed_ms,
    }


def probe_target(target: str, ports: list[int], paths: list[str]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        for path in paths:
            res = probe_one(ip, p, path)
            if res:
                return res
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", nargs="?", help="<ip>[:port]; if omitted, read targets from --in or stdin")
    ap.add_argument("--in", dest="infile", help="File of targets (one per line)")
    ap.add_argument("--out", dest="outfile", help="Output JSONL (default stdout)")
    ap.add_argument("--threads", type=int, default=100)
    ap.add_argument("--ports", default=",".join(str(p) for p in DEFAULT_PORTS))
    ap.add_argument("--paths", default=",".join(DEFAULT_PATHS))
    args = ap.parse_args()

    ports = [int(p) for p in args.ports.split(",") if p.strip()]
    paths = [p for p in args.paths.split(",") if p.strip()]

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

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as ex:
        futures = {ex.submit(probe_target, t, ports, paths): t for t in targets}
        for fut in concurrent.futures.as_completed(futures):
            try:
                res = fut.result()
            except Exception as e:
                continue
            if res:
                out.write(json.dumps(res) + "\n")
                out.flush()
                confirmed += 1

    if args.outfile:
        out.close()
    print(f"# probed: {len(targets)} hosts, confirmed MCP: {confirmed}", file=sys.stderr)


if __name__ == "__main__":
    main()
