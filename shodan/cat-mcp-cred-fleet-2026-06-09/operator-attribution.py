#!/usr/bin/env python3
"""
operator-attribution.py - NICE 541 cert/whois pivot for the MCP cred-fleet.

Restraint-clean reads:
  - reverse DNS (PTR lookup)
  - WHOIS RDAP via rdap.arin.net + delegated registries (HTTP read)
  - TLS direct-IP no-SNI cert read (surface customer OV/EV per ref_ov_cert_attribution)

Output: operator-attribution.json with per-host metadata and cluster summary.
"""
import json
import socket
import ssl
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from pathlib import Path


def rdns(ip, timeout=4):
    socket.setdefaulttimeout(timeout)
    try:
        return socket.gethostbyaddr(ip)[0]
    except Exception:
        return None


def rdap(ip, timeout=8):
    """ARIN RDAP redirects to the correct registry."""
    try:
        url = f"https://rdap.arin.net/registry/ip/{ip}"
        req = urllib.request.Request(url, headers={"Accept": "application/rdap+json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
            name = data.get("name", "")
            handle = data.get("handle", "")
            country = data.get("country", "")
            # walk entities for orgs
            orgs = []
            for e in data.get("entities", []) or []:
                roles = e.get("roles", []) or []
                vcard = e.get("vcardArray", []) or []
                if isinstance(vcard, list) and len(vcard) > 1:
                    for entry in vcard[1]:
                        if isinstance(entry, list) and len(entry) >= 4 and entry[0] == "fn":
                            orgs.append({"roles": roles, "name": entry[3]})
            cidr = ""
            for c in data.get("cidr0_cidrs", []) or []:
                cidr = f'{c.get("v4prefix") or c.get("v6prefix")}/{c.get("length")}'
                break
            return {"name": name, "handle": handle, "country": country, "cidr": cidr, "entities": orgs}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def cert_cn(ip, port=9090, timeout=6):
    """No-SNI direct-IP cert read. Captures customer OV/EV per Nick's lesson."""
    try:
        ctx = ssl._create_unverified_context()
        with socket.create_connection((ip, port), timeout=timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=None) as s:
                der = s.getpeercert(binary_form=True)
                # Parse subject/issuer cheaply via re-load
        # Re-handshake to get parsed cert (some servers won't expose without SNI)
        ctx2 = ssl._create_unverified_context()
        with socket.create_connection((ip, port), timeout=timeout) as raw:
            with ctx2.wrap_socket(raw) as s:
                cert = s.getpeercert()
                if not cert:
                    cert = {}
                subj = dict(x[0] for x in cert.get("subject", []) if x)
                iss = dict(x[0] for x in cert.get("issuer", []) if x)
                sans = [x[1] for x in cert.get("subjectAltName", []) if x]
                return {
                    "subject_cn": subj.get("commonName"),
                    "subject_o": subj.get("organizationName"),
                    "issuer_cn": iss.get("commonName"),
                    "issuer_o": iss.get("organizationName"),
                    "sans": sans,
                    "not_after": cert.get("notAfter"),
                }
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def attribute(ip):
    rec = {"ip": ip, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    rec["rdns"] = rdns(ip)
    rec["rdap"] = rdap(ip)
    rec["cert"] = cert_cn(ip, 9090)
    # /16 cluster key
    rec["slash16"] = ".".join(ip.split(".")[:2]) + ".0.0/16"
    return rec


def cluster(records):
    asn_org = Counter()
    countries = Counter()
    slash16 = Counter()
    cert_issuers = Counter()
    cert_subjects = Counter()
    rdns_suffixes = Counter()
    for r in records:
        rdap_d = r.get("rdap") or {}
        org_names = [e.get("name") for e in rdap_d.get("entities", []) or [] if e.get("name")]
        org = org_names[0] if org_names else rdap_d.get("name") or "?"
        asn_org[org] += 1
        countries[rdap_d.get("country") or "?"] += 1
        slash16[r.get("slash16") or "?"] += 1
        cert_d = r.get("cert") or {}
        cert_issuers[cert_d.get("issuer_cn") or cert_d.get("issuer_o") or "?"] += 1
        cert_subjects[cert_d.get("subject_cn") or "?"] += 1
        rdns_v = r.get("rdns")
        if rdns_v:
            parts = rdns_v.split(".")
            suffix = ".".join(parts[-3:]) if len(parts) >= 3 else rdns_v
            rdns_suffixes[suffix] += 1
    return {
        "operator_org_distribution": dict(asn_org),
        "country_distribution": dict(countries),
        "slash16_distribution": dict(slash16),
        "cert_issuer_distribution": dict(cert_issuers),
        "cert_subject_cn_distribution": dict(cert_subjects),
        "rdns_suffix_distribution": dict(rdns_suffixes),
    }


def main():
    if len(sys.argv) < 3:
        print("usage: operator-attribution.py <ip_list> <out.json>", file=sys.stderr)
        sys.exit(2)
    ips = [x.strip() for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
    out_path = Path(sys.argv[2])
    print(f"[+] attribution on {len(ips)} hosts (rdns + rdap + no-SNI cert)", file=sys.stderr)
    results = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(attribute, ip): ip for ip in ips}
        done = 0
        for f in as_completed(futs):
            try:
                rec = f.result()
            except Exception as e:
                rec = {"ip": futs[f], "error": f"{type(e).__name__}: {e}"}
            results.append(rec)
            done += 1
            tag = rec.get("rdap", {}).get("name", "?")
            print(f"[{done:>3}/{len(ips)}] {rec['ip']:<16} rdap={tag} rdns={rec.get('rdns')}", file=sys.stderr)
    cluster_s = cluster(results)
    out = {"hosts": results, "cluster_summary": cluster_s}
    out_path.write_text(json.dumps(out, indent=2))
    print(f"[+] -> {out_path}", file=sys.stderr)
    print(json.dumps(cluster_s, indent=2))


if __name__ == "__main__":
    main()
