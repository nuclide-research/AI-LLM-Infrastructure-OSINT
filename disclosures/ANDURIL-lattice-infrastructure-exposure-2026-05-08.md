---
to: disclosures@anduril.com
cc: abuse@nuclide-research.com
severity: HIGH
targets: "Telefonica ARO Grafana (lattice monitoring plane); andurildev.com Route53 zone (44+ subdomains leaking RFC-1918 IPs)"
status: DRAFT
date: 2026-05-08
gpg_key: https://www.anduril.com/.well-known/gpg-key.txt
---

**To:** disclosures@anduril.com
**Subject:** Anduril. Lattice Monitoring Plane Anonymous Grafana + Internal IP Leak in Public DNS

---

Nicholas Michael Kloster / NuClide Research
nicholas@nuclide-research.com
2026-05-08

This is a coordinated good-faith disclosure. Findings were identified through observation of publicly accessible HTTP endpoints (`/api/datasources` on a Grafana instance referenced in your Backstage CSP) and passive DNS resolution. No credentials were obtained or used; no systems were modified.

Your security.txt is properly configured at https://www.anduril.com/.well-known/security.txt; GPG key retrieved and ready for encrypted reply.

---

## Summary

| Severity | Finding | Owned by |
|---|---|---|
| HIGH | Telefonica-managed Grafana (`grafana-grafana-monitoring.apps.telefonica.centralus.aroapp.io`) returns 11 datasources unauthenticated, exposing internal cluster service URLs and external Lattice/Anduril infrastructure references | Telefonica (operator); Anduril impacted |
| HIGH | **Systemic split-horizon DNS leak across `andurildev.com` Route53 zone** — 44 of 157 sampled subdomains (28%) return RFC-1918 IPs in public DNS, exposing 9+ distinct internal subnets including the AI/ML data plane, SIE cluster topology, CI/CD environment (Crucible), Vault HA cluster, and the Maritime ASV's separate 172.16 addressing scheme | Anduril |
| MEDIUM | **Self-signed `CN=localhost, O=Anduril, L=Costa Mesa` certificate auto-renewing on 3 publicly-reachable Lattice deployments** — Microsoft UK / Phoenix, Oracle / Austin, Cloudflare / SF. Cert rotation regenerates the same broken template — deployment automation defect. | Anduril |
| LOW | `fleet-core-toc.fleet.internal` cert SAN on 2 AWS GovCloud Lattice hosts leaks internal namespace + service identity | Anduril |
| LOW | AKM (Altius Key Manager) **internal** AWS GovCloud-EAST ELB names (`internal-altius-key-store-mfgops-1358106531`, `…-1797229230`) exposed via public DNS CNAMEs at `mfg.akm.anduril.com` and `mfgops-dev.akm.anduril.com` | Anduril |

I am also flagging two **non-findings** that I want to surface to your team because they might be worth your judgment, but I am not asserting them as security issues. See the bottom of this email.

---

## Finding 1. HIGH: Telefonica ARO Grafana. `/api/datasources` Anonymous Access

**Endpoint:** `https://grafana-grafana-monitoring.apps.telefonica.centralus.aroapp.io/api/datasources`

This Grafana instance is referenced in the `Content-Security-Policy: frame-src` header of the Anduril Lattice Developer Platform served at `20.106.9.145` and `172.171.128.46`. It is running on a Telefonica-managed Azure Red Hat OpenShift (ARO) cluster (`ytterbic-canidae`, centralus region).

`GET /api/datasources` returns the full datasource inventory to unauthenticated requests:

```
[12] RHACM Governance API     marcusolsson-json   https://api.telefonica.centralus.aroapp.io:6443/apis/policy.open-cluster-management.io
[4]  elasticsearch            elasticsearch       http://elasticsearch.elk-stack.svc.cluster.local:9200
[8]  elasticsearch-events     elasticsearch       https://elasticsearch-elk-stack.apps.telefonica.centralus.aroapp.io
[15] grafana-postgresql       postgres            opencost-metrics-db.eastus.cloudapp.azure.com:5432
[7]  lattics-bsidp            prometheus          http://48.216.155.182
[3]  loki                     loki                https://logging-loki-openshift-logging.apps.telefonica.centralus.aroapp.io
[2]  prom-aro-vms             prometheus          https://thanos-querier.openshift-monitoring.svc:9091
[1]  prometheus - cluster…    prometheus          https://prometheus-k8s.openshift-monitoring.svc:9091
[5]  prometheus-aks-test      prometheus          http://52.226.228.140:9090
[11] Trivy API                marcusolsson-json   http://trivysvc.eastus.cloudapp.azure.com:5001/api/trivy
```

