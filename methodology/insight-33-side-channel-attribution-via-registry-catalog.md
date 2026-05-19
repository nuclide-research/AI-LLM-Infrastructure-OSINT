---
type: methodology
insight: 33
title: Side-channel attribution via Docker registry catalog content when direct fingerprinting fails
---

# Insight #33. Side-channel attribution via Docker registry catalog content when direct fingerprinting fails

_Source: Jetson / TensorRT-edge population survey, 2026-05-18. Direct dorks for Jetson hardware (body / title `Jetson`, `Tegra`, `L4T`, `Orin`) scattered into false positives. The exposed `/v2/_catalog` on adjacent Docker registries surfaced 3 of 5 registry operators as Jetson builders with high confidence. The registry catalog is the reliable attribution vector when the direct fingerprint fails._

## The rule

When the direct fingerprint for a target class (Shodan dork on title, body, port, banner) returns mostly false positives at population scale, look for an **adjacent service the operator runs whose content reveals what the direct probe could not**. Docker Registry V2 is the canonical such service: `/v2/_catalog` lists every image the operator builds or mirrors, and image names carry the operator's intent.

Apply the rule to any class where:

1. The direct dork is noise-dominated (real-rate well under 50%).
2. The operator likely runs supporting infrastructure that is itself enumerable.
3. The supporting infrastructure's content (catalog, manifest, config, registry) is operator-authored or operator-curated.

The supporting infrastructure is the side channel. Its content is the attribution.

## Empirical basis (Jetson / TensorRT survey, 2026-05-18)

Direct Jetson fingerprinting (Stage 0 - Stage 2 chain via Shodan dorks):

| Direct dork | Candidates | Verified Jetson | False-positive class |
|---|---|---|---|
| `http.title:"Jetson"` | many | 0 | Companies named Jetson, Optum Jetson Search, Jetson Software Solutions |
| `http.html:"Tegra"` | many | 0 | Tegra Brazil / Iceland / Germany / Canada (unrelated businesses) |
| `http.html:"l4t"` | many | 0 | `lat` substring matches (latex4technics, GPON home gateways) |
| `http.html:"DGX"` | many | 0 | Personal blogs, marketing pages |
| `"Orin Nano"` / `"Jetson Orin"` | many | 0 | Minecraft Bedrock MOTDs on port 19132 |
| `ssl.cert.subject.cn:"tegra"` | many | 0 | Tegra ERP, Tegra Brazil |
| Direct hardware total | many | **0** | |

Registry-side Jetson attribution (Docker Registry `/v2/_catalog` adjacent probe):

| Registry | Direct fingerprint result | Catalog content | Jetson confidence |
|---|---|---|---|
| F1 `37.27.229.120:5000` (Hetzner FI) | unauth Docker Registry, no Jetson banner | `mfgbot/l4t-base`, `mfgbot-os/jetson/*`, `nvcr.io/nvidia/l4t-base`, aarch64 base images | **high** |
| F2 `172.245.18.104:55000` (HostPapa US) | unauth Docker Registry | `nvidia/deepstream`, `ollama/ollama` (no Jetson signal) | none |
| F3 `14.103.220.38:5000` (Volcano Engine CN) | unauth Docker Registry | `nvidia/cuda`, `nvidia/driver`, `nvidia/gpu-operator`, `nvidia/k8s/*` (x86 cluster stack) | none |
| F4 `43.133.1.147:5000` (APNIC JP) | unauth Docker Registry | `dustynv/ollama` among 39 commodity-AI repos | **high** (single signal) |
| F5 `47.93.158.253:5000` (Aliyun CN) | unauth Docker Registry | `isaac-lab-base-full`, `isaac_ros_dev-x86_64-cpp`, `auriga/ros2_dev-aarch64-cpp`, `base_chassis_navigation_arm` | **high** (medium + arch) |

Three of five registries attribute the operator as Jetson / NVIDIA edge with high confidence. None of the direct Jetson dorks produced these attributions.

## Diagnostic signals

A target class is a candidate for side-channel attribution if **any** of these fire:

1. **The direct-dork class is FP-dominated** (real-rate under 50%) and the FPs share no common discriminator (no body-marker conjunct will rescue the dork).
2. **The product runs on standard developer infrastructure** the operator is likely to also expose (registry, CI artifacts, package mirror, build cache, log aggregator).
3. **The adjacent infrastructure carries operator-authored content** (image names, branch names, commit messages, dataset names, project names). Operator-authored content is far more selective than vendor banners.

