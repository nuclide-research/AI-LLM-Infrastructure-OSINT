# After Action Report: K8s FinOps Cost-API Survey (Kubecost / OpenCost)

**Date:** 2026-05-29
**Operator:** NuClide Research (Nicholas Kloster)
**Category:** K8s FinOps cost-allocation. Survey slice not covered by the 2026-05-19 cost/billing work.
**Posture:** Offline analysis of captured artifacts, then two gated outward steps under explicit authorization, run through Mullvad (us-lax-wg-608).

---

## 1. Bottom line up front

Sixty-seven exposed cost-model API instances were confirmed across Kubecost and OpenCost. Sixty-six of them answer their data API with no authentication. The cost API is not a billing dashboard. It is a cluster-wide reconnaissance oracle. A single unauthenticated GET returns the full namespace and workload map, the names of the security tooling running in the cluster, and a dollar-ranked list of which clusters are worth the most. All of it is read-only and free, before any secret is touched.

One outward sample then proved the chain runs further. On the kc5-aws cluster the unauthenticated `/model/helmValues` endpoint returned a live Grafana admin password in the open. The value was confirmed present and never read or stored. The chain is anonymous internet to cluster credential, with no login at any hop.

No critical label is claimed. No code execution, data write, or credential use was demonstrated. The work stopped at proof.

---

## 2. What was uncovered

**Population.** 67 confirmed instances. 50 Kubecost, 14 OpenCost, 3 vendor-undetermined. 66 unique IPs. Two of the IPs front the same cluster, so the true cluster count is slightly below the host count. Clouds: AWS 32, GCP 12, Azure 11, Alibaba 2, OVH 2, Oracle 1, plus a handful self-hosted.

**Auth.** 66 of 67 serve the cost-model API with no auth. There is no UI versus API asymmetry here. The dashboard is open and the API is open. This is not Insight #37. It is the plainer failure: the service ships with auth off and the operator put it behind a public LoadBalancer without adding a gate.

**Data exposed.** 59 hosts return full per-namespace topology and cost. Visible daily spend across the set sums to about 10,528 dollars. The largest single cluster reports 6,837 dollars per day. The namespace lists name the cluster's own defenses out loud: vault, cert-manager, falco, wiz, kyverno, gatekeeper, guardduty. An attacker reads the target's security stack before sending a single packet at it.

**Credential chain (outward, authorized, one sample).** On kc5-aws the helmValues endpoint returned the full Helm install values, 19,304 bytes, unauthenticated. Inside it: a real Grafana admin password, fourteen characters, not a placeholder or a template. The other secret-named keys were references, the names of Kubernetes secret objects and file paths to token files, not the values. So the honest read is one live inline credential, not a wholesale dump. The macchaffee-2021 helmValues leak class is still live and unpatched in the field.

**Negative result, recorded.** The co-located shadow surface sweep came back empty. Sixty-six hosts checked on Grafana 3000, node-exporter 9100, kubelet 10250, etcd 2379, and the API server 6443. Zero open. The LoadBalancer fronts only the cost service. The kubelet and etcd stay internal. Insight #62 does not hold for this population. That sharpens the finding rather than weakening it: the cost API is the only door, and it leaks the whole house.

---

## 3. The chain

1. Anonymous user finds a Kubecost host by its title on Shodan.
2. Unauthenticated GET to `/model/allocation` returns every namespace, every workload, and the running cost of each.
3. The same open API names the security tooling and ranks clusters by spend. The attacker now knows the map and the priorities.
4. Unauthenticated GET to `/model/helmValues` returns the install config, including a live Grafana admin password.
5. That password fronts Grafana, which holds datasource credentials, infrastructure dashboards, and a plugin surface. The work stopped here.

---

## 4. Insight candidate

