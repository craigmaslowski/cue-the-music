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
- **Routing:** React Router
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

## Architecture Notes

<!-- Key architectural decisions, folder structure, or patterns specific to this project -->

## Commands

<!-- Common commands for this project -->
