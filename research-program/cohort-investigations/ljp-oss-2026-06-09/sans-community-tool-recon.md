# SANS + Community Tool Recon for LJP-OSS Cohort

Goal: accelerate per-IP verification + sensitive-substrate detection across 12,577 hosts running Sub2API/Grok2API/cousins. Stars/last-push captured 2026-06-09.

## Tools we should adopt NOW

### 1. SpiderFoot — `smicallef/spiderfoot` (Python, 18.1k stars, 2026-04)
200+ module OSINT engine (Shodan, BinaryEdge, AbuseIPDB, crt.sh, passive DNS, JARM). Seed-to-pivot fan-out matches our per-IP deep-dive need exactly.
```bash
git clone https://github.com/smicallef/spiderfoot.git ~/Tools/spiderfoot && \
  cd ~/Tools/spiderfoot && pip install -r requirements.txt
python3 sf.py -s 1.2.3.4 -m sfp_shodan,sfp_abuseipdb,sfp_crtsh,sfp_dnsdb -o csv > out.csv
```
Output: CSV per IP with sibling hostnames, abuse history, ASN context. Feed VisorLog.

### 2. AbuseIPDB CLI — `kristuff/abuseipdb-cli` (PHP, 53 stars, 2023-05)
Reputation pre-screen. Free tier 1,000/day; bulk 491 cohort in one day.
```bash
composer global require kristuff/abuseipdb-cli
xargs -a ips.txt -P 4 -I{} abuseipdb check -i {} -d 90 -o json >> rep.jsonl
```
Output: 0-100 abuse score per IP. Non-zero on supposedly-clean cohort = prior abuse reports, escalates severity before publish.

### 3. SANS DShield — `DShield-ISC/dshield` (Python, 521 stars, 2026-06)
The repo is the sensor; we use the **DShield API endpoint** for global attack context. No auth, free.
```bash
for ip in $(cat ips.txt); do
  curl -s "https://isc.sans.edu/api/ip/${ip}?json" \
    | jq -c "{ip:\"$ip\", count:.ip.count, attacks:.ip.attacks, asname:.ip.asname}"
done > dshield.jsonl
```
Output: per-IP attack counts seen by DShield sensor net. High count = compromised, not just exposed.

### 4. favihunter — `eremit4/favihunter` (Python, 250 stars, 2025-10)
mmh3 favicon fan-out across Shodan + FOFA + ZoomEye + Censys + Quake + Hunter. Catches Chinese-engine-only LJP-OSS hosts Shodan misses (the bulk of Sub2API operators).
```bash
git clone https://github.com/eremit4/favihunter.git ~/Tools/favihunter
cd ~/Tools/favihunter && pip install -r requirements.txt
python3 favihunter.py -u https://target.example/favicon.ico
```
Output: hash + per-engine IP lists. Expect significant FOFA/Quake delta over Shodan.

### 5. ZoomEye CLI — `knownsec/ZoomEye-python` (Python, 562 stars, 2026-01)
Chinese search engine, stronger CN/HK/SG visibility than Shodan. Most Sub2API ops are Chinese-language - ZoomEye sees them first.
```bash
pip install zoomeye
zoomeye init -apikey <KEY>
zoomeye search 'app:"Sub2API" +country:"CN"' -num 10000 -filter ip,port,country,org
```
Output: population delta vs our Shodan harvest (Shodan undersamples APAC).

