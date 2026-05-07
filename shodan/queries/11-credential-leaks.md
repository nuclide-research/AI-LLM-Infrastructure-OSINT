# 11. Credential Leaks & Misconfigs

_Section verified: April 2026_

The high-impact category. Exposed environment files and provider keys collapse the attack chain from "exposed service" to "full provider account takeover" in a single step.

## Exposed API Keys

| Shodan Query | Notes |
|---|---|
| `"OPENAI_API_KEY" port:8000` | Env var leaked in banner/error page |
| `"sk-" "openai" port:3000` | OpenAI classic key format |
| `"sk-proj" port:3000 OR port:8000` | OpenAI project keys (newer format) |
| `"ANTHROPIC_API_KEY"` | Env-var name form |
| `"sk-ant-" -site:anthropic.com` | Raw Anthropic key prefix, catches leaks where the env var name was stripped |
| `"sk-ant-api03-"` | Anthropic v3 key format, narrower regex |
| `http.html:"MISTRAL_API_KEY"` | Mistral env var leaked in page body |
| `http.html:"DEEPSEEK_API_KEY"` | DeepSeek env var, frequent in 2026 self-hosted stacks |
| `"gsk_" OR "GROQ_API_KEY" port:8000` | Groq API keys (fast-growing in 2026) |
| `"AIzaSy" OR "GOOGLE_API_KEY" "generativelanguage"` | Gemini / Google AI keys |
| `"hf_" OR "HF_TOKEN" port:8080` | Hugging Face token |
| `".env" "API_KEY" port:8000` | Exposed .env file |
| `http.html:".env" ("OPENAI" OR "ANTHROPIC" OR "GROQ")` | .env files leaking multiple providers |
| `".claude/settings.json"` | Claude Code project config, reveals enabled MCP servers, hooks, allowed tools; pivots to §10 |

**Reporting note:** Keys surfaced via Shodan are already exposed to the index and to anyone who paid for a Shodan subscription. Rotation is the fix; reporting to the key owner is the disclosure. Do not test the key against the provider API, that crosses the line from passive recon into credentialed access.
