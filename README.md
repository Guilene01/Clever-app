# Notesy — DevOps Challenge

Welcome, and thanks for taking the time. Notesy is a small Django + HTMX notes app. It runs locally. **Your job is to make it production-ready.**

This is a real-shaped exercise: the app is the kind of thing a small team would hand you on day one, with all of the rough edges that implies.

---

## Time budget

We're aiming for **~3 hours of focused work**, followed by a **1-hour live walkthrough** with two engineers.

If you find yourself going significantly past 3 hours, stop and write down what you *would* have done in `SUBMISSION.md` — we explicitly value good prioritization over completeness.

## How to submit

1. Do not fork this repository for your submission.
2. Create a new private repository for your work. You may either create it from this repository as a template, or clone this repository locally and push the starter code to a new private repository.
3. Invite `mikejaffe` and `rymccue` to the private repository.
4. Do the work in your private repository.
5. Add your `SUBMISSION.md` (see below).
6. Open a pull request inside your private repository for reviewers to inspect.
7. Email your recruiter point of contact with the private repository and pull request links.

We will read the PR and run your stack locally (and in GitHub Actions on your repository) before the walkthrough.

Questions? Reach out to your Clever recruiting contact.

---

## What you're getting

A working app, with the kind of issues you'd inherit on a real team:

```
.
├── manage.py
├── notesy/                  # Django project (settings, urls, wsgi/asgi)
├── apps/notes/              # the actual app — models, views, templates
│   └── static_src/          # TypeScript source for the small client bundle
├── package.json             # esbuild + tsc toolchain
├── requirements.txt
├── pytest.ini
├── .github/workflows/ci.yml # the existing CI workflow (such as it is)
└── README.md                # you are here
```

## What it does

- Log in (session auth)
- List, create, edit, delete personal notes (HTMX-driven, no full page reloads)
- "Summarize" a note (calls out to an LLM-shaped service — currently stubbed)

## Run it locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
npm install
npm run build                        # compiles the TS bundle to static/js/
python manage.py migrate
python manage.py seed                # creates a demo user (demo/demo) + sample notes
python manage.py runserver
```

Then visit http://localhost:8000 and log in as `demo` / `demo`.

---

## Your deliverables

Three tiers, in order. Treat them as a priority queue — get tier 1 solid before climbing.

### Tier 1 — Make the app safe to run

Read through the code as if you've just inherited this. Make the changes you'd want before letting this anywhere near a real environment. We're looking for the kind of fixes that come from production experience, not a checklist.

### Tier 2 — Containerize it

Add the Docker pieces so a teammate can clone, run one command, and have the whole stack up. Postgres should be involved. Anyone running it should not have to set anything up on their host besides Docker.

### Tier 3 — Wire up CI/CD

There's a `.github/workflows/ci.yml` in the repo. It's a starting point, and not a good one. Make it a workflow you'd be willing to merge to `main` behind. We expect the image you build to be pushed to GitHub Container Registry (`ghcr.io`) on merge to `main`, tagged in a way that lets us roll back.

---

## Your `SUBMISSION.md`

Please add a `SUBMISSION.md` at the repo root with:

1. **What you changed and why** — one section per area (app / Docker / CI). Brief is fine.
2. **Tradeoffs you made** — anywhere you chose one option over another, what was the alternative?
3. **What you'd do with another day** — anything you saw and consciously chose not to fix.
4. **How to run your version** — if your `docker compose up` command isn't enough, document it.
5. **Deployment plan** — describe how you would take this from `docker compose up` on your laptop to a safe, production-ready deployment. You do NOT need to actually deploy it. We're looking for your thinking. Things worth covering:
   - Where you'd run it (platform, region(s), why)
   - How secrets reach the container (and rotate)
   - Rollout strategy and how you'd roll back a bad release
   - How database migrations run in your pipeline, and what you'd do about a migration that can't be rolled back
   - Logs, metrics, and where alerts would go
   - Anything you'd want in place before a real user touched it

   Pretend you're writing this for a teammate who's joining next week. We'll talk through it together in the walkthrough.

We pay more attention to `SUBMISSION.md` than to almost anything else. A small change with great reasoning beats a big change with no narrative.

---

## What we'll cover in the walkthrough

- You demo the stack running and walk us through the architecture
- We dig into 2-3 of your specific choices
- We throw a curveball or two (something breaks, something gets slow — diagnose live)
- We talk about what you'd do next with more time

There is no trick. We are looking for: production sense, calibration ("what matters now vs. later"), and the ability to explain your thinking.

---

## Constraints & rules

- **You can use any tools you like**, including LLMs. We assume you do — we do too. But you own every line you submit. In the walkthrough we will ask you to explain things.
- **Don't rewrite the app code**. Fix what's broken from an ops perspective. You can edit application code where it's necessary to fix a real operational issue (e.g. logging, config), but resist refactoring for taste.
- **Public infrastructure only**. Don't sign up for paid services on our behalf. GHCR via your own GitHub account is fine. AWS / GCP / Datadog accounts are not.
- **No git history rewrites** to hide work. We'd rather see honest commits than a polished single squash.

---

## Questions

If something is genuinely ambiguous or broken in a way that blocks you, email us. We'd rather unblock you than have you spin. If something seems wrong but you can work around it, log it in `SUBMISSION.md` and keep going — that's part of the signal.

Good luck. We're looking forward to talking through it.
