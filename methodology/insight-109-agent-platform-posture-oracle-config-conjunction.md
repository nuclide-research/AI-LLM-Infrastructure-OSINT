---
type: methodology
insight_number: 109
title: "Agent-platform posture oracle: one unauthenticated settings read self-reports identity AND the full severity vector, and severity is a config CONJUNCTION (code-act-agent AND confirmation_mode=false AND security_analyzer=null) not the auth binary, which saturates at 100% on a no-auth-default OSS mode"
status: candidate
codified: 2026-06-20
source_survey: OpenHands fleet fan 2026-06-20 (ai-llm-redteam-operator platform OpenHands, N=59, 58 live, 0 FP)
falsifiability_tier: high
falsified_by: an agent platform whose unauthenticated settings endpoint does NOT report the gating config (confirmation_mode / analyzer / agent class) - i.e. the posture oracle leaks identity but not severity, forcing a second authenticated probe to score the host. OpenHands reports all of it; a platform that splits identity and severity across an auth boundary breaks the one-read property.
related_insights: [16, 40, 52, 62, 63, 68, 72, 74]
---

# Insight #109 - Agent-platform posture oracle and the config-conjunction severity rule

## The pattern

For the agent-platform exposure class (OpenHands and its siblings), a SINGLE
unauthenticated read of the settings endpoint returns both halves of the
assessment at once:

