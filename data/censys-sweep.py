#!/usr/bin/env python3
"""
censys-sweep.py -- Censys v2 host search for AI/LLM infrastructure.

Cross-population complement to JAXEN/Shodan: queries Censys Search API v2,
extracts IPs + SAN cert data, diffs against existing Shodan hit list to
surface the "third population" Shodan missed.

Usage:
  python3 censys-sweep.py --query '<censys-query>' --slug <slug> \
    [--shodan-hits /tmp/shodan-<slug>-hits.txt] \
    [--out /tmp/censys-<slug>-hits.txt] \
    [--out-dir ~/recon/<slug>-<date>/] \
    [--max-pages 20]

Credentials (checked in priority order):
  1. CENSYS_API_ID / CENSYS_API_SECRET env vars
  2. ~/.config/censys/config.ini  [DEFAULT] api_id / api_secret

Outputs:
  censys-<slug>-hits.txt   all IPs from Censys (one per line)
  censys-<slug>-delta.txt  IPs not in Shodan hits (new cross-pop)
  censys-<slug>-sans.json  SAN list per IP for VisorGraph cert-pivot
  censys-<slug>-raw.json   full Censys hit objects

Exit codes:
  0  success (including 0-result queries)
  1  credentials not configured
  2  API error
"""

import argparse
import base64
import json
import os
import sys
import time
from configparser import ConfigParser
from pathlib import Path

import requests

CENSYS_SEARCH_URL = "https://search.censys.io/api/v2/hosts/search"
PAGE_SIZE = 100
RATE_SLEEP = 0.4  # polite gap between pages


def load_credentials():
    api_id = os.environ.get("CENSYS_API_ID")
    secret = os.environ.get("CENSYS_API_SECRET")
    if api_id and secret:
        return api_id, secret

    cfg_path = Path.home() / ".config" / "censys" / "config.ini"
    if cfg_path.exists():
        cfg = ConfigParser()
        cfg.read(cfg_path)
        # censys SDK writes [DEFAULT] with api_id/api_secret
        section = None
        if "DEFAULT" in cfg:
            section = cfg["DEFAULT"]
        elif cfg.sections():
            section = cfg[cfg.sections()[0]]
        if section:
            aid = section.get("api_id") or section.get("API_ID")
            sec = section.get("api_secret") or section.get("API_SECRET")
            if aid and sec:
                return aid, sec

    return None, None


def build_auth_header(api_id, secret):
    token = base64.b64encode(f"{api_id}:{secret}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def search_hosts(query, api_id, secret, max_pages=20):
    headers = build_auth_header(api_id, secret)
    results = []
    cursor = None
    page = 0

    while page < max_pages:
        payload = {"q": query, "per_page": PAGE_SIZE}
        if cursor:
            payload["cursor"] = cursor

        try:
            resp = requests.post(
                CENSYS_SEARCH_URL, json=payload, headers=headers, timeout=30
            )
        except requests.RequestException as e:
            print(f"  ERROR: request failed: {e}", file=sys.stderr)
            sys.exit(2)

        if resp.status_code == 401:
            print("  ERROR: Censys 401 — check CENSYS_API_ID / CENSYS_API_SECRET", file=sys.stderr)
            sys.exit(1)

        if resp.status_code == 429:
            print("  rate-limited; sleeping 60s", file=sys.stderr)
            time.sleep(60)
            continue

        if resp.status_code != 200:
            print(f"  ERROR: Censys returned HTTP {resp.status_code}: {resp.text[:200]}", file=sys.stderr)
            sys.exit(2)

        data = resp.json()
        hits = data.get("result", {}).get("hits", [])
        results.extend(hits)

        total = data.get("result", {}).get("total", 0)
        next_cursor = data.get("result", {}).get("links", {}).get("next")

        page += 1
        print(
            f"  page {page}: +{len(hits)} hits  (total reported: {total}, collected: {len(results)})",
            file=sys.stderr,
        )

        if not hits or not next_cursor:
            break

        cursor = next_cursor
        time.sleep(RATE_SLEEP)

    return results


def extract_sans(hits):
    san_map = {}
    for h in hits:
        ip = h.get("ip")
        if not ip:
            continue
        sans = set()
        for svc in h.get("services", []):
            cert = svc.get("certificate", {})
            leaf = cert.get("leaf_data", cert)  # v2 may nest differently
            names = leaf.get("names", [])
            if isinstance(names, list):
                sans.update(n for n in names if n)
        if sans:
            san_map[ip] = sorted(sans)
    return san_map


def load_shodan_ips(path):
    if not path:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    ips = set()
    for line in p.read_text().splitlines():
        ip = line.split(":")[0].strip()
        if ip:
            ips.add(ip)
    return ips


def main():
    ap = argparse.ArgumentParser(
        description="Censys v2 host sweep — cross-population complement to JAXEN/Shodan"
    )
    ap.add_argument("--query", required=True, help="Censys query string")
    ap.add_argument("--slug", required=True, help="Survey slug (e.g. argo, rag, ollama)")
    ap.add_argument("--shodan-hits", help="Existing Shodan hits file for cross-reference diff")
    ap.add_argument("--out", help="Output path for all Censys IPs (default: /tmp/censys-<slug>-hits.txt)")
    ap.add_argument("--out-dir", help="Directory for delta/SANs/raw outputs (default: /tmp)")
    ap.add_argument(
        "--max-pages",
        type=int,
        default=20,
        help="Max pages to fetch (default: 20 = up to 2000 hosts); controls API quota burn",
    )
    args = ap.parse_args()

    api_id, secret = load_credentials()
    if not api_id or not secret:
        print(
            "  WARN: No Censys credentials — set CENSYS_API_ID/CENSYS_API_SECRET "
            "or run: censys config  (pip install censys)",
            file=sys.stderr,
        )
        print("  → censys step skipped (no credentials)")
        sys.exit(1)

    out_path = Path(args.out or f"/tmp/censys-{args.slug}-hits.txt")
    out_dir = Path(args.out_dir) if args.out_dir else Path("/tmp")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"  query : {args.query}", file=sys.stderr)
    print(f"  limit : {args.max_pages} pages ({args.max_pages * PAGE_SIZE} hosts max)", file=sys.stderr)

    hits = search_hosts(args.query, api_id, secret, max_pages=args.max_pages)

    ips = sorted(set(h["ip"] for h in hits if h.get("ip")))
    out_path.write_text("\n".join(ips) + ("\n" if ips else ""))
    print(f"  → {len(ips)} unique IPs  →  {out_path}")

    shodan_ips = load_shodan_ips(args.shodan_hits)
    delta = [ip for ip in ips if ip not in shodan_ips]
    delta_path = out_dir / f"censys-{args.slug}-delta.txt"
    delta_path.write_text("\n".join(delta) + ("\n" if delta else ""))
    print(f"  → {len(delta)} delta IPs (not in Shodan)  →  {delta_path}")

    if shodan_ips and ips:
        overlap = len(set(ips) & shodan_ips)
        pct = round(100 * overlap / len(ips))
        print(f"  → overlap with Shodan: {overlap}/{len(ips)} ({pct}%)")

    san_map = extract_sans(hits)
    sans_path = out_dir / f"censys-{args.slug}-sans.json"
    json.dump(san_map, open(sans_path, "w"), indent=2)
    print(f"  → {len(san_map)} IPs with cert SANs  →  {sans_path}")

    raw_path = out_dir / f"censys-{args.slug}-raw.json"
    json.dump(hits, open(raw_path, "w"), indent=2)
    print(f"  → raw hits  →  {raw_path}")


if __name__ == "__main__":
    main()
