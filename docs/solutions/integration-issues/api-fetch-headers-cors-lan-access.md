---
title: "Host PIN verification and LAN access failures"
category: integration-issues
date: 2026-03-25
severity: critical
tags:
  - cors
  - fastapi
  - fetch-api
  - headers
  - lan-access
  - pydantic-settings
  - vite
components:
  - libs/frontend/data-access-collection/src/lib/api-client.ts
  - apps/backend/src/cue_the_music/main.py
  - apps/backend/src/cue_the_music/config.py
  - apps/frontend/vite.config.mts
commit: 95d4da7
---

# Host PIN Verification and LAN Access Failures

## Problem

Host PIN verification returned 422 for both the correct PIN and the default. All other API calls from LAN guests also failed.

## Symptoms

- Host PIN rejected for both real PIN (0808) and default (0000)
- All API calls from guests on LAN failed
- FastAPI returned 422 Unprocessable Entity on POST requests from the frontend

## Investigation

1. **Backend tests passed** — all 113 tests green, confirming endpoint logic was correct.
2. **Curl isolated the bug** — `Content-Type: application/json` produced 200; omitting it produced 422. FastAPI requires the header to parse JSON bodies.
3. **Traced the fetch wrapper** — `apiFetch` spread `...options` after the `headers` object, silently overwriting `Content-Type`.
4. **Checked CORS** — `allow_origins` was `["http://localhost:4200"]`, blocking LAN IPs.
5. **Checked Vite** — dev server bound to `localhost`, unreachable from other devices.
6. **Checked config.py** — `env_file=".env"` resolved relative to CWD, not the config file.

## Root Cause

### Primary: Object spread ordering in `apiFetch`

```ts
// BEFORE (broken) — ...options overwrites the headers object
const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,  // options.headers REPLACES the above
});
```

`hostFetch` always passed a `headers` property in options (even empty `{}`), so `Content-Type` was always lost for host endpoints. FastAPI requires `Content-Type: application/json` to parse JSON request bodies.

### Secondary

- **CORS origins** restricted to localhost — LAN guests blocked by browser CORS.
- **Vite host** bound to `localhost` — frontend unreachable from other devices.
- **`env_file=".env"`** resolved relative to CWD — `.env` silently not found depending on launch method, defaulting `HOST_PIN` to `"0000"`.
- **`API_BASE_URL`** hardcoded to `localhost:8000` — guest phones couldn't reach the backend.

## Solution

### Fix 1: Destructure headers before spreading

```ts
const { headers: optionHeaders, ...rest } = options ?? {};
const response = await fetch(url, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(optionHeaders instanceof Headers
        ? Object.fromEntries(optionHeaders.entries())
        : optionHeaders),
    },
});
```

### Fix 2: Open CORS for LAN access

```python
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"],
    allow_methods=["*"],
    allow_origins=["*"],  # Safe for local-network app with no credentials
)
```

### Fix 3: Bind Vite to all interfaces

```ts
server: { port: 4200, host: '0.0.0.0' },
preview: { port: 4200, host: '0.0.0.0' },
```

### Fix 4: Derive API base URL from hostname

```ts
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  `http://${window.location.hostname}:8000`;
```

### Fix 5: Absolute env_file path with caching

```python
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    if _ENV_FILE.is_file():
        logger.info("Loaded settings from %s", _ENV_FILE)
    else:
        logger.warning("No .env file found at %s", _ENV_FILE)
    return settings
```

## Prevention

- **Unit test header preservation**: Test that `apiFetch` with custom headers still includes `Content-Type: application/json`.
- **Never hardcode localhost** in a LAN-accessible app — derive from environment or `window.location`.
- **Anchor `env_file` to `__file__`** instead of relying on CWD.
- **Log startup config** — print resolved `.env` path and CORS origins at boot so misconfigurations are immediately visible.
- **CI smoke test** — verify the backend is reachable on `0.0.0.0` after startup.

## Key Insight

The object spread `{ defaults, ...options }` pattern is a common source of silent overwrites in JavaScript. When `options` contains a key that matches a default (like `headers`), the default is replaced entirely — not merged. Always destructure conflicting keys out of options before spreading.

## Cross-References

- Plan: `docs/plans/2026-03-25-002-fix-host-pin-env-loading-plan.md`
