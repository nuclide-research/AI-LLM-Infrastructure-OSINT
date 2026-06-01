# Insight #76 — The app is auth-on; the operator's debris is auth-off

**Survey:** Cat-31 Data Labeling (Extended), 2026-06-01.

## Statement

In single-operator and small-team ML/AI deployments, the *application's* auth
posture and the *operator's filesystem hygiene* are independent variables. The
purpose-built service can be correctly authenticated end-to-end while a
debug/utility process on the same host leaks every credential behind it. At
population scale the annotation/inference UI is the wrong place to look for the
breach — the breach is in the training-pipeline debris colocated with it.

## Evidence

Cat-31 verified auth posture across 158 annotation services: 3 unauth, 10
auth-gated, 465 unknown. The annotation front-ends (Label Studio, Argilla,
doccano) are overwhelmingly auth-on — the thesis holds, consistent with the
2026-05-04 result (doccano 98.9% auth-on).

The standout critical was not an annotation UI at all. On 185.66.109.62
(Imkerei Hablützel / Velutina Service, a Swiss Asian-hornet YOLO-detection SaaS):

- The SaaS APIs (`scan.velutinaportal.eu/api/*`, `/backend/auth/*`) correctly
  return `{"error":"auth_required"}`. The product is properly gated.
- On the **same box**, a `python3 -m http.server` left running on port 8000
  serves the operator's project home directory unauthenticated: `.env` (+4 dated
  backups), `.gcp/`, `.gsutil/`, `.ssh/`, training scripts, dataset tarballs.

The credentials behind the auth-on APIs are sitting in the open directory next
to them. Auth on the app bought nothing because the operator's working
directory was independently exposed.

## Why this happens

ML pipelines accrete operator debris that production web apps do not:
- ad-hoc file servers to move datasets/weights between a workstation and a GPU box
- `.env` backups with rotation timestamps (the operator iterates on secrets)
- cloud-CLI credential dirs (`.gcp/`, `.gsutil/`, `.aws/`) needed for dataset I/O
- SSH keys for ephemeral rented GPU instances (Vast.ai, Lambda, etc.)

A single person doing data → annotation → train → deploy keeps all of it in one
home directory, and the quickest way to share a tarball is `python -m http.server`.
The app gets a real auth layer because it faces users; the home directory never
does because "it's just my dev box."

## Methodological consequence

For ML/AI categories where the population is single-operator or small-team
(annotation tools, fine-tuning rigs, hobbyist/conservation/research SaaS), do
not score the survey on the front-end auth posture alone. Enumerate the **host**,
not just the **service**: adjacent ports (8000/5000/9000), open directories,
debug servers, and backup files. The auth-on rate of the headline platform will
read clean while the operator-debris tier is wide open. The breach class is
"colocated training-pipeline exposure," and it is invisible to a fingerprint that
only asks "does the annotation API require a token."

## Cross-references

- Insight #40 (auth-on-default strengthens across OSS generations) — explains
  why the front-ends read clean.
- Cat-31 brief threat model (annotation host credentials = lateral path into the
  data plane) — this insight is the empirical confirmation at host level.
- Case study: velutina-service-ml-training-opendirectory-185.66.109.62-2026-06-01.
