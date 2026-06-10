#!/usr/bin/env python3
"""Pull TLS certs via DER + cryptography parser. Required when verify=NONE so
getpeercert() returns {}."""
import json
import socket
import ssl
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.backends import default_backend


def parse_der(der):
    cert = x509.load_der_x509_certificate(der, default_backend())
    def attrs(name):
        return {a.oid._name: a.value for a in name}
    subj = attrs(cert.subject)
    iss = attrs(cert.issuer)
    sans = []
    try:
        ext = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
        for n in ext.value:
            sans.append(str(n.value))
    except Exception:
        pass
    return {
        "subject": subj,
        "issuer": iss,
        "sans": sans,
        "not_before": cert.not_valid_before_utc.isoformat() if hasattr(cert, "not_valid_before_utc") else str(cert.not_valid_before),
        "not_after": cert.not_valid_after_utc.isoformat() if hasattr(cert, "not_valid_after_utc") else str(cert.not_valid_after),
        "serial": format(cert.serial_number, "x"),
    }


def grab(ip, port=9090, timeout=6):
    ctx = ssl._create_unverified_context()
    out = {"ip": ip, "port": port}
    for sni in (ip, None):
        try:
            with socket.create_connection((ip, port), timeout=timeout) as raw:
                with ctx.wrap_socket(raw, server_hostname=sni) as s:
                    der = s.getpeercert(binary_form=True)
                    if der:
                        out[f"sni_{sni or 'none'}"] = parse_der(der)
                        return out
        except Exception as e:
            out[f"sni_{sni or 'none'}_err"] = f"{type(e).__name__}: {e}"
    return out


def main():
    ips = [x.strip() for x in Path(sys.argv[1]).read_text().splitlines() if x.strip()]
    results = []
    with ThreadPoolExecutor(max_workers=10) as ex:
        futs = {ex.submit(grab, ip): ip for ip in ips}
        done = 0
        for f in as_completed(futs):
            try:
                results.append(f.result())
            except Exception as e:
                results.append({"ip": futs[f], "error": str(e)})
            done += 1
    out = Path(sys.argv[2])
    out.write_text(json.dumps(results, indent=2))
    from collections import Counter
    issuers = Counter()
    subjects = Counter()
    sans = Counter()
    for r in results:
        for k in r:
            if k.startswith("sni_") and isinstance(r[k], dict):
                d = r[k]
                issuers[d["issuer"].get("commonName") or d["issuer"].get("organizationName") or "?"] += 1
                subjects[d["subject"].get("commonName") or "?"] += 1
                for s in d.get("sans", []):
                    sans[s] += 1
                break
    print(f"issuers: {dict(issuers)}")
    print(f"top subjects: {dict(subjects.most_common(10))}")
    print(f"top sans: {dict(sans.most_common(10))}")


if __name__ == "__main__":
    main()
