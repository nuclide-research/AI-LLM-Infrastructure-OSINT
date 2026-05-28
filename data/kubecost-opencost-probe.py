#!/usr/bin/env python3
"""
kubecost-opencost-probe.py — K8s FinOps cost-allocation verification probe.

WHY THIS EXISTS: aimap has no fingerprint for Kubecost/OpenCost (Insight #20 gap).
This is the manual->productize step of the manual->productize->re-run loop: a
single-purpose, read-only verifier for the cost-model API. Output is NDJSON that
feeds `visorlog ingest`, not a terminal print (STOP-and-check rule).

METHODOLOGY ANCHORS:
  #52  HTTP 200 at an API path is not that API. OpenCost :9090/allocation returns
       the UI SPA shell; the real JSON API is on :9003. We require the service's
       own emitted JSON shape ({"code":200,"data":[...]} with properties.cluster),
       never a bare 200.
  #66  DefaultPorts are survey-driven. Kubecost frontend proxies /model/* on
       80/443/9090; OpenCost API is :9003, UI :9090. K8s LB/ingress also exposes
       on 443/80. We probe the full resolved port set, not the doc default.
  #37  Asymmetric auth: the UI may be login-gated while the cost-model API is open.
       We probe BOTH surfaces and tier on which is open.
  #41/#38  Restraint: read NAMES not values. We pull aggregate=namespace (cluster +
       namespace names + aggregate cost = the finding evidence) and STOP. We never
       enumerate per-pod records. For /model/helmValues (Kubecost credential-leak
       class, macchaffee 2021) we record presence (status + size) ONLY — we do not
       store or print the secret body. That is Step 5 (attribution); Step 6 (reading
       a secret value) needs explicit re-authorization.
  #62  After a host confirms, the adjacent co-located Prometheus/kubelet is usually
       the bigger surface. We flag shadow candidates; the sweep is a separate pass.

Usage:
  python3 kubecost-opencost-probe.py targets.txt > findings.ndjson
  (targets.txt: one IP or IP:port per line; '#' comments ok)
"""
import sys, json, socket, concurrent.futures as cf
import urllib.request, urllib.error

TIMEOUT = 8
THREADS = 8
UA = "NuClide-Research/kubecost-opencost-probe (read-only verification; contact@nuclide-research.com)"

# Port sets per #66 — survey-driven, widest-first.
KUBECOST_PORTS = [80, 443, 9090]      # nginx frontend proxies /model/*
OPENCOST_API_PORTS = [9003, 9090]     # 9003 = API (definitive), 9090 = UI (proxy/SPA)


def http_get(url, want_json=False):
    """Read-only GET. Returns (status, size, text-or-None). Caps body read."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(200_000)  # cap; we only need shape + aggregate names
            txt = body.decode("utf-8", "replace")
            return r.status, len(body), txt
    except urllib.error.HTTPError as e:
        return e.code, 0, None
    except Exception:
        return None, 0, None


def is_costmodel_json(txt):
    """#52: require the service's own emitted JSON shape, not a 200."""
    if not txt or not txt.lstrip().startswith("{"):
        return None
    try:
        obj = json.loads(txt)
    except Exception:
        return None
    if obj.get("code") == 200 and "data" in obj:
        return obj
    return None


def namespace_names(alloc_obj, cap=60):
    """Extract aggregate namespace names + a cost rollup. NAMES not records (#41)."""
    names, total = [], 0.0
    data = alloc_obj.get("data") or []
    for window in data:
        if isinstance(window, dict):
            for key, val in window.items():
                names.append(key)
                if isinstance(val, dict):
                    try:
                        total += float(val.get("totalCost", 0) or 0)
                    except Exception:
                        pass
    return names[:cap], round(total, 4), len(names)


