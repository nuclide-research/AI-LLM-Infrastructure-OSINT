# Insight #65: TLS-Cert-Anchored Discovery Selects for Auth-Enforced Deployments

**Date:** 2026-05-27  
**Survey:** Argo Workflows (Category 29 — K8s Workflow Orchestration)  
**Anchoring data:** 67 confirmed instances, 0 auth-bypass in tested sample

## The Finding

Passive Shodan discovery anchored on a TLS certificate organizational field (e.g. `ssl:"ArgoProj"`) has inherent selection bias: it finds managed, production-grade deployments that are more likely to have authentication enforced.

**Argo Workflows case:**
- The Argo server generates a self-signed cert with Organization=ArgoProj when running with `--secure` (HTTPS mode)
- Production K8s deployments serve this through a LoadBalancer on port 443
- Operators who set up TLS + LoadBalancer + K8s ingress also tend to configure `--auth-mode=client`
- Result: every instance in the `ssl:"ArgoProj"` population returned HTTP 401 on all API endpoints

The **vulnerable population** (quick-start, plain HTTP, port 2746, `--auth-mode=server`) produces no TLS cert artifact and is therefore invisible to cert-based Shodan dorks.

## Discovery Gap

Port 2746 (Argo's native port) is Shodan-dark:
- Shodan does not index port 2746 HTML body content
- Shodan does not index port 2746 HTTP response headers
- The SPA JavaScript bundle (content-hashed filenames) is not indexed
- No alternative Shodan signal exists for plain-HTTP Argo instances

Verified: 15 distinct dorks attempted, 14 returned 0 results. Only `ssl:"ArgoProj"` worked, and it finds exclusively the TLS-enabled, auth-enforced population.

## Generalization

This selection bias applies to **any service where cert dorks are the primary discovery signal**:

| Dork Anchor | What It Finds | What It Misses |
|-------------|---------------|----------------|
| `ssl:"<vendor>"` self-signed cert | Production TLS deployments, likely auth-configured | Quick-start plain HTTP on native port |
| `http.title:"<service>"` | Services with HTTP banner indexing | HTTPS-only + non-standard ports |
| `ssl.cert.subject.cn:"<domain>"` | Named, formally-deployed instances | Unnamed, ephemeral, or internal deployments |

**Rule:** Certificate-based dorks find the MANAGED tier. Direct port scanning finds the EXPOSED tier. For auth-exposure research, direct scanning is mandatory; passive dork surveillance systematically undercounts the vulnerable population.

## Implication for Auth-on-Default Thesis

This finding does not refute the auth-on-default thesis — it sharpens it:

- **Managed deployments (cert dork population):** Auth-on-default holds strongly (0/67 unauth in sample)
- **Quick-start deployments (direct-scan population):** Auth-on-default historically weak (E.V.A. 2022: ~3,000 unauth)

The thesis stratifies by deployment class. Cert-dork surveillance measures the managed class only. Direct scanning measures both.

## Recommended Correction

For Argo Workflows (and similar services with native-port plain-HTTP default):
1. Use cert dork for census of managed deployments (baseline auth-enforced measurement)
2. Supplement with direct masscan of port 2746 against cloud IP ranges for unauth exposure
3. Report both populations separately — they represent different risk classes

## aimap Impact

- **v1.9.35:** Added ports 443, 80, 8080, 8443 to Argo Workflows `DefaultPorts` (81% found on 443)
- **v1.9.36:** Added `Argo Workflows (auth-enforced)` identity fingerprint at severity=info

The `DefaultPorts` fix also revealed that fingerprints must enumerate empirically-observed ports, not just vendor-documented defaults — the deployment pattern at scale can differ significantly from the documented default.