**What this discloses:**

1. **Internal cluster service URLs** (Kubernetes Service DNS) for the OpenShift cluster: `elasticsearch.elk-stack.svc.cluster.local:9200`, `thanos-querier.openshift-monitoring.svc:9091`, `prometheus-k8s.openshift-monitoring.svc:9091`. These are not directly reachable from outside, but they reveal the internal namespace + service architecture.

2. **External plain-HTTP backends in Azure commercial East US** that the Grafana proxies to:
   - `http://48.216.155.182`. `lattics-bsidp` Prometheus (named for Lattice Backstage IDP)
   - `http://52.226.228.140:9090`. `prometheus-aks-test` Prometheus
   - `http://trivysvc.eastus.cloudapp.azure.com:5001/api/trivy`. Trivy security scanner API
   - `opencost-metrics-db.eastus.cloudapp.azure.com:5432`. PostgreSQL backing OpenCost cost-metrics

3. **An RHACM (Red Hat Advanced Cluster Management) policy datasource** pointing at the Telefonica ARO cluster's K8s API server. Though that endpoint itself enforces auth, the URL discloses the cluster's API hostname.

The naming `lattics-bsidp` and `prometheus-aks-test` directly references Lattice ("lattics" appears to be a typo of "lattice" baked into the datasource name; bsidp = Backstage IDP). This is the Lattice monitoring plane. Anduril-relevant, even though the Grafana itself is on Telefonica infrastructure.

**Note on responsibility:** The Grafana sits on Telefonica's ARO. Remediation is in Telefonica's hands. I am disclosing to Anduril because (a) the datasource names embed Lattice-specific naming, indicating Anduril's monitoring is what's being exposed, and (b) you can coordinate with Telefonica more efficiently than I can.

