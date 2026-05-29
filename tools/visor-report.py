#!/usr/bin/env python3
"""
visor-report - NuClide survey -> interactive drill-down HTML report.

WHY THIS EXISTS: every survey ends as an ugly findings-breakdown.txt. This turns a
survey's findings into one self-contained HTML file with the drill-down UX:
findings accordion -> click a finding -> host chips -> click a host -> detail drawer
(spec table, color-coded namespaces/tags, operator attribution). One file, no server,
opens in any browser. Reusable for EVERY category, not just FinOps.

TWO INPUT PATHS:
  1. A report JSON in the schema below (rich, survey-author-defined findings):
       visor-report.py render data.json -o report.html
  2. Straight from the VisorLog ledger (auto, best-effort, every survey ingests there):
       visor-report.py from-visorlog --db nuclide.db --sector finops-cost-api -o report.html

REPORT JSON SCHEMA (v1):
{
  "meta": {
    "org": "NuClide Research", "kind": "// Field Survey", "date": "2026-05-29",
    "title_html": "...<span class='em'>accent</span>...",   # h1 (HTML allowed)
    "subtitle_html": "...",                                  # lede (HTML allowed)
    "stats": [ {"value": "67", "label": "instances", "style": ""} ]  # style: ""|"cyan"|"hot"
  },
  "findings": [ {"id":"F1","tier":"HIGH","title":"...","why":"...","basis":"...","hosts":["<key>"]} ],
                # tier in CRITICAL|HIGH|MEDIUM|LOW|INFO
  "hosts": { "<key>": {
      "label": "<display, defaults to key>",
      "chip": {"note":"$6,837/d", "flags":[{"cls":"cred|helm|attr","title":"..."}]},
      "badges": [ {"text":"OPEN_API","cls":""} ],            # cls: ""|"cred"|"helm"
      "spec": [ ["Cloud","AWS / EKS / us-east-2",""], ["Daily cost","$280/d","cost"] ],  # [label,value,cls] cls: ""|"cost"|"cy"
      "tag_groups": [ {"label":"Leaked namespaces","legend_html":"...","tags":[{"name":"vault","cls":"sec"}]} ],
                # tag cls: ""|"sec"|"ai" (or any class you style)
      "attribution": {"op":"...","conf":"high|low|none","note":"..."}   # or null
  } },
  "panels": [ {"title":"The chain","kind":"steps","items":["step 1","step 2"]},
              {"title":"Attribution","kind":"callout","callout":{"title":"Org","body":"..."}},
              {"title":"Caveats","kind":"bullets","items":["..."]} ]
}

Minimal valid input = meta(title_html) + findings + hosts. Everything else is optional.
"""
import json, sys, argparse, sqlite3, re

TEMPLATE = r'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{--bg:#070a0c;--panel:#0d1217;--panel-2:#11171d;--line:#1b242c;--line-2:#27333c;
 --ink:#cdd8de;--ink-dim:#8493a0;--ink-faint:#5a6975;--cyan:#3fe0c8;--cyan-dim:#1d6b62;
 --crit:#ff453a;--hi:#ff6b35;--med:#ffb340;--low:#4aa3ff;--info:#728495;--grid:rgba(63,224,200,.045);}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--ink);font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:13.5px;line-height:1.5;
 background-image:linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px);background-size:34px 34px;-webkit-font-smoothing:antialiased;}
body::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:1;opacity:.035;mix-blend-mode:overlay;
 background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");}
