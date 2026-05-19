# 26. Exfiltrated Credentials in HTML

_Section created: 2026-05-19. Companion to [methodology Insight #38](../../methodology/insight-38-exfiltrated-credential-hard-proof-chain.md): the six-step verification chain for credentials exposed in public HTML._

This section is the **Step 1 dork catalog** for the chain. Each entry is a vendor-specific credential-prefix dork. Subsequent chain steps (re-fetch, format-validate, verify, attribute, content-verify) are handled by `~/recon/tools/exfil_cred_verify.py`.

## Methodology note

Per [Insight #6](../../methodology/insight-06-conjunctive-matchers-required.md), short prefixes (e.g. bare `sk-`) need co-anchoring to avoid substring FPs. Where a vendor's prefix is unique (Langfuse `sk-lf-`, Helicone `sk-helicone-`, Anthropic `sk-ant-api03-`), the prefix alone is precise enough. Where the prefix is generic (OpenAI `sk-`, Slack `xoxb-`), combine with a co-anchor token.

Per [Insight #38](../../methodology/insight-38-exfiltrated-credential-hard-proof-chain.md), a Step-1 hit alone is INFO tier. Promotion to higher tiers requires the remaining steps. A dork-hit count is candidate population; verified-live-credential count is the actual finding.

## Langfuse

| Dork | Notes |
|---|---|
| `http.html:"sk-lf-"` | Langfuse secret key prefix. Vendor-unique format `sk-lf-{uuid}`. Verified 2026-05-19: 3 hits, 1 confirmed live + critical PII content. |
| `http.html:"pk-lf-"` | Paired public key. Often appears alongside sk-lf- in the same body. |
| `http.html:"LANGFUSE_SECRET_KEY"` | Env-var leak class. PaaS build-arg pattern per [Insight #36](../../methodology/insight-36-paas-build-arg-secret-baking.md). |
| `http.html:"LANGFUSE_PUBLIC_KEY"` | Env-var paired with secret. |
| `http.html:"sk-lf-" "us.cloud.langfuse.com"` | Co-anchored with cloud-US endpoint. |
| `http.html:"sk-lf-" "cloud.langfuse.com"` | Co-anchored with cloud endpoint. |

## Helicone

| Dork | Notes |
|---|---|
| `http.html:"sk-helicone-"` | Helicone API key prefix. Vendor-unique. |
| `http.html:"Helicone-Auth"` | Header name in request examples. |

## Stripe

| Dork | Notes |
|---|---|
| `http.html:"pk_live_"` | Stripe live publishable key. Public-by-design but useful for operator attribution. |
| `http.html:"sk_live_"` | Stripe live SECRET key. Critical-tier if found. |
| `http.html:"pk_test_"` | Stripe test publishable key. Lower severity but still operator attribution. |
| `http.html:"sk_test_"` | Stripe test secret key. Confirms test-environment exposure. |
| `http.html:"sk_live_" "pk_live_"` | Both keys co-present; full live-Stripe credential pair. |

## Anthropic

| Dork | Notes |
|---|---|
| `http.html:"sk-ant-api03-"` | Anthropic API key prefix (current versioning). |
| `http.html:"ANTHROPIC_API_KEY=sk-ant"` | Env-var with prefix co-anchor. |

## OpenAI

OpenAI's `sk-` prefix is too broad; needs co-anchoring.

| Dork | Notes |
|---|---|
| `http.html:"OPENAI_API_KEY=sk-"` | Env-var co-anchored with prefix. |
| `http.html:"sk-proj-" "openai"` | OpenAI's newer project-scoped key prefix. |
| `http.html:"sk-svcacct-" "openai"` | Service-account key prefix. |

## GitHub

| Dork | Notes |
|---|---|
| `http.html:"ghp_"` | GitHub personal access token. |
| `http.html:"gho_"` | GitHub OAuth token. |
| `http.html:"ghu_"` | GitHub user-to-server token. |
| `http.html:"ghs_"` | GitHub server-to-server token. |
| `http.html:"ghr_"` | GitHub refresh token. |
| `http.html:"GITHUB_TOKEN=ghp_"` | Env-var with prefix. |

## GitLab

| Dork | Notes |
|---|---|
| `http.html:"glpat-"` | GitLab personal access token prefix. |
| `http.html:"GITLAB_TOKEN=glpat-"` | Env-var with prefix. |

## AWS

| Dork | Notes |
|---|---|
| `http.html:"AKIA"` | AWS access key ID prefix. **Very high FP** (matches any string with AKIA). Co-anchor with `AWS_SECRET_ACCESS_KEY` for precision. |
| `http.html:"AKIA" "AWS_SECRET_ACCESS_KEY"` | Co-anchored access + secret. |
| `http.html:"AKIAIOSFODNN7EXAMPLE"` | The docs-example key. Filter OUT of any survey. |
| `http.html:"AWS_SECRET_ACCESS_KEY=" "AKIA"` | Env-var with both fields. Field-verified 2026-05-19: 710 hits on broader env_aws_key dork. |

## Slack

| Dork | Notes |
|---|---|
| `http.html:"xoxb-"` | Slack bot token prefix. |
| `http.html:"xoxp-"` | Slack user token prefix. |
| `http.html:"xapp-"` | Slack app-level token prefix. |
| `http.html:"xoxe-"` | Slack refresh token prefix. |

## SendGrid / Twilio / Mailgun

| Dork | Notes |
|---|---|
| `http.html:"SG."` | SendGrid API key prefix. |
| `http.html:"SENDGRID_API_KEY=SG."` | Env-var with prefix. |
| `http.html:"SK"` (Twilio) | Twilio API SID prefix. Co-anchor with `TWILIO`. |
| `http.html:"key-"` (Mailgun) | Mailgun key prefix. Too broad alone. |
| `http.html:"MAILGUN_API_KEY=key-"` | Env-var with prefix. |

## LangSmith / LangChain

| Dork | Notes |
|---|---|
| `http.html:"LANGCHAIN_API_KEY"` | LangChain API key env-var. |
| `http.html:"LANGSMITH_API_KEY"` | LangSmith API key env-var. |
| `http.html:"lsv2_pt_"` | LangSmith personal token prefix. |
| `http.html:"lsv2_sk_"` | LangSmith service key prefix. |

## Cohere / Mistral / DeepSeek

| Dork | Notes |
|---|---|
| `http.html:"COHERE_API_KEY"` | Cohere env-var. |
| `http.html:"MISTRAL_API_KEY"` | Mistral env-var. |
| `http.html:"DEEPSEEK_API_KEY"` | DeepSeek env-var. |
| `http.html:"sk-or-v1-"` | OpenRouter key prefix. |

## Humanloop / Braintrust / Helicone (already listed) / Other LLM ops

| Dork | Notes |
|---|---|
| `http.html:"HUMANLOOP_API_KEY"` | Humanloop env-var. |
| `http.html:"BRAINTRUST_API_KEY"` | Braintrust env-var. |
| `http.html:"hl_pk_"` | Humanloop public key prefix (per vendor docs). |
| `http.html:"bt_v1_"` | Braintrust key prefix. |

## How to use this catalog

1. **Pick a vendor** whose verification path you want to test.
2. **Run the matching dork** via Shodan (or via `~/recon/tools/exfil_cred_verify.py --vendor <name> --max-step 1`).
3. **Walk the chain** (Steps 2-6) per [Insight #38](../../methodology/insight-38-exfiltrated-credential-hard-proof-chain.md). The probe tool supports `--max-step` to cap at each chain level.
4. **Add new vendor entries** when a new credential class is encountered. The catalog is meant to grow.

## See also

- [Insight #38](../../methodology/insight-38-exfiltrated-credential-hard-proof-chain.md): the methodology
- [Insight #36](../../methodology/insight-36-paas-build-arg-secret-baking.md): why credentials reach public HTML in the first place (PaaS build-arg pattern)
- [Insight #6](../../methodology/insight-06-conjunctive-matchers-required.md): conjunctive matcher discipline for short prefixes
- `~/recon/tools/exfil_cred_verify.py`: the chain-runner tool
