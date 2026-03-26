---
title: "fix: Hide cancel button for queue items not owned by current user"
type: fix
status: active
date: 2026-03-26
---

# fix: Hide cancel button for queue items not owned by current user

## Problem

The cancel (✕) button on queue items is shown to all users, not just the user who queued the album. Non-host users who didn't request an album see a remove button that will fail with a 404 when clicked (the backend already enforces IP-based ownership on `DELETE /api/queue/{id}`).

## Proposed Solution

Add `is_mine: bool` to `QueueItemGetResponse` (same pattern as `my_vote` on votes). Computed server-side by comparing `requested_by_ip == client_ip`. Frontend conditionally renders the cancel button only when `is_mine` is true.

### Backend

**Modify:** `apps/backend/src/cue_the_music/schemas/queue_schemas.py`

Add `is_mine: bool` to `QueueItemGetResponse`.

**Modify:** `apps/backend/src/cue_the_music/services/queue_service.py`

- In `get_queue_state()`: set `is_mine=item.requested_by_ip == client_ip` when building each `QueueItemGetResponse`
- In `request_album()`: set `is_mine=True` (the requester always owns their own request)

**Regenerate frontend types** from updated OpenAPI schema.

### Frontend

**Modify:** `libs/frontend/feature-queue/src/lib/QueueItem/QueueItem.tsx`

Conditionally render cancel button: `{item.is_mine && <button ...>}`

### Tests

**Modify:** `apps/backend/tests/test_queue_endpoints.py`

- Verify `is_mine=true` on items requested by the current client
- Verify `is_mine=false` on items requested by a different IP (may need to mock IP)

## Acceptance Criteria

- [ ] Cancel button only shown on queue items the current user requested
- [ ] `is_mine` field present in queue state API response
- [ ] Requesting user sees `is_mine: true` on their own items
- [ ] Other users see `is_mine: false`
- [ ] Frontend types regenerated from OpenAPI
- [ ] Backend and frontend tests pass

## Sources

- `apps/backend/src/cue_the_music/schemas/queue_schemas.py:35-44` — QueueItemGetResponse
- `apps/backend/src/cue_the_music/services/queue_service.py:109-134` — get_queue_state builds response with client_ip
- `libs/frontend/feature-queue/src/lib/QueueItem/QueueItem.tsx:52-60` — unconditional cancel button render
