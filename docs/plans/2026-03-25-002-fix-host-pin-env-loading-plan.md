---
title: "fix: Host PIN verification broken by missing Content-Type header"
type: fix
status: completed
date: 2026-03-25
---

# fix: Host PIN verification broken by missing Content-Type header

Host PIN verification always fails (422) regardless of the PIN entered. A secondary issue prevents `.env` loading when the backend is started from the wrong CWD.

## Root Cause 1 — `apiFetch` headers overwrite (blocks ALL host endpoints)

`libs/frontend/data-access-collection/src/lib/api-client.ts:10-16`:

```js
const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',  // ← set here
      ...options?.headers,
    },
    ...options,  // ← options.headers OVERWRITES the above
  });
```

`hostFetch` always passes a `headers` object (even empty `{}`), so `...options` at the end replaces the entire `headers` property. The request is sent without `Content-Type: application/json`.

**Confirmed via curl:** FastAPI returns **422 Unprocessable Entity** when Content-Type is missing/wrong — it does not attempt JSON body parsing.

```
POST /api/host/verify-pin  Content-Type: application/json  → 200 ✓
POST /api/host/verify-pin  Content-Type: text/plain         → 422 ✗
POST /api/host/verify-pin  (no Content-Type)                → 422 ✗
```

This affects ALL `hostFetch` calls: verify-pin, promote, clear, remove, sync.

## Root Cause 2 — `.env` relative path (latent, masks real PIN)

`apps/backend/src/cue_the_music/config.py:14`: `env_file=".env"` resolves relative to CWD, not to `config.py`. If the backend isn't started from `apps/backend/`, the `.env` is not found and `HOST_PIN` silently defaults to `"0000"`.

## Acceptance Criteria

- [ ] `apiFetch` merges headers correctly — `Content-Type` is always present for JSON requests
- [ ] `hostFetch` calls include `Content-Type: application/json`
- [ ] `env_file` resolves to `apps/backend/.env` regardless of CWD
- [ ] Startup logs which `.env` file was loaded (or warns if none found)
- [ ] `get_settings()` is cached so `.env` is parsed once, not per-request
- [ ] Existing backend tests pass
- [ ] PIN verification works with the correct PIN (`0808`)

## MVP

### Fix 1: `libs/frontend/data-access-collection/src/lib/api-client.ts`

Destructure `headers` out of `options` so they merge instead of overwrite:

```ts
export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
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

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({
      detail: response.statusText,
    })) as { detail?: string };
    throw new ApiError(response.status, errorBody.detail ?? response.statusText);
  }

  return response.json() as Promise<T>;
}
```

### Fix 2: `apps/backend/src/cue_the_music/config.py`

```python
"""Application settings loaded from environment variables / .env file."""

import logging
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

# Resolve .env relative to the backend package root (three .parent hops from this file)
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Central configuration for Cue the Music."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DISCOGS_TOKEN: str
    DISCOGS_USERNAME: str
    HOST_PIN: str = "0000"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """FastAPI dependency that provides application settings (cached)."""
    settings = Settings()  # type: ignore[call-arg]
    if _ENV_FILE.is_file():
        logger.info("Loaded settings from %s", _ENV_FILE)
    else:
        logger.warning("No .env file found at %s — using env vars / defaults", _ENV_FILE)
    return settings
```

### Path math verification

`__file__` = `.../apps/backend/src/cue_the_music/config.py`
`.parent` × 3 = `.../apps/backend/` → `.env` at `.../apps/backend/.env` ✓

## Sources

- Frontend bug: `libs/frontend/data-access-collection/src/lib/api-client.ts:10-16`
- Host fetch wrapper: `libs/frontend/data-access-host/src/lib/host-fetch.ts:19`
- Backend config: `apps/backend/src/cue_the_music/config.py:14`
- .env location: `apps/backend/.env`
- NX serve CWD: `apps/backend/project.json:72`
