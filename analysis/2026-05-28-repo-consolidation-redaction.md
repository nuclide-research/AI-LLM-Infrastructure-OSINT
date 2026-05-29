# Session Analysis — 2026-05-28

**Type:** Repository consolidation + security redaction. Not a research assessment.

## What was done

Moved the NuClide repo estate from the `Nicholas-Kloster` personal account to the
`nuclide-research` account, redacted sensitive data that had been committed to public
repos, and made the Go toolchain `go install`-able under the new owner.

### Repository transfers (21 repos -> nuclide-research)
- `AI-LLM-Infrastructure-OSINT` (already there; verified)
- `aimap`, `JAXEN`, `VisorPlus`
- Visor family (12): `visor`, `VisorAgent`, `VisorBishop`, `VisorCorpus`, `VisorGoose`,
  `VisorGraph`, `VisorHollow`, `VisorLog`, `VisorRAG`, `VisorScuba`, `VisorSD`
- Arsenal (6): `BARE`, `recongraph`, `menlohunt`, `nu-recon`, `cortex-framework`, `tiptoe`
- Transfers from a User account (not an org) create PENDING transfers that the recipient
  account must accept. Nick accepted them.
- Left in place deliberately: `Nicholas-Kloster.github.io` (live website, separate repo,
  serves nuclide-research.com), `Nicholas-Kloster` (profile README), `jaxen-blindbox`
  (private gift app).

### Security redaction (the load-bearing work)
- **OSINT repo made PRIVATE.** It had been public for weeks carrying real third-party
  data. Token-scope note: the `Nicholas-Kloster` gh login here is a COLLABORATOR (push,
  not admin) on the transferred repos — visibility changes and transfers needed the owner
  account or the browser. Nick flipped visibility himself.
- Purged 91 raw-data artifacts from full OSINT history (git-filter-repo): `ollama-*-state.json`
  (fields: creds / account_takeover / system_prompts / cred_hunted), `operator-tokens.json`,
  `nuclide.db` / `visorlog.db` / `empire.db` ledgers, aimap scan JSON, openapi/HTTP captures,
  shodan-raw dumps, target/dork lists. Force-pushed. Verified 0 refs across 483 commits.
- Hardened `.gitignore` with globs so scan-state files can't be re-tracked.
- `recongraph`: 10 accidental `runs/*.json` recon outputs (live-target provenance graphs)
  purged from history; `.gitignore` rule added. The repo's own gitignore already excluded
  `runs/*.json` — they were committed by mistake.
- `BARE`: 10 harvested target IPs in `adapters/shodan/examples/` scrubbed from all history
  via filter-repo --replace-text -> RFC5737 doc IPs; synthetic fixture regenerated through
  the repo's own `shodan_to_bare.py`. Verified 0 real IPs on fresh clone.

### Go module paths + installability
- Repointed `go.mod` module path on 13 Go repos: `github.com/Nicholas-Kloster/X` ->
  `github.com/nuclide-research/X`. All build clean.
- Made all Go tools `go install`-able (aimap + 13). Required per-repo tagging since the
  path-fix commits were untagged (so `@latest` would otherwise resolve to a pre-fix tag).
- aimap: module was bare `module aimap` -> `github.com/nuclide-research/aimap`, tagged
  v1.9.38 then v1.9.39 (version.go bumped 1.9.37 -> 1.9.39 to match tag).

## What was found (verified)
- OSINT public exposure quantified before redaction: ~10 credential entries, ~14
  account_takeover records, ~98 captured system prompts across ollama state files, plus
  Azure account data in `operator-tokens.json`, on .gov and healthcare third-party hosts.
  0 forks (good), but treat all exposed credentials as compromised regardless — public for
  weeks, crawlers/archives may hold copies.
- `nuclide.db` itself was clean of literal secrets (25,709 rows scanned) — the risk was the
  state JSON files, not the ledger.
- Pre-transfer adversarial audit (6 arsenal repos, workflow): 0 real secrets in any. The 2
  data-artifact flags (BARE sample, recongraph runs) were target lists, not credentials.

## What changed (infra)
- Owner of 21 repos: Nicholas-Kloster -> nuclide-research (old paths redirect).
- OSINT repo visibility: public -> private.
- 14 Go tools now `go install`-able under nuclide-research.

## Go install reference (for READMEs later)
Root-package: `go install github.com/nuclide-research/<repo>@latest`
  aimap, JAXEN, VisorPlus, VisorAgent, VisorHollow, tiptoe, VisorGoose, VisorLog, VisorScuba
Subpath (main in cmd/):
  visor/cmd/visor, VisorBishop/cmd/visorbishop, VisorGraph/cmd/visorgraph,
  VisorCorpus/cmd/visorcorpus, VisorRAG/cmd/visor   (note: VisorRAG main is cmd/visor, not cmd/visorrag)
VisorCorpus ships 5 commands: visorcorpus, attack-sim, corpus-dump, visorfail, visorforge.

## What's next (open threads)
- Decide whether OSINT repo goes public again. If yes, the redaction makes it safe; flip
  from the nuclide-research account. If staying private, no action.
- Optional: update tool READMEs with the `go install` one-liners above.
- Optional: bump non-aimap tool version strings to match their new tags; tag-history gaps
  exist (e.g. aimap tags reached v1.9.21 while code was at 1.9.37 — many bumps untagged).
- Redaction backup bundles in /tmp (osint-PREDACT-*, BARE-*, recongraph-*) — delete once
  confident nothing needs recovery. They clear on reboot regardless.
- VisorSD/menlohunt use bare module names (shodan-audit/menlohunt); nu-recon/cortex-framework/
  recongraph/BARE have no root go.mod — none are go-installable, none need it.

## Lessons
1. **The redaction is now the case study.** A recon-tool estate accumulates harvested data
   in committed examples, run-output dirs, and state files. `.gitignore` rules that exist but
   were bypassed (recongraph runs/) are a recurring failure mode. Audit committed data
   artifacts BEFORE making/keeping a repo public, not after.
2. **filter-repo path-removal misses data in sibling files.** BARE's IPs were in findings.json
   AND an older bare_output.json AND would've survived if only the 2 audited paths were purged.
   Use --replace-text on the value set (the IPs), not just --invert-paths on filenames, when
   the same data is scattered.
3. **Owner-transfer != name-fix.** Rewriting `Nicholas-Kloster -> nuclide-research` in go.mod
   fixes the owner segment but not name-segment mismatches (visorgoose vs VisorGoose). Both
   must match the actual repo path for `go install`.
4. **main-in-cmd/ repos need the subpath** in the install command; bare-repo install fails
   with "does not contain package". Always check where `package main` lives.
5. **Go proxy @latest lags** minutes behind a fresh tag; verify with GOPROXY=direct, don't
   trust a stale @latest failure as a real error.
6. **Verify on a FRESH clone, not the working dir.** Several "done" claims this session were
   premature; the fresh-clone check caught a still-dirty BARE push and an empty findings.json.
7. **Tool friction:** the Write tool requires a prior Read on existing files — tripped twice,
   silently leaving real data in place. For generated fixtures, use a Python writer script.