**Remediation:**
- Telefonica should set `[auth.anonymous] enabled = false` in `grafana.ini`.
- If anonymous read-only dashboards are required, scope the anonymous role so it cannot reach `/api/datasources` (Grafana's `Viewer` role still has datasource visibility, needs custom RBAC).

---

## Finding 2. HIGH: Systemic Private-IP Leakage Across andurildev.com Route53 Zone

**Scope:** Of 157 unique subdomains under `andurildev.com` (sourced from `api.certspotter.com` certificate transparency data), **44 (28%) resolve to RFC-1918 private IP addresses in public DNS**. This is not a one-off. It spans the zone and exposes multiple distinct internal subnets.

### Internal subnets exposed (sampled, non-exhaustive)

| Internal range | Subdomains observed | Likely tier |
|---|---|---|
| `10.32.16.0/20` | `groundcover.metrics-dev`, `groundcover-ingest.metrics-dev` | Observability / metrics ingestion |
| `10.32.48.0/20` | `vault.cloudos`, `atlantis.cloudos`, `atlantis-queue.cloudos`, `deploy-sandbox`, `observability-trinode` | Secrets, Terraform automation, deployment |
| `10.32.65-75.x` | `ddb-alpha-1`, `ddb-alpha-2`, `ddb-alpha-3`, `ddb-alpha-4`, `cirilla-dev`, `ingest.dive-dev` | Application/data tier (4-node HA pattern) |
| `10.32.96-119.x` | `lattice-ai`, `data-catalog`, `asim`, `data-infra`, `ingest.dive-dev` | **AI/ML data plane** |
| `10.32.214.x` | `mmi-demo`, `mmi-demo-x` | MMI demo environment |
| `10.32.240-245.x` + `10.46.20-23.x` | `sie-dev`, `sie-dev-3`, `sie-dev-4`, `sie-staging`, `sie.sitl-manager-dev`, `*.env.sie-dev`, `*.env.sie-dev-3`, `*.env.sie-dev-4`, `*.env.sie-staging`, `*.env.sie.sitl-manager-dev`, `*.sandbox.sie-dev`, `*.sandbox.sie-dev-3`, `*.sandbox.sie-dev-4`, `*.sandbox.sie-staging`, `*.sandbox.sie.sitl-manager-dev`, `teleport.sie-staging` | SIE cluster — multiple environments + their `.env.` and `.sandbox.` namespaces + Teleport bastion |
| `10.33.8.x` | `ae-0.crucible`, `cloud-2.crucible`, `cloud-3.crucible`, `cloud-4.crucible`, `weekly1.crucible`, `weekly2.crucible` | Crucible CI/CD cluster |
| `10.44.133-143.x` + `10.44.236-238.x` | `jci.jama`, `release-eng.jama-dev`, `connect.cedar.sie` | Jama / Cedar |
| `10.45.42-46.x` | `lectronimo`, `access-metrics.lectronimo`, `smbcai-obs`, `access-metrics.smbcai-obs`, `ingest.smbcai-obs` | Customer / partner demo environments |
| **`172.16.0.x`** | `mwg.dev0.asv.maritime` | **Maritime ASV — separate 172.16/x addressing scheme** |

Sample evidence:

```
$ dig +short vault.cloudos.andurildev.com
10.32.56.187 / 10.32.53.191 / 10.32.48.87

$ dig +short lattice-ai.andurildev.com
10.32.114.54 / 10.32.98.211 / 10.32.105.165

$ dig +short ddb-alpha-1.andurildev.com
10.32.75.203 / 10.32.66.104 / 10.32.71.181

$ dig +short teleport.sie-staging.andurildev.com
10.32.241.147 / 10.32.245.161 / 10.46.20.162

$ dig +short mwg.dev0.asv.maritime.andurildev.com
172.16.0.110 / 172.16.0.77 / 172.16.0.92
```

### What this discloses

- **Internal subnet allocation strategy**: the `10.32.x.x` zone is partitioned by tier (observability / secrets / data / AI / SIE / customer-demo) at /19–/20 granularity. From an attacker's perspective: knowing which subnet hosts AI/ML, which hosts secrets, and which hosts SIE materially shortens the kill chain if any internal foothold is obtained later.
- **Per-tier deployment shape**: the consistent 3-IP-per-record pattern across most subdomains reveals 3-AZ HA topology. The `ddb-alpha-{1,2,3,4}` cluster reveals a 4-node sharding pattern.
- **Separate addressing scheme for maritime ASV**: `mwg.dev0.asv.maritime.andurildev.com` uses 172.16/24 instead of 10.32/16, indicating the autonomous surface vessel network is on its own VPC/transit. Useful intelligence about your platform's network segregation strategy.
- **SIE cluster matrix**: four `sie-dev*` environments + staging + their `env`/`sandbox`/`teleport` namespaces all leak. Whatever SIE is, its full multi-environment topology is enumerable from public DNS.
- **Customer / partner naming**: `lectronimo` and `smbcai-obs` (with sibling `*-obs`/`access-metrics`/`ingest` records) reveal customer-specific environments. `lectronimo` and `smbcai` are not intuitive to outsiders, but the existence of dedicated subnets for them in public DNS confirms which third parties have Lattice deployments.

### Class-of-issue, single-fix remediation

The fix is at the zone level, not per-record:

1. **Audit the entire `andurildev.com` Route53 hosted zone** for any A/AAAA records resolving to RFC-1918 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16).
2. **Move those records to an internal-only resolver** (Route53 Private Hosted Zone associated with the relevant VPCs, or an on-prem DNS) and remove from the public zone.
3. **Add a CI gate** on Route53 changes. Any PR adding an A record to the public zone must pass an "is this RFC-1918?" check.
4. If the records exist in the public zone deliberately for VPN-only name resolution: the same DNS view can be served from a private zone or a split-horizon resolver without publishing to the world.

We can provide the full 44-subdomain leak list and the certspotter source if your DNS team wants the raw input for the audit.

---

## Finding 3. MEDIUM: Self-Signed `localhost` Cert Auto-Renewing on 3 Public Lattice Deployments

Three publicly-reachable hosts serving "Anduril Lattice - Login" present a self-signed certificate with `Issuer/Subject: C=US, ST=CA, L=Costa Mesa, O=Anduril, CN=localhost`:

| IP | Host org | Port | Last cert observed |
|---|---|---|---|
| `62.10.249.86` | Microsoft Limited (Phoenix) | 443 | rotates regularly |
| `147.15.146.27` | Oracle Corporation (Austin) | 443 | new cert issued today (2026-05-08 21:58 UTC) |
| `172.65.50.118` | Cloudflare, Inc. (SF) | 443 | rotates regularly |