def probe_kubecost(ip):
    for port in KUBECOST_PORTS:
        scheme = "https" if port == 443 else "http"
        base = f"{scheme}://{ip}:{port}"
        st, sz, txt = http_get(f"{base}/model/clusterInfo")
        ci = is_costmodel_json(txt)
        if ci is None:
            continue
        info = ci.get("data", {}) if isinstance(ci.get("data"), dict) else {}
        rec = {
            "platform": "kubecost", "ip": ip, "port": port, "confirmed": True,
            "auth_state": "OPEN_API",
            "cluster_id": info.get("id") or info.get("name"),
            "provider": info.get("provider"), "provisioner": info.get("provisioner"),
            "region": info.get("region"), "profile": info.get("clusterProfile"),
            "version": info.get("version"), "account": info.get("account") or None,
        }
        # allocation: namespace NAMES + aggregate cost (the finding evidence)
        st2, sz2, txt2 = http_get(
            f"{base}/model/allocation?window=1d&aggregate=namespace&accumulate=true")
        alloc = is_costmodel_json(txt2)
        if alloc:
            ns, total, n = namespace_names(alloc)
            rec.update({"namespaces": ns, "namespace_count": n, "agg_cost_1d": total})
        # helmValues credential-leak class (#38): PRESENCE ONLY, never store body
        st3, sz3, _ = http_get(f"{base}/model/helmValues")
        rec["helmvalues_exposed"] = bool(st3 == 200 and sz3 > 200)
        rec["helmvalues_bytes"] = sz3 if st3 == 200 else 0
        # #37 asymmetric: is the UI root gated while the API answered?
        stui, _, txtui = http_get(f"{base}/")
        rec["ui_status"] = stui
        rec["asymmetric"] = bool(stui in (301, 302, 401, 403))
        return rec
    return None


def probe_opencost(ip):
    # API first (#52: :9003 is definitive; :9090 is the SPA shell)
    for port in OPENCOST_API_PORTS:
        base = f"http://{ip}:{port}"
        for path in ("/allocation?window=1d&aggregate=namespace",
                     "/allocation/compute?window=1d&aggregate=namespace"):
            st, sz, txt = http_get(f"{base}{path}")
            alloc = is_costmodel_json(txt)
            if alloc:
                ns, total, n = namespace_names(alloc)
                # cluster id from properties or /metrics
                cluster = None
                data = alloc.get("data") or []
                if data and isinstance(data[0], dict):
                    first = next(iter(data[0].values()), {})
                    cluster = (first.get("properties") or {}).get("cluster")
                rec = {
                    "platform": "opencost", "ip": ip, "port": port, "confirmed": True,
                    "auth_state": "OPEN_API", "api_path": path.split("?")[0],
                    "cluster_id": cluster, "namespaces": ns,
                    "namespace_count": n, "agg_cost_1d": total,
                }
                # /metrics carries kubecost_cluster_info (provider/region/version)
                stm, _, txtm = http_get(f"{base}/metrics")
                if txtm:
                    for line in txtm.splitlines():
                        if line.startswith("kubecost_cluster_info{"):
                            rec["cluster_info_metric"] = line[:400]
                            break
                return rec
    # API not reachable: is the UI shell exposed? (lower severity, no data)
    st, sz, txt = http_get(f"http://{ip}:9090/")
    if txt and "opencost-ui" in txt:
        return {"platform": "opencost", "ip": ip, "port": 9090, "confirmed": False,
                "auth_state": "UI_ONLY_NO_API",
                "note": "OpenCost UI SPA exposed; :9003 API not reachable -> no data exposure confirmed (#52)"}
    return None


def probe(target):
    target = target.strip()
    if not target or target.startswith("#"):
        return None
    ip = target.split(":")[0]
    # Try Kubecost first (its /model/clusterInfo is unambiguous), then OpenCost.
    return probe_kubecost(ip) or probe_opencost(ip)


def main():
    if len(sys.argv) < 2:
        print("usage: kubecost-opencost-probe.py targets.txt", file=sys.stderr)
        sys.exit(2)
    targets = open(sys.argv[1]).read().splitlines()
    with cf.ThreadPoolExecutor(max_workers=THREADS) as ex:
        for rec in ex.map(probe, targets):
            if rec:
                print(json.dumps(rec))


if __name__ == "__main__":
    main()
