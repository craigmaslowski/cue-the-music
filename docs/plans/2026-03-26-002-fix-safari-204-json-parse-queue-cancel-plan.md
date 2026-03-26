---
title: "fix: Queue not updating after cancel in Safari — 204 JSON parse error"
type: fix
status: active
date: 2026-03-26
---

# fix: Queue not updating after cancel in Safari — 204 JSON parse error

## Problem

Non-host user cancels their own queue item on mobile Safari → queue list doesn't update. Works on desktop Chrome.

## Root Cause

`apiFetch()` unconditionally calls `response.json()` after a successful response. The `DELETE /api/queue/{id}` endpoint returns **204 No Content** (empty body). Safari throws `SyntaxError: Unexpected end of JSON input` when parsing an empty body, while Chrome silently returns undefined. This causes the TanStack Query mutation to error instead of succeed, so `onSuccess` (which calls `invalidateQueries`) never fires.

Same issue affects ALL 204 endpoints: `DELETE /api/host/now-playing`, `DELETE /api/host/queue`, `DELETE /api/host/queue/{id}`, `POST /api/host/now-playing`, `DELETE /api/queue/{id}/vote`.

## Proposed Solution

**Modify:** `libs/frontend/data-access-collection/src/lib/api-client.ts`

Check for 204 status (or empty content-length) before calling `response.json()`:

```typescript
if (response.status === 204) {
  return undefined as T;
}
return response.json() as Promise<T>;
```

One-line fix in `apiFetch`. No other files need changes — all mutations already use `apiFetch`.

## Acceptance Criteria

- [ ] Cancel request works on mobile Safari — queue updates immediately
- [ ] All other 204 endpoints (host promote, clear, remove, vote delete) work on Safari
- [ ] Chrome behavior unchanged
