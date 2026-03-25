import type { IAlbum } from '@cue-the-music/core-types';

/** A single item in the queue. */
export interface IQueueItem {
  /** Album details */
  album: IAlbum;
  /** Down-vote count */
  down_count: number;
  /** Unique queue item ID */
  id: number;
  /** Whether this request was made by the current client */
  is_mine: boolean;
  /** Current client's vote: 1 (up), -1 (down), or null (no vote) */
  my_vote: 1 | -1 | null;
  /** IP of the guest who requested this album */
  requested_by_ip: string;
  /** Up-vote count */
  up_count: number;
}

/** The currently playing album, if any. */
export interface INowPlaying {
  /** Album details */
  album: IAlbum;
  /** Queue item ID */
  id: number;
  /** Timestamp when playback started */
  started_at: string;
}

/** Full queue state returned by GET /api/queue. */
export interface IQueueState {
  /** Total number of items in the queue (excluding now playing) */
  count: number;
  /** Ordered list of queued items */
  items: IQueueItem[];
  /** Currently playing album, or null */
  now_playing: INowPlaying | null;
}

/** Vote direction for PUT /api/queue/{id}/vote. */
export interface IVoteBody {
  value: 1 | -1;
}
