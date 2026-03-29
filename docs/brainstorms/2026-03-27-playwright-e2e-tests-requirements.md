---
date: 2026-03-27
topic: playwright-e2e-tests
---

# Playwright E2E Tests

## Problem Frame

The app has backend unit tests (pytest) and basic frontend smoke tests (Playwright), but no end-to-end tests that exercise full user journeys through the real UI + API. E2E tests must not touch the on-disk production/dev database.

## Requirements

- R1. E2E tests run against a real backend with a temp SQLite database (not the on-disk dev DB)
- R2. A test-only `POST /api/test/reset` endpoint truncates all tables and seeds baseline album data. Guarded by `TEST_MODE=true` env var — refuses to mount otherwise.
- R3. Each test suite calls the reset endpoint in `beforeAll` to start with a clean, seeded state
- R4. The temp database file is created in `globalSetup` and deleted in `globalTeardown`
- R5. Full user journey coverage:
  - **Guest flows**: browse collection, search, filter by genre/decade, view album detail, request album, see "In Queue" state, cancel own request, up/down vote
  - **Queue flows**: see queue updates in real time (SSE), see vote counts
  - **Host flows**: activate host mode via PIN, promote to now playing, remove queue item, clear all queue, deactivate host mode
  - **Navigation**: tab switching retains crate state, overlay open/close
- R6. Discogs sync is NOT tested in E2E — pre-seeded data covers album browsing. Sync is covered by backend unit tests.
- R7. Tests run on Chromium, mobile Chrome (Pixel 5 viewport), WebKit (Desktop Safari), and mobile Safari (iPhone 14 viewport)

## Success Criteria

- `npx nx e2e @cue-the-music/frontend-e2e` runs all E2E tests with zero manual setup beyond having Node + Python installed
- Tests do not create, modify, or read from the dev/production database
- Tests are independent — any suite can run in isolation with a fresh reset
- All tests pass on a clean checkout after `npm install` + `uv sync`

## Scope Boundaries

- No Discogs sync E2E test (covered by backend unit tests)
- No multi-user/multi-browser concurrent tests (SSE is tested by seeding data and checking UI updates, not by having two browsers interact simultaneously)
- No visual regression testing
- No performance/load testing

## Key Decisions

- **Temp DB + reset endpoint over fresh DB per suite**: Avoids restarting the backend between test files. One backend process for the entire run, reset via HTTP call. Fast and simple.
- **TEST_MODE guard on reset endpoint**: The endpoint only mounts when `TEST_MODE=true` is set. Zero production risk — the route doesn't exist unless explicitly enabled.
- **Skip Discogs sync E2E**: Sync involves rate-limited external API calls. It's well-tested in backend pytest. E2E tests use pre-seeded data.
- **Seed baseline data in reset endpoint**: The reset endpoint seeds a small, known set of albums (diverse genres, decades, tracklists) so tests have predictable data to browse, filter, and request.

## Outstanding Questions

### Deferred to Planning

- [Affects R2][Technical] What albums should be in the seed data? Needs enough variety for genre/decade filter tests (at least 3 genres, 2 decades, some with tracklists, some without). Can query apps/backend/cue_the_music.db for sample data to create fixtures.
- [Affects R1][Technical] How should Playwright's `webServer` config start both frontend and backend? The existing config only starts the frontend preview. May need a script that starts both.
- [Affects R4][Technical] Should the Playwright config set `DATABASE_URL` and `TEST_MODE` env vars, or should a wrapper script handle it?

## Next Steps

→ `/ce:plan` for structured implementation planning
