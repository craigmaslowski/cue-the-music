---
date: 2026-03-27
topic: container-production-setup
---

# Container Production Setup

## Problem Frame

The app runs in dev mode on a laptop. To use it at dinner parties, it needs to run reliably on a home server (macOS with Docker Desktop) so the host isn't tied to their development machine. Guests connect over LAN Wi-Fi.

## Requirements

- R1. Docker Compose file that starts both frontend and backend with `docker compose up -d`
- R2. Frontend container: Vite build output served by a static file server (e.g., `nginx:alpine` or `serve`), exposed on host port 8080
- R3. Backend container: FastAPI/uvicorn with production settings, exposed on host port 8000
- R4. SQLite database persists across container restarts via a named Docker volume
- R5. Alembic migrations run automatically on backend container startup (before uvicorn starts)
- R6. Frontend build bakes in the backend API URL via `VITE_API_BASE_URL` build arg — no runtime config needed since it's LAN-only and the host IP is known at build time
- R7. Environment variables for secrets (HOST_PIN, DISCOGS_TOKEN, DISCOGS_USERNAME) passed via `.env` file referenced by Docker Compose
- R8. A `.env.example` file documenting all required environment variables
- R9. Both containers restart automatically on failure (`restart: unless-stopped`)

## Success Criteria

- `docker compose up -d` from the project root starts both services with zero manual steps
- Guests on the same Wi-Fi can browse albums at `http://<server-ip>:8080` and queue requests
- Host can trigger sync, manage queue, and data survives container rebuilds
- Rebuilding containers (`docker compose up -d --build`) applies code changes without losing data

## Scope Boundaries

- No TLS/HTTPS (LAN only, no sensitive data beyond a 4-digit host PIN)
- No reverse proxy (direct port exposure)
- No CI/CD or image registry — build locally on the server
- No internet exposure (no Tailscale, Cloudflare Tunnel, or port forwarding)
- No container orchestration beyond Docker Compose (no Kubernetes, Swarm)
- No multi-arch builds (macOS x86_64/Intel only, building and running on the same machine)

## Key Decisions

- **Static file server for frontend**: The Vite dev server is not production-ready. Serve the built `dist/` output with `nginx:alpine` (tiny, fast, battle-tested) rather than a Node-based server.
- **Docker volume over bind mount**: Named volume is simpler, survives `docker compose down`, and Docker manages the lifecycle. No need to remember a host path.
- **Build-time API URL**: Since LAN IP is known at build time (the server's IP doesn't change), `VITE_API_BASE_URL` is baked into the frontend build as a Docker build arg. No runtime env injection needed.
- **Migrations on startup**: A small entrypoint script runs `alembic upgrade head` before launching uvicorn, ensuring the DB schema is always current after a redeploy.

## Outstanding Questions

### Deferred to Planning

- [Affects R6][Technical] Should the frontend fallback to `window.location.hostname:8000` if `VITE_API_BASE_URL` isn't set, preserving the current dev behavior? (It already does this for `apiFetch` and SSE — just needs confirmation the build doesn't break without the env var.)
- [Affects R3][Technical] Should uvicorn bind to `0.0.0.0` with a fixed worker count, or use gunicorn as a process manager? For a home server with <10 concurrent users, single-worker uvicorn is likely sufficient.

## Next Steps

→ `/ce:plan` for structured implementation planning
