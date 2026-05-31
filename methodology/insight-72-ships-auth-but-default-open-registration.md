# Insight #72 — Ships-auth-but-default-open-registration: the knob that re-opens a closed door

_Sourced to: the Data Labeling & Annotation survey, 2026-05-31 (case-studies/commercial/data-labeling-survey-2026-05-31.md)._

## The lesson

There is a failure class between "auth off by default" (#13) and "no auth layer
at all" (#71): a platform that ships **real authentication and a real authorization
layer**, both on by default, and then ships a **self-registration knob that
defaults open**. The data endpoints are correctly gated, the operator did nothing
wrong with the auth config, and the platform is still effectively unauthenticated
to the public internet, because anyone can create their own account in one step
and walk through the front door the auth layer was guarding.

The data-labeling survey isolated this cleanly. Three platforms, same category,
same managed-cloud population, same restraint conditions:

- **Label Studio** ships `DISABLE_SIGNUP_WITHOUT_LINK=False` (open self-registration
  is the default). `/user/signup` is reachable on **16 of 17** confirmed hosts.
  Anyone registers, gets an API token, and reads `/api/projects` and `/api/tasks`,
  the raw labeled training data. Effective-unauth at 94%.
- **CVAT** disables registration by default (OPA-backed authz since 2.0.0).
  **20 of 20** confirmed hosts returned 401/403 on `/api/projects`. Held.
- **doccano** ships `ALLOW_SIGNUP="False"`. Confirmed auth-on, consistent with the
  2026-05-04 pass (348/348 auth-on).

Same hosts, same clouds, same operators' skill level. The variable that predicted
effective-unauth was a single boolean: the **default value of the registration
knob**. Label Studio's default re-opened the door its own auth layer closed; CVAT's
and doccano's defaults kept it shut.

## Why it is distinct from #13 and #71

- **#13 (shipping defaults are load-bearing)** is the parent. This is the specific
  form where the load-bearing default is not the *auth* toggle but the *registration*
  toggle, on a platform whose auth is otherwise correct.
- **#71 (network-placement-as-auth)** is exposure = unauth because there is no auth
  layer. Here there IS an auth layer, and it works. The gap is one rung up the
  funnel: account acquisition, not credential bypass.
- The verification rung differs accordingly. A literal-no-auth read is inner-B/outer-1
  the moment you GET the data. Open-signup is **inner-A/outer-1 by restraint**: the
  signup form is reachable (observed), but you must register and then read to reach
  the data, and the NuClide ethic stops at "signup reachable, registration not
  exercised." The finding is real and the severity is medium, not high: it is one
  exercised step from data, and that step (creating an account on someone else's
  system) is exactly the line restraint does not cross.

## How to apply

1. **Enumerate the registration knob as a first-class auth-state.** For any platform
   that ships auth-on, the survey is not done at "data endpoint returns 401." Check
   whether self-registration is open (`/user/signup`, `/api/auth/register`, "anyone
   can join" workspace settings). An auth-on data endpoint behind an open signup is
   effective-unauth.
2. **Grade it medium, inner-A, and say why.** Signup-reachable is the finding;
   registering is the line not crossed. Do not inflate to high by registering, and
   do not dismiss it as "auth-on" because the data endpoint 401s.
3. **Carry a closed-default sibling as the discriminator.** When the corpus contains
   a comparable platform whose registration defaults closed (CVAT, doccano here), its
   holding under identical exposure proves the knob, not operator skill, is the cause.
4. **Default-credential is the same class.** A platform that ships a documented,
   un-rotated default key (Argilla's `owner.apikey` / `12345678`) is the credential
   form of the same failure: auth exists, the default re-opens it. Enumerate the
   default-key class as intel; never exercise the key against a live host.

## Relationships

- Specializes **#13** (shipping defaults are load-bearing) to the registration knob.
- Complements **#71** (network-placement-as-auth): different rung of the same funnel
  (account acquisition vs no-auth-layer).
- Uses **#16** (a 200 is identity, not auth-state) and the verification-rung grid
  (#68): open-signup is the canonical inner-A/outer-1 state (reachable, not exercised).
- Paired with **#73** (header-versioned APIs evade header-less fingerprinters), the
  other lesson from this survey.
