#!/usr/bin/env python3
"""ComfyUI deepen — restraint-bounded per-host enrichment.

For each confirmed-unauth host:
  - GET /object_info  → enumerate installed custom-node MODULE NAMES (counts
                         the loadout but does NOT pull node parameters or
                         metadata payloads).
  - GET /queue        → queue length (running + pending), NOT contents.
  - GET /history?max_items=1  → completed-job COUNT only, NOT job contents.

We never read /history's actual prompt text, we never download /view/<file>,
we never POST /prompt. Names + counts + lengths only.
"""
import concurrent.futures as cf
import json
import socket
import ssl
import sys
import urllib.request
import urllib.error
from collections import Counter
from pathlib import Path

TIMEOUT = 8
HEADERS = {"User-Agent": "NuClide-Research/comfyui-deepen-2026-06-08"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=TIMEOUT, context=CTX)


def deepen(ip: str) -> dict:
    out = {"ip": ip}
    base = f"http://{ip}:8188"
    # /object_info → top-level keys are node-class names; count them
    try:
        r = get(f"{base}/object_info")
        body = r.read(2_500_000).decode("utf-8", "replace")  # may be MB-class
        try:
            doc = json.loads(body)
        except json.JSONDecodeError:
            out["object_info_err"] = "not_json"
            doc = None
        if isinstance(doc, dict):
            node_classes = list(doc.keys())
            out["node_class_count"] = len(node_classes)
            # bucket by python module prefix (e.g. "nodes_audio.LoadAudio" → "nodes_audio")
            buckets = Counter()
            for nm in node_classes:
                # ComfyUI v0.20+ namespaces nodes via "_": we'll bucket by case-folded prefix word
                key = nm.split("_")[0] if "_" in nm else (nm.split(" ")[0] if " " in nm else nm)
                buckets[key[:30]] += 1
            out["node_top_buckets"] = dict(buckets.most_common(15))
            # detect known-vulnerable / common custom node families by NAME PRESENCE only
            wellknown = {
                "ComfyUI-Manager": "ComfyUI-Manager",  # package mgr — can install arbitrary nodes
                "ComfyUI-Impact": "ComfyUI-Impact-Pack",
                "ComfyUI-Custom-Scripts": "ComfyUI-Custom-Scripts",
                "ReActor": "ReActor (face swap — content risk)",
                "WAS_Node_Suite": "WAS Node Suite",
                "rgthree": "rgthree-comfy",
                "AnimateDiff": "AnimateDiff",
                "ControlNet": "ControlNet",
                "IPAdapter": "IPAdapter",
                "FaceID": "FaceID (identity model risk)",
                "Reroute": "Reroute",
            }
            seen_packages = []
            joined_keys = "|".join(node_classes)
            for needle, label in wellknown.items():
                if needle.lower() in joined_keys.lower():
                    seen_packages.append(label)
            out["custom_node_packages_present"] = seen_packages[:20]
    except urllib.error.HTTPError as e:
        out["object_info_status"] = f"http_{e.code}"
    except Exception as e:
        out["object_info_err"] = type(e).__name__

    # /queue → running + pending counts (no contents)
    try:
        r = get(f"{base}/queue")
        body = r.read(200_000).decode("utf-8", "replace")
        try:
            doc = json.loads(body)
            out["queue_running"] = len(doc.get("queue_running") or [])
            out["queue_pending"] = len(doc.get("queue_pending") or [])
        except json.JSONDecodeError:
            out["queue_err"] = "not_json"
    except urllib.error.HTTPError as e:
        out["queue_status"] = f"http_{e.code}"
    except Exception as e:
        out["queue_err"] = type(e).__name__

    # /history?max_items=1 → does the host have any history? count via length
    try:
        r = get(f"{base}/history?max_items=1")
        body = r.read(500_000).decode("utf-8", "replace")
        try:
            doc = json.loads(body)
            if isinstance(doc, dict):
                # history is a dict keyed by prompt-id; max_items caps server-side
                # we want: is there activity?  yes/no flag, NOT contents
                out["history_has_records"] = len(doc) > 0
                out["history_records_visible"] = len(doc)
            elif isinstance(doc, list):
                out["history_records_visible"] = len(doc)
        except json.JSONDecodeError:
            out["history_err"] = "not_json"
    except urllib.error.HTTPError as e:
        out["history_status"] = f"http_{e.code}"
    except Exception as e:
        out["history_err"] = type(e).__name__

    # rDNS
    try:
        rdns = socket.gethostbyaddr(ip)[0]
        out["rdns"] = rdns
    except Exception:
        out["rdns"] = None

    return out


def main():
    ips = [l.strip() for l in Path("confirmed-unauth.txt").read_text().splitlines() if l.strip()]
    print(f"[*] deepening {len(ips)} confirmed-unauth ComfyUI hosts...", file=sys.stderr)
    results = []
    with cf.ThreadPoolExecutor(max_workers=60) as ex:
        for i, r in enumerate(ex.map(deepen, ips)):
            results.append(r)
            if (i + 1) % 25 == 0:
                print(f"[*] {i+1}/{len(ips)}", file=sys.stderr)
    Path("deepen.ndjson").write_text("\n".join(json.dumps(r) for r in results))
    print(f"[done] wrote deepen.ndjson ({len(results)} hosts)", file=sys.stderr)


if __name__ == "__main__":
    main()
