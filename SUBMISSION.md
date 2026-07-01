# Submission

## What I changed and why

### App (Tier 1 — Security & Safety)

- **`.env` removed from git / `.gitignore` updated** — the committed `.env` contained a database password and a fake-but-realistic API key. Added `.env`, `staticfiles/`, `static/js/`, and `.sessions/` to `.gitignore`. Added `.env.example` as a safe template so new contributors know what vars to set without getting real secrets from the repo.

- **`settings.py` — all secrets moved to environment variables** — `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `DATABASE_URL` were all hardcoded. They now come from environment variables loaded at startup via `python-dotenv`. The app refuses to start if `DJANGO_SECRET_KEY` is missing rather than silently using an insecure default. `DEBUG` defaults to `false` so a misconfigured deploy fails loudly rather than exposing a debug page.

- **`DATABASE_URL` support via `dj-database-url`** — the original `settings.py` hardcoded SQLite regardless of the `DATABASE_URL` in `.env`. Added `dj-database-url` so the URL drives the database backend, with SQLite as the dev/test fallback when the env var isn't set.

- **Sessions switched from file to database** — file-based sessions (`SESSION_ENGINE = file`) don't work across multiple processes, leave session files on disk indefinitely, and were being created at import time via `os.makedirs()`. Switched to `django.contrib.sessions.backends.db`. `migrate` creates the table automatically.

- **`requests` upgraded from 2.20.0 → >=2.32.0** — the pinned version is from 2018 and has several known CVEs (credential leakage, SSRF via redirect). Nothing in this codebase calls `requests` directly but it's a transitive risk as soon as the summarizer stub is wired up.

- **`whitenoise` added** — serves compressed, fingerprinted static files from gunicorn without needing a separate nginx container in simple deployments. Added `WhiteNoiseMiddleware` immediately after `SecurityMiddleware`.

- **Logout changed from GET to POST** — a GET-based logout is a CSRF gotcha: any `<img src="/logout/">` on a page the user visits logs them out. Decorated `logout_view` with `@require_POST` and updated `base.html` to submit a small form with `{% csrf_token %}`.

- **`print()` replaced with `logging`** — `print()` bypasses Django's log routing, has no log levels, and can't be silenced in production without patching stdout. Replaced all five call sites with `logger.info()` / `logger.warning()` using the module-level `logger = logging.getLogger(__name__)` pattern. Added a `LOGGING` config to `settings.py` that routes `apps.*` at DEBUG in dev and INFO in production.

- **Production security headers** — when `DEBUG=False`, the settings enable HSTS (1 year + preload), SSL redirect, and `Secure` + `HttpOnly` flags on session and CSRF cookies.

### Docker (Tier 2)

- **`Dockerfile` — multi-stage build** — Stage 1 uses `node:20-slim` to compile TypeScript to `static/js/`. Stage 2 uses `python:3.12-slim`, installs Python deps, copies the app, pulls compiled assets from Stage 1, runs `collectstatic`, then drops to a non-root user (`appuser`). The final image has no Node.js toolchain, no source TypeScript, and runs as a non-root user.

- **`docker-compose.yml`** — defines `db` (postgres:16-alpine) and `web`. The `db` service has a `pg_isready` healthcheck; `web` waits on `service_healthy` before starting. The `web` command runs `migrate`, `seed`, then `gunicorn` in a single shell string so first-run setup is automatic. Secrets are read from environment variables with a clear dev-only fallback label.

- **`.dockerignore`** — excludes `.git`, `.env`, `node_modules`, `__pycache__`, `staticfiles`, and `.sessions` to keep the build context small and prevent secrets from leaking into image layers.

### CI (Tier 3)

- **Removed `|| true` from pytest** — the original workflow masked all test failures. CI was green regardless of whether tests passed. Removed the `|| true` and let the step fail naturally.

- **Added `DJANGO_SECRET_KEY` env var to the test job** — the new `settings.py` raises `ImproperlyConfigured` if the key is missing. CI sets it to a clearly-labeled dummy value so tests run without a `.env` file.

- **Added `build-and-push` job** — runs only after `test` passes, and only on direct pushes (not PRs). Logs into GHCR with `GITHUB_TOKEN` (no stored credentials needed) and uses `docker/metadata-action` to produce:
  - `sha-<short-sha>` — immutable, points to the exact commit
  - `main` — floating branch tag
  - `latest` — only on pushes to `main`
  - `v1.2.3` / `v1.2` — on semver tags, enabling pinned deploys

## Tradeoffs

- **`collectstatic` in Dockerfile with a dummy key** — using a dummy `DJANGO_SECRET_KEY` at build time is safe here because `collectstatic` only reads file paths and doesn't touch the key. The alternative (a build arg or multi-stage secret mount) adds complexity with no real benefit for a static-asset step.

- **Migrations run at container startup, not in a separate job** — this is fine for a single-instance app and keeps the compose file simple. For a multi-replica deployment this would need a dedicated init container or a pre-deploy hook to avoid concurrent migration runs.

- **Two gunicorn workers** — conservative default. Each worker blocks for up to 8 seconds on the summarize endpoint (`time.sleep(8)`), so with 2 workers, 2 concurrent summarize calls fully saturate the process. The right fix is async workers (gevent/uvicorn) or moving summarization to a task queue, but that's an application architecture change beyond the scope of this exercise.

- **No `package-lock.json` committed** — `npm install` in the Dockerfile gives non-deterministic frontend builds. Adding a lockfile is a one-liner (`npm install && git add package-lock.json`) and should be done before this ships.

## What I'd do with another day

- Add a `healthcheck` endpoint (`/healthz/`) that checks DB connectivity and wire it into the Dockerfile `HEALTHCHECK` instruction.
- Move note summarization off the request thread (Celery + Redis, or a lightweight background thread pool) so 8-second sleeps don't block gunicorn workers.
- Add Docker layer caching to the CI build (`cache-from: type=gha`).
- Pin base image digests (`python:3.12-slim@sha256:...`) for reproducible builds.
- Add a staging environment to the CI pipeline that deploys on every merge to `main` before promotion to production.
- Commit `package-lock.json` for deterministic JS builds.

## How to run

```bash
# First time or after a code change
docker compose up --build

