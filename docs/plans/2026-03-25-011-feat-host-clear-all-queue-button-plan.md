---
title: "feat: Host-only Clear All button to reset queue and now playing"
type: feat
status: active
date: 2026-03-25
---

# feat: Host-only Clear All button to reset queue and now playing

Add a "Clear All" button to the host mode indicator bar (left of Sync) that clears the entire queue and now playing in one action.

## Backend

### New: `DELETE /api/host/queue` endpoint

**Modify:** `apps/backend/src/cue_the_music/routers/host_queue_router.py`

Add a new endpoint protected by `HostAuthDep`:

```python
@router.delete("/queue", status_code=204)
async def clear_queue(
    _auth: HostAuthDep,
    service: Annotated[QueueService, Depends(get_queue_service)],
) -> None:
    """Clear all queue items and now playing."""
    await service.clear_queue()
```

### New: `clear_queue()` service method

**Modify:** `apps/backend/src/cue_the_music/services/queue_service.py`

Atomic operation that clears both queue items and now playing:

```python
async def clear_queue(self) -> None:
    """Clear all queue items and now playing."""
    await self._queue_repository.clear_all()
    await self._now_playing_repository.clear()
    await self._broadcaster.broadcast("queue_cleared", {})
```

### New: `clear_all()` repository method

**Modify:** `apps/backend/src/cue_the_music/repositories/queue_repository.py`

```python
async def clear_all(self) -> None:
    """Delete all queue items (cascades to votes)."""
    await self._session.execute(delete(QueueItem))
```

### Tests

**Modify:** `apps/backend/tests/test_album_endpoints.py` or create new test file

- Test `DELETE /api/host/queue` returns 204 and empties both queue and now playing
- Test returns 403 without valid host token
- Test works on already-empty queue (idempotent)

## Frontend

### New: `useClearQueue()` mutation hook

**Modify:** `libs/frontend/data-access-host/src/lib/host-mutations.ts`

```typescript
export function useClearQueue(options: IHostMutationOptions) {
  const queryClient = useQueryClient();
  return useMutation<unknown, ApiError, void>({
    mutationFn: () =>
      hostFetch('/api/host/queue', options.token, { method: 'DELETE' }, options.onUnauthorized),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queueKeys.all });
    },
  });
}
```

Export from barrel: `libs/frontend/data-access-host/src/index.ts`

### Add "Clear All" button to HostModeIndicator

**Modify:** `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator-types.ts`

Add `onClearQueue` callback prop.

**Modify:** `libs/frontend/feature-host/src/lib/HostModeIndicator/useHostModeIndicator.ts`

Wire up the `useClearQueue` mutation (or receive it as a prop — follow existing pattern where `onSync` is passed as prop from QueuePage).

**Modify:** `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator.tsx`

Add a "Clear All" button to the left of the Sync button in the actions row. Use a destructive/secondary style (pink/red border like the Remove button) to signal it's a destructive action.

**Modify:** `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator-elements.ts`

Add `clearAllButtonStyles` — pink/red outline pill matching `removeButtonStyles` from HostQueueControls.

**Modify:** `apps/frontend/src/app/pages/QueuePage.tsx`

Wire up `useClearQueue` mutation and pass `onClearQueue` handler to HostModeIndicator (follows the same pattern as `onSync`).

## Acceptance Criteria

- [ ] "Clear All" button visible in host mode indicator bar, left of Sync
- [ ] Clicking clears all queue items AND now playing in one API call
- [ ] Button styled as destructive (pink/red outline pill)
- [ ] Button disabled while clearing is in progress
- [ ] Requires valid host token (403 if invalid/missing)
- [ ] Works on empty queue (no error)
- [ ] Queue UI updates after clear (TanStack Query invalidation)
- [ ] Backend tests cover happy path, auth, and idempotent empty queue
- [ ] `npx nx typecheck @cue-the-music/frontend` passes
- [ ] `cd apps/backend && uv run pytest` passes

## Sources

- `apps/backend/src/cue_the_music/routers/host_queue_router.py` — existing host endpoints pattern
- `apps/backend/src/cue_the_music/services/queue_service.py` — service methods
- `apps/backend/src/cue_the_music/repositories/queue_repository.py` — repository pattern
- `apps/backend/src/cue_the_music/repositories/now_playing_repository.py:39-43` — existing `clear()` method
- `libs/frontend/data-access-host/src/lib/host-mutations.ts` — mutation pattern
- `libs/frontend/feature-host/src/lib/HostModeIndicator/HostModeIndicator.tsx` — button location
- `apps/frontend/src/app/pages/QueuePage.tsx` — wiring pattern (onSync)
