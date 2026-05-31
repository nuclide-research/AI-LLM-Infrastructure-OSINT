# Service Mesh Control Planes: when exposure is the authentication failure

_Network Perimeter / Service Mesh survey. 2026-05-31. New platform class._
_Findings: nuclide.db #36200-36216. Insight #71. Breakdown: data/findings-breakdown-service-mesh-2026-05-31.txt._

## Why this category

Every survey so far measured platforms that **have** an authentication layer and
ship it on or off. Service-mesh introspection planes are a harder test for the
auth-on-default thesis: most of them have **no auth layer at all.** Kiali's
anonymous strategy, Linkerd's viz dashboard, Cilium's Hubble UI and relay, Istio's
Envoy-admin and istiod-debug all rely on *network placement* (loopback,
ClusterIP, NetworkPolicy, "do not expose") as the entire control. The question
this survey asks: when the only control is network position, what does the exposed
population look like? The prediction (Insight #71, codified here): exposure and
unauthenticated are the same fact, so the rate approaches 100% by construction.

## Discovery

Shodan title-dorks from the prior session seeded the candidate set:
`http.title:"Kiali"` (140 hits), `http.title:"Hubble UI"` (22),
`http.html:"data-controller-namespace=\"linkerd"` (5), and a Cilium cluster-cert
pivot (`ssl:"hubble-grpc.cilium.io"`, 3). Harvested and capped to 23 unique IPs.
The high/odd introspection ports the intel doc flagged as the highest-value surface
(Envoy admin 15000, istiod 15014, Linkerd proxy-admin 4191, Hubble Relay 4245)
returned 0 on Shodan: that tier is Shodan-dark and was not in this corpus.

## The tool gap, closed first

aimap had **zero** fingerprints for the entire category. Per the
manual-to-productize-to-rerun discipline, the survey built nine into aimap
(v1.9.41 -> v1.9.42): Kiali, Hubble UI, Linkerd Viz, Linkerd Proxy Admin, Cilium
Metrics, Istio Envoy Admin, Istiod Debug, Pomerium, Kubernetes API. The design
point that makes them verification tools and not just identifiers: the
**data-layer probe is ordered first** in each fingerprint. A 200 plus marker on
`/kiali/api/namespaces`, `/config_dump`, or `/debug/endpointz` proves identity and
unauthenticated state simultaneously, because an authenticated plane returns 401
and the probe fails. The matcher records `MatchPath` on first hit, so a single run
classifies the auth state per host (Insight #16: a 200 is identity, not auth-state;
the *data path* is what earns the severity). Nineteen TP/FP unit tests, full suite
green.

## Verification (the load-bearing stage)

aimap v1.9.42 against the 23 hosts (`-ports-class network-mesh`, re-curated to the
real introspection ports): 21 service matches. `MatchPath` did the classification.

**Kiali, 4/4 reachable on the anonymous strategy (HIGH).** Every confirmed Kiali
matched on `/kiali/api/namespaces`, not the gated `/api/config` fallback: the
data-layer probe fired, returning the full Kubernetes namespace array unauthenticated
via the Kiali ServiceAccount. The namespace names are the finding (restraint ethic):

- `109.237.70.159:20001` — 13 ns, `cattle-fleet-system`, `cattle-impersonation-system`: Rancher/RKE.
- `146.56.204.28:20001` — 11 ns, `kubesphere-system`, `extension-s2ibuilder`, `loki`: KubeSphere (Oracle Cloud).
- `34.101.217.236:80` — 12 ns, `argocd`, `gke-managed-*`: GKE with ArgoCD.
- `34.151.222.47:80` — **479 namespaces**, `api-chatbot-97-review-*`: an AI chatbot
  platform's entire per-pull-request preview topology, fully enumerable. Censys
  placed the host in Sao Paulo, Brazil, on GCP; the Portuguese namespace fragments
  (`correcao`, `equalizaca`) corroborate a Brazilian operator. One unauthenticated
  GET maps every review environment, feature branch, and service in the cluster.

**Cilium Metrics, unauthenticated (MED).** `159.138.129.194` on 9962 and 9965
served `cilium_drop_count_total` and `hubble_flows_processed_total`: the workload
and flow-graph topology, unauthenticated by construction (Huawei Cloud).

**Hubble UI, 9 hosts exposed (LOW, one MED).** The console ships with no login by
design. `34.166.133.241` additionally returned `Access-Control-Allow-Origin: *`
(CVE-2025-23047, insecure-default CORS). The flow *data* a Hubble UI displays is
served by its backend over an in-cluster hop to the relay, so an exposed UI implies
flow visibility; that implication is logic-level (inner-A), not exercised, by
restraint.

**kube-apiserver, 3/3 exposed but anonymous-denied (LOW).** The three Cilium-cert
hosts run kube-apiserver v1.29.0 on public 6443. `/version` is anonymous-readable
(identity), but `/api/v1/namespaces` returned non-200 to anonymous: the anon-data
probe correctly did **not** fire. The one plane with a real authentication and RBAC
layer held under the same exposure as the planes that fell.

## The crown jewel stayed internal

Hubble Relay 4245 is the category's most dangerous surface: `observer.Observer/GetFlows`
is a cluster-wide live network tap with L7 HTTP, DNS, and Kafka visibility. aimap
cannot speak gRPC, so a `grpcurl` lane covered it, restricted to `ServerStatus`
(counts and version, never `GetFlows`, which would stream live traffic records).
Result: **0 of 12** Cilium hosts had a reachable relay (9 filtered, 3 refused).
Operators expose the human-readable console and keep the machine data-plane internal.
The measured unauth population is a console-tier population; the data-plane tier is a
separate one (Insight #71 corollary).

Pivot 1 then measured that data-plane tier directly against the authenticated Shodan
web UI. Every marker-anchored dork returned **zero**: `port:15000 "config_dump"` (Envoy
admin), `port:15014 "pilot_xds"` (istiod), `port:4191 "proxy_build_info"` (Linkerd
proxy-admin), `"hubble_flows_processed_total"` and `"cilium_drop_count_total"` (Cilium).
`port:4245` returned 30 hosts, but it is a shared port and gRPC is opaque to Shodan;
grpcurl across all 30 confirmed **0 reflection-enabled Hubble Relays** (most filtered or
timed out, one live plaintext-gRPC host with reflection off, 103.86.177.103, left as a
residual blind spot since the hubble CLI is not go-installable here and the binary fetch
was sandbox-blocked this session). The console titles (`http.title:"Kiali"`,
`http.title:"Hubble UI"`) do return populations. So the tier split is now empirical, not
assumed: the console tier is Shodan-visible, the data-plane tier is Shodan-invisible,
because the crawler never issues the introspection paths (`/config_dump`, `/debug/*`,
`/metrics`) that carry the marker strings. Measuring it needs Censys full-range or
tiptoe/naabu, the documented next lane.

## Impact

A reachable Kiali on the anonymous strategy is not "one unauthenticated dashboard."
It is **cluster-wide reconnaissance delivered as an API**: the full namespace list,
the service graph, workload identities, and the traffic topology, handed to any
anonymous caller. For the 479-namespace host, that is the complete dev and review
surface of a commercial AI product, including every feature branch under active
work, exposed as a map an attacker would otherwise have to assemble by hand. The
BARE semantic mapping places this finding in the same class as the FinOps/Kubecost
cost-API exposure (`auxiliary_gather_kubecost_opencost_costmodel_api_exposure`,
0.572) and Kubernetes enumeration, not in a commodity-RCE class: it is a
first-party recon-primitive, the kind that bridges anonymous access to a targeted
attack.

## Remediation

- **Kiali**: set `auth.strategy` to `token` or `openid` (never `anonymous` on an
  exposed install). Do not route the Kiali API to a bare public port; if it must be
  reachable, front it with an authenticating proxy.
- **Cilium**: do not expose Hubble UI or Relay publicly (port-forward only, as the
  docs assume). Set `hubble.relay.tls.server.enabled=true`. Bind metrics
  (9962/9963/9965) to the node-internal interface. Patch CVE-2025-23047 (CORS).
- **Kubernetes API**: keep 6443 off the public internet (the three here already
  enforce RBAC against anonymous, which is what saved them; that is the control to
  preserve, not the exposure).
- **Category-wide**: treat "do not expose" planes as having no second line. The
  fix is the network boundary; there is no credential to add after the fact.

## Toolchain provenance

The chain ran by hand, in order, all tools, results recorded (null is a result).

- **JAXEN / Shodan** (prior session): title-dorks, 23 IPs harvested.
- **aimap v1.9.42**: built 9 mesh fingerprints + 19 tests this session; 21 matches across 23 hosts. The verification engine.
- **grpcurl** (gRPC lane, aimap HTTP-only gap): Hubble Relay 4245 ServerStatus probe, 0/12 reachable. Restraint: no GetFlows.
- **VisorGraph**: cert-pivot, thin (bare cloud IPs; Huawei default cert `eapp610.huawei.com`); confirmed `/kiali/` path-prefix and `public_intended` exposure.
- **aimap-profile**: 34.151.222.47 -> Google LLC / GKE.
- **Censys (cencli view)**: 34.151.222.47 -> Sao Paulo, Brazil, GCP, 1 service (no curated-scan blind spot here). 1 credit left; population-delta sweep deferred.
- **VisorLog**: #36200-36216 ingested to nuclide.db (4 high, 2 medium, 11 low), per-host verified severities (not a blind aimap ingest).
- **VisorScuba**: 0/0 vacuous pass. AI baseline has no control for service-mesh / cluster-introspection planes (tool gap, same as KubeSphere).
- **BARE**: Kiali -> kubecost/k8s-enum/k8s-exec recon class (0.572/0.558/0.528); Cilium metrics + Hubble UI NO-MATCH (first-party, novel).
- **VisorBishop**: ip-shadow on 16 confirmed IPs, 27 ports each, 0 adjacent unauth (managed cloud does not co-expose the data tier; contrast self-hosted Phoenix 27%).
- **menlohunt**: swept 5 GCP /24s near the confirmed hosts; AI-gateway port set has no mesh ports, no mesh-plane neighbors (tool-note: needs a mesh port-set).
- **nu-recon**: 34.151.222.47, simulated/degraded (Shodan key invalid); no new attribution.
- **recongraph**: 34.151.222.47, 0 nodes (nothing to pivot on a bare GKE IP; matches VisorGraph).
- **VisorSD**: AS136907 (Huawei Cloud) dork set generated (dry-run); live sweep is the Shodan/Playwright lane, deferred.
- **VisorAgent**: list mode, vector catalog shown; not fired at the survey set (ethical-stop, controlled targets only).
- **VisorGoose / VisorPlus / VisorRAG / VisorCorpus**: gov/edu-CT discovery, orchestrator, and LLM-target tools respectively; the survey targets are control-plane infrastructure (substrate, not an LLM endpoint), so no in-scope target. Recorded, not silently skipped.
- **JS-bundle extraction**: the consoles (Kiali, Hubble UI) are standard OSS SPAs, not custom CDN-fronted `api.<brand>` apps, so there is no hidden backend host or env.js secret to mine (Insight #19 targets custom SPAs). N/A with reason.
- **VisorHollow**: not applicable, Windows-only.
