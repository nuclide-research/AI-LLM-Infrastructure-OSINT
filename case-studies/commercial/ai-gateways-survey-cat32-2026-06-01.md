---
type: case-study
category: 32
platform: AI Gateways (Portkey, Kong AI, Bifrost, one-api, new-api, LiteLLM, TensorZero, Helicone, Envoy AI Gateway, sub2api)
survey_date: 2026-06-01
status: complete
findings: 87 confirmed-unauth (Envoy admin) + 1,699 surface-open across 5 platforms
verification_rung: inner-A / outer-1 (banner-confirmed unauth on Envoy and Kong Admin; default-cred probe Depth-A negative on one-api/new-api; per-platform host samples, no population-wide active probe)
ledger: nuclide.db (visorlog) source tag survey-ai-gateways-2026-06-01, 1,786 events, 87 critical / 618 high / 1,081 medium
insights: 74, 75
---

# AI Gateways Population Survey: Cat-32 (2026-06-01)

_NuClide Research · 2026-06-01 (closed 2026-06-02)_

---

## Threat Model

An AI gateway sits in front of every upstream LLM provider an operator uses. It holds the OpenAI key, the Anthropic key, the Gemini key, the DeepSeek key. All in one process. That is the point of the product. It is also the problem.

<!-- ksat-tag:auto-generated:start -->
## DCWF KSAT coverage

Auto-derived from DCWF AI work-role rule files (`ksat-tag`).

- **672 (AI Test & Evaluation Specialist):** K7003, K7004, K7044, S7068, S7070, S7075, T5858, T5904, T5919
- **733 (AI Risk & Ethics Specialist):** K7040, T5868, T5893
- **overlap (Common AI KSATs (all 5 roles)):** K1158, K1159, K22, K6311, K6935, K7003, S7065

<!-- ksat-tag:auto-generated:end -->

A single exposed model server leaks one model. A single exposed gateway leaks the whole account. Every provider key. The prompt and response logs. The downstream user roster. The billing line those keys draw against. This is the master-key multiplier. It earns the gateway tier its own survey.

The hypothesis was the standing auth-on-default thesis. Any layer that ships without authentication on by default gets deployed without it at population scale. Gateways test it well. The products split on shipping defaults. Some ship a default credential. Some ship auth-on. Some ship no auth concept on the admin plane at all.

---

## Discovery

Passive throughout. Shodan search API only. Zero active probing of operator hosts. A 19-dork catalog produced 9 productive dorks and 2,624 unique IPs with full banner data.

The productive dorks, by platform:

| Platform | Dork | Signal |
|---|---|---|
| Envoy admin | `port:9901 http.html:"config_dump"` | admin index page served to the crawler |
| one-api | `http.title:"One API" port:3000` | admin web UI title |
| new-api | `http.title:"New API" port:3000` | admin web UI title (one-api fork) |
| LiteLLM | `port:4000 http.html:"litellm"` | API surface on the canonical port |
| Kong Admin API | `port:8001 http.html:"Welcome to Kong"` | admin API root JSON |
| Kong Manager | `http.favicon.hash:-112038367` | manager GUI favicon |
| Bifrost | `http.html:"getbifrost.ai" port:8080` | gateway landing |

The LiteLLM title dork (`http.title:"LiteLLM"`, 65,976 hits) is FP-heavy. The AS63949 honeypot fleet on Akamai and Linode inflates it. The real population came from `port:4000`, about 2,290 hosts. We recorded the title count and did not use it as the finding base.

---

## Fingerprinting

