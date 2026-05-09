#!/usr/bin/env python3
"""
Shodan sweep for new query categories 18-26.
Runs canonical fingerprint queries for each new platform class,
reports total hit counts, top countries, and top orgs.
"""

import os, sys, json, time
from pathlib import Path

try:
    import shodan
except ImportError:
    sys.exit("pip install shodan")

def load_key():
    if k := os.environ.get("SHODAN_API_KEY"):
        return k
    p = Path.home() / ".config/nuclide/shodan.key"
    if p.exists():
        return p.read_text().strip()
    sys.exit("No Shodan API key found")

api = shodan.Shodan(load_key())

QUERIES = {
    # 18 - Jupyter
    "jupyter_hub_port8000":         ('http.title:"JupyterHub" port:8000',         18),
    "jupyter_lab_port8888":         ('http.title:"JupyterLab" port:8888',          18),
    "jupyter_notebook_port8888":    ('http.title:"Jupyter Notebook" port:8888',    18),
    "jupyter_api_kernels":          ('http.html:"/api/kernels"',                   18),

    # 19 - Streamlit
    "streamlit_port8501":           ('port:8501',                                  19),
    "streamlit_stcore":             ('http.html:"_stcore/host-config"',            19),
    "streamlit_health":             ('http.html:"_stcore/health"',                 19),

    # 20 - Gradio / A1111 / Langflow
    "gradio_port7860":              ('port:7860 http.html:"gradio"',               20),
    "a1111_txt2img":                ('port:7860 http.html:"txt2img"',              20),
    "a1111_sdapi":                  ('port:7860 http.html:"sdapi"',                20),
    "langflow_auto_login":          ('http.html:"/api/v1/auto_login"',             20),
    "gradio_component_count":       ('port:7860 http.html:"component_count"',      20),

    # 21 - Browser agents
    "cdp_websocket_debugger":       ('"webSocketDebuggerUrl"',                     21),
    "cdp_headless_chrome_port9222": ('port:9222 "HeadlessChrome"',                21),
    "selenium_grid_port4444":       ('port:4444 "selenium"',                       21),
    "selenium_grid_status":         ('"Selenium Grid" port:4444',                  21),
    "browserless_port3000":         ('port:3000 "browserless"',                    21),
    "browserless_v1_image":         ('"HeadlessChrome 121.0.6167.85"',             21),

    # 22 - Data labeling
    "doccano_port8000":             ('http.html:"doccano" port:8000',              22),
    "doccano_v1_projects":          ('http.html:"/v1/projects" port:8000',         22),
    "argilla_port6900":             ('port:6900',                                  22),
    "argilla_api_info":             ('http.html:"/api/_info"',                     22),
    "labelstudio_port8080":         ('http.html:"Label Studio" port:8080',         22),
    "cvat_about":                   ('http.html:"Computer Vision Annotation Tool"',22),

    # 23 - AI safety eval
    "promptfoo_port15500":          ('port:15500',                                 23),
    "promptfoo_html":               ('http.html:"promptfoo" port:15500',           23),
    "langsmith_port1984":           ('port:1984 "langsmith"',                      23),
    "inspect_ai_port7575":          ('port:7575',                                  23),
    "garak_rest_endpoint":          ('http.html:"/api/v1/garak/version"',          23),

    # 24 - Observability
    "phoenix_port6006":             ('port:6006 http.html:"phoenix"',              24),
    "phoenix_arize":                ('port:6006 http.html:"arize"',                24),
    "tensorboard_port6006":         ('port:6006 http.html:"tensorboard"',          24),
    "tensorboard_title":            ('http.title:"TensorBoard" port:6006',         24),
    "tensorboard_data_runs":        ('http.html:"/data/runs" port:6006',           24),
    "clearml_port8080":             ('http.html:"clearml" port:8080',              24),
    "wandb_local":                  ('"wandb-local"',                              24),

    # 25 - Elasticsearch / OpenSearch
    "es_tagline":                   ('"You Know, for Search"',                     25),
    "es_port9200_open":             ('port:9200 "You Know, for Search"',           25),
    "es_port9200_noauth":           ('port:9200 "You Know, for Search" -port:443', 25),
    "es_7x":                        ('port:9200 "number":"7."',                    25),
    "es_ransomware":                ('port:9200 "read_me"',                        25),
    "opensearch_port9200":          ('port:9200 "opensearch"',                     25),
    "kibana_port5601":              ('http.title:"Kibana" port:5601',              25),
    "kibana_noauth":                ('http.title:"Kibana" port:5601 -port:443',    25),
    "es_kyb_data":                  ('port:9200 "kyb_data"',                       25),

    # 26 - Mem0 (via Qdrant / ChromaDB backends)
    "qdrant_port6333_open":         ('port:6333 http.status:200',                  26),
    "qdrant_mem0_collection":       ('port:6333 "mem0"',                           26),
    "chromadb_mem0_collection":     ('port:8000 "heartbeat" "mem0"',               26),
}

def facets(result, field, n=5):
    counts = {}
    for match in result.get("matches", []):
        v = match.get(field)
        if isinstance(v, list):
            for item in v:
                counts[str(item)] = counts.get(str(item), 0) + 1
        elif v:
            counts[str(v)] = counts.get(str(v), 0) + 1
    return sorted(counts.items(), key=lambda x: -x[1])[:n]

results = []
errors  = []

print(f"{'Query key':<40} {'§':<4} {'Hits':>8}  Top countries")
print("-" * 90)

for key, (query, section) in sorted(QUERIES.items(), key=lambda x: x[1][1]):
    try:
        r = api.count(query, facets="country:5,org:3")
        total = r["total"]
        countries = [f"{f['value']}:{f['count']}" for f in r.get("facets", {}).get("country", [])]
        orgs      = [f['value'] for f in r.get("facets", {}).get("org", [])]
        row = {
            "key": key, "section": section, "query": query,
            "total": total, "top_countries": countries, "top_orgs": orgs
        }
        results.append(row)
        print(f"{key:<40} {section:<4} {total:>8}  {', '.join(countries[:3])}")
    except shodan.APIError as e:
        errors.append({"key": key, "query": query, "error": str(e)})
        print(f"{key:<40} {section:<4}    ERROR  {e}")
    time.sleep(1.1)  # stay under 1 req/s rate limit

# Save full results
out = Path(__file__).parent / "shodan-new-categories-results.json"
out.write_text(json.dumps({"results": results, "errors": errors}, indent=2))
print(f"\nFull results → {out}")

# Print section summary
print("\n=== SECTION SUMMARY ===")
by_section = {}
for r in results:
    s = r["section"]
    by_section.setdefault(s, []).append(r)

section_names = {
    18: "Jupyter/JupyterHub",
    19: "Streamlit",
    20: "Gradio/A1111/Langflow",
    21: "Browser Agents",
    22: "Data Labeling",
    23: "AI Safety Eval",
    24: "LLM Observability",
    25: "Elasticsearch/OpenSearch",
    26: "Mem0/Agent Memory",
}

for s in sorted(by_section):
    rows = by_section[s]
    top   = sorted(rows, key=lambda x: -x["total"])
    total_max = top[0]["total"] if top else 0
    print(f"  §{s} {section_names.get(s,''):<30} top query hits: {total_max:>8}  ({top[0]['key'] if top else ''})")