### 6. ct-moniteur — `CERT-Polska/ct-moniteur` (Python, 26 stars, 2025-12)
Modern async CT monitor with **tiled-log support** (Google's new format). Most CT tools only handle classic logs and miss new issuances. CERT.PL maintained.
```bash
pip install ct-moniteur
ct-moniteur monitor --log-url https://ct.googleapis.com/logs/us1/argon2025h2/ \
  --keywords sub2api,grok2api,oneapi,one-api,newapi --output hits.jsonl
```
Output: live cert-issuance stream filtered to our keywords. Catches new LJP-OSS deployments within hours.

### 7. crtsh — `knqyf263/crtsh` (Go, 2025-12)
Fast Go binary with proper crt.sh pagination + rate-limit backoff. Better than `curl | jq`.
```bash
go install github.com/knqyf263/crtsh@latest
crtsh sub2api.com | jq -r .common_name | sort -u
```
Output: historical hostname list incl. expired/rotated infra. Often surfaces operator's other projects.

### 8. SANS-ISC IP API (no repo, endpoint)
Free per-IP ASN/country/port-scan history seen by DShield.
```bash
curl -s "https://isc.sans.edu/api/ipinfo/1.2.3.4?json" | jq .
```
Output: free pre-screen layer in our verification pipeline.

### 9. SANS DeepBlueCLI — `sans-blue-team/DeepBlueCLI` (PowerShell, 2.4k stars, 2023-10)
**Doctrine reference, not direct CLI.** Mine the heuristic catalog (rare-process spawn, credential-dumping signatures); port to HTTP-layer detection of LLM-jacked endpoints (rare model names, key-rotation events).

### 10. ioc-pivot — `0xPersist/ioc-pivot` (Python, 0 stars, 2026-03)
Tiny, unproven, but exact-fit: IP in -> VirusTotal+AbuseIPDB+Shodan out. 30-min eval; if it works it replaces three curl scripts.
```bash
git clone https://github.com/0xPersist/ioc-pivot && cd ioc-pivot
pip install -r requirements.txt && python3 ioc_pivot.py -i 1.2.3.4
```

## Tools to watch / consider

- **LeakLooker** (`woj-ciech`, 1.4k stars, 2020) — BinaryEdge open-DB hunter. Stale code, but the query patterns are gold for exposed-Redis/Mongo cousin cohorts.
- **certleak** (`d-Rickyy-b`, 12 stars, 2025-05) — async CT framework. Backup if ct-moniteur perf disappoints.
- **finder** (`Phennova`, 0 stars, 2026-05) — TUI BFS pivoter. Brand new; recursive-BFS pattern matches our 9-layer verification.
- **Cybersearch** (`RobertWang4`, 4 stars, 2025-08) — unified syntax across FOFA/ZoomEye/Shodan/Hunter/Quake/DayDayMap. Single pane > per-engine CLI churn.
- **ja4db-search** (`sans-blue-team`, 3 stars, 2026-03) — JA4 lookup. Future: fingerprint TLS client used by Sub2API installs for operator attribution.
- **geo-recon** (`radioactivetobi`, 394 stars, 2022-12) — older IP recon CLI. Maintained-enough; light eval.

## Dead ends / abandoned

- **certstream-server-python** (`CaliDog`, archived 2018) — WebSocket still up, use ct-moniteur instead.
- **sublert** (`yassineaboukir`, 1k stars, 2021) — depends on stale certstream. Concept good, code dead.
- **SANS for-509 / find-evil-\*** — every 2026 hackathon repo is a SIFT forensic agent, off-domain for our work.
- **anubis** (`louisbarrett`, 2021) — stale IP-rep Lambda.
- **pybinaryedge** (`Te-k`, 2023) — works, but BinaryEdge free tier is severely throttled now; not worth integrating without a paid key.
- **The 15+ "favicon hash for shodan" repos** — all 1-page snippets; favihunter (multi-engine) supersedes, or use the 4-line mmh3 idiom inline.
- **fofa_viewer** (`wgpsec`, 1.8k stars) — JavaFX desktop, paid FOFA required. Reference for query syntax only.
- **"openai/anthropic key abuse" searches** — zero usable tooling exists. **Confirms NuClide is in unmapped territory; the LJP-OSS detection gap is real.**

## Immediate next steps

1. SpiderFoot against 491 verified IPs (overnight batch).
2. Burn ZoomEye free credits on `app:"Sub2API"` + cousins, delta vs 12,577.
3. Stand up ct-moniteur with keyword set (sub2api, grok2api, one-api, oneapi, newapi, voapi) for continuous new-deployment alerts.
4. Pipe AbuseIPDB + DShield API into VisorLog per-IP record to boost sensitive-substrate scoring.
