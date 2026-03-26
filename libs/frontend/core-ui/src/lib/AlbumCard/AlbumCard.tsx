import {
  artistStyles,
  coverArtStyles,
  rootStyles,
  textContainerStyles,
  titleStyles,
  yearStyles,
} from './AlbumCard-elements';
import type { IAlbumCardProps } from './AlbumCard-types';
import { useAlbumCard } from './useAlbumCard';

/** Album card showing cover art, title, artist, and year for the crate grid. */
export function AlbumCard(props: IAlbumCardProps) {
  const { artist, coverArtThumbnailUrl, title, year } = props;
  const { handlePress } = useAlbumCard(props);

  return (
    <button className={rootStyles} onClick={handlePress} type="button">
      {coverArtThumbnailUrl ? (
        <img
          alt={`${title} by ${artist}`}
          className={coverArtStyles}
          height={300}
          loading="lazy"
          src={coverArtThumbnailUrl}
          width={300}
        />
      ) : (
        /* Placeholder for albums without cover art */
        <div className={coverArtStyles} />
      )}
      <div className={textContainerStyles}>
        <span className={titleStyles}>{title}</span>
        <span className={artistStyles}>{artist}</span>
        {year && <span className={yearStyles}>{year}</span>}
      </div>
    </button>
  );
}
