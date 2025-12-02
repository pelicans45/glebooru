# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

glebooru is a modern image board (booru) application, forked from szurubooru. It supports images, videos, Flash, and youtube-dl web content with features like tagging, pools, comments, annotations, and a rich search system.

## Development Commands

### Starting the Development Environment
```bash
# Start Docker containers (requires hosts file entries for booru, bagg, bfilter, bfilter2 pointing to 127.0.0.1)
./d                    # Start full stack
./d -w                 # Start with live client recompilation
```

### Client Development
```bash
npm --prefix client run build    # Build client bundles
npm --prefix client run watch    # Watch mode for development
```

### Running Tests
```bash
# Run all Python tests (inside Docker)
docker compose -f docker-compose.dev.yml exec server pytest

# Run specific test file
docker compose -f docker-compose.dev.yml exec server pytest szurubooru/tests/api/test_file.py

# Run specific test
docker compose -f docker-compose.dev.yml exec server pytest szurubooru/tests/api/test_file.py::test_name
```

### Database Migrations
```bash
docker compose -f docker-compose.dev.yml exec server doc/developer-utils/create-alembic-migration.sh
```

## Architecture

### Backend (Python 3.11 / FastWSGI)

The server is a WSGI application in `server/`:

- **Entry point**: `app.py` runs the FastWSGI server on port 6666
- **`szurubooru/facade.py`**: Creates the WSGI app, configures error handlers, validates config, starts background threads
- **`szurubooru/api/`**: REST API endpoints using decorator-based routing (`@routes.get`, `@routes.post`, etc.)
  - `post_api.py`, `tag_api.py`, `user_api.py`, `pool_api.py`, `comment_api.py`, etc.
- **`szurubooru/func/`**: Business logic modules
  - `posts.py`, `tags.py`, `users.py`, `pools.py` - CRUD operations
  - `auth.py` - Authentication and authorization with rank-based privileges
  - `images.py` - Image processing (thumbnails, signatures)
  - `serialization.py` - JSON serialization for API responses
- **`szurubooru/model/`**: SQLAlchemy ORM models (`post.py`, `tag.py`, `user.py`, `pool.py`, etc.)
- **`szurubooru/search/`**: Search query parsing and execution
- **`szurubooru/rest/`**: Custom lightweight REST framework with route decorators
- **`szurubooru/middleware/`**: Request/response middleware
- **`szurubooru/migrations/`**: Alembic database migrations

### Frontend (JavaScript / Browserify)

Client-side code in `client/`:

- **Build**: `build.js` bundles JS (Browserify + Babel) and compiles Stylus CSS
- **`js/api.js`**: API client class handling authentication and HTTP requests
- **`js/controllers/`**: Page controllers (MVC pattern)
- **`js/models/`**: Data models wrapping API responses
- **`js/views/`**: View classes for UI components
- **`js/util/`**: Helper utilities
- **`css/`**: Stylus stylesheets
- **`html/`**: HTML templates

### Configuration

- `server/config.yaml.dist` - Server configuration template (privileges, SMTP, thumbnails, etc.)
- `client/config.yaml` / `client/config.dev.yaml` - Client configuration
- `.env` - Environment variables (not committed)

### Testing

Tests are in `server/szurubooru/tests/` organized by layer:
- `api/` - API endpoint tests
- `func/` - Business logic tests
- `model/` - ORM model tests
- `search/` - Search functionality tests
- `conftest.py` - Shared fixtures (user_factory, post_factory, context_factory, etc.)

## Code Style

### Python
- Black formatter with 79 character line width
- isort for import sorting
- 4-space indentation, snake_case
- Target Python 3.11

### JavaScript
- CommonJS modules
- 2 or 4-space indentation (match existing files)
- Double-quoted strings
- PascalCase for view classes, camelCase for helpers
