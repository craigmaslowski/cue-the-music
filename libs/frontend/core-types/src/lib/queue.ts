/** A queue item as returned by the backend API. */
export interface IQueueItem {
  album: IQueueAlbum;
  created_at: string;
  down_count: number;
  id: number;
  my_vote: -1 | 1 | null;
  requested_by_ip: string;
  up_count: number;
}

/** Embedded album data within a queue item. */
export interface IQueueAlbum {
  artist: string;
  cover_art_thumbnail_url: string | null;
  id: number;
  title: string;
  year: number | null;
}

/** The currently playing album. */
export interface INowPlaying {
  album: IQueueAlbum;
  promoted_at: string;
}

/** Full queue state response from GET /api/queue. */
export interface IQueueResponse {
  items: IQueueItem[];
  now_playing: INowPlaying | null;
}

/** Response from POST /api/host/verify-pin. */
export interface IVerifyPinResponse {
  token: string;
}

/** Response from POST /api/host/sync. */
export interface ISyncResponse {
  album_count: number;
  status: string;
}
