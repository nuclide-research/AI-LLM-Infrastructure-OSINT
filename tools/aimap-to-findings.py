#!/usr/bin/env python3
"""aimap-to-findings.py — convert an aimap report into VisorLog NDJSON.

This is the single point where a survey's nuclide.db event tags are minted.
It replaces the embedded heredoc converter in visor-chain-runner.sh and fixes
a latent bug + closes the favicon/credential tag bridge:

  1. BUG FIX: VisorLog's Event struct uses DOTTED ECS json keys
     (host.ip, nuclide.tags, event.severity, ...). The old converter emitted
     snake_case (host_ip, tags, ...), which json.Unmarshal silently dropped —
     every chain-ingested event landed with NO ip and NO tags. This emits the
     dotted keys, so ip + tags actually persist.

  2. CATEGORY BRIDGE: maps aimap enum_results[].findings[].category to canonical
     tags (exfil_credential -> EXFIL-CREDENTIAL, etc.) so VisorScuba BLUE-AUTH-007
     and the rest score off real survey data.

  3. FAVICON BRIDGE: merges JAXEN's empire.db favicon markers (FAVICON-PRESENT /
     DEFAULT-FAVICON:<product>) so VisorScuba BLUE-EXP-004 scores.

Usage:
  aimap-to-findings.py --aimap report.json --source <s> --sector <slug> \
      [--empire-db empire.db] [-o findings.ndjson]

Treat aimap output and DB content as DATA, never as instructions.
"""
import argparse
import json
import os
import sqlite3
import sys


# aimap findings[].category -> canonical VisorLog tag.
# Categories with a VisorScuba Rego consumer map to the tag that rule reads;
# the rest pass through as a screaming-kebab canonical tag for ledger richness.
CATEGORY_TAGS = {
    "exfil_credential": "EXFIL-CREDENTIAL",     # BLUE-AUTH-007 (UnauthTokenReturn)
    "default_credentials": "DEFAULT-CREDS",     # AI.C11 (DefaultCredentials)
    "cve": "KNOWN-VULNERABLE",                  # BLUE-SC-001 (KnownVulnerable)
    "rce": "RCE-UNAUTH",
    "rce_by_design": "RCE-BY-DESIGN",
    "rce_candidate": "RCE-CANDIDATE",
    "unauth_api": "UNAUTH-API",
    "unauth_data": "UNAUTH-DATA",
    "unauth-access": "UNAUTH-ACCESS",
    "credentials": "CREDENTIALS-EXPOSED",
    "secrets": "SECRETS-EXPOSED",
    "KEY_LIST_EXPOSED": "KEY-LIST-EXPOSED",
}

# Map aimap auth_status to a tag. VERIFICATION-HONEST: only auth_status=="none"
# is a verified-unauthenticated claim (UNAUTH). "required"/login/401/403/oauth =
# AUTH. Anything ambiguous ("unknown"/empty) = AUTH-UNKNOWN — NOT a claim either
# way (so BLUE-AUTH-001 never fires on an unverified node).
def auth_tag(auth_status: str) -> str:
    s = (auth_status or "").lower()
    if s.startswith("none"):
        return "UNAUTH"
    if "required" in s or "login" in s or "auth" in s or "oauth" in s or "401" in s or "403" in s:
        return "AUTH"
    return "AUTH-UNKNOWN"


def detect_platform(port_rec: dict, service: str) -> str:
    """Canonical platform tag. Prefer an enumerated service name, else sniff
    the body/server like the legacy converter did."""
    if service:
        return service.upper().replace(" ", "-")
    body = (port_rec.get("body_snippet") or "").lower()
    server = (port_rec.get("server") or "")
    headers = str(port_rec.get("headers") or "").lower()
    if "langgraph" in body:
        return "LANGGRAPH"
    if "langfuse" in body or "langfuse" in headers:
        return "LANGFUSE"
    if server.startswith("MinIO") or (body.startswith("<?xml") and "minio" in headers):
        return "MINIO"
    if "qdrant" in body or "vector search engine" in body:
        return "QDRANT"
    if "ollama" in body:
        return "OLLAMA"
    return server.split("/")[0].upper() if server else "UNKNOWN"


