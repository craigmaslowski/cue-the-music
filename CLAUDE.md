# CLAUDE.md

## Project

A local-network web app for dinner parties and home listening sessions. Guests connect via Wi-Fi, browse the host's record collection (synced from Discogs), and request albums to be played. Requests appear in a shared queue visible to everyone. Guests can up- or down-vote requests; the host has a PIN-activated control layer to manage the queue and trigger Discogs sync.

No user accounts. No login. Identity is tracked by IP address only.

For more details: `docs/cue-the-music-overview.md`

## Standards

Read and follow these standards documents. They are enforceable constraints, not suggestions.

- Always: `docs/standards/STANDARDS-general.md`
- Frontend: `docs/standards/STANDARDS-frontend.md`
- Backend: `docs/standards/STANDARDS-backend.md`
- Agent: `docs/standards/STANDARDS-agent.md`

## Tech Stack

### Frontend (`apps/frontend`)

- **Bundler:** Vite 7
- **E2E tests:** Playwright
- **Formatter:** Prettier
- **Framework:** React 19
- **Linter:** ESLint + typescript-eslint
- **Routing:** TanStack Router
- **State (server):** TanStack Query
- **State (UI):** Zustand
- **UI Library:** ark-ui + Panda CSS
- **Unit tests:** vitest + Testing Library

### Backend (`apps/backend`)

- **Framework:** FastAPI
- **Language:** Python 3.13
- **Linter:** ruff
- **Migrations:** Alembic
- **ORM:** SQLAlchemy (SQLite)
- **Package manager:** uv
- **Server:** uvicorn
- **Unit tests:** pytest + pytest-cov
- **Data pipeline:** Discogs API

### Monorepo

- **Toolchain:** NX 22
  - **React NX plugin:** @nx/react
  - **Python NX plugin:** @nxlv/python

## Project-Specific Rules

- ALWAYS USE NX GENERATORS TO CREATE APPS AND LIBS

### Production (`docker-compose.yml`)

- **Containers:** Docker Compose (two services)
- **Frontend serving:** nginx:alpine (static Vite build)
- **Backend serving:** uvicorn (single worker)
- **Database:** SQLite in named Docker volume
- **Migrations:** Alembic (auto-run on container startup)

## Architecture Notes

- `DATABASE_URL` env var configures the SQLite path. Default: `sqlite+aiosqlite:///./cue_the_music.db` (no env var needed for dev).
- `VITE_API_BASE_URL` is baked into the frontend at build time for production. In dev, the frontend falls back to `window.location.hostname:8000`.

## Commands

### Development

- Frontend dev: `npx nx serve @cue-the-music/frontend`
- Backend dev: `cd apps/backend && uv run uvicorn cue_the_music.main:app --reload --host 0.0.0.0`
- Backend tests: `cd apps/backend && uv run pytest`
- Frontend build: `npx nx build @cue-the-music/frontend`
- Frontend typecheck: `npx nx typecheck @cue-the-music/frontend`
- Frontend E2E: `npx nx e2e @cue-the-music/frontend-e2e`
- All tests: `npx nx run-many -t test`

### Production (Docker)

- Start: `docker compose up -d`
- Rebuild after code changes: `docker compose up -d --build`
- View logs: `docker compose logs -f`
- Stop: `docker compose down`
- Reset database: `docker volume rm cue-the-music_db-data`

### First-time production setup

```bash
cp .env.example .env
# Edit .env — set DISCOGS_TOKEN, DISCOGS_USERNAME, HOST_PIN, VITE_API_BASE_URL
docker compose up -d
```
