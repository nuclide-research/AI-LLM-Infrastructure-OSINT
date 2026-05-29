#!/usr/bin/env python3
"""
finops_to_report.py - reference adapter: Kubecost/OpenCost probe NDJSON -> visor-report schema.

This is the per-survey adapter pattern. Each category writes one of these to map its
probe output into the generic visor-report JSON schema, then:
    python3 finops_to_report.py finops-probe-results.ndjson | visor-report.py render - -o report.html

Findings predicates here are FinOps-specific; copy this file as a starting point for a new category.
"""
import json, sys

SEC = {'cert-manager','external-secrets','external-secrets-system','vault','vault-central','vault2026',
 'falco','falco-system','falcon-system','falcon-kac','wiz','wazuh','kyverno','gatekeeper-system',
 'calico-system','tigera-operator','istio-system','amazon-guardduty'}
AI = {'aicore','aiexpert','litellm','vllm','vllm-inference','vllm-test','kubeflow','kubeflow-user',
 'mlflow','flowise','jupyter','jupyterhub','kagent','qdrant'}
ATTR = {
 '203.0.113.11': ('[operator redacted]','high','[product redacted]. kc5-aws cluster. helmValues returned a [credential redacted] (confirmed present, value not stored).'),
 '203.0.113.12': ('[operator redacted]','high','Second LoadBalancer IP fronting the same kc5-aws cluster (identical helmValues hash).'),
 '203.0.113.13': ('[operator redacted]','high','[product redacted]. g2r1 cluster, us-east-1. Same operator as kc5-aws.'),
 '203.0.113.14': ('Unattributed','none','$6,837/day spend leader (highest in corpus). GCP Mumbai. Candidate Scoutflo eliminated on scale + AWS-only stack.'),
 '203.0.113.15': ('Unnamed Alibaba ACK tenant','low','cn-shanghai. Provider Aliyun is not the operator.'),
}
HELM_CONFIRMED = {'203.0.113.11','203.0.113.12'}


def money(v): return ('$'+format(int(v),',')+'/d') if isinstance(v,(int,float)) and v > 0 else ''


