import {
  artistStyles,
  badgeStyles,
  contentStyles,
  coverArtStyles,
  emptyStyles,
  infoStyles,
  placeholderArtStyles,
  rootStyles,
  titleStyles,
} from './NowPlayingSection-elements';
import type { INowPlayingSectionProps } from './NowPlayingSection-types';
import { useNowPlayingSection } from './useNowPlayingSection';

/** Prominent Now Playing display with album art, title, and artist. */
export function NowPlayingSection(props: INowPlayingSectionProps) {
  const { nowPlaying } = props;
  const { isPlaying } = useNowPlayingSection(props);

  if (!isPlaying || !nowPlaying) {
    return (
      <div className={rootStyles}>
        <div className={emptyStyles}>
          <div className={placeholderArtStyles} />
          <span>Nothing playing yet</span>
        </div>
      </div>
    );
  }

  const { album } = nowPlaying;

  return (
    <div className={rootStyles}>
      <span className={badgeStyles}>Now Playing</span>
      <div className={contentStyles}>
        {album.cover_art_thumbnail_url ? (
          <img
            alt={`${album.title} by ${album.artist}`}
            className={coverArtStyles}
            src={album.cover_art_thumbnail_url}
          />
        ) : (
          <div className={coverArtStyles} />
        )}
        <div className={infoStyles}>
          <h2 className={titleStyles}>{album.title}</h2>
          <span className={artistStyles}>{album.artist}</span>
        </div>
      </div>
    </div>
  );
}
