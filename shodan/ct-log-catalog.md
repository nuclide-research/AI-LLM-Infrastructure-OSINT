# Certificate Transparency Log Catalog

_NuClide Research · CT-derived hostnames, operator attribution pivots, and infrastructure naming patterns._

## How this works

Every public TLS cert is logged to open, append-only CT logs (RFC 6962) before browsers trust it. Once logged, it cannot be removed. Mining SANs from crt.sh / Censys reveals:

- Internal hostnames that were accidentally given public certs
- Operator naming conventions (feeds VisorGraph pivot)
- New environments the moment a cert is issued (certstream)
- Rogue / mis-issued certs against your own domains

**Two uses in the research pipeline:**

1. **Stage -1 / Pre-assessment:** query vendor domains to map the platform's own infrastructure and naming conventions before scanning.
2. **Stage 3 / VisorGraph:** after confirmation, pivot on cert SANs from found IPs → operator attribution chain. VisorGraph already runs this; log the output here.

Query (run against your own targets or vendor domains):
```bash
# All subdomains ever cert-issued under a domain
curl -s 'https://crt.sh/?q=%.domain.com&output=json' \
  | python3 -c "import sys,json; [print(n) for c in json.load(sys.stdin) for n in c.get('name_value','').split('\n') if n and not n.startswith('*')]" \
  | sort -u

# Filter for high-value internal patterns
... | grep -Ei 'dev|stag|test|internal|admin|vpn|api|k8s|kube|gateway|proxy|ml|ai|llm'
```

---

## AI Gateways (surveyed 2026-06-01)

### portkey.ai

| Finding | Value |
|---|---|
| Domain queried | `portkey.ai` |
| Cert count | 963 |
| Total unique names | 39 |
| Cloud tier | GCP (`gcp-proxy`, `privatelink-gcp`) + Azure (`privatelink-az`) Private Link endpoints |
| Observability stack | `grafana.portkey.ai`, `loki.portkey.ai` (internal stack exposed via CT) |
| Operator-specific endpoints | `panic-button-*` subdomains -- cloud-managed SaaS, NOT self-hosted |
| Named operators (via panic-button-* SANs) | DoorDash, Xero, Ascend, Analog, CBA (?Commonwealth Bank AU), JHU (Johns Hopkins), PG&E |
| Self-host relevance | None -- `panic-button-*` = Portkey-managed SaaS. Self-hosted instances have no vendor-controlled subdomains. Fingerprint via body string only. |
| VisorGraph seeds | `api.portkey.ai`, `gcp-proxy.portkey.ai`, `gateway-proxy.privatelink-gcp.portkey.ai` |
| Notes | `doordash-urgent.portkey.ai` and `fmae-panic.portkey.ai` suggest feature-specific customer endpoints; financial/utilities/healthcare verticals confirmed as enterprise customers |

### getbifrost.ai / maxim.ai

| Finding | Value |
|---|---|
| Domain queried | `getbifrost.ai` |
| Cert count | crt.sh 502 error at query time |
| Status | Retry pending |
| VisorGraph seeds | N/A pending |

### konghq.com

| Finding | Value |
|---|---|
| Domain queried | `konghq.com` |
| Cert count | crt.sh timeout (large domain) |
| Status | Retry pending -- use Censys instead |
| VisorGraph seeds | N/A pending |

### tensorzero.com

| Finding | Value |
|---|---|
| Domain queried | `tensorzero.com` |
| Cert count | 473 |
| Total unique names | 28 |
| Interesting names | 10 |
| Cloud provider | GCP (`gcp-us-central1.api.tensorzero.com`) |
| API surface | `api`, `api2`, `authapi` -- tiered API with separate auth endpoint |
| Staging environments | `autopilot.staging.tensorzero.com`, `nanoagent.staging.tensorzero.com`, `staging.api.tensorzero.com` |
| Code editor integration | `proxy.code.tensorzero.com` -- Cursor / coding agent proxy endpoint |
| Test environment | `tensor0-test-api.tensorzero.com` |
| K8s surface | `api-kube.tensorzero.com` |
| VisorGraph seeds | `api.tensorzero.com`, `authapi.tensorzero.com`, `gcp-us-central1.api.tensorzero.com` |
| Notes | Staging environments named in CT = deployed with public certs; `nanoagent.staging` and `autopilot.staging` suggest active experimentation pipeline |

### helicone.ai

| Finding | Value |
|---|---|
| Domain queried | `helicone.ai` |
| Cert count | crt.sh 404 (domain may redirect; try `helicone.ai` without subdomain wildcard) |
| Status | Retry pending |
| VisorGraph seeds | N/A pending |

---

## Operator CT Pivots (from VisorGraph cert-pivot on confirmed hosts)

_Populated during Stage 3 of each survey. IP → TLS cert (no SNI) → SAN array → crt.sh subdomain expansion → operator footprint._

| IP | Cert CN/O | SANs | Operator | Survey | Notes |
|---|---|---|---|---|---|
| _Populated by VisorGraph runs_ | | | | | |

---

## CT Findings by Survey Category

### LLM Gateways (this survey)

_Populate after VisorGraph runs on confirmed hosts._

### Prior surveys (notable CT pivots)

| Operator | Discovered via | Key finding |
|---|---|---|
| Pharos (four-platform stack) | cert-pivot on bare IP | Four distinct platforms (MLflow+Langfuse+Attu+ClickHouse) attributed to single operator via cert SAN chain |
| proplay.co | VisorGraph rDNS+passive-DNS | Anonymous IP → named sports-tech operator |
| PENTECH | cert SAN → bucket path | aimap artifact path `aipod-crop` in S3 URL attributed the operator |

---

## Defensive Observations (encountered in the wild)

| Operator | Pattern observed | CT implication |
|---|---|---|
| Large enterprise AI stacks | Per-host `cert-manager` / ingress with ACME | Every internal service name in CT despite "internal" label |
| Self-hosted LLM builders | Let's Encrypt certs for `langflow-internal.*`, `flowise-dev.*` | Permanent public record; service assumed internal |
| K8s operators | `*.svc.cluster.local` in cert SAN arrays | Internal cluster naming leaked; namespace conventions exposed |

---

## Notes

- crt.sh is the primary query source; Censys adds full-port coverage for verification.
- VisorGraph runs CT expansion on every confirmed host (Stage 3, every survey).
- Censys `cencli view <asset>` returns the SAN array for targeted enrichment (1 credit/host; 7 credits remaining this week, resets 2026-06-08).
- **Cannot remove a logged entry.** Prevention only: private CA for internal services, wildcard certs for public services where specific names shouldn't appear.
- New cert monitoring: certstream feeds real-time issuance; use for operator footprint tracking on active engagements.
