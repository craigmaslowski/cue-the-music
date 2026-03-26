---
title: "fix: UI improvements — overlay auto-close, album count, host mode padding"
type: fix
status: completed
date: 2026-03-25
---

# fix: UI improvements — overlay auto-close, album count, host mode padding

Three targeted UI fixes in a single batch.

## 1. Auto-close overlay and navigate to queue after requesting

After a successful album request, close the overlay and switch to the queue tab so the user sees their request in the queue.

**Modify:** `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/useAlbumDetailOverlay.ts`

- Import `useNavigate` from `@tanstack/react-router`
- In `handleRequest` → `onSuccess`: after setting `requestSuccess(true)`, add a short delay (e.g., 800ms) so the user sees "Requested" feedback, then call `handleClose()` and `navigate({ to: '/queue' })`

## 2. Display album count under filter pills

Show a count like "142 albums" or "12 of 142 albums" (when filters active) below the filter chips on the crate screen.

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-types.ts`

- Add `filteredCount: number` and `totalCount: number` props

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch.tsx`

- Render count text below the filters div: `"{filteredCount} of {totalCount} albums"` when filters active, or `"{totalCount} albums"` when no filters

**Modify:** `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch-elements.ts`

- Add `countStyles` for the count text (small, muted color, left-aligned with padding)

**Modify:** `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx`

- Pass `filteredCount={filteredAlbums.length}` and `totalCount={allAlbums.length}` to `CollectionSearch`

## 3. Fix host mode styling — add padding

**Modify:** `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator-elements.ts`

- `rootStyles`: increase padding (e.g., `padding: '4'`)
- `deactivateButtonStyles`: increase padding (e.g., `padding: '2 3'`)

**Modify:** `libs/frontend/feature-host/src/lib/HostQueueControls/HostQueueControls-elements.ts`

- `promoteButtonStyles`: increase padding (e.g., `padding: '2 4'`)
- `removeButtonStyles`: increase padding (e.g., `padding: '2 4'`)

**Modify:** `libs/frontend/feature-host/src/lib/SyncButton/SyncButton-elements.ts`

- `buttonStyles`: increase padding (e.g., `padding: '2 4'`)

## Acceptance Criteria

- [ ] After requesting an album, overlay closes and queue tab is shown (with brief "Requested" feedback visible first)
- [ ] Album count displayed under filter pills on crate screen
- [ ] Count shows "X of Y albums" when filters active, "Y albums" when no filters
- [ ] Host mode indicator bar has comfortable padding
- [ ] All host mode buttons (Play, Remove, Sync, Exit) have comfortable tap targets
- [ ] `npx nx typecheck @cue-the-music/frontend` passes

## Sources

- `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/useAlbumDetailOverlay.ts:46-65` — request mutation onSuccess
- `libs/frontend/feature-crate/src/lib/CollectionSearch/CollectionSearch.tsx` — filter UI
- `libs/frontend/feature-crate/src/lib/CrateView/CrateView.tsx` — passes data to CollectionSearch
- `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator-elements.ts` — indicator bar styles
- `libs/frontend/feature-host/src/lib/HostQueueControls/HostQueueControls-elements.ts` — queue item button styles
- `libs/frontend/feature-host/src/lib/SyncButton/SyncButton-elements.ts` — sync button styles
- `apps/frontend/src/app/AppShell/useAppShell.ts` — tab navigation pattern via `useNavigate`
