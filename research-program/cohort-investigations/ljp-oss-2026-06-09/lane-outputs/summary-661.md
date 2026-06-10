# DCWF 661 R&D Specialist + DCWF 511 Cyber Defense Analyst
## JS Bundle + WebSocket Deep-Code Surface — LJP-OSS Cohort (491 hosts)

**Outfit:** jsbundle-ws-deep-analysis-661  
**Cohort:** ~/syllabus/cohort-megaset.txt (n=491)  
**Probes:** ports 8080 / 443 / 8000, root + each `<script src>` JS bundle + companion `.map`  
**Constraint:** READ-ONLY GETs; 2 MB cap per bundle/map; 12-worker pool  
**Raw artifact:** `check-661-jsbundle-ws.jsonl`  

> Research-engineering deep code analysis of JS bundle + WebSocket endpoint surface across 424 responsive cohort hosts (of 491 probed) identified **zero** code-level references to sensitive customer-side organizations (.gov / .edu / .mil / .bank / hospital / federal / defense / Ivy / top-bank substring catalog). Forensic footprint per K0268: every harvested identifier is catalogued below regardless of sensitivity classification.

## Coverage

| Metric | Value |
|---|---|
| IPs probed | 491 |
| IPs responsive on any of 8080/443/8000 | 424 (86.4%) |
| IPs with >=1 successful JS bundle fetch | 351 |
| IPs with >=1 successful sourcemap fetch | 343 |
| Total JS bundles fetched (across ports) | 471 |
| Total sourcemaps fetched | 403 |

## Per-check hit counts

| Check | Lane | Hits (cohort-wide unique values) | Hits (host-instance) |
|---|---|---|---|
| 6.a | GitHub owner/repo refs | 74 | 82 |
| 6.b | Embedded API tenant IDs | 0 | 0 |
| 6.c | Hardcoded upstream LLM provider URLs | 1 | 1 |
| 6.d | Absolute build-time path leaks | 2 | 2 |
| 6.e | Email addresses in code/comments | 22 | 27 |
| 6.f | Secret-key signatures (sk-/AKIA/ghp_/AIza/xox*/sk-ant-) | 0 | 0 |
| 8.a | wss:// / ws:// URLs | 0 | 0 |
| -- | Customer-attributable sensitive-substring hits | 0 | 0 |

## Sensitive-substring hits (verbatim)

**Zero hits.** No .gov / .edu / .mil / .bank / hospital / federal / defense / Ivy / top-bank substrings were found in any harvested JS bundle, sourcemap, SPA HTML, WebSocket URL, or embedded comment across the 424 responsive hosts.

Interpretation per DCWF 511 voice: absence of customer-side strings in operator client-bundles is a *consistent* posture for OSS-product hosts in this cohort — the bundle is shipped by the project, not regenerated per customer. Customer attribution on this cohort surfaces in upstream API traffic and ingress hostnames, not in client-bundle code. The probe did not find code-level provenance bridging operator -> sensitive customer.

## Operator code provenance — GitHub repos referenced in JS bundles (K0268)

Unique (owner, repo) pairs surfaced across the cohort: **74**. Per K0268, every footprint is catalogued.

