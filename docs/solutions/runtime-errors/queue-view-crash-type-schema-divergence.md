---
title: "QueueView crash from hand-written types diverging from API response shape"
category: runtime-errors
date: 2026-03-25
severity: critical
tags:
  - openapi
  - openapi-typescript
  - type-generation
  - type-safety
  - tanstack-query
components:
  - libs/frontend/core-types/src/lib/queue.ts
  - libs/frontend/core-types/src/lib/album.ts
  - libs/frontend/core-types/src/lib/generated-api.ts
  - libs/frontend/data-access-queue/src/lib/queue-types.ts
  - libs/frontend/feature-queue/src/lib/QueueView/useQueueView.ts
commit: 6d95078
standards_violated:
  - "STANDARDS-backend.md rule 4: frontend types must be generated from OpenAPI schema"
---

# QueueView Crash — Hand-Written Types Diverged from API Schema

## Problem

`QueueView` crashed on render with `TypeError: Cannot read properties of undefined (reading 'length')`.

## Symptoms

- Runtime crash at `useQueueView.ts:11` — `data.items.length` where `data.items` is `undefined`
- React error boundary caught the crash and tried to recreate the component tree
- Affected all users, not just empty queues

## Investigation

1. **Stack trace** pointed to `data.items.length` in `useQueueView.ts:11`.
2. **Backend schema** returns `queue: list[QueueItemGetResponse]` — not `items`.
3. **Extracted full OpenAPI schema** and compared every response model against hand-written frontend types.
4. **Cataloged 9+ mismatches** across queue, album, and host types.
5. **Read standards** — STANDARDS-backend.md rule 4: "OpenAPI schema is the contract — frontend types are generated from it."

## Root Cause

Frontend types in `core-types` and `data-access-queue` were hand-written and had drifted from the backend schema. Types were also duplicated across two libraries (violating single source of truth). (auto memory [claude]: User's standard requires generated types — this was flagged during planning.)

### Mismatch Table

| Frontend (hand-written) | Backend (actual) | Issue |
|---|---|---|
| `items: IQueueItem[]` | `queue: QueueItemGetResponse[]` | Wrong field name |
| `up_count`, `down_count`, `my_vote` (flat) | `votes: { up_count, down_count, my_vote }` | Flat vs nested |
| `is_mine: boolean` | does not exist | Fabricated field |
| `album_count: number` | `albums_synced: number` | Wrong field name |
| `total: number` | `count: number` | Wrong field name |
| `decades: string[]` | `decades: number[]` | Wrong element type |
| `genre_tags: string[]` | `genre_tags: string[] \| null` | Missing nullable |
| `style_tags: string[]` | `style_tags: string[] \| null` | Missing nullable |
| `tracklist: ITrack[]` | `tracklist: Record<string, string>[]` | Wrong item type |

## Solution

### Step 1: Install openapi-typescript and export schema

```bash
npm install -D openapi-typescript

# Export schema from FastAPI app (no running server needed)
cd apps/backend && uv run python -c "
import json
from cue_the_music.main import app
with open('../../libs/frontend/core-types/openapi.json', 'w') as f:
    json.dump(app.openapi(), f, indent=2)
"

# Generate TypeScript types
npx openapi-typescript libs/frontend/core-types/openapi.json \
  -o libs/frontend/core-types/src/lib/generated-api.ts
```

### Step 2: Replace hand-written types with aliases

```ts
// libs/frontend/core-types/src/lib/queue.ts
import type { components } from './generated-api';

export type IQueueState = components['schemas']['QueueStateResponse'];
export type IQueueItem = components['schemas']['QueueItemGetResponse'];
export type INowPlaying = components['schemas']['NowPlayingGetResponse'];
export type IAlbumSummary = components['schemas']['AlbumSummary'];
export type IVoteGetResponse = components['schemas']['VoteGetResponse'];
export type IVerifyPinResponse = components['schemas']['HostPinVerifyResponse'];
export type ISyncResponse = components['schemas']['CollectionSyncTriggerResponse'];
```

### Step 3: Remove duplicate types

Replace `data-access-queue/queue-types.ts` with re-exports from `@cue-the-music/core-types`.

### Step 4: Update all consumers

```ts
// data.items → data.queue
const hasItems = data.queue.length > 0;

// Flat votes → nested votes
<VoteControls
  downCount={item.votes.down_count}
  upCount={item.votes.up_count}
  isUpVoted={item.votes.my_vote === 1}
/>

// albumData.total → albumData.count
const total = albumData.count;

// Null-safe tag spread
const allTags = [...(album.genre_tags ?? []), ...(album.style_tags ?? [])];

// cover_art_url → cover_art_thumbnail_url (AlbumSummary doesn't have full URL)
src={album.cover_art_thumbnail_url}
```

## Prevention

- **Never hand-write types that mirror API responses** — always generate from the OpenAPI schema.
- **CI freshness check**: Regenerate types in CI and diff against committed file. Fail if they differ.
  ```bash
  npx openapi-typescript /tmp/openapi.json -o /tmp/generated-api.ts
  diff libs/frontend/core-types/src/lib/generated-api.ts /tmp/generated-api.ts
  ```
- **Single source of truth**: All API types live in `core-types` only. Data-access libraries re-export, never redefine.
- **Lint for shadow types**: Grep for `interface` or `type` declarations in data-access libs that match generated type names.

## Key Insight

Hand-written types that mirror an API schema are a maintenance liability. They will drift. The OpenAPI spec is already the contract between frontend and backend — use codegen to enforce it. The cost of setting up `openapi-typescript` is 5 minutes; the cost of debugging type drift is hours.

## Cross-References

- Standard: `docs/standards/STANDARDS-backend.md` rule 4
- Plan: `docs/plans/2026-03-25-003-fix-queue-view-empty-array-crash-plan.md`
