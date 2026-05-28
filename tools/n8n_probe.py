#!/usr/bin/env python3
"""n8n version sweep. Probes /rest/settings, header x-n8n-version, HTML body."""
import asyncio, csv, json, re, sys
import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONCURRENCY = 80
VER_RE = re.compile(r'"versionCli"\s*:\s*"([^"]+)"')
VER_RE2 = re.compile(r'n8n[/ ]v?(\d+\.\d+[\.\d]*)', re.I)

async def probe(session, target):
    base = target.rstrip('/')
    result = {'target': target, 'version': '', 'auth_state': '', 'method': ''}
    for path in ['/rest/settings', '/rest/version', '/']:
        url = base + path
        try:
            async with session.get(url, ssl=False, allow_redirects=True) as r:
                ver_header = r.headers.get('x-n8n-version', '')
                if ver_header:
                    result.update({'version': ver_header, 'auth_state': 'unauth', 'method': 'header'})
                    return result
                if r.status == 200:
                    body = await r.text(errors='ignore')
                    m = VER_RE.search(body) or VER_RE2.search(body)
                    if m:
                        result.update({'version': m.group(1), 'auth_state': 'unauth', 'method': path})
                        return result
                    result['auth_state'] = 'unauth'
                elif r.status in (401, 403):
                    result['auth_state'] = 'auth'
        except:
            pass
    return result

async def run(targets, out_path):
    sem = asyncio.Semaphore(CONCURRENCY)
    connector = aiohttp.TCPConnector(ssl=False, limit=CONCURRENCY + 20)
    rows = []
    async with aiohttp.ClientSession(connector=connector, timeout=TIMEOUT) as session:
        async def bounded(t):
            async with sem:
                return await probe(session, t)
        tasks = [bounded(t) for t in targets]
        done = 0
        for coro in asyncio.as_completed(tasks):
            r = await coro
            rows.append(r)
            done += 1
            if done % 100 == 0 or done == len(tasks):
                found = sum(1 for x in rows if x['version'])
                print(f'  [{done}/{len(tasks)}] versioned: {found}', file=sys.stderr)
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['target', 'version', 'auth_state', 'method'])
        w.writeheader()
        w.writerows(sorted(rows, key=lambda x: (not x['version'], x['target'])))
    versioned = sum(1 for r in rows if r['version'])
    print(f"Saved {out_path} ({len(rows)} rows, {versioned} versioned)")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('-o', '--output', default='n8n-versions.csv')
    args = p.parse_args()
    with open(args.input) as f:
        targets = [l.strip() for l in f if l.strip()]
    asyncio.run(run(targets, args.output))
