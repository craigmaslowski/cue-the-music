---
title: "fix: QueueView crash — generate frontend types from OpenAPI schema"
type: fix
status: completed
date: 2026-03-25
---

# fix: QueueView crash — generate frontend types from OpenAPI schema

`QueueView` throws `TypeError: Cannot read properties of undefined (reading 'length')` because hand-written frontend types don't match the backend's actual response shape. Per STANDARDS-backend.md rule 4: "OpenAPI schema is the contract — frontend types are generated from it."

## Root Cause

Frontend types in `core-types` and `data-access-queue` are hand-written and have drifted from the backend schema. Key mismatches:

| Field | Frontend (hand-written) | Backend (OpenAPI) |
|-------|------------------------|-------------------|
| Queue items field | `items` | `queue` |
| Queue state count | missing | `count: number` |
| Vote data | flat: `up_count`, `down_count`, `my_vote` | nested: `votes: { up_count, down_count, my_vote }` |
| Ownership | `is_mine: boolean` | does not exist |
| Sync response count | `album_count` | `albums_synced` |
| Album list total | `total` | `count` |
| Filter decades | `string[]` | `number[]` |
| Genre/style tags | `string[]` | `string[] \| null` |
| Tracklist item type | `ITrack` (typed) | `Record<string, string>` (dict) |

Additionally, `data-access-queue/queue-types.ts` duplicates types already in `core-types` (violating single source of truth).

## Proposed Solution

1. **Set up `openapi-typescript`** to generate types from the backend's `/openapi.json` endpoint
2. **Replace hand-written types** in `core-types` with generated types (or re-export from generated)
3. **Remove duplicate types** from `data-access-queue/queue-types.ts`
4. **Update all consumers** to use the correct field names and nested shapes
5. **Add an NX target** for type generation so it's repeatable

## Acceptance Criteria

- [ ] `openapi-typescript` is installed and configured with an NX target
- [ ] Generated types match the backend OpenAPI schema exactly
- [ ] `core-types` exports generated types (no hand-written API response types)
- [ ] Duplicate types in `data-access-queue/queue-types.ts` are removed
- [ ] All consumers updated to correct field names (`queue` not `items`, nested `votes`, etc.)
- [ ] `QueueView` renders without error for empty and non-empty queues
- [ ] Frontend typecheck passes
- [ ] No runtime errors in browser console

## Files to Change

### New/Modified infrastructure
- `package.json` — add `openapi-typescript` dev dependency
- `libs/frontend/core-types/project.json` — add `generate` NX target
- `libs/frontend/core-types/src/lib/generated.ts` — output from openapi-typescript

### Types to replace
- `libs/frontend/core-types/src/lib/queue.ts` — replace hand-written types with re-exports from generated
- `libs/frontend/core-types/src/lib/album.ts` — replace hand-written types with re-exports from generated
- `libs/frontend/core-types/src/index.ts` — update exports

### Duplicate types to remove
- `libs/frontend/data-access-queue/src/lib/queue-types.ts` — remove, import from `@cue-the-music/core-types` instead

### Consumers to update (use `queue` instead of `items`, nested `votes`, etc.)
- `libs/frontend/feature-queue/src/lib/QueueView/useQueueView.ts` — `data.queue` not `data.items`
- `libs/frontend/feature-queue/src/lib/QueueView/QueueView.tsx` — `data.queue` not `data.items`
- `libs/frontend/data-access-queue/src/lib/queue-queries.ts` — import types from core-types
- Any other consumers of `IQueueItem` that access flat vote fields or `is_mine`
- Any consumers of `ISyncResponse.album_count` → `albums_synced`
- Any consumers of `IAlbumListResponse.total` → `count`

## Sources

- Standard: STANDARDS-backend.md rule 4 — "OpenAPI schema is the contract — frontend types are generated from it"
- Standard: STANDARDS-general.md rule 5 — "Shared types live in dedicated core libraries"
- Stack trace: `useQueueView.ts:11` — `data.items.length` on undefined
- Backend schema: `apps/backend/src/cue_the_music/schemas/queue_schemas.py:56-61`
- Core types: `libs/frontend/core-types/src/lib/queue.ts`
- Duplicate types: `libs/frontend/data-access-queue/src/lib/queue-types.ts`
