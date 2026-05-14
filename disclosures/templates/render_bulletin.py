#!/usr/bin/env python3
"""
render_bulletin.py — render a disclosure into the NuClide Security
Disclosure Bulletin format (the claude.ai/design email-handoff template).

Input: a disclosure .md with YAML frontmatter + `## Section` blocks.
Output: writes <slug>.html and <slug>.txt into _rendered/, and (with
--queue) injects an entry into _gmail_drafts.json with both `body`
(plaintext) and `html` fields so send_drafts_api.py can build a
multipart/alternative message or a Gmail draft.

Frontmatter schema:
    ---
    to: info@example.com
    cc: abuse@host.com            # optional
    severity: CRITICAL
    target: api.example.com / 198.51.100.10
    issued_date: 2026-05-13       # → "13 MAY 2026" in the bulletin
    kind: Coordinated vulnerability disclosure  ·  no click required
    slug: EXAMPLE-disclosure-2026-05-13   # optional; defaults to filename
    ---

Body sections (markdown `## Heading`, case-insensitive match):
    ## Subject            — the email Subject line (one line)
    ## Who we are         — prose paragraph(s)
    ## What we found      — prose paragraph(s)
    ## How we found it    — prose paragraph(s)
    ## Infrastructure     — a pipe-table: | Field | Value |
    ## Findings           — a pipe-table: | Port | Service | Severity | Issue | Verify |
    ## Findings note      — prose paragraph after the findings table
    ## Evidence           — a fenced or raw block, rendered monospaced
    ## Verify it yourself — prose paragraph(s)
    ## Recommended fix    — numbered/bulleted list; "Head. body" splits on first period
"""
from __future__ import annotations
import argparse, json, re, sys, html as html_mod
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = Path(__file__).resolve().parent / "bulletin_template.html"
RENDERED = ROOT / "_rendered"
DRAFTS_JSON = ROOT / "_gmail_drafts.json"

SENDER_EMAIL = "contact@nuclide-research.com"
SENDER_DOMAIN = "nuclide-research.com"

# Severity → the dossier palette (matches the React prototype's SEV map).
SEV = {
    "CRITICAL": {"bg": "#7a1a14", "ink": "#7a1a14"},
    "HIGH":     {"bg": "#a8521a", "ink": "#8a3f10"},
    "MEDIUM":   {"bg": "#8a6a14", "ink": "#6e5410"},
    "LOW":      {"bg": "#4a5c2a", "ink": "#3a4a22"},
    "INFO":     {"bg": "#2d4a5a", "ink": "#2d4a5a"},
}

MONO = "'Courier New',Courier,monospace"


def esc(s: str) -> str:
    return html_mod.escape(s, quote=True)


