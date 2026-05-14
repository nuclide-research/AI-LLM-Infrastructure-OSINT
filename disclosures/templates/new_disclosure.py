#!/usr/bin/env python3
"""
new_disclosure.py — render NuClide disclosure emails from frontmatter source.

Input:  a single .md file with YAML frontmatter (the routing-header fields)
        and a structured body (findings table, fix block, etc.) in normal markdown.

Output: matching .html and .txt files in disclosures/_rendered/, ready to be
        consumed by send_drafts_api.py (which gets a new multipart/alternative
        sender — see send_multipart.py).

Usage:
    new_disclosure.py disclosures/SALUTEGROUP-smartshop-ai-amazonrec-2026-05-13.md
    new_disclosure.py --preview disclosures/<slug>.md   # opens in $BROWSER
    new_disclosure.py --all disclosures/                # render every .md

Frontmatter schema (additive to existing build_gmail_drafts.py schema):

    ---
    to: info@salutegroup.com.tr
    cc: abuse@pendc.com
    severity: CRITICAL
    target: api.amazonrec.space / 78.135.66.61
    recipient_name: Salute Group team
    disclosure_window_days: 14
    date: 2026-05-13
    repo_url: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
    case_study_url: case-studies/commercial/smartshop-ai-pentech-disclosure-2026-05-13.md
    status: DRAFT
    institution: Salute Group, SmartShop AI / amazonrec.space
    ---

    ## Subject
    Security advisory — unauthenticated production API on api.amazonrec.space / 78.135.66.61

    ## Standing paragraph
    (optional override; uses default if omitted)

    ## Summary
    One to three sentences. Markdown OK. Render to <p> in HTML, paragraph in text.

    ## Infrastructure
    | Field      | Value                                                  |
    |------------|--------------------------------------------------------|
    | IP         | 78.135.66.61                                           |
    | rDNS       | 78.135.66.61.pendns.net                                |
    | ASN        | AS48678                                                |
    | Org        | PENTECH BILISIM (Turkey)                               |

    ## Findings
    | Port  | Service        | Severity  | Issue                              |
    |-------|----------------|-----------|------------------------------------|
    | 443   | FastAPI        | CRITICAL  | 13 endpoints, no auth …            |
    | 5000  | MLflow tracker | CRITICAL  | Anonymous experiment list          |

    ## Evidence (optional)
    ```
    GET /api/v1/session/init →
    {"user_id":"AH2IJABK...", "interaction_count":19, ...}
    ```

    ## Why this matters
    One short paragraph.

    ## Recommended fix
    1. First step.
    2. Second step.
"""

from __future__ import annotations
import argparse
import re
import sys
import webbrowser
from datetime import date as Date, timedelta
from pathlib import Path

SEVERITY_COLORS = {
    "CRITICAL": "#C8312E",
    "HIGH":     "#B85C00",
    "MEDIUM":   "#7A6500",
    "LOW":      "#3A6B47",
    "INFO":     "#5C6B7A",
}

