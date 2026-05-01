#!/usr/bin/env python3
"""
Generate disclosure email drafts from case study .md files.
Output: disclosures/<slug>.md per institution + disclosures/index.md tracking sheet.

Each email contains the full case-study body (summary, infrastructure, model inventory,
all findings) extracted verbatim from the source file — not a template with a single finding.
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Contact map: slug → (to, cc)
CONTACTS = {
    # US
    "US-NY-columbia":      ("security@columbia.edu", None),
    "US-CA-ucsb":          ("security@ucsb.edu", None),
    "US-NY-suny-buffalo":  ("security@buffalo.edu", None),
    "US-NC-duke":          ("security@duke.edu", None),
    "US-IN-purdue-northwest": ("security@pnw.edu", None),
    "US-NY-rit":           ("security@rit.edu", None),
    "US-NY-syracuse":      ("security@syr.edu", None),
    "US-NY-suny-stony-brook": ("security@stonybrook.edu", None),
    "US-CA-ucdavis":       ("security@ucdavis.edu", None),
    "US-VA-vt":            ("security@vt.edu", None),
    # Canada
    "CA-ON-western-ontario": ("security@uwo.ca", None),
    "CA-MB-u-manitoba":    ("security@umanitoba.ca", None),
    # Australia
    "AU-newcastle":        ("security@newcastle.edu.au", None),
    "AU-monash":           ("security@monash.edu", None),
    # UK
    "GB-hertfordshire":    ("security@herts.ac.uk", None),
    # Sweden
    "SE-KTH":              ("security@kth.se", None),
    "SE-umea":             ("security@umu.se", None),
    # Czech Republic
    "CZ-brno-vutbr":       ("security@vutbr.cz", None),
    # Slovakia
    "SK-zilina":           ("security@uniza.sk", None),
    # Poland
    "PL-lodz-tul":         ("security@p.lodz.pl", None),
    # Russia
    "RU-itmo":             ("security@itmo.ru", None),
    # Greece
    "GR-tech-crete-ntua":  ("security@tuc.gr", "security@netmode.ece.ntua.gr"),
    "GR-u-crete-medical":  ("security@uoc.gr", None),
    # Armenia
    "AM-armenian-academy": ("security@sci.am", None),
    # Japan
    "JP-Keio":             ("security@keio.ac.jp", None),
    # South Korea
    "KR-POSTECH":          ("security@postech.ac.kr", None),
    "KR-yonsei":           ("security@yonsei.ac.kr", None),
    "KR-snu":              ("security@snu.ac.kr", None),
    "KR-inha":             ("security@inha.ac.kr", None),
    # Taiwan
    "TW-ncku":             ("security@ncku.edu.tw", None),
    "TW-ncu-aiden":        ("security@ncu.edu.tw", "janice.tsai@oplentia.com"),
    "TW-fju-medph":        ("security@fju.edu.tw", None),
    "TW-ntu-gpu":          ("security@ntu.edu.tw", None),
    # China
    "CN-shandong-med":     ("security@sdum.edu.cn", None),
    # Vietnam
    "VN-hanoi":            ("security@hanu.edu.vn", None),
    "VN-vnu-hanoi":        ("security@vnu.edu.vn", None),
    "VN-vnu-hcmc":         ("security@hcmuns.edu.vn", None),
    # Thailand
    "TH-Chulalongkorn":    ("security@chula.ac.th", None),
    "TH-moph":             ("security@moph.go.th", None),
    # India
    "IN-shiv-nadar":       ("security@snu.edu.in", None),
    # Pakistan
    "PK-comsats":          ("security@comsats.edu.pk", None),
    # Sri Lanka
    "LK-learn":            ("security@learn.ac.lk", None),
    # Kyrgyzstan
    "KG-krena":            ("noc@krena.kg", None),
    # Kenya
    "KE-JKUAT":            ("security@jkuat.ac.ke", None),
    # Egypt
    "EG-enstinet-nren":    ("security@enstinet.eg", "abuse@are.eg"),
    # Brazil
    "BR-cefet-rj":         ("security@cefet-rj.br", None),
    # Commercial
    "FR-emails-pro-rdv-bot": ("security@emails-pro.fr", None),
}

SENDER = "Nicholas Michael Kloster / NuClide Research"
SENDER_EMAIL = "nicholas@nuclide-research.com"
REPO = "https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT"

CVE_NOTE = """\
**CVE-2025-63389**

