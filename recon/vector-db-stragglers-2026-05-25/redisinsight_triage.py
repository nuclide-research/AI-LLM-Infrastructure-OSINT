#!/usr/bin/env python3
"""RedisInsight GUI corpus triage — metadata only, no key/value reads."""

import json
import socket
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

import requests
from requests.exceptions import RequestException

TIMEOUT = 5
WORKERS = 25
PORT = 8001
REDIS_PORT = 6379

AI_LABELS = {
    "vector", "embedding", "llm", "agent", "chatbot", "rag",
    "chroma", "weaviate", "qdrant", "pinecone", "langchain",
    "openai", "anthropic", "conversation", "semantic", "model",
    "inference", "prompt", "faiss", "milvus", "pgvector",
}

HIGHVAL_LABELS = {
    "prod", "production", "ldap", "user", "users", "session",
    "password", "passwd", "credential", "auth", "account",
    "customer", "crm", "pii", "personal", "private", "secret",
    "token", "key", "admin", "billing", "payment", "finance",
    "medical", "health", "hipaa", "gdpr",
}


def check_port(ip: str, port: int) -> bool:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except Exception:
        return False


def label_flags(name: str) -> list[str]:
    n = name.lower()
    flags = []
    for kw in AI_LABELS:
        if kw in n:
            flags.append(f"AI:{kw}")
    for kw in HIGHVAL_LABELS:
        if kw in n:
            flags.append(f"HV:{kw}")
    return flags


def probe(ip: str) -> dict:
    base = f"http://{ip}:{PORT}"
    result = {
        "ip": ip,
        "responsive": False,
        "version": None,
        "databases": [],
        "db_names": [],
        "flags": [],
        "redis_6379": False,
        "error": None,
    }

    # /api/info
    try:
        r = requests.get(f"{base}/api/info", timeout=TIMEOUT)
        if r.status_code == 200:
            result["responsive"] = True
            data = r.json()
            # version may be nested
            result["version"] = (
                data.get("appVersion")
                or data.get("version")
                or data.get("buildInfo", {}).get("appVersion")
                or "unknown"
            )
    except RequestException as e:
        result["error"] = str(e)[:80]
        return result

    # /api/databases
    try:
        r = requests.get(f"{base}/api/databases", timeout=TIMEOUT)
        if r.status_code == 200:
            dbs = r.json()
            if isinstance(dbs, list):
                result["databases"] = dbs
                names = []
                for db in dbs:
                    n = db.get("name") or db.get("nameFromProvider") or ""
                    h = db.get("host", "")
                    p = db.get("port", "")
                    label = n or f"{h}:{p}"
                    if label:
                        names.append(label)
                    # gather flags
                    for field in [n, h, db.get("provider", ""), db.get("connectionType", "")]:
                        result["flags"].extend(label_flags(str(field)))
                result["db_names"] = names
    except RequestException:
        pass

    # port 6379 check
    result["redis_6379"] = check_port(ip, REDIS_PORT)

    # deduplicate flags
    result["flags"] = sorted(set(result["flags"]))
    return result


