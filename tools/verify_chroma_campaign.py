#!/usr/bin/env python3
"""
verify_chroma_campaign — second-pass verifier for the 2026-06-02 Chroma
CVE-2024-45829 mass-exploitation campaign.

What's already known (from sweep_chroma.py 2026-06-08 00:46):
  - 307 TIER-2 unauth hosts (UNAUTH /api/{v1,v2}/collections returns list)
  - 173 carry "probe-base-<ns>" + "probe-ef-<ns>" canary collections
  - 254 unique nanosecond timestamps, all clustered 2026-06-02 00:02:06–00:04:05 UTC
  - 65 hosts surface trust_remote_code:true in (truncated) body

What this verifier does:
  - Re-pulls /api/v1/collections AND /api/v2/.../collections WITHOUT body truncation
  - Per host: extracts FULL canary set (collection-name pairs, embedding model_name token)
  - Classifies drift: still-pwnd / cleaned-up / now-auth-on / TCP-down
  - Writes per-host JSON evidence + campaign-rollup

Output: ~/syllabus/shodan/chroma-campaign/{rollup.json, hosts/<ip>_<port>.json}

Restraint ethic: metadata only. No data reads (no /get, no /query).
"""
import os, sys, json, time, ssl, asyncio, re, urllib.parse, urllib.request, urllib.error
from pathlib import Path
from collections import Counter, defaultdict

OUT = Path.home()/"syllabus"/"shodan"/"chroma-campaign"
OUT.mkdir(parents=True, exist_ok=True)
(OUT/"hosts").mkdir(exist_ok=True)

CONCURRENCY = 30
TIMEOUT = 6

V1_COLL = "/api/v1/collections"
V2_COLL = "/api/v2/tenants/default_tenant/databases/default_database/collections"

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

CANARY_RX = re.compile(r'probe-(base|ef)-(\d{19})')
CVE_RX = re.compile(r'(/?nonexistent/cve\d{5}\w+|chromadb-poc-nonexistent\w+|cve\d{5}\w+)', re.I)


def get(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research; minimize=true)'})
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
            return r.status, r.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, ''
    except Exception as e:
        return 0, type(e).__name__


async def aget(target, path):
    scheme = 'http'
    if ':443' in target or ':8443' in target:
        scheme = 'https'
    url = f"{scheme}://{target}{path}"
    loop = asyncio.get_running_loop()
    status, body = await loop.run_in_executor(None, get, url)
    return status, body, url


def classify(v1, v2):
    """Return (state, evidence_path, n_coll, canary_pairs, cve_tokens, body_len)."""
    bodies = []
    chosen = None
    for tag, (status, body, url) in (('v2', v2), ('v1', v1)):
        if status == 200 and body.lstrip().startswith('['):
            try:
                arr = json.loads(body)
                if isinstance(arr, list):
                    chosen = (tag, status, body, url, arr)
                    break
            except json.JSONDecodeError:
                pass
        bodies.append((tag, status, body[:200]))

    if not chosen:
        # could be drifted offline, auth flip, or v2 redirect
        # detect: any 401/403 -> AUTH-FLIP; any TCP 0/timeout -> OFFLINE; any 404 path -> PATH-DRIFT
        codes = {v1[0], v2[0]}
        if 401 in codes or 403 in codes:
            return 'AUTH-FLIP', None, 0, [], [], 0
        if codes == {0}:
            return 'OFFLINE', None, 0, [], [], 0
        if 404 in codes and 0 not in codes:
            return 'PATH-DRIFT', None, 0, [], [], 0
        return 'UNKNOWN', None, 0, [], [], 0

    tag, status, body, url, arr = chosen
    names = []
    for c in arr:
        if isinstance(c, dict):
            n = c.get('name', '')
            if n:
                names.append(n)
    # canary pairs (base+ef sharing same timestamp = matched pair)
    by_ts = defaultdict(set)
    for n in names:
        m = CANARY_RX.match(n)
        if m:
            by_ts[m.group(2)].add(m.group(1))
    pairs = [ts for ts, kinds in by_ts.items() if kinds == {'base', 'ef'}]
    cve_tokens = CVE_RX.findall(body)

    # state
    if pairs:
        state = 'PWND-STILL'
    elif len(names) == 0:
        state = 'EMPTY-OPEN'
    else:
        state = 'CLEAN-OPEN'

    n_coll = len(arr)
    return state, tag, n_coll, pairs, cve_tokens, len(body), names