## Procedural rules this insight generates

1. **When a direct fingerprint class produces zero real findings**, do not declare the class empty. Enumerate the adjacent infrastructure (Docker Registry, GitLab, Gitea, Jenkins, Drone CI, package mirrors) on the same operator IP range or in the same dork's overlap set and run a content-based attribution pass.

2. **The aimap Docker Registry deep enumerator runs the Jetson-attribution pass by default in v1.9.12.** When the registry catalog contains any high-confidence signal (`dustynv/`, `l4t`, `jetson`, `tegra`, `jetpack`), an `operator-attribution` finding is emitted. This is the canonical implementation of the rule. Other adjacent services should follow the same pattern.

3. **Operator-authored content beats vendor banners.** A `Server: NVIDIA-something` header is an installation artifact (vendor default). A `dustynv/ollama` image name is an operator choice (the operator chose to pull and run that specific image). Operator choices attribute; vendor defaults fingerprint a product class but not an operator.

4. **Negative-path discrimination is part of the design.** Generic `nvidia/*` images (`nvidia/cuda`, `nvidia/driver`, `nvidia/gpu-operator`, `nvidia/deepstream`, `nvidia/k8s/*`) are NOT Jetson signals. They appear on x86 GPU clusters too. The fingerprint must explicitly tier these. The F2 and F3 cases in the survey exercise the negative path and confirm the discrimination.

5. **Side-channel attribution does not replace direct probing.** It supplements it. If the direct Jetson SSH banner test runs on port 22 (deferred in the 2026-05-18 survey as write-tier), it provides the strongest possible evidence (the OS image itself). The registry attribution is the next-best evidence; the registry-attributed operator very likely runs Jetson hardware, but the registry itself may be on x86.

## Relationship to prior insights

- **Insight #6 (conjunctive marker-anchored matchers)**: the rule still applies inside the catalog matcher. Single-substring matches like `body_contains: "tegra"` against a raw HTTP response would FP-bloom. The registry pass applies the matchers to the parsed `repositories` array, not the raw body, so the matcher fires only on operator-curated image names. Same conjunctive discipline, different anchor surface.
- **Insight #9 (cross-survey correlation is a Shodan-free discovery vector)**: the family this insight extends. Both rely on data the operator exposed for one reason being usable as evidence for an unrelated question. Cross-survey correlation pivots across surveys; side-channel attribution pivots across services on the same operator.
- **Insight #11 (source code is authoritative; bug reports are framing)**: the same epistemology. Operator-authored content (image name, commit, source) is authority; vendor-emitted text (banner, marketing, dork hit) is framing. Always prefer authority.
- **Insight #15 (dork hits vs platform instances)**: marker-weak dorks (title / body words) hit 28-46% real-rate. This insight is the answer to "what do you do when the direct dork is below that?" Build the side-channel.
- **Insight #20 (aimap catalog gaps)**: a procedural complement. When a class is gappy in the catalog, look for an adjacent class that is well-fingerprinted (Docker Registry) and use it to attribute.

## Open questions

- **Which other adjacent services carry attribution-grade content?** Candidates: GitLab CE / Gitea repository listings, Jenkins build history, Drone CI configs, Helm chart repos, package mirrors (APT, RPM, PyPI, NPM). Each one is a separate aimap deep-enumerator opportunity.
- **What other operator classes attribute via registry content?** Robotics is one (Isaac / ROS / aarch64 = mobile autonomous robot). What others? Healthcare: `pacs-*`, `dcm4chee`, `orthanc-*` image names. Finance: `quantlib-*`, `vector-bt-*`. Defense: classified-namespace prefixes when leaked. Each new operator class produces a new attribution pass.
- **How does this scale to the registry crawl?** Today aimap only attributes when it scans a host that runs Docker Registry. To scale to "find every Jetson operator on the public internet," a registry-first crawl is needed: harvest all `/v2/_catalog` exposures (10,000+ on Shodan), run the attribution pass over each catalog, tabulate operators by attribution class.

## See also

- `case-studies/commercial/jetson-tensorrt-edge-survey-2026-05-18.md`. The survey that produced this rule.
- `insight-09-cross-survey-correlation-discovery-vector.md`. The family this insight extends.
- `insight-11-source-code-is-authority.md`. The epistemology this insight applies.
- `insight-20-aimap-catalog-gaps.md`. The procedural complement.
- aimap v1.9.12 CHANGELOG: the canonical implementation of the rule for Jetson attribution.