def main():
    ip_file = "/home/cowboy/AI-LLM-Infrastructure-OSINT/recon/vector-db-stragglers-2026-05-25/redisinsight-ips.txt"
    out_file = "/home/cowboy/AI-LLM-Infrastructure-OSINT/recon/vector-db-stragglers-2026-05-25/redisinsight-gui-triage.md"

    ips = []
    with open(ip_file) as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                ips.append(parts[-1])

    print(f"[*] Probing {len(ips)} IPs with {WORKERS} workers...", flush=True)

    results = []
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(probe, ip): ip for ip in ips}
        done = 0
        for fut in as_completed(futures):
            done += 1
            r = fut.result()
            results.append(r)
            status = "OK" if r["responsive"] else "MISS"
            if r["responsive"]:
                print(f"  [{status}] {r['ip']} | ver={r['version']} | dbs={len(r['db_names'])} | flags={r['flags']}", flush=True)
            if done % 10 == 0:
                print(f"  ... {done}/{len(ips)}", flush=True)

    results.sort(key=lambda x: (not x["responsive"], x["ip"]))

    responsive = [r for r in results if r["responsive"]]
    ai_hits = [r for r in responsive if any(f.startswith("AI:") for f in r["flags"])]
    hv_hits = [r for r in responsive if any(f.startswith("HV:") for f in r["flags"])]
    coloc = [r for r in responsive if r["redis_6379"]]
    elevated = sorted(
        set(r["ip"] for r in ai_hits + hv_hits),
        key=lambda ip: next(r for r in results if r["ip"] == ip)["ip"]
    )

    # Build report
    lines = [
        f"# RedisInsight GUI Corpus Triage — 2026-05-25",
        f"",
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}",
        f"",
        f"## Summary",
        f"",
        f"- {len(ips)} IPs probed",
        f"- **{len(responsive)}** instances responded",
        f"- **{len(ai_hits)}** instances with AI-adjacent database labels",
        f"- **{len(hv_hits)}** instances with production/credential labels",
        f"- **{len(coloc)}** co-located Redis (port 6379 open on same host)",
        f"",
        f"---",
        f"",
        f"## Elevated Findings",
        f"",
    ]

    if elevated:
        for ip in elevated:
            r = next(x for x in results if x["ip"] == ip)
            tag_str = ", ".join(r["flags"]) if r["flags"] else "none"
            names_str = ", ".join(r["db_names"]) if r["db_names"] else "(none listed)"
            colocated = "yes" if r["redis_6379"] else "no"
            lines += [
                f"### {ip}",
                f"- **Databases:** {names_str}",
                f"- **RedisInsight version:** {r['version']}",
                f"- **Flags:** {tag_str}",
                f"- **Co-located Redis (6379):** {colocated}",
                f"- **Raw db count:** {len(r['databases'])}",
                f"",
            ]
    else:
        lines.append("None flagged.\n")

    lines += [
        f"---",
        f"",
        f"## Full Results Table",
        f"",
        f"| IP | Databases | Version | Flags | 6379 |",
        f"|---|---|---|---|---|",
    ]

    for r in results:
        if not r["responsive"]:
            continue
        names = "; ".join(r["db_names"]) if r["db_names"] else "(none)"
        ver = r["version"] or "?"
        flags = ", ".join(r["flags"]) if r["flags"] else ""
        colocated = "yes" if r["redis_6379"] else "no"
        lines.append(f"| {r['ip']} | {names} | {ver} | {flags} | {colocated} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## Non-Responsive IPs",
        f"",
    ]
    missed = [r for r in results if not r["responsive"]]
    if missed:
        for r in missed:
            err = f" ({r['error']})" if r["error"] else ""
            lines.append(f"- {r['ip']}{err}")
    else:
        lines.append("All IPs responded.")

    lines += [
        f"",
        f"---",
        f"",
        f"## Case Study Candidates",
        f"",
        f"IPs warranting deeper investigation:",
        f"",
    ]

    # Case study candidates: AI flags + has named databases + co-located Redis
    candidates = [
        r for r in responsive
        if (any(f.startswith("AI:") for f in r["flags"]) and r["db_names"])
        or (any(f.startswith("HV:") for f in r["flags"]) and len(r["databases"]) > 1)
    ]
    if candidates:
        for r in candidates:
            lines.append(f"- **{r['ip']}** — flags: {', '.join(r['flags'])} | dbs: {', '.join(r['db_names'])}")
    else:
        lines.append("None identified at this tier.")

    report = "\n".join(lines) + "\n"

    with open(out_file, "w") as f:
        f.write(report)

    print(f"\n[+] Report written to {out_file}")
    print(f"[+] Responsive: {len(responsive)}/{len(ips)}")
    print(f"[+] AI-adjacent: {len(ai_hits)} | High-value labels: {len(hv_hits)} | Co-located: {len(coloc)}")


if __name__ == "__main__":
    main()
