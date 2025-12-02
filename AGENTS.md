# Repository Guidelines

## Project Structure & Module Organization
Top-level `server/` contains the FastWSGI Python backend (`szurubooru/` package, Alembic migrations, config templates) and all automated tests under `server/szurubooru/tests/`. Front-end assets live in `client/` (Stylus styles, CommonJS modules, build scripts). Shared documentation and example configs reside in `doc/`, while the `d` helper script plus `docker-compose*.yml` files orchestrate the dev containers.

## Build, Test, and Development Commands
Use `./d` to start the full Docker-based stack; add `-w` to enable live recompilation of client bundles. Rebuild the front-end manually with `npm --prefix client run build`, or keep it hot with `npm --prefix client run watch` when editing outside Docker. Run Python tests inside the server container via `docker compose -f docker-compose.dev.yml exec server pytest`. Apply new database migrations with `docker compose -f docker-compose.dev.yml exec server doc/developer-utils/create-alembic-migration.sh`.

## Coding Style & Naming Conventions
Backend code targets Python 3.11 with Black (79 character line width) and isort; prefer 4-space indents, snake_case modules, and self-documenting function names. Keep new modules under `szurubooru/` to preserve import locality. Client JavaScript sticks to CommonJS modules, 2- or 4-space indents as shown in existing files, and double-quoted strings; respect existing naming (PascalCase for view classes, camelCase for helpers). Regenerate bundles instead of committing built artifacts.

## Testing Guidelines
Pytest drives the backend suite (`server/szurubooru/tests/{api,func,model,...}`); mirror that layout when adding coverage. Name tests descriptively (`test_feature_behavior`) and rely on fixtures in `conftest.py` for setup. Run focused checks with `pytest path/to/test_file.py::test_case`. No formal coverage gate exists, but contributions should add or update tests alongside feature and bugfix work.

## Commit & Pull Request Guidelines
Craft commit messages in the imperative mood (`Fix tag merge regression`) and keep the subject under ~72 characters; amend or squash before raising a PR. Each PR should describe intent, link related issues, and include testing notes or screenshots for UI-facing changes. Flag migrations, config toggles, or manual follow-up steps so reviewers can validate them.

## Configuration & Secrets
Base settings live in `server/config.yaml.dist` and `doc/example.env`; copy them to environment-specific files, never commit credentials. For local overrides, rely on Docker secrets or `.env` files referenced in `docker-compose.dev.yml`. Rotate API tokens and third-party keys regularly, and document any new secrets in the PR so operators can provision them.
