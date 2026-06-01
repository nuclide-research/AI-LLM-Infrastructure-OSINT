# OPERATION ORDER — OSINT PLATOON
### Reference Doctrine: ATP 3-21.8 (Infantry Rifle Platoon and Squad)

---

## MISSION

Build a multi-agent OSINT research system in Python, architected on US Army infantry
platoon doctrine (ATP 3-21.8). The system receives a target (person, domain, org, or
username) and autonomously conducts layered reconnaissance, pivoting based on what
it finds, and produces a structured intelligence report.

Create a GitHub repo, push the initial structure, and implement the full system.

---

## SITUATION

### Doctrinal Foundation

This system mirrors the Infantry rifle platoon's command structure and troop leading
procedures exactly. Every architectural decision should have a doctrinal reason.

**Use extended thinking (Max effort) before writing any code.** Reason through the
full architecture first. The investment in planning pays off — this is the "Make a
Tentative Plan" step (TLP Step 3).

---

## EXECUTION

### Agent Hierarchy (Command Structure)

```
USER (Higher Command — issues the mission)
    │
    ▼
ORCHESTRATOR AGENT  ←── "Platoon Leader"
    │   - Receives target from user
    │   - Runs METT-TC(I) analysis
    │   - Issues tasking to squads
    │   - Replans based on scout reports
    │   - Produces final SALUTE report
    │
    ├──► RECON SQUAD ALPHA  ←── "1st Squad"
    │        Web search, news mentions, public records
    │
    ├──► RECON SQUAD BRAVO  ←── "2nd Squad"
    │        Domain/IP/WHOIS/DNS/cert transparency
    │
    ├──► RECON SQUAD CHARLIE  ←── "3rd Squad"
    │        Social footprint, username enumeration, profiles
    │
    └──► WEAPONS SQUAD  ←── "Weapons Squad"
             Document analysis, metadata extraction, PDF/image intel
```

**Platoon Sergeant role:** A state manager class that tracks what each squad has
found, prevents duplicate work, and maintains the running intelligence picture.

---

### The Eight-Step Troop Leading Procedures (Agent Loop)

Implement these as the core orchestration loop. Each step should be explicit in code
and logs — not implicit.

```
Step 1 — RECEIVE THE MISSION
    User provides: target identifier + target type + depth level (hasty/deliberate)

Step 2 — ISSUE WARNING ORDER (WARNO)
    Orchestrator emits a WARNO to all squads:
    - Target summary
    - Anticipated AO (attack surface / search space)
    - Initial squad assignments
    - Time constraint

Step 3 — MAKE A TENTATIVE PLAN
    Orchestrator runs METT-TC(I) analysis:
    - Mission: What are we trying to determine?
    - Enemy (Target): What do we already know?
    - Terrain: What surfaces are in scope? (web/DNS/social/docs)
    - Troops: Which squads/tools are available?
    - Time: Hasty (quick sweep) or Deliberate (deep dive)?
    - Civil/Info: Any legal/ethical constraints on this target?
    Output: Prioritized squad tasking list

Step 4 — INITIATE MOVEMENT
    Dispatch squads. Recon-first discipline enforced:
    - ALL squads start in PASSIVE mode (read-only, no account creation, no active probing)
    - Squads run in PARALLEL where tasks are independent
    - Base-of-fire pattern: one squad holds context while another advances

Step 5 — CONDUCT RECONNAISSANCE
    Squads execute and report back. Each squad returns a standardized SPOT report:
    {
      "squad": "alpha",
      "finds": [...],           # what was found
      "pivots": [...],          # suggested follow-on targets
      "confidence": 0.0-1.0,
      "raw": {...}              # raw data
    }

Step 6 — COMPLETE THE PLAN
    Orchestrator reads all SPOT reports.
    - Identifies high-value pivots
    - Reassigns squads to follow threads
    - Issues refined tasking (loop back to Step 4 if needed)
    - Determines when to stop (max iterations or diminishing returns)

Step 7 — ISSUE OPERATION ORDER (OPORD)
    On final loop: Orchestrator synthesizes all squad reports into a
    structured SALUTE report (Size, Activity, Location, Unit, Time, Equipment)
    mapped to OSINT context:
    - Subject: Who/what is the target
    - Activity: What are they doing / associated with
    - Location: Where are they present online/physically
    - Unit/Org: Affiliations, associated entities
    - Timeline: When was each finding timestamped
    - Exposure: What sensitive data is publicly accessible

Step 8 — SUPERVISE AND REFINE
    Post-mission: Log all agent calls, costs, and findings.
    Store session state for follow-on missions.
```