| # | owner/repo | host_count | example IP |
|---|---|---|---|
| 1 | `zloirock/core-js` | 4 | `115.159.195.20` |
| 2 | `vuejs/vue-next` | 3 | `116.198.232.131` |
| 3 | `pmndrs/zustand` | 2 | `23.95.72.50` |
| 4 | `remarkjs/react-markdown` | 2 | `23.95.72.50` |
| 5 | `syntax-tree/hast-util-to-jsx-runtime` | 2 | `23.95.72.50` |
| 6 | `Architec-Ton/wallet-tma` | 1 | `51.79.49.219` |
| 7 | `BuilderPulse/BuilderPulse` | 1 | `47.253.151.35` |
| 8 | `Jarred-Sumner/bun` | 1 | `38.49.212.156` |
| 9 | `OpenProduct/openmask-extension` | 1 | `51.79.49.219` |
| 10 | `SillyTavern/SillyTavern` | 1 | `82.158.91.77` |
| 11 | `SubConv/SubConv` | 1 | `64.186.251.131` |
| 12 | `ajaxorg/ace` | 1 | `23.95.72.50` |
| 13 | `angular/angular` | 1 | `38.49.212.156` |
| 14 | `angular/zone.js` | 1 | `38.49.212.156` |
| 15 | `babel/babel` | 1 | `47.89.248.24` |
| 16 | `bestiejs/punycode.js` | 1 | `38.49.212.156` |
| 17 | `bitgetwallet/download` | 1 | `51.79.49.219` |
| 18 | `bybit-web3/bybit-web3.github.io` | 1 | `51.79.49.219` |
| 19 | `crypto-browserify/crypto-browserify` | 1 | `43.165.167.176` |
| 20 | `cujojs/when` | 1 | `108.171.195.153` |
| 21 | `date-fns/date-fns` | 1 | `43.129.174.14` |
| 22 | `dcastil/tailwind-merge` | 1 | `67.230.176.252` |
| 23 | `delab-team/manifests-images` | 1 | `51.79.49.219` |
| 24 | `denoland/deno` | 1 | `38.49.212.156` |
| 25 | `dominictarr/hashlru` | 1 | `67.230.176.252` |
| 26 | `element-plus/element-plus` | 1 | `116.198.232.131` |
| 27 | `es-shims/es5-shim` | 1 | `38.49.212.156` |
| 28 | `farion1231/cc-switch` | 1 | `45.207.207.34` |
| 29 | `fatedier/frp` | 1 | `193.123.184.151` |
| 30 | `feross/ieee754` | 1 | `38.49.212.156` |
| 31 | `fintopio/ton-pub` | 1 | `51.79.49.219` |
| 32 | `go-gitea/gitea` | 1 | `193.177.221.237` |
| 33 | `gridstack/gridstack.js` | 1 | `108.171.195.153` |
| 34 | `hot-dao/media` | 1 | `51.79.49.219` |
| 35 | `iamkun/dayjs` | 1 | `43.110.41.162` |
| 36 | `jonschlinkert/is-plain-object` | 1 | `51.79.49.219` |
| 37 | `jrburke/requirejs` | 1 | `23.95.72.50` |
| 38 | `kitcambridge/es5-shim` | 1 | `38.49.212.156` |
| 39 | `labring/FastGPT` | 1 | `43.165.167.176` |
| 40 | `lukeed/clsx` | 1 | `67.230.176.252` |
| 41 | `m13253/libWinTF8` | 1 | `108.171.195.153` |
| 42 | `markedjs/marked` | 1 | `193.177.221.237` |
| 43 | `mathiasbynens/String.prototype.at` | 1 | `38.49.212.156` |
| 44 | `mozilla/rhino` | 1 | `38.49.212.156` |
| 45 | `mui/mui-x` | 1 | `43.110.41.162` |
| 46 | `nodejs/node` | 1 | `38.49.212.156` |
| 47 | `onidev1/tc-assets` | 1 | `51.79.49.219` |
| 48 | `oven-sh/bun` | 1 | `38.49.212.156` |
| 49 | `qianfree/team-api` | 1 | `42.193.158.252` |
| 50 | `salesforce/lwc` | 1 | `38.49.212.156` |
| 51 | `samanhappy/mcphub` | 1 | `67.230.176.252` |
| 52 | `stefanpenner/es6-promise` | 1 | `108.171.195.153` |
| 53 | `tailwindlabs/tailwindcss` | 1 | `67.230.176.252` |
| 54 | `tailwindlabs/tailwindcss.com` | 1 | `67.230.176.252` |
| 55 | `tc39/ecma262` | 1 | `38.49.212.156` |
| 56 | `tc39/proposal-array-filtering` | 1 | `38.49.212.156` |
| 57 | `tc39/proposal-array-find-from-last` | 1 | `38.49.212.156` |
| 58 | `tc39/proposal-array-from-async` | 1 | `38.49.212.156` |
| 59 | `tc39/proposal-arraybuffer-base64` | 1 | `38.49.212.156` |
| 60 | `tc39/proposal-async-explicit-resource-management` | 1 | `38.49.212.156` |
| 61 | `tc39/proposal-async-iterator-helpers` | 1 | `38.49.212.156` |
| 62 | `tc39/proposal-change-array-by-copy` | 1 | `38.49.212.156` |
| 63 | `tc39/proposal-explicit-resource-management` | 1 | `38.49.212.156` |
| 64 | `tc39/proposal-iterator-sequencing` | 1 | `38.49.212.156` |
| 65 | `tc39/proposal-json-parse-with-source` | 1 | `38.49.212.156` |
| 66 | `tc39/proposal-math-sum` | 1 | `38.49.212.156` |
| 67 | `tc39/proposal-set-methods` | 1 | `38.49.212.156` |
| 68 | `tc39/proposal-upsert` | 1 | `38.49.212.156` |
| 69 | `tc39/proposal-well-formed-stringify` | 1 | `38.49.212.156` |
| 70 | `ton-connect/docs` | 1 | `51.79.49.219` |
| 71 | `ton-connect/sdk` | 1 | `51.79.49.219` |
| 72 | `uuidjs/uuid` | 1 | `51.79.49.219` |
| 73 | `whatwg/html` | 1 | `38.49.212.156` |
| 74 | `whatwg/url` | 1 | `38.49.212.156` |

