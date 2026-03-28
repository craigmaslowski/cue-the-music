---
title: "feat: Docker container production setup"
type: feat
status: active
date: 2026-03-27
origin: docs/brainstorms/2026-03-27-container-production-setup-requirements.md
---

# feat: Docker container production setup

Containerize the app for reliable deployment on a home server (2012 MacBook Pro, Intel, macOS, Docker Desktop). Two containers managed by Docker Compose: nginx serving the Vite build, and uvicorn running FastAPI with SQLite persisted in a named volume.

(see origin: `docs/brainstorms/2026-03-27-container-production-setup-requirements.md`)

## Files to Create

### 1. `apps/backend/Dockerfile`

Multi-stage build:

**Stage 1: builder** — `python:3.13-slim`
- Install `uv`
- Copy `pyproject.toml`, `uv.lock`
- Run `uv sync --no-dev --frozen` to install production deps
- Copy source code

**Stage 2: runtime** — `python:3.13-slim`
- Copy virtualenv from builder
- Copy source, alembic config, and migrations
- Set `PYTHONPATH` so `cue_the_music` package is importable
- Expose port 8000
- Entrypoint: shell script that runs `alembic upgrade head` then `uvicorn`

```dockerfile
FROM python:3.13-slim AS builder
WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app /app
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"
EXPOSE 8000
COPY docker-entrypoint.sh .
RUN chmod +x docker-entrypoint.sh
ENTRYPOINT ["./docker-entrypoint.sh"]
```

### 2. `apps/backend/docker-entrypoint.sh`

```bash
#!/bin/sh
set -e
echo "Running database migrations..."
alembic upgrade head
echo "Starting uvicorn..."
exec uvicorn cue_the_music.main:app --host 0.0.0.0 --port 8000
```

### 3. `apps/frontend/Dockerfile`

Multi-stage build:

**Stage 1: builder** — `node:22-slim`
- Copy the entire monorepo (NX + Panda CSS need the full workspace for libs resolution)
- Run `npm ci`
- Run `npx panda codegen` (generates styled-system dir)
- Run `npx nx build @cue-the-music/frontend`
- Accept `VITE_API_BASE_URL` as a build arg

**Stage 2: runtime** — `nginx:alpine`
- Copy `apps/frontend/dist/` from builder to `/usr/share/nginx/html`
- Copy a custom `nginx.conf` for SPA routing (try_files → index.html)
- Expose port 80

```dockerfile
FROM node:22-slim AS builder
WORKDIR /app
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npx panda codegen --cwd apps/frontend
RUN npx nx build @cue-the-music/frontend

FROM nginx:alpine
COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### 4. `apps/frontend/nginx.conf`

SPA-friendly config that falls back to `index.html` for client-side routing:

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5. `docker-compose.yml` (project root)

```yaml
services:
  backend:
    build:
      context: ./apps/backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - db-data:/app/data
    environment:
      - DATABASE_URL=sqlite+aiosqlite:///./data/cue_the_music.db
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: apps/frontend/Dockerfile
      args:
        VITE_API_BASE_URL: ${VITE_API_BASE_URL}
    ports:
      - "8080:80"
    restart: unless-stopped
    depends_on:
      - backend

volumes:
  db-data:
```

### 6. `.env.example` (project root)

```env
# Discogs API credentials (required for collection sync)
DISCOGS_TOKEN=your_discogs_personal_access_token
DISCOGS_USERNAME=your_discogs_username

# Host PIN for admin controls (default: 0000)
HOST_PIN=1234

# Backend API URL for frontend build (your server's LAN IP)
VITE_API_BASE_URL=http://192.168.1.100:8000
```

### 7. `.dockerignore` (project root)

```
node_modules
.git
*.db
*.db-shm
*.db-wal
coverage
reports
.vite
dist
.nx
```

## Backend Config Change

**Modify:** `apps/backend/src/cue_the_music/config.py`

The `Settings` class needs to support `DATABASE_URL` as an env var so the Docker volume path can be configured. Currently the database path is hardcoded in `alembic.ini` and the SQLAlchemy engine setup.

**Modify:** `apps/backend/alembic.ini` or `alembic/env.py`

Override `sqlalchemy.url` from the `DATABASE_URL` env var when present, so migrations use the same volume-mounted path as the app.

## Acceptance Criteria

- [ ] `docker compose up -d` starts both containers from project root (R1)
- [ ] Frontend served by nginx on host port 8080 (R2)
- [ ] Backend runs uvicorn on host port 8000 with production settings (R3)
- [ ] SQLite database persists in named Docker volume across restarts (R4)
- [ ] Alembic migrations run on backend container startup (R5)
- [ ] Frontend build uses `VITE_API_BASE_URL` from `.env` (R6)
- [ ] Secrets passed via `.env` file (R7)
- [ ] `.env.example` documents all required variables (R8)
- [ ] Both containers restart on failure (R9)
- [ ] `docker compose up -d --build` rebuilds without losing data
- [ ] Guest on LAN can browse `http://<server-ip>:8080` and request albums

## Deferred Questions Resolved

- **R6 fallback**: The frontend already falls back to `window.location.hostname:8000` when `VITE_API_BASE_URL` isn't set. For containers, set it explicitly via `.env`. Dev mode continues to work without it.
- **R3 workers**: Single-worker uvicorn on `0.0.0.0:8000`. No gunicorn needed for <10 concurrent users.

## Sources

- **Origin document:** [docs/brainstorms/2026-03-27-container-production-setup-requirements.md](docs/brainstorms/2026-03-27-container-production-setup-requirements.md) — Key decisions: nginx:alpine for frontend, Docker volume for SQLite, build-time API URL, migrations on startup
- `apps/backend/pyproject.toml` — Python 3.13, uv build system, production deps
- `apps/backend/alembic.ini:90` — SQLite URL hardcoded, needs env var override
- `apps/backend/src/cue_the_music/config.py` — Settings via pydantic-settings, .env loading
- `apps/frontend/vite.config.mts` — build output to `./dist`, Panda CSS + TanStack Router plugins
- `apps/frontend/panda.config.ts` — includes `../../libs/frontend/*/src/**` (needs full monorepo context)
