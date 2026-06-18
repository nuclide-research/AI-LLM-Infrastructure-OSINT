# LightRAG /health config-disclosure: X post draft

Status: READY TO POST. Nick posts (outward-facing). Filed as GitHub issue #3294.
Tag: @huang_chao4969 (Chao Huang, Data Intelligence Lab @ HKU, LightRAG lab director).

---

## Option A: single post (fits one tweet)

Reported a config-disclosure default in @huang_chao4969's LightRAG.

/health is on the no-auth whitelist (config.py WHITELIST_PATHS), so it leaks
llm_binding, llm_model and working_directory on EVERY instance, including the
ones with auth fully enabled.

67/67 confirmed in a population survey. Fix + writeup: github.com/HKUDS/LightRAG/issues/3294

---

## Option B: 2-post thread (more detail)

1/
Found a default config-disclosure in LightRAG (@huang_chao4969 / HKUDS).

/health sits on the unauthenticated WHITELIST_PATHS, so it returns llm_binding,
llm_model and working_directory to anyone, even on instances with auth enabled.
A liveness probe leaking config.

2/
working_directory paths name the operator (/home/azureuser/...,
/usr/local/eagletalent/robot-graphrag/, /home/ubuntu/aidsmo-chatbot/).
67/67 instances in the survey leaked it.

One upstream fix: strip config from /health, or move it behind auth.
Details: github.com/HKUDS/LightRAG/issues/3294

---

## Notes
- No em dashes (NuClide voice rule). Plain, factual, no hype.
- Both options name the platform, the mechanism (whitelist), the blast radius
  (all instances incl. authed), the proof (67/67), and the fix (one upstream change).
- Issue #3294 is the canonical reference; the post points there for detail.
