#!/usr/bin/env python3
"""
verify_chroma_version — multi-signal version fingerprinter for Chroma.

Hypothesis to test (T&E discipline): 269 hosts return literal "1.0.0" on
/api/v2/version. Either they're all running 1.0.0 (suspicious uniformity) OR
the endpoint always returns a hardcoded string regardless of actual version
(the Jupyter /api flaw, applied here).

Signals collected per host:
  1. /api/v2/version             — what the host SAYS
  2. /api/v1/version             — present on 0.5.x family ONLY (removed in 0.6+)
  3. /api/v2/heartbeat           — universal Chroma signal, no version info
  4. /api/v2 (root)              — sometimes carries openapi or version info
  5. /openapi.json               — FastAPI's auto-generated schema; contains title+version
  6. /docs (Swagger)             — sometimes leaks version in <title>
  7. server / x-* response headers
  8. chroma-trace-id format      — 32-char hex always, no version info but confirms Chroma
  9. /api/v2/auth/identity       — exists in 1.x, may 404 on 0.6.x
  10. behavior on a NON-EXISTENT collection path — error message format changes between versions

Decision rule per host:
  - HIGH-CONF version: /api/v1/version + chroma-trace-id present (0.5.x confirmed)
  - HIGH-CONF version: /openapi.json info.version + matches /api/v2/version
  - MEDIUM-CONF version: /api/v2/version returns string AND /api/v1 returns 404 (0.6+)
  - LOW-CONF version: /api/v2/version literal "1.0.0" with no /openapi or other corroboration
    -> flag as "v2-endpoint-says-1.0.0-but-unverified"

Output: ~/syllabus/shodan/chroma-version-verify/rollup.json
"""
import asyncio, aiohttp, json, sys, re, ssl
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path.home()/"syllabus"/"shodan"/"chroma-version-verify"
OUT.mkdir(parents=True, exist_ok=True)

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONC = 40

PATHS = [
    ('/api/v1/version',         'v1_version'),
    ('/api/v2/version',         'v2_version'),
    ('/api/v2/heartbeat',       'v2_heartbeat'),
    ('/api/v2',                 'v2_root'),
    ('/openapi.json',           'openapi'),
    ('/docs',                   'docs'),
    ('/api/v2/auth/identity',   'v2_auth'),
    ('/api/v2/tenants/default_tenant/databases/default_database/collections/__non_existent_canary__',
                                'v2_404_format'),
]

VERSION_RX = re.compile(r'"version"\s*:\s*"([0-9]+\.[0-9]+\.[0-9]+[^"]*)"')


async def probe(s, target):
    base = target.rstrip('/')
    out = {'target': target, 'evidence': {}, 'headers': {}}
    for path, key in PATHS:
        url = base + path
        try:
            async with s.get(url, ssl=False, allow_redirects=False) as r:
                body = await r.text(errors='ignore')
                out['evidence'][key] = {
                    'status': r.status,
                    'body': body[:2000],
                    'content_type': r.headers.get('content-type',''),
                }
                if 'chroma-trace-id' in {k.lower() for k in r.headers.keys()}:
                    out['has_chroma_trace_id'] = True
                if key == 'v2_heartbeat':
                    out['headers'] = {k:v for k,v in r.headers.items() if k.lower() in (
                        'server','x-powered-by','x-version','chroma-trace-id','chroma-version'
                    )}
        except asyncio.TimeoutError:
            out['evidence'][key] = {'status': 0, 'body': '', 'err': 'timeout'}
        except Exception as e:
            out['evidence'][key] = {'status': 0, 'body': '', 'err': type(e).__name__}
    return classify(out)