# Subsequent runs (no code changes)
docker compose up
```

App is at http://localhost:8000 — log in with `demo` / `demo`.

To stop and remove volumes: `docker compose down -v`

## Deployment plan

**Where it runs**

A managed container platform (ECS Fargate, Cloud Run, or Fly.io) removes the need to manage EC2/VM patching. The image built by CI is pulled directly from GHCR.

**How secrets reach it**

Secrets (`DJANGO_SECRET_KEY`, `DATABASE_URL`, `SUMMARIZER_API_KEY`) are stored in the platform's secret manager (AWS Secrets Manager, GCP Secret Manager, or Fly secrets). They are injected as environment variables at container startup — never baked into the image. The CI pipeline never sees production secrets.

**Rollout and rollback**

Deploy using the immutable `sha-<commit>` tag rather than `latest`. The platform does a rolling replacement (one container at a time) so there is no downtime window. Rollback is `deploy --image ghcr.io/.../notesy:sha-<previous>` — a one-command, sub-minute operation.

**Migrations**

Run as a one-off task (`python manage.py migrate`) in the same image, before traffic is shifted to new containers. On ECS this is a "run task" step in the deploy pipeline; on Fly it is `fly ssh console -C "python manage.py migrate"`. Migrations must be backward-compatible with the running version so an in-progress rollout doesn't break live traffic.

**Logs, metrics, alerts**

- Structured logs (JSON) from gunicorn and Django ship to CloudWatch Logs / GCP Logging via the platform's log driver.
- Expose `/healthz/` for liveness and readiness probes. The platform restarts containers that fail the check.
- Alert on HTTP 5xx rate > 1% over 5 minutes and p99 latency > 2 s. The summarize endpoint is the obvious culprit to watch.

**Before a real user touches it**

- [ ] Real secret rotation (generate a new `SECRET_KEY`, rotate DB password)
- [ ] TLS termination at the load balancer / CDN edge
- [ ] `ALLOWED_HOSTS` set to the actual domain, not `*`
- [ ] Automated DB backups with a tested restore runbook
- [ ] Rate limiting on the login endpoint (brute-force protection)
- [ ] Move summarization off the request thread so gunicorn workers aren't saturated
