#!/usr/bin/env python3
"""
Epoch AI Model Database Lookup
==============================
Cross-reference model names found on exposed Ollama / vLLM / Triton instances against
the Epoch AI canonical model database for verified parameter counts, organization,
and notability.

Usage:
    epoch_lookup.py <model-name>          # fuzzy lookup
    epoch_lookup.py --org "DeepSeek"      # filter by organization
    epoch_lookup.py --country China       # filter by country
    epoch_lookup.py --since 2026-01       # filter by publication date
    epoch_lookup.py --niche               # print niche/uncommon models for Shodan queries
    epoch_lookup.py --frontier            # print frontier models worth flagging if exposed

Data source: Epoch AI Notable Models database
(https://epoch.ai/data/notable-ai-models). CSV stored at
data/epoch-ai/notable_ai_models.csv.
"""
import csv, sys, argparse, re
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "epoch-ai" / "notable_ai_models.csv"


def load():
    with open(DB, newline="") as f:
        return list(csv.DictReader(f))


def fmt_params(p):
    if not p:
        return "?"
    try:
        v = float(p)
        if v >= 1e12:
            return f"{v/1e12:.2f}T"
        if v >= 1e9:
            return f"{v/1e9:.1f}B"
        if v >= 1e6:
            return f"{v/1e6:.1f}M"
        return f"{int(v)}"
    except (ValueError, TypeError):
        return str(p)[:15]


def search(rows, query):
    q = query.lower()
    norm_q = re.sub(r'[^a-z0-9]', '', q)
    matches = []
    for r in rows:
        m = r["Model"].lower()
        norm_m = re.sub(r'[^a-z0-9]', '', m)
        score = 0
        if q in m or norm_q in norm_m:
            score = 10
        elif q in r.get("Parameters notes", "").lower():
            score = 3
        if score:
            matches.append((score, r))
    matches.sort(key=lambda x: (-x[0], x[1].get("Publication date", "")), reverse=True)
    return [m[1] for m in matches]


def print_row(r, verbose=False):
    name = r["Model"]
    org = r.get("Organization", "?")
    date = r.get("Publication date", "?")
    params = fmt_params(r.get("Parameters", ""))
    notes = r.get("Parameters notes", "")[:80]
    country = r.get("Country (of organization)", "?")
    print(f"  {name:40} | {org:20} | {date:12} | {params:8} | {country}")
    if verbose and notes:
        print(f"    notes: {notes}")


def cmd_search(args):
    rows = load()
    results = search(rows, args.query)
    if not results:
        print(f"No matches for '{args.query}'.")
        return
    print(f"# Matches for '{args.query}' ({len(results)} hit{'s' if len(results) != 1 else ''})")
    for r in results[:25]:
        print_row(r, args.verbose)


def cmd_filter(args):
    rows = load()
    out = rows
    if args.org:
        out = [r for r in out if args.org.lower() in r.get("Organization", "").lower()]
    if args.country:
        out = [r for r in out if args.country.lower() in r.get("Country (of organization)", "").lower()]
    if args.since:
        out = [r for r in out if r.get("Publication date", "") >= args.since]
    out.sort(key=lambda r: r.get("Publication date", ""), reverse=True)
    for r in out[:50]:
        print_row(r, args.verbose)


def cmd_niche(args):
    """
    Niche / uncommon model identifiers worth using as Shodan/HTTP banner queries.
    Filters: open-weights, recent, less-cited but published.
    """
    rows = load()
    keep = []
    for r in rows:
        if r.get("Open model weights?", "").lower() != "yes":
            continue
        try:
            cit = int(r.get("Citations") or 0)
        except (ValueError, TypeError):
            cit = 0
        if cit > 200:
            continue
        if r.get("Publication date", "") < "2025-01":
            continue
        keep.append(r)
    keep.sort(key=lambda r: r.get("Publication date", ""), reverse=True)
    print("# Niche open-weight models (recent, low citation count) — useful as banner-search needles\n")
    for r in keep[:60]:
        print_row(r)


def cmd_frontier(args):
    """
    Frontier / notable-discretion models — flag immediately if found on exposed infra.
    """
    rows = load()
    keep = [
        r for r in rows
        if "Discretionary" in r.get("Notability criteria", "")
        or "frontier" in r.get("Notability criteria notes", "").lower()
        or (r.get("Frontier model", "").lower() == "yes")
    ]
    keep.sort(key=lambda r: r.get("Publication date", ""), reverse=True)
    print(f"# Frontier / discretion-flag models ({len(keep)} entries)\n")
    for r in keep[:80]:
        print_row(r)


def main():
    # Shorthand: `epoch_lookup.py <query>` → `epoch_lookup.py search <query>`
    known = {"search", "filter", "niche", "frontier", "-h", "--help"}
    if len(sys.argv) >= 2 and sys.argv[1] not in known and not sys.argv[1].startswith("-"):
        sys.argv.insert(1, "search")

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    p_search = sp.add_parser("search", help="fuzzy lookup by model name")
    p_search.add_argument("query")
    p_search.add_argument("-v", "--verbose", action="store_true")

    p_filter = sp.add_parser("filter", help="filter by org/country/date")
    p_filter.add_argument("--org")
    p_filter.add_argument("--country")
    p_filter.add_argument("--since", help="YYYY-MM-DD")
    p_filter.add_argument("-v", "--verbose", action="store_true")

    sp.add_parser("niche", help="recent low-citation open-weight models (banner-search needles)")
    sp.add_parser("frontier", help="frontier / discretion-flag models")

    args = p.parse_args()

    if args.cmd == "filter":
        cmd_filter(args)
    elif args.cmd == "niche":
        cmd_niche(args)
    elif args.cmd == "frontier":
        cmd_frontier(args)
    elif args.cmd == "search":
        cmd_search(args)


if __name__ == "__main__":
    main()