Critically, **the cert was rotated today on at least one of these hosts (Oracle), and the new cert is still the broken `CN=localhost` template**. Whatever automation manages cert lifecycle on these hosts treats the localhost cert as the legitimate state and re-renews it. This isn't a one-time deployment mistake. It's a deployment-template + cert-renewal automation defect that quietly persists.

**Why this matters:**
- Browsers fail TLS validation against `CN=localhost` for any other hostname → trains users to click through TLS warnings on Anduril Lattice login pages
- Publishes the internal CA naming convention (`O=Anduril, L=Costa Mesa, CN=localhost`) in the cert chain → assists impersonation
- Suggests these deployments may be orphaned or wrong-environment instances that should not be public-facing

**Remediation:** audit the deployment template + add a CN/SAN-matches-deployment-hostname validation gate to the cert-renewal automation. Or: confirm these deployments should not be public, and remove the public DNS / firewall them.

---

## Finding 4. LOW: `fleet-core-toc.fleet.internal` cert SAN exposed on 2 AWS GovCloud Hosts

Hosts `15.205.183.4` and `56.136.102.127` (both AWS GovCloud Oregon, `us-gov-west-1`) serve "Anduril Lattice - Login" with cert `CN=fleet-core-toc.fleet.internal`. The internal namespace (`fleet.internal`) and service identity (`fleet-core-toc`, likely Fleet Core Tactical Operations Center) are leaked in the cert SAN, visible in CT logs and to anyone connecting to port 443.

Same root cause as Finding 3 (cert-template/renewal automation not validating SAN matches public hostname).

---

## Finding 5. LOW: AKM Internal-ALB Names Exposed via Public DNS CNAMEs

`mfg.akm.anduril.com` CNAMEs to `internal-altius-key-store-mfgops-1358106531.us-gov-east-1.elb.amazonaws.com`, and `mfgops-dev.akm.anduril.com` CNAMEs to `internal-altius-key-store-mfgops-1797229230.us-gov-east-1.elb.amazonaws.com`. The string `internal-` in the AWS-generated ALB DNS name indicates these are AWS internal-only ALBs that AWS will only route within the VPC, but the CNAMEs are in the public `anduril.com` Route53 zone.

The leak isn't the IP (internal ALBs aren't externally routable), it's:
- The **internal LB name** (an attacker who later obtains VPC access knows the exact LB to target)
- The **AKM (Altius Key Manager) operational tier naming** (`mfgops` = Manufacturing Ops, `eudops` = European Ops)
- The **AWS GovCloud-EAST region** for AKM's manufacturing-ops tier

`mfg-api.akm.anduril.com` (11 IPs) and `ops-api.akm.anduril.com` (9 IPs) further enumerate the AKM API tier in AWS GovCloud-EAST. These aren't internal-named so they're operationally intentional, but the size of the cluster is now public.

Same class as Finding 2; same fix (zone audit). Calling out separately because it specifically affects the encryption-key-management infrastructure for the Altius loitering munition program.

---

## Items Surfaced for Your Judgment (Not Asserted as Findings)

**(a) Internal Backstage CSP includes `http://route-ytterbic-canidae-openshift-operators.apps.telefonica.centralus.aroapp.io` (plain HTTP).**
The route currently returns 503, so this is not an active mixed-content vector. However the CSP `frame-src` permits a plain-HTTP iframe to your OpenShift Operator Lifecycle Manager interface. If the route comes back online, the Backstage page would be allowed to frame it cleartext. Consider auditing the CSP for any remaining `http:` entries.

**(b) Certificate Transparency log surface for `andurildev.com` includes classification-level and customer/program naming.**
CT publication is required by RFC 6962 for all publicly trusted certificates. This is not a security finding. I am surfacing it because the cert SAN naming convention in your CT data names specific customer programs and classification levels in a way that may warrant ITAR / information-control review:

