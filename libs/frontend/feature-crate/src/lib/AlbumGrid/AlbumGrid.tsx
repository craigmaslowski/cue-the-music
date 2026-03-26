import { AlbumCard } from '@cue-the-music/core-ui';

import {
  gridHeadingAccentStyles,
  gridHeadingStyles,
  gridStyles,
} from './AlbumGrid-elements';
import type { IAlbumGridProps } from './AlbumGrid-types';
import { useAlbumGrid } from './useAlbumGrid';

/** 2-column responsive grid of AlbumCard components. */
export function AlbumGrid(props: IAlbumGridProps) {
  const { albums, onAlbumPress } = props;
  useAlbumGrid(props);

  return (
    <>
      <div className={gridHeadingStyles}>
        <span className={gridHeadingAccentStyles}></span>
        The Crate
      </div>
      <div className={gridStyles}>
        {albums.map((album) => (
          <AlbumCard
            artist={album.artist}
            coverArtThumbnailUrl={album.cover_art_thumbnail_url}
            id={album.id}
            key={album.id}
            onPress={onAlbumPress}
            title={album.title}
            year={album.year}
          />
        ))}
      </div>
    </>
  );
}
