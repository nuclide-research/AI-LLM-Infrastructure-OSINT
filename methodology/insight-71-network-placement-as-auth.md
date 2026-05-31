# Insight #71 — Network-placement-as-auth: when exposure IS the authentication failure

_Sourced to: the Network Perimeter / Service Mesh survey, 2026-05-31 (case-studies/commercial/service-mesh-survey-2026-05-31.md)._

## The lesson

The auth-on-default thesis has, until now, measured platforms that **have** an
authentication layer and ship it on or off by default (Phoenix `ENABLE_AUTH=False`
vs Langfuse no-toggle). Service-mesh introspection planes are a different and
worse class: **they have no authentication layer at all.** Their entire access
control is *network placement*: loopback bind, ClusterIP-only, a NetworkPolicy,
"do not expose this." For Kiali's anonymous strategy, Linkerd's viz dashboard and
proxy-admin, Cilium's Hubble UI / relay / metrics, and Istio's Envoy-admin and
istiod-debug, there is no credential to set, no toggle to flip. The control is the
network position, and nothing else.

For this class, **exposure is not a precondition for the auth failure. Exposure
IS the auth failure.** The moment a NodePort, LoadBalancer, hostPort, ingress
path, or container escape changes the network position, the plane is unauthenticated
to whoever can now reach it. There is no second line. This makes the unauth rate
among *exposed* instances approach 100% by construction, not by operator error:
the only way to be exposed is to have already lost the only control.

## The in-band discriminator that proves it

The survey did not assert this from theory. It carried a built-in control: the
**kube-apiserver**, reachable on public 6443 on three of the same hosts, in the
same clouds (Huawei). The apiserver has a real authentication and RBAC layer.
Under identical exposure, the discriminator split cleanly:

- Placement-only planes (Kiali anonymous): **4/4 unauthenticated** — full namespace
  topology read via `/kiali/api/namespaces`, one host leaking 479 namespaces of a
  multi-tenant chatbot platform.
- Cilium metrics: unauthenticated topology leak.
- The authn-backed plane (kube-apiserver): **3/3 held** — `/version` anonymous-readable
  (identity), `/api/v1/namespaces` anonymous **denied** by RBAC.

Same hosts, same operators, same clouds, opposite outcomes. The variable that
predicted the result was **the type of control** (network-position vs
authentication), not operator skill, cloud, or patch level. That is the same
shape as Insight #13 (shipping defaults are load-bearing), pushed one rung
deeper: here the default is not "auth off," it is "no auth exists," and the
result tracks the control architecture with even less variance.

## Corollary — the discovery signal is biased toward the console tier

Operators expose the *human-readable console* (Kiali, Hubble UI) far more than
the *machine data-plane API* (Hubble Relay 4245, the cluster-wide flow tap). The
relay was reachable on **0 of 12** Cilium hosts; the UI was exposed on 9. So a
console brand-dork (`http.title:"Kiali"`, `http.title:"Hubble UI"`) selects a
subpopulation biased toward consoles, and the deepest data plane stays both
Shodan-dark and network-internal. The measured unauth rate is therefore a
*console-tier* rate. The data-plane tier (Envoy admin 15000, istiod 15014, Linkerd
proxy-admin 4191, Hubble Relay 4245) is a separate, Shodan-undersampled population
that needs Censys full-range or tiptoe/naabu to measure. This extends the
dork-population-substitution caution: the dork does not just bias toward
DNS-configured operators, it biases toward the *tier of the stack the operator
chose to put a friendly UI on*.

**Empirically measured (2026-05-31).** Against the authenticated Shodan web UI, every
data-plane marker dork returned zero: `port:15000 "config_dump"`, `port:15014 "pilot_xds"`,
`port:4191 "proxy_build_info"`, `"hubble_flows_processed_total"`, `"cilium_drop_count_total"`.
The console titles (`http.title:"Kiali"`, `http.title:"Hubble UI"`) returned populations.
`port:4245` returned 30 hosts but is a shared port and gRPC is opaque to Shodan; grpcurl
confirmed 0 reflection-enabled Hubble Relays. The tier split is therefore a measured fact,
not an assumption: Shodan indexes the console tier and is blind to the data-plane tier,
because its crawler never issues the introspection paths (`/config_dump`, `/debug/*`,
`/metrics`) that carry the marker strings. Measuring the data-plane tier requires full-range
coverage (Censys) or active scanning (tiptoe/naabu), not brand or marker dorks.

## How to apply

1. **Classify the control before scoring the finding.** Ask "is the access control
   a credential check, or a network position?" If it is network position, then
   "exposed" and "unauthenticated" are the same fact; do not score them as two
   steps or hedge the auth state. The data-layer probe confirms reachability;
   reachability is the finding.
2. **Carry an authn-backed plane as an in-band control when one exists.** When the
   target host also runs a plane with real authn (kube-apiserver, a real login),
   probe it under the same exposure. If it holds while the placement-only planes
   fall, you have proven the control-type discriminator on that exact host, not by
   analogy.
3. **State which tier the population represents.** A console brand-dork measures the
   console tier. Say so, and log the data-plane tier (high/odd introspection ports)
   as a distinct, unmeasured population requiring full-range discovery, not as
   "absent."
4. **Restraint holds especially here.** The leak is topology (namespace names, the
   service graph, flow metadata). Names are the finding. Enumerate the metadata,
   never stream the data plane (Hubble `GetFlows`, live request bodies) to "prove"
   severity. Downgrade the claim, do not upgrade the access.

## Relationships

- Deepens **#13** (shipping defaults are load-bearing): the limiting case where the
  default is "no auth layer exists."
- Uses **#16** (a 200 is identity, not auth-state) as the verification mechanism:
  the data-layer probe (`/kiali/api/namespaces`, not `/`) is what earned the HIGH.
- Pairs with **#69** (curated-scan negative is not a host negative) and the
  dork-population-substitution caution: console-dork populations are tier-biased.
- Same tool-gap shape as the NCKU KubeSphere case: VisorScuba has no control for
  cluster-introspection planes (0/0 vacuous pass), and aimap had zero fingerprints
  for the category until this survey built nine.
