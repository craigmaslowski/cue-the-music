import type { IAlbumGridProps, IUseAlbumGridReturn } from './AlbumGrid-types';

/** Encapsulates AlbumGrid state derivation. */
export function useAlbumGrid(props: IAlbumGridProps): IUseAlbumGridReturn {
  const { albums } = props;

  const hasAlbums = albums.length > 0;

  return { hasAlbums };
}
