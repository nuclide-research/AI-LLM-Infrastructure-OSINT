#!/usr/bin/env python3
"""
nuclide-contact.py — Per-target disclosure-recipient discovery.

Chains authoritative sources to derive the right contacts for a coordinated-
disclosure email, ranked by confidence:

  1. WHOIS abuse contact (ARIN / RIPE / APNIC / LACNIC / AFRINIC OrgAbuseEmail)
     — authoritative on IP-block ownership; works for every IP
  2. /.well-known/security.txt (RFC 9116)
     — operator-published security contact at the org's main domain
  3. DNS SOA record technical contact
     — legacy but universally present
  4. Pattern guess + MX validation
     — security@, csirt@, incident@, abuse@, helpdesk@ at recipient domain;
       only included if the domain's MX accepts mail
  5. Operator self-attribution from /.well-known/security.txt or homepage
     metadata (links to disclosure pages, contact pages)

Usage:
  python3 nuclide-contact.py --ip 1.2.3.4
  python3 nuclide-contact.py --domain example.edu
  python3 nuclide-contact.py --ip 1.2.3.4 --domain example.edu  # combined

Output: JSON with ranked contacts and source attribution.

Skips (intentionally out of v1 scope):
  - FIRST.org CSIRT directory (no easy API; would need scraping)
  - REN-ISAC member list (members-only)
  - GovCERT / national CERT directories (per-country complexity)
"""
import argparse
import json
import re
import socket
import ssl
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Optional

EMAIL_RE = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Multi-part TLDs where the registrable domain is last 3 labels
MULTI_TLDS = {
    "ac.jp", "co.jp", "ne.jp", "or.jp", "go.jp",
    "ac.uk", "co.uk", "gov.uk", "org.uk",
    "ac.kr", "co.kr",
    "edu.au", "com.au", "gov.au",
    "edu.tw", "com.tw", "gov.tw",
    "edu.vn", "com.vn", "gov.vn",
    "edu.pk", "com.pk",
    "edu.cn", "com.cn", "gov.cn",
    "edu.in", "co.in", "gov.in",
    "ac.lk",
    "sci.am",
    "ac.za", "co.za",
}


def registrable_domain(domain: str) -> str:
    """Return the registrable domain (eTLD+1) handling common multi-part TLDs."""
    domain = domain.lower().strip(".")
    parts = domain.split(".")
    if len(parts) <= 2:
        return domain
    last2 = ".".join(parts[-2:])
    last3 = ".".join(parts[-3:]) if len(parts) >= 3 else ""
    if last3 and ".".join(parts[-2:]) in MULTI_TLDS:
        return last3
    return last2


def http_get(url: str, timeout: float = 5.0) -> tuple[int, dict, bytes]:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "nuclide-contact/0.1 (research; security@nuclide-research.com)",
            "Accept": "text/plain, text/html, application/json",
        },
    )
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE  # tolerate self-signed
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, dict(resp.headers), resp.read(64 * 1024)
    except urllib.error.HTTPError as e:
        try:
            return e.code, dict(e.headers or {}), e.read()[:64 * 1024]
        except Exception:
            return e.code, {}, b""
    except Exception:
        return 0, {}, b""


def whois_abuse(ip_or_domain: str) -> list[dict]:
    """Run whois and extract abuse-mailbox / OrgAbuseEmail contacts."""
    try:
        r = subprocess.run(
            ["whois", ip_or_domain],
            capture_output=True, text=True, timeout=15,
        )
    except Exception:
        return []
    out = r.stdout
    contacts = []
    seen = set()

    # ARIN: OrgAbuseEmail / OrgTechEmail
    for label, key in (("OrgAbuseEmail", "abuse"), ("OrgTechEmail", "tech"), ("RAbuseEmail", "abuse"), ("RTechEmail", "tech")):
        for m in re.finditer(fr"^{label}:\s*(\S+@\S+)\s*$", out, re.MULTILINE):
            email = m.group(1).lower()
            if email not in seen:
                seen.add(email)
                contacts.append({
                    "email": email,
                    "source": f"WHOIS:{label}",
                    "rank": 1 if "abuse" in label.lower() else 2,
                })

    # RIPE / APNIC: abuse-mailbox: foo@bar
    for m in re.finditer(r"^abuse-mailbox:\s*(\S+@\S+)\s*$", out, re.MULTILINE):
        email = m.group(1).lower()
        if email not in seen:
            seen.add(email)
            contacts.append({"email": email, "source": "WHOIS:abuse-mailbox", "rank": 1})

    # Generic email scan as last resort
    if not contacts:
        for m in EMAIL_RE.finditer(out):
            email = m.group(0).lower()
            if email not in seen and "noreply" not in email and "registry" not in email.split("@")[0]:
                seen.add(email)
                contacts.append({"email": email, "source": "WHOIS:body-scan", "rank": 4})
                if len(contacts) >= 3:
                    break

    # Capture OrgName for context
    org_match = re.search(r"^(?:OrgName|org-name|owner):\s*(.+)$", out, re.MULTILINE | re.IGNORECASE)
    netname_match = re.search(r"^(?:NetName|netname):\s*(.+)$", out, re.MULTILINE | re.IGNORECASE)
    return contacts, {
        "org_name": org_match.group(1).strip() if org_match else "",
        "net_name": netname_match.group(1).strip() if netname_match else "",
    }