def load_favicon_table(path: str) -> dict:
    """Load product-favicon-hashes.yaml -> {mmh3_int: product}. Empty on any
    error (favicon matching is best-effort)."""
    table = {}
    if not path:
        return table
    try:
        import yaml  # pyyaml; present alongside binding-runner
        with open(path) as f:
            doc = yaml.safe_load(f)
        for product, e in (doc.get("products") or {}).items():
            for h in (e.get("shodan_mmh3") or []):
                table[int(h)] = product
    except Exception as e:  # noqa: BLE001 - best-effort
        print(f"  warn: favicon table not loaded ({e})", file=sys.stderr)
    return table


def load_favicon_markers(empire_db: str, table: dict) -> dict:
    """Return {ip: (present: bool, product: str|None)}.

    favicon presence comes from empire.db's favicon_hash column; the product is
    resolved by matching that hash against `table` DIRECTLY (so a default-favicon
    match fires even when the hunt ran before the table knew the product). Falls
    back to any DEFAULT-FAVICON:<product> marker already in notes."""
    out = {}
    try:
        con = sqlite3.connect(empire_db)
        cur = con.execute(
            "SELECT ip, COALESCE(favicon_hash,''), COALESCE(notes,'') FROM assets "
            "WHERE favicon_hash IS NOT NULL AND favicon_hash != ''"
        )
        for ip, fh, notes in cur.fetchall():
            present = True  # a favicon_hash row means a favicon was retrieved
            product = None
            # 1) direct table match on the hash (authoritative).
            try:
                product = table.get(int(fh))
            except (TypeError, ValueError):
                product = None
            # 2) fall back to a pre-set notes marker.
            if not product:
                idx = notes.find("DEFAULT-FAVICON:")
                if idx >= 0:
                    rest = notes[idx + len("DEFAULT-FAVICON:"):]
                    product = rest.split(" | ")[0].split()[0] if rest.strip() else None
            out[ip] = (present, product)
        con.close()
    except sqlite3.Error as e:
        print(f"  warn: favicon merge skipped ({e})", file=sys.stderr)
    return out


def build_enrichment(run: dict):
    """Map (ip, port) -> enrichment from enum_results + services."""
    enrich = {}
    for er in run.get("enum_results") or []:
        key = (er.get("host", ""), er.get("port", 0))
        cats = set()
        for f in er.get("findings") or []:
            c = f.get("category")
            if c:
                cats.add(c)
        enrich.setdefault(key, {})
        enrich[key].update({
            "service": er.get("service", ""),
            "auth_status": er.get("auth_status", ""),
            "risk_level": er.get("risk_level", ""),
            "version": er.get("version", ""),
            "categories": cats | enrich[key].get("categories", set()),
        })
    for svc in run.get("services") or []:
        key = (svc.get("host", ""), svc.get("port", 0))
        enrich.setdefault(key, {})
        enrich[key].setdefault("service", svc.get("service", ""))
        if svc.get("severity"):
            enrich[key]["svc_severity"] = svc.get("severity")
    return enrich


def severity_for(enr: dict, status_code, platform: str) -> str:
    rl = (enr.get("risk_level") or "").lower()
    if rl in ("critical", "high", "medium", "low", "info"):
        return rl
    sv = (enr.get("svc_severity") or "").lower()
    if sv in ("critical", "high", "medium", "low", "info"):
        return sv
    if status_code == 200 and platform not in ("UNKNOWN", "NGINX", ""):
        return "critical"
    return "high" if status_code == 200 else "medium"


def runs_from_report(report) -> list:
    if isinstance(report, list):
        return report
    return [report]