## Embedded API tenant IDs (pooled-account attribution surface)

**No embedded API tenant IDs surfaced.** No `openai_org_id` / `org-...` / `anthropic_workspace` / `azure_tenant_id` / `gcp_project_id` / `aws_account_id` / `hf_org` literal patterns matched in any responsive operator's client bundle. This is consistent with the LJP-OSS posture: the SPA forwards tenant identification through the API path, not as a build-time literal.

## Hardcoded upstream LLM provider URLs

Unique URLs: **1**.

| # | URL | host_count |
|---|---|---|
| 1 | `https://api.openai.com/v1` | 1 |

## Check 8 — WebSocket / SSE endpoint surface

**Zero wss:// / ws:// URL literals surfaced** in any responsive operator's JS bundle, SPA HTML, or sourcemap across the 424 responsive hosts. No `new WebSocket(...)` constructor with a literal URL argument was observed at populated cohort density.

Voice-of-DCWF-661 interpretation: the LJP gateway frontend speaks HTTP for the chat-completion call; long-poll / SSE is the streaming primitive (when present), not WebSocket. This means the WebSocket-borne attack surface (sub-protocol negotiation, persistent-connection state leakage) is materially smaller than in alt-architectures like an agent-control-plane SPA.

## Build-time absolute path leaks (K0268 forensic footprint)

Unique absolute paths: **2**.

| # | path | host_count | example IP |
|---|---|---|---|
| 1 | `/home/index.vue` | 1 | `150.158.39.118` |
| 2 | `/home/screen-entry.png` | 1 | `150.158.39.118` |

## Email addresses observed in bundle / SPA HTML / sourcemaps

Unique addresses: **22**. Per K0268, every match is catalogued. Interpretation: most entries are *placeholder strings* (`example@*`, `your@email.com`, `name@company.com`, `user1@outlook.com`) shipped in UI templates, and a handful (`t@click.stop`, `t@keyup.enter.native`) are Vue/Element-Plus event-modifier directives mis-matched by the email regex — NOT operator contact addresses. Real operator-attributable emails (e.g. `luke.edwards05@gmail.com`, `monyone.teihen@gmail.com`, `zhaoqsnyah@gmail.com`, `xqq@xqq.im`) appear inside upstream OSS library source maps (`@author` / `Copyright` comments), identifying the *library author*, not the cohort host's operator.