---

### Squad Specifications

#### ORCHESTRATOR (Platoon Leader)
```python
system_prompt = """
You are the Platoon Leader of an OSINT research unit, operating under ATP 3-21.8 doctrine.

Your responsibilities:
1. Receive a target and conduct METT-TC(I) analysis
2. Task specialized recon squads with specific objectives
3. Read squad SPOT reports and identify high-value pivots
4. Replan and retask based on findings
5. Know when the mission is complete (diminishing returns = consolidate)
6. Produce a final SALUTE-format intelligence report

Rules of Engagement:
- Passive before active. Recon before probing.
- Never task a squad to take actions that could alert the target.
- All findings must cite source and timestamp.
- If a squad finds something unexpected and significant, halt other squads and pivot.

You output structured JSON for squad tasking and SALUTE reports.
"""
```

#### SQUAD ALPHA — Web Recon
```
Tools: web_search
Mission: Surface-level reconnaissance. News, mentions, public profiles,
         forum posts, data breach references, paste sites.
ROE: Read-only. No account creation. No login.
Report format: SPOT JSON with source URLs and timestamps.
```

#### SQUAD BRAVO — Domain/IP/Infra Recon
```
Tools: web_search + DNS lookups (dnspython) + WHOIS (python-whois) + 
       cert transparency (crt.sh API)
Mission: Map technical infrastructure. Domains, IPs, ASNs, hosting providers,
         SSL certificates, subdomains, historical DNS records.
ROE: Passive DNS and CT log queries only. No active port scanning.
Report format: SPOT JSON with infrastructure graph nodes.
```

#### SQUAD CHARLIE — Social Footprint
```
Tools: web_search
Mission: Username enumeration across platforms, public social profiles,
         linked accounts, profile photos, bios, follower/following patterns.
ROE: Public data only. No authenticated scraping.
Report format: SPOT JSON with platform, handle, URL, last active.
```

#### WEAPONS SQUAD — Document & Metadata Intel
```
Tools: web_search + document fetching + metadata extraction
Mission: Find publicly accessible documents (PDFs, DOCX, XLSX) associated
         with target. Extract metadata (author, org, timestamps, GPS if present).
ROE: Only fetch documents that are publicly indexed.
Report format: SPOT JSON with document source, metadata fields extracted.
```

---

### Movement Techniques (Parallelism Pattern)

Implement the **base-of-fire + bounding** pattern from ATP 3-21.8 Chapter 3:

```python
# Squads Alpha and Charlie run in parallel (independent surfaces)
# Squad Bravo bounds forward on domain findings from Alpha
# Weapons Squad holds and synthesizes while others move

async def execute_squads(target, tasking):
    # Base of fire: run independent squads simultaneously
    alpha_task = asyncio.create_task(squad_alpha.run(target, tasking))
    charlie_task = asyncio.create_task(squad_charlie.run(target, tasking))
    
    # Bravo waits for Alpha's domain findings to bound off
    alpha_report = await alpha_task
    bravo_task = asyncio.create_task(squad_bravo.run(target, alpha_report.pivots))
    
    # Weapons Squad synthesizes as reports come in
    charlie_report = await charlie_task
    bravo_report = await bravo_task
    
    return await weapons_squad.synthesize([alpha_report, bravo_report, charlie_report])
```

