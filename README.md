# FastAPI Backend — MongoDB (Railway-ready)

Backend-only, MongoDB-powered version of the [official FastAPI Full-Stack Template](https://github.com/tiangolo/full-stack-fastapi-template), packaged for one-click deployment on [Railway](https://railway.app).

All frontend code and the PostgreSQL/SQLModel/Alembic stack have been removed. Data is stored in MongoDB (via `pymongo`), with the same REST API surface as the original template (JWT auth, users, items).

## Deploy on Railway

[![Deploy on Railway](https://railway.com/button.svg)](https://railway.com/deploy/fastapi-backend-mongo)

The template provisions:

- **backend** — FastAPI app (Dockerfile build, binds to Railway's `$PORT`, healthcheck at `/health`)
- **MongoDB** — Railway's MongoDB database plugin; the app reads its `MONGO_URL`

**No variables required before deployment.** Everything is wired automatically:

- `MONGO_URL` — pre-wired to `${{MongoDB.MONGO_URL}}` (the MongoDB service builds its own connection string from generated credentials)
- `SECRET_KEY` (JWT signing) and the MongoDB root username/password — generated fresh per deployment via `${{ secret(...) }}` references
- `PROJECT_NAME` and `FIRST_SUPERUSER` — defaults baked into the app (`FastAPI Backend Mongo`, `admin@example.com`)

After the deploy, copy the generated `FIRST_SUPERUSER_PASSWORD` from the `backend` service's **Variables** tab — that password (with `admin@example.com`) logs you into the API. To override any of the defaults, set the corresponding variable before the first boot (seeding is idempotent and only runs once).

Index creation and the first-superuser seed run automatically at container start (`scripts/prestart.sh`, chained before the server in both the Dockerfile `CMD` and the `railway.json` `startCommand`), so no manual migration step is needed.

## API

Interactive docs are served at `/docs` (OpenAPI at `/api/v1/openapi.json`). Health endpoints: `/health` (platform healthcheck) and `/api/v1/utils/health-check/`.

Main routes:

- `POST /api/v1/login/access-token` — OAuth2 password flow, returns a JWT
- `POST /api/v1/users/signup`, `GET/PATCH/DELETE /api/v1/users/me`, admin user CRUD under `/api/v1/users/`
- Items CRUD under `/api/v1/items/` (per-owner scoping, admin can read all)
- Development-only private route `/api/v1/private/users/` (`FASTAPI_ENV=development`)

## MongoDB data model

Two collections, no schema migrations required:

- `users` — `{ _id: <uuid string>, email (unique index), hashed_password, is_active, is_superuser, full_name, created_at }`
- `items` — `{ _id: <uuid string>, title, description, owner_id (indexed), created_at }`

Unique and query indexes are created at startup by `app/core/db.py::init_db`.

## Local development

Requirements: [Docker](https://www.docker.com/) and [uv](https://docs.astral.sh/uv/).

Start MongoDB and Mailpit, then run the app with hot reload:

```bash
docker compose up -d db mailpit
uv sync
uv run bash scripts/prestart.sh   # create indexes + seed the superuser
uv run fastapi dev
```

The API is available at `http://localhost:8000` (docs at `/docs`). Environment defaults come from `.env`.

Or run everything inside Docker:

```bash
docker compose up -d --build --wait
```

## Tests

```bash
docker compose up -d db
uv run bash scripts/tests-start.sh
```

The test suite runs against the MongoDB instance from Docker Compose.

## License

MIT — derived from [tiangolo/full-stack-fastapi-template](https://github.com/tiangolo/full-stack-fastapi-template).
