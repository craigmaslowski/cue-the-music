/**
 * Re-export queue types from the single source of truth in core-types.
 * Vote direction type alias for mutation hooks.
 */

export type {
  INowPlaying,
  IQueueItem,
  IQueueState,
  IVoteCastRequest as IVoteBody,
} from '@cue-the-music/core-types';