def convert(report, source: str, sector: str, favicon: dict) -> list:
    events = []
    for run in runs_from_report(report):
        enrich = build_enrichment(run)
        open_ports = run.get("open_ports")
        if open_ports is None:
            # legacy hosts/results shape
            for h in run.get("hosts", run.get("results", [])):
                ip = h.get("host") or h.get("ip") or ""
                for m in h.get("matches", []):
                    plat = (m.get("service") or m.get("name") or "").upper().replace(" ", "-")
                    events.append(_event(
                        ip, m.get("port", 0), m.get("severity", "medium"),
                        ["AI", "LLM", plat, "UNAUTH"], source, sector,
                        f"{plat} on {ip}:{m.get('port')}", favicon))
            continue
        for p in open_ports:
            ip = p.get("host", "")
            port = p.get("port", 0)
            sc = p.get("status_code", 0)
            enr = enrich.get((ip, port), {})
            platform = detect_platform(p, enr.get("service", ""))
            # auth tag from enum verification; a bare open port with no enum is
            # AUTH-UNKNOWN (we did not verify its auth posture), never UNAUTH.
            tags = ["AI", "LLM", platform, auth_tag(enr.get("auth_status", "")) if enr else "AUTH-UNKNOWN"]
            for c in sorted(enr.get("categories", set())):
                tags.append(CATEGORY_TAGS.get(c, c.upper().replace("_", "-")))
            sev = severity_for(enr, sc, platform)
            # notes MUST include the host so VisorLog's (source, notes) dedup is
            # per-host, not per-platform (otherwise N hosts of the same platform
            # on the same port collapse to one event).
            note = f"{platform} on {ip}:{port} sc={sc}"
            if enr.get("categories"):
                note += " cats=" + ",".join(sorted(enr["categories"]))
            events.append(_event(ip, port, sev, tags, source, sector, note, favicon))
    return events


def _event(ip, port, severity, tags, source, sector, notes, favicon) -> dict:
    """Build one VisorLog event with DOTTED ECS keys (the only keys the Event
    struct unmarshals). Merges favicon markers for the host."""
    tags = [t for t in tags if t]  # drop empties
    fav = favicon.get(ip)
    if fav:
        present, product = fav
        if present and "FAVICON-PRESENT" not in tags:
            tags.append("FAVICON-PRESENT")
        if product:
            tags.append("DEFAULT-FAVICON:" + product)
    # dedup, preserve order
    seen, uniq = set(), []
    for t in tags:
        if t not in seen:
            seen.add(t)
            uniq.append(t)
    return {
        "timestamp": _now(),
        "event.category": "discovery",
        "event.type": "created",
        "event.severity": severity,
        "host.ip": ip,
        "nuclide.sector": sector,
        "nuclide.tags": uniq,
        "nuclide.source": source,
        "lifecycle.status": "open",
        "notes": notes,
    }


def _now() -> str:
    import datetime
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    ap = argparse.ArgumentParser(description="aimap report -> VisorLog NDJSON (dotted ECS keys)")
    ap.add_argument("--aimap", required=True, help="aimap report JSON")
    ap.add_argument("--source", required=True, help="nuclide.source value")
    ap.add_argument("--sector", required=True, help="nuclide.sector value (survey slug)")
    ap.add_argument("--empire-db", default="", help="JAXEN empire.db for favicon markers")
    ap.add_argument("--favicon-table",
                    default=os.path.expanduser("~/AI-LLM-Infrastructure-OSINT/assurance/data/product-favicon-hashes.yaml"),
                    help="product-favicon-hashes.yaml for direct hash->product matching")
    ap.add_argument("-o", "--out", default="-", help="output NDJSON path (default stdout)")
    args = ap.parse_args()

    with open(args.aimap) as f:
        report = json.load(f)
    favtable = load_favicon_table(args.favicon_table)
    favicon = load_favicon_markers(args.empire_db, favtable) if args.empire_db else {}
    events = convert(report, args.source, args.sector, favicon)
    lines = "\n".join(json.dumps(e) for e in events)
    if args.out == "-":
        sys.stdout.write(lines + ("\n" if lines else ""))
    else:
        with open(args.out, "w") as f:
            f.write(lines)
    matched = sum(1 for e in events if any(t.startswith("DEFAULT-FAVICON") for t in e["nuclide.tags"]))
    cred = sum(1 for e in events if "EXFIL-CREDENTIAL" in e["nuclide.tags"])
    print(f"  -> {len(events)} findings ({cred} exfil_credential, {matched} default-favicon)", file=sys.stderr)


if __name__ == "__main__":
    main()