async def probe_host(target):
    v1 = await aget(target, V1_COLL)
    v2 = await aget(target, V2_COLL)
    state, api_tag, n_coll, pairs, cve_tokens, body_len, names = classify(v1, v2)
    out = {
        'target': target,
        'state': state,
        'api_tag': api_tag,
        'n_collections': n_coll,
        'canary_pairs': pairs,
        'cve_tokens_visible': cve_tokens,
        'body_len': body_len,
        'collection_names_sample': names[:10] if names else [],
        'probe_t': int(time.time()),
        'v1_status': v1[0],
        'v2_status': v2[0],
    }
    # write per-host full body for forensic record
    safe = target.replace(':', '_').replace('/', '_')
    full = {
        **out,
        'v1_body_full': v1[1],
        'v2_body_full': v2[1],
    }
    (OUT/"hosts"/f"{safe}.json").write_text(json.dumps(full, indent=2))
    return out


async def main():
    targets = [l.strip() for l in (Path.home()/"chroma_tier2_hosts.txt").open() if l.strip()] if (Path.home()/"chroma_tier2_hosts.txt").exists() else []
    if not targets:
        targets = [l.strip() for l in open('/tmp/chroma_tier2_hosts.txt') if l.strip()]
    print(f"[verify_chroma_campaign] targets={len(targets)} conc={CONCURRENCY} t/o={TIMEOUT}s", file=sys.stderr)

    sem = asyncio.Semaphore(CONCURRENCY)
    async def bounded(t):
        async with sem:
            try:
                return await probe_host(t)
            except Exception as e:
                return {'target': t, 'state': 'PROBE-ERR', 'err': repr(e)}

    rows = []
    t0 = time.time()
    tasks = [asyncio.create_task(bounded(t)) for t in targets]
    done = 0
    for coro in asyncio.as_completed(tasks):
        r = await coro
        rows.append(r)
        done += 1
        if done % 25 == 0 or done == len(tasks):
            elapsed = time.time() - t0
            print(f"  [{done}/{len(tasks)}] {elapsed:5.1f}s", file=sys.stderr)

    # rollup
    by_state = Counter(r['state'] for r in rows)
    print("\nSTATE ROLLUP:", file=sys.stderr)
    for s, n in by_state.most_common():
        print(f"  {n:>4}  {s}", file=sys.stderr)

    all_pairs = []
    all_cve = []
    for r in rows:
        all_pairs.extend(r.get('canary_pairs', []))
        all_cve.extend(r.get('cve_tokens_visible', []))
    print(f"\ncanary timestamp pairs total: {len(all_pairs)} (unique: {len(set(all_pairs))})", file=sys.stderr)
    print(f"cve token sightings: {len(all_cve)} (unique tokens: {len(set(all_cve))})", file=sys.stderr)

    rollup = {
        'sweep_t': int(time.time()),
        'targets': len(targets),
        'state_rollup': dict(by_state),
        'canary_pair_count': len(all_pairs),
        'canary_pair_unique': len(set(all_pairs)),
        'cve_tokens_unique': sorted(set(all_cve)),
        'rows': rows,
    }
    (OUT/"rollup.json").write_text(json.dumps(rollup, indent=2))
    print(f"\n-> {OUT}/rollup.json", file=sys.stderr)
    print(f"-> {OUT}/hosts/*.json ({len(rows)} files)", file=sys.stderr)


if __name__ == '__main__':
    asyncio.run(main())