- **identity** (the schema is vendor-unique: `APP_MODE`, `llm_base_url`,
  `confirmation_mode` keys only OpenHands' serializer emits), and
- **the complete severity vector** - auth mode, agent capability class, the
  action-gating config, the upstream model backend, and provider-key state.

`GET /api/settings` + `GET /api/options/config` together are a *posture oracle*:
they collapse Discover -> Fingerprint -> Verify -> Classify into one response for
this platform class. You do not probe a second time to score the host; the host
scores itself in the body it hands an anonymous client.

Two consequences, and the second is the load-bearing one:

1. **Auth-on-default is total, so it cannot be the discriminator.** Every live
   instance ran `APP_MODE=oss` (single-user OSS mode, no login). 58/58, 100%.
   A binary "is it authenticated" saturates and ranks nothing.

2. **Severity is a CONJUNCTION of config states, not the auth bit.** The
   dangerous tier is the host where `agent == CodeActAgent` AND
   `confirmation_mode == false` AND `security_analyzer == null` - an
   unauthenticated, ungated, code-execution-capable agent. That conjunction split
   the fleet almost exactly in half (29/58, 50.0%). The other half is open but
   gated (confirmation prompt on) or analyzed (guardrail set) or non-code agent.
   The auth bit is table stakes; the config conjunction is the finding.

## The discriminating principle

When a platform's exposure is an *agent*, not a *data store*, the question is not
"can I read it" but "what will it DO unauthenticated." The settings body answers
that directly:

- An exposed vector DB leaks DATA - you then probe for the data tier (#60).
- An exposed agent IS unauthenticated code execution (when ungated) AND a
  self-documented pivot: `settings.llm_base_url` NAMES the next hop. 1-in-6 of the
  fleet (9/58, 15.5%) pointed at an internal runtime (`192.168.20.210:11434`,
  `172.17.0.1:18000`, `host.docker.internal`, a bare `vllm:8000` service name).
  The public agent is a labeled bridge into the operator's own network; the
  platform leaks its internal topology in its own settings.
- 1-in-10 (6/58, 10.3%) also had a provider API key SET (`claude-3-5-sonnet`,
  `gemini-1.5-pro`), making the open instance a free-inference / llmjacking
  surface (Insight #39 family) on top of everything else.

The severity vector is read for free in the same byte stream that established
identity. That is why the verification-rung/breadth grid (#68) needs an
agent-platform refinement: BREADTH here is a config bit-vector the host reports,
not an extra probe you have to earn.

## The OpenHands posture-oracle fingerprint (concrete)

```
# IDENTITY + AUTH MODE (one read):
GET /api/options/config  ->  body contains "APP_MODE"
                             "oss"  == single-user, NO login (the no-auth default)

# SEVERITY VECTOR (one read, anonymous):
GET /api/settings  ->  agent             : CodeActAgent  = code-exec-capable ceiling
                       confirmation_mode : false         = no human gate on actions
                       security_analyzer : null          = no guardrail
                       llm_base_url      : <host:port>   = upstream backend (internal => pivot label)
                       llm_api_key       : <set?>        = llmjacking surface if set
                       language          : <locale>      = operator attribution hint

# CAPABILITY ENUM (confirms code-exec ceiling):
GET /api/options/agents  ->  list contains "CodeActAgent"

# DATA LEG (existence only, content NOT opened - restraint):
GET /api/conversations   ->  results[] length = recoverable agent history count

# CATCH-ALL GUARD (Insight #108): anchor every signal on a JSON field token
# (APP_MODE / llm_base_url / CodeActAgent), NEVER a bare 200. The OpenHands SPA
# returns 200 for unknown /api paths; /config.json returns the React index as
# text/html 200. A bare-200 signal false-confirms; a field-token signal does not.
```

Severity tiers (config conjunction, NOT the auth bit):
- **critical-class ceiling (config-proven, NOT exercised):** `oss` AND `CodeActAgent` AND `confirmation_mode=false` AND `security_analyzer=null`.
- **high:** `oss` open control plane + settings leak (always true here).
- **+high:** provider key set (llmjacking).
- **+medium:** internal `llm_base_url` (topology leak / pivot) or stored conversations present.

## Empirical founding case - OpenHands fleet fan 2026-06-20

Tool: `ai-llm-redteam-operator` v0.2.0, `platform OpenHands` focus (committed
`bcc3a5c`). Live, read-only, 7 GET/host, no writes, no LLM egress. N=59 probed.

```
live OpenHands ............................. 58 / 59   (98.3%)   1 dead, 0 false-positive
APP_MODE=oss, NO login ..................... 58 / 58   (100.0%)  <- auth binary saturates
CodeActAgent (code-exec-capable) ........... 55 / 58   ( 94.8%)
confirmation_mode=false (no action gate) ... 46 / 58   ( 79.3%)
security_analyzer null (no guardrail) ...... 37 / 58   ( 63.8%)
>> UNAUTH CODE-EXEC CEILING (3-way conj) ... 29 / 58   ( 50.0%)  <- the discriminator
internal llm_base_url (pivot label) ......... 9 / 58   ( 15.5%)
public  llm_base_url (2nd-hop target) ...... 15 / 58   ( 25.9%)
provider key SET (llmjacking) ............... 6 / 58   ( 10.3%)
stored conversations present (>0) .......... 15 / 58   ( 25.9%)
```

- **0 false-positives across 58** - the field-token signal design (Insight #108)
  held: `/config.json` returned SPA HTML 200 on every host and produced no finding
  because no signal keyed on a bare 200.
- **Not a deception fleet** (Insight #107 check): backends, models, analyzer
  states, and conversation counts vary widely and coherently (deepseek / nvidia /
  groq / moonshot / claude / gemini / internal ollama+vllm; conv 0..5). A poisoning
  fleet is uniform; this is genuine deployment diversity. The 100% `oss` is the
  platform default, not an echo.
- Illustrative host (the founding pick, Nick-chosen): `101.200.124.170:3000` -
  `oss` + `CodeActAgent` + `confirmation_mode=false` + `analyzer=null`, wired to
  internal Ollama `http://192.168.20.210:11434/v1`. The public agent is the bridge
  to a runtime that is not itself internet-reachable. Code-exec ceiling
  config-proven; NOT exercised (restraint - hard-proof rule).

## Why this counters and connects prior insights

- **#40 (auth-on-default shifts rightward in successor generations)** - OpenHands
  is the COUNTER-case, and #109 explains why. #40 says disclosure pressure hardens
  OSS auth defaults over generations. OpenHands is current, heavily covered, and
  STILL ships `APP_MODE=oss` (no auth) as its default single-user mode; 100% of
  public deployments inherit it. The escape hatch is the **mode split**: the
  platform "supports auth" (a SaaS mode exists) so it can claim hardening, while
  the default mode operators actually run is no-auth. #40's rightward shift is
  defeated by a platform that ships BOTH a hardened mode and a no-auth default and
  lets the operator pick the no-auth one by doing nothing.
- **#72 (ships auth but default-open registration)** - #109 is the agent-layer
  member of the same family: auth EXISTS in the product but the default
  deployment is open. #72 was open registration; #109 is open-by-mode.
- **#63 (install-experience predicts auth-posture)** - strongly confirmed.
  `APP_MODE=oss` is the zero-config local-dev default; the install experience IS
  no-auth, and the fleet posture is the install default published to the internet.
- **#62 (ai-agent-service-colocation compound surface)** and **#74 (gateway as
  master-key multiplier)** - #109 is the agent-platform multiplier: one open agent
  = code-exec ceiling + internal-backend pivot + key abuse + history recovery, and
  its OWN settings names the next hop.
- **#16 / #52 (a 200 is identity not auth state; a 200 at an API path is not that
  API)** - #109's posture oracle is read THROUGH these: the catch-all 200 is
  ignored, the JSON field tokens carry identity AND severity.
- **#68 (verification-rung / depth x breadth grid)** - agent-platform refinement:
  breadth is a config bit-vector the host self-reports in one read, so high-breadth
  classification costs no extra probe. Depth (exercising code-exec) is the rung we
  deliberately do NOT climb (restraint).

## How to apply (generalizes past OpenHands)

1. **For every agent platform, identify its posture-oracle endpoint** - the
   unauthenticated settings/config read that self-reports identity AND the gating
   config. Encode it in the tome platform JSON and the aimap fingerprint as the
   primary enumerator. Find the field names in source (Insight #11).

2. **Score severity as a config conjunction, not the auth bit.** When auth-off
   saturates (it will, for OSS-default agent platforms), the auth bit ranks
   nothing. The ranking signal is the stacked gating config (agent capability AND
   action-gate AND guardrail). Report the conjunction percentage, not just "% open."

3. **Treat `llm_base_url` as a pivot label, not a field.** An internal value is a
   self-documented next hop and an internal-topology leak. Record it; do NOT call
   it (restraint - the pivot is the finding, exercising it is not).

4. **Anchor signals on JSON field tokens, never bare 200 (Insight #108).** Agent
   SPAs catch-all 200 unknown paths; only a vendor-unique field token survives.

5. **Climb breadth for free, refuse depth by choice (Insight #68).** The posture
   oracle hands you full breadth in one read. The code-exec ceiling is
   config-PROVEN; do not exercise it. "Surface open, code-exec not exercised."

## Falsifiability

Falsified if an agent platform's unauthenticated endpoint reports identity but
NOT the gating config - i.e. severity sits behind an auth boundary and the
one-read posture-oracle property fails. Re-test on the next agent-platform survey
(Flowise, Langflow, a Dify/AutoGPT-class target): does one anonymous read yield
the full severity vector, or only identity? If only identity, #109 is
OpenHands-specific, not a class property, and downgrades to a platform note.

Also worth re-checking: does the OpenHands 50% code-exec-ceiling rate move on a
later survey? A drop would be evidence for #40 finally reaching this platform
(disclosure pressure flipping the default); a hold or rise extends the #40
counter-case.

## See also

- `ai-llm-redteam-operator` `platform OpenHands` focus (commit `bcc3a5c`) - the tool that fired the fan
- OpenHands fleet fan 2026-06-20 evidence (local, gitignored corpus): per-host JSON ledgers + posture census + findings-breakdown
- `insight-108-positive-anchor-negative-catchall-fingerprint-pair.md` - the catch-all-safe signal design this fan used at scale
- `insight-40-auth-on-default-shifts-rightward-in-successor-generations.md` - the trend #109 counters
- `insight-72-ships-auth-but-default-open-registration.md` - the ships-auth-but-default-open sibling
- `insight-63-install-experience-predicts-auth-posture.md` - the install-default-is-posture confirmation
- `insight-68-verification-rungs-claim-ladder.md` - the depth x breadth grid this refines for agent platforms

---

_Status: CANDIDATE. Promotion pending one additional agent-platform survey that
either confirms the one-read posture-oracle property generalizes (a second
platform self-reports its full severity vector to an anonymous client) OR
establishes it as OpenHands-specific. Cite OpenHands fleet fan 2026-06-20 (N=58
live, 100% oss, 50% code-exec ceiling, 0 FP) as the founding evidence._
