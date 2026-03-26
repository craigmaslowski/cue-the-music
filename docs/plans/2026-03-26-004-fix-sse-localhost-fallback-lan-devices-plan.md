---
title: "fix: SSE connects to localhost instead of LAN host on mobile devices"
type: fix
status: active
date: 2026-03-26
---

# fix: SSE connects to localhost instead of LAN host on mobile devices

## Problem

On mobile Safari (and any LAN device), the SSE EventSource connects to `http://localhost:8000/api/events` instead of the host machine's LAN IP. This means no real-time updates — queue changes from other users don't appear until manual refresh.

**Root cause:** `useSSEProvider` defaults to `http://localhost:8000` when `VITE_API_BASE_URL` isn't set. Meanwhile `apiFetch` correctly derives the base URL from `window.location.hostname`. The two URL strategies are inconsistent.

## Proposed Solution

**Modify:** `libs/frontend/feature-sse/src/lib/SSEProvider/useSSEProvider.ts`

Change `DEFAULT_URL` to match the `apiFetch` pattern:

```typescript
const DEFAULT_URL =
  import.meta.env?.VITE_API_BASE_URL ??
  `http://${window.location.hostname}:8000`;
```

One-line fix. No other files need changes.

## Acceptance Criteria

- [ ] Mobile Safari receives SSE events from the host machine
- [ ] Queue updates from other users appear in real-time on LAN devices
- [ ] Desktop Chrome behavior unchanged
- [ ] SSE reconnection still works after disconnects
