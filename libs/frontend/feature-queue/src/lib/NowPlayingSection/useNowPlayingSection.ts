import type {
  INowPlayingSectionProps,
  IUseNowPlayingSectionReturn,
} from './NowPlayingSection-types';

/** Encapsulates NowPlayingSection logic. */
export function useNowPlayingSection(
  props: INowPlayingSectionProps,
): IUseNowPlayingSectionReturn {
  return {
    isPlaying: props.nowPlaying !== null,
  };
}
