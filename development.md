# Local Development

## Requirements

* [Docker](https://www.docker.com/).
* [uv](https://docs.astral.sh/uv/) for Python package and environment management.

## Local Development

Run the backend locally and connect it to MongoDB in Docker Compose.

From the project root, start MongoDB and Mailpit:

```console
$ docker compose up -d db mailpit
```

Then, from the project root, install the dependencies, prepare the database, and start the development server:

```console
$ uv sync
$ uv run bash scripts/prestart.sh
$ uv run fastapi dev
```

The API is available at `http://localhost:8000`, with automatic interactive docs at `http://localhost:8000/docs`.

## General Workflow

Run backend commands from the project root with `uv run`. Make sure your editor uses the Python interpreter at `.venv/bin/python` in the project root.

### Docker Compose

Alternatively, run everything (backend + MongoDB + Mailpit) inside Docker:

```console
$ docker compose up -d --build --wait
```

The backend reloads on code changes thanks to the `develop.watch` sync in `compose.override.yml`.

## Data model

MongoDB is schemaless — there are no migrations. Collections and indexes:

* `users`: unique index on `email`
* `items`: indexes on `owner_id` and `created_at`

If you add a new query pattern, create the matching index in `app/core/db.py::init_db` so every environment (local, Docker, Railway) gets it at startup.

## Tests

```console
$ docker compose up -d db
$ uv run bash scripts/tests-start.sh
```

Tests import the app and hit it with `TestClient`, against the same MongoDB configured in `.env` (`MONGO_URL`). The suite cleans the `users` and `items` collections when it finishes.

## Style, formatting, linting

```console
$ uv run bash scripts/lint.sh
$ uv run bash scripts/format.sh
```
