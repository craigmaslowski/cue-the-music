---
title: "Host mode UI components never rendered after PIN verification"
category: ui-bugs
date: 2026-03-25
severity: critical
component: "QueuePage, HostModeIndicator, SyncButton, HostQueueControls, useTriggerSync"
tags: [host-mode, zustand, dead-code, missing-integration, queue-page, discogs-sync, tanstack-query, render-prop, nx-boundary]
related_issues: []
---

# Host mode UI components never rendered after PIN verification

## Problem

After entering the correct host PIN on the queue page, no visual change occurred — no "HOST MODE ACTIVE" indicator, no Discogs sync button, no per-item Play/Remove controls. The Zustand store updated correctly (`isHostMode: true`), but the queue page rendered identically for hosts and guests.

This broke requirements R23 (host controls inline on queue), R24 (promote to Now Playing), R25 (remove from queue), R26 (down-vote skip signals), and R27 (trigger Discogs sync).

## Root Cause

`HostModeIndicator` (sync button + status + exit) and `HostQueueControls` (per-item play/remove/skip-signal) were fully implemented and exported from `libs/frontend/feature-host`, but **never imported or rendered anywhere in the component tree**. `QueuePage.tsx` was a thin wrapper:

```tsx
// Before fix — no host wiring at all
export function QueuePage() {
  return <QueueView />;
}
```

Additionally, `useTriggerSync` existed in `data-access-host` but was never called and lacked `onSuccess` cache invalidation.

The app compiled and ran without errors because the components were purely additive — their absence caused no type errors or runtime failures.

## Investigation

1. Verified PIN verification flow worked end-to-end (POST `/api/host/verify-pin` returns token, `activateHostMode(token)` sets Zustand state)
2. Searched the import graph for consumers of `HostModeIndicator` and `HostQueueControls` — found zero
3. Confirmed `QueuePage.tsx` rendered only `<QueueView />` with no host-mode awareness
4. Identified NX boundary constraint: `feature-queue` cannot import `feature-host` (would create feature-to-feature dependency)
5. Confirmed `useTriggerSync` had no `onSuccess` handler (TanStack Query standard violation)

## Solution

### 1. Created `useQueuePage.ts` hook at the app layer

```ts
// apps/frontend/src/app/pages/useQueuePage.ts
const isHostMode = useHostStore((s) => s.isHostMode);
const sessionToken = useHostStore((s) => s.sessionToken);
const deactivateHostMode = useHostStore((s) => s.deactivateHostMode);

const mutationOptions = {
  onUnauthorized: deactivateHostMode, // graceful token-expiry handling
  token: sessionToken,
};

const syncMutation = useTriggerSync(mutationOptions);
const promoteMutation = usePromoteToNowPlaying(mutationOptions);
const removeMutation = useRemoveQueueItem(mutationOptions);
```

### 2. Updated `QueuePage.tsx` to mount host controls

```tsx
// apps/frontend/src/app/pages/QueuePage.tsx
<>
  <HostModeIndicator isSyncing={isSyncing} onSync={handleSync} />
  <QueueView renderItemActions={renderItemActions} />
</>
```

### 3. Render prop pattern to cross the NX boundary

Added an optional `renderItemActions` prop through the `feature-queue` component chain (`QueueView` -> `UpNextList` -> `QueueItem`):

```ts
// Added to QueueView, UpNextList, QueueItem prop types:
renderItemActions?: (item: IQueueItem) => ReactNode;

// QueueItem renders it at the end of its JSX:
{renderItemActions?.(item)}
```

The app layer creates the render function that returns `<HostQueueControls>` — `feature-queue` never imports `feature-host`.

### 4. Added `onSuccess` invalidation to `useTriggerSync`

```ts
onSuccess: () => {
  void queryClient.invalidateQueries({ queryKey: albumKeys.all });
}
```

### 5. Disabled Exit button while syncing

Added `disabled={isSyncing}` to the Exit button in `HostModeIndicator` with `_disabled` Panda CSS styling, preventing token clearing mid-request.

## Key Insight

The render prop pattern is the correct way to inject components from one NX feature library into another's rendering tree without creating a forbidden feature-to-feature import. All cross-feature wiring belongs at the **app layer**, which is allowed to import from any library. This keeps the dependency graph acyclic and each feature independently testable.

## Files Changed

| File | Change |
|------|--------|
| `apps/frontend/src/app/pages/useQueuePage.ts` | Created — hook owning host store reads + mutations |
| `apps/frontend/src/app/pages/QueuePage.tsx` | Mount `HostModeIndicator`, wire render prop |
| `libs/frontend/data-access-host/src/lib/host-mutations.ts` | Added `onSuccess` invalidation to `useTriggerSync` |
| `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator.tsx` | Disable Exit while syncing |
| `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator-elements.ts` | `_disabled` styling |
| `libs/frontend/feature-queue/src/lib/QueueView/QueueView-types.ts` | `renderItemActions` prop |
| `libs/frontend/feature-queue/src/lib/QueueView/QueueView.tsx` | Pass render prop through |
| `libs/frontend/feature-queue/src/lib/UpNextList/UpNextList-types.ts` | `renderItemActions` prop |
| `libs/frontend/feature-queue/src/lib/UpNextList/UpNextList.tsx` | Pass render prop through |
| `libs/frontend/feature-queue/src/lib/QueueItem/QueueItem-types.ts` | `renderItemActions` prop |
| `libs/frontend/feature-queue/src/lib/QueueItem/QueueItem.tsx` | Call `renderItemActions?.(item)` |

## Prevention

### Testing

- **E2E smoke test:** After PIN entry, assert host-only UI elements (sync button, "Host Mode Active" label, per-item Play/Remove buttons) are visible. This single test would have caught this bug.
- **Store-to-UI subscription test:** Render `QueuePage`, programmatically set `isHostMode: true` in Zustand, assert conditional children appear.
- **Mutation wiring test:** For every mutation hook, verify it is invoked by a UI interaction and its `onSuccess` invalidates the correct query keys.

### Code Review Checklist

- For every new component in a PR, confirm it appears in a parent's JSX — not just in a barrel export.
- If a PR modifies store state, verify at least one component subscribes to the changed slice.
- Every `useMutation` hook must have `onSuccess`/`onError` handling and must be wired to a trigger.

### Development Workflow

- **Wire top-down first:** Before building leaf components, mount a placeholder in the route/page component so the mount point exists from the first commit.
- **Definition of Done includes "mounted and visible":** A component is not done when it compiles and exports; it is done when it renders on screen under the correct conditions.

### NX Monorepo Checks

- Use `knip` or `ts-prune` to detect unused exports from feature libraries — a library barrel export with zero consumers is suspect.
- Use `nx graph` to verify feature libraries are depended upon by an app target.

## Related Solutions

- [API fetch headers / CORS / LAN access](../integration-issues/api-fetch-headers-cors-lan-access.md) — prerequisite fix for PIN verification POST requests
- [QueueView crash from type schema divergence](../runtime-errors/queue-view-crash-type-schema-divergence.md) — generated types used by queue page and host controls

## Plan Reference

- [docs/plans/2026-03-25-004-fix-host-controls-not-mounted-on-queue-page-plan.md](../../plans/2026-03-25-004-fix-host-controls-not-mounted-on-queue-page-plan.md)
