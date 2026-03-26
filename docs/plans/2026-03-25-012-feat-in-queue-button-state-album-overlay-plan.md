---
title: "feat: Show 'In Queue' disabled button when album already queued"
type: feat
status: active
date: 2026-03-25
---

# feat: Show "In Queue" disabled button when album already queued

When opening the album detail overlay, if the album is already in the queue (or is now playing), disable the request button and show "In Queue" — before the user attempts to request.

## Proposed Solution

In `useAlbumDetailOverlay`, check the cached queue state via `useQueryClient().getQueryData()`. If the album's ID appears in `queue[].album.id` or `now_playing?.album?.id`, set button to "In Queue" + disabled.

Falls back gracefully: if queue data isn't cached (user hasn't visited queue tab yet), the pre-check is skipped and the existing 409 error handling still works.

**Modify:** `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/useAlbumDetailOverlay.ts`

- Import `useQueryClient` and `queueKeys` from `@cue-the-music/data-access-queue`
- Import `IQueueState` type
- After getting `albumId`, peek at cached queue data
- Add `isInQueue` check: album ID matches any queue item's album.id or now_playing's album.id
- In the button state derivation, add `isInQueue` as the first check (before `alreadyInQueue`)

## Acceptance Criteria

- [ ] When album is in queue, button shows "In Queue" and is disabled on overlay open
- [ ] When album is now playing, button also shows "In Queue" and is disabled
- [ ] When queue data isn't cached, falls back to existing 409 error handling
- [ ] After requesting an album (success flow), overlay still auto-closes to queue

## Sources

- `libs/frontend/feature-crate/src/lib/AlbumDetailOverlay/useAlbumDetailOverlay.ts:68-85` — button state derivation
- `libs/frontend/data-access-queue/src/lib/queue-keys.ts` — `queueKeys.all`
- `libs/frontend/data-access-queue/src/lib/queue-types.ts` — `IQueueState` type
