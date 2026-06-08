#!/usr/bin/env python3
"""ComfyUI auth posture verifier — strict /system_stats marker probe.

Per case-studies/commercial/comfyui-cloud-survey-2026-05.md:
  - GET /system_stats must return JSON with top-level "system" AND "devices" keys
  - AS63949 honeypot salt: "wW0sffoqsk.EM"
  - 5-second timeout, read-only metadata only

NuClide restraint: names + counts only. No /history reads, no /prompt submits,
no /upload/image, no /view/<file> downloads.
"""
import concurrent.futures as cf
import json
import socket
import sys
import urllib.request
import urllib.error
from pathlib import Path

HONEYPOT_SALT = "wW0sffoqsk.EM"
TIMEOUT = 6
HEADERS = {"User-Agent": "NuClide-Research/comfyui-survey-2026-06-08"}

def probe(ip: str) -> dict:
    url = f"http://{ip}:8188/system_stats"
    out = {"ip": ip, "url": url, "verdict": "unknown"}
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(20480).decode("utf-8", "replace")
            out["status"] = r.status
            if HONEYPOT_SALT in body:
                out["verdict"] = "honeypot_as63949"
                return out
            try:
                doc = json.loads(body)
            except json.JSONDecodeError:
                out["verdict"] = "fp_not_json"
                return out
            has_system = isinstance(doc, dict) and "system" in doc
            has_devices = isinstance(doc, dict) and "devices" in doc
            if has_system and has_devices:
                out["verdict"] = "unauth_comfyui_confirmed"
                sysblock = doc.get("system", {}) or {}
                devs = doc.get("devices", []) or []
                out["os"] = sysblock.get("os", "")
                out["python"] = sysblock.get("python_version", "")[:50]
                out["comfyui_version"] = sysblock.get("comfyui_version", "")
                out["ram_total_gb"] = round((sysblock.get("ram_total") or 0) / (1024**3), 1)
                gpus = []
                vram_total = 0
                for d in devs:
                    name = d.get("name") or d.get("type") or ""
                    if name:
                        gpus.append(name[:90])
                    vram = d.get("vram_total") or 0
                    vram_total += vram
                out["gpus"] = gpus
                out["vram_total_gb"] = round(vram_total / (1024**3), 1)
            else:
                out["verdict"] = "fp_keys_missing"
    except urllib.error.HTTPError as e:
        out["verdict"] = f"http_{e.code}"
    except (urllib.error.URLError, socket.timeout, ConnectionResetError, ConnectionRefusedError, OSError) as e:
        out["verdict"] = "dead"
        out["err"] = str(e)[:80]
    except Exception as e:
        out["verdict"] = f"err_{type(e).__name__}"
        out["err"] = str(e)[:80]
    return out


def main(ip_file: str, out_file: str, workers: int = 80):
    ips = [l.strip() for l in Path(ip_file).read_text().splitlines() if l.strip() and not l.startswith("#")]
    print(f"[*] probing {len(ips)} ComfyUI candidates...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(probe, ips)):
            results.append(r)
            if (i + 1) % 100 == 0:
                print(f"[*] {i+1}/{len(ips)} done", file=sys.stderr)
    Path(out_file).write_text("\n".join(json.dumps(r) for r in results))
    # tally
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[TALLY]", file=sys.stderr)
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 80)