def security_txt(domain: str) -> list[dict]:
    """Fetch /.well-known/security.txt per RFC 9116."""
    contacts = []
    seen = set()
    for scheme in ("https", "http"):
        for path in ("/.well-known/security.txt", "/security.txt"):
            url = f"{scheme}://{domain}{path}"
            status, _, body = http_get(url)
            if status != 200 or not body:
                continue
            text = body.decode("utf-8", errors="replace")
            # Parse "Contact:" directives
            for m in re.finditer(r"^Contact:\s*(\S+)\s*$", text, re.MULTILINE | re.IGNORECASE):
                v = m.group(1)
                if v.startswith("mailto:"):
                    email = v[7:].lower()
                elif "@" in v:
                    email = v.lower()
                else:
                    continue  # tel: or url
                if email and email not in seen:
                    seen.add(email)
                    contacts.append({
                        "email": email,
                        "source": f"security.txt:{url}",
                        "rank": 0,  # highest priority — operator-published
                    })
            if contacts:
                return contacts
    return contacts


def dns_soa_contact(domain: str) -> list[dict]:
    """SOA record's RNAME field (admin email, dot-encoded)."""
    try:
        r = subprocess.run(["dig", "+short", "SOA", domain], capture_output=True, text=True, timeout=8)
    except Exception:
        return []
    if r.returncode != 0 or not r.stdout.strip():
        return []
    parts = r.stdout.strip().split()
    if len(parts) < 2:
        return []
    rname = parts[1].rstrip(".")
    # SOA RNAME format: first dot is @
    idx = rname.find(".")
    if idx < 0:
        return []
    email = rname[:idx] + "@" + rname[idx + 1:]
    if "@" not in email or "." not in email.split("@")[1]:
        return []
    return [{
        "email": email.lower(),
        "source": "DNS:SOA-RNAME",
        "rank": 3,
    }]


def has_mx(domain: str) -> bool:
    try:
        r = subprocess.run(["dig", "+short", "MX", domain], capture_output=True, text=True, timeout=5)
    except Exception:
        return False
    return bool(r.stdout.strip())


def pattern_guesses(domain: str) -> list[dict]:
    """Standard security-contact local-parts at the registrable domain."""
    if not has_mx(domain):
        return []
    locals_ = ["security", "csirt", "incident", "abuse", "soc", "infosec"]
    return [
        {
            "email": f"{loc}@{domain}",
            "source": "pattern-guess+MX",
            "rank": 5,
        }
        for loc in locals_
    ]


def reverse_dns(ip: str) -> Optional[str]:
    try:
        r = subprocess.run(["dig", "+short", "-x", ip], capture_output=True, text=True, timeout=5)
        out = r.stdout.strip().splitlines()
        if out:
            return out[0].rstrip(".")
    except Exception:
        pass
    return None


def main():
    ap = argparse.ArgumentParser(description="Per-target disclosure-recipient discovery (chains authoritative sources)")
    ap.add_argument("--ip", help="IP address of the exposure target")
    ap.add_argument("--domain", help="Operator domain (if known)")
    ap.add_argument("--json", action="store_true", help="JSON output (default human-readable)")
    args = ap.parse_args()

    if not args.ip and not args.domain:
        ap.print_help()
        sys.exit(1)

    contacts: list[dict] = []
    context = {"ip": args.ip, "domain": args.domain}

    # Step 1: WHOIS on IP and/or domain
    if args.ip:
        whois_contacts, whois_meta = whois_abuse(args.ip)
        contacts.extend(whois_contacts)
        context.update({"whois_org": whois_meta.get("org_name", ""), "whois_net": whois_meta.get("net_name", "")})
        rdns = reverse_dns(args.ip)
        if rdns:
            context["reverse_dns"] = rdns

    # Step 2: WHOIS on domain (different output shape — focuses on registrar)
    if args.domain:
        whois_contacts, _ = whois_abuse(args.domain)
        contacts.extend(whois_contacts)

    # If we have a domain (or can guess one from rDNS), pursue domain-based sources
    candidate_domain = args.domain
    if not candidate_domain and args.ip:
        rdns = context.get("reverse_dns") or ""
        if rdns and "." in rdns:
            candidate_domain = registrable_domain(rdns)
            context["candidate_domain"] = candidate_domain

    if candidate_domain:
        reg_dom = registrable_domain(candidate_domain)
        context["registrable_domain"] = reg_dom

        # Step 3: security.txt at multiple candidate domains
        for d in [candidate_domain, reg_dom] if candidate_domain != reg_dom else [reg_dom]:
            contacts.extend(security_txt(d))

        # Step 4: DNS SOA
        contacts.extend(dns_soa_contact(reg_dom))

        # Step 5: Pattern guesses with MX validation
        contacts.extend(pattern_guesses(reg_dom))

    # Dedupe + rank
    seen = set()
    deduped = []
    for c in contacts:
        e = c["email"].lower()
        if e in seen:
            continue
        seen.add(e)
        deduped.append(c)
    deduped.sort(key=lambda c: (c.get("rank", 9), c["email"]))

    result = {
        "context": context,
        "contacts": deduped,
        "primary": deduped[0]["email"] if deduped else None,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Target: ip={args.ip or '-'}  domain={args.domain or '-'}")
        for k, v in context.items():
            if v and k not in ("ip", "domain"):
                print(f"  {k}: {v}")
        print()
        print(f"Ranked contacts ({len(deduped)} unique):")
        print(f"  {'rank':<4}  {'source':<28}  email")
        print(f"  {'-'*4}  {'-'*28}  {'-'*40}")
        for c in deduped:
            print(f"  {c.get('rank', '?'):<4}  {c['source']:<28}  {c['email']}")
        if deduped:
            print(f"\nPrimary recipient: {deduped[0]['email']}  (source: {deduped[0]['source']})")


if __name__ == "__main__":
    main()