A cost or telemetry sidecar is a higher-value reconnaissance target than the workloads it monitors, because indexing the whole cluster is its entire job. When its data API ships open, it leaks more structural intelligence than any single exposed app would. The open-API exposure itself confirms the auth-on-default thesis at FinOps scale. The recon-oracle framing is the new corollary. If the same pattern holds on Prometheus federation, OTel collectors, or Grafana datasources in a later survey, it generalizes: telemetry sidecars are cluster-wide recon oracles.

---

## 5. What worked, what failed

**Worked.** The full arsenal ran on captured data without touching a host: visorlog ingest, visorscuba scoring, BARE ranking, six analysis lanes, and an adversarial verify pass. The verify pass rejected 11 of 26 material claims and caught fabricated detail from the pre-verify framing, including a namespace that did not exist and a namespace count off by a factor of twenty. BARE confirmed the cost-API class is novel: it scored 0.547 against a 0.55 corpus-coverage line, just below known Metasploit modules. The helmValues class, by contrast, matched the Rancher and Prometheus credential-gather modules, which is the same chain we then proved by hand.

**Failed, and fixed.** The first analysis workflow crashed at the final step. A single agent was asked to write files and then return a strict schema, and it ended in prose instead of the structured call. Fix: do not put heavy file writing and a strict schema on the same terminal agent. The workflow resumed from its journal with only that one agent re-run.

**My own error.** The first helmValues pull reported zero bytes and read as inconclusive. The cause was a shell mistake, a heredoc and a piped stdin fighting over the same input, not the host. Diagnosing it instead of concluding "no secrets" is the only reason the credential was found at all.

---

## 6. Honest caveats

- helmValues content is confirmed live on one cluster only. The other 48 endpoints are confirmed open but their contents were not read. Class proven, magnitude across the set not measured.
- The snapshot is about one day old. Hosts may have closed or rotated.
- Spend ranking misfires on a few hosts. One dev cluster ranks high. One 97-namespace cluster reports zero dollars.
- Three vendors stayed undetermined offline.
- Operator attribution is still running and is not yet folded in. The strongest lead is a shared namespace taxonomy (aicore, common, sdwan, nvo, oms, xcd, msp4xiq, wips, ztna1r1) that ties at least two clusters to one SASE or networking operator.
- No critical is supportable. No exec, no data write, no credential use was demonstrated.

---

## 7. Tooling gaps found, and builds in flight

The survey surfaced real gaps because the arsenal was actually run end to end:

- **aimap** has no Kubecost/OpenCost fingerprint, which is why a bespoke probe existed. Productizing it now.
- **ns-attribute**, a namespace-to-operator clusterer, did not exist. The attribution was done by hand. Building it now and validating against this corpus.
- **visorscuba** has no FinOps policy, so it mislabeled every cost host as "Unauthenticated Ollama." Adding an FO.C1 Rego module.
- **BARE** lacks a FinOps corpus entry, leaving the class a hair below the coverage line. Filling it.
- **visorlog** drops IP metadata on deduplicated aimap records. Logged for a fix.

---

## 8. Artifacts

- `data/finops-probe-results.ndjson` (67 confirmed, the ground truth)
- `data/finops-findings-breakdown.txt`
- `data/finops-helmvalues-sample-18_224_144_23.redacted.txt` and the paired IP (redacted, no secret bodies)
- `data/finops-shadow-sweep.json` (negative adjacency result)
- `data/finops-nuclide.db` (survey-scoped ledger)
- `case-studies/commercial/kubecost-opencost-finops-cost-api-survey-2026-05-28.md`
- `data/platform-intel/kubecost-opencost-finops-osint-2026-05-28.md` (pre-assessment intel)

---

## 9. Next steps

- Land operator attribution from the platoon run and the new ns-attribute tool.
- Review the four tool builds, then decide on install and release.
- Optional read-only pivots: cert-pivot the 11 Azure tenant GUIDs to named orgs; dedup clusters before any disclosure routing; snapshot diff later to measure how fast these close on their own.