def build(rows):
    hosts = {}
    for r in rows:
        ip = r['ip']; ns = r.get('namespaces') or []
        sec = [n for n in ns if n.lower() in SEC]; ai = [n for n in ns if n.lower() in AI]
        cost = r.get('agg_cost_1d'); helm = bool(r.get('helmvalues_exposed')); cred = ip in HELM_CONFIRMED
        a = ATTR.get(ip)
        flags = []
        if cred: flags.append({"cls": "cred", "title": "live credential confirmed"})
        elif helm: flags.append({"cls": "helm", "title": "helmValues endpoint open"})
        if a and a[1] == 'high': flags.append({"cls": "attr", "title": "attributed operator"})
        badges = [{"text": r.get('platform') or '?', "cls": ""}, {"text": r.get('auth_state') or '?', "cls": ""}]
        if cred: badges.append({"text": "live credential", "cls": "cred"})
        elif helm: badges.append({"text": "helmValues open", "cls": "helm"})
        cloud = ' / '.join(x for x in (r.get('provider'), r.get('provisioner'), r.get('region')) if x) or 'unknown'
        helmtxt = ('open + LIVE credential confirmed' if cred else
                   (f"endpoint open ({r.get('helmvalues_bytes')}B, content not exercised)" if helm else 'not exposed'))
        costtxt = money(cost) if (isinstance(cost,(int,float)) and cost > 0) else ('$0 (no scraped data)' if cost == 0 else '—')
        spec = [["Cloud", cloud, ""], ["Cluster id", r.get('cluster_id') or '—', "cy"],
                ["Profile", r.get('profile') or '—', ""], ["K8s version", r.get('version') or '—', ""],
                ["Port", str(r.get('port')), ""], ["Daily cost", costtxt, "cost"],
                ["Namespaces", str(r.get('namespace_count') or 0), ""], ["helmValues", helmtxt, ""],
                ["UI status", str(r.get('ui_status') or '—') + (" (asymmetric)" if r.get('asymmetric') else ""), ""]]
        tags = [{"name": n, "cls": ("sec" if n.lower() in SEC else ("ai" if n.lower() in AI else ""))} for n in ns]
        hosts[ip] = {"label": ip, "chip": {"note": money(cost), "flags": flags}, "badges": badges, "spec": spec,
                     "tag_groups": [{"label": "Leaked namespaces", "legend_html": "<span style='color:var(--hi)'>security</span> / <span style='color:var(--cyan)'>AI-LLM</span> / standard", "tags": tags}],
                     "attribution": ({"op": a[0], "conf": a[1], "note": a[2]} if a else None),
                     "_cost": cost if isinstance(cost,(int,float)) else 0, "_sec": sec, "_ai": ai,
                     "_platform": r.get('platform'), "_auth": r.get('auth_state'), "_nc": r.get('namespace_count') or 0,
                     "_helm": helm, "_account": r.get('account'), "_confirmed": r.get('confirmed'), "_provider": r.get('provider')}

    def ips(pred): return sorted([ip for ip, h in hosts.items() if pred(h)])
    findings = [
     {"id":"F1","tier":"HIGH","title":"Unauthenticated cost-model API = pre-attack reconnaissance primitive",
      "why":"A single unauthenticated GET to /model/allocation returns the full per-namespace cluster topology. Indexing the cluster is the cost sidecar's whole job, so it leaks more structural intelligence than the workloads it measures. Read-only, free, before any secret is touched.",
      "basis":"auth_state==OPEN_API AND namespace_count>0, gated on the service's own {\"code\":200,\"data\":[...]} shape (not a bare 200).",
      "hosts":ips(lambda h:h['_auth']=='OPEN_API' and h['_nc']>0)},
     {"id":"F2","tier":"MEDIUM","title":"Cost API enumerates the cluster security control plane as a free target list",
      "why":"The namespace list names the secret stores, admission controllers, and EDR/SIEM outright (vault, cert-manager, falco, wiz, wazuh, kyverno, gatekeeper, guardduty). An attacker learns what defenses to plan around before the first packet.",
      "basis":"namespaces[] contains one or more security-tooling namespace strings.",
      "hosts":ips(lambda h:len(h['_sec'])>0 and h['_nc']>0)},
     {"id":"F3","tier":"MEDIUM","title":"agg_cost_1d turns the population into a dollar-ranked target list",
      "why":"Daily spend is a proxy for production scale and blast radius. Free, unauthenticated prioritization by economic value. Aggregate visible spend ~$10,528/day; top single cluster $6,837/day.",
      "basis":"agg_cost_1d is real summed totalCost from the returned allocation windows (>0).",
      "hosts":ips(lambda h:h['_cost']>0)},
     {"id":"F4","tier":"MEDIUM","title":"Co-located AI/LLM namespaces tie the exposure to the AI-infra thesis",
      "why":"The same auth-on-default failure class as the broader AI-infra survey. The cost sidecar sits beside litellm/vllm/kubeflow/mlflow and indexes them too.",
      "basis":"namespaces[] contains AI/LLM tokens (aicore, litellm, vllm, kubeflow, mlflow, flowise, jupyter...).",
      "hosts":ips(lambda h:len(h['_ai'])>0)},
     {"id":"F5","tier":"MEDIUM","title":"OpenCost open API returning real topology + cost",
      "why":"CNCF OpenCost exposed on :9003 (definitive API) or :9090, returning namespace topology and per-namespace spend with no auth.",
      "basis":"platform==opencost AND confirmed AND namespace_count>0.",
      "hosts":ips(lambda h:h['_platform']=='opencost' and h['_confirmed'] and h['_nc']>0)},
     {"id":"F6","tier":"MEDIUM","title":"Vendor-undetermined cost-model API exposing data",
      "why":"Open cost-model API confirmed, vendor (Kubecost vs OpenCost) not disambiguated offline, returning topology + cost.",
      "basis":"platform==cost-model AND namespace_count>0.",
      "hosts":ips(lambda h:h['_platform']=='cost-model' and h['_nc']>0)},
     {"id":"F7","tier":"LOW","title":"helmValues endpoint exposed (one cluster confirmed to leak a live credential)",
      "why":"Corpus-wide this is presence-only: the endpoint answers 200 with a ~19KB body, content not fetched. One authorized sample on kc5-aws exercised it and returned a [credential redacted]. The macchaffee-2021 credential-leak class is live; magnitude across the other endpoints not measured.",
      "basis":"helmvalues_exposed==true (HTTP 200 + body>200B). One cluster (kc5-aws) sampled and confirmed.",
      "hosts":ips(lambda h:h['_helm'])},
     {"id":"F8","tier":"LOW","title":"clusterInfo metadata disclosure",
      "why":"GET /model/clusterInfo returns cloud provider, provisioner (EKS/GKE/AKS), region, version, profile, and cluster_id without auth.",
      "basis":"Kubecost probe path always fetches clusterInfo; returned for all Kubecost/cost-model hosts.",
      "hosts":ips(lambda h:h['_platform'] in ('kubecost','cost-model') and h['_provider'])},
     {"id":"F9","tier":"LOW","title":"Azure cloud-account identifier (UUID) leaked",
      "why":"A UUID-shaped Azure account/subscription identifier in clusterInfo. An identifier, not a credential. All are Azure tenants.",
      "basis":"account field non-null (verified primary-source from clusterInfo).",
      "hosts":ips(lambda h:h['_account'])},
     {"id":"F10","tier":"INFO","title":"OpenCost has no helmValues endpoint",
      "why":"Structural observation: the CNCF OpenCost build carries no /model/helmValues endpoint, so its exposure surface is topology+cost only.",
      "basis":"OpenCost rows show helmvalues_exposed=false / absent.",
      "hosts":ips(lambda h:h['_platform']=='opencost')},
    ]
    # strip internal _fields from hosts before emit
    for h in hosts.values():
        for k in [k for k in h if k.startswith('_')]: del h[k]
    spend = round(sum(r.get('agg_cost_1d') for r in rows if isinstance(r.get('agg_cost_1d'),(int,float)) and r.get('agg_cost_1d')>0))
    meta = {"org":"NuClide Research","kind":"// Field Survey","date":"2026-05-29",
            "title_html":"Unauthenticated FinOps cost APIs<br>hand attackers a <span class='em'>free cluster map</span>.",
            "subtitle_html":"Kubecost and OpenCost ship with auth off. Exposed on a public LoadBalancer, the cost-model API is not a billing page, it is a <b>reconnaissance oracle</b>: full namespace topology, the cluster's own security tooling named outright, and a dollar-ranked target list. Click a finding to drill in. Click a host to go deeper.",
            "stats":[{"value":len(rows),"label":"instances","style":""},
                     {"value":sum(1 for r in rows if r.get('auth_state')=='OPEN_API'),"label":"open API","style":"cyan"},
                     {"value":"$"+format(spend,','),"label":"$/day visible","style":"hot"},
                     {"value":sum(1 for r in rows if r.get('helmvalues_exposed')),"label":"helmValues open","style":""},
                     {"value":1,"label":"live cred confirmed","style":"hot"},
                     {"value":sum(1 for r in rows if r.get('platform')=='cost-model'),"label":"vendor unknown","style":"cyan"}]}
    panels = [
     {"title":"The chain: anonymous to cluster credential","kind":"steps","items":[
       "Anonymous internet user finds a Kubecost host by title on Shodan.",
       "GET /model/allocation returns every namespace and its daily cost. No auth.",
       "The same open API names the security stack and ranks clusters by spend.",
       "GET /model/helmValues returns the install config, including a live Grafana admin password.",
       "That credential fronts Grafana (datasource secrets, dashboards, plugin RCE). Work stopped at proof."]},
     {"title":"Operator attribution","kind":"callout","callout":{"title":"[operator redacted]",
       "body_html":"The credential-bearing cluster (kc5-aws) and its sibling (g2r1) resolve to [product redacted] with HIGH-confidence passive evidence: leaked namespaces map verbatim to live operator endpoints (uz-redirector, msp4xiq, sdwan, nvo)."}},
     {"title":"Honest negative space","kind":"bullets","items":[
       "helmValues content confirmed live on ONE cluster (kc5-aws); the other 48 endpoints are presence-only.",
       "Snapshot is ~1 day old; hosts may have closed or rotated.",
       "No CRITICAL is claimed: no exec, data-write, or credential use was demonstrated.",
       "Spend ranking is noisy: a dev cluster ranks high; one 97-namespace cluster reports $0/day.",
       "Shadow-adjacency sweep (kubelet/Grafana/etcd on 66 IPs) came back zero open: the cost API is the sole external door."]},
    ]
    return {"meta": meta, "findings": findings, "hosts": hosts, "panels": panels}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else '-'
    rows = [json.loads(l) for l in (sys.stdin if src == '-' else open(src)) if l.strip()]
    json.dump(build(rows), sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
