# Insight #78 — Shared deployment kits create operator-class exposure: one fingerprint, N unauth backends

**Survey:** Single-host ad-hoc assessments, xTom Japan (AS3258), 2026-06-05/06.

## Statement

When a deployment kit (a preconfigured stack template) circulates within an operator
community, every operator who deploys it inherits the same misconfiguration. The
fingerprint of the kit - version string, favicon hash, callback list, header set - is
identical across all deployments, so finding one instance immediately classifies all
others in the population. **A kit-level misconfiguration is not an individual operator
failure; it is a population-wide exposure rooted in a single upstream decision.**

## Evidence

Three unauth LiteLLM Enterprise instances found on separate xTom Japan VPS hosts operated
by independent Chinese AI API relay services within a single session:

| IP | Operator | Auth | Version | Favicon hash |
|---|---|---|---|---|
| 197.189.236.186 | Cozan Consulting (zigy.co.za) | NONE | v1.82.6 | -1875761561 |
| 103.201.131.99 | OrbitLink VPN (weee.teys.top) | NONE (historical) | v1.82.6 | -1875761561 |
| 176.126.114.133 | 曲奇 API (quqiai.top) | NONE | v1.82.6 | -1875761561 |

Shared fingerprint across all three:
- **Version:** LiteLLM Enterprise v1.82.6
- **Favicon hash:** -1875761561 (identical PNG)
- **Callback chain:** SkillsInjectionHook + _PROXY_VirtualKeyModelMaxBudgetLimiter + _PROXY_MaxBudgetLimiter + _PROXY_MaxParallelRequestsHandler_v3 + _PROXY_CacheControlCheck + ResponsesIDSecurity + _PROXY_MaxIterationsHandler + _PROXY_MaxBudgetPerSessionHandler + _PROXY_LiteLLMManagedFiles + _PROXY_LiteLLMManagedVectorStores + ServiceLogging
- **Config:** No Prisma DB, no master_key, auth=NONE on all three
- **Hosting:** All xTom Japan (AS3258)
- **Pattern:** Auth-gated commercial frontend (One API / V2Board) + unauth LiteLLM backend

The commercial frontend (One API's "曲奇 API", V2Board's OrbitLink) provides user-facing
auth and billing. The LiteLLM layer behind it is treated as an internal-only service but is
bound to all interfaces without a master_key. The kit author left auth unconfigured; every
operator who used the kit inherited the open backend.

## Mechanism

The auth-gated frontend creates a false sense of security: operators see their commercial
portal enforcing login and assume the stack is protected. The LiteLLM backend is a separate
process on a separate port - the frontend's auth does not propagate to it. Without a
`master_key` set in `litellm_config.yaml`, LiteLLM defaults to open. The kit was distributed
without that line.

This is a structural variant of Insight #02 (single-template auth-off propagates): the
template is not one operator's misconfiguration copied to their own fleet - it is a
third-party kit adopted independently by multiple operators who each made the same
assumption about the frontend providing coverage.

## Recon implication

The favicon hash (-1875761561) is a precise population selector for this kit. A Shodan
dork on `http.favicon.hash:-1875761561` will return the full population of hosts running
this kit regardless of domain, ASN, or country. The three confirmed instances are a floor,
not a ceiling. Expanding the sweep via favicon hash is the direct next step to bound the
full operator class.

The xTom Japan hosting concentration is a secondary signal - operators acquiring kit-sourced
stacks from the same Chinese AI service community appear to prefer xTom Japan as a VPS
provider. ASN + favicon hash together form a tight selector for this population.

## Implication for methodology

When a new finding has an identical fingerprint to a prior finding on a different operator:
1. Treat the match as a kit signal, not coincidence.
2. Immediately pivot to favicon hash / header hash / version string population sweep.
3. The root cause is the kit author's config, not each individual operator's negligence -
   remediation guidance should target the kit's default config, not the operator's setup.
4. Expect the full population to share the same misconfiguration unless the kit was patched
   downstream.

**The finding is: the kit is misconfigured. The population is: every operator who deployed it.**
