#!/usr/bin/env python3
"""
Langfuse auth-posture probe.

Reads langfuse-urls.tsv (url\thostname). For each row:
  1. Probe by IP (direct)
  2. If hostname differs from IP, probe by hostname with --resolve trick

Two endpoints tested:
  /api/public/health  — should return 200 always (no auth)
  /api/public/projects — auth-fronted in default Langfuse setup
     - 401 = auth enforced
     - 200 with {"data":[]} = unauth (no projects)
     - 200 with {"data":[...]} = unauth WITH data leaking
     - 403 = auth enforced (alternate)
     - 404 = wrong API shape / instance not Langfuse
"""
import sys, json, urllib.request, urllib.parse, ssl, socket, time
from concurrent.futures import ThreadPoolExecutor, as_completed

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def probe(url, hostname, host_resolves_to_ip):
    """Return dict with health_status, projects_status, projects_body_preview, error."""
    target_ip = url.split('://')[1].split(':')[0]
    target_port = url.split(':')[-1] if ':' in url.split('://')[1] else '443'
    target_proto = url.split('://')[0]

    # Strategy 1: direct by IP
    direct_result = _probe_one(url, ip=target_ip, host_header=None)
    # Strategy 2: by hostname (if hostname differs and looks like a real domain)
    hostname_result = None
    if hostname and hostname != target_ip and '.' in hostname and not hostname.endswith('amazonaws.com') and not hostname.endswith('googleusercontent.com'):
        host_url = f'{target_proto}://{hostname}:{target_port}'
        hostname_result = _probe_one(host_url, ip=target_ip, host_header=hostname)

    return {
        'url': url,
        'hostname': hostname,
        'direct': direct_result,
        'hostname_probe': hostname_result,
    }

def _probe_one(url, ip=None, host_header=None):
    """Probe a single URL. Use socket-level override if host_header provided."""
    try:
        # Manual socket connection to bypass DNS
        host = host_header or url.split('://')[1].split(':')[0]
        port = int(url.split(':')[-1])
        proto = url.split('://')[0]

        # Use httplib for fine control
        import http.client
        if proto == 'https':
            sock = socket.create_connection((ip or host, port), timeout=5)
            ssock = ssl_ctx.wrap_socket(sock, server_hostname=host)
            conn = http.client.HTTPSConnection(host, port, timeout=5)
            conn.sock = ssock
        else:
            conn = http.client.HTTPConnection(ip or host, port, timeout=5)

        results = {}
        for path in ['/api/public/health', '/api/public/projects']:
            try:
                conn.request('GET', path, headers={'Host': host, 'User-Agent': 'nuclide-research/2026-05-10'})
                resp = conn.getresponse()
                body = resp.read(500).decode('utf-8', errors='replace')
                results[path] = {
                    'status': resp.status,
                    'size': len(body),
                    'preview': body[:200],
                }
            except Exception as e:
                results[path] = {'error': str(e)[:80]}
            # Reset for next req on https (since we can't easily reuse)
            if proto == 'https':
                try: conn.close()
                except: pass
                sock = socket.create_connection((ip or host, port), timeout=5)
                ssock = ssl_ctx.wrap_socket(sock, server_hostname=host)
                conn = http.client.HTTPSConnection(host, port, timeout=5)
                conn.sock = ssock
        conn.close()
        return results
    except Exception as e:
        return {'error': str(e)[:120]}


def main():
    rows = []
    for line in open('langfuse-urls.tsv'):
        line = line.rstrip('\n')
        if '\t' not in line:
            url = line
            host = ''
        else:
            url, host = line.split('\t', 1)
        rows.append((url, host))

    print(f'Probing {len(rows)} hosts with concurrency=20', file=sys.stderr)
    results = []
    with ThreadPoolExecutor(max_workers=20) as ex:
        futs = {ex.submit(probe, url, host, True): (url, host) for url, host in rows}
        for i, fut in enumerate(as_completed(futs)):
            try: results.append(fut.result())
            except Exception as e:
                url, host = futs[fut]
                results.append({'url': url, 'hostname': host, 'error': str(e)[:100]})
            if (i + 1) % 50 == 0:
                print(f'  {i+1}/{len(rows)}', file=sys.stderr)

    with open('langfuse-probe-results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'Saved {len(results)} results to langfuse-probe-results.json', file=sys.stderr)


if __name__ == '__main__':
    main()
