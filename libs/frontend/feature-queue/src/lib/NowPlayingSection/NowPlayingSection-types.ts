import type { INowPlaying } from '@cue-the-music/data-access-queue';

export interface INowPlayingSectionProps {
  /** The currently playing album, or null if nothing is playing */
  nowPlaying: INowPlaying | null;
}

export interface IUseNowPlayingSectionReturn {
  /** Whether something is currently playing */
  isPlaying: boolean;
}