DEFAULT_STANDING = (
    "I'm an independent security researcher (NuClide Research). I hold "
    "CISA disclosures CVE-2025-4364 and ICSA-25-140-11 and conduct "
    "good-faith AI-infrastructure research. This is a coordinated, unsolicited "
    "disclosure — no engagement exists with your organization, and I have "
    "not accessed, modified, or exfiltrated any data beyond what was "
    "necessary to confirm the exposure."
)

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = Path(__file__).resolve().parent
HTML_TPL = TEMPLATES / "disclosure_template.html"
TXT_TPL = TEMPLATES / "disclosure_template.txt"
RENDERED = ROOT / "_rendered"


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Return (frontmatter_dict, body) from a YAML-frontmattered file."""
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("no YAML frontmatter found")
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def split_sections(body: str) -> dict[str, str]:
    """Split markdown body on `## Heading` boundaries. Case-insensitive keys."""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in body.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if current is not None:
                sections[current.lower()] = "\n".join(buf).strip()
            current = h.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current.lower()] = "\n".join(buf).strip()
    return sections


def parse_md_table(md: str) -> list[list[str]]:
    """Parse a pipe-table into a list-of-rows; first row is the header."""
    if not md.strip():
        return []
    rows: list[list[str]] = []
    for line in md.strip().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip the separator row
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def html_escape(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;"))


def render_infra_rows_html(rows: list[list[str]]) -> str:
    """Two-column key/value table. First row is header — discarded."""
    if not rows:
        return ""
    body_rows = rows[1:] if len(rows) > 1 else rows
    out = []
    for i, r in enumerate(body_rows):
        if len(r) < 2:
            continue
        key, val = r[0], " ".join(r[1:])
        border = "border-top: 1px solid #D6CFC2;" if i > 0 else ""
        out.append(
            f'<tr style="{border}">'
            f'<td width="120" style="padding: 10px 12px 10px 0; color: #5C6B7A; vertical-align: top; white-space: nowrap;">{html_escape(key)}</td>'
            f'<td style="padding: 10px 0; color: #1F1A14; vertical-align: top;">{html_escape(val)}</td>'
            f'</tr>'
        )
    return "\n              ".join(out)


def render_infra_rows_text(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    body = rows[1:] if len(rows) > 1 else rows
    return "\n".join(f"  {(r[0] + ':').ljust(14)} {' '.join(r[1:])}" for r in body if len(r) >= 2)


def render_findings_rows_html(rows: list[list[str]]) -> str:
    """4-column findings table: Port | Service | Severity | Issue."""
    if not rows:
        return ""
    body_rows = rows[1:] if len(rows) > 1 else rows
    out = []
    for i, r in enumerate(body_rows):
        # Pad to 4 cols
        while len(r) < 4:
            r.append("")
        port, svc, sev, issue = r[0], r[1], r[2], r[3]
        sev_upper = sev.upper().strip()
        sev_color = SEVERITY_COLORS.get(sev_upper, "#1F1A14")
        border = "border-top: 1px solid #D6CFC2;" if i > 0 else ""
        out.append(
            f'<tr style="{border}">'
            f'<td style="padding: 10px 12px 10px 0; color: #1F1A14; vertical-align: top; white-space: nowrap;">{html_escape(port)}</td>'
            f'<td style="padding: 10px 12px; color: #1F1A14; vertical-align: top;">{html_escape(svc)}</td>'
            f'<td style="padding: 10px 12px; color: {sev_color}; vertical-align: top; font-weight: 600; white-space: nowrap;">{html_escape(sev_upper)}</td>'
            f'<td style="padding: 10px 0 10px 12px; color: #1F1A14; vertical-align: top; line-height: 1.5;">{html_escape(issue)}</td>'
            f'</tr>'
        )
    return "\n              ".join(out)


def render_findings_rows_text(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    body = rows[1:] if len(rows) > 1 else rows
    out = []
    for r in body:
        while len(r) < 4:
            r.append("")
        out.append(f"  {r[0]:<6}  {r[1]:<18}  {r[2].upper():<10}  {r[3]}")
    return "\n".join(out)


def render_fix_html(md: str) -> str:
    """Convert a numbered/bulleted markdown list to <ol> HTML."""
    items = []
    for line in md.strip().splitlines():
        m = re.match(r"^\s*(?:\d+[\.\)]|[\-\*])\s+(.+?)\s*$", line)
        if m:
            items.append(html_escape(m.group(1)))
        elif items and line.strip():
            items[-1] += " " + html_escape(line.strip())
    if not items:
        return f'<p style="margin: 0;">{html_escape(md)}</p>'
    lis = "".join(f'<li style="margin-bottom: 10px;">{x}</li>' for x in items)
    return f'<ol style="margin: 0; padding-left: 22px;">{lis}</ol>'


def render_fix_text(md: str) -> str:
    """Number the fix list cleanly for plaintext."""
    items = []
    for line in md.strip().splitlines():
        m = re.match(r"^\s*(?:\d+[\.\)]|[\-\*])\s+(.+?)\s*$", line)
        if m:
            items.append(m.group(1))
        elif items and line.strip():
            items[-1] += " " + line.strip()
    if not items:
        return md.strip()
    return "\n".join(f"  {i+1}. {x}" for i, x in enumerate(items))


def render_evidence_html(md: str) -> str:
    """Optional <pre> block in HTML; empty string if no evidence."""
    body = md.strip()
    # Strip fenced code-block markers if present
    body = re.sub(r"^```\w*\n", "", body)
    body = re.sub(r"\n```$", "", body)
    if not body:
        return ""
    return (
        '<tr>\n'
        '          <td style="padding: 0 0 8px 0;">\n'
        '            <h2 style="margin: 0 0 14px 0; font-family: \'IBM Plex Mono\', \'Menlo\', \'Consolas\', monospace; font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase; color: #5C6B7A; font-weight: 600;">Evidence</h2>\n'
        '          </td>\n'
        '        </tr>\n'
        '        <tr>\n'
        '          <td style="padding: 0 0 32px 0;">\n'
        f'            <pre style="margin: 0; padding: 16px 18px; background: #F2EDE3; border-left: 3px solid #1F1A14; font-family: \'IBM Plex Mono\', \'Menlo\', \'Consolas\', monospace; font-size: 12.5px; line-height: 1.55; color: #1F1A14; white-space: pre-wrap; word-wrap: break-word; overflow-x: auto;">{html_escape(body)}</pre>\n'
        '          </td>\n'
        '        </tr>'
    )


def render_evidence_text(md: str) -> str:
    body = md.strip()
    body = re.sub(r"^```\w*\n", "", body)
    body = re.sub(r"\n```$", "", body)
    if not body:
        return ""
    indented = "\n".join("    " + line for line in body.splitlines())
    return f"EVIDENCE\n----------------------------------------------------------------\n{indented}\n\n"


def render(md_path: Path, output_dir: Path) -> tuple[Path, Path]:
    """Render an .md draft into matching .html and .txt under output_dir/."""
    text = md_path.read_text()
    fm, body = parse_frontmatter(text)
    sections = split_sections(body)

    # Required frontmatter
    severity = fm.get("severity", "INFO").upper()
    severity_color = SEVERITY_COLORS.get(severity, "#1F1A14")

    date_str = fm.get("date") or Date.today().isoformat()
    try:
        sent = Date.fromisoformat(date_str)
    except ValueError:
        sent = Date.today()
    window_days = int(fm.get("disclosure_window_days", "14"))
    publish = sent + timedelta(days=window_days)
    disclosure_window = f"{sent.isoformat()} → {publish.isoformat()}"

    target = fm.get("target") or fm.get("ip") or fm.get("institution", "")
    to_addr = fm.get("to", "")
    to_display = to_addr  # we don't expand to names; the To: header carries names

    recipient_name = fm.get("recipient_name") or sections.get("greeting") or "team"
    standing = sections.get("standing paragraph") or DEFAULT_STANDING
    summary = sections.get("summary", "").strip()
    why = sections.get("why this matters", "").strip()
    fix_md = sections.get("recommended fix", "").strip()
    evidence_md = sections.get("evidence", "").strip()

    repo_url = fm.get("repo_url", "https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT")
    case_study = fm.get("case_study_url", "").strip()
    if case_study:
        if not case_study.startswith("http"):
            repo_url = f"{repo_url.rstrip('/')}/blob/main/{case_study}"
    repo_url_display = repo_url.replace("https://", "").replace("http://", "")

    subject = sections.get("subject", "").strip() or fm.get("subject", "").strip()
    if not subject:
        subject = f"Security advisory — {target}"

    infra_rows = parse_md_table(sections.get("infrastructure", ""))
    findings_rows = parse_md_table(sections.get("findings", ""))

    # HTML render
    html_template = HTML_TPL.read_text()
    html_out = html_template
    replacements_html = {
        "{{subject}}": html_escape(subject),
        "{{severity}}": severity,
        "{{severity_color}}": severity_color,
        "{{target}}": html_escape(target),
        "{{to_display}}": html_escape(to_display),
        "{{disclosure_window}}": disclosure_window,
        "{{disclosure_window_days}}": str(window_days),
        "{{publish_date}}": publish.isoformat(),
        "{{date}}": sent.isoformat(),
        "{{recipient_name}}": html_escape(recipient_name),
        "{{standing_paragraph}}": html_escape(standing),
        "{{summary}}": html_escape(summary).replace("\n\n", "</p><p style=\"margin: 16px 0 0 0;\">"),
        "{{infra_table_rows}}": render_infra_rows_html(infra_rows),
        "{{findings_table_rows}}": render_findings_rows_html(findings_rows),
        "{{evidence_block}}": render_evidence_html(evidence_md),
        "{{why_it_matters}}": html_escape(why),
        "{{fix_block}}": render_fix_html(fix_md),
        "{{repo_url}}": repo_url,
        "{{repo_url_display}}": repo_url_display,
    }
    for k, v in replacements_html.items():
        html_out = html_out.replace(k, v)

    # Plaintext render
    text_template = TXT_TPL.read_text()
    text_out = text_template
    replacements_text = {
        "{{subject}}": subject,
        "{{severity}}": severity,
        "{{target}}": target,
        "{{to_display}}": to_display,
        "{{disclosure_window}}": disclosure_window,
        "{{disclosure_window_days}}": str(window_days),
        "{{publish_date}}": publish.isoformat(),
        "{{date}}": sent.isoformat(),
        "{{recipient_name}}": recipient_name,
        "{{standing_paragraph}}": standing,
        "{{summary}}": summary,
        "{{infra_table_text}}": render_infra_rows_text(infra_rows),
        "{{findings_table_text}}": render_findings_rows_text(findings_rows),
        "{{evidence_block_text}}": render_evidence_text(evidence_md),
        "{{why_it_matters}}": why,
        "{{fix_block_text}}": render_fix_text(fix_md),
        "{{repo_url}}": repo_url,
    }
    for k, v in replacements_text.items():
        text_out = text_out.replace(k, v)

    # Write
    output_dir.mkdir(parents=True, exist_ok=True)
    slug = md_path.stem
    html_path = output_dir / f"{slug}.html"
    txt_path = output_dir / f"{slug}.txt"
    html_path.write_text(html_out)
    txt_path.write_text(text_out)
    return html_path, txt_path


def main():
    ap = argparse.ArgumentParser(description="Render NuClide disclosure templates")
    ap.add_argument("paths", nargs="*", help=".md draft(s) to render")
    ap.add_argument("--all", metavar="DIR", help="Render every .md in DIR")
    ap.add_argument("--out", default=str(RENDERED), help="Output directory (default: _rendered/)")
    ap.add_argument("--preview", action="store_true", help="Open rendered HTML in browser")
    args = ap.parse_args()

    output_dir = Path(args.out)

    targets: list[Path] = []
    if args.all:
        for p in Path(args.all).glob("*.md"):
            if p.name.startswith("_"):
                continue
            targets.append(p)
    targets.extend(Path(p) for p in args.paths)

    if not targets:
        ap.error("provide one or more .md drafts or --all DIR")

    for md in targets:
        try:
            html_p, txt_p = render(md, output_dir)
            print(f"[+] {md.name}")
            print(f"    html → {html_p}")
            print(f"    txt  → {txt_p}")
            if args.preview and len(targets) == 1:
                webbrowser.open(html_p.as_uri())
        except Exception as e:
            print(f"[!] {md.name}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
