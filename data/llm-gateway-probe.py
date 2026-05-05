#!/usr/bin/env python3
"""
llm-gateway-probe.py — Probe a candidate host for OpenAI-compatible LLM gateways /
self-host inference servers.

Platforms detected (port → ordered list of platform handlers):
  - LiteLLM Proxy  — port 4000 default; /health/liveliness, /metrics (litellm_*)
  - LocalAI        — port 8080 default; /readyz returns OK, /system/info
  - oobabooga      — port 5000 default; /api/v1/model, "text generation web ui" in HTML
  - LM Studio      — port 1234 default; /v1/models with LM-Studio-specific shape
  - Jan AI         — port 1337 default; /v1/models with Jan-specific shape
  - OneAPI/NewAPI  — port 3000 default; /api/status, OpenAI-compat with admin UI

Each platform has a distinct response signature; the probe matches on those rather
than relying on port alone. Distinguishes from vLLM (already surveyed) by checking
`owned_by` field — vLLM returns `"owned_by": "vllm"`, gateways have other values.

Output JSONL per confirmed host:
  {ip, port, platform, version, model_count, models, auth_required, raw_signature}

Usage:
  echo -e "1.2.3.4:4000\\n5.6.7.8:8080" | python3 llm-gateway-probe.py
  python3 llm-gateway-probe.py --in ips.txt --out confirmed.jsonl --threads 200
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

DEFAULT_PORTS = [1234, 1337, 3000, 4000, 5000, 8080]
TIMEOUT_S = 5.0
MAX_BYTES = 65536


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
            "User-Agent": "nuclide-llm-gateway-probe/0.1 (research; security@nuclide-research.com)",
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


def parse_models_endpoint(ip: str, port: int) -> Optional[dict]:
    """Try /v1/models — OpenAI-compat. Return model list or None."""
    s, _, b = http_get(f"http://{ip}:{port}/v1/models")
    auth_required = (s == 401 or s == 403)
    if s == 401 or s == 403:
        return {"auth_required": True, "models": [], "model_count": 0, "owned_by_set": set()}
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict) or "data" not in data:
        return None
    models = data.get("data", [])
    if not isinstance(models, list):
        return None
    owned_by = set()
    model_ids = []
    for m in models[:100]:
        if isinstance(m, dict):
            mid = m.get("id", "")
            if mid:
                model_ids.append(mid)
            ob = m.get("owned_by", "")
            if ob:
                owned_by.add(ob)
    return {
        "auth_required": False,
        "models": model_ids[:30],
        "model_count": len(models),
        "owned_by_set": owned_by,
    }


def try_litellm(ip: str, port: int) -> Optional[dict]:
    # LiteLLM-distinctive: /health/liveliness returns {"status": "healthy"}
    s, _, b = http_get(f"http://{ip}:{port}/health/liveliness")
    if s != 200 or not b:
        # also try /health/readiness
        s, _, b = http_get(f"http://{ip}:{port}/health/readiness")
        if s != 200 or not b:
            return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict) or "status" not in data:
        return None
    # Extra confirmation: check /metrics for litellm_ prefix
    s2, _, b2 = http_get(f"http://{ip}:{port}/metrics")
    is_litellm = (s2 == 200 and b"litellm_" in b2)
    if not is_litellm:
        # Fallback signal: /litellm/info or /v1/models with proxy-style models
        s3, _, b3 = http_get(f"http://{ip}:{port}/v1/models")
        if s3 == 200 and b3 and (b"\"object\": \"list\"" in b3 or b"\"data\":" in b3):
            is_litellm = True
    if not is_litellm:
        return None

    models_info = parse_models_endpoint(ip, port) or {}
    return {
        "platform": "LiteLLM Proxy",
        "version": "",
        "auth_required": models_info.get("auth_required"),
        "model_count": models_info.get("model_count", 0),
        "models": models_info.get("models", []),
        "owned_by": sorted(models_info.get("owned_by_set", set())),
        "raw_signature": "/health/liveliness + /metrics litellm_ prefix",
    }


def try_localai(ip: str, port: int) -> Optional[dict]:
    # LocalAI: /readyz returns plain "OK"
    s, _, b = http_get(f"http://{ip}:{port}/readyz")
    if s != 200 or b.strip() != b"OK":
        return None
    # Confirm via /system/info or /v1/models with local-model-style ids
    s2, _, b2 = http_get(f"http://{ip}:{port}/system/info")
    sys_info = None
    if s2 == 200 and b2:
        try:
            sys_info = json.loads(b2)
        except Exception:
            pass
    models_info = parse_models_endpoint(ip, port) or {}
    # LocalAI distinctive: model owned_by is often empty or "localai"
    is_localai = (
        sys_info is not None and "loaded_backends" in (sys_info or {})
    ) or (
        "localai" in {ob.lower() for ob in models_info.get("owned_by_set", set())}
    )
    if not is_localai and not sys_info:
        # weak signal: /readyz returned OK but no other LocalAI markers — likely not LocalAI
        return None
    return {
        "platform": "LocalAI",
        "version": (sys_info or {}).get("version", "") if isinstance(sys_info, dict) else "",
        "auth_required": models_info.get("auth_required"),
        "model_count": models_info.get("model_count", 0),
        "models": models_info.get("models", []),
        "owned_by": sorted(models_info.get("owned_by_set", set())),
        "raw_signature": "/readyz=OK + /system/info or owned_by=localai",
    }


def try_oobabooga(ip: str, port: int) -> Optional[dict]:
    # oobabooga: /api/v1/model returns {"result": "<model_name>"}
    s, _, b = http_get(f"http://{ip}:{port}/api/v1/model")
    if s == 200 and b:
        try:
            data = json.loads(b)
            if isinstance(data, dict) and "result" in data:
                model_name = data.get("result", "")
                # Extra: check root HTML for "text generation web ui"
                s2, _, b2 = http_get(f"http://{ip}:{port}/")
                title_match = b"text generation web ui" in b2.lower() or b"oobabooga" in b2.lower()
                models_info = parse_models_endpoint(ip, port) or {}
                return {
                    "platform": "oobabooga (Text Generation WebUI)",
                    "version": "",
                    "auth_required": models_info.get("auth_required"),
                    "model_count": models_info.get("model_count", 1) or 1,
                    "models": models_info.get("models") or [model_name] if model_name else [],
                    "owned_by": sorted(models_info.get("owned_by_set", set())),
                    "raw_signature": "/api/v1/model returns {result:...}" + (" + html title match" if title_match else ""),
                }
        except Exception:
            pass
    return None


def try_lmstudio(ip: str, port: int) -> Optional[dict]:
    # LM Studio: /v1/models returns OpenAI-compat shape with id like "publisher/model"
    info = parse_models_endpoint(ip, port)
    if not info or info.get("auth_required") or info.get("model_count", 0) == 0:
        return None
    # LM Studio model IDs typically look like "huggingface-username/model-name"
    # or have ":Q4_K_M" GGUF quant suffixes
    models = info.get("models", [])
    looks_lmstudio = any(
        ("/" in m and (":Q" in m or m.endswith(".gguf") or m.startswith("hugging") or m.startswith("lm-studio")))
        for m in models
    )
    # LM Studio also responds with "lm-studio" in some headers / has /v0/models
    if not looks_lmstudio:
        s, _, b = http_get(f"http://{ip}:{port}/v0/models")
        if s != 200:
            return None
    return {
        "platform": "LM Studio",
        "version": "",
        "auth_required": info.get("auth_required"),
        "model_count": info.get("model_count", 0),
        "models": info.get("models", []),
        "owned_by": sorted(info.get("owned_by_set", set())),
        "raw_signature": "/v1/models with LM-Studio-style GGUF model ids" + (" + /v0/models" if not looks_lmstudio else ""),
    }


def try_janai(ip: str, port: int) -> Optional[dict]:
    # Jan AI: /v1/models OpenAI-compat
    info = parse_models_endpoint(ip, port)
    if not info or info.get("auth_required") or info.get("model_count", 0) == 0:
        return None
    # Jan AI distinctive: /healthz or /api/v1/app/version returns Jan-specific data
    s, _, b = http_get(f"http://{ip}:{port}/api/v1/app/version")
    is_jan = False
    if s == 200 and b and (b"jan" in b.lower() or b"cortex" in b.lower()):
        is_jan = True
    if not is_jan:
        # Fallback: model ids that look like Jan's model registry naming
        models = info.get("models", [])
        if any("cortex" in m.lower() or m.startswith("janai/") for m in models):
            is_jan = True
    if not is_jan:
        return None
    return {
        "platform": "Jan AI / Cortex",
        "version": "",
        "auth_required": info.get("auth_required"),
        "model_count": info.get("model_count", 0),
        "models": info.get("models", []),
        "owned_by": sorted(info.get("owned_by_set", set())),
        "raw_signature": "/api/v1/app/version returns jan/cortex marker",
    }


def try_oneapi(ip: str, port: int) -> Optional[dict]:
    # OneAPI / NewAPI: /api/status returns JSON with version and oneapi-specific keys
    s, _, b = http_get(f"http://{ip}:{port}/api/status")
    if s != 200 or not b:
        return None
    try:
        data = json.loads(b)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    # OneAPI status has fields like "version", "start_time", "user_count", "channel_count"
    if "version" not in data and "start_time" not in data:
        return None
    if not any(k in data for k in ("user_count", "channel_count", "logo", "system_name")):
        return None
    info = parse_models_endpoint(ip, port) or {}
    return {
        "platform": "OneAPI / NewAPI",
        "version": data.get("version", "") if isinstance(data.get("version"), str) else "",
        "auth_required": info.get("auth_required"),
        "model_count": info.get("model_count", 0),
        "models": info.get("models", []),
        "owned_by": sorted(info.get("owned_by_set", set())),
        "system_name": data.get("system_name", ""),
        "raw_signature": "/api/status with oneapi-specific keys",
    }


def try_generic_openai_compat(ip: str, port: int) -> Optional[dict]:
    """Catch-all: any OpenAI-compat /v1/models that doesn't match known platforms.
    Tag as 'generic' so it shows up in the survey but distinct from named gateways."""
    info = parse_models_endpoint(ip, port)
    if not info or info.get("auth_required") or info.get("model_count", 0) == 0:
        return None
    owned_by = info.get("owned_by_set", set())
    # Skip vLLM — already surveyed
    if "vllm" in {ob.lower() for ob in owned_by}:
        return None
    return {
        "platform": "OpenAI-compat (generic)",
        "version": "",
        "auth_required": info.get("auth_required"),
        "model_count": info.get("model_count", 0),
        "models": info.get("models", []),
        "owned_by": sorted(owned_by),
        "raw_signature": "/v1/models OpenAI-compat, no specific platform marker",
    }


PLATFORM_HANDLERS = {
    1234: [try_lmstudio, try_generic_openai_compat],
    1337: [try_janai, try_generic_openai_compat],
    3000: [try_oneapi, try_generic_openai_compat],
    4000: [try_litellm, try_generic_openai_compat],
    5000: [try_oobabooga, try_generic_openai_compat],
    8080: [try_localai, try_litellm, try_oneapi, try_generic_openai_compat],
}


def probe_target(target: str, ports: list[int]) -> Optional[dict]:
    ip, hint_port = parse_target(target)
    sweep = [hint_port] if hint_port else ports
    for p in sweep:
        handlers = PLATFORM_HANDLERS.get(p) or [
            try_litellm, try_localai, try_oobabooga, try_lmstudio, try_janai,
            try_oneapi, try_generic_openai_compat,
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
