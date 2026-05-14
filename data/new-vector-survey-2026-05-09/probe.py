import asyncio, aiohttp, json, sys
from pathlib import Path

OUTDIR = Path("/home/cowboy/AI-LLM-Infrastructure-OSINT/data/new-vector-survey-2026-05-09")

# platform → (ip_file, probe_targets: [(port, path, confirm_str)])
PLATFORMS = {
    "meilisearch":   ("meilisearch.txt",   [(7700, "/health", "available"), (80, "/health", "available"), (443, "/health", "available")]),
    "questdb":       ("questdb.txt",        [(9000, "/", "QuestDB"), (80, "/", "QuestDB"), (443, "/", "QuestDB")]),
    "valkey":        ("valkey.txt",         [(6379, None, None)]),   # TCP only, skip HTTP
    "keydb":         ("keydb.txt",          [(6379, None, None)]),
    "openobserve":   ("openobserve.txt",    [(5080, "/", "OpenObserve"), (80, "/", "OpenObserve"), (443, "/", "OpenObserve")]),
    "vald":          ("vald.txt",           [(8080, "/", "vald"), (80, "/", "vald")]),
    "pocketbase":    ("pocketbase.txt",     [(8090, "/", "PocketBase"), (80, "/", "PocketBase"), (443, "/", "PocketBase")]),
    "singlestore":   ("singlestore.txt",    [(80, "/", "singlestore"), (443, "/", "singlestore"), (8080, "/", "singlestore")]),
    "pinecone":      ("pinecone.txt",       [(80, "/", "pinecone"), (443, "/", "pinecone")]),
    "upstash":       ("upstash.txt",        [(80, "/", "upstash"), (443, "/", "upstash")]),
    "chroma-tenant": ("chroma-tenant.txt",  [(8000, "/api/v2/tenants", "tenant"), (8100, "/api/v2/tenants", "tenant")]),
    "couchdb":       ("couchdb.txt",        [(5984, "/", "couchdb"), (5984, "/_all_dbs", "["), (80, "/", "couchdb")]),
    "nats-jetstream":("nats-jetstream.txt", [(8222, "/jsz", "streams"), (80, "/jsz", "streams"), (4222, None, None)]),
}

TIMEOUT = aiohttp.ClientTimeout(total=5)
SEM = asyncio.Semaphore(150)
CONFIRMED = {}

async def probe_http(session, ip, port, path, confirm):
    schemes = ["https", "http"] if port == 443 else ["http", "https"]
    for scheme in schemes:
        url = f"{scheme}://{ip}:{port}{path}"
        try:
            async with SEM:
                async with session.get(url, ssl=False, allow_redirects=True) as r:
                    text = await r.text(errors="replace")
                    if confirm.lower() in text.lower() or r.status < 400:
                        return True, url, r.status, text[:300]
        except:
            pass
    return False, None, None, None

async def probe_platform(platform, ip_file, probes):
    ips = (OUTDIR / ip_file).read_text().strip().splitlines()
    results = []
    connector = aiohttp.TCPConnector(ssl=False, limit=200)
    async with aiohttp.ClientSession(timeout=TIMEOUT, connector=connector) as session:
        tasks = []
        for ip in ips:
            for port, path, confirm in probes:
                if path is None:
                    continue  # skip TCP-only (redis/valkey handled separately)
                tasks.append((ip, port, path, confirm, probe_http(session, ip, port, path, confirm)))
        
        results_raw = await asyncio.gather(*[t[4] for t in tasks], return_exceptions=True)
        
        confirmed = []
        for (ip, port, path, confirm, _), res in zip(tasks, results_raw):
            if isinstance(res, tuple) and res[0]:
                confirmed.append({"ip": ip, "port": port, "url": res[1], "status": res[2], "snippet": res[3]})
        
        # dedupe by IP
        seen = set()
        deduped = []
        for c in confirmed:
            if c["ip"] not in seen:
                seen.add(c["ip"])
                deduped.append(c)
        return deduped

async def main():
    for platform, (ip_file, probes) in PLATFORMS.items():
        if not (OUTDIR / ip_file).exists():
            continue
        http_probes = [(p, path, conf) for p, path, conf in probes if path is not None]
        if not http_probes:
            print(f"[{platform}] skipping (TCP-only)")
            continue
        results = await probe_platform(platform, ip_file, http_probes)
        CONFIRMED[platform] = results
        out = OUTDIR / f"{platform}-confirmed.json"
        out.write_text(json.dumps(results, indent=2))
        print(f"[{platform}] {len(results)} confirmed live → {out.name}")

asyncio.run(main())