All models on this instance are injectable via the unauthenticated `/api/create` endpoint — an attacker can overwrite any model's system prompt or delete models entirely. No patch exists as of this disclosure.

"""


def slugify(fname):
    return Path(fname).stem


def extract_fields(md_path):
    text = Path(md_path).read_text()
    lines = text.splitlines()

    # Institution name from H1
    institution = ""
    for l in lines:
        if l.startswith("# "):
            institution = l[2:].split("—")[0].split("(")[0].strip()
            break

    # IP extraction — try several formats then fall back to scanning text
    ip = None
    for pattern in [
        r'\|\s*IP\s*\|\s*([\d\.]+)\s*\|',           # standard key-value table
        r'\|\s*Primary IP\s*\|\s*([\d\.]+)\s*\|',    # POSTECH cluster style
        r'\*\*IP:\*\*\s*([\d\.]+)',                   # bold inline style
    ]:
        m = re.search(pattern, text)
        if m:
            ip = m.group(1)
            break
    if not ip:
        # Multi-node: collect all public IPs in order of appearance
        all_ips = re.findall(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b', text)
        seen, unique_ips = set(), []
        for addr in all_ips:
            first_oct = int(addr.split('.')[0])
            if first_oct in (0, 10, 127, 169, 172, 192, 255):
                continue
            if addr not in seen:
                seen.add(addr)
                unique_ips.append(addr)
        if len(unique_ips) == 1:
            ip = unique_ips[0]
        elif len(unique_ips) > 1:
            ip = f"{unique_ips[0]} (+{len(unique_ips)-1} nodes)"
        else:
            ip = "see case study"

    # Severity
    sev = "HIGH"
    if re.search(r'\(CRITICAL\)', text):
        sev = "CRITICAL"
    elif "200 OK" in text and "cloud" in text.lower():
        sev = "CRITICAL"
    elif "signin_url" in text or "credential leak" in text.lower() or "cred leak" in text.lower():
        sev = "CRITICAL"
    elif "auth.*disabled" in text.lower() or "auth disabled" in text.lower():
        sev = "CRITICAL"
    elif re.search(r'\(LOW\)', text):
        sev = "LOW"

    # Extract main body: everything from first ## heading to ## Remediation/Disclosure
    start = re.search(r'^## ', text, re.MULTILINE)
    end = re.search(r'^## (?:Remediation|Disclosure)', text, re.MULTILINE)

    if start and end:
        body = text[start.start():end.start()].strip()
    elif start:
        body = text[start.start():].strip()
    else:
        body = ""

    # Remove trailing separator lines that appear just before Remediation
    body = re.sub(r'\n---\s*$', '', body).strip()

    # Impact lines (derived from full text)
    impact_lines = []
    if "cloud" in text.lower() and ("200 ok" in text.lower() or "quota" in text.lower()):
        impact_lines.append(
            "Any internet actor can run inference against your cloud API subscription "
            "at your expense — this constitutes direct quota/billing theft."
        )
    if "cred" in text.lower() or "signin_url" in text.lower():
        impact_lines.append(
            "The credential leak (username + SSH public key) exposes your service account "
            "to enumeration and credential-stuffing against other services."
        )
    if "rag" in text.lower() or "embed" in text.lower():
        impact_lines.append(
            "An embedding model indicates an active RAG pipeline — documents loaded into "
            "your vector store are reachable via unauthenticated queries."
        )
    if "medical" in text.lower() or "medgemma" in text.lower() or "moph" in text.lower():
        impact_lines.append(
            "Medical AI models exposed without authentication create compliance risk "
            "(potential HIPAA/patient-data adjacent exposure depending on RAG content)."
        )
    if "system prompt" in text.lower() and "aiden" in str(md_path).lower():
        impact_lines.append(
            "The full system prompt of a production SaaS deployment is publicly readable, "
            "exposing your business logic, client contact details, and anti-injection "
            "rules to anyone."
        )
    if not impact_lines:
        impact_lines.append(
            "Any internet actor can run uncapped inference against your GPU at your "
            "compute cost, and inject malicious system prompts into any loaded model "
            "via CVE-2025-63389."
        )

    has_cve = "CVE-2025-63389" in text

    return {
        "institution": institution,
        "ip": ip,
        "severity": sev,
        "body_content": body,
        "impact": " ".join(impact_lines),
        "has_cve": has_cve,
    }


def make_email(slug, md_path, fields, to, cc):
    cc_line = f"cc: {cc}\n" if cc else ""
    cc_display = f"**Cc:** {cc}\n" if cc else ""
    cve_note = CVE_NOTE if fields["has_cve"] else ""
    rel = str(Path(md_path).relative_to(ROOT))

    return f"""\
