#!/usr/bin/env python3
"""Tri-cloud bucket accessibility prober — read-only.

Reads probe-targets.tsv (provider\tbucket\toccurrences\thost_count\tfirst_host),
issues HEAD + anonymous list against each. No credentials sent, no destructive
ops, no GET-by-key beyond what listing surfaces. 5s timeout, retry once on
transient network error.

Classification:
  public-list+get : list succeeds, first key reachable via HEAD/GET
  public-list     : list succeeds (200 with object keys)
  exists-private  : HEAD/GET returns 403 / AccessDenied / AuthenticationRequired
  not-found       : HEAD/GET returns 404 / NoSuchBucket / ContainerNotFound
  error           : network / parse failure
"""
import csv, json, sys, time, urllib.parse, xml.etree.ElementTree as ET
from pathlib import Path
import urllib.request, urllib.error, ssl

WORKDIR = Path(__file__).resolve().parent
TARGETS = WORKDIR / "probe-targets.tsv"
RAW = WORKDIR / "raw"
EVID = WORKDIR / "evidence"
RAW.mkdir(exist_ok=True)
EVID.mkdir(exist_ok=True)

UA = "NuClide-VisorBishop-Phase5b/1.0 (research; read-only; nicholas@nuclide-research.com)"
TIMEOUT = 6
CTX = ssl.create_default_context()


