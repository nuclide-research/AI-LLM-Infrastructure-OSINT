#!/usr/bin/env python3
"""
preview_gallery.py — Render the disclosure template once per severity tier and
emit a single HTML index page that frames all five side-by-side for visual review.

Usage:
    python3 preview_gallery.py
    # opens /tmp/nuclide-disclosure-preview/index.html in your browser
"""
import shutil
import subprocess
import webbrowser
from pathlib import Path

SEVERITIES = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
SEVERITY_COLORS = {
    "CRITICAL": "#C8312E",
    "HIGH":     "#B85C00",
    "MEDIUM":   "#7A6500",
    "LOW":      "#3A6B47",
    "INFO":     "#5C6B7A",
}

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = Path(__file__).resolve().parent
TPL = TEMPLATE_DIR / "disclosure_template.html"
OUT = Path("/tmp/nuclide-disclosure-preview")

SAMPLE_FRONTMATTER_BASE = """---
to: triage@example.com
cc: abuse@example-host.com
severity: {severity}
target: example-target.example.com / 198.51.100.42
recipient_name: Example team
disclosure_window_days: 14
date: 2026-05-13
repo_url: https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT
case_study_url: case-studies/commercial/example-2026-05-13.md
status: PREVIEW
institution: Example operator, sample disclosure used for template preview
ip: 198.51.100.42
---

## Subject
Security advisory — sample {severity} disclosure for template preview

## Summary
This is a sample render of the NuClide Research disclosure template at {severity} severity. The text below is placeholder content, used to show how each severity tier renders in the routing-header slab and in the findings table.

## Infrastructure
| Field | Value |
|---|---|
| IP | 198.51.100.42 |
| rDNS | host.example.com |
| ASN | AS65000 |
| Network | EXAMPLE-AS (Country) |
| Hostnames | api.example.com, app.example.com |
| Frontend | example.com (Vercel) |

## Findings
| Port | Service | Severity | Issue |
|---|---|---|---|
| 443 | Sample API | {severity} | Sample finding text showing how a single-line description renders in the issue column at this severity level. |
| 5000 | MLflow tracking | CRITICAL | Anonymous experiment listing exposes training-pipeline IP. |
| 6379 | Redis | HIGH | Internet-exposed database server. |
| 22 | OpenSSH | MEDIUM | Tagged eol-product by Shodan. |

## Evidence
GET /api/sample
HTTP/1.1 200 OK
Content-Type: application/json

{{"sample": "evidence block", "format": "monospaced"}}

## Why this matters
Short paragraph explaining the concrete impact. One sentence on direct harm, one sentence on indirect/operational harm. Avoids speculation; sticks to observed effects.

## Recommended fix
1. First remediation step, written so it can be done in under five minutes.
2. Second step, addressing the root cause.
3. Optional hardening step that prevents the class of issue recurring.
"""


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    rendered_paths = []
    for sev in SEVERITIES:
        md_path = OUT / f"sample-{sev.lower()}.md"
        md_path.write_text(SAMPLE_FRONTMATTER_BASE.format(severity=sev))
        # Use the canonical renderer
        result = subprocess.run(
            ["python3", str(TEMPLATE_DIR / "new_disclosure.py"),
             str(md_path), "--out", str(OUT)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            print(f"[!] {sev} failed: {result.stderr}")
            continue
        html_path = OUT / f"sample-{sev.lower()}.html"
        if not html_path.exists():
            print(f"[!] {sev}: expected output {html_path} not created")
            continue
        rendered_paths.append((sev, html_path))
        print(f"[+] {sev}  →  {html_path}")

    # Build the index
    index_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>NuClide Disclosure Template · Preview Gallery</title>
<style>
  :root {{
    --bg: #1a1814;
    --fg: #f0ebe0;
    --muted: #8a8275;
    --rule: #2e2a23;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    background: var(--bg);
    color: var(--fg);
    font-family: 'IBM Plex Mono', 'Menlo', 'Consolas', monospace;
    font-size: 13px;
    line-height: 1.6;
  }}
  header {{
    padding: 48px 40px 32px;
    border-bottom: 1px solid var(--rule);
  }}
  h1 {{
    margin: 0 0 8px;
    font-size: 16px;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }}
  header p {{
    margin: 0;
    color: var(--muted);
    max-width: 680px;
    font-size: 13px;
  }}
  .tabs {{
    display: flex;
    gap: 0;
    padding: 0 40px;
    border-bottom: 1px solid var(--rule);
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 10;
  }}
  .tab {{
    appearance: none;
    background: transparent;
    border: none;
    color: var(--muted);
    font-family: inherit;
    font-size: 12px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 18px 24px;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    transition: color 0.15s, border-color 0.15s;
  }}
  .tab:hover {{ color: var(--fg); }}
  .tab.active {{
    color: var(--fg);
    border-bottom-color: var(--fg);
  }}
  .swatch {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 10px;
    vertical-align: middle;
  }}
  main {{ padding: 0; }}
  iframe {{
    display: block;
    width: 100%;
    height: calc(100vh - 200px);
    border: 0;
    background: #FAF7F2;
  }}
  .meta {{
    padding: 12px 40px;
    color: var(--muted);
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--rule);
  }}
</style>
</head>
<body>
<header>
  <h1>NuClide · Disclosure Template Preview Gallery</h1>
  <p>Five severity tiers rendered through the same template. Tab between them to compare. Each preview is the actual HTML email body — the only thing that changes between severities is the routing-header slab color and the in-table severity label.</p>
</header>
<nav class="tabs">
"""
    for i, (sev, _) in enumerate(rendered_paths):
        active = " active" if i == 0 else ""
        index_html += f"""  <button class="tab{active}" data-target="frame-{sev.lower()}" data-sev="{sev}"><span class="swatch" style="background: {SEVERITY_COLORS[sev]};"></span>{sev}</button>
"""
    index_html += """</nav>
<div class="meta" id="meta">CRITICAL · oxide red · #C8312E</div>
<main>
"""
    for i, (sev, path) in enumerate(rendered_paths):
        hidden = "" if i == 0 else 'style="display:none"'
        index_html += f'  <iframe id="frame-{sev.lower()}" src="{path.name}" {hidden}></iframe>\n'
    index_html += """</main>
<script>
  const tabs = document.querySelectorAll('.tab');
  const meta = document.getElementById('meta');
  const colorNames = {
    CRITICAL: "oxide red · #C8312E",
    HIGH:     "brick orange · #B85C00",
    MEDIUM:   "mustard · #7A6500",
    LOW:      "forest · #3A6B47",
    INFO:     "slate · #5C6B7A"
  };
  tabs.forEach(t => t.addEventListener('click', () => {
    tabs.forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    document.querySelectorAll('iframe').forEach(f => f.style.display = 'none');
    document.getElementById(t.dataset.target).style.display = 'block';
    meta.textContent = t.dataset.sev + ' · ' + colorNames[t.dataset.sev];
  }));
</script>
</body>
</html>
"""

    index_path = OUT / "index.html"
    index_path.write_text(index_html)
    print(f"\n[+] gallery: {index_path}")
    webbrowser.open(index_path.as_uri())


if __name__ == "__main__":
    main()