---
institution: {fields["institution"]}
ip: {fields["ip"]}
to: {to}
{cc_line}severity: {fields["severity"]}
status: DRAFT
date: 2026-05-01
---

**To:** {to}
{cc_display}**Subject:** Unauthenticated AI inference endpoint — {fields["institution"]} ({fields["ip"]})

---

{SENDER}
{SENDER_EMAIL}

2026-05-01

**Re:** Unauthenticated Ollama AI inference endpoint — {fields["institution"]}
**IP / Host:** {fields["ip"]}
**Severity:** {fields["severity"]}

---

I'm an independent security researcher. I hold CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct good-faith AI infrastructure research under the NuClide Research umbrella. This is an unsolicited disclosure — no engagement exists with your organization, and I have not accessed, modified, or exfiltrated any data beyond what was necessary to confirm the exposure.

---

{fields["body_content"]}

---

**Why it matters**

{fields["impact"]}

**One-line fix**

```
OLLAMA_HOST=127.0.0.1:11434
systemctl restart ollama
```

This rebinds Ollama to loopback only. If running in Docker: `docker run -p 127.0.0.1:11434:11434 ollama/ollama`.

{cve_note}**Reference**

Full technical details, parameter counts, and remediation notes are in this public research repository:
{REPO}/blob/main/{rel}

This research is part of a broader sweep of university AI infrastructure exposures documented at:
{REPO}/blob/main/case-studies/universities/OVERVIEW.md

I'm happy to answer questions or assist with verification. No response is required.

Regards,
{SENDER}
{SENDER_EMAIL}
{REPO}
"""


def main():
    out_dir = ROOT / "disclosures"
    out_dir.mkdir(exist_ok=True)

    index_rows = []
    generated = 0

    paths = sorted(
        list((ROOT / "case-studies" / "universities").glob("*.md")) +
        list((ROOT / "case-studies" / "commercial").glob("*.md"))
    )

    for md_path in paths:
        slug = slugify(md_path)
        if slug in ("OVERVIEW", "index"):
            continue

        contact = CONTACTS.get(slug)
        if contact is None:
            print(f"  [no contact] {slug}", file=sys.stderr)
            continue

        to, cc = contact
        fields = extract_fields(md_path)

        email_body = make_email(slug, md_path, fields, to, cc)
        out_file = out_dir / f"{slug}.md"
        out_file.write_text(email_body)

        cc_str = cc or ""
        index_rows.append(
            f"| [{fields['institution']}]({slug}.md) | {fields['ip']} | {fields['severity']} "
            f"| {to} | {cc_str} | DRAFT |"
        )
        generated += 1
        print(f"  {slug}: {to}")

    # Sort index by severity
    def sev_key(row):
        if "CRITICAL" in row: return 0
        if "HIGH" in row: return 1
        return 2

    index_rows.sort(key=sev_key)

    header = """\
# Disclosure Email Queue

_NuClide Research · 2026-05-01_

Drafts generated from case studies. Send CRITICAL first, then HIGH, then LOW.
Update Status column as emails are sent / acknowledged.

| Institution | IP | Severity | To | Cc | Status |
|---|---|---|---|---|---|
"""
    (out_dir / "index.md").write_text(header + "\n".join(index_rows) + "\n")
    print(f"\n{generated} email drafts written to disclosures/")


if __name__ == "__main__":
    main()
