# Deploy and Host

Deploy a production-ready FastAPI backend with MongoDB on Railway in one click. The template provisions two services — a Docker-built FastAPI application and a MongoDB database — wired together automatically, with JWT authentication, user management, and a demo CRUD resource (items) working out of the box.

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/fastapi-backend-mongo)

## About Hosting

Hosting this template gives you:

- **backend** — the FastAPI app, built from the repo's `Dockerfile` (Python 3.14 + uv), binding to Railway's dynamic `$PORT`, with a healthcheck on `/health` and an automatic restart policy on failure. It is deployed from the GitHub repo, so it stays updatable.
- **MongoDB** — Railway's MongoDB database plugin with a persistent volume at `/data/db`. The backend reads its connection string from `MONGO_URL`, which is pre-wired to `${{MongoDB.MONGO_URL}}`.

The deploy form prompts you for:

| Service | Variable | What to enter |
| --- | --- | --- |
| MongoDB | `MONGOPORT` | `27017` |
| MongoDB | `MONGO_INITDB_ROOT_USERNAME` | `mongo` |
| backend | `PROJECT_NAME` | your project name (shown in the OpenAPI docs) |
| backend | `SECRET_KEY` | a strong random secret (`openssl rand -hex 32`) |
| backend | `FIRST_SUPERUSER` | the admin email to seed |
| backend | `FIRST_SUPERUSER_PASSWORD` | a strong password for the admin |

The MongoDB root password is generated fresh per deployment. Everything else is wired automatically, and the backend gets a public Railway domain on deploy.

MongoDB is schemaless, so there are no migrations to run: on every deploy the container start command creates the indexes (unique `email` on `users`, `owner_id`/`created_at` on `items`) and seeds the first superuser from the environment variables — this happens inside the container start (Dockerfile `CMD` and `railway.json` `startCommand` are identical), so it works on every Railway deploy path.

After the first deploy, optionally set `FRONTEND_HOST` on the `backend` service to your API's public domain (used for CORS origins and links in outgoing emails).

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
- **Environment variables on `backend`** — `PROJECT_NAME`, `SECRET_KEY`, `FIRST_SUPERUSER`, `FIRST_SUPERUSER_PASSWORD` (the deploy form prompts for all four; enter strong values for production use).
- **Python 3.14 + uv** — baked into the Docker image; no host toolchain needed.