- `dil-demo-secret-peer-1.dil-demo.andurildev.com`, `dil-demo-secret-peer-2.dil-demo.andurildev.com`, `dil-demo-secret-ra.dil-demo.andurildev.com`. DIL DEMO at **SECRET** classification (peer-1, peer-2, RA)
- `dil-demo-topsecret-peer-1.dil-demo.andurildev.com`, `dil-demo-topsecret-peer-2.dil-demo.andurildev.com`, `dil-demo-topsecret-ra.dil-demo.andurildev.com`. DIL DEMO at **TOP SECRET** classification
- `usaf-lattice-ssh-bastion.andurildev.com`: USAF Lattice SSH bastion
- `c2-jos-omega-red.andurildev.com`: JOS / Omega Red codename
- `gide8.andurildev.com`: GIDE 8 (Global Information Dominance Experiment 8, DoD JADC2 exercise)
- `c2-space.andurildev.com`, `c2-space-dev.andurildev.com`. Space C2 deployments
- `jsdf-development.andurildev.com`: Japan Self-Defense Forces
- `anduril-jadc2.andurildev.com`, `*.flux-ra.jadc2-dsb.andurildev.com`, `c2-safari.jadc2.andurildev.com`. JADC2-tier deployments
- Various program codenames in cert SANs: ghost, gauntlet, longbow, archangel, omega-red, kreacher, cirilla, juno, apollo, etc.

The classified peer/ra naming is the strongest concern: even if the underlying clusters are air-gapped, the existence + classification of `dil-demo-secret-*` and `dil-demo-topsecret-*` clusters is now a matter of public CT record (anyone watching CT logs has indexed them). Wildcard certificates (`*.andurildev.com` or per-environment wildcards) would suppress per-subdomain enumeration in CT going forward; cleanup of historical entries is not possible (CT is append-only).

**(c) Backstage instances at `20.106.9.145` and `172.171.128.46`.**
Both serve the Lattice Developer Platform on port 80. Anonymous probes of `/api/catalog/entities` returned HTTP 500 (server-side error with logId, not catalog data) and `/api/auth/` returned 404. I do not have evidence of unauthenticated catalog enumeration. Surfacing for completeness in case your team wants to investigate the 500 logIds (`6462fa999a55e94adce2`, `af902715344b97c002bc`). They may indicate a misconfiguration worth reviewing.

**(d) Klas Telecom Government / Voyager OEM relationship is publicly disclosed via redirect rule in armory.anduril.com's JavaScript.**
The Armory app's bundled JS contains a redirect rule: `{"from":"/voyager-support","to":"https://www.klasgroup.com/support/","type":301}`. This makes the Klas-Anduril hardware OEM relationship trivially discoverable via JS string analysis of the Armory marketplace. Not a security finding. Just noting that the supply-chain attribution your customers/partners likely treat as private is in client-side code. If the relationship is intentionally public, no action; if it's meant to be customer-only knowledge, consider routing /voyager-support through a server-side redirect instead of a client-side rule.

**(e) Palantir Workshop module ID exposed in customerportal.anduril.com 302 redirect.**
`https://customerportal.anduril.com/` returns a 302 to `https://alpha.palantirgov.com:443/workspace/module/view/latest/ri.workshop.main.module.f8c05d84-ac01-4a9b-8a9e-9cbc401d2cf8`. The Palantir Resource Identifier (RID) is a stable identifier for a specific Workshop module, anyone with credentials on `alpha.palantirgov.com` can navigate directly to that module by RID. Same observation as (d), likely intentional, but worth noting the RID is in the public 302 Location header.

---

## Researcher

**Nicholas Michael Kloster**
NuClide Research | https://nuclide-research.com
nicholas@nuclide-research.com
CISA disclosure history: CVE-2025-4364, ICSA-25-140-11

This disclosure is submitted under good faith per your published security.txt. No bounty requested.

Preferred timeline: 90 days standard. Happy to coordinate a longer window if Telefonica remediation requires it.

A **redacted** case study will be pushed to my public OSINT repo after this email lands (path: `case-studies/commercial/anduril-lattice-dev-infrastructure-2026-05-08.md` at https://github.com/Nicholas-Kloster/AI-LLM-Infrastructure-OSINT). The public form references this disclosure by file path and contains only what is already public via Certificate Transparency / Shodan. No IP-level cluster inventory, no per-tier cert SANs, no targeted operational dorks. The full cluster topology, IP fleet inventory, and tier-specific Shodan queries are held in this disclosure pack and will be added to the public artifact only after you acknowledge and a remediation window has passed. If you would prefer the redacted case study not be published at all, say so and I will hold it.
