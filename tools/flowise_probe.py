#!/usr/bin/env python3
"""Flowise version sweep. CVE-2024-36420: auth bypass < 1.8.2"""
import asyncio, csv, json, re, sys
import aiohttp
from packaging.version import Version, InvalidVersion

TIMEOUT = aiohttp.ClientTimeout(total=8, connect=4)
CONCURRENCY = 60
FIX_VER = Version('1.8.2')

def classify(ver):
    try:
        return 'VULNERABLE' if Version(ver) < FIX_VER else 'PATCHED'
    except InvalidVersion:
        return ''

async def probe(session, target):
    base = target.rstrip('/')
    result = {'target': target, 'version': '', 'auth_state': '', 'vulnerable': '', 'method': ''}
    for path in ['/api/v1/version', '/api/v1/chatflows', '/']:
        url = base + path
        try:
            async with session.get(url, ssl=False, allow_redirects=True) as r:
                if r.status == 200:
                    body = await r.text(errors='ignore')
                    if path == '/api/v1/version':
                        try:
                            j = json.loads(body)
                            ver = j.get('version') or j.get('versionNumber', '')
                            if ver:
                                result.update({'version': ver, 'auth_state': 'unauth',
                                               'vulnerable': classify(ver), 'method': path})
                                return result
                        except:
                            pass
                    m = re.search(r'"version"\s*:\s*"([^"]+)"', body)
                    if m:
                        ver = m.group(1)
                        result.update({'version': ver, 'auth_state': 'unauth',
                                       'vulnerable': classify(ver), 'method': path})
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
            if done % 50 == 0 or done == len(tasks):
                vuln = sum(1 for x in rows if x['vulnerable'] == 'VULNERABLE')
                print(f'  [{done}/{len(tasks)}] vulnerable: {vuln}', file=sys.stderr)
    order = {'VULNERABLE': 0, 'PATCHED': 1, '': 2}
    rows.sort(key=lambda x: (order.get(x['vulnerable'], 9), x['target']))
    with open(out_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['target', 'version', 'auth_state', 'vulnerable', 'method'])
        w.writeheader()
        w.writerows(rows)
    vuln = sum(1 for r in rows if r['vulnerable'] == 'VULNERABLE')
    pat = sum(1 for r in rows if r['vulnerable'] == 'PATCHED')
    print(f"Saved {out_path} | vulnerable: {vuln} | patched: {pat}")

if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('input')
    p.add_argument('-o', '--output', default='flowise-versions.csv')
    args = p.parse_args()
    with open(args.input) as f:
        targets = [l.strip() for l in f if l.strip()]
    asyncio.run(run(targets, args.output))
