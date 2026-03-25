---
title: "fix: Mount host controls on queue page after PIN verification"
type: fix
status: active
date: 2026-03-25
origin: docs/brainstorms/2026-03-25-vinyl-queue-app-requirements.md
---

# fix: Mount host controls on queue page after PIN verification

## Overview

After entering the correct host PIN on the queue page, no Discogs sync button, host mode indicator, or per-item queue controls appear. The components exist (`HostModeIndicator`, `SyncButton`, `HostQueueControls`) and are exported from `feature-host`, but **none are mounted in the component tree**. The Zustand store updates correctly — the rendering layer simply never consumes it on the queue page.

This violates R23, R24, R25, R26, and R27 from the requirements (see origin: `docs/brainstorms/2026-03-25-vinyl-queue-app-requirements.md`).

## Problem Statement

The PIN verification flow works end-to-end:
1. Tap lock icon in header (`AppShell.tsx:42-49`)
2. Enter PIN in `HostPinOverlay`
3. `useVerifyPin()` POSTs to `/api/host/verify-pin`
4. On success, `activateHostMode(token)` sets `isHostMode: true` in Zustand store

But after step 4, **nothing visual changes on the queue page** besides the lock icon toggling open/closed in the header. The host has no way to sync Discogs, promote albums to Now Playing, or remove queue items.

## Root Cause

`HostModeIndicator` and `HostQueueControls` are defined and exported from `libs/frontend/feature-host` but are never imported or rendered by any mounted component. `useTriggerSync` exists in `data-access-host` but is also unused.

## Proposed Solution

Mount host controls at the **app layer** (`QueuePage.tsx`) to avoid an NX boundary violation (`feature-queue` must not import `feature-host`). Create a `useQueuePage` hook to own the mutation wiring and store reads.

### Changes Required

#### 1. Create `useQueuePage` hook (`apps/frontend/src/app/pages/useQueuePage.ts`)

- Read `isHostMode` and `sessionToken` from `useHostStore` (granular selectors)
- Read `deactivateHostMode` from `useHostStore`
- Call `useTriggerSync({ token: sessionToken, onUnauthorized: deactivateHostMode })`
- Return `{ isHostMode, isSyncing: mutation.isPending, handleSync: mutation.mutate, handleDeactivate: deactivateHostMode }`

#### 2. Update `QueuePage.tsx` (`apps/frontend/src/app/pages/QueuePage.tsx`)

- Import `HostModeIndicator` from `@cue-the-music/feature-host`
- Use `useQueuePage` hook
- Conditionally render `HostModeIndicator` above `QueueView` when `isHostMode` is true
- Pass `isSyncing` and `onSync` props to `HostModeIndicator`

#### 3. Wire `HostQueueControls` into queue items

- `QueuePage.tsx` passes `isHostMode` down to `QueueView` as a prop (single level, within 2-level drill limit)
- `QueueView` renders `HostQueueControls` per queue item when `isHostMode` is true
- **Alternative:** If `QueueView` already reads items, `HostQueueControls` can be composed at the page level by wrapping queue items — investigate which approach respects the boundary better

#### 4. Add `onSuccess` invalidation to `useTriggerSync` (`libs/frontend/data-access-host/src/lib/host-mutations.ts`)

```typescript
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: albumKeys.all });
}
```

This complies with TanStack Query standard rule 5 and ensures the host's Crate view refreshes immediately after sync, rather than waiting for the SSE broadcast.

#### 5. Disable deactivation during sync

- `HostModeIndicator` Exit button should be disabled when `isSyncing` is true
- Prevents clearing the token mid-request, which would cause a spurious 403 on the in-flight sync mutation

## Technical Considerations

- **NX boundary:** `feature-queue` must not import `feature-host`. All wiring happens at the app layer in `QueuePage.tsx`. This preserves feature library independence.
- **Learnings — fetch headers:** Any new authenticated fetch calls must follow the destructured-headers pattern from `docs/solutions/integration-issues/api-fetch-headers-cors-lan-access.md` to avoid the `Content-Type` overwrite bug.
- **Learnings — generated types:** `IVerifyPinResponse`, `ISyncResponse`, and all API types must come from OpenAPI generation (`openapi-typescript`), never hand-written (see `docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md`).
- **SQLite concurrency:** Sync triggers long writes; WAL mode and busy timeout are already configured per `docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md`.

## Acceptance Criteria

- [ ] After entering the correct host PIN on the queue page, "HOST MODE ACTIVE" indicator, Sync button, and Exit button are visible (R23)
- [ ] Tapping the Sync button triggers a Discogs collection sync and shows a loading state (R27)
- [ ] After sync completes, the host's Crate view shows updated collection data without manual refresh (R34)
- [ ] Host can promote any queued album to Now Playing via inline controls (R24)
- [ ] Host can remove any album from the queue via inline controls (R25)
- [ ] Down-vote counts are prominently highlighted on queue items in host mode (R26)
- [ ] Host can deactivate host mode via the Exit button, which hides all host controls (R28)
- [ ] Exit button is disabled while a sync is in progress
- [ ] Expired/invalid token triggers graceful deactivation of host mode (no unhandled errors)
- [ ] No NX boundary violations: `feature-queue` does not import `feature-host`
- [ ] All API types used are generated from OpenAPI, not hand-written
- [ ] `useTriggerSync` has `onSuccess` invalidation of `albumKeys.all`

## Key Files

| File | Action | Purpose |
|------|--------|---------|
| `apps/frontend/src/app/pages/QueuePage.tsx` | Modify | Mount `HostModeIndicator`, wire mutations |
| `apps/frontend/src/app/pages/useQueuePage.ts` | Create | Hook owning host store reads + sync mutation |
| `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator.tsx` | Modify | Disable Exit while syncing |
| `libs/frontend/data-access-host/src/lib/host-mutations.ts` | Modify | Add `onSuccess` invalidation to `useTriggerSync` |
| `libs/frontend/feature-queue/src/lib/QueueView/QueueView.tsx` | Modify | Accept + render host controls per item |

## Dependencies & Risks

- **Risk:** `HostQueueControls` may need props not yet surfaced (e.g., per-item callbacks for promote/remove). Investigate the component's interface before implementing.
- **Risk:** If `QueueView` item rendering doesn't have a slot for host controls, it may need structural changes. Keep the diff minimal — a conditional render block, not a refactor.
- **Dependency:** `albumKeys` query key factory must be importable from wherever album queries are defined (likely `data-access-collection` or similar).

## Sources

- **Origin document:** [docs/brainstorms/2026-03-25-vinyl-queue-app-requirements.md](docs/brainstorms/2026-03-25-vinyl-queue-app-requirements.md) — R23, R24, R25, R26, R27, R28, R34
- **Learnings:** [docs/solutions/integration-issues/api-fetch-headers-cors-lan-access.md](docs/solutions/integration-issues/api-fetch-headers-cors-lan-access.md) — fetch header destructuring pattern
- **Learnings:** [docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md](docs/solutions/runtime-errors/queue-view-crash-type-schema-divergence.md) — generated types requirement
- **Learnings:** [docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md](docs/solutions/configuration-fixes/sqlite-async-fastapi-setup.md) — WAL mode for concurrent writes