aimap v1.9.46 shipped four new gateway fingerprints: Kong Admin API, Bifrost, Portkey, and Envoy Admin. The binary classified the 2,624-IP corpus by API shape, not by dork hit. That is what separates a platform instance from a title collision (Insight #15).

The split that matters is the shipping default:

- **Default-credential tier** (one-api, new-api): ship `root` / `123456`, documented in the README, no forced change on first run.
- **Auth-on tier** (LiteLLM current, TensorZero, Helicone): require a key out of the box.
- **No-auth-concept tier** (Envoy admin, Kong Admin API in default docker-compose): the admin plane has no authentication mechanism. Reachability is the only gate.

---

## Verification

The Envoy hosts are confirmed unauthenticated. The default-credential CRITICAL on one-api and new-api is not. The probe decided both, and it changed the headline number.

**Envoy admin: 87 hosts, CONFIRMED-UNAUTH.** The dork matches the Envoy admin index served on port 9901. The Envoy admin interface ships with no authentication mechanism. It is documented for loopback use only. An admin index served to a crawler means `/config_dump` is reachable. `/config_dump` returns every upstream cluster credential as JSON. The banner is the proof. We did not fetch the secrets. The finding is an unauthenticated admin plane, secret values present and not retrieved. Depth-A by banner, Breadth-1 across 87 hosts.

**one-api and new-api: 1,000 hosts, the CRITICAL that wasn't.** Both ship the documented default `root` / `123456`. The pre-survey framing tagged all 1,000 CRITICAL on that basis. So we probed it. One unauthenticated `POST /api/user/login` with `root` / `123456`, against a 20-host sample of each.

The result was 0/40. Every sampled operator had changed the default. All 40 returned `success:false`.

That negative result is load-bearing. The CRITICAL label rested on the default credential being live. The one probe aimed at it came back negative. A finding cannot keep a CRITICAL label when its evidence comes back negative. The confirmed state is narrower. The admin UI of a key-brokering gateway is surface-open. Auth is holding on the sample. That is MEDIUM. The CRITICAL ceiling survives only for the unmeasured part of the population. Forty hosts out of about 16,000 is too thin to size that part.

The ledger correction was 1,087 critical down to 87. One thousand findings moved from critical to medium. A probe moved them. The 87 that stayed are the Envoy hosts, every one banner-confirmed. The ledger's `CONFIRMED-UNAUTH` count and its critical count are now the same number. Nothing in the top tier rests on assumption.

**Kong Admin API: banner-confirmed unauth, not yet ledgered.** The `port:8001` dork matches the admin API root returning HTTP 200 with the full service registry and plugin list as JSON. That JSON is the proof. An unauthenticated Kong Admin API is the CVE-2020-11710 class. `POST /services` plus `POST /plugins` with a pre-function Lua body is unauthenticated remote code execution. Documented chain, not run. One caveat: the Kong Admin records did not reach the ingested ledger feed. The ledger's 87 critical is Envoy only. Kong Admin unauth is documented in the breakdown and the NIEMS attribution below, pending a feed reconciliation.

---

## Operator Attribution

VisorGraph passive cert-pivot returned 0 graph nodes. The admin ports that carry the findings, 8001 and 9901, are HTTP-only. There is no TLS certificate on those ports to pivot from. This is Insight #75. HTTP-only admin ports dead-end cert-pivot. The pivot has to reach a TLS port first, 443 or 6443, or fall back to banner hostnames.

The fallback was Shodan hostname extraction and `api.host()` dossiers. Three operators attributed. Each one carries the gateway on top of a deeper stack.

- **NIEMS, Thailand** (`api-portal-idems.niems.go.th`). A Thai Ministry of Public Health agency. Kong Admin API unauthenticated on Kong 2.7.2. That version has been end-of-life since 2022. The default self-signed Kong cert was never rotated. A Kubernetes kubelet is exposed on the same host. Government healthcare infrastructure, admin plane open, platform unpatched.
- **Purdue University RCAC** (`cms-h006.rcac.purdue.edu`). A research computing cluster. Envoy admin unauthenticated on a k3s node. The k3s API returns 401. Auth holds one layer up and the Envoy admin plane below it is open.
- **WAIcore / khotlenko.ru** (German VPS, Russian operator domain). The deepest stack in the survey. Envoy admin, HashiCorp Nomad, Consul, PostgreSQL, and end-of-life PHP 7.4.33. All on one IP. All under one personal domain whose cert SANs map the estate.

The pattern holds across all three. The gateway is the visible exposure. It sits on orchestration, a database, or an EOL runtime. The gateway is the door. The stack behind it is the house.

---

## Severity Model (corrected)

| Platform | Hosts | Severity | Basis |
|---|---|---|---|
| Envoy admin | 87 | CRITICAL | banner-confirmed unauth admin; config_dump reachable by Envoy design |
| Kong Admin API | 600 pop | CRITICAL (not ledgered) | banner shows unauth admin JSON; CVE-2020-11710 class; absent from the ingested feed |
| LiteLLM | 494 | HIGH | API/Swagger surface; older versions leak `/v1/models` and `/health` unauth |
| Kong Manager | 124 | HIGH | admin GUI reachable; implies Admin API exposure |
| one-api | 500 | MEDIUM | surface-open admin UI; default-cred probe NEGATIVE 0/20 |
| new-api | 500 | MEDIUM | surface-open admin UI; default-cred probe NEGATIVE 0/20 |
| Bifrost | 81 | MEDIUM | auth-bypass on `/` (GitHub Issue #937), `Server: fasthttp` |

Ledger total: 1,786 events. 87 critical, 618 high, 1,081 medium. Source tag `survey-ai-gateways-2026-06-01`. The Kong Admin API critical sits outside this count, pending feed reconciliation.

---

## Population Totals (Shodan, 2026-06-01)

| Platform | Population | Note |
|---|---|---|
| new-api | 13,456 | largest exposed gateway population; mostly Chinese-region cloud relays |
| Kong (all) | 70,924 | `Server: kong` across all deployments, not all admin-exposed |
| LiteLLM | 65,976 title / ~2,290 real | title dork FP-heavy via AS63949 honeypot fleet |
| one-api | 2,449 | default-cred tier |
| Kong Admin API | 600 | CVE-2020-11710 class when unauth |
| Kong AI plugin | 277 | AI plugin active on admin port |
| Kong Manager | 268 | admin GUI |
| Bifrost | 237 | auth bypass |
| Envoy config_dump | 87 confirmed (89 raw dork hits) | plaintext upstream credentials |
| Helicone | 2 | maintenance mode, auth enforced |
| TensorZero | 1 | auth-on-default |

The new-api population is the scale headline. 13,456 instances, mostly Chinese-region cloud infrastructure. They broker Western provider keys to downstream resale users. A pooled-resale model sitting on a documented default credential is the Insight #39 attribution-laundering pattern at the gateway tier.

---

## Insights

**Insight #74. The gateway is a master-key multiplier.** One exposed gateway leaks every upstream provider key the operator wired in, not one model. The harm scales with the gateway's downstream user count, not with host count. A single exposed new-api instance can hold provider keys for its whole resale base.

**Insight #75. HTTP-only admin ports kill cert-pivot.** Kong :8001 and Envoy :9901 are HTTP-only. VisorGraph returned 0 nodes because there is no certificate to pivot from. Attribution on this tier must reach a TLS port first or fall back to banner hostnames.

**Candidate observation (not codified).** The default-credential populations have rotated. one-api and new-api both ship `root` / `123456`. Zero of 40 sampled operators still ran it. The documented-default-credential model is a hypothesis to probe per host, not a severity to assume per population. It is the inverse of the auth-on-default thesis. When the default is a known-bad credential instead of open access, the sampled operators had all closed it. Worth a population-scale probe before it earns a number.

---

## Toolchain Provenance

| Tool | Role | Result |
|---|---|---|
| JAXEN / Shodan | discovery | 2,624 IPs, 9 productive dorks |
| aimap v1.9.46 | fingerprint | 4 new gateway fingerprints (Kong Admin, Bifrost, Portkey, Envoy Admin) |
| default-cred probe | verify | `cat32-defaultcred-probe.py`, 0/40 one-api and new-api |
| VisorGraph | attribution | 0 graph nodes (HTTP-only admin ports, Insight #75); fell back to Shodan dossiers |
| VisorLog | ledger | 1,786 events ingested to nuclide.db after severity correction |

We patched VisorGraph during the survey to expose a `-max-iter` flag. The engine capped at 50 fixed-point iterations and truncated a 187-seed run. The patch is committed. The cert-pivot still returned 0 here for the HTTP-only-port reason, not the iteration cap.

---

## Honest Negative Space

- **Portkey: 0 findings.** A pure API proxy. The health endpoint is not publicly indexed. Instances sit behind reverse proxies or VPN. No Shodan signal is not no deployment.
- **TensorZero: 1, auth-on. Helicone: 2, auth-on, maintenance mode.** These confirm the thesis by its contrapositive. Auth-on-default products produce near-zero unauth at population scale.
- **No active probing of operator hosts.** Every finding comes from Shodan's crawl banners and the one default-cred login probe. The Envoy and Kong Admin CRITICAL labels are banner-confirmed unauth, not run exploitation. Secret values were not retrieved. RCE chains were not run.
- **Default-cred sample is thin.** 40 of about 16,000 one-api and new-api hosts. The MEDIUM label is the verified floor, not a cleared population.
- **Kong Admin findings are not in the ledger.** The ingested feed held Envoy, LiteLLM, Kong Manager, one-api, new-api, and Bifrost. Kong Admin API records were not in it. The breakdown and attribution carry them. The ledger does not. Reconciliation pending.

---

## Remediation (population reference)

- **Envoy:** bind the admin interface to loopback (`--admin-address 127.0.0.1:9901`). It has no auth. It must never face the internet.
- **Kong:** firewall :8001 and :8444. Bind the admin API to loopback or a private network. Enable Kong RBAC if remote admin is required.
- **one-api / new-api:** change the default admin password on deploy. The install must not leave `root` / `123456` live. Bind to a private network or VPN.
- **LiteLLM:** upgrade to current. Set `LITELLM_MASTER_KEY`. Disable Swagger in production.
- **Bifrost:** front with an authenticated reverse proxy until Issue #937 is resolved.

---

## See Also

- `methodology/insight-74-gateway-as-master-key-multiplier.md`
- `methodology/insight-75-http-admin-ports-kill-cert-pivot.md`
- `data/findings-breakdown-ai-gateways-2026-06-01.txt` (full per-finding breakdown)
- `data/cat32-visorgraph-attribution.md` (operator attribution detail)
- `data/platform-intel/ai-gateways-osint-2026-06-01.md` (Stage -1 intel)
- `methodology/insight-39-pooled-account-attribution-laundering.md` (the new-api resale pattern)
- `methodology/insight-15-dork-hits-vs-platform-instances.md` (the LiteLLM title-dork FP class)