def parse_frontmatter(text: str):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.DOTALL)
    if not m:
        raise ValueError("no YAML frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"').strip("'")
    return fm, m.group(2)


def split_sections(body: str):
    sections, cur, buf = {}, None, []
    for line in body.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", line)
        if h:
            if cur is not None:
                sections[cur.lower()] = "\n".join(buf).strip()
            cur, buf = h.group(1).strip(), []
        else:
            buf.append(line)
    if cur is not None:
        sections[cur.lower()] = "\n".join(buf).strip()
    return sections


def parse_table(md: str):
    rows = []
    for line in md.strip().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.match(r"^\|[\s\-:|]+\|$", line):
            continue
        rows.append([c.strip() for c in line.strip("|").split("|")])
    return rows


def fmt_issued(d: str) -> str:
    """2026-05-13 → '13 MAY 2026'."""
    try:
        dt = date.fromisoformat(d)
        return dt.strftime("%d %b %Y").upper()
    except Exception:
        return d.upper()


def prose_to_html(md: str) -> str:
    """Each blank-line-separated block becomes a justified <p>. Inline
    `code` becomes a monospace span."""
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        if not block.strip():
            continue
        b = esc(block.strip()).replace("\n", " ")
        b = re.sub(r"`([^`]+)`",
                   r'<span style="font-family:' + MONO + r';font-size:13px;">\1</span>',
                   b)
        margin = "4px 0 0 0" if not out else "12px 0 0 0"
        out.append(f'<p style="margin:{margin};text-align:justify;">{b}</p>')
    return "\n  ".join(out)


def prose_to_text(md: str) -> str:
    blocks = []
    for block in re.split(r"\n\s*\n", md.strip()):
        if block.strip():
            b = re.sub(r"`([^`]+)`", r"\1", block.strip().replace("\n", " "))
            blocks.append(b)
    return "\n\n".join(blocks)


def render_infra_rows_html(rows):
    out = []
    body = rows[1:] if len(rows) > 1 else rows  # drop header row
    for i, r in enumerate(body):
        if len(r) < 2:
            continue
        k, v = r[0], r[1]
        bg = "#ebe2c5" if i % 2 else "transparent"
        v_html = esc(v).replace("\\n", "<br>")
        out.append(
            f'<tr style="background:{bg};">'
            f'<td style="width:110px;padding:8px 14px 8px 12px;vertical-align:top;border-bottom:1px solid #8a7d5e;">'
            f'<span style="font-family:{MONO};font-size:11px;letter-spacing:0.14em;color:#8a7d5e;font-weight:700;">{esc(k.upper())}</span></td>'
            f'<td style="padding:8px 12px 8px 0;vertical-align:top;border-bottom:1px solid #8a7d5e;">'
            f'<span style="font-family:{MONO};font-size:13px;color:#1a1612;">{v_html}</span></td>'
            f'</tr>'
        )
    return "\n    ".join(out)


def render_infra_rows_text(rows):
    body = rows[1:] if len(rows) > 1 else rows
    return "\n".join(f"  {r[0]+':':<14} {r[1].replace(chr(92)+'n', '; ')}"
                     for r in body if len(r) >= 2)


def sev_pill_html(level: str) -> str:
    s = SEV.get(level.upper(), SEV["INFO"])
    return (
        f'<span style="display:inline-block;font-family:{MONO};font-size:10.5px;'
        f'letter-spacing:0.14em;font-weight:700;color:{s["ink"]};white-space:nowrap;line-height:14px;">'
        f'<span style="display:inline-block;width:8px;height:8px;background:{s["bg"]};'
        f'margin-right:7px;vertical-align:1px;"></span>{esc(level.upper())}</span>'
    )


def render_findings_rows_html(rows):
    out = []
    body = rows[1:] if len(rows) > 1 else rows  # drop header
    for i, r in enumerate(body):
        while len(r) < 5:
            r.append("")
        port, svc, sev, issue, verify = r[0], r[1], r[2], r[3], r[4]
        bg = "#ebe2c5" if i % 2 else "transparent"
        is_url = verify.startswith("http")
        if is_url:
            verify_html = (f'<a href="{esc(verify)}" style="color:#1a1612;'
                           f'text-decoration:underline;text-underline-offset:2px;">{esc(verify)}</a>')
        else:
            verify_html = f'<span style="color:#1a1612;">{esc(verify)}</span>'
        verify_line = ""
        if verify:
            verify_line = (
                f'<div style="margin-top:5px;font-family:{MONO};font-size:11.5px;'
                f'color:#4a4234;line-height:1.5;word-break:break-all;">'
                f'<span style="color:#8a7d5e;margin-right:6px;">&#8627; verify</span>{verify_html}</div>'
            )
        out.append(
            f'<tr style="background:{bg};">'
            f'<td style="padding:10px 10px 12px 0;border-bottom:1px solid #8a7d5e;vertical-align:top;'
            f'font-family:{MONO};font-size:13px;color:#1a1612;white-space:nowrap;">{esc(port)}</td>'
            f'<td style="padding:10px 10px 12px 0;border-bottom:1px solid #8a7d5e;vertical-align:top;'
            f'font-size:13.5px;color:#1a1612;">{esc(svc)}</td>'
            f'<td style="padding:10px 10px 12px 0;border-bottom:1px solid #8a7d5e;vertical-align:top;">'
            f'{sev_pill_html(sev)}</td>'
            f'<td style="padding:10px 0 12px 0;border-bottom:1px solid #8a7d5e;vertical-align:top;">'
            f'<div style="font-size:13.5px;color:#1a1612;line-height:1.45;">{esc(issue)}</div>'
            f'{verify_line}</td>'
            f'</tr>'
        )
    return "\n    ".join(out)


def render_findings_rows_text(rows):
    body = rows[1:] if len(rows) > 1 else rows
    out = []
    for r in body:
        while len(r) < 5:
            r.append("")
        out.append(f"  {r[0]:<12} {r[1]:<28} {r[2].upper():<10} {r[3]}")
        if r[4]:
            out.append(f"      verify: {r[4]}")
    return "\n".join(out)


def render_fix_rows_html(md: str):
    items = []
    for line in md.strip().splitlines():
        m = re.match(r"^\s*(?:\d+[.\)]|[-*])\s+(.+?)\s*$", line)
        if m:
            items.append(m.group(1))
        elif items and line.strip():
            items[-1] += " " + line.strip()
    out = []
    for i, item in enumerate(items):
        # "Head sentence. Rest of body." → bold head, soft body
        parts = item.split(". ", 1)
        head = esc(parts[0] + ("." if not parts[0].endswith(".") else ""))
        rest = esc(parts[1]) if len(parts) > 1 else ""
        rest_span = f' <span style="color:#4a4234;">{rest}</span>' if rest else ""
        out.append(
            f'<tr><td style="width:34px;font-family:{MONO};font-size:11px;letter-spacing:0.1em;'
            f'color:#8a7d5e;font-weight:700;vertical-align:top;padding:8px 0 0 0;">{i+1:02d}</td>'
            f'<td style="vertical-align:top;padding:8px 0;font-size:14px;line-height:1.5;color:#1a1612;">'
            f'<span style="font-weight:600;">{head}</span>{rest_span}</td></tr>'
        )
    return "\n    ".join(out)


def render_fix_rows_text(md: str):
    items = []
    for line in md.strip().splitlines():
        m = re.match(r"^\s*(?:\d+[.\)]|[-*])\s+(.+?)\s*$", line)
        if m:
            items.append(m.group(1))
        elif items and line.strip():
            items[-1] += " " + line.strip()
    return "\n".join(f"  {i+1:2d}. {item}" for i, item in enumerate(items))


def render_evidence(md: str) -> str:
    body = md.strip()
    body = re.sub(r"^```\w*\n", "", body)
    body = re.sub(r"\n```$", "", body)
    return body


def render(md_path: Path):
    text = md_path.read_text()
    fm, body = parse_frontmatter(text)
    sec = split_sections(body)

    slug = fm.get("slug") or md_path.stem
    severity = fm.get("severity", "INFO").upper()
    to = fm.get("to", "")
    cc = fm.get("cc", "").strip() or None
    issued = fmt_issued(fm.get("issued_date") or fm.get("date") or date.today().isoformat())
    kind = fm.get("kind", "Coordinated vulnerability disclosure  ·  no click required")
    target = fm.get("target", fm.get("ip", ""))
    subject = sec.get("subject", "").strip() or f"Security advisory — {target}"

    infra_rows = parse_table(sec.get("infrastructure", ""))
    findings_rows = parse_table(sec.get("findings", ""))
    evidence = render_evidence(sec.get("evidence", ""))

    # ---- HTML ----
    tpl = TEMPLATE.read_text()
    repl = {
        "{{SUBJECT}}": esc(subject),
        "{{ISSUED_DATE}}": esc(issued),
        "{{TO}}": esc(to),
        "{{RE}}": esc(target),
        "{{KIND}}": esc(kind),
        "{{SENDER_EMAIL}}": esc(SENDER_EMAIL),
        "{{SENDER_DOMAIN}}": esc(SENDER_DOMAIN),
        "{{WHO_WE_ARE}}": prose_to_html(sec.get("who we are", "")),
        "{{WHAT_WE_FOUND}}": prose_to_html(sec.get("what we found", "")),
        "{{HOW_WE_FOUND_IT}}": prose_to_html(sec.get("how we found it", "")),
        "{{INFRA_ROWS}}": render_infra_rows_html(infra_rows),
        "{{FINDINGS_ROWS}}": render_findings_rows_html(findings_rows),
        "{{FINDINGS_NOTE}}": esc(sec.get("findings note", "")) or "",
        "{{EVIDENCE_BLOCK}}": esc(evidence),
        "{{VERIFY_TEXT}}": prose_to_html(sec.get("verify it yourself", "")),
        "{{FIX_ROWS}}": render_fix_rows_html(sec.get("recommended fix", "")),
    }
    html_out = tpl
    for k, v in repl.items():
        html_out = html_out.replace(k, v)

    # ---- plaintext fallback ----
    lines = []
    lines.append("NUCLIDE RESEARCH — SECURITY DISCLOSURE BULLETIN")
    lines.append(f"Issued: {issued}")
    lines.append("")
    lines.append(f"FROM  NuClide Research · {SENDER_DOMAIN}")
    lines.append(f"TO    {to}")
    lines.append(f"KIND  {kind}")
    lines.append(f"RE    {target}")
    lines.append("")
    lines.append("§ I — WHO WE ARE")
    lines.append(prose_to_text(sec.get("who we are", "")))
    lines.append("")
    lines.append("§ II — WHAT WE FOUND")
    lines.append(prose_to_text(sec.get("what we found", "")))
    lines.append("")
    lines.append("§ III — HOW WE FOUND IT")
    lines.append(prose_to_text(sec.get("how we found it", "")))
    lines.append("")
    lines.append("§ IV — INFRASTRUCTURE")
    lines.append(render_infra_rows_text(infra_rows))
    lines.append("")
    lines.append("§ V — FINDINGS")
    lines.append(render_findings_rows_text(findings_rows))
    if sec.get("findings note"):
        lines.append("")
        lines.append(prose_to_text(sec["findings note"]))
    lines.append("")
    lines.append("§ VI — EVIDENCE (EXCERPT)")
    lines.append(evidence)
    lines.append("")
    lines.append("§ VII — VERIFY IT YOURSELF")
    lines.append(prose_to_text(sec.get("verify it yourself", "")))
    lines.append("")
    lines.append("§ VIII — RECOMMENDED FIX")
    lines.append(render_fix_rows_text(sec.get("recommended fix", "")))
    lines.append("")
    lines.append("Thanks for your time,")
    lines.append("NuClide Research")
    lines.append("")
    lines.append("--")
    lines.append(f"NuClide Research · {SENDER_EMAIL} · {SENDER_DOMAIN}")
    lines.append("END OF BULLETIN · PRIVATE CORRESPONDENCE")
    text_out = "\n".join(lines) + "\n"

    return {
        "slug": slug, "to": to, "cc": cc, "subject": subject,
        "severity": severity, "html": html_out, "body": text_out,
    }


def main():
    ap = argparse.ArgumentParser(description="Render disclosure bulletin")
    ap.add_argument("md", help="disclosure .md (frontmatter + ## sections)")
    ap.add_argument("--queue", action="store_true",
                    help="inject into _gmail_drafts.json (replacing any same-slug entry)")
    args = ap.parse_args()

    rec = render(Path(args.md))

    RENDERED.mkdir(exist_ok=True)
    html_path = RENDERED / f"{rec['slug']}.html"
    txt_path = RENDERED / f"{rec['slug']}.txt"
    html_path.write_text(rec["html"])
    txt_path.write_text(rec["body"])
    print(f"[+] {rec['slug']}")
    print(f"    html → {html_path}")
    print(f"    txt  → {txt_path}")
    print(f"    subject: {rec['subject']}")
    print(f"    to: {rec['to']}  cc: {rec['cc']}  severity: {rec['severity']}")

    if args.queue:
        queue = []
        if DRAFTS_JSON.exists():
            queue = json.loads(DRAFTS_JSON.read_text())
        queue = [d for d in queue if d.get("slug") != rec["slug"]]
        queue.append({
            "slug": rec["slug"], "to": rec["to"], "cc": rec["cc"],
            "subject": rec["subject"], "body": rec["body"], "html": rec["html"],
            "severity": rec["severity"],
        })
        DRAFTS_JSON.write_text(json.dumps(queue, indent=2))
        print(f"    queued → {DRAFTS_JSON} ({len(queue)} entries)")


if __name__ == "__main__":
    main()
