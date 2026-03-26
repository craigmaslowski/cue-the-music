---
title: "feat: Auto-upvote album when requester adds it to queue"
type: feat
status: active
date: 2026-03-26
---

# feat: Auto-upvote album when requester adds it to queue

When a user requests an album, automatically cast an upvote on their behalf. The requester obviously wants the album played — their vote should count.

## Proposed Solution

Backend-only change in `QueueService.request_album()`.

**Modify:** `apps/backend/src/cue_the_music/services/queue_service.py`

After `add_to_queue()`, call `vote_repo.upsert_vote(item.id, ip, 1)` to cast an upvote. Update the response to reflect `up_count=1, my_vote=1`.

```python
# After adding to queue
item = await self._queue_repo.add_to_queue(album_id, ip)

# Auto-upvote by the requester
await self._vote_repo.upsert_vote(item.id, ip, 1)

response = QueueItemGetResponse(
    ...
    votes=VoteGetResponse(up_count=1, down_count=0, my_vote=1),
    ...
)
```

No frontend changes needed — the response already drives the vote display.

## Acceptance Criteria

- [ ] Newly queued album starts with 1 upvote from the requester
- [ ] Queue state shows `my_vote: 1` for the requester on their item
- [ ] Other users see `up_count: 1, my_vote: null` on the item
- [ ] Requester can still change their vote after queueing
- [ ] Backend tests pass

## Sources

- `apps/backend/src/cue_the_music/services/queue_service.py:78-99` — request_album method
- `apps/backend/src/cue_the_music/repositories/vote_repository.py:23-36` — upsert_vote
