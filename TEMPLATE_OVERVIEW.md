# Deploy and Host

Deploy a production-ready FastAPI backend with MongoDB on Railway in one click. The template provisions two services — a Docker-built FastAPI application and a MongoDB database — wired together automatically, with JWT authentication, user management, and a demo CRUD resource (items) working out of the box.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/fastapi-backend-mongo)

## About Hosting

Hosting this template gives you:

- **backend** — the FastAPI app, built from the repo's `Dockerfile` (Python 3.14 + uv), binding to Railway's dynamic `$PORT`, with a healthcheck on `/health` and an automatic restart policy on failure. It is deployed from the GitHub repo, so it stays updatable.
- **MongoDB** — Railway's MongoDB database plugin with a persistent volume at `/data/db`. The backend reads its connection string from `MONGO_URL`, which is pre-wired to `${{MongoDB.MONGO_URL}}`.

**Zero variables required before deployment.** Everything is wired automatically:

- `MONGO_URL` — set to `${{MongoDB.MONGO_URL}}`; the MongoDB service constructs its own connection string from generated credentials.
- `SECRET_KEY` (JWT signing) and the MongoDB root username/password — generated fresh per deployment via `${{ secret(...) }}` references.
- `PROJECT_NAME` and `FIRST_SUPERUSER` — sensible defaults baked into the app (`FastAPI Backend Mongo`, `admin@example.com`).

MongoDB is schemaless, so there are no migrations to run: on every deploy the container start command creates the indexes (unique `email` on `users`, `owner_id`/`created_at` on `items`) and seeds the first superuser — this happens inside the container start (Dockerfile `CMD` and `railway.json` `startCommand` are identical), so it works on every Railway deploy path.

After the deploy:

1. Open the `backend` service's **Variables** tab and copy the value of `FIRST_SUPERUSER_PASSWORD` — that generated password (with `admin@example.com`) logs you into the API.
2. Optionally set `FRONTEND_HOST` on the `backend` service to your API's public domain (used for CORS origins and links in outgoing emails).

## Why Deploy

- **Zero migration management** — MongoDB needs no schema migrations; index creation and superuser seeding are idempotent and run at boot.
- **Production-shaped auth out of the box** — OAuth2 password flow with JWT access tokens, Argon2 password hashing (with transparent bcrypt → argon2 upgrades), and role-based admin endpoints.
- **One domain, one service** — a pure backend API: no frontend build step, no static asset hosting, no CORS-bound SPA to configure.
- **Railway-native** — dynamic `$PORT` binding, `/health` healthcheck path, Dockerfile builder, and config-as-code via `railway.json` for GitHub-triggered deploys.

## Common Use Cases

- REST API backends for mobile and web apps that need authentication and user management on day one.
- Internal tools and admin APIs backed by MongoDB documents (users + items CRUD as the pattern to copy).
- A clean, official-template-based starting point for FastAPI teams that prefer MongoDB over SQL databases.
- Rapid prototyping of JWT-authenticated APIs with OpenAPI docs (`/docs`) generated automatically.

## Dependencies for

The deployed stack consists of the FastAPI backend service and the MongoDB database it persists to.

### Deployment Dependencies

- **MongoDB** — provisioned by the template; the backend connects using `MONGO_URL` (`${{MongoDB.MONGO_URL}}`). No other infrastructure is required.
- **No variables to fill in** — credentials are generated per deployment (`${{ secret(...) }}`), and `PROJECT_NAME`/`FIRST_SUPERUSER` default inside the app. Retrieve the generated `FIRST_SUPERUSER_PASSWORD` from the `backend` service's Variables tab after deploying.
- **Python 3.14 + uv** — baked into the Docker image; no host toolchain needed.