---

### Patrol Discipline (Recon-First ROE)

From ATP 3-21.8 Chapter 7 (Patrols and Patrolling):

> "Reconnaissance patrols collect information and confirm or deny the accuracy 
> of intelligence. They avoid contact."

Enforce this in code:
- Each squad has a `mode: "recon" | "active"` flag
- Default is always `"recon"` (passive)
- Orchestrator must explicitly authorize `"active"` mode
- Log every mode change with justification

---

### State Management (Platoon Sergeant)

```python
class PlatoonSergeant:
    """Tracks the running intelligence picture. Never lets squads duplicate work."""
    
    def __init__(self):
        self.intelligence_picture = {}   # All confirmed finds
        self.pending_pivots = []         # Unworked leads
        self.completed_tasks = set()     # Dedup tracker
        self.squad_status = {}           # What each squad is doing
        self.iteration = 0               # Loop count
        self.max_iterations = 5          # Stop condition
    
    def register_spot_report(self, squad, report): ...
    def get_next_tasking(self): ...
    def should_continue(self): ...
    def export_intelligence_picture(self): ...
```

---

## PROJECT STRUCTURE

```
osint-platoon/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── platoon/
│   ├── __init__.py
│   ├── orchestrator.py        # Platoon Leader — main agent loop
│   ├── platoon_sergeant.py    # State manager
│   ├── squads/
│   │   ├── __init__.py
│   │   ├── alpha.py           # Web recon
│   │   ├── bravo.py           # Domain/IP/infra
│   │   ├── charlie.py         # Social footprint
│   │   └── weapons.py         # Document/metadata
│   ├── models/
│   │   ├── spot_report.py     # SPOT report dataclass
│   │   ├── salute_report.py   # Final SALUTE report dataclass
│   │   └── tasking.py         # Squad tasking dataclass
│   └── utils/
│       ├── mett_tc.py         # METT-TC(I) analyzer
│       └── logger.py          # Structured mission logging
│
├── cli.py                     # Entry point: python cli.py --target <x> --type <domain|person|username>
└── reports/                   # Output directory for SALUTE reports
```

---

## TECH STACK

- **Language:** Python 3.11+
- **AI SDK:** `anthropic` (latest)
- **Model:** `claude-opus-4-5` for Orchestrator, `claude-sonnet-4-5` for squads (cost efficiency)
- **Async:** `asyncio` for parallel squad execution
- **Tools in API calls:** `web_search_20250305` tool type
- **DNS:** `dnspython`
- **WHOIS:** `python-whois`
- **HTTP:** `httpx` (async)
- **Data:** `pydantic` for all report models
- **Logging:** `structlog`
- **CLI:** `click`

---

## SERVICE AND SUPPORT

- Store `ANTHROPIC_API_KEY` in `.env`
- Log all API calls with token counts to `logs/mission_<timestamp>.jsonl`
- Each run produces a report in `reports/SALUTE_<target>_<timestamp>.md`
- Include a `--dry-run` flag that prints the METT-TC plan without executing squads

---

## COMMAND AND SIGNAL

**Entry point:**
```bash
python cli.py --target "example.com" --type domain --depth deliberate
python cli.py --target "johndoe" --type username --depth hasty
python cli.py --target "Acme Corp" --type org --depth deliberate
```

**GitHub repo:**
- Initialize git, create `.gitignore` (ignore `.env`, `reports/`, `logs/`)
- Create repo on GitHub via `gh` CLI
- Push initial commit with full structure
- Add a README that explains the ATP 3-21.8 doctrinal basis

---

## COMMANDER'S INTENT

The system should feel like a disciplined recon platoon, not a chatbot.
It plans before it moves. It reports in structured formats. It knows when
to push deeper and when to consolidate. Every agent call has a doctrinal
reason. The SALUTE report at the end should be immediately actionable.

Begin with extended thinking. Design before you build.