a{color:var(--cyan);text-decoration:none}.wrap{max-width:1180px;margin:0 auto;padding:0 22px;position:relative;z-index:2}
header{border-bottom:1px solid var(--line);padding:26px 0 20px;margin-bottom:2px}
.kicker{display:flex;gap:14px;align-items:center;font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--ink-faint)}
.kicker .dot{width:7px;height:7px;border-radius:50%;background:var(--cyan);box-shadow:0 0 10px var(--cyan)}.kicker .spacer{flex:1;height:1px;background:var(--line)}
h1{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:clamp(26px,4.4vw,46px);line-height:1.02;letter-spacing:-.02em;margin:16px 0 6px;color:#eef4f6}
h1 .em{color:var(--cyan)}.sub{color:var(--ink-dim);font-size:12.5px;max-width:64ch}.sub b{color:var(--ink)}
.stats{display:grid;grid-template-columns:repeat(var(--ncols,6),1fr);gap:1px;background:var(--line);border:1px solid var(--line);margin:22px 0 6px}
.stat{background:var(--panel);padding:14px 14px 12px}
.stat .n{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:24px;color:#eef4f6;letter-spacing:-.02em}
.stat .n.cyan{color:var(--cyan)}.stat .n.hot{color:var(--hi)}
.stat .l{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-faint);margin-top:3px}
.bar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:26px 0 14px}
.seg{display:flex;border:1px solid var(--line-2);border-radius:2px;overflow:hidden}
.seg button{background:transparent;border:0;border-right:1px solid var(--line);color:var(--ink-dim);font-family:inherit;font-size:11px;letter-spacing:.08em;text-transform:uppercase;padding:7px 11px;cursor:pointer}
.seg button:last-child{border-right:0}.seg button.on{background:var(--panel-2);color:#eef4f6}
.seg button.on[data-t=CRITICAL]{color:var(--crit)}.seg button.on[data-t=HIGH]{color:var(--hi)}.seg button.on[data-t=MEDIUM]{color:var(--med)}.seg button.on[data-t=LOW]{color:var(--low)}.seg button.on[data-t=INFO]{color:var(--info)}
.bar input{flex:1;min-width:180px;background:var(--panel);border:1px solid var(--line-2);color:var(--ink);font-family:inherit;font-size:12.5px;padding:8px 11px;border-radius:2px}
.bar input::placeholder{color:var(--ink-faint)}.bar input:focus{outline:0;border-color:var(--cyan-dim)}
.finding{border:1px solid var(--line);border-top:0;background:var(--panel)}.finding:first-of-type{border-top:1px solid var(--line)}
.fhead{display:grid;grid-template-columns:46px 84px 1fr auto;gap:14px;align-items:center;padding:15px 18px;cursor:pointer;transition:background .15s}.fhead:hover{background:var(--panel-2)}
.fid{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:17px;color:var(--ink-faint)}
.tier{font-size:10px;font-weight:600;letter-spacing:.12em;padding:4px 8px;text-align:center;border:1px solid;border-radius:2px}
.tier.CRITICAL{color:var(--crit);border-color:#5a2020;background:rgba(255,69,58,.08)}
.tier.HIGH{color:var(--hi);border-color:#5a2e1a;background:rgba(255,107,53,.07)}
.tier.MEDIUM{color:var(--med);border-color:#5a451a;background:rgba(255,179,64,.06)}
.tier.LOW{color:var(--low);border-color:#1f3a5a;background:rgba(74,163,255,.06)}
.tier.INFO{color:var(--info);border-color:#2a343c;background:rgba(114,132,149,.05)}
.ftitle{font-size:14px;color:#e6eef1;font-weight:500}
.fmeta{display:flex;align-items:center;gap:14px;color:var(--ink-faint);font-size:11px;letter-spacing:.05em}.fmeta .cnt{color:var(--ink);font-weight:600}
.caret{transition:transform .25s;color:var(--ink-faint)}.finding.open .caret{transform:rotate(90deg);color:var(--cyan)}
.fbody{max-height:0;overflow:hidden;transition:max-height .35s ease}.finding.open .fbody{max-height:2200px}
.fbody-in{padding:4px 18px 20px;border-top:1px dashed var(--line-2)}
.kv{margin:12px 0}.kv .k{font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);margin-bottom:4px}
.kv .v{color:var(--ink-dim);font-size:12.5px;max-width:92ch}.kv .v.mono{color:var(--ink-faint)}
.hosts{display:flex;flex-wrap:wrap;gap:7px;margin-top:6px}
.chip{display:flex;align-items:center;gap:8px;background:var(--panel-2);border:1px solid var(--line-2);padding:6px 9px;border-radius:2px;cursor:pointer;font-size:12px;transition:border-color .15s,transform .05s}
.chip:hover{border-color:var(--cyan-dim);transform:translateY(-1px)}.chip .ip{color:#dbe6ea}.chip .cost{color:var(--med);font-size:11px}
.chip .flag{width:6px;height:6px;border-radius:50%}.chip .flag.helm{background:var(--hi)}.chip .flag.attr{background:var(--cyan)}.chip .flag.cred{background:var(--crit);box-shadow:0 0 7px var(--crit)}
.lower{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:22px;margin:34px 0 60px}
.card{border:1px solid var(--line);background:var(--panel);padding:18px 20px}
.card h3{font-family:"Bricolage Grotesque",sans-serif;font-weight:700;font-size:15px;margin:0 0 14px;color:#eef4f6;letter-spacing:-.01em}
.chain{counter-reset:step;list-style:none;margin:0;padding:0}
.chain li{counter-increment:step;position:relative;padding:0 0 16px 34px;color:var(--ink-dim);font-size:12.5px}
.chain li::before{content:counter(step);position:absolute;left:0;top:-1px;width:22px;height:22px;border:1px solid var(--cyan-dim);color:var(--cyan);border-radius:50%;display:grid;place-items:center;font-size:11px}
.chain li::after{content:"";position:absolute;left:10.5px;top:23px;bottom:2px;width:1px;background:var(--line-2)}
.chain li:last-child{padding-bottom:0}.chain li:last-child::after{display:none}
.callout{border:1px solid #244;background:linear-gradient(180deg,rgba(63,224,200,.05),transparent);padding:14px}
.callout .org{font-family:"Bricolage Grotesque",sans-serif;font-weight:700;font-size:16px;color:var(--cyan)}.callout .d{color:var(--ink-dim);font-size:12px;margin-top:5px}
.bullets{margin:0;padding:0;list-style:none}
.bullets li{padding:7px 0 7px 18px;border-top:1px solid var(--line);color:var(--ink-dim);font-size:12px;position:relative}
.bullets li:first-child{border-top:0}.bullets li::before{content:"!";position:absolute;left:0;top:7px;color:var(--med);font-weight:600}
.scrim{position:fixed;inset:0;background:rgba(2,5,7,.72);backdrop-filter:blur(3px);opacity:0;pointer-events:none;transition:opacity .25s;z-index:40}.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100%;width:min(560px,94vw);background:var(--panel);border-left:1px solid var(--line-2);transform:translateX(100%);transition:transform .3s cubic-bezier(.4,0,.2,1);z-index:50;overflow-y:auto;box-shadow:-30px 0 60px rgba(0,0,0,.5)}.drawer.on{transform:translateX(0)}
.dhead{position:sticky;top:0;background:var(--panel);border-bottom:1px solid var(--line);padding:18px 22px;z-index:2}
.dhead .row{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.dhead .ip{font-family:"Bricolage Grotesque",sans-serif;font-weight:800;font-size:22px;color:#eef4f6;word-break:break-all}
.dhead .x{background:transparent;border:1px solid var(--line-2);color:var(--ink-dim);width:30px;height:30px;border-radius:2px;cursor:pointer;font-size:15px;flex:none}.dhead .x:hover{border-color:var(--hi);color:var(--hi)}
.dhead .tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
.dtag{font-size:10px;letter-spacing:.08em;text-transform:uppercase;padding:3px 7px;border:1px solid var(--line-2);color:var(--ink-dim);border-radius:2px}
.dtag.cred{color:var(--crit);border-color:#5a2020;background:rgba(255,69,58,.08)}.dtag.helm{color:var(--hi);border-color:#5a2e1a}
.dbody{padding:18px 22px 50px}
.spec{display:grid;grid-template-columns:140px 1fr;gap:2px 14px;font-size:12.5px;margin-bottom:18px}
.spec dt{color:var(--ink-faint);text-transform:uppercase;letter-spacing:.1em;font-size:10px;padding-top:3px}
.spec dd{margin:0;color:var(--ink);word-break:break-word}.spec dd.cost{color:var(--med)}.spec dd.cy{color:var(--cyan)}
.seclabel{font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:var(--cyan);margin:18px 0 8px;border-top:1px solid var(--line);padding-top:14px}
.ns{display:flex;flex-wrap:wrap;gap:5px}.ns span{font-size:11px;padding:3px 7px;border:1px solid var(--line-2);color:var(--ink-dim);border-radius:2px}
.ns span.sec{color:var(--hi);border-color:#5a2e1a;background:rgba(255,107,53,.06)}.ns span.ai{color:var(--cyan);border-color:var(--cyan-dim);background:rgba(63,224,200,.05)}
.attr-d{border:1px solid var(--line-2);padding:12px;font-size:12px}.attr-d .o{font-weight:600;color:#eef4f6}.attr-d .o.cy{color:var(--cyan)}
.attr-d .cf{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ink-faint);margin-left:8px}.attr-d .nt{color:var(--ink-dim);margin-top:6px}
footer{border-top:1px solid var(--line);padding:20px 0 40px;color:var(--ink-faint);font-size:11px;letter-spacing:.05em}
.reveal{opacity:0;transform:translateY(8px);animation:rise .5s forwards}@keyframes rise{to{opacity:1;transform:none}}
@media(max-width:820px){.stats{grid-template-columns:repeat(3,1fr)}}
</style></head><body>
<div class="wrap">
  <header>
    <div class="kicker"><span class="dot"></span><span id="k-org"></span><span id="k-kind"></span><span class="spacer"></span><span id="k-date"></span></div>
    <h1 id="h1"></h1><p class="sub" id="sub"></p>
    <div class="stats" id="stats"></div>
  </header>
  <div class="bar"><div class="seg" id="filters"></div><input id="search" placeholder="filter by host, tag, operator, anything..."></div>
  <div id="findings"></div>
  <div class="lower" id="panels"></div>
  <footer id="foot">NuClide Research // verification is the load-bearing stage // generated by visor-report</footer>
</div>
<div class="scrim" id="scrim"></div><aside class="drawer" id="drawer"></aside>
<script>
const REPORT_DATA = __DATA__;
const D=REPORT_DATA, H=D.hosts||{}, M=D.meta||{};
const $=(s,r=document)=>r.querySelector(s), el=(t,c,h)=>{const e=document.createElement(t);if(c)e.className=c;if(h!=null)e.innerHTML=h;return e;};
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
$('#k-org').textContent=M.org||'NuClide Research'; $('#k-kind').textContent=M.kind||'// Field Survey'; $('#k-date').textContent=M.date||'';
$('#h1').innerHTML=M.title_html||M.title||'Survey'; $('#sub').innerHTML=M.subtitle_html||M.subtitle||'';
const stats=M.stats||[]; const sc=$('#stats'); sc.style.setProperty('--ncols',Math.min(stats.length||1,6));
stats.forEach(s=>{const d=el('div','stat');d.innerHTML=`<div class="n ${s.style||''}">${esc(s.value)}</div><div class="l">${esc(s.label)}</div>`;sc.appendChild(d);});
// filter buttons from tiers present
const ORDER=['CRITICAL','HIGH','MEDIUM','LOW','INFO'];
const present=ORDER.filter(t=>(D.findings||[]).some(f=>f.tier===t));
const fb=$('#filters'); let filter='ALL', q='';
[['ALL','All'],...present.map(t=>[t,t[0]+t.slice(1).toLowerCase()])].forEach(([t,lab],i)=>{const b=el('button',i===0?'on':'',lab);b.dataset.t=t;fb.appendChild(b);});
fb.addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;[...fb.children].forEach(x=>x.classList.remove('on'));b.classList.add('on');filter=b.dataset.t;render();});
let tmr;$('#search').addEventListener('input',e=>{clearTimeout(tmr);tmr=setTimeout(()=>{q=e.target.value.trim().toLowerCase();render();},120);});
function hostSearchStr(k){const h=H[k]||{};let s=k+' '+(h.label||'');(h.spec||[]).forEach(r=>s+=' '+r[1]);(h.tag_groups||[]).forEach(g=>(g.tags||[]).forEach(t=>s+=' '+t.name));if(h.attribution)s+=' '+(h.attribution.op||'');(h.badges||[]).forEach(b=>s+=' '+b.text);return s.toLowerCase();}
function chip(k){const h=H[k]||{};const c=el('div','chip');c.onclick=()=>openHost(k);
  const fl=((h.chip||{}).flags||[]).map(f=>`<span class="flag ${f.cls}" title="${esc(f.title||'')}"></span>`).join('');
  const note=(h.chip||{}).note?`<span class="cost">${esc(h.chip.note)}</span>`:'';
  c.innerHTML=`<span class="ip">${esc(h.label||k)}</span>${note}${fl}`;return c;}
const fw=$('#findings');
function render(){fw.innerHTML='';
  (D.findings||[]).filter(f=>filter==='ALL'||f.tier===filter).forEach((f,i)=>{
    let hs=f.hosts||[];
    if(q){const hit=(f.id+' '+f.title+' '+(f.why||'')).toLowerCase().includes(q);hs=(f.hosts||[]).filter(k=>hostSearchStr(k).includes(q));if(!hit&&!hs.length)return;}
    const fd=el('div','finding reveal');fd.style.animationDelay=(i*40)+'ms';
    fd.innerHTML=`<div class="fhead"><span class="fid">${esc(f.id)}</span><span class="tier ${f.tier}">${esc(f.tier)}</span><span class="ftitle">${esc(f.title)}</span><span class="fmeta"><span class="cnt">${(f.hosts||[]).length}</span> hosts <span class="caret">&#9656;</span></span></div><div class="fbody"><div class="fbody-in">${f.why?`<div class="kv"><div class="k">Why it matters</div><div class="v">${esc(f.why)}</div></div>`:''}${f.basis?`<div class="kv"><div class="k">Verified basis</div><div class="v mono">${esc(f.basis)}</div></div>`:''}<div class="kv"><div class="k">Hosts${q&&hs.length!==(f.hosts||[]).length?` (${hs.length} match)`:''}</div><div class="hosts"></div></div></div></div>`;
    const box=fd.querySelector('.hosts');(q?hs:(f.hosts||[])).forEach(k=>box.appendChild(chip(k)));
    fd.querySelector('.fhead').onclick=()=>fd.classList.toggle('open');if(q)fd.classList.add('open');
    fw.appendChild(fd);});
  if(!fw.children.length)fw.appendChild(el('div','sub',`No findings match "${esc(q)}".`));}
const drawer=$('#drawer'),scrim=$('#scrim');
function openHost(k){const h=H[k];if(!h)return;
  const badges=(h.badges||[]).map(b=>`<span class="dtag ${b.cls||''}">${esc(b.text)}</span>`).join('');
  const spec=(h.spec||[]).map(r=>`<dt>${esc(r[0])}</dt><dd class="${r[2]||''}">${esc(r[1])}</dd>`).join('');
  const groups=(h.tag_groups||[]).map(g=>`<div class="seclabel">${g.label||'Tags'}${g.legend_html?' &mdash; '+g.legend_html:''}</div><div class="ns">${(g.tags||[]).map(t=>`<span class="${t.cls||''}">${esc(t.name)}</span>`).join('')||'<span>none</span>'}</div>`).join('');
  const a=h.attribution;const attr=a?`<div class="seclabel">Attribution</div><div class="attr-d"><span class="o ${a.conf==='high'?'cy':''}">${esc(a.op)}</span><span class="cf">conf: ${esc(a.conf)}</span><div class="nt">${esc(a.note||'')}</div></div>`:'';
  drawer.innerHTML=`<div class="dhead"><div class="row"><div class="ip">${esc(h.label||k)}</div><button class="x" onclick="closeHost()">&times;</button></div><div class="tags">${badges}</div></div><div class="dbody">${spec?`<dl class="spec">${spec}</dl>`:''}${attr}${groups}</div>`;
  drawer.classList.add('on');scrim.classList.add('on');}
function closeHost(){drawer.classList.remove('on');scrim.classList.remove('on');}
scrim.onclick=closeHost;document.addEventListener('keydown',e=>{if(e.key==='Escape')closeHost();});
// panels
const pw=$('#panels');(D.panels||[]).forEach(p=>{const c=el('div','card');let body='';
  if(p.kind==='steps')body=`<ol class="chain">${(p.items||[]).map(i=>`<li>${esc(i)}</li>`).join('')}</ol>`;
  else if(p.kind==='bullets')body=`<ul class="bullets">${(p.items||[]).map(i=>`<li>${esc(i)}</li>`).join('')}</ul>`;
  else if(p.kind==='callout'){const co=p.callout||{};body=`<div class="callout"><div class="org">${esc(co.title)}</div><div class="d">${co.body_html||esc(co.body||'')}</div></div>`;}
  c.innerHTML=`<h3>${esc(p.title)}</h3>${body}`;pw.appendChild(c);});
if(M.footer)$('#foot').textContent=M.footer;
render();
</script></body></html>'''


def render(data):
    title = re.sub('<[^>]+>', '', (data.get('meta', {}).get('title_html') or data.get('meta', {}).get('title') or 'NuClide Survey'))
    html = TEMPLATE.replace('__TITLE__', title)
    return html.replace('__DATA__', json.dumps(data, ensure_ascii=False))


def from_visorlog(db, sector=None):
    """Best-effort report straight from the VisorLog ledger (events table).
    Groups findings by event_type/severity within the sector. Rich per-host detail
    depends on what was ingested; a survey-specific adapter produces a better report."""
    c = sqlite3.connect(db); c.row_factory = sqlite3.Row
    where = "WHERE sector=?" if sector else ""
    rows = list(c.execute(f"SELECT * FROM events {where} ORDER BY event_severity", ([sector] if sector else [])))
    hosts, by_sev = {}, {}
    SEVTIER = {'critical': 'CRITICAL', 'high': 'HIGH', 'medium': 'MEDIUM', 'low': 'LOW', 'info': 'INFO', 'informational': 'INFO'}
    for r in rows:
        ip = r['host_ip'] or f"event-{r['id']}"
        try: tags = json.loads(r['tags'] or '[]')
        except Exception: tags = []
        try: raw = json.loads(r['raw'] or '{}')
        except Exception: raw = {}
        spec = [["Sector", r['sector'] or '—', ''], ["Severity", r['event_severity'] or '—', ''], ["Source", r['source'] or '—', '']]
        for k in ('base_url', 'port', 'title'):
            if raw.get(k) is not None: spec.append([k, str(raw[k]), 'cy' if k == 'base_url' else ''])
        if r['org_name']: spec.append(["Org", r['org_name'], ''])
        if r['org_country']: spec.append(["Country", r['org_country'], ''])
        hosts[ip] = {"label": ip, "chip": {"flags": []},
                     "badges": [{"text": t, "cls": ""} for t in tags] + [{"text": r['event_severity'] or '', "cls": ""}],
                     "spec": spec,
                     "tag_groups": [{"label": "Notes", "tags": [{"name": (r['notes'] or '').strip(), "cls": ""}]}] if r['notes'] else [],
                     "attribution": ({"op": r['org_name'], "conf": "low", "note": f"From ledger org_name ({r['org_country'] or 'country unknown'})."} if r['org_name'] else None)}
        tier = SEVTIER.get((r['event_severity'] or 'info').lower(), 'INFO')
        by_sev.setdefault(tier, []).append(ip)
    findings = []
    for i, tier in enumerate(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']):
        if tier in by_sev:
            findings.append({"id": f"S{i}", "tier": tier, "title": f"{tier.title()} severity findings in sector {sector or 'all'}",
                             "why": "Auto-grouped from the VisorLog ledger by severity. Use a survey-specific adapter for richer per-finding grouping.",
                             "basis": f"event_severity == {tier.lower()} in nuclide.db", "hosts": by_sev[tier]})
    data = {"meta": {"org": "NuClide Research", "kind": "// Ledger Report", "date": "",
                     "title_html": f"VisorLog ledger: <span class='em'>{sector or 'all sectors'}</span>",
                     "subtitle_html": f"Auto-generated from {len(rows)} ledger events. For the drill-down report quality, feed a survey-specific report JSON instead.",
                     "stats": [{"value": str(len(rows)), "label": "events", "style": ""},
                               {"value": str(len(hosts)), "label": "hosts", "style": "cyan"},
                               {"value": str(len(findings)), "label": "severity bands", "style": ""}]},
            "findings": findings, "hosts": hosts, "panels": []}
    return data


def main():
    ap = argparse.ArgumentParser(description="NuClide survey -> interactive drill-down HTML report")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("render", help="render a report JSON to HTML")
    r.add_argument("input", nargs="?", default="-", help="report JSON file, or - for stdin")
    r.add_argument("-o", "--out", default="-", help="output HTML file, or - for stdout")
    v = sub.add_parser("from-visorlog", help="auto-build a report from the VisorLog ledger")
    v.add_argument("--db", required=True)
    v.add_argument("--sector", default=None)
    v.add_argument("-o", "--out", default="-")
    a = ap.parse_args()
    if a.cmd == "render":
        data = json.load(sys.stdin if a.input == "-" else open(a.input))
    else:
        data = from_visorlog(a.db, a.sector)
    html = render(data)
    if a.out == "-": sys.stdout.write(html)
    else:
        open(a.out, "w").write(html); print(f"wrote {a.out} ({len(html)} bytes)", file=sys.stderr)


if __name__ == "__main__":
    main()
