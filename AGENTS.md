# Repository Guidelines

> **Note:** `CLAUDE.md` is a symlink to `AGENTS.md`. They are the same file.

## Project Overview

glebooru is a modern booru application (forked from szurubooru) supporting images, videos, Flash, and youtube-dl web content. Core features include tagging, pools, comments, annotations, and rich search.

## Project Structure & Module Organization

Top-level `server/` contains the Python backend (`szurubooru/` package, Alembic migrations, config templates) and automated tests under `server/szurubooru/tests/`. The HTTP server is FastWSGI via the `fastwsgi` Python package (started from `server/app.py`). Front-end assets live in `client/` (Stylus styles, CommonJS modules, build scripts). Shared documentation and example configs reside in `doc/`, while the `d` helper script plus `docker-compose*.yml` files orchestrate dev containers.

## Build, Test, and Development Commands

### Starting Development

```bash
# Requires hosts entries for booru, bagg, bfilter, bfilter2 -> 127.0.0.1
./d                    # Start full Docker stack
./d -w                 # Start stack with live client recompilation
```

### Client

```bash
bun --cwd client run build       # Build client bundles
bun --cwd client run watch       # Watch/rebuild client bundles
```

Use Bun for JS tooling by default (`bun`, `bun run`, `bunx`). Avoid `node`,
`npm`, and `npx` when an equivalent Bun workflow is available.

### Testing

```bash
# Always run backend tests inside Docker
docker compose -f docker-compose.dev.yml exec server pytest

# Run one test file
docker compose -f docker-compose.dev.yml exec server pytest szurubooru/tests/api/test_file.py

# Run one specific test
docker compose -f docker-compose.dev.yml exec server pytest szurubooru/tests/api/test_file.py::test_name

# Playwright E2E tests (against live dev stack)
bun --cwd client run e2e

# Install Playwright browsers (first-time setup)
bun --cwd client run e2e:install
```

### Database Migrations

```bash
docker compose -f docker-compose.dev.yml exec server doc/developer-utils/create-alembic-migration.sh
```

## Architecture

### Backend (Python 3.11 / FastWSGI)

The server is a WSGI application in `server/`:

- `app.py`: runs the HTTP server via `fastwsgi.run(...)` (FastWSGI, port 6666)
- `szurubooru/facade.py`: creates the WSGI app, validates config, wires handlers/background threads
- `szurubooru/api/`: REST endpoints using decorator-based routing (`@routes.get`, `@routes.post`, etc.)
- `szurubooru/func/`: business logic (`posts.py`, `tags.py`, `users.py`, `pools.py`, auth, serialization, image processing)
- `szurubooru/model/`: SQLAlchemy ORM models (`post.py`, `tag.py`, `user.py`, `pool.py`, etc.)
- `szurubooru/search/`: query parsing and execution
- `szurubooru/rest/`: lightweight REST framework
- `szurubooru/middleware/`: request/response middleware
- `szurubooru/migrations/`: Alembic migrations

### Frontend (JavaScript / Browserify)

Client code in `client/`:

- `build.js`: Browserify/Babel bundling + Stylus compilation
- `js/api.js`: API client for auth and HTTP requests
- `js/controllers/`: page controllers (MVC)
- `js/models/`: data model wrappers
- `js/views/`: UI view classes
- `js/util/`: helper utilities
- `css/`: Stylus stylesheets
- `html/`: templates

## Coding Style & Naming Conventions

Backend code targets Python 3.11 with Black (79-char line width) and isort; use 4-space indents, snake_case modules, and self-documenting function names. Keep new backend modules under `szurubooru/` to preserve import locality.

Client JavaScript uses CommonJS modules, 2- or 4-space indents (match local file style), and double-quoted strings; keep existing naming conventions (PascalCase for view classes, camelCase for helpers). Regenerate bundles instead of committing built artifacts.

Prefer Bun across frontend/dev tooling (`bun install`, `bun run`, `bunx`) and
only fall back to `node`/`npm` if a task is not Bun-compatible.

## Testing Guidelines

Pytest drives backend suites in `server/szurubooru/tests/{api,func,model,search,...}`; mirror that layout for new coverage. Name tests descriptively (`test_feature_behavior`) and rely on fixtures from `conftest.py`.

Always run backend tests inside Docker (never on the host), e.g.:

```bash
docker compose -f docker-compose.dev.yml exec server pytest
docker compose -f docker-compose.dev.yml exec server pytest path/to/test_file.py::test_case
```

No formal coverage gate exists, but feature and bugfix changes should add or update tests.

## Commit & Pull Request Guidelines

Use imperative commit subjects (e.g. `Fix tag merge regression`) and keep subjects under ~72 characters. Squash or amend locally before PRs. PRs should explain intent, link related issues, and include testing notes (plus screenshots for UI changes). Flag migrations, config toggles, and any manual follow-up steps.

## Configuration & Secrets

Base settings live in `server/config.yaml.dist` and `doc/example.env`; copy to environment-specific files and never commit secrets. For local overrides, use Docker secrets or `.env` files referenced by `docker-compose.dev.yml`. Rotate API tokens and third-party keys regularly, and document any new secrets in PR notes so operators can provision them.
