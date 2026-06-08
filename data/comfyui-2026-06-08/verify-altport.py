#!/usr/bin/env python3
"""Alt-port ComfyUI verifier — probes IP:PORT pairs (any port).

Use case: 176k+ ComfyUI hits on non-default ports are cloud GPU rental proxies
(RunPod, Vast.ai, Modal, AWS direct). Shodan saw IP:PORT respond at crawl
time; verify whether the unauth /system_stats marker still holds.
"""
import concurrent.futures as cf
import json
import socket
import sys
import urllib.request
import urllib.error
from pathlib import Path

HONEYPOT_SALT = "wW0sffoqsk.EM"
TIMEOUT = 5
HEADERS = {"User-Agent": "NuClide-Research/comfyui-altport-2026-06-08"}


def probe(ip_port: str) -> dict:
    ip, port = ip_port.split(":")
    port = int(port)
    out = {"ip": ip, "port": port, "verdict": "unknown"}
    for scheme in ("http", "https"):
        url = f"{scheme}://{ip}:{port}/system_stats"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            import ssl
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as r:
                body = r.read(20480).decode("utf-8", "replace")
                out["status"] = r.status
                out["scheme"] = scheme
                if HONEYPOT_SALT in body:
                    out["verdict"] = "honeypot_as63949"
                    return out
                try:
                    doc = json.loads(body)
                except json.JSONDecodeError:
                    out["verdict"] = "fp_not_json"
                    return out
                if isinstance(doc, dict) and "system" in doc and "devices" in doc:
                    out["verdict"] = "unauth_comfyui_confirmed"
                    sysblock = doc.get("system", {}) or {}
                    devs = doc.get("devices", []) or []
                    out["os"] = sysblock.get("os", "")
                    out["comfyui_version"] = sysblock.get("comfyui_version", "")
                    out["ram_total_gb"] = round((sysblock.get("ram_total") or 0) / (1024**3), 1)
                    gpus = []
                    vram_total = 0
                    for d in devs:
                        nm = d.get("name") or d.get("type") or ""
                        if nm:
                            gpus.append(nm[:90])
                        vram_total += d.get("vram_total") or 0
                    out["gpus"] = gpus
                    out["vram_total_gb"] = round(vram_total / (1024**3), 1)
                else:
                    out["verdict"] = "fp_keys_missing"
                return out
        except urllib.error.HTTPError as e:
            out["verdict"] = f"http_{e.code}"
            return out
        except (urllib.error.URLError, socket.timeout, ConnectionResetError,
                ConnectionRefusedError, ssl.SSLError, OSError) as e:
            # try next scheme on first-fail
            if scheme == "http":
                continue
            out["verdict"] = "dead"
            out["err"] = str(e)[:80]
            return out
        except Exception as e:
            out["verdict"] = f"err_{type(e).__name__}"
            return out
    return out


def main(ip_port_file: str, out_file: str, workers: int = 200):
    pairs = [l.strip() for l in Path(ip_port_file).read_text().splitlines() if l.strip() and ":" in l]
    print(f"[*] probing {len(pairs)} IP:port pairs (workers={workers})...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=workers) as ex:
        for i, r in enumerate(ex.map(probe, pairs)):
            results.append(r)
            if (i + 1) % 200 == 0:
                print(f"[*] {i+1}/{len(pairs)} done", file=sys.stderr)
    Path(out_file).write_text("\n".join(json.dumps(r) for r in results))
    tally = {}
    for r in results:
        tally[r["verdict"]] = tally.get(r["verdict"], 0) + 1
    print("\n[TALLY]", file=sys.stderr)
    for k, v in sorted(tally.items(), key=lambda x: -x[1]):
        print(f"  {v:5d}  {k}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 200)