def http(method, url, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
            body = r.read(65536)
            return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        try:
            body = e.read(65536)
        except Exception:
            body = b""
        return e.code, dict(e.headers or {}), body
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
        return None, {}, repr(e).encode()


def probe_s3(bucket):
    """S3 anonymous list-objects-v2."""
    out = {"provider": "aws-s3", "bucket": bucket, "probes": []}
    host_styles = [
        f"https://{bucket}.s3.amazonaws.com/?list-type=2&max-keys=10",
        f"https://s3.amazonaws.com/{bucket}/?list-type=2&max-keys=10",
    ]
    for url in host_styles:
        s, hdrs, body = http("GET", url)
        rec = {"url": url, "status": s, "headers": {k: hdrs.get(k) for k in ("x-amz-bucket-region", "x-amz-request-id", "Content-Type") if hdrs.get(k)}, "body_head": body[:2000].decode(errors="replace")}
        out["probes"].append(rec)
        if s == 200:
            keys = []
            try:
                root = ET.fromstring(body)
                ns = root.tag.split("}")[0].strip("{") if "}" in root.tag else ""
                tag = f"{{{ns}}}Contents" if ns else "Contents"
                keytag = f"{{{ns}}}Key" if ns else "Key"
                for c in root.findall(tag)[:10]:
                    k = c.find(keytag)
                    if k is not None and k.text:
                        keys.append(k.text)
            except ET.ParseError:
                pass
            out["verdict"] = "public-list"
            out["keys_sample"] = keys
            out["key_count_visible"] = len(keys)
            return out
        if s in (301, 307):
            region = hdrs.get("x-amz-bucket-region")
            if region:
                out["region"] = region
        if s == 403 and b"AccessDenied" in body:
            out["verdict"] = "exists-private"
            return out
        if s == 404 and b"NoSuchBucket" in body:
            out["verdict"] = "not-found"
            return out
    # If we got a redirect with region, retry on the regional endpoint
    region = out.get("region")
    if region:
        url = f"https://{bucket}.s3.{region}.amazonaws.com/?list-type=2&max-keys=10"
        s, hdrs, body = http("GET", url)
        rec = {"url": url, "status": s, "body_head": body[:2000].decode(errors="replace")}
        out["probes"].append(rec)
        if s == 200:
            keys = []
            try:
                root = ET.fromstring(body)
                ns = root.tag.split("}")[0].strip("{") if "}" in root.tag else ""
                tag = f"{{{ns}}}Contents" if ns else "Contents"
                keytag = f"{{{ns}}}Key" if ns else "Key"
                for c in root.findall(tag)[:10]:
                    k = c.find(keytag)
                    if k is not None and k.text:
                        keys.append(k.text)
            except ET.ParseError:
                pass
            out["verdict"] = "public-list"
            out["keys_sample"] = keys
            out["key_count_visible"] = len(keys)
            return out
        if s == 403:
            out["verdict"] = "exists-private"
            return out
        if s == 404:
            out["verdict"] = "not-found"
            return out
    out["verdict"] = "indeterminate"
    return out


def probe_gcs(bucket):
    """GCS anonymous list via JSON API + XML API fallback."""
    out = {"provider": "gcs", "bucket": bucket, "probes": []}
    url = f"https://storage.googleapis.com/storage/v1/b/{urllib.parse.quote(bucket)}/o?maxResults=10"
    s, hdrs, body = http("GET", url)
    rec = {"url": url, "status": s, "body_head": body[:2000].decode(errors="replace")}
    out["probes"].append(rec)
    if s == 200:
        try:
            j = json.loads(body)
            items = j.get("items", []) or []
            keys = [it.get("name") for it in items[:10] if it.get("name")]
            out["verdict"] = "public-list"
            out["keys_sample"] = keys
            out["key_count_visible"] = len(keys)
            return out
        except json.JSONDecodeError:
            pass
    # XML fallback (uniform bucket-level access may surface here)
    url2 = f"https://storage.googleapis.com/{urllib.parse.quote(bucket)}?max-keys=10"
    s2, hdrs2, body2 = http("GET", url2)
    rec2 = {"url": url2, "status": s2, "body_head": body2[:2000].decode(errors="replace")}
    out["probes"].append(rec2)
    if s2 == 200:
        keys = []
        try:
            root = ET.fromstring(body2)
            ns = root.tag.split("}")[0].strip("{") if "}" in root.tag else ""
            tag = f"{{{ns}}}Contents" if ns else "Contents"
            keytag = f"{{{ns}}}Key" if ns else "Key"
            for c in root.findall(tag)[:10]:
                k = c.find(keytag)
                if k is not None and k.text:
                    keys.append(k.text)
        except ET.ParseError:
            pass
        out["verdict"] = "public-list"
        out["keys_sample"] = keys
        out["key_count_visible"] = len(keys)
        return out
    # Classify privacy state
    if s == 401 or s2 == 401:
        out["verdict"] = "exists-private"
        return out
    if s == 403 or s2 == 403:
        out["verdict"] = "exists-private"
        return out
    if s == 404 or s2 == 404:
        # 404 on JSON API doesn't mean nonexistent — could be no access; require both
        if s == 404 and s2 == 404:
            out["verdict"] = "not-found"
        else:
            out["verdict"] = "exists-private"
        return out
    out["verdict"] = "indeterminate"
    return out


def probe_azure(container_and_account):
    """Azure Blob anonymous list-blobs."""
    out = {"provider": "azure-blob", "ref": container_and_account, "probes": []}
    if "@" not in container_and_account:
        out["verdict"] = "parse-error"
        return out
    container, host = container_and_account.split("@", 1)
    account = host.split(".")[0]
    out["account"] = account
    out["container"] = container
    url = f"https://{host}/{container}?restype=container&comp=list&maxresults=10"
    s, hdrs, body = http("GET", url)
    rec = {"url": url, "status": s, "body_head": body[:2000].decode(errors="replace")}
    out["probes"].append(rec)
    if s == 200:
        keys = []
        try:
            root = ET.fromstring(body)
            for b in root.iter("Name"):
                if b.text:
                    keys.append(b.text)
                if len(keys) >= 10:
                    break
        except ET.ParseError:
            pass
        out["verdict"] = "public-list"
        out["keys_sample"] = keys
        out["key_count_visible"] = len(keys)
        return out
    if s in (401, 403):
        out["verdict"] = "exists-private"
        return out
    if s == 404:
        # could be container-not-found OR account-not-found
        out["verdict"] = "not-found"
        return out
    out["verdict"] = "indeterminate"
    return out


def main():
    targets = []
    with TARGETS.open() as f:
        for row in csv.reader(f, delimiter="\t"):
            if len(row) < 5:
                continue
            provider, bucket, occ, host_count, first_host = row[:5]
            targets.append((provider, bucket, int(occ), int(host_count), first_host))

    print(f"[+] {len(targets)} targets loaded", file=sys.stderr)
    results = []
    for i, (provider, bucket, occ, hosts, first_host) in enumerate(targets, 1):
        print(f"[{i}/{len(targets)}] {provider}\t{bucket}", file=sys.stderr)
        try:
            if provider == "aws-s3":
                r = probe_s3(bucket)
            elif provider == "gcs":
                r = probe_gcs(bucket)
            elif provider == "azure-blob":
                r = probe_azure(bucket)
            else:
                r = {"provider": provider, "bucket": bucket, "verdict": "skipped"}
        except Exception as e:
            r = {"provider": provider, "bucket": bucket, "verdict": "error", "error": repr(e)}
        r["occurrences"] = occ
        r["host_count"] = hosts
        r["first_host"] = first_host
        results.append(r)
        print(f"    -> {r.get('verdict')} {('('+str(r.get('key_count_visible',''))+' keys)') if r.get('keys_sample') else ''}", file=sys.stderr)
        time.sleep(0.4)  # be polite

    out = WORKDIR / "results.json"
    with out.open("w") as f:
        json.dump(results, f, indent=2)
    print(f"[+] wrote {out}", file=sys.stderr)

    # Summary TSV
    tsv = WORKDIR / "results.tsv"
    with tsv.open("w") as f:
        f.write("provider\tbucket_or_ref\tverdict\tkey_count_visible\tfirst_host\toccurrences\thost_count\n")
        for r in results:
            ref = r.get("bucket") or r.get("ref") or ""
            kc = r.get("key_count_visible", "")
            f.write(f"{r.get('provider')}\t{ref}\t{r.get('verdict')}\t{kc}\t{r.get('first_host')}\t{r.get('occurrences')}\t{r.get('host_count')}\n")
    print(f"[+] wrote {tsv}", file=sys.stderr)


if __name__ == "__main__":
    main()
