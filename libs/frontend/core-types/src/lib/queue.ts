/**
 * Queue, vote, and host API types — derived from the generated OpenAPI schema.
 * Do not hand-write API response types; regenerate from the backend instead.
 */

import type { components } from './generated-api';

/** Full queue state response from GET /api/queue. */
export type IQueueState = components['schemas']['QueueStateResponse'];

/** A single queue item with album info and vote state. */
export type IQueueItem = components['schemas']['QueueItemGetResponse'];

/** Minimal album info embedded in queue responses. */
export type IAlbumSummary = components['schemas']['AlbumSummary'];

/** The currently playing album. */
export type INowPlaying = components['schemas']['NowPlayingGetResponse'];

/** Vote counts and the current client's vote on a queue item. */
export type IVoteGetResponse = components['schemas']['VoteGetResponse'];

/** Response from POST /api/host/verify-pin. */
export type IVerifyPinResponse = components['schemas']['HostPinVerifyResponse'];

/** Response from POST /api/host/sync. */
export type ISyncResponse = components['schemas']['CollectionSyncTriggerResponse'];

/** Request body for PUT /api/queue/{id}/vote. */
export type IVoteCastRequest = components['schemas']['VoteCastRequest'];