| # | address | host_count | example IP |
|---|---|---|---|
| 1 | `example@outlook.com` | 4 | `199.47.241.65` |
| 2 | `example@hotmail.com` | 2 | `203.88.120.193` |
| 3 | `xxx@laoudo.com` | 2 | `203.88.120.193` |
| 4 | `admin@sub2api.local` | 1 | `152.53.91.69` |
| 5 | `bp@coojoy.cn` | 1 | `47.93.89.19` |
| 6 | `ccaihub@outlook.com` | 1 | `72.249.207.93` |
| 7 | `luke.edwards05@gmail.com` | 1 | `67.230.176.252` |
| 8 | `monyone.teihen@gmail.com` | 1 | `108.171.195.153` |
| 9 | `msdn0303@gmail.com` | 1 | `115.159.195.20` |
| 10 | `name@company.com` | 1 | `198.44.177.33` |
| 11 | `t@click.prevent.stop` | 1 | `150.158.39.118` |
| 12 | `t@click.stop` | 1 | `150.158.39.118` |
| 13 | `t@click.stop.prevent` | 1 | `150.158.39.118` |
| 14 | `t@contextmenu.prevent.native` | 1 | `150.158.39.118` |
| 15 | `t@keydown.delete` | 1 | `150.158.39.118` |
| 16 | `t@keyup.enter.native` | 1 | `150.158.39.118` |
| 17 | `t@keyup.enter.native.stop` | 1 | `150.158.39.118` |
| 18 | `user1@outlook.com` | 1 | `199.47.241.65` |
| 19 | `user2@outlook.com` | 1 | `199.47.241.65` |
| 20 | `xqq@xqq.im` | 1 | `108.171.195.153` |
| 21 | `your@email.com` | 1 | `178.22.30.80` |
| 22 | `zhaoqsnyah@gmail.com` | 1 | `143.198.152.233` |

## Secret-key signature surface (NOT validated — passive footprint)

**No secret-key signatures** (sk-... / sk-ant-... / ghp_... / AKIA... / AIza... / xox*-...) observed in any client bundle across the cohort.

DCWF 511 voice: this is what an OSS gateway SHOULD look like — secrets live server-side, not in the SPA. The fact that this null result is reproducible across 424 responsive hosts at this scale is itself a publishable observation.

## Methodology + restraint

- All probes were unauthenticated GETs against root + linked JS bundles + companion `.map` files.
- Bodies capped at 2 MB per fetch; per-host bundle cap = 6; per-port HTML cap = 256 KB.
- Secret-key signatures were *fingerprinted by regex*, never validated against any provider API.
- Email addresses are surfaced as forensic footprint (K0268), not contacted.
- GitHub owner/repo strings are surfaced as code provenance (T0064), not navigated.
- Sensitive-substring catalog (cohort gap-check standard): `.gov` `.edu` `.mil` `.bank`, hospital/healthcare/university/college, federal/defense/nasa/naval/military, Harvard/MIT/Stanford/Berkeley/Princeton/Yale/Columbia/Cornell/Caltech, NIH/NASA/DOD/Navy/Army/AirForce/USA.gov/CMS/healthcare.gov, Wells Fargo/Chase/JPMorgan/BofA/Capital One/Citi.

## Closing posture

- **Check 6 (JS bundle deep-code):** the LJP-OSS cohort's client bundles do not leak customer-side sensitive identifiers. Operator GitHub provenance IS leaked (Vite/webpack chunk-name comments, vendor links, source-map `sources[]` arrays) — catalogued above as forensic footprint.
- **Check 8 (WebSocket / SSE):** WebSocket URL literals are not a meaningful surface for this product class at this cohort. SSE/EventSource is the streaming primitive when present and was scanned identically.
- **Sensitive customer attribution:** zero hits. Customer attribution on this cohort surfaces through TLS-SAN / cert-CN / favicon and ingress hostnames, not through client-bundle code. The DCWF 661+511 lane confirms the absence and locates the next probe avenue for downstream gap-check outfits.
- **Notable operator GitHub repos identified inside cohort bundles** (not just OSS libraries — these point at the cohort host's product identity): `labring/FastGPT` (one host runs the FastGPT SPA), `samanhappy/mcphub` (an MCP-hub frontend), `SillyTavern/SillyTavern`, `BuilderPulse/BuilderPulse`, `qianfree/team-api`, `farion1231/cc-switch`, `fatedier/frp` (operator exposed an FRP tunnel admin UI), `go-gitea/gitea` (operator runs Gitea on the same host). These are the load-bearing provenance findings for next-stage fingerprinting.