def classify(h):
    ev = h['evidence']
    decision = {
        'confidence': 'NONE',
        'version': None,
        'family': None,
        'reasons': [],
    }

    # Signal A: /api/v1/version returns a parseable version string
    v1 = ev.get('v1_version', {})
    if v1.get('status') == 200:
        body = v1.get('body','').strip().strip('"')
        m = re.match(r'^[0-9]+\.[0-9]+\.[0-9]+', body)
        if m:
            decision['version'] = m.group(0)
            decision['family'] = '0.5.x' if body.startswith('0.5') else ('0.6.x' if body.startswith('0.6') else 'unknown_v1')
            decision['confidence'] = 'HIGH'
            decision['reasons'].append(f'v1/version returned {body!r}')

    # Signal B: /api/v2/version
    v2 = ev.get('v2_version', {})
    v2_str = None
    if v2.get('status') == 200:
        body = v2.get('body','').strip().strip('"')
        m = re.match(r'^[0-9]+\.[0-9]+\.[0-9]+', body)
        if m:
            v2_str = m.group(0)

    # Signal C: /openapi.json version
    op = ev.get('openapi', {})
    op_version = None
    if op.get('status') == 200:
        body = op.get('body','')
        m = VERSION_RX.search(body)
        if m:
            op_version = m.group(1)
            decision['reasons'].append(f'openapi.info.version={op_version!r}')
            if decision['confidence'] != 'HIGH':
                decision['version'] = op_version
                decision['family'] = op_version.split('.',1)[0] + '.x'
                decision['confidence'] = 'HIGH'

    # Signal D: corroborate v2 string with openapi or other signal
    if v2_str and not decision['version']:
        v1_404 = ev.get('v1_version', {}).get('status') in (404, 410)
        if v1_404:
            # v2 string + v1 removed = 0.6+ or 1.x
            decision['version'] = v2_str
            decision['family'] = '1.x' if v2_str.startswith('1.') else '0.6.x'
            decision['confidence'] = 'MEDIUM'
            decision['reasons'].append(f'v2/version={v2_str!r} AND v1 returns {ev["v1_version"].get("status")}')
        else:
            decision['version'] = v2_str
            decision['family'] = 'unknown'
            decision['confidence'] = 'LOW'
            decision['reasons'].append(f'v2/version={v2_str!r} no v1 corroboration')

    # Flag the suspicious "1.0.0" case explicitly
    if v2_str == '1.0.0' and not op_version:
        decision['flag_unverified_1_0_0'] = True
        decision['reasons'].append('v2_version="1.0.0" with NO openapi corroboration — potential endpoint fingerprint quirk')

    # Auth-identity signal: only in 1.x
    auth = ev.get('v2_auth', {})
    if auth.get('status') == 200:
        decision['reasons'].append(f'v2/auth/identity present (1.x feature)')
        if decision['family'] in (None, 'unknown'):
            decision['family'] = '1.x_inferred'

    h['decision'] = decision
    return h


async def main():
    targets = [l.strip() for l in open('/tmp/chroma_tier2_urls.txt') if l.strip()]
    print(f"[verify_chroma_version] targets={len(targets)} conc={CONC}", file=sys.stderr)

    sem = asyncio.Semaphore(CONC)
    conn = aiohttp.TCPConnector(ssl=False, limit=CONC+10)
    async with aiohttp.ClientSession(connector=conn, timeout=TIMEOUT) as s:
        async def b(t):
            async with sem:
                return await probe(s, t)
        import time
        t0 = time.time()
        rows = []
        tasks = [asyncio.create_task(b(t)) for t in targets]
        done = 0
        for c in asyncio.as_completed(tasks):
            rows.append(await c)
            done += 1
            if done % 50 == 0:
                print(f"  [{done}/{len(tasks)}] {time.time()-t0:.1f}s", file=sys.stderr)

    # rollup
    conf = Counter(r['decision']['confidence'] for r in rows)
    fam = Counter(r['decision'].get('family') or 'none' for r in rows)
    ver = Counter(r['decision'].get('version') or 'none' for r in rows)
    unverified_1_0_0 = sum(1 for r in rows if r['decision'].get('flag_unverified_1_0_0'))
    has_openapi = sum(1 for r in rows if r['evidence'].get('openapi',{}).get('status') == 200)
    has_v2_auth = sum(1 for r in rows if r['evidence'].get('v2_auth',{}).get('status') == 200)

    print("\nCONFIDENCE distribution:", file=sys.stderr)
    for k,n in conf.most_common(): print(f"  {n:>4}  {k}", file=sys.stderr)
    print("\nFAMILY distribution:", file=sys.stderr)
    for k,n in fam.most_common(): print(f"  {n:>4}  {k}", file=sys.stderr)
    print("\nVERSION distribution (top 15):", file=sys.stderr)
    for k,n in ver.most_common(15): print(f"  {n:>4}  {k}", file=sys.stderr)
    print(f"\nopenapi.json present: {has_openapi}/{len(rows)}", file=sys.stderr)
    print(f"v2/auth/identity present (1.x signal): {has_v2_auth}/{len(rows)}", file=sys.stderr)
    print(f"flag_unverified_1_0_0 (v2 says 1.0.0 but no openapi corroborates): {unverified_1_0_0}/{len(rows)}", file=sys.stderr)

    json.dump(rows, open(OUT/'rollup.json','w'), indent=2)
    print(f"\n-> {OUT}/rollup.json", file=sys.stderr)

if __name__ == '__main__':
    asyncio.run(main())
